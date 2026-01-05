def format_duration(seconds: int) -> str:
    units = [
        ("week", 604800),
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]

    parts = []

    for name, unit_seconds in units:
        value, seconds = divmod(seconds, unit_seconds)
        if value:
            parts.append(f"{value} {name}{'s' if value != 1 else ''}")

    return ", ".join(parts) if parts else "0 seconds"