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
import re
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
CHAPTER_STRUCTURE_TEMPLATE_PATH = (
    REPO_ROOT / "config" / "rendering" / "chapter_structure_template.yaml"
)

# OPD-124: long-form runtimes must expose all seven canonical chapter roles in order.
LONG_FORM_RUNTIME_FORMATS = frozenset(
    {"standard_book", "extended_book_2h", "deep_book_4h", "deep_book_6h"}
)
MICRO_COLLAPSE_RUNTIME_FORMATS = frozenset({"micro_book_15", "micro_book_20"})

_CHAPTER_STRUCTURE_TEMPLATE_CACHE: Optional[dict[str, Any]] = None

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

# OPD-114 Phase B: scene-depth ladder targets per runtime (L1..N within one archetype).
RUNTIME_SCENE_STORY_DEPTH: dict[str, int] = {
    "micro_book_15": 1,
    "standard_book": 2,
    "extended_book_2h": 3,
    "deep_book_4h": 4,
    "deep_book_6h": 5,
}


def story_depth_for_runtime(runtime_format: Optional[str]) -> int:
    """Return scene ladder depth (1–5) for a runtime_format id."""
    rf = (runtime_format or "").strip()
    return int(RUNTIME_SCENE_STORY_DEPTH.get(rf, 2))


def load_chapter_structure_template(
    path: Optional[Path] = None,
) -> dict[str, Any]:
    """Load config/rendering/chapter_structure_template.yaml (OPD-124)."""
    global _CHAPTER_STRUCTURE_TEMPLATE_CACHE
    if _CHAPTER_STRUCTURE_TEMPLATE_CACHE is not None:
        return _CHAPTER_STRUCTURE_TEMPLATE_CACHE
    data = _load_yaml(path or CHAPTER_STRUCTURE_TEMPLATE_PATH)
    _CHAPTER_STRUCTURE_TEMPLATE_CACHE = data if isinstance(data, dict) else {}
    return _CHAPTER_STRUCTURE_TEMPLATE_CACHE


def _slot_type_to_canonical_role(slot_type: str, template: dict[str, Any]) -> str:
    """Map a canonical slot type to operator slot_role (hook, named_story, …)."""
    st = (slot_type or "").strip().upper()
    prefix = {str(x).strip().upper() for x in (template.get("prefix_slot_types") or [])}
    if st in prefix:
        return st.lower()
    for entry in template.get("canonical_chapter_sequence") or []:
        if not isinstance(entry, dict):
            continue
        role = str(entry.get("slot_role") or "").strip()
        types = {str(t).strip().upper() for t in (entry.get("slot_types") or [])}
        if st in types:
            return role or st.lower()
    return "other"


def _canonical_type_priority(template: dict[str, Any]) -> dict[str, int]:
    """Lower index = earlier in chapter (hook first)."""
    priority: dict[str, int] = {}
    idx = 0
    for entry in template.get("canonical_chapter_sequence") or []:
        if not isinstance(entry, dict):
            continue
        for st in entry.get("slot_types") or []:
            key = str(st).strip().upper()
            if key and key not in priority:
                priority[key] = idx
        idx += 1
    for st in template.get("prefix_slot_types") or []:
        key = str(st).strip().upper()
        if key and key not in priority:
            priority[key] = -1
    return priority


def enforce_canonical_chapter_sequence(
    row: list[str],
    *,
    runtime_format: Optional[str] = None,
    chapter_index: int = 0,
    template: Optional[dict[str, Any]] = None,
) -> tuple[list[str], list[str], list[str]]:
    """
    Reorder one chapter's slot types to hook → scene → section → named story → …

    Returns (reordered_slots, slot_roles, warnings). OPD-124.
    """
    rf = (runtime_format or "").strip()
    tmpl = template if template is not None else load_chapter_structure_template()
    warnings: list[str] = []

    base = [str(s).strip().upper() for s in row if str(s).strip()]
    if not base:
        return [], [], warnings

    if rf in MICRO_COLLAPSE_RUNTIME_FORMATS:
        deviations = (tmpl.get("deviations_allowed") or {})
        if deviations.get(rf) == "collapse_scene_section_allowed":
            if "SCENE" not in base and any(s in base for s in ("REFLECTION", "COMPRESSION")):
                warnings.append(
                    f"ch{chapter_index + 1}: micro format may collapse scene+section (no SCENE slot)"
                )
        roles = [_slot_type_to_canonical_role(s, tmpl) for s in base]
        return base, roles, warnings

    if rf not in LONG_FORM_RUNTIME_FORMATS:
        roles = [_slot_type_to_canonical_role(s, tmpl) for s in base]
        return base, roles, warnings

    priority = _canonical_type_priority(tmpl)
    prefix_types = {str(x).strip().upper() for x in (tmpl.get("prefix_slot_types") or [])}

    # OPD-124: cap SCENE at 2 before teaching/story block; first STORY after section content.
    scenes = [s for s in base if s == "SCENE"]
    if len(scenes) > 2:
        warnings.append(
            f"ch{chapter_index + 1}: SCENE count {len(scenes)} > 2; planner keeps first two before section"
        )
    section_types = frozenset({"REFLECTION", "COMPRESSION", "PIVOT"})
    sections = [s for s in base if s in section_types]
    stories = [s for s in base if s == "STORY"]
    teachers = [s for s in base if s in ("TEACHER_DOCTRINE", "COMPOSITE_TEACHER_DOCTRINE")]
    exercises = [s for s in base if s == "EXERCISE"]
    close_types = frozenset({"INTEGRATION", "TAKEAWAY", "THREAD", "PERMISSION"})
    closes = [s for s in base if s in close_types]
    hooks = [s for s in base if s == "HOOK"]
    prefixes = [s for s in base if s in prefix_types]
    other = [
        s
        for s in base
        if s
        not in (
            {"HOOK", "SCENE", "STORY", "EXERCISE"}
            | section_types
            | close_types
            | {"TEACHER_DOCTRINE", "COMPOSITE_TEACHER_DOCTRINE"}
            | prefix_types
        )
    ]

    if not hooks:
        warnings.append(f"ch{chapter_index + 1}: canonical sequence missing hook (HOOK)")
    if not scenes:
        warnings.append(
            f"ch{chapter_index + 1}: canonical sequence missing scene_or_section (SCENE)"
        )
    if not sections:
        warnings.append(
            f"ch{chapter_index + 1}: canonical sequence missing first_section_content "
            "(REFLECTION/COMPRESSION/PIVOT)"
        )
    if not stories:
        warnings.append(f"ch{chapter_index + 1}: canonical sequence missing named_story (STORY)")

    first_story = stories[:1]
    rest_stories = stories[1:]
    ordered = (
        prefixes
        + hooks
        + scenes[:2]
        + sections
        + first_story
        + teachers
        + other
        + exercises
        + rest_stories
        + closes
    )
    # Preserve any slot types not yet placed (stable append).
    placed = set(ordered)
    for s in base:
        if s not in placed:
            ordered.append(s)
            placed.add(s)

    roles = [_slot_type_to_canonical_role(s, tmpl) for s in ordered]

    # Role-order compliance: first STORY index must follow section content.
    if stories and sections:
        if ordered.index(stories[0]) < max(ordered.index(s) for s in sections):
            warnings.append(
                f"ch{chapter_index + 1}: STORY precedes first_section_content after reorder "
                "(check enrichment atom lengths separately)"
            )
    elif stories and hooks and not sections:
        if ordered.index(stories[0]) < ordered.index(hooks[0]):
            warnings.append(f"ch{chapter_index + 1}: STORY precedes HOOK")

    if scenes and stories and ordered.index(scenes[0]) > ordered.index(stories[0]):
        warnings.append(f"ch{chapter_index + 1}: SCENE follows STORY — sequence violation")

    return ordered, roles, warnings


def validate_named_story_slot_expectations(
    story_prose: str,
    *,
    chapter_index: int = 0,
    min_words: int = 200,
) -> list[str]:
    """
    Planner/render warning when a STORY atom is short or lacks a named-character tell.

    Uses the same classifier as chapter_composer (OPD-112/123). OPD-124 review aid.
    """
    warnings: list[str] = []
    body = (story_prose or "").strip()
    if not body:
        warnings.append(f"ch{chapter_index + 1}: STORY slot empty")
        return warnings
    word_count = len(re.findall(r"\b\w+\b", body))
    if word_count < min_words:
        warnings.append(
            f"ch{chapter_index + 1}: STORY atom short ({word_count} words < {min_words})"
        )
    try:
        from phoenix_v4.rendering.chapter_composer import _classify_atom

        if _classify_atom(body) != "named_story":
            warnings.append(
                f"ch{chapter_index + 1}: STORY atom lacks named-character opening tell"
            )
    except Exception:
        pass
    return warnings


@dataclass
class ChapterContract:
    chapter_index: int
    emotional_job: str
    reader_promise: str
    forbidden_repeats: list[str]
    required_escalation: str
    allowed_slot_types: list[str]
    max_exercises: int
    # When true, frame governance does not treat pre-entry spiritual lexicon as a blocking issue.
    allow_early_spiritual: bool = False


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
            allow_early_spiritual=False,
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
                allow_early_spiritual=bool(src.get("allow_early_spiritual", False)),
            )
        )
    return out


def resolve_effective_max_exercises(
    contract_max: int,
    runtime_format: Optional[str],
    *,
    chapter_architecture_version: int = 1,
    format_cap: Optional[int] = None,
) -> int:
    """
    Planner-owned exercise multiplicity ceiling.

    Applies OPD-135 five-part floor for deep_book_6h / arch v2 (when contract
    already permits ≥1 exercise) and optional runtime format_cap upper bound.
    Recognition / resolution chapters (contract_max=0) stay exercise-free.
    """
    rid = (runtime_format or "").strip()
    cap = int(contract_max)
    arch_v = int(chapter_architecture_version or 1)
    five_part_floor = 2 if (rid == "deep_book_6h" or arch_v == 2) else 0
    if five_part_floor and cap >= 1:
        cap = max(cap, five_part_floor)
    if format_cap is not None:
        cap = min(cap, int(format_cap))
    return max(0, cap)


def cap_exercise_slots_in_row(slot_row: list[str], max_exercises: int) -> list[str]:
    """Keep the first *max_exercises* EXERCISE entries; drop excess upstream."""
    limit = max(0, int(max_exercises))
    seen = 0
    out: list[str] = []
    for st in slot_row:
        key = str(st).strip().upper()
        if key == "EXERCISE":
            if seen < limit:
                out.append(st)
                seen += 1
            continue
        out.append(st)
    return out


def _strip_doctrine_intro_headers(text: str) -> str:
    chunks: list[str] = []
    for para in text.split("\n\n"):
        p = para.strip()
        if not p or p.startswith("## ") or p == "---":
            continue
        chunks.append(p)
    return "\n\n".join(chunks).strip()


def _teacher_doctrine_intro_fallback(teacher_id: str, repo_root: Path) -> str:
    path = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine" / "doctrine.yaml"
    data = _load_yaml(path)
    if not data:
        return ""
    tradition = str(data.get("tradition") or data.get("display_name") or teacher_id).strip()
    core = str(data.get("core_principles") or "").strip()
    if tradition and core:
        return f"{tradition} {core}"
    return tradition or core


def resolve_teacher_doctrine_intro(
    persona_id: str,
    topic: str,
    teacher_id: Optional[str],
    repo_root: Path,
    chapter_architecture_version: int = 1,
) -> str:
    """Holistic v2: book-level doctrine preamble before Chapter 1 (OPD-130)."""
    if int(chapter_architecture_version) != 2:
        return ""
    tid = (teacher_id or "").strip().lower()
    if not tid:
        return ""
    atom_path = (
        repo_root
        / "atoms"
        / persona_id
        / topic
        / "TEACHER_DOCTRINE_INTRO"
        / tid
        / "CANONICAL.txt"
    )
    if atom_path.is_file():
        return _strip_doctrine_intro_headers(atom_path.read_text(encoding="utf-8"))
    return _teacher_doctrine_intro_fallback(tid, repo_root)


# Phase pools (1-indexed chapter numbers). Keys must match BESTSELLER_STRUCTURES entries.
_PHASE_POOLS: dict[str, list[str]] = {
    "opening":      ["gladwell_spiral", "zoom_lens", "van_der_kolk"],
    "early_middle": ["promise_engine", "myth_killer", "case_file"],
    "mid_book":     ["contrast_engine", "ancestor", "permission_slip"],
    "late_middle":  ["atomic", "brene_brown", "case_file"],
    "closing":      ["zoom_lens", "letter", "gladwell_spiral"],
}


def _phase_pool(chapter_1indexed: int, total_chapters: int) -> list[str]:
    """Return the phase-appropriate structure pool for a chapter."""
    pct = (chapter_1indexed - 1) / max(total_chapters - 1, 1)
    if pct < 0.15:
        return _PHASE_POOLS["opening"]
    elif pct < 0.40:
        return _PHASE_POOLS["early_middle"]
    elif pct < 0.65:
        return _PHASE_POOLS["mid_book"]
    elif pct < 0.88:
        return _PHASE_POOLS["late_middle"]
    else:
        return _PHASE_POOLS["closing"]


def assign_bestseller_structures(chapter_count: int, selector_key_prefix: str) -> list[str]:
    """
    Assign one of the 12 Bestseller structures per chapter. Deterministic.

    Uses phase-aware selection: each chapter draws from a pool matching its
    narrative phase (opening / early-middle / mid-book / late-middle / closing)
    as defined in docs/BESTSELLER_STRUCTURES.md.

    Never more than MAX_BESTSELLER_RUN (3) of the same structure in a row.
    If the phase pool is exhausted due to the run constraint, falls back to
    the global BESTSELLER_STRUCTURES list as secondary candidates.
    """
    result: list[str] = []
    global_n = len(BESTSELLER_STRUCTURES)

    for ch in range(chapter_count):
        pool = _phase_pool(ch + 1, chapter_count)
        pool_n = len(pool)

        seed = f"{selector_key_prefix}:bestseller:ch{ch}"
        h = hashlib.sha256(seed.encode("utf-8")).digest()
        idx = int.from_bytes(h[:2], "big") % pool_n
        candidate = pool[idx]

        # Count current run length of the candidate
        run_len = 0
        for i in range(len(result) - 1, -1, -1):
            if result[i] == candidate:
                run_len += 1
            else:
                break

        if run_len >= MAX_BESTSELLER_RUN:
            # Structures used in the last MAX_BESTSELLER_RUN positions
            used = {result[i] for i in range(max(0, len(result) - MAX_BESTSELLER_RUN), len(result))}

            # Try phase pool first (deterministic rotation)
            found = False
            for j in range(1, pool_n):
                alt = pool[(idx + j) % pool_n]
                if alt not in used:
                    candidate = alt
                    found = True
                    break

            if not found:
                # Phase pool fully blocked; fall back to global list
                global_idx = int.from_bytes(h[2:4], "big") % global_n
                for j in range(global_n):
                    alt = BESTSELLER_STRUCTURES[(global_idx + j) % global_n]
                    if alt not in used:
                        candidate = alt
                        break

        result.append(candidate)
    return result


def derive_chapter_selector_targets(
    chapter_count: int,
    selector_key_prefix: str,
    emotional_role_sequence: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """
    Deterministic per-chapter targets for bestseller metadata matching (selector + enrichment scoring).
    """
    proof_modes = ("data", "story", "diagnosis", "lived_experience", "framework")
    tension_types = ("contradiction", "mystery", "stakes", "delayed_reveal", "moral")
    objections = (
        "selfishness",
        "not_enough_time",
        "already_tried",
        "not_broken_enough",
        "fear_of_relief",
    )
    shame_types = ("visibility", "incompetence", "burden", "comparison", "hypersensitivity")
    propulsion = ("question", "image_return", "stakes_rise", "open_tab", "next_mechanism")
    callback_roles = ("setup", "escalation", "return", "echo", "")
    intents = ("recognition", "mechanism", "permission", "integration", "propulsion")

    out: list[dict[str, Any]] = []
    for ch in range(chapter_count):
        seed = f"{selector_key_prefix}:ch_sel:{ch}"
        h = hashlib.sha256(seed.encode("utf-8")).digest()
        em = None
        if emotional_role_sequence and ch < len(emotional_role_sequence):
            em = str(emotional_role_sequence[ch]).strip().lower()
        proof = proof_modes[h[0] % len(proof_modes)]
        tension = tension_types[h[1] % len(tension_types)]
        objection = objections[h[2] % len(objections)]
        shame = shame_types[h[3] % len(shame_types)]
        prop = propulsion[h[4] % len(propulsion)]
        cb = callback_roles[h[5] % len(callback_roles)]
        intent = intents[h[6] % len(intents)]
        if em == "recognition":
            intent = "recognition"
        elif em in ("integration", "stabilization"):
            intent = "integration"
        share = int(h[7] % 4)
        thesis_sentence = (
            f"The chapter stresses {tension} tension with {proof} proof toward {intent}."
        )
        open_loop = f"What shifts if {objection} is not the final verdict?"
        out.append(
            {
                "reader_objection": objection,
                "proof_mode": proof,
                "tension_type": tension,
                "private_shame_type": shame,
                "propulsion_type": prop,
                "chapter_intent": intent,
                "thesis_sentence": thesis_sentence,
                "open_loop": open_loop,
                "callback_role": cb,
                "shareability": share,
            }
        )
    return out


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
    chapter_selector_targets: Optional[list[dict[str, Any]]] = None  # length == chapter_count
    angle_layer_by_chapter: Optional[dict[int, int]] = None
    angle_definition_paragraph_weight: Optional[int] = None
    chapter_slot_roles: Optional[list[list[str]]] = None  # OPD-124: hook, named_story, …


# Alias for specs that refer to book-level structure planning output.
BookStructurePlan = ChapterPlanResult


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
    angle_id: Optional[str] = None,
    runtime_format: Optional[str] = None,
) -> ChapterPlanResult:
    """
    Build chapter-level archetype/weight plan and derive effective slot_definitions.
    """
    from phoenix_v4.planning.angle_journey import (
        ANGLE_DEFINITION_PARAGRAPH_WEIGHT,
        apply_angle_journey_slots,
        is_angle_journey_runtime,
    )

    angle_layer_by_chapter: dict[int, int] = {}
    angle_journey_warnings: list[str] = []
    angle_definition_weight: Optional[int] = None
    working_slots = [list(row) for row in slot_definitions]
    runtime_story_depth = story_depth_for_runtime(runtime_format)

    policy = _load_yaml(policy_path or POLICY_PATH)
    if not policy:
        sel_t = derive_chapter_selector_targets(chapter_count, selector_key_prefix, emotional_role_sequence)
        out_slots_fb = working_slots
        if angle_id and is_angle_journey_runtime(runtime_format):
            out_slots_fb, angle_layer_by_chapter, angle_journey_warnings = apply_angle_journey_slots(
                out_slots_fb,
                angle_id=angle_id,
                runtime_format=runtime_format,
            )
            angle_definition_weight = ANGLE_DEFINITION_PARAGRAPH_WEIGHT
        enforced_slots: list[list[str]] = []
        enforced_roles: list[list[str]] = []
        seq_warnings: list[str] = []
        for ch, row in enumerate(out_slots_fb):
            new_row, roles, w = enforce_canonical_chapter_sequence(
                row, runtime_format=runtime_format, chapter_index=ch,
            )
            enforced_slots.append(new_row)
            enforced_roles.append(roles)
            seq_warnings.extend(w)
        return ChapterPlanResult(
            slot_definitions=enforced_slots,
            chapter_archetypes=["legacy_uniform"] * chapter_count,
            chapter_exercise_modes=["none"] * chapter_count,
            chapter_reflection_weights=["standard"] * chapter_count,
            chapter_story_depths=[str(runtime_story_depth)] * chapter_count,
            warnings=(
                ["chapter_planner_policies missing; fallback to uniform slot plan"]
                + angle_journey_warnings
                + seq_warnings
            ),
            chapter_selector_targets=sel_t,
            angle_layer_by_chapter=angle_layer_by_chapter or None,
            angle_definition_paragraph_weight=angle_definition_weight,
            chapter_slot_roles=enforced_roles,
        )

    size = book_size or infer_book_size(chapter_count, policy)
    warnings = _role_distribution_warnings(size, emotional_role_sequence, policy) + angle_journey_warnings
    if enforce_role_distribution and warnings:
        raise ValueError("; ".join(warnings))

    chapter_bestseller_structures = assign_bestseller_structures(chapter_count, selector_key_prefix)
    chapter_selector_targets = derive_chapter_selector_targets(
        chapter_count, selector_key_prefix, emotional_role_sequence
    )

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
        base_row = list(working_slots[ch]) if ch < len(working_slots) else []
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
        story_d = str(runtime_story_depth)

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

    final_slots = out_slots
    if angle_id and is_angle_journey_runtime(runtime_format):
        final_slots, angle_layer_by_chapter, aj_warns = apply_angle_journey_slots(
            final_slots,
            angle_id=angle_id,
            runtime_format=runtime_format,
        )
        warnings = warnings + aj_warns
        angle_definition_weight = ANGLE_DEFINITION_PARAGRAPH_WEIGHT

    enforced_slots: list[list[str]] = []
    enforced_roles: list[list[str]] = []
    for ch, row in enumerate(final_slots):
        new_row, roles, seq_warns = enforce_canonical_chapter_sequence(
            row, runtime_format=runtime_format, chapter_index=ch,
        )
        enforced_slots.append(new_row)
        enforced_roles.append(roles)
        warnings.extend(seq_warns)

    return ChapterPlanResult(
        slot_definitions=enforced_slots,
        chapter_archetypes=chapter_archetypes,
        chapter_exercise_modes=chapter_exercise_modes,
        chapter_reflection_weights=chapter_reflection_weights,
        chapter_story_depths=chapter_story_depths,
        warnings=warnings,
        chapter_bestseller_structures=chapter_bestseller_structures,
        chapter_selector_targets=chapter_selector_targets,
        angle_layer_by_chapter=angle_layer_by_chapter or None,
        angle_definition_paragraph_weight=angle_definition_weight,
        chapter_slot_roles=enforced_roles,
    )
