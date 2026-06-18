"""YouTube Data API v3 client.

This module defines a resilient client over YouTube Data API v3 used by
RePlayList. It centralizes authentication headers, rate limiting, retries, and
error handling. The public API mirrors the previous monolithic
`backend.replaylist.youtube.YouTubeAPI` for compatibility.

Design notes:
- Network effects are isolated behind `_make_request` with decorators for
  retry, rate limit and error mapping.
- Domain models live in `youtube.types` for reuse and single responsibility.

Authentication:
- Methods require a valid OAuth access token. Token refresh is performed by the
  auth layer; this client assumes a current token is provided.

Rate limiting:
- YouTube applies stricter quotas. We throttle calls conservatively to reduce
  bursts and stay within limits during pagination.
"""

from typing import Any, Dict, List, Optional, Tuple

import requests

from ..utils import handle_api_errors, rate_limit, retry_on_exception, setup_logging
from ..utils import clean_title, clean_artist, fuzzy_score
from .types import YouTubePlaylist, YouTubeVideo


logger = setup_logging()

# Minimum score for a candidate to be accepted as a match (same scale and
# threshold as SpotifyAPI._score_tracks: title weight x2 + artist, 0..300).
MATCH_THRESHOLD = 15


class YouTubeAPI:
    """High-level helper for common YouTube playlist and search operations.

    Attributes:
        access_token: OAuth access token for authenticated requests.
        headers: Precomputed headers for authenticated JSON requests.

    Thread-safety:
        Instances are not inherently thread-safe; share across threads only
        with external coordination.

    The class methods prefer simple Python types and `YouTube*` dataclasses to
    keep call sites clean and testable.
    """
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, access_token: str):
        """Initialize the client with a bearer token.

        Args:
            access_token: OAuth bearer token obtained from the auth flow.

        Raises:
            ValueError: If the token is empty.
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @retry_on_exception(max_retries=3, delay=1.0, exceptions=(requests.RequestException,))
    @rate_limit(calls_per_second=1.0)
    @handle_api_errors
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute an authenticated HTTP request to the YouTube API.

        Args:
            method: HTTP verb, e.g. "GET", "POST".
            endpoint: API path starting with "/".
            **kwargs: Forwarded to `requests.request` (e.g. params, json).

        Returns:
            Parsed JSON dict.

        Raises:
            requests.HTTPError: When response is non-2xx after retries.
            requests.RequestException: For network errors after retries.
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def get_user_playlists(self, max_results: int = 50, page_token: str | None = None) -> List[YouTubePlaylist]:
        """Return playlists owned by the authenticated user.

        Args:
            max_results: Max items per page (1..50).
            page_token: Optional page token to fetch a specific page.

        Returns:
            A list of playlists for the requested page.
        """
        params = {"part": "snippet,contentDetails", "mine": "true", "maxResults": max_results}
        if page_token:
            params["pageToken"] = page_token
        data = self._make_request("GET", "/playlists", params=params)
        playlists: List[YouTubePlaylist] = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            content_details = item.get("contentDetails", {})
            playlists.append(
                YouTubePlaylist(
                    id=item["id"],
                    title=snippet["title"],
                    description=snippet.get("description", ""),
                    channel_title=snippet["channelTitle"],
                    item_count=content_details.get("itemCount", 0),
                    privacy_status=item.get("status", {}).get("privacyStatus", "private"),
                    thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                )
            )
        return playlists

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def get_playlist_videos(
        self, playlist_id: str, max_results: int = 50, page_token: str | None = None
    ) -> List[YouTubeVideo]:
        """List videos in a playlist, optionally paginated.

        If `page_token` is None, iterates all pages and returns the full list.

        Returns:
            A list of `YouTubeVideo` items.
        """
        if page_token is None:
            return self._get_all_playlist_videos(playlist_id, max_results)
        return self._get_playlist_videos_page(playlist_id, max_results, page_token)

    def _get_all_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[YouTubeVideo]:
        """Fetch all videos from the given playlist using pagination.

        Note:
            Adds a tiny delay between page fetches to avoid bursts.
        """
        all_videos: List[YouTubeVideo] = []
        page_token: Optional[str] = None
        while True:
            page_videos, next_page_token = self._get_playlist_videos_page_with_token(
                playlist_id, max_results, page_token
            )
            if not page_videos:
                break
            all_videos.extend(page_videos)
            if not next_page_token:
                break
            page_token = next_page_token
            import time

            time.sleep(0.1)
        logger.info("Retrieved %d videos from playlist %s", len(all_videos), playlist_id)
        return all_videos

    def _get_playlist_videos_page(self, playlist_id: str, max_results: int, page_token: str) -> List[YouTubeVideo]:
        """Fetch a single page of videos for the given playlist and token.

        Returns:
            A list of videos for the page (may be empty at end of collection).
        """
        videos, _ = self._get_playlist_videos_page_with_token(playlist_id, max_results, page_token)
        return videos

    def _get_playlist_videos_page_with_token(
        self, playlist_id: str, max_results: int, page_token: str | None = None
    ) -> Tuple[List[YouTubeVideo], Optional[str]]:
        """Fetch one page of videos and return the page token for the next page."""
        params: Dict[str, Any] = {"part": "snippet,contentDetails", "playlistId": playlist_id, "maxResults": max_results}
        if page_token:
            params["pageToken"] = page_token
        data = self._make_request("GET", "/playlistItems", params=params)
        videos: List[YouTubeVideo] = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            content_details = item.get("contentDetails", {})
            videos.append(
                YouTubeVideo(
                    id=content_details.get("videoId", ""),
                    title=snippet["title"],
                    channel_title=snippet["channelTitle"],
                    duration=content_details.get("duration", ""),
                    published_at=snippet["publishedAt"],
                    thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                    description=snippet.get("description", ""),
                )
            )
        return videos, data.get("nextPageToken")

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def create_playlist(self, title: str, description: str = "", privacy_status: str = "private") -> YouTubePlaylist:
        """Create a new playlist owned by the authenticated user.

        Args:
            title: Playlist title.
            description: Optional description.
            privacy_status: One of "private", "public", "unlisted".
        """
        channel_data = self._make_request("GET", "/channels", params={"part": "snippet", "mine": "true"})
        if not channel_data.get("items"):
            raise ValueError("No channel information found. Make sure you're authenticated with YouTube.")
        channel_id = channel_data["items"][0]["id"]
        playlist_data = {
            "snippet": {"title": title, "description": description, "channelId": channel_id},
            "status": {"privacyStatus": privacy_status},
        }
        params = {"part": "snippet,status"}
        data = self._make_request("POST", "/playlists", params=params, json=playlist_data)
        snippet = data["snippet"]
        return YouTubePlaylist(
            id=data["id"],
            title=snippet["title"],
            description=snippet.get("description", ""),
            channel_title=snippet["channelTitle"],
            item_count=0,
            privacy_status=data["status"]["privacyStatus"],
            thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
        )

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def add_video_to_playlist(self, playlist_id: str, video_id: str, position: int | None = None) -> None:
        """Insert a video into a playlist at an optional position."""
        playlist_item_data: Dict[str, Any] = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        }
        if position is not None:
            playlist_item_data["snippet"]["position"] = position
        params = {"part": "snippet"}
        self._make_request("POST", "/playlistItems", params=params, json=playlist_item_data)

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def add_videos_to_playlist(self, playlist_id: str, video_ids: List[str]) -> None:
        """Insert multiple videos into a playlist maintaining the given order."""
        for i, video_id in enumerate(video_ids):
            self.add_video_to_playlist(playlist_id, video_id, i)
            logger.info("Added video %d/%d to playlist %s", i + 1, len(video_ids), playlist_id)

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def search_videos(self, query: str, max_results: int = 20) -> List[YouTubeVideo]:
        """Search for videos and return simplified results.

        Args:
            query: YouTube search query.
            max_results: Page size (1..50).
        """
        params = {"part": "snippet", "q": query, "type": "video", "maxResults": max_results, "order": "relevance"}
        data = self._make_request("GET", "/search", params=params)
        videos: List[YouTubeVideo] = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            videos.append(
                YouTubeVideo(
                    id=video_id,
                    title=snippet["title"],
                    channel_title=snippet["channelTitle"],
                    duration="",
                    published_at=snippet["publishedAt"],
                    thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                    description=snippet.get("description", ""),
                )
            )
        return videos

    def find_video_by_metadata(self, title: str, artist: str, duration: str = "") -> Optional[YouTubeVideo]:
        """Heuristic search for a video using title and optional artist hint.

        Fetches up to 50 candidates (one search.list call, fixed cost) and
        scores them by title/artist similarity, returning the best match above
        the threshold instead of blindly taking the first relevance result.
        """
        video, _score = self.find_video_by_metadata_scored(title, artist)
        return video

    def find_video_by_metadata_scored(self, title: str, artist: str) -> Tuple[Optional[YouTubeVideo], int]:
        """Like find_video_by_metadata but also returns the match score.

        Returns (best_video, score) or (None, best_score) when nothing clears
        the threshold.
        """
        query = " ".join(p for p in (title, artist) if p)
        videos = self.search_videos(query, max_results=50)
        if not videos:
            return None, 0

        target_title = clean_title(title)
        target_artist = clean_artist(artist)
        best: Optional[YouTubeVideo] = None
        best_score = 0
        for video in videos:
            cand_title = clean_title(video.title)
            title_score = max(
                fuzzy_score(cand_title, target_title),
                fuzzy_score(video.title, target_title),
            )
            # The uploader channel is usually the artist (or "Artist - Topic").
            artist_score = max(
                fuzzy_score(video.channel_title, target_artist),
                fuzzy_score(cand_title, target_artist),
                fuzzy_score(video.title, target_artist),
            )
            score = title_score * 2 + artist_score
            if score > best_score:
                best_score = score
                best = video
        if best is not None and best_score >= MATCH_THRESHOLD:
            return best, best_score
        return None, best_score

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def search_channels(self, query: str, max_results: int = 10) -> List[Tuple[str, str]]:
        """Search channels by name; returns a list of (channel_id, title)."""
        params = {"part": "snippet", "q": query, "type": "channel", "maxResults": max_results}
        data = self._make_request("GET", "/search", params=params)
        out: List[Tuple[str, str]] = []
        for item in data.get("items", []):
            channel_id = item.get("id", {}).get("channelId")
            if channel_id:
                out.append((channel_id, item.get("snippet", {}).get("title", "")))
        return out

    @retry_on_exception(max_retries=3, exceptions=(requests.RequestException,))
    def get_uploads_playlist_id(self, channel_id: str) -> Optional[str]:
        """Return the channel's 'uploads' playlist id (contains all its videos)."""
        data = self._make_request("GET", "/channels", params={"part": "contentDetails", "id": channel_id})
        items = data.get("items", [])
        if not items:
            return None
        return items[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

    def get_channel_videos(self, channel_id: str, max_videos: int = 250) -> List[YouTubeVideo]:
        """Enumerate up to `max_videos` of a channel's uploads (cheap: ~1 unit/page)."""
        uploads = self.get_uploads_playlist_id(channel_id)
        if not uploads:
            return []
        videos: List[YouTubeVideo] = []
        page_token: Optional[str] = None
        while True:
            page, page_token = self._get_playlist_videos_page_with_token(uploads, 50, page_token)
            videos.extend(page)
            if not page_token or len(videos) >= max_videos:
                break
            import time
            time.sleep(0.1)
        return videos[:max_videos]

    def get_playlist_info(self, playlist_id: str) -> Optional[YouTubePlaylist]:
        """Get details of a playlist by ID.

        Returns:
            A `YouTubePlaylist` or `None` if the playlist cannot be retrieved.
        """
        params = {"part": "snippet,contentDetails,status", "id": playlist_id}
        data = self._make_request("GET", "/playlists", params=params)
        if not data.get("items"):
            return None
        item = data["items"][0]
        snippet = item["snippet"]
        content_details = item.get("contentDetails", {})
        return YouTubePlaylist(
            id=item["id"],
            title=snippet["title"],
            description=snippet.get("description", ""),
            channel_title=snippet["channelTitle"],
            item_count=content_details.get("itemCount", 0),
            privacy_status=item.get("status", {}).get("privacyStatus", "private"),
            thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
        )

    def get_user_info(self) -> Dict[str, Any]:
        """Get profile/channel info of the authenticated user."""
        params = {"part": "snippet", "mine": "true"}
        data = self._make_request("GET", "/channels", params=params)
        if data.get("items"):
            return data["items"][0]
        return {}


