"""Tests for tabmark.dedupe."""

from __future__ import annotations

import pytest

from tabmark.bookmark import Bookmark
from tabmark.dedupe import deduplicate, find_duplicates


@pytest.fixture()
def bm() -> list[Bookmark]:
    return [
        Bookmark(url="https://example.com", title="Example", tags=["a"]),
        Bookmark(url="https://python.org", title="Python"),
        Bookmark(url="https://example.com/", title="Example (dup)", tags=["b"]),
        Bookmark(url="https://PYTHON.ORG", title="Python upper"),
        Bookmark(url="https://unique.io", title="Unique"),
    ]


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------

def test_find_duplicates_detects_url_duplicates(bm):
    groups = find_duplicates(bm)
    assert len(groups) == 2


def test_find_duplicates_groups_contain_correct_items(bm):
    groups = find_duplicates(bm)
    urls = {g[0].url.rstrip("/").lower() for g in groups}
    assert "https://example.com" in urls
    assert "https://python.org" in urls


def test_find_duplicates_returns_empty_for_unique_list():
    unique = [
        Bookmark(url="https://a.com", title="A"),
        Bookmark(url="https://b.com", title="B"),
    ]
    assert find_duplicates(unique) == []


def test_find_duplicates_empty_input():
    assert find_duplicates([]) == []


# ---------------------------------------------------------------------------
# deduplicate – keep='first'
# ---------------------------------------------------------------------------

def test_deduplicate_keep_first_removes_later(bm):
    result, removed = deduplicate(bm, keep="first")
    assert removed == 2
    titles = [b.title for b in result]
    assert "Example" in titles
    assert "Example (dup)" not in titles
    assert "Python" in titles
    assert "Python upper" not in titles


def test_deduplicate_keep_first_preserves_order(bm):
    result, _ = deduplicate(bm, keep="first")
    assert result[0].title == "Example"


# ---------------------------------------------------------------------------
# deduplicate – keep='last'
# ---------------------------------------------------------------------------

def test_deduplicate_keep_last_replaces_with_later(bm):
    result, removed = deduplicate(bm, keep="last")
    assert removed == 2
    titles = [b.title for b in result]
    assert "Example (dup)" in titles
    assert "Example" not in titles


def test_deduplicate_result_length(bm):
    result, removed = deduplicate(bm)
    assert len(result) + removed == len(bm)


def test_deduplicate_no_duplicates_unchanged():
    unique = [
        Bookmark(url="https://a.com", title="A"),
        Bookmark(url="https://b.com", title="B"),
    ]
    result, removed = deduplicate(unique)
    assert removed == 0
    assert len(result) == 2


def test_deduplicate_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate([], keep="newest")  # type: ignore[arg-type]
