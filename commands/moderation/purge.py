from discord.ext import commands
from discord import app_commands, Interaction, Forbidden, HTTPException

from core import check_permissions   
from content import COMMANDS, ERRORS, DESCRIPTIONS


class Purge(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name=COMMANDS["purge"]["name"],
        description=COMMANDS["purge"]["description"]
    )
    @app_commands.describe(
        amount=COMMANDS["purge"]["amount"]
    )
    async def purge(
        self,
        interaction: Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := await check_permissions(interaction, "purge"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )

        try:
            deleted = await interaction.channel.purge(
                limit=amount,
                before=interaction.created_at,
            )
            
        except (Forbidden, HTTPException):
            return await interaction.edit_original_response(
                content=ERRORS['interaction_error']
            )

        await interaction.edit_original_response(
            content = DESCRIPTIONS['moderation_purge'].format(len(deleted))
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Purge(client))