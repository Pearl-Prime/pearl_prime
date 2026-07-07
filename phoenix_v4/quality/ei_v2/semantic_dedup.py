"""
Semantic duplication detection for EI V2.

Detects near-duplicate atoms that surface text matching misses:
  - N-gram overlap (character and word level)
  - Structural similarity (sentence count, paragraph shape)
  - Narrative beat fingerprinting (inciting incident, turn, cost, resolution)

Two modes:
  - "ngram_plus_embedding": N-gram overlap + structural similarity.
    No external model needed.
  - "full": Adds embedding-based semantic similarity via embed_fn callback.

Returns pairs of candidates flagged as potential duplicates with
similarity scores and evidence.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Callable, Dict, List, Mapping, Optional, Set, Tuple

# Composite weights for atom-pool dedup (slot candidates). Do not use for
# within-book chapter uniqueness — beat/structure are intentional there.
ATOM_POOL_WEIGHTS: Dict[str, float] = {
    "ngram": 0.35,
    "char_ngram": 0.15,
    "structural": 0.25,
    "beat": 0.25,
}


def _word_ngrams(text: str, n: int) -> Set[str]:
    """Extract word-level n-grams from text."""
    words = re.findall(r"\b\w+\b", (text or "").lower())
    if len(words) < n:
        return set()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def _char_ngrams(text: str, n: int = 4) -> Set[str]:
    """Extract character-level n-grams (for fuzzy matching)."""
    t = (text or "").lower()
    if len(t) < n:
        return set()
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union) if union else 0.0


def _sentence_count(text: str) -> int:
    return len(re.split(r"[.!?]+", text.strip())) if text.strip() else 0


def _paragraph_shape(text: str) -> List[int]:
    """Return list of word counts per paragraph (structural fingerprint)."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [len(p.split()) for p in paragraphs]


def _shape_similarity(shape_a: List[int], shape_b: List[int]) -> float:
    """Compare paragraph shape vectors. 1.0 = identical structure."""
    if not shape_a or not shape_b:
        return 0.0
    if len(shape_a) != len(shape_b):
        len_sim = min(len(shape_a), len(shape_b)) / max(len(shape_a), len(shape_b))
    else:
        len_sim = 1.0

    min_len = min(len(shape_a), len(shape_b))
    if min_len == 0:
        return 0.0

    diffs = []
    for i in range(min_len):
        max_wc = max(shape_a[i], shape_b[i], 1)
        diffs.append(1.0 - abs(shape_a[i] - shape_b[i]) / max_wc)

    return (sum(diffs) / len(diffs)) * len_sim


# Narrative beat markers (heuristic fingerprinting for story atoms).
_BEAT_PATTERNS = {
    "inciting_incident": [
        re.compile(r"\b(?:that\s+(?:morning|day|night|moment)|one\s+(?:morning|day|night)|it\s+started\s+when)\b", re.I),
        re.compile(r"\b(?:the\s+(?:first|last)\s+time|the\s+moment\s+(?:when|that))\b", re.I),
    ],
    "escalation": [
        re.compile(r"\b(?:and\s+then|it\s+got\s+worse|each\s+time|every\s+day|kept\s+(?:going|growing|building))\b", re.I),
    ],
    "turning_point": [
        re.compile(r"\b(?:but\s+then|until\s+(?:one|that)|something\s+(?:shifted|changed|broke)|that'?s\s+when)\b", re.I),
    ],
    "cost_moment": [
        re.compile(r"\b(?:the\s+cost|what\s+it\s+cost|the\s+price|lost|gave\s+up|sacrificed|missed)\b", re.I),
    ],
    "resolution_or_open": [
        re.compile(r"\b(?:still|not\s+(?:yet|sure|done)|what\s+(?:comes|happens)\s+next|the\s+next\s+room)\b", re.I),
    ],
}


def _beat_fingerprint(text: str) -> Dict[str, bool]:
    """Detect narrative beats present in text."""
    result = {}
    for beat, patterns in _BEAT_PATTERNS.items():
        result[beat] = any(p.search(text) for p in patterns)
    return result


def _beat_similarity(fp_a: Dict[str, bool], fp_b: Dict[str, bool]) -> float:
    """Jaccard on narrative beat presence."""
    all_beats = set(fp_a.keys()) | set(fp_b.keys())
    if not all_beats:
        return 0.0
    match = sum(1 for b in all_beats if fp_a.get(b) == fp_b.get(b))
    return match / len(all_beats)


def _pair_evidence(
    text_a: str,
    text_b: str,
    *,
    ngram_n: int,
    weights: Mapping[str, float],
) -> Dict[str, Any]:
    """Similarity evidence for one text pair."""
    ngrams_a = _word_ngrams(text_a, ngram_n)
    ngrams_b = _word_ngrams(text_b, ngram_n)
    ngram_sim = _jaccard(ngrams_a, ngrams_b)

    char_a = _char_ngrams(text_a, 4)
    char_b = _char_ngrams(text_b, 4)
    char_sim = _jaccard(char_a, char_b)

    shape_a = _paragraph_shape(text_a)
    shape_b = _paragraph_shape(text_b)
    struct_sim = _shape_similarity(shape_a, shape_b)

    beats_a = _beat_fingerprint(text_a)
    beats_b = _beat_fingerprint(text_b)
    beat_sim = _beat_similarity(beats_a, beats_b)

    w_n = float(weights.get("ngram", ATOM_POOL_WEIGHTS["ngram"]))
    w_c = float(weights.get("char_ngram", ATOM_POOL_WEIGHTS["char_ngram"]))
    w_s = float(weights.get("structural", ATOM_POOL_WEIGHTS["structural"]))
    w_b = float(weights.get("beat", ATOM_POOL_WEIGHTS["beat"]))
    composite = w_n * ngram_sim + w_c * char_sim + w_s * struct_sim + w_b * beat_sim

    prose_similarity = (
        float(weights.get("prose_ngram", 0.70)) * ngram_sim
        + float(weights.get("prose_char", 0.30)) * char_sim
    )

    return {
        "similarity": round(composite, 4),
        "prose_similarity": round(prose_similarity, 4),
        "ngram_overlap": round(ngram_sim, 4),
        "char_ngram_overlap": round(char_sim, 4),
        "structural_similarity": round(struct_sim, 4),
        "beat_similarity": round(beat_sim, 4),
    }


def _within_book_cfg(cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    base = dict((cfg or {}).get("within_book_chapter") or {})
    return {
        "ngram_n": int((cfg or {}).get("ngram_n", 6)),
        "prose_ngram_weight": float(base.get("prose_ngram_weight", 0.70)),
        "prose_char_weight": float(base.get("prose_char_weight", 0.30)),
        "ngram_penalty_floor": float(base.get("ngram_penalty_floor", 0.10)),
        "ngram_penalty_scale": float(base.get("ngram_penalty_scale", 3.0)),
        "max_compare_chapters": base.get("max_compare_chapters"),
    }


def analyze_chapter_content_uniqueness(
    chapter_text: str,
    chapter_index: int,
    all_chapter_texts: List[str],
    *,
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Score shipped-book chapter uniqueness with pair-level evidence.

    Within-book comparison penalizes **prose** near-duplicates (word/char
    n-gram overlap), not shared therapeutic beat markers or paragraph rhythm
    that are intentional across a Pearl Prime spine.
    """
    wb = _within_book_cfg(cfg)
    ngram_n = wb["ngram_n"]
    chapter_id = f"ch{chapter_index}"

    pairs: List[Dict[str, Any]] = []
    others: List[Tuple[int, str]] = [
        (j, t) for j, t in enumerate(all_chapter_texts) if j != chapter_index and t.strip()
    ]
    max_compare = wb["max_compare_chapters"]
    if isinstance(max_compare, int) and max_compare > 0:
        others = others[:max_compare]

    for other_index, other_text in others:
        ev = _pair_evidence(
            chapter_text,
            other_text,
            ngram_n=ngram_n,
            weights={
                **ATOM_POOL_WEIGHTS,
                "prose_ngram": wb["prose_ngram_weight"],
                "prose_char": wb["prose_char_weight"],
            },
        )
        pairs.append(
            {
                "id_a": chapter_id,
                "id_b": f"ch{other_index}",
                "similarity": ev["similarity"],
                "prose_similarity": ev["prose_similarity"],
                "evidence": {
                    "ngram_overlap": ev["ngram_overlap"],
                    "char_ngram_overlap": ev["char_ngram_overlap"],
                    "structural_similarity": ev["structural_similarity"],
                    "beat_similarity": ev["beat_similarity"],
                },
            }
        )

    if not pairs:
        return {
            "content_uniqueness": 1.0,
            "worst_pair": None,
            "pairs_compared": 0,
            "max_prose_similarity": 0.0,
            "scoring_mode": "within_book_chapter_prose_first",
        }

    pairs.sort(key=lambda p: p["prose_similarity"], reverse=True)
    worst = pairs[0]
    max_ngram = max(p["evidence"]["ngram_overlap"] for p in pairs)
    max_char = max(p["evidence"]["char_ngram_overlap"] for p in pairs)
    prose_sim = wb["prose_ngram_weight"] * max_ngram + wb["prose_char_weight"] * max_char
    floor = wb["ngram_penalty_floor"]
    scale = wb["ngram_penalty_scale"]
    uniqueness = max(0.0, 1.0 - max(0.0, prose_sim - floor) * scale)

    return {
        "content_uniqueness": round(uniqueness, 4),
        "worst_pair": worst,
        "pairs_compared": len(pairs),
        "max_prose_similarity": round(prose_sim, 4),
        "max_ngram_overlap": round(max_ngram, 4),
        "max_char_ngram_overlap": round(max_char, 4),
        "top_pairs": pairs[:5],
        "scoring_mode": "within_book_chapter_prose_first",
    }


def detect_semantic_duplicates(
    texts: List[str],
    ids: List[str],
    *,
    cfg: Optional[Dict[str, Any]] = None,
    embed_fn: Optional[Callable[[str, str], List[float]]] = None,
) -> List[Dict[str, Any]]:
    """
    Detect semantic duplicates among candidate texts.

    Returns list of pair dicts:
      {"id_a": str, "id_b": str, "similarity": float, "evidence": {...}}
    Only pairs above threshold are returned.
    """
    cfg = cfg or {}
    ngram_n = int(cfg.get("ngram_n", 6))
    ngram_threshold = float(cfg.get("ngram_overlap_threshold", 0.30))
    weights = cfg.get("weights") or ATOM_POOL_WEIGHTS

    duplicates: List[Dict[str, Any]] = []

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            text_a, text_b = texts[i], texts[j]
            id_a, id_b = ids[i], ids[j]

            ev = _pair_evidence(text_a, text_b, ngram_n=ngram_n, weights=weights)
            ngram_sim = ev["ngram_overlap"]
            composite = ev["similarity"]

            if composite >= ngram_threshold or ngram_sim >= ngram_threshold:
                duplicates.append({
                    "id_a": id_a,
                    "id_b": id_b,
                    "similarity": composite,
                    "evidence": {
                        "ngram_overlap": ev["ngram_overlap"],
                        "char_ngram_overlap": ev["char_ngram_overlap"],
                        "structural_similarity": ev["structural_similarity"],
                        "beat_similarity": ev["beat_similarity"],
                    },
                })

    duplicates.sort(key=lambda x: x["similarity"], reverse=True)
    return duplicates
