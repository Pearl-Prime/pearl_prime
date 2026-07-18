#!/usr/bin/env python3
"""Validate plan-to-output manga traceability and emit a TSV."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

REQUIRED_IDS = (
    "series_id",
    "episode_id",
    "chapter_id",
    "panel_id",
    "beat_id",
    "doctrine_id",
    "layer_role",
    "support_zone_id",
)


def validate_trace_rows(
    planned_rows: Iterable[Mapping[str, Any]],
    output_rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    planned = [dict(row) for row in planned_rows]
    output = [dict(row) for row in output_rows]
    failures: list[dict[str, Any]] = []

    for scope, rows in (("planned", planned), ("output", output)):
        for index, row in enumerate(rows):
            for field in REQUIRED_IDS:
                if row.get(field) in (None, ""):
                    failures.append({
                        "rule": "TRACE-ID-001",
                        "scope": scope,
                        "index": index,
                        "message": f"missing {field}",
                    })

    planned_by_panel = {str(row.get("panel_id")): row for row in planned if row.get("panel_id")}
    output_by_panel = {str(row.get("panel_id")): row for row in output if row.get("panel_id")}

    if len(planned) != len(output):
        failures.append({
            "rule": "TRACE-COUNT-001",
            "message": f"planned panel count {len(planned)} != output panel count {len(output)}",
        })

    for panel_id, plan in planned_by_panel.items():
        actual = output_by_panel.get(panel_id)
        if actual is None:
            failures.append({
                "rule": "TRACE-PANEL-001",
                "panel_id": panel_id,
                "message": "planned panel missing from output",
            })
            continue
        checks = (
            ("beat_id", "TRACE-BEAT-001"),
            ("doctrine_id", "TRACE-DOCTRINE-001"),
            ("support_zone_id", "TRACE-SUPPORT-001"),
            ("lettering_locale", "TRACE-LOCALE-001"),
        )
        for field, rule in checks:
            if plan.get(field) != actual.get(field):
                failures.append({
                    "rule": rule,
                    "panel_id": panel_id,
                    "message": f"{field} planned={plan.get(field)!r} output={actual.get(field)!r}",
                })
        if plan.get("layer_role") != actual.get("layer_role"):
            recovery = actual.get("layer_role_recovery_note")
            if not recovery:
                failures.append({
                    "rule": "TRACE-LAYER-001",
                    "panel_id": panel_id,
                    "message": (
                        f"layer_role planned={plan.get('layer_role')!r} "
                        f"output={actual.get('layer_role')!r} without recovery note"
                    ),
                })

    orphaned = sorted(set(output_by_panel) - set(planned_by_panel))
    for panel_id in orphaned:
        failures.append({
            "rule": "TRACE-ORPHAN-001",
            "panel_id": panel_id,
            "message": "output panel has no planned panel",
        })

    return {
        "passed": not failures,
        "planned_panel_count": len(planned),
        "output_panel_count": len(output),
        "matched_panel_count": len(set(planned_by_panel) & set(output_by_panel)),
        "failures": failures,
        "manga-contract-enforcement": "green" if not failures else "partial",
        "overall-manga-green": "NOT_PROVEN",
        "rows": [
            {
                **plan,
                "output_present": panel_id in output_by_panel,
                "output": output_by_panel.get(panel_id),
            }
            for panel_id, plan in planned_by_panel.items()
        ],
    }


def write_trace_tsv(path: Path, report: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "series_id", "episode_id", "chapter_id", "panel_id", "beat_id",
        "doctrine_id", "layer_role", "support_zone_id", "lettering_locale",
        "output_present", "output_layer_role", "output_support_zone_id",
        "output_lettering_locale", "recovery_note",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in report.get("rows") or []:
            output = row.get("output") or {}
            writer.writerow({
                "series_id": row.get("series_id"),
                "episode_id": row.get("episode_id"),
                "chapter_id": row.get("chapter_id"),
                "panel_id": row.get("panel_id"),
                "beat_id": row.get("beat_id"),
                "doctrine_id": row.get("doctrine_id"),
                "layer_role": row.get("layer_role"),
                "support_zone_id": row.get("support_zone_id"),
                "lettering_locale": row.get("lettering_locale"),
                "output_present": row.get("output_present"),
                "output_layer_role": output.get("layer_role"),
                "output_support_zone_id": output.get("support_zone_id"),
                "output_lettering_locale": output.get("lettering_locale"),
                "recovery_note": output.get("layer_role_recovery_note"),
            })
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--planned", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tsv", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    planned = json.loads(args.planned.read_text(encoding="utf-8"))
    output = json.loads(args.output.read_text(encoding="utf-8"))
    planned_rows = planned.get("panels") or planned.get("rows") or []
    output_rows = output.get("panels") or output.get("rows") or []
    report = validate_trace_rows(planned_rows, output_rows)
    write_trace_tsv(args.tsv, report)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
