"""Resumable, quota-budgeted Spotify -> YouTube playlist migration.

Migrating every Spotify playlist to YouTube is expensive: each track needs a
YouTube search (~100 quota units) plus an insert (~50), against the default
10,000 units/day. This orchestrator therefore:

- Reads the source playlists/tracks from the local Spotify extract (so it does
  not re-hit Spotify).
- Processes at most ``track_budget`` tracks per run (default 60 ~= 9,000 units)
  so a daily run stays within quota.
- Persists progress per source playlist (which tracks are already done) so the
  next run resumes instead of redoing work.
- Reuses an existing target playlist of the same name on YouTube and skips
  videos already present, so re-runs never duplicate.
- Stops gracefully if YouTube signals the quota is exhausted.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from ..spotify import SpotifyAPI, SpotifyTrack
from ..store import LibraryStore, data_dir
from ..youtube import YouTubeAPI
from .matching import TrackMatcher

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[str], None]]


def _is_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "quota" in text or "exceeded" in text


class SpotifyToYouTubeMigrator:
    """Migrate all of a Spotify account's playlists to a YouTube account."""

    def __init__(
        self,
        spotify_api: SpotifyAPI,
        youtube_api: YouTubeAPI,
        source_account_id: str,
        target_account_id: str,
    ):
        self.spotify_api = spotify_api
        self.youtube_api = youtube_api
        self.source_account_id = source_account_id
        self.target_account_id = target_account_id
        self.matcher = TrackMatcher(spotify_api, youtube_api)
        self.source_store = LibraryStore("spotify", source_account_id)
        self.state_path = (
            data_dir()
            / "migrations"
            / f"spotify_{source_account_id}__youtube_{target_account_id}.json"
        )
        self.state = self._load_state()

    # --- state ---
    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        return {
            "source_account": self.source_account_id,
            "target_account": self.target_account_id,
            "playlists": {},
        }

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _playlist_state(self, source_pid: str, name: str) -> Dict[str, Any]:
        ps = self.state["playlists"].setdefault(
            source_pid,
            {"name": name, "target_id": None, "done": [], "matched": 0, "failed": 0, "completed": False},
        )
        ps["name"] = name
        return ps

    # --- target playlist resolution (idempotent) ---
    def _ensure_target_playlist(self, ps: Dict[str, Any], name: str, progress: ProgressCallback):
        """Return (target_id, set_of_existing_video_ids), creating/reusing as needed."""
        if ps.get("target_id"):
            existing = self._existing_video_ids(ps["target_id"])
            return ps["target_id"], existing

        # Reuse an existing YouTube playlist with the same title, if any.
        for pl in self.youtube_api.get_user_playlists(max_results=50):
            if pl.title == name:
                ps["target_id"] = pl.id
                if progress:
                    progress(f"Reusing existing YouTube playlist '{name}'")
                return pl.id, self._existing_video_ids(pl.id)

        if progress:
            progress(f"Creating YouTube playlist '{name}'")
        created = self.youtube_api.create_playlist(name, "Migrated from Spotify")
        ps["target_id"] = created.id
        return created.id, set()

    def _existing_video_ids(self, playlist_id: str) -> set:
        try:
            return {v.id for v in self.youtube_api.get_playlist_videos(playlist_id) if v.id}
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not read existing target videos for %s: %s", playlist_id, e)
            return set()

    # --- run ---
    def run(self, track_budget: int = 60, progress: ProgressCallback = None) -> Dict[str, Any]:
        if not self.source_store.has_extract():
            raise FileNotFoundError(
                f"No Spotify extract for account '{self.source_account_id}'. Run 'extract spotify' first."
            )

        source_playlists = self.source_store.load_playlists()
        total_tracks = 0
        total_done = 0
        processed = 0
        added = 0
        failed = 0
        quota_hit = False

        for pl in source_playlists:
            source_pid = pl["id"]
            name = pl.get("name") or source_pid
            cached = self.source_store.load_tracks(source_pid)
            tracks = (cached or {}).get("tracks", [])
            total_tracks += len(tracks)

            ps = self._playlist_state(source_pid, name)
            done_ids = set(ps["done"])
            total_done += len(done_ids)

            if quota_hit:
                continue
            remaining = [t for t in tracks if t.get("id") and t["id"] not in done_ids]
            if not remaining:
                ps["completed"] = True
                continue
            if processed >= track_budget:
                continue

            try:
                target_id, existing_videos = self._ensure_target_playlist(ps, name, progress)
            except Exception as e:  # noqa: BLE001
                if _is_quota_error(e):
                    quota_hit = True
                    if progress:
                        progress("YouTube quota exhausted; stopping. Resume tomorrow.")
                    continue
                logger.warning("Skipping playlist %s: %s", name, e)
                continue

            for track in remaining:
                if processed >= track_budget:
                    break
                track_obj = SpotifyTrack(**track)
                try:
                    match = self.matcher.find_matching_track(track_obj, "spotify", "youtube")
                    processed += 1
                    if match and match.id:
                        if match.id not in existing_videos:
                            self.youtube_api.add_video_to_playlist(target_id, match.id)
                            existing_videos.add(match.id)
                            added += 1
                        ps["matched"] += 1
                    else:
                        ps["failed"] += 1
                        failed += 1
                    ps["done"].append(track["id"])
                    total_done += 1
                except Exception as e:  # noqa: BLE001
                    if _is_quota_error(e):
                        quota_hit = True
                        if progress:
                            progress("YouTube quota exhausted; stopping. Resume tomorrow.")
                        break
                    logger.warning("Track failed (%s): %s", track.get("name"), e)
                    ps["failed"] += 1
                    failed += 1
                    ps["done"].append(track["id"])
                    total_done += 1
                finally:
                    if processed % 10 == 0:
                        self._save_state()
                if progress and processed % 5 == 0:
                    progress(f"{processed}/{track_budget} processed this run...")

            if all(t.get("id") in set(ps["done"]) for t in tracks if t.get("id")):
                ps["completed"] = True
            self._save_state()
            if quota_hit:
                break

        self._save_state()
        return {
            "processed": processed,
            "added": added,
            "failed": failed,
            "total_tracks": total_tracks,
            "total_done": total_done,
            "remaining": max(0, total_tracks - total_done),
            "quota_hit": quota_hit,
            "state_file": str(self.state_path),
        }
