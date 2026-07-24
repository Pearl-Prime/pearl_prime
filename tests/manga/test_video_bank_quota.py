"""Quota ledger math + max-seconds refusal for capture burn."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GOLDEN = REPO / "tests" / "fixtures" / "manga" / "video_bank" / "golden_capture_manifest.json"
SCHEMA = REPO / "schemas" / "manga" / "character_capture_manifest.schema.json"


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_quota_plan_math() -> None:
    from scripts.manga.video_bank.run_capture_burn import compute_quota_plan

    manifest = json.loads(GOLDEN.read_text(encoding="utf-8"))
    ledger = compute_quota_plan(manifest, max_seconds=20.0)
    assert ledger.requested_seconds == 10.0
    assert ledger.planned_seconds == 10.0
    assert ledger.reserve_seconds == 10.0
    assert ledger.remaining_under_cap == 10.0
    assert len(ledger.clips) == 2


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_max_seconds_refuses_overplan() -> None:
    from scripts.manga.video_bank.run_capture_burn import compute_quota_plan

    manifest = json.loads(GOLDEN.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="max-seconds"):
        compute_quota_plan(manifest, max_seconds=5.0)


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_preflight_writes_ledger(tmp_path: Path) -> None:
    from scripts.manga.video_bank.run_capture_burn import run_burn

    manifest = json.loads(GOLDEN.read_text(encoding="utf-8"))
    proof = tmp_path / "proof"
    ledger = run_burn(manifest, proof_root=proof, max_seconds=20.0, preflight_only=True)
    assert ledger.spent_seconds == 0.0
    path = proof / "quota_ledger.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["requested_seconds"] == 10.0
    assert any("preflight_only" in n for n in data["notes"])


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_rejects_non_cloud_engine_in_manifest() -> None:
    from scripts.manga.video_bank.run_capture_burn import compute_quota_plan

    manifest = json.loads(GOLDEN.read_text(encoding="utf-8"))
    manifest["capture_sets"][0]["engine"] = "wan2.7-r2v"
    with pytest.raises(ValueError, match="rejected"):
        compute_quota_plan(manifest, max_seconds=None)


@pytest.mark.skipif(not SCHEMA.is_file(), reason="capture manifest schema not on disk yet")
def test_stub_runner_records_spend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    from scripts.manga.video_bank import STUB_GUARD_BYTES
    from scripts.manga.video_bank.run_capture_burn import run_burn

    monkeypatch.setenv("PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW", "1")
    monkeypatch.setenv("DASHSCOPE_FREE_QUOTA_API_KEY", "test-free-key-not-real")

    manifest = json.loads(GOLDEN.read_text(encoding="utf-8"))
    manifest["capture_sets"] = [manifest["capture_sets"][0]]
    manifest["quota_budget"]["planned_seconds"] = 5

    def fake_runner(**kwargs):
        out_dir = Path(kwargs["out_dir"])
        dest = out_dir / f"{kwargs['stem']}.mp4"
        dest.write_bytes(b"\0" * (STUB_GUARD_BYTES + 10))
        return SimpleNamespace(
            task_id="fake",
            bytes=STUB_GUARD_BYTES + 10,
            local_path=dest,
        )

    proof = tmp_path / "proof"
    ledger = run_burn(
        manifest,
        proof_root=proof,
        max_seconds=5.0,
        preflight_only=False,
        video_runner=fake_runner,
    )
    assert ledger.spent_seconds == 5.0
    assert ledger.clips[0]["status"] == "captured"
    assert ledger.clips[0]["bytes"] >= STUB_GUARD_BYTES
