"""Extract and incrementally update a local JSON copy of a user's library.

Data is stored under ``<project_root>/data/<platform>/<account_id>/`` so that
multiple accounts (and both platforms) coexist without mixing:

    data/spotify/<spotify_user_id>/
        account.json              # identity + last extraction timestamp
        playlists.json            # list of playlist metadata (with change_key)
        tracks/<playlist_id>.json # tracks for one playlist (with change_key)

``change_key`` is the value used to decide whether a playlist needs to be
re-fetched on update: Spotify's ``snapshot_id`` (changes on any edit) and, for
YouTube, the playlist ``item_count`` (cheap, detects add/remove of videos).

Reading is inexpensive on both platforms, so extraction does not meaningfully
consume the scarce YouTube write/search quota.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..spotify import SpotifyAPI
from ..utils import setup_logging
from ..youtube import YouTubeAPI

logger = setup_logging()

ProgressCallback = Optional[Callable[[str], None]]


def project_root() -> Path:
    """Return the repository root (parent of the ``backend`` package tree)."""
    return Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    """Return the base directory where extracted libraries are stored."""
    return project_root() / "data"


def list_extracted_accounts(platform: str) -> Dict[str, Dict[str, Any]]:
    """Return basic stats for every locally-extracted account of a platform.

    Returns a mapping ``account_id -> {display_name, playlists, tracks,
    updated_at}`` by scanning ``data/<platform>/``. Track totals are summed from
    the per-playlist files.
    """
    base = data_dir() / platform
    out: Dict[str, Dict[str, Any]] = {}
    if not base.exists():
        return out
    for entry in sorted(base.iterdir()):
        if not entry.is_dir():
            continue
        store = LibraryStore(platform, entry.name)
        if not store.has_extract():
            continue
        playlists = store.load_playlists()
        tracks = sum((store.load_tracks(p["id"]) or {}).get("count", 0) for p in playlists)
        meta = {}
        if store.account_path.exists():
            meta = json.loads(store.account_path.read_text(encoding="utf-8"))
        header = json.loads(store.playlists_path.read_text(encoding="utf-8"))
        out[entry.name] = {
            "display_name": meta.get("display_name", entry.name),
            "playlists": len(playlists),
            "tracks": tracks,
            "updated_at": header.get("updated_at"),
        }
    return out


class LibraryStore:
    """Read/write access to one account's on-disk library."""

    def __init__(self, platform: str, account_id: str):
        self.platform = platform
        self.account_id = account_id
        self.base = data_dir() / platform / account_id
        self.tracks_dir = self.base / "tracks"

    # --- paths ---
    @property
    def playlists_path(self) -> Path:
        return self.base / "playlists.json"

    @property
    def account_path(self) -> Path:
        return self.base / "account.json"

    def tracks_path(self, playlist_id: str) -> Path:
        return self.tracks_dir / f"{playlist_id}.json"

    # --- reads ---
    def load_playlists(self) -> List[Dict[str, Any]]:
        if not self.playlists_path.exists():
            return []
        data = json.loads(self.playlists_path.read_text(encoding="utf-8"))
        return data.get("playlists", [])

    def load_tracks(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        path = self.tracks_path(playlist_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def has_extract(self) -> bool:
        return self.playlists_path.exists()

    # --- writes ---
    def write_account(self, info: Dict[str, Any]) -> None:
        self.base.mkdir(parents=True, exist_ok=True)
        self._dump(self.account_path, info)

    def write_playlists(self, playlists: List[Dict[str, Any]], updated_at: str) -> None:
        self.base.mkdir(parents=True, exist_ok=True)
        self._dump(
            self.playlists_path,
            {
                "platform": self.platform,
                "account_id": self.account_id,
                "updated_at": updated_at,
                "count": len(playlists),
                "playlists": playlists,
            },
        )

    def write_tracks(
        self, playlist_id: str, change_key: Optional[str], tracks: List[Dict[str, Any]], updated_at: str
    ) -> None:
        self.tracks_dir.mkdir(parents=True, exist_ok=True)
        self._dump(
            self.tracks_path(playlist_id),
            {
                "playlist_id": playlist_id,
                "change_key": change_key,
                "updated_at": updated_at,
                "count": len(tracks),
                "tracks": tracks,
            },
        )

    @staticmethod
    def _dump(path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


class LibraryExtractor:
    """Fetch playlists/tracks from a platform API into a :class:`LibraryStore`.

    Provide exactly the API client for the platform being extracted.
    """

    def __init__(self, spotify_api: Optional[SpotifyAPI] = None, youtube_api: Optional[YouTubeAPI] = None):
        self.spotify_api = spotify_api
        self.youtube_api = youtube_api

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _display_name(playlist: Dict[str, Any]) -> str:
        return playlist.get("name") or playlist.get("title") or playlist.get("id", "")

    # --- platform-specific helpers ---
    def _account_info(self, platform: str) -> Dict[str, Any]:
        if platform == "spotify":
            me = self.spotify_api.get_user_info()
            account_id = me.get("id")
            return {
                "platform": "spotify",
                "account_id": account_id,
                "display_name": me.get("display_name") or account_id,
            }
        channel = self.youtube_api.get_user_info()
        return {
            "platform": "youtube",
            "account_id": channel.get("id"),
            "display_name": channel.get("snippet", {}).get("title", ""),
        }

    def _fetch_playlists(self, platform: str, account_id: str) -> List[Dict[str, Any]]:
        if platform == "spotify":
            out: List[Dict[str, Any]] = []
            offset = 0
            while True:
                page = self.spotify_api.get_user_playlists(limit=50, offset=offset)
                if not page:
                    break
                for pl in page:
                    # Only extract playlists owned by this account; followed
                    # playlists (editorial / other users') are skipped.
                    if account_id and pl.owner_id and pl.owner_id != account_id:
                        continue
                    record = asdict(pl)
                    record["change_key"] = pl.snapshot_id
                    out.append(record)
                if len(page) < 50:
                    break
                offset += 50
            return out

        playlists = self.youtube_api.get_user_playlists(max_results=50)
        if len(playlists) == 50:
            logger.warning(
                "YouTube returned 50 playlists; pagination beyond the first page is not implemented yet."
            )
        out = []
        for pl in playlists:
            record = asdict(pl)
            record["change_key"] = str(pl.item_count)
            out.append(record)
        return out

    def _fetch_tracks(self, platform: str, playlist_id: str) -> List[Dict[str, Any]]:
        if platform == "spotify":
            return [asdict(t) for t in self.spotify_api.get_playlist_tracks(playlist_id)]
        return [asdict(v) for v in self.youtube_api.get_playlist_videos(playlist_id)]

    # --- public operations ---
    def extract(self, platform: str, progress: ProgressCallback = None) -> Dict[str, Any]:
        """Full extraction: fetch every playlist and all its tracks."""
        info = self._account_info(platform)
        if not info.get("account_id"):
            raise ValueError("Could not resolve account identity from the API.")

        store = LibraryStore(platform, info["account_id"])
        now = self._now()
        store.write_account({**info, "extracted_at": now})

        playlists = self._fetch_playlists(platform, info["account_id"])
        total = len(playlists)
        failed: List[str] = []
        for i, pl in enumerate(playlists, 1):
            if progress:
                progress(f"[{i}/{total}] {self._display_name(pl)}")
            try:
                tracks = self._fetch_tracks(platform, pl["id"])
                pl["track_error"] = None
                store.write_tracks(pl["id"], pl.get("change_key"), tracks, now)
            except Exception as e:  # noqa: BLE001
                # A single inaccessible playlist (e.g. 403 on another user's
                # playlist) must not abort the whole extraction. Annotate and
                # skip writing its tracks file so a later 'update' retries it.
                pl["track_error"] = str(e)
                failed.append(pl["id"])
                logger.warning("Could not fetch tracks for playlist %s: %s", pl["id"], e)
                if progress:
                    progress(f"      skipped (not accessible): {self._display_name(pl)}")

        store.write_playlists(playlists, now)
        return {"account": info, "playlists": total, "failed": len(failed), "data_dir": str(store.base)}

    def update(self, platform: str, progress: ProgressCallback = None) -> Dict[str, Any]:
        """Incremental update: only re-fetch tracks for new/changed playlists."""
        info = self._account_info(platform)
        if not info.get("account_id"):
            raise ValueError("Could not resolve account identity from the API.")

        store = LibraryStore(platform, info["account_id"])
        if not store.has_extract():
            raise FileNotFoundError(
                f"No previous extract found for {platform} account '{info['account_id']}'. "
                "Run 'extract' first."
            )

        previous = {p["id"]: p for p in store.load_playlists()}
        current = self._fetch_playlists(platform, info["account_id"])
        now = self._now()

        new: List[str] = []
        changed: List[str] = []
        unchanged: List[str] = []
        failed: List[str] = []

        total = len(current)
        for i, pl in enumerate(current, 1):
            pid = pl["id"]
            key = pl.get("change_key")
            cached = store.load_tracks(pid)
            label = self._display_name(pl)

            if pid not in previous:
                bucket, action = new, "new"
            elif cached is None or cached.get("change_key") != key:
                bucket, action = changed, "changed"
            else:
                unchanged.append(pid)
                pl["track_error"] = None
                if progress:
                    progress(f"[{i}/{total}] {label}: unchanged")
                continue

            bucket.append(pid)
            if progress:
                progress(f"[{i}/{total}] {label}: {action}, re-fetching tracks")
            try:
                tracks = self._fetch_tracks(platform, pid)
                pl["track_error"] = None
                store.write_tracks(pid, key, tracks, now)
            except Exception as e:  # noqa: BLE001
                pl["track_error"] = str(e)
                failed.append(pid)
                logger.warning("Could not fetch tracks for playlist %s: %s", pid, e)
                if progress:
                    progress(f"      skipped (not accessible): {label}")

        current_ids = {p["id"] for p in current}
        removed = [pid for pid in previous if pid not in current_ids]

        store.write_playlists(current, now)
        store.write_account({**info, "extracted_at": now})

        return {
            "account": info,
            "new": len(new),
            "changed": len(changed),
            "unchanged": len(unchanged),
            "removed": len(removed),
            "failed": len(failed),
            "data_dir": str(store.base),
        }
