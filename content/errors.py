SETTINGS_ERRORS = {
    "missing_token": {
        "title": "Configuration error",
        "message": "TOKEN is not set in the environment variables."
    },
    "missing_database_credentials": {
        "title": "Configuration error",
        "message": "Database credentials are missing."
    }
}


COMMAND_ERRORS = {
    "interaction_error": {
        "title": "Execution error",
        "message": "Something went wrong while executing this command."
    },
    "permissions_error": {
        "title": "Permission denied",
        "message": "You do not have permission to use this command."
    },
    "punish_yourself_error": {
        "title": "Invalid target",
        "message": "You cannot peform this action on yourself."
    },
    "punish_bot_error": {
        "title": "Invalid target",
        "message": "You cannot peform this action on bots."
    },
    "permissions_role_error": {
        "title": "Action not allowed",
        "message": "You cannot perform this action on this user."
    },
    "permissions_bot_error": {
        "title": "Missing permissions",
        "message": "I do not have permission to perform this action."
    },
    "invalid_user_id_error": {
        "title": "Invalid user ID",
        "message": "Invalid user ID."
    },
    "user_not_banned_error": {
        "title": "User not banned",
        "message": "This user is not banned or the ID is invalid."
    },
    "not_timed_out_error": {
        "title": "User not timed out",
        "message": "This user is not currently timed out."
    },
    "invalid_user": {
        "title": "User not found",
        "message": "That user could not be found. Make sure they are in the server."
    },
    "already_timed_out": {
        "title": "Already timed out",
        "message": "That user is already timed out."
    },
    "case_not_found": {
        "title": "Case not found",
        "message": "No case was found with that ID."
    },
    "confirm_error": {
        "title": "Confirmation required",
        "message": "Please type `confirm` to confirm this action."
    },
    "no_cases_error": {
        "title": "No cases found",
        "message": "This user has no cases."
    },
    "ticket_config_not_set_error": {
        "title": "Ticket system not configured",
        "message": "Please make sure `/ticket channel`, `/ticket role` and `/ticket transcripts` are configured."
    },
    "ticket_not_found_error": {
        "title": "Ticket not found",
        "message": "No ticket was found for this thread."
    },
    "already_verified_error": {
        "title": "Already verified",
        "message": "You are already verified."
    },
    "verification_role_error": {
        "title": "Invalid verification role",
        "message": "The verification role is invalid. Please contact an administrator to reconfigure it."
    },
    "verification_config_not_set_error": {
        "title": "Verification not configured",
        "message": "Please make sure `/verification role` and `/verification logs` are configured."
    },
    "already_verifying_error": {
        "title": "Verification in progress",
        "message": "You are already verifying. Please complete that verification to verify again."
    },
    "captcha_expired_error": {
        "title": "Captcha expired",
        "message": "You took too long to respond. Please try again."
    },
    "invalid_captcha_code_error": {
        "title": "Incorrect captcha",
        "message": "The captcha you entered was incorrect. Please try again."
    }
}