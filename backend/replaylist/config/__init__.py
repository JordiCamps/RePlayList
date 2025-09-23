"""Configuration subpackage for RePlayList.

Exports typed models and the Config manager for convenient imports.
"""

from .types import AppConfig, SpotifyConfig, YouTubeConfig
from .manager import Config

# Global config instance for convenient imports from package path
config = Config()

__all__ = ["AppConfig", "SpotifyConfig", "YouTubeConfig", "Config", "config"]


