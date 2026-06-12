"""Argument parsing and command execution for CLI."""

import argparse
import json
import sys
from typing import Optional

from replaylist.config import config
from .core import RePlayListCLI


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the CLI.
    
    Sets up all command-line arguments and subcommands for the RePlayList CLI,
    including authentication, playlist management, transfer operations, and search.
    
    Returns:
        Configured ArgumentParser instance
        
    Example:
        >>> parser = create_argument_parser()
        >>> args = parser.parse_args(['auth', 'spotify'])
        >>> print(args.command)  # 'auth'
        >>> print(args.platform)  # 'spotify'
    """
    parser = argparse.ArgumentParser(
        description="RePlayList - Transfer playlists between Spotify and YouTube"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authenticate with a platform')
    auth_parser.add_argument(
        'platform', 
        choices=['spotify', 'youtube'], 
        help='Platform to authenticate with'
    )
    
    # List playlists command
    list_parser = subparsers.add_parser('list', help='List playlists')
    list_parser.add_argument(
        'platform', 
        choices=['spotify', 'youtube'], 
        help='Platform to list playlists from'
    )
    
    # Show tracks command
    tracks_parser = subparsers.add_parser('tracks', help='Show tracks in a playlist')
    tracks_parser.add_argument('platform', choices=['spotify', 'youtube'], help='Platform')
    tracks_parser.add_argument('playlist_id', help='Playlist ID')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview a playlist transfer')
    preview_parser.add_argument(
        'source_platform', 
        choices=['spotify', 'youtube'], 
        help='Source platform'
    )
    preview_parser.add_argument('source_playlist_id', help='Source playlist ID')
    preview_parser.add_argument(
        'target_platform', 
        choices=['spotify', 'youtube'], 
        help='Target platform'
    )
    preview_parser.add_argument(
        '--target-playlist-id', 
        help='Target playlist ID (for append mode)'
    )
    preview_parser.add_argument(
        '--mode', 
        choices=['new_playlist', 'append'], 
        default='new_playlist', 
        help='Transfer mode'
    )
    
    # Transfer command
    transfer_parser = subparsers.add_parser('transfer', help='Transfer a playlist')
    transfer_parser.add_argument(
        'source_platform', 
        choices=['spotify', 'youtube'], 
        help='Source platform'
    )
    transfer_parser.add_argument('source_playlist_id', help='Source playlist ID')
    transfer_parser.add_argument(
        'target_platform', 
        choices=['spotify', 'youtube'], 
        help='Target platform'
    )
    transfer_parser.add_argument(
        '--target-playlist-id', 
        help='Target playlist ID (for append mode)'
    )
    transfer_parser.add_argument(
        '--mode', 
        choices=['new_playlist', 'append'], 
        default='new_playlist', 
        help='Transfer mode'
    )
    transfer_parser.add_argument(
        '--name', 
        help='Custom name for new playlist (only for new_playlist mode)'
    )
    
    # Accounts command
    accounts_parser = subparsers.add_parser(
        'accounts', help='List stored accounts per platform'
    )
    accounts_parser.add_argument(
        'platform',
        nargs='?',
        choices=['spotify', 'youtube'],
        help='Optional platform to filter'
    )

    # Use command (select active account)
    use_parser = subparsers.add_parser(
        'use', help='Set the active account for a platform'
    )
    use_parser.add_argument('platform', choices=['spotify', 'youtube'], help='Platform')
    use_parser.add_argument('account_id', help='Account id to activate (see "accounts")')

    # Extract command
    extract_parser = subparsers.add_parser(
        'extract', help='Extract all playlists and tracks to local storage'
    )
    extract_parser.add_argument(
        'platform',
        choices=['spotify', 'youtube'],
        help='Platform to extract'
    )

    # Update command
    update_parser = subparsers.add_parser(
        'update', help='Incrementally update the local library (only changed playlists)'
    )
    update_parser.add_argument(
        'platform',
        choices=['spotify', 'youtube'],
        help='Platform to update'
    )

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for tracks')
    search_parser.add_argument(
        'platform', 
        choices=['spotify', 'youtube'], 
        help='Platform to search on'
    )
    search_parser.add_argument('query', help='Search query')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show configuration')
    
    return parser


def execute_command(args: argparse.Namespace) -> None:
    """
    Execute the appropriate command based on parsed arguments.
    
    Routes the parsed command-line arguments to the appropriate CLI method
    and handles common exceptions like KeyboardInterrupt and general errors.
    
    Args:
        args: Parsed command-line arguments
        
    Raises:
        SystemExit: On error or when help is requested
        
    Example:
        >>> parser = create_argument_parser()
        >>> args = parser.parse_args(['list', 'spotify'])
        >>> execute_command(args)  # Lists Spotify playlists
    """
    if not args.command:
        parser = create_argument_parser()
        parser.print_help()
        return
    
    cli = RePlayListCLI()
    
    try:
        if args.command == 'auth':
            cli.authenticate_platform(args.platform)
        
        elif args.command == 'list':
            cli.list_playlists(args.platform)
        
        elif args.command == 'tracks':
            cli.show_playlist_tracks(args.platform, args.playlist_id)
        
        elif args.command == 'preview':
            cli.preview_transfer(
                args.source_platform,
                args.source_playlist_id,
                args.target_platform,
                args.target_playlist_id,
                args.mode
            )
        
        elif args.command == 'transfer':
            cli.transfer_playlist(
                args.source_platform,
                args.source_playlist_id,
                args.target_platform,
                args.target_playlist_id,
                args.mode,
                args.name
            )
        
        elif args.command == 'accounts':
            cli.list_accounts(args.platform)

        elif args.command == 'use':
            cli.use_account(args.platform, args.account_id)

        elif args.command == 'extract':
            cli.extract_library(args.platform)

        elif args.command == 'update':
            cli.update_library(args.platform)

        elif args.command == 'search':
            cli.search_tracks(args.platform, args.query)
        
        elif args.command == 'config':
            print("Current configuration:")
            print(json.dumps(config.get_config_data(), indent=2))
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main CLI entry point.
    
    Parses command-line arguments and executes the appropriate command.
    This is the primary entry point for the RePlayList CLI application.
    
    Example:
        >>> main()  # Called when running: python cli.py auth spotify
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    execute_command(args)


if __name__ == "__main__":
    main()
