"""Tests for tabmark.stats."""

import pytest

from tabmark.bookmark import Bookmark
from tabmark.stats import BookmarkStats, compute_stats, format_stats


@pytest.fixture()
def bookmarks():
    return [
        Bookmark(url="https://a.com", title="A", tags=["python", "dev"], description=""),
        Bookmark(url="https://b.com", title="B", tags=["python"], description="B desc"),
        Bookmark(url="https://c.com", title="C", tags=[], description=""),
        Bookmark(url="https://d.com", title="D", tags=["rust", "dev"], description=""),
    ]


def test_compute_stats_total(bookmarks):
    stats = compute_stats(bookmarks)
    assert stats.total == 4


def test_compute_stats_tagged_untagged(bookmarks):
    stats = compute_stats(bookmarks)
    assert stats.tagged == 3
    assert stats.untagged == 1


def test_compute_stats_unique_tags(bookmarks):
    stats = compute_stats(bookmarks)
    assert stats.unique_tags == 3  # python, dev, rust


def test_compute_stats_top_tags(bookmarks):
    stats = compute_stats(bookmarks)
    top_tag_names = [t for t, _ in stats.top_tags]
    # python and dev both appear twice; rust once
    assert "python" in top_tag_names
    assert "dev" in top_tag_names
    assert "rust" in top_tag_names


def test_compute_stats_avg_tags(bookmarks):
    stats = compute_stats(bookmarks)
    # total tags: 2+1+0+2 = 5, total bmarks: 4 => 1.25
    assert stats.avg_tags_per_bookmark == 1.25


def test_compute_stats_empty_list():
    stats = compute_stats([])
    assert stats.total == 0
    assert stats.tagged == 0
    assert stats.untagged == 0
    assert stats.unique_tags == 0
    assert stats.top_tags == []
    assert stats.avg_tags_per_bookmark == 0.0


def test_compute_stats_top_n_limit():
    bms = [
        Bookmark(url=f"https://{i}.com", title=str(i), tags=[f"tag{i}"], description="")
        for i in range(10)
    ]
    stats = compute_stats(bms, top_n=3)
    assert len(stats.top_tags) == 3


def test_format_stats_contains_totals(bookmarks):
    stats = compute_stats(bookmarks)
    text = format_stats(stats)
    assert "Total bookmarks" in text
    assert "4" in text


def test_format_stats_contains_top_tags(bookmarks):
    stats = compute_stats(bookmarks)
    text = format_stats(stats)
    assert "Top tags" in text
    assert "python" in text


def test_format_stats_empty():
    stats = compute_stats([])
    text = format_stats(stats)
    assert "0" in text
    assert "Top tags" not in text
