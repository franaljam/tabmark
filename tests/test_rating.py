"""Tests for tabmark.rating."""
from __future__ import annotations

import pytest

from tabmark.bookmark import Bookmark
from tabmark.rating import (
    clear_rating,
    get_bookmarks_by_rating,
    get_rating,
    get_top_rated,
    set_rating,
)


def _bm(url: str = "https://example.com", tags: list[str] | None = None) -> Bookmark:
    return Bookmark(url=url, title="Example", tags=tags or [])


# ---------------------------------------------------------------------------
# get_rating
# ---------------------------------------------------------------------------

def test_get_rating_returns_none_when_no_tag():
    assert get_rating(_bm()) is None


def test_get_rating_returns_value():
    bm = _bm(tags=["python", "rating:4"])
    assert get_rating(bm) == 4


def test_get_rating_ignores_malformed_tag():
    bm = _bm(tags=["rating:bad"])
    assert get_rating(bm) is None


def test_get_rating_ignores_out_of_range():
    bm = _bm(tags=["rating:9"])
    assert get_rating(bm) is None


# ---------------------------------------------------------------------------
# set_rating
# ---------------------------------------------------------------------------

def test_set_rating_adds_tag():
    bm = _bm()
    result = set_rating(bm, 3)
    assert get_rating(bm) == 3
    assert result.current == 3
    assert result.previous is None
    assert result.changed is True


def test_set_rating_replaces_existing():
    bm = _bm(tags=["rating:2"])
    result = set_rating(bm, 5)
    assert get_rating(bm) == 5
    assert result.previous == 2
    assert result.current == 5
    assert result.changed is True
    # Only one rating tag present
    assert sum(1 for t in bm.tags if t.startswith("rating:")) == 1


def test_set_rating_unchanged_flag_when_same_value():
    bm = _bm(tags=["rating:4"])
    result = set_rating(bm, 4)
    assert result.changed is False


def test_set_rating_raises_for_invalid():
    bm = _bm()
    with pytest.raises(ValueError):
        set_rating(bm, 0)
    with pytest.raises(ValueError):
        set_rating(bm, 6)


# ---------------------------------------------------------------------------
# clear_rating
# ---------------------------------------------------------------------------

def test_clear_rating_removes_tag():
    bm = _bm(tags=["dev", "rating:3"])
    result = clear_rating(bm)
    assert get_rating(bm) is None
    assert result.previous == 3
    assert result.current is None
    assert result.changed is True


def test_clear_rating_no_op_when_not_set():
    bm = _bm(tags=["dev"])
    result = clear_rating(bm)
    assert result.changed is False


# ---------------------------------------------------------------------------
# get_bookmarks_by_rating / get_top_rated
# ---------------------------------------------------------------------------

def _sample_list() -> list[Bookmark]:
    return [
        _bm("https://a.com", ["rating:5"]),
        _bm("https://b.com", ["rating:3"]),
        _bm("https://c.com", ["rating:5"]),
        _bm("https://d.com", []),
        _bm("https://e.com", ["rating:2"]),
    ]


def test_get_bookmarks_by_rating_filters_correctly():
    bms = _sample_list()
    fives = get_bookmarks_by_rating(bms, 5)
    assert len(fives) == 2
    assert all(get_rating(b) == 5 for b in fives)


def test_get_bookmarks_by_rating_returns_empty_when_none_match():
    bms = _sample_list()
    assert get_bookmarks_by_rating(bms, 1) == []


def test_get_top_rated_default_min_four():
    bms = _sample_list()
    top = get_top_rated(bms)
    assert all(get_rating(b) is not None and (get_rating(b) or 0) >= 4 for b in top)


def test_get_top_rated_sorted_descending():
    bms = _sample_list()
    top = get_top_rated(bms, min_rating=2)
    ratings = [get_rating(b) for b in top]
    assert ratings == sorted(ratings, reverse=True)


def test_get_top_rated_excludes_unrated():
    bms = _sample_list()
    top = get_top_rated(bms, min_rating=1)
    urls = [b.url for b in top]
    assert "https://d.com" not in urls
