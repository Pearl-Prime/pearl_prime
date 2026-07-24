"""Banned DashScope endpoint patterns must be absent from video_bank package."""

from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parents[2] / "scripts" / "manga" / "video_bank"

# Construct tokens at runtime so this test file itself is not a false positive
# against a naive repo-wide grep of the same literals.
BANNED = ("X-" + "DashScope-Async", "/" + "services/aigc/")


def test_video_bank_has_zero_dashscope_endpoint_patterns() -> None:
    hits: list[str] = []
    for path in sorted(PKG.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in BANNED:
            if token in text:
                hits.append(f"{path.relative_to(PKG.parent.parent.parent)}:{token}")
    assert hits == [], f"banned patterns in video_bank: {hits}"
