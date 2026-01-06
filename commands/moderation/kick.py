from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException

from core import check_permissions, check_action_allowed, send_log, send_mod_dm, LOGO
from ui import normal, log_embed, error
from logger import logger
from content import COMMANDS, COMMAND_ERRORS
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
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := (
            await check_permissions(interaction, "kick")
            or await check_action_allowed(interaction, member, "kick")
        ):
            data = COMMAND_ERRORS[error_key]
            return await interaction.edit_original_response(
                embed=error(
                    title=data["title"],
                    description=data["message"]
                )
            )  

        try: 
            await member.kick(reason=reason)

        except (Forbidden, HTTPException):
            return await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS["interaction_error"]["title"],
                    description=COMMAND_ERRORS["interaction_error"]["message"]
                )
            )

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