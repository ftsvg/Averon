from dataclasses import dataclass
from typing import Optional


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