#!/usr/bin/env python3
"""Pinpoint WHERE the residual 'task is open' HOOK cluster is injected.

The depth-dedup fix cuts deep_book_6h F1 224->121, but the size-14 HOOK cluster
only drops to 13. Either (a) the HOOK is depth-injected and the fix has a gap, or
(b) the HOOK is injected downstream of apply_depth_pass (the composer's HOOK
aggregation), i.e. OUT of enrichment_select's scope. This script counts the HOOK
phrase at each pipeline stage to decide:

  base slots (post select_enrichment)  -> if ~13: it's a BASE-plan slot (not depth)
  depth slots (post apply_depth_pass)  -> if jumps to ~13: DEPTH injects it (fix gap)
  composed prose                        -> if ~13 but slots ~0-2: COMPOSER injects it

Run: PYTHONPATH=. python3 artifacts/qa/f1_depth_dedup_verify_20260615/diag_hook_injector.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine  # noqa: E402
from phoenix_v4.planning.beatmap_compile import (  # noqa: E402
    compile_beatmap, load_format_spec, load_topic_engines,
)
from phoenix_v4.planning.enrichment_select import (  # noqa: E402
    EnrichmentRequest, apply_depth_pass, select_enrichment,
)
from phoenix_v4.rendering.book_renderer import clean_for_delivery  # noqa: E402
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book  # noqa: E402

TOPIC, PERSONA, TEACHER, SEED, FMT = "anxiety", "gen_z_professionals", "ahjan", "leverB_baseline", "deep_book_6h"
PROBES = ["The task is open", "Now, I want you to notice", "Just thirty seconds", "This is The Unspoken"]


def slot_text(enriched) -> str:
    parts = []
    for ch in enriched.chapters:
        for sl in ch.slots:
            parts.append(sl.content or "")
    return "\n\n".join(parts)


def counts(label: str, text: str) -> None:
    print(f"{label:28} | " + " | ".join(f"{p!r}: {text.count(p)}" for p in PROBES))


def main() -> int:
    spine = load_spine(TOPIC, ROOT, runtime_format=FMT)
    shaped = apply_knobs(spine, load_knob_profile(TOPIC, ROOT), runtime_format=FMT,
                         persona_id=PERSONA, repo_root=ROOT)
    beatmap = compile_beatmap(shaped, load_topic_engines(TOPIC, ROOT),
                              load_format_spec(FMT, ROOT), ROOT)
    req = EnrichmentRequest(beatmap=beatmap, teacher_id=TEACHER, persona_id=PERSONA,
                            topic_id=TOPIC, seed=SEED)
    enriched = select_enrichment(req, ROOT)
    counts("base slots (post-select)", slot_text(enriched))

    depth_map = yaml.safe_load(
        (ROOT / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    enriched = apply_depth_pass(enriched, depth_map, repo_root=ROOT)
    counts("depth slots (post-depth)", slot_text(enriched))

    prose = clean_for_delivery(compose_from_enriched_book(enriched, quality_profile="draft"))
    counts("composed prose", prose)

    # Which depth modules were added, and did any carry the HOOK?
    added = enriched.enrichment_audit.get("depth_modules_added", [])
    hook_depth = [a for a in added if "task is open" in str(a).lower()
                  or "task is open" in str(a.get("excerpt", "")).lower()]
    print(f"\ndepth_modules_added: {len(added)} total; "
          f"{len(hook_depth)} reference 'task is open'")
    # Stage attribution verdict
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
