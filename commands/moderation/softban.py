import traceback
from discord.ext import commands
from discord import app_commands, Interaction, Member, Object

from core import check_permissions, check_action_allowed, send_moderation_log, send_user_dm
from ui import create_embed
from content import COMMANDS, ERRORS
from database.handlers import CaseManager, LoggingManager


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
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := (
            await check_permissions(interaction, "softban")
            or await check_action_allowed(interaction, member, "softban")
        ):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to softban "
                f"{member} ({member.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

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
            error_id = logging_manager.create_log(
                'ERROR',
                traceback.format_exc()
            )
            return await interaction.edit_original_response(
                content=f"{ERRORS['interaction_error']}\n-# log id: {error_id}"
            )

        manager = CaseManager(guild.id)

        case_id = manager.create_case(
            user_id=member.id,
            moderator_id=interaction.user.id,
            case_type="softban",
            reason=reason
        )

        logging_manager.create_log(
            'INFO',
            f"Softban executed: {interaction.user} ({interaction.user.id}) softbanned "
            f"{member} ({member.id}) in {guild.name} (Case ID: {case_id})"
        )

        message = f"`[{case_id}]` **{member.name}** has been softbanned"
        if reason:
            message += f" for **{reason}**"

        await interaction.edit_original_response(
            content=message
        )

        embed = create_embed(
            author_name=f"softban [{case_id}]",
            fields=[
                ("User", f"{member.name} `{member.id}`", True),
                ("Moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("Reason", reason or "Not given.", False)
            ],
            timestamp=True
        )

        await send_moderation_log(interaction, embed)
        await send_user_dm(
            interaction, 
            member, 
            embed=embed, 
            content=f"You have been *softbanned* from **{interaction.guild.name}**."
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Softban(client))