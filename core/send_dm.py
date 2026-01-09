import traceback

from discord import Embed, Forbidden, HTTPException, Interaction, Member, User

from database.handlers import LoggingManager


async def send_user_dm(
    interaction: Interaction,
    member: User | Member,
    *,
    content: str | None = None,
    embed: Embed | None = None
) -> None:
    guild = interaction.guild
    if not guild:
        return

    logging_manager = LoggingManager(guild.id)

    try:
        await member.send(
            content=content,
            embed=embed
        )

        logging_manager.create_log(
            'INFO', f"DM sent to {member} ({member.id}) in guild {guild.id}"
        )

    except (Forbidden, HTTPException):
        logging_manager.create_log(
            'WARNING', f"Failed to send DM to {member} ({member.id}) in guild {guild.id}: DMs disabled or blocked"
        )
        return

    except Exception:
        logging_manager.create_log(
            'ERROR',
            traceback.format_exc()
        )