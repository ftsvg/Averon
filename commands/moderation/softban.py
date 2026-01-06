from discord.ext import commands
from discord import app_commands, Interaction, Member, Object

from core import check_permissions, check_action_allowed, send_log, send_mod_dm, LOGO
from ui import normal, error, log_embed
from logger import logger
from content import COMMANDS, COMMAND_ERRORS
from database.handlers import CaseManager


class Softban(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(
        name=COMMANDS["softban"]["name"],
        description=COMMANDS["softban"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["softban"]["member"],
        reason=COMMANDS["softban"]["reason"]
    )
    async def softban(
        self,
        interaction: Interaction,
        member: Member,
        reason: str | None = None
    ):
        await interaction.response.defer()

        if not await check_permissions(interaction, "softban"):
            return
        
        if not await check_action_allowed(interaction, member, "softban"):
            return

        guild = interaction.guild

        try:
            await member.ban(
                reason=reason,
                delete_message_days=7
            )

            await guild.unban(
                Object(id=member.id),
                reason="Softban unban"
            )

        except Exception:
            return await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS["softban_failed_error"]["title"],
                    description=COMMAND_ERRORS["softban_failed_error"]["message"]
                )
            )

        manager = CaseManager(guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="softban",
            reason=reason
        )

        logger.info(
            f"{interaction.user.name} softbanned {member} from {guild.name} - Case #{case_id}"
        )

        description = f"`{member}` has been softbanned"

        if reason:
            description += f" for **{reason}**"

        await interaction.edit_original_response(
            embed=normal(
                author_name=f"softban [{case_id}]",
                author_icon_url=LOGO,
                description=description
            )
        )

        _log_embed = log_embed(
            author_name=f"softban [{case_id}]",
            fields=[
                ("user", f"{member} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", reason or "Not given.", False)
            ]
        )

        await send_log(interaction, _log_embed)
        await send_mod_dm(
            member,
            guild_name=interaction.guild.name,
            action="softban",
            case_id=case_id,
            moderator=interaction.user,
            reason=reason
        )    


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Softban(client))