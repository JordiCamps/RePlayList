"""Track matching logic for playlist transfers."""

import logging
from typing import Any, Optional, Tuple

from ..spotify import SpotifyAPI
from ..youtube import YouTubeAPI

logger = logging.getLogger(__name__)


class TrackMatcher:
    """Handles track matching between platforms."""
    
    def __init__(self, spotify_api: SpotifyAPI, youtube_api: YouTubeAPI):
        """
        Initialize track matcher.
        
        Args:
            spotify_api: Spotify API client
            youtube_api: YouTube API client
        """
        self.spotify_api = spotify_api
        self.youtube_api = youtube_api
    
    def find_matching_track(self, source_track: Any, source_platform: str, target_platform: str) -> Optional[Any]:
        """
        Find matching track on target platform.
        
        Args:
            source_track: Source track object
            source_platform: Source platform ('spotify' or 'youtube')
            target_platform: Target platform ('spotify' or 'youtube')
            
        Returns:
            Matching track on target platform, or None if not found
        """
        if source_platform.lower() == 'spotify' and target_platform.lower() == 'youtube':
            # Spotify to YouTube
            spotify_track = source_track
            return self.youtube_api.find_video_by_metadata(
                spotify_track.name,
                ', '.join(spotify_track.artists),
                spotify_track.album
            )
            
        elif source_platform.lower() == 'youtube' and target_platform.lower() == 'spotify':
            # YouTube to Spotify
            youtube_video = source_track
            # Extract artist and title from YouTube video title
            extracted_artist, extracted_title = self._extract_artist_and_title_from_youtube_title(youtube_video.title)
            return self.spotify_api.find_track_by_metadata(
                extracted_title,
                extracted_artist
            )
            
        elif source_platform.lower() == target_platform.lower():
            # Same platform transfer (copy within platform)
            return source_track
        
        else:
            raise ValueError(f"Unsupported transfer: {source_platform} to {target_platform}")
    
    def _extract_artist_and_title_from_youtube_title(self, title: str) -> Tuple[str, str]:
        """
        Extract artist and song title from YouTube video title.
        
        Common patterns:
        - "Artist - Song Title"
        - "Artist: Song Title" 
        - "Song Title - Artist"
        - "Song Title by Artist"
        - "Artist | Song Title"
        - "Song Title (Artist)"
        - "Artist - Song Title (Official Video)"
        - "Song Title - Artist (Lyrics)"
        
        Args:
            title: YouTube video title
            
        Returns:
            Tuple of (artist, song_title)
        """
        if not title:
            return "", ""
        
        import re
        
        # Clean the title first
        cleaned_title = title.strip()
        
        # Common separators in order of preference
        separators = [
            r'\s*-\s*',  # dash
            r'\s*:\s*',  # colon
            r'\s*\|\s*',  # pipe
            r'\s+by\s+',  # "by"
            r'\s+\(',  # opening parenthesis
        ]
        
        # Try each separator
        for separator in separators:
            parts = re.split(separator, cleaned_title, 1)
            if len(parts) == 2:
                part1, part2 = parts
                
                # Clean up the parts
                part1 = part1.strip()
                part2 = part2.strip()
                
                # Remove common suffixes from part2
                part2 = re.sub(r'\s*\(.*?\)\s*$', '', part2)  # Remove trailing parentheses
                part2 = re.sub(r'\s*\[.*?\]\s*$', '', part2)  # Remove trailing brackets
                part2 = re.sub(r'\s*(official|lyrics|audio|video|hq|hd|4k|remastered|live|acoustic|cover).*$', '', part2, flags=re.IGNORECASE)
                
                # Heuristic: if part1 is shorter and part2 is longer, part1 is likely artist
                if len(part1) < len(part2) and len(part1) < 50:
                    return part1, part2
                # If part2 is shorter and part1 is longer, part2 is likely artist
                elif len(part2) < len(part1) and len(part2) < 50:
                    return part2, part1
                # If similar length, assume first part is artist (common pattern)
                else:
                    return part1, part2
        
        # If no separator found, try to extract from common patterns
        # Look for "Song Title (Artist)" pattern
        paren_match = re.match(r'^(.+?)\s*\(([^)]+)\)', cleaned_title)
        if paren_match:
            song_title = paren_match.group(1).strip()
            artist = paren_match.group(2).strip()
            return artist, song_title
        
        # Look for "Artist - Song Title" at the beginning
        dash_match = re.match(r'^([^-]+?)\s*-\s*(.+)$', cleaned_title)
        if dash_match:
            artist = dash_match.group(1).strip()
            song_title = dash_match.group(2).strip()
            # Clean up song title
            song_title = re.sub(r'\s*\(.*?\)\s*$', '', song_title)
            song_title = re.sub(r'\s*\[.*?\]\s*$', '', song_title)
            return artist, song_title
        
        # If all else fails, return the title as song title and empty artist
        # The search algorithm will try multiple strategies
        return "", cleaned_title
    
    def get_track_key(self, track: Any, platform: str) -> str:
        """
        Get a unique key for a track to detect duplicates.
        
        Args:
            track: Track object
            platform: Platform name
            
        Returns:
            Unique key string
        """
        if platform.lower() == 'spotify':
            # For Spotify tracks, use the track ID
            return f"spotify:{track.id}"
        elif platform.lower() == 'youtube':
            # For YouTube videos, use the video ID
            return f"youtube:{track.id}"
        else:
            # Fallback to string representation
            return str(track)
    
    def get_track_display_name(self, track: Any, platform: str) -> str:
        """
        Get a display name for a track.
        
        Args:
            track: Track object
            platform: Platform name
            
        Returns:
            Display name string
        """
        if platform.lower() == 'spotify':
            return f"{track.name} - {', '.join(track.artists)}"
        elif platform.lower() == 'youtube':
            return f"{track.title} - {track.channel_title}"
        else:
            return str(track)
    
    def is_duplicate_track(self, track1: Any, track2: Any, platform: str) -> bool:
        """
        Check if two tracks are duplicates based on metadata.
        
        Args:
            track1: First track data
            track2: Second track data
            platform: Platform name
            
        Returns:
            True if tracks are duplicates
        """
        if platform.lower() == 'spotify':
            # Compare by ID first (most reliable)
            if hasattr(track1, 'id') and hasattr(track2, 'id') and track1.id == track2.id:
                return True
            
            # Compare by name and artists (fuzzy matching)
            name1 = getattr(track1, 'name', '').lower().strip()
            name2 = getattr(track2, 'name', '').lower().strip()
            artists1 = [a.lower().strip() for a in getattr(track1, 'artists', [])]
            artists2 = [a.lower().strip() for a in getattr(track2, 'artists', [])]
            
            if name1 == name2 and set(artists1) == set(artists2):
                return True
        
        elif platform.lower() == 'youtube':
            # Compare by ID first (most reliable)
            if hasattr(track1, 'id') and hasattr(track2, 'id') and track1.id == track2.id:
                return True
            
            # Compare by title and channel
            title1 = getattr(track1, 'title', '').lower().strip()
            title2 = getattr(track2, 'title', '').lower().strip()
            channel1 = getattr(track1, 'channel_title', '').lower().strip()
            channel2 = getattr(track2, 'channel_title', '').lower().strip()
            
            if title1 == title2 and channel1 == channel2:
                return True
        
        return False
