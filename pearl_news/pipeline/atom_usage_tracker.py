"""
Pearl News deterministic-atom usage tracker — least-recently-used selector.

Operator directive 2026-05-17: "I want the article writer to vary the use of
the five atoms, the five variations per atom. Keep track. Use them so that
we have the fewest repeats."

Existing selector (deterministic_teacher_topic.py::_select_option):
    idx = _stable_index(f"{article_id}|{slot}|{teacher_id}|{topic}", len(candidates))
That's hash-deterministic per article_id, which produces *some* variety
across articles but DOES repeat the same option whenever the hash lands on
it again. With 5 options per slot, hash-only selection gives ~20% repeat
rate even if all 5 options are eligible.

This tracker adds state: a per-(teacher × topic × slot) ring buffer of
recently-used option_ids stored at:

    artifacts/pearl_news/atom_usage_log.json

Selector behavior change (when applied):

  1. Score each candidate by how recently it was used.
  2. Prefer options that have NEVER been used (cold-start). Tie-break by
     stable-index hash so behavior is still deterministic given the same
     log state + article_id.
  3. If every option has been used in the recent window, pick the
     least-recently-used one. Tie-break by stable-index hash.
  4. After the pick, append the chosen option_id to the log for that
     (teacher, topic, slot). Old entries roll off after RECENT_WINDOW
     selections per cell.

Log file format (JSON, one cell key per line if pretty-printed):

    {
      "ahjan|mental_health|hook_personal": ["hook_personal_03", "hook_personal_01"],
      "junko|climate|youth_somatic":       ["junko_climate_somatic_02"],
      ...
    }

Append order = most-recent-last. Ring length = RECENT_WINDOW (default 4).
With 5 options per slot, this guarantees that the next pick will be one
of the at least 1 options that hasn't been used in the last 4 articles
for that cell.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LOG_PATH = Path("artifacts/pearl_news/atom_usage_log.json")
RECENT_WINDOW = 4  # Number of recent picks to remember per cell. With 5
                   # options per slot, this keeps at least 1 always-unused.
_FILE_LOCK = threading.Lock()


def _cell_key(teacher_id: str, topic: str, slot: str) -> str:
    return f"{teacher_id}|{topic}|{slot}"


def _stable_index(seed_str: str, n: int) -> int:
    """Deterministic hash-based index in [0, n). Used as tie-breaker."""
    if n <= 0:
        return 0
    h = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
    return int(h, 16) % n


def _load_log(log_path: Path) -> dict[str, list[str]]:
    if not log_path.exists():
        return {}
    try:
        return json.loads(log_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        logger.warning("atom_usage_tracker: failed to parse %s: %s — starting fresh", log_path, exc)
        return {}


def _save_log(log: dict[str, list[str]], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Sort keys for stable diffs
    ordered = OrderedDict(sorted(log.items()))
    log_path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_least_recently_used(
    candidates: list[dict[str, Any]],
    *,
    teacher_id: str,
    topic: str,
    slot_name: str,
    article_id: str,
    log_path: Path | None = None,
    record_pick: bool = True,
    recent_window: int = RECENT_WINDOW,
) -> dict[str, Any]:
    """
    Pick one option from `candidates` with least-recently-used preference.

    `candidates`: list of option dicts, each must have an "id" key.
    `record_pick`: if True (default), append the chosen id to the usage log
                   under the (teacher, topic, slot) cell key.

    Returns the chosen option dict. Falls back to candidates[0] if the list
    is empty (shouldn't happen — caller should pre-filter).
    """
    if not candidates:
        return {}

    log_path = log_path or DEFAULT_LOG_PATH
    cell_key = _cell_key(teacher_id, topic, slot_name)

    with _FILE_LOCK:
        log = _load_log(log_path)
        recent = list(log.get(cell_key) or [])

    # Score each candidate by recency:
    #   never used → -1 (best)
    #   most recently used → recent.index(id) from the END (highest = oldest)
    # Tie-break by stable_index hash of (article_id|cell_key) over candidate position.
    def recency_score(opt_idx_id: tuple[int, str]) -> tuple[int, int]:
        _, opt_id = opt_idx_id
        if opt_id not in recent:
            return (-1, _stable_index(f"{article_id}|{cell_key}|{opt_id}", 1_000_000))
        # recent[-1] = most recent. We want LRU first.
        # distance from end: 0 = just used, len(recent)-1 = oldest in window
        distance_from_end = len(recent) - 1 - recent.index(opt_id)
        return (distance_from_end, _stable_index(f"{article_id}|{cell_key}|{opt_id}", 1_000_000))

    indexed = [(i, c.get("id") or f"_anon_{i}") for i, c in enumerate(candidates)]
    indexed.sort(key=lambda x: (-recency_score(x)[0], recency_score(x)[1]))
    # ↑ Most-recently-used first by score descending? No — we want LEAST recent.
    # Re-sort: smallest score (never-used = -1, then largest distance_from_end) wins.
    # Actually: -1 < 0 < 1 < 2 ..., so "smallest" = never used first.
    indexed.sort(key=lambda x: (recency_score(x)[0], recency_score(x)[1]))
    chosen_idx = indexed[0][0]
    chosen = candidates[chosen_idx]
    chosen_id = chosen.get("id") or f"_anon_{chosen_idx}"

    if record_pick:
        with _FILE_LOCK:
            log = _load_log(log_path)
            recent = list(log.get(cell_key) or [])
            # Remove existing entry of this id (we'll re-add at the end)
            recent = [x for x in recent if x != chosen_id]
            recent.append(chosen_id)
            # Trim to ring window
            if len(recent) > recent_window:
                recent = recent[-recent_window:]
            log[cell_key] = recent
            _save_log(log, log_path)

    return chosen


def reset_log(log_path: Path | None = None) -> None:
    """Wipe the usage log. Used by tests + when operator wants to re-baseline rotation."""
    log_path = log_path or DEFAULT_LOG_PATH
    if log_path.exists():
        log_path.unlink()


def get_cell_history(
    teacher_id: str, topic: str, slot_name: str,
    log_path: Path | None = None,
) -> list[str]:
    """Read-only view of recent option_ids picked for a (teacher, topic, slot) cell."""
    log_path = log_path or DEFAULT_LOG_PATH
    with _FILE_LOCK:
        log = _load_log(log_path)
    return list(log.get(_cell_key(teacher_id, topic, slot_name)) or [])
