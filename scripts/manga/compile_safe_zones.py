#!/usr/bin/env python3
"""Compile §5 inheritance YAML into the flat compiled safe-zones table.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §13.2 Phase B.1 step 1.

Inheritance chain (precedence increases left to right):

    base_contract -> framing_contract -> subject_contract -> genre_modifier -> archetype_exception

Output: config/manga/compiled/safe_zones.yaml (the flat compiled view; §5.7).

DETERMINISTIC. No model inference. No heuristics. No magic. Schema validation +
dict merge + override precedence + cycle detection + required-field enforcement.
Any error is fatal (exit code 2). This is feature, not bug — the compiler is
boring on purpose.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = REPO / "config" / "manga" / "safe_zones"
DEFAULT_OUTPUT = REPO / "config" / "manga" / "compiled" / "safe_zones.yaml"


class SchemaError(Exception):
    """Required field missing, unknown type, unknown reference, malformed input."""


class CycleError(Exception):
    """Subject_contract.inherits_from chain forms a cycle."""


_INPUT_FILES = {
    "base_contract": "base_contract.yaml",
    "framing_contract": "framing_contract.yaml",
    "subject_contract": "subject_contract.yaml",
    "genre_modifier": "genre_modifier.yaml",
    "archetype_exception": "archetype_exception.yaml",
}


def _load_yaml(path: Path) -> dict:
    if not path.is_file():
        raise SchemaError(f"input file not found: {path}")
    with path.open("r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise SchemaError(f"{path}: top-level must be a mapping")
    return data


def _require(d: dict, keys: list[str], where: str) -> None:
    missing = [k for k in keys if k not in d]
    if missing:
        raise SchemaError(f"missing required keys {missing} in {where}")


def load_all(input_dir: Path) -> dict[str, dict]:
    """Load and lightly schema-validate the 5 input YAMLs."""
    docs: dict[str, dict] = {}
    for expected_type, filename in _INPUT_FILES.items():
        doc = _load_yaml(input_dir / filename)
        _require(doc, ["schema_version", "type"], filename)
        if doc["type"] != expected_type:
            raise SchemaError(
                f"{filename}: type must be {expected_type!r}, got {doc['type']!r}"
            )
        docs[expected_type] = doc
    return docs


def _deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge overrides into base. Later wins. Returns new dict."""
    out = deepcopy(base)
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = deepcopy(v)
    return out


def _apply_dotted_overrides(target: dict, overrides: dict) -> dict:
    """Apply overrides where keys may be dotted paths.

    Two forms supported per key:
      "margin.top": 15            -> dotted path, single scalar leaf
      "margin": {top: 7, ...}     -> direct subtree merge
    """
    out = deepcopy(target)
    for k, v in overrides.items():
        if "." in k:
            parts = k.split(".")
            node = out
            for p in parts[:-1]:
                if p not in node or not isinstance(node[p], dict):
                    node[p] = {}
                node = node[p]
            node[parts[-1]] = deepcopy(v)
        else:
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = _deep_merge(out[k], v)
            else:
                out[k] = deepcopy(v)
    return out


def _subject_inherits_framing(
    subject_id: str,
    subject_doc: dict,
    _seen: set[str] | None = None,
) -> str | None:
    """Return the framing_id a subject inherits from, or None if base."""
    if _seen is None:
        _seen = set()
    if subject_id in _seen:
        raise CycleError(
            f"cycle in subject_contract inheritance: {' -> '.join(list(_seen) + [subject_id])}"
        )
    _seen = _seen | {subject_id}
    contracts = subject_doc.get("contracts", {})
    if subject_id not in contracts:
        raise SchemaError(f"unknown subject_contract {subject_id!r}")
    inh = contracts[subject_id].get("inherits_from", "")
    if inh.startswith("framing."):
        return inh.split(".", 1)[1]
    if inh.startswith("subject."):
        parent = inh.split(".", 1)[1]
        return _subject_inherits_framing(parent, subject_doc, _seen)
    return None


def resolve_subject(
    subject_id: str,
    subject_doc: dict,
    framing_doc: dict,
    base_doc: dict,
    _seen: set[str] | None = None,
) -> dict:
    """Resolve a subject_contract: base + framing + own overrides."""
    if _seen is None:
        _seen = set()
    if subject_id in _seen:
        raise CycleError(
            f"cycle in subject_contract inheritance: {' -> '.join(list(_seen) + [subject_id])}"
        )
    _seen = _seen | {subject_id}

    contracts = subject_doc.get("contracts", {})
    if subject_id not in contracts:
        raise SchemaError(f"unknown subject_contract {subject_id!r}")
    entry = contracts[subject_id]
    inh = entry.get("inherits_from", "")

    if inh.startswith("framing."):
        framing_id = inh.split(".", 1)[1]
        framings = framing_doc.get("contracts", {})
        if framing_id not in framings:
            raise SchemaError(
                f"unknown framing_contract {framing_id!r} referenced by subject_contract {subject_id!r}"
            )
        merged = _deep_merge(base_doc.get("contract", {}), framings[framing_id])
    elif inh.startswith("subject."):
        parent = inh.split(".", 1)[1]
        merged = resolve_subject(parent, subject_doc, framing_doc, base_doc, _seen)
    elif inh == "":
        merged = deepcopy(base_doc.get("contract", {}))
    else:
        raise SchemaError(
            f"unknown inherits_from {inh!r} in subject_contract {subject_id!r}"
        )

    overrides = entry.get("overrides", {})
    if overrides:
        merged = _apply_dotted_overrides(merged, overrides)
    return merged


def apply_genre(
    target: dict,
    subject_id: str,
    framing_id: str | None,
    genre_id: str,
    genre_doc: dict,
) -> dict:
    """Apply a genre_modifier to a resolved (subject, framing) contract.

    Genre overrides are scope-targeted: framing_overrides only fire if the
    subject's framing matches; subject_overrides only fire if the subject_id
    matches; composite_additions apply universally.
    """
    modifiers = genre_doc.get("modifiers", {})
    if genre_id not in modifiers:
        raise SchemaError(f"unknown genre_modifier {genre_id!r}")
    mod = modifiers[genre_id]

    out = deepcopy(target)

    fr_over = mod.get("framing_overrides", {}) or {}
    if framing_id and framing_id in fr_over:
        out = _apply_dotted_overrides(out, fr_over[framing_id])

    sb_over = mod.get("subject_overrides", {}) or {}
    if subject_id in sb_over:
        out = _apply_dotted_overrides(out, sb_over[subject_id])

    comp_add = mod.get("composite_additions", {}) or {}
    if comp_add:
        out = _apply_dotted_overrides(out, comp_add)

    return out


def resolve_archetype_exception(
    archetype_id: str,
    docs: dict[str, dict],
) -> dict:
    """Resolve an archetype_exception entry into its final compiled contract."""
    arch_doc = docs["archetype_exception"]
    exceptions = arch_doc.get("exceptions", {})
    if archetype_id not in exceptions:
        raise SchemaError(f"unknown archetype_exception {archetype_id!r}")
    entry = exceptions[archetype_id]

    base_path = entry.get("base", "")
    if not isinstance(base_path, str) or not base_path.startswith("subject_contract."):
        raise SchemaError(
            f"archetype_exception {archetype_id!r}: base must be 'subject_contract.<id>', got {base_path!r}"
        )
    subject_id = base_path.split(".", 1)[1]

    target = resolve_subject(
        subject_id,
        docs["subject_contract"],
        docs["framing_contract"],
        docs["base_contract"],
    )
    framing_id = _subject_inherits_framing(subject_id, docs["subject_contract"])

    genre_id = entry.get("genre", "")
    if genre_id:
        target = apply_genre(
            target, subject_id, framing_id, genre_id, docs["genre_modifier"]
        )

    overrides = entry.get("overrides", {})
    if overrides:
        target = _apply_dotted_overrides(target, overrides)

    target["_provenance"] = {
        "subject": subject_id,
        "framing": framing_id,
        "genre": genre_id or None,
        "archetype_exception": archetype_id,
    }
    return target


def compile_table(docs: dict[str, dict]) -> dict:
    """Produce the full compiled flat table.

    Rows:
      "subject=<id>|framing=<id>|genre=<id>"   -- one per (subject, genre) combination
      "archetype_exception=<id>"               -- one per archetype exception
    """
    rows: dict[str, dict] = {}

    subject_doc = docs["subject_contract"]
    framing_doc = docs["framing_contract"]
    base_doc = docs["base_contract"]
    genre_doc = docs["genre_modifier"]

    for subject_id in sorted(subject_doc.get("contracts", {})):
        framing_id = _subject_inherits_framing(subject_id, subject_doc)
        resolved = resolve_subject(subject_id, subject_doc, framing_doc, base_doc)
        for genre_id in sorted(genre_doc.get("modifiers", {})):
            row = apply_genre(resolved, subject_id, framing_id, genre_id, genre_doc)
            row["_provenance"] = {
                "subject": subject_id,
                "framing": framing_id,
                "genre": genre_id,
            }
            key = f"subject={subject_id}|framing={framing_id}|genre={genre_id}"
            rows[key] = row

    for arch_id in sorted(docs["archetype_exception"].get("exceptions", {})):
        rows[f"archetype_exception={arch_id}"] = resolve_archetype_exception(
            arch_id, docs
        )

    return {
        "schema_version": "1.0.0",
        "compiled": rows,
    }


def _stable_yaml_dump(data: Any) -> str:
    """Dump YAML with stable key ordering for hash determinism."""
    return yaml.safe_dump(
        data,
        default_flow_style=False,
        sort_keys=True,
        allow_unicode=True,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compile manga safe-zone inheritance YAML into flat table."
    )
    ap.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument(
        "--print-hash",
        action="store_true",
        help="Print sha256 of output for snapshot verification",
    )
    args = ap.parse_args(argv)

    try:
        docs = load_all(args.input_dir)
        table = compile_table(docs)
    except (SchemaError, CycleError) as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = _stable_yaml_dump(table)
    args.output.write_text(text)

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    n_rows = len(table["compiled"])
    if args.print_hash:
        print(f"output_sha256={digest}")
        print(f"output_path={args.output}")
        print(f"rows={n_rows}")
    else:
        print(f"wrote {args.output} ({n_rows} rows, sha256={digest[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
