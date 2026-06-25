#!/usr/bin/env python3
"""
Full catalog orchestrator for legacy teacher-matrix runs and bulk brand-target planning.

Sequence:
  1. Brand/teacher portfolio allocation (teacher_portfolio_planner)
  2. BookSpec planning per allocation (catalog_planner)
  3. Per-book compile Stage 1→2→3 (run_pipeline)
  4. Wave selection from compiled candidates (wave_orchestrator)

Use --brand and --max-books for "First 10 Books" evaluation (one brand, 10 books, no wave selection).
Use --books-per-brand with --brand or --all-brands-from for large deterministic brand-target batches
(for example: 37 brands × 800 books).
See docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md and docs/CREATIVE_QUALITY_VALIDATION_CHECKLIST.md.

Usage:
  python3 scripts/generate_full_catalog.py --max-books 10 --brand stillness_press --skip-wave-selection
  python3 scripts/generate_full_catalog.py --max-books 120 --candidates-dir artifacts/full_catalog/candidates --out-wave artifacts/waves/wave_selected.txt
  python3 scripts/generate_full_catalog.py --all-brands-from config/manga/canonical_brand_list.yaml --books-per-brand 800 --plan-only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
CONFIG_LOCALIZATION = REPO_ROOT / "config" / "localization"
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"
WAVE_ORCHESTRATOR = REPO_ROOT / "phoenix_v4" / "planning" / "wave_orchestrator.py"
_ARC_COMBO_CACHE = None


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _load_brand_ids_from_yaml(path: Path) -> list[str]:
    data = _load_yaml(path)
    brands = data.get("brands") if isinstance(data, dict) else None
    if isinstance(brands, dict):
        brand_ids = [str(brand_id) for brand_id in brands.keys()]
    elif isinstance(brands, list):
        brand_ids = [str(brand_id) for brand_id in brands]
    else:
        raise ValueError(f"{path} must contain a top-level 'brands' mapping or list")
    if not brand_ids:
        raise ValueError(f"{path} does not contain any brand ids")
    expected = data.get("total_brands") if isinstance(data, dict) else None
    if expected is not None and int(expected) != len(brand_ids):
        raise ValueError(
            f"brand-count drift in {path}: found {len(brand_ids)} brands but total_brands={expected}"
        )
    return brand_ids


def _stable_int_seed(seed_text: str) -> int:
    return int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:8], 16)


def _teacher_id_for_brand(brand_id: str, matrix_brands: dict[str, dict]) -> str:
    cfg = matrix_brands.get(brand_id) or {}
    teachers = cfg.get("teachers") or []
    return cfg.get("primary_teacher") or (teachers[0] if teachers else "default_teacher")


def _available_arc_persona_topic_pairs() -> set[tuple[str, str]]:
    global _ARC_COMBO_CACHE
    if _ARC_COMBO_CACHE is not None:
        return _ARC_COMBO_CACHE
    pairs: set[tuple[str, str]] = set()
    if not ARCS_ROOT.exists():
        _ARC_COMBO_CACHE = pairs
        return pairs
    for arc_path in ARCS_ROOT.glob("*.yaml"):
        parts = arc_path.stem.split("__")
        if len(parts) < 4:
            continue
        topic_id = parts[-3]
        persona_id = "__".join(parts[:-3])
        pairs.add((persona_id, topic_id))
    _ARC_COMBO_CACHE = pairs
    return pairs


def _collect_compileable_brand_specs(
    planner,
    *,
    brand_id: str,
    count: int,
    seed: str,
    teacher_id: str,
) -> list:
    available_pairs = _available_arc_persona_topic_pairs()
    if not available_pairs:
        raise ValueError(f"No master arcs found under {ARCS_ROOT}")

    collected = []
    seen: set[tuple[str, str, str | None, int | None, str]] = set()
    batch_size = max(count * 3, 64)
    for attempt in range(8):
        generated = planner.generate_for_brand(
            brand_id,
            batch_size,
            seed=f"{seed}:attempt:{attempt}",
            teacher_id=teacher_id,
            repo_root=REPO_ROOT,
        )
        for spec in generated:
            if (spec.persona_id, spec.topic_id) not in available_pairs:
                continue
            key = (
                spec.persona_id,
                spec.topic_id,
                spec.series_id,
                spec.installment_number,
                spec.angle_id,
            )
            if key in seen:
                continue
            seen.add(key)
            collected.append(spec)
            if len(collected) >= count:
                return collected

    raise ValueError(
        f"Could only resolve {len(collected)}/{count} compileable books for brand {brand_id}. "
        "Add more matching master arcs or adjust the planning registry."
    )


def _run_compile_command(
    cmd: list[str],
    out_path: Path,
    *,
    timeout_seconds: int,
    resume: bool,
) -> tuple[bool, bool, str]:
    if resume and out_path.exists() and out_path.stat().st_size > 0:
        return True, True, ""
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath else str(REPO_ROOT)
    )
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return False, False, f"TIMEOUT after {timeout_seconds}s"
    except Exception as exc:
        return False, False, f"EXCEPTION: {exc}"

    if result.returncode == 0:
        return True, False, ""

    stderr_tail = (result.stderr or "")[-500:]
    stdout_tail = (result.stdout or "")[-200:]
    error = stderr_tail or stdout_tail or f"non-zero exit {result.returncode}"
    return False, False, error


def _validate_brand_locale_matrix(
    brand_matrix_path: Path,
    extension_path: Path,
    locale_registry_path: Path,
) -> list[str]:
    """Ensure every brand in the matrix has valid locale/territory in extension and registry. Returns list of errors."""
    errors = []
    matrix = _load_yaml(brand_matrix_path)
    extension = _load_yaml(extension_path)
    locale_reg = _load_yaml(locale_registry_path)
    brands_matrix = set((matrix.get("brands") or {}).keys())
    brands_ext = (extension.get("brands") or {})
    locales_valid = set((locale_reg.get("locales") or {}).keys())

    for bid in brands_matrix:
        ext_cfg = brands_ext.get(bid)
        if not ext_cfg:
            errors.append(f"Brand '{bid}' in matrix not found in brand_registry_locale_extension.yaml")
            continue
        loc = ext_cfg.get("locale")
        territory = ext_cfg.get("territory")
        if not loc:
            errors.append(f"Brand '{bid}' has no 'locale' in locale extension")
        elif loc not in locales_valid:
            errors.append(f"Brand '{bid}' locale '{loc}' not in locale_registry.yaml")
        if territory is None or territory == "":
            errors.append(f"Brand '{bid}' has no 'territory' in locale extension")
    return errors


# Short formats (fewer chapters) — prefer when teacher×topic×persona fit is weak (TEACHER_UNIVERSAL_AND_SCORING_SPEC).
PREFER_SHORT_FORMAT_IDS = ("F001", "F002", "F003")


def _format_id_from_arc_path(arc_path: Path) -> str:
    """Extract format ID from arc filename, e.g. persona__topic__engine__F006.yaml -> F006."""
    name = arc_path.stem
    parts = name.split("__")
    return parts[-1] if len(parts) >= 4 else ""


def _resolve_arc_for_book(
    persona_id: str,
    topic_id: str,
    prefer_short_format: bool = False,
) -> Path | None:
    """Return path to an existing master arc for (persona, topic), or None.
    When prefer_short_format is True (weak fit), prefer arcs with F001/F002/F003 over F006 etc.
    """
    if not ARCS_ROOT.exists():
        return None
    pattern = f"{persona_id}__{topic_id}__*.yaml"
    matches = list(ARCS_ROOT.glob(pattern))
    if not matches:
        return None
    if prefer_short_format:
        # Sort so short formats come first; then take first match
        def key(p: Path) -> tuple[int, str]:
            fmt = _format_id_from_arc_path(p)
            return (0 if fmt in PREFER_SHORT_FORMAT_IDS else 1, p.name)

        matches = sorted(matches, key=key)
    else:
        matches = sorted(matches)
    return matches[0]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Orchestrate full catalog: portfolio → BookSpec → compile → wave selection",
    )
    ap.add_argument(
        "--max-books",
        type=int,
        default=60,
        help="Max books to plan and compile (default 60). Use 10 for First-10 evaluation.",
    )
    ap.add_argument(
        "--brand",
        default=None,
        help="Restrict to one brand (e.g. stillness_press). Omit for all brands.",
    )
    ap.add_argument(
        "--books-per-brand",
        type=int,
        default=None,
        help=(
            "Generate exactly N BookSpecs per target brand. Requires --brand or --all-brands-from. "
            "Bypasses teacher round-robin allocation and plans per brand directly."
        ),
    )
    ap.add_argument(
        "--all-brands-from",
        type=Path,
        default=None,
        help=(
            "YAML containing a top-level brands: mapping/list to use as the target brand set "
            "(e.g. config/manga/canonical_brand_list.yaml for the canonical 37-brand list)."
        ),
    )
    ap.add_argument(
        "--seed",
        default="catalog_seed_001",
        help="Seed for allocation and determinism.",
    )
    ap.add_argument(
        "--candidates-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "full_catalog" / "candidates",
        help="Directory to write compiled plan JSONs (default: artifacts/full_catalog/candidates).",
    )
    ap.add_argument(
        "--skip-wave-selection",
        action="store_true",
        help="Do not run wave_orchestrator (e.g. for First 10 Books evaluation).",
    )
    ap.add_argument(
        "--wave-size",
        type=int,
        default=60,
        help="Target wave size when running wave selection (default 60).",
    )
    ap.add_argument(
        "--out-wave",
        type=Path,
        default=REPO_ROOT / "artifacts" / "waves" / "wave_selected.txt",
        help="Output path for wave selection (one plan path per line).",
    )
    ap.add_argument(
        "--generate-freebies",
        action="store_true",
        help="Generate freebie HTML during compile (default: off for catalog speed).",
    )
    ap.add_argument(
        "--plan-only",
        action="store_true",
        help="Only allocate and produce BookSpecs; do not run compile/assembly or wave selection.",
    )
    ap.add_argument(
        "--locale-group",
        default=None,
        help="Locale group name from locale_registry.yaml (e.g. chinese_all). Resolves to list of locales; atoms root per book = atoms/<locale>.",
    )
    ap.add_argument(
        "--brand-matrix",
        type=Path,
        default=None,
        help="Path to brand/teacher matrix YAML (default: config/catalog_planning/brand_teacher_matrix.yaml).",
    )
    ap.add_argument(
        "--atoms-root",
        default=None,
        help="Atoms root for single-locale run (e.g. atoms/zh-TW). For --locale-group, derived per book from spec.locale.",
    )
    ap.add_argument(
        "--no-teacher-mode",
        action="store_true",
        help="Compile with default_teacher (shared atoms only). Skips teacher exercise pool gate; use for catalog when teacher banks are empty.",
    )
    ap.add_argument(
        "--allow-mixed-atoms-model",
        action="store_true",
        help="Allow wave to mix legacy and cluster atoms_model when using allocation_personas_file (e.g. ZH matrix). Default: assert all cluster.",
    )
    ap.add_argument(
        "--max-parallel",
        type=int,
        default=1,
        help="Compile up to N books in parallel (default 1).",
    )
    ap.add_argument(
        "--compile-timeout-seconds",
        type=int,
        default=300,
        help="Per-book compile timeout in seconds (default 300).",
    )
    ap.add_argument(
        "--resume",
        action="store_true",
        help="Skip compile for candidate JSONs that already exist and are non-empty.",
    )
    args = ap.parse_args()

    if args.books_per_brand is not None and args.books_per_brand <= 0:
        print("--books-per-brand must be > 0", file=sys.stderr)
        return 1
    if args.books_per_brand is not None and not args.brand and args.all_brands_from is None:
        print("--books-per-brand requires --brand or --all-brands-from", file=sys.stderr)
        return 1
    if args.brand and args.all_brands_from is not None:
        print("Use either --brand or --all-brands-from, not both", file=sys.stderr)
        return 1
    if args.max_parallel <= 0:
        print("--max-parallel must be > 0", file=sys.stderr)
        return 1
    if args.compile_timeout_seconds <= 0:
        print("--compile-timeout-seconds must be > 0", file=sys.stderr)
        return 1

    brand_matrix_path = args.brand_matrix
    if args.locale_group or brand_matrix_path:
        ext_path = CONFIG_LOCALIZATION / "brand_registry_locale_extension.yaml"
        loc_reg_path = CONFIG_LOCALIZATION / "locale_registry.yaml"
        matrix_path_for_val = brand_matrix_path or (REPO_ROOT / "config" / "catalog_planning" / "brand_teacher_matrix.yaml")
        if matrix_path_for_val.exists():
            errs = _validate_brand_locale_matrix(matrix_path_for_val, ext_path, loc_reg_path)
            if errs:
                for e in errs:
                    print(e, file=sys.stderr)
                print("Fix brand_registry_locale_extension and locale_registry so every matrix brand has valid locale/territory.", file=sys.stderr)
                return 1

    # --- Step 1: Teacher portfolio allocation ---
    from phoenix_v4.planning.teacher_portfolio_planner import (
        allocate_wave,
        load_brand_matrix,
        load_teacher_topic_persona_scores,
    )
    from phoenix_v4.planning.atoms_model_loader import get_allocation_personas_path

    matrix = load_brand_matrix(brand_matrix_path)
    brands = matrix.get("brands") or {}
    from phoenix_v4.planning.catalog_planner import CatalogPlanner, AtomsModel
    from phoenix_v4.planning.atoms_model_loader import atoms_model_for_persona

    planner = CatalogPlanner()
    specs = []
    prefer_short_for_weak = True
    personas_override = None

    if args.books_per_brand is not None:
        try:
            target_brand_ids = [args.brand] if args.brand else _load_brand_ids_from_yaml(args.all_brands_from)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        total_requested = len(target_brand_ids) * args.books_per_brand
        print(
            f"Brand-target planning: {len(target_brand_ids)} brands × {args.books_per_brand} books per brand = {total_requested} books."
        )
        for brand_index, brand_id in enumerate(target_brand_ids):
            teacher_id = _teacher_id_for_brand(brand_id, brands)
            try:
                brand_specs = _collect_compileable_brand_specs(
                    planner,
                    brand_id=brand_id,
                    count=args.books_per_brand,
                    seed=f"{args.seed}:{brand_index}:{brand_id}",
                    teacher_id=teacher_id,
                )
                for spec in brand_specs:
                    if spec.atoms_model is None:
                        spec.atoms_model = atoms_model_for_persona(spec.persona_id)
                    specs.append((None, spec))
            except Exception as e:
                print(f"Brand planning failed for {brand_id}: {e}", file=sys.stderr)
                continue
    else:
        all_teachers = []
        for b in brands.values():
            all_teachers.extend(b.get("teachers") or [])
        all_teachers = list(dict.fromkeys(all_teachers))  # preserve order, dedupe

        if not all_teachers:
            print("No teachers found in brand matrix. Check config/catalog_planning/brand_teacher_matrix.yaml.", file=sys.stderr)
            return 1

        # When using a custom brand matrix (e.g. ZH), optional allocation persona list from atoms_model.yaml
        personas_override = None
        allocation_path = get_allocation_personas_path()
        if brand_matrix_path and allocation_path and allocation_path.exists():
            data = _load_yaml(allocation_path)
            personas_list = data.get("personas") or data.get("persona_ids") or []
            if isinstance(personas_list, list) and personas_list:
                personas_override = list(personas_list)
                print(f"Using allocation personas from {allocation_path.name} ({len(personas_override)} personas).")

        wave_id = "full_catalog"
        total_to_allocate = args.max_books
        if args.brand:
            # Allocate extra so we have enough after filtering to one brand
            total_to_allocate = max(args.max_books * 4, 50)
        allocations = allocate_wave(
            wave_id=wave_id,
            teachers=all_teachers,
            total_books=total_to_allocate,
            seed=args.seed,
            brand_matrix_path=brand_matrix_path,
            personas_override=personas_override,
        )

        if args.brand:
            allocations = [a for a in allocations if a.brand_id == args.brand][: args.max_books]
            if not allocations:
                print(f"No allocations for brand '{args.brand}'.", file=sys.stderr)
                return 1
            print(f"Filtered to brand {args.brand}: {len(allocations)} books.")
        else:
            print(f"Portfolio allocated: {len(allocations)} books across brands.")

        # Weak-fit cap: at most N books per (teacher, topic, persona) when score_band == "weak"
        scores_cfg = load_teacher_topic_persona_scores()
        weak_max = (scores_cfg or {}).get("weak_fit_max_books_per_triple", 1)
        prefer_short_for_weak = (scores_cfg or {}).get("weak_fit_prefer_shorter_format", True)
        if weak_max is not None and weak_max >= 0:
            weak_triple_count: dict[tuple[str, str, str], int] = {}
            kept = []
            for a in allocations:
                key = (a.teacher_id, a.topic_id, a.persona_id)
                if getattr(a, "score_band", None) == "weak":
                    n = weak_triple_count.get(key, 0)
                    if n >= weak_max:
                        continue
                    weak_triple_count[key] = n + 1
                kept.append(a)
            if len(kept) < len(allocations):
                dropped = len(allocations) - len(kept)
                print(
                    f"Weak-fit cap: kept {len(kept)} allocations (dropped {dropped} over weak_fit_max_books_per_triple={weak_max})."
                )
                allocations = kept

        # --- Step 2: BookSpec per allocation ---
        for i, alloc in enumerate(allocations):
            try:
                atoms_model = atoms_model_for_persona(alloc.persona_id)
                spec = planner.produce_single(
                    topic_id=alloc.topic_id,
                    persona_id=alloc.persona_id,
                    teacher_id=alloc.teacher_id,
                    brand_id=alloc.brand_id,
                    seed=f"{args.seed}:{i}:{alloc.position_in_wave}",
                    teacher_mode=(alloc.teacher_id and alloc.teacher_id != "default_teacher"),
                    atoms_model=atoms_model,
                )
                specs.append((alloc, spec))
            except Exception as e:
                print(f"BookSpec failed for {alloc.teacher_id}/{alloc.topic_id}/{alloc.persona_id}: {e}", file=sys.stderr)
                continue

    if not specs:
        print("No BookSpecs produced.", file=sys.stderr)
        return 1

    # Mixed-models gate: when using allocation_personas_file (e.g. ZH matrix), expect all cluster unless --allow-mixed-atoms-model
    if personas_override is not None and not args.allow_mixed_atoms_model:
        non_cluster = [(a, s) for a, s in specs if s.atoms_model != AtomsModel.CLUSTER]
        if non_cluster:
            print(
                "Atoms model gate: allocation used cluster persona list but some specs are legacy. "
                "Use --allow-mixed-atoms-model to allow, or ensure allocation_personas_file contains cluster-only personas.",
                file=sys.stderr,
            )
            for alloc, spec in non_cluster[:5]:
                print(f"  {spec.persona_id} -> {spec.atoms_model.value}", file=sys.stderr)
            if len(non_cluster) > 5:
                print(f"  ... and {len(non_cluster) - 5} more.", file=sys.stderr)
            return 1

    # Cap to requested max_books in legacy allocation mode
    if args.books_per_brand is None and len(specs) > args.max_books:
        specs = specs[: args.max_books]
    print(f"BookSpecs produced: {len(specs)}.")

    # Diversity guard: max share per topic/persona when using locale-group or custom brand matrix
    if (args.locale_group or brand_matrix_path) and specs:
        guard_path = REPO_ROOT / "config" / "catalog_planning" / "diversity_guards.yaml"
        if guard_path.exists():
            guard_cfg = _load_yaml(guard_path)
            max_topic = guard_cfg.get("max_share_per_topic")
            max_persona = guard_cfg.get("max_share_per_persona")
            fail_on = guard_cfg.get("fail_on_violation", True)
            n = len(specs)
            if n and (max_topic is not None or max_persona is not None):
                from collections import Counter
                topic_ct = Counter(spec.topic_id for _, spec in specs)
                persona_ct = Counter(spec.persona_id for _, spec in specs)
                violations = []
                for tid, c in topic_ct.items():
                    if max_topic is not None and c / n > max_topic:
                        violations.append(f"topic {tid}: {c}/{n} ({100*c/n:.0f}%) > {100*max_topic:.0f}%")
                for pid, c in persona_ct.items():
                    if max_persona is not None and c / n > max_persona:
                        violations.append(f"persona {pid}: {c}/{n} ({100*c/n:.0f}%) > {100*max_persona:.0f}%")
                if violations:
                    for v in violations:
                        print(v, file=sys.stderr)
                    if fail_on:
                        print("Diversity guard failed. Adjust allocation or config/catalog_planning/diversity_guards.yaml", file=sys.stderr)
                        return 1
                    print("Diversity guard warning (fail_on_violation=false).", file=sys.stderr)

    if args.plan_only:
        args.candidates_dir.mkdir(parents=True, exist_ok=True)
        for i, (alloc, spec) in enumerate(specs):
            out_path = args.candidates_dir / f"book_{i:04d}_{spec.topic_id}_{spec.persona_id}.spec.json"
            out_path.write_text(
                json.dumps(spec.to_dict(), indent=2),
                encoding="utf-8",
            )
        print(f"Wrote {len(specs)} BookSpecs to {args.candidates_dir} (plan-only; no assemble).")
        return 0

    # --- Step 3: Compile each book via run_pipeline ---
    args.candidates_dir.mkdir(parents=True, exist_ok=True)
    freebies_flag = "--generate-freebies" if args.generate_freebies else "--no-generate-freebies"

    failed = 0
    compile_jobs: list[tuple[int, object | None, object, Path, list[str]]] = []
    for i, (alloc, spec) in enumerate(specs):
        prefer_short = prefer_short_for_weak and getattr(alloc, "score_band", None) == "weak"
        arc_path = _resolve_arc_for_book(spec.persona_id, spec.topic_id, prefer_short_format=prefer_short)
        if not arc_path or not arc_path.exists():
            print(f"Skip (no arc): {spec.persona_id} / {spec.topic_id}", file=sys.stderr)
            failed += 1
            continue

        out_path = args.candidates_dir / f"book_{i:04d}_{spec.topic_id}_{spec.persona_id}.json"
        atoms_root = None
        if args.locale_group and getattr(spec, "locale", None):
            atoms_root = str(REPO_ROOT / "atoms" / spec.locale)
        elif args.atoms_root:
            atoms_root = args.atoms_root
        elif spec.atoms_model == AtomsModel.CLUSTER:
            atoms_root = str(REPO_ROOT / "atoms")
        teacher_id = "default_teacher" if args.no_teacher_mode else (spec.teacher_id or "default_teacher")
        cmd = [
            sys.executable,
            str(RUN_PIPELINE),
            "--topic", spec.topic_id,
            "--persona", spec.persona_id,
            "--arc", str(arc_path),
            "--teacher", teacher_id,
            "--seed", spec.seed,
            "--out", str(out_path),
            "--atoms-model", spec.atoms_model.value,
            "--no-job-check",
            freebies_flag,
            "--no-update-freebie-index",
        ]
        if atoms_root:
            cmd += ["--atoms-root", atoms_root]
        if spec.series_id:
            cmd += ["--series", spec.series_id]
        if spec.installment_number is not None:
            cmd += ["--installment", str(spec.installment_number)]
        if spec.angle_id:
            cmd += ["--angle", spec.angle_id]

        compile_jobs.append((i, alloc, spec, out_path, cmd))

    compiled_count = 0
    reused_existing = 0
    total_jobs = len(compile_jobs)
    if args.max_parallel == 1:
        for completed, (_i, _alloc, spec, out_path, cmd) in enumerate(compile_jobs, start=1):
            ok, reused, error = _run_compile_command(
                cmd,
                out_path,
                timeout_seconds=args.compile_timeout_seconds,
                resume=args.resume,
            )
            if ok:
                compiled_count += 1
                if reused:
                    reused_existing += 1
                status = "REUSED" if reused else "OK"
                print(f"Compile {completed}/{total_jobs}: {spec.brand_id} · {spec.topic_id} × {spec.persona_id} [{status}]")
            else:
                failed += 1
                print(f"Compile {completed}/{total_jobs}: {spec.brand_id} · {spec.topic_id} × {spec.persona_id} [FAIL]", file=sys.stderr)
                print(f"  FAILED: {error}", file=sys.stderr)
    else:
        with ThreadPoolExecutor(max_workers=args.max_parallel) as executor:
            future_map = {
                executor.submit(
                    _run_compile_command,
                    cmd,
                    out_path,
                    timeout_seconds=args.compile_timeout_seconds,
                    resume=args.resume,
                ): (spec, out_path)
                for _i, _alloc, spec, out_path, cmd in compile_jobs
            }
            completed = 0
            for future in as_completed(future_map):
                completed += 1
                spec, _out_path = future_map[future]
                try:
                    ok, reused, error = future.result()
                except Exception as exc:
                    ok, reused, error = False, False, f"WORKER_EXCEPTION: {exc}"
                if ok:
                    compiled_count += 1
                    if reused:
                        reused_existing += 1
                    status = "REUSED" if reused else "OK"
                    print(f"Compile {completed}/{total_jobs}: {spec.brand_id} · {spec.topic_id} × {spec.persona_id} [{status}]")
                else:
                    failed += 1
                    print(f"Compile {completed}/{total_jobs}: {spec.brand_id} · {spec.topic_id} × {spec.persona_id} [FAIL]", file=sys.stderr)
                    print(f"  FAILED: {error}", file=sys.stderr)

    print(f"Compiled: {compiled_count} books ({failed} failed, {reused_existing} reused existing).")

    if args.skip_wave_selection:
        print("Wave selection skipped (--skip-wave-selection).")
        return 0 if failed == 0 else 1

    if compiled_count == 0:
        print("No compiled plans; cannot run wave selection.", file=sys.stderr)
        return 1

    # --- Step 4: Wave selection ---
    out_wave = Path(args.out_wave)
    out_wave.parent.mkdir(parents=True, exist_ok=True)
    cmd_wave = [
        sys.executable,
        str(WAVE_ORCHESTRATOR),
        "--candidates-dir", str(args.candidates_dir),
        "--wave-size", str(min(args.wave_size, compiled_count)),
        "--seed", str(_stable_int_seed(args.seed)),
        "--out", str(out_wave),
    ]
    print("Running wave orchestrator...")
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath else str(REPO_ROOT)
    )
    r = subprocess.run(cmd_wave, cwd=str(REPO_ROOT), env=env, timeout=120)
    if r.returncode != 0:
        print("Wave orchestrator failed.", file=sys.stderr)
        return 1
    print(f"Wave written: {out_wave}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
