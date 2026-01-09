import time
from typing import Optional

from core.utils import generate_id
from database import Cursor, LogEntry, LogLevel, ensure_cursor
from logger import logger


class LoggingManager:
    def __init__(self, guild_id: int) -> None:
        self._guild_id = guild_id


    @staticmethod
    def _log_id_exists(log_id: str, *, cursor: Cursor) -> bool:
        cursor.execute(
            "SELECT 1 FROM logging WHERE log_id = %s LIMIT 1",
            (log_id,)
        )
        return cursor.fetchone() is not None

    @staticmethod
    def _resolve_log_id(log_id: Optional[str], *, cursor: Cursor) -> str:
        if log_id and not LoggingManager._log_id_exists(
            log_id=log_id,
            cursor=cursor
        ):
            return log_id

        while True:
            new_log_id = generate_id(length=16)
            if not LoggingManager._log_id_exists(
                log_id=new_log_id,
                cursor=cursor
            ):
                return new_log_id
            

    @staticmethod
    def _emit_to_logger(level: LogLevel, message: str) -> None:
        match level:
            case 'DEBUG':
                logger.debug(message)
            case 'INFO':
                logger.info(message)
            case 'WARNING':
                logger.warning(message)
            case 'ERROR':
                logger.error(message)
            case 'CRITICAL':
                logger.critical(message)
            case _:
                logger.info(message)


    @ensure_cursor
    def create_log(
        self,
        log_level: LogLevel,
        log_description: str,
        _log_id: Optional[str] = None,
        *,
        cursor: Cursor = None
    ) -> str:
        created_at = int(time.time())

        log_id = self._resolve_log_id(
            _log_id,
            cursor=cursor
        )

        self._emit_to_logger(log_level, log_description)

        cursor.execute(
            """
            INSERT INTO logging
            (guild_id, log_id, log_level, log_description, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                self._guild_id,
                log_id,
                log_level,
                log_description,
                created_at
            )
        )

        return log_id


    @ensure_cursor
    def get_log(
        self,
        log_id: str,
        *,
        cursor: Cursor = None
    ) -> Optional[LogEntry]:
        cursor.execute(
            """
            SELECT
                id,
                guild_id,
                log_id,
                log_level,
                log_description,
                created_at
            FROM logging
            WHERE guild_id = %s AND log_id = %s
            """,
            (self._guild_id, log_id)
        )

        result = cursor.fetchone()
        if not result:
            return None

        return LogEntry(*result)