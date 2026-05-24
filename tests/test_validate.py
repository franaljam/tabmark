"""Tests for tabmark.validate."""

import pytest

from tabmark.bookmark import Bookmark
from tabmark.validate import (
    ValidationResult,
    validate_bookmark,
    validate_all,
)


def _bm(**kwargs) -> Bookmark:
    defaults = dict(url="https://example.com", title="Example")
    defaults.update(kwargs)
    return Bookmark(**defaults)


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------

def test_validation_result_is_valid_when_no_errors():
    assert ValidationResult().is_valid is True


def test_validation_result_is_invalid_when_errors_present():
    r = ValidationResult(errors=["something wrong"])
    assert r.is_valid is False


# ---------------------------------------------------------------------------
# validate_bookmark – URL checks
# ---------------------------------------------------------------------------

def test_valid_bookmark_passes():
    result = validate_bookmark(_bm())
    assert result.is_valid


def test_empty_url_fails():
    result = validate_bookmark(_bm(url=""))
    assert not result.is_valid
    assert any("URL" in e for e in result.errors)


def test_non_http_url_fails():
    result = validate_bookmark(_bm(url="ftp://example.com/file"))
    assert not result.is_valid
    assert any("http" in e for e in result.errors)


def test_https_url_passes():
    result = validate_bookmark(_bm(url="https://sub.domain.org/path?q=1#frag"))
    assert result.is_valid


# ---------------------------------------------------------------------------
# validate_bookmark – title checks
# ---------------------------------------------------------------------------

def test_empty_title_fails():
    result = validate_bookmark(_bm(title=""))
    assert not result.is_valid
    assert any("Title" in e for e in result.errors)


def test_title_too_long_fails():
    result = validate_bookmark(_bm(title="x" * 201))
    assert not result.is_valid
    assert any("Title" in e and "200" in e for e in result.errors)


# ---------------------------------------------------------------------------
# validate_bookmark – description checks
# ---------------------------------------------------------------------------

def test_description_too_long_fails():
    result = validate_bookmark(_bm(description="d" * 1001))
    assert not result.is_valid
    assert any("Description" in e for e in result.errors)


def test_description_at_limit_passes():
    result = validate_bookmark(_bm(description="d" * 1000))
    assert result.is_valid


# ---------------------------------------------------------------------------
# validate_bookmark – tag checks
# ---------------------------------------------------------------------------

def test_valid_tags_pass():
    result = validate_bookmark(_bm(tags=["python", "web-dev", "tool_2"]))
    assert result.is_valid


def test_tag_with_space_fails():
    result = validate_bookmark(_bm(tags=["bad tag"]))
    assert not result.is_valid
    assert any("invalid characters" in e for e in result.errors)


def test_tag_too_long_fails():
    result = validate_bookmark(_bm(tags=["t" * 51]))
    assert not result.is_valid
    assert any("50" in e for e in result.errors)


# ---------------------------------------------------------------------------
# validate_all
# ---------------------------------------------------------------------------

def test_validate_all_returns_only_invalid():
    bookmarks = [
        _bm(url="https://good.com", title="Good"),
        _bm(url="", title="No URL"),
        _bm(url="https://also-good.io", title="Also Good"),
        _bm(url="not-a-url", title="Bad URL"),
    ]
    invalid = validate_all(bookmarks)
    assert len(invalid) == 2
    assert "<empty-url>" in invalid
    assert "not-a-url" in invalid


def test_validate_all_empty_list():
    assert validate_all([]) == {}
