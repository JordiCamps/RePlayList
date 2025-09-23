"""Configuration management for RePlayList.

Loads, validates, updates, and saves configuration from a JSON file. Provides
typed accessors for app and provider-specific configuration.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional

from .types import AppConfig, SpotifyConfig, YouTubeConfig


class Config:
    """Main configuration class for RePlayList.

    Responsibilities:
        - Load configuration from JSON on disk
        - Validate presence of required sections/keys
        - Expose typed getters for sections
        - Persist updates with simple deep-merge semantics
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to config file. If None, uses project root
                `config.json`.
        """
        if config_path is None:
            # Search order for portable/packaged usage:
            # 1) Current working directory
            # 2) Directory of the running executable when frozen
            # 3) Project root (source checkout)
            candidates = [Path.cwd() / "config.json"]
            if getattr(sys, "frozen", False):  # PyInstaller/packaged
                exe_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)).resolve()
                candidates.append(exe_dir / "config.json")
            project_root = Path(__file__).parents[3]
            candidates.append(project_root / "config.json")
            # Pick the first that exists; otherwise default to project root path
            existing = next((p for p in candidates if p.exists()), None)
            config_path = existing or candidates[-1]

        self.config_path = Path(config_path)
        self._config_data: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from JSON file and validate it."""
        if not self.config_path.exists():
            # In CI or development, use default config if file doesn't exist
            if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
                self._config_data = self._get_default_config()
                return
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config_data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in config file: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to load config: {exc}") from exc
        self._validate_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for CI/development environments."""
        return {
            "spotify": {
                "client_id": "ci_client_id",
                "client_secret": "ci_client_secret",
                "redirect_uri": "http://127.0.0.1:8888/callback"
            },
            "youtube": {
                "client_id": "ci_client_id",
                "client_secret": "ci_client_secret",
                "redirect_uri": "http://127.0.0.1:8889/callback"
            },
            "app": {
                "debug": True,
                "default_transfer_mode": "new_playlist",
                "http_port": 5000,
                "log_level": "INFO"
            }
        }

    def _validate_config(self) -> None:
        """Validate that all required configuration keys are present."""
        required_keys = {
            "spotify": ["client_id", "client_secret", "redirect_uri"],
            "youtube": ["client_id", "client_secret", "redirect_uri"],
            "app": ["debug", "default_transfer_mode", "http_port", "log_level"],
        }
        for section, keys in required_keys.items():
            if section not in self._config_data:
                raise ValueError(f"Missing section '{section}' in config")
            for key in keys:
                if key not in self._config_data[section]:
                    raise ValueError(f"Missing key '{key}' in section '{section}'")

    def get_spotify_config(self) -> SpotifyConfig:
        """Return typed Spotify configuration."""
        spotify_data = self._config_data["spotify"]
        return SpotifyConfig(
            client_id=spotify_data["client_id"],
            client_secret=spotify_data["client_secret"],
            redirect_uri=spotify_data["redirect_uri"],
        )

    def get_youtube_config(self) -> YouTubeConfig:
        """Return typed YouTube configuration."""
        youtube_data = self._config_data["youtube"]
        return YouTubeConfig(
            client_id=youtube_data["client_id"],
            client_secret=youtube_data["client_secret"],
            redirect_uri=youtube_data["redirect_uri"],
        )

    def get_app_config(self) -> AppConfig:
        """Return typed application configuration."""
        app_data = self._config_data["app"]
        return AppConfig(
            debug=app_data["debug"],
            default_transfer_mode=app_data["default_transfer_mode"],
            http_port=app_data["http_port"],
            log_level=app_data["log_level"],
        )

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Deep-merge the provided updates and validate the result.

        Args:
            updates: Nested dictionary of changes to apply.
        """

        def deep_merge(base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
            result = base.copy()
            for key, value in incoming.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        self._config_data = deep_merge(self._config_data, updates)
        self._validate_config()

    def save_config(self) -> None:
        """Persist current configuration to disk."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to save config: {exc}") from exc

    def get_config_data(self) -> Dict[str, Any]:
        """Return a shallow copy of the raw configuration dictionary."""
        return self._config_data.copy()


