from discord.ext import commands
from discord import app_commands, Interaction, Object

from core import check_permissions, send_log
from ui import create_embed
from logger import logger
from content import COMMANDS, ERRORS
from database.handlers import CaseManager


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

        if error_key := await check_permissions(interaction, "ban"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )

        if not user_id.isdigit():
            return await interaction.edit_original_response(
                content=ERRORS['invalid_user_id_error']
            )

        guild = interaction.guild
        user = Object(id=int(user_id))

        try:
            await guild.unban(user, reason=reason)

        except Exception:
            return await interaction.edit_original_response(
                content=ERRORS['user_not_banned_error']
            )

        manager = CaseManager(guild.id)

        case_id = manager.create_case(
            user_id=user.id,
            moderator_id=interaction.user.id,
            case_type="unban",
            reason=reason
        )

        logger.info(
            f"{interaction.user.name} unbanned {user.id} from {guild.name} - Case #{case_id}"
        )

        msg = f"`[{case_id}]` **{user_id}** has been unbanned"

        if reason:
            msg += f" for **{reason}**"

        await interaction.edit_original_response(
            content=msg
        )

        embed = create_embed(
            author_name=f"unban [{case_id}]",
            fields=[
                ("user id", f"`{user.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", reason or "Not given.", False)
            ]
        )

        await send_log(interaction, embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Unban(client))