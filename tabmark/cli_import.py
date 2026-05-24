"""CLI sub-commands for importing bookmarks from external files."""
from __future__ import annotations

import argparse
from pathlib import Path

from tabmark.import_bookmarks import import_bookmarks
from tabmark.storage import load_bookmarks, save_bookmarks


def cmd_import(args: argparse.Namespace) -> None:
    """Import bookmarks from an external file and merge into the store."""
    source = Path(args.file)
    if not source.exists():
        print(f"Error: file not found: {source}")
        raise SystemExit(1)

    try:
        incoming = import_bookmarks(source, fmt=args.format)
    except ValueError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)

    store = Path(args.store)
    existing = load_bookmarks(store)
    existing_urls = {bm.url for bm in existing}

    added = 0
    skipped = 0
    for bm in incoming:
        if bm.url in existing_urls:
            skipped += 1
        else:
            existing.append(bm)
            existing_urls.add(bm.url)
            added += 1

    save_bookmarks(store, existing)
    print(f"Imported {added} bookmark(s), skipped {skipped} duplicate(s).")


def register_import_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
    store_default: str,
) -> None:
    """Attach the *import* sub-command to *subparsers*."""
    p = subparsers.add_parser(
        "import",
        help="Import bookmarks from an HTML, JSON, or CSV file.",
    )
    p.add_argument("file", help="Path to the file to import.")
    p.add_argument(
        "--format",
        choices=["html", "json", "csv"],
        default=None,
        help="Force a specific format (default: auto-detect from extension).",
    )
    p.add_argument(
        "--store",
        default=store_default,
        help="Path to the bookmark store (default: %(default)s).",
    )
    p.set_defaults(func=cmd_import)
