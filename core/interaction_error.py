import traceback
from discord import app_commands, Interaction, NotFound
from discord.app_commands import TransformerError

from ui.embeds import error as error_embed
from content import COMMAND_ERRORS


class InteractionErrorHandler:
    @staticmethod
    async def handle(interaction: Interaction, error: Exception) -> None:
        error = getattr(error, "original", error)
        traceback.print_exception(error)

        if isinstance(error, TransformerError):
            data = COMMAND_ERRORS["invalid_user"]
        else:
            data = COMMAND_ERRORS["interaction_error"]

        embed = error_embed(
            title=data["title"],
            description=data["message"]
        )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except NotFound:
            pass