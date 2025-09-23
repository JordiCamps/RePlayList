"""RePlayList - Transfer playlists between Spotify and YouTube."""

__version__ = "1.0.0"
__author__ = "RePlayList Team"
__description__ = "A cross-platform desktop application for transferring playlists between Spotify and YouTube"

from .config import config, Config, SpotifyConfig, YouTubeConfig, AppConfig
from .auth import auth_manager, AuthResult, SpotifyAuth, YouTubeAuth, AuthManager
from .spotify import SpotifyAPI, SpotifyTrack, SpotifyPlaylist
from .youtube import YouTubeAPI, YouTubeVideo, YouTubePlaylist
from .transfer import PlaylistTransfer, TransferStatus, TransferProgress, TransferResult
from .utils import (
    setup_logging, generate_transfer_id, sanitize_filename,
    normalize_track_title, normalize_artist_name, calculate_similarity,
    format_duration, format_file_size, create_error_response, create_success_response,
    validate_playlist_id, chunk_list, retry_on_exception
)

__all__ = [
    # Version info
    "__version__", "__author__", "__description__",
    
    # Config
    "config", "Config", "SpotifyConfig", "YouTubeConfig", "AppConfig",
    
    # Auth
    "auth_manager", "AuthResult", "SpotifyAuth", "YouTubeAuth", "AuthManager",
    
    # Spotify
    "SpotifyAPI", "SpotifyTrack", "SpotifyPlaylist",
    
    # YouTube
    "YouTubeAPI", "YouTubeVideo", "YouTubePlaylist",
    
    # Transfer
    "PlaylistTransfer", "TransferStatus", "TransferProgress", "TransferResult",
    
    # Utils
    "setup_logging", "generate_transfer_id", "sanitize_filename",
    "normalize_track_title", "normalize_artist_name", "calculate_similarity",
    "format_duration", "format_file_size", "create_error_response", "create_success_response",
    "validate_playlist_id", "chunk_list", "retry_on_exception"
]
