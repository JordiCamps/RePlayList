"""Playlist transfer logic between Spotify and YouTube."""

# Re-export everything from the transfer subpackage for backward compatibility
from .transfer import (
    PlaylistTransfer,
    TransferStatus,
    TransferProgress, 
    TransferResult,
    TrackMatcher,
    PlaylistManager,
    PlaylistNamer,
    TransferExecutor
)

__all__ = [
    "PlaylistTransfer",
    "TransferStatus",
    "TransferProgress", 
    "TransferResult",
    "TrackMatcher",
    "PlaylistManager",
    "PlaylistNamer",
    "TransferExecutor"
]