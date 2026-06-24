#!/usr/bin/env python3
"""Automated acceptance smoke for freebie single-capture build."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def _load_funnel_slugs() -> list[str]:
    import yaml

    cfg_path = REPO / "config/freebies/ghl_funnel_capture.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    slugs: list[str] = []
    for entry in cfg.get("funnel_pages") or []:
        if isinstance(entry, dict) and entry.get("funnel_slug"):
            slugs.append(str(entry["funnel_slug"]))
    if not slugs:
        slugs = [
            "compassion-fatigue-audit",
            "overthinking-thought-sorter",
            "financial-anxiety-check-in",
            "courage-decision-map",
            "anxiety-nervous-system-reset",
        ]
    return slugs


def _assert_funnel_wiring(slug: str) -> None:
    path = REPO / "brand-wizard-app/public/free" / slug / "index.html"
    if not path.is_file():
        _fail(f"missing landing page: {slug}")
    text = path.read_text(encoding="utf-8")
    if "phoenix_lead.js" not in text:
        _fail(f"{slug} missing phoenix_lead.js")
    if "data-ghl-webhook" not in text:
        _fail(f"{slug} missing data-ghl-webhook on body")
    wired = (
        "PhoenixLead.captureLead" in text
        or "PhoenixFunnel.bindEmailBeforeResult" in text
        or "submitEmailGate" in text
    )
    if not wired:
        _fail(f"{slug} missing captureLead / bindEmailBeforeResult wiring")


def main() -> int:
    # JS assets
    for rel in (
        "brand-wizard-app/public/free/js/phoenix_lead.js",
        "brand-wizard-app/public/free/js/phoenix_funnel.js",
        "public/free/js/phoenix_lead.js",
    ):
        if not (REPO / rel).exists():
            _fail(f"missing {rel}")

    # Breathwork bypass
    lps = list((REPO / "public/breathwork").glob("lp-*.html"))
    if len(lps) != 27:
        _fail(f"expected 27 breathwork LPs, found {len(lps)}")
    missing_lp = [p.name for p in lps if "phoenix_lead" not in p.read_text(encoding="utf-8")]
    if missing_lp:
        _fail(f"breathwork LPs missing phoenix_lead: {missing_lp[:3]}")

    # Somatic footer
    apps = list((REPO / "somatic_exercise_freebee_apps").glob("*.html"))
    if len(apps) != 42:
        _fail(f"expected 42 somatic apps, found {len(apps)}")
    missing_app = [p.name for p in apps if "phoenix-lead-footer" not in p.read_text(encoding="utf-8")]
    if missing_app:
        _fail(f"somatic apps missing footer: {missing_app[:3]}")

    # All 15 funnel landings — GHL wiring
    slugs = _load_funnel_slugs()
    if len(slugs) != 15:
        _fail(f"expected 15 funnel_pages in ghl_funnel_capture.yaml, found {len(slugs)}")
    for slug in slugs:
        _assert_funnel_wiring(slug)

    # E2 unlock URLs in templates (top 5)
    for topic in ("anxiety", "compassion_fatigue", "overthinking", "financial_anxiety", "courage"):
        tpl = REPO / "config/funnel/email_templates" / f"{topic}_nurture_5.yaml"
        text = tpl.read_text(encoding="utf-8")
        if "unlock=1&cid=" not in text:
            _fail(f"{topic} nurture E2 missing unlock cid URL")
        if "post_purchase_workbook" not in text:
            _fail(f"{topic} missing post_purchase_workbook slot")

    # Planner tests + PDF ratio
    for cmd in (
        [sys.executable, "-m", "pytest", "tests/test_freebie_planner_workbook.py", "-q"],
        [sys.executable, str(REPO / "scripts/freebies/validate_nurture_pdf_ratio.py")],
    ):
        r = subprocess.run(cmd, cwd=REPO, env={**dict(os.environ), "PYTHONPATH": "."})
        if r.returncode != 0:
            _fail(f"command failed: {' '.join(cmd)}")

    print(f"OK: freebie capture smoke passed ({len(slugs)}/15 funnel landings GHL-wired)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
