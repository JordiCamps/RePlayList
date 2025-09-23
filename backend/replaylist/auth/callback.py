"""OAuth callback HTTP handler.

Handles provider redirect callbacks and delegates token exchange to
`AuthManager`. This runs on a local HTTP server listening on the loopback
interface and is used to finalize the browser-based OAuth flow.

Security considerations:
- The handler only listens on 127.0.0.1 and validates the CSRF `state` value
  provided by the initiator before exchanging the code.
"""

from http.server import BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests

from ..utils import setup_logging
from .templates import render_cli_success_html, render_error_html, render_success_html
from .types import AuthResult


logger = setup_logging()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callbacks.

    The handler is instantiated by `AuthManager.start_callback_server` with an
    `auth_callback` function and a reference to the `AuthManager` instance so it
    can update shared state.
    """

    def __init__(self, auth_callback, auth_manager, *args, **kwargs):
        self.auth_callback = auth_callback
        self.auth_manager = auth_manager
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle the provider redirect and coordinate token exchange."""
        try:
            logger.info(f"Callback GET: {self.path}")
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            code = query_params.get("code", [None])[0]
            state = query_params.get("state", [None])[0]
            error = query_params.get("error", [None])[0]

            logger.info(
                f"Callback params code={code} state={state} error={error}"
            )

            if error:
                result = AuthResult(success=False, error=f"OAuth error: {error}")
                self.auth_manager._auth_results[state] = result
                self._send_web_ui_response(False, error, state)
            elif code and state:
                logger.info(f"Checking pending auth for state: {state}")
                logger.info(
                    f"Pending auth keys: {list(self.auth_manager._pending_auth.keys())}"
                )
                if state in self.auth_manager._pending_auth:
                    platform = self.auth_manager._pending_auth[state]["platform"]
                    logger.info(
                        f"Found web UI request for platform: {platform}"
                    )
                    try:
                        logger.info(
                            f"Exchanging code for tokens for platform: {platform}"
                        )
                        if platform == "spotify":
                            token_result = self.auth_manager.spotify_auth.exchange_code_for_token(code)
                        else:
                            token_result = self.auth_manager.youtube_auth.exchange_code_for_token(code)

                        logger.info(
                            "Token exchange result: success=%s error=%s",
                            token_result.success,
                            token_result.error,
                        )

                        if token_result.success:
                            self.auth_manager._auth_results[state] = token_result

                            try:
                                token_data = {
                                    "platform": platform,
                                    "access_token": token_result.access_token,
                                    "refresh_token": token_result.refresh_token,
                                    "expires_in": token_result.expires_in,
                                }

                                response = requests.post(
                                    "http://localhost:8000/auth/store-token",
                                    json=token_data,
                                    timeout=5,
                                )

                                if response.status_code == 200:
                                    logger.info(
                                        f"Token stored in main server for {platform}"
                                    )
                                else:
                                    logger.warning(
                                        "Failed to store token in main server: %s",
                                        response.status_code,
                                    )

                            except Exception as e:  # noqa: BLE001
                                logger.warning(f"Could not store token in main server: {e}")

                            logger.info("Sending web UI success response")
                            self._send_web_ui_response(True, None, state)
                        else:
                            self.auth_manager._auth_results[state] = token_result
                            logger.info(
                                f"Sending web UI error response: {token_result.error}"
                            )
                            self._send_web_ui_response(False, token_result.error, state)
                    except Exception as e:  # noqa: BLE001
                        logger.error(f"Token exchange failed: {e}")
                        self.auth_manager._auth_results[state] = AuthResult(success=False, error=str(e))
                        self._send_web_ui_response(False, str(e), state)
                else:
                    logger.info(
                        f"State {state} not in pending auth; treating as CLI request"
                    )
                    result = AuthResult(success=True, access_token=code)
                    self.auth_manager._auth_results[state] = result
                    self._send_cli_response()
            else:
                result = AuthResult(success=False, error="No authorization code received")
                if state:
                    self.auth_manager._auth_results[state] = result
                self._send_web_ui_response(False, "No authorization code received", state)

        except Exception as e:  # noqa: BLE001
            logger.error(f"Error handling OAuth callback: {e}")
            if 'state' in locals() and state:
                self.auth_manager._auth_results[state] = AuthResult(success=False, error=str(e))
            self._send_web_ui_response(False, str(e), locals().get("state"))

    def _send_web_ui_response(self, success: bool, error: Optional[str] = None, state: Optional[str] = None) -> None:
        """Send minimal HTML that signals the opener and closes the window."""
        platform = "unknown"
        if state and state in self.auth_manager._pending_auth:
            platform = self.auth_manager._pending_auth[state]["platform"]

        logger.info(
            "Sending web UI response: success=%s platform=%s error=%s",
            success,
            platform,
            error,
        )

        if success:
            html_content = render_success_html(platform)
        else:
            html_content = render_error_html(platform, error)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def _send_cli_response(self) -> None:
        """Send minimal HTML suitable for CLI flows to close the window."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(render_cli_success_html())

    def log_message(self, format, *args):  # noqa: A003 - required by BaseHTTPRequestHandler
        """Suppress default logging."""
        pass


