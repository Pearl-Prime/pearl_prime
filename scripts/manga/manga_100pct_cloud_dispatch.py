#!/usr/bin/env python3
"""Render a deterministic, dependency-gated cloud dispatch packet for manga 100%."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def foundation_gate(config: dict[str, Any], receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    foundation = config.get("foundation") or {}
    if receipt.get("repository") != config.get("repository"):
        blockers.append("foundation receipt repository mismatch")
    if receipt.get("pr_number") != foundation.get("pr_number"):
        blockers.append("foundation receipt PR number mismatch")
    expected_head = foundation.get("expected_head_sha")
    if expected_head and receipt.get("head_sha") != expected_head:
        blockers.append("foundation receipt head SHA mismatch")
    if receipt.get("merged") is not True:
        blockers.append("foundation PR is not merged")
    if receipt.get("required_checks_pass") is not True:
        blockers.append("foundation required checks are not green")
    if not SHA_RE.fullmatch(str(receipt.get("merge_sha") or "")):
        blockers.append("foundation merge SHA is missing or invalid")
    if receipt.get("dispatch_allowed") is not True:
        blockers.append("foundation watchdog did not authorize dispatch")
    return blockers


def _bullets(values: list[str], indent: str = "- ") -> str:
    return "\n".join(f"{indent}{value}" for value in values)


def render_pm_prompt(config: dict[str, Any], receipt: dict[str, Any]) -> str:
    foundation = config["foundation"]
    agents = config.get("agents") or {}
    lines = [
        "You are Pearl_PM, acting as the manga 100% execution dispatcher for Phoenix Omega.",
        "",
        f"Repo: {config['repository']}",
        f"Foundation PR: #{foundation['pr_number']}",
        f"Foundation merge SHA: {receipt['merge_sha']}",
        f"Program branch: {config['branch']}",
        "",
        "MISSION:",
        str(config["mission"]),
        "",
        "ABSOLUTE RULES:",
        _bullets(list(config.get("absolute_rules") or [])),
        "",
        "DISPATCH ORDER:",
        "1. Verify the foundation merge SHA exists on main and matches the watchdog receipt.",
        "2. Dispatch all agents without dependencies in parallel.",
        "3. Dispatch Pearl_QA only after its dependencies are merged and verified.",
        "4. Run the repo final integrator and Pearl_Auditor after all lane PRs merge.",
        "",
        "AGENTS:",
    ]
    for name, row in agents.items():
        dependencies = ", ".join(row.get("depends_on") or []) or "foundation only"
        mapped = ", ".join(row.get("maps_to_lanes") or [])
        lines.append(f"- {name}: lanes {mapped}; depends on {dependencies}; goal: {row.get('goal','')}")
    lines.extend([
        "",
        "FINAL OUTPUT:",
        "- PR list and verified merge SHAs",
        "- proof roots",
        "- test commands and results",
        "- blocker ledger",
        "- GREEN or NOT_GREEN final verdict",
        "",
        "Do not trust agent summaries. Verify files, proof roots, and SHAs.",
    ])
    return "\n".join(lines) + "\n"


def render_agent_prompt(name: str, row: dict[str, Any], config: dict[str, Any], receipt: dict[str, Any]) -> str:
    mapped = ", ".join(row.get("maps_to_lanes") or [])
    dependencies = row.get("depends_on") or []
    lines = [
        f"You are {name} working on the Phoenix Omega manga 100% program.",
        "",
        f"Repo: {config['repository']}",
        f"Foundation merge SHA: {receipt['merge_sha']}",
        f"Mapped repo lanes: {mapped}",
        f"Goal: {row.get('goal','')}",
        "",
    ]
    if dependencies:
        lines.extend([
            "DEPENDENCY GATE:",
            f"Do not start until these agent lanes are green and merged: {', '.join(dependencies)}.",
            "",
        ])
    lines.extend([
        "TASKS:",
        _bullets(list(row.get("tasks") or [])),
        "",
        "REQUIRED OUTPUT TAGS:",
        _bullets([f"{tag}=<honest-status>" for tag in row.get("output_tags") or []]),
        "",
        "TRUTH RULES:",
        _bullets(list(config.get("absolute_rules") or [])),
        "",
        "Write the closeout under artifacts/analysis/ and real proof under artifacts/qa/ where applicable.",
        "Do not claim overall manga GREEN or 100%; only the final integrator and auditor can do that.",
    ])
    return "\n".join(lines) + "\n"


def render_auditor_prompt(config: dict[str, Any], receipt: dict[str, Any]) -> str:
    row = config.get("final_auditor") or {}
    return "\n".join([
        f"You are {row.get('name', 'Pearl_Auditor')}.",
        "",
        f"Repo: {config['repository']}",
        f"Foundation merge SHA: {receipt['merge_sha']}",
        f"Audit config: {row.get('config')}",
        "",
        "TASKS:",
        _bullets(list(row.get("tasks") or [])),
        "",
        "Run:",
        "PYTHONPATH=.:scripts/manga python3 scripts/manga/manga_100pct_truth_audit.py \\",
        f"  --config {row.get('config')} \\",
        "  --repo-root . \\",
        "  --json-out artifacts/qa/manga_100pct_truth_audit_2026-07-14.json \\",
        "  --markdown-out artifacts/analysis/MANGA_100PCT_TRUTH_AUDIT_2026-07-14.md",
        "",
        "GREEN is allowed only when the command exits 0 and every evidence requirement passes.",
    ]) + "\n"


def dispatch(config_path: Path, receipt_path: Path, output_dir: Path) -> dict[str, Any]:
    config = _load_yaml(config_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    blockers = foundation_gate(config, receipt)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "schema_version": "1.0.0",
        "program_id": config.get("program_id"),
        "repository": config.get("repository"),
        "foundation_pr": (config.get("foundation") or {}).get("pr_number"),
        "foundation_merge_sha": receipt.get("merge_sha"),
        "dispatch_allowed": not blockers,
        "blockers": blockers,
        "prompts": [],
    }
    if blockers:
        (output_dir / "BLOCKED.md").write_text(
            "# Manga 100% cloud dispatch blocked\n\n" + "\n".join(f"- {item}" for item in blockers) + "\n",
            encoding="utf-8",
        )
    else:
        blocked_path = output_dir / "BLOCKED.md"
        if blocked_path.exists():
            blocked_path.unlink()
        prompt_files: list[str] = []
        pm_path = output_dir / "00_Pearl_PM.md"
        pm_path.write_text(render_pm_prompt(config, receipt), encoding="utf-8")
        prompt_files.append(pm_path.name)
        for index, (name, row) in enumerate((config.get("agents") or {}).items(), start=1):
            path = output_dir / f"{index:02d}_{name}.md"
            path.write_text(render_agent_prompt(name, row, config, receipt), encoding="utf-8")
            prompt_files.append(path.name)
        auditor_path = output_dir / f"{len(prompt_files):02d}_Pearl_Auditor.md"
        auditor_path.write_text(render_auditor_prompt(config, receipt), encoding="utf-8")
        prompt_files.append(auditor_path.name)
        manifest["prompts"] = prompt_files
    (output_dir / "dispatch_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--foundation-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = dispatch(args.config, args.foundation_receipt, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["dispatch_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
