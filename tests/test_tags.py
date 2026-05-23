"""Tests for tabmark.tags module."""

import pytest
from tabmark.bookmark import Bookmark
from tabmark.tags import (
    collect_all_tags,
    tag_frequency,
    rename_tag,
    remove_tag,
)


@pytest.fixture()
def bookmarks():
    return [
        Bookmark(url="https://a.com", title="A", tags=["python", "dev"]),
        Bookmark(url="https://b.com", title="B", tags=["python", "web"]),
        Bookmark(url="https://c.com", title="C", tags=["dev", "ops"]),
        Bookmark(url="https://d.com", title="D", tags=[]),
    ]


def test_collect_all_tags_sorted(bookmarks):
    tags = collect_all_tags(bookmarks)
    assert tags == ["dev", "ops", "python", "web"]


def test_collect_all_tags_empty():
    assert collect_all_tags([]) == []


def test_collect_all_tags_no_tags(bookmarks):
    only_empty = [bookmarks[-1]]
    assert collect_all_tags(only_empty) == []


def test_tag_frequency(bookmarks):
    freq = tag_frequency(bookmarks)
    assert freq["python"] == 2
    assert freq["dev"] == 2
    assert freq["web"] == 1
    assert freq["ops"] == 1


def test_tag_frequency_empty():
    assert tag_frequency([]) == {}


def test_rename_tag_updates_matching(bookmarks):
    result = rename_tag(bookmarks, "python", "py")
    urls_with_py = [bm.url for bm in result if "py" in bm.tags]
    assert set(urls_with_py) == {"https://a.com", "https://b.com"}


def test_rename_tag_removes_old(bookmarks):
    result = rename_tag(bookmarks, "python", "py")
    assert all("python" not in bm.tags for bm in result)


def test_rename_tag_deduplicates():
    bm = Bookmark(url="https://x.com", title="X", tags=["py", "python"])
    result = rename_tag([bm], "python", "py")
    assert result[0].tags == ["py"]


def test_rename_tag_preserves_unrelated(bookmarks):
    result = rename_tag(bookmarks, "python", "py")
    ops_bm = next(bm for bm in result if bm.url == "https://c.com")
    assert ops_bm.tags == ["dev", "ops"]


def test_remove_tag_strips_from_all(bookmarks):
    result = remove_tag(bookmarks, "dev")
    assert all("dev" not in bm.tags for bm in result)


def test_remove_tag_preserves_other_tags(bookmarks):
    result = remove_tag(bookmarks, "dev")
    py_bm = next(bm for bm in result if bm.url == "https://a.com")
    assert "python" in py_bm.tags


def test_remove_tag_no_op_when_absent(bookmarks):
    result = remove_tag(bookmarks, "nonexistent")
    assert [bm.tags for bm in result] == [bm.tags for bm in bookmarks]
