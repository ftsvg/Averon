from datetime import datetime, timezone
from discord import Embed

from core import MAIN_COLOR, LOGO


def log_embed(
    *,
    author_name: str,
    description: str | None = None,
    fields: list[tuple[str, str, bool]] | None = None,
    thumbnail: str | None = None
) -> Embed:
    embed = Embed(
        description=description,
        color=MAIN_COLOR,
        timestamp=datetime.now(timezone.utc)
    )

    embed.set_author(
        name=author_name,
        icon_url=LOGO
    )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if fields:
        for name, value, inline in fields:
            embed.add_field(
                name=name,
                value=value,
                inline=inline
            )

    return embed
