import time
from typing import Optional

from database import Cursor, Ticket, ensure_cursor


class TicketManager:
    def __init__(self, guild_id: int) -> None:
        self._guild_id = guild_id


    @ensure_cursor
    def create_ticket(
        self,
        user_id: int,
        channel_id: int,
        reason: Optional[str] = None,
        *,
        cursor: Cursor = None
    ) -> None:
        created_at = int(time.time())

        cursor.execute(
            """
            INSERT INTO tickets
            (guild_id, user_id, reason, channel_id, closed, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                self._guild_id,
                user_id,
                reason,
                channel_id,
                False,
                created_at
            )
        )


    @ensure_cursor
    def close_ticket(
        self,
        channel_id: int,
        closed_by: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            UPDATE tickets
            SET closed = %s, closed_by = %s
            WHERE guild_id = %s AND channel_id = %s
            """,
            (
                True,
                closed_by,
                self._guild_id,
                channel_id
            )
        )


    @ensure_cursor
    def get_ticket(
        self,
        channel_id: int,
        *,
        cursor: Cursor = None
    ) -> Optional[Ticket]:
        cursor.execute(
            """
            SELECT
                id, guild_id, user_id, reason,
                channel_id, closed, closed_by, created_at
            FROM tickets
            WHERE guild_id = %s AND channel_id = %s
            """,
            (self._guild_id, channel_id)
        )

        row = cursor.fetchone()
        if not row:
            return None

        return Ticket(*row)


    @ensure_cursor
    def delete_ticket(
        self,
        channel_id: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            DELETE FROM tickets
            WHERE guild_id = %s AND channel_id = %s
            """,
            (self._guild_id, channel_id)
        )


    @ensure_cursor
    def get_ticket_by_user(
        self,
        user_id: int,
        *,
        cursor: Cursor = None
    ) -> Optional[Ticket]:
        cursor.execute(
            """
            SELECT
                id, guild_id, user_id, reason,
                channel_id, closed, closed_by, created_at
            FROM tickets
            WHERE guild_id = %s
            AND user_id = %s
            AND closed = %s
            LIMIT 1
            """,
            (self._guild_id, user_id, False)
        )

        row = cursor.fetchone()
        if not row:
            return None

        return Ticket(*row)