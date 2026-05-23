"""CLI sub-commands for bookmark deduplication."""

from __future__ import annotations

import argparse

from tabmark.dedupe import deduplicate, find_duplicates
from tabmark.storage import load_bookmarks, save_bookmarks


def cmd_dedupe(args: argparse.Namespace) -> None:
    """Find and optionally remove duplicate bookmarks."""
    bookmarks = load_bookmarks(args.store)

    if args.dry_run:
        groups = find_duplicates(bookmarks)
        if not groups:
            print("No duplicates found.")
            return
        print(f"Found {len(groups)} duplicate group(s):")
        for group in groups:
            print(f"  URL: {group[0].url}")
            for bm in group:
                print(f"    - [{bm.title}]")
        return

    cleaned, removed = deduplicate(bookmarks, keep=args.keep)
    if removed == 0:
        print("No duplicates found.")
        return

    save_bookmarks(args.store, cleaned)
    print(f"Removed {removed} duplicate(s). {len(cleaned)} bookmark(s) remaining.")


def register_dedupe_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the 'dedupe' sub-command to *subparsers*."""
    p = subparsers.add_parser(
        "dedupe",
        help="find and remove duplicate bookmarks",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="report duplicates without modifying the store",
    )
    p.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="which occurrence to keep (default: first)",
    )
    p.set_defaults(func=cmd_dedupe)
