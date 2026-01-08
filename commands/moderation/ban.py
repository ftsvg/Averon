from discord.ext import commands
from discord import app_commands, Interaction, Member, Forbidden, HTTPException

from core import check_permissions, check_action_allowed, send_log, send_mod_dm
from ui import create_embed
from logger import logger
from content import COMMANDS, ERRORS
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
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := (
            await check_permissions(interaction, "ban")
            or await check_action_allowed(interaction, member, "ban")
        ):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )                

        try:
            await member.ban(reason=reason)

        except (Forbidden, HTTPException):
            return await interaction.edit_original_response(
                content=ERRORS['interaction_error']
            )

        user = await interaction.client.fetch_user(member.id)
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

        msg = f"`[{case_id}]` **{member.name}** has been banned"

        if reason:
            msg += f" for **{reason}**"

        await interaction.edit_original_response(
            content=msg
        )

        embed = create_embed(
            author_name=f"ban [{case_id}]",
            fields=[
                ("user", f"{member.name} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", f"{reason if reason else 'Not given.'}", False)
            ],
            timestamp=True
        )

        await send_log(interaction, embed)
        await send_mod_dm(
            user,
            guild_name=interaction.guild.name,
            action="ban",
            case_id=case_id,
            moderator=interaction.user,
            reason=reason
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Ban(client))