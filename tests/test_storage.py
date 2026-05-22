"""Tests for tabmark.storage."""

import json
import os
import pytest

from tabmark.bookmark import Bookmark
from tabmark.storage import (
    add_bookmark,
    load_bookmarks,
    remove_bookmark,
    save_bookmarks,
)


@pytest.fixture()
def store_path(tmp_path):
    return str(tmp_path / "bookmarks.json")


def _make_bookmark(url="https://example.com", title="Example"):
    return Bookmark(url=url, title=title, tags=["test"], description="A test bookmark")


# ---------------------------------------------------------------------------
# load / save round-trip
# ---------------------------------------------------------------------------

def test_load_returns_empty_list_when_file_missing(store_path):
    bookmarks = load_bookmarks(store_path)
    assert bookmarks == []


def test_save_and_load_round_trip(store_path):
    original = [_make_bookmark(), _make_bookmark(url="https://other.com", title="Other")]
    save_bookmarks(original, store_path)

    loaded = load_bookmarks(store_path)
    assert len(loaded) == 2
    assert loaded[0].url == "https://example.com"
    assert loaded[1].title == "Other"


def test_save_creates_parent_directories(tmp_path, store_path):
    nested_path = str(tmp_path / "a" / "b" / "c" / "bookmarks.json")
    save_bookmarks([], nested_path)
    assert os.path.exists(nested_path)


def test_load_raises_on_invalid_json_structure(store_path):
    with open(store_path, "w") as fh:
        json.dump({"not": "a list"}, fh)

    with pytest.raises(ValueError, match="Expected a JSON array"):
        load_bookmarks(store_path)


# ---------------------------------------------------------------------------
# add_bookmark
# ---------------------------------------------------------------------------

def test_add_bookmark_persists(store_path):
    bm = _make_bookmark()
    result = add_bookmark(bm, store_path)
    assert len(result) == 1
    assert load_bookmarks(store_path)[0].url == bm.url


def test_add_bookmark_skips_duplicate_url(store_path):
    bm = _make_bookmark()
    add_bookmark(bm, store_path)
    result = add_bookmark(bm, store_path)
    assert len(result) == 1


def test_add_multiple_bookmarks(store_path):
    add_bookmark(_make_bookmark(url="https://a.com", title="A"), store_path)
    add_bookmark(_make_bookmark(url="https://b.com", title="B"), store_path)
    assert len(load_bookmarks(store_path)) == 2


# ---------------------------------------------------------------------------
# remove_bookmark
# ---------------------------------------------------------------------------

def test_remove_bookmark(store_path):
    bm = _make_bookmark()
    add_bookmark(bm, store_path)
    result = remove_bookmark(bm.url, store_path)
    assert result == []
    assert load_bookmarks(store_path) == []


def test_remove_nonexistent_url_is_noop(store_path):
    bm = _make_bookmark()
    add_bookmark(bm, store_path)
    result = remove_bookmark("https://not-there.com", store_path)
    assert len(result) == 1
