"""Main playlist transfer class."""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

from ..spotify import SpotifyAPI, SpotifyTrack, SpotifyPlaylist
from ..youtube import YouTubeAPI, YouTubeVideo, YouTubePlaylist
from ..utils import setup_logging, generate_transfer_id
from .types import TransferStatus, TransferProgress, TransferResult
from .matching import TrackMatcher
from .playlist import PlaylistManager
from .executor import TransferExecutor

logger = setup_logging()


class PlaylistTransfer:
    """Main playlist transfer class."""
    
    def __init__(self, spotify_token: str, youtube_token: str):
        """
        Initialize playlist transfer.
        
        Args:
            spotify_token: Spotify access token
            youtube_token: YouTube access token
        """
        self.spotify_api = SpotifyAPI(spotify_token)
        self.youtube_api = YouTubeAPI(youtube_token)
        self.active_transfers: Dict[str, TransferProgress] = {}
        self.transfer_results: Dict[str, TransferResult] = {}
        self._transfer_lock = threading.Lock()
        
        # Initialize sub-components
        self.matcher = TrackMatcher(self.spotify_api, self.youtube_api)
        self.playlist_manager = PlaylistManager(self.spotify_api, self.youtube_api)
        self.executor = TransferExecutor(self.spotify_api, self.youtube_api)
    
    def preview_transfer(self, source_platform: str, source_playlist_id: str,
                        target_platform: str, target_playlist_id: Optional[str], mode: str,
                        progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Preview what will be transferred without actually doing the transfer.
        
        Returns:
            Dictionary with preview information including tracks that will be transferred,
            tracks that might fail, and estimated success rate.
        """
        try:
            # Get source playlist
            if progress_callback:
                progress_callback("Loading source playlist...")
            
            source_playlist, source_tracks = self.playlist_manager.get_source_playlist(
                source_platform, source_playlist_id
            )
            
            if progress_callback:
                progress_callback(f"Found {len(source_tracks)} tracks. Analyzing matches...")
            
            # Preview tracks
            preview_tracks = []
            estimated_failures = []
            
            for i, source_track in enumerate(source_tracks):
                # Update progress
                if progress_callback and i % 5 == 0:  # Update every 5 tracks
                    percentage = int((i + 1) / len(source_tracks) * 100)
                    progress_callback(f"Analyzing track {i+1}/{len(source_tracks)} ({percentage}%)...")
                
                # Find matching track on target platform
                target_track = self.matcher.find_matching_track(
                    source_track, source_platform, target_platform
                )
                
                if target_track:
                    preview_tracks.append({
                        'source': self.matcher.get_track_display_name(source_track, source_platform),
                        'target': self.matcher.get_track_display_name(target_track, target_platform),
                        'confidence': 'high'  # Could be enhanced with actual confidence scoring
                    })
                else:
                    estimated_failures.append({
                        'source': self.matcher.get_track_display_name(source_track, source_platform),
                        'reason': 'No matching track found'
                    })
            
            if progress_callback:
                progress_callback("Analysis complete!")
            
            success_rate = len(preview_tracks) / len(source_tracks) * 100 if source_tracks else 0
            
            return {
                'source_playlist': {
                    'name': source_playlist['name'],
                    'total_tracks': len(source_tracks)
                },
                'preview_tracks': preview_tracks,
                'estimated_failures': estimated_failures,
                'success_rate': round(success_rate, 1),
                'total_tracks': len(source_tracks),
                'estimated_success': len(preview_tracks),
                'estimated_failures_count': len(estimated_failures)
            }
            
        except Exception as e:
            logger.error(f"Failed to preview transfer: {e}")
            raise

    def start_transfer(
        self,
        source_platform: str,
        source_playlist_id: str,
        target_platform: str,
        target_playlist_id: Optional[str] = None,
        mode: str = "new_playlist",
        custom_playlist_name: Optional[str] = None,
        progress_callback: Optional[Callable[[TransferProgress], None]] = None
    ) -> str:
        """
        Start a playlist transfer.
        
        Args:
            source_platform: Source platform ('spotify' or 'youtube')
            source_playlist_id: Source playlist ID
            target_platform: Target platform ('spotify' or 'youtube')
            target_playlist_id: Target playlist ID (for append mode)
            mode: Transfer mode ('new_playlist' or 'append')
            custom_playlist_name: Custom name for new playlist (optional)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Transfer ID
        """
        transfer_id = generate_transfer_id()
        
        with self._transfer_lock:
            progress = TransferProgress(
                transfer_id=transfer_id,
                status=TransferStatus.PENDING
            )
            self.active_transfers[transfer_id] = progress
        
        # Start transfer in background thread
        thread = threading.Thread(
            target=self.executor.execute_transfer,
            args=(transfer_id, source_platform, source_playlist_id, 
                  target_platform, target_playlist_id, mode, custom_playlist_name, progress_callback,
                  self.active_transfers, self.transfer_results),
            daemon=True
        )
        thread.start()
        
        return transfer_id
    
    def get_transfer_progress(self, transfer_id: str) -> Optional[TransferProgress]:
        """Get transfer progress."""
        with self._transfer_lock:
            return self.active_transfers.get(transfer_id)
    
    def get_transfer_result(self, transfer_id: str) -> Optional[TransferResult]:
        """Get transfer result."""
        with self._transfer_lock:
            return self.transfer_results.get(transfer_id)
    
    def cancel_transfer(self, transfer_id: str) -> bool:
        """Cancel an active transfer."""
        with self._transfer_lock:
            if transfer_id in self.active_transfers:
                progress = self.active_transfers[transfer_id]
                if progress.status == TransferStatus.IN_PROGRESS:
                    progress.status = TransferStatus.CANCELLED
                    progress.completed_at = datetime.utcnow()
                    return True
        return False
    
    def get_active_transfers(self) -> List[TransferProgress]:
        """Get all active transfers."""
        with self._transfer_lock:
            return list(self.active_transfers.values())
    
    def cleanup_completed_transfers(self, max_age_hours: int = 24) -> None:
        """Clean up old completed transfers."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        with self._transfer_lock:
            # Clean up active transfers
            to_remove = []
            for transfer_id, progress in self.active_transfers.items():
                if (progress.status in [TransferStatus.COMPLETED, TransferStatus.FAILED, TransferStatus.CANCELLED] 
                    and progress.completed_at and progress.completed_at < cutoff_time):
                    to_remove.append(transfer_id)
            
            for transfer_id in to_remove:
                del self.active_transfers[transfer_id]
            
            # Clean up transfer results
            to_remove = []
            for transfer_id, result in self.transfer_results.items():
                if result.completed_at and result.completed_at < cutoff_time:
                    to_remove.append(transfer_id)
            
            for transfer_id in to_remove:
                del self.transfer_results[transfer_id]
            
            logger.info(f"Cleaned up {len(to_remove)} old transfers")
