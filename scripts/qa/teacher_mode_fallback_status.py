#!/usr/bin/env python3
"""Smoke status for teacher-mode strict/fallback surfaces (I003)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts/qa/archived_session_audit_gt30d_20260722/teacher_mode_fallback_status.json"

CANDIDATES = [
    "teachers/",
    "scripts/teacher_pages/render.py",
    "docs/agent_prompt_packs/20260720_teacher_onboarding_lang_and_hybrid_brands",
]


def main() -> int:
    rows = []
    for rel in CANDIDATES:
        p = REPO / rel
        rows.append({"path": rel, "exists": p.exists()})
    present = [r["path"] for r in rows if r["exists"]]
    missing = [r["path"] for r in rows if not r["exists"]]
    status = "PARTIAL" if present else "ABSENT"
    report = {
        "keeper": "I003",
        "status": status,
        "present": present,
        "missing": missing,
        "next": "Confirm strict-mode fail paths for missing STORY; wire fallback only where doctrine allows",
        "acceptance_layer": "CODE-WIRED status only — not full teacher-mode plan completion",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
