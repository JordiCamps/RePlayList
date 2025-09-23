"""Spotify facade: re-export client and types for backward compatibility.

Usage:
    from replaylist.spotify import SpotifyAPI, SpotifyTrack

This module preserves the historical import path while delegating implementation
to the `replaylist.spotify` subpackage so internal structure can evolve without
breaking imports.
"""

from .spotify.client import SpotifyAPI
from .spotify.types import SpotifyPlaylist, SpotifyTrack

__all__ = ["SpotifyAPI", "SpotifyPlaylist", "SpotifyTrack"]


