from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

from phoenix_v4.content_banks.loader import ContentBankRegistry, get_content_bank_registry
from phoenix_v4.content_banks.session import ContentBankSession
from phoenix_v4.content_banks.variant_log import VariantSelectionLogger

_RUNTIME_ALIASES: dict[str, List[str]] = {
    "standard_book": ["standard_book", "standard_book_1h"],
    "short_book_30": ["short_book_30", "quick_book_30m"],
    "micro_book_15": ["micro_book_15", "quick_book_15m"],
    "micro_book_20": ["micro_book_20", "quick_book_30m"],
    "extended_book_2h": ["extended_book_2h", "deep_book_2h"],
    "deep_book_4h": ["deep_book_4h"],
    "deep_book_6h": ["deep_book_6h"],
}


def _runtime_candidates(req: str) -> List[str]:
    r = (req or "").strip()
    if not r:
        return []
    out = [r]
    out.extend(_RUNTIME_ALIASES.get(r, []))
    return list(dict.fromkeys(out))


def _frame_tags(frame: str) -> List[str]:
    f = (frame or "").strip().lower().replace("-", "_")
    tags: List[str] = ["secular"]
    if "somatic" in f:
        tags.append("nervous_system")
    if "clinical" in f:
        tags.append("clinical")
    if "buddhist" in f:
        tags.append("buddhist")
    if "contemplative" in f:
        tags.append("contemplative")
    if "workplace" in f or "work" in f:
        tags.append("workplace")
    return list(dict.fromkeys(tags))


def _topic_ok(rec: dict[str, Any], topic_id: str) -> bool:
    t = (topic_id or "").strip()
    allow = rec.get("topic_allowlist") or []
    block = rec.get("topic_blocklist") or []
    if block and t in block:
        return False
    if allow and t not in allow:
        return False
    return True


def _persona_ok(rec: dict[str, Any], persona_id: str) -> bool:
    p = (persona_id or "").strip()
    allow = rec.get("persona_allowlist") or []
    block = rec.get("persona_blocklist") or []
    if block and p in block:
        return False
    if allow and p not in allow:
        return False
    return True


def _frame_ok(rec: dict[str, Any], frame: str) -> bool:
    tags = _frame_tags(frame)
    allow = rec.get("frame_allowlist") or []
    block = rec.get("frame_blocklist") or []
    if block and any(x in block for x in tags):
        return False
    if allow and not any(x in allow for x in tags):
        return False
    return True


def _runtime_ok(rec: dict[str, Any], runtime_format_id: str) -> bool:
    allow = rec.get("runtime_allowlist") or []
    if not allow:
        return True
    opts = _runtime_candidates(runtime_format_id)
    return any(x in allow for x in opts)


def _mechanism_depth_ok(rec: dict[str, Any], target: Optional[int]) -> bool:
    if target is None:
        return True
    try:
        d = int(rec.get("mechanism_depth"))
    except (TypeError, ValueError):
        return False
    return d == int(target)


def _band_ok(rec: dict[str, Any], allowed_bands: Optional[set[int]]) -> bool:
    if not allowed_bands:
        return True
    try:
        b = int(rec.get("band"))
    except (TypeError, ValueError):
        return False
    return b in allowed_bands


def _locale_key_ok(rec: dict[str, Any], locale_var_key: str) -> bool:
    if rec.get("slot_type") != "LOCALE_NP":
        return True
    return str(rec.get("locale_var_key") or "") == locale_var_key


@dataclass
class FragmentContext:
    topic_id: str = ""
    persona_id: str = ""
    frame: str = "somatic_first"
    runtime_format_id: str = "standard_book"
    chapter_index: int = 0
    book_seed: str = "book"
    slot_key: str = ""
    mechanism_depth: Optional[int] = None
    allowed_bands: Optional[set[int]] = None


def _stable_pick_index(seed: str, n: int, offset: int = 0) -> int:
    if n <= 0:
        return 0
    digest = hashlib.sha256(f"{seed}:{offset}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % n


def _collect_candidates(
    registry: ContentBankRegistry,
    bank_stems: Sequence[str],
    slot_type: str,
    ctx: FragmentContext,
    *,
    locale_var_key: str = "",
) -> List[dict[str, Any]]:
    cands: List[dict[str, Any]] = []
    for rec in registry.variants_for_stems(list(bank_stems)):
        if str(rec.get("slot_type") or "").upper() != slot_type.upper():
            continue
        if not _topic_ok(rec, ctx.topic_id):
            continue
        if not _persona_ok(rec, ctx.persona_id):
            continue
        if not _frame_ok(rec, ctx.frame):
            continue
        if not _runtime_ok(rec, ctx.runtime_format_id):
            continue
        if not _mechanism_depth_ok(rec, ctx.mechanism_depth):
            continue
        if not _band_ok(rec, ctx.allowed_bands):
            continue
        if locale_var_key and not _locale_key_ok(rec, locale_var_key):
            continue
        cands.append(rec)
    cands.sort(key=lambda r: str(r.get("variant_id") or ""))
    return cands


def _log_record(
    *,
    chapter_index: int,
    slot_key: str,
    bank_stem: str,
    variant: dict[str, Any],
    filters: str,
    logger: Optional[VariantSelectionLogger],
) -> None:
    if not logger or not logger.enabled():
        return
    logger.append(
        {
            "chapter_index": chapter_index,
            "slot_key": slot_key,
            "bank_id": bank_stem,
            "variant_id": variant.get("variant_id"),
            "collision_family": variant.get("collision_family"),
            "slot_type": variant.get("slot_type"),
            "filters_matched": filters,
        }
    )


def select_fragment(
    registry: ContentBankRegistry,
    *,
    bank_stems: Sequence[str],
    slot_type: str,
    ctx: FragmentContext,
    session: Optional[ContentBankSession] = None,
    logger: Optional[VariantSelectionLogger] = None,
    role: str = "",
    locale_var_key: str = "",
) -> Tuple[str, dict[str, Any]]:
    """Return (body, metadata) for first eligible variant after deterministic shuffle."""
    cands = _collect_candidates(
        registry,
        bank_stems,
        slot_type,
        ctx,
        locale_var_key=locale_var_key,
    )
    if not cands:
        return "", {"status": "no_match", "slot_type": slot_type, "banks": list(bank_stems)}

    bank_tag = ",".join(bank_stems)
    seed = f"{ctx.book_seed}|{ctx.slot_key or role}|{slot_type}|{bank_tag}|ch{ctx.chapter_index}"

    def try_pick(pool: List[dict[str, Any]], use_session: bool) -> Optional[dict[str, Any]]:
        n = len(pool)
        for attempt in range(n):
            idx = _stable_pick_index(seed, n, offset=attempt)
            cand = pool[idx]
            vid = str(cand.get("variant_id") or "")
            cf = str(cand.get("collision_family") or "")
            if use_session and session:
                if role == "flow_glue" and not session.flow_glue_ok(ctx.chapter_index, vid, cf):
                    continue
                if role == "scene_anchor" and not session.scene_anchor_ok(vid):
                    continue
            return cand
        return None

    cand: Optional[dict[str, Any]] = None
    if session and role in ("flow_glue", "scene_anchor"):
        cand = try_pick(cands, True)
    if cand is None:
        cand = try_pick(cands, False)
    if cand is None:
        idx = _stable_pick_index(seed, len(cands), offset=0)
        cand = cands[idx]

    if role == "flow_glue" and session:
        session.record_flow_glue(
            ctx.chapter_index,
            str(cand.get("variant_id") or ""),
            str(cand.get("collision_family") or ""),
        )
    if role == "scene_anchor" and session:
        session.record_scene_anchor(str(cand.get("variant_id") or ""))

    stem_used = bank_stems[0] if len(bank_stems) == 1 else bank_tag
    _log_record(
        chapter_index=ctx.chapter_index,
        slot_key=ctx.slot_key or role,
        bank_stem=stem_used,
        variant=cand,
        filters=f"topic={ctx.topic_id};persona={ctx.persona_id};frame={ctx.frame};runtime={ctx.runtime_format_id}",
        logger=logger,
    )

    body = str(cand.get("body") or "").strip()
    meta = {
        "status": "ok",
        "variant_id": cand.get("variant_id"),
        "collision_family": cand.get("collision_family"),
        "bank_stems": list(bank_stems),
    }
    return body, meta


def select_locale_np(
    registry: ContentBankRegistry,
    *,
    locale_var_key: str,
    chapter_index: int,
    book_seed: str,
    plan: Optional[dict] = None,
) -> str:
    ctx = FragmentContext(
        chapter_index=chapter_index,
        book_seed=book_seed,
        slot_key=f"locale_var:{locale_var_key}",
        runtime_format_id=str((plan or {}).get("runtime_format_id") or (plan or {}).get("book_spec", {}).get("runtime_format_id") or "standard_book"),
    )
    from phoenix_v4.content_banks.session import variant_logger_from_plan

    body, _ = select_fragment(
        registry,
        bank_stems=["global_locale_np_bank"],
        slot_type="LOCALE_NP",
        ctx=ctx,
        session=None,
        logger=variant_logger_from_plan(plan),
        role="locale_np",
        locale_var_key=locale_var_key,
    )
    return body


def select_scene_anchor_replace(
    registry: ContentBankRegistry,
    *,
    chapter_index: int,
    book_seed: str,
    plan: Optional[dict] = None,
) -> str:
    frame = str((plan or {}).get("frame") or (plan or {}).get("spine_context", {}).get("frame") or "somatic_first")
    runtime = str(
        (plan or {}).get("runtime_format_id")
        or (plan or {}).get("book_spec", {}).get("runtime_format_id")
        or "standard_book"
    )
    ctx = FragmentContext(
        frame=frame,
        runtime_format_id=runtime,
        chapter_index=chapter_index,
        book_seed=book_seed,
        slot_key="normalize_generic_scene_lighting",
    )
    from phoenix_v4.content_banks.session import get_or_create_bank_session, variant_logger_from_plan

    sess = get_or_create_bank_session(plan)
    body, _ = select_fragment(
        registry,
        bank_stems=["global_scene_anchor_bank"],
        slot_type="SCENE_ANCHOR",
        ctx=ctx,
        session=sess,
        logger=variant_logger_from_plan(plan),
        role="scene_anchor",
    )
    return body


def select_flow_glue(
    registry: ContentBankRegistry,
    *,
    chapter_index: int,
    book_seed: str,
    plan: Optional[dict] = None,
) -> str:
    frame = str((plan or {}).get("frame") or (plan or {}).get("spine_context", {}).get("frame") or "somatic_first")
    topic = str((plan or {}).get("topic_id") or (plan or {}).get("book_spec", {}).get("topic_id") or "")
    persona = str((plan or {}).get("persona_id") or (plan or {}).get("book_spec", {}).get("persona_id") or "")
    runtime = str(
        (plan or {}).get("runtime_format_id")
        or (plan or {}).get("book_spec", {}).get("runtime_format_id")
        or "standard_book"
    )
    ctx = FragmentContext(
        topic_id=topic,
        persona_id=persona,
        frame=frame,
        runtime_format_id=runtime,
        chapter_index=chapter_index,
        book_seed=book_seed,
        slot_key="flow_glue",
    )
    from phoenix_v4.content_banks.session import get_or_create_bank_session, variant_logger_from_plan

    sess = get_or_create_bank_session(plan)
    body, _ = select_fragment(
        registry,
        bank_stems=["global_flow_glue_bank"],
        slot_type="FLOW_GLUE",
        ctx=ctx,
        session=sess,
        logger=variant_logger_from_plan(plan),
        role="flow_glue",
    )
    return body


def reflection_band_window(chapter_1based: int) -> Optional[set[int]]:
    if chapter_1based <= 6:
        return None
    if chapter_1based <= 8:
        return {2, 3}
    return {3, 4}
