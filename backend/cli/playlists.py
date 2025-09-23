"""Playlist operations handler for CLI."""

from typing import Optional
from replaylist.spotify import SpotifyAPI
from replaylist.youtube import YouTubeAPI
from .types import CLIConfig
from .auth import AuthHandler


class PlaylistHandler:
    """
    Handles playlist-related operations for the CLI.
    
    This class manages playlist listing, track viewing, and provides
    formatted output for playlist information across different platforms.
    """
    
    def __init__(self, config: CLIConfig):
        """
        Initialize the playlist handler.
        
        Args:
            config: CLI configuration containing token management settings.
        """
        self.config = config
        self.auth_handler = AuthHandler(config)
    
    def list_playlists(self, platform: str) -> None:
        """
        List playlists for a platform.
        
        Displays a formatted list of all playlists accessible to the
        authenticated user on the specified platform, including metadata
        such as track count, owner, and privacy status.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            
        Raises:
            Exception: If authentication fails or API request fails
            
        Example:
            >>> handler = PlaylistHandler(config)
            >>> handler.list_playlists('spotify')
            Spotify Playlists (5):
            --------------------------------------------------
             1. My Favorites
                ID: 37i9dQZF1DXcBWIGoYBM5M
                Tracks: 50
                Owner: user123
                Public: Yes
        """
        try:
            if platform.lower() == 'spotify':
                self._list_spotify_playlists()
            elif platform.lower() == 'youtube':
                self._list_youtube_playlists()
            else:
                print(f"Unsupported platform: {platform}")
                
        except Exception as e:
            print(f"Error listing playlists: {e}")
    
    def _list_spotify_playlists(self) -> None:
        """
        List Spotify playlists.
        
        Internal method to handle Spotify-specific playlist listing.
        Checks authentication and displays formatted playlist information.
        """
        if not self.auth_handler.is_authenticated('spotify'):
            print("Not authenticated with Spotify. Run 'auth spotify' first.")
            return
        
        api = SpotifyAPI(self.config.spotify_token)
        playlists = api.get_user_playlists()
        
        print(f"\nSpotify Playlists ({len(playlists)}):")
        print("-" * 50)
        for i, playlist in enumerate(playlists, 1):
            print(f"{i:2d}. {playlist.name}")
            print(f"    ID: {playlist.id}")
            print(f"    Tracks: {playlist.tracks_count}")
            print(f"    Owner: {playlist.owner}")
            print(f"    Public: {'Yes' if playlist.public else 'No'}")
            print()
    
    def _list_youtube_playlists(self) -> None:
        """
        List YouTube playlists.
        
        Internal method to handle YouTube-specific playlist listing.
        Checks authentication and displays formatted playlist information.
        """
        if not self.auth_handler.is_authenticated('youtube'):
            print("Not authenticated with YouTube. Run 'auth youtube' first.")
            return
        
        api = YouTubeAPI(self.config.youtube_token)
        playlists = api.get_user_playlists()
        
        print(f"\nYouTube Playlists ({len(playlists)}):")
        print("-" * 50)
        for i, playlist in enumerate(playlists, 1):
            print(f"{i:2d}. {playlist.title}")
            print(f"    ID: {playlist.id}")
            print(f"    Videos: {playlist.item_count}")
            print(f"    Channel: {playlist.channel_title}")
            print(f"    Privacy: {playlist.privacy_status}")
            print()
    
    def show_playlist_tracks(self, platform: str, playlist_id: str) -> None:
        """
        Show tracks in a playlist.
        
        Displays detailed information about all tracks in the specified
        playlist, including title, artist, duration, and other metadata
        specific to each platform.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            playlist_id: Unique identifier for the playlist
            
        Raises:
            Exception: If authentication fails or playlist is not found
            
        Example:
            >>> handler = PlaylistHandler(config)
            >>> handler.show_playlist_tracks('spotify', '37i9dQZF1DXcBWIGoYBM5M')
            Spotify Playlist Tracks (25):
            ------------------------------------------------------------
              1. Bohemian Rhapsody
                 Artists: Queen
                 Album: A Night at the Opera
                 Duration: 5:55
        """
        try:
            if platform.lower() == 'spotify':
                self._show_spotify_tracks(playlist_id)
            elif platform.lower() == 'youtube':
                self._show_youtube_tracks(playlist_id)
            else:
                print(f"Unsupported platform: {platform}")
                
        except Exception as e:
            print(f"Error showing playlist tracks: {e}")
    
    def _show_spotify_tracks(self, playlist_id: str) -> None:
        """
        Show tracks in a Spotify playlist.
        
        Internal method to handle Spotify-specific track listing.
        Displays track information including artists, album, and duration.
        
        Args:
            playlist_id: Spotify playlist identifier
        """
        if not self.auth_handler.is_authenticated('spotify'):
            print("Not authenticated with Spotify.")
            return
        
        api = SpotifyAPI(self.config.spotify_token)
        tracks = api.get_playlist_tracks(playlist_id)
        
        print(f"\nSpotify Playlist Tracks ({len(tracks)}):")
        print("-" * 60)
        for i, track in enumerate(tracks, 1):
            print(f"{i:3d}. {track.name}")
            print(f"     Artists: {', '.join(track.artists)}")
            print(f"     Album: {track.album}")
            print(f"     Duration: {track.duration_ms // 60000}:{(track.duration_ms % 60000) // 1000:02d}")
            print()
    
    def _show_youtube_tracks(self, playlist_id: str) -> None:
        """
        Show tracks in a YouTube playlist.
        
        Internal method to handle YouTube-specific track listing.
        Displays video information including channel, duration, and publish date.
        
        Args:
            playlist_id: YouTube playlist identifier
        """
        if not self.auth_handler.is_authenticated('youtube'):
            print("Not authenticated with YouTube.")
            return
        
        api = YouTubeAPI(self.config.youtube_token)
        videos = api.get_playlist_videos(playlist_id)
        
        print(f"\nYouTube Playlist Videos ({len(videos)}):")
        print("-" * 60)
        for i, video in enumerate(videos, 1):
            print(f"{i:3d}. {video.title}")
            print(f"     Channel: {video.channel_title}")
            print(f"     Duration: {video.duration}")
            print(f"     Published: {video.published_at}")
            print()
