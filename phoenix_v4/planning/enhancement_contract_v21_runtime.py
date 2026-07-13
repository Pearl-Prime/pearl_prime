"""Runtime authority for Enhancement Contract V2.1 working-prior integrity.

This module keeps the V2.1 research-informed priors explicit and testable. It
does not decide creative quality; it fail-closes mechanical contradictions and
metadata gaps that would make the enhancement proof unauditable.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping, Sequence

SCHEMA_VERSION = "2.1.0"
PRIOR_SOURCE = "ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13"
TRADE_BOOK_CHAPTERS = 12

CHAPTER_ENGINE_SURFACES: tuple[str, ...] = (
    "VALIDATION_NORMALIZATION",
    "MECHANISM_EXPLANATION",
    "PRACTICE_APPLICATION",
    "TROUBLESHOOTING",
    "TRANSITION_GLUE",
    "CLOSING_TAKEAWAY",
    "PROPULSION",
)

PROOF_AND_EMBODIMENT_SURFACES: tuple[str, ...] = (
    "HOOK_STORY",
    "EXTERNAL_STORY",
    "AUTHOR_DISCLOSURE",
    "CASE_STUDY",
    "CITED_EVIDENCE",
)

OPTIONAL_ACCENT_SURFACES: tuple[str, ...] = (
    "QUOTE",
    "ENCOURAGEMENT",
    "REFLECTION_QUESTION",
    "AUTHOR_COMMENTARY",
    "WISDOM_ESSENCE",
)

COHESION_AND_CRAFT_SURFACES: tuple[str, ...] = (
    "CALLBACK_PLANT",
    "CALLBACK_RETURN",
    "MOTIF",
    "ANALOGY",
    "METAPHOR",
    "BRIDGE",
    "TRANSITION",
)

SURFACE_BUCKET_BY_CLASS: Dict[str, str] = {
    "QUOTE": "optional_accents",
    "ENCOURAGEMENT": "optional_accents",
    "REFLECTION_QUESTION": "optional_accents",
    "AUTHOR_COMMENTARY": "optional_accents",
    "WISDOM_ESSENCE": "optional_accents",
    "TROUBLESHOOTING": "chapter_engine",
    "CITED_EVIDENCE": "proof_and_embodiment",
    "EXTERNAL_STORY": "proof_and_embodiment",
    "AUTHOR_DISCLOSURE": "proof_and_embodiment",
    "ANALOGY": "cohesion_and_craft",
    "METAPHOR": "cohesion_and_craft",
    "CALLBACK_PLANT": "cohesion_and_craft",
    "CALLBACK_RETURN": "cohesion_and_craft",
}

COUNT_UNITS: Dict[str, str] = {
    "QUOTE": "borrowed_authority_block",
    "ENCOURAGEMENT": "substantial_encouragement_block",
    "REFLECTION_QUESTION": "standalone_reflection_prompt",
    "AUTHOR_COMMENTARY": "substantial_interpretive_commentary_block",
    "WISDOM_ESSENCE": "distilled_wisdom_block",
    "CITED_EVIDENCE": "evidence_block",
    "EXTERNAL_STORY": "substantial_vignette",
    "AUTHOR_DISCLOSURE": "substantial_first_person_disclosure",
    "ANALOGY": "major_explanatory_analogy",
    "METAPHOR": "developed_or_recurring_metaphor",
    "CALLBACK_RETURN": "meaningful_motif_return",
}

PREFERRED_POSITIONS: Dict[str, tuple[str, ...]] = {
    "QUOTE": ("before_HOOK", "before_THREAD"),
    "CITED_EVIDENCE": ("after_HOOK", "before_STORY"),
    "EXTERNAL_STORY": ("after_HOOK", "after_REFLECTION", "before_STORY"),
    "ENCOURAGEMENT": ("after_EXERCISE", "after_turning_point"),
    "TROUBLESHOOTING": ("after_INTEGRATION",),
    "REFLECTION_QUESTION": ("after_REFLECTION", "before_THREAD"),
    "AUTHOR_COMMENTARY": ("after_PIVOT", "after_EXERCISE", "after_REFLECTION", "before_THREAD"),
    "WISDOM_ESSENCE": ("after_REFLECTION", "before_THREAD"),
    "CALLBACK_RETURN": ("after_PIVOT", "before_THREAD"),
}

DISALLOWED_POSITIONS: Dict[str, tuple[str, ...]] = {
    "TROUBLESHOOTING": ("before_HOOK", "after_HOOK", "before_STORY"),
}

MEMO_OPTIONAL_PRIORS: Dict[str, Any] = {
    "target_accent_chapters": {"min": 5, "max": 7},
    "hard_max_accent_chapters": 8,
    "target_total_accents": {"min": 7, "max": 9},
    "hard_max_total_accents": 10,
    "max_accents_per_chapter": 2,
    "accent_free_chapters_minimum": 4,
}


def _as_mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) else []


def _scale_ceil(value: int, chapter_count: int, *, minimum: int = 0) -> int:
    if chapter_count <= 0:
        return minimum
    return max(minimum, -(-int(value) * int(chapter_count) // TRADE_BOOK_CHAPTERS))


def _scale_floor(value: int, chapter_count: int, *, minimum: int = 0) -> int:
    if chapter_count <= 0:
        return minimum
    return max(minimum, (int(value) * int(chapter_count)) // TRADE_BOOK_CHAPTERS)


def accent_class_bucket(accent_class: str) -> str:
    return SURFACE_BUCKET_BY_CLASS.get(str(accent_class or "").strip().upper(), "optional_accents")


def count_unit_for_surface(surface: str) -> str:
    return COUNT_UNITS.get(str(surface or "").strip().upper(), "tracked_surface")


def build_optional_accent_budget(
    *,
    chapter_count: int,
    max_accents_per_chapter: int = 2,
) -> Dict[str, Any]:
    """Return explicit 12-chapter priors plus scaled limits for the current book."""
    chapters = max(0, int(chapter_count or 0))
    memo = dict(MEMO_OPTIONAL_PRIORS)
    memo_target_chapters = dict(memo["target_accent_chapters"])
    memo_target_total = dict(memo["target_total_accents"])
    max_per_chapter = int(max_accents_per_chapter or memo["max_accents_per_chapter"])
    return {
        "prior_source": PRIOR_SOURCE,
        "memo_trade_book_chapters": TRADE_BOOK_CHAPTERS,
        "memo_target_accent_chapters": memo_target_chapters,
        "memo_hard_max_accent_chapters": int(memo["hard_max_accent_chapters"]),
        "memo_target_total_accents": memo_target_total,
        "memo_hard_max_total_accents": int(memo["hard_max_total_accents"]),
        "memo_max_accents_per_chapter": int(memo["max_accents_per_chapter"]),
        "memo_accent_free_chapters_minimum": int(memo["accent_free_chapters_minimum"]),
        "target_accent_chapters": {
            "min": _scale_ceil(int(memo_target_chapters["min"]), chapters, minimum=1 if chapters else 0),
            "max": _scale_ceil(int(memo_target_chapters["max"]), chapters, minimum=1 if chapters else 0),
        },
        "hard_max_accent_chapters": min(
            chapters,
            _scale_ceil(int(memo["hard_max_accent_chapters"]), chapters, minimum=1 if chapters else 0),
        ),
        "target_total_accents": {
            "min": _scale_ceil(int(memo_target_total["min"]), chapters, minimum=1 if chapters else 0),
            "max": _scale_ceil(int(memo_target_total["max"]), chapters, minimum=1 if chapters else 0),
        },
        "hard_max_total_accents": _scale_ceil(
            int(memo["hard_max_total_accents"]),
            chapters,
            minimum=max_per_chapter if chapters else 0,
        ),
        "max_accents_per_chapter": max_per_chapter,
        "accent_free_chapters_minimum": _scale_floor(
            int(memo["accent_free_chapters_minimum"]),
            chapters,
            minimum=0,
        ),
        "chapter_share_rounding": "ceil",
        "ceiling_interpretation": (
            "Class-level maxima are ceilings, not instructions to maximize every optional accent "
            "class simultaneously."
        ),
    }


def validate_optional_accent_budget(
    optional_budget: Mapping[str, Any],
    *,
    chapter_count: int,
) -> Dict[str, Any]:
    """Validate optional-accent math and actual assignment counts."""
    budget = _as_mapping(optional_budget)
    actual = _as_mapping(budget.get("actual"))
    target_chapters = _as_mapping(budget.get("target_accent_chapters"))
    target_total = _as_mapping(budget.get("target_total_accents"))
    hard_failures: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    def fail(code: str, detail: str, **extra: Any) -> None:
        hard_failures.append({"code": code, "detail": detail, **extra})

    def warn(code: str, detail: str, **extra: Any) -> None:
        warnings.append({"code": code, "detail": detail, **extra})

    chapters = max(0, int(chapter_count or 0))
    target_ch_min = int(target_chapters.get("min") or 0)
    target_ch_max = int(target_chapters.get("max") or 0)
    target_total_min = int(target_total.get("min") or 0)
    target_total_max = int(target_total.get("max") or 0)
    hard_max_chapters = int(budget.get("hard_max_accent_chapters") or 0)
    hard_max_total = int(budget.get("hard_max_total_accents") or 0)
    max_per_chapter = int(budget.get("max_accents_per_chapter") or 0)
    accent_free_min = int(budget.get("accent_free_chapters_minimum") or 0)

    if target_ch_min > target_ch_max:
        fail("impossible_optional_accent_arithmetic", "target_accent_chapters min exceeds max")
    if target_total_min > target_total_max:
        fail("impossible_optional_accent_arithmetic", "target_total_accents min exceeds max")
    if target_ch_max > hard_max_chapters:
        fail("impossible_optional_accent_arithmetic", "target_accent_chapters max exceeds hard chapter ceiling")
    if target_total_max > hard_max_total:
        fail("impossible_optional_accent_arithmetic", "target_total_accents max exceeds hard total ceiling")
    if hard_max_chapters > chapters:
        fail("invalid_optional_chapter_ceiling", "hard chapter ceiling exceeds chapter count")
    if max_per_chapter <= 0 and hard_max_total > 0:
        fail("impossible_optional_accent_arithmetic", "max_accents_per_chapter must be positive")
    if max_per_chapter * max(0, hard_max_chapters) < hard_max_total:
        warn(
            "unsupported_budget_capacity",
            "hard total ceiling is higher than hard chapter ceiling can physically host",
        )
    if accent_free_min + hard_max_chapters > chapters:
        fail("impossible_optional_accent_arithmetic", "accent-free minimum conflicts with hard chapter ceiling")

    assigned_total = int(actual.get("assigned_total_optional_accents") or 0)
    optional_chapter_count = int(actual.get("optional_accent_chapter_count") or 0)
    accent_free_count = int(actual.get("accent_free_chapter_count") or max(0, chapters - optional_chapter_count))
    per_chapter = _as_mapping(actual.get("per_chapter_optional_counts"))
    chapter_refs = [int(ch) for ch in _as_list(actual.get("chapters_with_optional_accents")) if str(ch).strip()]

    if assigned_total > hard_max_total:
        fail("hard_max_total_optional_accents_exceeded", "assigned optional accents exceed hard total ceiling")
    if optional_chapter_count > hard_max_chapters:
        fail("hard_max_optional_accent_chapters_exceeded", "optional-accent chapters exceed hard chapter ceiling")
    if accent_free_count < accent_free_min:
        fail("accent_free_minimum_not_met", "accent-free chapter minimum was not met")
    for raw_ch, raw_count in per_chapter.items():
        ch = int(raw_ch)
        count = int(raw_count)
        if ch < 1 or ch > chapters:
            fail("invalid_chapter_reference", "optional accent assigned outside book chapter range", chapter=ch)
        if count > max_per_chapter:
            fail("max_optional_accents_per_chapter_exceeded", "chapter exceeds optional accent ceiling", chapter=ch)
    for ch in chapter_refs:
        if ch < 1 or ch > chapters:
            fail("invalid_chapter_reference", "optional accent chapter reference outside book range", chapter=ch)

    if assigned_total < target_total_min:
        warn("supported_budget_underfill", "assigned optional accents are below target range")
    if optional_chapter_count < target_ch_min:
        warn("optional_accent_chapter_under_target", "optional-accent chapters are below target range")
    if optional_chapter_count > target_ch_max:
        warn("optional_accent_chapter_over_target", "optional-accent chapters are above target range")

    return {
        "status": "PASS" if not hard_failures else "FAIL",
        "hard_failures": hard_failures,
        "warnings": warnings,
    }


def _truth_metadata(row: Mapping[str, Any]) -> Dict[str, Any]:
    keys = _as_mapping(row.get("keys"))
    return _as_mapping(row.get("truth_metadata")) or _as_mapping(keys.get("truth_metadata"))


def _row_keys(row: Mapping[str, Any]) -> Dict[str, Any]:
    return _as_mapping(row.get("keys"))


def _has_any(mapping: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return any(str(mapping.get(key) or "").strip() for key in keys)


def _semantic_fingerprint(text: str) -> str:
    words = [w.lower() for w in str(text or "").split() if w.strip()]
    reduced = " ".join(words[:24])
    return hashlib.sha1(reduced.encode("utf-8")).hexdigest()[:12] if reduced else ""


def validate_contract_rows(
    *,
    accent_rows: Sequence[Mapping[str, Any]],
    core_surface_rows: Sequence[Mapping[str, Any]],
    chapter_count: int,
) -> Dict[str, Any]:
    """Validate row-level V2.1 metadata and cohesion invariants."""
    hard_failures: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    def fail(code: str, detail: str, **extra: Any) -> None:
        hard_failures.append({"code": code, "detail": detail, **extra})

    def warn(code: str, detail: str, **extra: Any) -> None:
        warnings.append({"code": code, "detail": detail, **extra})

    chapters = max(0, int(chapter_count or 0))
    analogy_fingerprints: Dict[str, int] = {}
    metaphor_fingerprints: Dict[str, int] = {}

    for row in accent_rows:
        cls = str(row.get("class") or "").strip().upper()
        chapter = int(row.get("chapter") or 0)
        accent_id = str(row.get("accent_id") or "")
        if chapter < 1 or chapter > chapters:
            fail("invalid_chapter_reference", "accent row chapter is outside book range", chapter=chapter, accent_id=accent_id)
        keys = _row_keys(row)
        truth = _truth_metadata(row)
        if cls == "EXTERNAL_STORY":
            story_function = str(row.get("story_function") or keys.get("story_function") or "").strip()
            if story_function not in {"recognition", "mechanism_proof", "turn", "possibility", "cautionary"}:
                fail("external_story_missing_function", "EXTERNAL_STORY needs a supported function tag", chapter=chapter, accent_id=accent_id)
            if not _has_any(truth, ("source", "source_url", "source_title")):
                fail("external_story_missing_source", "EXTERNAL_STORY needs source metadata", chapter=chapter, accent_id=accent_id)
            if not _has_any(truth, ("citation", "source", "source_url")):
                fail("external_story_missing_citation", "EXTERNAL_STORY needs citation metadata", chapter=chapter, accent_id=accent_id)
            if not _has_any(truth, ("truth_status", "rights_class", "verification_status")):
                fail("external_story_missing_truth_status", "EXTERNAL_STORY needs truth/rights status", chapter=chapter, accent_id=accent_id)
        if cls == "CITED_EVIDENCE":
            if not _has_any(truth, ("citation", "source", "source_url")):
                fail("cited_evidence_missing_citation", "CITED_EVIDENCE needs a citation", chapter=chapter, accent_id=accent_id)
            if not _has_any(truth, ("truth_status", "robustness", "verification_status", "year")):
                fail("cited_evidence_missing_verification", "CITED_EVIDENCE needs verification metadata", chapter=chapter, accent_id=accent_id)
            if not _has_any(truth, ("claim", "claim_supported")) and not str(row.get("selected_body_excerpt") or row.get("final_excerpt") or "").strip():
                fail("cited_evidence_missing_claim", "CITED_EVIDENCE needs a claim or rendered claim excerpt", chapter=chapter, accent_id=accent_id)
        if cls == "AUTHOR_DISCLOSURE":
            if not _has_any(keys, ("author_id", "author_authority", "authorized_source", "author_voice_authorized")):
                fail("author_voice_missing_authorization", "AUTHOR_DISCLOSURE needs explicit author authorization metadata", chapter=chapter, accent_id=accent_id)
        if cls == "AUTHOR_COMMENTARY" and str(keys.get("author_voice_type") or "").strip() == "disclosure":
            fail("author_voice_classification_mismatch", "AUTHOR_COMMENTARY row is marked as disclosure", chapter=chapter, accent_id=accent_id)
        story_type = str(keys.get("story_type") or row.get("story_type") or "").strip().lower()
        story_register = str(keys.get("story_register") or row.get("story_register") or "").strip().lower()
        if cls == "PARABLE" or story_type == "parable" or story_register == "parable":
            if cls not in {"EXTERNAL_STORY", "HOOK_STORY", "STORY"}:
                fail("invalid_parable_container", "parable must be carried by a story-like surface", chapter=chapter, accent_id=accent_id)
        if cls in {"ANALOGY", "METAPHOR"}:
            fp = str(keys.get("semantic_fingerprint") or "") or _semantic_fingerprint(
                str(row.get("selected_body_excerpt") or row.get("final_excerpt") or row.get("rendered_excerpt") or "")
            )
            if not fp:
                continue
            bucket = analogy_fingerprints if cls == "ANALOGY" else metaphor_fingerprints
            bucket[fp] = bucket.get(fp, 0) + 1

    for cls, bucket in (("ANALOGY", analogy_fingerprints), ("METAPHOR", metaphor_fingerprints)):
        for fp, count in bucket.items():
            if count > 1:
                warn("repeated_semantic_fingerprint", f"{cls} repeats semantic fingerprint", surface=cls, fingerprint=fp, count=count)

    plants: Dict[str, tuple[int, int]] = {}
    returns: List[Mapping[str, Any]] = []
    for idx, row in enumerate(core_surface_rows):
        role = str(row.get("callback_role") or "").strip()
        plant_id = str(row.get("plant_id") or "").strip()
        if not plant_id:
            continue
        chapter = int(row.get("chapter") or 0)
        order = int(row.get("final_order_index") if row.get("final_order_index") is not None else idx)
        if role == "plant":
            plants.setdefault(plant_id, (chapter, order))
        elif role == "return":
            returns.append(row)

    for row in returns:
        plant_id = str(row.get("plant_id") or "").strip()
        chapter = int(row.get("chapter") or 0)
        order = int(row.get("final_order_index") if row.get("final_order_index") is not None else 999999)
        plant_pos = plants.get(plant_id)
        if not plant_pos or plant_pos >= (chapter, order):
            fail("callback_return_without_prior_plant", "CALLBACK_RETURN needs a real prior plant", chapter=chapter, plant_id=plant_id)
        if not str(row.get("semantic_development") or "").strip():
            fail("callback_return_without_semantic_development", "CALLBACK_RETURN needs semantic development metadata", chapter=chapter, plant_id=plant_id)
        if not str(row.get("return_function") or "").strip():
            fail("callback_return_without_function", "CALLBACK_RETURN needs a return function", chapter=chapter, plant_id=plant_id)

    return {
        "status": "PASS" if not hard_failures else "FAIL",
        "hard_failures": hard_failures,
        "warnings": warnings,
    }


def validate_v21_integrity(
    *,
    optional_budget: Mapping[str, Any],
    accent_rows: Sequence[Mapping[str, Any]],
    core_surface_rows: Sequence[Mapping[str, Any]],
    chapter_count: int,
) -> Dict[str, Any]:
    optional = validate_optional_accent_budget(optional_budget, chapter_count=chapter_count)
    rows = validate_contract_rows(
        accent_rows=accent_rows,
        core_surface_rows=core_surface_rows,
        chapter_count=chapter_count,
    )
    hard_failures = list(optional["hard_failures"]) + list(rows["hard_failures"])
    warnings = list(optional["warnings"]) + list(rows["warnings"])
    return {
        "status": "PASS" if not hard_failures else "FAIL",
        "optional_budget": optional,
        "row_integrity": rows,
        "hard_failures": hard_failures,
        "warnings": warnings,
    }
