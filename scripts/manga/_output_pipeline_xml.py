"""Shared XML escaping for distribution pipeline outputs."""
from __future__ import annotations

from xml.sax.saxutils import escape


def xml_escape(text: str) -> str:
    return escape(text or "", {'"': "&quot;", "'": "&apos;"})
