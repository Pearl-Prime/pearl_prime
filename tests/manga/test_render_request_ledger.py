from __future__ import annotations

from pathlib import Path

from scripts.manga import render_request_ledger as ledger


def test_upsert_and_reconcile_usable_request(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.json"
    out_path = Path("artifacts/manga/demo/image_bank/L0/demo.png")
    real_out = tmp_path / out_path
    real_out.parent.mkdir(parents=True, exist_ok=True)
    real_out.write_bytes(b"x" * (ledger.MIN_REAL_BYTES + 10))

    orig_repo = ledger.REPO
    orig_blob_check = ledger._safe_blob_check
    try:
        ledger.REPO = tmp_path
        spec = ledger.build_request_spec(
            campaign_id="wave",
            series_key="mecha",
            series_id="demo_series",
            layer_id="demo",
            layer_class="L0",
            out_path=real_out,
            prompt="industrial hangar with readable structure",
            negative="blob",
            width=1080,
            height=1920,
            task="t2i_flux_dev_h1a",
        )
        ledger.upsert_requests([spec], ledger_path=ledger_path)
        ledger._safe_blob_check = lambda _p: False  # type: ignore[assignment]
        summary = ledger.reconcile_requests(ledger_path=ledger_path, queue_status_map={})
    finally:
        ledger.REPO = orig_repo
        ledger._safe_blob_check = orig_blob_check
    assert summary["counts"]["usable"] == 1
    doc = ledger.load_ledger(ledger_path)
    req = next(iter(doc["requests"].values()))
    assert req["status"] == "usable"


def test_reconcile_marks_blob_failed_and_requeueable(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.json"
    out_path = Path("artifacts/manga/demo/image_bank/L0/blob.png")
    real_out = tmp_path / out_path
    real_out.parent.mkdir(parents=True, exist_ok=True)
    real_out.write_bytes(b"x" * (ledger.MIN_REAL_BYTES + 10))

    orig_repo = ledger.REPO
    orig_blob_check = ledger._safe_blob_check
    try:
        ledger.REPO = tmp_path
        spec = ledger.build_request_spec(
            campaign_id="wave",
            series_key="thriller",
            series_id="demo_series",
            layer_id="blob",
            layer_class="L0",
            out_path=real_out,
            prompt="night corridor with readable fluorescent geometry",
            negative="blob",
            width=1080,
            height=1920,
            task="t2i_flux_dev_h1a",
        )
        doc, _ = ledger.upsert_requests([spec], ledger_path=ledger_path)
        rid = next(iter(doc["requests"].keys()))
        ledger.record_enqueue(rid, job_id=77, via="ssh:pearl_star", task="t2i_flux_dev_h1a", ledger_path=ledger_path)
        ledger._safe_blob_check = lambda _p: True  # type: ignore[assignment]
        ledger.reconcile_requests(ledger_path=ledger_path, queue_status_map={77: "succeeded"})
    finally:
        ledger.REPO = orig_repo
        ledger._safe_blob_check = orig_blob_check
    pending = ledger.request_ids_needing_enqueue(ledger_path=ledger_path)
    assert rid in pending
    req = ledger.load_ledger(ledger_path)["requests"][rid]
    assert req["status"] == "blob_failed"


def test_record_enqueue_sets_latest_job_and_history(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.json"
    orig_repo = ledger.REPO
    try:
        ledger.REPO = tmp_path
        spec = ledger.build_request_spec(
            campaign_id="wave",
            series_key="mecha",
            series_id="demo_series",
            layer_id="cockpit",
            layer_class="L0",
            out_path=tmp_path / "artifacts/manga/demo/image_bank/L0/cockpit.png",
            prompt="cockpit interior with harness and telemetry",
            negative="blob",
            width=1080,
            height=1920,
            task="t2i_flux_dev_h1a",
        )
        doc, _ = ledger.upsert_requests([spec], ledger_path=ledger_path)
        rid = next(iter(doc["requests"].keys()))
        row = ledger.record_enqueue(rid, job_id=12, via="local", task="t2i_flux_dev_h1a", ledger_path=ledger_path)
        assert row["latest_job_id"] == 12
        assert row["status"] == "queued"
        assert row["job_history"][-1]["job_id"] == 12
    finally:
        ledger.REPO = orig_repo
