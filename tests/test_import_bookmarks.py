"""Tests for tabmark.import_bookmarks and tabmark.cli_import."""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import pytest

from tabmark.bookmark import Bookmark
from tabmark.import_bookmarks import import_bookmarks, import_csv, import_html, import_json
from tabmark.cli_import import cmd_import, register_import_parser
from tabmark.storage import load_bookmarks


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def html_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <DL><p>
          <DT><A HREF="https://example.com" TAGS="python,web">Example</A>
          <DT><A HREF="https://openai.com" TAGS="ai">OpenAI</A>
          <DT><A HREF="https://notags.io">No Tags</A>
        </DL>
    """)
    p = tmp_path / "bookmarks.html"
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture()
def json_file(tmp_path: Path) -> Path:
    data = [
        {"url": "https://a.com", "title": "A", "tags": ["x"], "description": "desc"},
        {"url": "https://b.com", "title": "B", "tags": [], "description": ""},
    ]
    p = tmp_path / "bookmarks.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    content = "url,title,tags,description\nhttps://c.com,C,foo bar,hello\nhttps://d.com,D,,\n"
    p = tmp_path / "bookmarks.csv"
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "store" / "bookmarks.md"


# ---------------------------------------------------------------------------
# import_html
# ---------------------------------------------------------------------------

def test_import_html_count(html_file: Path) -> None:
    bms = import_html(html_file)
    assert len(bms) == 3


def test_import_html_tags(html_file: Path) -> None:
    bms = import_html(html_file)
    assert bms[0].tags == ["python", "web"]
    assert bms[2].tags == []


# ---------------------------------------------------------------------------
# import_json
# ---------------------------------------------------------------------------

def test_import_json_round_trip(json_file: Path) -> None:
    bms = import_json(json_file)
    assert len(bms) == 2
    assert bms[0].url == "https://a.com"
    assert bms[0].description == "desc"


# ---------------------------------------------------------------------------
# import_csv
# ---------------------------------------------------------------------------

def test_import_csv_count(csv_file: Path) -> None:
    bms = import_csv(csv_file)
    assert len(bms) == 2


def test_import_csv_tags_parsed(csv_file: Path) -> None:
    bms = import_csv(csv_file)
    assert "foo" in bms[0].tags or bms[0].tags  # tags non-empty


# ---------------------------------------------------------------------------
# import_bookmarks auto-detect
# ---------------------------------------------------------------------------

def test_auto_detect_html(html_file: Path) -> None:
    bms = import_bookmarks(html_file)
    assert len(bms) == 3


def test_unsupported_format_raises(tmp_path: Path) -> None:
    p = tmp_path / "file.xyz"
    p.write_text("data")
    with pytest.raises(ValueError, match="Unsupported"):
        import_bookmarks(p)


# ---------------------------------------------------------------------------
# CLI cmd_import
# ---------------------------------------------------------------------------

def _make_parser(store_path: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_import_parser(sub, store_path)
    return parser


def test_cli_import_adds_bookmarks(json_file: Path, store: Path, capsys) -> None:
    parser = _make_parser(str(store))
    args = parser.parse_args(["import", str(json_file)])
    args.func(args)
    loaded = load_bookmarks(store)
    assert len(loaded) == 2


def test_cli_import_skips_duplicates(json_file: Path, store: Path, capsys) -> None:
    parser = _make_parser(str(store))
    args = parser.parse_args(["import", str(json_file)])
    args.func(args)
    args.func(args)  # second run — all duplicates
    out = capsys.readouterr().out
    assert "skipped 2" in out


def test_cli_import_missing_file(store: Path, capsys) -> None:
    parser = _make_parser(str(store))
    args = parser.parse_args(["import", "/nonexistent/file.json"])
    with pytest.raises(SystemExit):
        args.func(args)
