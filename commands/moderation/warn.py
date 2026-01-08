from discord.ext import commands
from discord import app_commands, Interaction, Member

from core import check_permissions, check_action_allowed, send_log, send_mod_dm
from ui import create_embed
from logger import logger
from content import COMMANDS, ERRORS
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
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
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

        msg = f"`[{case_id}]` **{member.name}** has been warned"

        if reason:
            msg += f" for **{reason}**"

        await interaction.edit_original_response(
            content=msg
        )

        embed = create_embed(
            author_name=f"warn [{case_id}]",
            fields=[
                ("user", f"{member.name} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", f"{reason if reason else 'Not given.'}", False)
            ]
        )

        await send_log(interaction, embed)
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