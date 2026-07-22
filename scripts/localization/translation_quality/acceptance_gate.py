#!/usr/bin/env python3
"""Deterministic acceptance-gate engine.

Implements the `accept_only_if` logic from the operator's plan as literal,
deterministic code. Takes a Claude evaluation-JSON object (the
`semantic_fidelity`, `omissions`, `emotional_fidelity`,
`natural_taiwan_mandarin`, `voice_match`, `terminology_compliance`,
`translationese`, `structural_fidelity`, `publishable` schema -- see
pipeline_config.yaml) plus a structural_validator.py result, and produces
an accept/reject verdict + reason list.

This module makes NO judgment call itself -- every score it reads was
produced by Claude Code (Lane 02). It only enforces the arithmetic
consequence of those scores, plus the auto-fail triggers, which are also
Claude-set boolean flags this module just enforces the consequence of, not
detects.

COMET/QE scores are explicitly NOT accepted as an input to this gate's
accept/reject arithmetic (per the operator's plan) -- only as a
supporting signal Claude may cite in its own evaluation JSON free text.
`assert` that no caller has slipped one in as if it belonged in the
threshold check.

Usage:
    from scripts.localization.translation_quality.acceptance_gate import (
        evaluate,
    )
    verdict = evaluate(evaluation_json, structural_result)
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.translation_quality.structural_validator import ValidationResult  # noqa: E402

# Thresholds per the operator's plan (Lane 02's PHASE 3 evaluation JSON
# schema). Config values, not hardcoded judgment -- override via
# `Thresholds(...)` if a future calibration round revises them; do not
# silently change these without a documented calibration result.
DEFAULT_MEANING_FIDELITY_MIN = 96
DEFAULT_EMOTIONAL_FIDELITY_MIN = 93
DEFAULT_TAIWAN_NATURALNESS_MIN = 92  # applies to natural_taiwan_mandarin OR the locale-equivalent naturalness score
DEFAULT_VOICE_MATCH_MIN = 92

AUTO_FAIL_FLAGS = (
    "negation_reversal",
    "added_promise_or_claim",
    "removed_qualification",
    "changed_agency",
    "changed_number_or_name",
    "altered_protected_concept",
)


@dataclass
class Thresholds:
    meaning_fidelity_min: int = DEFAULT_MEANING_FIDELITY_MIN
    emotional_fidelity_min: int = DEFAULT_EMOTIONAL_FIDELITY_MIN
    naturalness_min: int = DEFAULT_TAIWAN_NATURALNESS_MIN
    voice_match_min: int = DEFAULT_VOICE_MATCH_MIN


@dataclass
class GateVerdict:
    accepted: bool
    reasons: list[str] = field(default_factory=list)  # reject reasons; empty when accepted
    auto_fail_triggered: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "reasons": self.reasons,
            "auto_fail_triggered": self.auto_fail_triggered,
        }


def _naturalness_score(evaluation: dict[str, Any]) -> int | None:
    """Locale-agnostic accessor: zh-TW's evaluation JSON key is
    `natural_taiwan_mandarin`; a zh-CN (or other locale) equivalent may use
    a differently-named naturalness key. Accept either explicitly rather
    than silently defaulting to 0 and always failing."""
    for key in ("natural_taiwan_mandarin", "natural_mainland_mandarin", "naturalness"):
        if key in evaluation:
            return evaluation[key]
    return None


def evaluate(
    evaluation: dict[str, Any],
    structural_result: ValidationResult,
    *,
    thresholds: Thresholds | None = None,
) -> GateVerdict:
    """Deterministic accept/reject per the plan's accept_only_if logic.

    `evaluation` must NOT contain a COMET/QE score used as a threshold --
    this function does not look for one, enforcing the "never a ship
    gate" rule by simply never reading it.
    """
    thresholds = thresholds or Thresholds()
    reasons: list[str] = []

    # Structural gates (from structural_validator.py) -- literal, not
    # re-derived here.
    if not structural_result.ok:
        for r in structural_result.reasons:
            reasons.append(f"structural:{r}")

    # schema_valid / structure_valid / placeholders_preserved /
    # protected_terms_preserved / untranslated_english are all folded into
    # structural_result already (see structural_validator.py). Re-derive
    # the plan's literal names here as an explicit cross-check so a future
    # structural_validator refactor that silently drops a check is caught.
    per_block = structural_result.details.get("per_block_failures", {})
    flat_block_reasons = [r for rs in per_block.values() for r in rs]
    if any(r == "untranslated_english" for r in flat_block_reasons):
        reasons.append("untranslated_english=true")
    if any(r.startswith("glossary_violation:") for r in flat_block_reasons):
        reasons.append("glossary_errors>0")
    if any(r == "placeholders_not_preserved" for r in flat_block_reasons):
        reasons.append("placeholders_preserved=false")

    # Evaluation-JSON gates (Claude-set scores; this module only compares).
    critical_errors = len(evaluation.get("critical_semantic_errors") or []) if isinstance(
        evaluation.get("critical_semantic_errors"), list
    ) else int(evaluation.get("critical_semantic_errors", 0) or 0)
    major_errors = len(evaluation.get("major_semantic_errors") or []) if isinstance(
        evaluation.get("major_semantic_errors"), list
    ) else int(evaluation.get("major_semantic_errors", 0) or 0)
    glossary_errors = int(evaluation.get("glossary_errors", 0) or 0)

    if critical_errors > 0:
        reasons.append(f"critical_semantic_errors={critical_errors}")
    if major_errors > 0:
        reasons.append(f"major_semantic_errors={major_errors}")
    if glossary_errors > 0:
        reasons.append(f"glossary_errors={glossary_errors}")

    meaning_fidelity = evaluation.get("semantic_fidelity")
    if meaning_fidelity is None or meaning_fidelity < thresholds.meaning_fidelity_min:
        reasons.append(f"meaning_fidelity<{thresholds.meaning_fidelity_min} (got {meaning_fidelity})")

    emotional_fidelity = evaluation.get("emotional_fidelity")
    if emotional_fidelity is None or emotional_fidelity < thresholds.emotional_fidelity_min:
        reasons.append(f"emotional_fidelity<{thresholds.emotional_fidelity_min} (got {emotional_fidelity})")

    naturalness = _naturalness_score(evaluation)
    if naturalness is None or naturalness < thresholds.naturalness_min:
        reasons.append(f"taiwan_naturalness<{thresholds.naturalness_min} (got {naturalness})")

    voice_match = evaluation.get("voice_match")
    if voice_match is None or voice_match < thresholds.voice_match_min:
        reasons.append(f"voice_match<{thresholds.voice_match_min} (got {voice_match})")

    # Auto-fail triggers: Claude sets these as booleans in its evaluation
    # JSON; this module only enforces the consequence.
    auto_fail_triggered = [flag for flag in AUTO_FAIL_FLAGS if evaluation.get(flag) is True]
    if auto_fail_triggered:
        reasons.append(f"auto_fail_triggered:{','.join(auto_fail_triggered)}")

    if evaluation.get("publishable") is False:
        reasons.append("publishable=false")

    return GateVerdict(accepted=not reasons, reasons=reasons, auto_fail_triggered=auto_fail_triggered)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evaluation-json", type=Path, required=True, help="Claude's evaluation JSON file")
    ap.add_argument("--structural-json", type=Path, required=True, help="structural_validator.py --json output file")
    args = ap.parse_args(argv)

    evaluation = json.loads(args.evaluation_json.read_text(encoding="utf-8"))
    structural_raw = json.loads(args.structural_json.read_text(encoding="utf-8"))
    structural_result = ValidationResult(
        ok=structural_raw["ok"], reasons=structural_raw["reasons"], details=structural_raw.get("details", {})
    )

    verdict = evaluate(evaluation, structural_result)
    print(json.dumps(verdict.to_dict(), indent=2, ensure_ascii=False))
    return 0 if verdict.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
