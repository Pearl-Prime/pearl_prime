"""Assert all funnel_pages in ghl_funnel_capture.yaml are wired for GHL capture."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
CFG = REPO / "config/freebies/ghl_funnel_capture.yaml"


def _funnel_pages() -> list[dict]:
    cfg = yaml.safe_load(CFG.read_text(encoding="utf-8")) or {}
    pages = cfg.get("funnel_pages") or []
    return [p for p in pages if isinstance(p, dict)]


@pytest.mark.parametrize("entry", _funnel_pages(), ids=lambda e: e.get("funnel_slug", "?"))
def test_ghl_funnel_page_wired(entry: dict) -> None:
    rel = entry.get("path")
    assert rel, "funnel_pages entry missing path"
    path = REPO / rel
    assert path.is_file(), f"missing file: {rel}"
    text = path.read_text(encoding="utf-8")
    assert "phoenix_lead.js" in text
    assert "data-ghl-webhook" in text
    assert (
        "PhoenixLead.captureLead" in text
        or "PhoenixFunnel.bindEmailBeforeResult" in text
        or "submitEmailGate" in text
    )


def test_funnel_pages_count() -> None:
    assert len(_funnel_pages()) == 15
