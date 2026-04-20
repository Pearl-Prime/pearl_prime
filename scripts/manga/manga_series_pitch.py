#!/usr/bin/env python3
"""Generate a named-series identity YAML stub (LLM wiring optional)."""
from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _slug(s: str) -> str:
    s = s.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]+", "", s) or "series"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--genre", required=True)
    ap.add_argument("--persona", default="gen_z_professionals")
    args = ap.parse_args()

    slug = _slug(f"{args.brand}_{args.topic}_{args.genre}")
    out_dir = REPO_ROOT / "config" / "source_of_truth" / "manga_series_identities"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}.yaml"

    doc = {
        "schema_version": "1.0.0",
        "series_slug": slug,
        "brand": args.brand,
        "topic": args.topic,
        "genre": args.genre,
        "persona": args.persona,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "marketing_title": f"{args.topic.replace('_', ' ').title()} — draft",
        "logline": "Operator: replace with Claude-generated logline when CLAUDE_API_KEY is wired.",
        "high_concept": "",
        "tagline": "",
        "volume_plan": [],
        "character_roster": [],
        "setting_bible": "",
        "llm": {
            "status": "stub",
            "note": "Set CLAUDE_API_KEY in Actions to enable full pitch generation.",
        },
    }
    if (os.environ.get("CLAUDE_API_KEY") or "").strip():
        doc["llm"]["status"] = "key_present_operator_to_extend"

    path.write_text(yaml.dump(doc, sort_keys=False, allow_unicode=True) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
