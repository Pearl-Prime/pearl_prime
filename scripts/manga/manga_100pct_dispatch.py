#!/usr/bin/env python3
"""Create the A-M manga program ledger and deterministic branch command packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def build_ledger(config: dict[str, Any], base_sha: str) -> str:
    lines = [
        "# Manga 100% Master Ledger — 2026-07-14",
        "",
        f"- base_sha: `{base_sha}`",
        "- raw-v5-layer-roles=not-green",
        "- selected-component-structural-assembly=green-for-proof",
        "- overall-manga-green=NOT_PROVEN",
        "",
        "| lane | name | branch | start SHA | final SHA | PR | status | tests | proof root | closeout | blockers | merged to main |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for lane, row in (config.get("lanes") or {}).items():
        lines.append(
            f"| {lane} | {row.get('name','')} | `{row.get('branch','')}` | `{base_sha}` |  |  | "
            f"not-started |  |  | `{row.get('closeout','')}` |  | no |"
        )
    lines.extend([
        "",
        "## Final Integrator",
        "",
        f"- Branch: `{(config.get('final_integrator') or {}).get('branch','')}`",
        f"- Closeout: `{(config.get('final_integrator') or {}).get('closeout','')}`",
        "- Status: not-started",
        "",
    ])
    return "\n".join(lines)


def branch_commands(config: dict[str, Any], base_sha: str) -> str:
    lines = [
        "# Branch commands",
        "",
        "Run each lane from a clean worktree. Do not stage unrelated dirty files.",
        "",
    ]
    for lane, row in (config.get("lanes") or {}).items():
        branch = row.get("branch")
        lines.extend([
            f"## Lane {lane}",
            "",
            "```bash",
            f"git fetch origin main",
            f"git worktree add ../phoenix_manga_lane_{lane.lower()} -b {branch} {base_sha}",
            f"cd ../phoenix_manga_lane_{lane.lower()}",
            "# apply the corresponding lane patch from the generated package",
            "git status --short",
            "```",
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--commands", required=True, type=Path)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.write_text(build_ledger(config, args.base_sha), encoding="utf-8")
    args.commands.parent.mkdir(parents=True, exist_ok=True)
    args.commands.write_text(branch_commands(config, args.base_sha), encoding="utf-8")
    print(json.dumps({
        "ledger": str(args.ledger),
        "commands": str(args.commands),
        "lane_count": len(config.get("lanes") or {}),
        "overall-manga-green": "NOT_PROVEN",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
