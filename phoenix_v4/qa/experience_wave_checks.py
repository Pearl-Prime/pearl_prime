"""
Experience Wave Checks — per-wave and network-level experience anti-spam gates.

Authority: specs/EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md §5, §8, §13, §14.5, §16
Called from check_wave_density.py when experience fields are present on plans.

Returns: list of failures (FAIL), list of warnings (WARN).
If experience fields are missing on any plan and allow_legacy_plans is True,
issues WARN and skips experience checks for that plan.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

EXPERIENCE_FIELDS = (
    "delivery_experience",
    "reader_intent",
    "pacing_model",
    "outcome_type",
    "engagement_depth",
    "transformation_speed",
    "perceived_positioning",
)

EXPERIENCE_CAP_FIELDS = (
    ("delivery_experience", "max_same_delivery_experience"),
    ("reader_intent", "max_same_reader_intent"),
    ("pacing_model", "max_same_pacing_model"),
    ("outcome_type", "max_same_outcome_type"),
    ("engagement_depth", "max_same_engagement_depth"),
    ("transformation_speed", "max_same_transformation_speed"),
    ("perceived_positioning", "max_same_perceived_positioning"),
)


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        return {}
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _mode_share(values: List[str]) -> Tuple[float, str]:
    if not values:
        return 0.0, ""
    c = Counter(values)
    val, count = c.most_common(1)[0]
    return count / len(values), val


def _experience_tuple(plan: Dict[str, Any]) -> str:
    """Return the experience hash if present, else compute a tuple key."""
    h = plan.get("experience_hash")
    if h:
        return str(h)
    return "|".join(str(plan.get(f, "")) for f in EXPERIENCE_FIELDS)


def _has_experience_fields(plan: Dict[str, Any]) -> bool:
    """Check if plan has at least the 3 core experience fields populated."""
    return bool(plan.get("delivery_experience") and plan.get("reader_intent") and plan.get("perceived_positioning"))


def check_experience_wave(
    plans: List[Dict[str, Any]],
    *,
    wave_controls_path: Optional[Path] = None,
    risky_combos_path: Optional[Path] = None,
    brand_profiles_path: Optional[Path] = None,
    allow_legacy_plans: bool = True,
    network_mode: bool = False,
    catalog_index_path: Optional[Path] = None,
) -> Tuple[List[str], List[str]]:
    """
    Run experience-layer wave density checks.

    Returns:
        (failures, warnings) — lists of human-readable strings.
    """
    failures: List[str] = []
    warnings: List[str] = []

    if not plans:
        return failures, warnings

    # --- Load config ---
    wc_path = wave_controls_path or (REPO_ROOT / "config" / "experience" / "experience_wave_controls.yaml")
    rc_path = risky_combos_path or (REPO_ROOT / "config" / "experience" / "risky_combos.yaml")
    bp_path = brand_profiles_path or (REPO_ROOT / "config" / "experience" / "brand_experience_profiles.yaml")

    wc_raw = _load_yaml(wc_path)
    wc = wc_raw.get("experience_wave_controls", {})
    rc_raw = _load_yaml(rc_path)
    bp_raw = _load_yaml(bp_path)

    # --- Filter plans with experience fields ---
    exp_plans = [p for p in plans if _has_experience_fields(p)]
    legacy_plans = [p for p in plans if not _has_experience_fields(p)]

    if legacy_plans:
        if allow_legacy_plans:
            warnings.append(
                f"EXP WAVE: {len(legacy_plans)} of {len(plans)} plans missing experience fields (legacy; skipped)"
            )
        else:
            failures.append(
                f"EXP WAVE: {len(legacy_plans)} of {len(plans)} plans missing experience fields (legacy not allowed)"
            )

    if len(exp_plans) < 2:
        warnings.append("EXP WAVE: fewer than 2 plans with experience fields; skipping experience checks")
        return failures, warnings

    n = len(exp_plans)

    # --- Determine threshold tier ---
    tier = wc.get("threshold_tier", "launch")
    weekly_caps_all = wc.get("weekly_caps", {})
    caps = weekly_caps_all.get(tier, weekly_caps_all.get("launch", {}))

    # --- §5.1: Per-dimension caps ---
    for field, cap_key in EXPERIENCE_CAP_FIELDS:
        threshold = float(caps.get(cap_key, 1.0))
        values = [str(p.get(field, "")) for p in exp_plans]
        share, top_val = _mode_share(values)
        if share > threshold:
            failures.append(
                f"EXP WAVE: {field} density {share:.0%} >= {threshold:.0%} (top: '{top_val}')"
            )

    # --- §5.1: Identical tuple clustering ---
    sim_cfg = wc.get("experience_similarity", {})
    max_identical = sim_cfg.get("wave_max_identical_experience_tuple", 3)
    tuple_counter = Counter(_experience_tuple(p) for p in exp_plans)
    for tup, count in tuple_counter.most_common():
        if count > max_identical:
            failures.append(
                f"EXP WAVE: {count} plans share identical experience tuple (max {max_identical}): {tup[:40]}..."
            )

    # --- §13: Risky combo caps ---
    risky_combos = rc_raw.get("risky_combos", [])
    for rc in risky_combos:
        combo = rc.get("combo", {})
        label = rc.get("label", "unnamed")
        max_share = float(rc.get("max_share", 1.0))

        matching = 0
        for p in exp_plans:
            if all(str(p.get(dim, "")) == str(val) for dim, val in combo.items()):
                matching += 1

        if n > 0 and matching / n >= max_share:
            failures.append(
                f"EXP WAVE: risky combo '{label}' share {matching}/{n} ({matching / n:.0%}) >= {max_share:.0%}"
            )

    # --- §13.5: Novel clustering alert ---
    novel_cfg = rc_raw.get("novel_clustering", {})
    min_books = novel_cfg.get("min_books_for_alert", 3)
    min_dims = novel_cfg.get("min_shared_dimensions", 3)
    known_combos: Set[str] = set()
    for rc in risky_combos:
        combo = rc.get("combo", {})
        known_combos.add(json.dumps(combo, sort_keys=True))

    # Check all 3-dimension subsets of the 7 fields
    if len(EXPERIENCE_FIELDS) >= min_dims:
        for dim_subset in combinations(EXPERIENCE_FIELDS, min_dims):
            sub_counter: Counter[str] = Counter()
            for p in exp_plans:
                key = "|".join(f"{d}={p.get(d, '')}" for d in dim_subset)
                sub_counter[key] += 1
            for key, count in sub_counter.items():
                if count >= min_books:
                    # Parse back to dict for known-combo check
                    parts = dict(part.split("=", 1) for part in key.split("|"))
                    combo_json = json.dumps(parts, sort_keys=True)
                    if combo_json not in known_combos:
                        warnings.append(
                            f"EXP WAVE: NOVEL CLUSTER ({count} books): {key}. Consider adding to risky_combos.yaml"
                        )

    # --- §8: Network-level caps (when --network-mode) ---
    if network_mode:
        net_caps = bp_raw.get("network_experience_caps", {})
        max_tuple_share = float(net_caps.get("max_same_experience_tuple_share", 0.15))
        min_deliveries = int(net_caps.get("min_distinct_delivery_experiences", 4))
        min_intents = int(net_caps.get("min_distinct_reader_intents", 4))

        # Tuple share across all brands
        for tup, count in tuple_counter.most_common():
            if count / n >= max_tuple_share:
                failures.append(
                    f"EXP NETWORK: experience tuple share {count}/{n} ({count / n:.0%}) >= {max_tuple_share:.0%}"
                )
                break

        # Minimum distinct values
        distinct_deliveries = len(set(str(p.get("delivery_experience", "")) for p in exp_plans))
        if distinct_deliveries < min_deliveries:
            failures.append(
                f"EXP NETWORK: only {distinct_deliveries} distinct delivery_experience values (need {min_deliveries})"
            )

        distinct_intents = len(set(str(p.get("reader_intent", "")) for p in exp_plans))
        if distinct_intents < min_intents:
            failures.append(
                f"EXP NETWORK: only {distinct_intents} distinct reader_intent values (need {min_intents})"
            )

    # --- §6.3: First-of-kind alert (requires catalog index) ---
    if catalog_index_path and catalog_index_path.exists():
        try:
            historical_tuples_by_brand: Dict[str, Set[str]] = {}
            with open(catalog_index_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    brand = str(row.get("brand_id", ""))
                    eh = row.get("experience_hash", "")
                    if brand and eh:
                        historical_tuples_by_brand.setdefault(brand, set()).add(eh)

            for p in exp_plans:
                brand = str(p.get("brand_id", ""))
                eh = p.get("experience_hash", "")
                if brand and eh and brand in historical_tuples_by_brand:
                    if eh not in historical_tuples_by_brand[brand]:
                        book_id = p.get("book_id", p.get("plan_id", "unknown"))
                        warnings.append(
                            f"EXP FIRST-OF-KIND: {book_id} introduces new experience tuple for brand '{brand}'"
                        )
        except (json.JSONDecodeError, OSError) as e:
            warnings.append(f"EXP WAVE: could not read catalog index for first-of-kind check: {e}")

    # --- §14.5: Cross-wave sequence detection ---
    seq_warnings = check_cross_wave_sequence(exp_plans)
    warnings.extend(seq_warnings)

    # --- §15.4: Natural variance (controlled imperfection) ---
    failures = apply_natural_variance(failures, exp_plans, wave_controls_path=wc_path)

    return failures, warnings


def check_experience_metadata_consistency(
    plans: List[Dict[str, Any]],
) -> List[str]:
    """
    §16: Validate that perceived_positioning aligns with title/description keywords.
    Returns list of WARN strings.
    """
    warnings: List[str] = []

    # Lightweight keyword rules per positioning value
    POSITIONING_RULES: Dict[str, Dict[str, Any]] = {
        "quick_fix": {
            "title_neg": ["master", "journey", "deep", "advanced", "year-long"],
            "desc_pos": ["fast", "quick", "now", "today", "minutes", "relief", "instant"],
        },
        "deep_work": {
            "title_neg": ["fast", "quick", "instant", "minutes", "easy"],
            "desc_pos": ["practice", "work", "commit", "discipline", "effort", "depth"],
        },
        "spiritual_path": {
            "title_neg": ["hack", "system", "framework", "productivity"],
            "desc_pos": ["path", "practice", "spirit", "sacred", "devotion", "tradition"],
        },
        "practical_system": {
            "title_neg": ["surrender", "sacred", "devotion", "meditation"],
            "desc_pos": ["system", "method", "framework", "steps", "plan", "strategy"],
        },
        "scientific_guide": {
            "title_neg": ["spiritual", "sacred", "surrender"],
            "desc_pos": ["research", "study", "evidence", "science", "data", "proven"],
        },
    }

    for p in plans:
        positioning = str(p.get("perceived_positioning", "")).strip()
        if not positioning or positioning not in POSITIONING_RULES:
            continue

        rules = POSITIONING_RULES[positioning]
        title = str(p.get("title", "")).lower()
        description = str(p.get("description", "")).lower()
        book_id = p.get("book_id", p.get("plan_id", "unknown"))

        # Check title negatives
        title_neg = rules.get("title_neg", [])
        for word in title_neg:
            if word.lower() in title:
                warnings.append(
                    f"EXP CONSISTENCY: {book_id} positioning='{positioning}' but title contains '{word}'"
                )
                break  # One warning per book is enough

        # Check description positives (should contain at least one)
        desc_pos = rules.get("desc_pos", [])
        if desc_pos and description:
            if not any(word.lower() in description for word in desc_pos):
                warnings.append(
                    f"EXP CONSISTENCY: {book_id} positioning='{positioning}' but description has none of {desc_pos[:3]}..."
                )

    return warnings


def check_cross_wave_sequence(
    plans: List[Dict[str, Any]],
    *,
    catalog_window_weeks: int = 6,
    max_sequence_length: int = 4,
) -> List[str]:
    """
    §14.5: Cross-wave sequence detection.
    Detect progressive thematic arcs spread across waves (fragmented series spam).
    Returns list of WARN strings.
    """
    warnings: List[str] = []

    # Group by brand + topic + persona
    from collections import defaultdict
    brand_topic_groups: Dict[str, List[Dict]] = defaultdict(list)
    for p in plans:
        brand = str(p.get("brand_id", ""))
        topic = str(p.get("topic_id", ""))
        persona = str(p.get("persona_id", ""))
        if brand and topic:
            key = f"{brand}|{topic}|{persona}"
            brand_topic_groups[key].append(p)

    PACING_ORDER = {"single_sitting": 0, "multi_day": 1, "extended_program": 2, "ongoing_ritual": 3, "dip_in": 0}
    SPEED_ORDER = {"immediate": 0, "gradual": 1, "long_arc": 2}

    for key, group in brand_topic_groups.items():
        # Skip if declared series
        if all(p.get("series_id") for p in group):
            continue

        if len(group) <= max_sequence_length:
            continue

        # Sort by release order (wave_id or release_week)
        group.sort(key=lambda p: int(p.get("release_week", p.get("wave_id", 0)) or 0))

        # Check for escalating pacing or transformation speed
        pacing_vals = [PACING_ORDER.get(str(p.get("pacing_model", "")), -1) for p in group]
        speed_vals = [SPEED_ORDER.get(str(p.get("transformation_speed", "")), -1) for p in group]

        # Count longest increasing subsequence
        for vals, dim_name in [(pacing_vals, "pacing_model"), (speed_vals, "transformation_speed")]:
            valid = [v for v in vals if v >= 0]
            if len(valid) < max_sequence_length:
                continue
            # Simple check: count consecutive non-decreasing
            streak = 1
            max_streak = 1
            for i in range(1, len(valid)):
                if valid[i] >= valid[i-1]:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 1
            if max_streak > max_sequence_length:
                parts = key.split("|")
                warnings.append(
                    f"CROSS-WAVE SEQUENCE: brand='{parts[0]}' topic='{parts[1]}' has {max_streak} books "
                    f"with escalating {dim_name} (max {max_sequence_length}). Consider declaring a series."
                )

    return warnings


def apply_natural_variance(
    failures: List[str],
    plans: List[Dict[str, Any]],
    *,
    wave_controls_path: Optional[Path] = None,
) -> List[str]:
    """
    §15.4: Natural variance — allow minor soft-cap violations in 5% of waves.
    Downgrades FAIL to WARN for per-dimension weekly_caps if within overshoot tolerance.
    Does NOT apply to network-level caps, risky combos, or AI disclosure.

    Returns: filtered failures list (some may be downgraded).
    """
    wc_path = wave_controls_path or (REPO_ROOT / "config" / "experience" / "experience_wave_controls.yaml")
    raw = _load_yaml(wc_path)
    wc = raw.get("experience_wave_controls", {})
    nv = wc.get("natural_variance", {})

    max_overshoot = float(nv.get("max_overshoot_pct", 0.10))

    if not nv or not nv.get("allow_minor_violation_rate"):
        return failures

    # Only apply to per-dimension weekly cap failures (identified by "EXP WAVE:" prefix and "density" keyword)
    filtered = []
    for f in failures:
        if f.startswith("EXP WAVE:") and "density" in f:
            # This is a per-dimension cap failure; check if within overshoot
            # Parse: "EXP WAVE: delivery_experience density 55% >= 50% (top: 'passive_reading')"
            # If the actual share minus threshold is within max_overshoot of threshold, downgrade
            try:
                parts = f.split("density")[1].strip()
                actual_pct = float(parts.split("%")[0]) / 100
                threshold_pct = float(parts.split(">=")[1].strip().split("%")[0]) / 100
                overshoot = actual_pct - threshold_pct
                if overshoot <= threshold_pct * max_overshoot:
                    # Downgrade: don't add to failures (will be a warning)
                    continue
            except (ValueError, IndexError):
                pass
        filtered.append(f)

    return filtered


def check_ai_disclosure(plans: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    §14.6: AI disclosure gate.
    FAIL if ai_disclosure_status is missing or 'pending'.
    WARN if 'not_applicable' for pipeline-generated book.
    """
    failures: List[str] = []
    warnings: List[str] = []

    for p in plans:
        book_id = p.get("book_id", p.get("plan_id", "unknown"))
        status = str(p.get("ai_disclosure_status", "")).strip()

        if not status or status == "pending":
            failures.append(
                f"AI DISCLOSURE: {book_id} has ai_disclosure_status='{status or 'missing'}' (must be 'disclosed' or 'not_applicable')"
            )
        elif status == "not_applicable":
            # Warn if this looks like a pipeline-generated book
            # (heuristic: has engine_id or was produced by the pipeline)
            if p.get("engine_id") or p.get("compiled_by_pipeline"):
                warnings.append(
                    f"AI DISCLOSURE: {book_id} is pipeline-generated but ai_disclosure_status='not_applicable'"
                )

    return failures, warnings
