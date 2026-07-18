"""
Re-entrant dispatch checkpoint for Pearl_Conductor v3 unattended fan-out.

Spec: ``docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`` §2.2
Cap entry: ``CONDUCTOR-V3-DISPATCH-BRIDGE-V1-01``

Backs the fault-tolerance wrapper from PR #1044
(``scripts/image_generation/batch_runner.py::_dispatch_with_retries``) by
giving it a kill-safe TSV of every batch's status.

TSV schema (tab-separated):
    ts_utc | batch_id | brand_id | locale | surface | status |
    dispatch_path | attempts | wall_seconds | output_path |
    error_class | error_msg

``status ∈ {pending, in_flight, succeeded, failed, skipped}``.

All writes are atomic (temp-file + ``os.replace``). Re-entrancy:
``init_checkpoint`` is idempotent on the same ``run_id`` so a restart resumes
without truncation.

CLI (utility):
    python3 scripts/catalog/v1_1_dispatch_checkpoint.py --run-id <id> --summary
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = REPO_ROOT / "artifacts" / "qa"

CHECKPOINT_FIELDS: tuple[str, ...] = (
    "ts_utc",
    "batch_id",
    "brand_id",
    "locale",
    "surface",
    "status",
    "dispatch_path",
    "attempts",
    "wall_seconds",
    "output_path",
    "error_class",
    "error_msg",
)

VALID_STATUS = frozenset({"pending", "in_flight", "succeeded", "failed", "skipped"})


def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def checkpoint_path(run_id: str, *, root: Path | None = None) -> Path:
    base = root or CHECKPOINT_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base / f"conductor_v3_{run_id}_checkpoint.tsv"


def _atomic_write_rows(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    """Atomic write: tmp file in same dir + ``os.replace``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=list(CHECKPOINT_FIELDS),
                delimiter="\t",
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in CHECKPOINT_FIELDS})
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return [dict(r) for r in reader]


def init_checkpoint(
    run_id: str,
    batches: list[dict[str, Any]],
    *,
    root: Path | None = None,
) -> Path:
    """Create the checkpoint TSV with all batches as ``pending``.

    Idempotent: if a TSV for ``run_id`` already exists, returns its path
    without truncation (preserves any in-flight progress on resume).
    """
    path = checkpoint_path(run_id, root=root)
    if path.exists():
        return path
    seeded: list[dict[str, Any]] = []
    seen: set[str] = set()
    ts = _now_utc()
    for b in batches:
        bid = str(b.get("batch_id") or "").strip()
        if not bid:
            raise ValueError("init_checkpoint: every batch must have batch_id")
        if bid in seen:
            raise ValueError(f"init_checkpoint: duplicate batch_id {bid!r}")
        seen.add(bid)
        seeded.append({
            "ts_utc": ts,
            "batch_id": bid,
            "brand_id": str(b.get("brand_id", "")),
            "locale": str(b.get("locale", "")),
            "surface": str(b.get("surface", "")),
            "status": "pending",
            "dispatch_path": str(b.get("dispatch_path", "")),
            "attempts": 0,
            "wall_seconds": 0.0,
            "output_path": str(b.get("output_path", "")),
            "error_class": "",
            "error_msg": "",
        })
    _atomic_write_rows(path, seeded)
    return path


def _update_row(
    run_id: str,
    batch_id: str,
    updates: dict[str, Any],
    *,
    root: Path | None = None,
) -> dict[str, Any] | None:
    path = checkpoint_path(run_id, root=root)
    rows = _read_rows(path)
    found: dict[str, Any] | None = None
    for r in rows:
        if r.get("batch_id") == batch_id:
            r.update(updates)
            r["ts_utc"] = _now_utc()
            found = r
            break
    if found is None:
        return None
    _atomic_write_rows(path, rows)
    return found


def next_pending(run_id: str, *, root: Path | None = None) -> dict[str, Any] | None:
    """Return the next ``pending`` row (or a recoverable ``in_flight`` row).

    ``in_flight`` rows are returned after ``pending`` is exhausted so a
    crashed dispatcher can resume work it claimed but did not finish.
    """
    rows = _read_rows(checkpoint_path(run_id, root=root))
    for r in rows:
        if r.get("status") == "pending":
            return r
    for r in rows:
        if r.get("status") == "in_flight":
            return r
    return None


def mark_in_flight(
    run_id: str,
    batch_id: str,
    *,
    root: Path | None = None,
) -> dict[str, Any] | None:
    return _update_row(run_id, batch_id, {"status": "in_flight"}, root=root)


def mark_succeeded(
    run_id: str,
    batch_id: str,
    wall_s: float,
    output_path: str,
    *,
    root: Path | None = None,
) -> dict[str, Any] | None:
    return _update_row(
        run_id,
        batch_id,
        {
            "status": "succeeded",
            "wall_seconds": float(wall_s),
            "output_path": output_path,
            "error_class": "",
            "error_msg": "",
        },
        root=root,
    )


def mark_failed(
    run_id: str,
    batch_id: str,
    error_class: str,
    error_msg: str,
    attempts: int,
    *,
    root: Path | None = None,
) -> dict[str, Any] | None:
    return _update_row(
        run_id,
        batch_id,
        {
            "status": "failed",
            "attempts": int(attempts),
            "error_class": str(error_class),
            "error_msg": str(error_msg)[:1024],
        },
        root=root,
    )


def mark_skipped(
    run_id: str,
    batch_id: str,
    reason: str,
    *,
    root: Path | None = None,
) -> dict[str, Any] | None:
    return _update_row(
        run_id,
        batch_id,
        {"status": "skipped", "error_class": "skipped", "error_msg": str(reason)[:1024]},
        root=root,
    )


def summary(run_id: str, *, root: Path | None = None) -> dict[str, Any]:
    rows = _read_rows(checkpoint_path(run_id, root=root))
    by_status: dict[str, int] = {s: 0 for s in VALID_STATUS}
    by_locale: dict[str, dict[str, int]] = {}
    by_surface: dict[str, dict[str, int]] = {}
    cumulative_wall_s = 0.0
    for r in rows:
        st = (r.get("status") or "").strip()
        by_status[st] = by_status.get(st, 0) + 1
        loc = r.get("locale") or "unknown"
        loc_bucket = by_locale.setdefault(loc, {s: 0 for s in VALID_STATUS})
        loc_bucket[st] = loc_bucket.get(st, 0) + 1
        sfc = r.get("surface") or "unknown"
        sfc_bucket = by_surface.setdefault(sfc, {s: 0 for s in VALID_STATUS})
        sfc_bucket[st] = sfc_bucket.get(st, 0) + 1
        try:
            cumulative_wall_s += float(r.get("wall_seconds") or 0.0)
        except (TypeError, ValueError):
            pass
    return {
        "run_id": run_id,
        "total": len(rows),
        "by_status": by_status,
        "by_locale": by_locale,
        "by_surface": by_surface,
        "cumulative_wall_seconds": round(cumulative_wall_s, 3),
    }


def _cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="dispatch checkpoint utility")
    p.add_argument("--run-id", required=True)
    p.add_argument("--summary", action="store_true")
    args = p.parse_args(argv)
    if args.summary:
        json.dump(summary(args.run_id), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    p.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli(sys.argv[1:]))
