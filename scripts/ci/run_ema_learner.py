#!/usr/bin/env python3
"""
Run EMA weight update pass from accumulated editorial feedback.

Usage:
  python3 scripts/ci/run_ema_learner.py
  python3 scripts/ci/run_ema_learner.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import yaml

from phoenix_v4.quality.ei_v2.learner import (
    LearnedParams,
    calibration_report,
    learn_from_feedback,
    load_feedback,
    load_learned_params,
    save_learned_params,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EMA_LOG_PATH = _REPO_ROOT / "artifacts" / "ei_v2" / "ema_update_log.jsonl"


def _load_config() -> dict:
    cfg_path = _REPO_ROOT / "config" / "quality" / "ei_v2_config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolve_path(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else _REPO_ROOT / p


def _learner_paths(cfg: dict) -> tuple[Path, Path]:
    learner_cfg = cfg.get("learner") or {}
    feedback_path = _resolve_path(
        learner_cfg.get("feedback_path", "artifacts/ei_v2/learner_feedback.jsonl")
    )
    params_path = _resolve_path(
        learner_cfg.get("params_path", "artifacts/ei_v2/learned_params.json")
    )
    return feedback_path, params_path


def _min_observations(cfg: dict) -> int:
    learner_cfg = cfg.get("learner") or {}
    return int(learner_cfg.get("min_observations", 10))


def _append_update_log(entry: dict) -> None:
    _EMA_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    with open(_EMA_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EMA weight update from editorial feedback")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing params",
    )
    args = parser.parse_args()

    cfg = _load_config()
    feedback_path, params_path = _learner_paths(cfg)
    min_obs = _min_observations(cfg)

    # Count records
    records = load_feedback(feedback_path)
    count = len(records)

    print(f"EMA learner: feedback_path={feedback_path}")
    print(f"EMA learner: params_path={params_path}")
    print(f"EMA learner: {count} record(s) found, min_observations={min_obs}")

    if count < min_obs:
        print(
            f"Warning: insufficient records ({count} < {min_obs}). "
            "No update performed."
        )
        return 0

    # Snapshot current params before update
    previous = load_learned_params(params_path if params_path.exists() else None)

    if args.dry_run:
        # Run learn_from_feedback into a tmp file to preview
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        save_learned_params(previous, tmp_path)
        updated = learn_from_feedback(feedback_path, tmp_path, cfg=cfg)
        tmp_path.unlink(missing_ok=True)
        print("[DRY-RUN] Changes NOT written to disk.")
    else:
        updated = learn_from_feedback(feedback_path, params_path, cfg=cfg)

    report = calibration_report(updated, previous)

    # Print old → new → delta for each dimension
    print("\nComposite weight changes:")
    for dim, info in report["composite_weights"].items():
        delta_str = f"{info['delta']:+.6f}"
        print(
            f"  {dim:20s}  {info['previous']:.6f} -> {info['current']:.6f}  "
            f"delta={delta_str}"
        )
    om = report["override_margin"]
    print(
        f"\n  {'override_margin':20s}  {om['previous']:.6f} -> {om['current']:.6f}  "
        f"delta={om['delta']:+.6f}"
    )
    print(f"\n  total_observations: {previous.total_observations} -> {updated.total_observations}")

    if not args.dry_run:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "records_used": count,
            "dry_run": False,
            "override_margin_before": previous.override_margin,
            "override_margin_after": updated.override_margin,
            "weights_before": dict(previous.composite_weights),
            "weights_after": dict(updated.composite_weights),
        }
        _append_update_log(log_entry)
        print(f"\nUpdate logged to {_EMA_LOG_PATH}")
        print(f"Params written to {params_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
