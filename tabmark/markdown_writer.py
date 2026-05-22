"""Renders a collection of Bookmarks to a Markdown file."""

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from tabmark.bookmark import Bookmark

HEADER = "# Bookmarks\n\n_Exported by tabmark — do not edit manually._\n"


def render_markdown(bookmarks: Iterable[Bookmark]) -> str:
    """Group bookmarks by folder and return a full Markdown document."""
    groups: dict[str, list[Bookmark]] = defaultdict(list)
    for bm in bookmarks:
        groups[bm.folder].append(bm)

    lines = [HEADER]
    for folder in sorted(groups):
        lines.append(f"## {folder}\n")
        for bm in sorted(groups[folder], key=lambda b: b.title.lower()):
            lines.append(bm.to_markdown_line())
        lines.append("")  # blank line after section

    return "\n".join(lines).rstrip() + "\n"


def write_markdown(bookmarks: Iterable[Bookmark], output_path: Path) -> None:
    """Write rendered Markdown to *output_path*, creating parent dirs as needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = render_markdown(bookmarks)
    output_path.write_text(content, encoding="utf-8")
