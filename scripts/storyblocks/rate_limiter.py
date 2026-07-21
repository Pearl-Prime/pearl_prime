"""Proactive Storyblocks rate limiter (§2.1 / §2.2).

Caps (aggregate process-local):
  - search: 600 / minute
  - download: 120 / minute
"""

from __future__ import annotations

import threading
import time
from collections import deque

from scripts.storyblocks.exceptions import StoryblocksRateLimitError

SEARCH_CAP_PER_MIN = 600
DOWNLOAD_CAP_PER_MIN = 120
WINDOW_SEC = 60.0


class SlidingWindowRateLimiter:
    """Thread-safe sliding-window limiter (in-process)."""

    def __init__(self, search_cap: int = SEARCH_CAP_PER_MIN, download_cap: int = DOWNLOAD_CAP_PER_MIN) -> None:
        self.search_cap = search_cap
        self.download_cap = download_cap
        self._search: deque[float] = deque()
        self._download: deque[float] = deque()
        self._lock = threading.Lock()

    def _prune(self, q: deque[float], now: float) -> None:
        cutoff = now - WINDOW_SEC
        while q and q[0] < cutoff:
            q.popleft()

    def acquire(self, kind: str, *, now: float | None = None) -> None:
        """Reserve a slot or raise StoryblocksRateLimitError."""
        if kind not in ("search", "download"):
            raise ValueError(f"unknown rate-limit kind: {kind}")
        ts = time.time() if now is None else now
        with self._lock:
            q = self._search if kind == "search" else self._download
            cap = self.search_cap if kind == "search" else self.download_cap
            self._prune(q, ts)
            if len(q) >= cap:
                raise StoryblocksRateLimitError(
                    f"Storyblocks {kind} rate limit exceeded ({cap}/{int(WINDOW_SEC)}s)"
                )
            q.append(ts)

    def reset(self) -> None:
        with self._lock:
            self._search.clear()
            self._download.clear()


# Process singleton used by API client unless injected.
default_rate_limiter = SlidingWindowRateLimiter()
