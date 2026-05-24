"""Tests for tabmark.remind."""

from datetime import date

import pytest

from tabmark.bookmark import Bookmark
from tabmark.remind import RemindResult, _parse_date, get_due_bookmarks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REF = date(2024, 6, 15)


def _bm(title: str, tags=None) -> Bookmark:
    return Bookmark(url=f"https://example.com/{title}", title=title, tags=tags or [])


# ---------------------------------------------------------------------------
# _parse_date
# ---------------------------------------------------------------------------


def test_parse_date_valid():
    assert _parse_date("2024-01-31") == date(2024, 1, 31)


def test_parse_date_invalid_returns_none():
    assert _parse_date("not-a-date") is None


def test_parse_date_none_returns_none():
    assert _parse_date(None) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# get_due_bookmarks — remind: tag
# ---------------------------------------------------------------------------


def test_remind_tag_past_is_due():
    bm = _bm("old", tags=["remind:2024-06-01"])
    result = get_due_bookmarks([bm], reference=REF)
    assert bm in result.due
    assert bm not in result.snoozed


def test_remind_tag_today_is_due():
    bm = _bm("today", tags=["remind:2024-06-15"])
    result = get_due_bookmarks([bm], reference=REF)
    assert bm in result.due


def test_remind_tag_future_is_snoozed():
    bm = _bm("future", tags=["remind:2024-12-31"])
    result = get_due_bookmarks([bm], reference=REF)
    assert bm in result.snoozed
    assert bm not in result.due


# ---------------------------------------------------------------------------
# get_due_bookmarks — added: tag fallback
# ---------------------------------------------------------------------------


def test_added_tag_old_enough_is_due():
    bm = _bm("stale", tags=["added:2024-04-01"])
    result = get_due_bookmarks([bm], days=30, reference=REF)
    assert bm in result.due


def test_added_tag_too_recent_is_ignored():
    bm = _bm("fresh", tags=["added:2024-06-10"])
    result = get_due_bookmarks([bm], days=30, reference=REF)
    assert bm not in result.due
    assert bm not in result.snoozed


# ---------------------------------------------------------------------------
# get_due_bookmarks — no relevant tags
# ---------------------------------------------------------------------------


def test_bookmark_without_remind_or_added_tag_ignored():
    bm = _bm("plain", tags=["python", "tools"])
    result = get_due_bookmarks([bm], reference=REF)
    assert bm not in result.due
    assert bm not in result.snoozed


# ---------------------------------------------------------------------------
# get_due_bookmarks — empty input
# ---------------------------------------------------------------------------


def test_empty_list_returns_empty_result():
    result = get_due_bookmarks([], reference=REF)
    assert result.due == []
    assert result.snoozed == []


# ---------------------------------------------------------------------------
# RemindResult repr
# ---------------------------------------------------------------------------


def test_remind_result_repr():
    r = RemindResult(due=[_bm("a")], snoozed=[_bm("b"), _bm("c")])
    text = repr(r)
    assert "due=1" in text
    assert "snoozed=2" in text
