"""OAuth2 authentication facade.

Re-exports provider auth classes and `AuthManager` from the `auth` subpackage
and provides a global `auth_manager` for backward compatibility. Existing
imports from `.auth` should continue to work.
"""

from .auth import AuthManager, SpotifyAuth, YouTubeAuth, AuthResult

auth_manager = AuthManager()
