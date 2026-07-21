"""Tests for fill_social_bank multi-topic orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.storyblocks.fill_social_bank import (
    fill_social_bank,
    plates_for_topic,
    write_bank_artifacts,
)
from scripts.storyblocks.license_store import LicenseStore
from scripts.storyblocks.mau_ledger import MauLedger


def test_fill_social_bank_dry_run_writes_index(tmp_path: Path):
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    store = LicenseStore(bank_root=tmp_path / "licensed", index_path=tmp_path / "lic.jsonl")
    result = fill_social_bank(
        topics=["anxiety", "burnout"],
        media_types=["video", "image"],
        brand_id="way_stream_sanctuary",
        locale="en-US",
        work_unit_id="test_bank_wu",
        max_per_topic=1,
        dry_run=True,
        mau_ledger=ledger,
        license_store=store,
    )
    assert result.mode == "dry_run"
    assert result.layer == "CODE-WIRED"
    assert len(result.assets) == 4
    assert result.mau_distinct_count == 1
    for a in result.assets:
        assert Path(a.local_uri).is_file()

    out = write_bank_artifacts(result, out_dir=tmp_path / "bank")
    index = json.loads((out / "BANK_INDEX.json").read_text(encoding="utf-8"))
    assert index["asset_count"] == 4
    plates = plates_for_topic("anxiety", media_type="image", bank_index=index)
    assert len(plates) == 1


def test_fill_downloads_share_one_mau_identity(tmp_path: Path):
    ledger = MauLedger(path=tmp_path / "mau.jsonl", hard_cap=104)
    store = LicenseStore(bank_root=tmp_path / "licensed", index_path=tmp_path / "lic.jsonl")
    fill_social_bank(
        topics=["anxiety"],
        media_types=["video"],
        work_unit_id="wu_search_mau",
        max_per_topic=2,
        dry_run=True,
        mau_ledger=ledger,
        license_store=store,
    )
    assert ledger.distinct_count() == 1
