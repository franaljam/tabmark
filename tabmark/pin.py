"""Pin/unpin bookmarks and retrieve pinned bookmarks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from tabmark.bookmark import Bookmark

PIN_TAG = "pinned"


@dataclass
class PinResult:
    url: str
    action: str  # 'pinned' | 'unpinned' | 'already_pinned' | 'not_pinned' | 'not_found'

    def __repr__(self) -> str:  # pragma: no cover
        return f"PinResult(url={self.url!r}, action={self.action!r})"


def is_pinned(bookmark: Bookmark) -> bool:
    """Return True if the bookmark carries the pin tag."""
    return PIN_TAG in (bookmark.tags or [])


def pin_bookmark(bookmarks: List[Bookmark], url: str) -> PinResult:
    """Add the pin tag to the bookmark matching *url*.

    Returns a :class:`PinResult` describing what happened.
    """
    for bm in bookmarks:
        if bm.url == url:
            if is_pinned(bm):
                return PinResult(url=url, action="already_pinned")
            tags = list(bm.tags or [])
            tags.insert(0, PIN_TAG)
            object.__setattr__(bm, "tags", tags)
            return PinResult(url=url, action="pinned")
    return PinResult(url=url, action="not_found")


def unpin_bookmark(bookmarks: List[Bookmark], url: str) -> PinResult:
    """Remove the pin tag from the bookmark matching *url*.

    Returns a :class:`PinResult` describing what happened.
    """
    for bm in bookmarks:
        if bm.url == url:
            if not is_pinned(bm):
                return PinResult(url=url, action="not_pinned")
            tags = [t for t in (bm.tags or []) if t != PIN_TAG]
            object.__setattr__(bm, "tags", tags)
            return PinResult(url=url, action="unpinned")
    return PinResult(url=url, action="not_found")


def get_pinned(bookmarks: List[Bookmark]) -> List[Bookmark]:
    """Return all bookmarks that are currently pinned, preserving order."""
    return [bm for bm in bookmarks if is_pinned(bm)]
