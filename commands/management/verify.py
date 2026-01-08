from discord.ext import commands
from discord import app_commands, Interaction, TextChannel, Role

from core import check_permissions
from ui import create_embed
from ui.views import VerificationView
from content import COMMANDS, ERRORS, DESCRIPTIONS
from database.handlers import VerificationManager


class Verify(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    verification = app_commands.Group(
        name='verification',
        description='verification related commands.',
    )

    @verification.command(
        name=COMMANDS['verification_role']['name'],
        description=COMMANDS['verification_role']['description']
    )
    @app_commands.describe(
        role=COMMANDS['verification_role']['role']
    )
    async def role(
        self, 
        interaction: Interaction,
        role: Role
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if error_key := await check_permissions(interaction, "admin"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )        

        settings = VerificationManager(interaction.guild.id)
        settings.set_role(role.id)

        await interaction.edit_original_response(
            content=DESCRIPTIONS['verification_role_set'].format(role.mention)
        )


    @verification.command(
        name=COMMANDS['verification_channel']['name'],
        description=COMMANDS['verification_channel']['description']
    )
    @app_commands.describe(
        channel=COMMANDS['verification_channel']['channel']
    )
    async def logs(
        self, 
        interaction: Interaction,
        channel: TextChannel
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if error_key := await check_permissions(interaction, "admin"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )       

        settings = VerificationManager(interaction.guild.id)
        settings.set_logs_channel(channel.id)

        await interaction.edit_original_response(
            content=DESCRIPTIONS['verification_logs_set'].format(channel.mention)
        )


    @verification.command(
        name=COMMANDS['verification_captcha']['name'],
        description=COMMANDS['verification_captcha']['description']
    )
    @app_commands.describe(
        enabled=COMMANDS['verification_captcha']['enable']
    )
    async def captcha(
        self,
        interaction: Interaction,
        enabled: bool
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if error_key := await check_permissions(interaction, "admin"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )

        settings = VerificationManager(interaction.guild.id)
        settings.set_captcha_enabled(enabled)

        await interaction.edit_original_response(
            content=DESCRIPTIONS['verification_captcha_set'].format('enabled' if enabled else 'disabled')
        )


    @verification.command(
        name=COMMANDS['verification_panel']['name'],
        description=COMMANDS['verification_panel']['description']
    )
    @app_commands.describe(
        channel=COMMANDS['verification_panel']['channel']
    )
    async def panel(
        self, 
        interaction: Interaction,
        channel: TextChannel
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if error_key := await check_permissions(interaction, "admin"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )       

        settings = VerificationManager(interaction.guild.id)
        settings.set_logs_channel(channel.id)

        await channel.send(
            embed=create_embed(
                author_name="Verification",
                description="Please click the button below to verify."                
            ), 
            view=VerificationView(self.client)
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['verification_panel'].format(channel.mention)
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Verify(client))