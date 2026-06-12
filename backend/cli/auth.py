"""Authentication handler for CLI operations."""

from typing import Callable, Optional
from replaylist.auth import auth_manager
from .types import CLIConfig


class AuthHandler:
    """
    Handles authentication operations for the CLI.
    
    This class manages platform authentication, token storage, and
    provides a clean interface for authentication-related CLI operations.
    """
    
    def __init__(self, config: CLIConfig):
        """
        Initialize the authentication handler.
        
        Args:
            config: CLI configuration containing token management settings.
        """
        self.config = config
    
    def authenticate_platform(self, platform: str, save_callback: Callable[[], None]) -> bool:
        """
        Authenticate with a platform.
        
        Initiates OAuth authentication flow for the specified platform.
        Upon successful authentication, the access token is stored in the
        configuration and the save callback is invoked to persist the token.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            save_callback: Callback function to save tokens after successful auth
            
        Returns:
            True if authentication was successful, False otherwise
            
        Example:
            >>> handler = AuthHandler(config)
            >>> success = handler.authenticate_platform('spotify', save_tokens)
            >>> if success:
            ...     print("Spotify authentication successful!")
        """
        try:
            print(f"Starting authentication with {platform}...")
            result = auth_manager.authenticate_platform(platform)

            if result.success:
                account_id, display_name = self._resolve_identity(platform, result.access_token)
                self.config.add_account(
                    platform,
                    account_id,
                    access_token=result.access_token,
                    refresh_token=result.refresh_token,
                    expires_in=result.expires_in,
                    display_name=display_name,
                )
                save_callback()
                print(f"Successfully authenticated with {platform} as {display_name} ({account_id})")
                return True
            else:
                print(f"Authentication failed: {result.error}")
                return False

        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def _resolve_identity(self, platform: str, token: Optional[str]) -> tuple:
        """
        Resolve the service account identity for a freshly obtained token.

        Used to key stored tokens by account so multiple accounts per platform
        can coexist.

        Args:
            platform: Platform name ('spotify' or 'youtube')
            token: Access token just obtained

        Returns:
            Tuple of (account_id, display_name). Falls back to ('default', ...)
            if the identity cannot be resolved.
        """
        try:
            if platform.lower() == 'spotify':
                from replaylist.spotify import SpotifyAPI
                me = SpotifyAPI(token).get_user_info()
                return me.get('id') or 'default', (me.get('display_name') or me.get('id') or 'default')
            else:
                from replaylist.youtube import YouTubeAPI
                channel = YouTubeAPI(token).get_user_info()
                return channel.get('id') or 'default', channel.get('snippet', {}).get('title', '') or 'default'
        except Exception as e:  # noqa: BLE001
            print(f"Warning: could not resolve account identity ({e}); storing as 'default'.")
            return 'default', 'default'
    
    def get_token(self, platform: str) -> Optional[str]:
        """
        Get the stored token for a platform.
        
        Retrieves the currently stored authentication token for the
        specified platform, if available.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            
        Returns:
            The stored token if available, None otherwise
        """
        if platform.lower() == 'spotify':
            return self.config.spotify_token
        elif platform.lower() == 'youtube':
            return self.config.youtube_token
        return None
    
    def is_authenticated(self, platform: str) -> bool:
        """
        Check if the user is authenticated with a platform.
        
        Verifies whether a valid token exists for the specified platform.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            
        Returns:
            True if authenticated, False otherwise
        """
        token = self.get_token(platform)
        return token is not None and token.strip() != ""
