"""Bookmark rating support — store a 1-5 star rating in bookmark tags."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from tabmark.bookmark import Bookmark

_RATING_PREFIX = "rating:"
_VALID_RATINGS = {1, 2, 3, 4, 5}


@dataclass
class RatingResult:
    url: str
    previous: Optional[int]
    current: Optional[int]
    changed: bool

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RatingResult(url={self.url!r}, previous={self.previous}, "
            f"current={self.current}, changed={self.changed})"
        )


def get_rating(bookmark: Bookmark) -> Optional[int]:
    """Return the numeric rating (1-5) stored in the bookmark's tags, or None."""
    for tag in bookmark.tags:
        if tag.startswith(_RATING_PREFIX):
            try:
                value = int(tag[len(_RATING_PREFIX):])
                if value in _VALID_RATINGS:
                    return value
            except ValueError:
                pass
    return None


def set_rating(bookmark: Bookmark, rating: int) -> RatingResult:
    """Attach or replace a rating tag on *bookmark*. Raises ValueError for invalid ratings."""
    if rating not in _VALID_RATINGS:
        raise ValueError(f"Rating must be between 1 and 5, got {rating!r}")

    previous = get_rating(bookmark)
    # Remove any existing rating tags
    cleaned = [t for t in bookmark.tags if not t.startswith(_RATING_PREFIX)]
    cleaned.append(f"{_RATING_PREFIX}{rating}")
    bookmark.tags = cleaned
    changed = previous != rating
    return RatingResult(url=bookmark.url, previous=previous, current=rating, changed=changed)


def clear_rating(bookmark: Bookmark) -> RatingResult:
    """Remove the rating tag from *bookmark* if present."""
    previous = get_rating(bookmark)
    bookmark.tags = [t for t in bookmark.tags if not t.startswith(_RATING_PREFIX)]
    return RatingResult(url=bookmark.url, previous=previous, current=None, changed=previous is not None)


def get_bookmarks_by_rating(
    bookmarks: List[Bookmark], rating: int
) -> List[Bookmark]:
    """Return bookmarks that have exactly *rating* stars."""
    return [b for b in bookmarks if get_rating(b) == rating]


def get_top_rated(
    bookmarks: List[Bookmark], min_rating: int = 4
) -> List[Bookmark]:
    """Return bookmarks with a rating >= *min_rating*, sorted descending."""
    rated = [(b, get_rating(b)) for b in bookmarks]
    filtered = [(b, r) for b, r in rated if r is not None and r >= min_rating]
    filtered.sort(key=lambda br: br[1], reverse=True)  # type: ignore[return-value]
    return [b for b, _ in filtered]
