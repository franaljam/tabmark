"""Attach and manage inline notes on bookmarks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from tabmark.bookmark import Bookmark

NOTE_PREFIX = "note:"


@dataclass
class NoteResult:
    url: str
    previous_note: Optional[str]
    new_note: Optional[str]
    action: str  # 'set', 'cleared', 'unchanged'

    def __repr__(self) -> str:  # pragma: no cover
        return f"NoteResult(url={self.url!r}, action={self.action!r})"


def get_note(bookmark: Bookmark) -> Optional[str]:
    """Return the note attached to *bookmark*, or None."""
    for tag in bookmark.tags:
        if tag.startswith(NOTE_PREFIX):
            return tag[len(NOTE_PREFIX):]
    return None


def set_note(bookmark: Bookmark, note: str) -> NoteResult:
    """Attach (or replace) a note on *bookmark*. Returns a NoteResult."""
    note = note.strip()
    previous = get_note(bookmark)
    # Remove any existing note tags
    cleaned = [t for t in bookmark.tags if not t.startswith(NOTE_PREFIX)]
    if note:
        cleaned.append(f"{NOTE_PREFIX}{note}")
        action = "set"
    else:
        action = "cleared"
    object.__setattr__(bookmark, "tags", cleaned)
    return NoteResult(url=bookmark.url, previous_note=previous, new_note=note or None, action=action)


def clear_note(bookmark: Bookmark) -> NoteResult:
    """Remove any note from *bookmark*."""
    return set_note(bookmark, "")


def bookmarks_with_notes(bookmarks: List[Bookmark]) -> List[Bookmark]:
    """Return only bookmarks that have a note attached."""
    return [b for b in bookmarks if get_note(b) is not None]
