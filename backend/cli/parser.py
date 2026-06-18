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
    transfer_parser.add_argument(
        '--source-account',
        help='Source account id to read from (defaults to the active account)'
    )
    transfer_parser.add_argument(
        '--target-account',
        help='Target account id to write to (defaults to the active account)'
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
    extract_parser.add_argument(
        '--account',
        help='Account id to extract (defaults to the active account)'
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
    update_parser.add_argument(
        '--account',
        help='Account id to update (defaults to the active account)'
    )

    # Migrate command (all Spotify playlists -> YouTube, resumable batches)
    migrate_parser = subparsers.add_parser(
        'migrate', help='Migrate all Spotify playlists to YouTube in resumable, quota-budgeted batches'
    )
    migrate_parser.add_argument('--source-account', required=True,
                                help='Spotify account id (must be extracted first)')
    migrate_parser.add_argument('--target-account', required=True,
                                help='Target YouTube account id')
    migrate_parser.add_argument('--max-units', type=int, default=9500,
                                help='Estimated YouTube quota-unit budget per run (default 9500 of 10,000/day)')
    migrate_parser.add_argument('--limit', type=int, default=None,
                                help='Optional hard cap on number of tracks this run (for small test runs)')

    # YouTube account-to-account copy command
    ytcopy_parser = subparsers.add_parser(
        'yt-copy', help='Copy a playlist between two YouTube accounts'
    )
    ytcopy_parser.add_argument('--from', dest='from_account', required=True,
                               help='Source YouTube account id (see "accounts")')
    ytcopy_parser.add_argument('--to', dest='to_account', required=True,
                               help='Target YouTube account id')
    ytcopy_parser.add_argument('--playlist', dest='source_playlist_id', required=True,
                               help='Source playlist id')
    ytcopy_parser.add_argument('--name', dest='target_name',
                               help='Title for the new target playlist')
    ytcopy_parser.add_argument('--target-playlist-id', dest='target_playlist_id',
                               help='Append into this existing target playlist instead of creating one')

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
                args.name,
                args.source_account,
                args.target_account
            )
        
        elif args.command == 'accounts':
            cli.list_accounts(args.platform)

        elif args.command == 'use':
            cli.use_account(args.platform, args.account_id)

        elif args.command == 'extract':
            cli.extract_library(args.platform, args.account)

        elif args.command == 'update':
            cli.update_library(args.platform, args.account)

        elif args.command == 'migrate':
            cli.migrate_spotify_to_youtube(
                args.source_account, args.target_account, args.max_units, args.limit
            )

        elif args.command == 'yt-copy':
            cli.copy_youtube_account(
                args.from_account,
                args.to_account,
                args.source_playlist_id,
                args.target_name,
                args.target_playlist_id,
            )

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
