"""Tests for tabmark.notes."""
from __future__ import annotations

import pytest

from tabmark.bookmark import Bookmark
from tabmark.notes import (
    NoteResult,
    bookmarks_with_notes,
    clear_note,
    get_note,
    set_note,
)


@pytest.fixture()
def _bm() -> Bookmark:
    return Bookmark(url="https://example.com", title="Example", tags=[], description="")


def test_get_note_returns_none_when_no_note(_bm):
    assert get_note(_bm) is None


def test_get_note_returns_text_when_present():
    bm = Bookmark(url="https://x.com", title="X", tags=["note:read later"], description="")
    assert get_note(bm) == "read later"


def test_set_note_attaches_note(_bm):
    result = set_note(_bm, "important")
    assert get_note(_bm) == "important"
    assert result.action == "set"
    assert result.new_note == "important"
    assert result.previous_note is None


def test_set_note_replaces_existing_note():
    bm = Bookmark(url="https://x.com", title="X", tags=["note:old"], description="")
    result = set_note(bm, "new")
    assert get_note(bm) == "new"
    assert result.previous_note == "old"
    assert result.action == "set"


def test_set_note_with_empty_string_clears_note():
    bm = Bookmark(url="https://x.com", title="X", tags=["note:something"], description="")
    result = set_note(bm, "")
    assert get_note(bm) is None
    assert result.action == "cleared"
    assert result.new_note is None


def test_clear_note_removes_note():
    bm = Bookmark(url="https://x.com", title="X", tags=["note:hello", "python"], description="")
    result = clear_note(bm)
    assert get_note(bm) is None
    assert "python" in bm.tags
    assert result.action == "cleared"


def test_clear_note_on_bookmark_without_note(_bm):
    result = clear_note(_bm)
    assert result.action == "cleared"
    assert result.previous_note is None


def test_set_note_preserves_other_tags():
    bm = Bookmark(url="https://x.com", title="X", tags=["python", "dev"], description="")
    set_note(bm, "my note")
    assert "python" in bm.tags
    assert "dev" in bm.tags


def test_bookmarks_with_notes_filters_correctly():
    bms = [
        Bookmark(url="https://a.com", title="A", tags=["note:foo"], description=""),
        Bookmark(url="https://b.com", title="B", tags=[], description=""),
        Bookmark(url="https://c.com", title="C", tags=["note:bar"], description=""),
    ]
    result = bookmarks_with_notes(bms)
    assert len(result) == 2
    assert all(get_note(b) is not None for b in result)


def test_bookmarks_with_notes_empty_list():
    assert bookmarks_with_notes([]) == []


def test_note_result_repr():
    r = NoteResult(url="https://x.com", previous_note=None, new_note="hi", action="set")
    assert "set" in repr(r)
