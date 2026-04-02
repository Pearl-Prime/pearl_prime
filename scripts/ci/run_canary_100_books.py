#!/usr/bin/env python3
"""Real pipeline canary for sampled (topic, persona, arc) combos.

The canary can run in simple sampling mode or in analyzer-driven mode that
filters arcs by the best/worst format IDs from a simulation analysis report.
It always writes a machine-readable summary for release evidence.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ARCS_DIR = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"


def _parse_arc_filename(name: str) -> tuple[str, str, str, str] | None:
    """Parse persona__topic__engine__format.yaml -> (persona, topic, engine, format_id)."""
    stem = name.replace(".yaml", "")
    parts = stem.split("__")
    if len(parts) >= 4:
        return parts[0], parts[1], parts[2], parts[3]
    return None


def _load_analysis(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _selected_formats_from_analysis(
    analysis: dict,
    combo_mode: str,
    combo_limit: int,
) -> list[str]:
    if combo_mode == "sample":
        return []

    combos: list[dict] = []
    if combo_mode in {"best", "best-worst"}:
        combos.extend((analysis.get("best_combos") or [])[:combo_limit])
    if combo_mode in {"worst", "best-worst"}:
        combos.extend((analysis.get("worst_combos") or [])[:combo_limit])

    selected: list[str] = []
    for combo in combos:
        format_id = combo.get("format_id")
        if format_id and format_id not in selected:
            selected.append(format_id)
    return selected


def _sample_arcs(
    n: int,
    seed: int = 42,
    allowed_formats: list[str] | None = None,
) -> list[tuple[Path, str, str, str]]:
    """Sample n arcs with diverse persona/topic coverage."""
    if not ARCS_DIR.exists():
        return []
    arc_files = sorted(ARCS_DIR.glob("*.yaml"))
    parsed: list[tuple[Path, str, str, str]] = []
    for ap in arc_files:
        p = _parse_arc_filename(ap.name)
        if p:
            if allowed_formats and p[3] not in allowed_formats:
                continue
            parsed.append((ap, p[0], p[1], p[3]))
    if not parsed:
        return []
    # Deterministic sample
    import random
    rng = random.Random(seed)
    k = min(n, len(parsed))
    return rng.sample(parsed, k)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run pipeline canary on sampled arcs")
    ap.add_argument("--n", type=int, default=20, help="Number of books (default 20 for CI speed)")
    ap.add_argument("--out-dir", default="", help="Output dir for plans (default: artifacts/canary_plans)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    ap.add_argument(
        "--analysis",
        default="",
        help="Optional simulation analysis JSON used for analyzer-driven selection",
    )
    ap.add_argument(
        "--combo-mode",
        choices=("sample", "best", "worst", "best-worst"),
        default="sample",
        help="How to use simulation analysis when --analysis is provided",
    )
    ap.add_argument(
        "--combo-limit",
        type=int,
        default=3,
        help="How many best/worst combos to use from analysis",
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else REPO_ROOT / "artifacts" / "canary_plans"
    out_dir.mkdir(parents=True, exist_ok=True)

    analysis = {}
    selected_formats: list[str] = []
    if args.analysis:
        analysis_path = Path(args.analysis)
        try:
            analysis = _load_analysis(analysis_path)
        except FileNotFoundError:
            if args.combo_mode != "sample":
                print(f"Analysis not found: {analysis_path}", file=sys.stderr)
                return 1
        else:
            selected_formats = _selected_formats_from_analysis(analysis, args.combo_mode, args.combo_limit)
            if args.combo_mode != "sample" and not selected_formats:
                print(
                    f"No format IDs selected from analysis {analysis_path} "
                    f"for combo_mode={args.combo_mode}",
                    file=sys.stderr,
                )
                return 1

    samples = _sample_arcs(args.n, args.seed, selected_formats or None)
    if not samples:
        print("No arcs found", file=sys.stderr)
        return 1

    pipeline_script = REPO_ROOT / "scripts" / "run_pipeline.py"
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
    failures: list[dict] = []
    executed: list[dict] = []

    for i, (arc_path, persona, topic, format_id) in enumerate(samples):
        plan_path = out_dir / f"canary_{i:03d}_{arc_path.stem}.json"
        cmd = [
            sys.executable,
            str(pipeline_script),
            "--topic", topic,
            "--persona", persona,
            "--arc", str(arc_path),
            "--out", str(plan_path),
            "--no-generate-freebies",
            "--no-update-freebie-index",
        ]
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=120)
        row = {
            "arc": arc_path.name,
            "persona": persona,
            "topic": topic,
            "format_id": format_id,
            "plan_path": str(plan_path),
            "exit_code": r.returncode,
        }
        if r.returncode != 0:
            row["stderr"] = (r.stderr or "")[:500]
            failures.append(dict(row))
            print(f"FAIL: {arc_path.name} ({persona}/{topic})", file=sys.stderr)
        elif not plan_path.exists():
            row["error"] = "output not created"
            failures.append(dict(row))
            print(f"FAIL: {arc_path.name} output missing", file=sys.stderr)
        else:
            row["status"] = "pass"
        executed.append(row)

    summary_path = out_dir / "canary_summary.json"
    summary = {
        "sample_size": len(samples),
        "failed": len(failures),
        "passed": len(samples) - len(failures),
        "out_dir": str(out_dir),
        "analysis_path": str(Path(args.analysis)) if args.analysis else "",
        "combo_mode": args.combo_mode,
        "selected_formats": selected_formats,
        "samples": executed,
    }
    summary_path.write_text(json.dumps(summary, indent=2))

    if failures:
        report_path = out_dir / "canary_failures.json"
        report_path.write_text(json.dumps({"failures": failures, "total": len(samples), "failed": len(failures)}, indent=2))
        print(
            f"Canary: {len(failures)}/{len(samples)} failed. "
            f"Summary: {summary_path}. Report: {report_path}",
            file=sys.stderr,
        )
        return 1
    print(f"Canary: {len(samples)}/{len(samples)} passed. Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
