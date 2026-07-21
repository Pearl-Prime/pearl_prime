#!/usr/bin/env python3
"""Smoke status for books-first engine-keyed STORY seeding + 4-cell rebuild (I045).

Does not author atoms. Reports whether slate/proof surfaces exist and what's missing.
Smoke→pilot measurement only (gt30d D03).

Usage:
  PYTHONPATH=. python3 scripts/qa/books_first_story_seed_status.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts/qa/archived_session_audit_gt30d_20260722/books_first_story_seed_status.json"

CANDIDATES = [
    "artifacts/analysis/books_first_thin_persona_repair_slate_20260714/SLATE.md",
    "artifacts/analysis/books_first_thin_persona_repair_slate_20260714/candidate_cells.tsv",
    "artifacts/qa/engine_keyed_story_seed_batch_a_20260714",
    "docs/agent_prompt_packs/20260714_books_first_epub_wave/03_Pearl_Writer_engine_keyed_story_seed_batch_a.md",
    "old_chat_specs/Untitled 366.txt",
]


def main() -> int:
    rows = []
    for rel in CANDIDATES:
        p = REPO / rel
        rows.append(
            {
                "path": rel,
                "exists": p.exists(),
                "is_dir": p.is_dir() if p.exists() else False,
                "bytes": (p.stat().st_size if p.is_file() else None),
            }
        )
    missing = [r["path"] for r in rows if not r["exists"]]
    present = [r["path"] for r in rows if r["exists"]]
    # Pilot readiness: slate + pack prompt present; seed proof dir may still be missing
    status = "PILOT_READY" if (
        (REPO / CANDIDATES[0]).exists() and (REPO / CANDIDATES[3]).exists()
    ) else "BLOCKED_MISSING_SLATE"
    if status == "PILOT_READY" and not (REPO / CANDIDATES[2]).exists():
        status = "SMOKE_OK_SEED_PROOF_ABSENT"
    report = {
        "keeper": "I045",
        "status": status,
        "present": present,
        "missing": missing,
        "next": (
            "Pearl_Writer: run engine-keyed STORY seed batch from slate; "
            "then 4-cell rebuild proof under artifacts/qa/"
        ),
        "acceptance_layer": "CODE-WIRED status tool only — not EXECUTED-REAL seeding",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status != "BLOCKED_MISSING_SLATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
