"""Duplicate detection helpers."""

from typing import Any, Dict


def is_duplicate_track(track1: Dict[str, Any], track2: Dict[str, Any], platform: str) -> bool:
    if platform.lower() == 'spotify':
        if track1.get('id') and track2.get('id') and track1['id'] == track2['id']:
            return True
        name1 = track1.get('name', '').lower().strip()
        name2 = track2.get('name', '').lower().strip()
        artists1 = [a.lower().strip() for a in track1.get('artists', [])]
        artists2 = [a.lower().strip() for a in track2.get('artists', [])]
        if name1 == name2 and set(artists1) == set(artists2):
            return True
    elif platform.lower() == 'youtube':
        if track1.get('id') and track2.get('id') and track1['id'] == track2['id']:
            return True
        title1 = track1.get('title', '').lower().strip()
        title2 = track2.get('title', '').lower().strip()
        channel1 = track1.get('channel_title', '').lower().strip()
        channel2 = track2.get('channel_title', '').lower().strip()
        if title1 == title2 and channel1 == channel2:
            return True
    return False


