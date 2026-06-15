#!/usr/bin/env python3
"""Evidence: does honoring compact_chapter_subset cut F1 + word-overshoot?

Renders gen_z_professionals x anxiety at the 3 subset-declaring compact formats
BOTH ways and scores each with the register gate:
  before_fix  = load_spine(topic)                  -> full 12-chapter spine (current bug)
  after_fix   = load_spine(topic, runtime_format)  -> declared subset (N chapters)

Also re-renders the 3 non-subset short tiers (12ch either way) as a faithfulness
sanity-check against artifacts/qa/duration_ladder_20260615 (should reproduce its
words / F1 numbers, proving this harness matches the published ladder).

Deterministic atom composition; NO paid LLM API (CLAUDE.md tier policy).
Run:  PYTHONPATH=. python3 artifacts/qa/duration_ladder_subset_proof_20260615/gen_proof.py
"""
from __future__ import annotations

import json
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
SEED = "pilot_v1"
OUT = Path(__file__).resolve().parent

COMPACT = [
    ("compact_book_5ch_15min", (3000, 4500)),
    ("compact_book_5ch_20min", (4000, 5500)),
    ("compact_book_8ch_30min", (5500, 7500)),
]
SHORT_REF = [
    ("micro_book_15", (2500, 4500)),
    ("short_book_30", (4500, 7500)),
    ("one_hour_book", (8000, 10000)),
]


import phoenix_v4.planning.knob_apply as _ka  # noqa: E402

_ORIG_SUBSET = _ka._load_compact_chapter_subset


def render(fmt: str, honor_subset: bool) -> str:
    # honor_subset=False reproduces the CURRENT origin/main bug (subset declared
    # but never applied) by neutralizing _load_compact_chapter_subset for BOTH the
    # spine load here AND the re-load inside compile_beatmap, keeping them consistent
    # at the full 12-chapter spine. honor_subset=True = both calls subset (fixed).
    _ka._load_compact_chapter_subset = (
        _ORIG_SUBSET if honor_subset else (lambda *a, **k: None)
    )
    try:
        spine = load_spine(TOPIC, ROOT, runtime_format=fmt)
        knobs = load_knob_profile(TOPIC, ROOT)
        shaped = apply_knobs(
            spine, knobs, runtime_format=fmt, persona_id=PERSONA, repo_root=ROOT
        )
        engines = load_topic_engines(TOPIC, ROOT)
        fmt_spec = load_format_spec(fmt, ROOT)
        beatmap = compile_beatmap(shaped, engines, fmt_spec, ROOT)
        req = EnrichmentRequest(
            beatmap=beatmap,
            teacher_id=None,
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
    finally:
        _ka._load_compact_chapter_subset = _ORIG_SUBSET


def score(prose: str) -> tuple[dict, dict]:
    res = evaluate_register(
        prose, persona_id=PERSONA, topic_id=TOPIC, quality_profile="production"
    )
    j = res.to_json()
    byid: dict[str, int] = {}
    for f in j.get("findings", []):
        fid = f.get("failure_id", "?")
        byid[fid] = byid.get(fid, 0) + 1
    return j, byid


def words(p: str) -> int:
    return len(p.split())


def chapters(p: str) -> int:
    return len(re.findall(r"(?m)^Chapter \d+$", p))


def overshoot_pct(w: int, wr: tuple[int, int]) -> str:
    lo, hi = wr
    if w > hi:
        return f"+{round(100 * (w - hi) / hi)}% OVER"
    if w < lo:
        return f"-{round(100 * (lo - w) / lo)}% UNDER"
    return "in-range"


def emit(fmt, variant, wr, prose, j, byid, rows):
    ch, w = chapters(prose), words(prose)
    d = OUT / f"{fmt}__{variant}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "book.txt").write_text(prose, encoding="utf-8")
    (d / "register_report.json").write_text(json.dumps(j, indent=2), encoding="utf-8")
    row = dict(
        fmt=fmt, variant=variant, word_range=list(wr), chapters=ch, words=w,
        overshoot=overshoot_pct(w, wr), verdict=j["verdict"],
        F1=byid.get("F1", 0), F2=byid.get("F2", 0), F7=byid.get("F7", 0),
        total_findings=len(j.get("findings", [])),
    )
    rows.append(row)
    print(f"{fmt:26} {variant:13} ch={ch:>2} words={w:>6} ({row['overshoot']:>10}) "
          f"F1={row['F1']:>3} F2={row['F2']:>2} F7={row['F7']:>2} {j['verdict']}")
    return row


def main() -> int:
    rows: list[dict] = []
    print("=== COMPACT formats: before_fix (12ch) vs after_fix (declared subset) ===")
    for fmt, wr in COMPACT:
        for honor, variant in ((False, "before_fix"), (True, "after_fix")):
            prose = render(fmt, honor)
            j, byid = score(prose)
            emit(fmt, variant, wr, prose, j, byid, rows)
    print("\n=== SHORT non-subset tiers: faithfulness check vs published ladder (still 12ch) ===")
    for fmt, wr in SHORT_REF:
        prose = render(fmt, True)  # no subset declared -> 12ch either way
        j, byid = score(prose)
        emit(fmt, "reference_12ch", wr, prose, j, byid, rows)

    (OUT / "SUMMARY.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT / 'SUMMARY.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
