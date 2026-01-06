from discord.ext import commands
from discord import app_commands, Interaction, TextChannel

from content import COMMANDS, COMMAND_ERRORS
from core import check_permissions, LOGO
from ui import normal, error
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
            data = COMMAND_ERRORS[error_key]
            return await interaction.edit_original_response(
                embed=error(
                    title=data["title"],
                    description=data["message"]
                )
            )
        
        settings = ModerationManager(interaction.guild.id)
        settings.set_log_channel(channel.id)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Moderation logs", author_icon_url=LOGO,
                description=f"Logs will now be sent to {channel.mention}"
            )
        )        


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Moderation(client))