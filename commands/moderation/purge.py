from discord.ext import commands
from discord import app_commands, Interaction, TextChannel, Forbidden, HTTPException

from core import check_permissions, LOGO   
from ui import normal, error
from content import COMMANDS, COMMAND_ERRORS


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
        await interaction.response.defer()

        if not await check_permissions(interaction, "purge"):
            return

        channel: TextChannel = interaction.channel

        try:
            deleted = await channel.purge(
                limit=amount,
                before=interaction.created_at,
                reason=f"Purge by {interaction.user}"
            )
        except (Forbidden, HTTPException):
            await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS["interaction_error"]["title"],
                    description=COMMAND_ERRORS["interaction_error"]["message"]
                )
            )
            return

        await interaction.edit_original_response(
            embed=normal(
                author_name="purge", author_icon_url=LOGO,
                description=f"Successfully purged `{len(deleted)}` messages in {channel.mention}"
            )
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Purge(client))