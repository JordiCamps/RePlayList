"""Playlist naming and validation utilities."""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class PlaylistNamer:
    """Handles playlist naming and validation."""
    
    def validate_and_sanitize_playlist_name(self, name: str, platform: str) -> str:
        """
        Validate and sanitize playlist name according to platform rules.
        
        Args:
            name: Original playlist name
            platform: Target platform ('spotify' or 'youtube')
            
        Returns:
            Sanitized playlist name
            
        Raises:
            ValueError: If name cannot be made valid
        """
        if not name or not name.strip():
            raise ValueError("Playlist name cannot be empty")
        
        # Clean the name
        sanitized = name.strip()
        
        if platform.lower() == 'spotify':
            # Spotify playlist name rules
            # - Max length: 100 characters (but we'll use 80 for better display)
            # - No control characters
            # - Avoid excessive special characters
            
            # Remove control characters
            sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
            
            # Limit length
            if len(sanitized) > 80:
                sanitized = sanitized[:77] + "..."
                logger.warning(f"Playlist name truncated to 80 characters: {sanitized}")
            
            # Remove excessive whitespace
            sanitized = re.sub(r'\s+', ' ', sanitized).strip()
            
            # Ensure it's not empty after cleaning
            if not sanitized:
                sanitized = "Untitled Playlist"
                logger.warning("Playlist name was empty after sanitization, using 'Untitled Playlist'")
            
        elif platform.lower() == 'youtube':
            # YouTube playlist title rules
            # - Max length: 150 characters
            # - No control characters
            
            sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
            
            if len(sanitized) > 150:
                sanitized = sanitized[:147] + "..."
                logger.warning(f"Playlist name truncated to 150 characters: {sanitized}")
            
            sanitized = re.sub(r'\s+', ' ', sanitized).strip()
            
            if not sanitized:
                sanitized = "Untitled Playlist"
                logger.warning("Playlist name was empty after sanitization, using 'Untitled Playlist'")
        
        else:
            raise ValueError(f"Unsupported platform for name validation: {platform}")
        
        return sanitized
