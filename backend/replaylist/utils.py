"""Utils facade: re-export helpers from the utils subpackage for compatibility."""

# Re-export everything from the utils subpackage for backward compatibility
from .utils import (
    setup_logging,
    generate_transfer_id,
    sanitize_filename,
    normalize_track_title,
    normalize_artist_name,
    calculate_similarity,
    format_duration,
    format_file_size,
    create_error_response,
    create_success_response,
    validate_playlist_id,
    validate_track_metadata,
    validate_playlist_metadata,
    retry_on_exception,
    rate_limit,
    handle_api_errors,
    chunk_list,
    is_duplicate_track,
)

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