import time
import string
import secrets
from typing import Optional

from database import ensure_cursor, Cursor, Case


def generate_case_id(length: int = 10) -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class CaseManager:
    @staticmethod
    def _case_id_exists(case_id: str, *, cursor: Cursor) -> bool:
        cursor.execute(
            "SELECT 1 FROM cases WHERE case_id = %s LIMIT 1", (case_id,)
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


    @staticmethod
    @ensure_cursor
    def create_case(
        guild_id: int,
        user_id: int,
        moderator_id: int,
        case_type: str,
        duration: Optional[int] = None,
        _case_id: Optional[str] = None,
        *,
        cursor: Cursor = None
    ) -> str:
        created_at = int(time.time())
        expires_at = created_at + duration if duration else None

        case_id = CaseManager._resolve_case_id(
            _case_id,
            cursor=cursor
        )

        cursor.execute(
            """
            INSERT INTO cases
            (guild_id, case_id, user_id, moderator_id, type, created_at, duration, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                guild_id,
                case_id,
                user_id,
                moderator_id,
                case_type,
                created_at,
                duration,
                expires_at
            )
        )

        return case_id


    @staticmethod
    @ensure_cursor
    def delete_case(case_id: str, *, cursor: Cursor = None) -> None:
        cursor.execute(
            "DELETE FROM cases WHERE case_id = %s", (case_id,)
        )


    @staticmethod
    @ensure_cursor
    def get_case(case_id: str, *, cursor: Cursor = None) -> Optional[Case]:
        cursor.execute(
            """
            SELECT 
                id, guild_id, case_id, user_id, moderator_id, type, created_at, duration, expires_at
            FROM cases
            HERE case_id = %s
            """,
            (case_id,)
        )

        result = cursor.fetchone()
        if not result:
            return None

        return Case(*result)