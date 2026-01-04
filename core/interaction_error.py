from discord import app_commands, Interaction, NotFound

from ui.embeds import error as error_embed
from content import COMMAND_ERRORS


class InteractionErrorHandler:
    @staticmethod
    async def handle(
        interaction: Interaction, error: Exception
    ) -> None:

        if isinstance(error, app_commands.AppCommandError):
            error = error.original or error

        embed = error_embed(
            COMMAND_ERRORS['interaction_error']['title'],
            COMMAND_ERRORS['interaction_error']['message']
        )

        if interaction.response.is_done():
            try:
                await interaction.edit_original_response(embed=embed)
            except NotFound:
                await interaction.followup.send(embed=embed, ephemeral=True)

        else:
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )