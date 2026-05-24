"""CLI sub-commands for pinning and unpinning bookmarks."""
from __future__ import annotations

import argparse
import sys

from tabmark.pin import get_pinned, pin_bookmark, unpin_bookmark
from tabmark.storage import load_bookmarks, save_bookmarks


def cmd_pin(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    result = pin_bookmark(bookmarks, args.url)
    if result.action == "not_found":
        print(f"Error: no bookmark found for {args.url}", file=sys.stderr)
        sys.exit(1)
    elif result.action == "already_pinned":
        print(f"Already pinned: {args.url}")
        return
    save_bookmarks(args.store, bookmarks)
    print(f"Pinned: {args.url}")


def cmd_unpin(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    result = unpin_bookmark(bookmarks, args.url)
    if result.action == "not_found":
        print(f"Error: no bookmark found for {args.url}", file=sys.stderr)
        sys.exit(1)
    elif result.action == "not_pinned":
        print(f"Not pinned: {args.url}")
        return
    save_bookmarks(args.store, bookmarks)
    print(f"Unpinned: {args.url}")


def cmd_list_pinned(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    pinned = get_pinned(bookmarks)
    if not pinned:
        print("No pinned bookmarks.")
        return
    for bm in pinned:
        tags = ", ".join(bm.tags or [])
        print(f"  {bm.title}  <{bm.url}>" + (f"  [{tags}]" if tags else ""))


def register_pin_parser(subparsers: argparse._SubParsersAction, store_default: str) -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--store", default=store_default)

    pin_p = subparsers.add_parser("pin", parents=[common], help="Pin a bookmark")
    pin_p.add_argument("url", help="URL of the bookmark to pin")
    pin_p.set_defaults(func=cmd_pin)

    unpin_p = subparsers.add_parser("unpin", parents=[common], help="Unpin a bookmark")
    unpin_p.add_argument("url", help="URL of the bookmark to unpin")
    unpin_p.set_defaults(func=cmd_unpin)

    lp = subparsers.add_parser("list-pinned", parents=[common], help="List pinned bookmarks")
    lp.set_defaults(func=cmd_list_pinned)
