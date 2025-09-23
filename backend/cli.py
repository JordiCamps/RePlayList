"""Command line interface for RePlayList.

This module provides a facade for the CLI functionality, re-exporting
the main classes and functions from the cli subpackage for backward
compatibility.
"""

# Re-export main CLI components for backward compatibility
try:
    from .cli.core import RePlayListCLI
    from .cli.parser import main
except ImportError:
    # Handle direct execution (python cli.py)
    from cli.core import RePlayListCLI
    from cli.parser import main

# Make main CLI components available at package level
__all__ = ['RePlayListCLI', 'main']

# Ensure the main function is available for direct execution
if __name__ == "__main__":
    main()
