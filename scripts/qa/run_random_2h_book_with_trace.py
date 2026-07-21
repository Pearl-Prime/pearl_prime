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
    return (repo_root / "atoms" / persona / topic).is_dir()


def _bindings_topic_key(topic: str) -> str:
    return "grief" if topic == "grief_topic" else topic


def _load_allowed_engines(repo_root: Path) -> dict[str, set[str]]:
    """topic → allowed_engines from topic_engine_bindings.yaml (loaded once)."""
    path = repo_root / "config" / "topic_engine_bindings.yaml"
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, set[str]] = {}
    for topic, cfg in data.items():
        if not isinstance(cfg, dict):
            continue
        allowed = cfg.get("allowed_engines") or []
        out[str(topic)] = {str(e) for e in allowed}
    return out


def _min_story_pool_size(repo_root: Path) -> int:
    path = repo_root / "config" / "gates.yaml"
    if not path.exists():
        return 12
    try:
        import yaml
    except ImportError:
        return 12
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    tvc = data.get("tuple_viability") or {}
    return int(tvc.get("min_story_pool_size", 12))


def _story_pool_depth(
    persona: str, topic: str, engine: str, *, repo_root: Path
) -> int:
    """Count ## headers in atoms/<persona>/<topic>/<engine>/CANONICAL.txt."""
    path = repo_root / "atoms" / persona / topic / engine / "CANONICAL.txt"
    if not path.is_file():
        return 0
    try:
        return sum(1 for line in path.open(encoding="utf-8") if line.startswith("## "))
    except OSError:
        return 0


def _tuple_is_viable(
    persona: str,
    topic: str,
    engine: str,
    format_id: str,
    *,
    repo_root: Path = REPO_ROOT,
    allowed_by_topic: Optional[dict[str, set[str]]] = None,
    min_story: Optional[int] = None,
) -> bool:
    """Fast preflight matching run_pipeline's tuple gate (binding + STORY depth).

    Arc existence is implied by the caller iterating master_arcs. Full
    check_tuple_viability is avoided here — it reloads YAML + parses CANONICAL
    per arc and is too slow for a 700+ arc scan.
    """
    _ = format_id  # kept for call-site parity / tests
    allowed_map = allowed_by_topic if allowed_by_topic is not None else _load_allowed_engines(repo_root)
    allowed = allowed_map.get(_bindings_topic_key(topic)) or set()
    if engine not in allowed:
        return False
    depth = _story_pool_depth(persona, topic, engine, repo_root=repo_root)
    need = min_story if min_story is not None else _min_story_pool_size(repo_root)
    return depth >= need


def _has_story_atoms(
    persona: str, topic: str, engine: str, *, repo_root: Path = REPO_ROOT
) -> bool:
    """True when research-fit story schedule can fire for this cell."""
    root = repo_root / "story_atoms" / persona / "anchored" / topic / engine
    if not root.is_dir():
        return False
    return any(root.rglob("*.txt"))


def list_candidates(
    *,
    repo_root: Path = REPO_ROOT,
    require_story_atoms: bool = False,
) -> list[CellCandidate]:
    """Pipeline-viable cells: arc + atom dir + binding + STORY pool depth.

    One candidate per persona×topic — the first *viable* engine in sorted arc
    order (not merely the first arc name). Avoids NO_BINDING picks like
    healthcare_rns×overthinking×comparison when false_alarm/spiral/watcher PASS.

    When require_story_atoms=True (bestseller-path), only cells with
    story_atoms/{persona}/anchored/{topic}/{engine}/ are returned so
    research_fit can fire.
    """
    arcs_root = repo_root / "config" / "source_of_truth" / "master_arcs"
    out: list[CellCandidate] = []
    seen: set[str] = set()
    if not arcs_root.is_dir():
        return out
    allowed_by_topic = _load_allowed_engines(repo_root)
    min_story = _min_story_pool_size(repo_root)
    for arc_path in sorted(arcs_root.glob("*.yaml")):
        parsed = _parse_arc_path(arc_path)
        if not parsed:
            continue
        persona, topic, engine, structural = parsed
        cell_key = f"{persona}__{topic}"
        if cell_key in seen:
            continue
        if not _has_atom_bank(persona, topic, repo_root=repo_root):
            continue
        if not _tuple_is_viable(
            persona,
            topic,
            engine,
            structural,
            repo_root=repo_root,
            allowed_by_topic=allowed_by_topic,
            min_story=min_story,
        ):
            continue
        if require_story_atoms and not _has_story_atoms(
            persona, topic, engine, repo_root=repo_root
        ):
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
        "--bestseller-path",
        action="store_true",
        help=(
            "Only pick cells with story_atoms/.../anchored/{topic}/{engine}/ "
            "so research_fit can fire (not raw tuple viability alone)"
        ),
    )
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root",
    )
    args = ap.parse_args(argv)
    repo_root = args.repo_root.resolve()

    candidates = list_candidates(
        repo_root=repo_root, require_story_atoms=bool(args.bestseller_path)
    )
    if args.bestseller_path and not candidates:
        print(
            "BLOCKED: --bestseller-path set but no cells have story_atoms coverage",
            file=sys.stderr,
        )
        return 2
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
        print(
            "Hint: re-run after pulling latest wrapper (candidates are tuple-viability filtered), "
            "or try: PYTHONPATH=. python3 scripts/qa/run_random_2h_book_with_trace.py --seed 7",
            file=sys.stderr,
        )
        return 2 if rc == 0 else rc or 2

    book_path = render_dir / "book.txt"
    print("")
    print("=== RANDOM 2H BOOK + TRACE ===")
    print(f"persona:  {cell.persona}")
    print(f"topic:    {cell.topic}")
    print(f"engine:   {cell.engine}")
    print(f"seed:     {seed}")
    print(f"runtime:  {RUNTIME_FORMAT}")
    print(f"book:     {book_path}")
    print(f"trace:    {trace_path}")
    print(f"pipeline_exit: {rc}")
    print(f"open book:  open {book_path!s}")
    print(f"open trace: open {trace_path!s}")
    print("USAGE: open the trace beside the book for beat → source(file:line) → atom → text")
    return 0 if (book_path.exists() and trace_path.exists()) else (rc or 1)


if __name__ == "__main__":
    raise SystemExit(main())
