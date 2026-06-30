#!/usr/bin/env python3
# NEW-ARTIFACT-JUSTIFIED: ~1000-plan COUNT-INVARIANT sweep runner. EXTENDS (imports,
# never forks) scripts/qa/plan_scale_qa_suite.py — reuses build_plan, plan_cohesion,
# _engine_from_arc, _arc_chapter_count. Plan-only (NO --render-book). New logic only:
# (a) stratified persona×topic×duration matrix over arc-backed cells, (b) a PLAN-LEVEL
# between-atom repetition DETECTOR (measure only — fix is owned by the Atom Cohesion
# Chunked Plan A–F / adjacency-aware selector). Drops the structural/chapter-count proxy
# from the verdict per GUARDRAIL A (compact_chapter_subset vs chapter_count_default is
# intended-by-design + documented in format_registry.yaml).
"""
Plan-scale QA — ~1000-PLAN COUNT-INVARIANT SWEEP.

Pilot verdict (PR #3605) gated this sweep and corrected its scope:
  - Leakage: clean. Quality proxy: mostly holds.
  - STRUCTURAL proxy (plan chapter count == assembled count) is a DOCUMENTED
    non-predictor (compact_chapter_subset spine path vs chapter_count_default
    auto-plan). It is DROPPED from the verdict here — not a per-plan failure.

This sweep is PLAN-ONLY (deterministic, CPU, no render, no LLM, no GPU). It scores
each plan on COUNT-INVARIANT cohesion only (the set that passed 14/14 in the pilot):
band-arc coverage, intensity cadence, structure variety, slot fill, dwell-beat +
scene-anchor placement, and the plan-evaluable register-family structural checks.

It also runs a PLAN-LEVEL repetition DETECTOR (GUARDRAIL B, measure-only).

Usage:
  PYTHONPATH=. python3 scripts/qa/plan_scale_qa_sweep.py \
      --out-dir artifacts/qa/plan_scale_qa_sweep_20260630 --workers 8
  PYTHONPATH=. python3 scripts/qa/plan_scale_qa_sweep.py --limit 40   # smoke
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# EXTEND the pilot harness (import, never fork).
from scripts.qa.plan_scale_qa_suite import (  # noqa: E402
    PILOT_DURATIONS,
    _arc_chapter_count,
    _engine_from_arc,
    build_plan,
    plan_cohesion,
)

ARCS_DIR = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"

# Observed full-spine length for these topic spines (GUARDRAIL A: formats with no
# compact_chapter_subset render the full 12-chapter spine). Used so the repetition
# detector scores at the count the ASSEMBLED book actually has, not the arc's 20.
_FULL_SPINE_CHAPTERS = 12


def effective_assembled_chapters(runtime_format: str) -> int:
    """The chapter count the ASSEMBLER produces (compact_chapter_subset length, else
    full spine). This is the DOCUMENTED spine-path count, not chapter_count_default
    and not the arc's declared count — see format_registry.yaml compact_chapter_subset."""
    import yaml

    reg = yaml.safe_load(
        (REPO_ROOT / "config" / "format_selection" / "format_registry.yaml").read_text(encoding="utf-8")
    ) or {}
    spec = (reg.get("runtime_formats") or {}).get(runtime_format) or {}
    subset = spec.get("compact_chapter_subset")
    if isinstance(subset, list) and subset:
        return len(subset)
    return _FULL_SPINE_CHAPTERS


# ───────────────────── MATRIX ENUMERATION (arc-backed cells) ─────────────────────


def enumerate_cells() -> list[dict[str, Any]]:
    """Every (persona, topic) that has >=1 master arc → prioritise buildable cells.

    Picks one representative arc per (persona, topic) deterministically (sorted →
    first engine). Cross with all 7 pilot durations."""
    by_cell: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for p in sorted(ARCS_DIR.glob("*.yaml")):
        parts = p.stem.split("__")
        if len(parts) < 3:
            continue
        persona, topic = parts[0], parts[1]
        by_cell[(persona, topic)].append(p)
    cells: list[dict[str, Any]] = []
    for (persona, topic), arcs in sorted(by_cell.items()):
        arc = sorted(arcs)[0]
        for dur in PILOT_DURATIONS:
            cells.append(
                {
                    "persona": persona,
                    "topic": topic,
                    "duration": dur,
                    "arc": str(arc.relative_to(REPO_ROOT)),
                    "engine": _engine_from_arc(arc),
                }
            )
    return cells


# ───────────────────── PLAN-LEVEL REPETITION DETECTOR (GUARDRAIL B) ─────────────────────


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _ngrams(text: str, n: int = 4) -> list[str]:
    words = _norm(text).split()
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)] if len(words) >= n else []


def within_book_repetition(plan: dict[str, Any]) -> dict[str, Any]:
    """Quantify recurring planned content WITHIN one book (plan-level).

    Plan-visible repetition surfaces: chapter thesis text, chapter intent text,
    and slot-type sequence patterns. (Atom prose is render-time; the plan exposes
    thesis/intent/slot structure — the recurring-fragment risk the blind read flagged
    originates here.)"""
    chapters = plan.get("chapters") or []
    theses = [c.get("thesis") for c in chapters if c.get("thesis")]
    intents = [c.get("intent") for c in chapters if c.get("intent")]
    slot_seqs = [tuple(c.get("slot_types") or []) for c in chapters]

    def _dup_rate(items: list[str]) -> tuple[float, int]:
        norm = [_norm(x) for x in items if x]
        if not norm:
            return 0.0, 0
        counts = Counter(norm)
        dups = sum(c - 1 for c in counts.values() if c > 1)
        return round(dups / len(norm), 3), dups

    thesis_dup_rate, thesis_dups = _dup_rate(theses)
    intent_dup_rate, intent_dups = _dup_rate(intents)

    # Cross-chapter 4-gram overlap on thesis text (near-duplicate phrasing).
    all_ngrams: Counter = Counter()
    for t in theses:
        all_ngrams.update(set(_ngrams(t, 4)))
    repeated_ngrams = {g: c for g, c in all_ngrams.items() if c >= 2}
    ngram_repeat_rate = round(len(repeated_ngrams) / max(1, len(all_ngrams)), 3)

    # Slot-sequence monotony: identical slot-type tuple repeated across chapters.
    seq_counts = Counter(slot_seqs)
    max_identical_slot_seq = max(seq_counts.values()) if seq_counts else 0
    slot_seq_monotony = round(max_identical_slot_seq / max(1, len(slot_seqs)), 3)

    # Severity — driven by THESIS content repetition + near-duplicate phrasing.
    # `intent` is a small by-design phase vocabulary ("Name the pattern…") and is
    # reported but NOT scored. `slot_seq_monotony` only contributes above 0.5.
    score = (
        thesis_dup_rate * 0.55
        + ngram_repeat_rate * 0.30
        + max(0.0, slot_seq_monotony - 0.6) * 0.30
    )
    if score >= 0.30 or thesis_dups >= 3:
        severity = "HIGH"
    elif score >= 0.10 or thesis_dups >= 1:
        severity = "MEDIUM"
    elif repeated_ngrams:
        severity = "LOW"
    else:
        severity = "NONE"

    return {
        "thesis_dup_rate": thesis_dup_rate,
        "thesis_exact_dups": thesis_dups,
        "intent_dup_rate": intent_dup_rate,
        "ngram_repeat_rate": ngram_repeat_rate,
        "repeated_thesis_ngrams": list(repeated_ngrams.keys())[:8],
        "slot_seq_monotony": slot_seq_monotony,
        "severity": severity,
        "severity_score": round(score, 3),
    }


# ───────────────────── PER-CELL WORKER (plan-only, count-invariant) ─────────────────────


def score_cell(cell: dict[str, Any]) -> dict[str, Any]:
    persona, topic, dur = cell["persona"], cell["topic"], cell["duration"]
    arc = REPO_ROOT / cell["arc"]
    engine = cell.get("engine") or _engine_from_arc(arc)
    out: dict[str, Any] = {
        "persona": persona,
        "topic": topic,
        "duration": dur,
        "engine": engine,
        "arc": cell["arc"],
    }
    plan = build_plan(topic, persona, dur, engine, arc=arc)
    if not plan.get("ok"):
        err = plan.get("error", "")
        if "NO_ARC" in err or "no arc" in err.lower():
            bld = "NO_ARC"
        elif "BAND_DEFICIT" in err or "band" in err.lower():
            bld = "BAND_DEFICIT"
        elif "NO_STORY_POOL" in err or "story" in err.lower():
            bld = "NO_STORY_POOL"
        else:
            bld = "PLAN_ERROR"
        out["buildability"] = bld
        out["plan_ok"] = False
        out["error"] = err
        out["count_invariant_cohesion"] = "UNPLANNABLE"
        return out

    # Attach plan-visible repetition surfaces onto chapters for the detector.
    # IMPORTANT: build the detector plan at the ASSEMBLED (spine-path) chapter count,
    # not the arc's declared count — so the repetition measured is what the READER
    # actually gets (GUARDRAIL A: assembled count = compact_chapter_subset / full spine).
    eff_chapters = effective_assembled_chapters(dur)
    out["effective_assembled_chapters"] = eff_chapters
    try:
        from phoenix_v4.planning.book_structure_plan import generate_book_plan

        full = generate_book_plan(
            topic, persona, dur, engine, chapter_count=eff_chapters
        )
        enriched_chapters = []
        for ch in full.chapters:
            sp = getattr(ch, "slot_plans", None) or []
            slot_types = [s.get("slot_type") or s.get("type") for s in sp if isinstance(s, dict)]
            enriched_chapters.append(
                {
                    "thesis": getattr(ch, "chapter_thesis", None),
                    "intent": getattr(ch, "chapter_intent", None),
                    "slot_types": slot_types,
                }
            )
        plan["chapters_enriched"] = enriched_chapters
    except Exception:  # noqa: BLE001
        plan["chapters_enriched"] = []

    out["buildability"] = "PLANNABLE"
    out["plan_ok"] = True
    out["chapter_count"] = plan.get("chapter_count")

    # COUNT-INVARIANT cohesion (drop the chapter_count==assembled axis entirely).
    pc = plan_cohesion(plan)
    # Remove the count-dependent check from the verdict surface (it always passes for a
    # self-consistent plan, but we make the count-invariance explicit).
    checks = dict(pc.get("checks") or {})
    count_invariant_checks = {
        k: v for k, v in checks.items() if k != "chapter_count_matches"
    }
    ci_fail = any(v is False for v in count_invariant_checks.values())
    out["count_invariant_cohesion"] = "FAIL" if ci_fail else "PASS"
    out["cohesion_checks"] = count_invariant_checks
    out["cohesion_issues"] = pc.get("issues") or []

    # Repetition detector (measure only).
    rep_plan = {"chapters": plan.get("chapters_enriched") or []}
    out["repetition"] = within_book_repetition(rep_plan)
    # carry thesis text for cross-cell repetition aggregation
    out["_theses"] = [c.get("thesis") for c in (plan.get("chapters_enriched") or []) if c.get("thesis")]
    return out


# ───────────────────── ORCHESTRATION ─────────────────────


def _score_one(cell: dict[str, Any]) -> dict[str, Any]:
    try:
        return score_cell(cell)
    except Exception as exc:  # noqa: BLE001
        return {**cell, "buildability": "PLAN_ERROR", "plan_ok": False,
                "error": f"{type(exc).__name__}: {exc}", "count_invariant_cohesion": "UNPLANNABLE"}


def main() -> int:
    ap = argparse.ArgumentParser(description="~1000-plan count-invariant sweep")
    ap.add_argument("--out-dir", default="artifacts/qa/plan_scale_qa_sweep_20260630")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="cap cells (smoke)")
    ap.add_argument("--skip-finder", action="store_true")
    args = ap.parse_args()

    out_dir = (REPO_ROOT / args.out_dir) if not Path(args.out_dir).is_absolute() else Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cells = enumerate_cells()
    if args.limit:
        cells = cells[: args.limit]
    print(f"[sweep] {len(cells)} plans across {len({(c['persona'], c['topic']) for c in cells})} arc-backed cells × {len(PILOT_DURATIONS)} durations", flush=True)

    results: list[dict[str, Any]] = []
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_score_one, c): c for c in cells}
            done = 0
            for fut in as_completed(futs):
                results.append(fut.result())
                done += 1
                if done % 100 == 0:
                    print(f"  …{done}/{len(cells)}", flush=True)
    else:
        for i, c in enumerate(cells):
            results.append(_score_one(c))
            if (i + 1) % 100 == 0:
                print(f"  …{i + 1}/{len(cells)}", flush=True)

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # ── Census + pass rates ──
    buildability: Counter = Counter(r.get("buildability", "?") for r in results)
    plannable = [r for r in results if r.get("buildability") == "PLANNABLE"]
    ci_pass = sum(1 for r in plannable if r.get("count_invariant_cohesion") == "PASS")

    # by duration × persona × topic
    by_duration: dict[str, dict[str, int]] = defaultdict(lambda: {"plannable": 0, "ci_pass": 0})
    by_persona: dict[str, dict[str, int]] = defaultdict(lambda: {"plannable": 0, "ci_pass": 0})
    by_topic: dict[str, dict[str, int]] = defaultdict(lambda: {"plannable": 0, "ci_pass": 0})
    for r in plannable:
        for bucket, key in ((by_duration, r["duration"]), (by_persona, r["persona"]), (by_topic, r["topic"])):
            bucket[key]["plannable"] += 1
            if r.get("count_invariant_cohesion") == "PASS":
                bucket[key]["ci_pass"] += 1

    # ── Repetition census (within-book) ──
    rep_sev: Counter = Counter(
        (r.get("repetition") or {}).get("severity", "NONE") for r in plannable
    )
    rep_flagged = [
        {
            "persona": r["persona"], "topic": r["topic"], "duration": r["duration"],
            "severity": (r.get("repetition") or {}).get("severity"),
            "score": (r.get("repetition") or {}).get("severity_score"),
            "thesis_dups": (r.get("repetition") or {}).get("thesis_exact_dups"),
            "repeated_ngrams": (r.get("repetition") or {}).get("repeated_thesis_ngrams"),
        }
        for r in plannable
        if (r.get("repetition") or {}).get("severity") in ("HIGH", "MEDIUM")
    ]
    rep_flagged.sort(key=lambda x: (-(x["score"] or 0)))

    # ── Cross-cell repetition: identical theses reused across DIFFERENT cells ──
    thesis_to_cells: dict[str, set] = defaultdict(set)
    for r in plannable:
        for t in r.get("_theses") or []:
            thesis_to_cells[_norm(t)].add(f"{r['persona']}×{r['topic']}")
    cross_cell = sorted(
        ({"thesis": t[:140], "cell_count": len(cs), "sample_cells": sorted(cs)[:5]}
         for t, cs in thesis_to_cells.items() if len(cs) >= 3),
        key=lambda x: -x["cell_count"],
    )[:30]

    summary = {
        "timestamp": ts,
        "scope": "count-invariant plan-only sweep (structural/chapter-count proxy DROPPED per GUARDRAIL A)",
        "total_plans": len(results),
        "arc_backed_cells": len({(c["persona"], c["topic"]) for c in cells}),
        "durations": PILOT_DURATIONS,
        "buildability_census": dict(buildability),
        "count_invariant_cohesion_pass": f"{ci_pass}/{len(plannable)}",
        "by_duration": {k: dict(v) for k, v in sorted(by_duration.items())},
        "by_persona": {k: dict(v) for k, v in sorted(by_persona.items())},
        "by_topic": {k: dict(v) for k, v in sorted(by_topic.items())},
        "repetition_severity_census": dict(rep_sev),
        "repetition_flagged_count": len(rep_flagged),
        "cross_cell_repeated_theses": len(cross_cell),
        "guardrail_A": "chapter-count clamp is INTENDED-BY-DESIGN + DOCUMENTED (compact_chapter_subset vs chapter_count_default); structural-proxy claim DROPPED; no OPD escalation.",
    }

    # ── Write aggregate evidence (cap: no per-plan files) ──
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    # MATRIX.tsv — all rows
    tsv = ["persona\ttopic\tduration\tengine\tbuildability\tchapter_count\tcount_invariant_cohesion\trepetition_severity\trep_score\tcohesion_issues"]
    for r in sorted(results, key=lambda x: (x["persona"], x["topic"], x["duration"])):
        rep = r.get("repetition") or {}
        tsv.append("\t".join(str(x) for x in [
            r["persona"], r["topic"], r["duration"], r.get("engine", ""),
            r.get("buildability"), r.get("chapter_count", ""),
            r.get("count_invariant_cohesion"), rep.get("severity", ""),
            rep.get("severity_score", ""),
            "; ".join(r.get("cohesion_issues") or [])[:120],
        ]))
    (out_dir / "MATRIX.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")

    # REPETITION_CENSUS.json — measure-only, route to Atom-Cohesion lane
    (out_dir / "REPETITION_CENSUS.json").write_text(json.dumps({
        "note": "DETECTOR ONLY. Fix owned by Atom Cohesion Chunked Plan (A–F) / adjacency-aware selector (chunks A+E dispatched). Cells below are a ROUTE to that lane, not a new lane.",
        "severity_census": dict(rep_sev),
        "within_book_flagged": rep_flagged[:200],
        "cross_cell_repeated_theses": cross_cell,
    }, indent=2, default=str), encoding="utf-8")

    print("\n=== SWEEP SUMMARY ===")
    print(f"total plans: {len(results)}  | buildability: {dict(buildability)}")
    print(f"count-invariant cohesion pass: {ci_pass}/{len(plannable)}")
    print(f"repetition severity: {dict(rep_sev)} | within-book flagged: {len(rep_flagged)} | cross-cell theses: {len(cross_cell)}")
    print(f"evidence: {out_dir}")

    if not args.skip_finder and sys.platform == "darwin":
        import subprocess
        subprocess.run(["open", str(out_dir)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
