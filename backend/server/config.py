"""Configuration endpoints for the RePlayList API."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from replaylist.config import config
from replaylist.utils import create_success_response

logger = logging.getLogger(__name__)

# Create router for config endpoints
router = APIRouter(prefix="/config", tags=["configuration"])


@router.get("")
async def get_config():
    """Get current configuration."""
    try:
        return create_success_response(data=config.get_config_data())
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def update_config(updates: Dict[str, Any]):
    """Update configuration."""
    try:
        config.update_config(updates)
        config.save_config()
        return create_success_response(message="Configuration updated successfully")
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
