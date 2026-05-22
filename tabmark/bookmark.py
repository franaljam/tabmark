"""Core data model for a browser bookmark."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Bookmark:
    """Represents a single browser bookmark."""

    title: str
    url: str
    folder: str = "Unsorted"
    tags: list[str] = field(default_factory=list)
    added_at: datetime = field(default_factory=datetime.utcnow)
    description: Optional[str] = None

    def to_markdown_line(self) -> str:
        """Render bookmark as a Markdown list item."""
        tag_str = " ".join(f"`{t}`" for t in self.tags) if self.tags else ""
        parts = [f"- [{self.title}]({self.url})"]
        if self.description:
            parts.append(f" — {self.description}")
        if tag_str:
            parts.append(f" {tag_str}")
        return "".join(parts)

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        """Construct a Bookmark from a plain dictionary."""
        added_raw = data.get("added_at")
        added_at = (
            datetime.fromisoformat(added_raw)
            if isinstance(added_raw, str)
            else (added_raw or datetime.utcnow())
        )
        return cls(
            title=data["title"],
            url=data["url"],
            folder=data.get("folder", "Unsorted"),
            tags=data.get("tags", []),
            added_at=added_at,
            description=data.get("description"),
        )

    def to_dict(self) -> dict:
        """Serialise bookmark to a plain dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "folder": self.folder,
            "tags": self.tags,
            "added_at": self.added_at.isoformat(),
            "description": self.description,
        }
