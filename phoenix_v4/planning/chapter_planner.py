"""
Chapter planner (Stage 3 pre-assembly policy layer).

Execution order is intentional and strict:
1) Generate archetype candidates per chapter
2) Filter invalid candidates (quotas, transitions, slot viability)
3) Novelty-score remaining candidates
4) Deterministic select

This prevents high-scoring but invalid chapter plans.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POLICY_PATH = REPO_ROOT / "config" / "source_of_truth" / "chapter_planner_policies.yaml"
CHAPTER_PURPOSE_CONTRACTS_PATH = REPO_ROOT / "config" / "source_of_truth" / "chapter_purpose_contracts.yaml"

ROLE_MAP = {
    "recognition": "introduce",
    "destabilization": "deepen",
    "reframe": "challenge",
    "stabilization": "resolve",
    "integration": "resolve",
}


# 12 Bestseller chapter structures (narrative shapes). Max 3 same in a row per book.
BESTSELLER_STRUCTURES = [
    "promise_engine",
    "gladwell_spiral",
    "van_der_kolk",
    "atomic",
    "brene_brown",
    "myth_killer",
    "case_file",
    "permission_slip",
    "zoom_lens",
    "contrast_engine",
    "ancestor",
    "letter",
]
MAX_BESTSELLER_RUN = 3


@dataclass
class ChapterContract:
    chapter_index: int
    emotional_job: str
    reader_promise: str
    forbidden_repeats: list[str]
    required_escalation: str
    allowed_slot_types: list[str]
    max_exercises: int


def infer_purpose_tier_by_count(chapter_count: int) -> str:
    """Map chapter count to purpose-contract arc tier (non-overlapping bands)."""
    if chapter_count <= 5:
        return "micro_book"
    if chapter_count < 8:
        return "short_book"
    if chapter_count <= 12:
        return "standard_book"
    if chapter_count <= 18:
        return "extended_book"
    return "deep_book"


def resolve_purpose_arc_key(arc_id: Optional[str], chapter_count: int) -> str:
    """Resolve YAML arc key from runtime_format hint or chapter count."""
    aid = (arc_id or "").strip().lower()
    if not aid:
        return infer_purpose_tier_by_count(chapter_count)
    if "micro" in aid:
        return "micro_book"
    if "short" in aid and "standard" not in aid:
        return "short_book"
    if "extended" in aid:
        return "extended_book"
    if "deep" in aid or "6h" in aid:
        return "deep_book"
    if "standard" in aid:
        return "standard_book"
    return infer_purpose_tier_by_count(chapter_count)


def _fallback_chapter_contracts(chapter_count: int) -> list[ChapterContract]:
    """Uniform soft contracts when YAML is missing (warn-only path)."""
    return [
        ChapterContract(
            chapter_index=i,
            emotional_job="integration",
            reader_promise="",
            forbidden_repeats=[],
            required_escalation="",
            allowed_slot_types=[
                "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE",
                "INTEGRATION", "COMPRESSION", "TEACHER_DOCTRINE",
            ],
            max_exercises=2,
        )
        for i in range(chapter_count)
    ]


def assign_chapter_purpose_contracts(
    chapter_count: int,
    arc_id: Optional[str] = None,
    *,
    policy_path: Optional[Path] = None,
) -> list[ChapterContract]:
    """
    Load chapter_purpose_contracts.yaml and return one ChapterContract per chapter.

    Falls back to uniform contracts if YAML is missing or invalid (logs warning only).
    """
    path = policy_path or CHAPTER_PURPOSE_CONTRACTS_PATH
    data = _load_yaml(path)
    if not data:
        logger.warning(
            "chapter_purpose_contracts.yaml missing or unloadable; using fallback ChapterContract list.",
        )
        return _fallback_chapter_contracts(chapter_count)

    arc_key = resolve_purpose_arc_key(arc_id, chapter_count)
    arcs = data.get("arcs") or {}
    arc = arcs.get(arc_key) or {}
    jobs_raw = list(arc.get("jobs") or [])
    if not jobs_raw:
        logger.warning("chapter purpose arc %r has no jobs; using fallback.", arc_key)
        return _fallback_chapter_contracts(chapter_count)

    templates: list[dict[str, Any]] = [j for j in jobs_raw if isinstance(j, dict)]
    templates.sort(key=lambda x: int(x.get("chapter_index", 0)))

    out: list[ChapterContract] = []
    for i in range(chapter_count):
        src = templates[i] if i < len(templates) else templates[-1]
        mx = src.get("max_exercises")
        out.append(
            ChapterContract(
                chapter_index=i,
                emotional_job=str(src.get("emotional_job") or "integration"),
                reader_promise=str(src.get("reader_promise") or ""),
                forbidden_repeats=[str(x) for x in (src.get("forbidden_repeats") or [])],
                required_escalation=str(src.get("required_escalation") or ""),
                allowed_slot_types=[str(x) for x in (src.get("allowed_slot_types") or [])],
                max_exercises=int(mx) if mx is not None else 2,
            )
        )
    return out


def assign_bestseller_structures(chapter_count: int, selector_key_prefix: str) -> list[str]:
    """
    Assign one of the 12 Bestseller structures per chapter. Deterministic.
    Never more than MAX_BESTSELLER_RUN (3) of the same structure in a row.
    """
    result: list[str] = []
    n = len(BESTSELLER_STRUCTURES)
    for ch in range(chapter_count):
        seed = f"{selector_key_prefix}:bestseller:ch{ch}"
        h = hashlib.sha256(seed.encode("utf-8")).digest()
        idx = int.from_bytes(h[:2], "big") % n
        candidate = BESTSELLER_STRUCTURES[idx]
        run_len = 0
        for i in range(len(result) - 1, -1, -1):
            if result[i] == candidate:
                run_len += 1
            else:
                break
        if run_len >= MAX_BESTSELLER_RUN:
            # Pick next distinct structure (deterministic)
            used = {result[i] for i in range(max(0, len(result) - MAX_BESTSELLER_RUN), len(result))}
            for j in range(1, n):
                next_idx = (idx + j) % n
                alt = BESTSELLER_STRUCTURES[next_idx]
                if alt not in used:
                    candidate = alt
                    break
        result.append(candidate)
    return result


def _augment_slots_for_bestseller_structure(
    base_row: list[str],
    structure_key: str,
) -> list[str]:
    """
    Augment a chapter's slot sequence to include slots required by its
    assigned bestseller structure. Uses the beat order from
    bestseller_structure_map.BESTSELLER_BEAT_STEPS.

    Strategy:
    - Start from the bestseller structure's full beat order
    - For each required beat step, include the slot
    - For optional beat steps, include if the slot exists in base_row
    - Preserve COMPRESSION and EXERCISE from base_row at their correct positions
    - Slots in base_row but not in the beat order (e.g. COMPRESSION) are
      inserted at their natural position relative to their neighbors
    """
    from phoenix_v4.planning.bestseller_structure_map import (
        BESTSELLER_BEAT_STEPS,
        normalize_structure_key,
    )

    key = normalize_structure_key(structure_key)
    steps = BESTSELLER_BEAT_STEPS.get(key)
    if not steps:
        logger.warning(
            "Unknown bestseller structure %r; keeping base slot row unchanged.", structure_key,
        )
        return base_row

    base_upper = [s.strip().upper() for s in base_row]

    # Build the target slot sequence from the beat order
    result: list[str] = []
    for optional, spec in steps:
        if isinstance(spec, frozenset):
            # SCENE|STORY alternative: pick whichever is in base_row first, default to first
            chosen = None
            for candidate in sorted(spec):
                if candidate in base_upper:
                    chosen = candidate
                    break
            if chosen is None:
                if optional:
                    continue
                chosen = sorted(spec)[0]
            result.append(chosen)
        else:
            slot_name = spec.strip().upper()
            if optional and slot_name not in base_upper:
                # Optional slot not in base — skip
                continue
            result.append(slot_name)

    # Preserve slots from base_row that aren't in the beat order vocabulary
    # (e.g. COMPRESSION, EXERCISE if not in beat steps).
    beat_vocab: set[str] = set()
    for _, spec in steps:
        if isinstance(spec, frozenset):
            beat_vocab |= set(spec)
        else:
            beat_vocab.add(spec.strip().upper())

    extra_slots = [s for s in base_upper if s not in beat_vocab and s not in result]
    for extra in extra_slots:
        # Insert COMPRESSION after REFLECTION (its natural home)
        if extra == "COMPRESSION" and "REFLECTION" in result:
            idx = result.index("REFLECTION") + 1
            result.insert(idx, extra)
        # Insert EXERCISE before INTEGRATION if not already present
        elif extra == "EXERCISE" and "EXERCISE" not in result:
            if "INTEGRATION" in result:
                idx = result.index("INTEGRATION")
                result.insert(idx, extra)
            else:
                result.append(extra)
        else:
            result.append(extra)

    return result


@dataclass
class ChapterPlanResult:
    slot_definitions: list[list[str]]
    chapter_archetypes: list[str]
    chapter_exercise_modes: list[str]
    chapter_reflection_weights: list[str]
    chapter_story_depths: list[str]
    warnings: list[str]
    chapter_bestseller_structures: Optional[list[str]] = None  # length == chapter_count


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def infer_book_size(chapter_count: int, policy: dict[str, Any]) -> str:
    ranges = policy.get("book_size_by_chapters") or {}
    for size in ("short", "medium", "long"):
        rr = ranges.get(size)
        if isinstance(rr, list) and len(rr) == 2 and rr[0] <= chapter_count <= rr[1]:
            return size
    if chapter_count <= 6:
        return "short"
    if chapter_count <= 10:
        return "medium"
    return "long"


def _role_distribution_warnings(
    book_size: str,
    emotional_role_sequence: Optional[list[str]],
    policy: dict[str, Any],
) -> list[str]:
    if not emotional_role_sequence:
        return []
    targets = (policy.get("role_distribution_targets") or {}).get(book_size) or {}
    if not targets:
        return []
    counts: dict[str, int] = {"introduce": 0, "deepen": 0, "challenge": 0, "resolve": 0}
    for role in emotional_role_sequence:
        mapped = ROLE_MAP.get(str(role).strip().lower())
        if mapped:
            counts[mapped] += 1
    warns: list[str] = []
    for role_name, bounds in targets.items():
        if not isinstance(bounds, list) or len(bounds) != 2:
            continue
        low, high = int(bounds[0]), int(bounds[1])
        c = counts.get(role_name, 0)
        if c < low or c > high:
            warns.append(
                f"arc_role_distribution[{book_size}] {role_name}={c} outside target [{low},{high}]"
            )
    return warns


def _apply_slot_policy(base_slots: list[str], slot_policy: dict[str, Any]) -> list[str]:
    base = [str(s).strip().upper() for s in base_slots]
    req = [str(s).strip().upper() for s in (slot_policy.get("require") or [])]
    opt = [str(s).strip().upper() for s in (slot_policy.get("optional") or [])]
    forbid = {str(s).strip().upper() for s in (slot_policy.get("forbid") or [])}

    out: list[str] = []
    for s in base:
        if s in forbid:
            continue
        if s in req or s in opt:
            out.append(s)

    # Ensure required slots exist in output in deterministic order, appended if absent.
    for s in req:
        if s not in out:
            out.append(s)

    # Basic viability: chapter should still carry narrative spine.
    if not any(s in out for s in ("HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION")):
        return []

    return out


def _chapter_role(emotional_role_sequence: Optional[list[str]], chapter_idx: int) -> str:
    if not emotional_role_sequence or chapter_idx >= len(emotional_role_sequence):
        return "deepen"
    return ROLE_MAP.get(str(emotional_role_sequence[chapter_idx]).strip().lower(), "deepen")


def _score_candidate(
    *,
    chapter_idx: int,
    archetype_id: str,
    archetype_cfg: dict[str, Any],
    chapter_archetypes: list[str],
    signature_counts: dict[str, int],
    selector_key_prefix: str,
) -> float:
    # Base priority
    score = float(archetype_cfg.get("priority") or 1.0)

    # Novelty penalties on sequence rhythm
    if chapter_archetypes and chapter_archetypes[-1] == archetype_id:
        score -= 0.35
    if len(chapter_archetypes) >= 2 and chapter_archetypes[-1] == archetype_id and chapter_archetypes[-2] == archetype_id:
        score -= 0.75

    sig = archetype_id
    score -= 0.12 * float(signature_counts.get(sig, 0))

    # Small deterministic jitter to avoid stable global tie bias.
    h = hashlib.sha256(f"{selector_key_prefix}:novelty:ch{chapter_idx}:{archetype_id}".encode("utf-8")).digest()
    score += (h[0] / 2550.0)

    return score


def plan_chapters(
    *,
    slot_definitions: list[list[str]],
    chapter_count: int,
    selector_key_prefix: str,
    emotional_role_sequence: Optional[list[str]] = None,
    book_size: Optional[str] = None,
    policy_path: Optional[Path] = None,
    enforce_role_distribution: bool = False,
) -> ChapterPlanResult:
    """
    Build chapter-level archetype/weight plan and derive effective slot_definitions.
    """
    policy = _load_yaml(policy_path or POLICY_PATH)
    if not policy:
        return ChapterPlanResult(
            slot_definitions=slot_definitions,
            chapter_archetypes=["legacy_uniform"] * chapter_count,
            chapter_exercise_modes=["none"] * chapter_count,
            chapter_reflection_weights=["standard"] * chapter_count,
            chapter_story_depths=["standard"] * chapter_count,
            warnings=["chapter_planner_policies missing; fallback to uniform slot plan"],
        )

    size = book_size or infer_book_size(chapter_count, policy)
    warnings = _role_distribution_warnings(size, emotional_role_sequence, policy)
    if enforce_role_distribution and warnings:
        raise ValueError("; ".join(warnings))

    chapter_bestseller_structures = assign_bestseller_structures(chapter_count, selector_key_prefix)

    archetypes = (policy.get("archetypes") or {})
    quotas = (policy.get("quotas") or {}).get(size) or {}
    full_exercise_max = int(quotas.get("full_exercise_max") or 0)
    reflection_heavy_max = int(quotas.get("reflection_heavy_max") or 0)

    chapter_archetypes: list[str] = []
    chapter_exercise_modes: list[str] = []
    chapter_reflection_weights: list[str] = []
    chapter_story_depths: list[str] = []
    out_slots: list[list[str]] = []

    signature_counts: dict[str, int] = {}
    full_ex_used = 0
    reflection_heavy_used = 0

    for ch in range(chapter_count):
        base_row = list(slot_definitions[ch]) if ch < len(slot_definitions) else []
        role = _chapter_role(emotional_role_sequence, ch)

        # 1) Candidate generation
        generated: list[tuple[str, dict[str, Any], list[str]]] = []
        for aid, cfg in archetypes.items():
            roles = [str(r).strip().lower() for r in (cfg.get("arc_roles") or [])]
            if role not in roles:
                continue
            slot_policy = cfg.get("slot_policy") or {}
            row = _apply_slot_policy(base_row, slot_policy)
            if row:
                generated.append((aid, cfg, row))

        if not generated:
            generated = [("legacy_uniform", {"slot_policy": {}}, base_row)]

        # 2) Hard filter (quotas + transitions) before scoring
        filtered: list[tuple[str, dict[str, Any], list[str]]] = []
        prev = chapter_archetypes[-1] if chapter_archetypes else None
        for aid, cfg, row in generated:
            sp = cfg.get("slot_policy") or {}
            ex_mode = str(sp.get("exercise_mode") or "none")
            refl_w = str(sp.get("reflection_weight") or "standard")

            # Transition compatibility
            if prev:
                prev_cfg = archetypes.get(prev) or {}
                allowed_next = [str(x) for x in (prev_cfg.get("allowed_next") or [])]
                if allowed_next and aid not in allowed_next:
                    continue

            # Exercise quota
            would_full = (ex_mode == "full")
            if would_full and full_ex_used >= full_exercise_max:
                continue

            # Reflection-heavy quota
            would_heavy = (refl_w == "heavy")
            if would_heavy and reflection_heavy_used >= reflection_heavy_max:
                continue

            filtered.append((aid, cfg, row))

        if not filtered:
            filtered = [("legacy_uniform", {"slot_policy": {}}, base_row)]

        # 3) Novelty scoring
        scored: list[tuple[float, str, dict[str, Any], list[str]]] = []
        for aid, cfg, row in filtered:
            score = _score_candidate(
                chapter_idx=ch,
                archetype_id=aid,
                archetype_cfg=cfg,
                chapter_archetypes=chapter_archetypes,
                signature_counts=signature_counts,
                selector_key_prefix=selector_key_prefix,
            )
            scored.append((score, aid, cfg, row))

        scored.sort(key=lambda x: (-x[0], x[1]))
        best_score = scored[0][0]
        best = [x for x in scored if x[0] == best_score]

        # 4) Deterministic selection among score ties
        h = hashlib.sha256(f"{selector_key_prefix}:choose:ch{ch}".encode("utf-8")).digest()
        pick_idx = h[0] % len(best)
        _, archetype_id, archetype_cfg, chosen_row = best[pick_idx]

        sp = archetype_cfg.get("slot_policy") or {}
        ex_mode = str(sp.get("exercise_mode") or "none")
        refl_w = str(sp.get("reflection_weight") or "standard")
        story_d = str(sp.get("story_depth") or "standard")

        if ex_mode == "none":
            chosen_row = [s for s in chosen_row if s != "EXERCISE"]
        elif ex_mode in ("micro", "full") and "EXERCISE" not in chosen_row and "INTEGRATION" in chosen_row:
            # Deterministic insertion before INTEGRATION for better chapter flow.
            ins = chosen_row.index("INTEGRATION")
            chosen_row = chosen_row[:ins] + ["EXERCISE"] + chosen_row[ins:]

        if ex_mode == "full":
            full_ex_used += 1
        if refl_w == "heavy":
            reflection_heavy_used += 1

        # 5) Augment slot row with bestseller structure beat order
        # This adds PIVOT, TAKEAWAY, THREAD, PERMISSION etc. as required by
        # the chapter's assigned bestseller structure.
        bs_key = chapter_bestseller_structures[ch] if ch < len(chapter_bestseller_structures) else None
        if bs_key:
            chosen_row = _augment_slots_for_bestseller_structure(chosen_row, bs_key)

        chapter_archetypes.append(archetype_id)
        chapter_exercise_modes.append(ex_mode)
        chapter_reflection_weights.append(refl_w)
        chapter_story_depths.append(story_d)
        out_slots.append(chosen_row)
        signature_counts[archetype_id] = signature_counts.get(archetype_id, 0) + 1

    return ChapterPlanResult(
        slot_definitions=out_slots,
        chapter_archetypes=chapter_archetypes,
        chapter_exercise_modes=chapter_exercise_modes,
        chapter_reflection_weights=chapter_reflection_weights,
        chapter_story_depths=chapter_story_depths,
        warnings=warnings,
        chapter_bestseller_structures=chapter_bestseller_structures,
    )
