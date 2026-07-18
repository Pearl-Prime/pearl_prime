#!/usr/bin/env python3
"""
Import therapeutic prose atoms from template_expand2/*.txt batch files into atoms/.

Skips chat logs, specs, and duplicate loose files; optional dedup against existing
atoms/ text (normalized SHA-256 of body).

New personas (e.g. midlife_women) are written under atoms/<persona>/...; canonical
personas skip import when body fingerprint matches an existing atom under that
persona/topic tree.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")

# template_expand2/<filename> -> (persona_id, topic_slug)
# topic_slug matches first-level folder under atoms/<persona>/.
FILE_PERSONA_TOPIC: Dict[str, Tuple[str, str]] = {
    "gen_alpha_students__anxiety__false_alarm__BATCH.txt": ("gen_alpha_students", "anxiety"),
    "gen_alpha_students__core__PILOT_BATCH.txt": ("gen_alpha_students", "core"),
    "gen_alpha_students__grief_topic__grief__CANONICAL.txt": ("gen_alpha_students", "grief"),
    "gen_alpha_students__grief_topic__watcher__CANONICAL.txt": ("gen_alpha_students", "grief"),
    "gen_z_professionals__grief_topic__grief__CANONICAL.txt": ("gen_z_professionals", "grief"),
    "gen_z_professionals__grief_topic__watcher__CANONICAL.txt": ("gen_z_professionals", "grief"),
    "healthcare_rns__grief_topic__grief__CANONICAL.txt": ("healthcare_rns", "grief"),
    "healthcare_rns__grief_topic__watcher__CANONICAL.txt": ("healthcare_rns", "grief"),
    "midlife_women__anxiety_part2__80atoms.txt": ("midlife_women", "anxiety"),
    "midlife_women__boundaries__ALL__60atoms.txt": ("midlife_women", "boundaries"),
    "midlife_women__boundaries_financial_courage__ALL.txt": ("midlife_women", "boundaries"),
    "midlife_women__compassion_fatigue_depression__ALL.txt": ("midlife_women", "compassion_fatigue"),
    "midlife_women__financial_stress_courage__120atoms.txt": ("midlife_women", "financial_stress"),
    "midlife_women__self_worth_grief_topic__ALL.txt": ("midlife_women", "self_worth"),
}

SKIP_NAMES = {
    "chat_er.txt",
    "chat_lkjkj.txt",
    "chat_personas_stuff.txt",
    "chat_s.txt",
    "old_chat_personas.txt",
    "midlife_women__boundaries_financial_courage__ALL (1).txt",
}


@dataclass
class ParsedAtom:
    header: str
    header_line: str
    body: str


def _norm_text(s: str) -> str:
    return " ".join(s.split())


def _fingerprint(s: str) -> str:
    return hashlib.sha256(_norm_text(s).encode("utf-8")).hexdigest()


def _engine_from_header(header_line: str) -> str:
    # "## ENGINE / ROLE v01 — ..."
    main = header_line.replace("##", "", 1).strip()
    main = main.split("—", 1)[0].strip()
    first = main.split("/", 1)[0].strip()
    return re.sub(r"[^A-Za-z0-9_]+", "_", first).upper().strip("_") or "UNKNOWN"


def parse_batch_file(filepath: Path) -> List[ParsedAtom]:
    """Parse a batch atom text file into structured atoms."""
    atoms: List[ParsedAtom] = []
    current_header: Optional[str] = None
    current_header_line: Optional[str] = None
    body_lines: List[str] = []

    def flush() -> None:
        nonlocal current_header, current_header_line, body_lines
        if current_header is None or current_header_line is None:
            body_lines = []
            return
        body = "".join(body_lines).strip()
        if body:
            atoms.append(
                ParsedAtom(
                    header=current_header,
                    header_line=current_header_line,
                    body=body,
                )
            )
        current_header = None
        current_header_line = None
        body_lines = []

    for line in filepath.read_text(encoding="utf-8", errors="replace").splitlines(True):
        if HEADER_RE.match(line):
            flush()
            current_header_line = line.strip()
            current_header = HEADER_RE.match(line).group(1).strip()
            body_lines = []
            continue
        if line.strip() == "---":
            continue
        if line.startswith("===="):
            continue
        if current_header is not None:
            body_lines.append(line)

    flush()
    return atoms


def _collect_existing_fingerprints(persona: str, topic: str, atoms_root: Path) -> set[str]:
    base = atoms_root / persona / topic
    out: set[str] = set()
    if not base.is_dir():
        return out
    for p in base.rglob("*.txt"):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out.add(_fingerprint(t))
    return out


def _iter_batch_txt(template_expand2: Path) -> Iterator[Path]:
    for p in sorted(template_expand2.glob("*.txt")):
        if p.name in SKIP_NAMES:
            continue
        if p.name not in FILE_PERSONA_TOPIC:
            continue
        yield p


def main() -> int:
    parser = argparse.ArgumentParser(description="Import template_expand2 atom batch .txt files into atoms/")
    parser.add_argument(
        "--source",
        type=Path,
        default=REPO_ROOT / "template_expand2",
        help="Directory containing batch .txt files",
    )
    parser.add_argument(
        "--atoms-root",
        type=Path,
        default=REPO_ROOT / "atoms",
        help="atoms/ root",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print plan only; do not write files")
    parser.add_argument(
        "--only-persona",
        action="append",
        default=[],
        help="Restrict import to persona id (repeatable). Default: all mapped files.",
    )
    args = parser.parse_args()

    if not args.source.is_dir():
        print(f"Missing source dir: {args.source}", file=sys.stderr)
        return 1

    only = set(args.only_persona) if args.only_persona else None

    total_written = 0
    total_skipped_dup = 0
    total_atoms = 0

    for fp in _iter_batch_txt(args.source):
        meta = FILE_PERSONA_TOPIC.get(fp.name)
        if not meta:
            continue
        persona, topic = meta
        if only and persona not in only:
            continue

        existing = _collect_existing_fingerprints(persona, topic, args.atoms_root)
        atoms = parse_batch_file(fp)
        total_atoms += len(atoms)

        safe_stem = re.sub(r"[^A-Za-z0-9_]+", "_", fp.stem).strip("_")[:80]

        for idx, atom in enumerate(atoms, start=1):
            fp_hash = _fingerprint(atom.body)
            if fp_hash in existing:
                total_skipped_dup += 1
                continue

            eng = _engine_from_header(atom.header_line)
            out_dir = args.atoms_root / persona / topic / eng
            stem = f"expand2_{safe_stem}_{idx:04d}_{eng.lower()}"
            out_path = out_dir / f"{stem}.txt"

            if args.dry_run:
                print(f"[dry-run] would write {out_path} ({len(atom.body.split())} words)")
                existing.add(fp_hash)
                total_written += 1
                continue

            out_dir.mkdir(parents=True, exist_ok=True)
            header_block = f"{atom.header_line}\n---\n"
            out_path.write_text(header_block + atom.body + "\n", encoding="utf-8")
            existing.add(fp_hash)
            total_written += 1

        print(f"{fp.name}: parsed={len(atoms)} persona={persona} topic={topic}")

    print(
        f"Done. atoms={total_atoms} written={total_written} "
        f"skipped_duplicate={total_skipped_dup} dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
