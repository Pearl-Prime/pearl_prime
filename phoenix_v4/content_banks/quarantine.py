from __future__ import annotations

import re
from typing import Any, List, Optional, Tuple

from phoenix_v4.content_banks.loader import ContentBankRegistry, get_content_bank_registry


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _topic_blocked(entry: dict[str, Any], topic_id: str) -> bool:
    t = (topic_id or "").strip()
    blocked = entry.get("blocked_in_plans_with_topics") or []
    return bool(t and t in blocked)


def _frame_allowed_for_quarantine(entry: dict[str, Any], frame: str) -> bool:
    """Quarantine applies (content should be rewritten) when frame is NOT in allowed list."""
    allowed = entry.get("allowed_in_plans_with_frames") or []
    f = (frame or "").strip().lower()
    if not allowed:
        return False
    return any(a and str(a).lower() in f for a in allowed)


def _pick_secular_replacement(
    registry: ContentBankRegistry,
    *,
    bank_key: str,
    slot_type: str,
    topic_id: str,
    persona_id: str,
    frame: str,
    runtime_format_id: str,
    seed: str,
) -> Optional[str]:
    from phoenix_v4.content_banks.selector import (
        FragmentContext,
        _frame_ok,
        _persona_ok,
        _runtime_ok,
        _topic_ok,
        _stable_pick_index,
    )

    pool: List[dict[str, Any]] = []
    for rec in registry.secular_replacements:
        if str(rec.get("replacement_bank_key") or "") != bank_key:
            continue
        if slot_type and str(rec.get("slot_type") or "").upper() != slot_type.upper():
            continue
        if not _topic_ok(rec, topic_id):
            continue
        if not _persona_ok(rec, persona_id):
            continue
        if not _frame_ok(rec, frame):
            continue
        if not _runtime_ok(rec, runtime_format_id):
            continue
        pool.append(rec)
    if not pool:
        return None
    pool.sort(key=lambda r: str(r.get("replacement_id") or r.get("variant_id") or ""))
    idx = _stable_pick_index(seed, len(pool), offset=0)
    return str(pool[idx].get("body") or "").strip()


def apply_doctrine_quarantine(
    text: str,
    *,
    topic_id: str,
    persona_id: str,
    frame: str,
    runtime_format_id: str,
    seed: str,
    registry: Optional[ContentBankRegistry] = None,
) -> Tuple[str, List[dict[str, Any]]]:
    """
    Strip or replace quarantined registry doctrine when topic/frame rules say so.
    Returns (new_text, audit_events).
    """
    reg = registry or get_content_bank_registry()
    if not text.strip() or not reg.quarantine_entries:
        return text, []

    events: List[dict[str, Any]] = []
    out = text
    # Longest original_text first reduces partial overshadowing
    entries = sorted(
        reg.quarantine_entries,
        key=lambda e: len(_norm_ws(str(e.get("original_text") or ""))),
        reverse=True,
    )
    for entry in entries:
        raw = str(entry.get("original_text") or "")
        needle = _norm_ws(raw)
        if len(needle) < 24:
            continue
        if not _topic_blocked(entry, topic_id):
            continue
        if _frame_allowed_for_quarantine(entry, frame):
            continue

        norm_out = _norm_ws(out)
        if needle not in norm_out:
            continue

        bank_key = str(entry.get("replacement_bank_key") or "")
        replacement = _pick_secular_replacement(
            reg,
            bank_key=bank_key,
            slot_type="MECHANISM_BRIDGE",
            topic_id=topic_id,
            persona_id=persona_id,
            frame=frame,
            runtime_format_id=runtime_format_id,
            seed=f"{seed}:{entry.get('quarantine_id')}",
        )
        if not replacement:
            replacement = ""
        # Replace first occurrence of whitespace-normalized substring via regex flex space
        parts = needle.split()
        if len(parts) < 6:
            continue
        pattern = r"\s+".join(re.escape(p) for p in parts)
        new_out, n = re.subn(pattern, replacement if replacement else "", out, count=1, flags=re.IGNORECASE)
        if n:
            events.append(
                {
                    "quarantine_id": entry.get("quarantine_id"),
                    "replacement_bank_key": bank_key,
                    "replaced_chars": len(needle),
                    "had_replacement_body": bool(replacement),
                }
            )
            out = new_out

    return out, events
