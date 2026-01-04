from discord import Interaction

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
    
    required_perms = PERMISSION_MAP.get(category)
    permissions = interaction.user.guild_permissions

    missing = [
        perm for perm in required_perms if not getattr(permissions, perm, False)
    ]

    if missing:
        embed = error_embed(
            COMMAND_ERRORS["permissions_error"]["title"],
            COMMAND_ERRORS["permissions_error"]["message"]
        )
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)

        return False

    return True