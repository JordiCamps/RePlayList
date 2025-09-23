"""Core CLI class for RePlayList command line interface."""

import json
import logging
from typing import Optional
from pathlib import Path

from replaylist.config import config
from replaylist.auth import auth_manager
from replaylist.spotify import SpotifyAPI
from replaylist.youtube import YouTubeAPI
from replaylist.transfer import PlaylistTransfer
from replaylist.utils import setup_logging, create_success_response, create_error_response

from .types import CLIConfig
from .auth import AuthHandler
from .playlists import PlaylistHandler
from .transfer import TransferHandler
from .search import SearchHandler


logger = setup_logging()


class RePlayListCLI:
    """
    Command line interface for RePlayList.
    
    This class provides a comprehensive CLI for managing playlists across
    Spotify and YouTube platforms, including authentication, playlist
    management, and transfer operations.
    """
    
    def __init__(self):
        """
        Initialize CLI with token management and handler instances.
        
        Sets up the CLI configuration, loads existing tokens, and initializes
        all handler classes for different operations.
        """
        self.config = CLIConfig()
        self._load_tokens()
        
        # Initialize handlers
        self.auth_handler = AuthHandler(self.config)
        self.playlist_handler = PlaylistHandler(self.config)
        self.transfer_handler = TransferHandler(self.config)
        self.search_handler = SearchHandler(self.config)
    
    def _load_tokens(self) -> None:
        """
        Load authentication tokens from the tokens file.
        
        Attempts to load previously saved tokens for both Spotify and YouTube
        platforms. If the file doesn't exist or is corrupted, tokens will
        remain None and authentication will be required.
        
        Raises:
            No exceptions are raised - errors are logged as warnings.
        """
        try:
            if self.config.tokens_file.exists():
                with open(self.config.tokens_file, 'r') as f:
                    tokens = json.load(f)
                    self.config.from_dict(tokens)
                    logger.info("Successfully loaded tokens from file")
        except Exception as e:
            print(f"Warning: Could not load tokens: {e}")
            logger.warning(f"Failed to load tokens: {e}")
    
    def _save_tokens(self) -> None:
        """
        Save current authentication tokens to the tokens file.
        
        Persists the current Spotify and YouTube tokens to disk for future
        use. This allows users to avoid re-authentication on subsequent runs.
        
        Raises:
            No exceptions are raised - errors are logged as warnings.
        """
        try:
            with open(self.config.tokens_file, 'w') as f:
                json.dump(self.config.to_dict(), f)
                logger.info("Successfully saved tokens to file")
        except Exception as e:
            print(f"Warning: Could not save tokens: {e}")
            logger.warning(f"Failed to save tokens: {e}")
    
    def authenticate_platform(self, platform: str) -> bool:
        """
        Authenticate with a platform.
        
        Initiates OAuth authentication flow for the specified platform.
        Upon successful authentication, the access token is stored and
        persisted for future use.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            
        Returns:
            True if authentication was successful, False otherwise
            
        Example:
            >>> cli = RePlayListCLI()
            >>> success = cli.authenticate_platform('spotify')
            >>> if success:
            ...     print("Ready to use Spotify!")
        """
        return self.auth_handler.authenticate_platform(platform, self._save_tokens)
    
    def list_playlists(self, platform: str) -> None:
        """
        List playlists for the specified platform.
        
        Displays a formatted list of all playlists accessible to the
        authenticated user on the specified platform.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            
        Raises:
            Exception: If authentication fails or API request fails
        """
        self.playlist_handler.list_playlists(platform)
    
    def show_playlist_tracks(self, platform: str, playlist_id: str) -> None:
        """
        Show tracks in a specific playlist.
        
        Displays detailed information about all tracks in the specified
        playlist, including title, artist, duration, and other metadata.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            playlist_id: Unique identifier for the playlist
            
        Raises:
            Exception: If authentication fails or playlist is not found
        """
        self.playlist_handler.show_playlist_tracks(platform, playlist_id)
    
    def preview_transfer(
        self,
        source_platform: str,
        source_playlist_id: str,
        target_platform: str,
        target_playlist_id: Optional[str] = None,
        mode: str = 'new_playlist'
    ) -> None:
        """
        Preview a playlist transfer without executing it.
        
        Shows what tracks would be transferred and provides matching
        statistics without actually performing the transfer operation.
        
        Args:
            source_platform: Source platform name ('spotify' or 'youtube')
            source_playlist_id: Source playlist identifier
            target_platform: Target platform name ('spotify' or 'youtube')
            target_playlist_id: Target playlist ID for append mode
            mode: Transfer mode ('new_playlist' or 'append')
            
        Raises:
            Exception: If authentication fails or transfer preview fails
        """
        self.transfer_handler.preview_transfer(
            source_platform, source_playlist_id, target_platform,
            target_playlist_id, mode
        )
    
    def transfer_playlist(
        self,
        source_platform: str,
        source_playlist_id: str,
        target_platform: str,
        target_playlist_id: Optional[str] = None,
        mode: str = 'new_playlist',
        custom_name: Optional[str] = None
    ) -> None:
        """
        Transfer a playlist from source to target platform.
        
        Performs the actual transfer operation, creating a new playlist
        or appending to an existing one based on the specified mode.
        
        Args:
            source_platform: Source platform name ('spotify' or 'youtube')
            source_playlist_id: Source playlist identifier
            target_platform: Target platform name ('spotify' or 'youtube')
            target_playlist_id: Target playlist ID for append mode
            mode: Transfer mode ('new_playlist' or 'append')
            custom_name: Custom name for new playlist (new_playlist mode only)
            
        Raises:
            Exception: If authentication fails or transfer fails
        """
        self.transfer_handler.transfer_playlist(
            source_platform, source_playlist_id, target_platform,
            target_playlist_id, mode, custom_name
        )
    
    def search_tracks(self, platform: str, query: str) -> None:
        """
        Search for tracks on the specified platform.
        
        Performs a search query and displays matching tracks with their
        metadata, useful for finding specific songs or artists.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            query: Search query string
            
        Raises:
            Exception: If authentication fails or search fails
        """
        self.search_handler.search_tracks(platform, query)
