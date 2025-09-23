"""Formatting helpers for durations and byte sizes."""


def format_duration(seconds: int) -> str:
    if seconds < 0:
        return "0:00"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    value = float(size_bytes)
    while value >= 1024 and i < len(size_names) - 1:
        value /= 1024.0
        i += 1
    return f"{value:.1f} {size_names[i]}"


