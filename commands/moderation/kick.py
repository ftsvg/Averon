import traceback
from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException

from core import check_permissions, check_action_allowed, send_moderation_log, send_mod_dm
from ui import create_embed
from content import COMMANDS, ERRORS
from database.handlers import CaseManager, LoggingManager


class Kick(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(
        name=COMMANDS["kick"]["name"],
        description=COMMANDS["kick"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["kick"]["member"],
        reason=COMMANDS["kick"]["reason"]
    )
    async def kick(
        self,
        interaction: Interaction,
        member: Member,
        reason: str | None = None
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := (
            await check_permissions(interaction, "kick")
            or await check_action_allowed(interaction, member, "kick")
        ):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to kick "
                f"{member} ({member.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        try:
            await member.kick(reason=reason)

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
            case_type="kick",
            reason=reason
        )

        logging_manager.create_log(
            'INFO',
            f"Kick executed: {interaction.user} ({interaction.user.id}) kicked "
            f"{member} ({member.id}) in {interaction.guild.name} "
            f"(Case ID: {case_id})"
        )

        message = f"`[{case_id}]` **{member.name}** has been kicked"
        if reason:
            message += f" for **{reason}**"

        await interaction.edit_original_response(
            content=message
        )

        embed = create_embed(
            author_name=f"kick [{case_id}]",
            fields=[
                ("User", f"{member.name} `{member.id}`", True),
                ("Moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("Reason", reason if reason else "Not given.", False)
            ],
            timestamp=True
        )

        await send_moderation_log(interaction, embed)
        await send_mod_dm(
            member,
            guild_name=interaction.guild.name,
            action="kick",
            case_id=case_id,
            moderator=interaction.user,
            reason=reason
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Kick(client))