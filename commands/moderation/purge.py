import traceback
from discord.ext import commands
from discord import app_commands, Interaction, Forbidden, HTTPException

from core import check_permissions
from content import COMMANDS, ERRORS, DESCRIPTIONS
from database.handlers import LoggingManager


class Purge(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(
        name=COMMANDS["purge"]["name"],
        description=COMMANDS["purge"]["description"]
    )
    @app_commands.describe(amount=COMMANDS["purge"]["amount"])
    async def purge(
        self,
        interaction: Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "purge"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to purge "
                f"{amount} messages in #{interaction.channel} ({interaction.channel.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        try:
            deleted = await interaction.channel.purge(
                limit=amount,
                before=interaction.created_at
            )

        except (Forbidden, HTTPException):
            error_id = logging_manager.create_log(
                'ERROR',
                traceback.format_exc()
            )
            return await interaction.edit_original_response(
                content=f"{ERRORS['interaction_error']}\n-# log id: {error_id}"
            )

        logging_manager.create_log(
            'INFO',
            f"Purge executed: {interaction.user} ({interaction.user.id}) deleted "
            f"{len(deleted)} messages in #{interaction.channel} ({interaction.channel.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['moderation_purge'].format(len(deleted))
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Purge(client))