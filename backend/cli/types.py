"""CLI-specific data types and multi-account token storage."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _empty_bucket() -> Dict[str, Any]:
    return {"active": None, "accounts": {}}


class CLIConfig:
    """Configuration and multi-account token storage for CLI operations.

    Tokens are stored per platform, keyed by the service account id, so several
    accounts (e.g. two YouTube channels) can coexist. One account per platform
    is marked "active"; the convenience properties ``spotify_token`` and
    ``youtube_token`` return the active account's access token so existing
    handlers keep working unchanged.
    """

    PLATFORMS = ("spotify", "youtube")

    def __init__(self, tokens_file: Optional[Path] = None):
        """Initialize CLI configuration.

        Args:
            tokens_file: Path to the tokens file. Defaults to "tokens.json".
        """
        self.tokens_file = tokens_file or Path("tokens.json")
        # platform -> {"active": account_id|None, "accounts": {account_id: {...}}}
        self._store: Dict[str, Dict[str, Any]] = {p: _empty_bucket() for p in self.PLATFORMS}

    # --- active-token convenience (consumed by the other handlers) ---
    @property
    def spotify_token(self) -> Optional[str]:
        return self.get_token("spotify")

    @property
    def youtube_token(self) -> Optional[str]:
        return self.get_token("youtube")

    # --- account management ---
    def add_account(
        self,
        platform: str,
        account_id: str,
        *,
        access_token: Optional[str],
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        display_name: str = "",
        make_active: bool = True,
    ) -> None:
        """Store (or refresh) one account's tokens and optionally make it active."""
        bucket = self._store.setdefault(platform.lower(), _empty_bucket())
        bucket["accounts"][account_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "display_name": display_name or account_id,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        if make_active or not bucket.get("active"):
            bucket["active"] = account_id

    def set_active(self, platform: str, account_id: str) -> bool:
        """Mark an existing account as active. Returns False if it is unknown."""
        bucket = self._store.get(platform.lower(), _empty_bucket())
        if account_id in bucket.get("accounts", {}):
            bucket["active"] = account_id
            return True
        return False

    def get_active(self, platform: str) -> Optional[str]:
        """Return the active account id for a platform, if any."""
        return self._store.get(platform.lower(), {}).get("active")

    def list_accounts(self, platform: str) -> Dict[str, Dict[str, Any]]:
        """Return the stored accounts for a platform keyed by account id."""
        return self._store.get(platform.lower(), {}).get("accounts", {})

    def get_token(self, platform: str, account_id: Optional[str] = None) -> Optional[str]:
        """Return an access token for a platform (active account unless specified)."""
        bucket = self._store.get(platform.lower(), {})
        account_id = account_id or bucket.get("active")
        if not account_id:
            return None
        account = bucket.get("accounts", {}).get(account_id)
        return account.get("access_token") if account else None

    # --- serialization ---
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the token store (schema version 2)."""
        data: Dict[str, Any] = {"version": 2}
        for platform in self.PLATFORMS:
            data[platform] = self._store.get(platform, _empty_bucket())
        return data

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load the token store, migrating the legacy flat format if needed."""
        if not isinstance(data, dict):
            return
        for platform in self.PLATFORMS:
            raw = data.get(platform)
            if isinstance(raw, dict) and "accounts" in raw:
                # Current (v2) format.
                self._store[platform] = {
                    "active": raw.get("active"),
                    "accounts": dict(raw.get("accounts", {})),
                }
            elif isinstance(raw, str) and raw:
                # Legacy (v1) format: a single bare token, account id unknown.
                # Migrate under "default"; the next auth re-keys it by identity.
                self._store[platform] = {
                    "active": "default",
                    "accounts": {"default": {"access_token": raw, "display_name": "default"}},
                }
            else:
                self._store.setdefault(platform, _empty_bucket())
