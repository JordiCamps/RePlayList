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

    def _build_extractor(self, platform: str, account_id=None):
        """Return a LibraryExtractor for a platform account, or None."""
        platform = platform.lower()
        token = self.config.get_token(platform, account_id)
        if not token:
            who = account_id or "active"
            print(f"No {platform} token for account '{who}'. Run 'auth {platform}' or check 'accounts'.")
            return None
        if platform == "spotify":
            return LibraryExtractor(spotify_api=SpotifyAPI(token))
        if platform == "youtube":
            return LibraryExtractor(youtube_api=YouTubeAPI(token))
        print(f"Unsupported platform: {platform}")
        return None

    def extract(self, platform: str, account_id=None) -> None:
        """Fully extract all playlists and tracks for an account."""
        extractor = self._build_extractor(platform, account_id)
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

    def update(self, platform: str, account_id=None) -> None:
        """Incrementally update the local library, re-fetching only what changed."""
        extractor = self._build_extractor(platform, account_id)
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
