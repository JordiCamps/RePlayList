"""Playlist operations for transfers."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from ..spotify import SpotifyAPI
from ..youtube import YouTubeAPI

logger = logging.getLogger(__name__)


class PlaylistManager:
    """Handles playlist operations for transfers."""
    
    def __init__(self, spotify_api: SpotifyAPI, youtube_api: YouTubeAPI):
        """
        Initialize playlist manager.
        
        Args:
            spotify_api: Spotify API client
            youtube_api: YouTube API client
        """
        self.spotify_api = spotify_api
        self.youtube_api = youtube_api
    
    def get_source_playlist(self, platform: str, playlist_id: str) -> Tuple[Dict[str, Any], List[Any]]:
        """
        Get source playlist and its tracks.
        
        Args:
            platform: Platform name ('spotify' or 'youtube')
            playlist_id: Playlist ID
            
        Returns:
            Tuple of (playlist_info, tracks)
            
        Raises:
            ValueError: If platform is unsupported or playlist not found
        """
        if platform.lower() == 'spotify':
            playlist = self.spotify_api.get_playlist_info(playlist_id)
            if not playlist:
                raise ValueError(f"Spotify playlist {playlist_id} not found")
            
            tracks = self.spotify_api.get_playlist_tracks(playlist_id)
            
            return {
                'id': playlist.id,
                'name': playlist.name,
                'description': playlist.description,
                'owner': playlist.owner,
                'tracks_count': playlist.tracks_count,
                'platform': 'spotify'
            }, tracks
            
        elif platform.lower() == 'youtube':
            playlist = self.youtube_api.get_playlist_info(playlist_id)
            if not playlist:
                raise ValueError(f"YouTube playlist {playlist_id} not found")
            
            videos = self.youtube_api.get_playlist_videos(playlist_id)
            
            return {
                'id': playlist.id,
                'name': playlist.title,
                'description': playlist.description,
                'owner': playlist.channel_title,
                'tracks_count': playlist.item_count,
                'platform': 'youtube'
            }, videos
            
        else:
            raise ValueError(f"Unsupported source platform: {platform}")
    
    def get_or_create_target_playlist(
        self, 
        platform: str, 
        playlist_id: Optional[str], 
        source_playlist: Dict[str, Any], 
        mode: str,
        custom_playlist_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get existing or create new target playlist.
        
        Args:
            platform: Target platform ('spotify' or 'youtube')
            playlist_id: Existing playlist ID (for append mode)
            source_playlist: Source playlist info
            mode: Transfer mode ('new_playlist' or 'append')
            custom_playlist_name: Custom name for new playlist
            
        Returns:
            Target playlist info
            
        Raises:
            ValueError: If platform is unsupported or playlist not found
        """
        if mode == "append" and playlist_id:
            # Use existing playlist
            if platform.lower() == 'spotify':
                playlist = self.spotify_api.get_playlist_info(playlist_id)
                if not playlist:
                    raise ValueError(f"Spotify playlist {playlist_id} not found")
                
                return {
                    'id': playlist.id,
                    'name': playlist.name,
                    'description': playlist.description,
                    'platform': 'spotify'
                }
                
            elif platform.lower() == 'youtube':
                playlist = self.youtube_api.get_playlist_info(playlist_id)
                if not playlist:
                    raise ValueError(f"YouTube playlist {playlist_id} not found")
                
                return {
                    'id': playlist.id,
                    'name': playlist.title,
                    'description': playlist.description,
                    'platform': 'youtube'
                }
        
        # Create new playlist
        if custom_playlist_name:
            from .naming import PlaylistNamer
            namer = PlaylistNamer()
            playlist_name = namer.validate_and_sanitize_playlist_name(custom_playlist_name, platform)
        else:
            # Generate default name
            default_name = f"Transferred from {source_playlist['name']}"
            from .naming import PlaylistNamer
            namer = PlaylistNamer()
            playlist_name = namer.validate_and_sanitize_playlist_name(default_name, platform)
        
        playlist_description = f"Transferred from {source_playlist['platform']} playlist: {source_playlist['description']}"
        
        if platform.lower() == 'spotify':
            playlist = self.spotify_api.create_playlist(playlist_name, playlist_description)
            return {
                'id': playlist.id,
                'name': playlist.name,
                'description': playlist.description,
                'platform': 'spotify'
            }
            
        elif platform.lower() == 'youtube':
            playlist = self.youtube_api.create_playlist(playlist_name, playlist_description)
            return {
                'id': playlist.id,
                'name': playlist.title,
                'description': playlist.description,
                'platform': 'youtube'
            }
        
        else:
            raise ValueError(f"Unsupported target platform: {platform}")
    
    def add_track_to_playlist(self, track: Any, platform: str, playlist_id: str) -> None:
        """
        Add track to target playlist.
        
        Args:
            track: Track object
            platform: Platform name
            playlist_id: Target playlist ID
            
        Raises:
            ValueError: If platform is unsupported
        """
        if platform.lower() == 'spotify':
            track_uri = f"spotify:track:{track.id}"
            self.spotify_api.add_tracks_to_playlist(playlist_id, [track_uri])
            
        elif platform.lower() == 'youtube':
            self.youtube_api.add_video_to_playlist(playlist_id, track.id)
        
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def get_existing_tracks(self, platform: str, playlist_id: str) -> List[Any]:
        """
        Get existing tracks from target playlist for duplicate checking.
        
        Args:
            platform: Platform name
            playlist_id: Playlist ID
            
        Returns:
            List of existing tracks
        """
        try:
            if platform.lower() == 'spotify':
                return self.spotify_api.get_playlist_tracks(playlist_id)
            elif platform.lower() == 'youtube':
                return self.youtube_api.get_playlist_videos(playlist_id)
            else:
                logger.warning(f"Unsupported platform for getting existing tracks: {platform}")
                return []
        except Exception as e:
            logger.warning(f"Could not fetch existing tracks from target playlist: {e}")
            return []
