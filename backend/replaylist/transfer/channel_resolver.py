"""Resolve a Spotify artist to its YouTube channel and match tracks locally.

For artists that appear many times in the library, resolving the artist's
YouTube channel once (one `search.list`, 100 units) and enumerating its uploads
(cheap, ~1 unit/page) lets us match all that artist's tracks **locally** with no
per-track search. Gated by an artist track-count threshold so it never costs
more than searching each track individually.

Persistent: the resolved channel and its video pool are cached on disk so they
are not re-resolved every run. Artists with no usable channel are remembered as
negatives with a TTL.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..store import data_dir
from ..utils import clean_artist, clean_title, fuzzy_score
from ..youtube import YouTubeAPI, YouTubeVideo

logger = logging.getLogger(__name__)

# A local pool match needs a decent title similarity to be trusted.
POOL_TITLE_THRESHOLD = 60
# Minimum channel-name similarity (+ Topic bonus) to accept a channel.
CHANNEL_MATCH_THRESHOLD = 40
CHANNEL_RESOLVE_COST = 100  # one search.list


def _is_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "quota" in text or "exceeded" in text


def artist_key(artist: Optional[str]) -> str:
    """Normalized key for an artist name, shared by counter and resolver."""
    return clean_artist(artist or "").lower().strip()


class ArtistChannelResolver:
    """Resolves artist -> YouTube channel and matches tracks against its uploads."""

    def __init__(self, youtube_api: YouTubeAPI, path: Optional[Path] = None,
                 negative_ttl_days: int = 30, min_tracks: int = 2):
        self.youtube_api = youtube_api
        self.path = path or (data_dir() / "cache" / "artist_channels.json")
        self.negative_ttl_days = negative_ttl_days
        self.min_tracks = min_tracks
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
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not read artist-channel cache %s (%s); starting empty.", self.path, e)
            self._entries = {}

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"version": 1, "entries": self._entries}
            tmp = self.path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self.path)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not save artist-channel cache %s: %s", self.path, e)

    def find_match(self, artist: Optional[str], track_title: str,
                   artist_track_count: int) -> Tuple[Optional[YouTubeVideo], int]:
        """Return (video|None, search_units_spent).

        Resolves the artist's channel on first use if the artist appears at
        least `min_tracks` times (otherwise returns (None, 0) so the caller does
        a normal per-track search). Quota errors propagate to the caller.
        """
        key = artist_key(artist)
        if not key:
            return None, 0

        entry = self._entries.get(key)
        units = 0

        if entry is None:
            if artist_track_count < self.min_tracks:
                return None, 0  # not worth resolving a channel for a one-off artist
            try:
                resolved = self._resolve_channel(artist)
                units += CHANNEL_RESOLVE_COST
            except Exception as e:  # noqa: BLE001
                if _is_quota_error(e):
                    raise
                logger.warning("Channel resolution failed for '%s': %s", artist, e)
                return None, units
            entry = resolved or {"channel_id": None, "updated_at": self._now()}
            self._entries[key] = entry

        if entry.get("channel_id") is None:
            # Negative: skip within TTL; if expired, drop so a future run retries.
            if not self._negative_is_fresh(entry.get("updated_at")):
                self._entries.pop(key, None)
            return None, units

        return self._best_in_pool(entry.get("pool", []), track_title), units

    def _resolve_channel(self, artist: str) -> Optional[Dict[str, Any]]:
        """Find the artist's channel (prefer 'Artist - Topic') and enumerate uploads."""
        results = self.youtube_api.search_channels(artist, max_results=10)
        if not results:
            return None
        target = clean_artist(artist).lower()
        chosen: Optional[Tuple[str, str]] = None
        best_score = 0
        for channel_id, title in results:
            title_l = title.lower()
            is_topic = title_l.endswith("- topic") or "topic" in title_l
            score = fuzzy_score(clean_artist(title).lower(), target) + (50 if is_topic else 0)
            if score > best_score:
                best_score = score
                chosen = (channel_id, title)
        if not chosen or best_score < CHANNEL_MATCH_THRESHOLD:
            return None
        channel_id, title = chosen
        videos = self.youtube_api.get_channel_videos(channel_id)
        pool = [
            {"id": v.id, "title": v.title, "channel_title": v.channel_title}
            for v in videos if v.id
        ]
        if not pool:
            return None
        return {"channel_id": channel_id, "channel_title": title, "pool": pool, "resolved_at": self._now()}

    def _best_in_pool(self, pool: List[Dict[str, Any]], track_title: str) -> Optional[YouTubeVideo]:
        target = clean_title(track_title)
        best: Optional[Dict[str, Any]] = None
        best_score = 0
        for item in pool:
            score = max(
                fuzzy_score(clean_title(item.get("title", "")), target),
                fuzzy_score(item.get("title", ""), target),
            )
            if score > best_score:
                best_score = score
                best = item
        if best and best_score >= POOL_TITLE_THRESHOLD:
            return YouTubeVideo(
                id=best["id"], title=best.get("title", ""),
                channel_title=best.get("channel_title", ""),
                duration="", published_at="", thumbnail_url="",
            )
        return None

    def _negative_is_fresh(self, updated_at: Optional[str]) -> bool:
        if not updated_at:
            return False
        try:
            ts = datetime.fromisoformat(updated_at)
        except ValueError:
            return False
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds() / 86400 < self.negative_ttl_days

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
