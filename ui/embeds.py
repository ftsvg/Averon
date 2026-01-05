from discord import Embed, Color

from core import MAIN_COLOR, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR


def base_embed(
    *,
    title: str | None = None,
    description: str | None = None,
    color: Color = MAIN_COLOR,
    thumbnail: str | None = None,
    footer: str | None = None,
    author_name: str | None = None,
    author_icon_url: str | None = None
) -> Embed:
    embed = Embed(
        title=title,
        description=description,
        color=color
    )

    if author_name:
        embed.set_author(
            name=author_name,
            icon_url=author_icon_url
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
    footer: str | None = None,
    author_name: str | None = None,
    author_icon_url: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=SUCCESS_COLOR,
        thumbnail=thumbnail,
        footer=footer,
        author_name=author_name,
        author_icon_url=author_icon_url
    )


def error(
    *,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None,
    author_name: str | None = None,
    author_icon_url: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=ERROR_COLOR,
        thumbnail=thumbnail,
        footer=footer,
        author_name=author_name,
        author_icon_url=author_icon_url
    )


def warning(
    *,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None,
    author_name: str | None = None,
    author_icon_url: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=WARNING_COLOR,
        thumbnail=thumbnail,
        footer=footer,
        author_name=author_name,
        author_icon_url=author_icon_url
    )


def normal(
    *,
    title: str | None = None,
    description: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None,
    author_name: str | None = None,
    author_icon_url: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=MAIN_COLOR,
        thumbnail=thumbnail,
        footer=footer,
        author_name=author_name,
        author_icon_url=author_icon_url
    )