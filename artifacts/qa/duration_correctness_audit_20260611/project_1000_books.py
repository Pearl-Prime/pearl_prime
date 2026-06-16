#!/usr/bin/env python3
"""
PLAN-ONLY projection of 1000 books. NO prose assembly, NO LLM, NO generation.

Every constant is sourced from repo config or measured from real output:
  - word_range, duration_minutes, chapter_count : config/format_selection/format_registry.yaml
  - intended listening pace 150 WPM             : config/duration_scorecard.yaml tts_wpm + OVERLAY_SPEC §413
  - reading pace 230 WPM                        : standard ebook reading speed (secondary edition)
  - production target REGIME per format         : see FORMATS[].regime + evidence
  - render inflation 1.073                       : MEASURED gold standard_book 21454 / 20000 (QA budget.json)
  - per-slot atom word counts                    : atom_wordcount_distributions.json (66k real variants)

Two failure modes are separated:
  MODE 1 (assembly overshoot of own word cap): projected_render vs word_range[max]
  MODE 2 (advertised duration is wrong wpm-math): implied minutes (words/wpm) vs advertised duration_minutes

Outputs:
  duration_audit_data.tsv        one row per planned book
  projection_results.json        per-format aggregates + Mode-2 deterministic table
"""
from __future__ import annotations
import json
import random
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

LISTEN_WPM = 150   # intended audiobook pace (config tts_wpm + OVERLAY_SPEC §413 "TTS pace (flat, 150 WPM)")
READ_WPM = 230     # secondary ebook reading edition

# Measured render inflation: gold standard_book rendered 21454 vs depth-fill target 20000.
RENDER_INFLATION_MEAN = 21454 / 20000   # = 1.0727
RENDER_INFLATION_SD = 0.05              # ASSUMPTION (only one clean anchor) — flagged in report

N_BOOKS = 1000
SEED = 20260611

# ── The 10 fully-specced runtime formats (advertised duration + word_range present) ──
# regime = where depth-fill lands the production word count inside [floor,cap]:
#   'cap'      standard_book: gold redirect fills to ceiling (QA + registry ceiling-raise history 13k→18k→20k)
#   'floor'    deep_book_6h : registry comment "compose retains ~72% → ~52K final (clear 50K floor)"
#   'midpoint' beatmap_compile.py:651 hard-validates plan total to midpoint ±10% (general default)
FORMATS = {
    "micro_book_15":          {"adv_min": 15,  "wr": [2500, 4500],  "ch": 5,  "regime": "midpoint"},
    "micro_book_20":          {"adv_min": 20,  "wr": [3000, 5500],  "ch": 6,  "regime": "midpoint"},
    "short_book_30":          {"adv_min": 30,  "wr": [4500, 7500],  "ch": 8,  "regime": "midpoint"},
    "standard_book":          {"adv_min": 55,  "wr": [9000, 20000], "ch": 12, "regime": "cap"},
    "extended_book_2h":       {"adv_min": 120, "wr": [17000, 25000],"ch": 14, "regime": "midpoint"},
    "deep_book_4h":           {"adv_min": 240, "wr": [20000, 40000],"ch": 16, "regime": "midpoint"},
    "deep_book_6h":           {"adv_min": 360, "wr": [50000, 72000],"ch": 20, "regime": "floor"},
    "compact_book_5ch_15min": {"adv_min": 15,  "wr": [3000, 4500],  "ch": 5,  "regime": "midpoint"},
    "compact_book_5ch_20min": {"adv_min": 20,  "wr": [4000, 5500],  "ch": 5,  "regime": "midpoint"},
    "compact_book_8ch_30min": {"adv_min": 30,  "wr": [5500, 7500],  "ch": 8,  "regime": "midpoint"},
}

GOLD_PERSONAS = {"gen_z_professionals", "corporate_managers", "working_parents",
                 "first_responders", "healthcare_rns"}
GOLD_TOPICS = {"anxiety", "overthinking", "burnout"}

# Default 6-beat chapter slot template (config/format_selection/format_registry.yaml default_slot_definitions)
BEAT = ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]


def regime_target(rng: random.Random, fmt: dict) -> float:
    """Production word target inside [floor,cap] per the format's depth-fill regime."""
    floor, cap = fmt["wr"]
    mid = (floor + cap) / 2.0
    r = fmt["regime"]
    if r == "cap":
        # depth-fill pins to ceiling; QA post_depth == cap exactly. tiny downward jitter only.
        return cap * rng.uniform(0.99, 1.00)
    if r == "floor":
        # deep_6h lands ~floor*1.04 (registry: ~52k vs 50k floor)
        return floor * rng.uniform(1.02, 1.06)
    # midpoint: beatmap ±10% validated band
    return mid * rng.uniform(0.90, 1.10)


def sample_inflation(rng: random.Random) -> float:
    v = rng.gauss(RENDER_INFLATION_MEAN, RENDER_INFLATION_SD)
    return max(0.95, v)  # render never compresses below ~plan


def tri(rng: random.Random, lo, mode, hi) -> float:
    lo, mode, hi = float(lo), float(mode), float(hi)
    if hi <= lo:
        return mode
    mode = min(max(mode, lo), hi)
    return rng.triangular(lo, hi, mode)


def atom_floor_words(rng: random.Random, dist: dict, persona: str, topic: str, n_ch: int) -> int:
    """Pre-depth-fill atom-sum FLOOR: n_ch chapters x one variant per 6-beat slot.
    Uses scoped (persona|topic|SLOT) distribution where available, else global SLOT."""
    g = dist["by_slot_global"]
    scoped = dist["by_persona_topic_slot"]
    total = 0
    for _ in range(n_ch):
        for slot in BEAT:
            key = f"{persona}|{topic}|{slot}"
            d = scoped.get(key) or g.get(slot) or {}
            if d.get("n", 0) >= 3:
                total += tri(rng, d["p10"], d["median"], d["p90"])
            else:
                total += g.get(slot, {}).get("median", 60)
    return int(total)


def pctl(vals, q):
    vals = sorted(vals)
    if not vals:
        return 0
    return vals[min(len(vals) - 1, max(0, int(q * (len(vals) - 1))))]


def main() -> None:
    rng = random.Random(SEED)
    dist = json.loads((HERE / "atom_wordcount_distributions.json").read_text())
    persona_topics = dist["persona_topics"]

    # Build a weighted (persona,topic) sampling frame; gold combos x3.
    combos = []
    for persona, topics in persona_topics.items():
        for topic in topics:
            w = 1
            if persona in GOLD_PERSONAS:
                w *= 2
            if topic in GOLD_TOPICS:
                w *= 3
            combos.extend([(persona, topic)] * w)

    locale = "en-US"
    per_fmt = N_BOOKS // len(FORMATS)

    rows = []
    for fmt_id, fmt in FORMATS.items():
        floor, cap = fmt["wr"]
        adv = fmt["adv_min"]
        for _ in range(per_fmt):
            persona, topic = rng.choice(combos)
            n_ch = max(1, fmt["ch"] + rng.choice([-1, 0, 0, 0, 1]))
            target = regime_target(rng, fmt)
            inflation = sample_inflation(rng)
            projected = target * inflation
            floor_words = atom_floor_words(rng, dist, persona, topic, n_ch)

            implied_listen = projected / LISTEN_WPM
            implied_read = projected / READ_WPM
            over_under_pct = (projected - cap) / cap * 100.0          # MODE 1 (vs cap)
            dur_gap_listen = (implied_listen - adv) / adv * 100.0      # MODE 2 (listening)
            dur_gap_read = (implied_read - adv) / adv * 100.0          # MODE 2 (reading)

            rows.append({
                "format": fmt_id, "persona": persona, "topic": topic, "locale": locale,
                "regime": fmt["regime"], "chapters": n_ch,
                "projected_words": int(round(projected)),
                "atom_floor_words": floor_words,
                "advertised_words_cap": cap, "advertised_words_floor": floor,
                "advertised_minutes": adv,
                "implied_min_listening": round(implied_listen, 1),
                "implied_min_reading": round(implied_read, 1),
                "over_under_pct_vs_cap": round(over_under_pct, 1),
                "duration_gap_pct_listening": round(dur_gap_listen, 1),
                "duration_gap_pct_reading": round(dur_gap_read, 1),
            })

    # ── write TSV ──
    cols = ["format", "persona", "topic", "locale", "regime", "chapters",
            "projected_words", "atom_floor_words", "advertised_words_floor",
            "advertised_words_cap", "advertised_minutes",
            "implied_min_listening", "implied_min_reading",
            "over_under_pct_vs_cap", "duration_gap_pct_listening", "duration_gap_pct_reading"]
    tsv = HERE / "duration_audit_data.tsv"
    with tsv.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")

    # ── per-format aggregates ──
    agg = {}
    for fmt_id, fmt in FORMATS.items():
        fr = [r for r in rows if r["format"] == fmt_id]
        floor, cap = fmt["wr"]
        mid = (floor + cap) / 2
        adv = fmt["adv_min"]
        pw = [r["projected_words"] for r in fr]
        fw = [r["atom_floor_words"] for r in fr]
        il = [r["implied_min_listening"] for r in fr]
        irr = [r["implied_min_reading"] for r in fr]
        ou = [r["over_under_pct_vs_cap"] for r in fr]
        # MODE 2 deterministic (no projection) at floor/mid/cap
        det = {
            pt_name: {
                "words": int(w),
                "listen_min": round(w / LISTEN_WPM, 1),
                "read_min": round(w / READ_WPM, 1),
                "gap_listen_pct": round((w / LISTEN_WPM - adv) / adv * 100, 1),
                "gap_read_pct": round((w / READ_WPM - adv) / adv * 100, 1),
                "implied_wpm": round(w / adv, 0),
            }
            for pt_name, w in (("floor", floor), ("mid", mid), ("cap", cap))
        }
        agg[fmt_id] = {
            "advertised_minutes": adv,
            "word_range": [floor, cap],
            "regime": fmt["regime"],
            "n": len(fr),
            "projected_words": {
                "median": int(st.median(pw)), "mean": int(st.mean(pw)),
                "p10": pctl(pw, .10), "p90": pctl(pw, .90),
                "min": min(pw), "max": max(pw),
            },
            "bare6beat_skeleton_words_median": int(st.median(fw)),
            "production_vs_bare6beat_ratio": round(st.median(pw) / max(1, st.median(fw)), 2),
            "pct_over_cap": round(100 * sum(1 for r in fr if r["projected_words"] > cap) / len(fr), 1),
            "pct_under_floor": round(100 * sum(1 for r in fr if r["projected_words"] < floor) / len(fr), 1),
            "over_under_vs_cap_median_pct": round(st.median(ou), 1),
            "implied_min_listening": {"median": round(st.median(il), 1), "p10": pctl(il, .1), "p90": pctl(il, .9)},
            "implied_min_reading": {"median": round(st.median(irr), 1), "p10": pctl(irr, .1), "p90": pctl(irr, .9)},
            "duration_gap_listening_median_pct": round(st.median([r["duration_gap_pct_listening"] for r in fr]), 1),
            "duration_gap_reading_median_pct": round(st.median([r["duration_gap_pct_reading"] for r in fr]), 1),
            "mode2_deterministic": det,
        }

    results = {
        "_meta": {
            "n_books": len(rows), "seed": SEED,
            "listen_wpm": LISTEN_WPM, "read_wpm": READ_WPM,
            "render_inflation_mean": round(RENDER_INFLATION_MEAN, 4),
            "render_inflation_sd": RENDER_INFLATION_SD,
            "render_inflation_source": "MEASURED gold standard_book 21454/20000 (QA budget.json); SINGLE anchor — flagged",
            "intended_pace_source": "config/duration_scorecard.yaml tts_wpm:150 + OVERLAY_SPEC §413",
            "field_notes": {
                "bare6beat_skeleton_words": "LOWER BOUND only: n_chapters x ONE variant per 6-beat slot "
                    "(HOOK/SCENE/STORY/REFLECTION/EXERCISE/INTEGRATION) sampled from real atoms. NOT the "
                    "pipeline's pre-depth total — production uses a far richer 15+ slot beatmap "
                    "(QA book pre_depth was 19,026 via ANGLE_DEFINITION/TEACHER_DOCTRINE/repeated slots). "
                    "Use this only to show a minimal-beat book is far shorter than the advertised-cap book.",
                "production_vs_bare6beat_ratio": "production median / bare-6beat median. Reflects richer beatmap "
                    "+ depth-fill combined; do NOT read as '% padding'.",
                "projected_words": "regime_target x render_inflation. Calibrated: standard_book median 21,514 vs "
                    "real gold render 21,454 (0.3%).",
            },
        },
        "per_format": agg,
    }
    (HERE / "projection_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"Wrote {tsv.name} ({len(rows)} rows) and projection_results.json\n")
    hdr = f"{'format':24s} {'adv':>4} {'cap':>6} {'proj_med':>8} {'%>cap':>6} {'listen_med':>10} {'gap_L%':>7} {'read_med':>8} {'gap_R%':>7}"
    print(hdr); print("-" * len(hdr))
    for fmt_id, a in agg.items():
        print(f"{fmt_id:24s} {a['advertised_minutes']:4d} {a['word_range'][1]:6d} "
              f"{a['projected_words']['median']:8d} {a['pct_over_cap']:6.0f} "
              f"{a['implied_min_listening']['median']:10.1f} {a['duration_gap_listening_median_pct']:7.0f} "
              f"{a['implied_min_reading']['median']:8.1f} {a['duration_gap_reading_median_pct']:7.0f}")


if __name__ == "__main__":
    main()
