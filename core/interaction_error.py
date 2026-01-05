from discord import app_commands, Interaction, NotFound
from discord.app_commands import TransformerError

from ui.embeds import error as error_embed
from content import COMMAND_ERRORS


class InteractionErrorHandler:
    @staticmethod
    async def handle(interaction: Interaction, error: Exception) -> None:
        error = getattr(error, "original", error)

        if isinstance(error, TransformerError):
            embed = error_embed(
                title=COMMAND_ERRORS["invalid_user"]["title"],
                description=COMMAND_ERRORS["invalid_user"]["message"]
            )
        else:
            embed = error_embed(
                title=COMMAND_ERRORS["interaction_error"]["title"],
                description=COMMAND_ERRORS["interaction_error"]["message"]
            )

        if interaction.response.is_done():
            try:
                await interaction.edit_original_response(embed=embed)
            except NotFound:
                await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)