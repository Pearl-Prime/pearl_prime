"""Cross-queue GPU-heavy lock (t2i + llm + external Ollama lanes).

Procrastinate per-queue concurrency=1 does NOT serialize t2i vs llm vs direct
Ollama — they fight for the same 16 GB VRAM. This module implements:

1. **gpu_lane sentinel** — operator priority (``pscli gpu-acquire cjk`` blocks t2i
   until ``pscli gpu-release``). OPD-20260629-003 Order A.
2. **fcntl flock** — short-lived exclusive GPU work inside workers (spec §4.7).

Lock paths under ``${PS_LIB_DIR}`` (default ``/var/lib/pearl-star/``).
"""

from __future__ import annotations

import fcntl
import json
import os
import socket
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

LIB_DIR = Path(os.environ.get("PS_LIB_DIR", "/var/lib/pearl-star"))
LOCK_PATH = LIB_DIR / "gpu_heavy.lock"
LANE_PATH = LIB_DIR / "gpu_lane"
DEFAULT_WAIT_S = float(os.environ.get("PS_GPU_HEAVY_WAIT_S", "300"))


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def lock_metadata(holder: str, *, note: str = "") -> dict[str, Any]:
    return {
        "holder": holder,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "since": _utc(),
        "note": note,
    }


def read_gpu_lane() -> str | None:
    if not LANE_PATH.is_file():
        return None
    try:
        text = LANE_PATH.read_text(encoding="utf-8").strip()
        if not text:
            return None
        if text.startswith("{"):
            data = json.loads(text)
            return str(data.get("holder") or "") or None
        return text
    except (OSError, json.JSONDecodeError):
        return None


def set_gpu_lane(lane: str, *, note: str = "") -> None:
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    meta = lock_metadata(lane, note=note)
    LANE_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def clear_gpu_lane() -> None:
    LANE_PATH.unlink(missing_ok=True)
    LOCK_PATH.unlink(missing_ok=True)


def read_lock_state() -> dict[str, Any] | None:
    if not LOCK_PATH.is_file():
        return None
    try:
        return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"holder": "unknown", "raw": True}


def assert_lane_allows(worker_lane: str) -> None:
    """Raise RuntimeError when an operator gpu_lane blocks this worker."""
    active = read_gpu_lane()
    if not active:
        return
    if active == worker_lane:
        return
    raise RuntimeError(
        f"gpu_lane={active!r} blocks {worker_lane!r} (pscli gpu-release to clear)"
    )


@contextmanager
def gpu_heavy_lock(
    holder: str,
    *,
    wait_s: float = DEFAULT_WAIT_S,
    note: str = "",
    worker_lane: str | None = None,
) -> Iterator[None]:
    """Acquire lane + flock before GPU work; release flock on exit."""
    if worker_lane:
        assert_lane_allows(worker_lane)
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + max(0.0, wait_s)
    fd = os.open(str(LOCK_PATH), os.O_RDWR | os.O_CREAT, 0o664)
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    meta = read_lock_state()
                    who = (meta or {}).get("holder", "?")
                    raise TimeoutError(
                        f"gpu_heavy flock held by {who!r} after {wait_s}s "
                        f"(wanted {holder!r})"
                    )
                time.sleep(2.0)
        payload = json.dumps(lock_metadata(holder, note=note), indent=2)
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, payload.encode("utf-8"))
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
