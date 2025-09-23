"""Spotify OAuth2 authentication handler.

Responsibilities:
- Build authorization URLs for the browser flow.
- Exchange authorization codes for access/refresh tokens.
- Fetch minimal user profile details for display.
"""

from typing import Any, Dict
from urllib.parse import urlencode
import requests

from ..config import config
from ..utils import setup_logging
from .types import AuthResult


logger = setup_logging()


class SpotifyAuth:
    """Helper for Spotify OAuth operations and user info retrieval."""

    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    USER_INFO_URL = "https://api.spotify.com/v1/me"

    def __init__(self) -> None:
        self.config = config.get_spotify_config()
        self.scopes = [
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-read-private",
            "user-read-email",
        ]

    def get_auth_url(self, state: str) -> str:
        """Generate Spotify authorization URL for the given state.

        Args:
            state: Opaque string used to prevent CSRF.
        """
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "show_dialog": "true",
        }

        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> AuthResult:
        """Exchange authorization code for tokens and return user info.

        Args:
            code: Authorization code returned to the redirect URI.

        Returns:
            `AuthResult` with tokens, expiry, and minimal account information.
        """
        try:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.config.redirect_uri,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }

            logger.info(f"Spotify token exchange request data: {data}")
            logger.info(f"Spotify token exchange URL: {self.TOKEN_URL}")

            response = requests.post(self.TOKEN_URL, data=data)
            logger.info(f"Spotify token exchange response status: {response.status_code}")
            logger.info(f"Spotify token exchange response text: {response.text}")
            response.raise_for_status()

            token_data: Dict[str, Any] = response.json()

            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            user_response = requests.get(self.USER_INFO_URL, headers=headers)
            user_response.raise_for_status()
            user_info: Dict[str, Any] = user_response.json()

            return AuthResult(
                success=True,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_in=token_data.get("expires_in"),
                account_info={
                    "id": user_info["id"],
                    "name": user_info["display_name"],
                    "email": user_info.get("email"),
                    "country": user_info.get("country"),
                },
            )

        except requests.RequestException as exc:
            logger.error(f"Spotify token exchange failed: {exc}")
            return AuthResult(success=False, error=f"Token exchange failed: {exc}")
        except Exception as exc:  # noqa: BLE001 - preserve behavior
            logger.error(f"Unexpected error in Spotify auth: {exc}")
            return AuthResult(success=False, error=f"Authentication failed: {exc}")


