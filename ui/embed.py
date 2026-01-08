from datetime import datetime, timezone
from discord import Embed

from core import MAIN_COLOR, LOGO


def create_embed(
    *,
    author_name: str | None = None,
    author_icon_url: str | None = LOGO,
    title: str | None = None,
    description: str | None = None,
    color: int | None = MAIN_COLOR,
    fields: list[tuple[str, str, bool]] | None = None,
    thumbnail: str | None = None,
    image: str | None = None,
    footer: str | None = None,
    footer_url: str | None = None,
    timestamp: bool = False
) -> Embed:

    embed = Embed(
        title=title,
        description=description,
        color=color
    )

    if author_name or author_icon_url:
        embed.set_author(name=author_name, icon_url=author_icon_url)

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if image:
        embed.set_image(url=image)

    if footer or footer_url:
        embed.set_footer(text=footer, icon_url=footer_url)

    if timestamp:
        embed.timestamp = datetime.now(timezone.utc)

    return embed