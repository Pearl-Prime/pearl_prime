#!/usr/bin/env python3
"""
Rank narrators from config/narrators/narrator_registry.yaml against an author_voice_profiles entry.
Heuristic v1: approved narrators in author.approved_narrator_ids that exist and are approved;
order preserved. Extend with scoring (persona_alignment, pacing) in v2.

Usage:
  python3 scripts/onboarding/match_narrators_for_author.py onboarding_demo_stillness
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHORS = ROOT / "config" / "authors" / "author_voice_profiles.yaml"
REGISTRY = ROOT / "config" / "narrators" / "narrator_registry.yaml"


def _load_yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    author_id = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not author_id:
        print("usage: match_narrators_for_author.py <author_id>", file=sys.stderr)
        return 1

    authors_doc = _load_yaml(AUTHORS)
    reg = _load_yaml(REGISTRY)
    authors = authors_doc.get("authors") or {}
    entry = authors.get(author_id)
    if not entry:
        print(f"unknown author_id {author_id!r}", file=sys.stderr)
        return 1

    narrators = reg.get("narrators") or {}
    preferred = entry.get("approved_narrator_ids") or []
    fallbacks = entry.get("fallback_narrator_ids") or []

    def ok(nid: str) -> bool:
        n = narrators.get(nid)
        return bool(n) and n.get("status") == "approved"

    ranked = [nid for nid in preferred if ok(nid)]
    for nid in fallbacks:
        if nid not in ranked and ok(nid):
            ranked.append(nid)

    print("author:", author_id)
    for i, nid in enumerate(ranked, 1):
        n = narrators[nid]
        print(f"  {i}. {nid} — {n.get('display_name')} edge={n.get('edge_tts_voice')!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
