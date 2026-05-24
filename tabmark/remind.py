"""Bookmark reminder: surface bookmarks that haven't been visited recently."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

from tabmark.bookmark import Bookmark


@dataclass
class RemindResult:
    """Result of a reminder query."""

    due: List[Bookmark] = field(default_factory=list)
    snoozed: List[Bookmark] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RemindResult(due={len(self.due)}, snoozed={len(self.snoozed)})"
        )


def _parse_date(value: str) -> Optional[date]:
    """Parse an ISO-8601 date string, returning None on failure."""
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def get_due_bookmarks(
    bookmarks: List[Bookmark],
    *,
    days: int = 30,
    reference: Optional[date] = None,
) -> RemindResult:
    """Return bookmarks whose ``remind_after`` tag date has passed.

    A bookmark opts in to reminders by including a tag of the form
    ``remind:YYYY-MM-DD``.  Bookmarks whose reminder date is on or before
    *reference* (defaults to today) are placed in ``RemindResult.due``;
    bookmarks with a future reminder date go into ``RemindResult.snoozed``.

    Bookmarks without any ``remind:`` tag are ignored entirely.

    Args:
        bookmarks: Full list of bookmarks to inspect.
        days: Fallback — if a bookmark has no ``remind:`` tag but was added
              more than *days* days ago (checked via an ``added:YYYY-MM-DD``
              tag), it is also considered due.
        reference: Date to compare against; defaults to :func:`date.today`.
    """
    ref = reference or date.today()
    cutoff = ref - timedelta(days=days)
    result = RemindResult()

    for bm in bookmarks:
        remind_date: Optional[date] = None
        added_date: Optional[date] = None

        for tag in bm.tags:
            if tag.startswith("remind:"):
                remind_date = _parse_date(tag[len("remind:"):])
            elif tag.startswith("added:"):
                added_date = _parse_date(tag[len("added:"):])

        if remind_date is not None:
            if remind_date <= ref:
                result.due.append(bm)
            else:
                result.snoozed.append(bm)
        elif added_date is not None and added_date <= cutoff:
            result.due.append(bm)

    return result
