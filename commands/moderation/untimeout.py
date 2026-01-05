from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException

from core import check_permissions, check_action_allowed, send_log, LOGO
from ui import normal, error, log_embed
from logger import logger
from content import COMMANDS, COMMAND_ERRORS
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
        await interaction.response.defer()

        if not await check_permissions(interaction, "untimeout"):
            return

        if not await check_action_allowed(interaction, member, "untimeout"):
            return

        if not member.is_timed_out():
            await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS["not_timed_out_error"]["title"],
                    description=COMMAND_ERRORS["not_timed_out_error"]["message"]
                )
            )
            return

        try:
            await member.timeout(None, reason=reason)
        except (Forbidden, HTTPException):
            await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS["interaction_error"]["title"],
                    description=COMMAND_ERRORS["interaction_error"]["message"]
                )
            )
            return

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

        description = f"`{member}` has been un-timed out"
        if reason:
            description += f"\n**Reason:** {reason}"

        await interaction.edit_original_response(
            embed=normal(
                author_name=f"untimeout [{case_id}]",
                author_icon_url=LOGO,
                description=description
            )
        )

        await send_log(
            interaction,
            log_embed(
                author_name=f"untimeout [{case_id}]",
                fields=[
                    ("user", f"{member} `{member.id}`", True),
                    ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                    ("reason", reason or "Not given.", False)
                ]
            )
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Untimeout(client))