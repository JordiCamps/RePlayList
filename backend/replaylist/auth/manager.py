"""Unified OAuth2 authentication manager.

Coordinates Spotify and YouTube OAuth flows and the local callback server.
This class owns short-lived state such as pending auth requests and results,
and exposes helper methods to start/stop the local callback HTTP server and to
perform end-to-end browser-based OAuth authentication.
"""

import threading
import webbrowser
from http.server import HTTPServer
from typing import Optional

from ..config import config
from ..utils import setup_logging
from .callback import OAuthCallbackHandler
from .spotify import SpotifyAuth
from .types import AuthResult
from .youtube import YouTubeAuth


logger = setup_logging()


class AuthManager:
    """High-level orchestrator for provider authentication.

    Responsibilities:
    - Manage provider clients (`SpotifyAuth`, `YouTubeAuth`).
    - Host a loopback callback server used by OAuth redirect flows.
    - Store pending auth requests and deliver results back to callers.
    """

    def __init__(self) -> None:
        self.spotify_auth = SpotifyAuth()
        self.youtube_auth = YouTubeAuth()
        self._callback_server: Optional[HTTPServer] = None
        self._callback_thread: Optional[threading.Thread] = None
        self._pending_auth = {}  # Store pending authentication requests
        self._auth_results = {}  # Store authentication results

    def start_callback_server(self, port: int | None = None) -> None:
        """Start local callback HTTP server.

        Args:
            port: TCP port to bind; defaults to the configured redirect URI port
                or 8080 if not present.

        Behavior:
            Spawns a daemon thread running a small HTTP server bound to
            127.0.0.1. The handler writes results back to `_auth_results`.
        """
        if port is None:
            spotify_config = config.get_spotify_config()
            if spotify_config.redirect_uri:
                from urllib.parse import urlparse

                parsed = urlparse(spotify_config.redirect_uri)
                port = int(parsed.port) if parsed.port else 8080
            else:
                port = 8080

        def create_handler(auth_callback):
            auth_manager_ref = self

            class Handler(OAuthCallbackHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(auth_callback, auth_manager_ref, *args, **kwargs)

            return Handler

        def run_server():
            def callback(result):
                if hasattr(callback, "current_state"):
                    self._auth_results[callback.current_state] = result

            handler = create_handler(callback)
            self._callback_server = HTTPServer(("127.0.0.1", port), handler)

            logger.info(f"OAuth callback server started on port {port}")
            self._callback_server.serve_forever()

        self._callback_thread = threading.Thread(target=run_server, daemon=True)
        self._callback_thread.start()

    def stop_callback_server(self) -> None:
        """Stop the callback server if it is running."""
        if self._callback_server:
            self._callback_server.shutdown()
            self._callback_server = None

    def authenticate_platform(self, platform: str) -> AuthResult:
        """Perform the full OAuth browser flow for a provider.

        Opens the system browser, waits for the redirect, and exchanges the
        authorization code for tokens.

        Args:
            platform: "spotify" or "youtube".

        Returns:
            An `AuthResult` describing success or error details.
        """
        import time
        import uuid
        from urllib.parse import urlparse

        state = str(uuid.uuid4())

        if platform.lower() == "spotify":
            auth_handler = self.spotify_auth
            config_obj = config.get_spotify_config()
        elif platform.lower() == "youtube":
            auth_handler = self.youtube_auth
            config_obj = config.get_youtube_config()
        else:
            return AuthResult(success=False, error=f"Unsupported platform: {platform}")

        parsed_uri = urlparse(config_obj.redirect_uri)
        port = int(parsed_uri.port) if parsed_uri.port else 8080

        if not self._callback_server or self._callback_server.server_port != port:
            if self._callback_server:
                self.stop_callback_server()
            self.start_callback_server(port)

        try:
            auth_url = auth_handler.get_auth_url(state)
            logger.info(f"Opening browser for {platform} authentication...")
            logger.info(f"Please complete authentication in your browser: {auth_url}")
            webbrowser.open(auth_url)

            timeout = 300
            start_time = time.time()

            while time.time() - start_time < timeout:
                if state in self._auth_results:
                    result = self._auth_results.pop(state)
                    if result.success and result.access_token:
                        code = result.access_token
                        return auth_handler.exchange_code_for_token(code)
                    else:
                        return result
                time.sleep(1)

            return AuthResult(success=False, error="Authentication timeout - please try again")

        except Exception as exc:  # noqa: BLE001
            logger.error(f"Authentication failed for {platform}: {exc}")
            return AuthResult(success=False, error=str(exc))

    def exchange_code(self, platform: str, code: str) -> AuthResult:
        """Exchange an authorization code for provider tokens."""
        if platform.lower() == "spotify":
            return self.spotify_auth.exchange_code_for_token(code)
        elif platform.lower() == "youtube":
            return self.youtube_auth.exchange_code_for_token(code)
        else:
            return AuthResult(success=False, error=f"Unsupported platform: {platform}")


