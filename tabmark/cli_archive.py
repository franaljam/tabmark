"""CLI sub-commands for archiving and unarchiving bookmarks."""
from __future__ import annotations

import argparse
import sys

from tabmark.archive import (
    archive_bookmark,
    get_archived,
    is_archived,
    unarchive_bookmark,
)
from tabmark.storage import load_bookmarks, save_bookmarks


def cmd_archive(args: argparse.Namespace) -> None:
    """Mark a bookmark as archived by URL."""
    bookmarks = load_bookmarks(args.store)
    updated = []
    found = False
    for bm in bookmarks:
        if bm.url == args.url:
            updated.append(archive_bookmark(bm))
            found = True
        else:
            updated.append(bm)
    if not found:
        print(f"No bookmark found with URL: {args.url}", file=sys.stderr)
        sys.exit(1)
    save_bookmarks(args.store, updated)
    print(f"Archived: {args.url}")


def cmd_unarchive(args: argparse.Namespace) -> None:
    """Remove the archived tag from a bookmark by URL."""
    bookmarks = load_bookmarks(args.store)
    updated = []
    found = False
    for bm in bookmarks:
        if bm.url == args.url:
            if not is_archived(bm):
                print(f"Bookmark is not archived: {args.url}", file=sys.stderr)
                sys.exit(1)
            updated.append(unarchive_bookmark(bm))
            found = True
        else:
            updated.append(bm)
    if not found:
        print(f"No bookmark found with URL: {args.url}", file=sys.stderr)
        sys.exit(1)
    save_bookmarks(args.store, updated)
    print(f"Unarchived: {args.url}")


def cmd_list_archived(args: argparse.Namespace) -> None:
    """List all archived bookmarks."""
    bookmarks = load_bookmarks(args.store)
    result = get_archived(bookmarks)
    if not result.archived:
        print("No archived bookmarks.")
        return
    for bm in result.archived:
        print(f"  [{bm.title}]({bm.url})")


def register_archive_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_arch = subparsers.add_parser("archive", help="Archive a bookmark")
    p_arch.add_argument("url", help="URL of the bookmark to archive")
    p_arch.set_defaults(func=cmd_archive)

    p_unarch = subparsers.add_parser("unarchive", help="Unarchive a bookmark")
    p_unarch.add_argument("url", help="URL of the bookmark to unarchive")
    p_unarch.set_defaults(func=cmd_unarchive)

    p_list = subparsers.add_parser("list-archived", help="List archived bookmarks")
    p_list.set_defaults(func=cmd_list_archived)
