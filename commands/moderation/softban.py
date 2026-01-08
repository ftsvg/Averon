from discord.ext import commands
from discord import app_commands, Interaction, Member, Object

from core import check_permissions, check_action_allowed, send_log, send_mod_dm
from ui import create_embed
from logger import logger
from content import COMMANDS, ERRORS
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
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := (
            await check_permissions(interaction, "softban")
            or await check_action_allowed(interaction, member, "softban")
        ):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
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
            return await interaction.edit_original_response(
                content=ERRORS['interaction_error']
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

        msg = f"`[{case_id}]` **{member.name}** has been softbanned"

        if reason:
            msg += f" for **{reason}**"

        await interaction.edit_original_response(
            content=msg
        )

        embed = create_embed(
            author_name=f"softban [{case_id}]",
            fields=[
                ("user", f"{member} `{member.id}`", True),
                ("moderator", f"{interaction.user.name} `{interaction.user.id}`", True),
                ("reason", reason or "Not given.", False)
            ],
            timestamp=True
        )

        await send_log(interaction, embed)
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