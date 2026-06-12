"""YouTube OAuth2 authentication handler.

Responsibilities:
- Build authorization URLs for Google OAuth consent.
- Exchange authorization codes for access/refresh tokens.
- Retrieve minimal user profile details for display.
"""

from typing import Any, Dict
from urllib.parse import urlencode
import requests

from ..config import config
from ..utils import setup_logging
from .types import AuthResult


logger = setup_logging()


class YouTubeAuth:
    """Helper for YouTube OAuth operations and user info retrieval."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self) -> None:
        self.config = config.get_youtube_config()
        self.scopes = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ]

    def get_auth_url(self, state: str) -> str:
        """Generate YouTube authorization URL for the given state.

        Args:
            state: Opaque string used to prevent CSRF.
        """
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",
            # select_account lets the user pick which Google account to use,
            # which is required to authenticate multiple YouTube accounts.
            "prompt": "select_account consent",
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

            response = requests.post(self.TOKEN_URL, data=data)
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
                    "name": user_info["name"],
                    "email": user_info.get("email"),
                    "picture": user_info.get("picture"),
                },
            )

        except requests.RequestException as exc:
            logger.error(f"YouTube token exchange failed: {exc}")
            return AuthResult(success=False, error=f"Token exchange failed: {exc}")
        except Exception as exc:  # noqa: BLE001 - preserve behavior
            logger.error(f"Unexpected error in YouTube auth: {exc}")
            return AuthResult(success=False, error=f"Authentication failed: {exc}")


