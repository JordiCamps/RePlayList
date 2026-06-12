"""Library extract/update handler for the CLI."""

from replaylist.spotify import SpotifyAPI
from replaylist.store import LibraryExtractor
from replaylist.youtube import YouTubeAPI

from .auth import AuthHandler
from .types import CLIConfig


class StoreHandler:
    """Handles local extraction and incremental update of a user's library."""

    def __init__(self, config: CLIConfig):
        self.config = config
        self.auth_handler = AuthHandler(config)

    def _build_extractor(self, platform: str):
        """Return a LibraryExtractor for an authenticated platform, or None."""
        platform = platform.lower()
        if platform == "spotify":
            if not self.auth_handler.is_authenticated("spotify"):
                print("Not authenticated with Spotify. Run 'auth spotify' first.")
                return None
            return LibraryExtractor(spotify_api=SpotifyAPI(self.config.spotify_token))
        if platform == "youtube":
            if not self.auth_handler.is_authenticated("youtube"):
                print("Not authenticated with YouTube. Run 'auth youtube' first.")
                return None
            return LibraryExtractor(youtube_api=YouTubeAPI(self.config.youtube_token))
        print(f"Unsupported platform: {platform}")
        return None

    def extract(self, platform: str) -> None:
        """Fully extract all playlists and tracks for the authenticated account."""
        extractor = self._build_extractor(platform)
        if not extractor:
            return
        try:
            print(f"Extracting {platform} library...")
            result = extractor.extract(platform, progress=lambda m: print(f"  {m}"))
            account = result["account"]
            print(
                f"\nExtracted {result['playlists']} playlists for "
                f"{account['display_name']} ({account['account_id']})."
            )
            if result.get("failed"):
                print(f"  ({result['failed']} playlist(s) skipped - tracks not accessible)")
            print(f"Saved to: {result['data_dir']}")
        except Exception as e:  # noqa: BLE001
            print(f"Error extracting library: {e}")

    def update(self, platform: str) -> None:
        """Incrementally update the local library, re-fetching only what changed."""
        extractor = self._build_extractor(platform)
        if not extractor:
            return
        try:
            print(f"Updating {platform} library...")
            result = extractor.update(platform, progress=lambda m: print(f"  {m}"))
            print(
                f"\nUpdate complete ({platform}): "
                f"{result['new']} new, {result['changed']} changed, "
                f"{result['unchanged']} unchanged, {result['removed']} removed."
            )
            if result.get("failed"):
                print(f"  ({result['failed']} playlist(s) skipped - tracks not accessible)")
            print(f"Data dir: {result['data_dir']}")
        except Exception as e:  # noqa: BLE001
            print(f"Error updating library: {e}")
