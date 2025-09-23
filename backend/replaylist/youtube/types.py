"""Data types for YouTube domain.

These dataclasses represent the minimal shape of videos and playlists used by
RePlayList, decoupled from raw YouTube API responses for clarity.
"""

from dataclasses import dataclass


@dataclass
class YouTubeVideo:
    """Simplified representation of a YouTube video used in the app.

    Attributes:
        id: Video ID.
        title: Video title.
        channel_title: Channel name that published the video.
        duration: ISO 8601 duration string when available.
        published_at: ISO timestamp of publication.
        thumbnail_url: Thumbnail URL (default quality).
        description: Optional description snippet.
    """
    id: str
    title: str
    channel_title: str
    duration: str
    published_at: str
    thumbnail_url: str
    description: str = ""


@dataclass
class YouTubePlaylist:
    """Simplified representation of a YouTube playlist used in the app.

    Attributes:
        id: Playlist ID.
        title: Playlist title.
        description: Playlist description.
        channel_title: Owner channel name.
        item_count: Number of items in the playlist.
        privacy_status: One of "private", "public", or "unlisted".
        thumbnail_url: Representative thumbnail URL, when present.
    """
    id: str
    title: str
    description: str
    channel_title: str
    item_count: int
    privacy_status: str
    thumbnail_url: str = ""


