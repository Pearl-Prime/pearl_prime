#!/usr/bin/env python3
"""
G-LAYER — catalog ship manifests must carry acceptance_layer.

Every shipped EPUB row (status ok / skip_r2 / skip_local) must include
acceptance_layer from the allowed enum. Default is path_works.

Shipping as system_working / bestseller_register without a Layer-3 /
Layer-4 artifact path is a hard fail.

Also enforces D3: top-level quality_profile must be production|flagship
(draft/debug cannot enter catalog ship manifests).

Authority: artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md

Usage:
  PYTHONPATH=. python3 scripts/ci/check_catalog_manifest_acceptance_layer.py
  PYTHONPATH=. python3 scripts/ci/check_catalog_manifest_acceptance_layer.py \\
      --manifest artifacts/catalog/assembly_manifests/foo_en_US.json

Exit: 0 pass (or no manifests); 1 fail.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_DIR = REPO_ROOT / "artifacts" / "catalog" / "assembly_manifests"

ALLOWED_LAYERS = frozenset(
    {
        "path_works",
        "path_works_prose_only",
        "structurally_clear",
        "authored_candidate",
        "authored_candidate_l3proxy",
        "system_working",
        "bestseller_register",
    }
)
SHIP_STATUSES = frozenset({"ok", "skip_r2", "skip_local"})
SHIP_PROFILES = frozenset({"production", "flagship"})
LAYER3_REQUIRED = frozenset({"system_working", "bestseller_register"})


def _normalize_layer(raw: object) -> str:
    return str(raw or "").strip().lower().replace(" ", "_").replace("-", "_")


def validate_manifest(data: dict, *, label: str) -> list[str]:
    violations: list[str] = []
    if not isinstance(data, dict):
        return [f"{label}: root must be a JSON object"]

    profile = str(data.get("quality_profile") or "").strip().lower()
    if profile and profile not in SHIP_PROFILES:
        violations.append(
            f"{label}: quality_profile={profile!r} not allowed for catalog ship "
            f"(D3: must be production|flagship)"
        )

    books = data.get("books") or []
    if not isinstance(books, list):
        return violations + [f"{label}: books must be a list"]

    for i, row in enumerate(books):
        if not isinstance(row, dict):
            violations.append(f"{label}: books[{i}] not an object")
            continue
        status = str(row.get("status") or "").strip()
        if status not in SHIP_STATUSES:
            continue
        bid = row.get("book_id") or f"index={i}"
        layer = _normalize_layer(row.get("acceptance_layer"))
        if not layer:
            violations.append(
                f"{label}: book {bid} status={status} missing acceptance_layer "
                f"(G-LAYER; default path_works)"
            )
            continue
        if layer not in ALLOWED_LAYERS:
            violations.append(
                f"{label}: book {bid} acceptance_layer={layer!r} not in "
                f"{sorted(ALLOWED_LAYERS)}"
            )
            continue
        if layer in LAYER3_REQUIRED:
            artifact = (
                row.get("layer3_artifact")
                or row.get("layer3_artifact_path")
                or row.get("ontgp_verdict_path")
                or ""
            )
            if layer == "bestseller_register":
                artifact = artifact or row.get("blind10_artifact") or row.get(
                    "layer4_artifact_path"
                ) or ""
            if not str(artifact).strip():
                violations.append(
                    f"{label}: book {bid} acceptance_layer={layer} requires "
                    f"layer3_artifact / ontgp_verdict_path"
                    + (
                        " (or blind10_artifact for bestseller_register)"
                        if layer == "bestseller_register"
                        else ""
                    )
                    + " — G-LAYER"
                )
    return violations


def iter_manifests(manifest_dir: Path, explicit: list[Path] | None) -> list[Path]:
    if explicit:
        return explicit
    if not manifest_dir.is_dir():
        return []
    return sorted(manifest_dir.glob("*.json"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G-LAYER catalog manifest acceptance_layer")
    ap.add_argument(
        "--manifest-dir",
        type=Path,
        default=DEFAULT_MANIFEST_DIR,
        help="Directory of assembly manifests",
    )
    ap.add_argument(
        "--manifest",
        action="append",
        type=Path,
        default=None,
        help="Explicit manifest path (repeatable)",
    )
    args = ap.parse_args(argv)

    paths = iter_manifests(args.manifest_dir, args.manifest)
    if not paths:
        print(
            "G-LAYER: PASS (no catalog assembly manifests present — nothing to validate)"
        )
        return 0

    violations: list[str] = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            violations.append(f"{path}: unreadable/invalid JSON ({exc})")
            continue
        try:
            rel = str(path.relative_to(REPO_ROOT))
        except ValueError:
            rel = str(path)
        violations.extend(validate_manifest(data, label=rel))

    if not violations:
        print(f"G-LAYER: PASS — {len(paths)} manifest(s) acceptance_layer OK")
        return 0

    print("G-LAYER: FAIL", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
        print(f"::error::{v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
