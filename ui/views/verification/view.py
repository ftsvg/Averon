import secrets
import string
import time

from captcha.image import ImageCaptcha
from discord import (
    ButtonStyle, 
    Client, 
    File, 
    Interaction, 
)
from discord.ui import Button, View, button
from gtts import gTTS

from content import DESCRIPTIONS, ERRORS
from core import send_verification_log
from database import VerificationSettings
from database.handlers import LoggingManager, VerificationManager
from ui import create_embed
from .captcha import CaptchaView


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
                'ERROR', f"Verification failed: verification not configured (requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.followup.send(
                content=ERRORS['verification_config_not_set_error'],
                ephemeral=True
            )

        role = interaction.guild.get_role(settings.role_id)

        if role is None:
            logging_manager.create_log(
                'ERROR', f"Verification failed: configured verification role missing (requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.followup.send(
                content=ERRORS['verification_role_error'],
                ephemeral=True
            )

        if role in interaction.user.roles:
            logging_manager.create_log(
                'INFO', f"Verification skipped: {interaction.user} ({interaction.user.id}) already verified"
            )
            return await interaction.followup.send(
                content=ERRORS['already_verified_error'],
                ephemeral=True
            )

        if not settings.captcha_enabled:
            await interaction.user.add_roles(role)
            logging_manager.create_log(
                'INFO', f"Verification completed: {interaction.user} ({interaction.user.id}) verified without captcha"
            )

            embed = create_embed(
                author_name="verification",
                fields=[
                    ("user", f"{interaction.user.name} `{interaction.user.id}`", True),
                    ("role added", f"{role.name} `{role.id}`", True)
                ],
                timestamp=True
            )
            await send_verification_log(interaction, embed)

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

        view = CaptchaView(
            interaction.user.id,
            captcha_sessions,
            verifying
        )

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
            'INFO', f"Captcha started: verification captcha issued for {interaction.user} ({interaction.user.id})"
        )
