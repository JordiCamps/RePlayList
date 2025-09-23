"""Search operations handler for CLI."""

from typing import Optional
from replaylist.spotify import SpotifyAPI
from replaylist.youtube import YouTubeAPI
from .types import CLIConfig
from .auth import AuthHandler


class SearchHandler:
    """
    Handles search operations for the CLI.
    
    This class manages track and video search across different platforms,
    providing formatted output for search results.
    """
    
    def __init__(self, config: CLIConfig):
        """
        Initialize the search handler.
        
        Args:
            config: CLI configuration containing token management settings.
        """
        self.config = config
        self.auth_handler = AuthHandler(config)
    
    def search_tracks(self, platform: str, query: str) -> None:
        """
        Search for tracks on a platform.
        
        Performs a search query on the specified platform and displays
        formatted results including track metadata and identifiers.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            query: Search query string
            
        Raises:
            Exception: If authentication fails or search fails
            
        Example:
            >>> handler = SearchHandler(config)
            >>> handler.search_tracks('spotify', 'bohemian rhapsody')
            Spotify Search Results for 'bohemian rhapsody' (10):
            ------------------------------------------------------------
             1. Bohemian Rhapsody
                Artists: Queen
                Album: A Night at the Opera
                ID: 4uLU6hMCjMI75M1A2tKUQC
        """
        try:
            if platform.lower() == 'spotify':
                self._search_spotify_tracks(query)
            elif platform.lower() == 'youtube':
                self._search_youtube_videos(query)
            else:
                print(f"Unsupported platform: {platform}")
                
        except Exception as e:
            print(f"Search error: {e}")
    
    def _search_spotify_tracks(self, query: str) -> None:
        """
        Search for tracks on Spotify.
        
        Internal method to handle Spotify-specific track search.
        Displays formatted track information including artists, album, and ID.
        
        Args:
            query: Search query string
        """
        if not self.auth_handler.is_authenticated('spotify'):
            print("Not authenticated with Spotify.")
            return
        
        api = SpotifyAPI(self.config.spotify_token)
        tracks = api.search_tracks(query)
        
        print(f"\nSpotify Search Results for '{query}' ({len(tracks)}):")
        print("-" * 60)
        for i, track in enumerate(tracks, 1):
            print(f"{i:2d}. {track.name}")
            print(f"    Artists: {', '.join(track.artists)}")
            print(f"    Album: {track.album}")
            print(f"    ID: {track.id}")
            print()
    
    def _search_youtube_videos(self, query: str) -> None:
        """
        Search for videos on YouTube.
        
        Internal method to handle YouTube-specific video search.
        Displays formatted video information including channel and ID.
        
        Args:
            query: Search query string
        """
        if not self.auth_handler.is_authenticated('youtube'):
            print("Not authenticated with YouTube.")
            return
        
        api = YouTubeAPI(self.config.youtube_token)
        videos = api.search_videos(query)
        
        print(f"\nYouTube Search Results for '{query}' ({len(videos)}):")
        print("-" * 60)
        for i, video in enumerate(videos, 1):
            print(f"{i:2d}. {video.title}")
            print(f"    Channel: {video.channel_title}")
            print(f"    ID: {video.id}")
            print()
