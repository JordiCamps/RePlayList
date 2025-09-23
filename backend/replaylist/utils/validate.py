"""Validation helpers for IDs and API payloads."""

from typing import Any, Dict
import logging


def validate_playlist_id(playlist_id: str, platform: str) -> bool:
    if not playlist_id or not isinstance(playlist_id, str):
        return False
    if platform.lower() == "spotify":
        return len(playlist_id) == 22 and playlist_id.isalnum()
    if platform.lower() == "youtube":
        return playlist_id.startswith("PL") and len(playlist_id) > 10
    return False


def validate_track_metadata(track_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
    validated: Dict[str, Any] = {}
    if platform.lower() == 'spotify':
        validated['id'] = track_data.get('id', '')
        validated['name'] = track_data.get('name', '').strip()
        validated['artists'] = [artist.get('name', '').strip() for artist in track_data.get('artists', [])]
        validated['album'] = track_data.get('album', {}).get('name', '').strip()
        validated['duration_ms'] = track_data.get('duration_ms', 0)
        validated['external_urls'] = track_data.get('external_urls', {})
        if not validated['name']:
            raise ValueError("Track name is required")
        if not validated['artists'] or not any(validated['artists']):
            raise ValueError("At least one artist is required")
        if validated['duration_ms'] <= 0:
            logging.getLogger('replaylist').warning(f"Invalid duration for track: {validated['name']}")
    elif platform.lower() == 'youtube':
        validated['id'] = track_data.get('id', '')
        validated['title'] = track_data.get('snippet', {}).get('title', '').strip()
        validated['channel_title'] = track_data.get('snippet', {}).get('channelTitle', '').strip()
        validated['duration'] = track_data.get('contentDetails', {}).get('duration', '')
        validated['published_at'] = track_data.get('snippet', {}).get('publishedAt', '')
        validated['thumbnail_url'] = track_data.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url', '')
        validated['description'] = track_data.get('snippet', {}).get('description', '').strip()
        if not validated['title']:
            raise ValueError("Video title is required")
        if not validated['channel_title']:
            raise ValueError("Channel title is required")
        if not validated['id']:
            raise ValueError("Video ID is required")
    return validated


def validate_playlist_metadata(playlist_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
    validated: Dict[str, Any] = {}
    if platform.lower() == 'spotify':
        validated['id'] = playlist_data.get('id', '')
        validated['name'] = playlist_data.get('name', '').strip()
        validated['description'] = playlist_data.get('description', '').strip()
        validated['tracks'] = playlist_data.get('tracks', {}).get('total', 0)
        validated['public'] = playlist_data.get('public', False)
        validated['external_urls'] = playlist_data.get('external_urls', {})
        if not validated['name']:
            raise ValueError("Playlist name is required")
        if not validated['id']:
            raise ValueError("Playlist ID is required")
    elif platform.lower() == 'youtube':
        validated['id'] = playlist_data.get('id', '')
        validated['title'] = playlist_data.get('snippet', {}).get('title', '').strip()
        validated['description'] = playlist_data.get('snippet', {}).get('description', '').strip()
        validated['channel_title'] = playlist_data.get('snippet', {}).get('channelTitle', '').strip()
        validated['item_count'] = playlist_data.get('contentDetails', {}).get('itemCount', 0)
        validated['privacy_status'] = playlist_data.get('status', {}).get('privacyStatus', 'private')
        validated['thumbnail_url'] = playlist_data.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url', '')
        if not validated['title']:
            raise ValueError("Playlist title is required")
        if not validated['id']:
            raise ValueError("Playlist ID is required")
        if not validated['channel_title']:
            raise ValueError("Channel title is required")
    return validated


