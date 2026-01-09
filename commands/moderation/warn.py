from discord.ext import commands
from discord import app_commands, Interaction, Member

from core import check_permissions, check_action_allowed, send_moderation_log, send_user_dm
from ui import create_embed
from content import COMMANDS, ERRORS
from database.handlers import CaseManager, LoggingManager


class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @app_commands.command(
        name=COMMANDS["warn"]["name"],
        description=COMMANDS["warn"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["warn"]["member"],
        reason=COMMANDS["warn"]["reason"]
    )
    async def warn(
        self,
        interaction: Interaction,
        member: Member,
        reason: str | None = None
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := (
            await check_permissions(interaction, "warn")
            or await check_action_allowed(interaction, member, "warn")
        ):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to warn "
                f"{member} ({member.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="warn",
            reason=reason
        )

        logging_manager.create_log(
            'INFO',
            f"Warning issued: {interaction.user} ({interaction.user.id}) warned "
            f"{member} ({member.id}) in {interaction.guild.name} (Case ID: {case_id})"
        )

        message = f"`[{case_id}]` **{member.name}** has been warned"
        if reason:
            message += f" for **{reason}**"

        await interaction.edit_original_response(
            content=message
        )

        embed = create_embed(
            author_name=f"warn [{case_id}]",
            fields=[
                ("User", f"{member.name} `{member.id}`", True),
                ("Moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("Reason", reason or "Not given.", False)
            ]
        )

        await send_moderation_log(interaction, embed)
        await send_user_dm(
            interaction, 
            member, 
            embed=embed, 
            content=f"You have been *warned* in **{interaction.guild.name}**."
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Warn(bot))