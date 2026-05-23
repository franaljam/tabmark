"""Tag management utilities for tabmark bookmarks."""

from collections import Counter
from typing import List, Dict

from tabmark.bookmark import Bookmark


def collect_all_tags(bookmarks: List[Bookmark]) -> List[str]:
    """Return a sorted list of unique tags across all bookmarks."""
    tag_set: set = set()
    for bm in bookmarks:
        tag_set.update(bm.tags)
    return sorted(tag_set)


def tag_frequency(bookmarks: List[Bookmark]) -> Dict[str, int]:
    """Return a dict mapping each tag to the number of bookmarks that use it."""
    counter: Counter = Counter()
    for bm in bookmarks:
        counter.update(bm.tags)
    return dict(counter)


def rename_tag(bookmarks: List[Bookmark], old_tag: str, new_tag: str) -> List[Bookmark]:
    """Return a new list of bookmarks with *old_tag* replaced by *new_tag*.

    Bookmarks that do not carry *old_tag* are returned unchanged.
    Duplicate tags introduced by the rename are deduplicated while preserving
    the original tag order.
    """
    updated: List[Bookmark] = []
    for bm in bookmarks:
        if old_tag in bm.tags:
            new_tags: List[str] = []
            seen: set = set()
            for t in bm.tags:
                effective = new_tag if t == old_tag else t
                if effective not in seen:
                    new_tags.append(effective)
                    seen.add(effective)
            updated.append(
                Bookmark(
                    url=bm.url,
                    title=bm.title,
                    tags=new_tags,
                    description=bm.description,
                    created_at=bm.created_at,
                )
            )
        else:
            updated.append(bm)
    return updated


def remove_tag(bookmarks: List[Bookmark], tag: str) -> List[Bookmark]:
    """Return a new list of bookmarks with *tag* stripped from every bookmark."""
    updated: List[Bookmark] = []
    for bm in bookmarks:
        if tag in bm.tags:
            updated.append(
                Bookmark(
                    url=bm.url,
                    title=bm.title,
                    tags=[t for t in bm.tags if t != tag],
                    description=bm.description,
                    created_at=bm.created_at,
                )
            )
        else:
            updated.append(bm)
    return updated
