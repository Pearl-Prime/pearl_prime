#!/usr/bin/env python3
"""Pick a random persona×topic, render a 2hr spine book, emit human_atom_trace.txt.

Usage:
  PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py
  PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py --seed 42
  PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py --list-candidates
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
ATOMS_ROOT = REPO_ROOT / "atoms"
RUNTIME_FORMAT = "extended_book_2h"


@dataclass(frozen=True)
class CellCandidate:
    persona: str
    topic: str
    engine: str
    structural_format: str
    arc_path: Path  # absolute

    @property
    def key(self) -> str:
        return f"{self.persona}__{self.topic}__{self.engine}__{self.structural_format}"


def _parse_arc_path(arc_path: Path) -> Optional[tuple[str, str, str, str]]:
    """Parse persona__topic__engine__F00N.yaml → (persona, topic, engine, structural)."""
    parts = arc_path.stem.split("__")
    if len(parts) != 4:
        return None
    persona, topic, engine, structural = (p.strip() for p in parts)
    if not persona or not topic or not engine or not structural.startswith("F"):
        return None
    return persona, topic, engine, structural


def _has_atom_bank(persona: str, topic: str, *, repo_root: Path = REPO_ROOT) -> bool:
    base = repo_root / "atoms" / persona / topic
    if not base.is_dir():
        return False
    for path in base.rglob("CANONICAL.txt"):
        if "/locales/" not in path.as_posix():
            return True
    return False


def list_candidates(*, repo_root: Path = REPO_ROOT) -> list[CellCandidate]:
    """Viable (arc + atom bank) cells for a random 2h render."""
    arcs_root = repo_root / "config" / "source_of_truth" / "master_arcs"
    out: list[CellCandidate] = []
    seen: set[str] = set()
    if not arcs_root.is_dir():
        return out
    for arc_path in sorted(arcs_root.glob("*.yaml")):
        parsed = _parse_arc_path(arc_path)
        if not parsed:
            continue
        persona, topic, engine, structural = parsed
        # One candidate per persona×topic (prefer first engine in sorted arc names)
        cell_key = f"{persona}__{topic}"
        if cell_key in seen:
            continue
        if not _has_atom_bank(persona, topic, repo_root=repo_root):
            continue
        seen.add(cell_key)
        out.append(
            CellCandidate(
                persona=persona,
                topic=topic,
                engine=engine,
                structural_format=structural,
                arc_path=arc_path.resolve(),
            )
        )
    return out


def pick_candidate(
    candidates: list[CellCandidate],
    *,
    seed: int,
) -> CellCandidate:
    if not candidates:
        raise RuntimeError("No viable persona×topic candidates (arcs + atom banks).")
    rng = random.Random(seed)
    return rng.choice(candidates)


def build_pipeline_command(
    *,
    cell: CellCandidate,
    render_dir: Path,
    seed: str,
    repo_root: Path = REPO_ROOT,
    python: str = sys.executable,
) -> list[str]:
    return [
        python,
        str(repo_root / "scripts" / "run_pipeline.py"),
        "--topic",
        cell.topic,
        "--persona",
        cell.persona,
        "--arc",
        str(cell.arc_path),
        "--pipeline-mode",
        "spine",
        "--runtime-format",
        RUNTIME_FORMAT,
        "--quality-profile",
        "production",
        "--exercise-journeys",
        "--no-job-check",
        "--render-book",
        "--render-dir",
        str(render_dir),
        "--out",
        str(render_dir / "plan.json"),
        "--no-generate-freebies",
        "--no-update-freebie-index",
        "--seed",
        seed,
    ]


def default_render_dir(
    cell: CellCandidate,
    *,
    seed: int,
    out_root: Path,
    day: Optional[str] = None,
) -> Path:
    stamp = day or datetime.now(timezone.utc).strftime("%Y%m%d")
    name = f"random_2h_{stamp}_{cell.persona}__{cell.topic}__{seed}"
    return (out_root / name).resolve()


def ensure_atom_trace(render_dir: Path, *, repo_root: Path = REPO_ROOT) -> Path:
    spa = render_dir / "section_packet_audit.json"
    book = render_dir / "book.txt"
    if not spa.exists() or not book.exists():
        missing = []
        if not spa.exists():
            missing.append("section_packet_audit.json")
        if not book.exists():
            missing.append("book.txt")
        raise FileNotFoundError(
            f"Cannot emit atom trace — missing {', '.join(missing)} under {render_dir}"
        )
    from scripts.qa.render_atom_trace import write_atom_trace

    return write_atom_trace(render_dir, repo_root=repo_root)


def run_render(
    cmd: list[str],
    *,
    cwd: Path = REPO_ROOT,
) -> int:
    print("Running:", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=str(cwd))
    return int(proc.returncode)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Random 2hr book render + human atom trace (persona×topic)."
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for cell pick + pipeline seed (default: UTC epoch seconds)",
    )
    ap.add_argument(
        "--out-root",
        type=Path,
        default=REPO_ROOT / "artifacts" / "qa" / "random_2h_books",
        help="Parent directory for render dirs",
    )
    ap.add_argument(
        "--render-dir",
        type=Path,
        default=None,
        help="Exact render dir (default: out-root/random_2h_<day>_<persona>__<topic>__<seed>)",
    )
    ap.add_argument(
        "--list-candidates",
        action="store_true",
        help="Print viable persona×topic count/sample and exit",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Pick cell and print pipeline command; do not render",
    )
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root",
    )
    args = ap.parse_args(argv)
    repo_root = args.repo_root.resolve()

    candidates = list_candidates(repo_root=repo_root)
    if args.list_candidates:
        personas = sorted({c.persona for c in candidates})
        topics = sorted({c.topic for c in candidates})
        print(f"candidates={len(candidates)} personas={len(personas)} topics={len(topics)}")
        for c in candidates[:20]:
            print(f"  {c.persona} × {c.topic}  engine={c.engine}  {c.structural_format}")
        if len(candidates) > 20:
            print(f"  ... ({len(candidates) - 20} more)")
        return 0

    seed = args.seed if args.seed is not None else int(datetime.now(timezone.utc).timestamp())
    cell = pick_candidate(candidates, seed=seed)
    render_dir = (
        args.render_dir.resolve()
        if args.render_dir
        else default_render_dir(cell, seed=seed, out_root=args.out_root.resolve())
    )
    render_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"PICKED persona={cell.persona!r} topic={cell.topic!r} "
        f"engine={cell.engine!r} structural={cell.structural_format!r} seed={seed}",
        flush=True,
    )
    print(f"ARC {cell.arc_path}", flush=True)
    print(f"RENDER_DIR {render_dir}", flush=True)
    print(f"RUNTIME {RUNTIME_FORMAT}", flush=True)

    cmd = build_pipeline_command(
        cell=cell,
        render_dir=render_dir,
        seed=str(seed),
        repo_root=repo_root,
    )
    if args.dry_run:
        print("DRY_RUN command:")
        print(" ".join(cmd))
        return 0

    rc = run_render(cmd, cwd=repo_root)
    # Trace whenever artifacts exist — even if gates failed after writing book/SPA.
    try:
        trace_path = ensure_atom_trace(render_dir, repo_root=repo_root)
    except FileNotFoundError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2 if rc == 0 else rc or 2

    book_path = render_dir / "book.txt"
    print("")
    print("=== RANDOM 2H BOOK + TRACE ===")
    print(f"persona:  {cell.persona}")
    print(f"topic:    {cell.topic}")
    print(f"seed:     {seed}")
    print(f"runtime:  {RUNTIME_FORMAT}")
    print(f"book:     {book_path}")
    print(f"trace:    {trace_path}")
    print(f"pipeline_exit: {rc}")
    print("USAGE: open the trace beside the book for beat → source(file:line) → atom → text")
    return 0 if (book_path.exists() and trace_path.exists()) else (rc or 1)


if __name__ == "__main__":
    raise SystemExit(main())
