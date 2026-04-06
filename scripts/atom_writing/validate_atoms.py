#!/usr/bin/env python3
"""
Atom Validator — validate_atoms.py

Standalone validator that can audit existing atoms OR validate new ones.
Checks format, metadata, word counts, forbidden constructions, and coverage.

Usage:
  # Validate a single file
  python scripts/atom_writing/validate_atoms.py \
    --file atoms/corporate_managers/anxiety/HOOK/CANONICAL.txt --slot HOOK

  # Audit all atoms for a persona
  python scripts/atom_writing/validate_atoms.py --audit --persona corporate_managers

  # Full catalog audit
  python scripts/atom_writing/validate_atoms.py --audit

  # Coverage report (counts only, fast)
  python scripts/atom_writing/validate_atoms.py --coverage

  # Output as JSON
  python scripts/atom_writing/validate_atoms.py --audit --json
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("atom_validator")

# ─── CONSTANTS ──────────────────────────────────────────────────────────────

ALL_PERSONAS = [
    "corporate_managers", "educators", "entrepreneurs", "first_responders",
    "gen_alpha_students", "gen_x_sandwich", "gen_z_professionals",
    "gen_z_student", "healthcare_rns", "millennial_women_professionals",
    "nyc_executives", "tech_finance_burnout", "working_parents",
]

ALL_TOPICS = [
    "adhd_focus", "anxiety", "boundaries", "burnout", "compassion_fatigue",
    "courage", "depression", "financial_anxiety", "financial_stress", "grief",
    "imposter_syndrome", "mindfulness", "overthinking", "self_worth",
    "sleep_anxiety", "social_anxiety", "somatic_healing",
]

CANONICAL_SLOT_TYPES = [
    "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION",
    "PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "COMPRESSION",
]

ENGINE_DIRS = [
    "watcher", "shame", "comparison", "false_alarm",
    "overwhelm", "grief", "spiral",
]

METADATA_FIELDS: dict[str, list[str]] = {
    "STORY": ["MECHANISM_DEPTH", "IDENTITY_STAGE", "COST_TYPE", "COST_INTENSITY"],
    "REFLECTION": ["family", "voice_mode", "mechanism_emphasis"],
    "INTEGRATION": ["integration_mode", "reframe_type"],
}

WORD_LIMITS: dict[str, int] = {
    "HOOK": 60,
    "SCENE": 80,
    "STORY": 300,
    "REFLECTION": 220,
    "EXERCISE": 80,
    "INTEGRATION": 250,
    "PIVOT": 40,
    "TAKEAWAY": 60,
    "THREAD": 60,
    "PERMISSION": 60,
    "COMPRESSION": 120,
}

# Engine atom word limits (same across all engines)
for eng in ENGINE_DIRS:
    WORD_LIMITS[eng] = 300

FORBIDDEN_PATTERNS = [
    (re.compile(r"\?"), "rhetorical_question"),
    (re.compile(r"\bperhaps\b", re.I), "tentative_perhaps"),
    (re.compile(r"\byou might\b", re.I), "tentative_you_might"),
    (re.compile(r"\bit'?s possible\b", re.I), "tentative_its_possible"),
    (re.compile(r"\bmaybe\b", re.I), "tentative_maybe"),
    (re.compile(r"\bcould be\b", re.I), "tentative_could_be"),
    (re.compile(r"\bmight be\b", re.I), "tentative_might_be"),
    (re.compile(r"\byou may want to\b", re.I), "tentative_you_may"),
    (re.compile(r"\bconsider trying\b", re.I), "tentative_consider"),
    (re.compile(r"\bwas feeling\b", re.I), "passive_was_feeling"),
    (re.compile(r"\bwas sitting\b", re.I), "passive_was_sitting"),
    (re.compile(r"\bwas thinking\b", re.I), "passive_was_thinking"),
    (re.compile(r"\bwere looking\b", re.I), "passive_were_looking"),
    (re.compile(r"\bhad been\b", re.I), "passive_had_been"),
]


# ─── VALIDATION ─────────────────────────────────────────────────────────────

@dataclass
class FileValidation:
    file_path: str
    valid: bool = True
    variants: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    word_counts: list[int] = field(default_factory=list)
    metadata_present: bool = False

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "valid": self.valid,
            "variants": self.variants,
            "errors": self.errors,
            "warnings": self.warnings,
            "word_counts": self.word_counts,
            "metadata_present": self.metadata_present,
        }


def parse_variants(content: str) -> list[tuple[str, str, str, str]]:
    """
    Parse CANONICAL.txt format into list of (type_name, variant_number, metadata_str, prose).
    """
    variants: list[tuple[str, str, str, str]] = []

    header_re = re.compile(r"^## (\w+) v(\d{2})\s*$", re.MULTILINE)
    headers = list(header_re.finditer(content))

    for idx, match in enumerate(headers):
        type_name = match.group(1)
        vnum = match.group(2)
        start = match.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(content)

        block = content[start:end].strip()
        parts = block.split("---")
        parts = [p for p in parts if p is not None]

        if len(parts) >= 3:
            metadata_str = parts[1].strip()
            prose = parts[2].strip()
            variants.append((type_name, vnum, metadata_str, prose))
        elif len(parts) == 2:
            metadata_str = parts[0].strip() if parts[0].strip() else ""
            prose = parts[1].strip()
            variants.append((type_name, vnum, metadata_str, prose))

    return variants


def validate_canonical(file_path: Path, slot_type: str | None = None) -> FileValidation:
    """
    Validate a single CANONICAL.txt file.

    Returns FileValidation with errors, warnings, word counts.
    """
    result = FileValidation(file_path=str(file_path))

    if not file_path.exists():
        result.valid = False
        result.errors.append("File does not exist")
        return result

    content = file_path.read_text(encoding="utf-8")
    if not content.strip():
        result.valid = False
        result.errors.append("File is empty")
        return result

    # Auto-detect slot type from path if not provided
    if slot_type is None:
        slot_type = file_path.parent.name

    variants = parse_variants(content)
    result.variants = len(variants)

    if not variants:
        result.valid = False
        result.errors.append("No valid variants found")
        return result

    word_limit = WORD_LIMITS.get(slot_type, 300)
    has_metadata = slot_type in METADATA_FIELDS

    for type_name, vnum, metadata_str, prose in variants:
        # Word count
        wc = len(prose.split())
        result.word_counts.append(wc)

        if wc > word_limit:
            result.warnings.append(
                f"v{vnum}: {wc} words exceeds soft limit of {word_limit} for {slot_type}"
            )

        if wc < 3:
            result.errors.append(f"v{vnum}: suspiciously short ({wc} words)")

        # Metadata check
        if has_metadata:
            required = METADATA_FIELDS[slot_type]
            missing = []
            for field_name in required:
                if field_name.lower() not in metadata_str.lower():
                    missing.append(field_name)
            if missing:
                result.warnings.append(f"v{vnum}: missing metadata: {', '.join(missing)}")
            else:
                result.metadata_present = True

        # Forbidden constructions
        for pattern, label in FORBIDDEN_PATTERNS:
            if pattern.search(prose):
                if label == "rhetorical_question":
                    result.warnings.append(f"v{vnum}: contains '?' ({label})")
                else:
                    result.warnings.append(f"v{vnum}: forbidden construction '{label}'")

    # Mark invalid only for hard errors
    if result.errors:
        result.valid = False

    return result


# ─── AUDIT MODE ─────────────────────────────────────────────────────────────

@dataclass
class AuditReport:
    total_files: int = 0
    total_variants: int = 0
    valid_files: int = 0
    invalid_files: int = 0
    files_with_warnings: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    coverage: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    details: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "total_variants": self.total_variants,
            "valid_files": self.valid_files,
            "invalid_files": self.invalid_files,
            "files_with_warnings": self.files_with_warnings,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "missing_count": len(self.missing),
            "missing": self.missing[:50],  # cap for readability
        }


def audit_atoms(
    personas: list[str] | None = None,
    topics: list[str] | None = None,
    include_engines: bool = True,
    atoms_dir: Path | None = None,
) -> AuditReport:
    """
    Scan atoms directory and validate all CANONICAL.txt files.
    Returns an AuditReport with coverage and validation results.
    """
    if atoms_dir is None:
        atoms_dir = REPO_ROOT / "atoms"

    if personas is None:
        personas = ALL_PERSONAS
    if topics is None:
        topics = ALL_TOPICS

    report = AuditReport()

    for persona in personas:
        persona_dir = atoms_dir / persona
        if not persona_dir.exists():
            for topic in topics:
                for slot in CANONICAL_SLOT_TYPES:
                    report.missing.append(f"{persona}/{topic}/{slot}")
            continue

        for topic in topics:
            topic_dir = persona_dir / topic
            if not topic_dir.exists():
                for slot in CANONICAL_SLOT_TYPES:
                    report.missing.append(f"{persona}/{topic}/{slot}")
                continue

            # Check canonical slot types
            for slot in CANONICAL_SLOT_TYPES:
                canon = topic_dir / slot / "CANONICAL.txt"
                if not canon.exists():
                    report.missing.append(f"{persona}/{topic}/{slot}")
                    continue

                result = validate_canonical(canon, slot)
                report.total_files += 1
                report.total_variants += result.variants
                report.total_errors += len(result.errors)
                report.total_warnings += len(result.warnings)

                if result.valid:
                    report.valid_files += 1
                else:
                    report.invalid_files += 1

                if result.warnings:
                    report.files_with_warnings += 1

                # Track coverage
                key = f"{persona}/{topic}"
                if key not in report.coverage:
                    report.coverage[key] = {}
                report.coverage[key][slot] = f"{result.variants}v"

                if result.errors or result.warnings:
                    report.details.append(result.to_dict())

            # Check engine dirs
            if include_engines:
                for engine in ENGINE_DIRS:
                    canon = topic_dir / engine / "CANONICAL.txt"
                    if not canon.exists():
                        continue  # Engine atoms are optional

                    result = validate_canonical(canon, engine)
                    report.total_files += 1
                    report.total_variants += result.variants

                    if result.valid:
                        report.valid_files += 1
                    else:
                        report.invalid_files += 1

    return report


# ─── COVERAGE REPORT ────────────────────────────────────────────────────────

def coverage_report(
    personas: list[str] | None = None,
    atoms_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Quick coverage count — no validation, just counts variants per slot.
    """
    if atoms_dir is None:
        atoms_dir = REPO_ROOT / "atoms"
    if personas is None:
        personas = ALL_PERSONAS

    coverage: dict[str, dict[str, int]] = {}
    totals: dict[str, int] = defaultdict(int)

    for persona in personas:
        persona_dir = atoms_dir / persona
        if not persona_dir.exists():
            continue

        for topic_dir in sorted(persona_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            topic = topic_dir.name
            key = f"{persona}/{topic}"
            coverage[key] = {}

            for slot_dir in sorted(topic_dir.iterdir()):
                if not slot_dir.is_dir():
                    continue
                slot = slot_dir.name
                canon = slot_dir / "CANONICAL.txt"

                if not canon.exists():
                    coverage[key][slot] = 0
                    continue

                content = canon.read_text(encoding="utf-8")
                header_re = re.compile(r"^## \w+ v\d{2}\s*$", re.MULTILINE)
                count = len(header_re.findall(content))
                coverage[key][slot] = count
                totals[slot] += count

    return {
        "coverage": coverage,
        "totals": dict(totals),
        "total_variants": sum(totals.values()),
        "total_cells": len(coverage),
    }


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(description="Validate Phoenix atoms")
    parser.add_argument("--file", type=Path, help="Validate a single CANONICAL.txt file")
    parser.add_argument("--slot", help="Slot type (auto-detected from path if not given)")
    parser.add_argument("--audit", action="store_true", help="Audit all atoms")
    parser.add_argument("--coverage", action="store_true", help="Quick coverage count")
    parser.add_argument("--persona", action="append", help="Filter to specific persona(s)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--atoms-dir", type=Path, default=None)

    args = parser.parse_args()

    personas = args.persona if args.persona else None

    # Single file validation
    if args.file:
        result = validate_canonical(args.file, args.slot)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            status = "VALID" if result.valid else "INVALID"
            print(f"{status}: {result.file_path}")
            print(f"  Variants: {result.variants}")
            print(f"  Word counts: {result.word_counts}")
            if result.errors:
                print(f"  Errors ({len(result.errors)}):")
                for e in result.errors:
                    print(f"    - {e}")
            if result.warnings:
                print(f"  Warnings ({len(result.warnings)}):")
                for w in result.warnings:
                    print(f"    - {w}")
        sys.exit(0 if result.valid else 1)

    # Coverage report
    if args.coverage:
        report = coverage_report(personas=personas, atoms_dir=args.atoms_dir)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Total variants: {report['total_variants']}")
            print(f"Total cells (persona/topic): {report['total_cells']}")
            print("\nSlot totals:")
            for slot, count in sorted(report["totals"].items(), key=lambda x: -x[1]):
                print(f"  {slot:20s} {count:6d}")
        sys.exit(0)

    # Full audit
    if args.audit:
        report = audit_atoms(personas=personas, atoms_dir=args.atoms_dir)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print("=== ATOM AUDIT REPORT ===")
            print(f"Files scanned:      {report.total_files}")
            print(f"Total variants:     {report.total_variants}")
            print(f"Valid files:        {report.valid_files}")
            print(f"Invalid files:      {report.invalid_files}")
            print(f"Files w/ warnings:  {report.files_with_warnings}")
            print(f"Total errors:       {report.total_errors}")
            print(f"Total warnings:     {report.total_warnings}")
            print(f"Missing slots:      {len(report.missing)}")
            if report.missing:
                print("\nFirst 20 missing slots:")
                for m in report.missing[:20]:
                    print(f"  {m}")
            if report.details:
                print(f"\nFiles with issues ({len(report.details)}):")
                for d in report.details[:10]:
                    print(f"  {d['file_path']}: {len(d['errors'])} errors, {len(d['warnings'])} warnings")
        sys.exit(0 if report.invalid_files == 0 else 1)

    parser.print_help()


if __name__ == "__main__":
    main()
