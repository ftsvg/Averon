from discord import Interaction, Member


PERMISSION_MAP = {
    "ban": ["ban_members"],
    "kick": ["kick_members"],
    "timeout": ["moderate_members"],
    "warn": ["manage_messages"],
    "purge": ["manage_messages"],
    "admin": ["administrator"],
    "other": ["manage_messages"]
}


async def check_permissions(
    interaction: Interaction,
    category: str
) -> str | None:
    required_perms = PERMISSION_MAP.get(category, [])
    permissions = interaction.user.guild_permissions

    for perm in required_perms:
        if not getattr(permissions, perm, False):
            return "permissions_error"

    return None


async def check_action_allowed(
    interaction: Interaction,
    target: Member,
    action: str
) -> str | None:
    guild = interaction.guild
    moderator = interaction.user

    if not guild or not guild.me:
        return "interaction_error"

    if target.id == moderator.id:
        return "punish_yourself_error"

    if target.bot:
        return "punish_bot_error"

    if target.top_role >= moderator.top_role:
        return "permissions_role_error"

    required_perms = PERMISSION_MAP.get(action, [])
    if required_perms:
        perm = required_perms[0]
        if not getattr(guild.me.guild_permissions, perm, False):
            return "permissions_bot_error"

    return None