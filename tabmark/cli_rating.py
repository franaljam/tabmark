"""CLI sub-commands for bookmark ratings."""
from __future__ import annotations

import argparse
import sys

from tabmark.storage import load_bookmarks, save_bookmarks
from tabmark.rating import (
    clear_rating,
    get_bookmarks_by_rating,
    get_rating,
    get_top_rated,
    set_rating,
)


def cmd_rate(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    match = next((b for b in bookmarks if b.url == args.url), None)
    if match is None:
        print(f"Error: bookmark not found: {args.url}", file=sys.stderr)
        sys.exit(1)
    result = set_rating(match, args.stars)
    save_bookmarks(args.store, bookmarks)
    action = "updated" if result.previous is not None else "set"
    print(f"Rating {action} to {result.current} star(s) for {args.url}")


def cmd_unrate(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    match = next((b for b in bookmarks if b.url == args.url), None)
    if match is None:
        print(f"Error: bookmark not found: {args.url}", file=sys.stderr)
        sys.exit(1)
    result = clear_rating(match)
    save_bookmarks(args.store, bookmarks)
    if result.changed:
        print(f"Rating removed from {args.url}")
    else:
        print(f"No rating was set for {args.url}")


def cmd_list_rated(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    if args.min:
        results = get_top_rated(bookmarks, min_rating=args.min)
    elif args.stars:
        results = get_bookmarks_by_rating(bookmarks, args.stars)
    else:
        results = [b for b in bookmarks if get_rating(b) is not None]
        results.sort(key=lambda b: get_rating(b) or 0, reverse=True)  # type: ignore[return-value]

    if not results:
        print("No rated bookmarks found.")
        return
    for b in results:
        stars = get_rating(b)
        print(f"[{'★' * (stars or 0)}{'☆' * (5 - (stars or 0))}] {b.url}  {b.title}")


def register_rating_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_rate = subparsers.add_parser("rate", help="Set a star rating (1-5) for a bookmark")
    p_rate.add_argument("url")
    p_rate.add_argument("stars", type=int, choices=range(1, 6), metavar="STARS")
    p_rate.set_defaults(func=cmd_rate)

    p_unrate = subparsers.add_parser("unrate", help="Remove the rating from a bookmark")
    p_unrate.add_argument("url")
    p_unrate.set_defaults(func=cmd_unrate)

    p_list = subparsers.add_parser("list-rated", help="List rated bookmarks")
    p_list.add_argument("--stars", type=int, choices=range(1, 6), metavar="STARS",
                        help="Filter by exact star count")
    p_list.add_argument("--min", type=int, choices=range(1, 6), metavar="MIN",
                        help="Show bookmarks with at least MIN stars")
    p_list.set_defaults(func=cmd_list_rated)
