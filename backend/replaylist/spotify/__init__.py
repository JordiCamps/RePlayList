"""Spotify client subpackage."""

from .types import SpotifyPlaylist, SpotifyTrack
from .client import SpotifyAPI

__all__ = ["SpotifyAPI", "SpotifyPlaylist", "SpotifyTrack"]


