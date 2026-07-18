#!/usr/bin/env python3
"""Generate an honest V2.1 enhancement writer-supply backlog."""
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUESTED = (
    "AUTHOR_DISCLOSURE", "PARABLE", "ANALOGY", "METAPHOR",
    "MOTIF", "CALLBACK_RETURN", "BRIDGE", "TRANSITION",
)

def build(repo: Path) -> dict:
    from phoenix_v4.planning import accent_planner
    executable = sorted(str(x) for x in accent_planner.ALL_ACCENT_CLASSES)
    rows = []
    for cls in REQUESTED:
        rows.append({
            "class": cls,
            "runtime_executable_as_accent": cls in executable,
            "writer_action": (
                "author_supply_with_v21_metadata"
                if cls in executable
                else "BLOCKED_DO_NOT_AUTHOR_TAXONOMY_ONLY_SUPPLY"
            ),
            "required_metadata": {
                "truth_metadata": cls in {"AUTHOR_DISCLOSURE"},
                "profile_gate": cls in {"AUTHOR_DISCLOSURE", "PARABLE"},
                "semantic_fingerprint": cls in {"ANALOGY", "METAPHOR"},
                "plant_id_return_function_semantic_development": cls == "CALLBACK_RETURN",
            },
        })
    return {
        "schema_version": "1.0.0",
        "runtime_executable_classes": executable,
        "requested_classes": rows,
        "safe_to_author_now": [r["class"] for r in rows if r["runtime_executable_as_accent"]],
        "blocked_classes": [r["class"] for r in rows if not r["runtime_executable_as_accent"]],
        "truth": "No supply is counted until the live runtime can select and prove it.",
    }

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/qa/enhancement_supply_backlog_20260714"),
    )
    args = p.parse_args()
    repo = args.repo_root.resolve()
    out = args.out if args.out.is_absolute() else repo / args.out
    out.mkdir(parents=True, exist_ok=True)
    payload = build(repo)
    (out / "enhancement_supply_backlog.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    lines = ["# Enhancement Supply Backlog", ""]
    for row in payload["requested_classes"]:
        lines.append(
            f"- `{row['class']}` — {row['writer_action']}"
        )
    (out / "writer_backlog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
