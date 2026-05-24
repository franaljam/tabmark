"""Bookmark archiving: mark bookmarks as archived and filter them out of active lists."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from tabmark.bookmark import Bookmark

ARCHIVE_TAG = "archived"


@dataclass
class ArchiveResult:
    archived: List[Bookmark] = field(default_factory=list)
    unarchived: List[Bookmark] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ArchiveResult(archived={len(self.archived)}, "
            f"unarchived={len(self.unarchived)})"
        )


def archive_bookmark(bookmark: Bookmark) -> Bookmark:
    """Return a copy of *bookmark* with the archive tag added."""
    tags = list(bookmark.tags)
    if ARCHIVE_TAG not in tags:
        tags.append(ARCHIVE_TAG)
    return Bookmark(
        url=bookmark.url,
        title=bookmark.title,
        tags=tags,
        description=bookmark.description,
        added=bookmark.added,
    )


def unarchive_bookmark(bookmark: Bookmark) -> Bookmark:
    """Return a copy of *bookmark* with the archive tag removed."""
    tags = [t for t in bookmark.tags if t != ARCHIVE_TAG]
    return Bookmark(
        url=bookmark.url,
        title=bookmark.title,
        tags=tags,
        description=bookmark.description,
        added=bookmark.added,
    )


def is_archived(bookmark: Bookmark) -> bool:
    """Return True if *bookmark* carries the archive tag."""
    return ARCHIVE_TAG in bookmark.tags


def partition_bookmarks(
    bookmarks: List[Bookmark],
) -> Tuple[List[Bookmark], List[Bookmark]]:
    """Split *bookmarks* into (active, archived) lists."""
    active = [b for b in bookmarks if not is_archived(b)]
    archived = [b for b in bookmarks if is_archived(b)]
    return active, archived


def get_archived(bookmarks: List[Bookmark]) -> ArchiveResult:
    """Return an :class:`ArchiveResult` describing the current archive state."""
    active, archived = partition_bookmarks(bookmarks)
    return ArchiveResult(archived=archived, unarchived=active)
