"""Tests for tabmark.search."""

from __future__ import annotations

import pytest

from tabmark.bookmark import Bookmark
from tabmark.search import filter_by_tag, search_bookmarks


@pytest.fixture()
def sample_bookmarks() -> list[Bookmark]:
    return [
        Bookmark(url="https://python.org", title="Python", tags=["python", "lang"]),
        Bookmark(url="https://docs.python.org", title="Python Docs", tags=["python", "docs"], description="Official docs"),
        Bookmark(url="https://github.com", title="GitHub", tags=["git", "dev"]),
        Bookmark(url="https://example.com", title="Example Site", tags=[]),
    ]


def test_search_by_query_title(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, query="python")
    assert len(results) == 2
    assert all("python" in b.title.lower() for b in results)


def test_search_by_query_description(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, query="official")
    assert len(results) == 1
    assert results[0].title == "Python Docs"


def test_search_by_single_tag(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, tags=["python"])
    assert len(results) == 2


def test_search_by_multiple_tags(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, tags=["python", "docs"])
    assert len(results) == 1
    assert results[0].title == "Python Docs"


def test_search_by_url_contains(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, url_contains="docs.python")
    assert len(results) == 1
    assert results[0].url == "https://docs.python.org"


def test_search_combined_criteria(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, query="python", tags=["docs"])
    assert len(results) == 1
    assert results[0].title == "Python Docs"


def test_search_no_match_returns_empty(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, query="nonexistent_xyz")
    assert results == []


def test_search_no_criteria_returns_all(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks)
    assert results == sample_bookmarks


def test_filter_by_tag_convenience(sample_bookmarks):
    results = filter_by_tag(sample_bookmarks, "dev")
    assert len(results) == 1
    assert results[0].title == "GitHub"


def test_tag_matching_is_case_insensitive(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, tags=["PYTHON"])
    assert len(results) == 2


def test_query_matching_is_case_insensitive(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, query="GITHUB")
    assert len(results) == 1


def test_search_by_url_contains_case_insensitive(sample_bookmarks):
    results = search_bookmarks(sample_bookmarks, url_contains="DOCS.PYTHON")
    assert len(results) == 1
    assert results[0].url == "https://docs.python.org"


def test_search_bookmark_with_no_tags(sample_bookmarks):
    """Bookmarks with empty tag lists should not appear in tag-filtered results."""
    results = search_bookmarks(sample_bookmarks, tags=["python"])
    assert all(b.url != "https://example.com" for b in results)
