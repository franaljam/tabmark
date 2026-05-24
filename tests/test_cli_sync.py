"""Tests for tabmark.cli_sync."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from tabmark.bookmark import Bookmark, to_markdown_line
from tabmark.cli_sync import register_sync_parser
from tabmark.storage import save_bookmarks


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "bookmarks.json"


@pytest.fixture()
def parser(store: Path) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register_sync_parser(sub, default_store=str(store))
    return p


@pytest.fixture()
def _two_bookmarks(store: Path) -> list[Bookmark]:
    bms = [
        Bookmark(url="https://a.com", title="A"),
        Bookmark(url="https://b.com", title="B", tags=["x"]),
    ]
    save_bookmarks(store, bms)
    return bms


def test_sync_export_creates_markdown(parser, store, _two_bookmarks, tmp_path, capsys):
    out = tmp_path / "out.md"
    args = parser.parse_args(["sync-export", "--output", str(out)])
    args.func(args)
    assert out.exists()


def test_sync_export_prints_count(parser, store, _two_bookmarks, tmp_path, capsys):
    out = tmp_path / "out.md"
    args = parser.parse_args(["sync-export", "--output", str(out)])
    args.func(args)
    captured = capsys.readouterr()
    assert "2" in captured.out


def test_sync_import_adds_bookmarks(parser, store, tmp_path, capsys):
    bms = [Bookmark(url="https://c.com", title="C")]
    md = tmp_path / "import.md"
    md.write_text(to_markdown_line(bms[0]))
    args = parser.parse_args(["sync-import", str(md)])
    args.func(args)
    captured = capsys.readouterr()
    assert "1" in captured.out


def test_sync_import_reports_already_present(parser, store, _two_bookmarks, tmp_path, capsys):
    md = tmp_path / "import.md"
    lines = [to_markdown_line(b) for b in _two_bookmarks]
    md.write_text("\n".join(lines))
    args = parser.parse_args(["sync-import", str(md)])
    args.func(args)
    captured = capsys.readouterr()
    assert "already present" in captured.out
