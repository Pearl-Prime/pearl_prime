"""Character-design constraint solver — V2 manga pipeline Phase A.1.

Implements CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md §2.2 verbatim:
deterministic catalog-wide character distinctness via 12-axis collision detection.

Algorithm (per spec):
    check_collision(new_design, catalog, brand_scope):
      1. Validate ≥9 of 12 axes have lockout=yes (lockout_minimum)
      2. Reject if any forbidden_combination matches the new design
      3. For each existing entry in catalog, count matching locked-axis values:
           threshold = 5 if same brand else 7 (per character_design_axes.yaml::
           solver_rules.collision_threshold)
         If match_count >= threshold → REJECT (return colliding axes for
         author iteration).
      4. Return ACCEPT.

Inputs come from `config/manga/character_design_axes.yaml` (vocab + rules) and
per-series `character_design` blocks at
`config/source_of_truth/manga_profiles/series/<series_id>.yaml`.

Pure Python; no LLM calls. Run as a CLI for solver-validation OR import for
use inside `build_panel_prompts.py` (Phase A.2 caller).
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_AXES_PATH = REPO_ROOT / "config" / "manga" / "character_design_axes.yaml"
DEFAULT_TEMPLATE_PATH = REPO_ROOT / "config" / "manga" / "character_design_template.yaml"
DEFAULT_PROFILES_DIR = REPO_ROOT / "config" / "source_of_truth" / "manga_profiles" / "series"


# ── Result types ─────────────────────────────────────────────────────────────

@dataclass
class SolverResult:
    """Outcome of running the solver against a candidate character_design."""
    accepted: bool
    series_id: str
    brand_id: str
    reasons: list[str] = field(default_factory=list)
    colliding_with: list[dict[str, Any]] = field(default_factory=list)
    forbidden_rules_hit: list[str] = field(default_factory=list)
    locked_axes_count: int = 0

    def __bool__(self) -> bool:
        return self.accepted

    def summary(self) -> str:
        if self.accepted:
            return f"ACCEPT {self.series_id} ({self.brand_id}) — {self.locked_axes_count} locked axes"
        return f"REJECT {self.series_id} ({self.brand_id}) — {'; '.join(self.reasons)}"


# ── Spec constants (sourced from character_design_axes.yaml::solver_rules) ───

DEFAULT_LOCKOUT_MIN = 9
DEFAULT_SAME_BRAND_THRESHOLD = 5
DEFAULT_CROSS_BRAND_THRESHOLD = 7


# ── Loaders ──────────────────────────────────────────────────────────────────

def load_axes_config(path: Path | None = None) -> dict:
    """Load `config/manga/character_design_axes.yaml`. Falls back to repo default."""
    p = Path(path) if path else DEFAULT_AXES_PATH
    return yaml.safe_load(p.read_text())


def load_catalog_designs(profiles_dir: Path | None = None) -> list[dict]:
    """Walk `config/source_of_truth/manga_profiles/series/*.yaml` and yield each
    series's `character_design` block (if present). Returns a list of dicts each
    augmented with `_series_id`/`_brand_id` keys for fast lookup."""
    p = Path(profiles_dir) if profiles_dir else DEFAULT_PROFILES_DIR
    if not p.is_dir():
        return []
    out: list[dict] = []
    for yaml_path in sorted(p.glob("*.yaml")):
        data = yaml.safe_load(yaml_path.read_text()) or {}
        cd = data.get("character_design")
        if not cd:
            continue
        cd = dict(cd)
        cd["_series_id"] = data.get("series_id") or cd.get("series_id") or yaml_path.stem
        cd["_brand_id"] = data.get("brand_id") or cd.get("brand_id") or "unknown_brand"
        out.append(cd)
    return out


# ── Axis comparison helpers ──────────────────────────────────────────────────

def _axis_lockout(axis_block: Any) -> bool:
    """Return True iff the axis block declares lockout=yes (or True)."""
    if not isinstance(axis_block, dict):
        return False
    val = axis_block.get("lockout")
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in {"yes", "true", "y"}
    return False


def _axis_value_signature(axis_block: Any) -> tuple:
    """Return a hashable tuple representing the axis's identity-relevant fields.

    Multi-attribute axes (eye_geometry, nose_construction, mouth_jaw, hair, ...)
    contribute every sub-key whose value is a primitive. The `lockout` key is
    excluded since it's metadata, not character identity. Free-form notes
    (`mangaka_tradition`, `signature_shape_note`, etc.) are also excluded —
    they're prose annotations, not identity signal.
    """
    if not isinstance(axis_block, dict):
        return (axis_block,)
    skip = {"lockout", "mangaka_tradition", "signature_shape_note", "notes"}
    keys = sorted(k for k in axis_block.keys() if k not in skip)
    parts: list[Any] = []
    for k in keys:
        v = axis_block[k]
        if isinstance(v, (str, int, float, bool)) or v is None:
            parts.append((k, v))
        elif isinstance(v, (list, tuple)):
            parts.append((k, tuple(v)))
        # nested dicts inside an axis are rare; skip rather than crash
    return tuple(parts)


def _resolve_dotted_path(design: dict, dotted: str) -> Any:
    """Resolve `eye_geometry.size` style paths against an axes block dict."""
    parts = dotted.split(".")
    head = design.get("axes", {}).get(parts[0])
    if head is None:
        return None
    cursor: Any = head
    for p in parts[1:]:
        if isinstance(cursor, dict):
            cursor = cursor.get(p)
        else:
            return None
    return cursor


def _market_demo(design: dict) -> Any:
    """Return market_demo from the design (top-level, per template schema)."""
    return design.get("market_demo")


# ── Forbidden combination check ──────────────────────────────────────────────

def check_forbidden_combinations(
    design: dict,
    forbidden_rules: list[dict],
) -> list[str]:
    """Return rule_ids whose `forbidden` clause matches the design.

    Each rule shape:
        rule_id: <str>
        axes: [<dotted-path>, ...]  # documentation only; not used by matcher
        forbidden: { <dotted-path>: <value>, ... }
        reason: <str>

    A rule matches when EVERY entry in `forbidden` matches the design (logical
    AND). Use multiple rules for OR semantics.
    """
    hits: list[str] = []
    for rule in forbidden_rules or []:
        forbidden = rule.get("forbidden") or {}
        if not forbidden:
            continue
        matched_all = True
        for path, expected in forbidden.items():
            if path == "market_demo":
                actual = _market_demo(design)
            else:
                actual = _resolve_dotted_path(design, path)
            if actual != expected:
                matched_all = False
                break
        if matched_all:
            hits.append(rule.get("rule_id") or "<unnamed>")
    return hits


# ── Collision counting (per spec §2.2 pseudocode) ────────────────────────────

def count_matching_locked_axes(
    a: dict,
    b: dict,
    *,
    axis_priority_order: list[str],
) -> tuple[int, list[str]]:
    """Per-spec: count axes where BOTH a and b have lockout=yes AND values match.
    Returns (count, matching_axis_names)."""
    a_axes = a.get("axes") or {}
    b_axes = b.get("axes") or {}
    matching: list[str] = []
    for axis_name in axis_priority_order:
        a_block = a_axes.get(axis_name)
        b_block = b_axes.get(axis_name)
        if not _axis_lockout(a_block) or not _axis_lockout(b_block):
            continue
        if _axis_value_signature(a_block) == _axis_value_signature(b_block):
            matching.append(axis_name)
    return len(matching), matching


def check_collision(
    new_design: dict,
    catalog: Iterable[dict],
    *,
    axes_config: dict,
    same_brand_threshold: int = DEFAULT_SAME_BRAND_THRESHOLD,
    cross_brand_threshold: int = DEFAULT_CROSS_BRAND_THRESHOLD,
    lockout_minimum: int = DEFAULT_LOCKOUT_MIN,
) -> SolverResult:
    """Run the solver against a candidate. Mirrors spec §2.2 pseudocode.

    new_design is the candidate character_design block (already extracted from
    a series YAML). catalog is an iterable of existing designs from
    load_catalog_designs() or equivalent.

    axes_config is the loaded character_design_axes.yaml. Threshold + axis
    priority + forbidden-combination rules are read from there with explicit
    parameter overrides allowed.
    """
    series_id = new_design.get("_series_id") or new_design.get("series_id") or "<unknown>"
    brand_id = new_design.get("_brand_id") or new_design.get("brand_id") or "<unknown>"

    solver_rules = axes_config.get("solver_rules") or {}
    axis_priority = solver_rules.get("axis_priority_order_for_solver") or []
    forbidden_rules = solver_rules.get("forbidden_combinations") or []

    # 1. lockout-axes minimum
    new_axes = new_design.get("axes") or {}
    locked = [name for name, blk in new_axes.items() if _axis_lockout(blk)]
    locked_count = len(locked)
    if locked_count < lockout_minimum:
        return SolverResult(
            accepted=False,
            series_id=series_id,
            brand_id=brand_id,
            reasons=[f"lockout_minimum violated: {locked_count} < {lockout_minimum}"],
            locked_axes_count=locked_count,
        )

    # 2. forbidden combinations
    forbidden_hits = check_forbidden_combinations(new_design, forbidden_rules)
    if forbidden_hits:
        return SolverResult(
            accepted=False,
            series_id=series_id,
            brand_id=brand_id,
            reasons=[f"forbidden combination(s): {', '.join(forbidden_hits)}"],
            forbidden_rules_hit=forbidden_hits,
            locked_axes_count=locked_count,
        )

    # 3. catalog collision
    collisions: list[dict[str, Any]] = []
    reasons: list[str] = []
    for existing in catalog:
        # Skip self-comparison (a series re-validating against the catalog
        # that already includes it).
        if existing.get("_series_id") == new_design.get("_series_id"):
            continue
        threshold = (
            same_brand_threshold
            if existing.get("_brand_id") == brand_id
            else cross_brand_threshold
        )
        match_count, matching_axes = count_matching_locked_axes(
            new_design, existing, axis_priority_order=axis_priority,
        )
        if match_count >= threshold:
            collisions.append({
                "existing_series_id": existing.get("_series_id"),
                "existing_brand_id": existing.get("_brand_id"),
                "scope": "same_brand" if existing.get("_brand_id") == brand_id else "cross_brand",
                "match_count": match_count,
                "threshold": threshold,
                "colliding_axes": matching_axes,
            })
            reasons.append(
                f"collision with {existing.get('_series_id')} on "
                f"{match_count} locked axes ({', '.join(matching_axes)})"
            )

    if collisions:
        return SolverResult(
            accepted=False,
            series_id=series_id,
            brand_id=brand_id,
            reasons=reasons,
            colliding_with=collisions,
            locked_axes_count=locked_count,
        )

    return SolverResult(
        accepted=True,
        series_id=series_id,
        brand_id=brand_id,
        reasons=[],
        locked_axes_count=locked_count,
    )


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate a character_design YAML against the catalog.",
    )
    ap.add_argument(
        "--series-yaml",
        help="Path to a single series YAML carrying a character_design block to validate.",
    )
    ap.add_argument(
        "--axes-config",
        default=str(DEFAULT_AXES_PATH),
        help="Path to character_design_axes.yaml.",
    )
    ap.add_argument(
        "--profiles-dir",
        default=str(DEFAULT_PROFILES_DIR),
        help="Directory of existing series profiles (catalog).",
    )
    ap.add_argument(
        "--validate-all",
        action="store_true",
        help="Walk the profiles dir and validate every series in the catalog "
             "against every other series (catalog audit mode).",
    )
    ap.add_argument(
        "--same-brand-threshold",
        type=int,
        default=DEFAULT_SAME_BRAND_THRESHOLD,
    )
    ap.add_argument(
        "--cross-brand-threshold",
        type=int,
        default=DEFAULT_CROSS_BRAND_THRESHOLD,
    )
    ap.add_argument(
        "--lockout-minimum",
        type=int,
        default=DEFAULT_LOCKOUT_MIN,
    )
    args = ap.parse_args()

    axes_config = load_axes_config(Path(args.axes_config))
    catalog = load_catalog_designs(Path(args.profiles_dir))

    if args.validate_all:
        # Walk catalog, validate each entry against the rest.
        bad = 0
        for cand in catalog:
            others = [c for c in catalog if c.get("_series_id") != cand.get("_series_id")]
            r = check_collision(
                cand, others,
                axes_config=axes_config,
                same_brand_threshold=args.same_brand_threshold,
                cross_brand_threshold=args.cross_brand_threshold,
                lockout_minimum=args.lockout_minimum,
            )
            print(r.summary())
            if not r.accepted:
                bad += 1
        return 0 if bad == 0 else 2

    if not args.series_yaml:
        print("Provide --series-yaml or --validate-all", file=sys.stderr)
        return 1

    series_path = Path(args.series_yaml)
    if not series_path.is_file():
        print(f"series YAML not found: {series_path}", file=sys.stderr)
        return 1
    series_data = yaml.safe_load(series_path.read_text()) or {}
    cand_design = series_data.get("character_design")
    if not cand_design:
        print(f"no character_design block in {series_path}", file=sys.stderr)
        return 1
    cand = dict(cand_design)
    cand["_series_id"] = series_data.get("series_id") or cand.get("series_id") or series_path.stem
    cand["_brand_id"] = series_data.get("brand_id") or cand.get("brand_id") or "unknown_brand"

    r = check_collision(
        cand, catalog,
        axes_config=axes_config,
        same_brand_threshold=args.same_brand_threshold,
        cross_brand_threshold=args.cross_brand_threshold,
        lockout_minimum=args.lockout_minimum,
    )
    print(r.summary())
    if r.colliding_with:
        for c in r.colliding_with:
            print(f"  ↳ {c['scope']} match {c['match_count']}/{c['threshold']} on axes: "
                  f"{', '.join(c['colliding_axes'])} (vs {c['existing_series_id']})")
    return 0 if r.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
