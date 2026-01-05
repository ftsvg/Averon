import time
import string
import secrets
from typing import Optional

from database import ensure_cursor, Cursor, Case


def generate_case_id(length: int = 6) -> str:
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class CaseManager:
    def __init__(self, guild_id: int) -> None:
        self._guild_id = guild_id


    @staticmethod
    def _case_id_exists(case_id: str, *, cursor: Cursor) -> bool:
        cursor.execute(
            "SELECT 1 FROM cases WHERE case_id = %s LIMIT 1",
            (case_id,)
        )
        return cursor.fetchone() is not None


    @staticmethod
    def _resolve_case_id(case_id: Optional[str], *, cursor: Cursor) -> str:
        if case_id and not CaseManager._case_id_exists(
            case_id=case_id,
            cursor=cursor
        ):
            return case_id

        while True:
            new_case_id = generate_case_id()
            if not CaseManager._case_id_exists(
                case_id=new_case_id,
                cursor=cursor
            ):
                return new_case_id
            

    @ensure_cursor
    def create_case(
        self,
        user_id: int,
        moderator_id: int,
        case_type: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None,
        _case_id: Optional[str] = None,
        *,
        cursor: Cursor = None
    ) -> str:
        created_at = int(time.time())
        expires_at = created_at + duration if duration else None

        case_id = self._resolve_case_id(
            _case_id,
            cursor=cursor
        )

        final_reason = reason if reason else "Not given."

        cursor.execute(
            """
            INSERT INTO cases
            (guild_id, case_id, user_id, moderator_id, type,
             reason, created_at, duration, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                self._guild_id,
                case_id,
                user_id,
                moderator_id,
                case_type,
                final_reason,
                created_at,
                duration,
                expires_at
            )
        )

        return case_id


    @ensure_cursor
    def delete_case(self, case_id: str, *, cursor: Cursor = None) -> None:
        cursor.execute(
            """
            DELETE FROM cases
            WHERE guild_id = %s AND case_id = %s
            """,
            (self._guild_id, case_id)
        )


    @ensure_cursor
    def get_case(self, case_id: str, *, cursor: Cursor = None) -> Optional[Case]:
        cursor.execute(
            """
            SELECT
                id, guild_id, case_id, user_id, moderator_id,
                type, reason, created_at, duration, expires_at
            FROM cases
            WHERE guild_id = %s AND case_id = %s
            """,
            (self._guild_id, case_id)
        )

        result = cursor.fetchone()
        if not result:
            return None

        return Case(*result)
    

    @ensure_cursor
    def update_reason(
        self,
        case_id: str,
        reason: str,
        *,
        cursor: Cursor = None
    ) -> None:
        final_reason = reason.strip() if reason else "Not given."

        cursor.execute(
            """
            UPDATE cases
            SET reason = %s
            WHERE guild_id = %s AND case_id = %s
            """,
            (final_reason, self._guild_id, case_id)
        )
