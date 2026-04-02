#!/usr/bin/env python3
"""Write a machine-readable manifest for a workflow run and its artifacts."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _artifact_entry(path: str) -> dict:
    p = Path(path)
    abs_path = p if p.is_absolute() else REPO_ROOT / p
    return {
        "path": path,
        "name": p.name,
        "exists": abs_path.exists(),
    }


def build_manifest(
    workflow_name: str,
    workflow_file: str,
    out_path: str,
    artifact_paths: list[str],
    *,
    repository: str = "",
    run_id: str = "",
    run_attempt: str = "",
    run_number: str = "",
    ref: str = "",
    sha: str = "",
    event_name: str = "",
    server_url: str = "",
) -> dict:
    repository = repository or _env("GITHUB_REPOSITORY")
    run_id = run_id or _env("GITHUB_RUN_ID")
    run_attempt = run_attempt or _env("GITHUB_RUN_ATTEMPT")
    run_number = run_number or _env("GITHUB_RUN_NUMBER")
    ref = ref or _env("GITHUB_REF")
    sha = sha or _env("GITHUB_SHA")
    event_name = event_name or _env("GITHUB_EVENT_NAME")
    server_url = server_url or _env("GITHUB_SERVER_URL", "https://github.com")

    run_url = ""
    if repository and run_id:
        run_url = f"{server_url.rstrip('/')}/{repository}/actions/runs/{run_id}"

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workflow_name": workflow_name,
        "workflow_file": workflow_file,
        "repository": repository,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "run_number": run_number,
        "ref": ref,
        "sha": sha,
        "event_name": event_name,
        "run_url": run_url,
        "out_path": out_path,
        "artifacts": [_artifact_entry(path) for path in artifact_paths],
        "artifact_paths": artifact_paths,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Write workflow run manifest")
    ap.add_argument("--workflow-name", required=True)
    ap.add_argument("--workflow-file", required=True)
    ap.add_argument(
        "--out",
        default="artifacts/release/workflow_run_manifest.json",
        help="Output JSON path",
    )
    ap.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="Artifact path to record; may be passed multiple times",
    )
    ap.add_argument("--repository", default="")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--run-attempt", default="")
    ap.add_argument("--run-number", default="")
    ap.add_argument("--ref", default="")
    ap.add_argument("--sha", default="")
    ap.add_argument("--event-name", default="")
    ap.add_argument("--server-url", default="")
    args = ap.parse_args()

    manifest = build_manifest(
        args.workflow_name,
        args.workflow_file,
        args.out,
        args.artifact,
        repository=args.repository,
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        run_number=args.run_number,
        ref=args.ref,
        sha=args.sha,
        event_name=args.event_name,
        server_url=args.server_url,
    )

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote workflow run manifest: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
