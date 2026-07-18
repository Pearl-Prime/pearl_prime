#!/usr/bin/env python3
"""
CDIS duration planner — spec §7. Input: brand, platform, locale, format, persona, intent.
Output: duration_plan.json with scoring and reasoning chain.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration._config import (  # noqa: E402
    config_snapshot_hash,
    load_duration_configs,
    should_skip_output,
    write_atomically,
)

INTENTS = ["discovery", "therapeutic", "engagement", "deep_engagement", "conversion"]


def _to_seconds(unit: str, value: float) -> float:
    u = (unit or "seconds").lower()
    if u == "seconds":
        return float(value)
    if u == "minutes":
        return float(value) * 60.0
    if u == "pages":
        return float(value) * 120.0
    if u == "panels":
        return float(value) * 45.0
    return float(value)


def _get_registry_row(cfgs: dict, fmt: str, intent: str) -> dict | None:
    reg = cfgs.get("duration_registry") or {}
    fmts = reg.get("formats") or {}
    if fmt not in fmts:
        return None
    block = fmts[fmt]
    return block.get(intent) or block.get("discovery")


def _platform_bounds(cfgs: dict, platform: str) -> dict:
    plat = (cfgs.get("platform_duration_profiles") or {}).get("platforms") or {}
    return plat.get(platform) or plat.get(platform.lower()) or {}


def _persona(cfgs: dict, persona: str) -> dict:
    pers = (cfgs.get("persona_duration_profiles") or {}).get("personas") or {}
    return pers.get(persona) or pers.get(persona.lower()) or {}


def _locale_mod(cfgs: dict, locale: str) -> dict:
    mods = (cfgs.get("persona_duration_profiles") or {}).get("locale_modifiers") or {}
    return mods.get(locale) or mods.get(locale.replace("_", "-")) or mods.get("en-US") or {"audio_multiplier": 1.0, "video_multiplier": 1.0, "reading_multiplier": 1.0}


def _therapeutic_minutes_for_modality(cfgs: dict, modality: str | None) -> float | None:
    if not modality:
        return None
    mods = (cfgs.get("therapeutic_dose_rules") or {}).get("modalities") or {}
    m = mods.get(modality) or mods.get(modality.replace("-", "_"))
    if not m:
        return None
    if m.get("minimum_effective_dose_minutes") is not None:
        return float(m["minimum_effective_dose_minutes"])
    sec = m.get("minimum_effective_dose_seconds")
    if sec is not None:
        return float(sec) / 60.0
    return None


def _fmt_looks_video(fmt: str) -> bool:
    return fmt.startswith("video") or fmt.startswith("podcast") or fmt.startswith("meditation")


def _fmt_looks_audio_book(fmt: str) -> bool:
    return fmt.startswith("audiobook")


def _fmt_looks_ebook(fmt: str) -> bool:
    return fmt.startswith("ebook")


def _fmt_looks_manga(fmt: str) -> bool:
    return fmt.startswith("manga")


def plan(
    cfgs: dict,
    *,
    brand_id: str,
    platform: str,
    locale: str,
    format_key: str,
    persona: str,
    intent: str,
    modality: str | None,
    micro_dose_protocol: bool,
) -> dict:
    reasoning: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    if intent not in INTENTS:
        intent = "discovery"
        warnings.append(f"unknown intent normalized to discovery")

    row = _get_registry_row(cfgs, format_key, intent)
    if not row:
        row = _get_registry_row(cfgs, format_key, "discovery")
    if not row:
        raise ValueError(f"unknown format: {format_key}")

    unit = row["unit"]
    vmin = float(row["min"])
    vopt = float(row["optimal"])
    vmax = float(row["max"])
    dose_flag = bool(row.get("therapeutic_dose_compliant"))
    algo_fit = float(row.get("platform_algo_fit", 0.8))

    plat = _platform_bounds(cfgs, platform)
    pers = _persona(cfgs, persona)
    loc = _locale_mod(cfgs, locale)

    # --- Step 2: platform hard constraints (time-based platforms)
    recommended = vopt
    if plat.get("hard_max_seconds") is not None and unit == "seconds":
        hmax = float(plat["hard_max_seconds"])
        hmin = float(plat["hard_min_seconds"] or 0)
        rec_sec = _to_seconds(unit, recommended)
        if rec_sec > hmax:
            warnings.append(f"clamped to platform hard_max {hmax}s")
            recommended = hmax / 1.0 if unit == "seconds" else recommended
            if unit == "seconds":
                recommended = min(recommended, hmax)
        if rec_sec < hmin and unit == "seconds":
            recommended = max(recommended, hmin)
            warnings.append(f"raised to platform hard_min {hmin}s")

    # Persona attention (session minutes) with locale multiplier
    sess_min = float(pers.get("preferred_session_length_min") or 5)
    sess_max = float(pers.get("preferred_session_length_max") or 60)
    if _fmt_looks_video(format_key):
        mult = float(loc.get("video_multiplier", 1.0))
    elif _fmt_looks_audio_book(format_key) or format_key.startswith("podcast"):
        mult = float(loc.get("audio_multiplier", 1.0))
    elif _fmt_looks_ebook(format_key):
        mult = float(loc.get("reading_multiplier", 1.0))
    else:
        mult = 1.0
    budget_min = sess_min * mult
    budget_max = sess_max * mult

    rec_sec_equiv = _to_seconds(unit, recommended)

    if budget_max > 0 and intent in ("discovery", "engagement", "conversion"):
        cap_sec = budget_max * 60.0 * 1.0
        if rec_sec_equiv > cap_sec * 1.2 and unit == "seconds":
            recommended = min(recommended, min(vmax, cap_sec))
            rec_sec_equiv = _to_seconds(unit, recommended)
            reasoning.append(f"persona session cap ~{budget_max} min (locale-adjusted)")

    # Therapeutic minimum (§6)
    tmin_min = _therapeutic_minutes_for_modality(cfgs, modality)
    if tmin_min and intent in ("therapeutic", "deep_engagement") and not micro_dose_protocol:
        need_sec = tmin_min * 60
        if rec_sec_equiv + 1 < need_sec and modality not in ("micro_mindfulness",):
            if _fmt_looks_video(format_key) and plat.get("hard_max_seconds") and float(plat["hard_max_seconds"]) < need_sec:
                blockers.append("therapeutic_minimum_exceeds_platform_cap_suggest_micro_dose")
                warnings.append("platform vs therapeutic conflict")
            else:
                if unit == "seconds":
                    recommended = max(recommended, need_sec)
                    rec_sec_equiv = _to_seconds(unit, recommended)
                reasoning.append(f"therapeutic floor from modality {modality}: {tmin_min} min")

    if micro_dose_protocol and intent == "therapeutic" and modality in ("breathing", "micro_mindfulness", None):
        warnings.append("micro_dose_protocol: conditional therapeutic compliance")
        dose_flag = True

    recommended = max(vmin, min(vmax, recommended))
    if unit == "seconds" and plat.get("hard_max_seconds") is not None:
        recommended = min(recommended, float(plat["hard_max_seconds"]))
        recommended = max(recommended, float(plat.get("hard_min_seconds") or 0))
    rec_sec_equiv = _to_seconds(unit, recommended)

    platform_compliant = True
    if unit == "seconds" and plat.get("hard_max_seconds") is not None:
        platform_compliant = rec_sec_equiv <= float(plat["hard_max_seconds"]) + 0.5

    # Scores §7.2
    span = max(vmax - vmin, 1e-6)
    t_score = 1.0 - abs(recommended - vopt) / span
    t_score = max(0.0, min(1.0, t_score))
    if dose_flag:
        t_score = min(1.0, t_score + 0.1)

    # platform fit: sweet spot seconds if available
    p_score = algo_fit
    if plat.get("sweet_spot_min_seconds") and unit == "seconds":
        lo, hi = float(plat["sweet_spot_min_seconds"]), float(plat["sweet_spot_max_seconds"] or plat["sweet_spot_min_seconds"])
        mid = (lo + hi) / 2
        if lo <= rec_sec_equiv <= hi:
            p_score = min(1.0, algo_fit + 0.05)
        else:
            p_score = max(0.2, algo_fit - min(1.0, abs(rec_sec_equiv - mid) / (hi - lo + 1)))

    sess_mid = (budget_min + budget_max) / 2
    rec_min = rec_sec_equiv / 60.0
    a_score = 1.0 - min(1.0, abs(rec_min - sess_mid) / max(sess_mid, 1))
    a_score = max(0.15, a_score)

    duration_fit = 0.40 * t_score + 0.35 * p_score + 0.25 * a_score

    ser = cfgs.get("serialization_cadence") or {}

    out = {
        "brand_id": brand_id,
        "platform": platform,
        "locale": locale,
        "format": format_key,
        "persona": persona,
        "intent": intent,
        "modality": modality,
        "micro_dose_protocol": micro_dose_protocol,
        "registry_unit": unit,
        "recommended_value": round(recommended, 3),
        "recommended_duration_sec": None,
        "recommended_page_count": None,
        "recommended_panel_count": None,
        "therapeutic_dose_compliant": dose_flag,
        "duration_fit_score": round(duration_fit, 4),
        "scores": {"therapeutic_fit": round(t_score, 4), "platform_fit": round(p_score, 4), "attention_fit": round(a_score, 4)},
        "platform_compliant": platform_compliant and not any("platform_cap" in b for b in blockers),
        "persona_budget_fit": rec_min <= budget_max * 1.2,
        "warnings": warnings,
        "blockers": blockers,
        "reasoning_chain": reasoning,
        "serialization_ref": {k: ser.get(k) for k in ["cadence_by_platform", "episode_counts"] if ser.get(k)},
        "config_hash": config_snapshot_hash(),
    }

    if unit == "seconds":
        out["recommended_duration_sec"] = round(recommended, 1)
    elif unit == "minutes":
        out["recommended_duration_sec"] = round(recommended * 60.0, 1)
    elif unit == "pages":
        out["recommended_page_count"] = int(round(recommended))
    elif unit == "panels":
        out["recommended_panel_count"] = int(round(recommended))

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="CDIS plan_duration — single combination")
    ap.add_argument("--brand", default="stillness_press", help="brand_id")
    ap.add_argument("--platform", default="youtube", help="platform_id")
    ap.add_argument("--locale", default="en-US")
    ap.add_argument("--format", default="video_short", dest="format_key", help="registry format key")
    ap.add_argument("--persona", default="millennial_women_professionals")
    ap.add_argument("--intent", default="therapeutic")
    ap.add_argument("--modality", default=None, help="e.g. breathing, visualization")
    ap.add_argument("--micro-dose-protocol", action="store_true")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    cfgs = load_duration_configs()
    out_path = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out_path, ["duration_fit_score", "format", "config_hash"], args.force, h):
        print(f"Skip: {out_path}")
        return 0
    try:
        doc = plan(
            cfgs,
            brand_id=args.brand,
            platform=args.platform,
            locale=args.locale,
            format_key=args.format_key,
            persona=args.persona,
            intent=args.intent,
            modality=args.modality,
            micro_dose_protocol=args.micro_dose_protocol,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    write_atomically(out_path, doc)
    print(f"Wrote {out_path} fit={doc['duration_fit_score']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
