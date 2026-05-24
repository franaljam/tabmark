"""Import bookmarks from external formats (HTML, JSON, CSV)."""
from __future__ import annotations

import csv
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import List

from tabmark.bookmark import Bookmark


class _NetscapeParser(HTMLParser):
    """Minimal parser for Netscape-format bookmark HTML files."""

    def __init__(self) -> None:
        super().__init__()
        self._bookmarks: List[Bookmark] = []
        self._current_url: str = ""
        self._current_tags: List[str] = []
        self._capture: bool = False
        self._current_title: str = ""

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "a":
            attr_dict = dict(attrs)
            self._current_url = attr_dict.get("href", "")
            raw_tags = attr_dict.get("tags", "") or attr_dict.get("tags", "")
            self._current_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
            self._capture = True
            self._current_title = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture:
            if self._current_url:
                self._bookmarks.append(
                    Bookmark(
                        url=self._current_url,
                        title=self._current_title.strip() or self._current_url,
                        tags=self._current_tags,
                    )
                )
            self._capture = False

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._current_title += data


def import_html(path: Path) -> List[Bookmark]:
    """Import bookmarks from a Netscape-format HTML file."""
    parser = _NetscapeParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser._bookmarks


def import_json(path: Path) -> List[Bookmark]:
    """Import bookmarks from a JSON file (list of dicts)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Bookmark.from_dict(item) for item in data]


def import_csv(path: Path) -> List[Bookmark]:
    """Import bookmarks from a CSV file with columns: url, title, tags, description."""
    bookmarks: List[Bookmark] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            tags_raw = row.get("tags", "")
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            bookmarks.append(
                Bookmark(
                    url=row["url"],
                    title=row.get("title", row["url"]),
                    tags=tags,
                    description=row.get("description", "") or "",
                )
            )
    return bookmarks


def import_bookmarks(path: Path, fmt: str | None = None) -> List[Bookmark]:
    """Auto-detect format from extension or use *fmt* ('html', 'json', 'csv')."""
    if fmt is None:
        fmt = path.suffix.lstrip(".").lower()
    dispatch = {"html": import_html, "json": import_json, "csv": import_csv}
    if fmt not in dispatch:
        raise ValueError(f"Unsupported import format: {fmt!r}")
    return dispatch[fmt](path)
