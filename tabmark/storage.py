"""JSON-based persistent storage for bookmarks."""

import json
import os
from typing import List

from tabmark.bookmark import Bookmark, from_dict, to_dict

DEFAULT_STORAGE_PATH = os.path.expanduser("~/.tabmark/bookmarks.json")


def load_bookmarks(path: str = DEFAULT_STORAGE_PATH) -> List[Bookmark]:
    """Load bookmarks from a JSON file.

    Returns an empty list if the file does not exist.
    """
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array in {path!r}, got {type(raw).__name__}")

    return [from_dict(item) for item in raw]


def save_bookmarks(bookmarks: List[Bookmark], path: str = DEFAULT_STORAGE_PATH) -> None:
    """Persist bookmarks to a JSON file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data = [to_dict(b) for b in bookmarks]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def add_bookmark(bookmark: Bookmark, path: str = DEFAULT_STORAGE_PATH) -> List[Bookmark]:
    """Append a bookmark to the store, avoiding exact URL duplicates.

    Returns the updated list of bookmarks.
    """
    bookmarks = load_bookmarks(path)

    if any(b.url == bookmark.url for b in bookmarks):
        return bookmarks

    bookmarks.append(bookmark)
    save_bookmarks(bookmarks, path)
    return bookmarks


def remove_bookmark(url: str, path: str = DEFAULT_STORAGE_PATH) -> List[Bookmark]:
    """Remove the bookmark with the given URL from the store.

    Returns the updated list of bookmarks.
    """
    bookmarks = load_bookmarks(path)
    filtered = [b for b in bookmarks if b.url != url]
    save_bookmarks(filtered, path)
    return filtered
