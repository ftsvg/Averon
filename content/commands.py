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
    "logs": {
        "name": "logs",
        "description": "Set the moderation log channel",
        "channel": "Channel where moderation logs will be sent",
    }
}