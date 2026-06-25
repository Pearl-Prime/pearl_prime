#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_full_catalog import _load_brand_ids_from_yaml  # noqa: E402

DEFAULT_BRAND_LIST = REPO_ROOT / "config" / "manga" / "canonical_brand_list.yaml"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "artifacts" / "full_catalog" / "canonical_37x800"
GENERATE_FULL_CATALOG = REPO_ROOT / "scripts" / "generate_full_catalog.py"


def build_shards(brands: list[str], brands_per_shard: int) -> list[dict[str, Any]]:
    if brands_per_shard <= 0:
        raise ValueError("brands_per_shard must be > 0")
    shards = []
    for idx in range(0, len(brands), brands_per_shard):
        chunk = brands[idx : idx + brands_per_shard]
        shards.append({
            "shard_id": f"shard_{len(shards):02d}",
            "brand_ids": chunk,
            "books_per_brand": 800,
        })
    return shards


def build_brand_command(
    brand_id: str,
    *,
    books_per_brand: int,
    output_root: Path,
    max_parallel: int,
    compile_timeout_seconds: int,
    plan_only: bool,
) -> list[str]:
    cmd = [
        sys.executable,
        str(GENERATE_FULL_CATALOG),
        "--brand", brand_id,
        "--books-per-brand", str(books_per_brand),
        "--candidates-dir", str(output_root / "brands" / brand_id),
    ]
    if plan_only:
        cmd.append("--plan-only")
    else:
        cmd += [
            "--skip-wave-selection",
            "--resume",
            "--no-teacher-mode",
            "--max-parallel", str(max_parallel),
            "--compile-timeout-seconds", str(compile_timeout_seconds),
        ]
    return cmd


def run_shard(shard: dict[str, Any], *, output_root: Path, max_parallel: int, compile_timeout_seconds: int, plan_only: bool, dry_run: bool) -> dict[str, Any]:
    results = []
    for brand_id in shard["brand_ids"]:
        cmd = build_brand_command(
            brand_id,
            books_per_brand=int(shard["books_per_brand"]),
            output_root=output_root,
            max_parallel=max_parallel,
            compile_timeout_seconds=compile_timeout_seconds,
            plan_only=plan_only,
        )
        if dry_run:
            results.append({"brand_id": brand_id, "returncode": 0, "command": cmd, "dry_run": True})
            continue
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        results.append({
            "brand_id": brand_id,
            "returncode": proc.returncode,
            "command": cmd,
            "stdout_tail": (proc.stdout or "")[-500:],
            "stderr_tail": (proc.stderr or "")[-500:],
        })
        if proc.returncode != 0:
            break
    return {
        "shard_id": shard["shard_id"],
        "brand_ids": list(shard["brand_ids"]),
        "results": results,
        "all_succeeded": all(r["returncode"] == 0 for r in results),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Shard runner for canonical 37-brand x 800-book bulk catalog work.")
    ap.add_argument("--brand-list", type=Path, default=DEFAULT_BRAND_LIST)
    ap.add_argument("--books-per-brand", type=int, default=800)
    ap.add_argument("--brands-per-shard", type=int, default=1)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument("--max-parallel", type=int, default=4)
    ap.add_argument("--compile-timeout-seconds", type=int, default=600)
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run-shard", default=None, help="Run a single shard_id (e.g. shard_00)")
    ap.add_argument("--run-all-shards", action="store_true")
    args = ap.parse_args()

    brands = _load_brand_ids_from_yaml(args.brand_list)
    shards = build_shards(brands, args.brands_per_shard)
    for shard in shards:
        shard["books_per_brand"] = args.books_per_brand
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_root / "bulk_manifest.json"
    manifest_path.write_text(json.dumps({"brand_count": len(brands), "shards": shards}, indent=2), encoding="utf-8")

    if not args.run_shard and not args.run_all_shards:
        print(json.dumps({"manifest_path": str(manifest_path), "shard_count": len(shards), "brands": len(brands)}, indent=2))
        return 0

    target_shards = shards if args.run_all_shards else [s for s in shards if s["shard_id"] == args.run_shard]
    if not target_shards:
        print(f"Unknown shard id: {args.run_shard}", file=sys.stderr)
        return 1

    overall_ok = True
    for shard in target_shards:
        summary = run_shard(
            shard,
            output_root=args.output_root,
            max_parallel=args.max_parallel,
            compile_timeout_seconds=args.compile_timeout_seconds,
            plan_only=args.plan_only,
            dry_run=args.dry_run,
        )
        summary_path = args.output_root / f"{shard['shard_id']}_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps({"shard_id": shard["shard_id"], "summary_path": str(summary_path), "all_succeeded": summary["all_succeeded"]}, indent=2))
        overall_ok = overall_ok and summary["all_succeeded"]
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
