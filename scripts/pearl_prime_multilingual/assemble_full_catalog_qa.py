#!/usr/bin/env python3
"""
Pearl_Publisher — Multilingual Full-Catalog QA Assembly.

Locale-parameterized generalization of scripts/pearl_prime_en_us/assemble_first_100_qa.py.
Supports en-US (baseline), zh-TW, ja-JP, zh-CN, and any other locale in
config/localization/locale_registry.yaml.

Pipeline per locale:
  1. Allocate BookSpecs via scripts/generate_full_catalog.py --plan-only.
     Over-allocate to absorb arc-gap filtering.
     For CJK locales, pass --brand-matrix config/catalog_planning/brand_teacher_matrix_zh.yaml
     and --locale-group {chinese_all | ...} as appropriate.
  2. Filter specs where no master_arc exists for (persona × topic), or where
     the selected arc's engine isn't in the teacher's allowed_engines.
  3. Assemble first N via scripts/run_pipeline.py with:
       --pipeline-mode spine
       --locale <locale>            (loads locale-specific atoms for CJK)
       --render-book --render-dir <per-book>
       --quality-profile <profile>  (default draft — render regardless of gates)
       --no-job-check --no-generate-freebies
  4. Emit per-book run.log + quality_summary.json, aggregate assembly_summary.json.

Output tree:
  artifacts/pearl_prime_<locale_slug>/full_catalog_qa/
    specs/book_NNNN_topic_persona.spec.json
    filter_report.json
    renders/book_NNNN_topic_persona/...
    assembly_summary.json

Usage:
  # en-US, 200 books, draft profile (defaults)
  python3 scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py --locale en-US --target 200

  # zh-TW, 100 books
  python3 scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py \
      --locale zh-TW --target 100 \
      --brand-matrix config/catalog_planning/brand_teacher_matrix_zh.yaml

  # zh-CN, smaller scope (40% atom coverage → expect fallbacks)
  python3 scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py \
      --locale zh-CN --target 50 \
      --brand-matrix config/catalog_planning/brand_teacher_matrix_zh.yaml
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
GENERATE_FULL_CATALOG = REPO_ROOT / "scripts" / "generate_full_catalog.py"
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"
TEACHER_MATRIX = REPO_ROOT / "config" / "catalog_planning" / "teacher_persona_matrix.yaml"

# Per-book timeout — spine+render+quality typically runs 10s-3min; 8 min is safety margin.
BOOK_TIMEOUT_SEC = 480


# -----------------------------------------------------------------------------
# Teacher × engine compatibility (mirrors scripts/pearl_prime_en_us/assemble_first_100_qa.py)
# -----------------------------------------------------------------------------

_TEACHER_ENGINES: dict[str, set[str]] | None = None


def load_teacher_allowed_engines() -> dict[str, set[str]]:
    import yaml
    data = yaml.safe_load(TEACHER_MATRIX.read_text()) or {}
    out: dict[str, set[str]] = {}
    for teacher_id, cfg in (data.get("teachers") or {}).items():
        out[teacher_id] = set(cfg.get("allowed_engines") or [])
    return out


def teacher_allowed_engines(teacher_id: str) -> set[str]:
    global _TEACHER_ENGINES
    if _TEACHER_ENGINES is None:
        _TEACHER_ENGINES = load_teacher_allowed_engines()
    return _TEACHER_ENGINES.get(teacher_id, set())


def engine_from_arc_path(arc_path: Path) -> str | None:
    parts = arc_path.stem.split("__")
    return parts[2] if len(parts) >= 3 else None


def pick_compatible_arc(persona_id: str, topic_id: str, teacher_id: str) -> tuple[Path | None, str | None]:
    matches = sorted(ARCS_ROOT.glob(f"{persona_id}__{topic_id}__*.yaml"))
    if not matches:
        return None, "no_master_arc"
    if teacher_id in (None, "default_teacher"):
        return matches[0], None
    allowed = teacher_allowed_engines(teacher_id)
    if not allowed:
        return matches[0], None
    for arc in matches:
        eng = engine_from_arc_path(arc)
        if eng and eng in allowed:
            return arc, None
    available = sorted({engine_from_arc_path(a) or "?" for a in matches})
    return None, f"teacher_engine_mismatch (teacher={teacher_id} allowed={sorted(allowed)} arcs_have={available})"


# -----------------------------------------------------------------------------
# Step 1: allocate
# -----------------------------------------------------------------------------

def allocate_specs(
    out_dir: Path,
    over_allocate: int,
    seed: str,
    locale: str,
    brand_matrix: Path | None,
    locale_group: str | None,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(GENERATE_FULL_CATALOG),
        "--max-books", str(over_allocate),
        "--skip-wave-selection",
        "--plan-only",
        "--candidates-dir", str(out_dir),
        "--seed", seed,
    ]
    if brand_matrix:
        cmd += ["--brand-matrix", str(brand_matrix)]
    if locale_group:
        cmd += ["--locale-group", locale_group]
    # Non-en-US single-locale: pass --atoms-root so per-book atom root is correct.
    # When --locale-group is set, per-book atoms root is derived from spec.locale.
    print(f"[{locale} allocate] {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=600)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        raise SystemExit(f"[{locale}] generate_full_catalog failed (exit {r.returncode})")
    return len(list(out_dir.glob("*.spec.json")))


# -----------------------------------------------------------------------------
# Step 2: filter
# -----------------------------------------------------------------------------

def load_specs_with_arcs(spec_dir: Path, target: int) -> tuple[list[dict], list[dict]]:
    kept: list[dict] = []
    dropped: list[dict] = []
    for spec_file in sorted(spec_dir.glob("*.spec.json")):
        spec = json.loads(spec_file.read_text())
        persona = spec.get("persona_id")
        topic = spec.get("topic_id")
        teacher = spec.get("teacher_id") or "default_teacher"
        arc, drop_reason = pick_compatible_arc(persona, topic, teacher)
        if arc is None:
            dropped.append({
                "spec_file": spec_file.name,
                "persona": persona,
                "topic": topic,
                "teacher": teacher,
                "reason": drop_reason,
            })
            continue
        kept.append({
            "spec_file": spec_file.name,
            "spec": spec,
            "arc_path": str(arc.relative_to(REPO_ROOT)),
        })
        if len(kept) >= target:
            break
    return kept, dropped


# -----------------------------------------------------------------------------
# Step 3: assemble (locale-aware)
# -----------------------------------------------------------------------------

def assemble_book(item: dict, render_dir: Path, locale: str, quality_profile: str) -> dict:
    spec = item["spec"]
    render_dir.mkdir(parents=True, exist_ok=True)

    teacher_id = spec.get("teacher_id") or "default_teacher"

    # Atoms root: for en-US baseline, repo atoms/. For CJK, pipeline uses --locale to
    # load atoms/{persona}/{topic}/{slot}/locales/{locale}/ — no --atoms-root override
    # needed (pipeline resolves locale subpath internally).
    atoms_root = str(REPO_ROOT / "atoms")

    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic", spec["topic_id"],
        "--persona", spec["persona_id"],
        "--arc", str(REPO_ROOT / item["arc_path"]),
        "--teacher", teacher_id,
        "--seed", spec["seed"],
        "--out", str(render_dir / "plan.json"),
        "--atoms-model", spec.get("atoms_model", "legacy"),
        "--atoms-root", atoms_root,
        "--locale", locale,
        "--pipeline-mode", "spine",
        "--exercise-journeys",
        "--render-book",
        "--render-dir", str(render_dir),
        "--quality-profile", quality_profile,
        "--no-job-check",
        "--no-generate-freebies",
    ]
    if spec.get("angle_id"):
        cmd += ["--angle", spec["angle_id"]]
    if spec.get("series_id"):
        cmd += ["--series", spec["series_id"]]
    if spec.get("installment_number") is not None:
        cmd += ["--installment", str(spec["installment_number"])]

    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=BOOK_TIMEOUT_SEC)
        returncode = r.returncode
        stdout, stderr = r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        returncode = -9
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + f"\nTIMEOUT after {BOOK_TIMEOUT_SEC}s"
    elapsed = time.time() - t0

    (render_dir / "run.log").write_text(
        f"# locale: {locale}\n# cmd: {' '.join(cmd)}\n# exit: {returncode}\n# elapsed: {elapsed:.1f}s\n\n"
        f"--- STDOUT ---\n{stdout}\n\n--- STDERR ---\n{stderr}\n"
    )

    qs_path = render_dir / "quality_summary.json"
    quality_summary = None
    if qs_path.exists():
        try:
            quality_summary = json.loads(qs_path.read_text())
        except Exception as e:
            quality_summary = {"parse_error": str(e)}

    book_txt = render_dir / "book.txt"
    has_book_txt = book_txt.exists() and book_txt.stat().st_size > 0
    book_word_count = len(book_txt.read_text().split()) if has_book_txt else None

    return {
        "locale": locale,
        "topic": spec["topic_id"],
        "persona": spec["persona_id"],
        "teacher": teacher_id,
        "brand": spec.get("brand_id"),
        "returncode": returncode,
        "elapsed_sec": round(elapsed, 1),
        "has_book_txt": has_book_txt,
        "book_word_count": book_word_count,
        "quality_gates_pass": returncode == 0,
        "quality_summary": quality_summary,
    }


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--locale", required=True, help="Locale code (en-US, zh-TW, ja-JP, zh-CN, ...)")
    ap.add_argument("--target", type=int, default=100)
    ap.add_argument("--over-allocate", type=int, default=None, help="Default: 2.5× target")
    ap.add_argument("--quality-profile", choices=["production", "draft", "debug", "flagship"], default="draft")
    ap.add_argument("--brand-matrix", default=None, help="Brand×teacher matrix YAML (e.g. for zh_* locales)")
    ap.add_argument("--locale-group", default=None, help="Locale group for multi-locale runs (e.g. chinese_all)")
    ap.add_argument("--out-root", default=None, help="Output root (default: artifacts/pearl_prime_<locale_slug>/full_catalog_qa)")
    ap.add_argument("--seed-tag", default=None)
    args = ap.parse_args()

    if args.over_allocate is None:
        args.over_allocate = max(50, int(args.target * 2.5))

    if args.seed_tag is None:
        args.seed_tag = f"multilingual_qa_{args.locale.replace('-', '_')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}"

    if args.out_root is None:
        locale_slug = args.locale.replace("-", "_").lower()
        args.out_root = REPO_ROOT / f"artifacts/pearl_prime_{locale_slug}/full_catalog_qa"
    else:
        args.out_root = Path(args.out_root)

    args.out_root.mkdir(parents=True, exist_ok=True)
    brand_matrix = Path(args.brand_matrix) if args.brand_matrix else None

    print(f"[{args.locale}] START — target={args.target} over_allocate={args.over_allocate} "
          f"profile={args.quality_profile} out={args.out_root}", flush=True)

    # Step 1: allocate
    spec_dir = args.out_root / "specs"
    n_specs = allocate_specs(
        spec_dir, args.over_allocate, args.seed_tag, args.locale, brand_matrix, args.locale_group,
    )
    print(f"[{args.locale} allocate] emitted {n_specs} BookSpecs", flush=True)

    # Step 2: filter
    kept, dropped = load_specs_with_arcs(spec_dir, args.target)
    filter_report = {
        "locale": args.locale,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "over_allocate": args.over_allocate,
        "specs_allocated": n_specs,
        "kept": len(kept),
        "dropped": len(dropped),
        "dropped_details": dropped,
    }
    (args.out_root / "filter_report.json").write_text(json.dumps(filter_report, indent=2))
    print(f"[{args.locale} filter] kept {len(kept)} / dropped {len(dropped)}", flush=True)
    if len(kept) < args.target:
        print(f"[{args.locale} filter] WARNING: only {len(kept)} viable specs (target={args.target}). "
              f"Increase --over-allocate if needed.", flush=True)

    # Step 3: assemble
    renders_root = args.out_root / "renders"
    renders_root.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    t_start = time.time()
    for i, item in enumerate(kept):
        render_name = f"book_{i:04d}_{item['spec']['topic_id']}_{item['spec']['persona_id']}"
        render_dir = renders_root / render_name
        print(f"[{args.locale} {i+1}/{len(kept)}] {item['spec']['topic_id']} × {item['spec']['persona_id']} "
              f"(teacher={item['spec'].get('teacher_id') or 'default_teacher'})", flush=True)
        outcome = assemble_book(item, render_dir, args.locale, args.quality_profile)
        outcome["idx"] = i
        outcome["render_name"] = render_name
        outcome["spec_file"] = item["spec_file"]
        results.append(outcome)

        if (i + 1) % 10 == 0 or (i + 1) == len(kept):
            n_pass = sum(1 for r in results if r["quality_gates_pass"])
            n_have_txt = sum(1 for r in results if r["has_book_txt"])
            elapsed_total = time.time() - t_start
            eta = (elapsed_total / (i + 1)) * (len(kept) - i - 1)
            print(f"  ▸ [{args.locale}] {i+1} done — {n_pass} pass gates, "
                  f"{n_have_txt} have book.txt. elapsed {elapsed_total/60:.1f}m, ETA {eta/60:.1f}m",
                  flush=True)

    # Step 4: summary
    n_pass = sum(1 for r in results if r["quality_gates_pass"])
    n_have_txt = sum(1 for r in results if r["has_book_txt"])
    mean_wc = int(sum((r["book_word_count"] or 0) for r in results) / max(1, n_have_txt))
    summary = {
        "locale": args.locale,
        "quality_profile": args.quality_profile,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "assembled": len(results),
        "quality_gates_pass": n_pass,
        "have_book_txt": n_have_txt,
        "mean_word_count_of_rendered": mean_wc,
        "elapsed_sec": round(time.time() - t_start, 1),
        "books": results,
    }
    (args.out_root / "assembly_summary.json").write_text(json.dumps(summary, indent=2))

    print(f"\n=== [{args.locale}] DONE ===\n"
          f"  assembled:            {len(results)}\n"
          f"  quality_gates_pass:   {n_pass}\n"
          f"  rendered book.txt:    {n_have_txt}\n"
          f"  mean word count:      {mean_wc}\n"
          f"  total elapsed:        {summary['elapsed_sec']/60:.1f} min\n"
          f"  artifacts:            {args.out_root}\n", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
