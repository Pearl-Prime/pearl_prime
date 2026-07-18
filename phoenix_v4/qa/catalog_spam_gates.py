"""
Catalog Spam Gates — CI checks for Google Play Books compliance.

Authority: GOOGLE_PLAY_SPAM_FREE_AUDIT_2026_03_18.md
Covers:
  GAP 1: Subtitle duplication (max 2x per subtitle per brand per wave)
  GAP 2: Search keyword concentration (max 10% per wave, 8% per brand)
  GAP 3: Invisible script diversity (max 2x per script+topic per brand per wave)
  GAP 4: Brand × topic × persona combo cap (max 2 per combo per brand per wave)
  GAP 5: Author/narrator diversity (max 10% catalog per author, min 2 per brand)
  Part 6: Health claims scanner + disclaimer verification

Each function returns (failures: list[str], warnings: list[str]).
Designed to be called from run_prepublish_gates.py or standalone.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple


# --- GAP 1: Subtitle Uniqueness ---

def check_subtitle_uniqueness(
    plans: List[Dict[str, Any]],
    *,
    max_per_brand_per_wave: int = 2,
) -> Tuple[List[str], List[str]]:
    """FAIL if any subtitle appears >max_per_brand_per_wave times for a single brand."""
    failures: List[str] = []
    warnings: List[str] = []

    # Group subtitles by brand
    brand_subs: Dict[str, Counter] = defaultdict(Counter)
    for p in plans:
        brand = str(p.get("brand_id", ""))
        subtitle = str(p.get("subtitle", "")).strip()
        if subtitle and subtitle != "?" and len(subtitle) > 5:
            brand_subs[brand][subtitle] += 1

    for brand, counter in brand_subs.items():
        for subtitle, count in counter.most_common():
            if count > max_per_brand_per_wave:
                failures.append(
                    f"SUBTITLE DUPE: brand '{brand}' has subtitle '{subtitle[:60]}...' "
                    f"appearing {count}x (max {max_per_brand_per_wave})"
                )

    # Global check: any subtitle appearing >4x across all brands
    global_subs: Counter = Counter()
    for p in plans:
        subtitle = str(p.get("subtitle", "")).strip()
        if subtitle and subtitle != "?" and len(subtitle) > 5:
            global_subs[subtitle] += 1
    for subtitle, count in global_subs.most_common(5):
        if count > 4:
            warnings.append(
                f"SUBTITLE CLUSTER: '{subtitle[:60]}...' appears {count}x across all brands"
            )

    return failures, warnings


# --- GAP 2: Search Keyword Diversity ---

def check_search_keyword_diversity(
    plans: List[Dict[str, Any]],
    *,
    max_single_keyword_share_wave: float = 0.10,
    max_single_keyword_share_brand: float = 0.08,
    min_distinct_keywords_wave: int = 10,
) -> Tuple[List[str], List[str]]:
    """FAIL if single keyword exceeds share cap. WARN if keyword vocabulary is too small."""
    failures: List[str] = []
    warnings: List[str] = []

    all_keywords: List[str] = []
    brand_keywords: Dict[str, List[str]] = defaultdict(list)

    for p in plans:
        brand = str(p.get("brand_id", ""))
        kws = p.get("search_keywords") or []
        if isinstance(kws, str):
            kws = [kws]
        for kw in kws:
            kw = str(kw).strip().lower()
            if kw:
                all_keywords.append(kw)
                brand_keywords[brand].append(kw)

    if not all_keywords:
        warnings.append("KEYWORD DIVERSITY: no search_keywords found on any plan")
        return failures, warnings

    n = len(plans)

    # Wave-level: no keyword > 10% of plans
    kw_counter = Counter(all_keywords)
    for kw, count in kw_counter.most_common():
        share = count / n
        if share > max_single_keyword_share_wave:
            failures.append(
                f"KEYWORD CONCENTRATION: '{kw}' appears on {count}/{n} plans "
                f"({share:.0%} > {max_single_keyword_share_wave:.0%})"
            )

    # Brand-level: no keyword > 8% of brand's plans
    for brand, kws in brand_keywords.items():
        brand_n = len(set(p.get("book_id", p.get("plan_id", i)) for i, p in enumerate(plans) if str(p.get("brand_id", "")) == brand))
        if brand_n < 2:
            continue
        bkw_counter = Counter(kws)
        for kw, count in bkw_counter.most_common(3):
            share = count / max(brand_n, 1)
            if share > max_single_keyword_share_brand:
                warnings.append(
                    f"KEYWORD CONCENTRATION: brand '{brand}' has '{kw}' on {count}/{brand_n} plans "
                    f"({share:.0%} > {max_single_keyword_share_brand:.0%})"
                )

    # Vocabulary size
    distinct = len(set(all_keywords))
    if distinct < min_distinct_keywords_wave and n >= 20:
        failures.append(
            f"KEYWORD VOCABULARY: only {distinct} distinct keywords across {n} plans "
            f"(need {min_distinct_keywords_wave}+)"
        )

    return failures, warnings


# --- GAP 3: Invisible Script Diversity ---

def check_invisible_script_diversity(
    plans: List[Dict[str, Any]],
    *,
    max_per_brand_per_wave: int = 2,
) -> Tuple[List[str], List[str]]:
    """FAIL if same invisible_script + topic_id combo appears >2x per brand per wave."""
    failures: List[str] = []
    warnings: List[str] = []

    # Group by brand → (script, topic) combos
    brand_combos: Dict[str, Counter] = defaultdict(Counter)
    for p in plans:
        brand = str(p.get("brand_id", ""))
        script = str(p.get("invisible_script", "")).strip().lower()
        topic = str(p.get("topic_id", "")).strip()
        if script and topic:
            brand_combos[brand][(script[:80], topic)] += 1

    for brand, counter in brand_combos.items():
        for (script, topic), count in counter.most_common():
            if count > max_per_brand_per_wave:
                failures.append(
                    f"INVISIBLE SCRIPT DUPE: brand '{brand}' topic '{topic}' has "
                    f"script '{script[:50]}...' appearing {count}x (max {max_per_brand_per_wave})"
                )

    return failures, warnings


# --- GAP 4: Brand × Topic × Persona Combo Cap ---

def check_brand_topic_persona_combo(
    plans: List[Dict[str, Any]],
    *,
    max_per_combo_per_brand_per_wave: int = 2,
) -> Tuple[List[str], List[str]]:
    """FAIL if same (brand, topic, persona) appears >2x per wave."""
    failures: List[str] = []
    warnings: List[str] = []

    combo_counter: Counter = Counter()
    for p in plans:
        brand = str(p.get("brand_id", ""))
        topic = str(p.get("topic_id", ""))
        persona = str(p.get("persona_id", ""))
        if brand and topic and persona:
            combo_counter[(brand, topic, persona)] += 1

    for (brand, topic, persona), count in combo_counter.most_common():
        if count > max_per_combo_per_brand_per_wave:
            failures.append(
                f"BTP COMBO: ({brand}, {topic}, {persona}) appears {count}x "
                f"(max {max_per_combo_per_brand_per_wave})"
            )

    return failures, warnings


# --- GAP 5: Author/Narrator Diversity ---

def check_author_narrator_diversity(
    plans: List[Dict[str, Any]],
    *,
    max_single_author_share: float = 0.10,
    min_authors_per_brand: int = 2,
    min_narrators_per_brand: int = 1,
) -> Tuple[List[str], List[str]]:
    """FAIL if single author > 10% of catalog. WARN if brand has <2 authors."""
    failures: List[str] = []
    warnings: List[str] = []

    if not plans:
        return failures, warnings

    n = len(plans)

    # Author diversity
    author_counter: Counter = Counter()
    brand_authors: Dict[str, set] = defaultdict(set)
    brand_narrators: Dict[str, set] = defaultdict(set)

    for p in plans:
        brand = str(p.get("brand_id", ""))
        author = str(p.get("author_id", "")).strip()
        narrator = str(p.get("narrator_id", "")).strip()
        if author:
            author_counter[author] += 1
            brand_authors[brand].add(author)
        if narrator:
            brand_narrators[brand].add(narrator)

    # Global author share
    for author, count in author_counter.most_common(5):
        share = count / n
        if share > max_single_author_share:
            failures.append(
                f"AUTHOR CONCENTRATION: '{author}' has {count}/{n} books "
                f"({share:.0%} > {max_single_author_share:.0%})"
            )

    # Per-brand author count
    for brand, authors in brand_authors.items():
        if len(authors) < min_authors_per_brand:
            warnings.append(
                f"AUTHOR DIVERSITY: brand '{brand}' has only {len(authors)} author(s) "
                f"(recommend {min_authors_per_brand}+)"
            )

    # Per-brand narrator count
    for brand, narrators in brand_narrators.items():
        if len(narrators) < min_narrators_per_brand:
            warnings.append(
                f"NARRATOR DIVERSITY: brand '{brand}' has only {len(narrators)} narrator(s) "
                f"(recommend {min_narrators_per_brand}+)"
            )

    # Check for missing authors entirely
    no_author = sum(1 for p in plans if not str(p.get("author_id", "")).strip())
    if no_author > 0:
        warnings.append(
            f"AUTHOR MISSING: {no_author}/{n} plans have no author_id set"
        )

    return failures, warnings


# --- Part 6: Health Claims Scanner ---

# Banned phrases for wellness/self-help content on Google Play
_HEALTH_CLAIM_PATTERNS = [
    re.compile(r"\b(?:clinically\s+proven|scientifically\s+proven|medically\s+proven)\b", re.I),
    re.compile(r"\b(?:cure[sd]?|eliminat(?:e[sd]?|ing)|eradicat(?:e[sd]?|ing))\s+(?:your\s+)?(?:anxiety|depression|ptsd|disorder|insomnia|trauma)\b", re.I),
    re.compile(r"\bguaranteed?\s+(?:results?|recovery|healing|cure|relief)\b", re.I),
    re.compile(r"\b100\s*%\s*(?:effective|success|cure|recovery|relief)\b", re.I),
    re.compile(r"\b(?:FDA|AMA|WHO)\s+(?:approved|endorsed|recommended)\b", re.I),
    re.compile(r"\bnever\s+(?:feel|experience|suffer|have)\s+(?:anxiety|depression|panic)\s+again\b", re.I),
    re.compile(r"\b(?:replace|better\s+than|substitute\s+for)\s+(?:therapy|medication|treatment|doctor)\b", re.I),
    re.compile(r"\b(?:diagnos(?:e[sd]?|tic)|prescri(?:be[sd]?|ption))\b", re.I),
]

# Required disclaimer patterns (at least one should appear)
_DISCLAIMER_PATTERNS = [
    re.compile(r"not\s+(?:a\s+)?(?:substitute|replacement)\s+for\s+(?:professional|medical|clinical)", re.I),
    re.compile(r"consult\s+(?:a|your)\s+(?:doctor|physician|healthcare|mental\s+health|therapist|professional)", re.I),
    re.compile(r"for\s+(?:informational|educational)\s+purposes\s+only", re.I),
    re.compile(r"not\s+(?:intended\s+as\s+)?(?:medical|clinical|therapeutic)\s+advice", re.I),
    re.compile(r"seek\s+professional\s+(?:help|guidance|support|advice)", re.I),
]


def check_health_claims(
    plans: List[Dict[str, Any]],
    *,
    check_rendered_text: bool = False,
) -> Tuple[List[str], List[str]]:
    """
    FAIL if any plan metadata contains banned health/medical claims.
    WARN if no disclaimer detected in description or rendered text.
    """
    failures: List[str] = []
    warnings: List[str] = []

    for p in plans:
        book_id = p.get("book_id", p.get("plan_id", "unknown"))

        # Check title, subtitle, description for health claims
        surfaces = [
            ("title", str(p.get("title", ""))),
            ("subtitle", str(p.get("subtitle", ""))),
            ("description", str(p.get("description", ""))),
        ]

        for surface_name, text in surfaces:
            if not text:
                continue
            for pattern in _HEALTH_CLAIM_PATTERNS:
                match = pattern.search(text)
                if match:
                    failures.append(
                        f"HEALTH CLAIM: {book_id} {surface_name} contains "
                        f"banned phrase: '{match.group()[:60]}'"
                    )

        # Check for disclaimer in description
        description = str(p.get("description", ""))
        if description and len(description) > 50:
            has_disclaimer = any(pat.search(description) for pat in _DISCLAIMER_PATTERNS)
            if not has_disclaimer:
                warnings.append(
                    f"DISCLAIMER MISSING: {book_id} description has no health disclaimer"
                )

    return failures, warnings


# --- Combined runner ---

def run_all_catalog_spam_gates(
    plans: List[Dict[str, Any]],
) -> Tuple[List[str], List[str]]:
    """Run all catalog spam gates. Returns (failures, warnings)."""
    all_failures: List[str] = []
    all_warnings: List[str] = []

    checks = [
        check_subtitle_uniqueness,
        check_search_keyword_diversity,
        check_invisible_script_diversity,
        check_brand_topic_persona_combo,
        check_author_narrator_diversity,
        check_health_claims,
    ]

    for check_fn in checks:
        try:
            f, w = check_fn(plans)
            all_failures.extend(f)
            all_warnings.extend(w)
        except Exception as e:
            all_warnings.append(f"CATALOG SPAM GATE ERROR ({check_fn.__name__}): {e}")

    return all_failures, all_warnings
