"""
PR #1037 worldwide Path X allocation TSV loader (Phase 2 V1.1).

Reads ``artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv``
and returns a dict keyed by ``(brand_id, locale, surface)`` with integer counts
and the source ``priority_phase`` tag.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, TypedDict

VALID_SURFACES = frozenset({"ebook", "manga"})


class AllocationCell(TypedDict):
    series_count: int
    episodes_per_series: int
    priority_phase: str


AllocationPlan = dict[tuple[str, str, str], AllocationCell]


def default_allocation_tsv_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "artifacts"
        / "qa"
        / "worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv"
    )


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def load_v1_1_brand_allocation_plan(tsv_path: Path, *, strict_surface: bool = True) -> AllocationPlan:
    """
    Parse the PR #1037 allocation TSV.

    ``strict_surface``: when True, rows whose ``surface`` is not ``ebook`` or
    ``manga`` raise ``ValueError`` (anti-drift for the 2-surface contract).
    """
    if not tsv_path.exists():
        raise FileNotFoundError(f"allocation TSV not found: {tsv_path}")

    out: AllocationPlan = {}
    with open(tsv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if reader.fieldnames is None:
            return out
        normalized = {h.strip().lower(): h for h in reader.fieldnames}

        def col(name: str) -> str | None:
            key = name.lower()
            return normalized.get(key)

        c_brand = col("brand_id")
        c_locale = col("locale")
        c_surface = col("surface")
        c_series = col("series_count")
        c_ep = col("episode_per_series_count") or col("episodes_per_series")
        c_phase = col("priority_phase")
        required = (c_brand, c_locale, c_surface, c_series, c_ep, c_phase)
        if not all(required):
            raise ValueError(
                "allocation TSV missing required columns "
                "(need brand_id, locale, surface, series_count, "
                "episode_per_series_count or episodes_per_series, priority_phase)"
            )

        for row in reader:
            brand_id = (row.get(c_brand) or "").strip()
            locale = (row.get(c_locale) or "").strip()
            surface = (row.get(c_surface) or "").strip().lower()
            if not brand_id or not locale or not surface:
                continue
            if strict_surface and surface not in VALID_SURFACES:
                raise ValueError(
                    f"invalid surface {surface!r} for brand_id={brand_id!r} "
                    f"locale={locale!r} (expected one of {sorted(VALID_SURFACES)})"
                )
            try:
                series_count = int((row.get(c_series) or "0").strip())
            except ValueError as e:
                raise ValueError(f"non-int series_count for {brand_id}/{locale}/{surface}") from e
            try:
                ep_raw = (row.get(c_ep) or "0").strip()
                episodes_per_series = int(ep_raw)
            except ValueError as e:
                raise ValueError(
                    f"non-int episode count for {brand_id}/{locale}/{surface}"
                ) from e
            phase = (row.get(c_phase) or "").strip()
            key = (brand_id, locale, surface)
            if key in out:
                raise ValueError(f"duplicate allocation key: {key}")
            out[key] = {
                "series_count": series_count,
                "episodes_per_series": episodes_per_series,
                "priority_phase": phase,
            }
    return out


def get_cell(
    plan: AllocationPlan,
    brand_id: str,
    locale: str,
    surface: str,
) -> AllocationCell | None:
    """Return the allocation cell or None if absent."""
    return plan.get((brand_id, locale, surface.lower()))


def summarize_by_locale(plan: AllocationPlan) -> dict[str, int]:
    """Count rows per ``locale`` (handy for QA summaries)."""
    counts: dict[str, int] = {}
    for _b, loc, _s in plan:
        counts[loc] = counts.get(loc, 0) + 1
    return dict(sorted(counts.items()))


def filter_v1_0_cells(plan: AllocationPlan) -> AllocationPlan:
    """Subset locked to shipped teacher-matrix cells (12 brands × 4 × 2)."""
    return {
        k: dict(v)
        for k, v in plan.items()
        if v.get("priority_phase") == "V1.0_matrix_confirmed"
    }
