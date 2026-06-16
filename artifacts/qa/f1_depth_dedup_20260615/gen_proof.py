#!/usr/bin/env python3
"""F1 depth-dedup proof — ws_f1_depth_dedup_20260615 (task_48b619ed).

Reproduces ⑤'s Lever-B baseline cell (gen_z_professionals × anxiety, teacher=ahjan)
at the three full-12 tiers and scores each with the register gate's F1 detector,
BEFORE and AFTER the cross-chapter fuzzy depth-dedup in
``enrichment_select.apply_depth_pass``.

⑤ baseline (origin/main a4021381c, identical composer): standard 61 / extended 67
/ deep 224 F1 clusters. The fix replaces the per-chapter EXACT-match
``book_seen_bodies`` dedup with a BOOK-WIDE FUZZY (Jaccard ≥ threshold) registry,
so the same atom body (modulo per-chapter trailing-clause variation) is not
re-injected across all 12 chapters; the depth selector instead rotates to an
unused sibling ARC block / variant (the HOOK atom has 88 blocks of headroom).

Toggle the fix via env ``PHOENIX_DEPTH_DEDUP_FUZZY`` (default "1" = on); set "0"
to render the legacy per-chapter exact-match baseline through the identical
harness. Both variants share the same composer, atoms, and seed, so the F1 delta
is attributable purely to the depth-dedup change.

Build is deterministic; NO paid LLM API (CLAUDE.md tier policy).
Run:  PYTHONPATH=. python3 artifacts/qa/f1_depth_dedup_20260615/gen_proof.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
assert (ROOT / "phoenix_v4").is_dir(), f"repo root wrong: {ROOT}"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine  # noqa: E402
from phoenix_v4.planning.beatmap_compile import (  # noqa: E402
    compile_beatmap,
    load_format_spec,
    load_topic_engines,
)
from phoenix_v4.planning.enrichment_select import (  # noqa: E402
    EnrichmentRequest,
    apply_depth_pass,
    select_enrichment,
)
from phoenix_v4.rendering.book_renderer import clean_for_delivery  # noqa: E402
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book  # noqa: E402
from phoenix_v4.quality.register_gate import evaluate_register  # noqa: E402

TOPIC = "anxiety"
PERSONA = "gen_z_professionals"
TEACHER = "ahjan"            # ⑤'s cell ("For Ahjan, the work begins in the body…")
SEED = "leverB_baseline"     # ⑤'s seed
OUT = Path(__file__).resolve().parent

# ⑤'s full-12 tiers + baseline F1 (origin/main a4021381c).
TIERS = [
    ("standard_book", 61),
    ("extended_book_2h", 67),
    ("deep_book_6h", 224),
]


def render(fmt: str) -> str:
    spine = load_spine(TOPIC, ROOT, runtime_format=fmt)
    knobs = load_knob_profile(TOPIC, ROOT)
    shaped = apply_knobs(spine, knobs, runtime_format=fmt, persona_id=PERSONA, repo_root=ROOT)
    engines = load_topic_engines(TOPIC, ROOT)
    fmt_spec = load_format_spec(fmt, ROOT)
    beatmap = compile_beatmap(shaped, engines, fmt_spec, ROOT)
    req = EnrichmentRequest(
        beatmap=beatmap,
        teacher_id=TEACHER,
        persona_id=PERSONA,
        topic_id=TOPIC,
        seed=SEED,
    )
    enriched = select_enrichment(req, ROOT)
    depth_map = yaml.safe_load(
        (ROOT / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    enriched = apply_depth_pass(enriched, depth_map, repo_root=ROOT)
    prose = compose_from_enriched_book(enriched, quality_profile="draft")
    return clean_for_delivery(prose)


def score(prose: str) -> dict:
    res = evaluate_register(prose, persona_id=PERSONA, topic_id=TOPIC, quality_profile="production")
    j = res.to_json()
    byid: dict[str, int] = {}
    f1_sizes: dict[int, int] = {}
    for f in j.get("findings", []):
        fid = f.get("failure_id", "?")
        byid[fid] = byid.get(fid, 0) + 1
        if fid == "F1":
            m = re.search(r"cluster size (\d+)", f.get("summary", ""))
            if m:
                sz = int(m.group(1))
                f1_sizes[sz] = f1_sizes.get(sz, 0) + 1
    return {
        "verdict": j["verdict"],
        "F1": byid.get("F1", 0),
        "F2": byid.get("F2", 0),
        "F7": byid.get("F7", 0),
        "total_findings": len(j.get("findings", [])),
        "F1_sizes": dict(sorted(f1_sizes.items())),
    }


def words(p: str) -> int:
    return len(p.split())


def chapters(p: str) -> int:
    return len(re.findall(r"(?m)^Chapter \d+$", p))


def cluster_phrase_counts(prose: str) -> dict[str, int]:
    """⑤'s named re-injection clusters — raw verbatim counts (completeness/F1 proxy)."""
    probes = {
        "HOOK v02 'The task is open'": "The task is open",
        "EXERCISE 'Just thirty seconds'": "Just thirty seconds",
        "EXERCISE 'Now, I want you to notice'": "Now, I want you to notice",
        "doctrine 'This is The Unspoken'": "This is The Unspoken",
    }
    return {label: prose.count(needle) for label, needle in probes.items()}


def main() -> int:
    variant = "after_fix" if os.environ.get("PHOENIX_DEPTH_DEDUP_FUZZY", "1") != "0" else "baseline"
    rows: list[dict] = []
    print(f"=== F1 depth-dedup proof — variant={variant} "
          f"(PHOENIX_DEPTH_DEDUP_FUZZY={os.environ.get('PHOENIX_DEPTH_DEDUP_FUZZY', '1')}) ===")
    print(f"cell: {PERSONA} × {TOPIC} (teacher={TEACHER}, seed={SEED})\n")
    for fmt, baseline_f1 in TIERS:
        prose = render(fmt)
        s = score(prose)
        ch, w = chapters(prose), words(prose)
        d = OUT / variant / fmt
        d.mkdir(parents=True, exist_ok=True)
        (d / "book.txt").write_text(prose, encoding="utf-8")
        probes = cluster_phrase_counts(prose)
        row = dict(
            fmt=fmt, variant=variant, chapters=ch, words=w,
            baseline_F1=baseline_f1, **s, cluster_phrase_counts=probes,
        )
        rows.append(row)
        print(f"{fmt:18} ch={ch:>2} words={w:>6} F1={s['F1']:>3} (⑤ base {baseline_f1:>3}) "
              f"F2={s['F2']:>2} F7={s['F7']:>2} {s['verdict']}")
        print(f"    F1_sizes={s['F1_sizes']}")
        print(f"    re-inject counts: " + ", ".join(f"{k.split(chr(39))[1] if chr(39) in k else k}={v}"
                                                     for k, v in probes.items()))
    (OUT / f"SUMMARY_{variant}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT / f'SUMMARY_{variant}.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
