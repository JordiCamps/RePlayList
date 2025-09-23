"""Text normalization and similarity helpers."""

from typing import List


def normalize_track_title(title: str) -> str:
    if not title:
        return ""
    normalized = title.lower().strip()
    common_words: List[str] = [
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    ]
    words = [word for word in normalized.split() if word not in common_words]
    return ' '.join(words)


def normalize_artist_name(artist: str) -> str:
    if not artist:
        return ""
    normalized = artist.lower().strip()
    prefixes_to_remove = ['feat.', 'featuring', 'ft.', 'ft', 'feat', '&', 'and']
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
    return normalized


def calculate_similarity(str1: str, str2: str) -> float:
    if not str1 or not str2:
        return 0.0
    norm1 = normalize_track_title(str1)
    norm2 = normalize_track_title(str2)
    if norm1 == norm2:
        return 1.0
    set1 = set(norm1)
    set2 = set(norm2)
    if not set1 and not set2:
        return 1.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


