"""Core Bookmark dataclass and serialisation helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Bookmark:
    url: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.tags = sorted(set(self.tags))


# Regex that matches lines written by to_markdown_line
_MD_PATTERN = re.compile(
    r"^- \[(?P<title>[^\]]+)\]\((?P<url>[^)]+)\)"
    r"(?:\s+<!--\s*tags:\s*(?P<tags>[^-]+?)\s*-->)?"
    r"(?:\s+<!--\s*desc:\s*(?P<desc>.+?)\s*-->)?\s*$"
)


def to_markdown_line(bm: Bookmark) -> str:
    """Render a bookmark as a single markdown list item."""
    parts = [f"- [{bm.title}]({bm.url})"]
    if bm.tags:
        parts.append(f"<!-- tags: {', '.join(bm.tags)} -->")
    if bm.description:
        parts.append(f"<!-- desc: {bm.description} -->")
    return " ".join(parts)


def from_markdown_line(line: str) -> Optional[Bookmark]:
    """Parse a markdown list item back into a :class:`Bookmark`.

    Returns *None* if the line does not match the expected format.
    """
    m = _MD_PATTERN.match(line.strip())
    if not m:
        return None
    tags_raw = m.group("tags") or ""
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    return Bookmark(
        url=m.group("url"),
        title=m.group("title"),
        description=(m.group("desc") or "").strip(),
        tags=tags,
    )


def from_dict(data: Dict[str, Any]) -> Bookmark:
    return Bookmark(
        url=data["url"],
        title=data["title"],
        description=data.get("description", ""),
        tags=data.get("tags", []),
    )


def to_dict(bm: Bookmark) -> Dict[str, Any]:
    return {
        "url": bm.url,
        "title": bm.title,
        "description": bm.description,
        "tags": bm.tags,
    }
