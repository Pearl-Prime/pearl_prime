"""
EI V2 hybrid selector: combine V1 and V2 selection with optional learned override.
Deterministic given selector_key; minimal V1 path when V2 unavailable.

V2 path (non-empty v2_cfg): scores mirror run_ei_v2_analysis / _select_v2_best:
cross-encoder rerank, safety (inverse risk), domain similarity (only when embed_fn
is provided, matching __init__.py), TTS readability.

Chapter-level emotion_arc (when emotion_arc.enabled and chapter_text + arc_intent):
if max(band_deviation, role_deviation) from validate_emotion_arc exceeds
hybrid.arc_block_threshold, margin-based V2 override is suppressed — final stays
V1 unless V1 is blocked (safety/dedup/TTS). A uniform composite penalty would not
change V2-best vs V1 margin; suppressing override is deterministic and conservative.

Blocking: V1 winner is replaced by V2-best (or first lexicographically-first
unblocked candidate) when safety, dedup, or TTS thresholds from hybrid.* fail.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from phoenix_v4.quality.ei_v2.config import ei_v2_repo_root, load_ei_v2_config
from phoenix_v4.quality.ei_v2.cross_encoder_reranker import rerank_candidates
from phoenix_v4.quality.ei_v2.domain_embeddings import domain_thesis_similarity
from phoenix_v4.quality.ei_v2.emotion_arc_validator import validate_emotion_arc
from phoenix_v4.quality.ei_v2.learner import LearnedParams, load_learned_params
from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates
from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability


@dataclass
class HybridDecision:
    slot: str
    chapter_index: int
    slot_index: int
    final_chosen_id: str
    v1_chosen_id: str
    v2_chosen_id: str
    override_applied: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _v1_pick(candidates_raw: List[Dict[str, Any]], selector_key: str) -> str:
    """Deterministic V1-style pick by selector_key (hash). Fail-open: first candidate or empty."""
    if not candidates_raw:
        return ""
    if len(candidates_raw) == 1:
        return (candidates_raw[0].get("atom_id") or "").strip()
    h = hashlib.sha256(selector_key.encode()).hexdigest()
    idx = int(h[:8], 16) % len(candidates_raw)
    return (candidates_raw[idx].get("atom_id") or "").strip()


def _deep_merge_v2_cfg(overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user v2_cfg over load_ei_v2_config() defaults (one-level dict merge)."""
    base = load_ei_v2_config()
    merged: Dict[str, Any] = {**base}
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v
    return merged


def _effective_composite_weights(cfg: Dict[str, Any], learned: Optional[LearnedParams]) -> Dict[str, float]:
    """YAML composite_weights merged with learner keys (domain/tts aliases)."""
    w = dict(cfg.get("composite_weights") or {})
    if not learned:
        return {k: float(v) for k, v in w.items()}
    lw = learned.composite_weights or {}
    alias = {
        "rerank": "rerank",
        "safety": "safety",
        "domain": "domain_similarity",
        "domain_similarity": "domain_similarity",
        "tts": "tts_readability",
        "tts_readability": "tts_readability",
    }
    for src, dest in alias.items():
        if src in lw:
            w[dest] = float(lw[src])
    return {k: float(v) for k, v in w.items()}


def _max_dedup_similarity_for_id(duplicates: List[Dict[str, Any]], cid: str) -> float:
    m = 0.0
    for d in duplicates:
        if d.get("id_a") == cid or d.get("id_b") == cid:
            m = max(m, float(d.get("similarity", 0.0)))
    return m


def _arc_suppresses_margin_override(
    chapter_text: Optional[str],
    arc_intent: Optional[Dict[str, Any]],
    cfg: Dict[str, Any],
    arc_block_threshold: float,
) -> bool:
    """
    True when chapter prose deviates from arc intent beyond arc_block_threshold
    (max of band_deviation and role_deviation from validate_emotion_arc metrics).
    """
    arc_cfg = cfg.get("emotion_arc") or {}
    if not arc_cfg.get("enabled", False) or not chapter_text or not arc_intent:
        return False
    result = validate_emotion_arc(chapter_text, arc_intent, cfg=arc_cfg)
    metrics = result.get("metrics") or {}
    band_d = float(metrics.get("band_deviation", 0.0))
    role_d = float(metrics.get("role_deviation", 0.0))
    dev = max(band_d, role_d)
    return dev > arc_block_threshold


def _score_composite(
    *,
    rerank_score: Optional[float],
    safety: Dict[str, Any],
    domain_similarity: Optional[float],
    tts_readability: Optional[Dict[str, Any]],
    duration_fit: Optional[float],
    weights: Dict[str, float],
    duration_neutral: float = 0.62,
) -> float:
    """Match _select_v2_best logic; optional duration_fit (CDIS §11)."""
    w_rerank = float(weights.get("rerank", 0.35))
    w_safety = float(weights.get("safety", 0.25))
    w_domain = float(weights.get("domain_similarity", 0.20))
    w_tts = float(weights.get("tts_readability", 0.20))
    w_dur = float(weights.get("duration_fit", 0.0))

    score = 0.0
    if rerank_score is not None:
        score += w_rerank * float(rerank_score)
    if isinstance(safety, dict):
        risk = float(safety.get("risk_score", 0.0))
        score += w_safety * (1.0 - risk)
    if domain_similarity is not None:
        score += w_domain * float(domain_similarity)
    if isinstance(tts_readability, dict):
        readability = float(tts_readability.get("composite", 0.5))
        score += w_tts * readability
    if w_dur > 0.0:
        df = float(duration_fit) if duration_fit is not None else duration_neutral
        score += w_dur * max(0.0, min(1.0, df))

    return max(0.0, score)


def _candidate_blocked(
    cid: str,
    *,
    safety_by_id: Dict[str, Dict[str, Any]],
    tts_by_id: Dict[str, Dict[str, Any]],
    duplicates: List[Dict[str, Any]],
    safety_block_threshold: float,
    dedup_block_threshold: float,
    tts_block_threshold: float,
) -> bool:
    safety = safety_by_id.get(cid, {})
    risk = float(safety.get("risk_score", 0.0))
    if risk > safety_block_threshold:
        return True
    tts = tts_by_id.get(cid, {})
    tts_comp = float(tts.get("composite", 1.0))
    if tts_comp < tts_block_threshold:
        return True
    if _max_dedup_similarity_for_id(duplicates, cid) > dedup_block_threshold:
        return True
    return False


def _pick_v2_best(composite_by_id: Dict[str, float], ids: List[str]) -> str:
    """Highest composite; tie-break lexicographically smallest id."""
    best_id = ""
    best_score = -1e9
    for cid in sorted(ids):
        s = composite_by_id.get(cid, -1e9)
        if s > best_score or (s == best_score and (best_id == "" or cid < best_id)):
            best_score = s
            best_id = cid
    return best_id


def _first_unblocked_sorted(
    ids: List[str],
    *,
    safety_by_id: Dict[str, Dict[str, Any]],
    tts_by_id: Dict[str, Dict[str, Any]],
    duplicates: List[Dict[str, Any]],
    safety_block_threshold: float,
    dedup_block_threshold: float,
    tts_block_threshold: float,
) -> str:
    for cid in sorted(ids):
        if not _candidate_blocked(
            cid,
            safety_by_id=safety_by_id,
            tts_by_id=tts_by_id,
            duplicates=duplicates,
            safety_block_threshold=safety_block_threshold,
            dedup_block_threshold=dedup_block_threshold,
            tts_block_threshold=tts_block_threshold,
        ):
            return cid
    return ""


def hybrid_select(
    *,
    slot: str,
    chapter_index: int,
    slot_index: int,
    candidates_raw: List[Dict[str, Any]],
    persona_id: str,
    topic_id: str,
    thesis: str,
    v1_cfg: Optional[Dict[str, Any]] = None,
    v2_cfg: Optional[Dict[str, Any]] = None,
    selector_key: Optional[str] = None,
    embed_fn: Optional[Callable[[str, str], List[float]]] = None,
    chapter_text: Optional[str] = None,
    arc_intent: Optional[Dict[str, Any]] = None,
    learned_params_path: Optional[Path] = None,
    call_llm_fn: Optional[Callable[..., Any]] = None,
    duration_fit_by_id: Optional[Dict[str, float]] = None,
) -> HybridDecision:
    """
    Hybrid selection: V1 hash pick, optional V2 composite scoring and override.

    V2 scoring runs only when ``v2_cfg`` is a **non-empty** dict (merged over defaults).
    Passing ``v2_cfg={}`` or ``None`` keeps legacy behavior: final = V1, v2_chosen = v1.

    Deterministic: same ``selector_key``, candidates, and config → same decision.
    """
    key = selector_key or f"{slot}:{chapter_index}:{slot_index}:{persona_id}:{topic_id}"
    v1_chosen = _v1_pick(candidates_raw, key)

    if not v2_cfg:
        return HybridDecision(
            slot=slot,
            chapter_index=chapter_index,
            slot_index=slot_index,
            final_chosen_id=v1_chosen,
            v1_chosen_id=v1_chosen,
            v2_chosen_id=v1_chosen,
            override_applied=False,
        )

    cfg = _deep_merge_v2_cfg(v2_cfg)
    hybrid_cfg = cfg.get("hybrid") or {}
    if not hybrid_cfg.get("enabled", True):
        return HybridDecision(
            slot=slot,
            chapter_index=chapter_index,
            slot_index=slot_index,
            final_chosen_id=v1_chosen,
            v1_chosen_id=v1_chosen,
            v2_chosen_id=v1_chosen,
            override_applied=False,
        )

    if not candidates_raw or not v1_chosen:
        return HybridDecision(
            slot=slot,
            chapter_index=chapter_index,
            slot_index=slot_index,
            final_chosen_id=v1_chosen,
            v1_chosen_id=v1_chosen,
            v2_chosen_id=v1_chosen,
            override_applied=False,
        )

    learned: Optional[LearnedParams] = None
    learned_from_explicit_path = False
    if learned_params_path is not None:
        if learned_params_path.is_file():
            learned = load_learned_params(learned_params_path)
            learned_from_explicit_path = True
    else:
        default_lp = ei_v2_repo_root() / "artifacts" / "ei_v2" / "learned_params.json"
        if default_lp.is_file():
            learned = load_learned_params(default_lp)

    override_margin = float(hybrid_cfg.get("override_margin", 0.12))
    if learned is not None:
        overlay_hybrid = (v2_cfg or {}).get("hybrid") or {}
        # Explicit learned_params_path: learner wins (tuned runs, test_hybrid_respects_learned_*).
        # Default artifact learned_params.json: only tune margin when the caller did not set
        # hybrid.override_margin in v2_cfg — otherwise repo artifacts overwrite explicit margins
        # and tests (see test_hybrid_v2_override_when_margin_exceeded).
        use_learned_margin = learned_from_explicit_path or "override_margin" not in overlay_hybrid
        if use_learned_margin:
            override_margin = float(learned.override_margin)

    safety_block_threshold = float(hybrid_cfg.get("safety_block_threshold", 0.5))
    dedup_block_threshold = float(hybrid_cfg.get("dedup_block_threshold", 0.6))
    arc_block_threshold = float(hybrid_cfg.get("arc_block_threshold", 0.5))
    tts_block_threshold = float(hybrid_cfg.get("tts_block_threshold", 0.3))

    weights = _effective_composite_weights(cfg, learned)
    dur_cfg = cfg.get("duration_fit") or {}
    duration_neutral = float(dur_cfg.get("neutral_when_unscored", 0.62))

    texts = [c.get("text", "") for c in candidates_raw]
    ids = [(c.get("id") or c.get("atom_id") or f"c{i}").strip() for i, c in enumerate(candidates_raw)]

    safety_by_id: Dict[str, Dict[str, Any]] = {}
    rerank_by_id: Dict[str, float] = {}
    domain_by_id: Dict[str, float] = {}
    tts_by_id: Dict[str, Dict[str, Any]] = {}
    duplicates: List[Dict[str, Any]] = []

    safety_cfg = cfg.get("safety_classifier") or {}
    if safety_cfg.get("enabled", False):
        for cid, text in zip(ids, texts):
            safety_by_id[cid] = classify_safety(
                text, slot=slot, cfg=safety_cfg, full_cfg=cfg, call_llm_fn=call_llm_fn
            )

    rerank_cfg = cfg.get("cross_encoder") or {}
    if rerank_cfg.get("enabled", False) and thesis:
        ranked = rerank_candidates(thesis, texts, ids, cfg=rerank_cfg)
        for r in ranked:
            rerank_by_id[r["id"]] = float(r["score"])

    domain_cfg = cfg.get("domain_embeddings") or {}
    if domain_cfg.get("enabled", False) and thesis and embed_fn is not None:
        for cid, text in zip(ids, texts):
            domain_by_id[cid] = domain_thesis_similarity(
                thesis,
                text,
                persona_id=persona_id,
                topic_id=topic_id,
                cfg=cfg,
                embed_fn=embed_fn,
            )

    tts_cfg = cfg.get("tts_readability") or {}
    if tts_cfg.get("enabled", False):
        for cid, text in zip(ids, texts):
            tts_by_id[cid] = score_tts_readability(text, cfg=tts_cfg)

    dedup_cfg = cfg.get("semantic_dedup") or {}
    if dedup_cfg.get("enabled", False) and len(texts) >= 2:
        duplicates = detect_semantic_duplicates(texts, ids, cfg=dedup_cfg)

    suppress_margin_override = _arc_suppresses_margin_override(
        chapter_text, arc_intent, cfg, arc_block_threshold
    )

    composite_by_id: Dict[str, float] = {}
    for cid in ids:
        dfs = duration_fit_by_id.get(cid) if duration_fit_by_id else None
        composite_by_id[cid] = _score_composite(
            rerank_score=rerank_by_id.get(cid),
            safety=safety_by_id.get(cid, {}),
            domain_similarity=domain_by_id.get(cid),
            tts_readability=tts_by_id.get(cid),
            duration_fit=dfs,
            weights=weights,
            duration_neutral=duration_neutral,
        )

    v2_best = _pick_v2_best(composite_by_id, ids)
    v1_in_ids = v1_chosen in ids

    v1_blocked = False
    if v1_in_ids:
        v1_blocked = _candidate_blocked(
            v1_chosen,
            safety_by_id=safety_by_id,
            tts_by_id=tts_by_id,
            duplicates=duplicates,
            safety_block_threshold=safety_block_threshold,
            dedup_block_threshold=dedup_block_threshold,
            tts_block_threshold=tts_block_threshold,
        )

    v2b_blocked = False
    if v2_best:
        v2b_blocked = _candidate_blocked(
            v2_best,
            safety_by_id=safety_by_id,
            tts_by_id=tts_by_id,
            duplicates=duplicates,
            safety_block_threshold=safety_block_threshold,
            dedup_block_threshold=dedup_block_threshold,
            tts_block_threshold=tts_block_threshold,
        )

    final = v1_chosen
    override = False

    if v1_blocked:
        override = True
        if v2_best and not v2b_blocked:
            final = v2_best
        else:
            fallback = _first_unblocked_sorted(
                ids,
                safety_by_id=safety_by_id,
                tts_by_id=tts_by_id,
                duplicates=duplicates,
                safety_block_threshold=safety_block_threshold,
                dedup_block_threshold=dedup_block_threshold,
                tts_block_threshold=tts_block_threshold,
            )
            final = fallback
    elif v1_in_ids and v2_best:
        s_v1 = composite_by_id.get(v1_chosen, 0.0)
        s_v2b = composite_by_id.get(v2_best, 0.0)
        if suppress_margin_override:
            final = v1_chosen
            override = False
        elif s_v2b - s_v1 > override_margin:
            final = v2_best
            override = True
        else:
            final = v1_chosen
            override = False
    else:
        final = v1_chosen
        override = False

    return HybridDecision(
        slot=slot,
        chapter_index=chapter_index,
        slot_index=slot_index,
        final_chosen_id=final,
        v1_chosen_id=v1_chosen,
        v2_chosen_id=v2_best or v1_chosen,
        override_applied=override,
    )
