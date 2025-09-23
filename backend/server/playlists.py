"""Playlist endpoints for the RePlayList API."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from replaylist.spotify import SpotifyAPI
from replaylist.youtube import YouTubeAPI
from .models import PlaylistInfo, TrackInfo
from .state import user_tokens

logger = logging.getLogger(__name__)

# Create router for playlist endpoints
router = APIRouter(prefix="/playlists", tags=["playlists"])


def get_user_id() -> str:
    """Get current user ID (simplified for demo)."""
    return "default_user"


@router.get("/{platform}", response_model=List[PlaylistInfo])
async def get_playlists(platform: str):
    """
    Get user's playlists for a platform.
    
    Args:
        platform: Platform name (spotify or youtube)
        
    Returns:
        List of playlists
    """
    try:
        user_id = get_user_id()
        token = user_tokens.get(user_id, {}).get(platform.lower())
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        if platform.lower() == 'spotify':
            api = SpotifyAPI(token)
            playlists = api.get_user_playlists()
            
            return [
                PlaylistInfo(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    owner=p.owner,
                    tracks_count=p.tracks_count,
                    platform='spotify'
                )
                for p in playlists
            ]
            
        elif platform.lower() == 'youtube':
            api = YouTubeAPI(token)
            playlists = api.get_user_playlists()
            
            return [
                PlaylistInfo(
                    id=p.id,
                    name=p.title,
                    description=p.description,
                    owner=p.channel_title,
                    tracks_count=p.item_count,
                    platform='youtube'
                )
                for p in playlists
            ]
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")
            
    except Exception as e:
        logger.error(f"Failed to get playlists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{platform}/{playlist_id}", response_model=List[TrackInfo])
async def get_playlist_tracks(platform: str, playlist_id: str):
    """
    Get tracks from a playlist.
    
    Args:
        platform: Platform name
        playlist_id: Playlist ID
        
    Returns:
        List of tracks
    """
    try:
        user_id = get_user_id()
        token = user_tokens.get(user_id, {}).get(platform.lower())
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        if platform.lower() == 'spotify':
            api = SpotifyAPI(token)
            tracks = api.get_playlist_tracks(playlist_id)
            
            return [
                TrackInfo(
                    id=t.id,
                    title=t.name,
                    artists=t.artists,
                    album=t.album,
                    duration=f"{t.duration_ms // 60000}:{(t.duration_ms % 60000) // 1000:02d}",
                    platform='spotify'
                )
                for t in tracks
            ]
            
        elif platform.lower() == 'youtube':
            api = YouTubeAPI(token)
            videos = api.get_playlist_videos(playlist_id)
            
            return [
                TrackInfo(
                    id=v.id,
                    title=v.title,
                    artists=[v.channel_title],
                    album="",
                    duration=v.duration,
                    platform='youtube'
                )
                for v in videos
            ]
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")
            
    except Exception as e:
        logger.error(f"Failed to get playlist tracks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
