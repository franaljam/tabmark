"""CLI sub-commands for exporting bookmarks to HTML, JSON, or CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tabmark.export import FORMATS, export_bookmarks
from tabmark.storage import load_bookmarks


def cmd_export_fmt(args: argparse.Namespace) -> None:
    """Handle the 'export-fmt' sub-command."""
    store = Path(args.store)
    bookmarks = load_bookmarks(store)

    if not bookmarks:
        print("No bookmarks to export.", file=sys.stderr)
        return

    try:
        output = export_bookmarks(bookmarks, args.format)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Exported {len(bookmarks)} bookmark(s) to {out_path}")
    else:
        sys.stdout.write(output)


def register_export_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
    store_default: str,
) -> None:
    """Register the 'export-fmt' sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "export-fmt",
        help="Export bookmarks to HTML, JSON, or CSV",
    )
    p.add_argument(
        "--store",
        default=store_default,
        help="Path to the bookmark store JSON file",
    )
    p.add_argument(
        "-f",
        "--format",
        choices=list(FORMATS),
        default="json",
        help="Output format (default: json)",
    )
    p.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write output to this file instead of stdout",
    )
    p.set_defaults(func=cmd_export_fmt)
