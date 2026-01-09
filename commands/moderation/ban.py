import traceback
from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException

from core import check_permissions, check_action_allowed, send_moderation_log, send_mod_dm
from ui import create_embed
from content import COMMANDS, ERRORS
from database.handlers import CaseManager, LoggingManager


class Ban(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(
        name=COMMANDS["ban"]["name"],
        description=COMMANDS["ban"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["ban"]["member"],
        reason=COMMANDS["ban"]["reason"]
    )
    async def ban(
        self,
        interaction: Interaction,
        member: Member,
        reason: str | None = None
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := (
            await check_permissions(interaction, "ban")
            or await check_action_allowed(interaction, member, "ban")
        ):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to ban "
                f"{member} ({member.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        try:
            await member.ban(reason=reason)

        except (Forbidden, HTTPException):
            error_id = logging_manager.create_log(
                'ERROR',
                traceback.format_exc()
            )
            return await interaction.edit_original_response(
                content=f"{ERRORS['interaction_error']}\n-# log id: {error_id}"
            )

        user = await interaction.client.fetch_user(member.id)
        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="ban",
            reason=reason
        )

        logging_manager.create_log(
            'INFO',
            f"Ban executed: {interaction.user} ({interaction.user.id}) banned "
            f"{member} ({member.id}) in {interaction.guild.name} "
            f"(Case ID: {case_id})"
        )

        message = f"`[{case_id}]` **{member.name}** has been banned"
        if reason:
            message += f" for **{reason}**"

        await interaction.edit_original_response(
            content=message
        )

        embed = create_embed(
            author_name=f"ban [{case_id}]",
            fields=[
                ("User", f"{member.name} `{member.id}`", True),
                ("Moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("Reason", reason if reason else "Not given.", False)
            ],
            timestamp=True
        )

        await send_moderation_log(interaction, embed)
        await send_mod_dm(
            user,
            guild_name=interaction.guild.name,
            action="ban",
            case_id=case_id,
            moderator=interaction.user,
            reason=reason
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Ban(client))