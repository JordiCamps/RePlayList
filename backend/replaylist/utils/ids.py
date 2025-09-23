"""ID and filename utilities."""

import uuid


def generate_transfer_id() -> str:
    """Generate a unique transfer identifier (UUID4 string)."""
    return str(uuid.uuid4())


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage.

    Replaces invalid characters with underscores and caps length at 255 bytes.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    return filename


