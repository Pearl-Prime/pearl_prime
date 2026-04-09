"""
EI v2 dimensions adapted for Pearl News HTML articles (post-expansion, pre-validation).
Uses phoenix_v4.quality.ei_v2 classifiers where available (no embed_fn required for domain).
"""
from __future__ import annotations

import logging
import re
from typing import Any

from phoenix_v4.quality.ei_v2.dimension_gates import gate_engagement
from phoenix_v4.quality.ei_v2.domain_embeddings import domain_thesis_similarity
from phoenix_v4.quality.ei_v2.safety_classifier import classify_safety
from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability
from phoenix_v4.quality.ei_v2.visual_therapeutic import vt_stealth

logger = logging.getLogger(__name__)


def _html_to_text(html: str) -> str:
    if not html:
        return ""
    t = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.DOTALL)
    t = re.sub(r"<style[^>]*>.*?</style>", " ", t, flags=re.I | re.DOTALL)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def score_engagement(text_plain: str, _: dict[str, Any]) -> dict[str, Any]:
    g = gate_engagement(text_plain, 0)
    return {"score": float(g.score), "status": g.status, "issues": g.issues}


def check_stealth_compliance(text_plain: str, full_ei_cfg: dict[str, Any]) -> dict[str, Any]:
    score = float(vt_stealth(text_plain, cfg=full_ei_cfg))
    return {"score": score, "pass": score >= 1.0}


def score_article_ei(
    item: dict[str, Any],
    *,
    pearl_ei_cfg: dict[str, Any],
    full_ei_cfg: dict[str, Any],
) -> dict[str, Any]:
    """
    Populate item with _ei_scores, _ei_composite, optional _ei_review_flags.
    pearl_ei_cfg: llm_expansion.yaml `ei_scoring` section.
    full_ei_cfg: loaded EI v2 config (dimensions, thresholds).
    """
    raw = item.get("content") or ""
    text = _html_to_text(raw)
    topic = (item.get("topic") or "").strip() or "partnerships"
    title = (item.get("article_title") or item.get("title") or "").strip()
    thesis = f"{topic}: {title}".strip()
    persona = (item.get("_persona") or pearl_ei_cfg.get("default_persona") or "gen_z_professionals").strip()

    safety_cfg = full_ei_cfg.get("safety_classifier") or {}
    tts_cfg = full_ei_cfg.get("tts_readability") or {}
    domain_cfg = full_ei_cfg.get("domain_embeddings")

    scores: dict[str, Any] = {}

    if safety_cfg.get("enabled", True):
        scores["safety"] = classify_safety(
            text, slot="pearl_news_article", cfg=safety_cfg, full_cfg=full_ei_cfg
        )
    else:
        scores["safety"] = {"risk_score": 0.0, "categories": {}, "reason_codes": [], "mode": "disabled"}

    if tts_cfg.get("enabled", True):
        scores["tts_readability"] = score_tts_readability(text, cfg=tts_cfg)
    else:
        scores["tts_readability"] = {"composite": 0.5, "disabled": True}

    if domain_cfg and domain_cfg.get("enabled", True):
        scores["domain_similarity"] = domain_thesis_similarity(
            thesis,
            text,
            persona_id=persona,
            topic_id=topic,
            cfg=full_ei_cfg,
            embed_fn=None,
        )
    else:
        scores["domain_similarity"] = 0.5

    scores["stealth"] = check_stealth_compliance(text, full_ei_cfg)
    scores["engagement"] = score_engagement(text, pearl_ei_cfg)

    corpus_path = pearl_ei_cfg.get("recent_articles_corpus_path")
    if corpus_path:
        scores["semantic_dedup"] = {"skipped": True, "note": "corpus path reserved", "path": corpus_path}
    else:
        scores["semantic_dedup"] = {"skipped": True, "reason": "no_corpus_configured"}

    composite = compute_article_composite(
        scores,
        pearl_ei_cfg.get("composite_weights"),
    )
    item["_ei_scores"] = scores
    item["_ei_composite"] = composite

    risk = float((scores.get("safety") or {}).get("risk_score") or 0.0)
    tts_c = float((scores.get("tts_readability") or {}).get("composite") or 0.5)
    stealth_s = float((scores.get("stealth") or {}).get("score") or 1.0)

    flags: list[str] = []
    if risk > float(pearl_ei_cfg.get("safety_block_threshold", 0.5)):
        flags.append("ei_safety_block")
    tts_min = pearl_ei_cfg.get("tts_min_score")
    if tts_min is not None and tts_c < float(tts_min):
        flags.append("ei_tts_warn")
    if stealth_s < float(pearl_ei_cfg.get("stealth_block_threshold", 0.5)):
        flags.append("ei_stealth_block")
    cw = pearl_ei_cfg.get("composite_warn")
    if cw is not None and composite < float(cw):
        flags.append("ei_composite_warn")

    item["_ei_flags"] = flags
    if any(x in flags for x in ("ei_safety_block", "ei_stealth_block")):
        item["_needs_manual_review"] = True
        item["_ei_hard_fail"] = True
        logger.warning("Article %s: EI hard flag %.4f %s", item.get("id"), composite, flags)

    return item


def compute_article_composite(
    scores: dict[str, Any],
    weights: dict[str, float] | None = None,
) -> float:
    w = weights or {
        "safety": 0.25,
        "tts_readability": 0.2,
        "domain_similarity": 0.2,
        "stealth": 0.2,
        "engagement": 0.15,
    }
    safety = scores.get("safety") or {}
    risk = float(safety.get("risk_score") or 0.0)
    safety_term = 1.0 - risk

    tts = float((scores.get("tts_readability") or {}).get("composite") or 0.5)
    dom = float(scores.get("domain_similarity") or 0.5)
    stealth = float((scores.get("stealth") or {}).get("score") or 0.0)
    eng = float((scores.get("engagement") or {}).get("score") or 0.5)

    total_w = sum(w.values()) or 1.0
    comp = (
        w.get("safety", 0) * safety_term
        + w.get("tts_readability", 0) * tts
        + w.get("domain_similarity", 0) * dom
        + w.get("stealth", 0) * stealth
        + w.get("engagement", 0) * eng
    ) / total_w
    return round(max(0.0, min(1.0, comp)), 4)


def run_ei_article_scoring(
    items: list[dict[str, Any]],
    *,
    pearl_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    from phoenix_v4.quality.ei_v2.config import load_ei_v2_config

    ei_yaml = pearl_cfg.get("ei_scoring") or {}
    if not ei_yaml.get("enabled", False):
        return items

    full_ei = load_ei_v2_config()
    for item in items:
        if not (item.get("content") or "").strip():
            continue
        try:
            score_article_ei(item, pearl_ei_cfg=ei_yaml, full_ei_cfg=full_ei)
        except Exception as e:
            logger.warning("EI scoring failed for %s: %s", item.get("id"), e)
            item["_ei_scores"] = {"error": str(e)}
            item["_ei_composite"] = None
    return items
