"""Shared state for the server application."""

from typing import Dict
from replaylist.transfer import PlaylistTransfer

# Global storage for active transfers and tokens
active_transfers: Dict[str, PlaylistTransfer] = {}
user_tokens: Dict[str, Dict[str, str]] = {}  # {user_id: {platform: token}}
