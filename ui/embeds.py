from discord import Embed, Color

from core import MAIN_COLOR, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR


def base_embed(
    *,
    title: str | None = None,
    description: str | None = None,
    color: Color = MAIN_COLOR
) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=color
    )


def success(
    title: str, 
    description: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=SUCCESS_COLOR
    )


def error(
    title: str, 
    description: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=ERROR_COLOR
    )


def warning(
    title: str, 
    description: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=WARNING_COLOR
    )


def normal(
    title: str, 
    description: str | None = None
) -> Embed:
    return base_embed(
        title=title,
        description=description,
        color=MAIN_COLOR
    )


