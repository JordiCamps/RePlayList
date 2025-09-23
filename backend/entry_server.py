"""Standalone entrypoint to run the FastAPI backend with Uvicorn.

This module is designed to be bundled as a single executable using PyInstaller
and launched by Tauri as a sidecar. It preserves existing behavior without
changing the app code.
"""

import os
import sys


def _ensure_pythonpath() -> None:
    """Ensure project paths are importable when frozen or run from source.

    - Adds the backend directory (this file's parent) to sys.path
    - Adds the project root to sys.path so `replaylist` package can be imported
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

    for path in (current_dir, project_root):
        if path not in sys.path:
            sys.path.insert(0, path)


def main() -> None:
    _ensure_pythonpath()
    import uvicorn  # type: ignore
    # Import after path fix so `main:app` resolves correctly
    from replaylist.config import config  # noqa: F401

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()


