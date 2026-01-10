import os

from discord import (
    ButtonStyle,
    File,
    Interaction,
    Message,
)
from discord.ui import Button, View, button

from content import ERRORS
from database.handlers import LoggingManager
from .modals import CaptchaModal


class CaptchaView(View):
    def __init__(
        self,
        user_id: int,
        captcha_sessions: dict,
        verifying: set,
    ):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.captcha_sessions = captcha_sessions
        self.verifying = verifying
        self.message: Message | None = None

    def _bind_message(self, interaction: Interaction):
        if self.message is None:
            self.message = interaction.message

    @button(label="Enter Code", style=ButtonStyle.blurple)
    async def enter_code(self, interaction: Interaction, button: Button):
        self._bind_message(interaction)

        await interaction.response.send_modal(
            CaptchaModal(
                user_id=self.user_id,
                captcha_sessions=self.captcha_sessions,
                verifying=self.verifying,
            )
        )

    @button(label="Audio", style=ButtonStyle.gray)
    async def audio(self, interaction: Interaction, button: Button):
        session = self.captcha_sessions.get(self.user_id)
        if not session:
            return

        audio_file = File(
            session["audio_path"],
            filename="captcha.mp3",
        )

        await interaction.response.send_message(
            content=(
                "**Here is the audio version of the captcha.**\n"
                "-# This message will be deleted in 10 seconds."
            ),
            file=audio_file,
            delete_after=10,
            ephemeral=True,
        )

    async def on_timeout(self):
        session = self.captcha_sessions.get(self.user_id)
        if not session:
            return

        logging_manager = LoggingManager(session["guild_id"])
        message: Message = session["message"]

        await message.edit(
            content=ERRORS["captcha_expired_error"],
            embed=None,
            view=None,
            attachments=[],
        )

        self.verifying.discard(self.user_id)
        self.captcha_sessions.pop(self.user_id, None)

        logging_manager.create_log(
            "INFO",
            f"Captcha expired: verification captcha expired for user ID {self.user_id}",
        )

        try:
            os.remove(session["file_path"])
            os.remove(session["audio_path"])
        except Exception:
            pass