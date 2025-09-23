"""Config facade: re-export models and manager with global instance.

This preserves the historical import path while allowing internal structure to
evolve in `replaylist.config` subpackage.
"""

from .config.types import AppConfig, SpotifyConfig, YouTubeConfig
from .config.manager import Config

# Global config instance
config = Config()