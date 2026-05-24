"""Tests for tabmark.sync."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tabmark.bookmark import Bookmark, to_markdown_line
from tabmark.storage import save_bookmarks
from tabmark.sync import sync_from_markdown, sync_to_markdown


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "data" / "bookmarks.json"


@pytest.fixture()
def sample_bookmarks() -> list[Bookmark]:
    return [
        Bookmark(url="https://example.com", title="Example", tags=["web"]),
        Bookmark(
            url="https://python.org",
            title="Python",
            description="Official site",
            tags=["python", "dev"],
        ),
    ]


# ---------------------------------------------------------------------------
# sync_to_markdown
# ---------------------------------------------------------------------------


def test_sync_to_markdown_creates_file(store, sample_bookmarks, tmp_path):
    save_bookmarks(store, sample_bookmarks)
    out = tmp_path / "out.md"
    result = sync_to_markdown(store, out)
    assert out.exists()
    assert result.markdown_path == out


def test_sync_to_markdown_result_added_when_new(store, sample_bookmarks, tmp_path):
    save_bookmarks(store, sample_bookmarks)
    out = tmp_path / "out.md"
    result = sync_to_markdown(store, out)
    assert result.added == len(sample_bookmarks)
    assert result.unchanged == 0


def test_sync_to_markdown_result_unchanged_when_exists(store, sample_bookmarks, tmp_path):
    save_bookmarks(store, sample_bookmarks)
    out = tmp_path / "out.md"
    out.write_text("existing content")
    result = sync_to_markdown(store, out)
    assert result.unchanged == len(sample_bookmarks)
    assert result.added == 0


def test_sync_to_markdown_content_contains_urls(store, sample_bookmarks, tmp_path):
    save_bookmarks(store, sample_bookmarks)
    out = tmp_path / "out.md"
    sync_to_markdown(store, out)
    content = out.read_text()
    for bm in sample_bookmarks:
        assert bm.url in content


# ---------------------------------------------------------------------------
# sync_from_markdown
# ---------------------------------------------------------------------------


def test_sync_from_markdown_adds_new_bookmarks(store, sample_bookmarks, tmp_path):
    md = tmp_path / "import.md"
    lines = [to_markdown_line(bm) for bm in sample_bookmarks]
    md.write_text("\n".join(lines))
    result = sync_from_markdown(md, store)
    assert result.added == len(sample_bookmarks)


def test_sync_from_markdown_skips_duplicates(store, sample_bookmarks, tmp_path):
    save_bookmarks(store, sample_bookmarks)
    md = tmp_path / "import.md"
    lines = [to_markdown_line(bm) for bm in sample_bookmarks]
    md.write_text("\n".join(lines))
    result = sync_from_markdown(md, store)
    assert result.added == 0
    assert result.unchanged == len(sample_bookmarks)


def test_sync_from_markdown_skips_invalid_lines(store, tmp_path):
    md = tmp_path / "import.md"
    md.write_text("# Heading\nsome random text\n\n")
    result = sync_from_markdown(md, store)
    assert result.added == 0


def test_sync_from_markdown_missing_file_adds_nothing(store, tmp_path):
    md = tmp_path / "nonexistent.md"
    result = sync_from_markdown(md, store)
    assert result.added == 0
