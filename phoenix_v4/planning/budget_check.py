"""
Pre-render word-budget sufficiency check.

Estimates achievable word count from the selected atom pool BEFORE rendering
so the pipeline can fail fast instead of wasting time and API calls on a
render that will not meet the word-count gate.

Usage (inside run_pipeline.py, after plan assembly, before rendering):

    from phoenix_v4.planning.budget_check import check_word_budget, BudgetResult
    result = check_word_budget(plan, format_config)
    if not result.sufficient:
        ...  # abort or warn
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChapterEstimate:
    """Per-chapter word-count estimate."""
    chapter_index: int
    estimated_words: int
    target_min: int
    slot_count: int
    shortfall: int  # 0 when sufficient; positive when short


@dataclass
class BudgetResult:
    """Outcome of the pre-render budget check."""
    estimated_words: int
    target_min: int
    target_max: int
    sufficient: bool
    per_chapter_estimates: list[ChapterEstimate] = field(default_factory=list)
    message: str = ""


def _estimate_atom_words(prose_text: str) -> int:
    """Estimate word count for an atom's prose via whitespace split."""
    if not prose_text:
        return 0
    return len(prose_text.split())


def check_word_budget(
    plan: dict[str, Any],
    format_config: dict[str, Any],
    *,
    prose_map: Optional[dict[str, str]] = None,
    atoms_root: Optional[Path] = None,
) -> BudgetResult:
    """
    Estimate total achievable word count from the atom pool assigned in *plan*
    and compare against the word-range targets in *format_config*.

    Parameters
    ----------
    plan : dict
        Compiled plan containing ``chapter_slot_sequence`` and ``atom_ids``.
    format_config : dict
        Runtime format config containing ``word_range: [min, max]`` and
        optionally ``chapter_count_default``.
    prose_map : dict, optional
        Pre-resolved atom-id -> prose text mapping.  When ``None`` the
        function resolves prose via ``resolve_prose_for_plan``.
    atoms_root : Path, optional
        Override for the atoms directory (forwarded to the prose resolver).

    Returns
    -------
    BudgetResult
    """
    chapter_slot_sequence = plan.get("chapter_slot_sequence", [])
    atom_ids = plan.get("atom_ids", [])
    chapter_count = len(chapter_slot_sequence)

    # Resolve prose if not supplied
    if prose_map is None:
        try:
            from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan

            kwargs: dict[str, Any] = {}
            if atoms_root is not None:
                kwargs["atoms_root"] = atoms_root
            rr = resolve_prose_for_plan(plan, **kwargs)
            prose_map = rr.prose_map
        except Exception as exc:
            logger.warning("Budget check: prose resolution failed (%s); using empty map", exc)
            prose_map = {}

    # Extract word-range from format config
    word_range = format_config.get("word_range", [0, 0])
    if isinstance(word_range, (list, tuple)) and len(word_range) >= 2:
        target_min = int(word_range[0])
        target_max = int(word_range[1])
    else:
        target_min = 0
        target_max = 0

    # Per-chapter minimum (distribute book target evenly across chapters)
    if chapter_count > 0 and target_min > 0:
        ch_target_min = target_min // chapter_count
    else:
        ch_target_min = 0

    # Walk atom_ids in slot order, grouped by chapter
    atom_idx = 0
    total_estimated = 0
    per_chapter: list[ChapterEstimate] = []

    for ch_idx, slots in enumerate(chapter_slot_sequence):
        ch_words = 0
        for _slot in slots:
            if atom_idx >= len(atom_ids):
                break
            aid = atom_ids[atom_idx]
            atom_idx += 1
            prose = prose_map.get(aid, "")
            ch_words += _estimate_atom_words(prose)

        shortfall = max(0, ch_target_min - ch_words)
        per_chapter.append(
            ChapterEstimate(
                chapter_index=ch_idx,
                estimated_words=ch_words,
                target_min=ch_target_min,
                slot_count=len(slots),
                shortfall=shortfall,
            )
        )
        total_estimated += ch_words

    sufficient = total_estimated >= target_min

    if sufficient:
        message = (
            f"Budget check: estimated {total_estimated} words, "
            f"target {target_min}-{target_max}, PASS"
        )
    else:
        shortfall_total = target_min - total_estimated
        message = (
            f"Budget check: estimated {total_estimated} words, "
            f"target {target_min}-{target_max}, "
            f"FAIL: {shortfall_total} words short"
        )

    return BudgetResult(
        estimated_words=total_estimated,
        target_min=target_min,
        target_max=target_max,
        sufficient=sufficient,
        per_chapter_estimates=per_chapter,
        message=message,
    )
