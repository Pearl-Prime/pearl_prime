"""Content-uniqueness truth sources — shipped spine vs legacy registry.

Pearl Prime sellability/uniqueness reporting must not treat
``registry/{topic}.yaml`` atom pools as shipped-book quality. This module
labels provenance explicitly and scores the canonical trigram-Jaccard metric
from ``scripts/analysis/score_catalog_deep.py`` against the correct corpus.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# ── Truth-source labels (stable contract for reports / dashboards) ──

TRUTH_SOURCE_SHIPPED_SPINE = "shipped_spine_book"
TRUTH_SOURCE_LEGACY_REGISTRY = "legacy_registry_artifact"

DEFAULT_SELLABILITY_UNIQUENESS_TRUTH_SOURCE = TRUTH_SOURCE_SHIPPED_SPINE

SCORER_TRIGRAM_JACCARD = "trigram_jaccard_cross_chapter"
SCORER_EI_V2_SEMANTIC_DEDUP = "ei_v2_semantic_dedup_chapter"

LEGACY_REGISTRY_WARNING = (
    "NOT shipped-book quality — scores legacy registry/{topic}.yaml section "
    "variants only. Do not use for sellability or SELLABLE_AS_IS claims."
)

SHIPPED_SPINE_NOTE = (
    "Shipped Pearl Prime spine output (--pipeline-mode spine); canonical "
    "sellability/uniqueness truth source."
)


@dataclass
class UniquenessTruthResult:
    """One content_uniqueness measurement with explicit provenance."""

    content_uniqueness: float
    truth_source: str
    scorer: str
    chapter_count: int
    topic_id: str = ""
    persona_id: str = ""
    book_path: str = ""
    registry_path: str = ""
    warning: str = ""
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "content_uniqueness": self.content_uniqueness,
            "truth_source": self.truth_source,
            "scorer": self.scorer,
            "chapter_count": self.chapter_count,
        }
        if self.topic_id:
            out["topic_id"] = self.topic_id
        if self.persona_id:
            out["persona_id"] = self.persona_id
        if self.book_path:
            out["book_path"] = self.book_path
        if self.registry_path:
            out["registry_path"] = self.registry_path
        if self.warning:
            out["warning"] = self.warning
        if self.note:
            out["note"] = self.note
        if self.extra:
            out.update(self.extra)
        return out

    @property
    def is_shipped_truth(self) -> bool:
        return self.truth_source == TRUTH_SOURCE_SHIPPED_SPINE

    @property
    def is_legacy_registry(self) -> bool:
        return self.truth_source == TRUTH_SOURCE_LEGACY_REGISTRY


def split_shipped_book_chapters(book_text: str) -> list[str]:
    """Split assembled ``book.txt`` into chapter bodies."""
    parts = re.split(r"\n(?=Chapter \d+)", book_text.strip())
    return [p.strip() for p in parts if p.strip()]


def _score_trigram(chapters: list[str]) -> float:
    from scripts.analysis.score_catalog_deep import score_content_uniqueness

    return score_content_uniqueness(chapters)


def score_from_registry(
    topic_id: str,
    *,
    registry_dir: Optional[Path] = None,
    persona_id: str = "",
) -> Optional[UniquenessTruthResult]:
    """Score legacy registry artifact — NOT shipped-book truth."""
    from scripts.analysis.score_catalog_deep import extract_chapter_texts, load_registry

    registry = load_registry(topic_id)
    if registry is None:
        return None
    chapters = extract_chapter_texts(registry)
    if not chapters:
        return None
    texts = [ch["full_text"] for ch in chapters]
    reg_path = (registry_dir or Path(__file__).resolve().parents[2] / "registry") / f"{topic_id}.yaml"
    return UniquenessTruthResult(
        content_uniqueness=_score_trigram(texts),
        truth_source=TRUTH_SOURCE_LEGACY_REGISTRY,
        scorer=SCORER_TRIGRAM_JACCARD,
        chapter_count=len(texts),
        topic_id=topic_id,
        persona_id=persona_id,
        registry_path=str(reg_path),
        warning=LEGACY_REGISTRY_WARNING,
    )


def score_from_shipped_book(
    book_path: Path | str,
    *,
    topic_id: str = "",
    persona_id: str = "",
) -> UniquenessTruthResult:
    """Score assembled spine ``book.txt`` — canonical sellability truth."""
    path = Path(book_path)
    text = path.read_text(encoding="utf-8")
    chapters = split_shipped_book_chapters(text)
    return UniquenessTruthResult(
        content_uniqueness=_score_trigram(chapters),
        truth_source=TRUTH_SOURCE_SHIPPED_SPINE,
        scorer=SCORER_TRIGRAM_JACCARD,
        chapter_count=len(chapters),
        topic_id=topic_id,
        persona_id=persona_id,
        book_path=str(path),
        note=SHIPPED_SPINE_NOTE,
    )


def compare_truth_sources(
    book_path: Path | str,
    topic_id: str,
    *,
    persona_id: str = "",
) -> dict[str, Any]:
    """Side-by-side shipped vs legacy registry for proof dashboards."""
    shipped = score_from_shipped_book(book_path, topic_id=topic_id, persona_id=persona_id)
    legacy = score_from_registry(topic_id, persona_id=persona_id)
    return {
        "topic_id": topic_id,
        "persona_id": persona_id,
        "default_sellability_truth_source": DEFAULT_SELLABILITY_UNIQUENESS_TRUTH_SOURCE,
        "shipped_spine_book": shipped.to_dict(),
        "legacy_registry_artifact": legacy.to_dict() if legacy else None,
        "measurement_path_divergence": (
            legacy is not None
            and shipped.content_uniqueness != legacy.content_uniqueness
        ),
    }


def assert_report_truth_source(report: dict[str, Any]) -> None:
    """Raise if a uniqueness report omits truth_source or mislabels registry as shipped."""
    src = report.get("truth_source")
    if not src:
        raise ValueError("content_uniqueness report missing required truth_source")
    if src == TRUTH_SOURCE_LEGACY_REGISTRY and not report.get("warning"):
        raise ValueError("legacy registry uniqueness report must carry warning label")
    if src == TRUTH_SOURCE_LEGACY_REGISTRY and report.get("sellability_truth") is True:
        raise ValueError("legacy registry path cannot be marked sellability_truth")


def enrich_catalog_book_result(result: dict[str, Any], topic: str) -> dict[str, Any]:
    """Tag a score_catalog_deep book row so it cannot masquerade as shipped quality."""
    enriched = dict(result)
    enriched["truth_source"] = TRUTH_SOURCE_LEGACY_REGISTRY
    enriched["scorer"] = SCORER_TRIGRAM_JACCARD
    enriched["sellability_truth"] = False
    enriched["warning"] = LEGACY_REGISTRY_WARNING
    enriched["registry_path"] = f"registry/{topic}.yaml"
    return enriched
