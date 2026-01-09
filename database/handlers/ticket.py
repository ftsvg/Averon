import time
from typing import Optional

from core.utils import generate_id
from database import Cursor, Ticket, ensure_cursor


class TicketManager:
    def __init__(self, guild_id: int) -> None:
        self._guild_id = guild_id


    @staticmethod
    def _ticket_id_exists(ticket_id: str, guild_id: int, *, cursor: Cursor) -> bool:
        cursor.execute(
            """
            SELECT 1 FROM tickets
            WHERE guild_id = %s AND ticket_id = %s
            LIMIT 1
            """,
            (guild_id, ticket_id)
        )
        return cursor.fetchone() is not None


    @staticmethod
    def _resolve_ticket_id(
        guild_id: int,
        *,
        cursor: Cursor
    ) -> str:
        while True:
            ticket_id = generate_id()
            if not TicketManager._ticket_id_exists(
                ticket_id=ticket_id,
                guild_id=guild_id,
                cursor=cursor
            ):
                return ticket_id


    @ensure_cursor
    def create_ticket(
        self,
        user_id: int,
        channel_id: int,
        reason: Optional[str] = None,
        *,
        cursor: Cursor = None
    ) -> str:
        created_at = int(time.time())

        ticket_id = self._resolve_ticket_id(
            guild_id=self._guild_id,
            cursor=cursor
        )

        cursor.execute(
            """
            INSERT INTO tickets
            (guild_id, ticket_id, user_id, reason, channel_id, closed, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                self._guild_id,
                ticket_id,
                user_id,
                reason,
                channel_id,
                False,
                created_at
            )
        )

        return ticket_id


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
                id, guild_id, ticket_id, user_id,
                reason, channel_id, closed, closed_by, created_at
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
                id, guild_id, ticket_id, user_id,
                reason, channel_id, closed, closed_by, created_at
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
    

    @ensure_cursor
    def get_ticket_by_id(
        self,
        ticket_id: int,
        *,
        cursor: Cursor = None
    ) -> Optional[Ticket]:
        cursor.execute(
            """
            SELECT
                id, guild_id, ticket_id, user_id,
                reason, channel_id, closed, closed_by, created_at
            FROM tickets
            WHERE guild_id = %s
            AND ticket_id = %s
            AND closed = %s
            LIMIT 1
            """,
            (self._guild_id, ticket_id, False)
        )

        row = cursor.fetchone()
        if not row:
            return None

        return Ticket(*row)