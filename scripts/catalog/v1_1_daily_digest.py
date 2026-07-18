"""
V1.1 daily digest writer for Pearl_Conductor v3 unattended fan-out.

Spec: ``docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`` §2.3
Cap entry: ``CONDUCTOR-V3-DISPATCH-BRIDGE-V1-01``

Reads the checkpoint TSV (``v1_1_dispatch_checkpoint``) + the RunComfy spend
ledger (``artifacts/finance/runcomfy_spend_ledger.tsv``, PR #1045) and emits
``artifacts/coordination/conductor_v3_daily_digest_YYYY-MM-DD.md`` once per
UTC day. Appends a one-line summary to
``artifacts/coordination/CONDUCTOR_HANDOFF.md`` per CLAUDE.md cross-session
continuity schema.

CLI:
    python3 scripts/catalog/v1_1_daily_digest.py --run-id <id> [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog.v1_1_dispatch_checkpoint import (  # noqa: E402
    checkpoint_path,
    summary as checkpoint_summary,
)

DEFAULT_LEDGER = REPO_ROOT / "artifacts" / "finance" / "runcomfy_spend_ledger.tsv"
COORDINATION_DIR = REPO_ROOT / "artifacts" / "coordination"
HANDOFF_PATH = COORDINATION_DIR / "CONDUCTOR_HANDOFF.md"
DEFAULT_CAP_USD = 10.0


def _today_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).date().isoformat()


def _read_ledger_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for r in reader:
            rows.append(dict(r))
    return rows


def cumulative_runcomfy_spend(
    ledger_rows: list[dict[str, Any]],
    *,
    day: str | None = None,
) -> tuple[float, float]:
    """Return (cumulative_month_usd, day_usd).

    cumulative_month_usd: latest ``cumulative_month_usd`` value in ledger.
    day_usd: sum of ``est_usd`` whose ``date_local`` equals ``day``.
    """
    cumulative = 0.0
    day_usd = 0.0
    for r in ledger_rows:
        try:
            cm = float(r.get("cumulative_month_usd") or 0.0)
            if cm > cumulative:
                cumulative = cm
        except (TypeError, ValueError):
            pass
        if day and (r.get("date_local") or "").strip() == day:
            try:
                day_usd += float(r.get("est_usd") or 0.0)
            except (TypeError, ValueError):
                pass
    return round(cumulative, 4), round(day_usd, 4)


def _read_checkpoint_rows(run_id: str, *, root: Path | None = None) -> list[dict[str, Any]]:
    path = checkpoint_path(run_id, root=root)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh, delimiter="\t")]


def _est_completion_eta(
    succeeded: int,
    pending_total: int,
    *,
    day_window: float = 1.0,
) -> str:
    """Linear extrapolation. ``day_window`` defaults to 1 UTC day."""
    if succeeded <= 0 or pending_total <= 0:
        return "n/a (insufficient signal)"
    days = (pending_total / succeeded) * day_window
    eta_dt = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(days=days)
    return eta_dt.date().isoformat() + f" (~{days:.1f} days at current rate)"


def compute_digest(
    run_id: str,
    *,
    date: str | None = None,
    checkpoint_root: Path | None = None,
    ledger_path: Path | None = None,
    cap_usd: float = DEFAULT_CAP_USD,
) -> dict[str, Any]:
    day = date or _today_utc()
    rows = _read_checkpoint_rows(run_id, root=checkpoint_root)
    summary = checkpoint_summary(run_id, root=checkpoint_root)
    by_status = summary["by_status"]

    succeeded = by_status.get("succeeded", 0)
    failed = by_status.get("failed", 0)
    pending = by_status.get("pending", 0) + by_status.get("in_flight", 0)

    # cells_retried: rows with attempts > 1 and status succeeded
    retried = sum(
        1 for r in rows
        if r.get("status") == "succeeded" and _safe_int(r.get("attempts")) > 1
    )

    # error_class histogram (top 5)
    err_counter: Counter[str] = Counter()
    for r in rows:
        if r.get("status") == "failed":
            ec = (r.get("error_class") or "unknown").strip() or "unknown"
            err_counter[ec] += 1
    top5 = err_counter.most_common(5)

    # Pearl Star GPU seconds (sum wall_seconds where dispatch_path=pearl_star)
    pearl_seconds = 0.0
    for r in rows:
        if (r.get("dispatch_path") or "").strip().lower() == "pearl_star":
            try:
                pearl_seconds += float(r.get("wall_seconds") or 0.0)
            except (TypeError, ValueError):
                pass

    ledger_rows = _read_ledger_rows(ledger_path or DEFAULT_LEDGER)
    cumulative, day_spend = cumulative_runcomfy_spend(ledger_rows, day=day)
    cap_remaining = round(max(0.0, cap_usd - cumulative), 4)

    eta = _est_completion_eta(succeeded, pending)

    return {
        "run_id": run_id,
        "day_window_utc": day,
        "cells_succeeded": succeeded,
        "cells_failed_permanently": failed,
        "cells_retried": retried,
        "total_units_generated": succeeded,
        "cumulative_runcomfy_spend_usd": cumulative,
        "day_runcomfy_spend_usd": day_spend,
        "cap_remaining_usd": cap_remaining,
        "gpu_seconds_pearl_star": round(pearl_seconds, 3),
        "top_5_transient_causes": [{"error_class": e, "count": c} for e, c in top5],
        "est_completion_eta": eta,
        "by_locale": summary["by_locale"],
        "by_surface": summary["by_surface"],
        "total_pending": pending,
    }


def _safe_int(v: Any) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def digest_to_markdown(digest: dict[str, Any]) -> str:
    top5 = "\n".join(
        f"- `{e['error_class']}` × {e['count']}"
        for e in digest["top_5_transient_causes"]
    ) or "- (no failures recorded)"
    locale_table = "\n".join(
        f"| `{loc}` | {counts.get('succeeded', 0)} | {counts.get('failed', 0)} |"
        f" {counts.get('pending', 0) + counts.get('in_flight', 0)} |"
        for loc, counts in sorted(digest["by_locale"].items())
    ) or "| (no rows) | | | |"
    surface_table = "\n".join(
        f"| `{sfc}` | {counts.get('succeeded', 0)} | {counts.get('failed', 0)} |"
        f" {counts.get('pending', 0) + counts.get('in_flight', 0)} |"
        for sfc, counts in sorted(digest["by_surface"].items())
    ) or "| (no rows) | | | |"
    return f"""# Pearl_Conductor v3 daily digest — {digest['day_window_utc']}

**run_id:** `{digest['run_id']}`
**day_window_utc:** {digest['day_window_utc']} (00:00Z–24:00Z)

## Cells

| metric | value |
|---|---:|
| cells_succeeded | {digest['cells_succeeded']} |
| cells_failed_permanently | {digest['cells_failed_permanently']} |
| cells_retried | {digest['cells_retried']} |
| total_units_generated | {digest['total_units_generated']} |
| total_pending | {digest['total_pending']} |

## Spend (RunComfy)

| metric | value |
|---|---:|
| cumulative_runcomfy_spend_usd | ${digest['cumulative_runcomfy_spend_usd']:.4f} |
| day_runcomfy_spend_usd | ${digest['day_runcomfy_spend_usd']:.4f} |
| cap_remaining_usd | ${digest['cap_remaining_usd']:.4f} |

## GPU

| metric | value |
|---|---:|
| gpu_seconds_pearl_star | {digest['gpu_seconds_pearl_star']} |

## Top 5 transient causes

{top5}

## Per-locale

| locale | succeeded | failed | pending |
|---|---:|---:|---:|
{locale_table}

## Per-surface

| surface | succeeded | failed | pending |
|---|---:|---:|---:|
{surface_table}

## ETA

{digest['est_completion_eta']}

---

Spec: `docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`
"""


def _handoff_line(digest: dict[str, Any]) -> str:
    return (
        f"{digest['day_window_utc']} | run_id={digest['run_id']} | "
        f"succeeded={digest['cells_succeeded']} | "
        f"failed={digest['cells_failed_permanently']} | "
        f"pending={digest['total_pending']} | "
        f"spend=${digest['cumulative_runcomfy_spend_usd']:.4f} | "
        f"cap_remaining=${digest['cap_remaining_usd']:.4f} | "
        f"eta={digest['est_completion_eta']}\n"
    )


def append_handoff(digest: dict[str, Any], *, handoff_path: Path | None = None) -> Path:
    """Append (idempotent on same (date, run_id)) to CONDUCTOR_HANDOFF.md."""
    path = handoff_path or HANDOFF_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    line = _handoff_line(digest)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
    else:
        existing = (
            "# CONDUCTOR_HANDOFF — Pearl_Conductor cross-session continuity\n\n"
            "One line per daily digest. Schema:\n"
            "`day | run_id | succeeded | failed | pending | spend | cap_remaining | eta`\n\n"
        )
    # Idempotency key: (day, run_id)
    key = f"{digest['day_window_utc']} | run_id={digest['run_id']} |"
    lines = existing.splitlines(keepends=True)
    kept = [ln for ln in lines if not ln.startswith(key)]
    new_text = "".join(kept)
    if not new_text.endswith("\n"):
        new_text += "\n"
    new_text += line
    path.write_text(new_text, encoding="utf-8")
    return path


def write_digest(
    run_id: str,
    *,
    date: str | None = None,
    output_dir: Path | None = None,
    checkpoint_root: Path | None = None,
    ledger_path: Path | None = None,
    handoff_path: Path | None = None,
    cap_usd: float = DEFAULT_CAP_USD,
) -> Path:
    digest = compute_digest(
        run_id,
        date=date,
        checkpoint_root=checkpoint_root,
        ledger_path=ledger_path,
        cap_usd=cap_usd,
    )
    out_dir = output_dir or COORDINATION_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"conductor_v3_daily_digest_{digest['day_window_utc']}.md"
    out_path.write_text(digest_to_markdown(digest), encoding="utf-8")
    append_handoff(digest, handoff_path=handoff_path)
    return out_path


def _cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="V1.1 conductor v3 daily digest")
    p.add_argument("--run-id", required=True)
    p.add_argument("--date", default=None, help="YYYY-MM-DD; default today UTC")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--cap-usd", type=float, default=DEFAULT_CAP_USD)
    p.add_argument("--print-json", action="store_true")
    args = p.parse_args(argv)
    digest = compute_digest(args.run_id, date=args.date, cap_usd=args.cap_usd)
    out_path = write_digest(
        args.run_id,
        date=args.date,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        cap_usd=args.cap_usd,
    )
    if args.print_json:
        json.dump(digest, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print(str(out_path))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli(sys.argv[1:]))
