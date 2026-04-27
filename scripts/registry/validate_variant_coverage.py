#!/usr/bin/env python3
"""Spec #739 Phase 1 — variant coverage validator.

Walks two coverage axes that spec ``specs/SPEC_5_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md``
declares load-bearing for the 5-variants-per-section rule:

1. Topic registry side — ``registry/<topic>.yaml``.
   Every section declares ``min_variants_required`` (the universal generator emits 5).
   This validator asserts ``len(variants) >= min_variants_required`` per section.

2. Persona atom side — ``atoms/<persona>/<topic>/<section_type>/CANONICAL.txt``.
   Variants are concatenated inside ``CANONICAL.txt`` under one of two header
   conventions in active use across the repo:

       ``## <SECTION_TYPE> vNN``   (~96% of variant headers; canonical going forward)
       ``--- variant: vNN``        (~4%; legacy format, primarily gen_z_professionals
                                    + 10 other personas; superset includes the rare
                                    ``--- variant: <TYPE> vNN`` typed dash form)

   This validator counts both header conventions and asserts ``>= min_variants``
   per required (persona × topic × section_type) tuple. Reconciling the two
   formats to a single canonical convention is a separate Pearl_Architect routing
   decision tracked outside this validator's scope.

Required section_types (spec §3.1 SOMATIC_10_SLOT_GRID + §3.3 beat overlay):

    HOOK, STORY, REFLECTION, EXERCISE, TEACHER_DOCTRINE, INTEGRATION,
    PIVOT, PERMISSION, TAKEAWAY, THREAD, COMPRESSION

Default exit code is 0 (warn-only). Spec §6 risk row 2 says Phase 1 ships
permissive so that CI does not break on the existing ~4,200-atom backlog;
``--strict`` flips to non-zero on any gap once Phase 2 authoring closes
coverage.

The default report path is ``artifacts/qa/variant_coverage_gap_<YYYY-MM-DD>.md``
to match spec §4.1 step 3.

This validator does no LLM calls and reads only from the local filesystem,
in compliance with the CLAUDE.md tier policy.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_DIR = REPO_ROOT / "registry"
DEFAULT_ATOMS_DIR = REPO_ROOT / "atoms"
DEFAULT_REPORT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "qa"
    / f"variant_coverage_gap_{dt.date.today().isoformat()}.md"
)

REQUIRED_SECTION_TYPES: tuple[str, ...] = (
    "HOOK",
    "STORY",
    "REFLECTION",
    "EXERCISE",
    "TEACHER_DOCTRINE",
    "INTEGRATION",
    "PIVOT",
    "PERMISSION",
    "TAKEAWAY",
    "THREAD",
    "COMPRESSION",
)

VARIANT_HEADER_RE = re.compile(
    r"^(?:##\s+[A-Z_]+\s+v\d+|---\s+variant:\s+(?:[A-Z_]+\s+)?v\d+)",
    re.MULTILINE,
)
DEFAULT_MIN_VARIANTS = 5


@dataclass
class RegistryGap:
    topic: str
    chapter: str
    section: str
    section_type: str
    have: int
    need: int


@dataclass
class AtomGap:
    persona: str
    topic: str
    section_type: str
    have: int
    need: int
    reason: str  # "below_threshold" | "missing_file"


@dataclass
class CoverageResult:
    registry_passed: int = 0
    registry_gaps: list[RegistryGap] = field(default_factory=list)
    atom_passed: int = 0
    atom_gaps: list[AtomGap] = field(default_factory=list)

    @property
    def total_gaps(self) -> int:
        return len(self.registry_gaps) + len(self.atom_gaps)


def discover_personas(atoms_dir: Path) -> list[str]:
    if not atoms_dir.is_dir():
        return []
    return sorted(p.name for p in atoms_dir.iterdir() if p.is_dir())


def discover_topics(registry_dir: Path) -> list[str]:
    if not registry_dir.is_dir():
        return []
    return sorted(p.stem for p in registry_dir.glob("*.yaml"))


def check_registry(registry_dir: Path, min_variants: int) -> tuple[int, list[RegistryGap]]:
    passed = 0
    gaps: list[RegistryGap] = []
    if not registry_dir.is_dir():
        return passed, gaps
    for yaml_path in sorted(registry_dir.glob("*.yaml")):
        topic = yaml_path.stem
        try:
            data = yaml.safe_load(yaml_path.read_text())
        except yaml.YAMLError as exc:
            print(
                f"variant-coverage: skipping registry/{yaml_path.name}: YAML parse error: {exc}",
                file=sys.stderr,
            )
            continue
        if not isinstance(data, dict):
            continue
        sections_root = data.get("sections", {}) or {}
        for chapter_key in sorted(sections_root):
            chapter = sections_root[chapter_key] or {}
            inner = chapter.get("sections", {}) or {}
            for section_key in sorted(inner):
                section = inner[section_key] or {}
                sec_type = section.get("type") or "UNKNOWN"
                need = int(section.get("min_variants_required") or min_variants)
                have = len(section.get("variants") or [])
                if have >= need:
                    passed += 1
                else:
                    gaps.append(
                        RegistryGap(
                            topic=topic,
                            chapter=chapter_key,
                            section=section_key,
                            section_type=sec_type,
                            have=have,
                            need=need,
                        )
                    )
    return passed, gaps


def count_atom_variants(canonical_path: Path) -> int:
    try:
        text = canonical_path.read_text(errors="replace")
    except OSError:
        return 0
    return len(VARIANT_HEADER_RE.findall(text))


def check_atoms(
    atoms_dir: Path,
    personas: list[str],
    topics: list[str],
    section_types: tuple[str, ...],
    min_variants: int,
) -> tuple[int, list[AtomGap]]:
    passed = 0
    gaps: list[AtomGap] = []
    for persona in personas:
        for topic in topics:
            base = atoms_dir / persona / topic
            for section_type in section_types:
                canonical = base / section_type / "CANONICAL.txt"
                if not canonical.is_file():
                    gaps.append(
                        AtomGap(
                            persona=persona,
                            topic=topic,
                            section_type=section_type,
                            have=0,
                            need=min_variants,
                            reason="missing_file",
                        )
                    )
                    continue
                count = count_atom_variants(canonical)
                if count >= min_variants:
                    passed += 1
                else:
                    gaps.append(
                        AtomGap(
                            persona=persona,
                            topic=topic,
                            section_type=section_type,
                            have=count,
                            need=min_variants,
                            reason="below_threshold",
                        )
                    )
    return passed, gaps


def render_report(result: CoverageResult, min_variants: int, today: str | None = None) -> str:
    today = today or dt.date.today().isoformat()
    lines: list[str] = []
    lines.append(f"# Variant Coverage Gap Report — {today}")
    lines.append("")
    lines.append(
        "Generated by `scripts/registry/validate_variant_coverage.py` per "
        "[`specs/SPEC_5_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md`](../../specs/SPEC_5_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md) "
        "Phase 1 §4.1."
    )
    lines.append("")
    lines.append("Phase 1 ships warn-only per spec §6 risk row 2. Strict mode (CI fail on gap) is gated on Phase 2 atom authoring closing the inventory.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- minimum variants per section: **{min_variants}**")
    lines.append(f"- registry sections passing: **{result.registry_passed}**")
    lines.append(f"- registry sections failing: **{len(result.registry_gaps)}**")
    lines.append(
        f"- atom (persona × topic × section_type) tuples passing: **{result.atom_passed}**"
    )
    lines.append(f"- atom tuples failing: **{len(result.atom_gaps)}**")
    lines.append(f"- total gaps: **{result.total_gaps}**")
    lines.append("")

    lines.append("## Registry gaps")
    lines.append("")
    if not result.registry_gaps:
        lines.append("_None — every registry section meets `min_variants_required`._")
    else:
        lines.append("| topic | chapter | section | type | have | need |")
        lines.append("|---|---|---|---|---:|---:|")
        for gap in sorted(
            result.registry_gaps,
            key=lambda g: (g.topic, g.chapter, g.section),
        ):
            lines.append(
                f"| {gap.topic} | {gap.chapter} | {gap.section} | {gap.section_type} "
                f"| {gap.have} | {gap.need} |"
            )
    lines.append("")

    below = [g for g in result.atom_gaps if g.reason == "below_threshold"]
    lines.append("## Atom gaps — below threshold")
    lines.append("")
    if not below:
        lines.append("_None — every present `CANONICAL.txt` has ≥ threshold variants._")
    else:
        lines.append("| persona | topic | section_type | have | need |")
        lines.append("|---|---|---|---:|---:|")
        for gap in sorted(below, key=lambda g: (g.persona, g.topic, g.section_type)):
            lines.append(
                f"| {gap.persona} | {gap.topic} | {gap.section_type} "
                f"| {gap.have} | {gap.need} |"
            )
    lines.append("")

    missing = [g for g in result.atom_gaps if g.reason == "missing_file"]
    lines.append("## Atom gaps — missing files")
    lines.append("")
    if not missing:
        lines.append(
            "_None — every required (persona × topic × section_type) tuple has a `CANONICAL.txt`._"
        )
    else:
        lines.append(
            "Each missing tuple means `atoms/<persona>/<topic>/<section_type>/CANONICAL.txt` does not exist."
        )
        lines.append("")
        lines.append("### Missing tuples by persona")
        lines.append("")
        lines.append("| persona | missing tuples |")
        lines.append("|---|---:|")
        for persona, count in sorted(Counter(g.persona for g in missing).items()):
            lines.append(f"| {persona} | {count} |")
        lines.append("")
        lines.append("### Missing tuples by topic")
        lines.append("")
        lines.append("| topic | missing tuples |")
        lines.append("|---|---:|")
        for topic, count in sorted(Counter(g.topic for g in missing).items()):
            lines.append(f"| {topic} | {count} |")
        lines.append("")
        lines.append("### Missing tuples by section_type")
        lines.append("")
        lines.append("| section_type | missing tuples |")
        lines.append("|---|---:|")
        for st, count in sorted(Counter(g.section_type for g in missing).items()):
            lines.append(f"| {st} | {count} |")
        lines.append("")
        lines.append("### Full missing tuple list")
        lines.append("")
        lines.append("| persona | topic | section_type |")
        lines.append("|---|---|---|")
        for gap in sorted(missing, key=lambda g: (g.persona, g.topic, g.section_type)):
            lines.append(f"| {gap.persona} | {gap.topic} | {gap.section_type} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Spec #739 Phase 1 variant-coverage gate. "
            "Default mode is warn-only (exit 0); pass --strict to fail on any gap."
        )
    )
    parser.add_argument(
        "--registry-dir", default=DEFAULT_REGISTRY_DIR, type=Path,
        help=f"Directory of <topic>.yaml registries. Default: {DEFAULT_REGISTRY_DIR}",
    )
    parser.add_argument(
        "--atoms-dir", default=DEFAULT_ATOMS_DIR, type=Path,
        help=f"Directory of persona atom trees. Default: {DEFAULT_ATOMS_DIR}",
    )
    parser.add_argument(
        "--report-out", default=DEFAULT_REPORT_PATH, type=Path,
        help="Output path for the markdown gap report.",
    )
    parser.add_argument(
        "--min-variants", default=DEFAULT_MIN_VARIANTS, type=int,
        help="Minimum variants per section/tuple. Spec §3.1 requires 5.",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit non-zero if any gap is found (Phase 2+ mode).",
    )
    parser.add_argument(
        "--skip-registry", action="store_true",
        help="Skip the registry/<topic>.yaml axis.",
    )
    parser.add_argument(
        "--skip-atoms", action="store_true",
        help="Skip the atoms/<persona>/<topic>/<section_type> axis.",
    )
    parser.add_argument(
        "--persona", action="append", default=None,
        help="Restrict atom check to the given persona (repeatable). "
             "Defaults to every persona discovered under --atoms-dir.",
    )
    parser.add_argument(
        "--topic", action="append", default=None,
        help="Restrict atom check to the given topic (repeatable). "
             "Defaults to every topic discovered under --registry-dir.",
    )
    parser.add_argument(
        "--no-report", action="store_true",
        help="Skip writing the markdown report to disk.",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-gap stderr lines.",
    )
    args = parser.parse_args(argv)

    result = CoverageResult()

    if not args.skip_registry:
        passed, gaps = check_registry(args.registry_dir, args.min_variants)
        result.registry_passed = passed
        result.registry_gaps = gaps

    if not args.skip_atoms:
        personas = args.persona or discover_personas(args.atoms_dir)
        topics = args.topic or discover_topics(args.registry_dir)
        passed, gaps = check_atoms(
            args.atoms_dir,
            personas,
            topics,
            REQUIRED_SECTION_TYPES,
            args.min_variants,
        )
        result.atom_passed = passed
        result.atom_gaps = gaps

    print(
        f"variant-coverage: registry passed={result.registry_passed} "
        f"gaps={len(result.registry_gaps)}; "
        f"atoms passed={result.atom_passed} "
        f"gaps={len(result.atom_gaps)}; "
        f"total_gaps={result.total_gaps}; "
        f"min_variants={args.min_variants}; "
        f"mode={'strict' if args.strict else 'warn-only'}"
    )

    if not args.no_report:
        report_path = args.report_out
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(render_report(result, args.min_variants))
        print(f"variant-coverage: report written to {report_path}")

    if not args.quiet:
        for gap in result.registry_gaps[:20]:
            print(
                f"  WARN registry: {gap.topic}/{gap.chapter}/{gap.section} "
                f"({gap.section_type}) have={gap.have} need={gap.need}",
                file=sys.stderr,
            )
        below = [g for g in result.atom_gaps if g.reason == "below_threshold"]
        for gap in below[:20]:
            print(
                f"  WARN atoms: {gap.persona}/{gap.topic}/{gap.section_type} "
                f"have={gap.have} need={gap.need}",
                file=sys.stderr,
            )
        missing_count = sum(1 for g in result.atom_gaps if g.reason == "missing_file")
        if missing_count:
            print(
                f"  WARN atoms: {missing_count} (persona × topic × section_type) "
                "tuples missing CANONICAL.txt",
                file=sys.stderr,
            )

    if args.strict and result.total_gaps > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
