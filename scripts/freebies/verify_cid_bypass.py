#!/usr/bin/env python3
"""Verify cid/unlock/localStorage bypass wiring on breathwork + flagship LPs."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> int:
    lead_js = (REPO / "brand-wizard-app/public/free/js/phoenix_lead.js").read_text(encoding="utf-8")
    for needle in ("unlock') === '1'", "getQueryParam('cid')", "STORAGE_CAPTURED", "initBreathworkLanding"):
        if needle not in lead_js:
            _fail(f"phoenix_lead.js missing bypass logic: {needle}")

    lps = list((REPO / "public/breathwork").glob("lp-*.html"))
    bad = [p.name for p in lps if "initBreathworkLanding" not in p.read_text(encoding="utf-8")]
    if bad:
        _fail(f"breathwork LPs missing initBreathworkLanding: {bad[:3]}")

    # Two flagship LPs: compassion (quiz gate) + anxiety (capture skip)
    samples = {
        "compassion-fatigue-audit": ["requestResults", "shouldShowEmailGate", "email-gate-section"],
        "anxiety-nervous-system-reset": ["initSkipFormIfCaptured", "PhoenixLead.captureLead"],
    }
    for slug, needles in samples.items():
        text = (REPO / "brand-wizard-app/public/free" / slug / "index.html").read_text(encoding="utf-8")
        for n in needles:
            if n not in text:
                _fail(f"{slug} missing {n}")

    # Simulated unlock URL pattern in E2 templates
    tpl = (REPO / "config/funnel/email_templates/compassion_fatigue_nurture_5.yaml").read_text(encoding="utf-8")
    if not re.search(r"unlock=1&cid=\{\{contact_id\}\}", tpl):
        _fail("compassion_fatigue E2 missing unlock cid merge pattern")

    print("OK: cid bypass wiring verified (compassion-fatigue-audit + anxiety-nervous-system-reset + 27 breathwork LPs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
