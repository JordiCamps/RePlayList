"""Typed configuration models for RePlayList."""

from dataclasses import dataclass


@dataclass
class SpotifyConfig:
    """Spotify API configuration.

    Attributes:
        client_id: OAuth client ID.
        client_secret: OAuth client secret.
        redirect_uri: Loopback redirect URI used in the OAuth flow.
    """

    client_id: str
    client_secret: str
    redirect_uri: str


@dataclass
class YouTubeConfig:
    """YouTube API configuration.

    Attributes are analogous to `SpotifyConfig`.
    """

    client_id: str
    client_secret: str
    redirect_uri: str


@dataclass
class AppConfig:
    """Application-level configuration values.

    Attributes:
        debug: Enable verbose logging and debugging aids.
        default_transfer_mode: Initial transfer mode preference.
        http_port: Port for local HTTP server.
        log_level: Logging verbosity string (e.g., INFO, DEBUG).
    """

    debug: bool
    default_transfer_mode: str
    http_port: int
    log_level: str


