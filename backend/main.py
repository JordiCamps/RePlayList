"""FastAPI server for RePlayList application."""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from replaylist.config import config
from replaylist.auth import auth_manager, AuthResult
from replaylist.spotify import SpotifyAPI
from replaylist.youtube import YouTubeAPI
from replaylist.transfer import PlaylistTransfer, TransferStatus
from replaylist.utils import setup_logging, create_error_response, create_success_response
from server.models import (
    AuthRequest,
    AuthResponse,
    TokenExchangeRequest,
    PlaylistInfo,
    TrackInfo,
    TransferRequest,
    TransferResponse,
    ProgressResponse,
    SummaryResponse
)
from server.state import active_transfers, user_tokens
from server.auth import router as auth_router
from server.playlists import router as playlists_router
from server.transfer import router as transfer_router
from server.config import router as config_router


# Set up logging
logger = setup_logging(config.get_app_config().log_level)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting RePlayList server...")
    yield
    logger.info("Shutting down RePlayList server...")


# Create FastAPI app
app = FastAPI(
    title="RePlayList API",
    description="API for transferring playlists between Spotify and YouTube",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(playlists_router)
app.include_router(transfer_router)
app.include_router(config_router)






# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RePlayList API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}










if __name__ == "__main__":
    import uvicorn
    
    app_config = config.get_app_config()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=app_config.http_port,
        reload=app_config.debug,
        log_level=app_config.log_level.lower()
    )
