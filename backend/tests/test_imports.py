"""
Basic smoke tests for RePlayList backend.
"""

import pytest
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)


def test_basic_imports():
    """Test that basic modules can be imported."""
    # Test main module
    import main
    assert hasattr(main, 'app')
    
    # Test replaylist package
    import replaylist
    assert hasattr(replaylist, '__version__')


def test_auth_imports():
    """Test auth module imports."""
    from replaylist.auth import AuthManager
    from replaylist.auth.types import AuthResult
    assert AuthManager is not None
    assert AuthResult is not None


def test_config_imports():
    """Test config module imports."""
    from replaylist.config import Config
    from replaylist.config.types import SpotifyConfig
    assert Config is not None
    assert SpotifyConfig is not None


def test_utils_imports():
    """Test utils module imports."""
    from replaylist.utils import setup_logging
    assert setup_logging is not None


def test_python_version():
    """Test that we're running on a supported Python version."""
    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"


if __name__ == "__main__":
    pytest.main([__file__])
