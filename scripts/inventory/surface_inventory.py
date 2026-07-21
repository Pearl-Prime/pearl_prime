#!/usr/bin/env python3
"""Measurement-only atom surface/depth inventory.

This extends the existing atom coverage audit with parsed variant counts and
reader-transformation signals. It never edits atom text and starts as warn-only.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TAXONOMY = REPO_ROOT / "config" / "atoms" / "surface_taxonomy.yaml"
DEFAULT_THRESHOLDS = REPO_ROOT / "config" / "qa" / "variation_thresholds.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "inventory"
KNOWN_NON_SURFACE_PARTS = {"locales"}

HEADING_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
VARIANT_RE = re.compile(r"(?m)^---\s*variant:\s*(\S+)\s*$", re.IGNORECASE)
WORD_RE = re.compile(r"[A-Za-z0-9']+")


@dataclass(frozen=True)
class ParsedVariant:
    variant_id: str
    surface_key: str
    metadata: dict[str, str]
    body: str
    word_count: int
    signals: dict[str, bool]
    warnings: tuple[str, ...]


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def _strip_closing_fence(lines: list[str]) -> list[str]:
    if lines and lines[-1].strip() == "---":
        return lines[:-1]
    return lines


def _parse_metadata(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    if not lines or lines[0].strip() != "---":
        return {}, lines
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            meta: dict[str, str] = {}
            for raw in lines[1:idx]:
                if ":" in raw:
                    key, value = raw.split(":", 1)
                    meta[key.strip()] = value.strip()
            return meta, lines[idx + 1 :]
    return {}, lines


def _variant_blocks(text: str) -> list[tuple[str, str]]:
    headings = list(HEADING_RE.finditer(text))
    if headings:
        blocks: list[tuple[str, str]] = []
        for idx, match in enumerate(headings):
            end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
            blocks.append((match.group(1).strip(), text[match.end() : end]))
        return blocks

    variant_markers = list(VARIANT_RE.finditer(text))
    if variant_markers:
        blocks = []
        for idx, match in enumerate(variant_markers):
            end = variant_markers[idx + 1].start() if idx + 1 < len(variant_markers) else len(text)
            blocks.append((match.group(1).strip(), text[match.end() : end]))
        return blocks

    stripped = text.strip()
    return [("variant_001", stripped)] if stripped else []


def _surface_from_label(label: str, fallback: str) -> str:
    token = (label or "").strip().split()
    if token:
        surface = re.sub(r"[^A-Za-z0-9_]+", "_", token[0]).upper()
        if surface and not surface.startswith("V"):
            return surface
    return fallback.upper()


def _signals(text: str, metadata: dict[str, str]) -> dict[str, bool]:
    lower = (text or "").lower()
    meta_keys = {k.upper() for k in metadata}
    return {
        "intro": _word_count(text) >= 5,
        "felt_concrete_experience": bool(
            re.search(r"\b(body|chest|hands?|feet|breath|jaw|room|car|shift|floor|wall|eyes?)\b", lower)
        ),
        "insight_aha": bool(
            re.search(r"\b(realiz(?:e|ed)|underst(?:and|ood)|notice|truth|learn|because|not .{0,40} but)\b", lower)
        ),
        "integration": bool(
            re.search(r"\b(now|then|try|practice|repeat|breathe|notice|let|carry|return|remember)\b", lower)
        ),
        "handoff": bool(
            re.search(r"\b(now|then|after|next|carry|return|remember|repeat|let)\b", lower[-260:])
        ),
        "source_provenance": bool(meta_keys & {"SOURCE", "CITATION", "QUOTE_SOURCE", "PROVENANCE"})
        or bool(re.search(r"\b(according to|study|research|quote|source)\b", lower)),
        "story_event": bool(re.search(r"\b(that|one|the)\s+(day|morning|night|week|tuesday|moment)\b", lower)),
        "story_stake": bool(re.search(r"\b(needed|wanted|afraid|risk|threat|safe|unsafe|couldn't|had to)\b", lower)),
        "story_turn": bool(re.search(r"\b(but|then|until|when|that was|changed|instead)\b", lower)),
        "story_cost": bool(re.search(r"\b(cost|lost|hurt|broke|price|debt|alone|exhausted|shame)\b", lower)),
        "story_residue": bool(re.search(r"\b(after|still|stayed|left|remained|followed|carried)\b", lower)),
        "exercise_body_step": bool(re.search(r"\b(press|breathe|inhale|exhale|stand|sit|hands?|feet|count|notice)\b", lower)),
    }


def parse_canonical_variants(path: Path, *, fallback_surface: str, min_body_words: int = 3) -> list[ParsedVariant]:
    """Parse real variant bodies from a CANONICAL.txt file."""
    text = path.read_text(encoding="utf-8")
    variants: list[ParsedVariant] = []
    for label, block in _variant_blocks(text):
        lines = _strip_closing_fence(block.strip().splitlines())
        metadata, body_lines = _parse_metadata(lines)
        body = "\n".join(_strip_closing_fence(body_lines)).strip()
        wc = _word_count(body)
        if wc < min_body_words:
            continue
        surface_key = _surface_from_label(label, fallback_surface)
        signals = _signals(body, metadata)
        warnings: list[str] = []
        if wc < 18:
            warnings.append("SHALLOW_SHORT_BODY")
        if body.count("\n") >= 4 and wc / max(body.count("\n") + 1, 1) < 8:
            warnings.append("BULLET_LIKE_DENSITY")
        variants.append(
            ParsedVariant(
                variant_id=label,
                surface_key=surface_key,
                metadata=metadata,
                body=body,
                word_count=wc,
                signals=signals,
                warnings=tuple(warnings),
            )
        )
    return variants


def _canonical_paths(repo_root: Path) -> Iterable[Path]:
    atoms_root = repo_root / "atoms"
    if not atoms_root.exists():
        return []
    return sorted(
        p for p in atoms_root.glob("*/*/**/CANONICAL.txt")
        if KNOWN_NON_SURFACE_PARTS.isdisjoint(p.relative_to(atoms_root).parts)
    )


def _path_cell(path: Path, repo_root: Path) -> tuple[str, str, str] | None:
    rel = path.relative_to(repo_root)
    parts = rel.parts
    if len(parts) < 5 or parts[0] != "atoms":
        return None
    persona, topic, surface = parts[1], parts[2], parts[3]
    if surface in KNOWN_NON_SURFACE_PARTS:
        return None
    return persona, topic, surface.upper()


def _threshold_for(surface: str, taxonomy_row: dict[str, Any], thresholds: dict[str, Any]) -> int:
    by_surface = thresholds.get("min_variants_by_surface") or {}
    if surface in by_surface:
        return int(by_surface[surface])
    if taxonomy_row.get("min_variants_per_cell"):
        return int(taxonomy_row["min_variants_per_cell"])
    return int(thresholds.get("default_min_variants_per_cell") or 3)


def _story_warnings(variants: list[ParsedVariant], required: list[str]) -> list[str]:
    if not variants:
        return ["NO_STORY_VARIANTS"]
    present = {
        "event": any(v.signals["story_event"] for v in variants),
        "stake": any(v.signals["story_stake"] for v in variants),
        "turn": any(v.signals["story_turn"] for v in variants),
        "cost": any(v.signals["story_cost"] for v in variants),
        "residue": any(v.signals["story_residue"] for v in variants),
    }
    return [f"STORY_SIGNAL_MISSING_{name.upper()}" for name in required if not present.get(name)]


def _exercise_warnings(variants: list[ParsedVariant]) -> list[str]:
    if not variants:
        return ["NO_EXERCISE_VARIANTS"]
    warnings: list[str] = []
    if not any(v.signals["exercise_body_step"] for v in variants):
        warnings.append("EXERCISE_BODY_STEP_MISSING")
    if not any(v.signals["insight_aha"] for v in variants):
        warnings.append("EXERCISE_AHA_MISSING")
    if not any(v.signals["integration"] for v in variants):
        warnings.append("EXERCISE_INTEGRATION_MISSING")
    return warnings


def build_surface_inventory(
    *,
    repo_root: Path = REPO_ROOT,
    personas: list[str] | None = None,
    topics: list[str] | None = None,
    max_cells: int | None = None,
    taxonomy_path: Path = DEFAULT_TAXONOMY,
    thresholds_path: Path = DEFAULT_THRESHOLDS,
) -> dict[str, Any]:
    taxonomy = _load_yaml(taxonomy_path)
    thresholds = _load_yaml(thresholds_path)
    surface_types = taxonomy.get("surface_types") or {}
    default_taxonomy = taxonomy.get("default") or {}
    min_body_words = int(thresholds.get("min_body_words") or 3)
    persona_filter = set(personas or [])
    topic_filter = set(topics or [])
    cells: list[dict[str, Any]] = []

    for path in _canonical_paths(repo_root):
        cell = _path_cell(path, repo_root)
        if cell is None:
            continue
        persona, topic, surface = cell
        if persona_filter and persona not in persona_filter:
            continue
        if topic_filter and topic not in topic_filter:
            continue
        taxonomy_row = dict(surface_types.get(surface) or default_taxonomy)
        variants = parse_canonical_variants(path, fallback_surface=surface, min_body_words=min_body_words)
        variant_count = len(variants)
        min_variants = _threshold_for(surface, taxonomy_row, thresholds)
        warnings: list[str] = []
        if surface not in surface_types:
            warnings.append("PROVISIONAL_UNMAPPED_SURFACE")
        if variant_count < min_variants:
            warnings.append(f"VARIANT_COUNT_BELOW_MIN_{variant_count}_LT_{min_variants}")
        warnings.extend(sorted({w for v in variants for w in v.warnings}))
        story_policy = str(taxonomy_row.get("story_policy") or "")
        exercise_policy = str(taxonomy_row.get("exercise_policy") or "")
        if story_policy == "same_person_story":
            warnings.extend(_story_warnings(variants, list(thresholds.get("story_required_signals") or [])))
        if exercise_policy == "canonical_exercise":
            warnings.extend(_exercise_warnings(variants))
        if taxonomy_row.get("source_provenance_required") and not any(v.signals["source_provenance"] for v in variants):
            warnings.append("SOURCE_PROVENANCE_MISSING")
        cells.append(
            {
                "cell_id": f"{persona}/{topic}/{surface}",
                "persona": persona,
                "topic": topic,
                "surface_key": surface,
                "canonical_path": str(path.relative_to(repo_root)),
                "role": taxonomy_row.get("role"),
                "allowed_slots": taxonomy_row.get("allowed_slots") or [],
                "depth_contract": taxonomy_row.get("depth_contract") or [],
                "reader_state_entry": taxonomy_row.get("reader_state_entry"),
                "reader_state_exit": taxonomy_row.get("reader_state_exit"),
                "source_provenance_required": bool(taxonomy_row.get("source_provenance_required")),
                "exercise_policy": exercise_policy,
                "story_policy": story_policy,
                "variant_count": variant_count,
                "min_variants_per_cell": min_variants,
                "variant_word_counts": [v.word_count for v in variants],
                "variant_ids": [v.variant_id for v in variants],
                "warnings": sorted(set(warnings)),
                "status": "WARN" if warnings else "PASS",
            }
        )
        if max_cells and len(cells) >= max_cells:
            break

    warn_count = sum(1 for c in cells if c["status"] == "WARN")
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_spec": str(taxonomy.get("source_spec") or ""),
        "warn_only": bool(thresholds.get("warn_only", True)),
        "repo_root": str(repo_root),
        "cells": cells,
        "stats": {
            "cells": len(cells),
            "pass": len(cells) - warn_count,
            "warn": warn_count,
            "atom_text_edited": False,
        },
    }


def _markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Atom Surface Inventory",
        "",
        f"Generated: {manifest['generated_at']}",
        f"Warn only: {manifest['warn_only']}",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Cells | {manifest['stats']['cells']} |",
        f"| PASS | {manifest['stats']['pass']} |",
        f"| WARN | {manifest['stats']['warn']} |",
        f"| Atom text edited | {str(manifest['stats']['atom_text_edited']).lower()} |",
        "",
        "## Cells",
        "",
        "| Cell | Variants | Min | Status | Warnings |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for cell in manifest["cells"]:
        warnings = ", ".join(cell["warnings"][:6])
        lines.append(
            f"| `{cell['cell_id']}` | {cell['variant_count']} | "
            f"{cell['min_variants_per_cell']} | {cell['status']} | {warnings} |"
        )
    return "\n".join(lines) + "\n"


def write_surface_inventory(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    basename: str = "surface_inventory",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    md_path = output_dir / f"{basename}.md"
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(manifest), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit measurement-only atom surface/depth inventory")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--persona", action="append", dest="personas")
    parser.add_argument("--topic", action="append", dest="topics")
    parser.add_argument("--max-cells", type=int)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    manifest = build_surface_inventory(
        repo_root=args.repo_root,
        personas=args.personas,
        topics=args.topics,
        max_cells=args.max_cells,
    )
    paths = write_surface_inventory(manifest, args.output_dir)
    print(f"JSON written: {paths['json']}")
    print(f"Report written: {paths['markdown']}")
    print(f"Cells: {manifest['stats']['cells']} WARN: {manifest['stats']['warn']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
