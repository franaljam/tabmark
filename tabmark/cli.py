"""Minimal CLI for tabmark bookmark management."""

import argparse
import sys

from tabmark.bookmark import Bookmark
from tabmark.markdown_writer import render_markdown, write_markdown
from tabmark.storage import (
    DEFAULT_STORAGE_PATH,
    add_bookmark,
    load_bookmarks,
    remove_bookmark,
)


def cmd_add(args: argparse.Namespace) -> int:
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    bm = Bookmark(
        url=args.url,
        title=args.title,
        tags=tags,
        description=args.description or "",
    )
    bookmarks = add_bookmark(bm, args.store)
    print(f"Saved. Total bookmarks: {len(bookmarks)}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    bookmarks = remove_bookmark(args.url, args.store)
    print(f"Removed. Total bookmarks: {len(bookmarks)}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    bookmarks = load_bookmarks(args.store)
    if not bookmarks:
        print("No bookmarks stored yet.")
        return 0
    for bm in bookmarks:
        tag_str = f"  [{', '.join(bm.tags)}]" if bm.tags else ""
        print(f"  {bm.title}{tag_str}\n    {bm.url}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    bookmarks = load_bookmarks(args.store)
    md = render_markdown(bookmarks)
    write_markdown(md, args.output)
    print(f"Exported {len(bookmarks)} bookmark(s) to {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tabmark",
        description="Lightweight bookmark manager that syncs to Markdown.",
    )
    parser.add_argument("--store", default=DEFAULT_STORAGE_PATH, metavar="PATH",
                        help="Path to the JSON bookmark store.")

    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new bookmark.")
    p_add.add_argument("url", help="Bookmark URL.")
    p_add.add_argument("title", help="Human-readable title.")
    p_add.add_argument("--tags", help="Comma-separated list of tags.")
    p_add.add_argument("--description", help="Optional description.")
    p_add.set_defaults(func=cmd_add)

    # remove
    p_rm = sub.add_parser("remove", help="Remove a bookmark by URL.")
    p_rm.add_argument("url", help="URL of the bookmark to remove.")
    p_rm.set_defaults(func=cmd_remove)

    # list
    p_ls = sub.add_parser("list", help="List all stored bookmarks.")
    p_ls.set_defaults(func=cmd_list)

    # export
    p_ex = sub.add_parser("export", help="Export bookmarks to a Markdown file.")
    p_ex.add_argument("output", help="Destination Markdown file path.")
    p_ex.set_defaults(func=cmd_export)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
