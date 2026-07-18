"""
Duration Adherence Scorecard.

Read-only measurement: how well pipeline outputs hit planned duration/word-count
targets per runtime_format × structural_format combination.

Produces:
- Per-runtime-format summary table
- Per-structural-format breakdown
- Worst offenders list
- Overall pipeline health score + grade

Output: artifacts/ops/duration_scorecard_{date}.json

Exit: 0 grade A/B/C, 1 grade D/F.

When no production outputs exist, --synthetic generates sample data from
format_registry.yaml targets for infrastructure validation.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------------------
# Data loading: discover plan JSONs in artifacts/
# ---------------------------------------------------------------------------

def discover_plan_outputs(artifacts_dir: Path) -> List[dict]:
    """Find all .plan.json files under artifacts/ that contain assembled book data."""
    plans = []
    for p in artifacts_dir.rglob("*.plan.json"):
        data = _load_json(p)
        if data and isinstance(data, dict):
            data["_source_path"] = str(p)
            plans.append(data)
    # Also check rendered/ for any JSON manifests
    for p in artifacts_dir.rglob("*.json"):
        if p.suffix == ".json" and "plan" not in p.name and p.name != "manifest.json":
            continue
        data = _load_json(p)
        if data and isinstance(data, dict) and "chapters" in data:
            if str(p) not in [pl.get("_source_path") for pl in plans]:
                data["_source_path"] = str(p)
                plans.append(data)
    return plans


def generate_synthetic_outputs(
    registry: dict,
    count_per_format: int = 3,
    seed: int = 42,
) -> List[dict]:
    """Generate synthetic plan outputs from format_registry targets for testing."""
    rng = random.Random(seed)
    runtime_formats = registry.get("runtime_formats") or {}
    structural_formats = registry.get("structural_formats") or {}
    plans: List[dict] = []

    for rt_id, rt in runtime_formats.items():
        word_min, word_max = rt.get("word_range", [5000, 10000])
        ch_default = rt.get("chapter_count_default", 10)
        duration_min = rt.get("duration_minutes", 55)
        compatible = rt.get("compatible_structural_formats", [])
        tier = (rt.get("compatible_tiers") or ["A"])[0]

        for i in range(count_per_format):
            # Pick a structural format
            sf_id = compatible[i % len(compatible)] if compatible else "F006"
            sf = structural_formats.get(sf_id, {})
            ch_range = sf.get("chapter_range", [ch_default, ch_default])

            # Vary word count around target (some within range, some outside)
            target_mid = (word_min + word_max) / 2
            deviation = rng.gauss(0, (word_max - word_min) * 0.3)
            actual_words = max(500, int(target_mid + deviation))

            # Vary chapter count
            ch_target = ch_default
            ch_actual = ch_target + rng.choice([-1, 0, 0, 0, 1])
            ch_actual = max(1, ch_actual)

            # Build synthetic chapters with slots
            chapters = []
            slots_per_ch = ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
            if rng.random() > 0.3:
                slots_per_ch.extend(["PIVOT", "TAKEAWAY", "THREAD"])
            if rng.random() > 0.6:
                slots_per_ch.append("PERMISSION")

            words_per_ch = actual_words // ch_actual if ch_actual > 0 else actual_words
            for ch_idx in range(ch_actual):
                slots = []
                remaining = words_per_ch
                for slot_type in slots_per_ch:
                    slot_words = max(5, int(remaining / max(1, len(slots_per_ch) - len(slots))))
                    # Add some noise
                    slot_words = max(3, slot_words + rng.randint(-10, 10))
                    slots.append({
                        "slot_type": slot_type,
                        "word_count": slot_words,
                    })
                    remaining -= slot_words
                chapters.append({
                    "chapter_index": ch_idx,
                    "slots": slots,
                    "emotional_intensity": _clamp01(0.3 + 0.5 * (ch_idx / max(1, ch_actual - 1)) + rng.gauss(0, 0.1)),
                })

            plans.append({
                "_source_path": f"synthetic/{rt_id}_{sf_id}_{i}",
                "_synthetic": True,
                "runtime_format": rt_id,
                "structural_format": sf_id,
                "tier": tier,
                "chapters": chapters,
                "total_word_count": actual_words,
                "target_duration_minutes": duration_min,
            })

    return plans


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_word_adherence(
    plans: List[dict],
    runtime_formats: dict,
) -> Tuple[float, Dict[str, Any]]:
    """% of outputs within runtime's word_range; mean deviation for out-of-range."""
    if not plans:
        return 0.5, {"n": 0, "within_range": 0, "mean_deviation_pct": 0}
    within = 0
    deviations = []
    for p in plans:
        rt_id = p.get("runtime_format", "standard_book")
        rt = runtime_formats.get(rt_id, {})
        wmin, wmax = rt.get("word_range", [9000, 11000])
        actual = p.get("total_word_count", 0)
        if not actual:
            actual = sum(
                s.get("word_count", 0)
                for ch in p.get("chapters", [])
                for s in ch.get("slots", [])
            )
        if wmin <= actual <= wmax:
            within += 1
            deviations.append(0.0)
        else:
            mid = (wmin + wmax) / 2
            dev = abs(actual - mid) / mid if mid > 0 else 0
            deviations.append(dev)
    score = within / len(plans)
    mean_dev = sum(deviations) / len(deviations) if deviations else 0
    return _clamp01(score), {
        "n": len(plans),
        "within_range": within,
        "within_range_pct": round(score * 100, 1),
        "mean_deviation_pct": round(mean_dev * 100, 1),
    }


def score_chapter_adherence(
    plans: List[dict],
    registry: dict,
) -> Tuple[float, Dict[str, Any]]:
    """Exact match % and ±1 match % for chapter count."""
    if not plans:
        return 0.5, {"n": 0}
    runtime_formats = registry.get("runtime_formats") or {}
    structural_formats = registry.get("structural_formats") or {}
    exact = 0
    close = 0
    for p in plans:
        actual_ch = len(p.get("chapters", []))
        rt_id = p.get("runtime_format", "standard_book")
        rt = runtime_formats.get(rt_id, {})
        target_ch = rt.get("chapter_count_default", 12)
        if actual_ch == target_ch:
            exact += 1
            close += 1
        elif abs(actual_ch - target_ch) <= 1:
            close += 1
    exact_pct = exact / len(plans)
    close_pct = close / len(plans)
    # Weighted: 70% exact + 30% close
    score = 0.70 * exact_pct + 0.30 * close_pct
    return _clamp01(score), {
        "n": len(plans),
        "exact_match_pct": round(exact_pct * 100, 1),
        "plus_minus_1_pct": round(close_pct * 100, 1),
    }


def score_slot_budget_adherence(
    plans: List[dict],
    config: dict,
) -> Tuple[float, Dict[str, Any]]:
    """% of slots within word budget ceilings."""
    ceilings = config.get("duration_adherence_scorecard", {}).get("slot_word_ceilings", {})
    if not plans or not ceilings:
        return 0.5, {"n_slots": 0}
    total_slots = 0
    within_budget = 0
    for p in plans:
        tier = p.get("tier", "A")
        for ch in p.get("chapters", []):
            for s in ch.get("slots", []):
                slot_type = s.get("slot_type", "")
                wc = s.get("word_count", 0)
                ceiling_val = ceilings.get(slot_type)
                if ceiling_val is None:
                    # Unknown slot type — skip
                    continue
                total_slots += 1
                if isinstance(ceiling_val, dict):
                    # Tier-based (REFLECTION) or min/max (INTEGRATION)
                    if "min" in ceiling_val:
                        ceiling = ceiling_val.get("max", 200)
                    else:
                        ceiling = ceiling_val.get(tier, ceiling_val.get("A", 200))
                else:
                    ceiling = ceiling_val
                if wc <= ceiling:
                    within_budget += 1
    score = within_budget / total_slots if total_slots > 0 else 0.5
    return _clamp01(score), {
        "n_slots": total_slots,
        "within_budget": within_budget,
        "within_budget_pct": round(score * 100, 1),
    }


def score_duration_adherence(
    plans: List[dict],
    runtime_formats: dict,
    config: dict,
) -> Tuple[float, Dict[str, Any]]:
    """Estimated runtime vs target. Uses TTS WPM if no audio duration."""
    sc_cfg = config.get("duration_adherence_scorecard", {})
    wpm = sc_cfg.get("tts_wpm", 150)
    tolerance = sc_cfg.get("duration_tolerance_pct", 10) / 100.0
    if not plans:
        return 0.5, {"n": 0}
    within = 0
    for p in plans:
        rt_id = p.get("runtime_format", "standard_book")
        rt = runtime_formats.get(rt_id, {})
        target_min = rt.get("duration_minutes", 55)
        actual_words = p.get("total_word_count", 0)
        if not actual_words:
            actual_words = sum(
                s.get("word_count", 0)
                for ch in p.get("chapters", [])
                for s in ch.get("slots", [])
            )
        estimated_min = actual_words / wpm if wpm > 0 else 0
        if target_min > 0 and abs(estimated_min - target_min) / target_min <= tolerance:
            within += 1
    score = within / len(plans)
    return _clamp01(score), {
        "n": len(plans),
        "within_tolerance": within,
        "within_tolerance_pct": round(score * 100, 1),
        "wpm_used": wpm,
        "tolerance_pct": round(tolerance * 100, 1),
    }


def score_arc_fidelity(
    plans: List[dict],
) -> Tuple[float, Dict[str, Any]]:
    """Emotional curve correlation: actual vs expected rising arc."""
    if not plans:
        return 0.5, {"n": 0}
    correlations = []
    for p in plans:
        chapters = p.get("chapters", [])
        if len(chapters) < 3:
            correlations.append(0.5)
            continue
        actual = [ch.get("emotional_intensity", 0.5) for ch in chapters]
        n = len(actual)
        # Expected: linear rise from 0.3 to 0.8 (standard arc shape)
        expected = [0.3 + 0.5 * (i / (n - 1)) for i in range(n)]
        # Pearson correlation
        mean_a = sum(actual) / n
        mean_e = sum(expected) / n
        num = sum((a - mean_a) * (e - mean_e) for a, e in zip(actual, expected))
        den_a = math.sqrt(sum((a - mean_a) ** 2 for a in actual))
        den_e = math.sqrt(sum((e - mean_e) ** 2 for e in expected))
        if den_a > 0 and den_e > 0:
            corr = num / (den_a * den_e)
        else:
            corr = 0.0
        # Map correlation [-1, 1] to score [0, 1]
        correlations.append(_clamp01((corr + 1) / 2))
    avg = sum(correlations) / len(correlations)
    return _clamp01(avg), {
        "n": len(plans),
        "mean_correlation_score": round(avg, 4),
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def grade_from_score(score: float, grade_thresholds: dict) -> str:
    for g in ["A", "B", "C", "D"]:
        if score >= grade_thresholds.get(g, 0):
            return g
    return "F"


def build_per_format_summary(
    plans: List[dict],
    runtime_formats: dict,
    config: dict,
) -> List[dict]:
    """One row per runtime_format."""
    by_rt: Dict[str, List[dict]] = {}
    for p in plans:
        rt = p.get("runtime_format", "unknown")
        by_rt.setdefault(rt, []).append(p)

    grades_cfg = config.get("duration_adherence_scorecard", {}).get("grades", {})
    rows = []
    for rt_id in sorted(by_rt.keys()):
        rt_plans = by_rt[rt_id]
        rt = runtime_formats.get(rt_id, {})
        ws, _ = score_word_adherence(rt_plans, runtime_formats)
        ds, _ = score_duration_adherence(rt_plans, runtime_formats, config)
        cs, _ = score_chapter_adherence(rt_plans, {"runtime_formats": runtime_formats})
        ss, _ = score_slot_budget_adherence(rt_plans, config)
        af, _ = score_arc_fidelity(rt_plans)
        weights = config.get("duration_adherence_scorecard", {}).get("weights", {})
        composite = (
            weights.get("word_adherence", 0.30) * ws
            + weights.get("duration_adherence", 0.25) * ds
            + weights.get("slot_budget_adherence", 0.20) * ss
            + weights.get("chapter_adherence", 0.15) * cs
            + weights.get("arc_fidelity", 0.10) * af
        )
        rows.append({
            "format_id": rt_id,
            "target_duration_min": rt.get("duration_minutes"),
            "target_word_range": rt.get("word_range"),
            "n_produced": len(rt_plans),
            "word_adherence_pct": round(ws * 100, 1),
            "duration_adherence_pct": round(ds * 100, 1),
            "chapter_adherence_pct": round(cs * 100, 1),
            "slot_budget_adherence_pct": round(ss * 100, 1),
            "arc_fidelity_score": round(af, 4),
            "composite": round(composite, 4),
            "overall_grade": grade_from_score(composite, grades_cfg),
        })
    return rows


def build_structural_format_breakdown(
    plans: List[dict],
    structural_formats: dict,
    config: dict,
) -> List[dict]:
    """One row per structural format."""
    by_sf: Dict[str, List[dict]] = {}
    for p in plans:
        sf = p.get("structural_format", "unknown")
        by_sf.setdefault(sf, []).append(p)

    rows = []
    for sf_id in sorted(by_sf.keys()):
        sf_plans = by_sf[sf_id]
        sf = structural_formats.get(sf_id, {})
        ch_range = sf.get("chapter_range", [0, 0])
        # Chapter match
        exact = sum(
            1 for p in sf_plans
            if ch_range[0] <= len(p.get("chapters", [])) <= ch_range[1]
        )
        ch_pct = exact / len(sf_plans) if sf_plans else 0
        ss, _ = score_slot_budget_adherence(sf_plans, config)
        af, _ = score_arc_fidelity(sf_plans)
        rows.append({
            "format_id": sf_id,
            "chapter_target": ch_range,
            "n_produced": len(sf_plans),
            "chapter_match_pct": round(ch_pct * 100, 1),
            "slot_budget_pct": round(ss * 100, 1),
            "emotional_curve_fidelity": round(af, 4),
        })
    return rows


def build_worst_offenders(
    plans: List[dict],
    runtime_formats: dict,
    config: dict,
    count: int = 10,
) -> List[dict]:
    """Top N outputs with highest deviation from target."""
    scored = []
    for p in plans:
        rt_id = p.get("runtime_format", "standard_book")
        rt = runtime_formats.get(rt_id, {})
        wmin, wmax = rt.get("word_range", [9000, 11000])
        actual = p.get("total_word_count", 0)
        if not actual:
            actual = sum(
                s.get("word_count", 0)
                for ch in p.get("chapters", [])
                for s in ch.get("slots", [])
            )
        mid = (wmin + wmax) / 2
        word_dev = abs(actual - mid) / mid if mid > 0 else 0

        target_min = rt.get("duration_minutes", 55)
        wpm = config.get("duration_adherence_scorecard", {}).get("tts_wpm", 150)
        est_min = actual / wpm if wpm > 0 else 0
        dur_dev = abs(est_min - target_min) / target_min if target_min > 0 else 0

        worst_dim = "word_count" if word_dev >= dur_dev else "duration"
        worst_val = max(word_dev, dur_dev)

        scored.append({
            "source": p.get("_source_path", "unknown"),
            "runtime_format": rt_id,
            "structural_format": p.get("structural_format", "unknown"),
            "actual_words": actual,
            "target_word_range": [wmin, wmax],
            "estimated_duration_min": round(est_min, 1),
            "target_duration_min": target_min,
            "worst_dimension": worst_dim,
            "deviation_pct": round(worst_val * 100, 1),
        })
    scored.sort(key=lambda x: x["deviation_pct"], reverse=True)
    return scored[:count]


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------

def run(
    config: dict,
    registry: dict,
    plans: List[dict],
    report_date: str,
) -> dict:
    """Compute full scorecard from plans."""
    runtime_formats = registry.get("runtime_formats") or {}
    structural_formats = registry.get("structural_formats") or {}
    sc_cfg = config.get("duration_adherence_scorecard", {})
    weights = sc_cfg.get("weights", {})
    grades_cfg = sc_cfg.get("grades", {})

    ws, w_detail = score_word_adherence(plans, runtime_formats)
    ds, d_detail = score_duration_adherence(plans, runtime_formats, config)
    ss, s_detail = score_slot_budget_adherence(plans, config)
    cs, c_detail = score_chapter_adherence(plans, registry)
    af, a_detail = score_arc_fidelity(plans)

    composite = (
        weights.get("word_adherence", 0.30) * ws
        + weights.get("duration_adherence", 0.25) * ds
        + weights.get("slot_budget_adherence", 0.20) * ss
        + weights.get("chapter_adherence", 0.15) * cs
        + weights.get("arc_fidelity", 0.10) * af
    )
    composite = round(_clamp01(composite), 4)
    grade = grade_from_score(composite, grades_cfg)

    per_format = build_per_format_summary(plans, runtime_formats, config)
    structural = build_structural_format_breakdown(plans, structural_formats, config)
    offenders_count = sc_cfg.get("worst_offenders_count", 10)
    worst = build_worst_offenders(plans, runtime_formats, config, offenders_count)

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_date": report_date,
        "data_source": "synthetic" if any(p.get("_synthetic") for p in plans) else "production",
        "n_outputs_scored": len(plans),
        "components": {
            "word_adherence": {"score": round(ws, 4), **w_detail},
            "duration_adherence": {"score": round(ds, 4), **d_detail},
            "slot_budget_adherence": {"score": round(ss, 4), **s_detail},
            "chapter_adherence": {"score": round(cs, 4), **c_detail},
            "arc_fidelity": {"score": round(af, 4), **a_detail},
        },
        "composite_score": composite,
        "overall_grade": grade,
        "per_runtime_format": per_format,
        "per_structural_format": structural,
        "worst_offenders": worst,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Duration Adherence Scorecard")
    ap.add_argument("--report-date", default=None, help="YYYY-MM-DD; default today UTC")
    ap.add_argument("--config", type=Path, default=None)
    ap.add_argument("--registry", type=Path, default=None)
    ap.add_argument("--artifacts-dir", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--runtime-format", default=None, help="Filter to one runtime format")
    ap.add_argument("--synthetic", action="store_true", help="Generate synthetic data from registry targets")
    ap.add_argument("--md", action="store_true", help="Also write .md summary")
    args = ap.parse_args()

    repo_root = REPO_ROOT
    report_date = args.report_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    config = _load_yaml(args.config or repo_root / "config" / "duration_scorecard.yaml")
    registry = _load_yaml(args.registry or repo_root / "config" / "format_selection" / "format_registry.yaml")
    artifacts_dir = args.artifacts_dir or repo_root / "artifacts"

    if args.synthetic:
        plans = generate_synthetic_outputs(registry)
    else:
        plans = discover_plan_outputs(artifacts_dir)

    if args.runtime_format:
        plans = [p for p in plans if p.get("runtime_format") == args.runtime_format]

    if not plans:
        print("No outputs found to score. Use --synthetic for infrastructure validation.")
        return 0

    result = run(config, registry, plans, report_date)

    out_dir = Path(config.get("duration_adherence_scorecard", {}).get("output_dir", "artifacts/ops"))
    if not out_dir.is_absolute():
        out_dir = repo_root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output or out_dir / f"duration_scorecard_{report_date}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if args.md:
        md_path = out_path.with_suffix(".md")
        lines = [
            f"# Duration Adherence Scorecard — {report_date}",
            "",
            f"**Composite:** {result['composite_score']}  **Grade:** {result['overall_grade']}  **Source:** {result['data_source']}  **N:** {result['n_outputs_scored']}",
            "",
            "## Components",
        ]
        for name, detail in result["components"].items():
            lines.append(f"- {name}: {detail['score']}")
        lines.extend(["", "## Per-Runtime Format"])
        for row in result.get("per_runtime_format", []):
            lines.append(f"- {row['format_id']}: grade={row['overall_grade']} composite={row['composite']} n={row['n_produced']}")
        lines.extend(["", f"See JSON: {out_path.name}"])
        md_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Written: {md_path}")

    print(f"Written: {out_path}")
    print(f"Composite: {result['composite_score']}  Grade: {result['overall_grade']}  N: {result['n_outputs_scored']}")
    return 0 if result["overall_grade"] in ("A", "B", "C") else 1


if __name__ == "__main__":
    sys.exit(main())
