COMMANDS = {
    "warn": {
        "name": "warn",
        "description": "Warn a user",
        "member": "The user to warn",
        "reason": "Reason for the warning"
    },
    "kick": {
        "name": "kick",
        "description": "Kick a user",
        "member": "The user to kick",
        "reason": "Reason for the kick"
    },
    "ban": {
        "name": "ban",
        "description": "Ban a user",
        "member": "The user to ban",
        "reason": "Reason for the ban"
    },
    "unban": {
        "name": "unban",
        "description": "Unban a user",
        "user_id": "The id of the user you want to unban",
        "reason": "Reason for the unban"
    },
    "softban": {
        "name": "softban",
        "description": "Softban a user (kick + delete messages)",
        "member": "User to softban",
        "reason": "Reason for the softban"
    },
    "timeout": {
        "name": "timeout",
        "description": "Timeout a user",
        "member": "User to timeout",
        "duration": "Timeout duration",
        "reason": "Reason for the timeout"
    },
    "untimeout": {
        "name": "untimeout",
        "description": "Remove an active timeout from a user",
        "member": "The user to remove the timeout from",
        "reason": "Reason for removing the timeout"
    },
    "logs": {
        "name": "logs",
        "description": "Set the moderation log channel",
        "channel": "Channel where moderation logs will be sent",
    },
    "purge": {
        "name": "purge",
        "description": "Delete a number of messages from the current channel",
        "amount": "Number of messages to delete (1-100)"
    },
    "case_view": {
        "name": "view",
        "description": "View a moderation case",
        "case_id": "The ID of the case to view"
    },
    "case_delete": {
        "name": "delete",
        "description": "Delete a moderation case",
        "case_id": "The ID of the case to delete"
    },
    "case_clear": {
        "name": "clear",
        "description": "Clear a user's case history",
        "member": "The user whose case history will be cleared"
    },
    "case_history": {
        "name": "history",
        "description": "View a user's case history",
        "member": "The user you want to view"
    },
    "ticket_panel": {
        "name": "panel",
        "description": "Sends a panel to the specified channel",
        "channel": "The channel to send the panel to"
    },
    "ticket_channel": {
        "name": "channel",
        "description": "Setup ticket channel",
        "channel": "The channel where tickets get created"
    },
    "ticket_role": {
        "name": "role",
        "description": "Setup ticket staff role",
        "role": "The staff role for ticket access"
    },
    "ticket_transcripts": {
        "name": "transcripts",
        "description": "Setup ticket transcripts channel",
        "channel": "The channel where ticket transcripts will be sent"
    },
    "ticket_close": {
        "name": "close",
        "description": "Close an active ticket",
        "channel": "The ticket thread you want to close"
    },
    "verification_role": {
        "name": "role",
        "description": "Setup verification role",
        "role": "The role given after verification"
    },
    "verification_channel": {
        "name": "logs",
        "description": "Setup verification logs channel",
        "channel": "The channel where verification logs will be sent"
    },
    "verification_captcha": {
        "name": "captcha",
        "description": "Enable or disable verification captcha",
        "enable": "Whether captcha verification is enabled"
    },
    "verification_panel": {
        "name": "panel",
        "description": "Sends a verification panel to the specified channel",
        "channel": "The channel to send the panel to"
    },
}