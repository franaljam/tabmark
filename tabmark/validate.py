"""Bookmark validation utilities for tabmark."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from tabmark.bookmark import Bookmark

_URL_RE = re.compile(
    r"^https?://"
    r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}"
    r"(?::\d{1,5})?"
    r"(?:[/?#]\S*)?"
    r"$"
)

_MAX_TITLE_LEN = 200
_MAX_DESC_LEN = 1000
_MAX_TAG_LEN = 50
_TAG_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


@dataclass
class ValidationResult:
    """Holds errors found during bookmark validation."""

    errors: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def __repr__(self) -> str:  # pragma: no cover
        status = "valid" if self.is_valid else f"{len(self.errors)} error(s)"
        return f"ValidationResult({status})"


def validate_bookmark(bm: Bookmark) -> ValidationResult:
    """Validate a single bookmark and return a ValidationResult."""
    result = ValidationResult()

    # URL
    if not bm.url or not bm.url.strip():
        result.errors.append("URL must not be empty.")
    elif not _URL_RE.match(bm.url.strip()):
        result.errors.append(f"URL is not a valid http/https URL: {bm.url!r}")

    # Title
    if not bm.title or not bm.title.strip():
        result.errors.append("Title must not be empty.")
    elif len(bm.title) > _MAX_TITLE_LEN:
        result.errors.append(
            f"Title exceeds maximum length of {_MAX_TITLE_LEN} characters."
        )

    # Description
    if bm.description and len(bm.description) > _MAX_DESC_LEN:
        result.errors.append(
            f"Description exceeds maximum length of {_MAX_DESC_LEN} characters."
        )

    # Tags
    for tag in bm.tags:
        if len(tag) > _MAX_TAG_LEN:
            result.errors.append(
                f"Tag {tag!r} exceeds maximum length of {_MAX_TAG_LEN} characters."
            )
        elif not _TAG_RE.match(tag):
            result.errors.append(
                f"Tag {tag!r} contains invalid characters (allowed: A-Z, a-z, 0-9, _, -)."
            )

    return result


def validate_all(bookmarks: List[Bookmark]) -> dict[str, ValidationResult]:
    """Validate a list of bookmarks. Returns a mapping of URL -> ValidationResult
    for any bookmark that has at least one error."""
    invalid: dict[str, ValidationResult] = {}
    for bm in bookmarks:
        result = validate_bookmark(bm)
        if not result.is_valid:
            key = bm.url or "<empty-url>"
            invalid[key] = result
    return invalid
