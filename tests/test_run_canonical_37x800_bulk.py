from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run_canonical_37x800_bulk as bulk


def test_build_shards_partitions_deterministically() -> None:
    shards = bulk.build_shards(["a", "b", "c", "d", "e"], 2)
    assert [s["shard_id"] for s in shards] == ["shard_00", "shard_01", "shard_02"]
    assert shards[0]["brand_ids"] == ["a", "b"]
    assert shards[1]["brand_ids"] == ["c", "d"]
    assert shards[2]["brand_ids"] == ["e"]


def test_build_brand_command_plan_only() -> None:
    cmd = bulk.build_brand_command(
        "stillness_press",
        books_per_brand=800,
        output_root=Path("/tmp/out"),
        max_parallel=4,
        compile_timeout_seconds=600,
        plan_only=True,
    )
    assert "--plan-only" in cmd
    assert "--resume" not in cmd
    assert cmd[cmd.index("--brand") + 1] == "stillness_press"


def test_build_brand_command_compile_mode() -> None:
    cmd = bulk.build_brand_command(
        "stillness_press",
        books_per_brand=800,
        output_root=Path("/tmp/out"),
        max_parallel=4,
        compile_timeout_seconds=600,
        plan_only=False,
    )
    assert "--skip-wave-selection" in cmd
    assert "--resume" in cmd
    assert "--no-teacher-mode" in cmd


def test_main_writes_manifest_and_dry_run_summary(monkeypatch, tmp_path: Path) -> None:
    brand_list = tmp_path / "brands.yaml"
    brand_list.write_text(
        "total_brands: 3\nbrands:\n  alpha: {}\n  beta: {}\n  gamma: {}\n",
        encoding="utf-8",
    )
    out_root = tmp_path / "bulk"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_canonical_37x800_bulk.py",
            "--brand-list",
            str(brand_list),
            "--brands-per-shard",
            "2",
            "--output-root",
            str(out_root),
            "--run-shard",
            "shard_00",
            "--plan-only",
            "--dry-run",
        ],
    )

    rc = bulk.main()

    assert rc == 0
    manifest = json.loads((out_root / "bulk_manifest.json").read_text(encoding="utf-8"))
    assert manifest["brand_count"] == 3
    summary = json.loads((out_root / "shard_00_summary.json").read_text(encoding="utf-8"))
    assert summary["all_succeeded"] is True
    assert [r["brand_id"] for r in summary["results"]] == ["alpha", "beta"]
    assert all(r["dry_run"] for r in summary["results"])
