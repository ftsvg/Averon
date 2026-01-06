from typing import Optional

from database import ensure_cursor, Cursor, TicketSettings


class TicketSettingsManager:
    def __init__(self, guild_id: int) -> None:
        self._guild_id = guild_id

    @ensure_cursor
    def set_ticket_channel(
        self,
        channel_id: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            INSERT INTO ticket_settings (guild_id, ticket_channel_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE ticket_channel_id = VALUES(ticket_channel_id)
            """,
            (self._guild_id, channel_id)
        )


    @ensure_cursor
    def set_staff_role(
        self,
        role_id: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            INSERT INTO ticket_settings (guild_id, staff_role_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE staff_role_id = VALUES(staff_role_id)
            """,
            (self._guild_id, role_id)
        )


    @ensure_cursor
    def set_transcripts_channel(
        self,
        channel_id: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            INSERT INTO ticket_settings (guild_id, transcripts_channel_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE transcripts_channel_id = VALUES(transcripts_channel_id)
            """,
            (self._guild_id, channel_id)
        )


    @ensure_cursor
    def get_settings(
        self,
        *,
        cursor: Cursor = None
    ) -> Optional[TicketSettings]:
        cursor.execute(
            """
            SELECT
                guild_id,
                ticket_channel_id,
                staff_role_id,
                transcripts_channel_id
            FROM ticket_settings
            WHERE guild_id = %s
            """,
            (self._guild_id,)
        )

        row = cursor.fetchone()
        if not row:
            return None

        return TicketSettings(*row)