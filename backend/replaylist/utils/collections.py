"""Collection utilities."""

from typing import Any, List


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


