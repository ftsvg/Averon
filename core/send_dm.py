from discord import Member, User, Forbidden, HTTPException
from logger import logger
from ui import create_embed


_ACTION_PAST = {
    "warn": "warned",
    "ban": "banned",
    "timeout": "timed out",
    "kick": "kicked",
    "softban": "softbanned"
}


async def send_mod_dm(
    member: User | Member,
    *,
    guild_name: str,
    action: str,
    case_id: str,
    moderator: Member,
    reason: str | None = None,
    duration: str | None = None
) -> None:
    
    past_action = _ACTION_PAST.get(action, action)
    content = f"You have been *{past_action}* in **{guild_name}**."

    fields = [
        ("user", f"{member.name} `{member.id}`", True),
        ("moderator", f"{moderator.name} `{moderator.id}`", True),
    ]

    if duration:
        fields.append(("duration", duration, False))

    fields.append(("reason", reason or "Not given.", False))

    embed = create_embed(
        author_name=f"{action} [{case_id}]",
        fields=fields
    )

    try:
        await member.send(
            content=content,
            embed=embed
        )

    except (Forbidden, HTTPException):
        return

    except Exception as exc:
        logger.error(f"Failed to send DM to user {member.id}: {exc}")