"""Transfer endpoints for the RePlayList API."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from replaylist.transfer import PlaylistTransfer, TransferStatus
from .models import TransferRequest, TransferResponse, ProgressResponse, SummaryResponse
from .state import active_transfers, user_tokens

logger = logging.getLogger(__name__)

# Create router for transfer endpoints
router = APIRouter(prefix="/transfer", tags=["transfer"])


def get_user_id() -> str:
    """Get current user ID (simplified for demo)."""
    return "default_user"


def get_transfer_manager(user_id: str, source_platform: str, target_platform: str) -> PlaylistTransfer:
    """Get or create transfer manager for user."""
    user_token_data = user_tokens.get(user_id, {})
    source_token = user_token_data.get(source_platform)
    target_token = user_token_data.get(target_platform)
    
    if not source_token:
        raise HTTPException(status_code=401, detail=f"Not authenticated with {source_platform}")
    
    # For same-platform transfers, we only need one token
    if source_platform != target_platform and not target_token:
        raise HTTPException(status_code=401, detail=f"Not authenticated with {target_platform}")
    
    # Create a unique key for this transfer combination
    transfer_key = f"{user_id}_{source_platform}_{target_platform}"
    
    if transfer_key not in active_transfers:
        # Get all available tokens for the transfer manager
        spotify_token = user_token_data.get('spotify')
        youtube_token = user_token_data.get('youtube')
        
        active_transfers[transfer_key] = PlaylistTransfer(spotify_token, youtube_token)
    
    return active_transfers[transfer_key]


@router.post("/preview", response_model=dict)
async def preview_transfer(request: TransferRequest):
    """
    Preview what will be transferred without actually doing the transfer.
    
    Args:
        request: Transfer request
        
    Returns:
        Preview information including tracks that will be transferred
    """
    try:
        user_id = get_user_id()
        
        # Validate authentication for the required platforms
        user_token_data = user_tokens.get(user_id, {})
        source_token = user_token_data.get(request.source['platform'])
        target_token = user_token_data.get(request.target['platform'])
        
        if not source_token:
            raise HTTPException(status_code=401, detail=f"Not authenticated with {request.source['platform']}")
        
        if not target_token:
            raise HTTPException(status_code=401, detail=f"Not authenticated with {request.target['platform']}")
        
        # Get transfer manager
        transfer_manager = get_transfer_manager(user_id, request.source['platform'], request.target['platform'])
        
        # Preview transfer
        preview = transfer_manager.preview_transfer(
            request.source['platform'],
            request.source['playlist_id'],
            request.target['platform'],
            request.target.get('playlist_id'),
            request.mode
        )
        
        return preview
        
    except Exception as e:
        logger.error(f"Failed to preview transfer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start", response_model=TransferResponse)
async def start_transfer(request: TransferRequest):
    """
    Start a playlist transfer.
    
    Args:
        request: Transfer request
        
    Returns:
        Transfer response with transfer ID
    """
    try:
        user_id = get_user_id()
        logger.info(f"Starting transfer for user {user_id}")
        logger.info(f"Transfer request: {request}")
        
        # Validate authentication for the required platforms
        user_token_data = user_tokens.get(user_id, {})
        logger.info(f"User token data: {list(user_token_data.keys())}")
        
        source_token = user_token_data.get(request.source['platform'])
        target_token = user_token_data.get(request.target['platform'])
        
        if not source_token:
            logger.error(f"No token found for source platform: {request.source['platform']}")
            raise HTTPException(status_code=401, detail=f"Not authenticated with {request.source['platform']}")
        
        if not target_token:
            logger.error(f"No token found for target platform: {request.target['platform']}")
            raise HTTPException(status_code=401, detail=f"Not authenticated with {request.target['platform']}")
        
        logger.info("Authentication successful, proceeding with transfer")
        
        # Get transfer manager
        transfer_manager = get_transfer_manager(user_id, request.source['platform'], request.target['platform'])
        
        # Start transfer
        transfer_id = transfer_manager.start_transfer(
            source_platform=request.source['platform'],
            source_playlist_id=request.source['playlist_id'],
            target_platform=request.target['platform'],
            target_playlist_id=request.target.get('playlist_id'),
            mode=request.mode,
            custom_playlist_name=request.custom_playlist_name
        )
        
        return TransferResponse(transfer_id=transfer_id, status="started")
        
    except Exception as e:
        logger.error(f"Transfer start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{transfer_id}/progress", response_model=ProgressResponse)
async def get_transfer_progress(transfer_id: str):
    """
    Get transfer progress.
    
    Args:
        transfer_id: Transfer ID
        
    Returns:
        Progress information
    """
    try:
        user_id = get_user_id()
        
        # Find the transfer manager by looking through active transfers
        transfer_manager = None
        for key, manager in active_transfers.items():
            if key.startswith(f"{user_id}_"):
                transfer_manager = manager
                break
        
        if not transfer_manager:
            raise HTTPException(status_code=404, detail="No active transfers found")
        
        progress = transfer_manager.get_transfer_progress(transfer_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        return ProgressResponse(
            transfer_id=progress.transfer_id,
            status=progress.status.value,
            completed=progress.completed,
            total=progress.total,
            current_track=progress.current_track,
            error_message=progress.error_message
        )
        
    except Exception as e:
        logger.error(f"Failed to get transfer progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{transfer_id}/summary", response_model=SummaryResponse)
async def get_transfer_summary(transfer_id: str):
    """
    Get transfer summary.
    
    Args:
        transfer_id: Transfer ID
        
    Returns:
        Transfer summary
    """
    try:
        user_id = get_user_id()
        
        # Find the transfer manager by looking through active transfers
        transfer_manager = None
        for key, manager in active_transfers.items():
            if key.startswith(f"{user_id}_"):
                transfer_manager = manager
                break
        
        if not transfer_manager:
            raise HTTPException(status_code=404, detail="No active transfers found")
        
        result = transfer_manager.get_transfer_result(transfer_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Transfer result not found")
        
        return SummaryResponse(
            transfer_id=result.transfer_id,
            status=result.status.value,
            source_playlist=result.source_playlist,
            target_playlist=result.target_playlist,
            success_count=result.success_count,
            fail_count=result.fail_count,
            failed_tracks=result.failed_tracks,
            skipped_tracks=result.skipped_tracks,
            created_playlist=result.created_playlist
        )
        
    except Exception as e:
        logger.error(f"Failed to get transfer summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
