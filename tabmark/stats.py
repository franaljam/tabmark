"""Bookmark collection statistics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from tabmark.bookmark import Bookmark
from tabmark.tags import tag_frequency


@dataclass
class BookmarkStats:
    total: int
    tagged: int
    untagged: int
    unique_tags: int
    top_tags: List[tuple]  # list of (tag, count)
    avg_tags_per_bookmark: float


def compute_stats(bookmarks: List[Bookmark], top_n: int = 5) -> BookmarkStats:
    """Compute summary statistics for a list of bookmarks."""
    total = len(bookmarks)

    if total == 0:
        return BookmarkStats(
            total=0,
            tagged=0,
            untagged=0,
            unique_tags=0,
            top_tags=[],
            avg_tags_per_bookmark=0.0,
        )

    tagged = sum(1 for b in bookmarks if b.tags)
    untagged = total - tagged

    freq = tag_frequency(bookmarks)
    unique_tags = len(freq)
    top_tags = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

    total_tag_count = sum(len(b.tags) for b in bookmarks)
    avg_tags = round(total_tag_count / total, 2)

    return BookmarkStats(
        total=total,
        tagged=tagged,
        untagged=untagged,
        unique_tags=unique_tags,
        top_tags=top_tags,
        avg_tags_per_bookmark=avg_tags,
    )


def format_stats(stats: BookmarkStats) -> str:
    """Return a human-readable string summary of BookmarkStats."""
    lines = [
        f"Total bookmarks : {stats.total}",
        f"Tagged          : {stats.tagged}",
        f"Untagged        : {stats.untagged}",
        f"Unique tags     : {stats.unique_tags}",
        f"Avg tags/bmark  : {stats.avg_tags_per_bookmark}",
    ]
    if stats.top_tags:
        top = ", ".join(f"{t}({c})" for t, c in stats.top_tags)
        lines.append(f"Top tags        : {top}")
    return "\n".join(lines)
