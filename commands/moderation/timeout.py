from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException
from datetime import datetime, timedelta, timezone

from core import check_permissions, check_action_allowed, send_log, send_mod_dm
from ui import create_embed
from logger import logger
from content import COMMANDS, ERRORS
from database.handlers import CaseManager


TIMEOUT_DURATIONS = {
    "60 seconds": timedelta(seconds=60),
    "5 minutes": timedelta(minutes=5),
    "10 minutes": timedelta(minutes=10),
    "1 hour": timedelta(hours=1),
    "1 day": timedelta(days=1),
    "1 week": timedelta(weeks=1),
}


class Timeout(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name=COMMANDS["timeout"]["name"],
        description=COMMANDS["timeout"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["timeout"]["member"],
        duration=COMMANDS["timeout"]["duration"],
        reason=COMMANDS["timeout"]["reason"]
    )
    @app_commands.choices(
        duration=[
            app_commands.Choice(name=name, value=name)
            for name in TIMEOUT_DURATIONS.keys()
        ]
    )
    async def timeout(
        self,
        interaction: Interaction,
        member: Member,
        duration: app_commands.Choice[str],
        reason: str | None = None
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := (
            await check_permissions(interaction, "timeout")
            or await check_action_allowed(interaction, member, "timeout")
        ):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )

        if member.is_timed_out():
            return await interaction.edit_original_response(
                content=ERRORS['already_timed_out'].format(member.name)
            )

        delta = TIMEOUT_DURATIONS.get(duration.value)
        if not delta:
            return await interaction.edit_original_response(
                content=ERRORS['interaction_error']
            )

        until = datetime.now(timezone.utc) + delta
        duration_seconds = int(delta.total_seconds())

        try:
            await member.timeout(until, reason=reason)
            
        except (Forbidden, HTTPException):
            return await interaction.edit_original_response(
                content=ERRORS['interaction_error']
            )

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="timeout",
            reason=reason,
            duration=duration_seconds
        )

        logger.info(
            f"{interaction.user.name} timed out {member} for {duration.name} - Case #{case_id}"
        )

        msg = f"`[{case_id}]` **{member}** has been timed out for `{duration.name}`"
        if reason:
            msg += f"\n**Reason:** {reason}"

        await interaction.edit_original_response(
            content=msg
        )

        embed = create_embed(
            author_name=f"timeout [{case_id}]",
            fields=[
                ("user", f"{member} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("duration", duration.name, False),
                ("reason", reason or "Not given.", False)
            ]            
        )

        await send_log(interaction, embed)
        await send_mod_dm(
            member,
            guild_name=interaction.guild.name,
            action="timeout",
            case_id=case_id,
            moderator=interaction.user,
            duration=duration.name,
            reason=reason
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Timeout(client))