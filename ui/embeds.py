from discord import Embed, Color

from core import MAIN_COLOR, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR


def base_embed(
    *,
    title: str | None = None,
    description: str | None = None,
    color: Color = MAIN_COLOR,
    thumbnail: str | None = None,
    footer: str | None = None
) -> Embed:
    embed = Embed(
        title=title,
        description=description,
        color=color
    )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if footer:
        embed.set_footer(text=footer)

    return embed


def success(
    *,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=SUCCESS_COLOR,
        thumbnail=thumbnail,
        footer=footer
    )


def error(
    *,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=ERROR_COLOR,
        thumbnail=thumbnail,
        footer=footer
    )


def warning(
    *,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=WARNING_COLOR,
        thumbnail=thumbnail,
        footer=footer
    )


def normal(
    *,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=MAIN_COLOR,
        thumbnail=thumbnail,
        footer=footer
    )
