"""
EI v2 dimension: duration_fit — content duration vs registry optimal (rule-based).
Spec: CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md §11.
"""
from __future__ import annotations

from typing import Any

from phoenix_v4.quality.ei_v2.config import ei_v2_repo_root, load_ei_v2_config

try:
    import yaml
except ImportError:
    yaml = None


def _load_registry() -> dict[str, Any]:
    root = ei_v2_repo_root()
    path = root / "config" / "duration" / "duration_registry.yaml"
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def score_duration_fit(
    content_meta: dict[str, Any],
    cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    content_meta keys: format (registry key), intent, duration_sec | page_count | panel_count,
    platform (optional), persona (optional).
    Returns score 0..1, pass flag vs threshold.
    """
    cfg = cfg or load_ei_v2_config()
    df_cfg = (cfg.get("duration_fit") or {})
    if not df_cfg.get("enabled", True):
        return {"dimension": "duration_fit", "score": 0.5, "skipped": True, "pass": True}

    fmt = str(content_meta.get("format") or "")
    intent = str(content_meta.get("intent") or "therapeutic")
    reg = _load_registry()
    fmts = reg.get("formats") or {}
    if fmt not in fmts or intent not in (fmts[fmt] or {}):
        if fmt in fmts:
            intent = "discovery" if "discovery" in fmts[fmt] else next(iter(fmts[fmt].keys()))
        else:
            return {"dimension": "duration_fit", "score": 0.5, "pass": True, "note": "unknown_format"}

    row = fmts[fmt][intent]
    unit = row.get("unit", "seconds")
    vmin, vopt, vmax = float(row["min"]), float(row["optimal"]), float(row["max"])

    if unit == "seconds":
        actual = float(content_meta.get("duration_sec") or 0)
    elif unit == "minutes":
        actual = float(content_meta.get("duration_sec") or 0) / 60.0
    elif unit == "pages":
        actual = float(content_meta.get("page_count") or 0)
    elif unit == "panels":
        actual = float(content_meta.get("panel_count") or 0)
    else:
        actual = float(content_meta.get("duration_sec") or 0)

    if actual <= 0:
        return {"dimension": "duration_fit", "score": 0.0, "pass": False, "issues": ["no_duration"]}

    span = max(vmax - vmin, 1e-6)
    dist = abs(actual - vopt) / span
    base = max(0.0, 1.0 - dist)
    if vmin <= actual <= vmax:
        base = min(1.0, base + 0.15)

    th = (df_cfg.get("thresholds") or {})
    pass_th = float(th.get("pass", 0.60))
    warn_th = float(th.get("warn", 0.45))

    passed = base >= pass_th
    status = "PASS" if passed else ("WARN" if base >= warn_th else "FAIL")

    w = df_cfg.get("weights") or {}
    note = {
        "therapeutic_fit_weight": w.get("therapeutic_fit", 0.40),
        "platform_fit_weight": w.get("platform_fit", 0.35),
        "rule_note": "single-axis distance_to_optimal; full planner separates t/p/a",
    }

    return {
        "dimension": "duration_fit",
        "score": round(base, 4),
        "pass": passed,
        "status": status,
        "format": fmt,
        "intent": intent,
        "unit": unit,
        "actual": actual,
        "optimal": vopt,
        **note,
    }


__all__ = ["score_duration_fit"]
