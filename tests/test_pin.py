"""Tests for tabmark.pin and tabmark.cli_pin."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from tabmark.bookmark import Bookmark
from tabmark.pin import (
    PIN_TAG,
    PinResult,
    get_pinned,
    is_pinned,
    pin_bookmark,
    unpin_bookmark,
)
from tabmark.storage import save_bookmarks


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _bm(url: str, tags=None) -> Bookmark:
    return Bookmark(url=url, title=url.split("/")[-1], tags=tags or [])


@pytest.fixture()
def bookmarks():
    return [
        _bm("https://example.com", ["dev"]),
        _bm("https://python.org", [PIN_TAG, "lang"]),
        _bm("https://github.com"),
    ]


# ---------------------------------------------------------------------------
# Unit tests – pin module
# ---------------------------------------------------------------------------


def test_is_pinned_false_when_no_pin_tag(bookmarks):
    assert is_pinned(bookmarks[0]) is False


def test_is_pinned_true_when_pin_tag_present(bookmarks):
    assert is_pinned(bookmarks[1]) is True


def test_pin_bookmark_adds_tag(bookmarks):
    result = pin_bookmark(bookmarks, "https://example.com")
    assert result.action == "pinned"
    assert PIN_TAG in bookmarks[0].tags


def test_pin_bookmark_already_pinned(bookmarks):
    result = pin_bookmark(bookmarks, "https://python.org")
    assert result.action == "already_pinned"


def test_pin_bookmark_not_found(bookmarks):
    result = pin_bookmark(bookmarks, "https://missing.io")
    assert result.action == "not_found"


def test_unpin_bookmark_removes_tag(bookmarks):
    result = unpin_bookmark(bookmarks, "https://python.org")
    assert result.action == "unpinned"
    assert PIN_TAG not in bookmarks[1].tags


def test_unpin_bookmark_not_pinned(bookmarks):
    result = unpin_bookmark(bookmarks, "https://github.com")
    assert result.action == "not_pinned"


def test_unpin_bookmark_not_found(bookmarks):
    result = unpin_bookmark(bookmarks, "https://missing.io")
    assert result.action == "not_found"


def test_get_pinned_returns_only_pinned(bookmarks):
    pinned = get_pinned(bookmarks)
    assert len(pinned) == 1
    assert pinned[0].url == "https://python.org"


def test_get_pinned_empty_when_none_pinned():
    bms = [_bm("https://a.com"), _bm("https://b.com")]
    assert get_pinned(bms) == []


# ---------------------------------------------------------------------------
# Integration tests – CLI
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path):
    p = tmp_path / "bookmarks.md"
    bms = [
        _bm("https://example.com", ["dev"]),
        _bm("https://python.org", ["lang"]),
    ]
    save_bookmarks(p, bms)
    return p


def _ns(store, **kwargs):
    ns = argparse.Namespace(store=store)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_cli_pin_adds_tag(store, capsys):
    from tabmark.cli_pin import cmd_pin
    from tabmark.storage import load_bookmarks

    cmd_pin(_ns(store, url="https://example.com"))
    bms = load_bookmarks(store)
    assert PIN_TAG in bms[0].tags
    out = capsys.readouterr().out
    assert "Pinned" in out


def test_cli_pin_already_pinned_no_save(store, capsys):
    from tabmark.cli_pin import cmd_pin

    cmd_pin(_ns(store, url="https://example.com"))
    cmd_pin(_ns(store, url="https://example.com"))
    out = capsys.readouterr().out
    assert "Already pinned" in out


def test_cli_pin_unknown_url_exits(store):
    from tabmark.cli_pin import cmd_pin

    with pytest.raises(SystemExit):
        cmd_pin(_ns(store, url="https://nope.io"))


def test_cli_unpin_removes_tag(store, capsys):
    from tabmark.cli_pin import cmd_pin, cmd_unpin
    from tabmark.storage import load_bookmarks

    cmd_pin(_ns(store, url="https://python.org"))
    cmd_unpin(_ns(store, url="https://python.org"))
    bms = load_bookmarks(store)
    assert PIN_TAG not in bms[1].tags


def test_cli_list_pinned_shows_pinned(store, capsys):
    from tabmark.cli_pin import cmd_list_pinned, cmd_pin

    cmd_pin(_ns(store, url="https://example.com"))
    cmd_list_pinned(_ns(store))
    out = capsys.readouterr().out
    assert "example.com" in out
