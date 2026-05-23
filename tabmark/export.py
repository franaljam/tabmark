"""Export bookmarks to various formats (HTML, JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from tabmark.bookmark import Bookmark, to_dict


def export_html(bookmarks: List[Bookmark]) -> str:
    """Render bookmarks as a Netscape-style HTML bookmark file."""
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This is an automatically generated file. -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
    ]
    for bm in bookmarks:
        tags_attr = ""
        if bm.tags:
            tags_attr = f' TAGS="{" ".join(bm.tags)}"'
        desc = bm.description or ""
        lines.append(
            f'    <DT><A HREF="{bm.url}"{tags_attr}>{bm.title}</A>'
        )
        if desc:
            lines.append(f"    <DD>{desc}")
    lines.append("</DL><p>")
    return "\n".join(lines) + "\n"


def export_json(bookmarks: List[Bookmark]) -> str:
    """Serialize bookmarks to a JSON string."""
    data = [to_dict(bm) for bm in bookmarks]
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def export_csv(bookmarks: List[Bookmark]) -> str:
    """Serialize bookmarks to a CSV string."""
    output = io.StringIO()
    fieldnames = ["title", "url", "tags", "description"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for bm in bookmarks:
        writer.writerow(
            {
                "title": bm.title,
                "url": bm.url,
                "tags": ",".join(bm.tags) if bm.tags else "",
                "description": bm.description or "",
            }
        )
    return output.getvalue()


FORMATS = {
    "html": export_html,
    "json": export_json,
    "csv": export_csv,
}


def export_bookmarks(bookmarks: List[Bookmark], fmt: str) -> str:
    """Export bookmarks in the given format. Raises ValueError for unknown formats."""
    if fmt not in FORMATS:
        raise ValueError(f"Unknown export format: {fmt!r}. Choose from {list(FORMATS)}.")
    return FORMATS[fmt](bookmarks)
