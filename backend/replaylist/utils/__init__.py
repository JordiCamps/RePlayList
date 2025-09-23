"""Utility subpackage exports for RePlayList.

Groups helpers by concern while exposing a flat import surface for convenience.
"""

from .logging import setup_logging
from .ids import generate_transfer_id, sanitize_filename
from .text import normalize_track_title, normalize_artist_name, calculate_similarity
from .format import format_duration, format_file_size
from .api import create_error_response, create_success_response
from .validate import (
    validate_playlist_id,
    validate_track_metadata,
    validate_playlist_metadata,
)
from .decorators import retry_on_exception, rate_limit, handle_api_errors
from .collections import chunk_list
from .dupes import is_duplicate_track

__all__ = [
    "setup_logging",
    "generate_transfer_id",
    "sanitize_filename",
    "normalize_track_title",
    "normalize_artist_name",
    "calculate_similarity",
    "format_duration",
    "format_file_size",
    "create_error_response",
    "create_success_response",
    "validate_playlist_id",
    "validate_track_metadata",
    "validate_playlist_metadata",
    "retry_on_exception",
    "rate_limit",
    "handle_api_errors",
    "chunk_list",
    "is_duplicate_track",
]


