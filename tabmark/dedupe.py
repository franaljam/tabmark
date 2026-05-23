"""Deduplication utilities for bookmarks."""

from __future__ import annotations

from typing import List, Tuple

from tabmark.bookmark import Bookmark


def find_duplicates(bookmarks: List[Bookmark]) -> List[List[Bookmark]]:
    """Return groups of bookmarks that share the same URL.

    Each group contains two or more Bookmark objects with identical URLs
    (compared case-insensitively, ignoring a trailing slash).
    """
    from collections import defaultdict

    groups: dict[str, List[Bookmark]] = defaultdict(list)
    for bm in bookmarks:
        key = bm.url.rstrip("/").lower()
        groups[key].append(bm)

    return [group for group in groups.values() if len(group) > 1]


def deduplicate(
    bookmarks: List[Bookmark],
    *,
    keep: str = "first",
) -> Tuple[List[Bookmark], int]:
    """Remove duplicate bookmarks, keeping one representative per URL.

    Parameters
    ----------
    bookmarks:
        Input list of bookmarks (not mutated).
    keep:
        ``"first"`` keeps the earliest occurrence; ``"last"`` keeps the
        latest occurrence.

    Returns
    -------
    (deduplicated_list, removed_count)
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    seen: dict[str, int] = {}  # normalised URL -> index in result list
    result: List[Bookmark] = []
    removed = 0

    for bm in bookmarks:
        key = bm.url.rstrip("/").lower()
        if key in seen:
            if keep == "last":
                result[seen[key]] = bm
            removed += 1
        else:
            seen[key] = len(result)
            result.append(bm)

    return result, removed
