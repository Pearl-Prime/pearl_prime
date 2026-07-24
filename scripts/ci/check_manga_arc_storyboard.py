#!/usr/bin/env python3
"""Arc storyboard gate — no production visual without story_move + visual_proof.

Authority: docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md
Schema: schemas/manga/arc_storyboard_plan.schema.json

Blocks the "standing around talking" failure mode: panels that show faces /
dialogue without a world or relationship change the next panel depends on.

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py \\
        --arc-plan artifacts/manga/arc_storyboards/<series>/ep_001.arc_storyboard.yaml
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py \\
        --base origin/main --head HEAD

Exit: 0 ok; 1 violation (named reason).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

REPO_ROOT = repo_root_from_script(Path(__file__))
ARC_DIR = "artifacts/manga/arc_storyboards"
CHAPTER_DIR = "artifacts/manga/chapter_scripts"
SCENE_TEMPLATES_DIR = REPO_ROOT / "config" / "manga" / "genre_scene_templates"
SCHEMA_PATH = REPO_ROOT / "schemas" / "manga" / "arc_storyboard_plan.schema.json"

_FACE_ONLY_RE = re.compile(
    r"\b(face[_\s-]?reaction[_\s-]?only|talking[_\s-]?head|same[_\s-]?face\s*cu|"
    r"close[_\s-]?up\s*(on\s*)?(jaw|lips|eyes|face|mouth)|reaction\s*shot\s*only)\b",
    re.IGNORECASE,
)
_NOOP_MOVE_RE = re.compile(
    r"^(none|n/?a|null|-|stand\s*around|sit\s*(and|&)\s*talk|talking|listening\s*only|"
    r"show\s*face|face\s*only|no\s*change|unchanged)\.?$",
    re.IGNORECASE,
)
_MAX_CONSECUTIVE_FACE_ONLY = 2


class ArcStoryboardError(Exception):
    """Raised when an arc plan or linked chapter fails the contract."""


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise ArcStoryboardError(f"PyYAML required to load {path}")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ArcStoryboardError(f"{path}: expected mapping root")
    return data


def _required_story_functions(genre_id: str) -> list[str]:
    path = SCENE_TEMPLATES_DIR / f"{genre_id}.yaml"
    if not path.is_file():
        return []
    if yaml is None:
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    planning = data.get("story_scene_planning") or {}
    req = planning.get("required_story_functions_per_story") or []
    return [str(x) for x in req if str(x).strip()]


def _is_face_only(visual_proof: str) -> bool:
    return bool(_FACE_ONLY_RE.search(visual_proof or ""))


def _is_noop_move(story_move: str) -> bool:
    return bool(_NOOP_MOVE_RE.match((story_move or "").strip()))


def validate_arc_plan(plan: Mapping[str, Any], *, path: Path | None = None) -> list[str]:
    """Return list of failure reasons (empty = PASS)."""
    label = str(path) if path else "<arc_plan>"
    errs: list[str] = []

    if plan.get("artifact_type") != "arc_storyboard_plan":
        errs.append(f"{label}: artifact_type must be arc_storyboard_plan")
    for key in (
        "series_id",
        "chapter_id",
        "genre_id",
        "logline",
        "stakes_now",
        "stakes_end",
        "genre_cadence",
        "page_turn_promises",
        "panels",
        "acceptance_layer",
    ):
        if not plan.get(key):
            errs.append(f"{label}: missing required field {key}")

    logline = str(plan.get("logline") or "")
    if logline and len(logline.strip()) < 24:
        errs.append(f"{label}: logline too short (need external-force sentence)")

    panels = plan.get("panels") or []
    if not isinstance(panels, list) or len(panels) < 6:
        errs.append(f"{label}: need ≥6 panels in arc plan")
        return errs

    face_streak = 0
    for i, panel in enumerate(panels):
        if not isinstance(panel, dict):
            errs.append(f"{label}: panel[{i}] not a mapping")
            continue
        pid = panel.get("panel_id") or f"idx{i}"
        move = str(panel.get("story_move") or "").strip()
        proof = str(panel.get("visual_proof") or "").strip()
        delta = str(panel.get("information_delta") or "").strip()
        if len(move) < 8:
            errs.append(f"{label}:{pid}: story_move missing/too short")
        if len(proof) < 8:
            errs.append(f"{label}:{pid}: visual_proof missing/too short")
        if len(delta) < 4:
            errs.append(f"{label}:{pid}: information_delta missing/too short")

        face_only = _is_face_only(proof) or "face_reaction_only" in (
            panel.get("forbidden") or []
        )
        if face_only:
            face_streak += 1
            if face_streak > _MAX_CONSECUTIVE_FACE_ONLY:
                errs.append(
                    f"{label}:{pid}: talking-head density — >{_MAX_CONSECUTIVE_FACE_ONLY} "
                    "consecutive face-only visual_proof panels"
                )
        else:
            face_streak = 0

        # Dialogue allowed only if move is real (silence breaths exempt when not noop)
        silence = bool(panel.get("silence"))
        if _is_noop_move(move) and face_only and not silence:
            errs.append(
                f"{label}:{pid}: illegal face-only + noop story_move "
                "(standing/talking without arc motion)"
            )
        if _is_noop_move(move) and not silence:
            errs.append(f"{label}:{pid}: story_move is a no-op synonym")

    genre_id = str(plan.get("genre_id") or "")
    required = _required_story_functions(genre_id)
    if required:
        cadence = [str(x) for x in (plan.get("genre_cadence") or [])]
        panel_fns = {
            str(p.get("story_function"))
            for p in panels
            if isinstance(p, dict) and p.get("story_function")
        }
        covered = set(cadence) | panel_fns
        missing = [fn for fn in required if fn not in covered]
        if missing:
            errs.append(
                f"{label}: genre {genre_id} missing required story functions: "
                + ", ".join(missing)
            )

    layer = str(plan.get("acceptance_layer") or "")
    if layer in {"proven_at_bar", "bestseller"}:
        errs.append(
            f"{label}: acceptance_layer={layer!r} forbidden on arc plan alone "
            "(use authored_candidate / structurally_clear)"
        )

    return errs


def assert_arc_plan(path: Path) -> None:
    errs = validate_arc_plan(_load(path), path=path)
    if errs:
        raise ArcStoryboardError("; ".join(errs))


def _arc_plan_for_series_chapter(series_id: str, chapter_id: str) -> Path | None:
    cand = REPO_ROOT / ARC_DIR / series_id / f"{chapter_id}.arc_storyboard.yaml"
    if cand.is_file():
        return cand
    # also accept .json
    cand_j = cand.with_suffix(".json")
    return cand_j if cand_j.is_file() else None


def _chapter_requires_arc(chapter_path: Path) -> tuple[bool, str | None, str | None]:
    """Return (requires, series_id, chapter_id) for chapter scripts with governed genres."""
    try:
        data = _load(chapter_path)
    except Exception:
        return False, None, None
    series_id = str(data.get("series_id") or chapter_path.parent.name)
    chapter_id = str(data.get("chapter_id") or chapter_path.stem)
    genre = str(
        data.get("genre")
        or data.get("genre_id")
        or data.get("genre_family")
        or ""
    )
    # Infer mecha from series path / craft notes when genre unset
    if not genre and "mecha" in series_id.lower():
        genre = "mecha"
    notes = str(data.get("craft_notes") or data.get("notes") or "").lower()
    if not genre and "mecha" in notes:
        genre = "mecha"
    if not genre:
        # Look for genre in scene palette / engine tags
        if "mecha" in str(data).lower()[:2000]:
            genre = "mecha"
    if genre and _required_story_functions(genre):
        return True, series_id, chapter_id
    # Explicit ref always requires validation of the plan
    if data.get("arc_storyboard_ref"):
        return True, series_id, chapter_id
    return False, series_id, chapter_id


def check_chapter_has_arc(chapter_path: Path) -> list[str]:
    requires, series_id, chapter_id = _chapter_requires_arc(chapter_path)
    if not requires:
        return []
    data = _load(chapter_path)
    ref = data.get("arc_storyboard_ref")
    plan_path: Path | None = None
    if ref:
        plan_path = Path(str(ref))
        if not plan_path.is_absolute():
            plan_path = REPO_ROOT / plan_path
    if plan_path is None or not plan_path.is_file():
        if series_id and chapter_id:
            plan_path = _arc_plan_for_series_chapter(series_id, chapter_id)
    if plan_path is None or not plan_path.is_file():
        return [
            f"{chapter_path}: governed chapter missing arc storyboard plan "
            f"(expected {ARC_DIR}/{series_id}/{chapter_id}.arc_storyboard.yaml "
            "or arc_storyboard_ref)"
        ]
    return validate_arc_plan(_load(plan_path), path=plan_path)


def _iter_arc_plans(root: Path) -> list[Path]:
    base = root / ARC_DIR
    if not base.is_dir():
        return []
    out: list[Path] = []
    for p in sorted(base.rglob("*.arc_storyboard.yaml")):
        out.append(p)
    for p in sorted(base.rglob("*.arc_storyboard.json")):
        out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    global REPO_ROOT, SCENE_TEMPLATES_DIR, SCHEMA_PATH

    ap = argparse.ArgumentParser(description="Manga arc storyboard contract gate")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--arc-plan", type=Path, default=None)
    ap.add_argument("--chapter-script", type=Path, default=None)
    ap.add_argument("--base", default=None)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument(
        "--all-plans",
        action="store_true",
        help="validate every arc_storyboard under artifacts/manga/arc_storyboards/",
    )
    args = ap.parse_args(argv)

    REPO_ROOT = args.repo_root.resolve()
    SCENE_TEMPLATES_DIR = REPO_ROOT / "config" / "manga" / "genre_scene_templates"
    SCHEMA_PATH = REPO_ROOT / "schemas" / "manga" / "arc_storyboard_plan.schema.json"

    failures: list[str] = []

    if args.arc_plan:
        try:
            assert_arc_plan(args.arc_plan)
            print(f"PASS {args.arc_plan}")
            return 0
        except ArcStoryboardError as e:
            print(f"FAIL {e}", file=sys.stderr)
            return 1

    if args.chapter_script:
        failures.extend(check_chapter_has_arc(args.chapter_script))
        if failures:
            for f in failures:
                print(f"FAIL {f}", file=sys.stderr)
            return 1
        print(f"PASS {args.chapter_script}")
        return 0

    paths: list[Path] = []
    if args.base:
        try:
            changed = changed_paths(args.base, args.head, repo_root=REPO_ROOT)
        except Exception as e:
            print(f"WARN could not diff {args.base}...{args.head}: {e}", file=sys.stderr)
            changed = []
        for rel in changed:
            p = REPO_ROOT / rel
            if not p.is_file():
                continue
            if ARC_DIR in rel and (
                rel.endswith(".arc_storyboard.yaml")
                or rel.endswith(".arc_storyboard.json")
            ):
                paths.append(p)
            if CHAPTER_DIR in rel and rel.endswith((".yaml", ".yml", ".json")):
                failures.extend(check_chapter_has_arc(p))
    elif args.all_plans:
        paths = _iter_arc_plans(REPO_ROOT)
    else:
        # Default CI: all arc plans + any chapter that already declares a ref
        paths = _iter_arc_plans(REPO_ROOT)
        chap_root = REPO_ROOT / CHAPTER_DIR
        if chap_root.is_dir():
            for p in sorted(chap_root.rglob("ep_*.yaml")):
                # Only enforce when sibling arc plan exists OR explicit ref —
                # avoids mass-failing legacy corpus on first land.
                try:
                    data = _load(p)
                except Exception:
                    continue
                if data.get("arc_storyboard_ref") or _arc_plan_for_series_chapter(
                    str(data.get("series_id") or p.parent.name),
                    str(data.get("chapter_id") or p.stem),
                ):
                    failures.extend(check_chapter_has_arc(p))

    for p in paths:
        failures.extend(validate_arc_plan(_load(p), path=p))

    if failures:
        for f in failures:
            print(f"FAIL {f}", file=sys.stderr)
        print(f"arc_storyboard: {len(failures)} failure(s)", file=sys.stderr)
        return 1

    print(f"PASS arc_storyboard plans={len(paths)} linked_checks_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
