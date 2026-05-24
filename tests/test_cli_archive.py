"""Tests for tabmark.cli_archive CLI commands."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from tabmark.archive import ARCHIVE_TAG, is_archived
from tabmark.bookmark import Bookmark
from tabmark.cli_archive import register_archive_parser
from tabmark.storage import load_bookmarks, save_bookmarks


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "bookmarks.md"


@pytest.fixture()
def parser(store: Path) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--store", default=store)
    sub = p.add_subparsers()
    register_archive_parser(sub)
    return p


@pytest.fixture()
def _two_bookmarks(store: Path) -> list[Bookmark]:
    bms = [
        Bookmark(url="https://active.com", title="Active", tags=["dev"]),
        Bookmark(url="https://old.com", title="Old Site", tags=[ARCHIVE_TAG]),
    ]
    save_bookmarks(store, bms)
    return bms


def test_archive_adds_tag(store: Path, parser: argparse.ArgumentParser, _two_bookmarks: list) -> None:
    args = parser.parse_args(["--store", str(store), "archive", "https://active.com"])
    args.func(args)
    bookmarks = load_bookmarks(store)
    target = next(b for b in bookmarks if b.url == "https://active.com")
    assert is_archived(target)


def test_archive_unknown_url_exits(store: Path, parser: argparse.ArgumentParser, _two_bookmarks: list) -> None:
    args = parser.parse_args(["--store", str(store), "archive", "https://missing.com"])
    with pytest.raises(SystemExit):
        args.func(args)


def test_unarchive_removes_tag(store: Path, parser: argparse.ArgumentParser, _two_bookmarks: list) -> None:
    args = parser.parse_args(["--store", str(store), "unarchive", "https://old.com"])
    args.func(args)
    bookmarks = load_bookmarks(store)
    target = next(b for b in bookmarks if b.url == "https://old.com")
    assert not is_archived(target)


def test_unarchive_active_bookmark_exits(store: Path, parser: argparse.ArgumentParser, _two_bookmarks: list) -> None:
    args = parser.parse_args(["--store", str(store), "unarchive", "https://active.com"])
    with pytest.raises(SystemExit):
        args.func(args)


def test_list_archived_prints_archived(store: Path, parser: argparse.ArgumentParser, _two_bookmarks: list, capsys: pytest.CaptureFixture) -> None:
    args = parser.parse_args(["--store", str(store), "list-archived"])
    args.func(args)
    out = capsys.readouterr().out
    assert "https://old.com" in out
    assert "https://active.com" not in out


def test_list_archived_empty_store(store: Path, parser: argparse.ArgumentParser, capsys: pytest.CaptureFixture) -> None:
    save_bookmarks(store, [])
    args = parser.parse_args(["--store", str(store), "list-archived"])
    args.func(args)
    out = capsys.readouterr().out
    assert "No archived" in out
