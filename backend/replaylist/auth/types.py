"""Shared authentication types for OAuth flows.

`AuthResult` communicates the outcome of an OAuth flow or token exchange.
It is used across providers and the `AuthManager`.

Semantics:
- When `success` is False, `error` contains a human-readable message.
- In certain intermediate steps, `access_token` may temporarily hold the
  authorization code (pre-exchange) within the local callback handler.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AuthResult:
    """Result of an OAuth authentication flow.

    Attributes:
        success: True if the flow succeeded.
        access_token: Access token, or temporarily the authorization code prior
            to token exchange where noted.
        refresh_token: Refresh token if provided by the provider.
        expires_in: Lifetime in seconds when returned by the provider.
        account_info: Minimal user profile info dict.
        error: Error message when unsuccessful.
    """

    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    account_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


