from discord import Interaction, TextChannel, app_commands
from discord.ext import commands

from content import COMMANDS, DESCRIPTIONS, ERRORS
from core import check_permissions
from database.handlers import LoggingManager, ModerationManager


class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    moderation = app_commands.Group(
        name='moderation',
        description='Moderation settings related commands.',
    )


    @moderation.command(
        name=COMMANDS['logs']['name'],
        description=COMMANDS['logs']['description']
    )
    @app_commands.describe(channel=COMMANDS['logs']['channel'])
    async def logs(
        self,
        interaction: Interaction,
        channel: TextChannel
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "admin"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to set "
                f"moderation log channel to {channel} ({channel.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        settings = ModerationManager(interaction.guild.id)
        settings.set_log_channel(channel.id)

        logging_manager.create_log(
            'INFO',
            f"Moderation log channel updated: {interaction.user} ({interaction.user.id}) set "
            f"log channel to {channel} ({channel.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['moderation_logs'].format(channel.mention)
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Moderation(client))