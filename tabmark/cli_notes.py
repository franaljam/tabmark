"""CLI sub-commands for managing bookmark notes."""
from __future__ import annotations

import argparse
import sys

from tabmark.notes import bookmarks_with_notes, clear_note, get_note, set_note
from tabmark.storage import load_bookmarks, save_bookmarks


def cmd_set_note(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    target = next((b for b in bookmarks if b.url == args.url), None)
    if target is None:
        print(f"Error: bookmark not found: {args.url}", file=sys.stderr)
        sys.exit(1)
    result = set_note(target, args.note)
    save_bookmarks(args.store, bookmarks)
    print(f"Note {result.action} on {result.url}")


def cmd_clear_note(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    target = next((b for b in bookmarks if b.url == args.url), None)
    if target is None:
        print(f"Error: bookmark not found: {args.url}", file=sys.stderr)
        sys.exit(1)
    result = clear_note(target)
    save_bookmarks(args.store, bookmarks)
    print(f"Note cleared from {result.url}")


def cmd_list_notes(args: argparse.Namespace) -> None:
    bookmarks = load_bookmarks(args.store)
    noted = bookmarks_with_notes(bookmarks)
    if not noted:
        print("No bookmarks with notes.")
        return
    for b in noted:
        note = get_note(b)
        print(f"{b.url}  [{note}]")


def register_notes_parser(subparsers: argparse._SubParsersAction, parent: argparse.ArgumentParser) -> None:
    notes_p = subparsers.add_parser("notes", help="Manage bookmark notes")
    notes_sub = notes_p.add_subparsers(dest="notes_cmd", required=True)

    p_set = notes_sub.add_parser("set", parents=[parent], help="Attach a note to a bookmark")
    p_set.add_argument("url", help="Bookmark URL")
    p_set.add_argument("note", help="Note text")
    p_set.set_defaults(func=cmd_set_note)

    p_clear = notes_sub.add_parser("clear", parents=[parent], help="Remove the note from a bookmark")
    p_clear.add_argument("url", help="Bookmark URL")
    p_clear.set_defaults(func=cmd_clear_note)

    p_list = notes_sub.add_parser("list", parents=[parent], help="List bookmarks that have notes")
    p_list.set_defaults(func=cmd_list_notes)
