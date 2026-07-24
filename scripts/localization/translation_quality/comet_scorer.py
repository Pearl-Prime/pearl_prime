#!/usr/bin/env python3
"""xCOMET-XL / CometKiwi (wmt22-cometkiwi-da) QE scoring integration.

**License note (tag every score with this -- non-negotiable per this
lane's brief):** `cc-by-nc-sa-4.0, non-commercial -- internal signal only,
not a ship gate`. `acceptance_gate.py` must never let a COMET score alone
accept or reject anything; this module never asserts otherwise.

These models are GPU-bound. Per docs/ROBUST_AGENT_PROTOCOL.md, dispatch is
queue-first via `pscli enqueue`, one item per job, atomic -- never a direct
blocking Bash call for a batch. This module is deliberately split into:
  - `build_job_payload()` / `parse_job_result()` -- pure, testable,
    no GPU/network dependency, usable from the enqueue/dequeue call sites.
  - `score_local()` -- the actual model call, meant to run ON Pearl Star
    inside a pscli-dispatched job process, not from an agent session's
    interactive shell.
  - `enqueue_comet_job()` / CLI `--enqueue` -- the RAP-compliant dispatch
    wrapper an agent session should actually call.

Usage (from Pearl Star, inside a dispatched job):
    python3 scripts/localization/translation_quality/comet_scorer.py \\
        --score-local --source-file src.txt --candidate-file cand.txt \\
        --model wmt22-cometkiwi-da --out result.json

Usage (from an agent session, RAP queue-first dispatch):
    python3 scripts/localization/translation_quality/comet_scorer.py \\
        --enqueue --source-file src.txt --candidate-file cand.txt \\
        --model wmt22-cometkiwi-da
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]

COMET_LICENSE_NOTE = (
    "cc-by-nc-sa-4.0, non-commercial -- internal signal only, not a ship gate"
)

SUPPORTED_MODELS = {
    "xcomet-xl": "Unbabel/XCOMET-XL",
    "wmt22-cometkiwi-da": "Unbabel/wmt22-cometkiwi-da",
}

PSCLI_TASK_NAME = "translation_quality_comet_score"


@dataclass
class CometScoreResult:
    model: str
    hf_model_id: str
    score: float  # 0.0-1.0 QE score (reference-free for CometKiwi; may use
    # a reference for xCOMET-XL if one was supplied)
    flagged_spans: list[dict[str, Any]] = field(default_factory=list)
    license_note: str = COMET_LICENSE_NOTE
    is_ship_gate: bool = False  # always False -- documents the rule inline

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "hf_model_id": self.hf_model_id,
            "score": self.score,
            "flagged_spans": self.flagged_spans,
            "license_note": self.license_note,
            "is_ship_gate": self.is_ship_gate,
        }


def build_job_payload(
    source_text: str,
    candidate_text: str,
    model: str,
    *,
    reference_text: str | None = None,
    item_id: str | None = None,
) -> dict[str, Any]:
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported COMET model {model!r}; choose from {sorted(SUPPORTED_MODELS)}")
    return {
        "task": PSCLI_TASK_NAME,
        "model": model,
        "hf_model_id": SUPPORTED_MODELS[model],
        "source_text": source_text,
        "candidate_text": candidate_text,
        "reference_text": reference_text,
        "item_id": item_id,
    }


def parse_job_result(raw: dict[str, Any]) -> CometScoreResult:
    return CometScoreResult(
        model=raw["model"],
        hf_model_id=raw.get("hf_model_id", SUPPORTED_MODELS.get(raw["model"], "")),
        score=float(raw["score"]),
        flagged_spans=list(raw.get("flagged_spans") or []),
    )


def score_local(payload: dict[str, Any]) -> CometScoreResult:
    """Actual model inference. Import comet/unbabel-comet lazily -- this
    function is meant to run inside a Pearl Star job process, which has
    the GPU + model weights; an agent session's local shell typically does
    not and should never call this directly (use enqueue_comet_job)."""
    try:
        from comet import download_model, load_from_checkpoint
    except ImportError as exc:  # pragma: no cover - exercised on Pearl Star only
        raise RuntimeError(
            "unbabel-comet not installed in this environment. This function "
            "is meant to run inside a Pearl Star pscli job, not an agent "
            "session's local shell -- see module docstring."
        ) from exc

    hf_model_id = payload["hf_model_id"]
    model_path = download_model(hf_model_id)
    model = load_from_checkpoint(model_path)

    data = [
        {
            "src": payload["source_text"],
            "mt": payload["candidate_text"],
            **({"ref": payload["reference_text"]} if payload.get("reference_text") else {}),
        }
    ]
    output = model.predict(data, batch_size=1, gpus=1)
    score = float(output.scores[0])
    flagged_spans = getattr(output, "metadata", {}).get("error_spans", [[]])[0] if hasattr(output, "metadata") else []

    return CometScoreResult(
        model=payload["model"],
        hf_model_id=hf_model_id,
        score=score,
        flagged_spans=flagged_spans,
    )


def _pscli_available() -> bool:
    return shutil.which("pscli") is not None


def enqueue_comet_job(payload: dict[str, Any]) -> str:
    """RAP-compliant queue-first dispatch. Returns the pscli job_id.

    Per docs/ROBUST_AGENT_PROTOCOL.md §2: PRE-CHECK pscli status, then
    ENQUEUE. This function does the enqueue step only -- polling/verify is
    the caller's job (calibration_harness.py drives that loop), matching
    RAP's own stall-threshold guidance rather than this module inventing
    its own.
    """
    if not _pscli_available():
        raise RuntimeError(
            "pscli not found on PATH. COMET scoring is GPU-bound and must "
            "be dispatched queue-first via pscli per docs/ROBUST_AGENT_PROTOCOL.md "
            "-- do not run score_local() directly from an agent session."
        )
    status = subprocess.run(["pscli", "status"], capture_output=True, text=True, timeout=15)
    if status.returncode != 0 or "PAUSED" in status.stdout:
        raise RuntimeError(f"pscli queue not RUNNING (status output: {status.stdout!r}); not enqueuing.")

    proc = subprocess.run(
        ["pscli", "enqueue", "--task", PSCLI_TASK_NAME, "--payload", json.dumps(payload)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"pscli enqueue failed: {proc.stdout} {proc.stderr}")
    # pscli enqueue is expected to print the job_id as the last non-empty line.
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError(f"pscli enqueue produced no output: {proc.stdout!r}")
    return lines[-1].strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-file", type=Path, required=True)
    ap.add_argument("--candidate-file", type=Path, required=True)
    ap.add_argument("--reference-file", type=Path, default=None)
    ap.add_argument("--item-id", default=None)
    ap.add_argument("--model", default="wmt22-cometkiwi-da", choices=sorted(SUPPORTED_MODELS))
    ap.add_argument("--out", type=Path, default=None)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--enqueue", action="store_true", help="Queue-first dispatch via pscli (agent-session path)")
    mode.add_argument("--score-local", action="store_true", help="Run inference in-process (Pearl Star job path only)")
    args = ap.parse_args(argv)

    payload = build_job_payload(
        args.source_file.read_text(encoding="utf-8"),
        args.candidate_file.read_text(encoding="utf-8"),
        model=args.model,
        reference_text=args.reference_file.read_text(encoding="utf-8") if args.reference_file else None,
        item_id=args.item_id,
    )

    if args.enqueue:
        job_id = enqueue_comet_job(payload)
        print(f"enqueued job_id={job_id}")
        return 0

    result = score_local(payload)
    out_json = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(out_json + "\n", encoding="utf-8")
    print(out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
