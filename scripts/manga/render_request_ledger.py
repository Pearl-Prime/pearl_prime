#!/usr/bin/env python3
"""Durable operator-facing ledger for manga render requests.

Procrastinate persists *jobs*. This ledger persists the operator's *requested
render set* so unfinished pictures do not disappear after a single enqueue
attempt. A request stays in the ledger until it is either:

1. backed by a usable local PNG, or
2. explicitly archived by the operator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO / "artifacts" / "qa" / "manga_render_queue" / "request_ledger.json"
DEFAULT_LEDGER_ENV = "PHOENIX_MANGA_RENDER_REQUEST_LEDGER_PATH"
SCHEMA_VERSION = "manga_render_request_ledger_v1"
MIN_REAL_BYTES = 50_000

REQUEUEABLE_STATES = frozenset(
    {
        "requested",
        "failed",
        "blob_failed",
        "undersized",
        "missing_output",
        "stale_request",
        "no_job_recorded",
    }
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _prompt_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def default_ledger_path() -> Path:
    override = (os.environ.get(DEFAULT_LEDGER_ENV) or "").strip()
    if override:
        return Path(override).expanduser()
    return DEFAULT_LEDGER


def load_ledger(path: Path | None = None) -> dict[str, Any]:
    target = path or default_ledger_path()
    if not target.is_file():
        return {
            "schema_version": SCHEMA_VERSION,
            "updated_at": _utc_now(),
            "requests": {},
        }
    doc = json.loads(target.read_text(encoding="utf-8"))
    doc.setdefault("schema_version", SCHEMA_VERSION)
    doc.setdefault("updated_at", _utc_now())
    doc.setdefault("requests", {})
    return doc


def save_ledger(doc: dict[str, Any], path: Path | None = None) -> Path:
    target = path or default_ledger_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    doc["updated_at"] = _utc_now()
    target.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def make_request_id(*, series_key: str, layer_id: str, layer_class: str) -> str:
    return f"{series_key}:{layer_class}:{layer_id}"


def build_request_spec(
    *,
    campaign_id: str,
    series_key: str,
    series_id: str,
    layer_id: str,
    layer_class: str,
    out_path: Path,
    prompt: str,
    negative: str,
    width: int,
    height: int,
    task: str,
) -> dict[str, Any]:
    try:
        rel = str(out_path.resolve().relative_to(REPO))
    except ValueError:
        rel = str(out_path.resolve())
    return {
        "request_id": make_request_id(
            series_key=series_key,
            layer_id=layer_id,
            layer_class=layer_class,
        ),
        "campaign_id": campaign_id,
        "series_key": series_key,
        "series_id": series_id,
        "layer_id": layer_id,
        "layer_class": layer_class,
        "out_path": rel,
        "prompt_sha256": _prompt_sha(prompt),
        "prompt_chars": len(prompt),
        "negative_sha256": _prompt_sha(negative),
        "width": int(width),
        "height": int(height),
        "task": task,
        "desired_state": "usable_png",
    }


def upsert_requests(
    specs: list[dict[str, Any]],
    *,
    ledger_path: Path | None = None,
) -> tuple[dict[str, Any], list[str]]:
    doc = load_ledger(ledger_path)
    requests = doc["requests"]
    changed: list[str] = []
    now = _utc_now()
    for spec in specs:
        rid = spec["request_id"]
        existing = requests.get(rid)
        if existing is None:
            requests[rid] = {
                **spec,
                "created_at": now,
                "updated_at": now,
                "status": "requested",
                "archived": False,
                "job_history": [],
                "latest_job_id": None,
                "latest_queue_status": None,
                "last_error": None,
            }
            changed.append(rid)
            continue
        prompt_changed = existing.get("prompt_sha256") != spec["prompt_sha256"]
        for key, value in spec.items():
            existing[key] = value
        existing["updated_at"] = now
        existing.setdefault("job_history", [])
        existing.setdefault("archived", False)
        if prompt_changed and not existing.get("archived", False):
            existing["status"] = "stale_request"
            existing["last_error"] = "prompt changed; rerender required"
            changed.append(rid)
    save_ledger(doc, ledger_path)
    return doc, changed


def record_enqueue(
    request_id: str,
    *,
    job_id: int | str,
    via: str,
    task: str,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    doc = load_ledger(ledger_path)
    requests = doc["requests"]
    req = requests[request_id]
    req["latest_job_id"] = int(job_id)
    req["latest_queue_status"] = "todo"
    req["status"] = "queued"
    req["last_error"] = None
    req.setdefault("job_history", []).append(
        {
            "job_id": int(job_id),
            "task": task,
            "via": via,
            "enqueued_at": _utc_now(),
        }
    )
    req["updated_at"] = _utc_now()
    save_ledger(doc, ledger_path)
    return req


def _safe_blob_check(path: Path) -> bool:
    from scripts.manga.bank_layer_blob_gate import is_blob_png

    return bool(is_blob_png(path))


def evaluate_output_state(out_path: Path) -> tuple[str, dict[str, Any]]:
    if not out_path.is_file():
        return "missing_output", {"exists": False}
    size = out_path.stat().st_size
    meta = {"exists": True, "bytes": size}
    if size < MIN_REAL_BYTES:
        return "undersized", meta
    try:
        if _safe_blob_check(out_path):
            return "blob_failed", meta
    except Exception as exc:  # pragma: no cover - defensive
        meta["blob_check_error"] = str(exc)
        return "present_unchecked", meta
    return "usable", meta


def fetch_queue_status_map(
    job_ids: list[int | str],
    *,
    ssh_host: str = "pearl_star",
) -> dict[int, str]:
    ids = sorted({int(j) for j in job_ids if str(j).strip()})
    if not ids:
        return {}

    py = (
        "import json, os, psycopg\n"
        f"ids = {ids!r}\n"
        "dsn = os.environ.get('PS_QUEUE_DSN', '')\n"
        "if not dsn:\n"
        "    print(json.dumps({'error': 'PS_QUEUE_DSN not set', 'statuses': {}}))\n"
        "    raise SystemExit(2)\n"
        "with psycopg.connect(dsn) as conn:\n"
        "    with conn.cursor() as cur:\n"
        "        cur.execute('SELECT id, status FROM procrastinate_jobs WHERE id = ANY(%s)', (ids,))\n"
        "        rows = {int(i): s for i, s in cur.fetchall()}\n"
        "print(json.dumps({'statuses': rows}))\n"
    )
    if os.environ.get("PS_QUEUE_DSN", "").strip():
        cmd = ["python3", "-c", py]
    else:
        remote = (
            "set -a; . /etc/pearl-star/queue.env 2>/dev/null; "
            f". {REPO}/.pearl_star_queue.env 2>/dev/null; set +a; "
            f"/opt/pearl-star/venv/bin/python -c {json.dumps(py)}"
        )
        cmd = ["ssh", "-o", "BatchMode=yes", ssh_host, remote]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "queue status query failed")
    payload = json.loads((proc.stdout or "").strip().splitlines()[-1])
    rows = payload.get("statuses") or {}
    return {int(k): str(v) for k, v in rows.items()}


def reconcile_requests(
    *,
    ledger_path: Path | None = None,
    queue_status_map: dict[int, str] | None = None,
) -> dict[str, Any]:
    doc = load_ledger(ledger_path)
    requests = doc["requests"]
    summary = Counter()
    for req in requests.values():
        if req.get("archived"):
            summary["archived"] += 1
            continue

        out_path = REPO / req["out_path"]
        local_state, meta = evaluate_output_state(out_path)
        latest_job_id = req.get("latest_job_id")
        queue_state = None
        if latest_job_id is not None and queue_status_map is not None:
            queue_state = queue_status_map.get(int(latest_job_id))
        if queue_state is not None:
            req["latest_queue_status"] = queue_state

        req["output_state"] = meta
        if local_state == "usable":
            req["status"] = "usable"
            req["last_error"] = None
            req["usable_at"] = req.get("usable_at") or _utc_now()
        elif local_state == "present_unchecked":
            req["status"] = "present_unchecked"
            req["last_error"] = meta.get("blob_check_error")
        elif queue_state in {"todo", "doing"}:
            req["status"] = "queued"
            req["last_error"] = local_state
        elif queue_state == "failed":
            req["status"] = "failed"
            req["last_error"] = local_state
        elif queue_state == "succeeded":
            req["status"] = local_state
            req["last_error"] = local_state
        elif latest_job_id is None:
            req["status"] = "requested"
            req["last_error"] = local_state
        else:
            req["status"] = local_state if local_state != "missing_output" else "no_job_recorded"
            req["last_error"] = local_state
        req["updated_at"] = _utc_now()
        summary[req["status"]] += 1

    save_ledger(doc, ledger_path)
    target = (ledger_path or default_ledger_path()).resolve()
    try:
        display = str(target.relative_to(REPO))
    except ValueError:
        display = str(target)
    return {
        "ledger_path": display,
        "counts": dict(summary),
        "requeueable_states": sorted(REQUEUEABLE_STATES),
    }


def request_ids_needing_enqueue(
    *,
    ledger_path: Path | None = None,
) -> set[str]:
    doc = load_ledger(ledger_path)
    out: set[str] = set()
    for rid, req in doc["requests"].items():
        if req.get("archived"):
            continue
        if req.get("status") in REQUEUEABLE_STATES:
            out.add(rid)
    return out


def archive_request(request_id: str, *, ledger_path: Path | None = None) -> dict[str, Any]:
    doc = load_ledger(ledger_path)
    req = doc["requests"][request_id]
    req["archived"] = True
    req["status"] = "archived"
    req["updated_at"] = _utc_now()
    save_ledger(doc, ledger_path)
    return req


def _cmd_summary(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger) if args.ledger else default_ledger_path()
    doc = load_ledger(ledger)
    counts = Counter()
    for req in doc["requests"].values():
        counts[req.get("status", "unknown")] += 1
    print(json.dumps({"ledger": str(ledger), "counts": dict(counts)}, indent=2))
    return 0


def _cmd_reconcile(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger) if args.ledger else default_ledger_path()
    doc = load_ledger(ledger)
    job_ids = [
        int(req["latest_job_id"])
        for req in doc["requests"].values()
        if req.get("latest_job_id") is not None and not req.get("archived")
    ]
    status_map = fetch_queue_status_map(job_ids, ssh_host=args.ssh_host) if job_ids else {}
    summary = reconcile_requests(ledger_path=ledger, queue_status_map=status_map)
    print(json.dumps(summary, indent=2))
    return 0


def _cmd_list_pending(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger) if args.ledger else default_ledger_path()
    doc = load_ledger(ledger)
    pending = [
        req for req in doc["requests"].values()
        if not req.get("archived") and req.get("status") in REQUEUEABLE_STATES
    ]
    print(json.dumps({"pending": pending}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default="", help="Override ledger path")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_summary = sub.add_parser("summary")
    p_summary.set_defaults(fn=_cmd_summary)

    p_reconcile = sub.add_parser("reconcile")
    p_reconcile.add_argument("--ssh-host", default="pearl_star")
    p_reconcile.set_defaults(fn=_cmd_reconcile)

    p_pending = sub.add_parser("list-pending")
    p_pending.set_defaults(fn=_cmd_list_pending)

    args = ap.parse_args(argv)
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
