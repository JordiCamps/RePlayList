"""
Test that all backend modules can be imported successfully.
This is a basic smoke test to ensure the refactored modules work correctly.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_import_main():
    """Test that main module can be imported."""
    import main
    assert hasattr(main, 'app')


def test_import_replaylist_package():
    """Test that replaylist package can be imported."""
    import replaylist
    assert hasattr(replaylist, '__version__')


def test_import_auth_modules():
    """Test that auth modules can be imported."""
    from replaylist.auth import AuthManager, SpotifyAuth, YouTubeAuth
    from replaylist.auth.types import AuthResult
    assert AuthManager is not None
    assert SpotifyAuth is not None
    assert YouTubeAuth is not None
    assert AuthResult is not None


def test_import_config_modules():
    """Test that config modules can be imported."""
    from replaylist.config import Config
    from replaylist.config.types import SpotifyConfig, YouTubeConfig, AppConfig
    assert Config is not None
    assert SpotifyConfig is not None
    assert YouTubeConfig is not None
    assert AppConfig is not None


def test_import_spotify_modules():
    """Test that Spotify modules can be imported."""
    from replaylist.spotify import SpotifyAPI
    from replaylist.spotify.types import SpotifyTrack, SpotifyPlaylist
    assert SpotifyAPI is not None
    assert SpotifyTrack is not None
    assert SpotifyPlaylist is not None


def test_import_youtube_modules():
    """Test that YouTube modules can be imported."""
    from replaylist.youtube import YouTubeAPI
    from replaylist.youtube.types import YouTubeVideo, YouTubePlaylist
    assert YouTubeAPI is not None
    assert YouTubeVideo is not None
    assert YouTubePlaylist is not None


def test_import_transfer_modules():
    """Test that transfer modules can be imported."""
    from replaylist.transfer import PlaylistTransfer
    from replaylist.transfer.types import TransferStatus, TransferProgress, TransferResult
    assert PlaylistTransfer is not None
    assert TransferStatus is not None
    assert TransferProgress is not None
    assert TransferResult is not None


def test_import_utils_modules():
    """Test that utils modules can be imported."""
    from replaylist.utils import setup_logging, generate_transfer_id, normalize_track_title
    assert setup_logging is not None
    assert generate_transfer_id is not None
    assert normalize_track_title is not None


def test_import_cli_modules():
    """Test that CLI modules can be imported."""
    from replaylist.cli import RePlayListCLI, main
    assert RePlayListCLI is not None
    assert main is not None


def test_import_server_modules():
    """Test that server modules can be imported."""
    from replaylist.server.models import AuthRequest, TransferRequest
    from replaylist.server.state import active_transfers, user_tokens
    assert AuthRequest is not None
    assert TransferRequest is not None
    assert active_transfers is not None
    assert user_tokens is not None


if __name__ == "__main__":
    pytest.main([__file__])
