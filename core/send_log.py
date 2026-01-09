import traceback

from discord import Embed, Interaction

from database import TicketSettings
from database.handlers import LoggingManager, ModerationManager, TicketSettingsManager



async def send_moderation_log(
    interaction: Interaction,
    embed: Embed
) -> None:
    
    guild = interaction.guild
    if not guild:
        return

    logging_manager = LoggingManager(guild.id)

    settings = ModerationManager(guild.id)
    channel_id = settings.get_log_channel()

    if not channel_id:
        logging_manager.create_log(
            'WARNING',
            f"Moderation log channel not configured for guild {guild.id}"
        )
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        logging_manager.create_log(
            'ERROR',
            f"Configured moderation log channel {channel_id} does not exist in guild {guild.id}"
        )
        return

    try:
        await channel.send(embed=embed)

    except Exception:
        logging_manager.create_log(
            'ERROR', traceback.format_exc()
        )


async def send_transcript_log(
    interaction: Interaction,
    embed: Embed
) -> None:
    
    guild = interaction.guild
    if not guild:
        return

    logging_manager = LoggingManager(guild.id)

    settings: TicketSettings = TicketSettingsManager(guild.id).get_settings()

    channel_id = settings.transcripts_channel_id

    if not channel_id:
        logging_manager.create_log(
            'WARNING',
            f"Transcript channel not configured for guild {guild.id}"
        )
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        logging_manager.create_log(
            'ERROR',
            f"Transcript channel {channel_id} does not exist in guild {guild.id}"
        )
        return

    try:
        await channel.send(embed=embed)

    except Exception:
        logging_manager.create_log(
            'ERROR', traceback.format_exc()
        )