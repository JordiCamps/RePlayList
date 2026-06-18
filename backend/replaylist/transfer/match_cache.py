"""Persistent Spotify-track -> YouTube-video match cache.

A Spotify track maps to the same YouTube video regardless of account, so this
cache is global (one JSON file). It lets the migrator skip the expensive
YouTube search (100 quota units) for tracks already resolved in a previous
playlist or run.

Positive entries never expire. Negative entries (no match found) expire after
`negative_ttl_days` so an occasional miss can be retried later, but is not
re-searched on every run.

The file is plain JSON, inspectable, and intentionally shareable in a future
phase. It tolerates a missing/corrupt file by starting empty.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from ..store import data_dir
from ..youtube import YouTubeVideo

logger = logging.getLogger(__name__)

CACHE_VERSION = 1


class MatchCache:
    """Read/write access to the global Spotify->YouTube match cache."""

    def __init__(self, path: Optional[Path] = None, negative_ttl_days: int = 30):
        self.path = path or (data_dir() / "cache" / "match_cache.json")
        self.negative_ttl_days = negative_ttl_days
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            entries = data.get("entries", {})
            if isinstance(entries, dict):
                self._entries = entries
        except Exception as e:  # noqa: BLE001 - never let a bad cache break migration
            logger.warning("Could not read match cache %s (%s); starting empty.", self.path, e)
            self._entries = {}

    def lookup(self, spotify_id: str) -> Tuple[str, Optional[YouTubeVideo]]:
        """Return ("hit", video) | ("miss", None) | ("unknown", None).

        - "hit": a cached positive match (reconstructed YouTubeVideo).
        - "miss": a cached negative within TTL (skip, do not search).
        - "unknown": absent or an expired negative (eligible to search).
        """
        entry = self._entries.get(spotify_id)
        if not entry:
            return "unknown", None

        youtube_id = entry.get("youtube_id")
        if youtube_id:
            video = YouTubeVideo(
                id=youtube_id,
                title=entry.get("title", ""),
                channel_title=entry.get("channel_title", ""),
                duration="",
                published_at="",
                thumbnail_url="",
            )
            return "hit", video

        # Negative entry: honour the TTL, self-heal on bad/old timestamps.
        if self._negative_is_fresh(entry.get("updated_at")):
            return "miss", None
        return "unknown", None

    def _negative_is_fresh(self, updated_at: Optional[str]) -> bool:
        if not updated_at:
            return False
        try:
            ts = datetime.fromisoformat(updated_at)
        except ValueError:
            return False
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - ts).total_seconds() / 86400
        return age_days < self.negative_ttl_days

    def put_match(self, spotify_id: str, video: YouTubeVideo, score: Optional[int] = None) -> None:
        self._entries[spotify_id] = {
            "youtube_id": video.id,
            "title": video.title,
            "channel_title": video.channel_title,
            "score": score,
            "updated_at": self._now(),
        }

    def put_miss(self, spotify_id: str) -> None:
        self._entries[spotify_id] = {
            "youtube_id": None,
            "updated_at": self._now(),
        }

    def invalidate(self, spotify_id: str) -> None:
        self._entries.pop(spotify_id, None)

    def save(self) -> None:
        """Write the cache atomically (tmp + replace)."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"version": CACHE_VERSION, "entries": self._entries}
            tmp = self.path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self.path)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not save match cache %s: %s", self.path, e)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
