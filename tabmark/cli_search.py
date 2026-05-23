"""CLI helpers for the 'search' sub-command."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from tabmark.search import search_bookmarks
from tabmark.storage import load_bookmarks
from tabmark.bookmark import to_markdown_line


def cmd_search(args: argparse.Namespace) -> None:
    """Handle the ``tabmark search`` sub-command."""
    store = Path(args.store)
    bookmarks = load_bookmarks(store)

    tags: List[str] = args.tags if args.tags else []

    results = search_bookmarks(
        bookmarks,
        query=args.query or None,
        tags=tags if tags else None,
        url_contains=args.url or None,
    )

    if not results:
        print("No bookmarks matched your criteria.")
        return

    print(f"Found {len(results)} bookmark(s):\n")
    for bm in results:
        print(to_markdown_line(bm))


def register_search_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Attach the *search* sub-command to an existing subparser group."""
    p = subparsers.add_parser(
        "search",
        help="Search bookmarks by title, tag, or URL fragment.",
    )
    p.add_argument(
        "-q", "--query",
        metavar="TEXT",
        help="Substring to match against title and description.",
    )
    p.add_argument(
        "-t", "--tags",
        nargs="+",
        metavar="TAG",
        help="One or more tags that must all be present.",
    )
    p.add_argument(
        "-u", "--url",
        metavar="FRAGMENT",
        help="Substring to match against the URL.",
    )
    p.set_defaults(func=cmd_search)
