"""Standalone entrypoint to run the FastAPI backend with Uvicorn.

This module is designed to be bundled as a single executable using PyInstaller
and launched by Tauri as a sidecar. It preserves existing behavior without
changing the app code.
"""

import os
import sys


def _ensure_runtime_environment() -> None:
    """Ensure project paths are importable when frozen or run from source.

    - Adds the backend directory (this file's parent) to sys.path
    - Adds the project root to sys.path so `replaylist` package can be imported
    - Changes working directory to the executable folder so `config.json`
      placed next to the EXE is discoverable
    """
    # When frozen, __file__ points to a temp dir. The executable path is the
    # correct location to use for both imports and local files like config.
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    current_dir = exe_dir
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

    for path in (current_dir, project_root):
        if path not in sys.path:
            sys.path.insert(0, path)

    # Ensure working directory is the exe folder so relative files are found
    try:
        os.chdir(exe_dir)
    except Exception:
        pass


def main() -> None:
    _ensure_runtime_environment()
    import uvicorn  # type: ignore
    # Import after path fix so `main` resolves correctly and force PyInstaller
    # to include the module by direct import.
    from main import app  # type: ignore
    from replaylist.config import config  # noqa: F401

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()


