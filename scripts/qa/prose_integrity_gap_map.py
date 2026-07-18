#!/usr/bin/env python3
"""Map refreshed prose-integrity candidates onto existing gate ownership."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "artifacts" / "qa" / "session_mining_specs_do_all_20260718"

GAP_MAP = [
    {
        "id": "PI-1",
        "name": "no-story-adjacency",
        "decision": "merged_gap_warn",
        "existing_authority": [
            "phoenix_v4/quality/register_gate.py",
            "story/literary repair acceptance artifacts",
            "scripts/inventory/surface_inventory.py story signal warnings",
        ],
        "patch_applied": "surface manifest warns on story event/stake/turn/cost/residue gaps",
        "hard_gate": False,
    },
    {
        "id": "PI-2",
        "name": "quote-bridge",
        "decision": "mapped_to_existing_plus_warn",
        "existing_authority": [
            "source/evidence truth gates",
            "config/atoms/surface_taxonomy.yaml source_provenance_required",
            "scripts/inventory/surface_inventory.py SOURCE_PROVENANCE_MISSING",
        ],
        "patch_applied": "warn-only source provenance measurement for QUOTE surfaces",
        "hard_gate": False,
    },
    {
        "id": "PI-3",
        "name": "composite-teaching-band",
        "decision": "mapped_to_atom_depth",
        "existing_authority": [
            "reader-layer standards",
            "deep atom taxonomy",
            "register F13 dwell/integration starvation",
        ],
        "patch_applied": "surface/depth manifest records reader entry/exit and depth contracts",
        "hard_gate": False,
    },
    {
        "id": "PI-4",
        "name": "tool-vs-exercise",
        "decision": "mapped_to_exercise_policy",
        "existing_authority": [
            "deep five-layer exercise spec",
            "config/atoms/surface_taxonomy.yaml exercise_policy",
            "scripts/inventory/surface_inventory.py EXERCISE_* warnings",
        ],
        "patch_applied": "exercise/tool/reflection policy is measured per surface",
        "hard_gate": False,
    },
    {
        "id": "PI-5",
        "name": "fallback-sweep",
        "decision": "mapped_to_selection_provenance",
        "existing_authority": [
            "phoenix_v4/planning/enrichment_select.py provenance/waterfall",
            "tuple viability story fallback fix",
            "atom coverage and surface manifest",
        ],
        "patch_applied": "report-only; no new monolithic validator",
        "hard_gate": False,
    },
]


def build_gap_map() -> dict:
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_spec": "docs/specs/session_mining_batch_20260718/PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC.md",
        "new_parallel_module_created": False,
        "hard_ship_gate_created": False,
        "rows": GAP_MAP,
        "stats": {
            "gaps_mapped": len(GAP_MAP),
            "patches_applied": sum(1 for row in GAP_MAP if row["patch_applied"]),
            "hard_gates": sum(1 for row in GAP_MAP if row["hard_gate"]),
        },
    }


def _markdown(report: dict) -> str:
    lines = [
        "# Prose Integrity Gap Map",
        "",
        f"Generated: {report['generated_at']}",
        "New parallel module created: no",
        "Hard ship gate created: no",
        "",
        "| ID | Candidate | Decision | Patch |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["rows"]:
        lines.append(f"| {row['id']} | {row['name']} | {row['decision']} | {row['patch_applied']} |")
    return "\n".join(lines) + "\n"


def write_gap_map(report: dict, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "prose_integrity_gap_map.json"
    md_path = output_dir / "prose_integrity_gap_map.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Write prose integrity gap map")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = build_gap_map()
    paths = write_gap_map(report, args.output_dir)
    print(f"Gap map written: {paths['json']}")
    print(f"Gaps mapped: {report['stats']['gaps_mapped']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
