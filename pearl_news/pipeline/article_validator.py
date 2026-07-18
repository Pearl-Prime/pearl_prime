"""
Pearl News — hard post-generation validation gates.
Runs after LLM expansion. Any FAIL → article flagged for manual review.
On FAIL: caller should retry once (already handled in run_expansion), then flag.

Gates:
  1. six_sections_present  — <h1> lede, news_summary, youth_impact, teacher, sdg, forward_look
  2. named_teacher         — teacher section contains a named teacher (not generic placeholder)
  3. teacher_three_points  — teacher section has 3 distinct substantive paragraphs
  4. sdg_number_present    — SDG number (e.g. "SDG 16" or "SDG16") appears in content
  5. sdg_full_title        — a known SDG title keyword appears near the SDG number
  6. youth_anchor          — youth/impact section has at least one anchor (number/%, place, age band)
  7. no_banned_phrases     — none of the "never write" phrases appear in content
  8. source_line_present   — Source: line at end is preserved
"""
from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Known SDG keywords (title fragments) for gate 5
# ---------------------------------------------------------------------------
_SDG_TITLE_KEYWORDS = {
    "1": ["no poverty", "poverty"],
    "2": ["zero hunger", "hunger", "food security"],
    "3": ["good health", "well-being", "wellbeing", "health"],
    "4": ["quality education", "education"],
    "5": ["gender equality", "gender"],
    "6": ["clean water", "sanitation"],
    "7": ["affordable energy", "clean energy"],
    "8": ["decent work", "economic growth", "employment"],
    "9": ["industry", "innovation", "infrastructure"],
    "10": ["reduced inequalit", "inequality"],
    "11": ["sustainable cities", "communities"],
    "12": ["responsible consumption", "production"],
    "13": ["climate action", "climate"],
    "14": ["life below water", "ocean"],
    "15": ["life on land", "biodiversity"],
    "16": ["peace", "justice", "strong institutions"],
    "17": ["partnerships", "global goals"],
}

# ---------------------------------------------------------------------------
# Banned phrases (from PEARL_NEWS_WRITER_SPEC.md §10 / expansion_system.txt)
# ---------------------------------------------------------------------------
_BANNED_PHRASES = [
    r"young people around the world are feeling",
    r"now more than ever",
    r"in these uncertain times",
    r"historic\b.{0,30}(agreement|summit|accord|resolution|decision)",  # without context
    r"landmark\b.{0,30}(agreement|summit|accord|resolution|decision)",
    r"pearl news.{0,40}(affiliated|affiliation|partner|partnership) with the united nations",
    r"in a world where",
    r"as \w+ continues to",
    r"\bwe\b",  # avoid "we" in articles
]

# Teacher generic placeholder phrases — if these appear, named_teacher gate fails
_GENERIC_TEACHER_PHRASES = [
    "a teacher from the united spiritual leaders forum",
    "a spiritual leader says",
    "teachers believe",
    "forum collectively",
]

# Youth anchor patterns
_YOUTH_ANCHOR_PATTERNS = [
    r"\b\d+\s*%",               # percentage e.g. "47%"
    r"\b\d[\d,\.]+\s*(million|billion|thousand)\b",  # large numbers
    r"\b(gen z|gen alpha|generation z|generation alpha)\b",  # named generation
    r"\bages?\s+\d+",            # age band e.g. "ages 15-28"
    r"\b\d+\s*(to|-)\s*\d+\s*year",  # age range
    r"\b(japan|china|india|nigeria|brazil|indonesia|philippines|mexico|uk|us|usa|australia)\b",  # named country
    r"\b(tokyo|beijing|shanghai|jakarta|nairobi|lagos|sao paulo|london|new york)\b",  # named city
]

# ---------------------------------------------------------------------------
# Gate functions
# ---------------------------------------------------------------------------

def _has_h1(content: str) -> bool:
    return bool(re.search(r"<h1[^>]*>", content, re.IGNORECASE))


def _count_paragraphs(content: str) -> int:
    return len(re.findall(r"<p[^>]*>", content, re.IGNORECASE))


def _teacher_section_text(content: str) -> str:
    """Best-effort: extract text near teacher-related keywords."""
    lower = content.lower()
    idx = -1
    for keyword in ["teacher perspective", "tradition", "teaches that", "spiritual"]:
        i = lower.find(keyword)
        if i != -1:
            idx = i
            break
    if idx == -1:
        return ""
    return content[max(0, idx - 200): idx + 2000]


def _youth_section_text(content: str) -> str:
    """Best-effort: extract text in the youth impact section."""
    lower = content.lower()
    idx = lower.find("youth")
    if idx == -1:
        idx = lower.find("young")
    if idx == -1:
        return content  # fallback: check whole article
    return content[max(0, idx - 100): idx + 3000]


def _is_cjk_locale(language: str | None) -> bool:
    l = (language or "en").strip().lower()
    if l in {"ja", "ko", "zh-cn", "zh-tw", "zh-hk", "zh-sg", "vi", "zh"}:
        return True
    return l.startswith("zh-")


def gate_six_sections_present(content: str, language: str | None = None) -> tuple[bool, str]:
    """Check that all 6 required sections are present (proxied by structural signals)."""
    lower = content.lower()
    youth_ok = any(k in lower for k in ["youth", "young people", "gen z", "gen alpha", "adolescent"])
    teacher_ok = any(k in lower for k in ["tradition", "teaches that", "teach", "teacher"])
    forward_ok = any(
        k in lower for k in ["upcoming", "next", "will", "deadline", "summit", "vote", "action", "can "]
    )
    source_ok = "source:" in lower
    if _is_cjk_locale(language):
        youth_ok = youth_ok or any(x in content for x in ("若者", "青年", "年轻人", "Z世代", "z世代", "世代"))
        teacher_ok = teacher_ok or any(x in content for x in ("伝統", "教え", "老师", "教師", "스승"))
        forward_ok = forward_ok or any(x in content for x in ("今後", "予定", "即将", "将", "来月", "다음", "예정"))
        source_ok = source_ok or "出典" in content or "来源" in content
    checks = {
        "lede (<h1>)": _has_h1(content),
        "news_summary (≥2 <p>)": _count_paragraphs(content) >= 2,
        "youth_impact": youth_ok,
        "teacher_perspective": teacher_ok,
        "sdg_connection": bool(re.search(r"sdg\s*\d+", lower) or "sustainable development goal" in lower),
        "forward_look": forward_ok,
        "source_line": source_ok,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        return False, f"Missing sections: {', '.join(failed)}"
    return True, "all 6 sections present"


def gate_named_teacher(content: str, language: str | None = None) -> tuple[bool, str]:
    """Teacher section must not be the generic placeholder."""
    lower = content.lower()
    for phrase in _GENERIC_TEACHER_PHRASES:
        if phrase in lower:
            return False, f"Generic teacher placeholder detected: '{phrase}'"
    has_tradition = "tradition" in lower
    has_teaches = "teaches that" in lower
    if _is_cjk_locale(language):
        has_tradition = has_tradition or "伝統" in content or "传统" in content
        has_teaches = has_teaches or "教え" in content or "教导" in content
    if not (has_tradition or has_teaches):
        return False, "No named teacher attribution found (missing 'tradition' or 'teaches that')"
    return True, "named teacher present"


def gate_teacher_three_points(content: str, language: str | None = None) -> tuple[bool, str]:
    """Teacher section should have at least 3 substantive paragraphs."""
    teacher_text = _teacher_section_text(content)
    paras = re.findall(r"<p[^>]*>(.+?)</p>", teacher_text, re.IGNORECASE | re.DOTALL)
    min_words = 20
    if _is_cjk_locale(language):
        substantive = [
            p
            for p in paras
            if len(p.strip().split()) >= min_words or len(re.sub(r"<[^>]+>", "", p).strip()) >= 40
        ]
    else:
        substantive = [p for p in paras if len(p.strip().split()) >= min_words]
    if len(substantive) < 3:
        return False, f"Teacher section has only {len(substantive)} substantive paragraphs (need ≥3)"
    return True, f"teacher has {len(substantive)} substantive paragraphs"


def gate_sdg_number(content: str) -> tuple[bool, str]:
    """SDG number must appear in content."""
    if re.search(r"SDG\s*\d+|sustainable development goal\s*\d+", content, re.IGNORECASE):
        return True, "SDG number present"
    return False, "No SDG number found (e.g. 'SDG 13' or 'Sustainable Development Goal 13')"


def gate_sdg_full_title(content: str, primary_sdg: str) -> tuple[bool, str]:
    """A keyword from the SDG's full title must appear near the SDG number."""
    keywords = _SDG_TITLE_KEYWORDS.get(str(primary_sdg), [])
    if not keywords:
        return True, f"No keyword list for SDG {primary_sdg} — skipped"
    lower = content.lower()
    for kw in keywords:
        if kw.lower() in lower:
            return True, f"SDG title keyword '{kw}' found"
    return False, f"SDG {primary_sdg} title keywords not found (expected one of: {keywords[:3]})"


def gate_youth_anchor(content: str) -> tuple[bool, str]:
    """Youth section must have at least one concrete anchor."""
    youth_text = _youth_section_text(content)
    for pattern in _YOUTH_ANCHOR_PATTERNS:
        if re.search(pattern, youth_text, re.IGNORECASE):
            return True, f"Youth anchor found (pattern: {pattern[:30]})"
    return False, "No concrete youth anchor found (need number/%, place, or age band in youth section)"


def gate_no_banned_phrases(content: str) -> tuple[bool, str]:
    """None of the banned phrases should appear."""
    for phrase in _BANNED_PHRASES:
        if re.search(phrase, content, re.IGNORECASE):
            return False, f"Banned phrase detected: '{phrase}'"
    return True, "no banned phrases"


def gate_source_line(content: str, language: str | None = None) -> tuple[bool, str]:
    """Source: line must be preserved at end (localized labels allowed for CJK)."""
    lower = content.lower()
    if "source:" in lower or "<em>source:" in lower:
        return True, "Source line present"
    if _is_cjk_locale(language):
        if "出典" in content or "来源" in content:
            return True, "Source line present (localized label)"
    return False, "Source line missing — was stripped during expansion"


# ---------------------------------------------------------------------------
# Run all gates
# ---------------------------------------------------------------------------

def validate_article(
    content: str,
    primary_sdg: str = "17",
    strict: bool = True,
    language: str | None = None,
) -> dict[str, Any]:
    """
    Run all validation gates on expanded article content.
    Returns:
      passed: bool — True if all required gates pass
      gates: dict of gate_name → {passed, message}
      failed_gates: list of gate names that failed
      retry_recommended: bool — True if any required gate failed
    """
    results: dict[str, dict] = {}

    # Run gates
    gates_to_run = [
        ("six_sections_present", gate_six_sections_present(content, language=language)),
        ("named_teacher", gate_named_teacher(content, language=language)),
        ("teacher_three_points", gate_teacher_three_points(content, language=language)),
        ("sdg_number", gate_sdg_number(content)),
        ("sdg_full_title", gate_sdg_full_title(content, primary_sdg)),
        ("youth_anchor", gate_youth_anchor(content)),
        ("no_banned_phrases", gate_no_banned_phrases(content)),
        ("source_line", gate_source_line(content, language=language)),
    ]

    for gate_name, (passed, message) in gates_to_run:
        results[gate_name] = {"passed": passed, "message": message}

    failed_gates = [name for name, r in results.items() if not r["passed"]]
    all_passed = len(failed_gates) == 0

    return {
        "passed": all_passed,
        "gates": results,
        "failed_gates": failed_gates,
        "retry_recommended": not all_passed,
        "gate_count": len(gates_to_run),
        "passed_count": len(gates_to_run) - len(failed_gates),
    }


def run_validation(
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Run validation on all items. Attaches _validation result to each item.
    Items that fail are flagged _validation_failed=True and _needs_manual_review=True.
    """
    for item in items:
        content = item.get("content") or ""
        primary_sdg = str(item.get("primary_sdg") or "17")
        if not content:
            item["_validation"] = {"passed": False, "failed_gates": ["no_content"], "gates": {}}
            item["_validation_failed"] = True
            item["_needs_manual_review"] = True
            continue

        result = validate_article(
            content,
            primary_sdg=primary_sdg,
            language=str(item.get("language") or "en").lower(),
        )
        if item.get("_ei_hard_fail"):
            failed = list(result.get("failed_gates") or [])
            if "ei_v2_hard_fail" not in failed:
                failed.append("ei_v2_hard_fail")
            gates = dict(result.get("gates") or {})
            gates["ei_v2_hard_fail"] = {"passed": False, "message": "EI v2 safety or stealth block"}
            gc = int(result.get("gate_count") or 0) + 1
            result = {
                **result,
                "passed": False,
                "failed_gates": failed,
                "gates": gates,
                "retry_recommended": True,
                "gate_count": gc,
                "passed_count": max(0, gc - len(failed)),
            }
        item["_validation"] = result
        item["_validation_failed"] = not result["passed"]
        item["_needs_manual_review"] = (not result["passed"]) or item.get("_needs_manual_review", False)

        if not result["passed"]:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "Article %s failed validation gates: %s",
                item.get("id"), result["failed_gates"],
            )
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                "Article %s passed all %d validation gates",
                item.get("id"), result["gate_count"],
            )

    return items
