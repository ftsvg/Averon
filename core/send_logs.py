from discord import Interaction, Embed

from database.handlers import ModerationManager
from logger import logger


async def send_log(
    interaction: Interaction,
    embed: Embed
) -> None:

    guild = interaction.guild
    if not guild:
        return

    settings = ModerationManager(guild.id)
    channel_id = settings.get_log_channel()

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        logger.warning(
            f"Log channel {channel_id} not found in guild {guild.id}"
        )
        return

    try:
        await channel.send(embed=embed)

    except Exception as exc:
        logger.error(
            f"Failed to send log in guild {guild.id}: {exc}"
        )