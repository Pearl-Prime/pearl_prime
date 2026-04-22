#!/usr/bin/env python3
"""
Generate browser translation queue files for 30-tab parallel translation.

Outputs one JSONL file per locale to artifacts/translation/browser_queues/.
Atoms already translated (output exists and size > 20 bytes) are skipped.
COMPRESSION atoms are written directly (no LLM).

Usage:
    python3 scripts/translation/browser_translation_prep.py \
        --locales zh-TW zh-CN ja-JP \
        [--force-redo zh-TW]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Priority persona order (spec Section 7)
PERSONA_PRIORITY = [
    "gen_z_professionals",
    "millennial_women_professionals",
    "healthcare_rns",
    "working_parents",
    "tech_finance_burnout",
    "midlife_women",
]


def _persona_sort_key(src_path: Path, atoms_root: Path) -> tuple[int, str]:
    """Return (priority_index, path_str) for sorting."""
    try:
        persona = src_path.relative_to(atoms_root).parts[0]
    except (ValueError, IndexError):
        persona = ""
    try:
        idx = PERSONA_PRIORITY.index(persona)
    except ValueError:
        idx = len(PERSONA_PRIORITY)
    return (idx, str(src_path))


def _out_path(src_path: Path, locale: str) -> Path:
    """atoms/persona/topic/TYPE/CANONICAL.txt
    → atoms/persona/topic/TYPE/locales/{locale}/CANONICAL.txt"""
    return src_path.parent / "locales" / locale / "CANONICAL.txt"


def _is_compression(src_path: Path) -> bool:
    return src_path.parent.name.upper() == "COMPRESSION"


def _already_done(out_path: Path) -> bool:
    return out_path.is_file() and out_path.stat().st_size > 20


def build_queues(
    locales: list[str],
    atoms_root: Path,
    force_redo: set[str],
    queues_dir: Path,
    failures_dir: Path,
    dry_run: bool,
) -> None:
    # Collect all source CANONICAL.txt, excluding anything already inside /locales/
    all_sources = sorted(
        p for p in atoms_root.rglob("CANONICAL.txt")
        if "locales" not in p.parts
    )

    queues_dir.mkdir(parents=True, exist_ok=True)
    failures_dir.mkdir(parents=True, exist_ok=True)

    for locale in locales:
        # Sort by priority
        sources = sorted(all_sources, key=lambda p: _persona_sort_key(p, atoms_root))

        queue: list[dict] = []
        n_skipped_done = 0
        n_compression = 0

        for src in sources:
            out = _out_path(src, locale)
            atom_id = str(src.relative_to(atoms_root).parent)  # e.g. gen_z_professionals/anxiety/HOOK

            if _is_compression(src):
                n_compression += 1
                if not dry_run:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                continue

            if locale not in force_redo and _already_done(out):
                n_skipped_done += 1
                continue

            content = src.read_text(encoding="utf-8")
            # Use paths relative to repo root if src is inside it, else relative to atoms_root parent
            try:
                src_rel = str(src.relative_to(REPO_ROOT))
                out_rel = str(out.relative_to(REPO_ROOT))
            except ValueError:
                src_rel = str(src.relative_to(atoms_root.parent))
                out_rel = str(out.relative_to(atoms_root.parent))
            queue.append({
                "id": atom_id,
                "src_path": src_rel,
                "out_path": out_rel,
                "locale": locale,
                "content": content,
                "status": "pending",
            })

        jsonl_path = queues_dir / f"{locale}.jsonl"
        if not dry_run:
            with open(jsonl_path, "w", encoding="utf-8") as f:
                for item in queue:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

        print(
            f"{locale}: {len(queue)} queued, {n_skipped_done} already done, "
            f"{n_compression} COMPRESSION (copied)"
            + (" [DRY RUN]" if dry_run else f" → {jsonl_path}")
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate browser translation queue JSONL files.")
    parser.add_argument("--locales", nargs="+", default=["zh-TW", "zh-CN", "ja-JP"])
    parser.add_argument("--atoms-root", type=Path, default=REPO_ROOT / "atoms")
    parser.add_argument(
        "--force-redo",
        nargs="*",
        default=[],
        help="Locales to re-queue even if output already exists",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "artifacts/translation/browser_queues",
    )
    parser.add_argument(
        "--failures-dir",
        type=Path,
        default=REPO_ROOT / "artifacts/translation/browser_failures",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.atoms_root.is_dir():
        print(f"[ERROR] atoms-root not found: {args.atoms_root}", file=sys.stderr)
        sys.exit(1)

    build_queues(
        locales=args.locales,
        atoms_root=args.atoms_root,
        force_redo=set(args.force_redo or []),
        queues_dir=args.out_dir,
        failures_dir=args.failures_dir,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
