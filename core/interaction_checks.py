from discord import Interaction, Member, Embed

from ui import error as error_embed
from content import COMMAND_ERRORS


PERMISSION_MAP = {
    "ban": ["ban_members"],
    "kick": ["kick_members"],
    "timeout": ["moderate_members"],
    "warn": ["manage_messages"],
}


async def check_permissions(
    interaction: Interaction,
    category: str
) -> bool:
    required_perms = PERMISSION_MAP.get(category, [])
    permissions = interaction.user.guild_permissions

    missing = [
        perm for perm in required_perms
        if not getattr(permissions, perm, False)
    ]

    if missing:
        await _send_message(
            interaction, COMMAND_ERRORS["permissions_error"]
        )
        return False

    return True


async def check_action_allowed(
    interaction: Interaction,
    target: Member,
    action: str
) -> bool:
    
    moderator = interaction.user
    guild = interaction.guild
    bot = guild.me if guild else None

    if not guild or not bot:
        return False

    if target.id == moderator.id:
        await _send_message(
            interaction, COMMAND_ERRORS["punish_yourself_error"]
        )
        return False

    if target.bot:
        await _send_message(
            interaction, COMMAND_ERRORS["punish_bot_error"]
        )
        return False

    if target.top_role >= moderator.top_role:
        await _send_message(
            interaction, COMMAND_ERRORS["permissions_role_error"]
        )
        return False

    required_perms = PERMISSION_MAP.get(action, [])
    if required_perms:
        perm = required_perms[0]
        if not getattr(bot.guild_permissions, perm, False):
            await _send_message(
                interaction, COMMAND_ERRORS["permissions_bot_error"]
            )
            return False

    return True


async def _send_message(
    interaction: Interaction,
    data
):
    if isinstance(data, Embed):
        embed = data
    else:
        embed = error_embed(
            title=data["title"],
            description=data["message"]
        )

    if interaction.response.is_done():
        await interaction.edit_original_response(embed=embed)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)