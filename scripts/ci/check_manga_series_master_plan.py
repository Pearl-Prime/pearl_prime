#!/usr/bin/env python3
"""Series Master Plan gate — genre-derived arc cadence, no fixed-12, no stubs.

Authority: docs/specs/MANGA_SERIES_MASTER_PLAN_CONTRACT.md
Schema: schemas/manga/series_master_plan.schema.json

Validates the per-series long-horizon plan layer (default 100 episodes) that
sits ABOVE per-arc storyboards and BELOW the series_plan listing:

  1. Schema shape (jsonschema when available; structural fallback otherwise).
  2. Genre resolves via manga_pacing_by_genre.yaml genre_family_aliases to a
     pacing family carrying an arc_cadence block (or a declared study source
     for webtoon / US-illustrated frames — no YAML family row exists for those).
  3. Arc spans tile 1..episode_horizon with no gaps or overlaps.
  4. Cadence conformance: arc lengths within the family episodes_per_arc_range
     +/- tolerance (default 25%, matching the pacing file's MDLG-08 convention).
  5. first_major_shift branches on the family's first_major_shift_by:
     null (healing, horror, supernatural_everyday, gag, essay) => the plan MUST
     NOT force a status-quo shift (cyclical segmentation); non-null => a shift
     must land by that episode (+ tolerance).
  6. Stub-marker lint + teacher-name scan on all plan prose (primitives reused
     from check_manga_story_authored).
  7. Mode-arc XOR per config/manga/manga_mode_vessels.yaml: teacher XOR music
     XOR explicit none; every arc's mode matches the series mode.
  8. Episode-plan pass integrity: detailed arcs carry per-episode plans that
     cover their span exactly.

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_series_master_plan.py
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_series_master_plan.py \\
        --plan artifacts/manga/series_master_plans/<series>.master_plan.yaml
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_series_master_plan.py \\
        --base origin/main --head HEAD

Exit: 0 ok; 1 violation (named reason).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

# Reuse the stub-marker + teacher-name primitives from the story-authored gate
# (same directory). Fallback mirrors are kept byte-identical to that module's
# own fallback so the light CI env behaves the same.
try:
    import check_manga_story_authored as _story_gate

    _STUB_RE = _story_gate._STUB_RE
    _TEACHER_NAME_RES = _story_gate._TEACHER_NAME_RES
except Exception:  # pragma: no cover - exercised only if sibling gate moves
    _STUB_RE = re.compile(
        r"\{[a-z_]+\}"
        r"|\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b"
        r"|\bHOOK\b|\bPLACEHOLDER\b|\bLOREM IPSUM\b|\bCHAPTER_END_HOOK\b",
        re.IGNORECASE,
    )
    _TEACHER_NAME_RES = (
        re.compile(r"\bAhjan\b", re.IGNORECASE),
        re.compile(r"\bSai\s*Maa?\b", re.IGNORECASE),
        re.compile(r"\bAdi\s*Da\b", re.IGNORECASE),
    )

REPO_ROOT = repo_root_from_script(Path(__file__))
MASTER_PLAN_DIR = "artifacts/manga/series_master_plans"
REWORK_INPUTS_SEGMENT = "rework_inputs"
PACING_PATH = REPO_ROOT / "config" / "manga" / "manga_pacing_by_genre.yaml"
VESSELS_PATH = REPO_ROOT / "config" / "manga" / "manga_mode_vessels.yaml"
SCHEMA_PATH = REPO_ROOT / "schemas" / "manga" / "series_master_plan.schema.json"

# Cadence range tolerance: +/-25%, the same deviation band the pacing file's
# own description uses for MDLG-08 (genre_authenticity) on per-title pacing.
CADENCE_TOLERANCE_PCT = 25.0

# Webtoon lane has NO family row in manga_pacing_by_genre.yaml (Lane 03 named
# follow-up). Arc grain comes from the study: 15-30 episodes per arc,
# platform seasons 78-115+ (artifacts/research/manga_arc_cadence_study_2026-07-24.md
# §Webtoon). Do NOT edit the pacing yaml to add a row from here.
WEBTOON_ARC_RANGE = (15, 30)
WEBTOON_STUDY_REF = "artifacts/research/manga_arc_cadence_study_2026-07-24.md#webtoon-lanes"

# Families with no 100-episode long-runner evidence (study: confidence LOW,
# single/few-volume forms). These MAY plan a shorter horizon (48-60) with a
# horizon_rationale citing the evidence line. Everyone else defaults to 100.
LOW_EVIDENCE_HORIZON_FAMILIES = {"essay", "memoir", "graphic_medicine"}
DEFAULT_HORIZON = 100
SHORT_HORIZON_RANGE = (48, 100)

_PROSE_ARC_KEYS = ("arc_premise", "arc_promise", "status_quo_shift")
_PROSE_MODE_KEYS = (
    "vessel",
    "arc_teaching_resolution",
    "motif",
    "opening",
    "mid_recurrence",
    "closing",
)
_PROSE_EP_KEYS = ("logline", "genre_pleasure_beat", "self_help_topic_beat")


class SeriesMasterPlanError(Exception):
    """Raised when a series master plan fails the contract."""


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise SeriesMasterPlanError(f"PyYAML required to load {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SeriesMasterPlanError(f"{path}: expected mapping root")
    return data


def _pacing() -> dict[str, Any]:
    if not PACING_PATH.is_file():
        return {}
    try:
        return _load_yaml(PACING_PATH)
    except Exception:
        return {}


def resolve_pacing_family(genre_id: str, pacing: Mapping[str, Any]) -> str | None:
    """Resolve a canonical genre id to a pacing family via genre_family_aliases."""
    aliases = pacing.get("genre_family_aliases") or {}
    families = pacing.get("genre_pacing") or {}
    if genre_id in aliases:
        return str(aliases[genre_id])
    if genre_id in families:
        return genre_id
    return None


def _family_arc_cadence(family: str, pacing: Mapping[str, Any]) -> Mapping[str, Any] | None:
    fam = (pacing.get("genre_pacing") or {}).get(family) or {}
    ac = fam.get("arc_cadence")
    return ac if isinstance(ac, Mapping) else None


def _iter_plan_prose(plan: Mapping[str, Any]) -> Iterable[tuple[str, str]]:
    """Yield (where, text) for every reader-facing / planning prose field.

    Metadata identity fields (series_id, brand_id, teacher_id, musician_id,
    file paths, refs) are deliberately NOT scanned — the teacher-never-named
    rule targets prose, mirroring check_manga_story_authored's panel-text scope.
    """
    for key in ("notes", "horizon_rationale", "episode_unit_mapping_note"):
        v = plan.get(key)
        if isinstance(v, str):
            yield key, v
    fms = plan.get("first_major_shift")
    if isinstance(fms, Mapping) and isinstance(fms.get("description"), str):
        yield "first_major_shift.description", fms["description"]
    for wheel in plan.get("season_wheels") or []:
        if isinstance(wheel, Mapping) and isinstance(wheel.get("drift"), str):
            yield f"season_wheels[{wheel.get('wheel_id')}].drift", wheel["drift"]
    for arc in plan.get("arcs") or []:
        if not isinstance(arc, Mapping):
            continue
        aid = arc.get("arc_id", "?")
        for key in _PROSE_ARC_KEYS:
            v = arc.get(key)
            if isinstance(v, str):
                yield f"{aid}.{key}", v
        mcv = arc.get("mc_change_vector")
        if isinstance(mcv, Mapping):
            for key in ("from_state", "to_state"):
                v = mcv.get(key)
                if isinstance(v, str):
                    yield f"{aid}.mc_change_vector.{key}", v
        mode_arc = arc.get("mode_arc")
        if isinstance(mode_arc, Mapping):
            for key in _PROSE_MODE_KEYS:
                v = mode_arc.get(key)
                if isinstance(v, str):
                    yield f"{aid}.mode_arc.{key}", v
        for ep in arc.get("episodes") or []:
            if not isinstance(ep, Mapping):
                continue
            eid = ep.get("episode", "?")
            for key in _PROSE_EP_KEYS:
                v = ep.get(key)
                if isinstance(v, str):
                    yield f"{aid}.ep{eid}.{key}", v
            hook = ep.get("hook")
            if isinstance(hook, Mapping) and isinstance(hook.get("promise"), str):
                yield f"{aid}.ep{eid}.hook.promise", hook["promise"]


def _schema_errors(plan: Mapping[str, Any]) -> list[str]:
    """jsonschema validation when available; minimal structural fallback."""
    errs: list[str] = []
    try:
        import jsonschema  # type: ignore
    except Exception:
        jsonschema = None  # type: ignore
    if jsonschema is not None and SCHEMA_PATH.is_file():
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for e in sorted(validator.iter_errors(dict(plan)), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in e.path) or "<root>"
            errs.append(f"schema: {loc}: {e.message[:200]}")
        return errs
    # structural fallback (light CI env)
    for key in (
        "schema_version",
        "artifact_type",
        "series_id",
        "genre_id",
        "episode_horizon",
        "arcs",
        "conformance",
        "acceptance_layer",
    ):
        if key not in plan:
            errs.append(f"schema-fallback: missing required key {key!r}")
    if plan.get("artifact_type") not in (None, "series_master_plan"):
        errs.append("schema-fallback: artifact_type must be series_master_plan")
    return errs


def validate_master_plan(plan: Mapping[str, Any], *, path: Path | None = None) -> list[str]:
    """Return list of failure reasons (empty = PASS)."""
    label = str(path) if path else "<master_plan>"
    errs: list[str] = []

    if plan.get("artifact_type") != "series_master_plan":
        errs.append(f"{label}: artifact_type must be series_master_plan")
        return errs

    for msg in _schema_errors(plan):
        errs.append(f"{label}: {msg}")

    pacing = _pacing()
    genre_id = str(plan.get("genre_id") or "")
    declared_family = str(plan.get("pacing_family") or "")
    cadence_source = str(plan.get("cadence_source") or "pacing_yaml")
    plan_frame = str(plan.get("plan_frame") or "serialized_episode")

    resolved = resolve_pacing_family(genre_id, pacing) if pacing else None
    if pacing and resolved is None:
        errs.append(
            f"{label}: genre_id {genre_id!r} does not resolve to any pacing family "
            f"(genre_family_aliases / genre_pacing in {PACING_PATH.name})"
        )
    if pacing and resolved and declared_family and declared_family != resolved:
        errs.append(
            f"{label}: pacing_family {declared_family!r} != alias resolution "
            f"{resolved!r} for genre_id {genre_id!r}"
        )

    ac = _family_arc_cadence(resolved, pacing) if resolved else None
    if pacing and resolved and cadence_source == "pacing_yaml" and ac is None:
        errs.append(
            f"{label}: family {resolved!r} has no arc_cadence block; "
            f"cadence numbers must trace to the pacing yaml (never a fixed 12)"
        )

    # ── horizon rule ────────────────────────────────────────────────────
    horizon = plan.get("episode_horizon")
    if isinstance(horizon, int):
        if horizon != DEFAULT_HORIZON:
            fam_for_horizon = resolved or declared_family
            if fam_for_horizon not in LOW_EVIDENCE_HORIZON_FAMILIES:
                errs.append(
                    f"{label}: episode_horizon {horizon} != {DEFAULT_HORIZON} but family "
                    f"{fam_for_horizon!r} is not a low-evidence family "
                    f"({', '.join(sorted(LOW_EVIDENCE_HORIZON_FAMILIES))})"
                )
            elif not (SHORT_HORIZON_RANGE[0] <= horizon <= SHORT_HORIZON_RANGE[1]):
                errs.append(
                    f"{label}: short horizon {horizon} outside allowed "
                    f"{SHORT_HORIZON_RANGE} for low-evidence family"
                )
            if not str(plan.get("horizon_rationale") or "").strip():
                errs.append(
                    f"{label}: episode_horizon != {DEFAULT_HORIZON} requires "
                    f"horizon_rationale citing the study evidence line"
                )
    else:
        errs.append(f"{label}: episode_horizon must be an integer")
        horizon = None

    # ── arc tiling ──────────────────────────────────────────────────────
    arcs = [a for a in (plan.get("arcs") or []) if isinstance(a, Mapping)]
    if not arcs:
        errs.append(f"{label}: no arcs")
        return errs
    spans: list[tuple[int, int, str]] = []
    for arc in arcs:
        aid = str(arc.get("arc_id") or "?")
        try:
            start, end = int(arc.get("episode_start")), int(arc.get("episode_end"))
        except (TypeError, ValueError):
            errs.append(f"{label}: {aid}: episode_start/episode_end must be integers")
            continue
        if end < start:
            errs.append(f"{label}: {aid}: episode_end {end} < episode_start {start}")
            continue
        spans.append((start, end, aid))
    spans.sort()
    if spans and horizon:
        if spans[0][0] != 1:
            errs.append(f"{label}: first arc starts at ep {spans[0][0]}, must start at 1")
        prev_end, prev_aid = None, None
        for start, end, aid in spans:
            if prev_end is not None:
                if start == prev_end:  # same-episode overlap boundary
                    errs.append(f"{label}: {prev_aid}/{aid} overlap at ep {start}")
                elif start < prev_end:
                    errs.append(
                        f"{label}: {aid} overlaps {prev_aid} "
                        f"(starts ep {start} <= {prev_aid} end {prev_end})"
                    )
                elif start > prev_end + 1:
                    errs.append(
                        f"{label}: gap between {prev_aid} (ends ep {prev_end}) and "
                        f"{aid} (starts ep {start}) — arcs must tile 1..{horizon}"
                    )
            prev_end, prev_aid = end, aid
        if spans[-1][1] != horizon:
            errs.append(
                f"{label}: last arc ends at ep {spans[-1][1]}, must end at "
                f"episode_horizon {horizon}"
            )

    # ── cadence conformance ────────────────────────────────────────────
    if plan_frame in ("book_format", "strip_serial"):
        arc_range = None  # book/strip frames carry page/word-mass targets, not episode cadence
    elif cadence_source == "study_webtoon":
        arc_range = WEBTOON_ARC_RANGE
    elif ac is not None:
        rng = ac.get("episodes_per_arc_range") or []
        arc_range = (int(rng[0]), int(rng[1])) if len(rng) == 2 else None
    else:
        arc_range = None
    if arc_range:
        tol = CADENCE_TOLERANCE_PCT / 100.0
        lo = max(1, int(arc_range[0] * (1 - tol)))
        hi = max(1, round(arc_range[1] * (1 + tol)))
        for start, end, aid in spans:
            length = end - start + 1
            if not (lo <= length <= hi):
                errs.append(
                    f"{label}: {aid}: length {length} eps outside genre cadence "
                    f"{list(arc_range)} +/-{CADENCE_TOLERANCE_PCT:.0f}% "
                    f"([{lo}, {hi}]) for family {resolved or declared_family!r}"
                )

    # ── first_major_shift branch (null semantics, not missing data) ────
    shift_by = ac.get("first_major_shift_by") if ac is not None else None
    fms = plan.get("first_major_shift")
    if ac is not None and cadence_source == "pacing_yaml":
        if shift_by is None:
            if fms is not None:
                errs.append(
                    f"{label}: family {resolved!r} has first_major_shift_by: null "
                    f"(no status-quo-shift convention — the loop is the product); "
                    f"first_major_shift must be null, not forced"
                )
            for arc in arcs:
                if arc.get("status_quo_shift") is not None:
                    errs.append(
                        f"{label}: {arc.get('arc_id')}: status_quo_shift must be null "
                        f"in a no-shift family ({resolved}) — cyclical segmentation, "
                        f"never a forced shift"
                    )
        else:
            if not isinstance(fms, Mapping):
                errs.append(
                    f"{label}: family {resolved!r} expects a first major shift by "
                    f"ep {shift_by}; first_major_shift must be declared"
                )
            else:
                try:
                    ep = int(fms.get("episode"))
                except (TypeError, ValueError):
                    ep = None
                cap = round(int(shift_by) * (1 + CADENCE_TOLERANCE_PCT / 100.0))
                if ep is None:
                    errs.append(f"{label}: first_major_shift.episode must be an integer")
                elif ep > cap:
                    errs.append(
                        f"{label}: first_major_shift at ep {ep} exceeds family "
                        f"first_major_shift_by {shift_by} (+{CADENCE_TOLERANCE_PCT:.0f}% "
                        f"= ep {cap})"
                    )
                shift_arc = str(fms.get("arc_id") or "")
                arc_ids = {str(a.get("arc_id")) for a in arcs}
                if shift_arc and shift_arc not in arc_ids:
                    errs.append(
                        f"{label}: first_major_shift.arc_id {shift_arc!r} not in arcs"
                    )
                else:
                    holder = next(
                        (a for a in arcs if str(a.get("arc_id")) == shift_arc), None
                    )
                    if holder is not None and holder.get("status_quo_shift") is None:
                        errs.append(
                            f"{label}: {shift_arc}: holds first_major_shift but "
                            f"declares status_quo_shift: null"
                        )

    # ── mode-arc XOR + coherence ───────────────────────────────────────
    mode = str(plan.get("mode") or "none")
    if mode == "teacher" and plan.get("musician_id"):
        errs.append(f"{label}: mode=teacher must not carry musician_id (XOR)")
    if mode == "music" and not plan.get("musician_id"):
        errs.append(f"{label}: mode=music requires musician_id (XOR)")
    for arc in arcs:
        aid = str(arc.get("arc_id") or "?")
        mode_arc = arc.get("mode_arc")
        if not isinstance(mode_arc, Mapping):
            errs.append(f"{label}: {aid}: missing mode_arc (regular series: explicit mode: none)")
            continue
        arc_mode = str(mode_arc.get("mode") or "")
        if arc_mode != mode:
            errs.append(
                f"{label}: {aid}: mode_arc.mode {arc_mode!r} != series mode {mode!r} "
                f"(one mode per series, XOR per manga_mode_vessels.yaml)"
            )
        if arc_mode == "teacher" and not str(mode_arc.get("vessel") or "").strip():
            errs.append(f"{label}: {aid}: teacher mode_arc requires a genre-native vessel")
        if arc_mode == "music" and not str(mode_arc.get("motif") or "").strip():
            errs.append(f"{label}: {aid}: music mode_arc requires an arc-level motif")

    # ── self_help_topic membership ─────────────────────────────────────
    topic_set = {str(t) for t in (plan.get("self_help_topic_set") or [])}
    if topic_set:
        for arc in arcs:
            topic = str(arc.get("self_help_topic") or "")
            if topic and topic not in topic_set:
                errs.append(
                    f"{label}: {arc.get('arc_id')}: self_help_topic {topic!r} not in "
                    f"self_help_topic_set"
                )

    # ── episode-plan pass integrity (detailed arcs) ────────────────────
    for arc in arcs:
        aid = str(arc.get("arc_id") or "?")
        if str(arc.get("detail_level") or "") != "detailed":
            continue
        eps = [e for e in (arc.get("episodes") or []) if isinstance(e, Mapping)]
        try:
            start, end = int(arc.get("episode_start")), int(arc.get("episode_end"))
        except (TypeError, ValueError):
            continue
        want = list(range(start, end + 1))
        got = sorted(int(e.get("episode")) for e in eps if isinstance(e.get("episode"), int))
        if got != want:
            errs.append(
                f"{label}: {aid}: detail_level=detailed but episode plans cover "
                f"{got or 'nothing'} instead of {start}..{end}"
            )

    # ── migration credit ───────────────────────────────────────────────
    migration = plan.get("migration") or {}
    if isinstance(migration, Mapping) and migration.get("migrated_from_48ep"):
        try:
            window_end = int(migration.get("detailed_window_end") or 48)
        except (TypeError, ValueError):
            window_end = 48
        for start, end, aid in spans:
            if start <= window_end:
                holder = next((a for a in arcs if str(a.get("arc_id")) == aid), None)
                if holder is not None and not str(holder.get("source_arc_ref") or "").strip():
                    errs.append(
                        f"{label}: {aid}: inside migrated 48-ep window (<= ep "
                        f"{window_end}) but missing source_arc_ref credit"
                    )

    # ── stub-marker lint + teacher-name scan on prose ──────────────────
    teacher_pats = list(_TEACHER_NAME_RES)
    tid = str(plan.get("teacher_id") or "").strip().lower()
    if tid in ("ahjan", "sai_ma", "sai_maa", "adi_da"):
        teacher_pats.append(re.compile(rf"\b{re.escape(tid)}\b", re.IGNORECASE))
        teacher_pats.append(
            re.compile(rf"\b{re.escape(tid.replace('_', ' '))}\b", re.IGNORECASE)
        )
    for where, text in _iter_plan_prose(plan):
        m = _STUB_RE.search(text)
        if m:
            errs.append(f"{label}: {where}: unfilled stub marker {m.group(0)!r}")
        for pat in teacher_pats:
            tm = pat.search(text)
            if tm:
                errs.append(
                    f"{label}: {where}: brand teacher named in plan prose "
                    f"({tm.group(0)!r}) — doctrine enters via a genre-native vessel; "
                    f"never name the teacher"
                )
                break

    return errs


def assert_master_plan_valid(path: Path) -> None:
    """Raise SeriesMasterPlanError unless the plan passes the contract."""
    if not path.is_file():
        raise SeriesMasterPlanError(f"no series master plan at {path}")
    plan = _load_yaml(path)
    errors = validate_master_plan(plan, path=path)
    if errors:
        raise SeriesMasterPlanError("; ".join(errors[:10]))


def _discover_plans() -> list[Path]:
    root = REPO_ROOT / MASTER_PLAN_DIR
    if not root.is_dir():
        return []
    return [
        p
        for p in sorted(root.rglob("*.master_plan.yaml"))
        if REWORK_INPUTS_SEGMENT not in p.parts
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan", type=Path, help="validate a single master plan file")
    ap.add_argument("--base", help="git base ref for changed-file mode")
    ap.add_argument("--head", default="HEAD", help="git head ref for changed-file mode")
    args = ap.parse_args(argv)

    if args.plan:
        targets = [args.plan]
    elif args.base:
        changed = changed_paths(args.base, args.head, repo_root=REPO_ROOT)
        targets = [
            REPO_ROOT / c
            for c in changed
            if c.startswith(MASTER_PLAN_DIR + "/")
            and c.endswith(".master_plan.yaml")
            and REWORK_INPUTS_SEGMENT not in Path(c).parts
            and (REPO_ROOT / c).is_file()
        ]
    else:
        targets = _discover_plans()

    if not targets:
        print("check_manga_series_master_plan: no master plans in scope; PASS")
        return 0

    failures = 0
    for path in targets:
        try:
            plan = _load_yaml(path)
        except Exception as e:
            print(f"FAIL {path}: {e}", file=sys.stderr)
            failures += 1
            continue
        errors = validate_master_plan(plan, path=path)
        if errors:
            failures += 1
            for err in errors:
                print(f"FAIL {err}", file=sys.stderr)
        else:
            arcs = len(plan.get("arcs") or [])
            print(
                f"PASS {path.relative_to(REPO_ROOT) if path.is_absolute() else path} "
                f"({arcs} arcs, horizon {plan.get('episode_horizon')}, "
                f"family {plan.get('pacing_family')})"
            )
    if failures:
        print(
            f"check_manga_series_master_plan: {failures} plan(s) FAILED",
            file=sys.stderr,
        )
        return 1
    print(f"check_manga_series_master_plan: {len(targets)} plan(s) PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
