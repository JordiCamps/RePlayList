"""YouTube facade: re-export client and types for backward compatibility.

This module provides the same import surface as the original monolithic
`replaylist.youtube`, while delegating implementation to the
`replaylist.youtube` subpackage.
"""

from .youtube.client import YouTubeAPI
from .youtube.types import YouTubePlaylist, YouTubeVideo

__all__ = ["YouTubeAPI", "YouTubePlaylist", "YouTubeVideo"]