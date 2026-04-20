"""
Regression Museum — Pearl News detectors.

Five blocking failure classes (INV-1 through INV-6):
  pearl_news_multi_teacher_article
  pearl_news_topic_duplication_in_run
  pearl_news_language_mismatch
  pearl_news_missing_layout_shell
  pearl_news_missing_sidebar

Each function returns list[Violation]. Zero LLM spend. Deterministic.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml
except ImportError:
    _yaml = None


@dataclass
class Violation:
    failure_class: str
    severity: str       # "block" | "warn"
    location: str       # e.g. "article_abc123.json"
    evidence: str       # excerpt that tripped the gate
    description: str


# ---------------------------------------------------------------------------
# Teacher language map — mirrors TEACHER_LANGUAGE in run_daily_news_cycle.py
# Used to validate language field without importing the script.
# ---------------------------------------------------------------------------
TEACHER_LANGUAGE: dict[str, str] = {
    "ahjan": "en",
    "sai_ma": "en",
    "ra": "en",
    "pamela_fellows": "en",
    "maat": "en",
    "junko": "ja",
    "miki": "ja",
    "joshin": "ja",
    "master_feung": "zh-cn",
    "master_wu": "zh-cn",
}

_BYLINE_RE = re.compile(r'class="pn-byline"', re.IGNORECASE)
_SIDEBAR_RE = re.compile(r'<aside[^>]+class="pn-sidebar"', re.IGNORECASE)
_INTERFAITH_TEMPLATE = "interfaith_dialogue_report"


def _load_article(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _article_files(run_dir: Path) -> list[Path]:
    return sorted(p for p in run_dir.glob("article_*.json") if p.is_file())


# ---------------------------------------------------------------------------
# INV-2: One article = one teacher
# ---------------------------------------------------------------------------
def detect_pearl_news_multi_teacher_article(run_dir: Path) -> list[Violation]:
    """
    Flag articles where teacher_id is None in a non-interfaith template.
    The pipeline's resolve_teacher() always picks one teacher; None means
    either the fallback group teacher fired on a template that shouldn't use
    group voice, or teacher resolution failed entirely.
    """
    violations: list[Violation] = []
    for path in _article_files(run_dir):
        art = _load_article(path)
        template = art.get("article_type", "")
        teacher_id = art.get("teacher_id")
        teacher_used_id = (art.get("teacher_used") or {}).get("teacher_id")

        if template == _INTERFAITH_TEMPLATE:
            continue  # group voice is permitted for this template

        if teacher_id is None and teacher_used_id is None:
            violations.append(Violation(
                failure_class="pearl_news_multi_teacher_article",
                severity="block",
                location=path.name,
                evidence=f"teacher_id=None, teacher_used.teacher_id=None, template={template!r}",
                description=(
                    "Article has no teacher assigned. "
                    "Every non-interfaith article must have exactly one teacher."
                ),
            ))
    return violations


# ---------------------------------------------------------------------------
# INV-4: No duplicate topics within a run
# ---------------------------------------------------------------------------
def detect_pearl_news_topic_duplication_in_run(
    run_dir: Path,
    max_per_topic: int = 2,
) -> list[Violation]:
    """
    Flag when more than max_per_topic articles share the same topic in a run.

    Default max_per_topic=2: with 10 teachers and 7 available topics, some
    topic sharing is unavoidable. The allocator minimizes duplication; this
    detector blocks egregious cases (same topic appearing in 3+ articles)
    which indicate the allocator was bypassed or broken.

    Set max_per_topic=1 for strict uniqueness enforcement (useful for smaller
    teacher sets where the teacher count ≤ topic count).
    """
    topic_to_files: dict[str, list[str]] = {}
    for path in _article_files(run_dir):
        art = _load_article(path)
        topic = (art.get("topic") or "").strip().lower()
        if not topic:
            continue
        topic_to_files.setdefault(topic, []).append(path.name)

    violations: list[Violation] = []
    for topic, files in topic_to_files.items():
        if len(files) > max_per_topic:
            violations.append(Violation(
                failure_class="pearl_news_topic_duplication_in_run",
                severity="block",
                location=", ".join(files),
                evidence=f"topic={topic!r} appears in {len(files)} articles: {files}",
                description=(
                    f"Topic '{topic}' is shared by {len(files)} articles in this run "
                    f"(threshold: {max_per_topic}). "
                    "The topic allocator should prevent this — check allocate_teacher_topics()."
                ),
            ))
    return violations


# ---------------------------------------------------------------------------
# INV-3: Language = teacher's assigned language
# ---------------------------------------------------------------------------
def detect_pearl_news_language_mismatch(run_dir: Path) -> list[Violation]:
    """
    Flag articles whose language field does not match TEACHER_LANGUAGE[teacher_id].
    Articles with no teacher_id (group voice) are skipped.
    """
    violations: list[Violation] = []
    for path in _article_files(run_dir):
        art = _load_article(path)
        teacher_id = art.get("teacher_id") or (art.get("teacher_used") or {}).get("teacher_id")
        if not teacher_id:
            continue  # group voice — no language constraint
        article_lang = (art.get("language") or "").strip().lower()
        expected_lang = TEACHER_LANGUAGE.get(teacher_id, "").strip().lower()
        if not expected_lang:
            continue  # unknown teacher, can't validate
        if article_lang != expected_lang:
            violations.append(Violation(
                failure_class="pearl_news_language_mismatch",
                severity="block",
                location=path.name,
                evidence=(
                    f"teacher_id={teacher_id!r}, "
                    f"article.language={article_lang!r}, "
                    f"expected={expected_lang!r}"
                ),
                description=(
                    f"Teacher '{teacher_id}' must write in '{expected_lang}' "
                    f"but article language is '{article_lang}'."
                ),
            ))
    return violations


# ---------------------------------------------------------------------------
# INV-5: Layout shell (byline) present
# ---------------------------------------------------------------------------
def detect_pearl_news_missing_layout_shell(run_dir: Path) -> list[Violation]:
    """
    Flag articles whose content HTML is missing the .pn-byline block.
    """
    violations: list[Violation] = []
    for path in _article_files(run_dir):
        art = _load_article(path)
        content = art.get("content") or ""
        if not _BYLINE_RE.search(content):
            violations.append(Violation(
                failure_class="pearl_news_missing_layout_shell",
                severity="block",
                location=path.name,
                evidence='No class="pn-byline" found in article content',
                description=(
                    "Article content is missing the teacher byline block (.pn-byline). "
                    "INV-5 requires a byline with teacher name, tradition, language, and date."
                ),
            ))
    return violations


# ---------------------------------------------------------------------------
# INV-6: Sidebar present
# ---------------------------------------------------------------------------
def detect_pearl_news_missing_sidebar(run_dir: Path) -> list[Violation]:
    """
    Flag articles missing the sidebar block in content HTML or the sidebar JSON field.
    """
    violations: list[Violation] = []
    for path in _article_files(run_dir):
        art = _load_article(path)
        content = art.get("content") or ""
        sidebar = art.get("sidebar") or {}

        html_missing = not _SIDEBAR_RE.search(content)
        json_missing = not sidebar.get("teacher_name")

        if html_missing or json_missing:
            evidence_parts = []
            if html_missing:
                evidence_parts.append('No <aside class="pn-sidebar"> in content HTML')
            if json_missing:
                evidence_parts.append("sidebar.teacher_name missing from article JSON")
            violations.append(Violation(
                failure_class="pearl_news_missing_sidebar",
                severity="block",
                location=path.name,
                evidence="; ".join(evidence_parts),
                description=(
                    "Article is missing sidebar. INV-6 requires an <aside class=\"pn-sidebar\"> "
                    "HTML block and a populated sidebar JSON field."
                ),
            ))
    return violations


# ---------------------------------------------------------------------------
# Composite runner — check all Pearl News invariants against a run directory
# ---------------------------------------------------------------------------
def run_museum_gates_pearl_news(run_dir: Path) -> dict:
    """
    Run all 5 Pearl News museum detectors against run_dir.
    Returns a dict: {blocked, violations, counts}.
    """
    all_violations: list[Violation] = []
    for fn in [
        detect_pearl_news_multi_teacher_article,
        detect_pearl_news_topic_duplication_in_run,
        detect_pearl_news_language_mismatch,
        detect_pearl_news_missing_layout_shell,
        detect_pearl_news_missing_sidebar,
    ]:
        try:
            all_violations.extend(fn(run_dir))
        except Exception as e:
            all_violations.append(Violation(
                failure_class=fn.__name__,
                severity="block",
                location=str(run_dir),
                evidence=str(e),
                description=f"Detector raised exception: {e}",
            ))

    blocked = any(v.severity == "block" for v in all_violations)
    return {
        "blocked": blocked,
        "run_dir": str(run_dir),
        "article_count": len(_article_files(run_dir)),
        "violation_count": len(all_violations),
        "violations": [
            {
                "failure_class": v.failure_class,
                "severity": v.severity,
                "location": v.location,
                "evidence": v.evidence,
                "description": v.description,
            }
            for v in all_violations
        ],
    }
