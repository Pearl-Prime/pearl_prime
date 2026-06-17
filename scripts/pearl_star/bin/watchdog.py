#!/usr/bin/env python3
"""Pearl Star Job Queue V1 — stall/crash watchdog (Phase A).

Implements the stall-detection contract (spec §5.1-§5.3). Runs as
``pearl-star-watchdog.service`` on a 60 s tick (PS_WATCHDOG_TICK_S):

  * Reads every heartbeat journal in /run/pearl-star/heartbeat/*.jsonl.
  * For each ACTIVE job compares ``elapsed_s`` to ``stall_warn_at_s`` (2x
    expected) and ``stall_kill_at_s`` (3x expected).
  * Heartbeat silent > 90 s (PS_HEARTBEAT_SILENCE_KILL_S) => worker CRASHED =>
    skip WARN, go straight to KILL.
  * AUTO-KILL = SIGTERM -> 10 s grace -> SIGKILL -> verify VRAM reclaim ->
    drop a STALL_KILL / WORKER_CRASHED alert. (Requeue is Procrastinate's job
    via the task retry budget once the worker dies; the watchdog only kills +
    alerts in Phase A.)

Emits alerts via monitor.emit_alert(): STALL_WARN, STALL_KILL, WORKER_CRASHED,
VRAM_SATURATED (spec §5.4 alert types).

Tier policy: pure stdlib + nvidia-smi. No paid LLM API (CLAUDE.md).
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# monitor.py is deployed alongside this file (PS_HOME/app); import for alerts.
try:
    from monitor import emit_alert
except Exception:  # pragma: no cover - monitor optional in unit tests
    def emit_alert(alert_type: str, payload: dict) -> None:  # type: ignore
        print(f"[watchdog][alert:{alert_type}] {json.dumps(payload)}", file=sys.stderr)

HEARTBEAT_DIR = Path(os.environ.get("PS_HEARTBEAT_DIR", "/run/pearl-star/heartbeat"))
TICK_S = int(os.environ.get("PS_WATCHDOG_TICK_S", "60"))
SILENCE_KILL_S = int(os.environ.get("PS_HEARTBEAT_SILENCE_KILL_S", "90"))
SIGTERM_GRACE_S = int(os.environ.get("PS_SIGTERM_GRACE_S", "10"))
LOG = Path(os.environ.get("PS_LOG_DIR", "/var/log/pearl-star")) / "watchdog.log"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(msg: str) -> None:
    line = f"{_utc()} {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def _last_record(journal: Path) -> dict[str, Any] | None:
    """Return the last JSONL record in a heartbeat journal, or None."""
    try:
        last = None
        with journal.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    last = line
        return json.loads(last) if last else None
    except Exception:
        return None


def _pid_of(worker_id: str) -> int | None:
    """worker_id is '<host>-t2i-<pid>'. Extract the pid tail."""
    try:
        return int(worker_id.rsplit("-", 1)[1])
    except Exception:
        return None


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, not ours to signal


def _vram_used_mb() -> int | None:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip().splitlines()
        return int(out[0].strip())
    except Exception:
        return None


def _auto_kill(worker_id: str, pid: int, reason: str, rec: dict) -> None:
    """SIGTERM -> grace -> SIGKILL -> verify VRAM reclaim (spec §5.2)."""
    _log(f"AUTO-KILL worker={worker_id} pid={pid} reason={reason}")
    emit_alert("STALL_KILL" if reason.startswith("stall") else "WORKER_CRASHED",
               {"worker_id": worker_id, "pid": pid, "reason": reason,
                "job_id": rec.get("job_id"), "elapsed_s": rec.get("elapsed_s")})
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        _log(f"  pid {pid} already gone before SIGTERM")
        return
    # grace
    deadline = time.monotonic() + SIGTERM_GRACE_S
    while time.monotonic() < deadline:
        if not _alive(pid):
            break
        time.sleep(0.5)
    if _alive(pid):
        _log(f"  grace expired; SIGKILL pid {pid}")
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    # verify VRAM reclaim within 30 s (spec §13 criterion 4)
    base_deadline = time.monotonic() + 30
    reclaimed = False
    while time.monotonic() < base_deadline:
        used = _vram_used_mb()
        if used is not None and used < 2000:  # near-baseline for a 16GB card at idle
            reclaimed = True
            break
        time.sleep(2)
    _log(f"  VRAM reclaim {'OK' if reclaimed else 'NOT-CONFIRMED'} "
         f"(used={_vram_used_mb()} MB)")
    # Clean the stale journal so we don't re-kill a recycled pid.
    try:
        (HEARTBEAT_DIR / f"{worker_id}.jsonl").unlink(missing_ok=True)
    except Exception:
        pass


def check_once() -> None:
    """One watchdog pass over all heartbeat journals."""
    if not HEARTBEAT_DIR.exists():
        return
    now = time.time()
    for journal in sorted(HEARTBEAT_DIR.glob("*.jsonl")):
        rec = _last_record(journal)
        if not rec:
            continue
        worker_id = rec.get("worker_id") or journal.stem
        phase = rec.get("phase", "")
        if phase in ("done",):
            continue  # finished cleanly
        pid = _pid_of(worker_id)

        # --- crash detection: heartbeat silence (spec §5.2) ----------------
        try:
            ts = datetime.fromisoformat(rec["ts"]).timestamp()
        except Exception:
            ts = journal.stat().st_mtime
        silent_s = now - ts
        if silent_s > SILENCE_KILL_S:
            if pid and _alive(pid):
                _auto_kill(worker_id, pid,
                           f"crashed:heartbeat_silent_{int(silent_s)}s", rec)
            else:
                _log(f"WORKER_CRASHED worker={worker_id} silent={int(silent_s)}s "
                     "(process already dead; Procrastinate retry will re-dispatch)")
                emit_alert("WORKER_CRASHED",
                           {"worker_id": worker_id, "job_id": rec.get("job_id"),
                            "silent_s": int(silent_s)})
                try:
                    journal.unlink(missing_ok=True)
                except Exception:
                    pass
            continue

        # --- stall detection: elapsed vs 2x / 3x thresholds (spec §5.2) ----
        elapsed = float(rec.get("elapsed_s") or 0)
        warn_at = float(rec.get("stall_warn_at_s") or 0)
        kill_at = float(rec.get("stall_kill_at_s") or 0)
        if kill_at and elapsed >= kill_at:
            if pid:
                _auto_kill(worker_id, pid,
                           f"stall:elapsed_{int(elapsed)}s>=kill_{int(kill_at)}s", rec)
        elif warn_at and elapsed >= warn_at:
            _log(f"STALL_WARN worker={worker_id} job={rec.get('job_id')} "
                 f"elapsed={elapsed}s warn_at={warn_at}s")
            emit_alert("STALL_WARN",
                       {"worker_id": worker_id, "job_id": rec.get("job_id"),
                        "elapsed_s": elapsed, "warn_at_s": warn_at})

        # --- VRAM saturation note (spec §5.4) ------------------------------
        free = rec.get("vram_free_mb")
        if isinstance(free, int) and free < 512:
            emit_alert("VRAM_SATURATED",
                       {"worker_id": worker_id, "vram_free_mb": free})


def main() -> int:
    once = "--once" in sys.argv
    _log(f"watchdog start tick={TICK_S}s silence_kill={SILENCE_KILL_S}s "
         f"grace={SIGTERM_GRACE_S}s dir={HEARTBEAT_DIR} once={once}")
    if once:
        check_once()
        return 0
    while True:
        try:
            check_once()
        except Exception as exc:  # never let the watchdog die silently
            _log(f"watchdog pass error: {exc!r}")
        time.sleep(TICK_S)


if __name__ == "__main__":
    raise SystemExit(main())
