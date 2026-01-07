import time
import os
import random
from discord import Client, Interaction, ButtonStyle, Embed, File, Message 
from captcha.image import ImageCaptcha
from discord.ui import View, button, Button, Modal, TextInput

from database.handlers import VerificationManager
from database import VerificationSettings
from ui import error, normal
from content import COMMAND_ERRORS
from core import LOGO, MAIN_COLOR


verifying = set()
letters = list("abcdegkmnopqsuvwxyz")
captcha_sessions = {}


class VerificationView(View):
    def __init__(self, client: Client):
        super().__init__(timeout=None)
        self.client = client

    @button(label="Verify", style=ButtonStyle.gray, custom_id="verify_ticket")
    async def verify(self, interaction: Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        manager = VerificationManager(interaction.guild.id)
        settings: VerificationSettings = manager.get_settings()

        if not settings or not settings.role_id or not settings.logs_channel_id:
            return await interaction.followup.send(
                embed=error(
                    title=COMMAND_ERRORS["verification_config_not_set_error"]["title"],
                    description=COMMAND_ERRORS["verification_config_not_set_error"]["message"]
                ),
                ephemeral=True
            )

        role = interaction.guild.get_role(settings.role_id)

        if role is None:
            return await interaction.followup.send(
                embed=error(
                    title=COMMAND_ERRORS['verification_role_error']['title'],
                    description=COMMAND_ERRORS['verification_role_error']['message']
                ),
                ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.followup.send(
                embed=error(
                    title=COMMAND_ERRORS['already_verified_error']['title'],
                    description=COMMAND_ERRORS['already_verified_error']['message']
                ),
                ephemeral=True
            )

        if not settings.captcha_enabled:
            await interaction.user.add_roles(role)
            return await interaction.followup.send(
                embed=normal(
                    author_name="Verified", author_icon_url=LOGO,
                    description="You have successfully been verified."
                ),
                ephemeral=True
            )

        if interaction.user.id in verifying:
            return await interaction.followup.send(
                embed=error(
                    title=COMMAND_ERRORS['already_verifying_error']['title'],
                    description=COMMAND_ERRORS['already_verifying_error']['message']
                ),
                ephemeral=True
            )

        verifying.add(interaction.user.id)

        captcha_str = ''.join(random.choice(letters) for _ in range(random.randint(6, 8)))
        file_path = f"./assets/captcha/{interaction.user.id}-captcha.jpg"

        image = ImageCaptcha(
            width=280,
            height=90,
            fonts=["./assets/font/Roboto.ttf"],
            font_sizes=[60]
        )
        image.write(captcha_str, file_path)

        file = File(file_path, filename="captcha.jpg")

        embed = Embed(
            title="Captcha",
            description=(
                "You have `1 minute` to answer the captcha correctly.\n"
                "The captcha will only contain **lowercase** letters."
            ),
            color=MAIN_COLOR
        )
        embed.set_image(url="attachment://captcha.jpg")

        view = CaptchaView(interaction.user.id)

        message = await interaction.followup.send(
            embed=embed,
            file=file,
            view=view,
            ephemeral=True
        )

        captcha_sessions[interaction.user.id] = {
            "answer": captcha_str.lower(),
            "expires": time.time() + 60,
            "role": role,
            "message": message,
            "file_path": file_path
        }


class CaptchaView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id

    @button(label="Enter Code", style=ButtonStyle.blurple)
    async def enter_code(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(CaptchaModal(self.user_id))

    async def on_timeout(self):
        session = captcha_sessions.get(self.user_id)
        if not session:
            return

        message: Message = session["message"]

        await message.edit(
            embed=error(
                title=COMMAND_ERRORS['captcha_expired_error']['title'],
                description=COMMAND_ERRORS['captcha_expired_error']['message']
            ),
            view=None,
            attachments=[]
        )

        verifying.discard(self.user_id)
        captcha_sessions.pop(self.user_id, None)

        try:
            os.remove(session["file_path"])
        except Exception:
            pass


class CaptchaModal(Modal, title="Captcha Verification"):
    captcha_input = TextInput(
        label="Enter the captcha",
        placeholder="Type the letters shown in the image",
        required=True,
        max_length=8
    )

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer()

        session = captcha_sessions.get(self.user_id)
        message: Message = session["message"]

        def cleanup():
            verifying.discard(self.user_id)
            captcha_sessions.pop(self.user_id, None)
            try:
                os.remove(session["file_path"])
            except Exception:
                pass

        if self.captcha_input.value.lower() != session["answer"]:
            cleanup()
            return await message.edit(
                embed=error(
                    title=COMMAND_ERRORS['invalid_captcha_code_error']['title'],
                    description=COMMAND_ERRORS['invalid_captcha_code_error']['message']
                ),
                view=None,
                attachments=[]
            )

        await interaction.user.add_roles(session["role"])
        cleanup()

        await message.edit(
            embed=normal(
                author_name="Verified", author_icon_url=LOGO,
                description="You have successfully been verified."
            ),
            view=None,
            attachments=[]
        )