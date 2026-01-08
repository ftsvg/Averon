import traceback
from discord import Interaction, NotFound
from discord.app_commands import TransformerError

from content import ERRORS


class InteractionErrorHandler:
    @staticmethod
    async def handle(interaction: Interaction, error: Exception) -> None:
        error = getattr(error, "original", error)
        traceback.print_exception(error)

        if isinstance(error, TransformerError):
            msg = ERRORS["invalid_user"]
        else:
            msg = ERRORS["interaction_error"]

        try:
            if interaction.response.is_done():
                await interaction.followup.send(content=msg, ephemeral=True)
            else:
                await interaction.response.send_message(content=msg, ephemeral=True)
        except NotFound:
            pass