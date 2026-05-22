"""Tests for the Bookmark model and MarkdownWriter."""

from datetime import datetime
from pathlib import Path

import pytest

from tabmark.bookmark import Bookmark
from tabmark.markdown_writer import render_markdown, write_markdown


# ---------------------------------------------------------------------------
# Bookmark model
# ---------------------------------------------------------------------------

class TestBookmark:
    def _sample(self, **kwargs) -> Bookmark:
        defaults = dict(
            title="Example",
            url="https://example.com",
            folder="Dev",
            tags=["python", "tools"],
            added_at=datetime(2024, 1, 15, 10, 0, 0),
            description="A handy site",
        )
        defaults.update(kwargs)
        return Bookmark(**defaults)

    def test_to_markdown_line_with_tags_and_description(self):
        bm = self._sample()
        line = bm.to_markdown_line()
        assert "[Example](https://example.com)" in line
        assert "A handy site" in line
        assert "`python`" in line
        assert "`tools`" in line

    def test_to_markdown_line_minimal(self):
        bm = Bookmark(title="Minimal", url="https://minimal.io")
        line = bm.to_markdown_line()
        assert line == "- [Minimal](https://minimal.io)"

    def test_round_trip_dict(self):
        bm = self._sample()
        restored = Bookmark.from_dict(bm.to_dict())
        assert restored.title == bm.title
        assert restored.url == bm.url
        assert restored.folder == bm.folder
        assert restored.tags == bm.tags
        assert restored.added_at == bm.added_at
        assert restored.description == bm.description

    def test_from_dict_missing_optional_fields(self):
        bm = Bookmark.from_dict({"title": "T", "url": "https://t.io"})
        assert bm.folder == "Unsorted"
        assert bm.tags == []
        assert bm.description is None


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------

class TestRenderMarkdown:
    def _bookmarks(self):
        return [
            Bookmark(title="Zsh Docs", url="https://zsh.org", folder="Shell"),
            Bookmark(title="Python", url="https://python.org", folder="Dev"),
            Bookmark(title="Awesome List", url="https://awesome.re", folder="Dev"),
        ]

    def test_contains_header(self):
        md = render_markdown(self._bookmarks())
        assert "# Bookmarks" in md

    def test_folders_as_h2(self):
        md = render_markdown(self._bookmarks())
        assert "## Dev" in md
        assert "## Shell" in md

    def test_folders_sorted(self):
        md = render_markdown(self._bookmarks())
        assert md.index("## Dev") < md.index("## Shell")

    def test_bookmarks_sorted_within_folder(self):
        md = render_markdown(self._bookmarks())
        assert md.index("Awesome List") < md.index("Python")

    def test_write_markdown(self, tmp_path):
        out = tmp_path / "output" / "bookmarks.md"
        write_markdown(self._bookmarks(), out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "## Dev" in content
