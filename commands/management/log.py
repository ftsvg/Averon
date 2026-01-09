from discord.ext import commands
from discord import app_commands, Interaction

from content import ERRORS, COMMANDS
from database.handlers import LoggingManager


class Log(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(
        name=COMMANDS["log"]["name"],
        description=COMMANDS["log"]["description"]
    )
    @app_commands.describe(
        log_id=COMMANDS["log"]["log_id"]
    )
    async def error(
        self,
        interaction: Interaction,
        log_id: str
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if not await self.client.is_owner(interaction.user):
            return await interaction.edit_original_response(
                content=ERRORS["permissions_error"]
            )

        logging_manager = LoggingManager(interaction.guild.id if interaction.guild else 0)
        log = logging_manager.get_log(log_id)

        if not log:
            return await interaction.edit_original_response(
                content=ERRORS["error_not_found"]
            )

        content = (
            f"log id: `{log.log_id}`\n"
            f"log level: `{log.log_level}`\n"
            f"created at: <t:{log.created_at}:R>\n\n"
            f"```{log.log_description}```"
        )

        await interaction.edit_original_response(
            content=content
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Log(client))