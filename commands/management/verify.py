from discord.ext import commands
from discord import app_commands, Interaction, TextChannel, Role

from core import LOGO, check_permissions
from ui import normal, error, log_embed
from content import COMMANDS, COMMAND_ERRORS
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
            data = COMMAND_ERRORS[error_key]
            return await interaction.edit_original_response(
                embed=error(
                    title=data["title"],
                    description=data["message"]
                )
            )        

        settings = VerificationManager(interaction.guild.id)
        settings.set_role(role.id)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Verification role", author_icon_url=LOGO,
                description=f"Verification role set to {role.mention}"
            )
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
            data = COMMAND_ERRORS[error_key]
            return await interaction.edit_original_response(
                embed=error(
                    title=data["title"],
                    description=data["message"]
                )
            )        

        settings = VerificationManager(interaction.guild.id)
        settings.set_logs_channel(channel.id)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Verification logs", author_icon_url=LOGO,
                description=f"Verification logs channel set to {channel.mention}"
            )
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
            data = COMMAND_ERRORS[error_key]
            return await interaction.edit_original_response(
                embed=error(
                    title=data["title"],
                    description=data["message"]
                )
            )

        settings = VerificationManager(interaction.guild.id)
        settings.set_captcha_enabled(enabled)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Verification captcha",
                author_icon_url=LOGO,
                description=f"Captcha verification {'enabled' if enabled else 'disabled'}"
            )
        )

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Verify(client))