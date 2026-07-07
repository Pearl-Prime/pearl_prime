#!/usr/bin/env python3
"""
Deep Catalog Scoring Script — Phoenix Omega
============================================
Scores all 15 canonical topics across 15 dimensions (10 existing EI + 5 new research-backed).
Uses registry content as the representative book corpus (one variant family per chapter per topic).
LLM scoring for new dimensions uses Qwen on Pearl Star (192.168.1.112:11434, qwen2.5:14b) — $0 cost.

Usage:
    python3 scripts/analysis/score_catalog_deep.py [--topic TOPIC] [--skip-llm] [--output PATH]

Output:
    artifacts/analysis/catalog_deep_scores.json

Dimensions scored (15 total):
    EI v2 heuristic (10):
        1.  safety_score           — clinical/promotional language risk (inverted)
        2.  tts_readability        — sentence length, rhythm, patterns
        3.  domain_similarity      — persona + topic + thesis alignment
        4.  emotion_arc            — valence/arousal trajectory
        5.  content_uniqueness     — structural repeat detection
        6.  engagement             — hooks, tension, pull-forward markers
        7.  somatic_precision      — body-aware language density
        8.  listen_experience      — repetition, monotony detection
        9.  cohesion               — cross-chapter references, thread continuity
        10. duration_fit           — content length vs therapeutic dose

    New research-backed (5):
        11. opening_hook_strength  — first 500 words quality
        12. exercise_quality       — specificity, body/time anchors, audiobook doability
        13. story_specificity      — concrete details per scene
        14. topic_mechanism_clarity — mechanism named in body terms, early, matching engine
        15. voice_consistency      — register variance, prohibited term presence
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

# ── Repo root ──
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.content_uniqueness_truth import (
    DEFAULT_SELLABILITY_UNIQUENESS_TRUTH_SOURCE,
    LEGACY_REGISTRY_WARNING,
    TRUTH_SOURCE_LEGACY_REGISTRY,
    enrich_catalog_book_result,
)

# ── Config ──
CANONICAL_TOPICS = [
    "anxiety", "boundaries", "burnout", "compassion_fatigue", "courage",
    "depression", "financial_anxiety", "financial_stress", "grief",
    "imposter_syndrome", "overthinking", "self_worth", "sleep_anxiety",
    "social_anxiety", "somatic_healing",
]
CANONICAL_PERSONAS = [
    "millennial_women_professionals", "gen_z_professionals", "healthcare_rns",
]

QWEN_HOST = "http://192.168.1.112:11434"
QWEN_MODEL = "qwen2.5:14b"
REGISTRY_DIR = REPO_ROOT / "registry"
OUTPUT_DIR = REPO_ROOT / "artifacts" / "analysis"

# ── Prohibited terms from topic_skins.yaml (global) ──
GLOBAL_PROHIBITED = frozenset([
    "journey", "transform", "heal", "healing journey", "self-care", "wellness",
    "mindfulness", "empower", "empowering", "overcome", "conquer", "battle",
    "fight", "warrior", "survivor", "thrive", "manifest", "authentic self",
    "best self", "inner child", "trigger warning", "safe space", "toxic",
    "self-love", "you've got this", "be gentle with yourself",
])

TOPIC_PROHIBITED: Dict[str, frozenset] = {
    "anxiety": frozenset(["anxiety attack", "panic attack", "anxiety disorder", "mental health", "coping mechanism", "grounding technique"]),
    "boundaries": frozenset(["healthy boundaries", "toxic people", "protect your energy", "boundary setting", "self-protection", "compassion satisfaction"]),
    "compassion_fatigue": frozenset(["burnout", "self-care", "caregiver fatigue", "emotional labor", "set boundaries", "compassion satisfaction"]),
    "courage": frozenset(["brave", "fearless", "courageous", "bold", "leap of faith", "comfort zone"]),
    "depression": frozenset(["depression", "depressed", "mental illness", "chemical imbalance", "antidepressant", "clinical", "diagnosis"]),
    "financial_stress": frozenset(["abundance mindset", "money blocks", "financial freedom", "wealth consciousness", "prosperity", "manifest money"]),
    "grief": frozenset(["closure", "move on", "get over it", "stages of grief", "grief process", "healing process"]),
    "self_worth": frozenset(["self-esteem", "self-worth", "worthy", "deserve", "enough", "imposter syndrome", "inner critic"]),
}

BODY_WORDS = frozenset([
    "shoulder", "shoulders", "breath", "breathing", "stomach", "jaw", "chest",
    "heart", "racing", "tight", "tensed", "tension", "relax", "release",
    "ground", "grounded", "body", "sensation", "felt", "feeling", "spine",
    "throat", "belly", "lungs", "exhale", "inhale", "pulse", "muscle", "nerves",
])

EXERCISE_TIME_PATTERNS = [r"\d+\s*(breath|second|minute|count)", r"for\s+\d+", r"three breath", r"ten second", r"sixty second"]
EXERCISE_BODY_PATTERNS = [r"\b(hand|chest|stomach|jaw|shoulder|breath|belly|throat|spine)\b"]
SPECIFIC_DETAIL_PATTERNS = [r"\b(street|city|desk|chair|train|morning|night|window|floor|wall|door|phone|coffee|rain|light|dark)\b"]


def load_registry(topic: str) -> Optional[Dict[str, Any]]:
    """Load registry YAML for a topic. Returns None if missing."""
    try:
        import yaml
    except ImportError:
        print("  [WARN] PyYAML not available, using JSON fallback")
        return None
    path = REGISTRY_DIR / f"{topic}.yaml"
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  [WARN] Failed to load registry/{topic}.yaml: {e}")
        return None


def extract_chapter_texts(registry: Dict[str, Any], max_chapters: int = 12) -> List[Dict[str, Any]]:
    """Extract one representative text per chapter from registry (F1 variant, fallback F2)."""
    sections_data = registry.get("sections", {})
    chapters = []
    for ch_key in sorted(sections_data.keys())[:max_chapters]:
        ch_data = sections_data[ch_key]
        chapter_idx = int(ch_data.get("chapter", len(chapters) + 1)) - 1
        chapter_title = ch_data.get("title", ch_key)
        sections = ch_data.get("sections", {})

        # Collect text from all section types in this chapter
        full_text_parts = []
        exercise_texts = []
        scene_texts = []
        hook_text = ""

        for sec_key in sorted(sections.keys()):
            sec = sections[sec_key]
            sec_type = sec.get("type", "UNKNOWN")
            variants = sec.get("variants", [])
            if not variants:
                continue
            # Pick F1 variant, fallback to first
            chosen = variants[0]
            for v in variants:
                if v.get("variant_family") == "F1":
                    chosen = v
                    break
            text = chosen.get("content", "")
            if not text:
                continue

            full_text_parts.append(text)
            if sec_type == "EXERCISE":
                exercise_texts.append(text)
            elif sec_type in ("SCENE", "STORY"):
                scene_texts.append(text)
            elif sec_type == "HOOK" and not hook_text:
                hook_text = text

        chapters.append({
            "chapter_index": chapter_idx,
            "chapter_key": ch_key,
            "title": chapter_title,
            "full_text": "\n\n".join(full_text_parts),
            "exercise_texts": exercise_texts,
            "scene_texts": scene_texts,
            "hook_text": hook_text,
        })

    return chapters


# ── EI heuristic dimensions ──

def score_safety(text: str) -> float:
    """Safety score (inverted risk): 1.0 = safe, 0.0 = high risk."""
    text_lower = text.lower()
    risk = 0.0
    clinical_terms = ["diagnose", "clinical depression", "psychiatric", "medication", "antidepressant", "disorder", "syndrome", "therapy session"]
    promo_terms = ["buy now", "get yours", "limited offer", "sign up", "subscribe"]
    medical_claims = ["cures", "proven to treat", "scientifically proven to heal", "medical breakthrough"]
    for t in clinical_terms:
        if t in text_lower:
            risk += 0.05
    for t in promo_terms:
        if t in text_lower:
            risk += 0.15
    for t in medical_claims:
        if t in text_lower:
            risk += 0.20
    return max(0.0, min(1.0, 1.0 - risk))


def score_tts_readability_heuristic(text: str) -> float:
    """TTS readability: sentence length variance, paragraph breaks, pattern avoidance.

    ACT-013 calibration fix: Phoenix's writer spec intentionally uses short sentences
    (1-4 words) for TTS pacing. Replace the rigid 8-25 word "ideal" range with a
    sentence-length-range coverage metric: variety of very-short to medium sentences
    is scored positively. Zero rhythm_variance is acceptable when median length ≤ 6.
    """
    if not text.strip():
        return 0.0
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 0.0
    lengths = [len(s.split()) for s in sentences]
    if not lengths:
        return 0.0
    median_len = sorted(lengths)[len(lengths) // 2]
    avg_len = sum(lengths) / len(lengths)
    # Variance — waived for intentional short-sentence style (median ≤ 6)
    variance = sum((l - avg_len) ** 2 for l in lengths) / max(len(lengths), 1)
    if median_len <= 6:
        variance_score = 1.0  # short-sentence style is intentional, not a defect
    else:
        variance_score = min(1.0, variance / 50.0)
    # Coverage: mix of very-short (1-3), short (4-8), medium (9-25)
    buckets = {"xs": 0, "s": 0, "m": 0}
    for l in lengths:
        if l <= 3:
            buckets["xs"] += 1
        elif l <= 8:
            buckets["s"] += 1
        elif l <= 25:
            buckets["m"] += 1
    filled = sum(1 for v in buckets.values() if v > 0)
    coverage_score = filled / 3.0
    # Paragraph breaks (per 500 words)
    word_count = len(text.split())
    para_breaks = text.count("\n\n")
    para_score = min(1.0, (para_breaks / max(word_count / 500, 1)) / 3.0)
    # Penalize very long words (15+ chars)
    long_words = re.findall(r"\b\w{15,}\b", text)
    long_word_penalty = min(0.3, len(long_words) * 0.05)
    composite = 0.3 * variance_score + 0.35 * coverage_score + 0.25 * para_score - long_word_penalty
    return round(max(0.0, min(1.0, composite)), 3)


def score_domain_similarity(text: str, topic: str, persona: str) -> float:
    """Heuristic domain similarity: topic keyword and persona keyword density."""
    text_lower = text.lower()
    topic_keywords = {
        "anxiety": ["anxiety", "anxious", "alarm", "threat", "nervous", "worry", "fear"],
        "burnout": ["burnout", "exhausted", "depleted", "empty", "capacity", "drained"],
        "grief": ["grief", "loss", "absent", "missing", "mourn", "gone"],
        "self_worth": ["worth", "value", "judgment", "outcome", "verdict"],
        "depression": ["distance", "numb", "flat", "absent", "glass", "detach"],
        "boundaries": ["limit", "no", "boundary", "block", "gate", "permission"],
        "imposter_syndrome": ["fraud", "competence", "credibility", "pretend", "exposure"],
        "overthinking": ["thought", "loop", "ruminate", "spiral", "chain", "circle"],
        "compassion_fatigue": ["caring", "empty", "vessel", "giving", "drain"],
        "courage": ["action", "fear", "gate", "risk", "move", "proceed"],
        "financial_anxiety": ["money", "debt", "number", "account", "finance"],
        "financial_stress": ["money", "debt", "number", "tight", "bills"],
        "sleep_anxiety": ["sleep", "night", "bed", "wake", "insomnia"],
        "social_anxiety": ["social", "visible", "seen", "crowd", "observed"],
        "somatic_healing": ["body", "sensation", "somatic", "nervous system", "tissue"],
    }
    persona_keywords = {
        "gen_z_professionals": ["work", "career", "professional", "job", "team"],
        "millennial_women_professionals": ["work", "career", "balance", "professional"],
        "healthcare_rns": ["patient", "shift", "care", "clinical", "nurse", "hospital"],
    }
    topic_kws = topic_keywords.get(topic, [])
    persona_kws = persona_keywords.get(persona, [])
    topic_hits = sum(1 for kw in topic_kws if kw in text_lower)
    persona_hits = sum(1 for kw in persona_kws if kw in text_lower)
    topic_score = min(1.0, topic_hits / max(len(topic_kws), 1) * 2.0)
    persona_score = min(1.0, persona_hits / max(len(persona_kws), 1))
    return round(0.6 * topic_score + 0.4 * persona_score, 3)


def score_emotion_arc(chapters: List[str]) -> float:
    """Emotion arc: check valence progression across chapters (low → medium → high → integration)."""
    if not chapters:
        return 0.0
    VALENCE_POS = frozenset(["relief", "clarity", "peace", "ground", "still", "open", "free", "connect", "present", "accept"])
    VALENCE_NEG = frozenset(["trap", "stuck", "heavy", "tight", "numb", "fear", "alarm", "threat", "drain", "empty"])
    scores = []
    for ch_text in chapters:
        words = set(re.findall(r"\w+", ch_text.lower()))
        pos = len(words & VALENCE_POS)
        neg = len(words & VALENCE_NEG)
        val = (pos - neg) / max(pos + neg, 1)
        scores.append(val)
    if len(scores) < 2:
        return 0.5
    # Ideal: arc goes from negative → positive
    first_half_mean = sum(scores[:len(scores)//2]) / max(len(scores)//2, 1)
    second_half_mean = sum(scores[len(scores)//2:]) / max(len(scores) - len(scores)//2, 1)
    # Score: higher if arc rises
    arc_rise = (second_half_mean - first_half_mean + 1.0) / 2.0
    return round(max(0.0, min(1.0, arc_rise)), 3)


def score_content_uniqueness(chapters: List[str]) -> float:
    """Content uniqueness: penalize structural phrase repeats across chapters.

    ACT-013 calibration fix: use 3-word phrase (trigram) overlap instead of word
    overlap. Books about one topic share topic vocabulary by design (not a defect).
    Only structural phrase repetition (identical trigram constructions) is penalized.
    phrase_jaccard > 0.25 is treated as structural repetition.
    """
    if len(chapters) < 2:
        return 1.0

    def _trigrams(text: str) -> frozenset:
        words = re.findall(r"\w+", text.lower())
        return frozenset(tuple(words[i:i+3]) for i in range(len(words) - 2))

    overlaps = []
    for i in range(len(chapters)):
        for j in range(i + 1, len(chapters)):
            tri_i = _trigrams(chapters[i])
            tri_j = _trigrams(chapters[j])
            if not tri_i or not tri_j:
                continue
            jaccard = len(tri_i & tri_j) / len(tri_i | tri_j)
            overlaps.append(jaccard)
    if not overlaps:
        return 1.0
    avg_overlap = sum(overlaps) / len(overlaps)
    # phrase_jaccard > 0.25 signals structural repetition; penalize proportionally
    penalty = max(0.0, avg_overlap - 0.25) * 4.0
    return round(max(0.0, min(1.0, 1.0 - penalty)), 3)


def score_engagement(text: str) -> float:
    """Engagement: hooks, tension, pull-forward markers."""
    if not text.strip():
        return 0.0
    text_lower = text.lower()
    hook_patterns = [r"\?", r"here's the thing", r"but here's", r"the problem is", r"what if"]
    tension_patterns = [r"but", r"however", r"except", r"until", r"unless", r"not yet"]
    pull_patterns = [r"in the next", r"we'll", r"coming up", r"as we'll see", r"more on this"]
    hook_count = sum(len(re.findall(p, text_lower)) for p in hook_patterns)
    tension_count = sum(len(re.findall(p, text_lower)) for p in tension_patterns)
    pull_count = sum(len(re.findall(p, text_lower)) for p in pull_patterns)
    word_count = len(text.split())
    density = (hook_count + tension_count * 0.5 + pull_count * 0.3) / max(word_count / 100, 1)
    return round(max(0.0, min(1.0, density / 5.0)), 3)


def score_somatic_precision(text: str) -> float:
    """Somatic precision: body-aware language density.

    ACT-013 calibration fix: use fixed denominator of 15 body words as target
    (not proportional to total length). A 10,000-word book with 15+ body words
    scores full marks — proportional density was penalising long-form content.
    """
    if not text.strip():
        return 0.0
    words = set(re.findall(r"\w+", text.lower()))
    body_hits = len(words & BODY_WORDS)
    return round(min(1.0, body_hits / 15.0), 3)


def score_listen_experience(text: str) -> float:
    """Listen experience: audio repetition penalty, jargon density, rhythm."""
    if not text.strip():
        return 0.0
    words = re.findall(r"\b[\w'-]+\b", text.lower())
    # Long-word jargon penalty
    long_words = [w for w in words if len(w) >= 10]
    jargon_penalty = min(0.3, len(long_words) / max(len(words), 1) * 5.0)
    # Repetition: word 4-gram repeats
    ngrams = [tuple(words[i:i+4]) for i in range(len(words) - 3)]
    from collections import Counter
    ngram_counts = Counter(ngrams)
    repeat_count = sum(1 for c in ngram_counts.values() if c >= 2)
    repeat_penalty = min(0.3, repeat_count * 0.05)
    # TTS rhythm
    tts = score_tts_readability_heuristic(text)
    score = 0.6 * tts - jargon_penalty - repeat_penalty + 0.2
    return round(max(0.0, min(1.0, score)), 3)


def score_cohesion(chapters: List[str]) -> float:
    """Cohesion: backward linkage between consecutive chapters."""
    if len(chapters) < 2:
        return 1.0
    TRANSITIONAL = ["as we saw", "in the last chapter", "building on", "earlier", "that pattern", "remember when"]
    phrase_scores = []
    word_overlap_scores = []
    for i in range(1, len(chapters)):
        curr = chapters[i].lower()
        prev = chapters[i-1].lower()
        phrase_hits = sum(1 for p in TRANSITIONAL if p in curr)
        phrase_scores.append(min(1.0, phrase_hits / 2.0))
        curr_words = set(re.findall(r"\w+", curr)) - {"the", "a", "and", "or", "in", "of", "is", "it", "to", "for"}
        prev_words = set(re.findall(r"\w+", prev)) - {"the", "a", "and", "or", "in", "of", "is", "it", "to", "for"}
        overlap = len(curr_words & prev_words) / max(len(curr_words), 1)
        word_overlap_scores.append(min(1.0, overlap / 0.15))
    avg_phrase = sum(phrase_scores) / max(len(phrase_scores), 1)
    avg_overlap = sum(word_overlap_scores) / max(len(word_overlap_scores), 1)
    return round(0.4 * avg_phrase + 0.6 * avg_overlap, 3)


def score_duration_fit(chapters: List[str], topic: str) -> float:
    """Duration fit: content length vs therapeutic dose targets."""
    # Target: 12 chapters × ~600-800 words each = 7200-9600 words total
    total_words = sum(len(c.split()) for c in chapters)
    IDEAL_MIN = 5000
    IDEAL_MAX = 12000
    if total_words < IDEAL_MIN:
        return round(max(0.3, total_words / IDEAL_MIN), 3)
    if total_words > IDEAL_MAX:
        return round(max(0.5, 1.0 - (total_words - IDEAL_MAX) / IDEAL_MAX * 0.5), 3)
    return round(0.7 + 0.3 * (total_words - IDEAL_MIN) / (IDEAL_MAX - IDEAL_MIN), 3)


# ── New research-backed dimensions ──

def score_opening_hook_strength(hook_text: str) -> float:
    """Score the first 500 words of chapter 1."""
    if not hook_text:
        return 0.0
    text = hook_text[:3000]  # limit to first ~500 words area
    words = text.split()
    first_500 = " ".join(words[:500])
    score = 0.0
    # 1. Names a specific recognizable behavior or pattern (not abstract)
    specific_behavior = re.search(r"\b(you|your)\b.{0,50}\b(feel|say|do|think|notice|check|wait|avoid|hold|loop|run|stop)\b", first_500, re.IGNORECASE)
    if specific_behavior:
        score += 0.25
    # 2. Uses second-person present tense (immersive)
    second_person = len(re.findall(r"\byou\b", first_500, re.IGNORECASE))
    if second_person >= 5:
        score += 0.20
    elif second_person >= 2:
        score += 0.10
    # 3. Pattern naming — "The pattern is..." / "The sentence is..." / "Here's what..."
    pattern_naming = re.search(r"(the pattern is|the sentence is|here'?s the|this is the|the rule is|the loop is)", first_500, re.IGNORECASE)
    if pattern_naming:
        score += 0.25
    # 4. Short first paragraph (audiobook constraint: shorter = more punchy)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if paras and len(paras[0].split()) <= 20:
        score += 0.15
    elif paras and len(paras[0].split()) <= 40:
        score += 0.10
    # 5. Question or direct address in opening
    if "?" in first_500[:200]:
        score += 0.15
    return round(min(1.0, score), 3)


def score_exercise_quality(exercise_texts: List[str]) -> float:
    """Score exercise sections: specificity, body/time anchors, audiobook doability."""
    if not exercise_texts:
        return 0.0
    scores = []
    for ex in exercise_texts:
        ex_lower = ex.lower()
        s = 0.0
        # Is instruction specific? (not "take a moment to reflect")
        vague = ["take a moment", "reflect on", "sit with", "think about", "consider"]
        specific = ["place your", "breathe in", "exhale", "press your", "close your", "notice the", "feel the", "count to"]
        vague_count = sum(1 for v in vague if v in ex_lower)
        specific_count = sum(1 for sp in specific if sp in ex_lower)
        if specific_count > vague_count:
            s += 0.30
        elif specific_count > 0:
            s += 0.15
        # Names a body part
        body_match = any(re.search(p, ex_lower) for p in EXERCISE_BODY_PATTERNS)
        if body_match:
            s += 0.30
        # Has time indicator
        time_match = any(re.search(p, ex_lower) for p in EXERCISE_TIME_PATTERNS)
        if time_match:
            s += 0.25
        # Doable while listening (not "look at yourself in the mirror", "write down")
        not_audiobook = ["write down", "journal", "draw", "look in the mirror", "take out a pen"]
        if not any(n in ex_lower for n in not_audiobook):
            s += 0.15
        scores.append(min(1.0, s))
    return round(sum(scores) / max(len(scores), 1), 3)


def score_story_specificity(scene_texts: List[str]) -> float:
    """Score scene/story sections: concrete details per scene."""
    if not scene_texts:
        return 0.0
    scores = []
    for scene in scene_texts:
        scene_lower = scene.lower()
        s = 0.0
        # Specific place, object, or sensory detail
        specific_matches = sum(len(re.findall(p, scene_lower)) for p in SPECIFIC_DETAIL_PATTERNS)
        if specific_matches >= 3:
            s += 0.40
        elif specific_matches >= 1:
            s += 0.20
        # Avoids generic "imagine yourself" phrasing
        generic = ["imagine yourself", "picture a place", "think of a time when", "envision"]
        if not any(g in scene_lower for g in generic):
            s += 0.30
        # Has at least 3 concrete nouns (places, objects)
        concrete_nouns = re.findall(r"\b(street|room|desk|chair|car|train|office|kitchen|bed|phone|door|window|face|hand|eye|voice)\b", scene_lower)
        if len(concrete_nouns) >= 3:
            s += 0.30
        elif len(concrete_nouns) >= 1:
            s += 0.15
        scores.append(min(1.0, s))
    return round(sum(scores) / max(len(scores), 1), 3)


def score_topic_mechanism_clarity(full_text: str, chapters: List[str], topic: str) -> float:
    """Check if the psychological mechanism is clearly named in body terms, early in the book."""
    if not chapters:
        return 0.0
    MECHANISM_KEYWORDS = {
        "anxiety": ["nervous system", "alarm", "threat response", "amygdala", "body responds", "fight or flight"],
        "burnout": ["capacity", "depletion", "stress cycle", "nervous system", "complete the cycle"],
        "grief": ["absence", "waves", "pattern", "grief response", "longing", "severed connection"],
        "self_worth": ["mechanism", "translation", "automatic", "verdict", "external event"],
        "depression": ["distance", "glass", "detachment", "numbness", "anhedonia", "flat response"],
        "boundaries": ["limit", "gate", "exposure fear", "fawn response", "body alarm"],
        "imposter_syndrome": ["exposure fear", "competence", "credibility gap", "fraud response"],
        "overthinking": ["thought chain", "spiral", "rumination loop", "cognitive loop"],
        "compassion_fatigue": ["empathy drain", "secondary trauma", "capacity limit", "vicarious"],
        "courage": ["action impulse", "threat response", "body alarm", "fight-flight"],
        "financial_anxiety": ["threat response", "scarcity signal", "stress response", "body tightens"],
        "financial_stress": ["scarcity", "threat", "stress cycle", "fight-or-flight"],
        "sleep_anxiety": ["hyperarousal", "sleep pressure", "cortisol", "alarm", "sleep drive"],
        "social_anxiety": ["threat detection", "evaluation fear", "exposure", "shame response"],
        "somatic_healing": ["body memory", "somatic response", "nervous system", "tissue", "fascia"],
    }
    mechanism_kws = MECHANISM_KEYWORDS.get(topic, [])
    if not mechanism_kws:
        return 0.5
    score = 0.0
    # Named in first 2 chapters
    early_text = " ".join(chapters[:2]).lower()
    early_hits = sum(1 for kw in mechanism_kws if kw in early_text)
    if early_hits >= 2:
        score += 0.50
    elif early_hits >= 1:
        score += 0.30
    # Named in body terms (not just cognitive)
    full_lower = full_text.lower()
    body_mechanism = any(kw in full_lower for kw in ["nervous system", "body", "sensation", "physical", "somatic", "breath", "chest", "stomach"])
    if body_mechanism:
        score += 0.30
    # Mechanism present in total book
    total_hits = sum(1 for kw in mechanism_kws if kw in full_lower)
    if total_hits >= 3:
        score += 0.20
    elif total_hits >= 1:
        score += 0.10
    return round(min(1.0, score), 3)


def score_voice_consistency(chapters: List[str], topic: str) -> float:
    """Voice consistency: register variance, prohibited term presence."""
    if not chapters:
        return 0.0
    score = 1.0
    all_text = " ".join(chapters).lower()
    # Penalize prohibited global terms
    for term in GLOBAL_PROHIBITED:
        if term in all_text:
            score -= 0.05
    # Penalize topic-specific prohibited terms
    topic_terms = TOPIC_PROHIBITED.get(topic, frozenset())
    for term in topic_terms:
        if term in all_text:
            score -= 0.08
    # Check sentence length variance consistency (not wild swings chapter to chapter)
    length_vars = []
    for ch in chapters:
        sents = [len(s.split()) for s in re.split(r"[.!?]+", ch) if s.strip()]
        if len(sents) >= 2:
            avg = sum(sents) / len(sents)
            var = sum((l - avg) ** 2 for l in sents) / len(sents)
            length_vars.append(var)
    if length_vars:
        var_of_vars = max(length_vars) - min(length_vars) if len(length_vars) > 1 else 0
        if var_of_vars > 200:
            score -= 0.10
        elif var_of_vars > 100:
            score -= 0.05
    return round(max(0.0, min(1.0, score)), 3)


# ── Qwen LLM scoring (optional, for validation) ──

def qwen_score_dimension(text: str, dimension: str, topic: str, persona: str) -> Optional[float]:
    """
    Call Qwen on Pearl Star for LLM-validated dimension scoring.
    Returns float 0-1 or None on failure.
    Only used for validation — heuristic scores are primary.
    """
    prompts = {
        "opening_hook_strength": f"""Rate the opening hook quality of this therapeutic audiobook chapter for topic='{topic}' persona='{persona}'.
Score 0.0-1.0 where:
- 1.0: Names a specific recognizable behavior, uses second-person present, has a pattern-naming sentence, punchy short opening
- 0.5: Some direct address, but abstract or unclear
- 0.0: Generic, clinical, or uses "journey"/"heal"/"transform" language

Text (first 500 words):
{text[:1500]}

Respond with ONLY a float like: 0.72""",
        "exercise_quality": f"""Rate the exercise quality in this therapeutic audiobook section for topic='{topic}'.
Score 0.0-1.0 where:
- 1.0: Specific body part named, time indicator (X breaths, Y seconds), doable while listening (no writing/mirror)
- 0.5: Somewhat specific but missing time anchor or body part
- 0.0: Vague ("take a moment to reflect"), requires visual/writing

Text:
{text[:1500]}

Respond with ONLY a float like: 0.63""",
    }
    prompt = prompts.get(dimension)
    if not prompt:
        return None
    try:
        payload = json.dumps({
            "model": QWEN_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 20},
        }).encode("utf-8")
        req = Request(f"{QWEN_HOST}/api/generate", data=payload, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        response_text = result.get("response", "").strip()
        # Extract float from response
        match = re.search(r"(\d+\.\d+|\d+)", response_text)
        if match:
            val = float(match.group(1))
            return max(0.0, min(1.0, val))
    except (URLError, json.JSONDecodeError, ValueError, OSError):
        pass
    return None


# ── Composite scoring per book ──

def score_book(topic: str, persona: str, registry: Dict[str, Any], use_llm: bool = False) -> Dict[str, Any]:
    """Score one topic × persona combination."""
    chapters = extract_chapter_texts(registry)
    if not chapters:
        return {"error": "no chapters extracted"}

    chapter_texts = [ch["full_text"] for ch in chapters]
    exercise_texts = []
    scene_texts = []
    hook_text = chapters[0]["hook_text"] if chapters else ""

    for ch in chapters:
        exercise_texts.extend(ch["exercise_texts"])
        scene_texts.extend(ch["scene_texts"])

    full_text = "\n\n".join(chapter_texts)

    # ── Existing EI heuristic dimensions ──
    dims = {}
    dims["safety_score"] = score_safety(full_text)
    dims["tts_readability"] = score_tts_readability_heuristic(full_text)
    dims["domain_similarity"] = score_domain_similarity(full_text, topic, persona)
    dims["emotion_arc"] = score_emotion_arc(chapter_texts)
    dims["content_uniqueness"] = score_content_uniqueness(chapter_texts)
    dims["engagement"] = score_engagement(full_text)
    dims["somatic_precision"] = score_somatic_precision(full_text)
    dims["listen_experience"] = score_listen_experience(full_text)
    dims["cohesion"] = score_cohesion(chapter_texts)
    dims["duration_fit"] = score_duration_fit(chapter_texts, topic)

    # ── New research-backed dimensions ──
    dims["opening_hook_strength"] = score_opening_hook_strength(hook_text)
    dims["exercise_quality"] = score_exercise_quality(exercise_texts)
    dims["story_specificity"] = score_story_specificity(scene_texts)
    dims["topic_mechanism_clarity"] = score_topic_mechanism_clarity(full_text, chapter_texts, topic)
    dims["voice_consistency"] = score_voice_consistency(chapter_texts, topic)

    # ── Optional Qwen LLM validation (opening hook + exercise) ──
    if use_llm:
        llm_hook = qwen_score_dimension(hook_text, "opening_hook_strength", topic, persona)
        if llm_hook is not None:
            # Blend heuristic (70%) + LLM (30%)
            dims["opening_hook_strength"] = round(0.7 * dims["opening_hook_strength"] + 0.3 * llm_hook, 3)
        if exercise_texts:
            llm_ex = qwen_score_dimension(exercise_texts[0], "exercise_quality", topic, persona)
            if llm_ex is not None:
                dims["exercise_quality"] = round(0.7 * dims["exercise_quality"] + 0.3 * llm_ex, 3)

    # ── Composite ──
    # Weighted composite across all 15 dimensions
    weights = {
        "safety_score": 0.10,
        "tts_readability": 0.08,
        "domain_similarity": 0.08,
        "emotion_arc": 0.08,
        "content_uniqueness": 0.05,
        "engagement": 0.08,
        "somatic_precision": 0.08,
        "listen_experience": 0.08,
        "cohesion": 0.06,
        "duration_fit": 0.05,
        "opening_hook_strength": 0.08,
        "exercise_quality": 0.08,
        "story_specificity": 0.05,
        "topic_mechanism_clarity": 0.06,
        "voice_consistency": 0.05,
    }
    composite = sum(dims.get(k, 0.0) * w for k, w in weights.items())
    composite = round(composite, 3)

    # ── Strengths / weaknesses ──
    sorted_dims = sorted(dims.items(), key=lambda x: x[1], reverse=True)
    strengths = [k for k, v in sorted_dims[:3] if v >= 0.6]
    weaknesses = [k for k, v in sorted_dims if v < 0.5][:3]

    # ── Enhancement ideas ──
    ideas = []
    if dims["opening_hook_strength"] < 0.6:
        ideas.append("Rewrite ch1 HOOK F1 to name specific behavior in 2nd person present with pattern-naming sentence")
    if dims["exercise_quality"] < 0.6:
        ideas.append("Add body part + time indicator (e.g., '3 breaths', '10 seconds') to all EXERCISE sections")
    if dims["story_specificity"] < 0.5:
        ideas.append("Add 3+ concrete sensory details (place, object, sound) to every SCENE/STORY variant")
    if dims["topic_mechanism_clarity"] < 0.5:
        ideas.append("Name the psychological mechanism in body terms in chapters 1-2")
    if dims["voice_consistency"] < 0.7:
        ideas.append("Audit for prohibited terms from topic_skins.yaml; tighten register consistency")
    if dims["cohesion"] < 0.5:
        ideas.append("Add backward-linking phrases ('as we saw', 'building on') to chapters 2+")
    if dims["somatic_precision"] < 0.5:
        ideas.append("Increase body-word density (shoulder, breath, chest, jaw) — target 4+ body words per 100 words")

    return {
        "book_id": f"{persona}__{topic}",
        "topic": topic,
        "persona": persona,
        "chapter_count": len(chapters),
        "total_words": len(full_text.split()),
        "dimensions": dims,
        "composite": composite,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "enhancement_ideas": ideas,
    }


def main():
    parser = argparse.ArgumentParser(description="Deep catalog scoring — 15 topics × 3 personas")
    parser.add_argument("--topic", help="Score only this topic")
    parser.add_argument("--skip-llm", action="store_true", help="Skip Qwen LLM validation")
    parser.add_argument("--output", default=str(OUTPUT_DIR / "catalog_deep_scores.json"))
    args = parser.parse_args()

    use_llm = not args.skip_llm

    topics = [args.topic] if args.topic else CANONICAL_TOPICS
    personas = CANONICAL_PERSONAS

    scored_books = []
    errors = []
    start = time.time()

    print(f"\n{'='*60}")
    print(f"Deep Catalog Scoring — {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"Topics: {len(topics)} | Personas: {len(personas)} | LLM: {'Qwen@Pearl Star' if use_llm else 'disabled'}")
    print(f"{'='*60}\n")

    # Test Qwen connectivity
    if use_llm:
        try:
            req = Request(f"{QWEN_HOST}/api/tags", headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=5) as resp:
                resp.read()
            print(f"  [OK] Qwen reachable at {QWEN_HOST}")
        except Exception:
            print(f"  [WARN] Qwen not reachable at {QWEN_HOST} — running heuristic-only")
            use_llm = False

    for topic in topics:
        print(f"\nTopic: {topic}")
        registry = load_registry(topic)
        if registry is None:
            print(f"  [SKIP] No registry for {topic}")
            errors.append({"topic": topic, "error": "no registry"})
            continue

        for persona in personas:
            print(f"  Scoring {persona} × {topic} ...", end=" ", flush=True)
            t0 = time.time()
            try:
                result = enrich_catalog_book_result(
                    score_book(topic, persona, registry, use_llm=use_llm),
                    topic,
                )
                elapsed = round(time.time() - t0, 2)
                print(f"composite={result['composite']:.3f} ({elapsed}s)")
                scored_books.append(result)
            except Exception as e:
                print(f"ERROR: {e}")
                errors.append({"topic": topic, "persona": persona, "error": str(e)})

    total_elapsed = round(time.time() - start, 2)

    # ── Cross-dimensional analysis ──
    all_composites = [b["composite"] for b in scored_books]
    composite_mean = round(sum(all_composites) / max(len(all_composites), 1), 4)

    # Per-topic aggregates
    topic_composites = {}
    for t in topics:
        tc = [b["composite"] for b in scored_books if b["topic"] == t]
        if tc:
            topic_composites[t] = round(sum(tc) / len(tc), 4)

    # Per-dimension aggregates
    all_dims = {}
    for dim in scored_books[0]["dimensions"].keys() if scored_books else []:
        vals = [b["dimensions"].get(dim, 0.0) for b in scored_books]
        all_dims[dim] = {
            "mean": round(sum(vals) / max(len(vals), 1), 4),
            "min": round(min(vals), 4),
            "max": round(max(vals), 4),
            "p25": round(sorted(vals)[len(vals) // 4], 4) if vals else 0.0,
            "p50": round(sorted(vals)[len(vals) // 2], 4) if vals else 0.0,
            "p75": round(sorted(vals)[3 * len(vals) // 4], 4) if vals else 0.0,
        }

    # Weakest and strongest topics
    strongest_topic = max(topic_composites, key=topic_composites.get) if topic_composites else "N/A"
    weakest_topic = min(topic_composites, key=topic_composites.get) if topic_composites else "N/A"

    # Systemic weaknesses (dims where >50% of books score < 0.5)
    systemic_weak = []
    for dim, stats in all_dims.items():
        below_half = sum(1 for b in scored_books if b["dimensions"].get(dim, 0.0) < 0.5)
        if below_half > len(scored_books) * 0.5:
            systemic_weak.append({"dimension": dim, "mean": stats["mean"], "fail_rate": round(below_half / max(len(scored_books), 1), 3)})
    systemic_weak.sort(key=lambda x: x["mean"])

    output = {
        "scored_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scoring_method": "heuristic_15_dims" + ("_plus_qwen_llm" if not args.skip_llm else ""),
        "truth_source": TRUTH_SOURCE_LEGACY_REGISTRY,
        "default_sellability_truth_source": DEFAULT_SELLABILITY_UNIQUENESS_TRUTH_SOURCE,
        "sellability_truth": False,
        "corpus_warning": LEGACY_REGISTRY_WARNING,
        "note": "Scores registry/{topic}.yaml atom pools — NOT shipped spine books.",
        "qwen_host": QWEN_HOST if use_llm else None,
        "topics_scored": len(set(b["topic"] for b in scored_books)),
        "personas_scored": len(set(b["persona"] for b in scored_books)),
        "total_books": len(scored_books),
        "total_elapsed_s": total_elapsed,
        "errors": errors,
        "summary": {
            "composite_mean": composite_mean,
            "composite_target": 0.75,
            "strongest_topic": strongest_topic,
            "strongest_composite": topic_composites.get(strongest_topic, 0.0),
            "weakest_topic": weakest_topic,
            "weakest_composite": topic_composites.get(weakest_topic, 0.0),
            "by_topic": topic_composites,
            "by_dimension": all_dims,
            "systemic_weaknesses": systemic_weak,
        },
        "books": scored_books,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"SCORING COMPLETE")
    print(f"  Books scored: {len(scored_books)}")
    print(f"  Composite mean: {composite_mean:.4f} (target: 0.75+)")
    print(f"  Strongest topic: {strongest_topic} ({topic_composites.get(strongest_topic, 0):.4f})")
    print(f"  Weakest topic: {weakest_topic} ({topic_composites.get(weakest_topic, 0):.4f})")
    print(f"  Systemic weaknesses: {[s['dimension'] for s in systemic_weak]}")
    print(f"  Errors: {len(errors)}")
    print(f"  Elapsed: {total_elapsed}s")
    print(f"  Output: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
