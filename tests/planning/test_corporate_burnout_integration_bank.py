from __future__ import annotations

from collections import Counter
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[2]
BANK = REPO / "atoms/corporate_managers/burnout/INTEGRATION/CANONICAL.txt"
HEADER_RE = re.compile(r"(?m)^## INTEGRATION v(\d+)\s*$")
PLACEHOLDER = "[Integration content for corporate_managers × burnout]"


def _blocks() -> list[tuple[str, str]]:
    text = BANK.read_text(encoding="utf-8")
    headers = list(HEADER_RE.finditer(text))
    out = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        out.append((header.group(1), text[header.end():end]))
    return out


def _prose_words(payload: str) -> int:
    pieces = re.split(r"(?m)^---\s*$", payload)
    # Last non-empty segment is prose for both canonical and legacy shapes.
    segments = [piece.strip() for piece in pieces if piece.strip()]
    prose = segments[-1] if segments else ""
    prose_lines = [
        line for line in prose.splitlines()
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_ ]*:\s*", line.strip())
    ]
    return len(" ".join(prose_lines).split())


def test_corporate_burnout_integration_bank_has_no_duplicate_ids():
    versions = [version for version, _ in _blocks()]
    duplicates = [version for version, count in Counter(versions).items() if count > 1]
    assert not duplicates


def test_corporate_burnout_integration_has_no_placeholder_stubs():
    text = BANK.read_text(encoding="utf-8")
    assert PLACEHOLDER not in text
    assert all(_prose_words(payload) >= 40 for _, payload in _blocks())


def test_real_v26_remains_usable():
    payload = next(payload for version, payload in _blocks() if version == "26")
    assert _prose_words(payload) > 100
    assert "One 1:1 a week" in payload
