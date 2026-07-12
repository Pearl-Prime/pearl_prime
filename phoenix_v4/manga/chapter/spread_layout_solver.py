"""Spread/page layout solver for manga page composition.

Provides a machine-checkable decision surface for page layout selection. This
goes beyond the frame renderer's historical "double the width for spreads"
behavior by:

1. selecting between standard / splash / dedicated double-spread shapes,
2. emitting explicit constraint results for each candidate, and
3. returning normalized panel assignments that downstream validators can reuse.
"""
from __future__ import annotations

import functools
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
GRID_LIBRARY_PATH = _REPO_ROOT / "config" / "manga" / "page_grid_templates.yaml"
FORMAT_GRAMMAR_PATH = _REPO_ROOT / "config" / "manga" / "format_adaptation_grammars.yaml"

ASPECT_HINT_WH: dict[str, float] = {
    "square_1_1": 1.0,
    "portrait_4_5": 4 / 5,
    "tall_9_16": 9 / 16,
    "wide_16_9": 16 / 9,
    "portrait_4_5_or_square_1_1": (4 / 5 + 1.0) / 2,
    "square_1_1_or_portrait_4_5": (1.0 + 4 / 5) / 2,
    "wide_16_9_or_tall_9_16": (16 / 9 + 9 / 16) / 2,
}

_HERO_TOKENS = (
    "hero",
    "spread",
    "splash",
    "climax",
    "climactic",
    "impact",
    "reveal",
    "establish",
    "establishing",
    "opener",
    "title",
)


@functools.lru_cache(maxsize=4)
def load_grid_library(path: str | None = None) -> dict[str, Any]:
    """Load the page-grid template library."""
    p = Path(path) if path else GRID_LIBRARY_PATH
    if not p.is_file():
        raise RuntimeError(f"grid library not found: {p}")
    with p.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if "layout_families" not in data or "genre_profiles" not in data:
        raise RuntimeError(f"grid library {p} missing required sections")
    return data


@functools.lru_cache(maxsize=2)
def load_format_grammars(path: str | None = None) -> dict[str, Any]:
    p = Path(path) if path else FORMAT_GRAMMAR_PATH
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def normalize_reading_direction(reading_direction: str | None) -> str:
    """Normalize repo variants into rtl / ltr / vertical_scroll."""
    rd = str(reading_direction or "").strip().lower()
    if not rd:
        return "ltr"
    if rd == "rtl" or "right_to_left" in rd:
        return "rtl"
    if rd == "vertical_scroll" or "top_to_bottom" in rd or "vertical" in rd:
        return "vertical_scroll"
    return "ltr"


def _resolve_genre_profile(genre: str | None, lib: Mapping[str, Any]) -> dict[str, Any]:
    profiles = lib.get("genre_profiles") or {}
    alias = lib.get("genre_alias") or {}
    key = str(genre or "").strip().lower()
    key = str(alias.get(key, key))
    prof = profiles.get(key) or profiles.get("default")
    if prof is None:
        raise RuntimeError("grid library missing default genre profile")
    return dict(prof)


def _page_pixel_size(page_aspect: str, long_edge_px: int) -> tuple[int, int]:
    try:
        ws, hs = page_aspect.replace("approx_", "").split(":")
        wr, hr = float(ws), float(hs)
    except Exception:
        wr, hr = 2.0, 3.0
    if hr >= wr:
        h = int(long_edge_px)
        w = int(round(long_edge_px * wr / hr))
    else:
        w = int(long_edge_px)
        h = int(round(long_edge_px * hr / wr))
    return max(1, w), max(1, h)


def _page_type_rule(page_type: str, lib: Mapping[str, Any]) -> dict[str, Any]:
    rules = lib.get("page_type_rules") or {}
    raw = rules.get(page_type) or {}
    return dict(raw)


def _select_standard_cells(
    panel_count: int,
    *,
    genre: str | None,
    lib: Mapping[str, Any],
) -> tuple[list[list[float]], dict[str, Any]]:
    prof = _resolve_genre_profile(genre, lib)
    family_name = str(prof.get("layout_family") or "standard")
    family = (lib.get("layout_families") or {}).get(family_name) or (
        lib.get("layout_families") or {}
    ).get("standard")
    if not isinstance(family, Mapping):
        raise RuntimeError(f"layout family missing: {family_name}")

    max_cap = max(1, int(prof.get("max_panels_per_page", 6)))
    want = max(1, min(int(panel_count), max_cap))
    available = sorted(int(k) for k in family.keys())
    chosen_n = next((n for n in available if n == want), None)
    if chosen_n is None:
        less_equal = [n for n in available if n <= want]
        chosen_n = max(less_equal) if less_equal else min(available)
    raw_cells = family[chosen_n]
    cells = [list(row["bbox"]) for row in raw_cells]
    return cells, prof


def _dedicated_spread_cells(panel_count: int) -> list[list[float]]:
    """Return normalized content-area cells for a facing-page spread."""
    count = max(1, min(int(panel_count), 6))
    if count == 1:
        return [[0.0, 0.0, 1.0, 1.0]]
    if count == 2:
        return [
            [0.0, 0.0, 0.5, 1.0],
            [0.5, 0.0, 0.5, 1.0],
        ]
    if count == 3:
        return [
            [0.0, 0.0, 1.0, 0.42],
            [0.0, 0.42, 0.5, 0.58],
            [0.5, 0.42, 0.5, 0.58],
        ]
    if count == 4:
        return [
            [0.0, 0.0, 0.5, 0.5],
            [0.5, 0.0, 0.5, 0.5],
            [0.0, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5, 0.5],
        ]
    if count == 5:
        return [
            [0.0, 0.0, 1.0, 0.34],
            [0.0, 0.34, 0.5, 0.33],
            [0.5, 0.34, 0.5, 0.33],
            [0.0, 0.67, 0.5, 0.33],
            [0.5, 0.67, 0.5, 0.33],
        ]
    return [
        [0.0, 0.0, 0.3333, 0.5],
        [0.3333, 0.0, 0.3334, 0.5],
        [0.6667, 0.0, 0.3333, 0.5],
        [0.0, 0.5, 0.3333, 0.5],
        [0.3333, 0.5, 0.3334, 0.5],
        [0.6667, 0.5, 0.3333, 0.5],
    ]


def _panel_meta_for_page(
    page: Mapping[str, Any],
    panel_meta_by_id: Mapping[str, Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    by_id = panel_meta_by_id or {}
    for index, panel in enumerate(page.get("panels") or []):
        pid = str(panel.get("panel_id") or f"panel_{index + 1}")
        merged = dict(by_id.get(pid) or {})
        merged.update(dict(panel))
        merged["panel_id"] = pid
        out.append(merged)
    return out


def _panel_aspect(meta: Mapping[str, Any]) -> float:
    hint = str(meta.get("aspect_hint") or "").strip()
    if hint in ASPECT_HINT_WH:
        return ASPECT_HINT_WH[hint]
    for wk, hk in (
        ("width_px", "height_px"),
        ("render_width", "render_height"),
        ("width", "height"),
    ):
        w = meta.get(wk)
        h = meta.get(hk)
        try:
            if w is not None and h not in (None, 0):
                return max(0.1, float(w) / float(h))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
    return 0.8


def _panel_is_hero(meta: Mapping[str, Any]) -> bool:
    if bool(meta.get("spread_candidate")):
        return True
    hay = " ".join(
        str(meta.get(key) or "")
        for key in (
            "panel_function",
            "beat_type",
            "role",
            "composition",
            "camera_intent",
        )
    ).lower()
    return any(tok in hay for tok in _HERO_TOKENS)


def _cell_crosses_spine(cell: Sequence[float]) -> bool:
    x, _, w, _ = cell
    return x < 0.5 < (x + w)


def _cell_area(cell: Sequence[float]) -> float:
    return float(cell[2]) * float(cell[3])


def _mirror_cells_rtl(cells: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[1.0 - float(x) - float(w), float(y), float(w), float(h)] for x, y, w, h in cells]


def _reserve_center_gutter(
    cells: Sequence[Sequence[float]],
    *,
    page_w: int,
    center_gutter_px: int,
) -> list[list[float]]:
    """Map logical spread cells into physical spread cells with a real gutter."""
    if center_gutter_px <= 0:
        return [list(map(float, row)) for row in cells]

    logical_total = float(page_w * 2)
    physical_total = logical_total + float(center_gutter_px)
    if logical_total <= 0 or physical_total <= 0:
        return [list(map(float, row)) for row in cells]

    out: list[list[float]] = []
    eps = 1e-9
    for row in cells:
        x, y, w, h = (float(v) for v in row)
        x0 = x * logical_total
        x1 = (x + w) * logical_total
        crosses_spine = x < (0.5 - eps) and (x + w) > (0.5 + eps)
        right_page = x >= (0.5 - eps)
        if right_page:
            x0 += center_gutter_px
            x1 += center_gutter_px
        elif crosses_spine:
            x1 += center_gutter_px
        out.append(
            [
                x0 / physical_total,
                y,
                max(0.0, (x1 - x0) / physical_total),
                h,
            ]
        )
    return out


def _cell_page_side(cell: Sequence[float]) -> str:
    center_x = float(cell[0]) + float(cell[2]) / 2.0
    if center_x < 0.48:
        return "left"
    if center_x > 0.52:
        return "right"
    return "center"


def _page_type_candidates(
    requested_page_type: str,
    *,
    panels: Sequence[Mapping[str, Any]],
    spread_allowed: bool,
) -> list[str]:
    requested = str(requested_page_type or "standard")
    candidates: list[str] = []
    if requested == "splash":
        candidates.append("splash")
    elif requested == "double_spread":
        if spread_allowed:
            candidates.append("double_spread")
        candidates.append("standard")
    else:
        spread_hint = any(_panel_is_hero(p) for p in panels) and len(panels) <= 4
        if spread_allowed and (spread_hint or bool(next((p for p in panels if p.get("spread_candidate")), None))):
            candidates.append("double_spread")
        candidates.append("standard")
        if len(panels) == 1 and any(_panel_is_hero(p) for p in panels):
            candidates.insert(0, "splash")
    seen: set[str] = set()
    ordered: list[str] = []
    for item in candidates:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered or ["standard"]


def _spread_allowed(
    reading_direction: str,
    *,
    format_id: str | None,
    format_grammars: Mapping[str, Any],
) -> bool:
    if normalize_reading_direction(reading_direction) == "vertical_scroll":
        return False
    if not format_id:
        return True
    fmts = (format_grammars.get("formats") or {})
    row = fmts.get(format_id)
    if not isinstance(row, Mapping):
        return True
    return bool(row.get("spread_enabled", True))


def _constraint(
    rule_id: str,
    status: str,
    detail: str,
    *,
    severity: str = "hard",
    value: Any | None = None,
) -> dict[str, Any]:
    out = {
        "rule_id": rule_id,
        "status": status,
        "severity": severity,
        "detail": detail,
    }
    if value is not None:
        out["value"] = value
    return out


def _score_candidate(
    candidate_page_type: str,
    *,
    requested_page_type: str,
    panels: Sequence[Mapping[str, Any]],
    genre: str | None,
    reading_direction: str,
    page_aspect: str,
    long_edge_px: int,
    lib: Mapping[str, Any],
    spread_allowed: bool,
) -> dict[str, Any]:
    pt_rule = _page_type_rule(candidate_page_type, lib)
    page_w, page_h = _page_pixel_size(page_aspect, long_edge_px)
    if candidate_page_type == "double_spread":
        logical_cells = _dedicated_spread_cells(len(panels))
        prof = _resolve_genre_profile(genre, lib)
    else:
        logical_cells, prof = _select_standard_cells(len(panels), genre=genre, lib=lib)

    cells = (
        _mirror_cells_rtl(logical_cells)
        if normalize_reading_direction(reading_direction) == "rtl"
        else [list(row) for row in logical_cells]
    )

    panel_capacity = len(cells)
    panel_count = len(panels)
    placed_count = min(panel_count, panel_capacity)
    overflow_count = max(0, panel_count - panel_capacity)
    spread = candidate_page_type == "double_spread"
    center_gutter_px = int(pt_rule.get("center_gutter_px", 60)) if spread else 0
    if spread:
        cells = _reserve_center_gutter(
            cells,
            page_w=page_w,
            center_gutter_px=center_gutter_px,
        )

    constraints: list[dict[str, Any]] = []
    if spread:
        constraints.append(
            _constraint(
                "spread_supported",
                "pass" if spread_allowed else "fail",
                "reading/format grammar allows double spreads"
                if spread_allowed
                else "spread requested on a vertical-scroll / spread-disabled grammar",
                value=spread_allowed,
            )
        )
    else:
        constraints.append(
            _constraint(
                "spread_supported",
                "pass",
                "single-page layout does not require spread support",
                severity="soft",
            )
        )

    constraints.append(
        _constraint(
            "panel_capacity",
            "pass" if overflow_count == 0 else "warn",
            "all panels fit the chosen layout"
            if overflow_count == 0
            else f"{overflow_count} panel(s) spill to a follow-on page",
            severity="soft" if overflow_count else "hard",
            value={"panel_count": panel_count, "panel_capacity": panel_capacity},
        )
    )

    largest_area = max((_cell_area(cell) for cell in cells), default=1.0)
    aspect_total = 0.0
    hero_penalty = 0.0
    spine_fails = 0
    assignments: list[dict[str, Any]] = []
    for idx, panel in enumerate(panels[:placed_count]):
        cell = cells[idx]
        aspect = _panel_aspect(panel)
        cell_aspect = max(0.1, float(cell[2]) / max(float(cell[3]), 1e-6))
        aspect_total += abs(math.log(max(aspect, 0.1) / cell_aspect))

        is_hero = _panel_is_hero(panel)
        area = _cell_area(cell)
        if is_hero and area < (largest_area * 0.85):
            hero_penalty += 1.0

        crosses_spine = spread and _cell_crosses_spine(cell)
        allow_spine = bool(panel.get("allow_spine_crossing")) or is_hero
        if crosses_spine and not allow_spine:
            spine_fails += 1

        assignments.append(
            {
                "panel_id": str(panel.get("panel_id") or f"panel_{idx + 1}"),
                "cell_index": idx,
                "bbox_norm": [round(float(v), 4) for v in cell],
                "page_side": _cell_page_side(cell),
                "panel_aspect": round(aspect, 4),
                "cell_aspect": round(cell_aspect, 4),
                "hero_panel": is_hero,
                "spine_crossing": crosses_spine,
            }
        )

    constraints.append(
        _constraint(
            "spine_safety",
            "pass" if spine_fails == 0 else "fail",
            "assigned panels respect the spread spine"
            if spine_fails == 0
            else f"{spine_fails} assigned panel(s) cross the spine without an explicit allow flag",
            value={"spine_fails": spine_fails},
        )
    )

    request_penalty = 0.0
    if requested_page_type == "double_spread" and candidate_page_type != "double_spread":
        request_penalty += 3.0
    if requested_page_type == "splash" and candidate_page_type != "splash":
        request_penalty += 3.0

    hero_reward = 0.0
    if spread and any(_panel_is_hero(p) for p in panels):
        hero_reward = 0.35

    total = aspect_total + hero_penalty + request_penalty + (overflow_count * 0.75) - hero_reward
    valid = not any(
        c["status"] == "fail" and c.get("severity") == "hard" for c in constraints
    )

    return {
        "requested_page_type": requested_page_type,
        "resolved_page_type": candidate_page_type,
        "reading_direction": normalize_reading_direction(reading_direction),
        "genre_profile": prof,
        "page_type_rule": pt_rule,
        "spread": spread,
        "page_size_px": {
            "width": (page_w * 2 + center_gutter_px) if spread else page_w,
            "height": page_h,
        },
        "page_aspect": page_aspect,
        "long_edge_px": long_edge_px,
        "panel_count": panel_count,
        "panel_capacity": panel_capacity,
        "overflow_count": overflow_count,
        "cells": cells,
        "logical_cells": logical_cells,
        "panel_assignments": assignments,
        "constraints": constraints,
        "scores": {
            "aspect_total": round(aspect_total, 4),
            "hero_penalty": round(hero_penalty, 4),
            "request_penalty": round(request_penalty, 4),
            "overflow_penalty": round(overflow_count * 0.75, 4),
            "hero_reward": round(hero_reward, 4),
            "total": round(total, 4),
        },
        "valid": valid,
    }


def validate_layout_decision(decision: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize pass/warn/fail counts for a solver decision."""
    counts = {"pass": 0, "warn": 0, "fail": 0}
    failures: list[str] = []
    for row in decision.get("constraints") or []:
        status = str(row.get("status") or "pass")
        counts[status] = counts.get(status, 0) + 1
        if status == "fail":
            failures.append(str(row.get("rule_id") or "unknown"))
    return {
        "valid": bool(decision.get("valid", False)),
        "counts": counts,
        "failures": failures,
    }


def solve_page_layout(
    page: Mapping[str, Any],
    *,
    genre: str | None = None,
    reading_direction: str | None = None,
    page_aspect: str | None = None,
    long_edge_px: int | None = None,
    lib: Mapping[str, Any] | None = None,
    format_id: str | None = None,
    format_grammars: Mapping[str, Any] | None = None,
    panel_meta_by_id: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Solve the best page/spread layout for one logical page.

    Returns a machine-checkable decision packet with normalized panel
    assignments and explicit constraint results.
    """
    library = dict(lib or load_grid_library())
    grammars = dict(format_grammars or load_format_grammars())
    defaults = library.get("page_defaults") or {}
    page_aspect = str(page_aspect or defaults.get("page_aspect", "2:3"))
    long_edge_px = int(long_edge_px or defaults.get("long_edge_px", 2400))
    rd = normalize_reading_direction(
        reading_direction or page.get("reading_direction") or "ltr"
    )

    panels = _panel_meta_for_page(page, panel_meta_by_id)
    requested_page_type = str(page.get("page_type") or "standard")
    spread_allowed = _spread_allowed(rd, format_id=format_id, format_grammars=grammars)
    candidates = _page_type_candidates(
        requested_page_type,
        panels=panels,
        spread_allowed=spread_allowed,
    )

    scored = [
        _score_candidate(
            candidate,
            requested_page_type=requested_page_type,
            panels=panels,
            genre=genre,
            reading_direction=rd,
            page_aspect=page_aspect,
            long_edge_px=long_edge_px,
            lib=library,
            spread_allowed=spread_allowed,
        )
        for candidate in candidates
    ]
    scored.sort(key=lambda row: (0 if row["valid"] else 1, row["scores"]["total"]))
    best = scored[0] if scored else _score_candidate(
        "standard",
        requested_page_type=requested_page_type,
        panels=panels,
        genre=genre,
        reading_direction=rd,
        page_aspect=page_aspect,
        long_edge_px=long_edge_px,
        lib=library,
        spread_allowed=spread_allowed,
    )

    issues: list[dict[str, Any]] = []
    if requested_page_type != best["resolved_page_type"]:
        issues.append(
            {
                "rule_id": "requested_page_type_downgrade",
                "severity": "soft",
                "detail": f"requested {requested_page_type} resolved to {best['resolved_page_type']}",
            }
        )
    best["issues"] = issues
    best["validation"] = validate_layout_decision(best)
    return best
