from typing import Optional

from database import Cursor, VerificationSettings, ensure_cursor


class VerificationManager:
    def __init__(self, guild_id: int) -> None:
        self._guild_id = guild_id

    @ensure_cursor
    def set_role(
        self,
        role_id: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            INSERT INTO verification (guild_id, role_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)
            """,
            (self._guild_id, role_id)
        )


    @ensure_cursor
    def set_logs_channel(
        self,
        channel_id: int,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            INSERT INTO verification (guild_id, logs_channel_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE logs_channel_id = VALUES(logs_channel_id)
            """,
            (self._guild_id, channel_id)
        )


    @ensure_cursor
    def set_captcha_enabled(
        self,
        enabled: bool,
        *,
        cursor: Cursor = None
    ) -> None:
        cursor.execute(
            """
            INSERT INTO verification (guild_id, captcha_enabled)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE captcha_enabled = VALUES(captcha_enabled)
            """,
            (self._guild_id, enabled)
        )


    @ensure_cursor
    def get_settings(
        self,
        *,
        cursor: Cursor = None
    ) -> Optional[VerificationSettings]:
        cursor.execute(
            """
            SELECT
                guild_id,
                role_id,
                logs_channel_id,
                captcha_enabled
            FROM verification
            WHERE guild_id = %s
            """,
            (self._guild_id,)
        )

        row = cursor.fetchone()
        if not row:
            return None

        return VerificationSettings(*row)
