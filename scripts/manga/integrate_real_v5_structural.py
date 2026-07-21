#!/usr/bin/env python3
"""Integrate real V5 selected-component structural assembly at workspace scale.

This is the production-entrypoint adapter for the repo-native
``assemble_real_v5_structural.py`` bridge. It scans a workspace for V5 panel roots,
assembles each panel through the existing structural gates, and writes an index
that can be consumed by page/webtoon composition.

``layer_00.png`` is never passed as an assembly source.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

from manga_100pct_common import Manga100PctError, repo_rel, write_json  # noqa: E402

REQUIRED_SOURCE_FILES = ("layer_00.png", "layer_01.png", "_telemetry.json")
FOREGROUND_CANDIDATES = ("layer_02.png", "layer_03.png")
REQUIRED_OUTPUTS = (
    "structural_plan.json",
    "assembly_manifest.yaml",
    "gate_report.json",
    "_provenance.json",
    "REAL_V5_STRUCTURAL_CLOSEOUT.json",
)
REQUIRED_GATES = {
    "L0_STRUCTURAL_PURITY",
    "L2_STRUCTURAL_PURITY",
    "L2_QUALITY",
    "L0_SUPPORT_ZONE",
}


def discover_v5_panel_roots(workspace: Path) -> list[Path]:
    """Return deterministic panel roots that satisfy the minimum V5 input shape."""
    roots: list[Path] = []
    for telemetry in sorted(workspace.rglob("_telemetry.json")):
        parent = telemetry.parent
        if not all((parent / name).is_file() for name in REQUIRED_SOURCE_FILES):
            continue
        if not any((parent / name).is_file() for name in FOREGROUND_CANDIDATES):
            continue
        roots.append(parent)
    return roots


def _load_gate_names(gate_path: Path) -> tuple[bool, set[str]]:
    payload = json.loads(gate_path.read_text(encoding="utf-8"))
    panels = payload.get("panels") or []
    if not panels:
        return False, set()
    names = {
        str(row.get("gate"))
        for row in panels[0].get("gates") or []
        if isinstance(row, dict)
    }
    return bool(panels[0].get("passed")), names


def _default_assembler(**kwargs: Any) -> Any:
    from assemble_real_v5_structural import assemble_real_v5_structural
    return assemble_real_v5_structural(**kwargs)


def integrate_workspace(
    *,
    workspace: Path,
    out_dir: Path,
    fail_fast: bool = True,
    tests: str | None = None,
    assembler: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Assemble every discovered panel and emit episode-scale status artifacts."""
    workspace = workspace.resolve()
    out_dir = out_dir.resolve()
    assembler = assembler or _default_assembler
    roots = discover_v5_panel_roots(workspace)
    if not roots:
        raise Manga100PctError(f"no V5 panel roots found under {workspace}")

    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for index, panel_root in enumerate(roots, start=1):
        telemetry = json.loads((panel_root / "_telemetry.json").read_text(encoding="utf-8"))
        panel_id = str(telemetry.get("panel_id") or panel_root.name)
        panel_out = out_dir / panel_id
        try:
            result = assembler(
                v5_panel_root=panel_root,
                out_dir=panel_out,
                panel_id=panel_id,
                tests=tests,
            )
            missing_outputs = [name for name in REQUIRED_OUTPUTS if not (panel_out / name).is_file()]
            if missing_outputs:
                raise Manga100PctError(
                    f"{panel_id}: structural adapter missing outputs {missing_outputs}"
                )
            manifest_text = (panel_out / "assembly_manifest.yaml").read_text(encoding="utf-8")
            provenance_text = (panel_out / "_provenance.json").read_text(encoding="utf-8")
            if "layer_00.png" in manifest_text or "layer_00.png" in provenance_text:
                raise Manga100PctError(f"{panel_id}: layer_00 appeared as assembly authority")
            gate_passed, gate_names = _load_gate_names(panel_out / "gate_report.json")
            missing_gates = sorted(REQUIRED_GATES - gate_names)
            if not gate_passed or missing_gates:
                raise Manga100PctError(
                    f"{panel_id}: gate failure; passed={gate_passed} missing={missing_gates}"
                )
            closeout = json.loads(
                (panel_out / "REAL_V5_STRUCTURAL_CLOSEOUT.json").read_text(encoding="utf-8")
            )
            rows.append({
                "panel_index": index,
                "panel_id": panel_id,
                "source_panel_root": repo_rel(panel_root, REPO),
                "status": "green",
                "selected_candidate": (
                    closeout.get("selected_candidate") or {}
                ).get("source_name", ""),
                "removed_px": (
                    closeout.get("selected_candidate") or {}
                ).get("removed_px", 0),
                "final_image": repo_rel(Path(result.final_path), REPO),
                "gate_names": sorted(gate_names),
                "error": "",
            })
        except Exception as exc:  # noqa: BLE001
            rows.append({
                "panel_index": index,
                "panel_id": panel_id,
                "source_panel_root": repo_rel(panel_root, REPO),
                "status": "blocked",
                "selected_candidate": "",
                "removed_px": "",
                "final_image": "",
                "gate_names": [],
                "error": str(exc),
            })
            if fail_fast:
                _write_outputs(out_dir, workspace, rows)
                raise
    return _write_outputs(out_dir, workspace, rows)


def _write_outputs(out_dir: Path, workspace: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    index = {
        "schema_version": "1.0.0",
        "workspace": repo_rel(workspace, REPO),
        "panel_count": len(rows),
        "green_count": sum(row["status"] == "green" for row in rows),
        "blocked_count": sum(row["status"] != "green" for row in rows),
        "raw-v5-layer-roles": "not-green",
        "selected-component-structural-assembly": (
            "green-for-proof" if rows and all(row["status"] == "green" for row in rows)
            else "partial"
        ),
        "overall-manga-green": "NOT_PROVEN",
        "panels": rows,
    }
    write_json(out_dir / "structural_assembly_index.json", index)
    with (out_dir / "panel_status.tsv").open("w", encoding="utf-8", newline="") as fh:
        fields = [
            "panel_index", "panel_id", "source_panel_root", "status",
            "selected_candidate", "removed_px", "final_image", "error",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--continue-on-panel-fail", action="store_true")
    parser.add_argument("--tests", default=None)
    args = parser.parse_args(argv)
    if args.fail_fast and args.continue_on_panel_fail:
        parser.error("--fail-fast and --continue-on-panel-fail are mutually exclusive")
    try:
        result = integrate_workspace(
            workspace=args.workspace,
            out_dir=args.out_dir,
            fail_fast=not args.continue_on_panel_fail,
            tests=args.tests,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["blocked_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
