#!/usr/bin/env python3
"""
Write a machine-readable Pearl Prime release evidence bundle.

This script makes the main pipeline's release contract explicit in repo truth by
recording the authoritative entrypoints, required checks, and the evidence files
produced by release-gates and related workflows.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

AUTHORITY_DOCS = [
    "docs/RIGOROUS_SYSTEM_TEST.md",
    "docs/PRODUCTION_READINESS_GO_NO_GO.md",
    "docs/RELEASE_PRODUCTION_READINESS_CHECKLIST.md",
    "docs/PEARL_PRIME_RELEASE_CONTRACT.md",
]

AUTHORITY_CODE = {
    "pipeline_entrypoint": "scripts/run_pipeline.py",
    "release_workflow": ".github/workflows/release-gates.yml",
    "simulation_workflow": ".github/workflows/simulation-10k.yml",
    "rigorous_runner": "scripts/ci/run_rigorous_system_test.py",
    "canary_runner": "scripts/ci/run_canary_100_books.py",
    "rollback_smoke": "scripts/release/rollback_smoke.sh",
}


def _load_required_checks() -> dict:
    path = REPO_ROOT / "config" / "governance" / "required_checks.yaml"
    if not path.exists() or yaml is None:
        return {"required_checks": [], "non_blocking_checks": []}
    data = yaml.safe_load(path.read_text()) or {}
    return {
        "required_checks": data.get("required_checks") or [],
        "non_blocking_checks": data.get("non_blocking_checks") or [],
    }


def _latest(glob_pattern: str) -> str | None:
    matches = sorted(REPO_ROOT.glob(glob_pattern), key=lambda p: p.stat().st_mtime)
    return str(matches[-1].relative_to(REPO_ROOT)) if matches else None


def _exists(rel_path: str | None) -> bool:
    return bool(rel_path) and (REPO_ROOT / rel_path).exists()


def build_bundle(profile: str) -> dict:
    checks = _load_required_checks()
    release_artifacts = {
        "rollback_smoke_evidence": "artifacts/release/rollback_smoke_evidence.json",
        "canary_summary": "artifacts/canary_plans/canary_summary.json",
        "canary_failures": "artifacts/canary_plans/canary_failures.json",
        "release_evidence_bundle": "artifacts/release/pearl_prime_release_evidence.json",
    }
    dynamic_artifacts = {
        "latest_systems_test_report": (
            "artifacts/release/latest_systems_test_report.json"
            if _exists("artifacts/release/latest_systems_test_report.json")
            else _latest("artifacts/systems_test/report_*.json")
        ),
        "latest_signal_snapshot": _latest("artifacts/observability/signal_snapshot*.json"),
        "simulation_analysis": "artifacts/reports/pearl_prime_sim_analysis.json",
        "simulation_baseline": "artifacts/reports/pearl_prime_sim_baseline.json",
        "observability_evidence_log": "artifacts/observability/evidence_log.jsonl",
    }
    required_release_paths: list[str | None] = [
        release_artifacts["rollback_smoke_evidence"],
        release_artifacts["canary_summary"],
    ]
    if profile == "release":
        required_release_paths.append(dynamic_artifacts["latest_systems_test_report"])

    evidence = []
    missing_required = []
    for label, rel_path in {**release_artifacts, **dynamic_artifacts}.items():
        evidence.append({"id": label, "path": rel_path, "exists": _exists(rel_path)})
    for rel_path in required_release_paths:
        if not _exists(rel_path):
            missing_required.append(rel_path)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "profile": profile,
        "pipeline": "pearl-prime",
        "authority_docs": AUTHORITY_DOCS,
        "authority_code": AUTHORITY_CODE,
        "required_checks": checks["required_checks"],
        "non_blocking_checks": checks["non_blocking_checks"],
        "authoritative_signal_note": (
            "GitHub required checks and release evidence artifacts are authoritative. "
            "External Cloudflare preview checks remain non-blocking unless this contract changes."
        ),
        "evidence": evidence,
        "missing_required_evidence": missing_required,
        "ready": len(missing_required) == 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Write Pearl Prime release evidence bundle")
    ap.add_argument("--profile", choices=["pr", "release"], default="release")
    ap.add_argument(
        "--out",
        default="artifacts/release/pearl_prime_release_evidence.json",
        help="Output JSON path",
    )
    ap.add_argument("--strict", action="store_true", help="Exit 1 if required evidence is missing")
    args = ap.parse_args()

    bundle = build_bundle(args.profile)
    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote Pearl Prime release evidence: {out_path}")
    if args.strict and not bundle["ready"]:
        print("Missing required evidence:", ", ".join(str(p) for p in bundle["missing_required_evidence"]))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
