#!/usr/bin/env python3
"""Generate onboarding proof completion report from example registry."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config" / "onboarding" / "example_registry.json"
OUT_DIR = ROOT / "artifacts" / "onboarding"
OUT_MD = OUT_DIR / "proof_completion_latest.md"


def render() -> str:
    rows = json.loads(REGISTRY.read_text(encoding="utf-8"))
    status_counts = Counter(row["status"] for row in rows)

    sets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        set_id = row.get("comparison_set_id")
        if set_id:
            sets[set_id].append(row)

    lines: list[str] = []
    lines.append("# Onboarding Proof Completion Report")
    lines.append("")
    lines.append(f"- Total rows: **{len(rows)}**")
    lines.append(
        "- Status counts: "
        f"ready={status_counts.get('ready', 0)}, "
        f"planned={status_counts.get('planned', 0)}, "
        f"missing={status_counts.get('missing', 0)}"
    )
    lines.append("")
    lines.append("## Comparison sets")
    lines.append("")
    lines.append("| comparison_set_id | ready | planned | missing | total |")
    lines.append("|---|---:|---:|---:|---:|")
    for set_id in sorted(sets):
        counts = Counter(row["status"] for row in sets[set_id])
        total = len(sets[set_id])
        lines.append(
            f"| `{set_id}` | {counts.get('ready', 0)} | "
            f"{counts.get('planned', 0)} | {counts.get('missing', 0)} | {total} |"
        )

    lines.append("")
    lines.append("## Persona-lane-market paths with no ready proof")
    lines.append("")
    lines.append("| persona | lane | market | planned | missing |")
    lines.append("|---|---|---|---:|---:|")

    grouped: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    for row in rows:
        key = (row["persona"], row["lane"], row["market"])
        grouped[key][row["status"]] += 1

    for (persona, lane, market), counts in sorted(grouped.items()):
        if counts.get("ready", 0) == 0:
            lines.append(
                f"| `{persona}` | `{lane}` | `{market}` | "
                f"{counts.get('planned', 0)} | {counts.get('missing', 0)} |"
            )

    lines.append("")
    lines.append(
        "This report is descriptive only; it does not fail CI. "
        "Use it to target real-asset generation for final proof completion."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = render()
    OUT_MD.write_text(report, encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
