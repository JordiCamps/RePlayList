"""Transfer execution logic."""

import logging
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .types import TransferProgress, TransferResult, TransferStatus
from .matching import TrackMatcher
from .playlist import PlaylistManager

logger = logging.getLogger(__name__)


class TransferExecutor:
    """Handles the execution of playlist transfers."""
    
    def __init__(self, spotify_api, youtube_api):
        """
        Initialize transfer executor.
        
        Args:
            spotify_api: Spotify API client
            youtube_api: YouTube API client
        """
        self.matcher = TrackMatcher(spotify_api, youtube_api)
        self.playlist_manager = PlaylistManager(spotify_api, youtube_api)
        self._transfer_lock = threading.Lock()
    
    def execute_transfer(
        self,
        transfer_id: str,
        source_platform: str,
        source_playlist_id: str,
        target_platform: str,
        target_playlist_id: Optional[str],
        mode: str,
        custom_playlist_name: Optional[str],
        progress_callback: Optional[Callable[[TransferProgress], None]],
        active_transfers: Dict[str, TransferProgress],
        transfer_results: Dict[str, TransferResult]
    ) -> None:
        """
        Execute the actual transfer in a background thread.
        
        Args:
            transfer_id: Unique transfer identifier
            source_platform: Source platform ('spotify' or 'youtube')
            source_playlist_id: Source playlist ID
            target_platform: Target platform ('spotify' or 'youtube')
            target_playlist_id: Target playlist ID (for append mode)
            mode: Transfer mode ('new_playlist' or 'append')
            custom_playlist_name: Custom name for new playlist
            progress_callback: Optional callback for progress updates
            active_transfers: Dictionary of active transfers
            transfer_results: Dictionary of transfer results
        """
        try:
            with self._transfer_lock:
                progress = active_transfers.get(transfer_id)
                if not progress:
                    return
                
                progress.status = TransferStatus.IN_PROGRESS
            
            # Get source playlist and tracks
            source_playlist, source_tracks = self.playlist_manager.get_source_playlist(
                source_platform, source_playlist_id
            )
            
            if not source_tracks:
                raise ValueError("Source playlist is empty or could not be accessed")
            
            # Update progress
            with self._transfer_lock:
                progress.total = len(source_tracks)
                progress.completed = 0
            
            if progress_callback:
                progress_callback(progress)
            
            # Get or create target playlist
            try:
                target_playlist = self.playlist_manager.get_or_create_target_playlist(
                    target_platform, target_playlist_id, source_playlist, mode, custom_playlist_name
                )
            except ValueError as e:
                # Handle validation errors (e.g., invalid playlist name)
                logger.error(f"Playlist validation error: {e}")
                with self._transfer_lock:
                    progress.status = TransferStatus.FAILED
                    progress.error_message = f"Invalid playlist name: {e}. Please try a different name."
                    progress.completed_at = datetime.utcnow()
                if progress_callback:
                    progress_callback(progress)
                return
            except Exception as e:
                # Handle other errors (e.g., API errors, network issues)
                logger.error(f"Failed to create/get target playlist: {e}")
                with self._transfer_lock:
                    progress.status = TransferStatus.FAILED
                    progress.error_message = f"Failed to create target playlist: {e}"
                    progress.completed_at = datetime.utcnow()
                if progress_callback:
                    progress_callback(progress)
                return
            
            # Get existing tracks from target playlist (for duplicate checking)
            existing_target_tracks = []
            if mode == "append" and target_playlist_id:
                existing_target_tracks = self.playlist_manager.get_existing_tracks(
                    target_platform, target_playlist_id
                )
            
            # Transfer tracks
            success_count = 0
            fail_count = 0
            failed_tracks = []
            skipped_tracks = []  # Track skipped songs with reasons
            added_tracks = set()  # Track duplicates within current transfer
            
            for i, source_track in enumerate(source_tracks):
                try:
                    # Update progress
                    with self._transfer_lock:
                        progress.completed = i
                        # Handle different track types
                        if hasattr(source_track, 'name') and hasattr(source_track, 'artists'):
                            # Spotify track
                            progress.current_track = f"{source_track.name} - {', '.join(source_track.artists)}"
                        elif hasattr(source_track, 'title') and hasattr(source_track, 'channel_title'):
                            # YouTube video - extract artist and title for better display
                            if source_platform.lower() == 'youtube' and target_platform.lower() == 'spotify':
                                extracted_artist, extracted_title = self.matcher._extract_artist_and_title_from_youtube_title(source_track.title)
                                if extracted_artist and extracted_title:
                                    progress.current_track = f"{extracted_title} - {extracted_artist}"
                                else:
                                    progress.current_track = f"{source_track.title} - {source_track.channel_title}"
                            else:
                                progress.current_track = f"{source_track.title} - {source_track.channel_title}"
                        else:
                            # Generic fallback
                            progress.current_track = str(source_track)
                    
                    if progress_callback:
                        progress_callback(progress)
                    
                    # Find matching track on target platform
                    target_track = self.matcher.find_matching_track(
                        source_track, source_platform, target_platform
                    )
                    
                    if target_track:
                        # Check for duplicates within current transfer
                        track_key = self.matcher.get_track_key(target_track, target_platform)
                        if track_key in added_tracks:
                            track_display = self.matcher.get_track_display_name(target_track, target_platform)
                            logger.info(f"Skipping duplicate within transfer: {track_display}")
                            skipped_tracks.append({
                                'title': getattr(target_track, 'name', getattr(target_track, 'title', 'Unknown')),
                                'artists': getattr(target_track, 'artists', [getattr(target_track, 'channel_title', 'Unknown')]),
                                'reason': 'Duplicate within transfer'
                            })
                            fail_count += 1
                            continue
                        
                        # Check for duplicates against existing target playlist tracks
                        is_duplicate = False
                        for existing_track in existing_target_tracks:
                            if self.matcher.is_duplicate_track(target_track, existing_track, target_platform):
                                track_display = self.matcher.get_track_display_name(target_track, target_platform)
                                logger.info(f"Skipping duplicate in target playlist: {track_display}")
                                skipped_tracks.append({
                                    'title': getattr(target_track, 'name', getattr(target_track, 'title', 'Unknown')),
                                    'artists': getattr(target_track, 'artists', [getattr(target_track, 'channel_title', 'Unknown')]),
                                    'reason': 'Already exists in target playlist'
                                })
                                is_duplicate = True
                                break
                        
                        if is_duplicate:
                            fail_count += 1
                            continue
                        
                        # Add track to target playlist
                        self.playlist_manager.add_track_to_playlist(
                            target_track, target_platform, target_playlist['id']
                        )
                        added_tracks.add(track_key)
                        success_count += 1
                        # Handle different track types for success logging
                        if hasattr(source_track, 'name'):
                            logger.info(f"Successfully transferred: {source_track.name}")
                        elif hasattr(source_track, 'title'):
                            logger.info(f"Successfully transferred: {source_track.title}")
                        else:
                            logger.info(f"Successfully transferred: {source_track}")
                    else:
                        fail_count += 1
                        # Handle different track types for failed tracks
                        if hasattr(source_track, 'name') and hasattr(source_track, 'artists'):
                            failed_tracks.append({
                                'title': source_track.name,
                                'artists': source_track.artists,
                                'reason': 'No matching track found'
                            })
                            logger.warning(f"Could not find match for: {source_track.name}")
                        elif hasattr(source_track, 'title') and hasattr(source_track, 'channel_title'):
                            failed_tracks.append({
                                'title': source_track.title,
                                'artists': [source_track.channel_title],
                                'reason': 'No matching track found'
                            })
                            logger.warning(f"Could not find match for: {source_track.title}")
                        else:
                            failed_tracks.append({
                                'title': str(source_track),
                                'artists': [],
                                'reason': 'No matching track found'
                            })
                            logger.warning(f"Could not find match for: {source_track}")
                
                except Exception as e:
                    fail_count += 1
                    # Handle different track types for error logging
                    if hasattr(source_track, 'name') and hasattr(source_track, 'artists'):
                        failed_tracks.append({
                            'title': source_track.name,
                            'artists': source_track.artists,
                            'reason': str(e)
                        })
                        logger.error(f"Error transferring track {source_track.name}: {e}")
                    elif hasattr(source_track, 'title') and hasattr(source_track, 'channel_title'):
                        failed_tracks.append({
                            'title': source_track.title,
                            'artists': [source_track.channel_title],
                            'reason': str(e)
                        })
                        logger.error(f"Error transferring track {source_track.title}: {e}")
                    else:
                        failed_tracks.append({
                            'title': str(source_track),
                            'artists': [],
                            'reason': str(e)
                        })
                        logger.error(f"Error transferring track {source_track}: {e}")
            
            # Create final result
            result = TransferResult(
                transfer_id=transfer_id,
                status=TransferStatus.COMPLETED,
                source_playlist=source_playlist,
                target_playlist=target_playlist,
                success_count=success_count,
                fail_count=fail_count,
                failed_tracks=failed_tracks,
                skipped_tracks=skipped_tracks,
                created_playlist=target_playlist if mode == "new_playlist" else None,
                completed_at=datetime.utcnow()
            )
            
            with self._transfer_lock:
                progress.status = TransferStatus.COMPLETED
                progress.completed = progress.total
                progress.completed_at = datetime.utcnow()
                transfer_results[transfer_id] = result
            
            if progress_callback:
                progress_callback(progress)
            
            logger.info(f"Transfer {transfer_id} completed: {success_count} successful, {fail_count} failed")
            
        except Exception as e:
            logger.error(f"Transfer {transfer_id} failed: {e}")
            
            with self._transfer_lock:
                if transfer_id in active_transfers:
                    progress = active_transfers[transfer_id]
                    progress.status = TransferStatus.FAILED
                    progress.error_message = str(e)
                    progress.completed_at = datetime.utcnow()
                
                if progress_callback:
                    progress_callback(progress)
