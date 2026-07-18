#!/usr/bin/env python3
"""Pearl Star Job Queue V1 — operator-alert emitter + periodic monitor.

Two roles (spec §5.4):

1. ``emit_alert(type, payload)`` — file-drop alert helper imported by the
   watchdog and workers. Writes one JSONL line to
   ``<PS_ALERT_DIR>/<UTC>_<type>.jsonl``. Alert types (spec §5.4):
   STALL_WARN, STALL_KILL, WORKER_CRASHED, DEAD_LETTER, QUEUE_DEPTH_HIGH,
   VRAM_SATURATED, BROKER_HEARTBEAT_MISS.

2. ``pearl-star-monitor.service`` main loop — every PS_WATCHDOG_TICK_S polls
   queue depth (Postgres) + GPU (nvidia-smi) and emits QUEUE_DEPTH_HIGH /
   VRAM_SATURATED / BROKER_HEARTBEAT_MISS when thresholds trip. This is the
   light, always-on health sampler distinct from the per-job watchdog.

Tier policy: stdlib + psycopg + nvidia-smi. No paid LLM API (CLAUDE.md).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALERT_DIR = Path(os.environ.get("PS_ALERT_DIR", "/var/lib/pearl-star/operator_alerts"))
TICK_S = int(os.environ.get("PS_WATCHDOG_TICK_S", "60"))
QUEUE_DEPTH_HIGH = int(os.environ.get("PS_QUEUE_DEPTH_HIGH", "200"))
VRAM_FREE_FLOOR_MB = int(os.environ.get("PS_VRAM_FREE_FLOOR_MB", "512"))
DSN = os.environ.get("PS_QUEUE_DSN", "")
SCHEMA = os.environ.get("PS_PG_SCHEMA", "pearl_star_queue")
LOG = Path(os.environ.get("PS_LOG_DIR", "/var/log/pearl-star")) / "monitor.log"

VALID_ALERTS = {
    "STALL_WARN", "STALL_KILL", "WORKER_CRASHED", "DEAD_LETTER",
    "QUEUE_DEPTH_HIGH", "VRAM_SATURATED", "BROKER_HEARTBEAT_MISS",
}


def _utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def emit_alert(alert_type: str, payload: dict[str, Any]) -> Path:
    """Drop a single operator alert as JSONL (spec §5.4). Returns the path."""
    if alert_type not in VALID_ALERTS:
        raise ValueError(f"unknown alert type {alert_type!r}; expected one of {sorted(VALID_ALERTS)}")
    ALERT_DIR.mkdir(parents=True, exist_ok=True)
    path = ALERT_DIR / f"{_utc_compact()}_{alert_type}.jsonl"
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "type": alert_type, **payload}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return path


def _log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def _vram() -> tuple[int | None, int | None]:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip().splitlines()
        used, free = (int(x.strip()) for x in out[0].split(","))
        return used, free
    except Exception:
        return None, None


def _queue_depth() -> int | None:
    """Count pending+doing Procrastinate jobs. Also our broker liveness probe."""
    if not DSN:
        return None
    try:
        import psycopg
        with psycopg.connect(DSN, connect_timeout=5) as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT count(*) FROM {SCHEMA}.procrastinate_jobs "
                "WHERE status IN ('todo','doing')"
            )
            return int(cur.fetchone()[0])
    except Exception as exc:
        emit_alert("BROKER_HEARTBEAT_MISS", {"error": str(exc)[:300]})
        _log(f"BROKER_HEARTBEAT_MISS {exc!r}")
        return None


def check_once() -> None:
    depth = _queue_depth()
    if depth is not None and depth >= QUEUE_DEPTH_HIGH:
        emit_alert("QUEUE_DEPTH_HIGH", {"depth": depth, "threshold": QUEUE_DEPTH_HIGH})
        _log(f"QUEUE_DEPTH_HIGH depth={depth}")
    used, free = _vram()
    if free is not None and free < VRAM_FREE_FLOOR_MB:
        emit_alert("VRAM_SATURATED", {"vram_used_mb": used, "vram_free_mb": free})
        _log(f"VRAM_SATURATED free={free}MB")


def main() -> int:
    if "--once" in sys.argv:
        check_once()
        return 0
    _log(f"monitor start tick={TICK_S}s depth_high={QUEUE_DEPTH_HIGH} "
         f"vram_floor={VRAM_FREE_FLOOR_MB}MB")
    while True:
        try:
            check_once()
        except Exception as exc:
            _log(f"monitor pass error: {exc!r}")
        time.sleep(TICK_S)


if __name__ == "__main__":
    raise SystemExit(main())
