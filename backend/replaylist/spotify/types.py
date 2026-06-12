"""Data types for Spotify domain used by RePlayList.

These dataclasses model the subset of Spotify entities the app needs and help
decouple the rest of the codebase from raw Web API responses.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SpotifyTrack:
    """Simplified representation of a Spotify track used in the app.

    Attributes:
        id: Unique Spotify track ID.
        name: Track title as displayed by Spotify.
        artists: Ordered list of artist names.
        album: Album name containing the track.
        duration_ms: Duration in milliseconds.
        external_urls: Mapping of provider name to URL (e.g., {"spotify": ...}).
        preview_url: Optional 30s preview URL when available.
    """

    id: str
    name: str
    artists: List[str]
    album: str
    duration_ms: int
    external_urls: Dict[str, str]
    preview_url: Optional[str] = None


@dataclass
class SpotifyPlaylist:
    """Simplified representation of a Spotify playlist used in the app.

    Attributes:
        id: Unique Spotify playlist ID.
        name: Playlist display name.
        description: Playlist description text.
        owner: Display name of the playlist owner.
        tracks_count: Number of tracks.
        public: Whether the playlist is public.
        external_urls: Mapping of provider name to URL.
        snapshot_id: Spotify playlist version identifier; changes whenever the
            playlist is modified. Used for incremental sync. May be None when
            not provided by the API response.
    """

    id: str
    name: str
    description: str
    owner: str
    tracks_count: int
    public: bool
    external_urls: Dict[str, str]
    snapshot_id: Optional[str] = None
    owner_id: str = ""


