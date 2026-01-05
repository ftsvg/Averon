from database import ensure_cursor, Cursor


class ModerationManager:
    def __init__(self, guild_id: int):
        self._guild_id = guild_id

    @ensure_cursor
    def get_log_channel(
        self,
        *,
        cursor: Cursor = None
    ) -> int | None:
        cursor.execute(
            """
            SELECT log_channel_id
            FROM moderation_settings
            WHERE guild_id = %s
            """,
            (self._guild_id,)
        )

        row = cursor.fetchone()
        return row[0] if row else None


    @ensure_cursor
    def set_log_channel(
        self,
        channel_id: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            INSERT INTO moderation_settings (guild_id, log_channel_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                log_channel_id = VALUES(log_channel_id)
            """,
            (self._guild_id, channel_id)
        )