import os

from discord import Interaction, Message, Role
from discord.ui import Modal, TextInput

from content import DESCRIPTIONS, ERRORS
from core import send_verification_log
from database.handlers import LoggingManager
from ui import create_embed


class CaptchaModal(Modal, title="Captcha Verification"):
    captcha_input = TextInput(
        label="Enter the captcha",
        placeholder="Enter the letters and numbers shown in the image",
        required=True,
        max_length=6,
    )

    def __init__(
        self,
        user_id: int,
        captcha_sessions: dict,
        verifying: set,
    ):
        super().__init__()
        self.user_id = user_id
        self.captcha_sessions = captcha_sessions
        self.verifying = verifying

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        session = self.captcha_sessions.get(self.user_id)
        if not session:
            return

        message: Message = session["message"]
        role: Role = session["role"]

        logging_manager = LoggingManager(interaction.guild.id)

        def cleanup():
            self.verifying.discard(self.user_id)
            self.captcha_sessions.pop(self.user_id, None)

            try:
                os.remove(session["file_path"])
                os.remove(session["audio_path"])
            except Exception:
                pass

        if self.captcha_input.value != session["answer"]:
            cleanup()

            logging_manager.create_log(
                "WARNING",
                f"Captcha failed: invalid captcha entered by "
                f"{interaction.user} ({interaction.user.id})",
            )

            await message.edit(
                content=ERRORS["invalid_captcha_code_error"],
                embed=None,
                view=None,
                attachments=[],
            )
            return

        await interaction.user.add_roles(role)

        embed = create_embed(
            author_name="verification",
            fields=[
                ("user", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("role added", f"{role.name} `{role.id}`", True),
            ],
            timestamp=True,
        )
        await send_verification_log(interaction, embed)

        cleanup()

        logging_manager.create_log(
            "INFO",
            f"Verification completed: {interaction.user} "
            f"({interaction.user.id}) successfully verified via captcha",
        )

        await message.edit(
            content=DESCRIPTIONS["verification_success"],
            embed=None,
            view=None,
            attachments=[],
        )
