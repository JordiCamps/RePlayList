"""Copy a playlist between two YouTube accounts.

YouTube video ids are identical across accounts, so copying is a direct
id-based copy with no fuzzy matching: read the source playlist's video ids
(from the local extract when available, otherwise the API) and insert them into
a playlist owned by the target account.

Quota note: inserting a playlist item costs ~50 units each, and creating a
playlist ~50 units, against the default 10,000/day YouTube quota. Reading the
source is cheap (or free if served from the local cache).
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..youtube import YouTubeAPI

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[str], None]]


class YouTubeAccountCopier:
    """Copy playlists from one YouTube account to another."""

    def __init__(
        self,
        source_api: YouTubeAPI,
        target_api: YouTubeAPI,
        source_account_id: Optional[str] = None,
    ):
        """
        Args:
            source_api: YouTubeAPI authenticated as the source account.
            target_api: YouTubeAPI authenticated as the target account.
            source_account_id: Source account id; when set, the source playlist
                is read from the local extract (data/youtube/<id>/) if present,
                avoiding API calls.
        """
        self.source_api = source_api
        self.target_api = target_api
        self.source_account_id = source_account_id

    def _source_video_ids(self, playlist_id: str, progress: ProgressCallback) -> Tuple[List[str], str]:
        """Return (video_ids, source_playlist_name), preferring the local cache."""
        if self.source_account_id:
            # Lazy import to avoid a package import cycle.
            from ..store import LibraryStore

            store = LibraryStore("youtube", self.source_account_id)
            cached = store.load_tracks(playlist_id)
            if cached and cached.get("tracks"):
                ids = [t["id"] for t in cached["tracks"] if t.get("id")]
                name = next(
                    (
                        p.get("title") or p.get("name")
                        for p in store.load_playlists()
                        if p.get("id") == playlist_id
                    ),
                    playlist_id,
                )
                if progress:
                    progress(f"Using local cache for source ({len(ids)} videos).")
                return ids, name

        if progress:
            progress("Fetching source playlist from the YouTube API...")
        videos = self.source_api.get_playlist_videos(playlist_id)
        info = self.source_api.get_playlist_info(playlist_id)
        name = info.title if info else playlist_id
        return [v.id for v in videos if v.id], name

    def copy_playlist(
        self,
        source_playlist_id: str,
        target_name: Optional[str] = None,
        target_playlist_id: Optional[str] = None,
        privacy_status: str = "private",
        progress: ProgressCallback = None,
    ) -> Dict[str, Any]:
        """Copy a source playlist into a new or existing target playlist.

        Args:
            source_playlist_id: Playlist id on the source account.
            target_name: Title for the new target playlist (defaults to source name).
            target_playlist_id: If given, append into this existing target playlist
                instead of creating a new one.
            privacy_status: Privacy of the created playlist ("private"/"public"/"unlisted").
            progress: Optional progress callback.

        Returns:
            Summary dict with counts and any failures.
        """
        video_ids, source_name = self._source_video_ids(source_playlist_id, progress)
        if not video_ids:
            raise ValueError("Source playlist has no videos (or is not accessible).")

        if target_playlist_id:
            target_id = target_playlist_id
            target_title = target_name or source_name
        else:
            title = target_name or source_name
            if progress:
                progress(f"Creating target playlist '{title}'...")
            created = self.target_api.create_playlist(
                title, f"Copied from YouTube playlist {source_playlist_id}", privacy_status
            )
            target_id = created.id
            target_title = created.title

        added = 0
        failures: List[Dict[str, str]] = []
        total = len(video_ids)
        for i, video_id in enumerate(video_ids, 1):
            if progress:
                progress(f"[{i}/{total}] adding {video_id}")
            try:
                self.target_api.add_video_to_playlist(target_id, video_id)
                added += 1
            except Exception as e:  # noqa: BLE001
                failures.append({"video_id": video_id, "error": str(e)})
                logger.warning("Failed to add video %s: %s", video_id, e)

        return {
            "source_playlist": source_playlist_id,
            "source_name": source_name,
            "target_playlist_id": target_id,
            "target_title": target_title,
            "total": total,
            "added": added,
            "failed": len(failures),
            "failures": failures,
        }
