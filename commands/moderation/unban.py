import traceback
from discord.ext import commands
from discord import app_commands, Interaction, Object

from core import check_permissions, send_moderation_log
from ui import create_embed
from content import COMMANDS, ERRORS
from database.handlers import CaseManager, LoggingManager


class Unban(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    @app_commands.command(
        name=COMMANDS["unban"]["name"],
        description=COMMANDS["unban"]["description"]
    )
    @app_commands.describe(
        user_id=COMMANDS["unban"]["user_id"],
        reason=COMMANDS["unban"]["reason"]
    )
    async def unban(
        self,
        interaction: Interaction,
        user_id: str,
        reason: str | None = None
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "ban"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to unban user ID {user_id}"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        if not user_id.isdigit():
            error_id = logging_manager.create_log(
                'ERROR',
                f"Invalid user ID supplied for unban: '{user_id}' "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.edit_original_response(
                content=f"{ERRORS['invalid_user_id_error']}"
            )

        guild = interaction.guild
        user = Object(id=int(user_id))

        try:
            await guild.unban(user, reason=reason)

        except Exception:
            error_id = logging_manager.create_log(
                'ERROR',
                traceback.format_exc()
            )
            return await interaction.edit_original_response(
                content=f"{ERRORS['user_not_banned_error']}\n-# log id: {error_id}"
            )

        manager = CaseManager(guild.id)

        case_id = manager.create_case(
            user_id=user.id,
            moderator_id=interaction.user.id,
            case_type="unban",
            reason=reason
        )

        logging_manager.create_log(
            'INFO',
            f"Unban executed: {interaction.user} ({interaction.user.id}) unbanned "
            f"user ID {user.id} in {guild.name} (Case ID: {case_id})"
        )

        message = f"`[{case_id}]` **{user.id}** has been unbanned"
        if reason:
            message += f" for **{reason}**"

        await interaction.edit_original_response(
            content=message
        )

        embed = create_embed(
            author_name=f"unban [{case_id}]",
            fields=[
                ("User ID", f"`{user.id}`", True),
                ("Moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("Reason", reason or "Not given.", False)
            ]
        )

        await send_moderation_log(interaction, embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Unban(client))