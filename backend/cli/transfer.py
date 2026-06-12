"""Transfer operations handler for CLI."""

import json
import time
from datetime import datetime
from typing import Optional
from replaylist.transfer import PlaylistTransfer
from .types import CLIConfig
from .auth import AuthHandler


class TransferHandler:
    """
    Handles transfer operations for the CLI.
    
    This class manages playlist transfers between platforms, including
    preview functionality, progress monitoring, and result reporting.
    """
    
    def __init__(self, config: CLIConfig):
        """
        Initialize the transfer handler.
        
        Args:
            config: CLI configuration containing token management settings.
        """
        self.config = config
        self.auth_handler = AuthHandler(config)
    
    def preview_transfer(
        self,
        source_platform: str,
        source_playlist_id: str,
        target_platform: str,
        target_playlist_id: Optional[str] = None,
        mode: str = "new_playlist",
        source_account: Optional[str] = None,
        target_account: Optional[str] = None
    ) -> None:
        """
        Preview what will be transferred between platforms.
        
        Shows a detailed preview of the transfer operation without actually
        executing it, including success rate estimates and potential issues.
        
        Args:
            source_platform: Source platform name ('spotify' or 'youtube')
            source_playlist_id: Source playlist identifier
            target_platform: Target platform name ('spotify' or 'youtube')
            target_playlist_id: Target playlist ID for append mode
            mode: Transfer mode ('new_playlist' or 'append')
            
        Raises:
            Exception: If authentication fails or preview fails
            
        Example:
            >>> handler = TransferHandler(config)
            >>> handler.preview_transfer('spotify', 'playlist123', 'youtube')
            Previewing transfer from spotify to youtube...
            Mode: new_playlist
            
            📋 Transfer Preview
            Source Playlist: My Favorites
            Total Tracks: 25
            Estimated Success: 20 (80.0%)
            Estimated Failures: 5
        """
        try:
            # Check authentication for the specified (or active) accounts
            self._check_authentication(source_platform, target_platform, source_account, target_account)

            # Create transfer manager bound to the chosen accounts
            transfer_manager = self._create_transfer_manager(
                source_platform, target_platform, source_account, target_account
            )

            print(f"Previewing transfer from {source_platform} to {target_platform}...")
            print(f"Mode: {mode}")
            print()
            
            # Progress callback for preview
            def progress_callback(message: str):
                print(f"⏳ {message}")
            
            # Get preview
            preview = transfer_manager.preview_transfer(
                source_platform, source_playlist_id, target_platform, 
                target_playlist_id, mode, progress_callback
            )
            
            # Display preview results
            self._display_preview_results(preview, target_platform)
            
        except Exception as e:
            print(f"Error previewing transfer: {e}")
    
    def transfer_playlist(
        self,
        source_platform: str,
        source_playlist_id: str,
        target_platform: str,
        target_playlist_id: Optional[str] = None,
        mode: str = "new_playlist",
        custom_name: Optional[str] = None,
        source_account: Optional[str] = None,
        target_account: Optional[str] = None
    ) -> None:
        """
        Transfer a playlist between platforms.
        
        Executes the actual transfer operation, creating a new playlist
        or appending to an existing one based on the specified mode.
        Monitors progress and provides detailed results.
        
        Args:
            source_platform: Source platform name ('spotify' or 'youtube')
            source_playlist_id: Source playlist identifier
            target_platform: Target platform name ('spotify' or 'youtube')
            target_playlist_id: Target playlist ID for append mode
            mode: Transfer mode ('new_playlist' or 'append')
            custom_name: Custom name for new playlist (new_playlist mode only)
            
        Raises:
            Exception: If authentication fails or transfer fails
            
        Example:
            >>> handler = TransferHandler(config)
            >>> handler.transfer_playlist('spotify', 'playlist123', 'youtube')
            Starting transfer from spotify to youtube...
            Mode: new_playlist
            Transfer started with ID: transfer_abc123
            Monitoring progress...
            Progress: 15/25 (60.0%)
            Current: Bohemian Rhapsody - Queen
        """
        try:
            # Check authentication for the specified (or active) accounts
            self._check_authentication(source_platform, target_platform, source_account, target_account)

            # Create transfer manager bound to the chosen accounts
            transfer_manager = self._create_transfer_manager(
                source_platform, target_platform, source_account, target_account
            )

            print(f"Starting transfer from {source_platform} to {target_platform}...")
            print(f"Mode: {mode}")
            
            # Validate playlist name if provided
            if custom_name:
                self._validate_playlist_name(custom_name, target_platform)
            
            # Start transfer
            transfer_id = transfer_manager.start_transfer(
                source_platform=source_platform,
                source_playlist_id=source_playlist_id,
                target_platform=target_platform,
                target_playlist_id=target_playlist_id,
                mode=mode,
                custom_playlist_name=custom_name
            )
            
            print(f"Transfer started with ID: {transfer_id}")
            print("Monitoring progress...")
            
            # Monitor progress
            self._monitor_transfer_progress(transfer_manager, transfer_id)
            
            # Show final result
            self._display_transfer_results(transfer_manager, transfer_id, target_platform)
            
        except Exception as e:
            print(f"Transfer error: {e}")
    
    def _check_authentication(
        self,
        source_platform: str,
        target_platform: str,
        source_account: Optional[str] = None,
        target_account: Optional[str] = None,
    ) -> None:
        """
        Check that tokens exist for the chosen source/target accounts.

        Args:
            source_platform: Source platform name
            target_platform: Target platform name
            source_account: Source-platform account id (None = active)
            target_account: Target-platform account id (None = active)

        Raises:
            Exception: If a required token is missing
        """
        if not self.config.get_token(source_platform, source_account):
            who = source_account or "active"
            raise Exception(f"Not authenticated with {source_platform} (account '{who}').")
        if not self.config.get_token(target_platform, target_account):
            who = target_account or "active"
            raise Exception(f"Not authenticated with {target_platform} (account '{who}').")

    def _create_transfer_manager(
        self,
        source_platform: str,
        target_platform: str,
        source_account: Optional[str] = None,
        target_account: Optional[str] = None,
    ) -> PlaylistTransfer:
        """
        Create a PlaylistTransfer bound to the chosen source/target accounts.

        Resolves the Spotify and YouTube access tokens from whichever side
        (source/target) maps to each platform.

        Returns:
            Configured PlaylistTransfer instance
        """
        tokens = {
            source_platform.lower(): self.config.get_token(source_platform, source_account),
            target_platform.lower(): self.config.get_token(target_platform, target_account),
        }
        return PlaylistTransfer(
            tokens.get("spotify") or "dummy",
            tokens.get("youtube") or "dummy",
        )
    
    def _validate_playlist_name(self, name: str, platform: str) -> None:
        """
        Validate and sanitize a playlist name using PlaylistNamer.

        Args:
            name: Playlist name to validate
            platform: Target platform

        Raises:
            ValueError: If playlist name is invalid
        """
        try:
            from replaylist.transfer import PlaylistNamer
            validated_name = PlaylistNamer().validate_and_sanitize_playlist_name(name, platform)
            if validated_name != name:
                print(f"⚠️  Playlist name sanitized: '{name}' → '{validated_name}'")
        except ValueError as e:
            raise ValueError(f"Invalid playlist name: {e}")
        except Exception as e:
            print(f"⚠️  Could not validate playlist name: {e}")
    
    def _display_preview_results(self, preview: dict, target_platform: str) -> None:
        """
        Display preview results in a formatted way.
        
        Args:
            preview: Preview data from transfer manager
            target_platform: Target platform name
        """
        print(f"\n📋 Transfer Preview")
        print(f"Source Playlist: {preview['source_playlist']['name']}")
        print(f"Total Tracks: {preview['total_tracks']}")
        print(f"Estimated Success: {preview['estimated_success']} ({preview['success_rate']}%)")
        print(f"Estimated Failures: {preview['estimated_failures_count']}")
        
        if preview['preview_tracks']:
            print(f"\n✅ Tracks that will be transferred:")
            for i, track in enumerate(preview['preview_tracks'][:10], 1):  # Show first 10
                print(f"  {i}. {track['source']} → {track['target']}")
            
            if len(preview['preview_tracks']) > 10:
                print(f"  ... and {len(preview['preview_tracks']) - 10} more tracks")
        
        if preview['estimated_failures']:
            print(f"\n❌ Tracks that might fail ({len(preview['estimated_failures'])} tracks):")
            for i, track in enumerate(preview['estimated_failures'][:10], 1):  # Show first 10
                print(f"  {i}. {track['source']}")
                print(f"     Reason: {track['reason']}")
            
            if len(preview['estimated_failures']) > 10:
                print(f"  ... and {len(preview['estimated_failures']) - 10} more tracks")
            
            print(f"\n💡 You can manually search for these tracks on {target_platform.title()} and add them later.")
            
            # Save failed tracks to file for easy reference
            self._save_failed_tracks_to_file(preview['estimated_failures'], "preview")
        
        print(f"\n💡 Use 'transfer' command to proceed with the transfer.")
    
    def _monitor_transfer_progress(self, transfer_manager: PlaylistTransfer, transfer_id: str) -> None:
        """
        Monitor transfer progress and display updates.
        
        Args:
            transfer_manager: Transfer manager instance
            transfer_id: Transfer identifier
        """
        while True:
            progress = transfer_manager.get_transfer_progress(transfer_id)
            if not progress:
                print("Transfer not found.")
                break
            
            if progress.status.value in ['completed', 'failed', 'cancelled']:
                break
            
            if progress.total > 0:
                print(f"Progress: {progress.completed}/{progress.total} ({progress.completed/progress.total*100:.1f}%)")
            else:
                print(f"Progress: {progress.completed}/{progress.total}")
            
            if progress.current_track:
                print(f"Current: {progress.current_track}")
            
            time.sleep(2)
    
    def _display_transfer_results(self, transfer_manager: PlaylistTransfer, transfer_id: str, target_platform: str) -> None:
        """
        Display final transfer results.
        
        Args:
            transfer_manager: Transfer manager instance
            transfer_id: Transfer identifier
            target_platform: Target platform name
        """
        result = transfer_manager.get_transfer_result(transfer_id)
        if result:
            print(f"\nTransfer completed!")
            print(f"Status: {result.status.value}")
            print(f"Success: {result.success_count}")
            print(f"Failed: {result.fail_count}")
            
            if result.failed_tracks:
                print(f"\n❌ Failed tracks ({len(result.failed_tracks)} tracks):")
                for i, track in enumerate(result.failed_tracks[:10], 1):  # Show first 10
                    print(f"  {i}. {track['title']} by {', '.join(track['artists'])}")
                    if 'reason' in track:
                        print(f"     Reason: {track['reason']}")
                
                if len(result.failed_tracks) > 10:
                    print(f"  ... and {len(result.failed_tracks) - 10} more tracks")
                
                print(f"\n💡 You can manually search for these tracks on {target_platform.title()} and add them to your playlist.")
                
                # Save failed tracks to file for easy reference
                self._save_failed_tracks_to_file(result.failed_tracks, "transfer")
    
    def _save_failed_tracks_to_file(self, failed_tracks: list, prefix: str) -> None:
        """
        Save failed tracks to a JSON file for easy reference.
        
        Args:
            failed_tracks: List of failed track information
            prefix: File prefix ('preview' or 'transfer')
        """
        failed_tracks_file = f"{prefix}_failed_tracks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(failed_tracks_file, 'w', encoding='utf-8') as f:
            json.dump(failed_tracks, f, indent=2, ensure_ascii=False)
        print(f"📄 Failed tracks saved to: {failed_tracks_file}")
