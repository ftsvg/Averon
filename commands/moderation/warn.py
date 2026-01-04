from discord.ext import commands
from discord import app_commands, Interaction, Member

from core import check_permissions, check_action_allowed
from ui import success, error
from logger import logger
from content import COMMAND_ERRORS, COMMANDS
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
        await interaction.response.defer()

        if not await check_permissions(interaction, "warn"):
            return
        
        if not await check_action_allowed(interaction, member, "warn"):
            return          

        manager = CaseManager(interaction.guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type='warn',
            reason=reason
        ) 

        logger.info(
            f"{interaction.user.name} warned {member.name} in {interaction.guild.name} | Case #{case_id}"
        )

        await interaction.edit_original_response(
            embed=success(
                title=f"Warn #{case_id}",
                description=(
                    f"`{member.name}` has been warned by `{interaction.user.name}`.\n"
                )
            )
        ) 

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Warn(bot))