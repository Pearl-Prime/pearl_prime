#!/usr/bin/env python3
"""Metric library for the music-brand diversity gate (G1-G8).

Ratified thresholds (MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES,
docs/PEARL_ARCHITECT_STATE.md; restated in artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
row ws_pearl_dev_music_brand_diversity_ci_guard_20260611):

  G1 — per-slot-pool variant reuse    <= max(5, ceil(N/5))         HARD_FAIL
  G2 — topic concentration            <= 30%                       HARD_FAIL
  G3 — persona concentration          <= 30%                       HARD_FAIL
  G4 — format concentration           <= 50%                       HARD_FAIL
  G5 — locale concentration           per-platform (KDP US <= 70%, HARD_FAIL
                                       KDP JP <= 50%; other <= 60%)
  G6 — title fuzzy-similarity cluster <= ceil(N/20)                 WARN
  G7 — author-bio reuse               <= 60%                       WARN
  G8 — slot-atom rotation Gini        <= 0.4                       WARN

This module does NO I/O and takes only plain data structures (lists of strings /
dicts) so every metric is independently unit-testable. The CLI
(``scripts/ci/check_music_brand_diversity.py``) owns loading atoms/catalog metadata
from disk and applying the HARD_FAIL vs WARN / quality-profile / Phase-A
degraded-mode policy; this module only computes the numbers.

G1-G8 threshold source note: the cap amendment in ``docs/PEARL_ARCHITECT_STATE.md``
states the numeric thresholds; the ws-row restatement above matches it. Per the
lane's PRE-REQUISITE CHECKS, these constants are the ratified defaults either way.
"""
from __future__ import annotations

import math
from collections import Counter
from difflib import SequenceMatcher
from typing import Any, Mapping, Sequence

# --- G1: per-slot-pool variant reuse ---------------------------------------------
G1_MIN_CAP = 5
G1_N_DIVISOR = 5

# --- G2-G4: topic / persona / format concentration -------------------------------
G2_TOPIC_MAX = 0.30
G3_PERSONA_MAX = 0.30
G4_FORMAT_MAX = 0.50

# --- G5: locale concentration, per-platform tunable -------------------------------
G5_LOCALE_MAX_BY_PLATFORM: dict[str, float] = {
    "kdp_us": 0.70,
    "kdp_jp": 0.50,
}
G5_LOCALE_DEFAULT_MAX = 0.60  # conservative fallback for a platform not yet tuned

# --- G6: title fuzzy-similarity clustering ----------------------------------------
G6_TITLE_CLUSTER_DIVISOR = 20
G6_SIMILARITY_THRESHOLD = 0.85  # difflib.SequenceMatcher ratio treated as "near-dup"

# --- G7: author-bio reuse ----------------------------------------------------------
G7_AUTHOR_BIO_MAX = 0.60

# --- G8: slot-atom rotation Gini ---------------------------------------------------
G8_GINI_MAX = 0.40

# Below this many catalog book-plan rows, G2-G8 need catalog-scale N to be
# meaningful and are skipped rather than false-passed on n=3 synthetic-scale data
# (Phase-A degraded mode; only G1 runs at small N).
PHASE_A_N_THRESHOLD = 50


def normalize_text(text: Any) -> str:
    """Whitespace/case-insensitive normalization for reuse/similarity comparisons."""
    return " ".join(str(text or "").strip().lower().split())


# ---------------------------------------------------------------------------------
# G1 — per-slot-pool variant reuse
# ---------------------------------------------------------------------------------
def g1_variant_reuse_limit(n: int) -> int:
    """max(5, ceil(N/5)) — the reuse ceiling for a pool of N usage instances."""
    if n <= 0:
        return G1_MIN_CAP
    return max(G1_MIN_CAP, math.ceil(n / G1_N_DIVISOR))


def compute_variant_reuse(usages: Sequence[str]) -> dict[str, Any]:
    """G1 metric for ONE slot pool.

    ``usages`` is one entry per usage instance drawn from that pool: in Phase-A
    degraded mode (no catalog-scale book data yet) that is every variant body on
    every atom currently in the pool's bank directory (the anti-copy-paste check
    on the SOURCE pool itself); once catalog-scale data exists it becomes every
    chapter's actually-selected body across the brand's books.
    """
    n = len(usages)
    limit = g1_variant_reuse_limit(n)
    counts = Counter(normalize_text(u) for u in usages if str(u or "").strip())
    if not counts:
        return {"n": 0, "limit": limit, "max_reuse": 0, "top": None, "reused": {}, "violation": False}
    top_body, top_count = counts.most_common(1)[0]
    return {
        "n": n,
        "limit": limit,
        "max_reuse": top_count,
        "top": top_body,
        "reused": {body: count for body, count in counts.items() if count > 1},
        "violation": top_count > limit,
    }


# ---------------------------------------------------------------------------------
# G2-G5 — shared concentration helper (single most-common value's share of N)
# ---------------------------------------------------------------------------------
def concentration(values: Sequence[Any]) -> dict[str, Any]:
    cleaned = [str(v).strip() for v in values if str(v or "").strip()]
    n = len(cleaned)
    if n == 0:
        return {"n": 0, "top": None, "fraction": 0.0, "counts": {}}
    counts = Counter(cleaned)
    top_value, top_count = counts.most_common(1)[0]
    return {"n": n, "top": top_value, "fraction": top_count / n, "counts": dict(counts)}


def g2_topic_concentration(books: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = concentration([b.get("topic") for b in books])
    result["limit"] = G2_TOPIC_MAX
    result["violation"] = result["n"] > 0 and result["fraction"] > G2_TOPIC_MAX
    return result


def g3_persona_concentration(books: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = concentration([b.get("persona") for b in books])
    result["limit"] = G3_PERSONA_MAX
    result["violation"] = result["n"] > 0 and result["fraction"] > G3_PERSONA_MAX
    return result


def g4_format_concentration(books: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = concentration([b.get("format") for b in books])
    result["limit"] = G4_FORMAT_MAX
    result["violation"] = result["n"] > 0 and result["fraction"] > G4_FORMAT_MAX
    return result


def g5_locale_concentration(books: Sequence[Mapping[str, Any]], *, platform: str = "kdp_us") -> dict[str, Any]:
    limit = G5_LOCALE_MAX_BY_PLATFORM.get(str(platform or "").strip().lower(), G5_LOCALE_DEFAULT_MAX)
    result = concentration([b.get("locale") for b in books])
    result["platform"] = platform
    result["limit"] = limit
    result["violation"] = result["n"] > 0 and result["fraction"] > limit
    return result


# ---------------------------------------------------------------------------------
# G6 — title fuzzy-similarity clustering
# ---------------------------------------------------------------------------------
def title_similarity(a: str, b: str) -> float:
    """difflib ratio on normalized text — dependency-light, no heavy NLP deps."""
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def g6_title_clusters(
    titles: Sequence[str],
    *,
    threshold: float = G6_SIMILARITY_THRESHOLD,
) -> dict[str, Any]:
    """Union-find clustering of near-duplicate titles by pairwise difflib ratio."""
    cleaned = [str(t) for t in titles if str(t or "").strip()]
    n = len(cleaned)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            if title_similarity(cleaned[i], cleaned[j]) >= threshold:
                union(i, j)

    clusters: dict[int, list[str]] = {}
    for i in range(n):
        clusters.setdefault(find(i), []).append(cleaned[i])
    dup_clusters = [members for members in clusters.values() if len(members) > 1]
    limit = math.ceil(n / G6_TITLE_CLUSTER_DIVISOR) if n else 0
    return {
        "n": n,
        "limit": limit,
        "cluster_count": len(dup_clusters),
        "clusters": dup_clusters,
        "violation": len(dup_clusters) > limit,
    }


# ---------------------------------------------------------------------------------
# G7 — author-bio reuse
# ---------------------------------------------------------------------------------
def g7_author_bio_reuse(bios: Sequence[str]) -> dict[str, Any]:
    result = concentration([normalize_text(b) for b in bios])
    result["limit"] = G7_AUTHOR_BIO_MAX
    result["violation"] = result["n"] > 0 and result["fraction"] > G7_AUTHOR_BIO_MAX
    return result


# ---------------------------------------------------------------------------------
# G8 — slot-atom rotation Gini coefficient
# ---------------------------------------------------------------------------------
def gini_coefficient(values: Sequence[float]) -> float:
    """Standard Gini index on non-negative usage counts. 0 = perfectly even rotation."""
    vals = sorted(float(v) for v in values if v is not None)
    n = len(vals)
    total = sum(vals)
    if n == 0 or total == 0:
        return 0.0
    weighted = sum((i + 1) * v for i, v in enumerate(vals))
    return (2 * weighted) / (n * total) - (n + 1) / n


def g8_rotation_gini(usage_counts: Sequence[float]) -> dict[str, Any]:
    g = gini_coefficient(usage_counts)
    return {
        "n": len(usage_counts),
        "gini": g,
        "limit": G8_GINI_MAX,
        "violation": g > G8_GINI_MAX,
    }
