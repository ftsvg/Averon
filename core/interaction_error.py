import traceback

from discord import Interaction, NotFound
from discord.app_commands import TransformerError

from content import ERRORS
from database.handlers import LoggingManager


class InteractionErrorHandler:
    @staticmethod
    async def handle(interaction: Interaction, error: Exception) -> None:
        error = getattr(error, "original", error)

        logging_manager = LoggingManager(
            interaction.guild.id if interaction.guild else 0
        )

        error_id = logging_manager.create_log(
            'ERROR', traceback.format_exc()
        )

        if isinstance(error, TransformerError):
            msg = ERRORS["invalid_user"]
        else:
            msg = ERRORS["interaction_error"]

        msg = f"{msg}\n-# log id: {error_id}"

        try:
            if interaction.response.is_done():
                await interaction.followup.send(content=msg, ephemeral=True)
            else:
                await interaction.response.send_message(content=msg, ephemeral=True)
        except NotFound:
            pass