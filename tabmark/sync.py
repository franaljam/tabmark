"""Sync bookmarks to/from a markdown file on disk."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from tabmark.bookmark import Bookmark, from_dict
from tabmark.markdown_writer import render_markdown, write_markdown
from tabmark.storage import load_bookmarks, save_bookmarks


class SyncResult:
    """Holds the outcome of a sync operation."""

    def __init__(
        self,
        added: int = 0,
        removed: int = 0,
        unchanged: int = 0,
        markdown_path: Optional[Path] = None,
    ) -> None:
        self.added = added
        self.removed = removed
        self.unchanged = unchanged
        self.markdown_path = markdown_path

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SyncResult(added={self.added}, removed={self.removed}, "
            f"unchanged={self.unchanged})"
        )


def sync_to_markdown(store_path: Path, output_path: Path) -> SyncResult:
    """Write current bookmarks from *store_path* to a markdown file at *output_path*.

    Returns a :class:`SyncResult` describing what changed on disk.
    """
    bookmarks: List[Bookmark] = load_bookmarks(store_path)
    existed_before = output_path.exists()
    write_markdown(bookmarks, output_path)
    return SyncResult(
        added=0 if existed_before else len(bookmarks),
        unchanged=len(bookmarks) if existed_before else 0,
        markdown_path=output_path,
    )


def sync_from_markdown(markdown_path: Path, store_path: Path) -> SyncResult:
    """Import bookmarks from a markdown file into the JSON store.

    Lines that do not match the bookmark format are silently skipped.
    Already-present URLs are not duplicated.
    """
    from tabmark.bookmark import from_markdown_line  # local import to avoid cycles

    existing: List[Bookmark] = load_bookmarks(store_path)
    existing_urls = {b.url for b in existing}

    new_bookmarks: List[Bookmark] = []
    if markdown_path.exists():
        for line in markdown_path.read_text(encoding="utf-8").splitlines():
            bm = from_markdown_line(line)
            if bm is not None and bm.url not in existing_urls:
                new_bookmarks.append(bm)
                existing_urls.add(bm.url)

    merged = existing + new_bookmarks
    save_bookmarks(store_path, merged)
    return SyncResult(
        added=len(new_bookmarks),
        unchanged=len(existing),
        markdown_path=markdown_path,
    )
