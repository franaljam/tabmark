"""Tests for tabmark.archive."""
from __future__ import annotations

import pytest

from tabmark.archive import (
    ARCHIVE_TAG,
    ArchiveResult,
    archive_bookmark,
    get_archived,
    is_archived,
    partition_bookmarks,
    unarchive_bookmark,
)
from tabmark.bookmark import Bookmark


@pytest.fixture()
def bm() -> Bookmark:
    return Bookmark(url="https://example.com", title="Example", tags=["python"])


@pytest.fixture()
def bm_archived() -> Bookmark:
    return Bookmark(url="https://archived.com", title="Old", tags=["archived", "old"])


def test_is_archived_false_for_active(bm: Bookmark) -> None:
    assert is_archived(bm) is False


def test_is_archived_true_for_archived(bm_archived: Bookmark) -> None:
    assert is_archived(bm_archived) is True


def test_archive_bookmark_adds_tag(bm: Bookmark) -> None:
    result = archive_bookmark(bm)
    assert ARCHIVE_TAG in result.tags


def test_archive_bookmark_preserves_existing_tags(bm: Bookmark) -> None:
    result = archive_bookmark(bm)
    assert "python" in result.tags


def test_archive_bookmark_idempotent(bm_archived: Bookmark) -> None:
    result = archive_bookmark(bm_archived)
    assert result.tags.count(ARCHIVE_TAG) == 1


def test_archive_bookmark_does_not_mutate_original(bm: Bookmark) -> None:
    archive_bookmark(bm)
    assert ARCHIVE_TAG not in bm.tags


def test_unarchive_bookmark_removes_tag(bm_archived: Bookmark) -> None:
    result = unarchive_bookmark(bm_archived)
    assert ARCHIVE_TAG not in result.tags


def test_unarchive_bookmark_preserves_other_tags(bm_archived: Bookmark) -> None:
    result = unarchive_bookmark(bm_archived)
    assert "old" in result.tags


def test_unarchive_does_not_mutate_original(bm_archived: Bookmark) -> None:
    unarchive_bookmark(bm_archived)
    assert ARCHIVE_TAG in bm_archived.tags


def test_partition_bookmarks(bm: Bookmark, bm_archived: Bookmark) -> None:
    active, archived = partition_bookmarks([bm, bm_archived])
    assert bm in active
    assert bm_archived in archived


def test_partition_bookmarks_all_active(bm: Bookmark) -> None:
    active, archived = partition_bookmarks([bm])
    assert len(active) == 1
    assert len(archived) == 0


def test_get_archived_result_counts(bm: Bookmark, bm_archived: Bookmark) -> None:
    result = get_archived([bm, bm_archived])
    assert isinstance(result, ArchiveResult)
    assert len(result.archived) == 1
    assert len(result.unarchived) == 1


def test_get_archived_empty_list() -> None:
    result = get_archived([])
    assert result.archived == []
    assert result.unarchived == []
