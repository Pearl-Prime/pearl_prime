"""
EnrichmentSelect — fills Beatmap slots with prose using the registry_resolver waterfall.

Priority (aligned with phoenix_v4.planning.registry_resolver.resolve_book):
  1. Teacher atoms (approved_atoms/{SLOT_TYPE}/) when teacher_id is set and
     slot type is in the teacher-overlay set (see registry_resolver).
  2. Persona atoms (HOOK, SCENE, STORY) from atoms/{persona}/{topic}/.
  3. For EXERCISE only: practice library before registry variant.
  4. Registry variant from registry/{topic}.yaml (nth section of that type per chapter).
  5. Content bank fallbacks from config/content_banks/*.yaml (slot-type mapped bridges).
  6. Empty: visible CONTENT GAP marker + ERROR log (or EnrichmentGapError when publishable_book).

Practice library: logs WARNING via get_exercise_for_chapter when used.

Depth pass (apply_depth_pass): after select_enrichment, fills thin chapters using
config/depth/depth_module_map.yaml — existing content only, no LLM generation.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from phoenix_v4.planning.beatmap_compile import Beatmap, BeatmapChapter, BeatmapSlot
from phoenix_v4.planning.injection_resolver import BookSlotTracker, resolve_injections
from phoenix_v4.planning.selection_allowlist import atom_passes_book_governance
from phoenix_v4.planning.slot_resolver import _bestseller_metadata_score
from phoenix_v4.planning.story_planner import SCENE_SECTION_INDICES, StorySchedule, build_story_schedule
from phoenix_v4.planning.registry_resolver import (
    _TEACHER_TYPE_MAP,
    _TEACHER_OVERLAY_TYPES,
    _PERSONA_OVERLAY_TYPES,
    _deterministic_index,
    _load_composite_doctrine_atoms,
    _load_persona_atoms,
    _load_teacher_atoms,
    _load_yaml,
    _pick_composite_pool,
    load_registry,
)
from phoenix_v4.planning.chapter_object_continuity import (
    CONTINUITY_CONNECTIVE_SLOTS,
    chapter_context_from_spine,
    continuity_bank_empty,
    filter_connective_pool,
    filter_persona_pool_one_character,
    is_twelve_shape_continuity_active,
    load_chapter_continuity_plan,
)
from phoenix_v4.planning.doctrine_rotation import (
    is_reflection_rotation_slot,
    load_doctrine_rotation_config,
    normalize_doctrine_id,
    pick_doctrine_atom_by_id,
    resolve_chapter_doctrine_id,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# OPD-115 Phase B: composite teacher doctrine/reflection (regular mode only).
_COMPOSITE_DOCTRINE_SLOT_TYPES = frozenset({
    "TEACHER_DOCTRINE", "COMPRESSION", "COMPOSITE_TEACHER_DOCTRINE",
})
_COMPOSITE_REFLECTION_SLOT_TYPES = frozenset({
    "REFLECTION", "COMPOSITE_TEACHER_REFLECTION",
})
_COMPOSITE_SLOT_TYPES = _COMPOSITE_DOCTRINE_SLOT_TYPES | _COMPOSITE_REFLECTION_SLOT_TYPES

# De-injection 2026-07-05: one authored occupant per slot — no registry stacking on
# persona HOOK/SCENE or on composite doctrine/reflection blocks.
_REGISTRY_SINGLE_OCCUPANT_SLOTS = frozenset({"HOOK", "SCENE"})

# ---------------------------------------------------------------------------
# ACT-010: Doctrine quarantine — pre-selection filter for somatic_first frame
# Synced from phoenix_v4/quality/frame_governor.py :: SPIRITUAL_LEXICON
# ---------------------------------------------------------------------------
_SOMATIC_QUARANTINE_TERMS: frozenset[str] = frozenset({
    "soul contract",
    "past life",
    "karma",
    "chakra",
    "frequency",
    "vibration",
    "akashic",
    "ascension",
    "manifestation",
    "energy field",
    "aura",
    "divine timing",
    "cosmic",
    "sacred geometry",
    "light body",
})


def _is_doctrine_quarantined(atom_text: str, frame: str) -> bool:
    """Return True if atom should be excluded from the candidate pool.

    somatic_first (or unset/empty): block spiritual/doctrine terms.
    spiritual_first: no quarantine — spiritual lexicon is permitted.
    """
    if frame == "spiritual_first":
        return False
    if not atom_text or not _SOMATIC_QUARANTINE_TERMS:
        return False
    text_lower = atom_text.lower()
    return any(term in text_lower for term in _SOMATIC_QUARANTINE_TERMS)

# Registry beatmap slot type → content-bank slot_type values (enrichment_slot_fallback_bank.yaml).
_ENRICH_BANK_SLOT_TYPES: Dict[str, Tuple[str, ...]] = {
    "HOOK": ("FALLBACK_PROSE",),
    "SCENE": ("FALLBACK_PROSE",),
    "REFLECTION": ("MECHANISM_BRIDGE",),
    "PIVOT": ("FLOW_GLUE",),
    "INTEGRATION": ("INTEGRATION_LAND", "FLOW_GLUE"),
    "THREAD": ("CHAPTER_PROPULSION",),
    "TAKEAWAY": ("TAKEAWAY_PULL",),
    "COMPRESSION": ("DOCTRINE_SECULAR_BRIDGE", "MECHANISM_BRIDGE"),
    "TEACHER_DOCTRINE": ("DOCTRINE_SECULAR_BRIDGE", "MECHANISM_BRIDGE"),
}


class EnrichmentGapError(RuntimeError):
    """Publishable-book runs must not ship visible [CONTENT GAP: ...] markers."""


class InsufficientVariantsError(RuntimeError):
    """Runtime mirror of the CI --strict variant-coverage gate (SPEC-739-THRESHOLD-01).

    Raised when a persona/topic section type has fewer than DEFAULT_MIN_VARIANTS (3)
    atom variants loaded — the same condition that causes validate_variant_coverage.py
    --strict to exit non-zero.  Author atoms upstream to resolve.
    """


class PersonaPoolEmptyError(RuntimeError):
    """OPD-118: the target persona/topic atom pool is empty for a required slot.

    Raised (or logged as planner WARNING for non-critical slots) when the
    BookSpec persona×topic pool is empty for a slot the selector would have
    filled. Pre-OPD-118 the selector silently spilled into sibling-persona
    atoms (cross-persona contamination); the fix replaces that fallback with
    an explicit signal so the planner can surface the gap upstream rather
    than ship a book stitched from the wrong personas' content.
    """


# ---------------------------------------------------------------------------
# OPD-109 Phase 3: per-book persona-pool rotation state
# ---------------------------------------------------------------------------
# Defect: the deterministic-index selector picks an atom via
# `_deterministic_index(seed_key, len(pool))`. With 96 SCENE-class slots and
# ~57 atoms in pool, the mod-distribution is mathematically reasonable, but
# the within-slot expansion (which pulls ADDITIONAL atoms via
# `_expand_atom_pool_blocks`) re-ranks by SHA(seed_key + label + index) every
# call. Because the SHA-rank is independent of book-level usage, the same few
# atoms top the rank at every slot's expansion call, so ~50% of the pool is
# never touched even though the pool is large enough. Pearl_Writer #2's
# diagnosis: deep_book_6h post-Phase-2 still picks 3-5 unique SCENE atoms
# across 96 slots.
#
# Fix: thread a per-book rotation state through `select_enrichment`. The
# selector and expansion paths both consult `least_used_index_order(pool)` so
# atoms with lower book-level usage rank first; ties are broken by the
# existing SHA-rank so re-renders at the same seed reproduce. This matches
# the pattern in `phoenix_v4/rendering/chapter_composer.WithinSlotRotationState`
# introduced by PR #1217 for within-slot bridge variants.
# ---------------------------------------------------------------------------


class PersonaPoolRotationState:
    """Book-level usage counter for persona atom IDs.

    Two methods are exposed:
      - `pick_index(pool, seed_key)`: deterministic least-used-first selection.
      - `register(atom_id)`: increment book-level usage after the pick.

    Identity of an atom is its `atom_id`. Two atoms with identical content but
    different IDs are treated as distinct (matches `_expand_atom_pool_blocks`
    semantics, which already dedupes on normalized text inside the expansion).
    """

    def __init__(self) -> None:
        # atom_id -> count of uses across the entire book render
        self._book_usage: Dict[str, int] = {}

    def book_count(self, atom_id: str) -> int:
        return self._book_usage.get(atom_id, 0)

    def register(self, atom_id: str) -> None:
        if not atom_id:
            return
        self._book_usage[atom_id] = self._book_usage.get(atom_id, 0) + 1

    def pick_index(self, pool: List[Dict[str, Any]], seed_key: str) -> int:
        """Return the index of the least-used atom in `pool`.

        Ties (atoms used the same number of times so far in this book) are
        broken by the existing `_deterministic_index` SHA seed, so re-renders
        at the same seed reproduce identically.
        """
        if not pool:
            return 0
        n = len(pool)
        # Hash-derived primary index gives the original deterministic anchor.
        primary = _deterministic_index(seed_key, n)
        # Rank every index by (book-usage-count, distance-from-primary).
        # Lower count wins; identical count → closer to primary wins.
        def _key(i: int) -> Tuple[int, int]:
            aid = str(pool[i].get("atom_id") or i)
            return (self._book_usage.get(aid, 0), (i - primary) % n)
        order = sorted(range(n), key=_key)
        return order[0]

    def least_used_order(
        self,
        pool: List[Dict[str, Any]],
        seed_key: str,
        label: str,
    ) -> List[int]:
        """Return indices ordered from least-used to most-used.

        Tie-break by SHA(seed_key:label:i) so re-renders are deterministic and
        the order respects the existing `_expand_atom_pool_blocks` ranking
        convention (which uses SHA-of-key-label-index).
        """
        if not pool:
            return []
        n = len(pool)
        def _key(i: int) -> Tuple[int, str]:
            aid = str(pool[i].get("atom_id") or i)
            tiebreak = hashlib.sha256(
                f"{seed_key}:{label}:{i}".encode("utf-8")
            ).hexdigest()
            return (self._book_usage.get(aid, 0), tiebreak)
        return sorted(range(n), key=_key)


# ---------------------------------------------------------------------------
# ws_enrichment_primary_dedup_20260616: thread the book-wide _SeenBodies
# registry into PRIMARY HOOK/SCENE/STORY selection.
#
# Until now the book-wide ``_SeenBodies`` dedup (defined further below) was
# consulted ONLY by the depth/delivery passes (``_pick_canonical_block_per_section``
# / ``_select_prose_chunk_unique``). The PRIMARY persona pick in
# ``select_enrichment`` used ``PersonaPoolRotationState.pick_index`` alone, which
# spreads picks by *usage count* but is blind to body *content* — each chapter is
# a fresh slot whose usage count is anchored independently, so the SAME atom body
# could be chosen as the primary for the same slot-type across multiple
# chapters/clusters, re-stamping a HOOK/SCENE/STORY body book-wide. That is a
# large share of the deep-tier F1 repetition (~93). This helper makes the primary
# pick dedup-aware by reusing the EXISTING ``least_used_order`` ranking and the
# EXISTING ``_SeenBodies`` exact+fuzzy membership — no new registry, no new
# similarity logic.
def _pick_primary_index_unseen(
    rotation: "PersonaPoolRotationState",
    pool: List[Dict[str, Any]],
    seed_key: str,
    label: str,
    seen_bodies: Any,
) -> int:
    """Least-used index whose body has NOT been used book-wide.

    Walks ``rotation.least_used_order(...)`` (least-used-first, deterministic SHA
    tiebreak — identical ordering convention to the expansion paths) and returns
    the first index whose ``content`` is neither an exact nor a fuzzy match to a
    body already noted in ``seen_bodies``. If every candidate is already seen (or
    ``seen_bodies`` is falsy / the pool is exhausted), falls back to the plain
    ``pick_index`` anchor — so behavior is unchanged when no unused body exists,
    and both determinism and the never-empty contract are preserved.
    """
    if not pool:
        return 0
    if not seen_bodies:
        return rotation.pick_index(pool, seed_key)
    order = rotation.least_used_order(pool, seed_key, label)
    for i in order:
        body = str(pool[i].get("content") or "")
        if not body.strip():
            continue
        norm = _norm_ws(body)
        if norm in seen_bodies or _seen_similar(seen_bodies, body):
            continue
        return i
    # Every candidate already used book-wide → keep the deterministic anchor.
    return rotation.pick_index(pool, seed_key)


def _note_primary_body(seen_bodies: Any, body: str) -> None:
    """Record a chosen PRIMARY body in the book-wide registry (exact + fuzzy).

    Mirrors the depth-pass call-sites: ``add(_norm_ws(body))`` records the exact
    normalized string and (via ``_SeenBodies.add``) auto-notes the fuzzy word-set.
    Tolerates a plain ``set`` (records exact only) and a None registry (no-op).
    """
    if seen_bodies is None or not body or not body.strip():
        return
    add = getattr(seen_bodies, "add", None)
    if callable(add):
        add(_norm_ws(body))


def _pick_hook_index_unique(
    rotation: "PersonaPoolRotationState",
    pool: List[Dict[str, Any]],
    seed_key: str,
    label: str,
    seen_bodies: Any,
    used_hooks: set[str],
    *,
    contract: Optional[dict] = None,
    engine: str = "",
) -> int:
    """HOOK primary pick — never reuse the same hook body twice per book (Part F)."""
    if not pool:
        return 0
    from phoenix_v4.planning.book_identity_contract import (
        banned_phrase_penalty,
        engine_metaphor_bonus,
    )

    order = rotation.least_used_order(pool, seed_key, label)
    best_idx: Optional[int] = None
    best_score = float("-inf")
    for i in order:
        body = str(pool[i].get("content") or "")
        if not body.strip():
            continue
        norm = _norm_ws(body)
        if norm in used_hooks:
            continue
        if seen_bodies and (norm in seen_bodies or _seen_similar(seen_bodies, body)):
            continue
        score = -float(rotation.book_count(str(pool[i].get("atom_id") or "")))
        if contract:
            score -= banned_phrase_penalty(body, contract)
            score += engine_metaphor_bonus(body, contract, engine)
        if score > best_score:
            best_score = score
            best_idx = i
    if best_idx is not None:
        return best_idx
    return _pick_primary_index_unseen(rotation, pool, seed_key, label, seen_bodies)


# ---------------------------------------------------------------------------
# OPD-114 Phase B: scene-depth ladder (one anchor archetype per chapter)
# ---------------------------------------------------------------------------


class SceneArchetypeRotationState:
    """Book-level usage counter for scene archetype ids (least-used-first)."""

    def __init__(self) -> None:
        self._usage: Dict[str, int] = {}

    def pick_archetype(
        self,
        archetype_keys: List[str],
        chapter_id: int,
        seed: str,
    ) -> str:
        if not archetype_keys:
            return "__null__"
        if len(archetype_keys) == 1:
            return archetype_keys[0]

        def _key(arch: str) -> Tuple[int, str]:
            tie = hashlib.sha256(
                f"{seed}:scene_arch:ch{chapter_id}:{arch}".encode("utf-8")
            ).hexdigest()
            return (self._usage.get(arch, 0), tie)

        chosen = sorted(archetype_keys, key=_key)[0]
        self._usage[chosen] = self._usage.get(chosen, 0) + 1
        return chosen


def pick_scene_ladder(
    chapter_id: int,
    archetype_pool: List[Dict[str, Any]],
    story_depth: int,
    rotation_state: SceneArchetypeRotationState,
    *,
    seed: str = "",
    planner_warnings: Optional[List[str]] = None,
) -> List["SceneAtom"]:
    """Pick depth-ordered SCENE atoms L1..story_depth for one anchor archetype."""
    from phoenix_v4.planning.scene_atom_header_parser import SceneAtom, scene_atom_from_dict

    warns = planner_warnings if planner_warnings is not None else []
    depth_target = max(1, int(story_depth))
    atoms = [scene_atom_from_dict(a) for a in archetype_pool if str(a.get("content") or "").strip()]
    if not atoms:
        return []

    by_arch: Dict[str, List[SceneAtom]] = defaultdict(list)
    for atom in atoms:
        key = atom.archetype if atom.archetype is not None else "__null__"
        by_arch[key].append(atom)

    for group in by_arch.values():
        group.sort(key=lambda a: (a.depth_level, a.atom_id))

    anchor = rotation_state.pick_archetype(sorted(by_arch.keys()), chapter_id, seed)
    pool = by_arch.get(anchor) or atoms
    by_level = {a.depth_level: a for a in pool}
    max_level = max(by_level.keys()) if by_level else 1

    ladder: List[SceneAtom] = []
    for level in range(1, depth_target + 1):
        if level in by_level:
            ladder.append(by_level[level])
        else:
            break

    if len(ladder) < depth_target:
        warns.append(
            f"chapter {chapter_id}: scene archetype {anchor!r} has {max_level} depth level(s), "
            f"story_depth={depth_target}; scene ladder fallback to available levels"
        )
        if not ladder and max_level in by_level:
            ladder = [by_level[max_level]]

    return ladder


# ---------------------------------------------------------------------------
# ACT-007: Bestseller metadata field bonuses and collision_family dedup
# ---------------------------------------------------------------------------

def _metadata_field_bonus(metadata: Dict[str, Any], ch_tgt: Optional[Dict[str, Any]]) -> float:
    """Additive bonus for atom metadata matching chapter targets.

    Bonuses (additive, graceful fallback when field absent):
      reader_objection match  → +0.15  (target-gated)
      proof_mode match        → +0.10  (target-gated)
      tension_type match      → +0.10  (target-gated)
      propulsion_type match   → +0.08  (target-gated)
      shareability >= 4       → +0.05  (unconditional — signals high-share atom)

    Returns total bonus (0.0 when metadata absent or no fields present).
    """
    if not metadata:
        return 0.0
    m = metadata
    ch_tgt_ = ch_tgt or {}
    bonus = 0.0

    def _eq(field: str) -> bool:
        want = ch_tgt_.get(field)
        if want is None or str(want).strip() == "":
            return False
        got = m.get(field)
        if got is None:
            return False
        return str(got).strip().lower() == str(want).strip().lower()

    if _eq("reader_objection"):
        bonus += 0.15
    if _eq("proof_mode"):
        bonus += 0.10
    if _eq("tension_type"):
        bonus += 0.10
    if _eq("propulsion_type"):
        bonus += 0.08
    try:
        sh = m.get("shareability")
        if sh is not None and int(sh) >= 4:
            bonus += 0.05
    except (TypeError, ValueError):
        pass
    return bonus


def _collision_family_penalty(
    metadata: Dict[str, Any],
    recent_families: List[str],
) -> float:
    """Return -0.20 if collision_family matches any family in the recent window.

    recent_families: collision_family values from the previous 2 chapters' selected atoms.
    Returns 0.0 when field absent or no match.
    """
    cf = str(metadata.get("collision_family") or "").strip()
    if not cf:
        return 0.0
    if cf in recent_families:
        return -0.20
    return 0.0


def _try_content_bank_fallback(
    *,
    reg: Any,
    slot_type: str,
    seed_key: str,
    topic: str,
    persona_id: str,
    frame: str,
    runtime_format: str,
    chapter_index0: int,
    seed: str,
    chapter_targets: Dict[str, Any],
) -> Optional[Tuple[str, str, str, Dict[str, Any]]]:
    """Return (content, source, source_id, score_meta) or None."""
    from phoenix_v4.content_banks.selector import (
        FragmentContext,
        _collect_candidates,
        reflection_band_window,
    )

    st = slot_type.strip().upper()
    aliases = _ENRICH_BANK_SLOT_TYPES.get(st, ())
    if not aliases:
        return None
    # Late-book REFLECTION (chapters 7–12, index ≥ 6): try REFLECTION slot type first
    # so anxiety_genz_reflection_late_book_bank.yaml variants are prioritised before
    # the generic MECHANISM_BRIDGE fallback.
    if st == "REFLECTION" and chapter_index0 >= 6:
        aliases = ("REFLECTION",) + tuple(aliases)
    stems = list(reg.banks.keys())
    if not stems:
        return None
    # Wire band window for REFLECTION: ch7/8 → bands {2,3}, ch9+ → {3,4}, earlier → None.
    # Fixes self_worth/grief ch7/ch8 CONTENT GAP — atoms exist in pool but were not
    # reaching the enrichment path because allowed_bands was never set on FragmentContext.
    _bands = reflection_band_window(chapter_index0 + 1) if st == "REFLECTION" else None
    ctx = FragmentContext(
        topic_id=topic,
        persona_id=persona_id,
        frame=frame,
        runtime_format_id=runtime_format,
        chapter_index=chapter_index0,
        book_seed=seed,
        slot_key=seed_key,
        allowed_bands=_bands,
    )
    pool: List[dict[str, Any]] = []
    for alias in aliases:
        pool.extend(_collect_candidates(reg, stems, alias, ctx))
    if not pool:
        return None
    pool.sort(key=lambda r: str(r.get("variant_id") or ""))
    scored = sorted(
        pool,
        key=lambda r: (
            -_bestseller_metadata_score(r, chapter_targets),
            str(r.get("variant_id") or ""),
        ),
    )
    digest = hashlib.sha256(seed_key.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(scored)
    picked = scored[idx]
    body = str(picked.get("body") or "").strip()
    if len(body.split()) < 11:
        return None
    vid = str(picked.get("variant_id") or "")
    bscore = _bestseller_metadata_score(picked, chapter_targets)
    return (
        body,
        "content_bank",
        vid,
        {"bestseller_target_score": bscore, "content_bank_variant_id": vid},
    )

def _load_runtime_word_bounds(
    runtime_format: str,
    repo_root: Path,
) -> Optional[Tuple[int, int]]:
    """Return (min_words, max_words) from config/format_selection/format_registry.yaml."""
    rf = (runtime_format or "").strip()
    if not rf:
        return None
    path = repo_root / "config" / "format_selection" / "format_registry.yaml"
    if not path.exists():
        return None
    data = _load_yaml(path)
    block = (data.get("runtime_formats") or {}).get(rf)
    if not isinstance(block, dict):
        return None
    wr = block.get("word_range")
    if not isinstance(wr, (list, tuple)) or len(wr) < 2:
        return None
    try:
        lo = int(wr[0])
        hi = int(wr[1])
    except (TypeError, ValueError):
        return None
    if hi <= 0:
        return None
    return lo, hi


@dataclass
class EnrichmentRequest:
    beatmap: Beatmap
    teacher_id: Optional[str]
    persona_id: str
    topic_id: str
    seed: str
    spine_context: Optional[Dict[str, Any]] = None
    content_banks_dir: Optional[Path] = None
    ei_v2_config: Optional[Dict[str, Any]] = None  # P0.9: hybrid_select wiring
    # Locale for persona-atom loading (e.g. 'ja-JP', 'zh-TW'). When set and not 'en-US',
    # persona atoms are read from atoms/{persona}/{topic}/{slot}/locales/{locale}/CANONICAL.txt
    # with a fallback to the base English CANONICAL.txt when the locale variant is missing.
    # Mirrors the locale-aware loading already present in prose_resolver.py for the
    # registry/teacher path.
    locale: Optional[str] = None
    # Legacy flags preserved as no-ops for backward-compat with older callers.
    # additive_enrichment is the ONLY mode (PR #612). publishable_book is implicit —
    # gap always raises EnrichmentGapError.
    publishable_book: bool = True  # no-op — kept to avoid breaking callers
    additive_enrichment: bool = True  # no-op — stacking is the only mode


@dataclass
class EnrichedSlot:
    slot_type: str
    content: str
    source: str
    source_id: str
    target_words: int
    actual_words: int
    enrichment_applied: List[str]
    exercise_phase: Optional[str] = None
    journey_exercise_id: Optional[str] = None
    variant_id: str = ""
    atom_id: str = ""
    teacher_content: str = ""
    match_scores: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichedChapter:
    number: int
    role: str
    working_title: str
    thesis: str
    slots: List[EnrichedSlot]
    total_words: int
    source_breakdown: Dict[str, int]
    exercise_journey: Optional[Dict[str, Any]] = None


@dataclass
class EnrichedBook:
    schema_version: int
    stage: str
    topic: str
    teacher_id: Optional[str]
    persona_id: str
    runtime_format: str
    chapters: List[EnrichedChapter]
    total_words: int
    enrichment_audit: Dict[str, Any]
    spine_context: Dict[str, Any] = field(default_factory=dict)
    # Locale propagated from EnrichmentRequest so depth pass + downstream
    # passes can re-use the same locale-aware atom loading path.
    locale: Optional[str] = None


# Non-null sentinel teacher_id used ONLY to drive generalized-mode wrapper framing
# for composite (no-teacher) brand doctrine. It deliberately has NO teacher_registry
# entry, so resolve_wrapper resolves no TEACHER_NAME and selects generalized mode
# (teacher_wrapper.py:216-219). It is never used for teacher-bank atom loading.
_GENERALIZED_WRAPPER_SENTINEL = "__generalized__"


def _norm_teacher_id(teacher_id: Optional[str]) -> Optional[str]:
    if not teacher_id:
        return None
    t = teacher_id.strip()
    return t.lower() if t else None


def _chapter_key(chapter_num: int) -> str:
    return f"chapter_{chapter_num:02d}"


# DEFECT 4 (cross-persona bleed, COMPOSER_FRONTIER_FIX_SPEC_20260614): registry/
# {topic}.yaml is topic-keyed and was authored 100% from one persona (label
# "Gen Z" == persona_id "gen_z_professionals"). The registry read path had NO
# persona filter, so corporate_managers books rendered gen_z-authored HOOK
# content (verified books 04/05, 12 foreign lines each). The fix below makes the
# registry read persona-aware: any section whose `metadata.persona` resolves to a
# DIFFERENT persona_id than the spine persona is dropped; on no-match the
# selector falls through to persona_atom/teacher (mirrors the OPD-118
# "no cross-persona spillover" policy, extended from deep_book_6h to standard_book).

# Explicit registry-label -> canonical persona_id aliases. The registry stores a
# display label ("Gen Z"); the spine emits a persona_id ("gen_z_professionals").
# This map disambiguates labels that a token match alone cannot resolve (e.g.
# bare "Gen Z" must map to gen_z_professionals, NOT gen_z_student).
_REGISTRY_PERSONA_LABEL_ALIASES: Dict[str, str] = {
    "genz": "gen_z_professionals",
    "genzprofessional": "gen_z_professionals",
    "genzprofessionals": "gen_z_professionals",
}

# Unauthored registry stub content (e.g. "[Persona-specific hook for X × Y]").
# Per DEFECT 4 fix point (3): reject these so placeholder text never renders
# regardless of persona. Matches a bracketed editorial stub that names a hook.
_REGISTRY_PLACEHOLDER_RE = re.compile(
    r"^\s*\[[^\]]*\b(?:persona-specific|hook for|placeholder|tbd|tktk|todo|draft)\b[^\]]*\]\s*$",
    re.IGNORECASE,
)


def _norm_persona_token(value: Any) -> str:
    """Reduce a persona id/label to a comparable lowercase alphanumeric token.

    "Gen Z" -> "genz"; "gen_z_professionals" -> "genzprofessionals".
    """
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _registry_persona_canonical(label: Any) -> str:
    """Resolve a registry persona label to a canonical persona_id token.

    Returns the normalized alphanumeric token of the resolved persona_id, or ""
    when the label is blank (unknown/unlabeled -> caller treats as "no claim").
    """
    tok = _norm_persona_token(label)
    if not tok:
        return ""
    if tok in _REGISTRY_PERSONA_LABEL_ALIASES:
        return _norm_persona_token(_REGISTRY_PERSONA_LABEL_ALIASES[tok])
    return tok


def _registry_persona_matches(section_persona_label: Any, spine_persona_id: str) -> bool:
    """True iff a registry section's persona is compatible with the spine persona.

    Fail-OPEN only on absence: a section with NO persona label cannot be proven
    foreign, so it is allowed (absence is not the documented bleed vector — the
    bleed is explicitly-labeled "Gen Z" leaking into other personas). A section
    whose label resolves to a DIFFERENT persona_id than the spine is rejected.
    When the spine persona_id is itself blank we cannot compare, so allow.
    """
    spine_tok = _norm_persona_token(spine_persona_id)
    if not spine_tok:
        return True
    sec_tok = _registry_persona_canonical(section_persona_label)
    if not sec_tok:
        return True
    if sec_tok == spine_tok:
        return True
    # Prefix tolerance for label/id granularity drift (e.g. a label that
    # resolves to the family stem of a more specific spine id), but only when
    # the section token is a strict prefix of the spine token AND not itself a
    # known sibling alias — this keeps gen_z_professionals vs gen_z_student
    # distinct because both resolve via the alias map to full ids.
    return False


def _registry_section_persona(sec_data: Dict[str, Any]) -> Any:
    """Extract a section's authored persona label from its metadata block."""
    meta = sec_data.get("metadata") if isinstance(sec_data.get("metadata"), dict) else {}
    return meta.get("persona") or sec_data.get("persona")


def _registry_type_lists(
    ch_data: Dict[str, Any],
    persona_id: str = "",
) -> Dict[str, List[Dict[str, Any]]]:
    """Group a chapter's registry sections by slot type.

    When ``persona_id`` is provided, sections whose authored persona resolves to
    a different persona_id are dropped (DEFECT 4 cross-persona-bleed fix). A
    section with no persona label is retained (cannot be proven foreign).
    """
    sections = ch_data.get("sections") or {}
    by_type: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    if not isinstance(sections, dict):
        return by_type
    spine_tok = _norm_persona_token(persona_id)
    for sec_key in sorted(sections.keys()):
        sec_data = sections[sec_key]
        if not isinstance(sec_data, dict):
            continue
        if spine_tok and not _registry_persona_matches(
            _registry_section_persona(sec_data), persona_id
        ):
            logger.warning(
                "DEFECT4: dropping registry section %s (persona=%r) — foreign to "
                "spine persona_id=%r; falling through to persona_atom/teacher.",
                sec_key, _registry_section_persona(sec_data), persona_id,
            )
            continue
        st = str(sec_data.get("type") or "REFLECTION").strip().upper()
        by_type[st].append(sec_data)
    return by_type


def _pick_teacher_pool(teacher_atoms: Dict[str, List[dict]], slot_type: str) -> List[dict]:
    st = slot_type.strip().upper()
    if st not in _TEACHER_OVERLAY_TYPES:
        return []
    for dir_name in _TEACHER_TYPE_MAP.get(st, [st]):
        pool = teacher_atoms.get(dir_name, [])
        if pool:
            return pool
    return []


def _doctrine_rotation_active(
    topic_id: str,
    spine_context: Optional[Dict[str, Any]],
    *,
    repo_root: Optional[Path] = None,
) -> bool:
    ctx = spine_context or {}
    if ctx.get("chapter_continuity_plan"):
        return True
    topic = (topic_id or "").strip()
    sequences = (
        (load_doctrine_rotation_config(repo_root).get("topic_sequences") or {}).get(topic)
    )
    return bool(sequences)


def _try_composite_content(
    composite_atoms: Dict[str, List[dict]],
    slot_type: str,
    seed_key: str,
    *,
    topic_id: str = "",
    persona_id: str = "",
    book_frame: str = "somatic_first",
    seen_bodies: Any = None,
    chapter_index0: int = 0,
    spine_context: Optional[Dict[str, Any]] = None,
    used_doctrine_ids: Optional[set[str]] = None,
    recent_doctrine_ids: Optional[List[str]] = None,
    chapter_count: Optional[int] = None,
    repo_root: Optional[Path] = None,
) -> Optional[Tuple[str, str, int, Dict[str, Any]]]:
    """Regular mode: topic composite doctrine/reflection before persona pool."""
    pool = _pick_composite_pool(composite_atoms, slot_type)
    pool = [
        a
        for a in pool
        if not _is_doctrine_quarantined(str(a.get("content") or ""), book_frame)
        and atom_passes_book_governance(
            a.get("metadata"),
            topic_id=topic_id,
            persona_id=persona_id,
            book_frame=book_frame,
        )
    ]
    if not pool:
        return None

    if is_reflection_rotation_slot(slot_type) and _doctrine_rotation_active(
        topic_id, spine_context, repo_root=repo_root,
    ):
        assigned = resolve_chapter_doctrine_id(
            topic_id,
            chapter_index0,
            spine_context=spine_context,
            book_frame=book_frame,
            repo_root=repo_root,
        )
        if not assigned:
            return None
        # `assigned` IS this chapter's single doctrine (doctrine_distribution_plan
        # rule 1). Passing it as current_chapter_doctrine_id lets the guard tell an
        # intra-chapter re-pick (multi-REFLECTION templates like deep_book_6h resolve
        # the same doctrine for each REFLECTION slot — allowed) apart from a genuine
        # cross-chapter repeat. Under bounded reuse the guard permits SPACED repeats
        # (window = min(pool_size, chapter_count)) and, when the assigned variant is
        # missing or would repeat too soon, degrades to a least-recently-used pool
        # atom — never dropping the slot (silent gap) or raising (the pre-#4673 crash).
        atom = pick_doctrine_atom_by_id(
            pool,
            assigned,
            used_doctrine_ids=used_doctrine_ids,
            current_chapter_doctrine_id=assigned,
            recent_doctrine_ids=recent_doctrine_ids,
            chapter_count=chapter_count,
        )
        if is_twelve_shape_continuity_active(spine_context) and assigned:
            exact = _pick_persona_atom_by_id(pool, assigned) or next(
                (
                    a
                    for a in pool
                    if normalize_doctrine_id(str(a.get("atom_id") or ""))
                    == normalize_doctrine_id(assigned)
                ),
                None,
            )
            if exact:
                atom = exact
        if not atom:
            return None
        content = str(atom.get("content") or "").strip()
        if not content:
            return None
        # Use the RETURNED atom's id — an LRU fallback may hand back a different
        # variant than `assigned`, so key aid/idx off what was actually picked.
        aid = str(atom.get("atom_id") or assigned)
        picked_norm = normalize_doctrine_id(aid)
        logger.info(
            "doctrine_rotation: ch%s topic=%s assigned=%s atom=%s",
            chapter_index0 + 1,
            topic_id,
            normalize_doctrine_id(assigned),
            aid,
        )
        idx = next(
            (i for i, a in enumerate(pool) if normalize_doctrine_id(str(a.get("atom_id") or "")) == picked_norm),
            0,
        )
        return content, aid, idx, dict(atom.get("metadata") or {})

    # Dedup-aware pick: deterministic anchor, then walk forward skipping bodies
    # already used book-wide — reuses the SAME _SeenBodies exact+fuzzy membership
    # as the persona path (no parallel dedup). Falls back to the anchor when every
    # block is already seen, preserving determinism + the never-empty contract.
    # Without this, two chapters whose seed_keys collide to the same index
    # re-drew the SAME section_06 block (the repeated-phrase Hold residual).
    anchor = _deterministic_index(f"{seed_key}:composite", len(pool))
    idx = anchor
    if seen_bodies:
        n = len(pool)
        _found = False
        for _step in range(n):
            _j = (anchor + _step) % n
            _body = str(pool[_j].get("content") or "")
            if not _body.strip():
                continue
            if _norm_ws(_body) in seen_bodies or _seen_similar(seen_bodies, _body):
                continue
            idx = _j
            _found = True
            break
        if not _found:
            # Pool exhausted book-wide (more composite slots than distinct blocks)
            # → return None so the caller defers to the persona pool rather than
            # re-drawing an already-used block (which trips repeated-phrase density).
            return None
    atom = pool[idx]
    content = str(atom.get("content") or "").strip()
    if not content:
        return None
    aid = str(atom.get("atom_id") or f"composite_{idx}")
    return content, aid, idx, dict(atom.get("metadata") or {})


def _try_teacher_content(
    teacher_atoms: Dict[str, List[dict]],
    slot_type: str,
    seed_key: str,
    *,
    topic_id: str = "",
    persona_id: str = "",
    book_frame: str = "somatic_first",
) -> Optional[Tuple[str, str, int, Dict[str, Any]]]:
    pool = _pick_teacher_pool(teacher_atoms, slot_type)
    pool = [
        a
        for a in pool
        if atom_passes_book_governance(
            a.get("metadata"),
            topic_id=topic_id,
            persona_id=persona_id,
            book_frame=book_frame,
        )
    ]
    if not pool:
        return None
    idx = _deterministic_index(f"{seed_key}:teacher", len(pool))
    atom = pool[idx]
    content = str(atom.get("content") or "").strip()
    if not content:
        return None
    aid = str(atom.get("atom_id") or f"auto_{idx}")
    meta = dict(atom.get("metadata") or {})
    return content, aid, idx, meta


def _try_persona_content(
    persona_atoms: Dict[str, List[dict]],
    slot_type: str,
    seed_key: str,
    *,
    topic_id: str = "",
    persona_id: str = "",
    book_frame: str = "somatic_first",
) -> Optional[Tuple[str, str, int, Dict[str, Any]]]:
    st = slot_type.strip().upper()
    if st not in _PERSONA_OVERLAY_TYPES:
        return None
    pool = [
        a
        for a in (persona_atoms.get(st, []))
        if atom_passes_book_governance(
            a.get("metadata"),
            topic_id=topic_id,
            persona_id=persona_id,
            book_frame=book_frame,
        )
    ]
    if not pool:
        return None
    idx = _deterministic_index(f"{seed_key}:persona", len(pool))
    atom = pool[idx]
    content = str(atom.get("content") or "").strip()
    if not content:
        return None
    meta = dict(atom.get("metadata") or {})
    return content, str(atom.get("atom_id") or f"persona_{idx}"), idx, meta


# ---------------------------------------------------------------------------
# EXERCISE-slot contract: practice-with-steps only, no teaching essays
# ---------------------------------------------------------------------------
# Background (PR #612 follow-up): teacher_atoms[EXERCISE] is loaded by directory
# name (SOURCE_OF_TRUTH/teacher_banks/<tid>/approved_atoms/EXERCISE/*.yaml), but
# some atoms in that directory are kb_mine_v1 essay synthesis from blog RTF —
# their content is teaching prose ("Bhakti Yoga is the practice of...", "selfless
# giving teaches us to..."), not instruction-with-steps. The keen-sinoussi book
# audit caught this: EXERCISE slot rendered an essay about Bhakti Yoga where the
# reader expected "count five breaths, place your hand on your chest". This
# filter refuses essay-shaped atoms at selection time; the fallback chain
# (practice_library) then provides the actual practice.
#
# Heuristic: an atom is treated as practice-shaped iff
#   (a) its metadata declares slot_type == "exercise" / shape == "practice", OR
#   (b) its content contains at least one practice-step marker (imperative verbs
#       like "count", "notice", "place your", "inhale", "exhale", "breathe",
#       "feel", "hold", a numbered-step prefix like "1.", "Step 1", or a
#       sensory/body cue like "tongue", "shoulders", "jaw").
# Essay markers ("Bhakti Yoga teaches", "transcendent", "is the practice of"
# without imperative) are NOT positive evidence; we require positive practice
# evidence to pass.
_PRACTICE_STEP_MARKERS: tuple[str, ...] = (
    "inhale",
    "exhale",
    "breathe in",
    "breathe out",
    "count to ",
    "count five",
    "count four",
    "count three",
    "count down",
    "count back",
    "place your hand",
    "place your palm",
    "place your feet",
    "place one hand",
    "place both hands",
    "rest your hand",
    "rest your palm",
    "notice the ",
    "notice your ",
    "notice how ",
    "notice what ",
    "notice where ",
    "feel your ",
    "feel the ",
    "feel where ",
    "drop your shoulders",
    "soften your jaw",
    "unclench your jaw",
    "relax your tongue",
    "step 1",
    "step 2",
    "step one",
    "step two",
    "first, ",
    "next, ",
    "then, ",
    "now, ",
    "for thirty seconds",
    "for sixty seconds",
    "for one minute",
    "for two minutes",
    "for five minutes",
    "close your eyes",
    "open your eyes",
    "sit comfortably",
    "stand with your",
    "lie down on",
)

# Numbered-step regex: lines starting with "1.", "1)", "(1)" etc.
_NUMBERED_STEP_RE = re.compile(r"(?m)^\s*(?:\(?\d{1,2}[\.\)])\s+\S")

# ---------------------------------------------------------------------------
# OPD-107 follow-up: negative-evidence (residue) guards for _is_practice_atom
# ---------------------------------------------------------------------------
# Background: ahjan_EXERCISE_064_mined ships as a `body:` field whose content
# begins with `Helvetica;ArialMT; ;;;;; ;; ...Step 1. Choose products...`.
# The literal substring "Step 1." trips _NUMBERED_STEP_RE / _PRACTICE_STEP_MARKERS
# and the atom is accepted as a valid practice atom. It then wins all 24 EXERCISE
# slots in ahjan x gen_z_professionals x anxiety x deep_book_6h (Book 3),
# blocking the persona-pool fallthrough that OPD-107 (PR #1211) plumbed in.
#
# Root cause: positive-evidence patterns ("Step 1.", "first,", "now,") fire
# inside RTF/blog residue text just as readily as inside legitimate practice
# scripts. We need an *additive* negative-evidence pass: if any marker in
# _RESIDUE_MARKERS is found in the atom content (case-insensitive substring),
# reject the atom regardless of positive evidence.
#
# Markers are grouped by source:
#  - Font-stack tells: RTF \fonttbl ASCII output leaves bare font family
#    names followed by ; or , (e.g. "Helvetica;", "ArialMT;", "Times New Roman,")
#  - RTF artifact tokens: leftovers from raw RTF parses that escape mining
#  - HTML/markdown residue: tags or entities never rendered out
#  - Blog/marketing tells: high-confidence non-practice content signals
#    (affiliate marketing posts, YouTube CTAs, URL fragments). A real practice
#    script never says "Click here" or links to https://...
#  - Mining-tool stamps: synthesis_method may say kb_mine_v1, but body text
#    sometimes carries through "kb_mine" / "synthesis_method" artifacts too.
#
# All markers are lowercase substrings; content is lowercased before match.
# To add an exception (a legitimate atom that intentionally contains one of
# these markers), append the atom_id to _PRACTICE_RESIDUE_ALLOWLIST below.
_RESIDUE_MARKERS: tuple[str, ...] = (
    # --- Font-stack tells (RTF \fonttbl residue) ----------------------------
    # Bare font family names followed by ; or , — never appears in clean prose.
    "helvetica;",
    "helvetica,",
    "arialmt;",
    "arialmt,",
    "times new roman;",
    "times new roman,",
    "courier;",
    "courier,",
    "verdana;",
    "verdana,",
    "georgia;",
    "georgia,",
    # --- RTF artifact tokens ------------------------------------------------
    # Survives raw RTF if the parser misses control-word stripping.
    r"\fonttbl",
    r"\rtf1",
    r"\fs2",
    r"\f0\fs",
    "{\\colortbl",
    ";}\\",
    # --- HTML / markdown residue --------------------------------------------
    # Practice scripts are plain prose; HTML tags = unconverted source residue.
    "<p>",
    "</p>",
    "<br>",
    "<br/>",
    "<br />",
    "<div",
    "</div>",
    "<span",
    "</span>",
    "&nbsp;",
    "&amp;",
    "&quot;",
    # --- Blog / marketing tells ---------------------------------------------
    # Practice scripts never include affiliate-marketing CTAs or URLs.
    "click here",
    "affiliate marketing",
    "affiliate link",
    "affiliate product",
    "affiliate program",
    "subscribe to",
    "youtube channel",
    "youtube video",
    "comparison video",
    "step-by-step guide on how to do it",  # blog phrasing, never a real cue
    "potential earnings",
    "hypothetical example",
    "http://",
    "https://",
    "www.",
    # --- Mining-tool stamps -------------------------------------------------
    # If any of these survive into atom content, the body was assembled
    # mechanically without prose normalization.
    "synthesis_method:",
    "quote_hash:",
    "kb_mine_v1",
    "doc_id:",
)


# Allow-list escape-hatch: explicit atom_ids that pass the residue filter
# even if their content contains one of _RESIDUE_MARKERS. Empty by default.
# Add only after operator review; entries should explain why the marker is
# intentional (e.g. a teaching atom that intentionally references a URL or
# discusses HTML tags pedagogically). Maintained in code (not YAML) to keep
# the filter logic self-contained and auditable; switch to a config file
# only when this list exceeds ~10 entries.
_PRACTICE_RESIDUE_ALLOWLIST: frozenset[str] = frozenset({
    # Format: "atom_id"  # reason
})


def _has_residue_markers(content_lower: str) -> bool:
    """Return True iff content contains any RTF / blog / HTML residue marker.

    `content_lower` MUST already be lowercased by the caller (we don't
    re-lowercase per marker for performance).
    """
    if not content_lower:
        return False
    for marker in _RESIDUE_MARKERS:
        if marker in content_lower:
            return True
    return False


def _is_practice_atom(atom: dict, *, atom_id: str = "", source_path: str = "") -> bool:
    """Return True iff atom looks like instruction-with-steps, not a teaching essay.

    Multi-signal classifier; positive practice evidence required.
    Reference: enrichment_select.py:988 EXERCISE branch (PR #612 follow-up).

    OPD-107 follow-up (residue filter): atoms whose content contains RTF font-
    stack tells (`Helvetica;`), HTML residue (`<p>`), blog/marketing tells
    (`Click here`, `https://`), or mining-tool stamps (`kb_mine_v1`) are
    rejected before any positive evidence is considered. Rationale: such
    atoms were mined from raw RTF blog files and never sanitized; their
    "Step 1."/"first,"/"now," substrings are residue from the source doc,
    not real practice cues. Add atom_ids to _PRACTICE_RESIDUE_ALLOWLIST to
    bypass this check (for intentional URL or HTML-discussion content).
    """
    if not isinstance(atom, dict):
        return False

    # Resolve effective atom_id (caller may pass explicitly, else read from dict).
    eff_atom_id = atom_id or str(atom.get("atom_id") or "").strip()

    # Read content early — residue check runs BEFORE metadata short-circuits
    # because metadata flags (slot_type: exercise) can't compensate for an atom
    # whose body is literal blog scaffolding. Atoms also load content from
    # `body` upstream (registry_resolver._load_teacher_atoms) so by the time we
    # see them the field is always "content".
    content_lower = str(atom.get("content") or "").strip().lower()

    # Negative evidence (additive filter): reject residue regardless of any
    # positive signal, unless explicitly allow-listed by operator.
    if content_lower and eff_atom_id not in _PRACTICE_RESIDUE_ALLOWLIST:
        if _has_residue_markers(content_lower):
            return False

    meta = atom.get("metadata") or {}
    if isinstance(meta, dict):
        slot_meta = str(meta.get("slot_type") or "").strip().lower()
        if slot_meta in ("exercise", "practice"):
            return True
        shape_meta = str(meta.get("shape") or meta.get("atom_shape") or "").strip().lower()
        if shape_meta in ("practice", "instruction", "exercise"):
            return True
        atom_type = str(meta.get("atom_type") or meta.get("type") or "").strip().lower()
        if atom_type in ("practice", "exercise", "instruction"):
            return True

    if not content_lower:
        return False

    # Numbered step list is strong practice evidence.
    if _NUMBERED_STEP_RE.search(content_lower):
        return True

    # Imperative / sensory step markers — case-insensitive substring search.
    for marker in _PRACTICE_STEP_MARKERS:
        if marker in content_lower:
            return True

    return False


def _filter_practice_pool(pool: List[dict]) -> List[dict]:
    """Keep only atoms whose content is instruction-with-steps (not teaching essay)."""
    return [a for a in (pool or []) if _is_practice_atom(a)]


_ANGLE_FALLBACK_CACHE: Optional[dict[str, Any]] = None


def _load_angle_journey_fallback() -> dict[str, Any]:
    global _ANGLE_FALLBACK_CACHE
    if _ANGLE_FALLBACK_CACHE is not None:
        return _ANGLE_FALLBACK_CACHE
    path = REPO_ROOT / "config" / "planning" / "angle_journey_fallback.yaml"
    _ANGLE_FALLBACK_CACHE = _load_yaml(path) if path.exists() else {}
    return _ANGLE_FALLBACK_CACHE


def _angle_entry_meta(angle_id: str) -> dict[str, Any]:
    from phoenix_v4.planning.angle_journey import merge_angle_journey
    from phoenix_v4.planning.angle_resolver import get_angle_context, load_angle_registry

    reg = load_angle_registry()
    leaf = get_angle_context(angle_id) or {}
    journey = merge_angle_journey(angle_id, reg)
    return {
        "display_name": str(leaf.get("display_name") or angle_id),
        "core_frame": str(leaf.get("core_frame") or ""),
        "analogy_lens": str(journey.get("analogy_lens") or ""),
        "layer_progression": list(journey.get("layer_progression") or []),
    }


def _read_text_atom(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _try_angle_definition(
    *,
    persona_id: str,
    topic_id: str,
    angle_id: str,
    repo_root: Path,
    fallback_warnings: List[str],
) -> Optional[Tuple[str, str, str]]:
    aid = (angle_id or "").strip()
    if not aid or not persona_id or not topic_id:
        return None
    base = repo_root / "atoms" / persona_id / topic_id / "ANGLE_DEFINITION" / aid / "CANONICAL.txt"
    body = _read_text_atom(base)
    if body:
        return body, "angle_atom", f"angle_def:{aid}"
    meta = _angle_entry_meta(aid)
    lens = meta["analogy_lens"]
    from phoenix_v4.planning.angle_journey import family_default_angle_id

    fam = family_default_angle_id(lens) if lens else None
    if fam and fam != aid:
        fam_path = repo_root / "atoms" / persona_id / topic_id / "ANGLE_DEFINITION" / fam / "CANONICAL.txt"
        body = _read_text_atom(fam_path)
        if body:
            fallback_warnings.append(
                f"ANGLE_DEFINITION: family default {fam!r} for {aid!r}"
            )
            return body, "angle_atom_family", f"angle_def_family:{fam}"
    fb = (_load_angle_journey_fallback().get("generic") or {}).get("angle_definition") or ""
    tpl = str(fb).format(
        display_name=meta["display_name"],
        analogy_lens=lens or "progressive_compression",
        core_frame=meta["core_frame"] or meta["display_name"],
    ).strip()
    fallback_warnings.append(
        f"ANGLE_DEFINITION: planner-template fallback for {aid!r}"
    )
    return tpl, "angle_template", f"angle_def_tpl:{aid}"


def _try_angle_callback(
    *,
    persona_id: str,
    topic_id: str,
    angle_id: str,
    layer: int,
    repo_root: Path,
    fallback_warnings: List[str],
) -> Optional[Tuple[str, str, str]]:
    aid = (angle_id or "").strip()
    if not aid or not persona_id or not topic_id or layer < 1:
        return None
    path = repo_root / "atoms" / persona_id / topic_id / "ANGLE_CALLBACK" / aid / f"level_{layer}.yaml"
    if path.exists():
        data = _load_yaml(path)
        if isinstance(data, dict):
            body = str(data.get("body") or data.get("content") or "").strip()
            if body:
                return body, "angle_atom", f"angle_cb:{aid}:L{layer}"
    meta = _angle_entry_meta(aid)
    lens = meta["analogy_lens"]
    from phoenix_v4.planning.angle_journey import family_default_angle_id

    fam = family_default_angle_id(lens) if lens else None
    if fam and fam != aid:
        fam_path = repo_root / "atoms" / persona_id / topic_id / "ANGLE_CALLBACK" / fam / f"level_{layer}.yaml"
        if fam_path.exists():
            data = _load_yaml(fam_path)
            if isinstance(data, dict):
                body = str(data.get("body") or data.get("content") or "").strip()
                if body:
                    fallback_warnings.append(
                        f"ANGLE_CALLBACK: family default {fam!r} L{layer}"
                    )
                    return body, "angle_atom_family", f"angle_cb_family:{fam}:L{layer}"
    from phoenix_v4.planning.angle_resolver import load_angle_registry

    reg = load_angle_registry()
    chain: list[str] = []
    seen: set[str] = set()
    current: Optional[str] = aid
    while current and current not in seen:
        chain.append(current)
        seen.add(current)
        entry = (reg.get("angles") or {}).get(current) or {}
        parent = str(entry.get("parent_universal") or "").strip()
        current = parent or None
    for candidate in chain:
        if candidate == aid:
            continue
        parent_path = (
            repo_root
            / "atoms"
            / persona_id
            / topic_id
            / "ANGLE_CALLBACK"
            / candidate
            / f"level_{layer}.yaml"
        )
        if not parent_path.exists():
            continue
        data = _load_yaml(parent_path)
        if isinstance(data, dict):
            body = str(data.get("body") or data.get("content") or "").strip()
            if body:
                fallback_warnings.append(
                    f"ANGLE_CALLBACK: parent chain {candidate!r} L{layer} for {aid!r}"
                )
                return body, "angle_atom_parent", f"angle_cb_parent:{candidate}:L{layer}"
    fallback_warnings.append(
        f"ANGLE_CALLBACK: no authored atom L{layer} for {aid!r}; fail-closed"
    )
    return None


def _pick_persona_atom_by_id(pool: list[dict], atom_id: str) -> Optional[dict]:
    target = (atom_id or "").strip()
    if not target or not pool:
        return None
    for atom in pool:
        if str(atom.get("atom_id") or "").strip() == target:
            return atom
    return None


def _try_practice_library_by_id(
    exercise_id: str,
    chapter_index: int,
    seed: str,
    *,
    content_only: bool = False,
) -> Optional[Tuple[str, str]]:
    """Compose a specific practice_library exercise (full or content-only assembly)."""
    try:
        from phoenix_v4.exercises.practice_library_loader import (
            compose_exercise,
            load_component_templates,
            load_practice_library,
        )

        library = load_practice_library()
        all_exercises: List[dict] = []
        for exercises in library.values():
            if isinstance(exercises, list):
                all_exercises.extend(exercises)
        exercise = next((e for e in all_exercises if e.get("id") == exercise_id), None)
        if not exercise:
            logger.warning("practice_library: exercise_id %s not found", exercise_id)
            return None
        composed = compose_exercise(
            exercise,
            chapter_index,
            seed,
            load_component_templates(),
            content_only=content_only,
        )
        if composed and composed.strip():
            return composed.strip(), exercise_id
    except Exception as e:
        logger.warning("Practice library by id failed (%s): %s", exercise_id, e)
    return None


def _try_practice_library(
    chapter_index: int,
    topic_id: str,
    persona_id: str,
    seed: str,
) -> Optional[Tuple[str, str]]:
    try:
        from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter

        composed = get_exercise_for_chapter(
            chapter_index=chapter_index,
            topic_id=topic_id,
            persona_id=persona_id or "",
            seed=seed,
        )
        if composed and composed.strip():
            return composed.strip(), "practice_library"
    except Exception as e:
        logger.warning("Practice library failed: %s", e)
    return None


def _norm_ws(text: str) -> str:
    return " ".join((text or "").split())


def _wc(text: str) -> int:
    return len((text or "").split())


# ─────────────────────────────────────────────────────────────────────────────
# Cross-chapter fuzzy depth-dedup (ws_f1_depth_dedup_20260615, task_48b619ed)
# ─────────────────────────────────────────────────────────────────────────────
# The depth pass (apply_depth_pass) re-reads atom CANONICAL blocks per chapter.
# The legacy dedup kept a PER-CHAPTER set of exact ``_norm_ws(body)`` strings, so
# (a) it never saw what an earlier chapter already used, and (b) even within a
# book-wide set the exact match was defeated by per-chapter trailing-clause
# variation (e.g. the composer appends a different one-line tail to the same HOOK
# atom in each chapter). Result: the SAME atom body (HOOK v02 "The task is open",
# EXERCISE/doctrine blocks) was re-injected across all 12 chapters, producing the
# bulk of the full-12 F1 mass (⑤ leverB attribution: 223/224 deep-tier clusters).
#
# ``_SeenBodies`` replaces that set with a BOOK-WIDE registry that is still
# set-compatible (``x in reg`` exact membership + ``reg.add(x)`` are unchanged, so
# every existing call-site and test keeps working) but additionally exposes
# ``seen_similar(text)`` — a Jaccard word-set overlap check that MIRRORS the
# register-gate F1 detector (``_word_set`` + ``_cosine_jaccard`` at
# ``phoenix_v4/quality/register_gate.py``). A depth candidate whose body is
# ≥ threshold-similar to one already used book-wide is rejected, so the selector
# rotates to an unused sibling ARC block / variant instead of re-stamping the same
# one. Bodies below ``min_words`` are exempt (short transitions may legitimately
# repeat — matches F1's ≥3-sentence floor and the renderer's min_words exemption).
#
# The fuzzy layer is feature-flagged via env ``PHOENIX_DEPTH_DEDUP_FUZZY`` (default
# on); set "0" to fall back to pure exact-match behavior (the pre-fix baseline).
_DEPTH_DEDUP_SIM_THRESHOLD = 0.55   # = register_gate F1_SIMILARITY_THRESHOLD
_DEPTH_DEDUP_MIN_WORDS = 30         # paragraph-class bodies only; short beats exempt
_DEPTH_DEDUP_TOKEN_RE = re.compile(r"[A-Za-z']+")


def _depth_dedup_fuzzy_enabled() -> bool:
    return (os.environ.get("PHOENIX_DEPTH_DEDUP_FUZZY", "1") or "1") != "0"


def _depth_dedup_threshold() -> float:
    """Similarity threshold for the cross-chapter fuzzy depth-dedup.

    Defaults to ``_DEPTH_DEDUP_SIM_THRESHOLD`` (0.55 = register-gate F1) and is
    tunable via ``PHOENIX_DEPTH_DEDUP_THRESHOLD`` for calibration sweeps. Higher
    values dedup only near-identical re-injections (true HOOK/EXERCISE re-stamps,
    Jaccard ~0.85+) and leave merely-thematically-adjacent atoms in place, which
    reduces rotation churn on short tiers.
    """
    raw = os.environ.get("PHOENIX_DEPTH_DEDUP_THRESHOLD")
    if raw:
        try:
            return max(0.0, min(1.0, float(raw)))
        except (TypeError, ValueError):
            pass
    return _DEPTH_DEDUP_SIM_THRESHOLD


def _depth_tokens(text: str) -> List[str]:
    """Lowercased alpha-token list — identical tokenization to register_gate._word_set
    so the dedup operates on exactly the tokens the F1 detector would cluster."""
    return _DEPTH_DEDUP_TOKEN_RE.findall((text or "").lower())


def _depth_word_set(text: str) -> frozenset:
    return frozenset(_depth_tokens(text))


def _depth_jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    union = len(a | b)
    return (len(a & b) / union) if union else 0.0


class _SeenBodies:
    """Book-wide registry of used depth-atom bodies.

    Backward-compatible with the plain ``set`` it replaces:
      * ``_norm_ws(body) in reg``  → exact-string membership (unchanged)
      * ``reg.add(_norm_ws(body))`` → record exact string (unchanged)
    Plus a fuzzy layer for cross-chapter near-duplicate suppression:
      * ``reg.note(raw_body)``      → record the body's word-set for fuzzy checks
      * ``reg.seen_similar(raw_body)`` → True if ≥ threshold-similar to a prior body

    ``add`` also notes the word-set, so the existing call-sites that register a
    used body via ``add(_norm_ws(content))`` automatically populate the fuzzy
    index too — no extra wiring needed at those sites.
    """

    __slots__ = ("_exact", "_sets", "_threshold", "_min_words", "_fuzzy")

    def __init__(self, threshold: Optional[float] = None,
                 min_words: int = _DEPTH_DEDUP_MIN_WORDS,
                 fuzzy: Optional[bool] = None) -> None:
        self._exact: set = set()
        self._sets: List[frozenset] = []
        self._threshold = _depth_dedup_threshold() if threshold is None else threshold
        self._min_words = min_words
        self._fuzzy = _depth_dedup_fuzzy_enabled() if fuzzy is None else fuzzy

    # --- set-compatible surface (used by legacy call-sites/tests) ---
    def __contains__(self, key: str) -> bool:
        return key in self._exact

    def add(self, key: str) -> None:
        self._exact.add(key)
        self.note(key)

    def __len__(self) -> int:  # pragma: no cover - convenience
        return len(self._exact)

    # --- fuzzy surface ---
    def note(self, raw_body: str) -> None:
        """Record a body's word-set so later candidates can be fuzzy-compared.

        Bodies whose TOTAL token count is below ``min_words`` are not indexed —
        short transitions are allowed to repeat. The Jaccard set itself is what's
        stored (deduped tokens) but the size gate is on the raw token count so a
        normal 3-sentence atom paragraph (~30+ words, ~25 unique) still qualifies.
        """
        if not self._fuzzy:
            return
        toks = _depth_tokens(raw_body)
        if len(toks) >= self._min_words:
            self._sets.append(frozenset(toks))

    def seen_similar(self, raw_body: str) -> bool:
        """True if ``raw_body`` is ≥ threshold-similar (Jaccard) to any noted body.

        Short bodies (< min_words TOTAL tokens) are never considered duplicates
        so legitimate short transitions keep repeating.
        """
        if not self._fuzzy:
            return False
        toks = _depth_tokens(raw_body)
        if len(toks) < self._min_words:
            return False
        ws = frozenset(toks)
        thr = self._threshold
        for prev in self._sets:
            if _depth_jaccard(ws, prev) >= thr:
                return True
        return False


def _seen_similar(book_seen_bodies: Any, raw_body: str) -> bool:
    """Duck-typed fuzzy check that tolerates a plain ``set`` (legacy callers).

    Returns False when ``book_seen_bodies`` has no fuzzy layer (e.g. a bare set
    passed by an old test), so those paths keep their exact-only semantics.
    """
    fn = getattr(book_seen_bodies, "seen_similar", None)
    return bool(fn(raw_body)) if callable(fn) else False


def _personas_with_topic(topic: str, repo_root: Path) -> List[str]:
    atoms_root = repo_root / "atoms"
    if not atoms_root.is_dir():
        return []
    out: List[str] = []
    for p in sorted(atoms_root.iterdir()):
        if p.is_dir() and (p / topic).is_dir():
            out.append(p.name)
    return out


def _merged_persona_atoms_deep_6h(
    primary_persona: str,
    topic: str,
    repo_root: Path,
    locale: Optional[str] = None,
) -> Dict[str, List[dict]]:
    """
    OPD-118 (2026-05-20): persona-isolated pool loader for deep_book_6h.

    PRIOR BEHAVIOR (PR #939 Sprint-1, removed here): this function merged
    HOOK/SCENE/STORY atoms from EVERY persona that shared `topic`, so a render
    of `gen_z_professionals × anxiety` was pulling HOOK content authored for
    `tech_finance_burnout × anxiety` (trading-floor vignettes),
    `first_responders × anxiety` (fire-station vignettes), and
    `corporate_managers × anxiety` (executive vignettes). The stitched prose
    read as "scene-scene-scene / all over the place" because each atom was
    written for a different setting and persona voice. This is the root cause
    of the operator's persistent Book 3 cross-persona scene-hopping complaint.

    CURRENT BEHAVIOR: load atoms ONLY from `atoms/{primary_persona}/{topic}/`.
    No cross-persona spillover. If the primary persona's pool is empty for a
    slot, the selector emits a planner WARNING via `PersonaPoolEmptyError`
    rather than silently substituting another persona's content.

    Function signature and return shape preserved so existing callers in
    `select_enrichment` and `peek_registry_content_for_beatmap_slot` keep
    working without edits. The `repo_root` and `_personas_with_topic` params
    are retained for backward-compatibility; `_personas_with_topic` is no
    longer consulted for atom selection.

    When ``locale`` is set and not 'en-US', atoms are loaded from the
    locale-specific CANONICAL.txt where present, falling back to English
    (unchanged from prior behavior; the locale-awareness is intra-persona).
    """
    # Touch repo_root so callers that pass a custom root still resolve via
    # `_load_persona_atoms` (which uses ATOMS_ROOT bound at import time). The
    # arg is preserved in the signature for backward-compat; runtime resolution
    # is unchanged from the rest of the selector.
    _ = repo_root
    primary_atoms = _load_persona_atoms(primary_persona, topic, locale=locale)
    if not primary_atoms:
        logger.warning(
            "OPD-118: persona atom pool empty for '%s/%s' locale=%s — "
            "no cross-persona spillover will be substituted. Author atoms "
            "upstream at atoms/%s/%s/ to resolve.",
            primary_persona, topic, locale or "en-US",
            primary_persona, topic,
        )
        return {}
    merged: Dict[str, List[dict]] = {}
    for st in _PERSONA_OVERLAY_TYPES:
        seen: set[str] = set()
        acc: List[dict] = []
        for atom in primary_atoms.get(st, []):
            txt = str(atom.get("content") or "").strip()
            n = _norm_ws(txt)
            if not n or n in seen:
                continue
            seen.add(n)
            aid = str(atom.get("atom_id") or f"{primary_persona}_{len(acc)}")
            acc.append({"atom_id": aid, "content": txt})
        if acc:
            merged[st] = acc
        else:
            logger.warning(
                "OPD-118: %s pool empty for '%s/%s' locale=%s — selector will "
                "fall through to registry/teacher overlays for this slot type. "
                "Cross-persona substitution is BLOCKED.",
                st, primary_persona, topic, locale or "en-US",
            )
    return merged


def _max_extra_chunks_for_format(runtime_format: str, slot_target_words: int) -> int:
    """Cap additional registry/persona/teacher variants per slot (format + beatmap slot target).

    OPD-109 Phase 1 cap reductions (2026-05-18):
        - deep_book_6h: 18 → 8 (was stacking up to 24 atoms/slot, no bridges)
        - deep_book_4h: 7 → 5
        - extended_book_2h: 5 → 4
        - hard cap on tw-derived extras tightened: was min(24, ...), now min(12, ...)
    Other formats unchanged. Phase 2 will address word-target re-tuning via
    atom expansion. See docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md.
    """
    rf = (runtime_format or "").strip()
    tw = max(0, int(slot_target_words or 0))
    if rf in ("micro_book_15", "micro_book_20"):
        base = 0
    elif rf in ("compact_book_5ch_15min", "compact_book_5ch_20min"):
        # 5 chapters → larger per-chapter share than micro_book_*; allow
        # one extra chunk per slot to fill the higher per-section budget.
        base = 1
    elif rf == "short_book_30":
        base = 1
    elif rf == "compact_book_8ch_30min":
        # 8 chapters at the same word band as short_book_30 (7 chapters);
        # per-chapter share is similar, so match short_book_30's budget.
        base = 1
    elif rf == "standard_book":
        base = 3
    elif rf == "extended_book_2h":
        # OPD-109 Phase 1: was 5; reduced to 4 to thin the per-slot stack.
        base = 4
    elif rf == "deep_book_4h":
        # OPD-109 Phase 1: was 7; reduced to 5.
        base = 5
    elif rf == "deep_book_6h":
        # OPD-109 Phase 1: was 18 (cap min(24, 18+x)); reduced to 8 to address
        # the "type-block dumping" reader experience. Combined with the within-
        # slot bridge generator, this drops Ch1 from ~45 atoms to ~25 while
        # adding 1-sentence transitions between every remaining atom pair.
        base = 8
    else:
        base = 3
    extra = max(0, tw - 320) // 160
    # OPD-109 Phase 1: hard cap tightened from 24 to 12 to keep long-form
    # slots from re-stacking via the tw-derived extra path.
    return min(12, base + extra)


def _extra_registry_variant_bodies(
    sec_data: Dict[str, Any],
    primary_v_idx: int,
    seed_key: str,
    goal_extra_words: int,
    max_chunks: int,
) -> List[str]:
    variants = sec_data.get("variants") or []
    if not variants or goal_extra_words <= 0 or max_chunks <= 0:
        return []
    indices = [i for i in range(len(variants)) if i != primary_v_idx]
    if not indices:
        return []
    indices.sort(
        key=lambda i: hashlib.sha256(f"{seed_key}:rv:{i}".encode("utf-8")).hexdigest()
    )
    primary_norm = ""
    if 0 <= primary_v_idx < len(variants):
        pv = variants[primary_v_idx]
        if isinstance(pv, dict):
            primary_norm = _norm_ws(str(pv.get("content") or ""))
    out: List[str] = []
    seen: set[str] = set()
    running = 0
    for i in indices:
        if running >= goal_extra_words or len(out) >= max_chunks:
            break
        v = variants[i]
        if not isinstance(v, dict):
            continue
        txt = str(v.get("content") or "").strip()
        if _wc(txt) < 11:
            continue
        norm = _norm_ws(txt)
        if not norm or norm == primary_norm or norm in seen:
            continue
        seen.add(norm)
        out.append(txt)
        running += _wc(txt)
    return out


def _expand_atom_pool_blocks(
    pool: List[dict],
    primary_idx: int,
    seed_key: str,
    label: str,
    goal_extra_words: int,
    max_chunks: int,
    rotation_state: Optional["PersonaPoolRotationState"] = None,
) -> List[str]:
    """Pull additional atoms from `pool` to top up a slot toward its target words.

    OPD-109 Phase 3: when `rotation_state` is provided, the candidate order is
    least-used-first (book-level usage), with the original SHA-of-key-label-index
    tiebreak so re-renders at the same seed reproduce. When `rotation_state`
    is None, falls back to pure SHA-ordering (legacy behavior; preserves
    callers that have not adopted the rotation tracker yet).

    Picks are registered into `rotation_state` so subsequent slots see the
    increased usage and prefer not-yet-touched atoms.
    """
    if len(pool) <= 1 or goal_extra_words <= 0 or max_chunks <= 0:
        return []
    if rotation_state is not None:
        # Least-used-first ordering; SHA tiebreak via the state helper.
        order_full = rotation_state.least_used_order(pool, seed_key, label)
        order = [i for i in order_full if i != primary_idx]
    else:
        order = [i for i in range(len(pool)) if i != primary_idx]
        order.sort(
            key=lambda i: hashlib.sha256(
                f"{seed_key}:{label}:{i}".encode("utf-8")
            ).hexdigest()
        )
    primary = pool[primary_idx]
    primary_norm = _norm_ws(str(primary.get("content") or ""))
    out: List[str] = []
    seen: set[str] = {primary_norm} if primary_norm else set()
    running = 0
    for i in order:
        if running >= goal_extra_words or len(out) >= max_chunks:
            break
        atom = pool[i]
        txt = str(atom.get("content") or "").strip()
        if _wc(txt) < 11:
            continue
        norm = _norm_ws(txt)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(txt)
        running += _wc(txt)
        # Register the pick so book-level usage updates for the next slot.
        if rotation_state is not None:
            aid = str(atom.get("atom_id") or "")
            if aid:
                rotation_state.register(aid)
    return out


def _slot_spec_for(
    context: Dict[str, Any],
    chapter_number: int,
    slot_index: int,
) -> Dict[str, Any]:
    specs = (context or {}).get("atom_slot_specs") or {}
    chapter_specs = specs.get(str(chapter_number)) or specs.get(chapter_number) or []
    if isinstance(chapter_specs, list) and 0 <= slot_index < len(chapter_specs):
        item = chapter_specs[slot_index]
        return item if isinstance(item, dict) else {}
    return {}


def _atom_allowed_by_slot_spec(atom: dict, slot_spec: Dict[str, Any]) -> bool:
    """Apply deterministic persona/topic/forbidden tag filters when metadata exists."""
    if not slot_spec:
        return True
    metadata = atom.get("metadata") if isinstance(atom.get("metadata"), dict) else {}
    tags = {
        str(t).strip().lower()
        for t in (
            atom.get("tags")
            or metadata.get("tags")
            or metadata.get("topic_tags")
            or []
        )
    }
    forbidden = {str(t).strip().lower() for t in slot_spec.get("forbidden_tags") or []}
    if tags and forbidden and tags & forbidden:
        return False
    text = str(atom.get("content") or "").lower()
    for bad in forbidden:
        if bad and bad not in {"clinical_dsm"} and bad.replace("_", " ") in text:
            return False
    personas = {str(p).strip() for p in slot_spec.get("persona_filter") or []}
    atom_persona = str(atom.get("persona_id") or metadata.get("persona_id") or "").strip()
    if atom_persona and personas and atom_persona not in personas:
        return False
    topics = {str(t).strip() for t in slot_spec.get("topic_filter") or []}
    atom_topic = str(atom.get("topic_id") or metadata.get("topic_id") or "").strip()
    if atom_topic and topics and atom_topic not in topics:
        return False
    return True


def _filtered_pool(pool: List[dict], slot_spec: Dict[str, Any]) -> List[dict]:
    if not slot_spec:
        return pool
    return [atom for atom in pool if _atom_allowed_by_slot_spec(atom, slot_spec)]


def _try_registry_variant(
    reg_lists: Dict[str, List[Dict[str, Any]]],
    slot_type: str,
    reg_counters: Dict[str, int],
    seed_key: str,
) -> Optional[Tuple[str, str, Dict[str, Any], int]]:
    st = slot_type.strip().upper()
    lst = reg_lists.get(st, [])
    idx = reg_counters[st]
    reg_counters[st] += 1
    if idx >= len(lst):
        return None
    sec_data = lst[idx]
    variants = sec_data.get("variants") or []
    if not variants:
        return None
    v_idx = _deterministic_index(f"{seed_key}:registry", len(variants))
    var = variants[v_idx]
    content = str(var.get("content") or "").strip()
    vid = str(var.get("variant_id") or f"v{v_idx}")
    if not content:
        return None
    # DEFECT 4 fix point (3): reject unauthored registry stubs so placeholder
    # text never renders. Fall through to persona_atom/teacher instead.
    if _REGISTRY_PLACEHOLDER_RE.match(content):
        return None
    return content, vid, sec_data, v_idx


def _peek_registry_variant(
    reg_lists: Dict[str, List[Dict[str, Any]]],
    slot_type: str,
    reg_counters: Dict[str, int],
    seed_key: str,
) -> Optional[Tuple[str, str]]:
    """Same as _try_registry_variant but does not advance reg_counters."""
    st = slot_type.strip().upper()
    lst = reg_lists.get(st, [])
    idx = reg_counters[st]
    if idx >= len(lst):
        return None
    sec_data = lst[idx]
    variants = sec_data.get("variants") or []
    if not variants:
        return None
    v_idx = _deterministic_index(f"{seed_key}:registry", len(variants))
    var = variants[v_idx]
    content = str(var.get("content") or "").strip()
    if not content:
        return None
    # DEFECT 4 fix point (3): reject unauthored registry stubs (see
    # _try_registry_variant). Keeps the peek consistent with selection.
    if _REGISTRY_PLACEHOLDER_RE.match(content):
        return None
    vid = str(var.get("variant_id") or f"v{v_idx}")
    return content, vid


def peek_registry_content_for_beatmap_slot(
    *,
    beatmap: Beatmap,
    chapter_number: int,
    slot_index: int,
    topic_id: str,
    teacher_id: Optional[str],
    persona_id: str,
    seed: str,
    repo_root: Optional[Path] = None,
    locale: Optional[str] = None,
) -> str:
    """
    Registry variant text that would apply at this beatmap slot if teacher/persona/practice
    did not consume the slot — counters match select_enrichment() for prior slots.
    Used to stack teacher (or persona) overlay with registry baseline without double-consuming.
    """
    topic = topic_id
    tid = _norm_teacher_id(teacher_id)
    bm_ch = next((c for c in beatmap.chapters if c.number == chapter_number), None)
    if bm_ch is None or slot_index < 0 or slot_index >= len(bm_ch.slots):
        return ""

    reg = load_registry(topic)
    sections_root = reg.get("sections") or {}
    ch_key = _chapter_key(chapter_number)
    ch_data = sections_root.get(ch_key)
    if not isinstance(ch_data, dict):
        ch_data = {}
    pid = (persona_id or "").strip()
    reg_lists = _registry_type_lists(ch_data, persona_id=pid)
    reg_counters: Dict[str, int] = defaultdict(int)

    root = repo_root or REPO_ROOT
    teacher_atoms: Dict[str, List[dict]] = _load_teacher_atoms(tid) if tid else {}
    rf = (beatmap.runtime_format or "").strip()
    if rf == "deep_book_6h" and pid:
        persona_atoms = _merged_persona_atoms_deep_6h(pid, topic, root, locale=locale)
        # Supplement with remaining slot types (REFLECTION, EXERCISE, etc.) from the
        # primary persona. _merged_persona_atoms_deep_6h only merges HOOK/SCENE/STORY;
        # beatmap slots like the second REFLECTION (slot_index=6) need persona atoms too.
        _primary_atoms = _load_persona_atoms(pid, topic, locale=locale)
        for _st, _atoms in _primary_atoms.items():
            if _st not in persona_atoms and _atoms:
                persona_atoms[_st] = _atoms
    elif pid:
        persona_atoms = _load_persona_atoms(pid, topic, locale=locale)
    else:
        persona_atoms = {}
    chapter_index0 = chapter_number - 1

    for slot_i in range(slot_index):
        slot = bm_ch.slots[slot_i]
        stype = slot.slot_type.strip().upper()
        seed_key = f"{seed}:topic:{topic}:ch{bm_ch.number}:slot:{slot_i}:{stype}"
        content: Optional[str] = None

        if tid and teacher_atoms:
            t_hit = _try_teacher_content(
                teacher_atoms,
                stype,
                seed_key,
                topic_id=topic,
                persona_id=persona_id,
                book_frame="somatic_first",
            )
            if t_hit:
                content = t_hit[0]

        if not content and persona_atoms:
            p_hit = _try_persona_content(
                persona_atoms,
                stype,
                seed_key,
                topic_id=topic,
                persona_id=persona_id,
                book_frame="somatic_first",
            )
            if p_hit:
                content = p_hit[0]

        if not content and stype == "EXERCISE":
            pl = _try_practice_library(chapter_index0, topic, persona_id, seed)
            if pl:
                content = pl[0]

        if not content:
            r_hit = _try_registry_variant(reg_lists, stype, reg_counters, seed_key)
            if r_hit:
                content = r_hit[0]

    stype = bm_ch.slots[slot_index].slot_type.strip().upper()
    seed_key = f"{seed}:topic:{topic}:ch{bm_ch.number}:slot:{slot_index}:{stype}"
    peek = _peek_registry_variant(reg_lists, stype, reg_counters, seed_key)
    return peek[0] if peek else ""


def select_enrichment(
    request: EnrichmentRequest,
    repo_root: Optional[Path] = None,
) -> EnrichedBook:
    root = repo_root or REPO_ROOT
    topic = request.topic_id
    bm = request.beatmap
    seed = request.seed
    persona_id = request.persona_id
    tid = _norm_teacher_id(request.teacher_id)

    reg = load_registry(topic)
    sections_root = reg.get("sections") or {}
    teacher_atoms: Dict[str, List[dict]] = _load_teacher_atoms(tid) if tid else {}
    composite_atoms: Dict[str, List[dict]] = (
        _load_composite_doctrine_atoms(topic, repo_root=root) if not tid else {}
    )
    pid = (persona_id or "").strip()
    locale = request.locale
    # F-COHERENCE (DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC §6): route atom
    # selection by the plan's bound engine — (topic, engine), not topic alone. The engine
    # arrives via spine_context (run_pipeline sets it from arc.engine). It (a) filters the
    # STORY engine-bank pool to that engine in _load_persona_atoms and (b) is folded into
    # the selection seed so every (topic, engine) draws its own deterministic pick from the
    # shared topic-level pools (HOOK/SCENE/REFLECTION/…). Without it, engine-LEGAL siblings
    # (e.g. burnout__overwhelm vs burnout__grief) rendered byte-identical prose.
    engine = str((request.spine_context or {}).get("engine") or "").strip()
    if engine:
        seed = f"{seed}:engine:{engine}"
    rf_bm = (bm.runtime_format or "").strip()
    if rf_bm == "deep_book_6h" and pid:
        persona_atoms = _merged_persona_atoms_deep_6h(pid, topic, root, locale=locale)
        # Supplement with remaining slot types (REFLECTION, EXERCISE, etc.) from the
        # primary persona. _merged_persona_atoms_deep_6h only merges HOOK/SCENE/STORY;
        # beatmap slots like the second REFLECTION (slot_index=6) need persona atoms too.
        _primary_atoms = _load_persona_atoms(pid, topic, locale=locale, engine=engine)
        for _st, _atoms in _primary_atoms.items():
            if _st not in persona_atoms and _atoms:
                persona_atoms[_st] = _atoms
    elif pid:
        persona_atoms = _load_persona_atoms(pid, topic, locale=locale, engine=engine)
    else:
        persona_atoms = {}

    if locale and locale != "en-US":
        logger.info(
            "select_enrichment: locale=%s active for persona atom loading (%s/%s)",
            locale, pid, topic,
        )

    # SPEC-739-THRESHOLD-01: runtime mirror of CI --strict gate.
    _MIN_VARIANTS = 3
    for _stype, _stype_atoms in persona_atoms.items():
        if len(_stype_atoms) < _MIN_VARIANTS:
            raise InsufficientVariantsError(
                f"atom inventory too thin: {pid}/{topic}/{_stype} has "
                f"{len(_stype_atoms)} variant(s), need >= {_MIN_VARIANTS} "
                "(SPEC-739-THRESHOLD-01). Author atoms upstream."
            )

    from phoenix_v4.content_banks.loader import load_content_bank_registry

    try:
        cb_reg = load_content_bank_registry(banks_dir=request.content_banks_dir)
    except Exception as e:
        logger.warning("Content bank registry unavailable: %s", e)
        cb_reg = None

    _spine = request.spine_context or {}
    _frame = str(_spine.get("book_frame") or _spine.get("frame") or "somatic_first").strip()
    _sel_targets = list(_spine.get("chapter_selector_targets") or [])

    format_bounds = _load_runtime_word_bounds(bm.runtime_format, root)
    format_wmax: Optional[int] = format_bounds[1] if format_bounds else None

    audit_counts = {
        "total_slots": 0,
        "slots_from_teacher": 0,
        "slots_from_persona": 0,
        "slots_from_registry": 0,
        "slots_from_practice_library": 0,
        "slots_from_twelve_shape_plan_exercise": 0,
        "practice_library_warnings": 0,
        "slots_empty": 0,
        "slots_format_scaled": 0,
        "format_word_cap_max": format_wmax,
        "slots_from_content_bank": 0,
    }
    total_target_words = 0
    gap_details: List[Dict[str, Any]] = []

    enriched_chapters: List[EnrichedChapter] = []
    plan_context = dict(request.spine_context or {})
    if pid and topic:
        _existing_plan = plan_context.get("chapter_continuity_plan")
        if not _existing_plan:
            _loaded_plan = load_chapter_continuity_plan(pid, topic, root)
            if _loaded_plan:
                plan_context["chapter_continuity_plan"] = _loaded_plan
                plan_context.setdefault("twelve_shape_continuity", True)
    _angle_id_enrich = str(plan_context.get("angle_id") or "").strip()
    _angle_layer_by_ch = dict(plan_context.get("angle_layer_by_chapter") or {})
    _angle_fallback_warnings: List[str] = list(plan_context.get("angle_journey_warnings") or [])

    # ACT-007: collision_family dedup — track families used in last 2 chapters
    # Each entry is a list of collision_family values for that chapter (0-based index).
    _chapter_collision_families: List[List[str]] = []

    _book_tracker = BookSlotTracker()

    # OPD-109 Phase 3: per-book rotation state for persona atom picks. Prefers
    # least-used atoms (with deterministic SHA tiebreak), so the selector spreads
    # picks across the available pool instead of hammering the same 3-5 atoms
    # across all 96 SCENE-class slots. See `PersonaPoolRotationState` doc above.
    _persona_rotation = PersonaPoolRotationState()
    _scene_arch_rotation = SceneArchetypeRotationState()
    # ws_enrichment_primary_dedup_20260616: book-wide registry of PRIMARY bodies
    # already stamped into a slot, so the same HOOK/SCENE/STORY/EXERCISE body is
    # not re-picked as the primary across chapters/clusters. Same _SeenBodies
    # registry the depth/delivery passes already use (exact + fuzzy Jaccard);
    # gated by the same PHOENIX_DEPTH_DEDUP_FUZZY flag. The least-used rotation
    # still drives ordering — this only skips already-used bodies within that
    # order, falling back to the deterministic anchor when none are unused.
    _book_seen_bodies = _SeenBodies()
    _book_used_hooks: set[str] = set()
    _book_used_doctrine_ids: set[str] = set()
    # Bounded-reuse doctrine rotation: ORDERED per-chapter doctrine history (keyed by
    # chapter_index0) so the picker can enforce a spacing window instead of the old
    # unordered no-repeat set. Keyed per chapter — multi-REFLECTION slots re-stamp the
    # same chapter's doctrine, they do not extend the history.
    _book_doctrine_by_chapter: Dict[int, str] = {}
    _book_chapter_count = len(bm.chapters) if getattr(bm, "chapters", None) else 12
    _identity_contract = None
    try:
        from phoenix_v4.planning.book_identity_contract import load_book_identity_contract

        _identity_contract = load_book_identity_contract(topic)
    except ImportError:
        _identity_contract = None
    _scene_ladder_done: set[int] = set()
    _chapter_story_depths_raw = list(_spine.get("chapter_story_depths") or [])
    _planner_warnings_mut: List[str] = list(_spine.get("chapter_planner_warnings") or [])

    # Story schedule + BookSlotTracker: unconditional as of PR #612.
    _story_schedule: StorySchedule = build_story_schedule(
        persona_id=persona_id,
        topic=topic,
        seed=seed,
        repo_root=root,
        runtime_format=rf_bm,
        planner_warnings=_planner_warnings_mut,
        continuity_plan=plan_context.get("chapter_continuity_plan")
        if is_twelve_shape_continuity_active(plan_context)
        else None,
    )

    # Section packet audit: per-slot source detail (written to enrichment_audit at end).
    _slot_audit: List[Dict[str, Any]] = []

    for bm_ch in bm.chapters:
        ch_key = _chapter_key(bm_ch.number)
        ch_data = sections_root.get(ch_key)
        if not isinstance(ch_data, dict):
            ch_data = {}
        reg_lists = _registry_type_lists(ch_data, persona_id=pid)
        reg_counters: Dict[str, int] = defaultdict(int)

        chapter_index0 = bm_ch.number - 1
        slots_out: List[EnrichedSlot] = []
        ch_breakdown: Dict[str, int] = defaultdict(int)
        ch_words = 0
        _chapter_composite_doctrine = False

        for slot_i, slot in enumerate(bm_ch.slots):
            audit_counts["total_slots"] += 1
            total_target_words += slot.target_words
            stype = slot.slot_type.strip().upper()
            seed_key = f"{seed}:topic:{topic}:ch{bm_ch.number}:slot:{slot_i}:{stype}"
            slot_spec = _slot_spec_for(plan_context, bm_ch.number, slot_i)
            ch_tgt = (
                _sel_targets[chapter_index0] if chapter_index0 < len(_sel_targets) else {}
            )

            content: str = ""
            source: str = ""
            source_id: str = ""
            variant_id = ""
            atom_id = ""
            teacher_content_val: str = ""
            match_scores: Dict[str, Any] = {}
            hooks_fired: List[str] = []
            reg_sec_meta: Optional[Tuple[Dict[str, Any], int]] = None
            persona_expand_pool: Optional[List[dict]] = None
            persona_primary_idx: Optional[int] = None
            teacher_expand_pool: Optional[List[dict]] = None
            teacher_primary_idx: Optional[int] = None

            if not content and stype == "ANGLE_DEFINITION":
                _angle_for_slot = _angle_id_enrich
                if is_twelve_shape_continuity_active(plan_context):
                    _cont_angle = chapter_context_from_spine(plan_context, chapter_index0)
                    if _cont_angle and _cont_angle.angle_id:
                        _angle_for_slot = _cont_angle.angle_id
                if _angle_for_slot:
                    _ad = _try_angle_definition(
                        persona_id=pid,
                        topic_id=topic,
                        angle_id=_angle_for_slot,
                        repo_root=root,
                        fallback_warnings=_angle_fallback_warnings,
                    )
                else:
                    _ad = None
                if _ad:
                    content, source, source_id = _ad[0], _ad[1], _ad[2]
                    atom_id = source_id
            elif not content and _angle_id_enrich and stype == "ANGLE_CALLBACK":
                _layer = _angle_layer_by_ch.get(bm_ch.number)
                if _layer:
                    _ac = _try_angle_callback(
                        persona_id=pid,
                        topic_id=topic,
                        angle_id=_angle_id_enrich,
                        layer=int(_layer),
                        repo_root=root,
                        fallback_warnings=_angle_fallback_warnings,
                    )
                    if _ac:
                        content, source, source_id = _ac[0], _ac[1], _ac[2]
                        atom_id = source_id
                        match_scores["angle_layer"] = int(_layer)
                    elif is_twelve_shape_continuity_active(plan_context):
                        content = f"[BANK EMPTY: ANGLE_CALLBACK ch{bm_ch.number}]"
                        source = "continuity_bank_empty"
                        source_id = "EMPTY"
                        atom_id = "EMPTY"

            # 0) Story schedule: named-character arcs replace SCENE/STORY slots at section indices 2/5/9.
            # section_index is 1-based. StorySchedule keys: (chapter_number, section_index).
            # STORY check added 2026-04-26 alongside SOMATIC_10_SLOT_GRID sec 2/5/9 SCENE→STORY change:
            # preserves story_schedule routing for personas with story_atoms/anchored coverage (gen_z_professionals × anxiety today);
            # personas without coverage fall through to persona_atoms["STORY"] waterfall (engine bank + generic 859-bank merged).
            #
            # OPD-142 fix (2026-05-21): PR #1248 (OPD-116/117 angle journey) inserted ANGLE_DEFINITION /
            # ANGLE_CALLBACK slots into the slot list, breaking the `slot_i + 1 == somatic_section_index`
            # invariant that PR #669's routing depended on. We now key off the slot's preserved
            # somatic_section_index (patch_beatmap_angle_journey preserves it; see beatmap_compile.py:209-212).
            # Fall back to slot_i + 1 only when somatic_section_index is not set (short formats / non-v2).
            _sec_idx = getattr(slot, "somatic_section_index", 0) or (slot_i + 1)
            _twelve_shape_active = is_twelve_shape_continuity_active(plan_context)
            _story_routable = stype == "STORY" or (
                stype == "SCENE" and not _twelve_shape_active
            )
            if _story_routable and _sec_idx in SCENE_SECTION_INDICES:
                _sched_slot = _story_schedule.get(bm_ch.number, _sec_idx)
                if _sched_slot is not None and _sched_slot.text:
                    content = _sched_slot.text
                    source = "story_plan"
                    source_id = _sched_slot.source
                    atom_id = _sched_slot.source
                    audit_counts["slots_from_persona"] += 1  # story atoms count as persona-class
                    # ws_enrichment_primary_dedup_20260616: register the story-plan
                    # SCENE/STORY body so the persona waterfall below won't re-pick a
                    # near-duplicate primary in a later chapter.
                    _note_primary_body(_book_seen_bodies, content)

            # --- PR #612 + OPD-107: additive is the ONLY mode. Two code paths:
            #   EXERCISE slots: teacher → persona (practice-shaped only) → practice_library → FAIL
            #     PR #612 originally locked EXERCISE to teacher → practice_library because
            #     persona atoms and registry templates were "short reflections" that shipped
            #     bad books when rendered as EXERCISE content. OPD-107 (2026-05-18) re-opens
            #     persona consultation but ONLY through the same _filter_practice_pool gate
            #     the teacher pool uses — so the original guarantee (no essay-shaped atom
            #     can enter an EXERCISE slot) holds. Registry templates remain excluded.
            #   All other slots: persona + registry + teacher stacked
            if not content:
                _add_pieces: List[str] = []
                _add_sources: List[str] = []
                _add_ids: List[str] = []

                if stype == "EXERCISE":
                    _cont_ex_ctx = (
                        chapter_context_from_spine(plan_context, chapter_index0)
                        if is_twelve_shape_continuity_active(plan_context)
                        else None
                    )
                    if _cont_ex_ctx and _cont_ex_ctx.exercise_id:
                        _pl_by_id = _try_practice_library_by_id(
                            _cont_ex_ctx.exercise_id,
                            chapter_index0,
                            seed,
                            content_only=(chapter_index0 == 0),
                        )
                        if _pl_by_id:
                            _add_pieces.append(_pl_by_id[0])
                            _add_sources.append("practice_library")
                            _add_ids.append(_pl_by_id[1])
                            audit_counts["slots_from_practice_library"] += 1
                            audit_counts["slots_from_twelve_shape_plan_exercise"] += 1
                    # EXERCISE-slot rule (PR #612): teacher exercise wins; else practice_library;
                    # else fall through to hard-fail gap raise below.
                    #
                    # EXERCISE-slot contract (post-PR #612 follow-up): teacher_atoms[EXERCISE]
                    # is loaded by directory name, but some atoms in approved_atoms/EXERCISE/
                    # are kb_mine_v1 essay synthesis (teaching prose about Bhakti Yoga,
                    # selfless giving, transcendence) — not instruction-with-steps. Refuse
                    # essay-shaped atoms here; fall through to practice_library which
                    # produces actual practice content. See _is_practice_atom() above.
                    _at_hit_ex = None
                    if _add_pieces:
                        pass
                    elif tid and teacher_atoms:
                        _at_for_slot_ex = {
                            _k: [
                                _a for _a in _pool
                                if not _is_doctrine_quarantined(str(_a.get("content") or ""), _frame)
                            ]
                            for _k, _pool in teacher_atoms.items()
                        }
                        # Hard contract: EXERCISE pool must contain only practice-shaped atoms.
                        _at_for_slot_ex["EXERCISE"] = _filter_practice_pool(
                            _at_for_slot_ex.get("EXERCISE") or []
                        )
                        _at_hit_ex = _try_teacher_content(
                            _at_for_slot_ex,
                            stype,
                            seed_key,
                            topic_id=topic,
                            persona_id=persona_id,
                            book_frame=_frame,
                        )
                    if _at_hit_ex:
                        from phoenix_v4.rendering.teacher_wrapper import apply_wrapper as _aw
                        _at_content_ex = _aw(
                            _at_hit_ex[0], teacher_id=tid, section_type=stype,
                            seed=seed_key, spine_context=plan_context,
                        )
                        _add_pieces.append(_at_content_ex)
                        _add_sources.append("teacher_atom")
                        _add_ids.append(_at_hit_ex[1])
                        teacher_content_val = _at_content_ex
                        audit_counts["slots_from_teacher"] += 1
                    elif not _add_pieces and persona_atoms:
                        # OPD-107 (2026-05-18): consult persona EXERCISE pool through the
                        # SAME shape gate before falling through to practice_library.
                        # Pre-fix, the EXERCISE branch hard-coded teacher → practice_library;
                        # 30 practice-shaped persona atoms in
                        # atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt were invisible to
                        # primary fill even though 29/30 pass _filter_practice_pool cleanly.
                        # PR #612's original guarantee is preserved: only practice-shaped
                        # atoms (passing the same _is_practice_atom filter the teacher pool
                        # uses) can enter the EXERCISE slot. Essay-shaped persona atoms
                        # still get rejected and fall through to practice_library exactly
                        # as before. See docs/diagnostics/OPD-107_PRACTICE_SHAPE_FILTER_2026-05-18.md
                        _persona_ex_pool = _filter_practice_pool(
                            persona_atoms.get("EXERCISE") or []
                        )
                        _persona_ex_pool = [
                            _a for _a in _persona_ex_pool
                            if not _is_doctrine_quarantined(str(_a.get("content") or ""), _frame)
                            and atom_passes_book_governance(
                                _a.get("metadata"),
                                topic_id=topic,
                                persona_id=persona_id,
                                book_frame=_frame,
                            )
                        ]
                        if _persona_ex_pool:
                            # OPD-109 Phase 3: rotation-aware least-used pick for
                            # EXERCISE persona atoms too. Without this, the same
                            # 1-3 practice atoms win every EXERCISE slot when
                            # the teacher pool misses; rotation spreads picks
                            # across the 16-30 atom pool typical for gen_z
                            # professionals/anxiety EXERCISE.
                            # ws_enrichment_primary_dedup_20260616: dedup-aware
                            # primary pick — skip EXERCISE bodies already stamped
                            # book-wide (short/practice bodies are exempt via the
                            # _SeenBodies min_words floor; full pick is preserved
                            # when no unused body exists).
                            _ap_idx = _pick_primary_index_unseen(
                                _persona_rotation, _persona_ex_pool,
                                f"{seed_key}:persona_ex", "persona_ex",
                                _book_seen_bodies,
                            )
                            _ap_atom = _persona_ex_pool[_ap_idx]
                            _ap_content = str(_ap_atom.get("content") or "").strip()
                            if _ap_content:
                                _add_pieces.append(_ap_content)
                                _add_sources.append("persona_atom")
                                _ap_aid = str(_ap_atom.get("atom_id") or f"persona_ex_{_ap_idx}")
                                _add_ids.append(_ap_aid)
                                audit_counts["slots_from_persona"] += 1
                                _persona_rotation.register(_ap_aid)
                                _note_primary_body(_book_seen_bodies, _ap_content)
                    if not _add_pieces:
                        # Final EXERCISE fallback: practice_library (unchanged path).
                        _apl = _try_practice_library(chapter_index0, topic, persona_id, seed)
                        if _apl:
                            _add_pieces.append(_apl[0])
                            _add_sources.append("practice_library")
                            _add_ids.append("practice_library")
                            audit_counts["slots_from_practice_library"] += 1
                else:
                    # Non-EXERCISE: stack persona + registry + teacher
                    _composite_filled = False
                    # 0) composite doctrine/reflection (regular mode; OPD-115 Phase B)
                    if not tid and composite_atoms and stype in _COMPOSITE_SLOT_TYPES:
                        _cx_hit = _try_composite_content(
                            composite_atoms,
                            stype,
                            seed_key,
                            topic_id=topic,
                            persona_id=persona_id,
                            book_frame=_frame,
                            seen_bodies=_book_seen_bodies,
                            chapter_index0=chapter_index0,
                            spine_context=plan_context,
                            used_doctrine_ids=_book_used_doctrine_ids,
                            # Ordered prior-chapter doctrines (oldest→newest) for the
                            # bounded-reuse spacing window; excludes this chapter.
                            recent_doctrine_ids=[
                                _book_doctrine_by_chapter[_c]
                                for _c in sorted(_book_doctrine_by_chapter)
                                if _c < chapter_index0
                            ],
                            chapter_count=_book_chapter_count,
                            repo_root=root,
                        )
                        if _cx_hit:
                            # Composite brands have no named teacher, so the doctrine body
                            # must carry GENERALIZED-mode attribution ("The contemplative
                            # tradition teaches...") rather than ship un-wrapped. We route
                            # through apply_wrapper with a non-null sentinel teacher_id that
                            # has no teacher_registry entry: resolve_wrapper then finds no
                            # TEACHER_NAME slot and selects generalized mode (teacher_wrapper
                            # .py:216-219), filling {TRADITION} from spine_context or the
                            # template slot_defaults. Teacher brands never reach this block
                            # (it is gated `if not tid`), so named framing is unaffected.
                            #
                            # Twelve-shape flagship: plan-bound doctrine atoms are complete
                            # beats — skip generalized wrapper glue (v03_pure doctrine).
                            _cx_body = _cx_hit[0]
                            if not (
                                is_twelve_shape_continuity_active(plan_context)
                                and stype in _COMPOSITE_REFLECTION_SLOT_TYPES
                            ):
                                from phoenix_v4.rendering.teacher_wrapper import (
                                    apply_wrapper as _aw_composite,
                                )
                                _cx_body = _aw_composite(
                                    _cx_hit[0],
                                    teacher_id=_GENERALIZED_WRAPPER_SENTINEL,
                                    section_type=stype,
                                    seed=f"{seed_key}:composite",
                                    spine_context=plan_context,
                                )
                            _add_pieces.append(_cx_body)
                            _add_sources.append("composite_doctrine")
                            _add_ids.append(_cx_hit[1])
                            # Dedup keys on the RAW doctrine body (not the rotating wrapper
                            # stem) so two sections sharing the same doctrine are still caught.
                            _note_primary_body(_book_seen_bodies, _cx_hit[0])
                            _composite_filled = True
                            _chapter_composite_doctrine = True
                            if is_reflection_rotation_slot(stype):
                                _picked_norm = normalize_doctrine_id(_cx_hit[1])
                                _book_used_doctrine_ids.add(_picked_norm)
                                # Record THIS chapter's doctrine once (idempotent across
                                # its multi-REFLECTION slots) so later chapters see an
                                # ordered recency history for the spacing window.
                                _book_doctrine_by_chapter[chapter_index0] = _picked_norm
                            audit_counts["slots_from_composite"] = (
                                audit_counts.get("slots_from_composite", 0) + 1
                            )

                    # 1) persona (skipped when composite pool supplied content)
                    _ap_pool = [
                        _a for _a in (persona_atoms.get(stype) or [])
                        if not _is_doctrine_quarantined(str(_a.get("content") or ""), _frame)
                        and atom_passes_book_governance(
                            _a.get("metadata"),
                            topic_id=topic,
                            persona_id=persona_id,
                            book_frame=_frame,
                        )
                    ]
                    if is_twelve_shape_continuity_active(plan_context):
                        _twelve_ctx = chapter_context_from_spine(plan_context, chapter_index0)
                        if _twelve_ctx and _twelve_ctx.character:
                            _ap_pool = filter_persona_pool_one_character(
                                _ap_pool, _twelve_ctx.character, forbidden=_twelve_ctx.forbidden_names
                            )
                    _continuity_gap_filled = False
                    if (
                        is_twelve_shape_continuity_active(plan_context)
                        and stype in CONTINUITY_CONNECTIVE_SLOTS
                    ):
                        _cont_ctx = chapter_context_from_spine(plan_context, chapter_index0)
                        if _cont_ctx:
                            _plan_entry = next(
                                (
                                    c
                                    for c in (plan_context.get("chapter_continuity_plan") or [])
                                    if int(c.get("chapter") or 0) == bm_ch.number
                                ),
                                None,
                            )
                            _connective_picks = (
                                (_plan_entry or {}).get("connective_picks") or {}
                            )
                            _forced_id = str(_connective_picks.get(stype) or "").strip()
                            if _forced_id:
                                _forced = _pick_persona_atom_by_id(_ap_pool, _forced_id)
                                if _forced and str(_forced.get("content") or "").strip():
                                    content = str(_forced.get("content") or "").strip()
                                    source = "persona_atom"
                                    source_id = _forced_id
                                    atom_id = _forced_id
                                    audit_counts["slots_from_persona"] += 1
                                    _continuity_gap_filled = True
                            if not _continuity_gap_filled:
                                _ap_pool = filter_connective_pool(_ap_pool, stype, _cont_ctx)
                                if not _ap_pool:
                                    logger.warning(
                                        "12-shape continuity BANK EMPTY: %s ch%s object=%s character=%s",
                                        stype,
                                        bm_ch.number,
                                        _cont_ctx.anxiety_object,
                                        _cont_ctx.character,
                                    )
                                    content = continuity_bank_empty(stype, _cont_ctx)
                                    source = "continuity_bank_empty"
                                    source_id = "EMPTY"
                                    atom_id = "EMPTY"
                                    _continuity_gap_filled = True
                    if _ap_pool and not _composite_filled and not _continuity_gap_filled:
                        if (
                            stype == "SCENE"
                            and chapter_index0 not in _scene_ladder_done
                        ):
                            from phoenix_v4.planning.chapter_planner import story_depth_for_runtime

                            if chapter_index0 < len(_chapter_story_depths_raw):
                                _story_d = int(str(_chapter_story_depths_raw[chapter_index0]))
                            else:
                                _story_d = story_depth_for_runtime(rf_bm)
                            _ladder = pick_scene_ladder(
                                bm_ch.number,
                                _ap_pool,
                                _story_d,
                                _scene_arch_rotation,
                                seed=seed,
                                planner_warnings=_planner_warnings_mut,
                            )
                            _scene_ladder_done.add(chapter_index0)
                            if _ladder:
                                _ladder_body = "\n\n".join(
                                    a.content for a in _ladder if a.content
                                )
                                _add_pieces.append(_ladder_body)
                                _add_sources.append("persona_atom")
                                _ladder_ids = [a.atom_id for a in _ladder if a.atom_id]
                                _add_ids.append("+".join(_ladder_ids) or "scene_ladder")
                                match_scores["scene_ladder"] = [
                                    {"archetype": a.archetype, "depth_level": a.depth_level}
                                    for a in _ladder
                                ]
                                audit_counts["slots_from_persona"] += 1
                                for a in _ladder:
                                    if a.atom_id:
                                        _persona_rotation.register(a.atom_id)
                                # ws_enrichment_primary_dedup_20260616: note the
                                # whole SCENE-ladder body so a later chapter's SCENE
                                # primary won't re-pick a near-duplicate.
                                _note_primary_body(_book_seen_bodies, _ladder_body)
                        else:
                            # OPD-109 Phase 3: rotation-aware least-used pick. Falls
                            # back to hash-anchor (`_deterministic_index`) for the
                            # tiebreak so seed-determinism is preserved.
                            # ws_enrichment_primary_dedup_20260616: dedup-aware
                            # primary pick for HOOK/SCENE/STORY — within the same
                            # least-used order, skip a body already stamped book-wide
                            # so the identical primary isn't re-injected across
                            # chapters/clusters (the deep-tier F1 ~93 driver). The
                            # least-used anchor is preserved when no unused body
                            # exists, keeping determinism + the never-empty contract.
                            if stype == "HOOK":
                                _ap_idx = _pick_hook_index_unique(
                                    _persona_rotation, _ap_pool,
                                    f"{seed_key}:persona", "persona",
                                    _book_seen_bodies,
                                    _book_used_hooks,
                                    contract=_identity_contract,
                                    engine=engine,
                                )
                            else:
                                _ap_idx = _pick_primary_index_unseen(
                                    _persona_rotation, _ap_pool,
                                    f"{seed_key}:persona", "persona",
                                    _book_seen_bodies,
                                )
                            _ap_atom = _ap_pool[_ap_idx]
                            _ap_content = str(_ap_atom.get("content") or "").strip()
                            if _ap_content:
                                _add_pieces.append(_ap_content)
                                _add_sources.append("persona_atom")
                                _ap_aid = str(_ap_atom.get("atom_id") or f"persona_{_ap_idx}")
                                _add_ids.append(_ap_aid)
                                audit_counts["slots_from_persona"] += 1
                                persona_expand_pool = _ap_pool
                                persona_primary_idx = _ap_idx
                                _persona_rotation.register(_ap_aid)
                                _note_primary_body(_book_seen_bodies, _ap_content)
                                if stype == "HOOK":
                                    _book_used_hooks.add(_norm_ws(_ap_content))

                    # 2) registry (baseline) — skip when slot already has primary content
                    _skip_registry_stack = (
                        (stype in _REGISTRY_SINGLE_OCCUPANT_SLOTS and bool(_add_pieces))
                        or _composite_filled
                        or (stype == "REFLECTION" and _chapter_composite_doctrine)
                        or (
                            is_twelve_shape_continuity_active(plan_context)
                            and stype in CONTINUITY_CONNECTIVE_SLOTS
                            and bool(_add_pieces)
                        )
                    )
                    if not _skip_registry_stack and not _continuity_gap_filled:
                        _ar_hit = _try_registry_variant(reg_lists, stype, reg_counters, seed_key)
                        if _ar_hit and not _is_doctrine_quarantined(_ar_hit[0], _frame):
                            _add_pieces.append(_ar_hit[0])
                            _add_sources.append("registry")
                            _add_ids.append(_ar_hit[1])
                            reg_sec_meta = (_ar_hit[2], _ar_hit[3])
                            variant_id = _ar_hit[1]
                            audit_counts["slots_from_registry"] += 1
                            _book_tracker.record(_ar_hit[1], slot_type=stype)

                    # 3) teacher (respects _TEACHER_OVERLAY_TYPES)
                    if tid and teacher_atoms:
                        _at_for_slot = {
                            _k: [
                                _a for _a in _pool
                                if not _is_doctrine_quarantined(str(_a.get("content") or ""), _frame)
                            ]
                            for _k, _pool in teacher_atoms.items()
                        }
                        _at_hit = _try_teacher_content(
                            _at_for_slot,
                            stype,
                            seed_key,
                            topic_id=topic,
                            persona_id=persona_id,
                            book_frame=_frame,
                        )
                        if _at_hit:
                            from phoenix_v4.rendering.teacher_wrapper import apply_wrapper as _aw
                            _at_raw = _at_hit[0]
                            _at_content = _aw(
                                _at_raw, teacher_id=tid, section_type=stype,
                                seed=seed_key, spine_context=plan_context,
                            )
                            _add_pieces.append(_at_content)
                            _add_sources.append("teacher_atom")
                            _add_ids.append(_at_hit[1])
                            teacher_content_val = _at_content
                            audit_counts["slots_from_teacher"] += 1

                if _add_pieces and not (content and _continuity_gap_filled):
                    content = "\n\n".join(_add_pieces)
                    source = "+".join(_add_sources)
                    source_id = "+".join(_add_ids)
                    atom_id = variant_id or (_add_ids[0] if _add_ids else "")

            # PR #612: hard-fail on missing content. No waterfall fallbacks.
            # No content_bank fallback. No [CONTENT GAP: ...] string placeholder.
            # If the additive block above produced nothing, the book can't ship.
            if not content:
                audit_counts["slots_empty"] += 1
                gap_details.append(
                    {"chapter": bm_ch.number, "slot_index": slot_i, "slot_type": stype}
                )
                if (
                    is_twelve_shape_continuity_active(plan_context)
                    and stype in CONTINUITY_CONNECTIVE_SLOTS
                ):
                    _cont_ctx_gap = chapter_context_from_spine(plan_context, chapter_index0)
                    if _cont_ctx_gap:
                        content = continuity_bank_empty(stype, _cont_ctx_gap)
                        source = "continuity_bank_empty"
                        source_id = "EMPTY"
                        atom_id = "EMPTY"
                        logger.warning(
                            "12-shape continuity fail-closed: %s ch%s",
                            stype,
                            bm_ch.number,
                        )
                if not content:
                    raise EnrichmentGapError(
                    f"No enrichable content for slot {stype} "
                    f"(topic={topic} chapter={bm_ch.number} slot_index={slot_i}). "
                    f"Sources tried: persona={bool(persona_atoms.get(stype) if persona_atoms else False)}, "
                    f"registry={bool(reg_lists.get(stype))}, "
                    f"teacher={bool(tid and teacher_atoms)}"
                    + (f", practice_library (EXERCISE slot)" if stype == 'EXERCISE' else "")
                    + ". Add atoms upstream."
                )

            # Record registry/story picks in BookSlotTracker (unconditional as of PR #612).
            if True:
                if variant_id:
                    _book_tracker.record(variant_id, slot_type=stype)
                if source == "story_plan":
                    _book_tracker.record(source_id, slot_type=stype)

            # Resolve injection markers and locale/mechanism tokens if present.
            _INJECTION_MARKS = (
                "[STORY_INJECTION_POINT]",
                "[EXERCISE_INJECTION_POINT]",
                "[SCENE_INJECTION_POINT]",
                "[INTEGRATION_SCENE_POINT]",
            )
            if content and not content.startswith("[CONTENT GAP:") and (
                any(m in content for m in _INJECTION_MARKS) or "{" in content
            ):
                try:
                    _ri_result = resolve_injections(
                        content,
                        chapter_index=bm_ch.number,
                        section_index=_sec_idx,
                        section_type=stype,
                        topic=topic,
                        persona_id=persona_id,
                        teacher_id=tid,
                        exercise_phase=None,
                        seed=seed_key,
                        repo_root=root,
                        story_schedule=_story_schedule,
                        slot_tracker=_book_tracker,
                    )
                    content = _ri_result["text"]
                    if _ri_result.get("injections_resolved"):
                        source_id = source_id + ":resolved"
                except Exception as _ri_err:
                    logger.warning("resolve_injections ch%d slot%d: %s", bm_ch.number, slot_i, _ri_err)

            # Section packet audit: record per-slot source provenance.
            _slot_audit.append({
                "chapter": bm_ch.number,
                "slot_index": slot_i,
                "slot_type": stype,
                "source": source,
                "source_id": source_id,
                "variant_id": variant_id,
                "words": len(content.split()),
            })

            if content and not content.startswith("[CONTENT GAP:"):
                book_words_prior = (
                    sum(c.total_words for c in enriched_chapters) + ch_words
                )
                tw_tgt = slot.target_words
                max_x = _max_extra_chunks_for_format(bm.runtime_format, tw_tgt)
                base_wc = _wc(content)
                if format_wmax is not None:
                    room_book = max(0, format_wmax - book_words_prior)
                    if base_wc > room_book:
                        content = _truncate_to_word_budget(content, room_book)
                        base_wc = _wc(content)
                shortfall = max(0, tw_tgt - base_wc)
                extra_bodies: List[str] = []
                if max_x > 0 and shortfall >= 100:
                    goal = min(shortfall, tw_tgt)
                    if format_wmax is not None:
                        room_after_base = max(0, format_wmax - book_words_prior - base_wc)
                        goal = min(goal, room_after_base)
                    if goal < 100:
                        goal = 0
                    # OPD-109 Phase 3: source is now a "+"-joined string when
                    # multiple sources stack (e.g. "persona_atom+registry+teacher_atom").
                    # Use substring detection so expansion fires regardless of stack
                    # order. Priority: persona pool first (16-57 atoms typical for
                    # gen_z_professionals/anxiety), then registry, then teacher.
                    _src_parts = source.split("+") if source else []
                    _has_persona = "persona_atom" in _src_parts
                    _has_registry = "registry" in _src_parts
                    _has_teacher = "teacher_atom" in _src_parts
                    if (
                        goal >= 100
                        and _has_persona
                        and persona_expand_pool
                        and persona_primary_idx is not None
                        and len(persona_expand_pool) > 1
                    ):
                        extra_bodies = _expand_atom_pool_blocks(
                            persona_expand_pool,
                            persona_primary_idx,
                            seed_key,
                            "persona_x",
                            goal,
                            max_x,
                            rotation_state=_persona_rotation,
                        )
                    elif _has_registry and reg_sec_meta is not None and goal >= 100:
                        sd, vi = reg_sec_meta
                        extra_bodies = _extra_registry_variant_bodies(
                            sd, vi, seed_key, goal, max_x
                        )
                    elif (
                        goal >= 100
                        and _has_teacher
                        and teacher_expand_pool
                        and teacher_primary_idx is not None
                        and len(teacher_expand_pool) > 1
                    ):
                        extra_bodies = _expand_atom_pool_blocks(
                            teacher_expand_pool,
                            teacher_primary_idx,
                            seed_key,
                            "teacher_x",
                            goal,
                            max_x,
                        )
                if extra_bodies:
                    content = "\n\n".join([content] + extra_bodies)
                    nx = len(extra_bodies)
                    audit_counts["slots_format_scaled"] += 1
                    # OPD-109 Phase 3: when expansion comes from the registry
                    # path we annotate as "+vN" (registry variant), else "+stackN"
                    # (atom-pool stack). The detection is now substring-based so
                    # stacked-source `source` like "persona_atom+registry+teacher_atom"
                    # still records the correct annotation.
                    _src_parts_post = source.split("+") if source else []
                    _used_registry_path = (
                        "registry" in _src_parts_post
                        and "persona_atom" not in _src_parts_post
                        and reg_sec_meta is not None
                    )
                    if _used_registry_path:
                        source_id = f"{source_id}+v{nx}"
                    else:
                        source_id = f"{source_id}+stack{nx}"

                if format_wmax is not None:
                    room_slot = max(0, format_wmax - book_words_prior)
                    if _wc(content) > room_slot:
                        content = _truncate_to_word_budget(content, room_slot)

            actual_w = len(content.split())
            ch_words += actual_w
            ch_breakdown[source] += 1

            if content and not content.startswith("[CONTENT GAP:") and slot.enrichment_hooks:
                hooks_fired = list(slot.enrichment_hooks)

            slots_out.append(
                EnrichedSlot(
                    slot_type=stype,
                    content=content,
                    source=source,
                    source_id=source_id,
                    target_words=slot.target_words,
                    actual_words=actual_w,
                    enrichment_applied=hooks_fired,
                    variant_id=variant_id,
                    atom_id=atom_id,
                    teacher_content=teacher_content_val,
                    match_scores=dict(match_scores),
                )
            )

        # ACT-007: record collision_families used in this chapter for dedup window
        _ch_fams: List[str] = []
        for _sl in slots_out:
            _cf_val = str(_sl.match_scores.get("_collision_family") or "").strip()
            if _cf_val:
                _ch_fams.append(_cf_val)
        _chapter_collision_families.append(_ch_fams)

        enriched_chapters.append(
            EnrichedChapter(
                number=bm_ch.number,
                role=bm_ch.role,
                working_title=bm_ch.working_title,
                thesis=bm_ch.thesis,
                slots=slots_out,
                total_words=ch_words,
                source_breakdown=dict(ch_breakdown),
                exercise_journey=None,
            )
        )

    total_words = sum(ch.total_words for ch in enriched_chapters)
    enrichment_audit: Dict[str, Any] = {
        **audit_counts,
        "total_words": total_words,
        "total_target_words": total_target_words,
        "gap_details": gap_details,
        "persona_id": persona_id,
        "teacher_id": tid or "",
        "section_packet_audit": _slot_audit,
        "book_slot_tracker_used_ids": list(_book_tracker._used_ids),
        # OQ-3 (PR-18 2026-04-27): top-level story_schedule key. Per-slot
        # source_id is already discoverable via section_packet_audit; this
        # makes the structural schedule directly queryable for downstream
        # auditors. Text intentionally omitted (already in slot.content).
        "story_schedule": [
            {
                "chapter_index": ch_i,
                "section_index": sec_i,
                "arc_position": slot.arc_position,
                "source": slot.source,
            }
            for (ch_i, sec_i), slot in sorted(_story_schedule.assignments.items())
        ],
        "angle_journey_fallback_warnings": _angle_fallback_warnings,
        "angle_id": _angle_id_enrich,
        "angle_layer_by_chapter": _angle_layer_by_ch,
    }

    _out_spine = dict(plan_context)
    if _planner_warnings_mut:
        _existing_warns = list(_out_spine.get("chapter_planner_warnings") or [])
        _out_spine["chapter_planner_warnings"] = _existing_warns + _planner_warnings_mut

    return EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic=topic,
        teacher_id=tid,
        persona_id=persona_id,
        runtime_format=bm.runtime_format,
        chapters=enriched_chapters,
        total_words=total_words,
        enrichment_audit=enrichment_audit,
        spine_context=_out_spine,
        locale=locale,
    )


def enriched_book_to_jsonable(book: EnrichedBook) -> Dict[str, Any]:
    return {
        "schema_version": book.schema_version,
        "stage": book.stage,
        "topic": book.topic,
        "teacher_id": book.teacher_id,
        "persona_id": book.persona_id,
        "runtime_format": book.runtime_format,
        "total_words": book.total_words,
        "enrichment_audit": book.enrichment_audit,
        "spine_context": dict(book.spine_context or {}),
        "chapters": [
            {
                "number": ch.number,
                "role": ch.role,
                "working_title": ch.working_title,
                "thesis": ch.thesis,
                "total_words": ch.total_words,
                "source_breakdown": ch.source_breakdown,
                "slots": [asdict(s) for s in ch.slots],
                "exercise_journey": ch.exercise_journey,
            }
            for ch in book.chapters
        ],
    }


def dump_enriched_book_json(book: EnrichedBook, indent: int = 2) -> str:
    return json.dumps(enriched_book_to_jsonable(book), indent=indent, ensure_ascii=False)


def selected_content_variants_artifact(book: EnrichedBook) -> Dict[str, Any]:
    """Render artifact: variant_id / atom_id / match_scores per enriched slot."""
    return {
        "schema_version": 1,
        "stage": "selected_content_variants",
        "topic": book.topic,
        "persona_id": book.persona_id,
        "teacher_id": book.teacher_id or "",
        "runtime_format": book.runtime_format,
        "chapters": [
            {
                "number": ch.number,
                "slots": [
                    {
                        "slot_type": s.slot_type,
                        "variant_id": s.variant_id,
                        "atom_id": s.atom_id,
                        "source": s.source,
                        "source_id": s.source_id,
                        "target_words": s.target_words,
                        "actual_words": s.actual_words,
                        "enrichment_applied": list(s.enrichment_applied or []),
                        "exercise_phase": s.exercise_phase,
                        "journey_exercise_id": s.journey_exercise_id,
                        "match_scores": dict(s.match_scores or {}),
                    }
                    for s in ch.slots
                ],
            }
            for ch in book.chapters
        ],
    }


def write_selected_content_variants_json(book: EnrichedBook, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(selected_content_variants_artifact(book), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def budget_from_enriched(book: EnrichedBook) -> Dict[str, Any]:
    return {
        "total_words": book.total_words,
        "chapter_count": len(book.chapters),
        "chapters": [
            {
                "chapter": ch.number,
                "working_title": ch.working_title,
                "words": ch.total_words,
                "slots": [
                    {
                        "type": s.slot_type,
                        "target_words": s.target_words,
                        "actual_words": s.actual_words,
                        "source": s.source,
                    }
                    for s in ch.slots
                ],
            }
            for ch in book.chapters
        ],
    }


DEFAULT_DEPTH_PRIORITY: List[str] = [
    "recognition_depth",
    "mechanism_depth",
    "story_scene",
    "consequence_exposure",
    "somatic_detail",
    "practice_scaffold",
    "bridge_transition",
    "integration_landing",
]

# Per-chapter depth budget reservation constants
MIN_DEPTH_WORDS_PER_CHAPTER = 180
TARGET_DEPTH_WORDS_PER_CHAPTER = 300
MAX_DEPTH_WORDS_PER_CHAPTER = 600


def _chapter_phase(chapter_number: int, chapter_count: int) -> str:
    """early / mid / late per docs/DEPTH_MODULE_PROTOCOL.md."""
    if chapter_count <= 0:
        return "late"
    early_end = (chapter_count + 2) // 3  # ceil(n/3)
    mid_end = (2 * chapter_count) // 3  # floor(2n/3)
    if chapter_number <= early_end:
        return "early"
    if chapter_number <= mid_end:
        return "mid"
    return "late"


def _module_banned(
    module_name: str,
    chapter_number: int,
    phase: str,
    topic_overrides: Dict[str, Any],
) -> bool:
    banned_early = topic_overrides.get("banned_early") or []
    if phase == "early" and module_name in banned_early:
        return True
    banned_chapters = topic_overrides.get("banned_chapters") or {}
    if isinstance(banned_chapters, dict):
        ch_list = banned_chapters.get(module_name) or []
        if chapter_number in ch_list:
            return True
    return False


def _chapter_affinity_ok(affinity: Any, chapter_number: int) -> bool:
    if affinity is None or affinity == "all":
        return True
    if isinstance(affinity, list):
        return chapter_number in affinity
    return False


def _truncate_to_word_budget(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip()


def _phoenix_standard_text_candidates(data: Dict[str, Any]) -> List[str]:
    """Collect prose-sized strings from phoenix standard YAML (flat or nested)."""
    out: List[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if str(k).startswith("#"):
                    continue
                walk(v)
        elif isinstance(node, str):
            t = node.strip()
            if t and len(t.split()) > 20:
                out.append(t)

    walk(data)
    return out


def _collect_bridge_template_strings(tpl_root: Any) -> List[str]:
    strings: List[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, str):
            t = node.strip()
            if t and len(t.split()) > 5:
                strings.append(t)

    walk(tpl_root)
    return strings


def _extract_prose_from_canonical(raw: str) -> str:
    """
    Extract only prose text from a CANONICAL.txt file.

    CANONICAL.txt uses atom blocks of the form::

        ## TYPE vNN
        ---
        metadata: value
        ---
        Prose text here.
        ---

    This function strips all ``## TYPE vNN`` headers and metadata blocks,
    returning only the concatenated prose bodies.  The raw text is safe to
    pass to ``_truncate_to_word_budget`` after this call.
    """
    # Split on atom header lines (## WORD vNN …)
    header_re = re.compile(r"^##\s+\S+\s+v\d+", re.MULTILINE)
    blocks = header_re.split(raw)
    prose_parts: List[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Each block: [metadata section between first and second ---] [prose]
        # Split on bare --- lines
        segments = re.split(r"(?m)^---\s*$", block)
        # segments[0]: empty or leftover header text
        # segments[1]: metadata key: value lines
        # segments[2]: prose text
        # segments[3+]: may contain sub-blocks (some files have multiple --- prose pairs)
        # Collect all segments that look like prose (not YAML key: value lines)
        for seg in segments[2:]:
            text = seg.strip()
            if not text:
                continue
            # Skip segments that are purely YAML metadata
            lines = text.splitlines()
            metadata_only = all(
                re.match(r"^[A-Z_]+\s*:", l.strip()) or not l.strip()
                for l in lines
            )
            if metadata_only:
                continue
            prose_parts.append(text)
    return "\n\n".join(prose_parts)


# ── Per-section ARC block parsing (patch (d) of dedupe-leak diagnosis) ───────
#
# CANONICAL.txt files in atoms/{persona}/{topic}/{engine}/ (and locale
# overlays under .../locales/{locale}/CANONICAL.txt) are structured as a
# sequence of ``## <ARC_POSITION> v<NN>`` blocks. Examples of ARC positions:
# RECOGNITION, MECHANISM_PROOF, TURNING_POINT, EMBODIMENT, COST_REVEAL,
# RECKONING (see atoms/corporate_managers/anxiety/spiral/CANONICAL.txt).
#
# Pre-patch (d), the persona_atom branch of ``_load_depth_content`` read each
# CANONICAL.txt with ``_extract_prose_from_canonical`` (which concatenates ALL
# atom prose bodies with ``\n\n``) and then called ``_select_prose_chunk_unique``
# to grab ~150 words starting from a deterministic paragraph index. When the
# starting paragraph and the next paragraph happened to be the long Tanya
# (RECOGNITION v05) and Sarah (MECHANISM_PROOF v02) blocks from the same file,
# both bodies were pasted together into the same DEPTH slot — and the same
# concatenation re-appeared in every chapter the depth pass touched, surfacing
# as the 9× "campaign that underperforms expectations" leak in Integration
# Smoke #2 (artifacts/qa/integration_smoke_v2_2026-05-16.md).
#
# Integration Smoke #2 confirmed that ``injection_resolver.py`` patches (b) and
# (c) (PRs #1137 / #1140) are DEAD CODE in spine mode: the spine pipeline
# routes STORY/SCENE-class content through this file's ``persona_atom`` /
# ``teacher_atom`` resolution, not through ``resolve_injections``'s
# ``[STORY_INJECTION_POINT]`` marker path. Patch (d) ports patch (b)'s
# per-section ARC-block selection logic into the spine-mode resolution path
# at the leak's source.
#
# The selection uses a hash-deterministic index over arc-block candidates
# keyed on (book_seed, engine, arc_position, chapter, section_index_proxy)
# so each (chapter, section) coordinate receives a distinct ARC block from
# the same CANONICAL.txt source.

_ARC_POSITIONS_PATCH_D = (
    "recognition", "mechanism_proof", "turning_point", "embodiment",
)
_CANONICAL_BLOCK_RE_PATCH_D = re.compile(
    r"^##\s+(?P<arc>RECOGNITION|MECHANISM_PROOF|TURNING_POINT|EMBODIMENT|COST_REVEAL|RECKONING)"
    r"\s+(?P<var>v\d+)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _split_canonical_into_atom_blocks(text: str) -> List[Dict[str, str]]:
    """Parse a CANONICAL.txt into discrete atom blocks.

    Each block's body is the prose between the second ``---`` separator and
    the next ``---`` (or the next ``## `` header / end of file).

    Returns a list of dicts ``{arc_position, variant, text}`` in source order.
    Returns ``[]`` if the file does not use the ``## ARC vNN`` block
    convention; the caller should fall back to whole-file behavior in that
    case (and is expected to log the degradation).

    Mirrors ``phoenix_v4.planning.injection_resolver._split_canonical_into_atom_blocks``
    (introduced in PR #1137). Kept as an inline copy in this module so patch (d)
    is independent of PR #1140's merge state — see commit message for details.
    """
    out: List[Dict[str, str]] = []
    if not text:
        return out
    matches = list(_CANONICAL_BLOCK_RE_PATCH_D.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[m.start():end]
        parts = chunk.split("---")
        # Header line is parts[0]; YAML-like metadata is parts[1]; prose body
        # is parts[2]. Some atoms in the wild only have one separator before
        # the body — fall through to the last part in that case.
        body = (parts[2] if len(parts) >= 3 else parts[-1]).strip()
        if not body:
            continue
        out.append({
            "arc_position": m.group("arc").lower(),
            "variant": m.group("var").lower(),
            "text": body,
        })
    return out


def _chapter_to_arc_position_patch_d(chapter_index: int) -> str:
    """Map 1-based chapter index to arc_position name using 3-chapter bands.

    Mirrors ``phoenix_v4.planning.injection_resolver._chapter_to_arc_position``.
    Inlined to keep patch (d) independent of injection_resolver imports.
    """
    phase = max(0, min((chapter_index - 1) // 3, len(_ARC_POSITIONS_PATCH_D) - 1))
    return _ARC_POSITIONS_PATCH_D[phase]


def _pick_canonical_block_per_section(
    raw_text: str,
    *,
    chapter_index: int,
    section_index: int,
    seed: str,
    slot_label: str,
    source_path: Path,
    reject: Optional[Any] = None,
) -> Optional[Dict[str, str]]:
    """Select a single ARC block from a CANONICAL.txt body per (chapter, section).

    Returns the picked block dict (``{arc_position, variant, text}``) or
    ``None`` when ``raw_text`` contains no usable blocks.

    Per-pick INFO telemetry is emitted as
    ``[enrichment_per_section] selected ARC v{N} for chapter {C} section {S}
    slot {slot_label}``. When the file is single-block we just paste it
    silently; when the file has 0 ARC blocks (plain-prose CANONICAL.txt) we
    emit a WARNING so the degraded fallback is visible.

    ``reject``: optional ``predicate(text) -> bool`` (ws_f1_depth_dedup). When
    supplied and the deterministically-picked block's body is rejected (already
    used book-wide / fuzzy-duplicate), the picker ROTATES deterministically
    through the remaining same-arc candidates to find an unused sibling block
    (multi-block files like HOOK carry dozens of blocks of headroom). If every
    same-arc candidate is rejected, returns the original deterministic pick so
    the slot is still filled (completeness over strict no-repeat) — the rare
    forced-repeat is then caught by the downstream renderer dedupe. ``reject`` is
    not applied to single-block files (no sibling to rotate to).
    """
    if not raw_text:
        return None
    blocks = _split_canonical_into_atom_blocks(raw_text)
    if not blocks:
        # Plain-prose CANONICAL.txt without the ## ARC vNN convention —
        # the caller should fall back to the legacy whole-file chunk path
        # (degraded) so we never go silent.
        logger.warning(
            "[enrichment_per_section] no ARC blocks parsed from %s; "
            "falling back to legacy prose-chunk path (degraded). "
            "Consider authoring story_atoms/ or restructuring this file "
            "with ## ARC_POSITION vNN headers.",
            source_path,
        )
        return None
    if len(blocks) == 1:
        # Single-block file: paste verbatim (no warning — this is fine).
        only = blocks[0]
        logger.info(
            "[enrichment_per_section] selected ARC %s %s for chapter %s "
            "section %s slot %s from %s (single-block file)",
            only["arc_position"], only["variant"],
            chapter_index, section_index, slot_label, source_path,
        )
        return only
    # Multi-block file: prefer blocks tagged with this chapter's arc_position;
    # widen to any block if no arc match exists.
    arc_pos = _chapter_to_arc_position_patch_d(chapter_index)
    candidates = [b for b in blocks if b["arc_position"] == arc_pos] or blocks
    book_seed = seed.split(":inject:")[0] if ":inject:" in seed else seed
    phase = max(0, min((chapter_index - 1) // 3, 3))
    pick_seed = (
        f"{book_seed}:enrichment_per_section:{source_path.parent.name}:"
        f"{arc_pos}:phase{phase}:{chapter_index}:{section_index}:{slot_label}"
    )
    start = _deterministic_index(pick_seed, len(candidates))
    pick = candidates[start]
    if callable(reject):
        # Rotate deterministically (wrap-around) past rejected siblings so the
        # same atom is not re-stamped across chapters; keep the first acceptable
        # block. Falls back to the original pick if all siblings are rejected.
        n = len(candidates)
        for i in range(n):
            cand = candidates[(start + i) % n]
            if not reject(cand["text"]):
                pick = cand
                break
    logger.info(
        "[enrichment_per_section] selected ARC %s %s for chapter %s "
        "section %s slot %s from %s",
        pick["arc_position"], pick["variant"],
        chapter_index, section_index, slot_label, source_path,
    )
    return pick


def _select_prose_chunk(content: str, seed: str, min_words: int = 21) -> Optional[str]:
    """
    Select a coherent prose chunk from extracted CANONICAL text.

    Splits on paragraph breaks so the returned text starts at a paragraph
    boundary (not mid-sentence).  Uses ``seed`` to pick a deterministic
    starting paragraph so different call-sites (chapters) get different
    passages from the same file.

    Returns None if no adequate prose is available.
    """
    if not content:
        return None
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", content) if p.strip()]
    # Keep only substantial paragraphs
    paras = [p for p in paragraphs if len(p.split()) >= min_words]
    if not paras:
        return None
    # Pick a starting paragraph deterministically
    start_idx = _deterministic_index(f"{seed}:pa_para", len(paras))
    # Collect from start_idx, wrapping around, until we have ≥ 150 words
    collected: List[str] = []
    target = 150
    for i in range(len(paras)):
        para = paras[(start_idx + i) % len(paras)]
        collected.append(para)
        if sum(len(p.split()) for p in collected) >= target:
            break
    return "\n\n".join(collected) if collected else None


def _select_prose_chunk_unique(
    content: str,
    seed: str,
    book_seen_bodies: Optional[set],
    min_words: int = 21,
) -> Optional[str]:
    """
    Like _select_prose_chunk but skips individual paragraphs already in book_seen_bodies.

    Each paragraph is checked individually against book_seen_bodies (not the whole chunk).
    This allows collecting ~150 words of prose from unique paragraphs even when the
    CANONICAL.txt shares some atoms with base enrichment.

    Returns None only if fewer than min_words of unique content can be collected.
    Falls back to _select_prose_chunk (no dedup filter) when book_seen_bodies is None.
    """
    if book_seen_bodies is None:
        return _select_prose_chunk(content, seed, min_words)
    if not content:
        return None
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", content) if p.strip()]
    paras = [p for p in paragraphs if len(p.split()) >= min_words]
    if not paras:
        return None
    start_idx = _deterministic_index(f"{seed}:pa_para", len(paras))
    collected: List[str] = []
    target = 150
    for i in range(len(paras)):
        para = paras[(start_idx + i) % len(paras)]
        # Skip paragraphs already used (base or prior depth) — exact match, plus
        # (ws_f1_depth_dedup) cross-chapter fuzzy near-duplicates when the
        # registry carries a fuzzy layer.
        if _norm_ws(para) in book_seen_bodies or _seen_similar(book_seen_bodies, para):
            continue
        collected.append(para)
        if sum(len(p.split()) for p in collected) >= target:
            break
    if not collected:
        return None
    # Only return if we have at least min_words of unique content
    total = sum(len(p.split()) for p in collected)
    if total < min_words:
        return None
    return "\n\n".join(collected)


def _load_depth_content(
    source: Dict[str, Any],
    topic: str,
    teacher_id: Optional[str],
    persona_id: str,
    chapter_number: int,
    seed: str,
    repo_root: Path,
    book_seen_bodies: Optional[set] = None,
    locale: Optional[str] = None,
    section_index: int = 0,
) -> Optional[str]:
    """
    Load actual content for a depth module from a specific source.
    Returns the prose text, or None if not available.

    book_seen_bodies: optional book-level set of _norm_ws(body) strings already used.
    When provided, any content whose normalized body is already in the set is skipped
    so the caller can fall through to the next source and avoid producing duplicate
    paragraphs that _dedup_repeated_blocks would strip later.

    section_index: positional index of this depth-slot within its chapter. Added
    by patch (d) of dedupe-leak diagnosis (2026-05-16) so the persona_atom
    branch can pick a distinct CANONICAL.txt ARC block per (chapter, section)
    via _pick_canonical_block_per_section. Defaults to 0 for legacy callers
    so existing tests stay green.
    """
    source_type = source.get("type")
    persona_id = (persona_id or "").strip()

    # ws_f1_depth_dedup: a body is "already used" if it is an EXACT prior body OR
    # (when book_seen_bodies carries a fuzzy layer) ≥ Jaccard-threshold similar to
    # one used earlier in the book. Mirrors the register-gate F1 detector so the
    # selector rotates off bodies that would otherwise form an F1 cluster.
    def _already_used(body: str) -> bool:
        if book_seen_bodies is None:
            return False
        return _norm_ws(body) in book_seen_bodies or _seen_similar(book_seen_bodies, body)

    if source_type == "teacher_atom":
        if not teacher_id:
            return None
        slot_types = source.get("slot_types", [])
        for slot_type in slot_types:
            atom_dir = (
                repo_root
                / "SOURCE_OF_TRUTH"
                / "teacher_banks"
                / teacher_id
                / "approved_atoms"
                / slot_type
            )
            if not atom_dir.exists():
                continue
            atoms = sorted(atom_dir.glob("*.yaml"))
            if not atoms:
                continue
            # Patch (d): include chapter_index and section_index in the seed so
            # that multiple depth_module:teacher_atom slots in the same chapter
            # pick distinct YAML atoms rather than the same idx. Teacher YAMLs
            # are atomic (one body per file), so no ARC-block parsing is
            # required here — but per-section variation in the index is still
            # the right behavior. INFO telemetry mirrors the persona_atom path
            # so audit is consistent.
            start = _deterministic_index(
                f"{seed}:teacher:{slot_type}:ch{chapter_number}:sec{section_index}",
                len(atoms),
            )
            # ws_f1_depth_dedup: rotate deterministically across this slot_type's
            # atom files so a teacher atom already used in an earlier chapter is
            # not re-stamped; keep the first unused body. Falls back to the
            # original pick if every atom here is used (caller then tries the
            # next slot_type / source).
            chosen: Optional[str] = None
            fallback: Optional[Tuple[Path, str]] = None
            for off in range(len(atoms)):
                atom_path = atoms[(start + off) % len(atoms)]
                atom_data = _load_yaml(atom_path)
                content = str(atom_data.get("body") or atom_data.get("content") or "").strip()
                if not (content and len(content.split()) > 20):
                    continue
                if fallback is None:
                    fallback = (atom_path, content)
                if not _already_used(content):
                    chosen = content
                    logger.info(
                        "[enrichment_per_section] selected teacher_atom %s for chapter %s "
                        "section %s slot %s from %s",
                        atom_path.stem, chapter_number, section_index, slot_type, atom_path,
                    )
                    break
            if chosen is not None:
                return chosen
            # Every atom in this slot_type is already used — try the next
            # slot_type rather than forcing a duplicate here.
            continue
        return None

    if source_type == "persona_atom":
        # Locale-aware path: prefer atoms/{persona}/{topic}/{slot}/locales/{locale}/CANONICAL.txt
        # when locale is set and not 'en-US'; fall back to the base English file.
        def _canonical_for(slot_dir: Path) -> Path:
            if locale and locale != "en-US":
                lp = slot_dir / "locales" / locale / "CANONICAL.txt"
                if lp.exists():
                    return lp
            return slot_dir / "CANONICAL.txt"

        slot_types = source.get("slot_types", [])
        for slot_type in slot_types:
            slot_dir = repo_root / "atoms" / persona_id / topic / slot_type
            canonical = _canonical_for(slot_dir)
            if not canonical.exists():
                continue
            raw = canonical.read_text(encoding="utf-8")
            # Patch (d): try ARC-block selection FIRST. If the file is properly
            # structured with ## ARC vNN headers, this gives one block per
            # (chapter, section) and closes the cross-atom paragraph
            # concatenation leak that surfaced as the 9× Tanya paragraph in
            # Integration Smoke #2 (artifacts/qa/integration_smoke_v2_2026-05-16.md).
            block = _pick_canonical_block_per_section(
                raw,
                chapter_index=chapter_number,
                section_index=section_index,
                seed=f"{seed}:depth_pa:{slot_type}",
                slot_label=f"depth_pa:{slot_type}",
                source_path=canonical,
                reject=_already_used,  # ws_f1_depth_dedup: rotate off used siblings
            )
            if block is not None:
                btext = block["text"]
                if _already_used(btext):
                    continue  # all siblings used — skip to next slot_type
                return btext
            # Plain-prose CANONICAL.txt without ARC headers — fall back to the
            # legacy prose-chunk path so we never go silent (a WARNING was
            # already emitted by _pick_canonical_block_per_section above).
            prose = _extract_prose_from_canonical(raw)
            chunk = _select_prose_chunk_unique(
                prose,
                f"{seed}:depth_pa:{chapter_number}:{slot_type}:sec{section_index}",
                book_seen_bodies,
            )
            if chunk:
                if _already_used(chunk):
                    continue
                return chunk
        topic_dir = repo_root / "atoms" / persona_id / topic
        if topic_dir.exists():
            for engine_dir in sorted(topic_dir.iterdir()):
                if not engine_dir.is_dir():
                    continue
                if engine_dir.name.isupper():
                    continue
                if engine_dir.name == "locales":
                    continue
                canonical = _canonical_for(engine_dir)
                if not canonical.exists():
                    continue
                raw = canonical.read_text(encoding="utf-8")
                # Patch (d): ARC-block selection on the engine-dir path. THIS
                # is the actual leak site — pre-patch this branch concatenated
                # adjacent atom prose bodies (e.g. RECOGNITION v05 Tanya +
                # MECHANISM_PROOF v02 Sarah) into the same DEPTH slot.
                block = _pick_canonical_block_per_section(
                    raw,
                    chapter_index=chapter_number,
                    section_index=section_index,
                    seed=f"{seed}:depth_eng:{engine_dir.name}",
                    slot_label=f"depth_eng:{engine_dir.name}",
                    source_path=canonical,
                    reject=_already_used,  # ws_f1_depth_dedup: rotate off used siblings
                )
                if block is not None:
                    btext = block["text"]
                    if _already_used(btext):
                        continue
                    return btext
                # Plain-prose engine CANONICAL.txt — degraded fallback.
                prose = _extract_prose_from_canonical(raw)
                chunk = _select_prose_chunk_unique(
                    prose,
                    f"{seed}:depth_eng:{chapter_number}:{engine_dir.name}:sec{section_index}",
                    book_seen_bodies,
                )
                if chunk:
                    if _already_used(chunk):
                        continue
                    return chunk
        return None

    if source_type == "registry_variant":
        section_types = source.get("section_types", [])
        variant_preference = source.get("variant_preference", ["F2", "F3", "F4"])
        registry_path = repo_root / "registry" / f"{topic}.yaml"
        if not registry_path.exists():
            return None
        registry = _load_yaml(registry_path)
        sections = registry.get("sections", {})
        ch_key = f"chapter_{chapter_number:02d}"
        ch_data = sections.get(ch_key, {})
        inner = ch_data.get("sections", {})
        if not isinstance(inner, dict):
            return None
        for _sec_key, sec_data in inner.items():
            if not isinstance(sec_data, dict):
                continue
            if sec_data.get("type") not in section_types:
                continue
            # DEFECT 4 (cross-persona bleed): skip sections authored for a
            # different persona than the spine. This depth-resolver does not go
            # through _registry_type_lists, so the persona filter is applied here
            # directly. On no matching-persona section we return None and the
            # caller falls through to persona_atom/teacher.
            if persona_id and not _registry_persona_matches(
                _registry_section_persona(sec_data), persona_id
            ):
                logger.warning(
                    "DEFECT4: skipping depth registry section %s (persona=%r) — "
                    "foreign to spine persona_id=%r.",
                    _sec_key, _registry_section_persona(sec_data), persona_id,
                )
                continue
            variants = sec_data.get("variants", [])
            # ws_f1_depth_dedup: collect all preference-matching variant bodies,
            # then prefer one NOT already used book-wide; fall back to the first
            # match so the slot is still filled.
            reg_first: Optional[str] = None
            for pref in variant_preference:
                pref_l = pref.lower()
                for v in variants:
                    if not isinstance(v, dict):
                        continue
                    fam = str(v.get("variant_family", "")).lower()
                    vid = str(v.get("variant_id", "")).lower()
                    if pref_l in fam or pref_l in vid:
                        content = str(v.get("content") or "").strip()
                        # DEFECT 4 fix point (3): never return unauthored stubs.
                        if _REGISTRY_PLACEHOLDER_RE.match(content):
                            continue
                        if content and len(content.split()) > 20:
                            if reg_first is None:
                                reg_first = content
                            if not _already_used(content):
                                return content
            if reg_first is not None:
                return reg_first
        return None

    if source_type == "component_template":
        rel = source.get("source_path", "config/pearl_practice/component_templates.yaml")
        templates_path = repo_root / rel
        if not templates_path.exists():
            return None
        templates = _load_yaml(templates_path)
        pool = source.get("pool", "bridge")
        items = templates.get(pool, [])
        if not items:
            return None

        def _item_text(it: Any) -> Optional[str]:
            if isinstance(it, str):
                return it.strip() or None
            if isinstance(it, dict):
                return str(it.get("text") or it.get("content") or "").strip() or None
            return None

        # ws_f1_depth_dedup: rotate across the pool from the deterministic start
        # so a template body used in an earlier chapter is not re-stamped.
        start = _deterministic_index(f"{seed}:template:{pool}", len(items))
        first: Optional[str] = None
        for off in range(len(items)):
            txt = _item_text(items[(start + off) % len(items)])
            if not txt:
                continue
            if first is None:
                first = txt
            if not _already_used(txt):
                return txt
        return first

    if source_type == "phoenix_standard":
        rel = source.get("source_path", "")
        path = repo_root / rel if rel else Path()
        if not path.exists():
            return None
        data = _load_yaml(path)
        blocks = _phoenix_standard_text_candidates(data)
        if not blocks:
            return None
        # Include chapter_number in seed so different chapters pick different blocks
        # from the pool (integration_landing has 7 blocks; 12 chapters → some repeats
        # but cross-chapter dedup is better than all chapters getting block 0).
        # ws_f1_depth_dedup: rotate across blocks to prefer an unused one.
        start = _deterministic_index(f"{seed}:phoenix:{chapter_number}", len(blocks))
        first = None
        for off in range(len(blocks)):
            blk = blocks[(start + off) % len(blocks)]
            if first is None:
                first = blk
            if not _already_used(blk):
                return blk
        return first

    if source_type == "exercise_atom":
        rel = source.get("source_path", "")
        path = repo_root / rel if rel else Path()
        if not path.exists():
            return None
        atoms = sorted(path.glob("*.yaml"))
        if not atoms:
            return None
        # ws_f1_depth_dedup: rotate across exercise atoms so the same EXERCISE
        # body ("Just thirty seconds…") is not re-injected across all chapters.
        start = _deterministic_index(f"{seed}:exercise", len(atoms))
        first = None
        for off in range(len(atoms)):
            atom_data = _load_yaml(atoms[(start + off) % len(atoms)])
            body = str(atom_data.get("body") or atom_data.get("content") or "").strip()
            if not body:
                continue
            if first is None:
                first = body
            if not _already_used(body):
                return body
        return first

    if source_type == "practice_library":
        try:
            from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter

            composed = get_exercise_for_chapter(
                chapter_index=chapter_number - 1,
                topic_id=topic,
                persona_id=persona_id,
                seed=seed,
            )
            if composed and composed.strip() and len(composed.split()) > 20:
                return composed.strip()
        except Exception as e:  # pragma: no cover
            logger.warning("Depth practice_library load failed: %s", e)
        return None

    if source_type == "exercise_bridge":
        rel = source.get("source_path", "SOURCE_OF_TRUTH/exercises_v4/bridge_templates.yaml")
        path = repo_root / rel
        if not path.exists():
            return None
        data = _load_yaml(path)
        tpl_root = data.get("templates") or {}
        strings = _collect_bridge_template_strings(tpl_root)
        long_strings = [s for s in strings if len(s.split()) > 20]
        pool = long_strings or strings
        if not pool:
            return None
        # ws_f1_depth_dedup: rotate across the bridge-template pool.
        start = _deterministic_index(f"{seed}:exercise_bridge", len(pool))
        first = None
        for off in range(len(pool)):
            cand = pool[(start + off) % len(pool)]
            if first is None:
                first = cand
            if not _already_used(cand):
                return cand
        return first

    return None


def _fill_chapter_depth(
    chapter: EnrichedChapter,
    enriched_book: EnrichedBook,
    modules: Dict[str, Any],
    topic_overrides: Dict[str, Any],
    topic: str,
    tid: Optional[str],
    persona_id: str,
    chapter_count: int,
    rf: str,
    root: Path,
    max_words_to_add: int,
    book_budget_remaining: Optional[int],
    depth_round: int,
    pass_label: str,
    audit_list: List[Dict[str, Any]],
    deficit_floor: int,
    book_seen_bodies: Optional[set] = None,
    locale: Optional[str] = None,
) -> int:
    """
    Attempt to fill one chapter with depth content up to max_words_to_add.
    Returns total words added.

    book_seen_bodies: optional book-level set of _norm_ws(body) strings already used.
    Passed through to _load_depth_content to skip duplicate atoms across chapters.
    After adding content, registers both the raw and truncated body so subsequent
    chapters cannot reuse the same atom.
    """
    phase = _chapter_phase(chapter.number, chapter_count)
    priority_key = f"depth_priority_{phase}"
    priority_list = list(topic_overrides.get(priority_key) or [])
    if not priority_list:
        priority_list = list(DEFAULT_DEPTH_PRIORITY)

    words_added_total = 0
    remaining_allowance = max_words_to_add

    for module_name in priority_list:
        if remaining_allowance <= deficit_floor:
            break
        if _module_banned(module_name, chapter.number, phase, topic_overrides):
            continue
        module = modules.get(module_name)
        if not module:
            continue
        if not _chapter_affinity_ok(module.get("chapter_affinity"), chapter.number):
            continue
        restriction = module.get("topic_restriction")
        if restriction and topic not in restriction:
            continue

        tw_bounds = module.get("target_words_per_chapter") or [200, 400]
        upper_cap = int(tw_bounds[1]) if len(tw_bounds) > 1 else 400
        if rf == "deep_book_6h":
            upper_cap = min(1400, max(upper_cap, int(round(upper_cap * 2.4))))

        for source in module.get("sources", []):
            if not isinstance(source, dict):
                continue
            # Patch (d): pass the current positional offset within the chapter
            # as section_index. Each successive _load_depth_content call (and
            # therefore each appended depth slot) gets a distinct section_index,
            # which feeds _pick_canonical_block_per_section's pick_seed and
            # ensures per-section variation across multiple depth slots in the
            # same chapter+module+round+pass.
            _sec_idx_for_depth = len(chapter.slots)
            content = _load_depth_content(
                source=source,
                topic=topic,
                teacher_id=tid,
                persona_id=persona_id,
                chapter_number=chapter.number,
                seed=f"depth:{topic}:{chapter.number}:{module_name}:r{depth_round}:{pass_label}",
                repo_root=root,
                book_seen_bodies=book_seen_bodies,
                locale=locale,
                section_index=_sec_idx_for_depth,
            )
            if not content:
                continue
            word_list = content.split()
            if len(word_list) <= 20:
                continue

            max_chunk = min(remaining_allowance, upper_cap)
            if book_budget_remaining is not None:
                if book_budget_remaining - words_added_total <= 0:
                    return words_added_total
                max_chunk = min(max_chunk, book_budget_remaining - words_added_total)

            trimmed = _truncate_to_word_budget(content, max_chunk)
            added_w = len(trimmed.split())
            if added_w <= 0:
                continue

            if source.get("type") == "teacher_atom" and tid:
                from phoenix_v4.rendering.teacher_wrapper import apply_wrapper as _aw
                _depth_seed = f"depth:{topic}:{chapter.number}:{module_name}"
                trimmed = _aw(trimmed, teacher_id=tid, section_type=module_name, seed=_depth_seed, spine_context=enriched_book.spine_context)

            slot_type_out = (
                "EXERCISE"
                if module_name == "practice_scaffold"
                else f"DEPTH_{module_name.upper()}"
            )
            depth_slot = EnrichedSlot(
                slot_type=slot_type_out,
                content=trimmed,
                source=f"depth_module:{module_name}:{source.get('type')}",
                source_id=f"depth_{module_name}_{chapter.number}_{pass_label}",
                target_words=max_chunk,
                actual_words=added_w,
                enrichment_applied=[module_name],
            )
            chapter.slots.append(depth_slot)
            chapter.total_words += added_w
            words_added_total += added_w
            remaining_allowance -= added_w

            # Register used atom bodies book-wide so subsequent chapters skip them
            if book_seen_bodies is not None:
                book_seen_bodies.add(_norm_ws(content))   # full raw atom
                _trimmed_norm = _norm_ws(trimmed)
                if _trimmed_norm != _norm_ws(content):
                    book_seen_bodies.add(_trimmed_norm)   # truncated fragment

            audit_list.append({
                "chapter": chapter.number,
                "module": module_name,
                "source_type": source.get("type"),
                "words_added": added_w,
                "remaining_deficit": max(0, remaining_allowance),
                "depth_round": depth_round,
                "pass": pass_label,
            })

            if remaining_allowance <= deficit_floor:
                break

        if remaining_allowance <= deficit_floor:
            break

    return words_added_total


def apply_depth_pass(
    enriched_book: EnrichedBook,
    depth_map: Dict[str, Any],
    repo_root: Optional[Path] = None,
) -> EnrichedBook:
    """
    Fill thin chapters/slots by requesting depth modules from the depth_module_map.

    Runs AFTER select_enrichment(). Uses two-pass per-chapter budget reservation
    to prevent early chapters from starving late chapters (chapters 9–12).

    Pass 1 (Reservation): Each chapter gets up to MIN_DEPTH_WORDS_PER_CHAPTER (180w)
    before any chapter gets priority fill. Early chapters cannot consume late chapters'
    reserved budget.

    Pass 2 (Priority fill): Remaining budget distributed by priority — late chapters
    first, then by deficit size.
    """
    from phoenix_v4.planning.chapter_object_continuity import is_twelve_shape_continuity_active

    if is_twelve_shape_continuity_active(enriched_book.spine_context):
        logger.info(
            "twelve_shape_continuity: depth_module pass disabled to preserve "
            "approved 12-slot chapter shape"
        )
        return enriched_book
    root = repo_root or REPO_ROOT
    topic = enriched_book.topic
    modules = depth_map.get("depth_modules") or {}
    topic_overrides = (depth_map.get("topic_overrides") or {}).get(topic, {})
    tid = enriched_book.teacher_id
    persona_id = enriched_book.persona_id
    locale = getattr(enriched_book, "locale", None)
    chapter_count = len(enriched_book.chapters)
    rf = (enriched_book.runtime_format or "").strip()
    _bounds = _load_runtime_word_bounds(rf, root)
    book_wmax: Optional[int] = _bounds[1] if _bounds else None
    deficit_floor = 55 if rf == "deep_book_6h" else 100
    # OPD-109 Phase 1: deep_book_6h depth_rounds reduced from 3 to 2.
    # Three rounds × 2 passes × ~6 module hits stacked ~35 depth atoms into
    # Ch1's STORY+REFLECTION buckets, producing the "8 tableaus in a row"
    # operator complaint. Two rounds still fills word budget when paired with
    # the relaxed _max_extra_chunks_for_format and within-slot bridges.
    # See docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md.
    depth_rounds = 2 if rf == "deep_book_6h" else 1

    enriched_book.enrichment_audit.setdefault("depth_modules_added", [])

    # Format-aware per-chapter depth budget caps.
    # Short formats (short_book_30: 7500w) keep the conservative defaults.
    # Large formats (deep_book_6h: 65000w) need proportionally larger caps.
    if book_wmax is not None and chapter_count > 0:
        fair_share = book_wmax // chapter_count
        min_depth_per_ch = max(MIN_DEPTH_WORDS_PER_CHAPTER, fair_share // 4)
        target_depth_per_ch = max(TARGET_DEPTH_WORDS_PER_CHAPTER, fair_share // 2)
        max_depth_per_ch = max(MAX_DEPTH_WORDS_PER_CHAPTER, fair_share)
    else:
        min_depth_per_ch = MIN_DEPTH_WORDS_PER_CHAPTER
        target_depth_per_ch = TARGET_DEPTH_WORDS_PER_CHAPTER
        max_depth_per_ch = MAX_DEPTH_WORDS_PER_CHAPTER

    # Per-chapter tracking for audit telemetry
    pre_depth_words: Dict[int, int] = {ch.number: ch.total_words for ch in enriched_book.chapters}
    depth_words_added_by_chapter: Dict[int, int] = {ch.number: 0 for ch in enriched_book.chapters}
    depth_budget_starvation: List[Dict[str, Any]] = []
    audit_list: List[Dict[str, Any]] = enriched_book.enrichment_audit["depth_modules_added"]

    # BOOK-WIDE paragraph dedup (ws_f1_depth_dedup_20260615): one registry shared
    # across ALL chapters + depth rounds + passes. This is the F1 fix.
    #
    # Previously this was a PER-CHAPTER set ({chapter.number: set()}), so the depth
    # selector never saw that an earlier chapter had already injected a given atom
    # body — the same HOOK/EXERCISE/doctrine block was re-stamped in all 12 chapters
    # (⑤ leverB attribution: 223/224 deep-tier F1 clusters originate here). The old
    # comment claimed "cross-chapter duplicates are handled by _dedup_repeated_blocks
    # in clean_for_delivery", but that downstream pass is chapter-scoped + exact-match
    # and is defeated by the per-chapter trailing-clause variation the composer adds,
    # so the duplicates survive into the rendered book and fire F1.
    #
    # _SeenBodies is book-wide AND fuzzy: a candidate body that is ≥ Jaccard-threshold
    # similar (mirrors the register-gate F1 detector) to one already used anywhere in
    # the book is rejected, so the selector rotates to an unused sibling ARC block /
    # variant (HOOK has 88 blocks of headroom) — book completeness is preserved by
    # filling with DIFFERENT content, not by dropping the slot. Intra-chapter
    # repetition is still suppressed as a side effect (a body used in this chapter is
    # in the same book-wide registry). Short bodies stay exempt (see _SeenBodies).
    _book_seen_bodies = _SeenBodies()

    # Pre-seed the registry with the bodies select_enrichment already placed in every
    # chapter (HOOK / STORY / base slots). Without this, the depth rotation could
    # pick a sibling block that is itself near-duplicate to a BASE paragraph (which
    # the depth pass never registered), trading a depth re-injection for a fresh
    # base↔depth F1 pair. Seeding the existing content first makes the depth pass
    # avoid colliding with what is already in the book — paragraph-level so multi-atom
    # slots are each compared. Only the fuzzy index is seeded (note, not add): exact
    # base strings must stay selectable by depth where intended; we only steer the
    # rotation away from near-duplicates.
    for _ch in enriched_book.chapters:
        for _slot in _ch.slots:
            body = _slot.content or ""
            for _para in re.split(r"\n{2,}", body):
                _para = _para.strip()
                if _para:
                    _book_seen_bodies.note(_para)

    for _depth_round in range(depth_rounds):

        # ── Pass 1: Reservation ─────────────────────────────────────────────
        # Each chapter gets up to MIN_DEPTH_WORDS_PER_CHAPTER from a shared
        # reservation pool. No chapter may consume another chapter's reserved share.
        #
        # Reservation pool = MIN × n_chapters (≤ 85% of book_wmax for safety).
        reservation_pool = min_depth_per_ch * chapter_count
        if book_wmax is not None:
            reservation_pool = min(reservation_pool, int(book_wmax * 0.85))

        reservation_used = 0

        for ch_idx, chapter in enumerate(enriched_book.chapters):
            # Guard the reservation budget for remaining chapters:
            # chapters after this one each need at least MIN.
            remaining_after_count = chapter_count - ch_idx - 1
            protected_for_later = remaining_after_count * min_depth_per_ch
            available_reservation = reservation_pool - reservation_used - protected_for_later
            available_reservation = max(0, min(available_reservation, min_depth_per_ch))

            if available_reservation <= deficit_floor:
                # Reservation pool cannot serve this chapter
                if depth_words_added_by_chapter[chapter.number] < min_depth_per_ch:
                    depth_budget_starvation.append({
                        "chapter": chapter.number,
                        "reserved_min_met": False,
                        "reason": "reservation_pool_exhausted",
                        "depth_round": _depth_round,
                    })
                continue

            # Only add depth if chapter actually needs it
            target_words = sum(s.target_words for s in chapter.slots)
            deficit = target_words - chapter.total_words
            if deficit <= deficit_floor:
                continue

            # How much can still be added this round (respect MAX cap)?
            already_added = depth_words_added_by_chapter[chapter.number]
            room_in_cap = max(0, max_depth_per_ch - already_added)
            want = min(available_reservation, deficit, room_in_cap)
            if want <= deficit_floor:
                continue

            # Compute global book budget remaining
            book_room: Optional[int] = None
            if book_wmax is not None:
                current_book = sum(ch.total_words for ch in enriched_book.chapters)
                book_room = book_wmax - current_book
                if book_room <= 0:
                    break

            added = _fill_chapter_depth(
                chapter=chapter,
                enriched_book=enriched_book,
                modules=modules,
                topic_overrides=topic_overrides,
                topic=topic,
                tid=tid,
                persona_id=persona_id,
                chapter_count=chapter_count,
                rf=rf,
                root=root,
                max_words_to_add=want,
                book_budget_remaining=book_room,
                depth_round=_depth_round,
                pass_label=f"p1r{_depth_round}",
                audit_list=audit_list,
                deficit_floor=deficit_floor,
                book_seen_bodies=_book_seen_bodies,
                locale=locale,
            )
            reservation_used += added
            depth_words_added_by_chapter[chapter.number] += added

            if added == 0:
                # No eligible candidates found despite budget being available
                depth_budget_starvation.append({
                    "chapter": chapter.number,
                    "reserved_min_met": False,
                    "reason": "no_eligible_depth_candidates",
                    "depth_round": _depth_round,
                })

        # ── Pass 2: Priority fill ───────────────────────────────────────────
        # Distribute remaining budget. Late chapters (7–12) come first,
        # then by highest deficit.
        pass2_order = sorted(
            enriched_book.chapters,
            key=lambda ch: (
                0 if ch.number >= 7 else 1,          # late chapters first
                -(sum(s.target_words for s in ch.slots) - ch.total_words),  # largest deficit first
            ),
        )

        for chapter in pass2_order:
            if book_wmax is not None:
                current_book = sum(ch.total_words for ch in enriched_book.chapters)
                book_room = book_wmax - current_book
                if book_room <= 0:
                    break
            else:
                book_room = None

            target_words = sum(s.target_words for s in chapter.slots)
            deficit = target_words - chapter.total_words
            if deficit <= deficit_floor:
                continue

            already_added = depth_words_added_by_chapter[chapter.number]
            room_in_cap = max(0, max_depth_per_ch - already_added)
            # Target up to TARGET per chapter, max up to MAX
            want = min(deficit, room_in_cap, target_depth_per_ch)
            if want <= deficit_floor:
                continue

            if book_room is not None:
                want = min(want, book_room)
            if want <= deficit_floor:
                continue

            added = _fill_chapter_depth(
                chapter=chapter,
                enriched_book=enriched_book,
                modules=modules,
                topic_overrides=topic_overrides,
                topic=topic,
                tid=tid,
                persona_id=persona_id,
                chapter_count=chapter_count,
                rf=rf,
                root=root,
                max_words_to_add=want,
                book_budget_remaining=book_room,
                depth_round=_depth_round,
                pass_label=f"p2r{_depth_round}",
                audit_list=audit_list,
                deficit_floor=deficit_floor,
                book_seen_bodies=_book_seen_bodies,
                locale=locale,
            )
            depth_words_added_by_chapter[chapter.number] += added

    # ── Audit telemetry ─────────────────────────────────────────────────────
    depth_budget_by_chapter: List[Dict[str, Any]] = []
    for chapter in enriched_book.chapters:
        added = depth_words_added_by_chapter.get(chapter.number, 0)
        starved = any(
            s["chapter"] == chapter.number and not s["reserved_min_met"]
            for s in depth_budget_starvation
        )
        depth_budget_by_chapter.append({
            "chapter": chapter.number,
            "pre_depth_words": pre_depth_words.get(chapter.number, 0),
            "depth_words_added": added,
            "post_depth_words": chapter.total_words,
            "reserved_min_met": added >= min_depth_per_ch and not starved,
        })

    enriched_book.enrichment_audit["depth_budget_policy"] = {
        "mode": "per_chapter_reservation",
        "book_wmax": book_wmax,
        "reserved_min_per_chapter": min_depth_per_ch,
        "target_per_chapter": target_depth_per_ch,
        "max_per_chapter": max_depth_per_ch,
    }
    enriched_book.enrichment_audit["depth_budget_by_chapter"] = depth_budget_by_chapter
    enriched_book.enrichment_audit["depth_budget_starvation"] = depth_budget_starvation

    enriched_book.total_words = sum(ch.total_words for ch in enriched_book.chapters)
    enriched_book.enrichment_audit["total_words"] = enriched_book.total_words
    return enriched_book


def attach_exercise_journeys(
    enriched_book: EnrichedBook,
    *,
    seed: str,
    enabled: bool = True,
    repo_root: Optional[Path] = None,
) -> EnrichedBook:
    """
    After enrichment + depth pass: attach per-chapter exercise journeys to chapters and
    EXERCISE slots at template sections (4 / 8 / 10). Logs warnings when thesis outcome
    validation fails, prerequisites fail, or redundancy is detected.
    """
    if not enabled:
        return enriched_book

    from phoenix_v4.planning.exercise_journey_planner import (
        plan_exercise_journey,
        resolve_thesis_id,
    )
    from phoenix_v4.planning.exercise_registry_loader import (
        load_exercise_registry,
        load_journey_templates,
        load_thesis_outcome_map,
    )

    root = repo_root or REPO_ROOT
    exercises = load_exercise_registry(repo_root=root)
    thesis_outcomes = load_thesis_outcome_map(repo_root=root)
    templates = load_journey_templates(repo_root=root)

    ej_audit: List[Dict[str, Any]] = []
    topic = enriched_book.topic
    runtime = enriched_book.runtime_format or "standard_book"

    for chapter in enriched_book.chapters:
        thesis_id = resolve_thesis_id(topic, chapter.number, seed)
        journey = plan_exercise_journey(
            chapter.number,
            thesis_id,
            runtime,
            seed=seed,
            exercise_registry=exercises,
            thesis_outcomes=thesis_outcomes,
            journey_templates=templates,
        )

        if not journey.outcome_ok:
            logger.warning(
                "Exercise journey outcome mismatch ch=%s thesis=%s violations=%s",
                chapter.number,
                thesis_id,
                journey.outcome_violations,
            )
        if journey.prerequisite_violations:
            logger.warning(
                "Exercise journey prerequisites ch=%s violations=%s",
                chapter.number,
                journey.prerequisite_violations,
            )
        if journey.redundancy_warnings:
            logger.warning(
                "Exercise journey redundancy ch=%s warnings=%s",
                chapter.number,
                journey.redundancy_warnings,
            )

        chapter.exercise_journey = {
            "journey_type": journey.journey_type,
            "template_id": journey.template_id,
            "aligned_with_thesis": journey.aligned_with_thesis,
            "expected_outcome": journey.expected_outcome,
            "outcome_ok": journey.outcome_ok,
            "outcome_violations": list(journey.outcome_violations),
            "prerequisite_violations": list(journey.prerequisite_violations),
            "redundancy_warnings": list(journey.redundancy_warnings),
            "phases": [
                {
                    "name": p.name,
                    "target_section": p.target_section,
                    "exercise_id": p.exercise_id,
                    "intro": p.intro,
                }
                for p in journey.phases
            ],
        }

        used_sections: Dict[int, str] = {}
        for phase in journey.phases:
            sec = int(phase.target_section)
            for si, slot in enumerate(chapter.slots):
                if si + 1 != sec:
                    continue
                if slot.slot_type.strip().upper() != "EXERCISE":
                    continue
                if sec in used_sections:
                    continue
                slot.exercise_phase = phase.name
                slot.journey_exercise_id = phase.exercise_id
                used_sections[sec] = phase.exercise_id
                break

        ej_audit.append(
            {
                "chapter": chapter.number,
                "thesis_id": thesis_id,
                "journey_type": journey.journey_type,
                "exercise_ids": [p.exercise_id for p in journey.phases],
            }
        )

    enriched_book.enrichment_audit["exercise_journeys"] = ej_audit
    return enriched_book
