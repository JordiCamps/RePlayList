"""Pure text-matching helpers shared across providers.

These functions implement the fuzzy matching previously kept as private methods
on `SpotifyAPI`. They are provider-agnostic so both the Spotify and YouTube
clients can score candidates with identical semantics.
"""

from __future__ import annotations

import re

__all__ = ["clean_title", "clean_artist", "fuzzy_score", "char_similarity"]


def clean_title(title: str) -> str:
    """Normalize a track/video title by stripping common noise and suffixes."""
    if not title:
        return ""
    suffixes_to_remove = [
        r"\s*\(official\s+video\)",
        r"\s*\(official\s+music\s+video\)",
        r"\s*\(lyrics\)",
        r"\s*\(lyric\s+video\)",
        r"\s*\(audio\)",
        r"\s*\(official\s+audio\)",
        r"\s*\(hq\)",
        r"\s*\(hd\)",
        r"\s*\(4k\)",
        r"\s*\(remastered\)",
        r"\s*\(remaster\)",
        r"\s*\(live\)",
        r"\s*\(live\s+performance\)",
        r"\s*\(acoustic\)",
        r"\s*\(cover\)",
        r"\s*\(ft\.\?\s+.*?\)",
        r"\s*\(feat\.\?\s+.*?\)",
        r"\s*\(featuring\s+.*?\)",
        r"\s*\[.*?\]",
        r"\s*\(.*?version.*?\)",
        r"\s*\(.*?edit.*?\)",
        r"\s*\(.*?mix.*?\)",
    ]
    cleaned = title.strip()
    for pattern in suffixes_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().strip(".,;:!?")
    return cleaned


def clean_artist(artist: str) -> str:
    """Normalize an artist/channel name by stripping decorations."""
    if not artist:
        return ""
    suffixes_to_remove = [
        r"\s*\(official\)",
        r"\s*\(official\s+channel\)",
        r"\s*\(music\)",
        r"\s*\(vevo\)",
        r"\s*\(topic\)",
        r"\s*-\s*topic\s*$",
        r"\s*\[.*?\]",
    ]
    cleaned = artist.strip()
    for pattern in suffixes_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def char_similarity(text1: str, text2: str) -> float:
    """Normalized Levenshtein-based similarity in 0..1 (1 = identical)."""
    if not text1 or not text2:
        return 0.0

    def levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    distance = levenshtein_distance(text1, text2)
    max_len = max(len(text1), len(text2))
    if max_len == 0:
        return 1.0
    return 1.0 - (distance / max_len)


def fuzzy_score(text1: str, text2: str) -> int:
    """Fuzzy match score 0..100 combining word and character similarity."""
    if not text1 or not text2:
        return 0
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()
    if t1 == t2:
        return 100
    if t1 in t2 or t2 in t1:
        return 80
    words1 = set(t1.split())
    words2 = set(t2.split())
    if not words1 or not words2:
        return 0
    inter = words1 & words2
    union = words1 | words2
    word_similarity = len(inter) / len(union) if union else 0
    char_sim = char_similarity(t1, t2)
    return int((word_similarity * 70) + (char_sim * 30))
