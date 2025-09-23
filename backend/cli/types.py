"""CLI-specific data types and structures."""

from typing import Optional, Dict, Any
from pathlib import Path


class CLIConfig:
    """Configuration for CLI operations."""
    
    def __init__(self, tokens_file: Optional[Path] = None):
        """
        Initialize CLI configuration.
        
        Args:
            tokens_file: Path to the tokens file. Defaults to "tokens.json".
        """
        self.tokens_file = tokens_file or Path("tokens.json")
        self.spotify_token: Optional[str] = None
        self.youtube_token: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration.
        """
        return {
            'spotify': self.spotify_token,
            'youtube': self.youtube_token
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load configuration from dictionary.
        
        Args:
            data: Dictionary containing token data.
        """
        self.spotify_token = data.get('spotify')
        self.youtube_token = data.get('youtube')
