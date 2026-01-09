import traceback
from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException

from core import check_permissions, check_action_allowed, send_moderation_log
from ui import create_embed
from content import COMMANDS, ERRORS
from database.handlers import CaseManager, LoggingManager


class Untimeout(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(
        name=COMMANDS["untimeout"]["name"],
        description=COMMANDS["untimeout"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["untimeout"]["member"],
        reason=COMMANDS["untimeout"]["reason"]
    )
    async def untimeout(
        self,
        interaction: Interaction,
        member: Member,
        reason: str | None = None
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := (
            await check_permissions(interaction, "timeout")
            or await check_action_allowed(interaction, member, "timeout")
        ):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to remove timeout from "
                f"{member} ({member.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        if not member.is_timed_out():
            logging_manager.create_log(
                'INFO',
                f"Untimeout skipped: {member} ({member.id}) is not currently timed out "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.edit_original_response(
                content=ERRORS['not_timed_out_error'].format(member.name)
            )

        try:
            await member.timeout(None, reason=reason)

        except (Forbidden, HTTPException):
            error_id = logging_manager.create_log(
                'ERROR',
                traceback.format_exc()
            )
            return await interaction.edit_original_response(
                content=f"{ERRORS['interaction_error']}\n-# log id: {error_id}"
            )

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="untimeout",
            reason=reason
        )

        logging_manager.create_log(
            'INFO',
            f"Untimeout executed: {interaction.user} ({interaction.user.id}) removed timeout from "
            f"{member} ({member.id}) in {interaction.guild.name} (Case ID: {case_id})"
        )

        message = f"`[{case_id}]` **{member.name}** has been un-timed out"
        if reason:
            message += f"\n**Reason:** {reason}"

        await interaction.edit_original_response(
            content=message
        )

        embed = create_embed(
            author_name=f"untimeout [{case_id}]",
            fields=[
                ("User", f"{member.name} `{member.id}`", True),
                ("Moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("Reason", reason or "Not given.", False)
            ]
        )

        await send_moderation_log(interaction, embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Untimeout(client))