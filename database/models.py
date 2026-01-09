from dataclasses import dataclass
from typing import Literal, Optional


LogLevel = Literal[
    'DEBUG', 
    'INFO', 
    'WARNING', 
    'ERROR', 
    'CRITICAL'
]


@dataclass(slots=True)
class Case:
    id: int
    guild_id: int
    case_id: str
    user_id: int
    moderator_id: int
    type: str
    reason: str
    created_at: int
    duration: Optional[int]
    expires_at: Optional[int]


@dataclass(slots=True)
class Ticket:
    id: int
    guild_id: int
    ticket_id: str
    user_id: int
    reason: str
    channel_id: int
    closed: bool
    closed_by: Optional[int]
    created_at: int


@dataclass(slots=True)
class TicketSettings:
    guild_id: int
    ticket_category_id: Optional[int]
    staff_role_id: Optional[int]
    transcripts_channel_id: Optional[int]


@dataclass(slots=True)
class VerificationSettings:
    guild_id: int
    role_id: Optional[int]
    logs_channel_id: Optional[int]
    captcha_enabled: bool


@dataclass(slots=True)
class LogEntry:
    id: Optional[int]
    guild_id: int
    log_id: str
    log_level: LogLevel
    log_description: str
    created_at: int