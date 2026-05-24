"""Tests for tabmark.cli_notes."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from tabmark.bookmark import Bookmark
from tabmark.cli_notes import cmd_clear_note, cmd_list_notes, cmd_set_note, register_notes_parser
from tabmark.notes import get_note
from tabmark.storage import load_bookmarks, save_bookmarks


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "marks.md"


@pytest.fixture()
def _two_bookmarks(store: Path) -> list[Bookmark]:
    bms = [
        Bookmark(url="https://alpha.com", title="Alpha", tags=[], description=""),
        Bookmark(url="https://beta.com", title="Beta", tags=["note:existing"], description=""),
    ]
    save_bookmarks(store, bms)
    return bms


def _ns(store, **kwargs):
    return argparse.Namespace(store=store, **kwargs)


def test_set_note_persists(store, _two_bookmarks):
    cmd_set_note(_ns(store, url="https://alpha.com", note="check this"))
    bms = load_bookmarks(store)
    target = next(b for b in bms if b.url == "https://alpha.com")
    assert get_note(target) == "check this"


def test_set_note_replaces_existing(store, _two_bookmarks):
    cmd_set_note(_ns(store, url="https://beta.com", note="updated"))
    bms = load_bookmarks(store)
    target = next(b for b in bms if b.url == "https://beta.com")
    assert get_note(target) == "updated"


def test_set_note_unknown_url_exits(store, _two_bookmarks):
    with pytest.raises(SystemExit):
        cmd_set_note(_ns(store, url="https://unknown.com", note="hi"))


def test_clear_note_removes_note(store, _two_bookmarks):
    cmd_clear_note(_ns(store, url="https://beta.com"))
    bms = load_bookmarks(store)
    target = next(b for b in bms if b.url == "https://beta.com")
    assert get_note(target) is None


def test_clear_note_unknown_url_exits(store, _two_bookmarks):
    with pytest.raises(SystemExit):
        cmd_clear_note(_ns(store, url="https://nope.com"))


def test_list_notes_prints_noted_bookmarks(store, _two_bookmarks, capsys):
    cmd_list_notes(_ns(store))
    out = capsys.readouterr().out
    assert "https://beta.com" in out
    assert "existing" in out
    assert "https://alpha.com" not in out


def test_list_notes_empty_store(store, capsys):
    save_bookmarks(store, [])
    cmd_list_notes(_ns(store))
    out = capsys.readouterr().out
    assert "No bookmarks" in out


def test_register_notes_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--store", default="marks.md")
    subs = parser.add_subparsers(dest="cmd")
    register_notes_parser(subs, parent)
    args = parser.parse_args(["notes", "list"])
    assert args.notes_cmd == "list"
