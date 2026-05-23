"""Tests for tabmark.export and tabmark.cli_export."""

from __future__ import annotations

import json
import csv
import io
from pathlib import Path

import pytest

from tabmark.bookmark import Bookmark
from tabmark.export import export_html, export_json, export_csv, export_bookmarks


@pytest.fixture()
def sample() -> list[Bookmark]:
    return [
        Bookmark(title="Python", url="https://python.org", tags=["dev", "lang"], description="Official site"),
        Bookmark(title="GitHub", url="https://github.com", tags=[], description=None),
    ]


# --- HTML ---

def test_export_html_contains_urls(sample):
    html = export_html(sample)
    assert "https://python.org" in html
    assert "https://github.com" in html


def test_export_html_contains_tags(sample):
    html = export_html(sample)
    assert 'TAGS="dev lang"' in html


def test_export_html_contains_description(sample):
    html = export_html(sample)
    assert "Official site" in html


def test_export_html_no_tags_attr_when_empty(sample):
    html = export_html(sample)
    # GitHub bookmark has no tags — TAGS attribute must not appear for it
    lines = [l for l in html.splitlines() if "github.com" in l]
    assert lines
    assert "TAGS=" not in lines[0]


# --- JSON ---

def test_export_json_valid(sample):
    raw = export_json(sample)
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) == 2


def test_export_json_fields(sample):
    data = json.loads(export_json(sample))
    first = data[0]
    assert first["title"] == "Python"
    assert first["url"] == "https://python.org"
    assert first["tags"] == ["dev", "lang"]


# --- CSV ---

def test_export_csv_valid(sample):
    raw = export_csv(sample)
    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    assert len(rows) == 2


def test_export_csv_tags_joined(sample):
    raw = export_csv(sample)
    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    assert rows[0]["tags"] == "dev,lang"
    assert rows[1]["tags"] == ""


# --- dispatch ---

def test_export_bookmarks_unknown_format_raises(sample):
    with pytest.raises(ValueError, match="Unknown export format"):
        export_bookmarks(sample, "xml")


def test_export_bookmarks_dispatches_correctly(sample):
    result = export_bookmarks(sample, "json")
    assert json.loads(result)  # valid JSON

    result = export_bookmarks(sample, "csv")
    assert "title" in result  # has header

    result = export_bookmarks(sample, "html")
    assert "NETSCAPE" in result
