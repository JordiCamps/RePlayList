"""Pydantic models for the RePlayList API."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    """Authentication request model."""
    platform: str = Field(..., description="Platform name (spotify or youtube)")


class AuthResponse(BaseModel):
    """Authentication response model."""
    success: bool
    auth_url: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None


class TokenExchangeRequest(BaseModel):
    """Token exchange request model."""
    platform: str = Field(..., description="Platform name")
    code: str = Field(..., description="Authorization code")


class PlaylistInfo(BaseModel):
    """Playlist information model."""
    id: str
    name: str
    description: str
    owner: str
    tracks_count: int
    platform: str


class TrackInfo(BaseModel):
    """Track information model."""
    id: str
    title: str
    artists: List[str]
    album: str
    duration: str
    platform: str


class TransferRequest(BaseModel):
    """Transfer request model."""
    source: Dict[str, str] = Field(..., description="Source platform and playlist ID")
    target: Dict[str, Any] = Field(..., description="Target platform and optional playlist ID")
    mode: str = Field(default="new_playlist", description="Transfer mode (new_playlist or append)")
    custom_playlist_name: Optional[str] = Field(None, description="Custom name for new playlist")


class TransferResponse(BaseModel):
    """Transfer response model."""
    transfer_id: str
    status: str


class ProgressResponse(BaseModel):
    """Progress response model."""
    transfer_id: str
    status: str
    completed: int
    total: int
    current_track: str
    error_message: Optional[str] = None


class SummaryResponse(BaseModel):
    """Summary response model."""
    transfer_id: str
    status: str
    source_playlist: Dict[str, Any]
    target_playlist: Dict[str, Any]
    success_count: int
    fail_count: int
    failed_tracks: List[Dict[str, Any]]
    skipped_tracks: List[Dict[str, Any]]
    created_playlist: Optional[Dict[str, Any]] = None
