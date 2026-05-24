"""CLI sub-commands for markdown sync."""

from __future__ import annotations

import argparse
from pathlib import Path

from tabmark.sync import sync_from_markdown, sync_to_markdown


def cmd_sync_export(args: argparse.Namespace) -> None:
    """Push bookmarks from the JSON store to a markdown file."""
    result = sync_to_markdown(
        store_path=Path(args.store),
        output_path=Path(args.output),
    )
    total = result.added + result.unchanged
    print(
        f"Synced {total} bookmark(s) to '{args.output}' "
        f"({result.added} new, {result.unchanged} unchanged)."
    )


def cmd_sync_import(args: argparse.Namespace) -> None:
    """Pull bookmarks from a markdown file into the JSON store."""
    result = sync_from_markdown(
        markdown_path=Path(args.input),
        store_path=Path(args.store),
    )
    print(
        f"Imported {result.added} new bookmark(s) from '{args.input}' "
        f"({result.unchanged} already present)."
    )


def register_sync_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
    default_store: str,
) -> None:
    """Attach *sync-export* and *sync-import* sub-commands to *subparsers*."""
    # sync-export
    p_export = subparsers.add_parser(
        "sync-export",
        help="write bookmarks to a markdown file",
    )
    p_export.add_argument(
        "-o",
        "--output",
        default="bookmarks.md",
        help="destination markdown file (default: bookmarks.md)",
    )
    p_export.add_argument("--store", default=default_store, help=argparse.SUPPRESS)
    p_export.set_defaults(func=cmd_sync_export)

    # sync-import
    p_import = subparsers.add_parser(
        "sync-import",
        help="read bookmarks from a markdown file into the store",
    )
    p_import.add_argument(
        "input",
        help="source markdown file to import from",
    )
    p_import.add_argument("--store", default=default_store, help=argparse.SUPPRESS)
    p_import.set_defaults(func=cmd_sync_import)
