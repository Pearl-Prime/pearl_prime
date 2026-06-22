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

    # Flagships
    flagships = [
        "compassion-fatigue-audit",
        "overthinking-thought-sorter",
        "financial-anxiety-check-in",
        "courage-decision-map",
        "anxiety-nervous-system-reset",
    ]
    for slug in flagships:
        path = REPO / "brand-wizard-app/public/free" / slug / "index.html"
        text = path.read_text(encoding="utf-8")
        if "phoenix_lead.js" not in text:
            _fail(f"{slug} missing phoenix_lead.js")
        if "data-ghl-webhook" not in text:
            _fail(f"{slug} missing data-ghl-webhook on body")

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

    print("OK: freebie capture smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
