"""Search and filter bookmarks by various criteria."""

from __future__ import annotations

from typing import List, Optional

from tabmark.bookmark import Bookmark


def search_bookmarks(
    bookmarks: List[Bookmark],
    query: Optional[str] = None,
    tags: Optional[List[str]] = None,
    url_contains: Optional[str] = None,
) -> List[Bookmark]:
    """Return bookmarks matching all provided criteria.

    Args:
        bookmarks: Source list of bookmarks to search.
        query: Case-insensitive substring matched against title and description.
        tags: Every tag in this list must be present on the bookmark.
        url_contains: Case-insensitive substring matched against the URL.

    Returns:
        Filtered list of :class:`Bookmark` objects.
    """
    results = bookmarks

    if query:
        q = query.lower()
        results = [
            b for b in results
            if q in b.title.lower()
            or (b.description and q in b.description.lower())
        ]

    if tags:
        required = {t.lower() for t in tags}
        results = [
            b for b in results
            if required.issubset({t.lower() for t in (b.tags or [])})
        ]

    if url_contains:
        uc = url_contains.lower()
        results = [b for b in results if uc in b.url.lower()]

    return results


def filter_by_tag(bookmarks: List[Bookmark], tag: str) -> List[Bookmark]:
    """Convenience wrapper: return bookmarks that carry *tag* (case-insensitive)."""
    return search_bookmarks(bookmarks, tags=[tag])
