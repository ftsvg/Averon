from discord.ext import commands
from discord import app_commands, Interaction, Member

from core import check_permissions, check_action_allowed, send_log, LOGO
from ui import normal, log_embed
from logger import logger
from content import COMMANDS
from database.handlers import CaseManager


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
        await interaction.response.defer()

        if not await check_permissions(interaction, "ban"):
            return
        
        if not await check_action_allowed(interaction, member, "ban"):
            return

        await member.ban(reason=reason)

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="ban",
            reason=reason
        )

        logger.info(
            f"{interaction.user.name} banned {member.name} from {interaction.guild.name} - Case #{case_id}"
        )

        description = f"`{member.name}` has been banned"

        if reason:
            description += f" for **{reason}**"

        await interaction.edit_original_response(
            embed=normal(
                author_name=f"ban [{case_id}]",
                author_icon_url=LOGO,
                description=description
            )
        )

        _log_embed = log_embed(
            author_name=f"ban [{case_id}]",
            fields=[
                ("user", f"{member.name} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", f"{reason if reason else 'Not given.'}", False)
            ]
        )

        await send_log(interaction, _log_embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Ban(client))