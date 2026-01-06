from discord.ext import commands
from discord import app_commands, Interaction, Member

from core import check_permissions, check_action_allowed, send_log, send_mod_dm, LOGO
from ui import normal, log_embed, error
from logger import logger
from content import COMMANDS, COMMAND_ERRORS
from database.handlers import CaseManager


class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @app_commands.command(
        name=COMMANDS["warn"]["name"], 
        description=COMMANDS["warn"]['description']
    )
    @app_commands.describe(
        member=COMMANDS["warn"]['member'],
        reason=COMMANDS["warn"]['reason']
    )
    async def warn(
        self, 
        interaction: Interaction,
        member: Member,
        reason: str | None = None
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := (
            await check_permissions(interaction, "warn")
            or await check_action_allowed(interaction, member, "warn")
        ):
            data = COMMAND_ERRORS[error_key]
            return await interaction.edit_original_response(
                embed=error(
                    title=data["title"],
                    description=data["message"]
                )
            )         

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type='warn',
            reason=reason
        ) 

        logger.info(
            f"{interaction.user.name} warned {member.name} in {interaction.guild.name} - Case #{case_id}"
        )

        description = f"`{member.name}` has been warned"

        if reason:
            description += f" for **{reason}**"

        await interaction.edit_original_response(
            embed=normal(
                author_name=f"warn [{case_id}]",
                author_icon_url=LOGO,
                description=description
            )
        )

        _log_embed = log_embed(
            author_name=f"warn [{case_id}]",
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
            action="warn",
            case_id=case_id,
            moderator=interaction.user,
            reason=reason
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Warn(bot))    