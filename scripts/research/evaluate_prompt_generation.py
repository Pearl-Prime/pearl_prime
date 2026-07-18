#!/usr/bin/env python3
"""Generate before/after Pearl_Research prompt-builder examples.

This evaluation does not execute downstream research. It renders the legacy
runner prompt beside the new research brief and provider-specific compiled
prompts, then scores both prompts against the prompt-quality requirements.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from research_prompt_builder import (  # noqa: E402
    ResearchPromptInputs,
    build_prompt_package,
    score_prompt_quality,
    slugify,
    write_prompt_package,
)
from run_research import load_layer_bundle  # noqa: E402


DEFAULT_CASES = SCRIPT_DIR / "examples" / "prompt_generation_cases.yaml"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "research" / "prompt_generation_examples"


def _require_yaml() -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required for prompt generation evaluation.")
    return yaml


def _load_cases(path: Path) -> list[dict[str, Any]]:
    loader = _require_yaml()
    with open(path, "r", encoding="utf-8") as f:
        data = loader.safe_load(f) or {}
    return data.get("cases", [])


def _legacy_prompt_for_case(case: dict[str, Any]) -> str:
    system, task, yaml_instruction = load_layer_bundle(case["prompt_id"], case.get("transcript", ""))
    return (
        f"# Legacy Pearl_Research Prompt Preview: {case['id']}\n\n"
        "This is the old direct research prompt shape assembled by "
        "`scripts/research/run_research.py` before the new brief/compiler layer.\n\n"
        "## System\n\n"
        f"```text\n{system}\n```\n\n"
        "## User Task\n\n"
        f"```text\n{task}\n```\n\n"
        "## YAML Pass Instruction\n\n"
        f"```text\n{yaml_instruction}\n```\n"
    )


def _case_inputs(case: dict[str, Any]) -> ResearchPromptInputs:
    return ResearchPromptInputs(
        transcript=case.get("transcript", ""),
        issue_description=case.get("issue_description", ""),
        prompt_id=case.get("prompt_id", ""),
        title=case.get("title", ""),
        markets=case.get("markets", []),
        locales=case.get("locales", []),
        platforms=case.get("platforms", []),
        source_preferences=case.get("source_preferences", []),
        exclusions=case.get("exclusions", []),
        repo_context="Evaluation case for Pearl_Research prompt-generation layer.",
    )


def _score_table(before: dict[str, Any], after: dict[str, Any]) -> str:
    rows = [
        "| Criterion | Legacy | New |",
        "|---|---:|---:|",
    ]
    for criterion in before["checks"]:
        rows.append(
            "| "
            + criterion
            + " | "
            + ("yes" if before["checks"][criterion] else "no")
            + " | "
            + ("yes" if after["checks"][criterion] else "no")
            + " |"
        )
    rows.append(f"| **Total** | **{before['score']}/{before['max_score']}** | **{after['score']}/{after['max_score']}** |")
    return "\n".join(rows)


def evaluate_cases(cases_path: Path, out_dir: Path) -> Path:
    cases = _load_cases(cases_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_lines = [
        "# Pearl_Research Prompt Generation Evaluation",
        "",
        "This artifact compares the old direct runner prompt against the new",
        "brief-plus-compiler layer. It does not perform downstream research.",
        "",
        "| Case | Route | Legacy score | New score | Package |",
        "|---|---|---:|---:|---|",
    ]

    for case in cases:
        case_slug = slugify(case["id"])
        case_dir = out_dir / case_slug
        case_dir.mkdir(parents=True, exist_ok=True)

        legacy_prompt = _legacy_prompt_for_case(case)
        legacy_path = case_dir / "before_legacy_prompt.md"
        legacy_path.write_text(legacy_prompt, encoding="utf-8")

        package = build_prompt_package(_case_inputs(case))
        package_paths = write_prompt_package(package, case_dir, case_slug)
        recommended_key = package["recommended_prompt_key"]
        after_prompt = package["prompts"][recommended_key]
        before_score = score_prompt_quality(legacy_prompt)
        after_score = score_prompt_quality(after_prompt)

        why_better = [
            "# Before / After Evaluation",
            "",
            f"Case: `{case['id']}`",
            f"Recommended route: `{package['routing']['provider_display_name']}`",
            f"Recommended prompt key: `{recommended_key}`",
            "",
            "## Quality Score",
            "",
            _score_table(before_score, after_score),
            "",
            "## Why The New Prompt Is Stronger",
            "",
            "- It adds a structured research brief before execution, preserving the operator's messy context without asking the downstream engine to infer the real decision from noise.",
            "- It routes explicitly using `config/research/deep_research_prompt_routing.yaml`, so China, Japan, and global cases are inspectable and editable.",
            "- It asks for hypotheses, disconfirming evidence, source-quality rules, contradictions, open risks, and Phoenix Omega implementation implications.",
            "- It emits provider-specific variants instead of one generic prompt.",
            "",
            "## Files",
            "",
            f"- Legacy prompt: `{legacy_path.name}`",
        ]
        for label, path in package_paths.items():
            why_better.append(f"- {label}: `{path.name}`")
        eval_path = case_dir / "evaluation.md"
        eval_path.write_text("\n".join(why_better) + "\n", encoding="utf-8")

        summary_lines.append(
            f"| `{case['id']}` | {package['routing']['provider_display_name']} | "
            f"{before_score['score']}/{before_score['max_score']} | "
            f"{after_score['score']}/{after_score['max_score']} | "
            f"`{case_slug}/evaluation.md` |"
        )

    summary_path = out_dir / "SUMMARY.md"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    return summary_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Pearl_Research prompt generation examples.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="YAML file of evaluation cases.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory for generated examples.")
    args = parser.parse_args()

    summary = evaluate_cases(Path(args.cases), Path(args.out_dir))
    print(summary)


if __name__ == "__main__":
    main()
