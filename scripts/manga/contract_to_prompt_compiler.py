#!/usr/bin/env python3
"""Compile a layer's contract inputs into a (positive, negative) prompt bundle.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §5.9 — Phase B.1 step 1.5.

Pipeline position: takes the COMPILED safe-zone row + character_design +
continuity_state + light_rig + style_state + scene_inventory + genre fields,
substitutes them into a layer-specific template, returns a stable PromptBundle.

DETERMINISTIC. No model inference. No fuzzy fallbacks. The substitution layer
is `string.Formatter.vformat` with a custom `get_field` that treats dotted
slot names as flat dict keys (not Python attribute access).

Validation rules (§5.9 v0.5.1 additive-safe semantics):
  - Template references slot NOT in registry           -> CompilerError
  - Template references REQUIRED slot, contract missing -> CompilerError
  - Template references OPTIONAL slot, contract missing -> use default_when_missing
  - Contract provides slot not referenced by template   -> WARN (not blocking)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from string import Formatter
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE_DIR = REPO / "config" / "manga" / "prompt_templates"
DEFAULT_REGISTRY = DEFAULT_TEMPLATE_DIR / "slot_registry.yaml"

# Matches {slot.name} but ignores {{escaped}} braces.
_SLOT_RE = re.compile(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_.]*)\}(?!\})")

# v0.6.3: known clauses in scene_context_clause that contradict safe_zone margin
# requirements. Qwen-Image resolves the contradiction by obeying composition
# intent (the scene_context) over geometric margin (the safe_zone), so we WARN
# at compile time. Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §12.3.
_CONTRADICTING_PHRASES_WITH_MARGIN = (
    "fill the frame", "fills the frame", "edge to edge", "edge-to-edge",
    "occupies full canvas", "occupies entire canvas", "fills entire canvas",
    "fills canvas", "head occupying upper 70", "head occupying upper 80",
    "head occupying upper 90", "extreme close-up portrait, face and shoulders fill",
    "dominates frame", "dominate frame", "dominates canvas",
)


class CompilerError(Exception):
    """Fatal: slot missing, unknown reference, malformed template, schema fail."""


@dataclass
class PromptBundle:
    positive: str
    negative: str
    parameters: dict
    cache_key: str
    provenance: dict
    warnings: list = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# loaders
# ─────────────────────────────────────────────────────────────────────────────


def load_registry(registry_path: Path = DEFAULT_REGISTRY) -> dict:
    if not registry_path.is_file():
        raise CompilerError(f"slot_registry not found: {registry_path}")
    data = yaml.safe_load(registry_path.read_text())
    if not isinstance(data, dict) or "slots_by_layer" not in data:
        raise CompilerError(
            f"{registry_path}: top-level must be a mapping with 'slots_by_layer' key"
        )
    return data


def load_template(layer_type: str, form: str, template_dir: Path) -> str:
    if form not in ("positive", "negative"):
        raise CompilerError(f"form must be 'positive' or 'negative', got {form!r}")
    p = template_dir / f"{layer_type}.{form}.template.txt"
    if not p.is_file():
        raise CompilerError(f"template not found: {p}")
    return p.read_text()


# ─────────────────────────────────────────────────────────────────────────────
# slot extraction + validation
# ─────────────────────────────────────────────────────────────────────────────


def extract_slot_refs(template: str) -> set[str]:
    """Return slot references used in the template (e.g., 'safe_zone.margin.top')."""
    return set(_SLOT_RE.findall(template))


def _layer_slot_spec(registry: dict, layer_type: str) -> tuple[set[str], dict]:
    """Return (required_slots, optional_slots_with_metadata) for a layer."""
    slots_by_layer = registry.get("slots_by_layer", {})
    if layer_type not in slots_by_layer:
        raise CompilerError(
            f"slot_registry has no entry for layer {layer_type!r} "
            f"(known: {sorted(slots_by_layer.keys())})"
        )
    layer = slots_by_layer[layer_type] or {}
    required = set(layer.get("required") or [])
    optional = layer.get("optional") or {}
    return required, optional


def _validate_template_slots_are_known(
    refs: set[str],
    layer_type: str,
    required: set[str],
    optional: dict,
) -> None:
    """Every template ref must be declared in registry."""
    known = required | set(optional.keys())
    unknown = refs - known
    if unknown:
        raise CompilerError(
            f"templates for {layer_type}: unknown slot references "
            f"{sorted(unknown)} (declare in slot_registry.yaml first)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# dotted-path resolution
# ─────────────────────────────────────────────────────────────────────────────


def _resolve_dotted(d: dict, key: str) -> Any:
    """Walk a dotted key path through nested dicts. Raise KeyError if missing."""
    if key in d:
        return d[key]
    if "." not in key:
        raise KeyError(key)
    node: Any = d
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise KeyError(key)
    return node


def _flatten_keys(d: dict, prefix: str = "") -> set[str]:
    """Yield every leaf and intermediate dotted key in a nested dict."""
    out: set[str] = set()
    for k, v in d.items():
        path = f"{prefix}{k}"
        if isinstance(v, dict):
            out |= _flatten_keys(v, prefix=f"{path}.")
        out.add(path)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# dotted-key formatter
# ─────────────────────────────────────────────────────────────────────────────


class _DottedKeyFormatter(Formatter):
    """Treat the WHOLE field name as a single dict key (no attribute access).

    Python's default Formatter splits 'a.b' into get('a').b — we override to
    keep 'a.b' as one literal key so dotted slot names work directly.
    """

    def get_field(self, field_name: str, args, kwargs):
        return kwargs[field_name], field_name


# ─────────────────────────────────────────────────────────────────────────────
# main compiler
# ─────────────────────────────────────────────────────────────────────────────


def compile_prompt(
    layer_type: str,
    contract_inputs: dict,
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
    registry: dict | None = None,
    parameters: dict | None = None,
) -> PromptBundle:
    """Compile contract_inputs into a PromptBundle for the given layer type.

    Args:
        layer_type: one of L0, L1, L2, L3, L4
        contract_inputs: nested dict with all slot values
        template_dir: where templates live
        registry: pre-loaded slot_registry dict (else loaded from template_dir)
        parameters: model/sampler parameters to bundle with the prompt

    Raises:
        CompilerError on any deterministic-contract violation.

    Returns:
        PromptBundle with positive, negative, parameters, cache_key, provenance.
    """
    if registry is None:
        registry = load_registry(template_dir / "slot_registry.yaml")
    parameters = parameters or {}

    required, optional = _layer_slot_spec(registry, layer_type)

    pos_template = load_template(layer_type, "positive", template_dir)
    neg_template = load_template(layer_type, "negative", template_dir)
    pos_refs = extract_slot_refs(pos_template)
    neg_refs = extract_slot_refs(neg_template)
    all_refs = pos_refs | neg_refs

    _validate_template_slots_are_known(all_refs, layer_type, required, optional)

    # Build flat substitution dict.
    sub: dict[str, Any] = {}
    warnings: list[str] = []

    for slot in sorted(all_refs):
        if slot in required:
            try:
                sub[slot] = _resolve_dotted(contract_inputs, slot)
            except KeyError:
                raise CompilerError(
                    f"missing required slot {slot!r} for layer {layer_type} "
                    f"(template references it; contract did not provide value)"
                )
        elif slot in optional:
            try:
                sub[slot] = _resolve_dotted(contract_inputs, slot)
            except KeyError:
                sub[slot] = optional[slot].get("default_when_missing", "")
        else:
            # Should be impossible after _validate_template_slots_are_known.
            raise CompilerError(
                f"slot {slot!r} not classified as required or optional"
            )

    # v0.6.3: detect scene_context_clause / margin contradiction (class-B WARN).
    # Qwen resolves clause-conflicts by obeying composition intent over geometric
    # margin (B-test #3 2026-05-20 empirical evidence). Catch the known fail
    # phrases at compile time so the orchestrator can flag and re-author.
    sc_value = sub.get("archetype.scene_context_clause", "")
    if isinstance(sc_value, str) and sc_value:
        sc_lower = sc_value.lower()
        margin_required = any(
            float(sub.get(f"safe_zone.margin.{side}", 0) or 0) > 0
            for side in ("top", "bottom", "left", "right")
        )
        hits = [p for p in _CONTRADICTING_PHRASES_WITH_MARGIN if p in sc_lower]
        if hits and margin_required:
            warnings.append(
                f"scene_context_clause contains margin-contradicting phrase(s) {hits!r} "
                f"while safe_zone declares non-zero margins. Qwen will likely obey "
                f"composition intent over margin (B-test #3 2026-05-20 lesson). "
                f"Rewrite scene_context to use 'breathing room', 'subject does not touch frame edges', "
                f"'centered portrait' instead."
            )

    # Additive-safe warning for provided-but-unreferenced slots.
    provided = _flatten_keys(contract_inputs)
    parent_paths_of_refs = {
        p.rsplit(".", 1)[0] for p in all_refs if "." in p
    }
    referenced_or_parents = all_refs | parent_paths_of_refs
    extra = provided - referenced_or_parents
    if extra:
        sample = sorted(extra)[:8]
        suffix = "..." if len(extra) > len(sample) else ""
        warnings.append(
            f"provided slots not referenced by any {layer_type} template "
            f"({len(extra)} total): {sample}{suffix}"
        )

    # Substitute via dotted-key formatter.
    formatter = _DottedKeyFormatter()
    try:
        positive = formatter.vformat(pos_template, (), sub)
        negative = formatter.vformat(neg_template, (), sub)
    except KeyError as e:
        raise CompilerError(
            f"vformat failed on slot {e!s} (this should have been caught upstream)"
        )

    positive = positive.strip()
    negative = negative.strip()

    cache_payload = json.dumps(
        {
            "layer_type": layer_type,
            "positive": positive,
            "negative": negative,
            "parameters": parameters,
        },
        sort_keys=True,
    )
    cache_key = hashlib.sha256(cache_payload.encode("utf-8")).hexdigest()

    return PromptBundle(
        positive=positive,
        negative=negative,
        parameters=parameters,
        cache_key=cache_key,
        provenance={
            "layer_type": layer_type,
            "template_dir": str(template_dir),
            "required_slots_used": sorted(required & all_refs),
            "optional_slots_used": sorted(set(optional.keys()) & all_refs),
            "template_versions": {
                "positive": hashlib.sha256(pos_template.encode()).hexdigest()[:16],
                "negative": hashlib.sha256(neg_template.encode()).hexdigest()[:16],
            },
        },
        warnings=warnings,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compile a layer's contract inputs into a prompt bundle."
    )
    ap.add_argument("--layer-type", required=True, choices=["L0", "L1", "L2", "L3", "L4"])
    ap.add_argument(
        "--contract-inputs",
        type=Path,
        required=True,
        help="Path to YAML or JSON file with the nested contract_inputs dict",
    )
    ap.add_argument("--template-dir", type=Path, default=DEFAULT_TEMPLATE_DIR)
    ap.add_argument("--parameters", type=Path, help="Optional JSON file with model parameters")
    ap.add_argument("--print-hash", action="store_true")
    args = ap.parse_args(argv)

    text = args.contract_inputs.read_text()
    try:
        inputs = (
            json.loads(text)
            if args.contract_inputs.suffix.lower() == ".json"
            else yaml.safe_load(text)
        )
    except Exception as e:
        print(f"ERROR: failed to parse contract inputs: {e}", file=sys.stderr)
        return 2

    params = {}
    if args.parameters and args.parameters.is_file():
        params = json.loads(args.parameters.read_text())

    try:
        bundle = compile_prompt(
            args.layer_type,
            inputs,
            template_dir=args.template_dir,
            parameters=params,
        )
    except CompilerError as e:
        print(f"ERROR: CompilerError: {e}", file=sys.stderr)
        return 2

    print("=== POSITIVE ===")
    print(bundle.positive)
    print()
    print("=== NEGATIVE ===")
    print(bundle.negative)
    print()
    print(f"cache_key={bundle.cache_key}")
    if args.print_hash:
        print(f"required_slots_used={bundle.provenance['required_slots_used']}")
        print(f"optional_slots_used={bundle.provenance['optional_slots_used']}")
    for w in bundle.warnings:
        print(f"warning: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
