from discord.ext import commands
from discord import app_commands, Interaction, Member

from core import check_permissions, check_action_allowed, send_log, LOGO
from ui import normal, log_embed
from logger import logger
from content import COMMANDS
from database.handlers import CaseManager


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
        await interaction.response.defer()

        if not await check_permissions(interaction, "kick"):
            return
        
        if not await check_action_allowed(interaction, member, "kick"):
            return

        await member.kick(reason=reason)

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="kick",
            reason=reason
        )

        logger.info(
            f"{interaction.user.name} kicked {member.name} from {interaction.guild.name} - Case #{case_id}"
        )

        description = f"`{member.name}` has been kicked"
    
        if reason:
            description += f" for **{reason}**"

        await interaction.edit_original_response(
            embed=normal(
                author_name=f"kick [{case_id}]",
                author_icon_url=LOGO,
                description=description
            )
        )

        _log_embed = log_embed(
            author_name=f"kick [{case_id}]",
            fields=[
                ("user", f"{member.name} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", f"{reason if reason else 'Not given.'}", False)
            ]
        )

        await send_log(interaction, _log_embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Kick(client))