from discord.ext import commands
from discord import app_commands, Interaction, TextChannel

from content import COMMANDS, ERRORS, DESCRIPTIONS
from core import check_permissions
from database.handlers import ModerationManager


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    moderation = app_commands.Group(
        name='moderation',
        description='Moderation settings related commands.',
    )

    @moderation.command(
        name=COMMANDS['logs']['name'],
        description=COMMANDS['logs']['description']
    )
    @app_commands.describe(
        channel=COMMANDS['logs']['channel']
    )
    async def logs(
        self,
        interaction: Interaction,
        channel: TextChannel
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := await check_permissions(interaction, "admin"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            ) 
        
        settings = ModerationManager(interaction.guild.id)
        settings.set_log_channel(channel.id)

        await interaction.edit_original_response(
            content=DESCRIPTIONS['moderation_logs'].format(channel.mention)
        )        


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Moderation(client))