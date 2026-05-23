"""Integration tests for the dedupe CLI sub-command."""

from __future__ import annotations

import json
import pathlib

import pytest

from tabmark.bookmark import Bookmark
from tabmark.cli_dedupe import register_dedupe_parser
from tabmark.storage import save_bookmarks

import argparse


@pytest.fixture()
def store(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "bookmarks.json"


def _parser(store: pathlib.Path) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.set_defaults(store=store)
    sub = p.add_subparsers()
    register_dedupe_parser(sub)
    return p


def _bookmarks_with_dups() -> list[Bookmark]:
    return [
        Bookmark(url="https://example.com", title="First"),
        Bookmark(url="https://python.org", title="Python"),
        Bookmark(url="https://example.com/", title="Duplicate"),
    ]


def test_dedupe_removes_duplicates(store, capsys):
    save_bookmarks(store, _bookmarks_with_dups())
    p = _parser(store)
    args = p.parse_args(["dedupe"])
    args.func(args)
    data = json.loads(store.read_text())
    urls = [d["url"] for d in data]
    assert urls.count("https://example.com") == 1
    assert "https://example.com/" not in urls


def test_dedupe_reports_removed_count(store, capsys):
    save_bookmarks(store, _bookmarks_with_dups())
    p = _parser(store)
    args = p.parse_args(["dedupe"])
    args.func(args)
    out = capsys.readouterr().out
    assert "1" in out


def test_dedupe_dry_run_does_not_modify_store(store, capsys):
    save_bookmarks(store, _bookmarks_with_dups())
    original = store.read_text()
    p = _parser(store)
    args = p.parse_args(["dedupe", "--dry-run"])
    args.func(args)
    assert store.read_text() == original


def test_dedupe_dry_run_prints_groups(store, capsys):
    save_bookmarks(store, _bookmarks_with_dups())
    p = _parser(store)
    args = p.parse_args(["dedupe", "--dry-run"])
    args.func(args)
    out = capsys.readouterr().out
    assert "example.com" in out.lower()


def test_dedupe_no_duplicates_message(store, capsys):
    unique = [Bookmark(url="https://a.com", title="A")]
    save_bookmarks(store, unique)
    p = _parser(store)
    args = p.parse_args(["dedupe"])
    args.func(args)
    out = capsys.readouterr().out
    assert "No duplicates" in out
