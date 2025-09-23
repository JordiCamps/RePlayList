"""Spotify Web API client used by RePlayList.

This module defines a resilient client around Spotify's Web API. It retains the
public surface of the previous monolithic `SpotifyAPI` so existing imports
continue to work, while centralizing concerns like retries, rate limits, and
error handling in `_make_request`.

Design notes:
- Network access is funneled through a single method decorated with
  `retry_on_exception`, `rate_limit`, and `handle_api_errors` from
  `replaylist.utils`.
- Domain types live in `spotify.types` to keep responsibilities tidy and enable
  reuse.

Authentication:
- All methods require a valid OAuth access token. Token refresh is handled by
  the auth layer; this client assumes a current token is provided.

Rate limiting:
- While Spotify allows high throughput, we keep conservative per-method limits
  to avoid bursts and provide a smoother user experience.
"""

from typing import Any, Dict, List, Optional

import requests

from ..utils import handle_api_errors, rate_limit, retry_on_exception, setup_logging
from .types import SpotifyPlaylist, SpotifyTrack


logger = setup_logging()


class SpotifyAPI:
    """High-level helper for playlist, track, and profile operations.

    Attributes:
        access_token: OAuth access token for authenticated requests.
        headers: Standard JSON headers with Authorization.

    Thread-safety:
        Instances are not inherently thread-safe; if sharing across threads,
        ensure external synchronization for mutation (e.g., rotating tokens).
    """
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, access_token: str):
        """Initialize Spotify API client with a bearer token.

        Args:
            access_token: OAuth bearer token obtained via the Spotify auth flow.

        Raises:
            ValueError: If the token is an empty string.
        """
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    @retry_on_exception(max_retries=3, delay=1.0, exceptions=(requests.RequestException,))
    @rate_limit(calls_per_second=2.0)
    @handle_api_errors
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute an authenticated HTTP request to the Spotify API.

        Args:
            method: HTTP verb, e.g. "GET" or "POST".
            endpoint: API path beginning with "/".
            **kwargs: Forwarded to `requests.request`.

        Returns:
            Parsed JSON response.

        Raises:
            requests.HTTPError: For non-2xx responses after retries.
            requests.RequestException: For network-level errors after retries.
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def get_user_playlists(self, limit: int = 50, offset: int = 0) -> List[SpotifyPlaylist]:
        """Return playlists owned or followed by the current user.

        Args:
            limit: Maximum playlists per page (1..50).
            offset: Zero-based index of the first item to return.

        Returns:
            A list of `SpotifyPlaylist` representing the current page.
        """
        params = {"limit": limit, "offset": offset}
        data = self._make_request("GET", "/me/playlists", params=params)
        playlists: List[SpotifyPlaylist] = []
        for item in data.get("items", []):
            playlists.append(
                SpotifyPlaylist(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    owner=item["owner"]["display_name"],
                    tracks_count=item["tracks"]["total"],
                    public=item["public"],
                    external_urls=item["external_urls"],
                )
            )
        return playlists

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def get_playlist_tracks(self, playlist_id: str, limit: int = 100, offset: int = 0) -> List[SpotifyTrack]:
        """Return tracks in a playlist; iterates all pages if offset is 0.

        Args:
            playlist_id: Spotify playlist ID.
            limit: Page size (1..100).
            offset: If zero, fetches all pages; otherwise a single page.

        Returns:
            A list of `SpotifyTrack` instances.
        """
        if offset == 0:
            return self._get_all_playlist_tracks(playlist_id, limit)
        return self._get_playlist_tracks_page(playlist_id, limit, offset)

    def _get_all_playlist_tracks(self, playlist_id: str, limit: int = 100) -> List[SpotifyTrack]:
        """Fetch all tracks from a playlist using pagination.

        Note:
            Adds a tiny delay between page fetches to avoid bursts.
        """
        all_tracks: List[SpotifyTrack] = []
        current_offset = 0
        while True:
            page_tracks = self._get_playlist_tracks_page(playlist_id, limit, current_offset)
            if not page_tracks:
                break
            all_tracks.extend(page_tracks)
            if len(page_tracks) < limit:
                break
            current_offset += limit
            import time

            time.sleep(0.1)
        logger.info("Retrieved %d tracks from playlist %s", len(all_tracks), playlist_id)
        return all_tracks

    def _get_playlist_tracks_page(self, playlist_id: str, limit: int, offset: int) -> List[SpotifyTrack]:
        """Fetch a single page of tracks for a playlist.

        Returns:
            A list of tracks for the page (may be empty at end of collection).
        """
        params = {"limit": limit, "offset": offset, "fields": "items(track(id,name,artists,album,duration_ms,external_urls,preview_url))"}
        data = self._make_request("GET", f"/playlists/{playlist_id}/tracks", params=params)
        tracks: List[SpotifyTrack] = []
        for item in data.get("items", []):
            track_data = item.get("track")
            if track_data and track_data.get("id"):
                tracks.append(
                    SpotifyTrack(
                        id=track_data["id"],
                        name=track_data["name"],
                        artists=[artist["name"] for artist in track_data["artists"]],
                        album=track_data["album"]["name"],
                        duration_ms=track_data["duration_ms"],
                        external_urls=track_data["external_urls"],
                        preview_url=track_data.get("preview_url"),
                    )
                )
        return tracks

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def create_playlist(self, name: str, description: str = "", public: bool = False) -> SpotifyPlaylist:
        """Create a new playlist for the current user.

        Args:
            name: Playlist name.
            description: Optional description.
            public: Whether the playlist should be public.

        Returns:
            The created `SpotifyPlaylist` with initial metadata.
        """
        user_data = self._make_request("GET", "/me")
        user_id = user_data["id"]
        playlist_data = {"name": name, "description": description, "public": public}
        data = self._make_request("POST", f"/users/{user_id}/playlists", json=playlist_data)
        return SpotifyPlaylist(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            owner=data["owner"]["display_name"],
            tracks_count=0,
            public=data["public"],
            external_urls=data["external_urls"],
        )

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> None:
        """Append tracks to a playlist in batches of up to 100 URIs.

        Args:
            playlist_id: Target playlist ID.
            track_uris: The Spotify track URIs to append in order.

        Raises:
            ValueError: If `track_uris` is empty.
        """
        batch_size = 100
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i : i + batch_size]
            self._make_request("POST", f"/playlists/{playlist_id}/tracks", json={"uris": batch})
            logger.info("Added %d tracks to playlist %s", len(batch), playlist_id)

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def search_tracks(self, query: str, limit: int = 20) -> List[SpotifyTrack]:
        """Search for tracks and return simplified track objects.

        Args:
            query: Spotify search query syntax supported (e.g., track:"..." artist:"...").
            limit: Max number of results to return.
        """
        params = {"q": query, "type": "track", "limit": limit}
        data = self._make_request("GET", "/search", params=params)
        tracks: List[SpotifyTrack] = []
        for item in data.get("tracks", {}).get("items", []):
            tracks.append(
                SpotifyTrack(
                    id=item["id"],
                    name=item["name"],
                    artists=[artist["name"] for artist in item["artists"]],
                    album=item["album"]["name"],
                    duration_ms=item["duration_ms"],
                    external_urls=item["external_urls"],
                    preview_url=item.get("preview_url"),
                )
            )
        return tracks

    def find_track_by_metadata(self, title: str, artist: str, album: str = "") -> Optional[SpotifyTrack]:
        """Heuristically find a track using title, artist, and optional album.

        Strategy:
            Runs a sequence of narrowing search queries and selects the top
            candidate using fuzzy scoring across title and artist fields.
        """
        clean_title = self._clean_title(title)
        clean_artist = self._clean_artist(artist)
        search_strategies = [
            f'track:"{clean_title}" artist:"{clean_artist}"',
            f'track:"{clean_title}" {clean_artist}',
            f'{clean_title} artist:"{clean_artist}"',
            f'{clean_title} {clean_artist}',
            f'track:"{title}" artist:"{artist}"',
            f'track:"{self._extract_main_title(title)}" artist:"{clean_artist}"',
            f'{self._extract_main_title(title)} {clean_artist}',
            f'track:"{clean_title}"',
            f'artist:"{clean_artist}"',
        ]
        if album:
            clean_album = self._clean_title(album)
            search_strategies.extend(
                [
                    f'track:"{clean_title}" artist:"{clean_artist}" album:"{clean_album}"',
                    f'{clean_title} {clean_artist} album:"{clean_album}"',
                ]
            )
        for q in search_strategies:
            try:
                tracks = self.search_tracks(q, limit=20)
                if tracks:
                    best_track = self._score_tracks(tracks, clean_title, clean_artist)
                    if best_track:
                        return best_track
            except Exception:
                continue
        return None

    def _clean_title(self, title: str) -> str:
        """Normalize a title by stripping common noise words and suffixes.

        Removes markers like "(official video)", "(lyrics)", and bracketed
        annotations, then collapses whitespace and trims punctuation.
        """
        import re as _re

        if not title:
            return ""
        suffixes_to_remove = [
            r"\s*\(official\s+video\)",
            r"\s*\(official\s+music\s+video\)",
            r"\s*\(lyrics\)",
            r"\s*\(lyric\s+video\)",
            r"\s*\(audio\)",
            r"\s*\(official\s+audio\)",
            r"\s*\(hq\)",
            r"\s*\(hd\)",
            r"\s*\(4k\)",
            r"\s*\(remastered\)",
            r"\s*\(remaster\)",
            r"\s*\(live\)",
            r"\s*\(live\s+performance\)",
            r"\s*\(acoustic\)",
            r"\s*\(cover\)",
            r"\s*\(ft\.\?\s+.*?\)",
            r"\s*\(feat\.\?\s+.*?\)",
            r"\s*\(featuring\s+.*?\)",
            r"\s*\[.*?\]",
            r"\s*\(.*?version.*?\)",
            r"\s*\(.*?edit.*?\)",
            r"\s*\(.*?mix.*?\)",
        ]
        cleaned = title.strip()
        for pattern in suffixes_to_remove:
            cleaned = _re.sub(pattern, "", cleaned, flags=_re.IGNORECASE)
        cleaned = _re.sub(r"\s+", " ", cleaned).strip().strip(".,;:!?")
        return cleaned

    def _clean_artist(self, artist: str) -> str:
        """Normalize an artist name by stripping channel decorations.

        Removes suffixes like "(official)", "(vevo)", and similar markers.
        """
        import re as _re

        if not artist:
            return ""
        suffixes_to_remove = [
            r"\s*\(official\)",
            r"\s*\(official\s+channel\)",
            r"\s*\(music\)",
            r"\s*\(vevo\)",
            r"\s*\(topic\)",
            r"\s*\[.*?\]",
        ]
        cleaned = artist.strip()
        for pattern in suffixes_to_remove:
            cleaned = _re.sub(pattern, "", cleaned, flags=_re.IGNORECASE)
        return _re.sub(r"\s+", " ", cleaned).strip()

    def _extract_main_title(self, title: str) -> str:
        """Remove common separators/prefixes, then clean the result.

        Drops everything up to the first dash, colon, or pipe, then calls
        `_clean_title` for final normalization.
        """
        import re as _re

        if not title:
            return ""
        prefixes_to_remove = [r"^.*?-\s*", r"^.*?:\s*", r"^.*?\|\s*"]
        cleaned = title.strip()
        for pattern in prefixes_to_remove:
            cleaned = _re.sub(pattern, "", cleaned, flags=_re.IGNORECASE)
        return self._clean_title(cleaned)

    def _score_tracks(self, tracks: List[SpotifyTrack], target_title: str, target_artist: str) -> Optional[SpotifyTrack]:
        """Score tracks by fuzzy similarity and return the best match above a threshold.

        Heuristic:
            Title similarity is weighted 2x artist similarity; returns `None`
            if the best score does not meet a minimum threshold.
        """
        if not tracks:
            return None
        best_track: Optional[SpotifyTrack] = None
        best_score = 0
        for track in tracks:
            score = 0
            title_score = self._calculate_fuzzy_score(track.name, target_title)
            score += title_score * 2
            best_artist_score = 0
            for track_artist in track.artists:
                artist_score = self._calculate_fuzzy_score(track_artist, target_artist)
                best_artist_score = max(best_artist_score, artist_score)
            score += best_artist_score
            if score > best_score:
                best_score = score
                best_track = track
        return best_track if best_score >= 15 else None

    def _calculate_fuzzy_score(self, text1: str, text2: str) -> int:
        """Compute a fuzzy match score using word and character similarity.

        Combines Jaccard word overlap (70%) with normalized Levenshtein-based
        character similarity (30%). Returns an integer 0..100.
        """
        if not text1 or not text2:
            return 0
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()
        if t1 == t2:
            return 100
        if t1 in t2 or t2 in t1:
            return 80
        words1 = set(t1.split())
        words2 = set(t2.split())
        if not words1 or not words2:
            return 0
        inter = words1 & words2
        union = words1 | words2
        word_similarity = len(inter) / len(union) if union else 0
        char_similarity = self._calculate_char_similarity(t1, t2)
        return int((word_similarity * 70) + (char_similarity * 30))

    def _calculate_char_similarity(self, text1: str, text2: str) -> float:
        """Compute normalized Levenshtein-based similarity between two strings.

        Returns a float in 0..1 where 1 represents identical strings.
        """
        if not text1 or not text2:
            return 0.0
        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
        distance = levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        return 1.0 - (distance / max_len)

    def get_playlist_info(self, playlist_id: str) -> Optional[SpotifyPlaylist]:
        """Get playlist metadata by ID.

        Returns:
            A `SpotifyPlaylist` or `None` if the playlist cannot be retrieved.
        """
        data = self._make_request("GET", f"/playlists/{playlist_id}")
        return SpotifyPlaylist(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            owner=data["owner"]["display_name"],
            tracks_count=data["tracks"]["total"],
            public=data["public"],
            external_urls=data["external_urls"],
        )

    def get_user_info(self) -> Dict[str, Any]:
        """Get the current user's profile information."""
        return self._make_request("GET", "/me")


