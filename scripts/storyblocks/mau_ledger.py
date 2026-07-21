"""MAU ledger — downloads only, hard cap 104 (Q-SB-01 / Q-SB-PP).

Ledger key: (year_month_utc, anonymized_user_id).
Search queries must never touch this ledger.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.storyblocks.exceptions import StoryblocksMauCapError
from scripts.storyblocks.identity import anonymize_user_id

logger = logging.getLogger(__name__)

MAU_HARD_CAP = 104
WARN_THRESHOLDS = (80, 100)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER_PATH = REPO_ROOT / "artifacts" / "storyblocks" / "mau_ledger.jsonl"


def utc_year_month(now: datetime | None = None) -> str:
    dt = now or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m")


@dataclass(frozen=True)
class MauReserveResult:
    year_month: str
    user_id: str
    brand_id: str
    locale: str
    was_new: bool
    distinct_count: int
    warnings: tuple[int, ...]


class MauLedger:
    """JSONL + in-memory index with file lock for race-safe reserve."""

    def __init__(self, path: Path | None = None, hard_cap: int = MAU_HARD_CAP) -> None:
        self.path = path or Path(os.environ.get("STORYBLOCKS_MAU_LEDGER_PATH", str(DEFAULT_LEDGER_PATH)))
        self.hard_cap = hard_cap
        self._lock = threading.Lock()
        self._lock_path = self.path.with_suffix(self.path.suffix + ".lock")

    def _ensure_parent(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load_month_ids(self, year_month: str) -> set[str]:
        ids: set[str] = set()
        if not self.path.exists():
            return ids
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("year_month") == year_month and row.get("user_id"):
                    ids.add(str(row["user_id"]))
        return ids

    def _append(self, row: dict[str, Any]) -> None:
        self._ensure_parent()
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def distinct_count(self, year_month: str | None = None) -> int:
        ym = year_month or utc_year_month()
        with self._lock:
            return len(self._load_month_ids(ym))

    def reserve_or_block(
        self,
        brand_id: str,
        locale: str,
        *,
        now: datetime | None = None,
    ) -> MauReserveResult:
        """Reserve download identity for the UTC month or hard-block at 105th."""
        user_id = anonymize_user_id(brand_id, locale)
        year_month = utc_year_month(now)
        with self._lock:
            self._ensure_parent()
            # Simple exclusive lock file for cross-process safety on one host.
            self._lock_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._lock_path, "a+", encoding="utf-8") as lock_fh:
                try:
                    import fcntl

                    fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
                except (ImportError, OSError):
                    pass  # best-effort on platforms without fcntl
                existing = self._load_month_ids(year_month)
                if user_id in existing:
                    return MauReserveResult(
                        year_month=year_month,
                        user_id=user_id,
                        brand_id=brand_id,
                        locale=locale,
                        was_new=False,
                        distinct_count=len(existing),
                        warnings=(),
                    )
                if len(existing) >= self.hard_cap:
                    logger.warning(
                        "storyblocks.mau.cap_blocked year_month=%s count=%s brand=%s",
                        year_month,
                        len(existing),
                        brand_id,
                    )
                    raise StoryblocksMauCapError(
                        f"Storyblocks MAU hard cap ({self.hard_cap}) reached for "
                        f"{year_month}; refusing new download identity for "
                        f"{brand_id}:{locale}"
                    )
                row = {
                    "year_month": year_month,
                    "user_id": user_id,
                    "brand_id": brand_id,
                    "locale": locale,
                    "first_download_at": (now or datetime.now(timezone.utc)).isoformat(),
                }
                self._append(row)
                new_count = len(existing) + 1
                warnings = tuple(t for t in WARN_THRESHOLDS if new_count == t)
                for thr in warnings:
                    logger.warning(
                        "storyblocks.mau.warning year_month=%s count=%s threshold=%s",
                        year_month,
                        new_count,
                        thr,
                    )
                return MauReserveResult(
                    year_month=year_month,
                    user_id=user_id,
                    brand_id=brand_id,
                    locale=locale,
                    was_new=True,
                    distinct_count=new_count,
                    warnings=warnings,
                )


default_mau_ledger = MauLedger()
