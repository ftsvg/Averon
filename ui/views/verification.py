import os
import secrets
import string
import time

from captcha.image import ImageCaptcha
from discord import ButtonStyle, Client, File, Interaction, Message
from discord.ui import Button, Modal, TextInput, View, button
from gtts import gTTS

from content import DESCRIPTIONS, ERRORS
from database import VerificationSettings
from database.handlers import LoggingManager, VerificationManager
from ui import create_embed


verifying = set()
captcha_sessions = {}


class VerificationView(View):
    def __init__(self, client: Client):
        super().__init__(timeout=None)
        self.client = client

    @button(label="Verify", style=ButtonStyle.gray, custom_id="verify_ticket")
    async def verify(self, interaction: Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        manager = VerificationManager(interaction.guild.id)
        settings: VerificationSettings = manager.get_settings()

        if not settings or not settings.role_id or not settings.logs_channel_id:
            logging_manager.create_log(
                'ERROR',
                f"Verification failed: verification not configured "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.followup.send(
                content=ERRORS['verification_config_not_set_error'],
                ephemeral=True
            )

        role = interaction.guild.get_role(settings.role_id)

        if role is None:
            logging_manager.create_log(
                'ERROR',
                f"Verification failed: configured verification role missing "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.followup.send(
                content=ERRORS['verification_role_error'],
                ephemeral=True
            )

        if role in interaction.user.roles:
            logging_manager.create_log(
                'INFO',
                f"Verification skipped: {interaction.user} ({interaction.user.id}) already verified"
            )
            return await interaction.followup.send(
                content=ERRORS['already_verified_error'],
                ephemeral=True
            )

        if not settings.captcha_enabled:
            await interaction.user.add_roles(role)
            logging_manager.create_log(
                'INFO',
                f"Verification completed: {interaction.user} ({interaction.user.id}) verified without captcha"
            )
            return await interaction.followup.send(
                content=DESCRIPTIONS['verification_success'],
                ephemeral=True
            )

        if interaction.user.id in verifying:
            return await interaction.followup.send(
                content=ERRORS['already_verifying_error'],
                ephemeral=True
            )

        verifying.add(interaction.user.id)

        captcha_str = ''.join(
            secrets.choice(string.ascii_lowercase + string.digits)
            for _ in range(6)
        )

        file_path = f"./assets/captcha/{interaction.user.id}-captcha.jpg"

        image = ImageCaptcha(
            width=280,
            height=90,
            fonts=["./assets/font/Roboto.ttf"],
            font_sizes=[60]
        )
        image.write(captcha_str, file_path)
        file = File(file_path, filename="captcha.jpg")

        audio_path = f"./assets/captcha/{interaction.user.id}-captcha.mp3"

        tts_text = " ".join(captcha_str)
        tts = gTTS(text=f"{tts_text}", lang="en")
        tts.save(audio_path)

        embed = create_embed(
            author_name="Captcha",
            description=(
                "You have `1 minute` to answer the captcha correctly.\n"
                "The captcha will only contain **lowercase** letters and numbers.\n\n"
                "If you can't read the image, use the **Audio** button."
            ),
            image="attachment://captcha.jpg"
        )

        view = CaptchaView(interaction.user.id)

        message = await interaction.followup.send(
            embed=embed,
            file=file,
            view=view,
            ephemeral=True
        )

        captcha_sessions[interaction.user.id] = {
            "answer": captcha_str,
            "expires": time.time() + 60,
            "role": role,
            "message": message,
            "guild_id": interaction.guild.id,
            "file_path": file_path,
            "audio_path": audio_path
        }

        logging_manager.create_log(
            'INFO',
            f"Captcha started: verification captcha issued for "
            f"{interaction.user} ({interaction.user.id})"
        )


class CaptchaView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id

    @button(label="Enter Code", style=ButtonStyle.blurple)
    async def enter_code(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(CaptchaModal(self.user_id))


    @button(label="Audio", style=ButtonStyle.gray)
    async def audio(self, interaction: Interaction, button: Button):
        session = captcha_sessions.get(self.user_id)           

        audio_file = File(
            session['audio_path'],
            filename="captcha.mp3"
        )

        await interaction.response.send_message(
            content="**Here is the audio version of the captcha.**\n-# This message will be deleted in 15 seconds.",
            file=audio_file,
            delete_after=15,
            ephemeral=True,
        )

    async def on_timeout(self):
        session = captcha_sessions.get(self.user_id)
        if not session:
            return

        logging_manager = LoggingManager(session["guild_id"])

        message: Message = session["message"]

        await message.edit(
            content=ERRORS['captcha_expired_error'],
            embed=None,
            view=None,
            attachments=[]
        )

        verifying.discard(self.user_id)
        captcha_sessions.pop(self.user_id, None)

        logging_manager.create_log(
            'INFO', f"Captcha expired: verification captcha expired for user ID {self.user_id}"
        )

        try:
            os.remove(session["file_path"])
            os.remove(session['audio_path'])
        except Exception:
            pass


class CaptchaModal(Modal, title="Captcha Verification"):
    captcha_input = TextInput(
        label="Enter the captcha",
        placeholder="Type the letters and numbers shown in the image",
        required=True,
        max_length=6
    )

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer()

        session = captcha_sessions.get(self.user_id)
        message: Message = session["message"]

        logging_manager = LoggingManager(interaction.guild.id)

        def cleanup():
            verifying.discard(self.user_id)
            captcha_sessions.pop(self.user_id, None)
            try:
                os.remove(session["file_path"])
                os.remove(session['audio_path'])
            except Exception:
                pass

        if self.captcha_input.value != session["answer"]:
            cleanup()
            logging_manager.create_log(
                'WARNING',
                f"Captcha failed: invalid captcha entered by "
                f"{interaction.user} ({interaction.user.id})"
            )
            return await message.edit(
                content=ERRORS['invalid_captcha_code_error'],
                embed=None,
                view=None,
                attachments=[]
            )

        await interaction.user.add_roles(session["role"])
        cleanup()

        logging_manager.create_log(
            'INFO',
            f"Verification completed: {interaction.user} ({interaction.user.id}) "
            f"successfully verified via captcha"
        )

        await message.edit(
            content=DESCRIPTIONS['verification_success'],
            embed=None,
            view=None,
            attachments=[]
        )