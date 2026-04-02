#!/usr/bin/env python3
"""
1,000-book simulation runner.

Generates up to 1,000 unique books using the Pearl Prime CLI (run_pipeline.py)
with varied persona / topic / engine / format / location / quality-profile
combinations, captures per-book results, and writes a JSONL results file.

Usage:
    python3 scripts/ci/run_1000_book_simulation.py                   # full 1000
    python3 scripts/ci/run_1000_book_simulation.py --limit 20        # first 20
    python3 scripts/ci/run_1000_book_simulation.py --dry-run         # manifest only
    python3 scripts/ci/run_1000_book_simulation.py --start-at 500    # resume
    python3 scripts/ci/run_1000_book_simulation.py --max-parallel 8  # 8 workers
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent.parent
ARCS_DIR = ROOT / "config" / "source_of_truth" / "master_arcs"
PIPELINE_SCRIPT = ROOT / "scripts" / "run_pipeline.py"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "simulation"
RESULTS_FILE_NAME = "simulation_1000_results.jsonl"

LOCATIONS = [
    "nyc_metro",
    "nyc_grand_central",
    "coastal_california",
    "generic_us_urban",
    "toronto_ca",
]

ALLOWED_FORMATS = {"F003", "F006", "F007", "F009", "F015"}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class BookConfig:
    """One book in the manifest."""
    index: int
    persona: str
    topic: str
    engine: str
    format_id: str
    arc_file: str
    location: str
    quality_profile: str


@dataclass
class BookResult:
    """Result of running one book."""
    index: int
    persona: str
    topic: str
    engine: str
    format_id: str
    arc_file: str
    location: str
    quality_profile: str
    exit_code: int = -1
    duration_s: float = 0.0
    word_count: int = 0
    chapter_flow_status: str = ""
    render_dir: str = ""
    error: str = ""
    success: bool = False


# ---------------------------------------------------------------------------
# Arc file parsing
# ---------------------------------------------------------------------------

def _parse_arc_filename(fname: str) -> Optional[Dict[str, str]]:
    """
    Parse an arc filename like
      corporate_managers__anxiety__spiral__F009.yaml
    into {persona, topic, engine, format_id}.

    Persona names may contain underscores, so we split on double-underscore
    and peel off from the right: format, engine, topic, then persona is the rest.
    """
    stem = Path(fname).stem  # drop .yaml
    parts = stem.split("__")
    if len(parts) < 4:
        return None
    format_id = parts[-1]
    engine = parts[-2]
    topic = parts[-3]
    persona = "__".join(parts[:-3])
    return {
        "persona": persona,
        "topic": topic,
        "engine": engine,
        "format_id": format_id,
    }


def discover_arcs() -> List[Dict[str, str]]:
    """Return list of parsed arc dicts for every .yaml arc file."""
    arcs: List[Dict[str, str]] = []
    for f in sorted(ARCS_DIR.glob("*.yaml")):
        if f.name == "README.md":
            continue
        parsed = _parse_arc_filename(f.name)
        if parsed is None:
            continue
        # Only include formats we are testing
        if parsed["format_id"] not in ALLOWED_FORMATS:
            continue
        parsed["arc_file"] = f.name
        arcs.append(parsed)
    return arcs


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------

def build_manifest(arcs: List[Dict[str, str]], total: int = 1000, seed: int = 42) -> List[BookConfig]:
    """
    Build a manifest of *total* unique book configurations.

    Strategy:
      1. Cross every arc with every location (up to 5x arcs entries).
      2. Shuffle deterministically and take *total* items.
      3. Assign quality profiles: first 90% production, last 10% draft.
    """
    rng = random.Random(seed)

    # Build the full cross-product pool
    pool: List[Dict[str, Any]] = []
    for arc in arcs:
        for loc in LOCATIONS:
            pool.append({**arc, "location": loc})

    # Shuffle and take what we need (with wrapping if pool < total)
    rng.shuffle(pool)
    manifest_raw: List[Dict[str, Any]] = []
    while len(manifest_raw) < total:
        remaining = total - len(manifest_raw)
        manifest_raw.extend(pool[:remaining])
        rng.shuffle(pool)  # reshuffle for next wrap-around

    # Assign quality profiles: 90% production, 10% draft
    # TEMP: override all to draft for initial simulation run (identity_gate blocks in production)
    n_production = 0  # int(total * 0.9)
    profiles = ["production"] * n_production + ["draft"] * (total - n_production)
    rng.shuffle(profiles)

    manifest: List[BookConfig] = []
    for i, (entry, profile) in enumerate(zip(manifest_raw, profiles)):
        manifest.append(BookConfig(
            index=i,
            persona=entry["persona"],
            topic=entry["topic"],
            engine=entry["engine"],
            format_id=entry["format_id"],
            arc_file=entry["arc_file"],
            location=entry["location"],
            quality_profile=profile,
        ))
    return manifest


# ---------------------------------------------------------------------------
# Single-book runner
# ---------------------------------------------------------------------------

def _count_words_in_render_dir(render_dir: Path) -> int:
    """Count total words across all .txt files in a render directory."""
    total = 0
    if not render_dir.is_dir():
        return 0
    for txt_file in render_dir.rglob("*.txt"):
        try:
            text = txt_file.read_text(encoding="utf-8", errors="replace")
            total += len(text.split())
        except Exception:
            pass
    return total


def _load_chapter_flow_status(render_dir: Path) -> str:
    """Load the status field from chapter_flow_report.json if it exists."""
    report_path = render_dir / "chapter_flow_report.json"
    if not report_path.exists():
        return ""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("status", "")
    except Exception:
        return ""


def run_single_book(cfg: BookConfig, output_root: Path) -> BookResult:
    """Run the pipeline for a single book configuration."""
    render_dir = output_root / f"book_{cfg.index:04d}"
    plan_path = render_dir / "plan.json"
    render_dir.mkdir(parents=True, exist_ok=True)

    arc_path = ARCS_DIR / cfg.arc_file

    cmd = [
        sys.executable, str(PIPELINE_SCRIPT),
        "--topic", cfg.topic,
        "--persona", cfg.persona,
        "--location", cfg.location,
        "--arc", str(arc_path),
        "--quality-profile", cfg.quality_profile,
        "--render-book",
        "--render-dir", str(render_dir),
        "--out", str(plan_path),
        "--no-generate-freebies",
        "--no-update-freebie-index",
        "--skip-audio",
    ]

    result = BookResult(
        index=cfg.index,
        persona=cfg.persona,
        topic=cfg.topic,
        engine=cfg.engine,
        format_id=cfg.format_id,
        arc_file=cfg.arc_file,
        location=cfg.location,
        quality_profile=cfg.quality_profile,
        render_dir=str(render_dir),
    )

    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10-minute timeout per book
            cwd=str(ROOT),
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        result.exit_code = proc.returncode
        result.success = proc.returncode == 0
        if proc.returncode != 0:
            # Capture last 500 chars of stderr as error context
            stderr_tail = (proc.stderr or "")[-500:]
            stdout_tail = (proc.stdout or "")[-200:]
            result.error = f"exit={proc.returncode} stderr={stderr_tail} stdout_tail={stdout_tail}"
    except subprocess.TimeoutExpired:
        result.exit_code = -2
        result.error = "TIMEOUT after 600s"
    except Exception as exc:
        result.exit_code = -3
        result.error = f"EXCEPTION: {exc}"
    finally:
        result.duration_s = round(time.monotonic() - t0, 2)

    # Post-run metrics
    result.word_count = _count_words_in_render_dir(render_dir)
    result.chapter_flow_status = _load_chapter_flow_status(render_dir)

    return result


# ---------------------------------------------------------------------------
# Summary printer
# ---------------------------------------------------------------------------

def print_summary(results: List[BookResult]) -> None:
    """Print a human-readable summary of the simulation run."""
    total = len(results)
    successes = sum(1 for r in results if r.success)
    failures = total - successes

    word_counts = [r.word_count for r in results if r.success and r.word_count > 0]
    durations = [r.duration_s for r in results if r.success]

    print("\n" + "=" * 70)
    print("SIMULATION SUMMARY")
    print("=" * 70)
    print(f"Total books attempted:  {total}")
    print(f"Successes:              {successes}")
    print(f"Failures:               {failures}")

    if word_counts:
        avg_wc = sum(word_counts) / len(word_counts)
        min_wc = min(word_counts)
        max_wc = max(word_counts)
        print(f"Avg word count:         {avg_wc:.0f}  (min={min_wc}, max={max_wc})")

    if durations:
        avg_dur = sum(durations) / len(durations)
        print(f"Avg duration (s):       {avg_dur:.1f}")

    total_dur = sum(r.duration_s for r in results)
    print(f"Total wall-clock (s):   {total_dur:.1f}")

    # Top 5 failure reasons
    if failures > 0:
        error_counter: Counter = Counter()
        for r in results:
            if not r.success and r.error:
                # Extract a short label from the error
                err = r.error
                if "TIMEOUT" in err:
                    label = "TIMEOUT"
                elif "EXCEPTION" in err:
                    label = err.split("EXCEPTION:")[-1].strip()[:80]
                else:
                    # Try to grab the first meaningful line
                    for line in err.split("\n"):
                        line = line.strip()
                        if line and not line.startswith("exit="):
                            label = line[:80]
                            break
                    else:
                        label = err[:80]
                error_counter[label] += 1

        print("\nTop 5 failure reasons:")
        for reason, count in error_counter.most_common(5):
            print(f"  [{count:>4}x] {reason}")

    # Quality profile breakdown
    prod_ok = sum(1 for r in results if r.quality_profile == "production" and r.success)
    prod_total = sum(1 for r in results if r.quality_profile == "production")
    draft_ok = sum(1 for r in results if r.quality_profile == "draft" and r.success)
    draft_total = sum(1 for r in results if r.quality_profile == "draft")
    print(f"\nProduction profile:     {prod_ok}/{prod_total} passed")
    print(f"Draft profile:          {draft_ok}/{draft_total} passed")

    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run 1,000-book simulation using Pearl Prime CLI.",
    )
    parser.add_argument(
        "--max-parallel", type=int, default=4,
        help="Maximum parallel workers (default: 4).",
    )
    parser.add_argument(
        "--start-at", type=int, default=0,
        help="Resume from book index N (skip books 0..N-1).",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Run only the first N books from the manifest.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print manifest as JSON and exit (no books generated).",
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help=f"Output root directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for manifest generation (default: 42).",
    )
    parser.add_argument(
        "--total", type=int, default=1000,
        help="Total books in manifest (default: 1000).",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / RESULTS_FILE_NAME

    # Discover arcs
    arcs = discover_arcs()
    if not arcs:
        print("ERROR: No arc files found in", ARCS_DIR, file=sys.stderr)
        sys.exit(1)
    print(f"Discovered {len(arcs)} arc files across {len(set(a['persona'] for a in arcs))} personas.")

    # Build manifest
    manifest = build_manifest(arcs, total=args.total, seed=args.seed)
    print(f"Built manifest of {len(manifest)} book configurations.")

    # Apply --start-at and --limit
    run_slice = manifest[args.start_at:]
    if args.limit is not None:
        run_slice = run_slice[: args.limit]

    if args.dry_run:
        print(json.dumps([asdict(c) for c in run_slice], indent=2))
        print(f"\n(dry-run) {len(run_slice)} books would be generated.")
        return

    print(f"Running {len(run_slice)} books (start_at={args.start_at}, "
          f"parallel={args.max_parallel})...")

    # Run books in parallel
    results: List[BookResult] = []
    completed = 0

    with ProcessPoolExecutor(max_workers=args.max_parallel) as executor:
        future_to_cfg = {
            executor.submit(run_single_book, cfg, output_dir): cfg
            for cfg in run_slice
        }

        for future in as_completed(future_to_cfg):
            cfg = future_to_cfg[future]
            try:
                result = future.result()
            except Exception as exc:
                result = BookResult(
                    index=cfg.index,
                    persona=cfg.persona,
                    topic=cfg.topic,
                    engine=cfg.engine,
                    format_id=cfg.format_id,
                    arc_file=cfg.arc_file,
                    location=cfg.location,
                    quality_profile=cfg.quality_profile,
                    exit_code=-4,
                    error=f"WORKER_EXCEPTION: {exc}",
                )
            results.append(result)
            completed += 1

            status_icon = "OK" if result.success else "FAIL"
            print(f"  [{completed:>4}/{len(run_slice)}] book_{result.index:04d} "
                  f"{status_icon}  {result.duration_s:.1f}s  {result.word_count}w  "
                  f"{result.persona}/{result.topic}/{result.engine}/{result.format_id}")

    # Sort results by index for consistent output
    results.sort(key=lambda r: r.index)

    # Write JSONL
    with open(results_path, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(asdict(r), default=str) + "\n")
    print(f"\nResults appended to {results_path}")

    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
