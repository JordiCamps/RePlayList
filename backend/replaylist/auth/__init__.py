"""Authentication subpackage.

Exports key classes and a global manager for convenient imports. This keeps the
public API compact while allowing internal modules (`manager`, `spotify`,
`youtube`, `callback`, `templates`, `types`) to evolve independently.
"""

from .types import AuthResult
from .spotify import SpotifyAuth
from .youtube import YouTubeAuth
from .manager import AuthManager

# Global manager instance for convenience/backward-compatibility
auth_manager = AuthManager()

__all__ = [
    "AuthResult",
    "SpotifyAuth",
    "YouTubeAuth",
    "AuthManager",
    "auth_manager",
]


