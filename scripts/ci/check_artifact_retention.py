#!/usr/bin/env python3
"""Dry-run artifact retention classifier. It never deletes or offloads files."""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = REPO_ROOT / "config" / "artifacts" / "retention_policy.yaml"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "qa" / "session_mining_specs_do_all_20260718" / "spec8_artifact_retention"


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def classify_path(rel_path: str, policy: dict[str, Any]) -> dict[str, Any]:
    for rule in policy.get("rules") or []:
        for pattern in rule.get("patterns") or []:
            base = pattern[:-3] if pattern.endswith("/**") else ""
            if fnmatch.fnmatch(rel_path, pattern) or (base and (rel_path == base or rel_path.startswith(base + "/"))):
                return rule
    return {
        "artifact_class": "UNCLASSIFIED",
        "owner": "unknown",
        "keep_duration": "review_required",
        "durable_archive_required": True,
        "r2_pointer_required": False,
        "local_prune_eligible": False,
        "operator_approval_required_for_deletion": True,
        "restore_procedure": "operator review required",
    }


def _path_bytes(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                continue
    return total


def build_retention_manifest(
    *,
    repo_root: Path = REPO_ROOT,
    policy_path: Path = DEFAULT_POLICY,
    roots: list[str] | None = None,
    max_families: int = 20,
) -> dict[str, Any]:
    policy = _load_yaml(policy_path)
    roots = roots or ["artifacts"]
    candidates: list[Path] = []
    for root in roots:
        base = repo_root / root
        if base.is_dir():
            candidates.extend(p for p in base.iterdir() if not p.name.startswith("."))
        elif base.exists():
            candidates.append(base)
    families = sorted(
        (
            {
                "path": _rel(path, repo_root),
                "bytes": _path_bytes(path),
                "rule": classify_path(_rel(path, repo_root), policy),
            }
            for path in candidates
        ),
        key=lambda row: row["bytes"],
        reverse=True,
    )[:max_families]
    rows: list[dict[str, Any]] = []
    dry_run_reclaimable = 0
    for family in families:
        rule = family["rule"]
        prune_eligible = bool(rule.get("local_prune_eligible"))
        if prune_eligible:
            dry_run_reclaimable += int(family["bytes"])
        rows.append(
            {
                "path": family["path"],
                "bytes": family["bytes"],
                "artifact_class": rule.get("artifact_class"),
                "owner": rule.get("owner"),
                "keep_duration": rule.get("keep_duration"),
                "durable_archive_required": bool(rule.get("durable_archive_required")),
                "r2_pointer_required": bool(rule.get("r2_pointer_required")),
                "local_prune_eligible": prune_eligible,
                "operator_approval_required_for_deletion": bool(
                    rule.get("operator_approval_required_for_deletion", True)
                ),
                "restore_procedure": rule.get("restore_procedure"),
                "action": "DRY_RUN_ONLY_NO_DELETE",
            }
        )
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "policy_path": _rel(policy_path, repo_root),
        "files_deleted": 0,
        "real_offloads": 0,
        "history_rewrites": 0,
        "rows": rows,
        "stats": {
            "families_classified": len(rows),
            "dry_run_reclaimable_bytes": dry_run_reclaimable,
        },
    }


def validate_retention_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("files_deleted") != 0:
        errors.append("files_deleted must be 0")
    if manifest.get("real_offloads") != 0:
        errors.append("real_offloads must be 0")
    for idx, row in enumerate(manifest.get("rows") or []):
        for field in (
            "path",
            "artifact_class",
            "owner",
            "keep_duration",
            "durable_archive_required",
            "r2_pointer_required",
            "local_prune_eligible",
            "operator_approval_required_for_deletion",
            "restore_procedure",
            "action",
        ):
            if field not in row:
                errors.append(f"rows[{idx}] missing {field}")
        if row.get("action") != "DRY_RUN_ONLY_NO_DELETE":
            errors.append(f"rows[{idx}] action must be dry-run only")
    return errors


def _markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Artifact Retention Dry Run",
        "",
        f"Generated: {manifest['generated_at']}",
        "Files deleted: 0",
        "Real offloads: 0",
        "",
        "| Path | Bytes | Class | Prune Eligible | Owner |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in manifest["rows"]:
        lines.append(
            f"| `{row['path']}` | {row['bytes']} | {row['artifact_class']} | "
            f"{str(row['local_prune_eligible']).lower()} | {row['owner']} |"
        )
    return "\n".join(lines) + "\n"


def write_manifest(manifest: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    errors = validate_retention_manifest(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "artifact_retention_dry_run.json"
    md_path = output_dir / "artifact_retention_dry_run.md"
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(manifest), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run artifact retention classifier")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--root", action="append", dest="roots")
    parser.add_argument("--max-families", type=int, default=20)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    manifest = build_retention_manifest(
        repo_root=args.repo_root,
        policy_path=args.policy,
        roots=args.roots,
        max_families=args.max_families,
    )
    paths = write_manifest(manifest, args.output_dir)
    print(f"Retention dry-run written: {paths['json']}")
    print(
        "Families: {families_classified} Dry-run reclaimable bytes: {dry_run_reclaimable_bytes}".format(
            **manifest["stats"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
