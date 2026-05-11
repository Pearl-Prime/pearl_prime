"""Tests for ``scripts/catalog/v1_1_dispatch_checkpoint.py``.

Covers:
- init_checkpoint creates pending TSV
- init_checkpoint is idempotent (resume safe)
- next_pending advances through pending → in_flight → empty
- mark_succeeded / mark_failed / mark_skipped persist correctly
- atomic write (kill mid-flight cannot corrupt TSV)
- summary aggregates per-locale, per-surface, by_status
- re-entrancy: simulated kill + restart resumes pending; succeeded NOT redone
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog import v1_1_dispatch_checkpoint as cp  # noqa: E402


@pytest.fixture
def sample_batches() -> list[dict]:
    return [
        {"batch_id": f"b{i:03d}", "brand_id": "stillness_press",
         "locale": "en-US" if i % 2 == 0 else "ja-JP",
         "surface": "cover" if i < 3 else "panel",
         "dispatch_path": "pearl_star" if i < 3 else "runcomfy",
         "output_path": f"/tmp/out/b{i:03d}.png"}
        for i in range(6)
    ]


def test_init_creates_pending_tsv(tmp_path, sample_batches):
    p = cp.init_checkpoint("r1", sample_batches, root=tmp_path)
    assert p.exists()
    rows = list(csv.DictReader(p.open(), delimiter="\t"))
    assert len(rows) == 6
    assert all(r["status"] == "pending" for r in rows)


def test_init_is_idempotent(tmp_path, sample_batches):
    p1 = cp.init_checkpoint("r2", sample_batches, root=tmp_path)
    # Mark one as succeeded, then re-init — must NOT truncate
    cp.mark_succeeded("r2", "b000", 12.5, "/tmp/out/b000.png", root=tmp_path)
    p2 = cp.init_checkpoint("r2", sample_batches, root=tmp_path)
    assert p1 == p2
    rows = list(csv.DictReader(p2.open(), delimiter="\t"))
    succeeded = [r for r in rows if r["status"] == "succeeded"]
    assert len(succeeded) == 1
    assert succeeded[0]["batch_id"] == "b000"


def test_init_rejects_duplicate_batch_id(tmp_path):
    with pytest.raises(ValueError, match="duplicate batch_id"):
        cp.init_checkpoint(
            "r3",
            [
                {"batch_id": "x", "brand_id": "a", "locale": "en", "surface": "cover"},
                {"batch_id": "x", "brand_id": "a", "locale": "en", "surface": "cover"},
            ],
            root=tmp_path,
        )


def test_init_rejects_missing_batch_id(tmp_path):
    with pytest.raises(ValueError, match="batch_id"):
        cp.init_checkpoint(
            "r4",
            [{"brand_id": "a", "locale": "en", "surface": "cover"}],
            root=tmp_path,
        )


def test_next_pending_advances(tmp_path, sample_batches):
    cp.init_checkpoint("r5", sample_batches, root=tmp_path)
    seen = set()
    for _ in range(6):
        nxt = cp.next_pending("r5", root=tmp_path)
        assert nxt is not None
        bid = nxt["batch_id"]
        assert bid not in seen
        seen.add(bid)
        cp.mark_succeeded("r5", bid, 1.0, f"/tmp/{bid}.png", root=tmp_path)
    assert cp.next_pending("r5", root=tmp_path) is None


def test_in_flight_recoverable_after_pending_exhausted(tmp_path, sample_batches):
    cp.init_checkpoint("r6", sample_batches, root=tmp_path)
    cp.mark_in_flight("r6", "b000", root=tmp_path)
    # Drain remaining 5 pending
    for i in range(1, 6):
        cp.mark_succeeded("r6", f"b{i:03d}", 1.0, "x", root=tmp_path)
    nxt = cp.next_pending("r6", root=tmp_path)
    assert nxt is not None
    assert nxt["batch_id"] == "b000"
    assert nxt["status"] == "in_flight"


def test_mark_failed_records_error(tmp_path, sample_batches):
    cp.init_checkpoint("r7", sample_batches, root=tmp_path)
    cp.mark_failed("r7", "b001", "RunComfyTimeout", "queue stuck 30s", 3, root=tmp_path)
    s = cp.summary("r7", root=tmp_path)
    assert s["by_status"]["failed"] == 1
    rows = list(csv.DictReader(cp.checkpoint_path("r7", root=tmp_path).open(), delimiter="\t"))
    failed = next(r for r in rows if r["batch_id"] == "b001")
    assert failed["error_class"] == "RunComfyTimeout"
    assert failed["attempts"] == "3"


def test_mark_skipped(tmp_path, sample_batches):
    cp.init_checkpoint("r8", sample_batches, root=tmp_path)
    cp.mark_skipped("r8", "b002", "cap exceeded", root=tmp_path)
    s = cp.summary("r8", root=tmp_path)
    assert s["by_status"]["skipped"] == 1


def test_summary_aggregates(tmp_path, sample_batches):
    cp.init_checkpoint("r9", sample_batches, root=tmp_path)
    cp.mark_succeeded("r9", "b000", 10.0, "x", root=tmp_path)
    cp.mark_succeeded("r9", "b001", 20.0, "x", root=tmp_path)
    cp.mark_failed("r9", "b002", "E", "msg", 1, root=tmp_path)
    s = cp.summary("r9", root=tmp_path)
    assert s["total"] == 6
    assert s["by_status"]["succeeded"] == 2
    assert s["by_status"]["failed"] == 1
    assert s["by_status"]["pending"] == 3
    assert s["cumulative_wall_seconds"] == 30.0
    assert "en-US" in s["by_locale"]
    assert "cover" in s["by_surface"]


def test_reentrancy_after_simulated_kill(tmp_path, sample_batches):
    """Simulate: process A processes 2 batches then dies; process B resumes
    the remaining pending without redoing succeeded."""
    cp.init_checkpoint("r10", sample_batches, root=tmp_path)
    # Process A: succeed 2
    cp.mark_succeeded("r10", "b000", 5.0, "/x/0.png", root=tmp_path)
    cp.mark_succeeded("r10", "b001", 5.0, "/x/1.png", root=tmp_path)
    # Process A claims a third then "dies" mid-flight
    cp.mark_in_flight("r10", "b002", root=tmp_path)

    # Process B starts: re-init must NOT clobber state
    cp.init_checkpoint("r10", sample_batches, root=tmp_path)
    rows_b = list(csv.DictReader(cp.checkpoint_path("r10", root=tmp_path).open(), delimiter="\t"))
    succeeded = [r for r in rows_b if r["status"] == "succeeded"]
    in_flight = [r for r in rows_b if r["status"] == "in_flight"]
    pending = [r for r in rows_b if r["status"] == "pending"]
    assert len(succeeded) == 2
    assert len(in_flight) == 1
    assert len(pending) == 3

    # Process B drains: pending first, then in_flight
    drained: list[str] = []
    while True:
        nxt = cp.next_pending("r10", root=tmp_path)
        if nxt is None:
            break
        drained.append(nxt["batch_id"])
        cp.mark_succeeded("r10", nxt["batch_id"], 1.0, "x", root=tmp_path)
    # Pending b003, b004, b005 first; then in_flight b002
    assert drained[:3] == ["b003", "b004", "b005"]
    assert drained[3] == "b002"
    # No batch processed twice
    assert len(set(drained)) == len(drained)

    final = cp.summary("r10", root=tmp_path)
    assert final["by_status"]["succeeded"] == 6
    assert final["by_status"]["pending"] == 0
    assert final["by_status"]["in_flight"] == 0


def test_atomic_write_no_partial_file(tmp_path, sample_batches, monkeypatch):
    """Simulate exception mid-write: TSV must remain unchanged."""
    p = cp.init_checkpoint("r11", sample_batches, root=tmp_path)
    original = p.read_text(encoding="utf-8")
    real_replace = __import__("os").replace

    def boom(*_a, **_k):
        raise RuntimeError("simulated crash")

    monkeypatch.setattr("os.replace", boom)
    with pytest.raises(RuntimeError):
        cp.mark_succeeded("r11", "b000", 1.0, "x", root=tmp_path)
    monkeypatch.setattr("os.replace", real_replace)
    # File still intact
    assert p.read_text(encoding="utf-8") == original


def test_update_unknown_batch_returns_none(tmp_path, sample_batches):
    cp.init_checkpoint("r12", sample_batches, root=tmp_path)
    assert cp.mark_succeeded("r12", "no_such_batch", 1.0, "x", root=tmp_path) is None


def test_summary_empty_run(tmp_path):
    s = cp.summary("never_init", root=tmp_path)
    assert s["total"] == 0
    assert s["cumulative_wall_seconds"] == 0.0


def test_cli_summary_outputs_json(tmp_path, sample_batches, capsys):
    cp.init_checkpoint("r_cli", sample_batches, root=tmp_path)
    # CLI writes to default location, which we override only via --root if
    # the CLI supported it. For now verify _cli summary path runs.
    rc = cp._cli(["--run-id", "r_cli", "--summary"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "by_status" in out
