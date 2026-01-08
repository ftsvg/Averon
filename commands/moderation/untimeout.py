from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException

from core import check_permissions, check_action_allowed, send_log
from ui import create_embed
from logger import logger
from content import COMMANDS, ERRORS
from database.handlers import CaseManager


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

        if error_key := (
            await check_permissions(interaction, "timeout")
            or await check_action_allowed(interaction, member, "timeout")
        ):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )

        if not member.is_timed_out():
            return await interaction.edit_original_response(
                content=ERRORS['not_timed_out_error'].format(member.name)
            )

        try:
            await member.timeout(None, reason=reason)

        except (Forbidden, HTTPException):
            return await interaction.edit_original_response(
                content=ERRORS['interaction_error']
            )

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="untimeout",
            reason=reason
        )

        logger.info(
            f"{interaction.user.name} removed timeout from {member} - Case #{case_id}"
        )

        msg = f"`[{case_id}] **{member}** has been un-timed out"

        if reason:
            msg += f"\n**Reason:** {reason}"

        await interaction.edit_original_response(
            content=msg
        )

        embed = create_embed(
            author_name=f"untimeout [{case_id}]",
            fields=[
                ("user", f"{member} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", reason or "Not given.", False)
            ]            
        )

        await send_log(interaction, embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Untimeout(client))