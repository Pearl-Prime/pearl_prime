#!/usr/bin/env python3
"""
CDIS §10 — Book duration (audiobook hours / ebook pages) from persona + SOMATIC_BOOK_BLUEPRINT.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration._config import config_snapshot_hash, load_yaml, should_skip_output, write_atomically  # noqa: E402

# §10.2 persona targets (hours, chapter min)
PERSONA_AUDIO = {
    "gen_alpha_students": (4.0, 12),
    "gen_z_professionals": (4.5, 12),
    "healthcare_rns": (4.0, 12),
    "first_responders": (4.0, 12),
    "working_parents": (5.5, 17),
    "millennial_women_professionals": (6.0, 22),
    "gen_x_sandwich": (6.5, 22),
    "corporate_managers": (6.0, 22),
    "tech_finance_burnout": (6.0, 22),
    "entrepreneurs": (6.0, 20),
}


def plan_book(
    persona: str,
    book_format: str,
    intent: str,
) -> dict:
    blueprint = load_yaml(REPO_ROOT / "docs" / "assembly" / "SOMATIC_BOOK_BLUEPRINT.yaml")
    br = blueprint.get("book_rules") or {}
    ch = blueprint.get("chapter_structure") or {}
    ex = (blueprint.get("exercise_policy") or {}).get("phase_3") or {}

    min_ch = int(br.get("min_story_atoms") or 8)
    max_ch = int(br.get("max_story_atoms") or 14)
    slots = len([k for k in ch if k.startswith("slot_")])

    ahours, ch_len = PERSONA_AUDIO.get(persona, (6.0, 22))
    if intent == "discovery":
        ahours = min(ahours, 3.0)

    eb_pages = {"lead_magnet": (25, 40), "short_read": (80, 100), "standard": (190, 220), "comprehensive": (300, 360)}
    use = "standard" if intent == "therapeutic" else "short_read" if intent == "discovery" else "standard"
    plo, phi = eb_pages[use]

    doc = {
        "persona": persona,
        "format": book_format,
        "intent": intent,
        "blueprint_id": blueprint.get("blueprint_id"),
        "chapters_min": min_ch,
        "chapters_max": max_ch,
        "slots_per_chapter": slots or 10,
        "exercise_max_seconds_phase_3": ex.get("max_duration_seconds", 600),
        "audiobook_target_hours": ahours if book_format == "audiobook" else None,
        "audiobook_chapter_target_minutes": ch_len if book_format == "audiobook" else None,
        "ebook_target_pages_min": plo if book_format == "ebook" else None,
        "ebook_target_pages_max": phi if book_format == "ebook" else None,
        "config_hash": config_snapshot_hash(),
    }
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description="CDIS book duration planner")
    ap.add_argument("--brand", default="stillness_press")
    ap.add_argument("--persona", default="millennial_women_professionals")
    ap.add_argument("--format", dest="book_format", choices=["audiobook", "ebook"], default="audiobook")
    ap.add_argument("--intent", default="therapeutic")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    outp = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(outp, ["chapters_min", "config_hash"], args.force, h):
        print(f"Skip: {outp}")
        return 0
    doc = plan_book(args.persona, args.book_format, args.intent)
    doc["brand_id"] = args.brand
    write_atomically(outp, doc)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
