"""
Planner-owned accent / story intelligence.

Assigns sparse accent_beats, accent_budget, accent_signature, and story_mix_profile.
Renderer materializes planner-assigned accents only.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter
from phoenix_v4.planning.enhancement_contract_v21_runtime import (
    build_optional_accent_budget,
    validate_optional_accent_budget,
)
from phoenix_v4.text.wordcount import count_words, has_cjk_script

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ACCENT_BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "accent_banks"

ACCENT_CLASSES_V1 = frozenset(
    {
        "ENCOURAGEMENT",
        "CITED_EVIDENCE",
        "WISDOM_ESSENCE",
        "AUTHOR_COMMENTARY",
        "EXTERNAL_STORY",
    }
)

ACCENT_CLASSES_V2 = frozenset(
    {
        "REFLECTION_QUESTION",
        "TROUBLESHOOTING",
        "QUOTE",
    }
)

# v2.1: AUTHOR_DISCLOSURE is a proof_and_embodiment surface, distinct from
# AUTHOR_COMMENTARY (see ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md
# section 11). It is planner-selected from its own bank/budget like the other
# classes; it does not draw on the optional-accent slot budget.
ACCENT_CLASSES_V3 = frozenset(
    {
        "AUTHOR_DISCLOSURE",
    }
)

ALL_ACCENT_CLASSES = ACCENT_CLASSES_V1 | ACCENT_CLASSES_V2 | ACCENT_CLASSES_V3

ENHANCEMENT_CONTRACT_V21_SCHEMA_VERSION = "2.1.0"

V21_CHAPTER_ENGINE_SURFACES: tuple[str, ...] = (
    "VALIDATION_NORMALIZATION",
    "MECHANISM_EXPLANATION",
    "PRACTICE_APPLICATION",
    "TROUBLESHOOTING",
    "TRANSITION_GLUE",
    "CLOSING_TAKEAWAY",
    "PROPULSION",
)

V21_PROOF_AND_EMBODIMENT_SURFACES: tuple[str, ...] = (
    "HOOK_STORY",
    "EXTERNAL_STORY",
    "AUTHOR_DISCLOSURE",
    "CASE_STUDY",
    "CITED_EVIDENCE",
)

V21_OPTIONAL_ACCENT_SURFACES: tuple[str, ...] = (
    "QUOTE",
    "ENCOURAGEMENT",
    "REFLECTION_QUESTION",
    "AUTHOR_COMMENTARY",
    "WISDOM_ESSENCE",
)

V21_COHESION_AND_CRAFT_SURFACES: tuple[str, ...] = (
    "CALLBACK_PLANT",
    "CALLBACK_RETURN",
    "MOTIF",
    "ANALOGY",
    "METAPHOR",
    "BRIDGE",
    "TRANSITION",
)

V21_SURFACE_BUCKET_BY_CLASS: Dict[str, str] = {
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

V21_COUNT_UNITS: Dict[str, str] = {
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

V21_PREFERRED_POSITIONS: Dict[str, Tuple[str, ...]] = {
    "QUOTE": ("before_HOOK", "before_THREAD"),
    "CITED_EVIDENCE": ("after_HOOK", "before_STORY"),
    "EXTERNAL_STORY": ("after_HOOK", "after_REFLECTION", "before_STORY"),
    "ENCOURAGEMENT": ("after_EXERCISE", "after_turning_point"),
    "TROUBLESHOOTING": ("after_INTEGRATION",),
    "REFLECTION_QUESTION": ("after_REFLECTION", "before_THREAD"),
    "AUTHOR_COMMENTARY": ("after_PIVOT", "after_EXERCISE", "after_REFLECTION", "before_THREAD"),
    "AUTHOR_DISCLOSURE": ("after_PIVOT", "after_REFLECTION", "before_THREAD"),
    "WISDOM_ESSENCE": ("after_REFLECTION", "before_THREAD"),
    "CALLBACK_RETURN": ("after_PIVOT", "before_THREAD"),
}

V21_DISALLOWED_POSITIONS: Dict[str, Tuple[str, ...]] = {
    "TROUBLESHOOTING": ("before_HOOK", "after_HOOK", "before_STORY"),
}

V21_PHASE_WEIGHTS_BY_CLASS: Dict[str, Dict[str, int]] = {
    "REFLECTION_QUESTION": {"early": 6, "mid": 10, "late": 14},
    "TROUBLESHOOTING": {"early": 4, "mid": 8, "late": 12},
    "QUOTE": {"early": 14, "mid": 8, "late": 12},
    "ENCOURAGEMENT": {"early": 6, "mid": 10, "late": 8},
    "CITED_EVIDENCE": {"early": 12, "mid": 10, "late": 6},
    "EXTERNAL_STORY": {"early": 8, "mid": 10, "late": 10},
    "WISDOM_ESSENCE": {"early": 6, "mid": 10, "late": 12},
    "AUTHOR_COMMENTARY": {"early": 6, "mid": 10, "late": 10},
    "AUTHOR_DISCLOSURE": {"early": 10, "mid": 8, "late": 6},
}

V21_ROLE_WEIGHTS_BY_CLASS: Dict[str, Dict[str, int]] = {
    "REFLECTION_QUESTION": {"recognition": 4, "reframe": 2, "integration": 2},
    "TROUBLESHOOTING": {"practice": 3, "integration": 4, "application": 3},
    "CITED_EVIDENCE": {"recognition": 3, "reframe": 3, "understand": 2},
    "EXTERNAL_STORY": {"recognition": 3, "reframe": 3, "turn": 2},
    "ENCOURAGEMENT": {"practice": 3, "integration": 3, "repair": 2},
}

ACCENT_SELECTION_ORDER: Tuple[str, ...] = (
    "REFLECTION_QUESTION",
    "TROUBLESHOOTING",
    "QUOTE",
    "ENCOURAGEMENT",
    "CITED_EVIDENCE",
    "EXTERNAL_STORY",
    "WISDOM_ESSENCE",
    "AUTHOR_COMMENTARY",
    "AUTHOR_DISCLOSURE",
)

CLASS_DEFAULT_POSITIONS: Dict[str, Tuple[str, ...]] = {
    "ENCOURAGEMENT": ("after_EXERCISE", "after_turning_point"),
    "CITED_EVIDENCE": ("after_HOOK", "before_STORY"),
    "WISDOM_ESSENCE": ("after_REFLECTION", "before_THREAD"),
    "AUTHOR_COMMENTARY": ("after_REFLECTION", "after_EXERCISE", "before_THREAD"),
    "AUTHOR_DISCLOSURE": ("after_PIVOT", "after_REFLECTION", "before_THREAD"),
    "EXTERNAL_STORY": ("after_REFLECTION", "before_STORY", "after_HOOK"),
    "REFLECTION_QUESTION": ("after_REFLECTION", "before_THREAD"),
    "TROUBLESHOOTING": ("after_INTEGRATION",),
    "QUOTE": ("before_HOOK", "before_THREAD"),
}

DEFAULT_BOOK_IDEA = "recognition_before_action"
DEFAULT_BOOK_MOTIF = "quiet_capacity"

BOOK_PHASE_ORDER = ("problem", "history", "knowledge", "action", "maintenance")

# Explicit flagship minima for gen_z_professionals × anxiety (contract-v1).
# Prefer config/accent/brand_accent_profiles.yaml pilot_cells.accent_budget_overrides;
# these remain as a hard floor so the anxiety pilot cannot silently drop quotes/RQ/TS.
#
# AUTHOR_DISCLOSURE is deliberately NOT floored here (PR #5585,
# GOLDEN_5585_SCOPE_AWAY_2026-07-14): this exact pilot cell
# (gen_z_professionals:anxiety) is the flagship full-book golden's plan_id
# (gen_z_professionals_anxiety_twelve_shape_v2, ratified OPD
# OPD-20260711-PROPRIME-ACCENT-PIPELINE-100PCT). Forcing a guaranteed
# AUTHOR_DISCLOSURE slot here makes it compete for and win a slot that the
# ratified CANONICAL_FLAGSHIP_BOOK.txt golden does not contain, which is a
# real (not false-positive) full-book parity diff. AUTHOR_DISCLOSURE remains
# fully wired and selectable for every OTHER persona/topic pair — this
# exclusion is scoped to the one pilot cell the frozen golden depends on.
# Remove this exclusion only alongside a fresh golden ratification that
# includes AUTHOR_DISCLOSURE content for this pilot.
_PILOT_ACCENT_MINIMUMS: Dict[str, Dict[str, int]] = {
    "gen_z_professionals:anxiety": {
        "QUOTE": 3,
        "ENCOURAGEMENT": 2,
        "REFLECTION_QUESTION": 3,
        "TROUBLESHOOTING": 1,
        "CITED_EVIDENCE": 1,
        "EXTERNAL_STORY": 2,
        "WISDOM_ESSENCE": 1,
        "AUTHOR_COMMENTARY": 1,
    },
    # AUTHOR_DISCLOSURE supply extension (2026-07-14): same author (ravi_chandra,
    # config/author_registry.yaml) as the anxiety pilot, three OTHER topics he is
    # already registered for. Each has its own real authored bank under
    # SOURCE_OF_TRUTH/accent_banks/author_disclosure/<topic>/ravi_chandra/. The
    # gen_z_professionals:anxiety cell above is deliberately untouched — it stays
    # entangled with the frozen flagship golden (see GOLDEN_5585_SCOPE_AWAY_2026-07-14
    # and _author_commentary_and_disclosure_pools() below).
    "gen_z_professionals:overthinking": {
        "AUTHOR_DISCLOSURE": 1,
    },
    "gen_z_professionals:sleep_anxiety": {
        "AUTHOR_DISCLOSURE": 1,
    },
    "gen_z_professionals:social_anxiety": {
        "AUTHOR_DISCLOSURE": 1,
    },
}
_PILOT_SHARE_CAP_FLOOR: Dict[str, float] = {
    "gen_z_professionals:anxiety": 0.85,
}

CONTRACT_V1_SPINE_KEY = "enrichment_contract_v1"


def enrichment_contract_v1_enabled(spine_context: Optional[Mapping[str, Any]]) -> bool:
    """Deterministically activate the contract from explicit or production doctrine."""
    ctx = spine_context or {}
    if bool(ctx.get(CONTRACT_V1_SPINE_KEY)):
        return True
    quality_profile = str(
        ctx.get("quality_profile") or ctx.get("profile") or ""
    ).strip().lower()
    runtime_format = str(
        ctx.get("runtime_format")
        or ctx.get("runtime_format_id")
        or ""
    ).strip()
    return (
        quality_profile in {"production", "flagship"}
        and runtime_format == "extended_book_2h"
    )


def accent_class_bucket(accent_class: str) -> str:
    return V21_SURFACE_BUCKET_BY_CLASS.get(str(accent_class or "").strip().upper(), "optional_accents")


def count_unit_for_surface(surface: str) -> str:
    return V21_COUNT_UNITS.get(str(surface or "").strip().upper(), "tracked_surface")


def preferred_positions_for_surface(surface: str) -> List[str]:
    key = str(surface or "").strip().upper()
    return list(V21_PREFERRED_POSITIONS.get(key) or CLASS_DEFAULT_POSITIONS.get(key) or ())


def disallowed_positions_for_surface(surface: str) -> List[str]:
    key = str(surface or "").strip().upper()
    return list(V21_DISALLOWED_POSITIONS.get(key) or ())


_TEACHER_NAME_TOKENS = frozenset(
    {
        "ahjan",
        "master wu",
        "master feung",
        "junko",
        "sai ma",
        "master sha",
        "dalai lama",
        "jagadguru",
    }
)

_QUESTION_RE = re.compile(r"(?:^|\n)([^\n?]{12,}\?)\s*$", re.MULTILINE)
_TROUBLESHOOTING_RE = re.compile(
    r"(?:^|\n)((?:When you|If you forget|If you miss|What if you|When this happens)[^\n]{20,}(?:\.|\?))",
    re.MULTILINE | re.IGNORECASE,
)


@dataclass(frozen=True)
class AccentBeat:
    class_: str
    accent_id: str
    position: str
    body: str
    keys: Dict[str, Any] = field(default_factory=dict)

    def to_plan_dict(self) -> Dict[str, Any]:
        return {
            "class": self.class_,
            "accent_id": self.accent_id,
            "position": self.position,
            "keys": dict(self.keys),
        }


@dataclass(frozen=True)
class AccentPlanResult:
    accent_budget: Dict[str, int]
    story_mix_profile: str
    flat_rows: List[Dict[str, Any]]
    signature: str
    chapter_assignments: Dict[int, List[AccentBeat]]
    strategy_report: Dict[str, Any]
    alignment_report: Dict[str, Any]


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def locale_to_cluster(locale: Optional[str]) -> str:
    loc = (locale or "en-US").strip().replace("-", "_")
    if loc.lower() in ("en_us", "en"):
        return "en_US"
    return loc


def _book_idea(spine_context: Optional[Mapping[str, Any]]) -> str:
    ctx = spine_context or {}
    for key in ("book_idea", "idea", "book_idea_key"):
        val = ctx.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return DEFAULT_BOOK_IDEA


def _book_motif(spine_context: Optional[Mapping[str, Any]]) -> str:
    ctx = spine_context or {}
    for key in ("book_motif", "motif", "book_motif_key"):
        val = ctx.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return DEFAULT_BOOK_MOTIF


def _chapter_phase(chapter_number: int, chapter_count: int) -> str:
    if chapter_count <= 0:
        return "late"
    early_end = (chapter_count + 2) // 3
    mid_end = (2 * chapter_count) // 3
    if chapter_number <= early_end:
        return "early"
    if chapter_number <= mid_end:
        return "mid"
    return "late"


def _book_phase_for_chapter(chapter_number: int, chapter_count: int) -> str:
    """Map chapter index to five-phase macro-arc labels used by accent banks."""
    if chapter_count <= 0:
        return BOOK_PHASE_ORDER[-1]
    if chapter_count <= len(BOOK_PHASE_ORDER):
        idx = max(0, min(chapter_number - 1, len(BOOK_PHASE_ORDER) - 1))
        return BOOK_PHASE_ORDER[idx]
    weights = {
        "problem": 0.18,
        "history": 0.17,
        "knowledge": 0.25,
        "action": 0.22,
        "maintenance": 0.18,
    }
    counts = {phase: 1 for phase in BOOK_PHASE_ORDER}
    remaining = chapter_count - len(BOOK_PHASE_ORDER)
    fractions: List[Tuple[float, str]] = []
    for phase in BOOK_PHASE_ORDER:
        raw = weights[phase] * remaining
        whole = int(raw)
        counts[phase] += whole
        fractions.append((raw - whole, phase))
    leftover = remaining - sum(counts[p] - 1 for p in BOOK_PHASE_ORDER)
    for _, phase in sorted(fractions, key=lambda item: (-item[0], BOOK_PHASE_ORDER.index(item[1]))):
        if leftover <= 0:
            break
        counts[phase] += 1
        leftover -= 1
    labels: List[str] = []
    for phase in BOOK_PHASE_ORDER:
        labels.extend([phase] * counts[phase])
    return labels[min(max(chapter_number - 1, 0), len(labels) - 1)]


def resolve_story_mix_profile(
    brand_id: str,
    *,
    persona_id: str = "",
    topic_id: str = "",
    repo_root: Path = REPO_ROOT,
) -> str:
    accent_profiles = _load_yaml(repo_root / "config" / "accent" / "brand_accent_profiles.yaml")
    pilot = (accent_profiles.get("pilot_cells") or {}).get(f"{persona_id}:{topic_id}")
    if isinstance(pilot, dict) and pilot.get("story_mix_profile"):
        return str(pilot["story_mix_profile"])
    data = _load_yaml(repo_root / "config" / "authoring" / "story_mix_profiles.yaml")
    return str((data.get("default_by_brand") or {}).get(brand_id) or "practical_credible")


def _scale_from_trade_book(value: int, chapter_count: int, *, minimum: int = 0) -> int:
    if chapter_count <= 0:
        return minimum
    return max(minimum, int(math.ceil((float(value) * float(chapter_count)) / 12.0)))


def _surface_tracking_row(
    surface: str,
    *,
    requested: int,
    assigned: int,
    planner_tracking_mode: str,
) -> Dict[str, Any]:
    return {
        "surface": surface,
        "bucket": accent_class_bucket(surface),
        "requested": int(requested),
        "assigned": int(assigned),
        "count_unit": count_unit_for_surface(surface),
        "preferred_positions": preferred_positions_for_surface(surface),
        "disallowed_positions": disallowed_positions_for_surface(surface),
        "planner_tracking_mode": planner_tracking_mode,
    }


def build_enhancement_contract_v21_summary(
    *,
    accent_budget: Mapping[str, int],
    flat_rows: Sequence[Mapping[str, Any]],
    chapter_count: int,
    story_mix_profile: str,
    max_accents_per_chapter: int,
    persona_id: str = "",
    topic_id: str = "",
) -> Dict[str, Any]:
    counts = _assignment_counts(flat_rows)
    optional_counts = {
        cls: int(counts.get(cls, 0))
        for cls in V21_OPTIONAL_ACCENT_SURFACES
        if int(accent_budget.get(cls, 0)) > 0 or int(counts.get(cls, 0)) > 0
    }
    optional_requested = {
        cls: int(accent_budget.get(cls, 0))
        for cls in V21_OPTIONAL_ACCENT_SURFACES
        if int(accent_budget.get(cls, 0)) > 0 or int(counts.get(cls, 0)) > 0
    }
    optional_per_chapter: Dict[int, int] = {}
    for row in flat_rows:
        cls = str(row.get("class") or "").strip().upper()
        if cls not in V21_OPTIONAL_ACCENT_SURFACES:
            continue
        chapter = int(row.get("chapter") or 0)
        optional_per_chapter[chapter] = optional_per_chapter.get(chapter, 0) + 1
    optional_chapters = sorted(optional_per_chapter)
    tracked_surfaces: List[Dict[str, Any]] = []
    for surface in V21_OPTIONAL_ACCENT_SURFACES:
        tracked_surfaces.append(
            _surface_tracking_row(
                surface,
                requested=int(accent_budget.get(surface, 0)),
                assigned=int(counts.get(surface, 0)),
                planner_tracking_mode="planner_counted",
            )
        )
    for surface in ("TROUBLESHOOTING", "CITED_EVIDENCE", "EXTERNAL_STORY", "AUTHOR_DISCLOSURE"):
        tracked_surfaces.append(
            _surface_tracking_row(
                surface,
                requested=int(accent_budget.get(surface, 0)),
                assigned=int(counts.get(surface, 0)),
                planner_tracking_mode="planner_counted" if surface in accent_budget else "tracked_surface_only",
            )
        )
    for surface in ("ANALOGY", "METAPHOR", "CALLBACK_RETURN"):
        tracked_surfaces.append(
            _surface_tracking_row(
                surface,
                requested=0,
                assigned=0,
                planner_tracking_mode="downstream_audit_only",
            )
        )
    optional_budget = build_optional_accent_budget(
        chapter_count=chapter_count,
        max_accents_per_chapter=int(max_accents_per_chapter),
    )
    optional_budget.update(
        {
            "class_hard_maxima": optional_requested,
            "actual": {
                "assigned_total_optional_accents": sum(optional_counts.values()),
                "optional_assignment_counts": optional_counts,
                "chapters_with_optional_accents": optional_chapters,
                "optional_accent_chapter_count": len(optional_chapters),
                "accent_free_chapter_count": max(0, int(chapter_count) - len(optional_chapters)),
                "per_chapter_optional_counts": {
                    str(ch): int(count)
                    for ch, count in sorted(optional_per_chapter.items())
                },
            },
        }
    )
    optional_integrity = validate_optional_accent_budget(
        optional_budget,
        chapter_count=chapter_count,
    )
    return {
        "schema_version": ENHANCEMENT_CONTRACT_V21_SCHEMA_VERSION,
        "truth_label": "research_informed_working_priors",
        "surface_taxonomy": {
            "chapter_engine": list(V21_CHAPTER_ENGINE_SURFACES),
            "proof_and_embodiment": list(V21_PROOF_AND_EMBODIMENT_SURFACES),
            "optional_accents": list(V21_OPTIONAL_ACCENT_SURFACES),
            "cohesion_and_craft": list(V21_COHESION_AND_CRAFT_SURFACES),
        },
        "count_units": dict(V21_COUNT_UNITS),
        "tracked_surfaces": tracked_surfaces,
        "optional_accent_budget": optional_budget,
        "optional_accent_integrity": optional_integrity,
        "phase_strategy": {
            "story_mix_profile": story_mix_profile,
            "chapter_phase_order": list(BOOK_PHASE_ORDER),
            "phase_weights_by_class": dict(V21_PHASE_WEIGHTS_BY_CLASS),
            "role_weights_by_class": dict(V21_ROLE_WEIGHTS_BY_CLASS),
            "anxiety_flagship_mode": (
                "validation_plus_mechanism_hybrid"
                if str(persona_id or "").strip() == "gen_z_professionals" and str(topic_id or "").strip() == "anxiety"
                else "profile_default"
            ),
        },
        "tracking_notes": [
            "TROUBLESHOOTING, CITED_EVIDENCE, and EXTERNAL_STORY are tracked outside the optional-accent bucket.",
            "AUTHOR_DISCLOSURE is distinct from AUTHOR_COMMENTARY even when no authored disclosure bank is present.",
            "ANALOGY, METAPHOR, and callback return surfaces are counted downstream from slots/hooks and audits, not from optional accent budgets.",
        ],
    }


def _external_story_function(entry: Mapping[str, Any]) -> Tuple[str, str]:
    explicit = str(entry.get("story_function") or entry.get("story_role") or "").strip()
    allowed = {"recognition", "mechanism_proof", "turn", "possibility", "cautionary"}
    if explicit in allowed:
        return explicit, "authored_bank"
    emotion = str(entry.get("emotional_shape") or entry.get("emotional_register") or "").strip()
    emotion_map = {
        "quiet-recognition": "recognition",
        "humor": "recognition",
        "tearjerker": "recognition",
        "contrast": "turn",
        "breakthrough": "possibility",
        "underdog": "possibility",
        "cautionary": "cautionary",
    }
    if emotion in emotion_map:
        return emotion_map[emotion], "inferred_emotional_shape"
    fit = str(entry.get("position_fit") or "").upper()
    if "PIVOT" in fit:
        return "turn", "inferred_position_fit"
    if "HOOK" in fit:
        return "recognition", "inferred_position_fit"
    if "TAKEAWAY" in fit:
        return "possibility", "inferred_position_fit"
    return "recognition", "default_recognition"


def _truth_metadata_for_entry(accent_class: str, entry: Mapping[str, Any]) -> Dict[str, Any]:
    cls = str(accent_class or "").strip().upper()
    if cls == "EXTERNAL_STORY":
        return {
            "source": str(entry.get("source") or "").strip(),
            "citation": str(entry.get("citation") or "").strip(),
            "rights_class": str(entry.get("rights_class") or "").strip(),
            "truth_status": str(entry.get("rights_class") or "unspecified").strip() or "unspecified",
        }
    if cls == "CITED_EVIDENCE":
        return {
            "citation": str(entry.get("citation") or "").strip(),
            "year": entry.get("year"),
            "robustness": str(entry.get("robustness") or "").strip(),
            "truth_status": str(entry.get("robustness") or "unspecified").strip() or "unspecified",
        }
    return {}


def resolve_enrichment_strategy_profile(
    brand_id: str,
    *,
    persona_id: str = "",
    topic_id: str = "",
    repo_root: Path = REPO_ROOT,
) -> str:
    """Alias for resolve_story_mix_profile — enrichment strategy family selector."""
    return resolve_story_mix_profile(
        brand_id,
        persona_id=persona_id,
        topic_id=topic_id,
        repo_root=repo_root,
    )


def _dosage_target(dosage_envelope: Mapping[str, Any], accent_class: str) -> int:
    spec = dosage_envelope.get(accent_class)
    if isinstance(spec, (int, float)):
        return int(spec)
    if not isinstance(spec, dict):
        return 0
    if spec.get("target") is not None:
        return int(spec["target"])
    if spec.get("min") is not None:
        return int(spec["min"])
    return 0


def _story_mix_profile_data(profile_name: str, repo_root: Path) -> dict[str, Any]:
    data = _load_yaml(repo_root / "config" / "authoring" / "story_mix_profiles.yaml")
    return dict((data.get("profiles") or {}).get(profile_name) or {})


def resolve_accent_budget(
    brand_id: str,
    *,
    persona_id: str = "",
    topic_id: str = "",
    enrichment_contract_v1: bool = False,
    repo_root: Path = REPO_ROOT,
) -> Tuple[Dict[str, int], str, float]:
    data = _load_yaml(repo_root / "config" / "accent" / "brand_accent_profiles.yaml")
    pilot = (data.get("pilot_cells") or {}).get(f"{persona_id}:{topic_id}")
    if isinstance(pilot, dict) and pilot.get("profile"):
        profile_name = str(pilot["profile"])
    else:
        profile_name = str(
            (data.get("default_by_brand") or {}).get(brand_id)
            or data.get("default_profile")
            or "minimal_accent"
        )
    brand_profile = (data.get("profiles") or {}).get(profile_name) or {}
    if not enrichment_contract_v1:
        budget = {
            k: int(v)
            for k, v in (brand_profile.get("accent_budget") or {}).items()
            if k in ACCENT_CLASSES_V1
        }
        for cls in ACCENT_CLASSES_V1:
            budget.setdefault(cls, 0)
        share_cap = float(brand_profile.get("max_accent_chapter_share", 0.25))
        return budget, profile_name, share_cap

    brand_budget = {
        k: int(v)
        for k, v in (brand_profile.get("accent_budget") or {}).items()
        if k in ALL_ACCENT_CLASSES
    }

    story_mix_profile = resolve_story_mix_profile(
        brand_id,
        persona_id=persona_id,
        topic_id=topic_id,
        repo_root=repo_root,
    )
    mix_profile = _story_mix_profile_data(story_mix_profile, repo_root)
    dosage_envelope = mix_profile.get("dosage_envelope") or {}

    budget: Dict[str, int] = {}
    for cls in ALL_ACCENT_CLASSES:
        brand_val = int(brand_budget.get(cls, 0))
        dosage_val = _dosage_target(dosage_envelope, cls)
        budget[cls] = max(brand_val, dosage_val)

    share_cap = float(
        mix_profile.get("max_accent_chapter_share")
        if mix_profile.get("max_accent_chapter_share") is not None
        else brand_profile.get("max_accent_chapter_share", 0.25)
    )
    pilot_key = f"{persona_id}:{topic_id}"
    if enrichment_contract_v1:
        # Config-authored overrides on the pilot cell take precedence as floors.
        if isinstance(pilot, dict):
            for cls, minimum in (pilot.get("accent_budget_overrides") or {}).items():
                if cls in ALL_ACCENT_CLASSES:
                    budget[cls] = max(int(budget.get(cls, 0)), int(minimum))
            if pilot.get("max_accent_chapter_share") is not None:
                share_cap = max(share_cap, float(pilot["max_accent_chapter_share"]))
        for cls, minimum in (_PILOT_ACCENT_MINIMUMS.get(pilot_key) or {}).items():
            budget[cls] = max(int(budget.get(cls, 0)), int(minimum))
        if pilot_key in _PILOT_SHARE_CAP_FLOOR:
            share_cap = max(share_cap, _PILOT_SHARE_CAP_FLOOR[pilot_key])
    return budget, profile_name, share_cap


def compute_accent_signature(
    assignments: Sequence[Mapping[str, Any]],
    *,
    accent_budget: Mapping[str, int],
) -> str:
    counts = {k: 0 for k in ALL_ACCENT_CLASSES}
    placements: List[Tuple[int, str, str]] = []
    for row in assignments:
        cls = str(row.get("class") or "")
        if cls in counts:
            counts[cls] += 1
        placements.append((int(row.get("chapter") or 0), cls, str(row.get("position") or "")))
    payload = {
        "budget": {k: int(accent_budget.get(k, 0)) for k in sorted(ALL_ACCENT_CLASSES)},
        "counts": counts,
        "placements": sorted(placements),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _deterministic_rank(seed: str, key: str) -> int:
    return int(hashlib.sha256(f"{seed}:{key}".encode("utf-8")).hexdigest()[:12], 16)


def _spread_chapters(candidates: List[int], count: int, seed: str, salt: str) -> List[int]:
    if count <= 0 or not candidates:
        return []
    ranked = sorted(candidates, key=lambda ch: _deterministic_rank(seed, f"{salt}:ch{ch}"))
    if count >= len(ranked):
        return ranked[:count]
    step = max(1, len(ranked) // count)
    picked = [ranked[i] for i in range(0, len(ranked), step)][:count]
    for ch in ranked:
        if len(picked) >= count:
            break
        if ch not in picked:
            picked.append(ch)
    return sorted(picked)[:count]


def _chapter_slot_types(ch: EnrichedChapter) -> List[str]:
    return [str(s.slot_type or "").strip().upper() for s in ch.slots if str(s.slot_type or "").strip()]


def _chapter_renderable_words(ch: EnrichedChapter) -> int:
    """Count words available for accent insertion (empty chapters cannot host accents)."""
    total = 0
    for slot in ch.slots or []:
        actual = int(getattr(slot, "actual_words", 0) or 0)
        if actual > 0:
            total += actual
            continue
        content = str(getattr(slot, "content", "") or "").strip()
        if content:
            total += len(content.split())
    return total


def _chapter_can_host_accents(ch: EnrichedChapter, *, min_words: int = 80) -> bool:
    """Skip chapters whose slot streams are empty/stub — accents would not survive compose."""
    return _chapter_renderable_words(ch) >= min_words and bool(_chapter_slot_types(ch))


def _position_fits(position: str, slot_types: Sequence[str]) -> bool:
    st = list(slot_types)
    if position == "before_HOOK":
        return "HOOK" in st
    if position == "after_HOOK":
        return "HOOK" in st
    if position == "before_STORY":
        return any(x == "STORY" for x in st)
    if position == "after_EXERCISE":
        return "EXERCISE" in st
    if position == "after_REFLECTION":
        return "REFLECTION" in st
    if position == "before_THREAD":
        return "THREAD" in st
    if position == "after_PIVOT":
        return "PIVOT" in st
    if position == "after_INTEGRATION":
        return "INTEGRATION" in st
    if position == "after_turning_point":
        return st.count("STORY") >= 2
    return False


def _pick_position(
    accent_class: str,
    slot_types: Sequence[str],
    *,
    seed: str,
    chapter_number: int,
    allowed_positions: Optional[Sequence[str]] = None,
) -> Optional[str]:
    options = [p for p in CLASS_DEFAULT_POSITIONS.get(accent_class, ()) if _position_fits(p, slot_types)]
    if allowed_positions:
        allowed = {str(v).strip() for v in allowed_positions}
        options = [p for p in options if p in allowed]
    if not options:
        return None
    return options[_deterministic_rank(seed, f"pos:{accent_class}:ch{chapter_number}") % len(options)]


def _allowed_positions_ok(entry: Mapping[str, Any], position: str) -> bool:
    """Honor authored bank `allowed_positions` contracts when present."""
    allowed = entry.get("allowed_positions")
    if allowed is None:
        return True
    values = allowed if isinstance(allowed, list) else [allowed]
    normalized = {str(v).strip() for v in values if str(v).strip()}
    if not normalized:
        return True
    return position in normalized


def _locale_fit_ok(entry: Mapping[str, Any], locale_cluster: str) -> bool:
    fit = entry.get("locale_fit")
    if fit is None:
        return True
    if isinstance(fit, list):
        normalized = {str(x).strip() for x in fit}
        return "universal" in normalized or locale_cluster in normalized
    return str(fit).strip() in ("universal", locale_cluster)


def _composite_body_safe(body: str, *, composite_mode: bool) -> bool:
    if not composite_mode:
        return True
    lower = body.lower()
    return not any(tok in lower for tok in _TEACHER_NAME_TOKENS)


def _secular_entry_ok(entry: Mapping[str, Any], *, composite_mode: bool) -> bool:
    if not composite_mode:
        return True
    if entry.get("secular_safe") is False or entry.get("composite_safe") is False:
        return False
    return _composite_body_safe(_entry_body(entry), composite_mode=True)


def _entry_body(entry: Mapping[str, Any]) -> str:
    variants = entry.get("position_variants")
    if isinstance(variants, dict):
        for v in variants.values():
            if isinstance(v, dict) and v.get("body"):
                return str(v["body"]).strip()
    for key in ("body", "story", "claim", "text", "text_en", "question"):
        val = entry.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    reg = entry.get("register_variants")
    if isinstance(reg, dict):
        sec = reg.get("secular")
        if isinstance(sec, dict) and sec.get("body"):
            return str(sec["body"]).strip()
    return ""


def _wrap_cited_evidence(
    claim: str,
    citation: str,
    *,
    position: str,
    entry: Optional[Mapping[str, Any]] = None,
) -> str:
    claim = claim.strip()
    citation = citation.strip()
    prefix = ""
    try:
        from phoenix_v4.rendering.science_wrapper import resolve_wrapper

        ctx = {
            "FINDING": claim,
            "FIELD": str((entry or {}).get("field") or "affective neuroscience and stress physiology"),
            "FIELD_SHORT": str((entry or {}).get("field_short") or "stress-physiology"),
            "MECHANISM": str(
                (entry or {}).get("mechanism")
                or "the body's threat-and-safety response"
            ),
        }
        researcher = str((entry or {}).get("researcher") or "").strip()
        study = str((entry or {}).get("study") or "").strip()
        if researcher:
            ctx["RESEARCHER"] = researcher
        if study:
            ctx["STUDY"] = study
        prefix, _suffix = resolve_wrapper(
            section_type="STORY" if position in ("after_HOOK", "before_STORY") else "REFLECTION",
            seed=f"{(entry or {}).get('evidence_id') or citation or claim}:{position}",
            spine_context=ctx,
        )
    except Exception:
        prefix = ""
    lead = (
        "That replay has a nervous-system explanation."
        if position in ("after_HOOK", "before_STORY")
        else "The body pattern has a research-shaped edge worth naming."
    )
    handoff = (
        "Carry that explanation back into the scene that follows."
        if position in ("after_HOOK", "before_STORY")
        else "Let that finding sit beside what the body already showed you."
    )
    science_sentence = (prefix or claim).strip().rstrip(".")
    if prefix and claim and claim.lower() not in prefix.lower():
        science_sentence = f"{science_sentence}: {claim.rstrip('.')}"
    citation_part = f" ({citation})." if citation else "."
    return f"{lead} {science_sentence}{citation_part} {handoff}"


def _wrap_external_story(story: str, source: str, *, position: str) -> str:
    story = story.strip()
    source = source.strip()
    if position == "after_HOOK":
        lead = "The same alarm can scale from one body to a whole room."
    elif position == "after_REFLECTION":
        lead = "Before returning to this body, widen the lens for one outside example."
    else:
        lead = "One outside story can make the pattern easier to see."
    source_sentence = f" Public accounts name this arc as {source}." if source else ""
    handoff = (
        "Now bring that pattern back into what happens next in this room."
        if position != "before_THREAD"
        else "Carry that image into the thread that follows."
    )
    return f"{lead} {story}{source_sentence} {handoff}"


def _wrap_encouragement(prose: str, *, position: str) -> str:
    handoff = (
        "Take that recognition into the integration that follows."
        if position == "after_EXERCISE"
        else "Let that land before the next story beat."
    )
    return f"{prose.strip()}\n\n{handoff}".strip()


def _wrap_reflection_question(question: str, *, position: str) -> str:
    handoff = (
        "Carry that question into the thread that follows."
        if position == "before_THREAD"
        else "Sit with that question before the next beat."
    )
    return f"{question.strip()}\n\n{handoff}".strip()


def _wrap_troubleshooting(prose: str, *, position: str) -> str:
    _ = position
    return (
        f"When the practice wobbles, this is what to do next. {prose.strip()} "
        "Return to the thread when you are ready."
    ).strip()


def _wrap_quote(text: str, author: str, source: str, *, position: str) -> str:
    handoff = (
        "Let that line open the chapter before the hook lands."
        if position == "before_HOOK"
        else "Carry that line into the thread that follows."
    )
    attribution = f"{author.strip()}"
    if source.strip():
        attribution = f"{author.strip()}, {source.strip()}"
    return f'"{text.strip()}" — {attribution}. {handoff}'


def _load_external_stories(topic: str, locale_cluster: str, repo_root: Path) -> List[dict[str, Any]]:
    data = _load_yaml(ACCENT_BANKS / "external_stories" / f"{topic}_entries.yaml")
    clusters = data.get("clusters") or {}
    rows = list(clusters.get("universal") or []) + list(clusters.get(locale_cluster) or [])
    return [r for r in rows if isinstance(r, dict)]


def _load_cited_evidence(topic: str, repo_root: Path) -> List[dict[str, Any]]:
    return [
        e
        for e in (_load_yaml(ACCENT_BANKS / "evidence" / topic / "entries.yaml").get("entries") or [])
        if isinstance(e, dict)
    ]


def _load_wisdom_essence(topic: str, repo_root: Path) -> List[dict[str, Any]]:
    return [
        e
        for e in (_load_yaml(ACCENT_BANKS / "wisdom_essence" / topic / "entries.yaml").get("entries") or [])
        if isinstance(e, dict)
    ]


def _load_author_commentary(topic: str, author_id: str, locale_cluster: str, repo_root: Path) -> List[dict[str, Any]]:
    data = _load_yaml(ACCENT_BANKS / "author_commentary" / topic / author_id / f"{locale_cluster}.yaml")
    return [r for r in (data.get("commentaries") or data.get("entries") or []) if isinstance(r, dict)]


def _load_author_disclosure(topic: str, author_id: str, locale_cluster: str, repo_root: Path) -> List[dict[str, Any]]:
    """AUTHOR_DISCLOSURE pool — distinct from AUTHOR_COMMENTARY (see
    ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md section 11)."""
    data = _load_yaml(ACCENT_BANKS / "author_disclosure" / topic / author_id / f"{locale_cluster}.yaml")
    return [r for r in (data.get("disclosures") or data.get("entries") or []) if isinstance(r, dict)]


def _is_flagship_frozen_golden_pilot(persona_id: str, topic_id: str) -> bool:
    """True for the exact persona/topic cell the ratified flagship full-book golden
    (artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt, plan_id
    gen_z_professionals_anxiety_twelve_shape_v2, OPD-20260711-PROPRIME-ACCENT-PIPELINE-100PCT)
    is built from. See GOLDEN_5585_SCOPE_AWAY_2026-07-14."""
    return persona_id == "gen_z_professionals" and topic_id == "anxiety"


# Original, single-file order of the 10 gen_z_professionals:anxiety AUTHOR_COMMENTARY
# entries before PR #5585 split 3 of them out into AUTHOR_DISCLOSURE (frozen historical
# fact, not re-derived — see GOLDEN_5585_SCOPE_AWAY_2026-07-14). _select_entry picks by
# `candidates[hash(...) % len(candidates)]`, which is sensitive to LIST ORDER, not just
# list membership/count — so restoring the right 10 entries in the WRONG order still
# changes the deterministic pick. This is the exact order from
# `git show 71bd6883b3^:SOURCE_OF_TRUTH/accent_banks/author_commentary/anxiety/ravi_chandra/en_US.yaml`
# (the commit immediately before the first AUTHOR_DISCLOSURE split commit).
_FLAGSHIP_FROZEN_COMMENTARY_ORIGINAL_ORDER: Tuple[str, ...] = (
    "ac_ravi_anxiety_observed_standup_v01",
    "ac_ravi_anxiety_observed_noting_v01",
    "ad_ravi_anxiety_admission_body_lead_v01",  # now lives in AUTHOR_DISCLOSURE
    "ac_ravi_anxiety_endorsement_stuck_v01",
    "ac_ravi_anxiety_skeptic_standup_v01",
    "ad_ravi_anxiety_disclosure_ahjan_v01",  # now lives in AUTHOR_DISCLOSURE
    "ac_ravi_anxiety_observed_freeze_v01",
    "ad_ravi_anxiety_admission_perform_fine_v01",  # now lives in AUTHOR_DISCLOSURE
    "ac_ravi_anxiety_endorsement_small_v01",
    "ac_ravi_anxiety_skeptic_loading_screen_v01",
)


def _author_commentary_and_disclosure_pools(
    persona_id: str, topic_id: str, author_id: str, locale_cluster: str, repo_root: Path
) -> Tuple[List[dict[str, Any]], List[dict[str, Any]]]:
    """Load the AUTHOR_COMMENTARY and AUTHOR_DISCLOSURE pools, with one frozen-golden
    exception (GOLDEN_5585_SCOPE_AWAY_2026-07-14).

    Splitting 3 entries out of AUTHOR_COMMENTARY into the new AUTHOR_DISCLOSURE bank
    (PR #5585) shrank the AUTHOR_COMMENTARY candidate set from 10 to 7 for every cell.
    That is the correct, intended improvement everywhere EXCEPT the one flagship
    persona/topic cell the ratified full-book golden was rendered from: the
    deterministic per-chapter ranking in _select_entry picks `candidates[hash(...) %
    len(candidates)]`, which depends on both the CANDIDATE COUNT and their LIST ORDER.
    A smaller/reordered AUTHOR_COMMENTARY pool changes which entry wins at a given
    chapter position even with AUTHOR_DISCLOSURE's own budget floor removed.

    For that one frozen cell only: merge AUTHOR_DISCLOSURE's entries back into the
    AUTHOR_COMMENTARY candidate pool IN THEIR ORIGINAL RELATIVE ORDER (restoring the
    exact original 10-candidate ranking universe byte-for-byte, not just the same 10
    members in a different order) and return an empty AUTHOR_DISCLOSURE pool (so it
    cannot also be organically selected as its own class here, independent of the
    budget floor). Every other persona/topic cell is unaffected and gets the real 7+3
    split.
    """
    commentary = _load_author_commentary(topic_id, author_id, locale_cluster, repo_root)
    disclosure = _load_author_disclosure(topic_id, author_id, locale_cluster, repo_root)
    if author_id == "ravi_chandra" and _is_flagship_frozen_golden_pilot(persona_id, topic_id):
        by_id = {
            str(e.get("commentary_id") or e.get("disclosure_id")): e
            for e in (commentary + disclosure)
        }
        merged = [by_id[i] for i in _FLAGSHIP_FROZEN_COMMENTARY_ORIGINAL_ORDER if i in by_id]
        # Fail loud (not silently short) if the bank content ever drifts from the
        # frozen 10-entry set this reconstruction depends on.
        if len(merged) != len(commentary) + len(disclosure):
            raise RuntimeError(
                "GOLDEN_5585_SCOPE_AWAY reconstruction mismatch: expected the frozen "
                f"10-entry id set, got {len(commentary) + len(disclosure)} live entries "
                f"but only matched {len(merged)} against "
                "_FLAGSHIP_FROZEN_COMMENTARY_ORIGINAL_ORDER — the commentary/disclosure "
                "banks changed since this fix was written and need re-verification."
            )
        return merged, []
    return commentary, disclosure


def _load_encouragement_pool(persona_id: str, topic_id: str, repo_root: Path) -> List[dict[str, Any]]:
    out: List[dict[str, Any]] = []
    for sub in ("PERMISSION_GRANT", "PERMISSION"):
        path = repo_root / "atoms" / persona_id / topic_id / sub / "CANONICAL.txt"
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        for i, block in enumerate(re.split(r"(?m)^##\s+\S+\s+v\d+", raw)):
            prose = re.sub(r"(?ms)^---\s*$.*?^---\s*$", "", block).strip()
            if len(prose.split()) < 12:
                continue
            out.append(
                {
                    "accent_id": f"enc_{persona_id}_{topic_id}_{sub.lower()}_v{i:02d}",
                    "body": prose,
                    "secular_safe": True,
                    "topic_keys": [topic_id],
                }
            )
    return out


def _load_authored_bank_entries(bank_dir: str, topic: str, repo_root: Path) -> List[dict[str, Any]]:
    path = ACCENT_BANKS / bank_dir / topic / "entries.yaml"
    if not path.exists():
        return []
    return [e for e in (_load_yaml(path).get("entries") or []) if isinstance(e, dict)]


def _load_reflection_questions_bank(topic: str, repo_root: Path) -> List[dict[str, Any]]:
    _ = repo_root
    return _load_authored_bank_entries("reflection_questions", topic, REPO_ROOT)


def _load_troubleshooting_bank(topic: str, repo_root: Path) -> List[dict[str, Any]]:
    _ = repo_root
    return _load_authored_bank_entries("troubleshooting", topic, REPO_ROOT)


def _parse_atom_blocks(path: Path) -> List[str]:
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"(?m)^##\s+\S+\s+v\d+", raw)
    out: List[str] = []
    for block in blocks:
        prose = re.sub(r"(?ms)^---\s*$.*?^---\s*$", "", block).strip()
        if prose:
            out.append(prose)
    return out


def _load_reflection_question_pool(
    persona_id: str,
    topic_id: str,
    repo_root: Path,
) -> Tuple[List[dict[str, Any]], str]:
    authored = _load_authored_bank_entries("reflection_questions", topic_id, repo_root)
    if authored:
        return authored, "authored_bank"
    out: List[dict[str, Any]] = []
    path = repo_root / "atoms" / persona_id / topic_id / "REFLECTION" / "CANONICAL.txt"
    for i, prose in enumerate(_parse_atom_blocks(path)):
        for match in _QUESTION_RE.finditer(prose):
            question = match.group(1).strip()
            if len(question.split()) < 6:
                continue
            out.append(
                {
                    "accent_id": f"rq_atom_{persona_id}_{topic_id}_v{i:02d}_{len(out):02d}",
                    "question": question,
                    "body": question,
                    "secular_safe": True,
                    "topic_keys": [topic_id],
                    "provenance": "atom_fallback",
                }
            )
        if not _QUESTION_RE.search(prose):
            sentences = re.split(r"(?<=[.!?])\s+", prose)
            if sentences and sentences[-1].strip().endswith("?"):
                question = sentences[-1].strip()
                if len(question.split()) >= 6:
                    out.append(
                        {
                            "accent_id": f"rq_atom_{persona_id}_{topic_id}_v{i:02d}_tail",
                            "question": question,
                            "body": question,
                            "secular_safe": True,
                            "topic_keys": [topic_id],
                            "provenance": "atom_fallback",
                        }
                    )
    return out, "atom_fallback"


def _load_troubleshooting_pool(
    persona_id: str,
    topic_id: str,
    repo_root: Path,
) -> Tuple[List[dict[str, Any]], str]:
    authored = _load_authored_bank_entries("troubleshooting", topic_id, repo_root)
    if authored:
        return authored, "authored_bank"
    out: List[dict[str, Any]] = []
    path = repo_root / "atoms" / persona_id / topic_id / "INTEGRATION" / "CANONICAL.txt"
    for i, prose in enumerate(_parse_atom_blocks(path)):
        for j, match in enumerate(_TROUBLESHOOTING_RE.finditer(prose)):
            body = match.group(1).strip()
            if len(body.split()) < 10:
                continue
            out.append(
                {
                    "accent_id": f"ts_atom_{persona_id}_{topic_id}_v{i:02d}_{j:02d}",
                    "body": body,
                    "secular_safe": True,
                    "topic_keys": [topic_id],
                    "provenance": "atom_fallback",
                }
            )
    return out, "atom_fallback"


def _load_quotes(topic: str, locale_cluster: str, repo_root: Path) -> List[dict[str, Any]]:
    for loc in (locale_cluster, "universal", "en_US"):
        data = _load_yaml(ACCENT_BANKS / "quotes" / topic / f"{loc}.yaml")
        rows = [q for q in (data.get("quotes") or []) if isinstance(q, dict)]
        if rows:
            return rows
    return []


def _topic_match(entry: Mapping[str, Any], topic_id: str) -> bool:
    keys = entry.get("topic_keys") or []
    return not keys or topic_id in keys


def _entry_id(entry: Mapping[str, Any]) -> str:
    return str(
        entry.get("accent_id")
        or entry.get("story_id")
        or entry.get("evidence_id")
        or entry.get("essence_id")
        or entry.get("commentary_id")
        or entry.get("quote_id")
        or entry.get("question_id")
        or entry.get("troubleshooting_id")
        or ""
    )


def _phase_fit_ok(entry: Mapping[str, Any], phase: str) -> bool:
    fit = entry.get("phase_fit")
    if fit is None:
        return True
    normalized = {str(x).strip() for x in fit} if isinstance(fit, list) else {str(fit).strip()}
    if phase in normalized:
        return True
    # Allow adjacent macro-phase matches when banks tag problem/history/... but scorer used early/mid/late.
    if phase in {"early", "mid", "late"}:
        phase_aliases = {
            "early": {"problem", "history"},
            "mid": {"history", "knowledge", "action"},
            "late": {"action", "maintenance"},
        }
        return bool(normalized.intersection(phase_aliases.get(phase, set())))
    return False


def _persona_fit_ok(entry: Mapping[str, Any], persona_id: str) -> bool:
    fit = entry.get("persona_fit")
    if fit is None:
        return True
    normalized = {str(x).strip() for x in fit} if isinstance(fit, list) else {str(fit).strip()}
    return not normalized or persona_id in normalized


def _position_fit_ok(entry: Mapping[str, Any], position: str) -> bool:
    if not _allowed_positions_ok(entry, position):
        return False
    fit = entry.get("position_fit")
    if fit is None:
        return True
    values = fit if isinstance(fit, list) else [fit]
    normalized = {str(v).strip().lower() for v in values}
    joined = " ".join(normalized)
    if "supports pivot" in joined or "pivot" in normalized:
        return position in {"after_PIVOT", "before_STORY"}
    if "supports hook" in joined or "hook" in normalized:
        return position in {"after_HOOK", "before_STORY"}
    if "supports reflection" in joined or "reflection" in normalized:
        return position in {"after_REFLECTION", "before_THREAD"}
    if "supports takeaway" in joined or "takeaway" in normalized:
        return position in {"before_THREAD", "after_INTEGRATION"}
    if position == "before_HOOK" and "opener" in normalized:
        return True
    if position == "before_THREAD" and "closer" in normalized:
        return True
    if position.replace("_", " ").lower() in normalized:
        return True
    return not normalized.intersection({"opener", "closer"})


def _score_chapter_for_class(
    ch: EnrichedChapter,
    accent_class: str,
    *,
    chapter_count: int,
    seed: str,
) -> int:
    slot_types = _chapter_slot_types(ch)
    position = _pick_position(accent_class, slot_types, seed=seed, chapter_number=ch.number)
    if not position:
        return -1
    phase = _chapter_phase(ch.number, chapter_count)
    score = 0
    score += V21_PHASE_WEIGHTS_BY_CLASS.get(accent_class, {}).get(phase, 5)
    role = str(getattr(ch, "role", "") or "").strip().lower()
    score += int(V21_ROLE_WEIGHTS_BY_CLASS.get(accent_class, {}).get(role, 0))
    if accent_class == "QUOTE":
        if position == "before_HOOK" and phase == "early":
            score += 8
        if position == "before_THREAD" and phase == "late":
            score += 8
    score += _deterministic_rank(seed, f"chscore:{accent_class}:{ch.number}") % 5
    return score


def _story_mix_weight_bonus(
    entry: Mapping[str, Any],
    *,
    accent_class: str,
    story_mix_profile_data: Optional[Mapping[str, Any]],
    used_story_types: Optional[Sequence[str]] = None,
) -> int:
    """Apply research story-mix type/emotional weights for EXTERNAL_STORY picks."""
    if accent_class != "EXTERNAL_STORY" or not story_mix_profile_data:
        return 0
    bonus = 0
    type_weights = dict(story_mix_profile_data.get("type_weights") or {})
    emotional_weights = dict(story_mix_profile_data.get("emotional_weights") or {})
    story_type = str(
        entry.get("story_type")
        or entry.get("type")
        or entry.get("external_story_type")
        or ""
    ).strip()
    if story_type and story_type in type_weights:
        bonus += int(round(float(type_weights[story_type]) * 40))
    emotion = str(
        entry.get("emotional_shape")
        or entry.get("emotional_register")
        or entry.get("emotion")
        or ""
    ).strip()
    if emotion and emotion in emotional_weights:
        bonus += int(round(float(emotional_weights[emotion]) * 20))
    # Soft anti-repeat: prefer unused story types when the profile is diverse.
    if used_story_types and story_type:
        repeats = sum(1 for t in used_story_types if t == story_type)
        if repeats:
            bonus -= min(18, repeats * 9)
    return bonus


def _score_entry_for_chapter(
    entry: Mapping[str, Any],
    *,
    accent_class: str,
    topic_id: str,
    locale_cluster: str,
    composite_mode: bool,
    chapter_number: int,
    chapter_count: int,
    position: str,
    book_idea: str,
    book_motif: str,
    seed: str,
    persona_id: str = "",
    story_mix_profile_data: Optional[Mapping[str, Any]] = None,
    used_story_types: Optional[Sequence[str]] = None,
) -> int:
    if not _topic_match(entry, topic_id) or not _locale_fit_ok(entry, locale_cluster):
        return -1
    if not _persona_fit_ok(entry, persona_id):
        return -1
    if not _secular_entry_ok(entry, composite_mode=composite_mode):
        return -1
    body = _entry_body(entry)
    min_words = 6 if accent_class in ("REFLECTION_QUESTION", "QUOTE") else 8
    # CJK-honest length: whitespace tokenization treats a whole Han/kana quote as
    # a single "word", which would reject every localized zh/ja/ko accent. count_words
    # counts each CJK glyph as one unit and is identical to len(text.split()) for
    # whitespace-delimited scripts, so this is not a threshold relaxation.
    if count_words(body) < min_words:
        return -1
    if not _position_fit_ok(entry, position):
        return -1
    book_phase = _book_phase_for_chapter(chapter_number, chapter_count)
    if not _phase_fit_ok(entry, book_phase):
        return -1
    score = 10
    idea_keys = entry.get("book_idea_keys") or entry.get("idea_keys") or []
    if book_idea in idea_keys:
        score += 8
    motif_keys = entry.get("motif_keys") or entry.get("book_motif_keys") or []
    if book_motif in motif_keys:
        score += 6
    doctrine_keys = entry.get("doctrine_keys") or []
    if doctrine_keys:
        score += 3
    score += _story_mix_weight_bonus(
        entry,
        accent_class=accent_class,
        story_mix_profile_data=story_mix_profile_data,
        used_story_types=used_story_types,
    )
    score += _deterministic_rank(seed, f"entry:{accent_class}:ch{chapter_number}:{_entry_id(entry)}") % 7
    return score


def _select_entry_scored(
    pool: Sequence[Mapping[str, Any]],
    *,
    accent_class: str,
    topic_id: str,
    locale_cluster: str,
    composite_mode: bool,
    chapter_number: int,
    chapter_count: int,
    position: str,
    book_idea: str,
    book_motif: str,
    seed: str,
    used_ids: set[str],
    persona_id: str = "",
    story_mix_profile_data: Optional[Mapping[str, Any]] = None,
    used_story_types: Optional[Sequence[str]] = None,
) -> Optional[dict[str, Any]]:
    scored: List[Tuple[int, dict[str, Any]]] = []
    for row in pool:
        aid = _entry_id(row)
        if aid and aid in used_ids:
            continue
        score = _score_entry_for_chapter(
            row,
            accent_class=accent_class,
            topic_id=topic_id,
            locale_cluster=locale_cluster,
            composite_mode=composite_mode,
            chapter_number=chapter_number,
            chapter_count=chapter_count,
            position=position,
            book_idea=book_idea,
            book_motif=book_motif,
            seed=seed,
            persona_id=persona_id,
            story_mix_profile_data=story_mix_profile_data,
            used_story_types=used_story_types,
        )
        if score >= 0:
            scored.append((score, dict(row)))
    if not scored:
        return None
    scored.sort(key=lambda item: (-item[0], _deterministic_rank(seed, f"tie:{_entry_id(item[1])}")))
    return scored[0][1]


def _resolve_quote_text(entry: Mapping[str, Any], *, locale_cluster: str = "en_US") -> str:
    """Pick the quote surface text honoring the render locale.

    For CJK render locales (or when the localized original is itself CJK) render
    the localized ``text`` — the real, verified in-language quote — falling back
    to the English translation only if no localized original exists. For non-CJK
    locales keep the historical ``text_en``-first order so en_US flagship output
    stays byte-identical.
    """
    text_local = str(entry.get("text") or "").strip()
    text_en = str(entry.get("text_en") or "").strip()
    prefer_local = str(locale_cluster or "").lower().startswith(("zh", "ja", "ko")) or has_cjk_script(text_local)
    if prefer_local and text_local:
        return text_local
    if not prefer_local and text_en:
        return text_en
    return text_local or text_en or _entry_body(entry)


def _resolve_body(accent_class: str, entry: Mapping[str, Any], *, position: str, composite_mode: bool, locale_cluster: str = "en_US") -> Tuple[str, str]:
    if accent_class == "CITED_EVIDENCE":
        aid = str(entry.get("evidence_id") or "cited_unknown")
        return aid, _wrap_cited_evidence(
            str(entry.get("claim") or _entry_body(entry)),
            str(entry.get("citation") or ""),
            position=position,
            entry=entry,
        )
    if accent_class == "EXTERNAL_STORY":
        aid = str(entry.get("story_id") or "ext_unknown")
        return aid, _wrap_external_story(str(entry.get("story") or ""), str(entry.get("source") or ""), position=position)
    if accent_class == "WISDOM_ESSENCE":
        reg = entry.get("register_variants") or {}
        sec = reg.get("secular") if isinstance(reg, dict) else {}
        return str(entry.get("essence_id") or "we_unknown"), str((sec or {}).get("body") or _entry_body(entry))
    if accent_class == "AUTHOR_COMMENTARY":
        variants = entry.get("position_variants") or {}
        pv = variants.get(position) if isinstance(variants, dict) else {}
        return str(entry.get("commentary_id") or "ac_unknown"), str((pv or {}).get("body") or _entry_body(entry))
    if accent_class == "AUTHOR_DISCLOSURE":
        variants = entry.get("position_variants") or {}
        pv = variants.get(position) if isinstance(variants, dict) else {}
        return str(entry.get("disclosure_id") or "ad_unknown"), str((pv or {}).get("body") or _entry_body(entry))
    if accent_class == "ENCOURAGEMENT":
        return str(entry.get("accent_id") or "enc_unknown"), _wrap_encouragement(_entry_body(entry), position=position)
    if accent_class == "REFLECTION_QUESTION":
        return str(entry.get("accent_id") or entry.get("question_id") or "rq_unknown"), _wrap_reflection_question(
            str(entry.get("question") or _entry_body(entry)),
            position=position,
        )
    if accent_class == "TROUBLESHOOTING":
        return str(entry.get("accent_id") or entry.get("troubleshooting_id") or "ts_unknown"), _wrap_troubleshooting(
            _entry_body(entry),
            position=position,
        )
    if accent_class == "QUOTE":
        text = _resolve_quote_text(entry, locale_cluster=locale_cluster)
        return str(entry.get("quote_id") or "quote_unknown"), _wrap_quote(
            text,
            str(entry.get("author") or ""),
            str(entry.get("primary_source") or entry.get("source") or ""),
            position=position,
        )
    return str(entry.get("accent_id") or "accent_unknown"), _entry_body(entry)


def _build_pools_with_provenance(
    *,
    persona_id: str,
    topic_id: str,
    author_id: str,
    locale_cluster: str,
    repo_root: Path,
) -> Tuple[Dict[str, List[dict[str, Any]]], Dict[str, str]]:
    rq_pool, rq_prov = _load_reflection_question_pool(persona_id, topic_id, repo_root)
    ts_pool, ts_prov = _load_troubleshooting_pool(persona_id, topic_id, repo_root)
    commentary_pool, disclosure_pool = _author_commentary_and_disclosure_pools(
        persona_id, topic_id, author_id or "ravi_chandra", locale_cluster, repo_root
    )
    pools = {
        "EXTERNAL_STORY": _load_external_stories(topic_id, locale_cluster, repo_root),
        "CITED_EVIDENCE": _load_cited_evidence(topic_id, repo_root),
        "WISDOM_ESSENCE": _load_wisdom_essence(topic_id, repo_root),
        "AUTHOR_COMMENTARY": commentary_pool,
        "AUTHOR_DISCLOSURE": disclosure_pool,
        "ENCOURAGEMENT": _load_encouragement_pool(persona_id, topic_id, repo_root),
        "REFLECTION_QUESTION": rq_pool,
        "TROUBLESHOOTING": ts_pool,
        "QUOTE": _load_quotes(topic_id, locale_cluster, repo_root),
    }
    provenance = {
        "REFLECTION_QUESTION": rq_prov,
        "TROUBLESHOOTING": ts_prov,
        "EXTERNAL_STORY": "authored_bank" if pools["EXTERNAL_STORY"] else "missing",
        "CITED_EVIDENCE": "authored_bank" if pools["CITED_EVIDENCE"] else "missing",
        "WISDOM_ESSENCE": "authored_bank" if pools["WISDOM_ESSENCE"] else "missing",
        "AUTHOR_COMMENTARY": "authored_bank" if pools["AUTHOR_COMMENTARY"] else "missing",
        "AUTHOR_DISCLOSURE": "authored_bank" if pools["AUTHOR_DISCLOSURE"] else "missing",
        "ENCOURAGEMENT": "atom_pool" if pools["ENCOURAGEMENT"] else "missing",
        "QUOTE": "authored_bank" if pools["QUOTE"] else "missing",
    }
    return pools, provenance


def _assignment_counts(flat_rows: Sequence[Mapping[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {cls: 0 for cls in ALL_ACCENT_CLASSES}
    for row in flat_rows:
        cls = str(row.get("class") or "")
        if cls in counts:
            counts[cls] += 1
    return counts


def _capability_gaps(
    accent_budget: Mapping[str, int],
    pools: Mapping[str, Sequence[Mapping[str, Any]]],
) -> Dict[str, str]:
    gaps: Dict[str, str] = {}
    for cls, cap in accent_budget.items():
        if int(cap) <= 0:
            continue
        if not pools.get(cls):
            gaps[cls] = "no_supply_pool"
    return gaps


def _supported_underfilled_budget_by_class(
    accent_budget: Mapping[str, int],
    counts: Mapping[str, int],
    pools: Mapping[str, Sequence[Mapping[str, Any]]],
) -> Dict[str, int]:
    underfilled: Dict[str, int] = {}
    for cls, cap in accent_budget.items():
        cap_i = int(cap)
        if cap_i <= 0:
            continue
        assigned = int(counts.get(cls, 0))
        if assigned < cap_i and pools.get(cls):
            underfilled[cls] = cap_i - assigned
    return underfilled


def preflight_accent_supply(
    accent_budget: Mapping[str, int],
    pools: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    locale_cluster: str = "en_US",
) -> List[str]:
    """Precise, early missing-supply blockers for required accent floors.

    For every accent class carrying a positive budget floor whose supply pool is
    EMPTY for this locale, emit an actionable line naming the class, the exact
    shortfall, and the reason. Surfacing this at plan time converts the confusing
    late ``[PRODUCTION GATE] Supported accent underfill`` stop — which only fires
    when a pool exists but was left unfilled — into an early, precise signal for
    the genuinely-missing-supply case (no bank authored/authorized for this
    topic+locale).
    """
    blockers: List[str] = []
    for cls in sorted(accent_budget):
        cap_i = int(accent_budget.get(cls, 0))
        if cap_i <= 0:
            continue
        if not pools.get(cls):
            blockers.append(
                f"{cls}: need {cap_i}, 0 available — no supply pool for "
                f"locale '{locale_cluster}'; author or authorize a {cls} bank for "
                f"this topic+locale before requiring it in the accent budget"
            )
    return blockers


def _build_strategy_report(
    *,
    accent_budget: Mapping[str, int],
    flat_rows: Sequence[Mapping[str, Any]],
    pools: Mapping[str, Sequence[Mapping[str, Any]]],
    supply_provenance: Mapping[str, str],
    story_mix_profile: str,
    brand_profile_name: str,
    book_idea: str,
    book_motif: str,
    share_cap: float,
    max_accents_per_chapter: int,
    chapter_count: int,
    persona_id: str,
    topic_id: str,
    locale_cluster: str = "en_US",
    repo_root: Path = REPO_ROOT,
) -> Dict[str, Any]:
    counts = _assignment_counts(flat_rows)
    capability_gaps = _capability_gaps(accent_budget, pools)
    underfilled = _supported_underfilled_budget_by_class(accent_budget, counts, pools)
    supply_preflight_blockers = preflight_accent_supply(
        accent_budget, pools, locale_cluster=locale_cluster
    )
    chapters_with = {int(r.get("chapter") or 0) for r in flat_rows}
    mix_data = _story_mix_profile_data(story_mix_profile, repo_root)
    assignment_diagnostics: Dict[str, Any] = {}
    for cls in ACCENT_SELECTION_ORDER:
        if cls not in accent_budget:
            continue
        assignment_diagnostics[cls] = {
            "budget": int(accent_budget.get(cls, 0)),
            "assigned": int(counts.get(cls, 0)),
            "pool_size": len(pools.get(cls) or []),
            "supply_provenance": supply_provenance.get(cls, "missing"),
            "underfilled": int(underfilled.get(cls, 0)),
            "capability_gap": cls in capability_gaps,
        }
    capability_by_class = {
        cls: ("available" if pools.get(cls) else "missing_topic_supply")
        for cls in ALL_ACCENT_CLASSES
        if int(accent_budget.get(cls, 0)) > 0
    }
    v21_summary = build_enhancement_contract_v21_summary(
        accent_budget=accent_budget,
        flat_rows=flat_rows,
        chapter_count=chapter_count,
        story_mix_profile=story_mix_profile,
        max_accents_per_chapter=max_accents_per_chapter,
        persona_id=persona_id,
        topic_id=topic_id,
    )
    return {
        "strategy_profile": story_mix_profile,
        "style_family": mix_data.get("strategy_family") or story_mix_profile,
        "enrichment_strategy_profile": story_mix_profile,
        "brand_accent_profile": brand_profile_name,
        "book_idea": book_idea,
        "book_motif": book_motif,
        "requested_budget": dict(accent_budget),
        "accent_budget": dict(accent_budget),
        "assignment_counts": counts,
        "fulfilled_counts": dict(counts),
        "capability_by_class": capability_by_class,
        "assignments": list(flat_rows),
        "supply_provenance_by_class": dict(supply_provenance),
        "assignment_diagnostics_by_class": assignment_diagnostics,
        "supported_underfilled_budget_by_class": underfilled,
        "underfilled_budget_by_class": {
            cls: max(0, int(accent_budget.get(cls, 0)) - int(counts.get(cls, 0)))
            for cls in ALL_ACCENT_CLASSES
            if int(accent_budget.get(cls, 0)) > int(counts.get(cls, 0))
        },
        "capability_gaps": capability_gaps,
        "accent_supply_preflight_blockers": supply_preflight_blockers,
        "share_cap": share_cap,
        "max_accents_per_chapter": max_accents_per_chapter,
        "chapters_with_accents": sorted(chapters_with),
        "chapter_count": chapter_count,
        "accent_chapter_share": len(chapters_with) / max(1, chapter_count),
        "enhancement_contract_v21": v21_summary,
    }


def _build_alignment_report(
    *,
    story_mix_profile: str,
    accent_budget: Mapping[str, int],
    flat_rows: Sequence[Mapping[str, Any]],
    book_idea: str,
    book_motif: str,
    strategy_report: Mapping[str, Any],
    repo_root: Path,
) -> Dict[str, Any]:
    signatures_path = repo_root / "config" / "authoring" / "bestseller_enrichment_signatures.yaml"
    data = _load_yaml(signatures_path)
    exemplar_config_missing = not signatures_path.exists()
    profile_exemplars = ((data.get("profiles") or {}).get(story_mix_profile) or {}).get("exemplars") or []
    counts = _assignment_counts(flat_rows)
    chapters_with = {int(r.get("chapter") or 0) for r in flat_rows}
    chapter_count = max(chapters_with) if chapters_with else 0
    actual_share = len(chapters_with) / max(1, chapter_count)

    best_match: Optional[dict[str, Any]] = None
    best_score = -1
    for ex in profile_exemplars:
        if not isinstance(ex, dict):
            continue
        score = 0
        if ex.get("book_idea") == book_idea:
            score += 5
        if ex.get("book_motif") == book_motif:
            score += 5
        ex_counts = ex.get("accent_counts") or {}
        for cls, target in ex_counts.items():
            delta = abs(int(counts.get(cls, 0)) - int(target))
            score += max(0, 5 - delta)
        ex_share = float(ex.get("max_accent_chapter_share") or 0)
        score += max(0, 5 - int(abs(actual_share - ex_share) * 10))
        if score > best_score:
            best_score = score
            best_match = ex

    supported_underfilled = dict(strategy_report.get("supported_underfilled_budget_by_class") or {})
    capability_gaps = dict(strategy_report.get("capability_gaps") or {})
    underfilled_all = dict(strategy_report.get("underfilled_budget_by_class") or {})
    status = "PASS"
    if supported_underfilled:
        status = "FAIL"
    elif exemplar_config_missing or not profile_exemplars:
        status = "WARN"
    elif capability_gaps or any(v > 0 for v in underfilled_all.values()):
        status = "WARN"

    return {
        "strategy_profile": story_mix_profile,
        "story_mix_profile": story_mix_profile,
        "status": status,
        "book_idea": book_idea,
        "book_motif": book_motif,
        "requested_budget": dict(accent_budget),
        "fulfilled_counts": dict(counts),
        "underfilled_budget_by_class": dict(strategy_report.get("underfilled_budget_by_class") or {}),
        "supported_underfilled_budget_by_class": supported_underfilled,
        "capability_gaps": {
            cls: int(accent_budget.get(cls, 0))
            for cls, reason in capability_gaps.items()
        },
        "supply_provenance_by_class": dict(strategy_report.get("supply_provenance_by_class") or {}),
        "assignment_diagnostics_by_class": dict(strategy_report.get("assignment_diagnostics_by_class") or {}),
        "actual_accent_counts": counts,
        "actual_accent_chapter_share": actual_share,
        "chapters_with_accents": sorted(chapters_with),
        "chapter_share": actual_share,
        "exemplar_config_present": not exemplar_config_missing,
        "exemplar_config_path": str(signatures_path.relative_to(repo_root)) if not exemplar_config_missing else None,
        "exemplar_pool_size": len(profile_exemplars),
        "nearest_exemplar_id": (best_match or {}).get("exemplar_id"),
        "nearest_exemplar_label": (best_match or {}).get("label"),
        "nearest_exemplar_score": best_score if best_match else 0,
        "budget_alignment_delta": {
            cls: int(counts.get(cls, 0)) - int((best_match or {}).get("accent_counts", {}).get(cls, accent_budget.get(cls, 0)))
            for cls in ALL_ACCENT_CLASSES
            if int(accent_budget.get(cls, 0)) > 0 or int(counts.get(cls, 0)) > 0
        },
        "warnings": (
            ["bestseller_enrichment_signatures.yaml missing — alignment is budget-fill only, not exemplar match"]
            if exemplar_config_missing
            else (
                [f"no exemplars configured for story_mix_profile={story_mix_profile}"]
                if not profile_exemplars
                else []
            )
        ),
        "enhancement_contract_v21": dict(strategy_report.get("enhancement_contract_v21") or {}),
    }


def _apply_share_cap_with_refill(
    flat_rows: List[Dict[str, Any]],
    chapter_assignments: Dict[int, List[AccentBeat]],
    *,
    accent_budget: Mapping[str, int],
    pools: Mapping[str, Sequence[Mapping[str, Any]]],
    enriched: EnrichedBook,
    locale_cluster: str,
    composite_mode: bool,
    book_idea: str,
    book_motif: str,
    seed: str,
    share_cap: float,
    max_accents_per_chapter: int,
    topic_id: str,
    used_ids: set[str],
    supply_provenance: Optional[Mapping[str, str]] = None,
    story_mix_profile_data: Optional[Mapping[str, Any]] = None,
) -> Tuple[List[Dict[str, Any]], Dict[int, List[AccentBeat]]]:
    total_chapters = max(1, len(enriched.chapters))
    if share_cap <= 0 or not flat_rows:
        return flat_rows, chapter_assignments

    max_chapters = max(1, int(total_chapters * share_cap))
    beats_by_id = {b.accent_id: b for beats in chapter_assignments.values() for b in beats}
    trim_order = list(reversed(ACCENT_SELECTION_ORDER))
    provenance_map = dict(supply_provenance or {})
    used_story_types: List[str] = []
    for row in flat_rows:
        if row.get("class") == "EXTERNAL_STORY":
            st = str((row.get("keys") or {}).get("story_type") or "")
            if st:
                used_story_types.append(st)

    def _chapter_count(rows: List[Dict[str, Any]]) -> int:
        return len({int(r["chapter"]) for r in rows})

    working_rows = list(flat_rows)
    while working_rows and _chapter_count(working_rows) > max_chapters:
        removed = False
        for cls in trim_order:
            for i in range(len(working_rows) - 1, -1, -1):
                if working_rows[i]["class"] == cls:
                    working_rows.pop(i)
                    removed = True
                    break
            if removed:
                break
        if not removed:
            working_rows.pop()

    rebuilt: Dict[int, List[AccentBeat]] = {}
    for row in working_rows:
        beat = beats_by_id.get(str(row["accent_id"]))
        if beat:
            rebuilt.setdefault(int(row["chapter"]), []).append(beat)

    counts = _assignment_counts(working_rows)
    chapters_used = {int(r["chapter"]) for r in working_rows}

    for accent_class in ACCENT_SELECTION_ORDER:
        need = int(accent_budget.get(accent_class, 0)) - int(counts.get(accent_class, 0))
        if need <= 0 or not pools.get(accent_class):
            continue
        candidates = [
            ch.number
            for ch in enriched.chapters
            if _chapter_can_host_accents(ch)
            and _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch.number)
        ]
        ranked = sorted(
            candidates,
            key=lambda ch: _score_chapter_for_class(
                next(c for c in enriched.chapters if c.number == ch),
                accent_class,
                chapter_count=total_chapters,
                seed=seed,
            ),
            reverse=True,
        )
        for ch_num in ranked:
            if need <= 0:
                break
            if ch_num in chapters_used and len(rebuilt.get(ch_num, [])) >= max_accents_per_chapter:
                continue
            if any(r["class"] == accent_class and int(r["chapter"]) == ch_num for r in working_rows):
                continue
            if len(chapters_used) >= max_chapters and ch_num not in chapters_used:
                continue
            ch = next((c for c in enriched.chapters if c.number == ch_num), None)
            if ch is None or not _chapter_can_host_accents(ch):
                continue
            position = _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch_num)
            if not position:
                continue
            entry = _select_entry_scored(
                pools[accent_class],
                accent_class=accent_class,
                topic_id=topic_id,
                locale_cluster=locale_cluster,
                composite_mode=composite_mode,
                chapter_number=ch_num,
                chapter_count=total_chapters,
                position=position,
                book_idea=book_idea,
                book_motif=book_motif,
                seed=seed,
                used_ids=used_ids,
                persona_id=enriched.persona_id,
                story_mix_profile_data=story_mix_profile_data,
                used_story_types=used_story_types,
            )
            if not entry:
                continue
            accent_id, body = _resolve_body(accent_class, entry, position=position, composite_mode=composite_mode, locale_cluster=locale_cluster)
            if not body or not _composite_body_safe(body, composite_mode=composite_mode):
                continue
            used_ids.add(accent_id)
            prov = provenance_map.get(accent_class) or entry.get("provenance") or "authored_bank"
            if accent_class in ("REFLECTION_QUESTION", "TROUBLESHOOTING"):
                prov = provenance_map.get(accent_class) or entry.get("provenance") or "authored_bank"
            beat_keys = {
                "topic_id": topic_id,
                "persona_id": enriched.persona_id,
                "supply_provenance": prov,
                "surface_bucket": accent_class_bucket(accent_class),
                "count_unit": count_unit_for_surface(accent_class),
                "preferred_positions": preferred_positions_for_surface(accent_class),
                "disallowed_positions": disallowed_positions_for_surface(accent_class),
            }
            story_type = str(entry.get("story_type") or entry.get("type") or entry.get("external_story_type") or "")
            if story_type:
                beat_keys["story_type"] = story_type
                used_story_types.append(story_type)
            truth_metadata = _truth_metadata_for_entry(accent_class, entry)
            if truth_metadata:
                beat_keys["truth_metadata"] = truth_metadata
            if accent_class == "EXTERNAL_STORY":
                story_function, story_function_source = _external_story_function(entry)
                beat_keys["story_function"] = story_function
                beat_keys["story_function_source"] = story_function_source
            beat = AccentBeat(
                accent_class,
                accent_id,
                position,
                body,
                beat_keys,
            )
            rebuilt.setdefault(ch_num, []).append(beat)
            working_rows.append(
                {
                    "chapter": ch_num,
                    "class": accent_class,
                    "accent_id": accent_id,
                    "position": position,
                    "supply_source": str(beat.keys.get("supply_provenance") or "authored_bank"),
                    "keys": dict(beat.keys),
                }
            )
            chapters_used.add(ch_num)
            counts[accent_class] = counts.get(accent_class, 0) + 1
            need -= 1

    return working_rows, rebuilt


def _select_entry(
    pool: Sequence[Mapping[str, Any]],
    *,
    accent_class: str,
    topic_id: str,
    locale_cluster: str,
    composite_mode: bool,
    seed: str,
    chapter_number: int,
    position: str,
    used_ids: set[str],
) -> Optional[dict[str, Any]]:
    """Legacy v1 picker — preserved for flagship golden parity when contract-v1 is off."""
    candidates: List[dict[str, Any]] = []
    for row in pool:
        if not _topic_match(row, topic_id) or not _locale_fit_ok(row, locale_cluster) or not _secular_entry_ok(row, composite_mode=composite_mode):
            continue
        if not _position_fit_ok(row, position):
            continue
        aid = _entry_id(row)
        if aid and aid in used_ids:
            continue
        if len(_entry_body(row).split()) < 8:
            continue
        candidates.append(dict(row))
    if not candidates:
        return None
    return candidates[_deterministic_rank(seed, f"pick:{accent_class}:ch{chapter_number}") % len(candidates)]


def _plan_accent_beats_for_book_legacy(
    enriched: EnrichedBook,
    *,
    brand_id: str = "phoenix",
    author_id: Optional[str] = None,
    seed: str = "",
    locale: Optional[str] = None,
    teacher_mode: bool = False,
    repo_root: Path = REPO_ROOT,
) -> AccentPlanResult:
    """Pre-contract-v1 accent planner — byte-stable with flagship golden renders."""
    persona_id, topic_id = enriched.persona_id, enriched.topic
    accent_budget, brand_profile_name, share_cap = resolve_accent_budget(
        brand_id,
        persona_id=persona_id,
        topic_id=topic_id,
        enrichment_contract_v1=False,
        repo_root=repo_root,
    )
    story_mix_profile = resolve_story_mix_profile(
        brand_id,
        persona_id=persona_id,
        topic_id=topic_id,
        repo_root=repo_root,
    )
    book_idea = _book_idea(enriched.spine_context)
    book_motif = _book_motif(enriched.spine_context)
    empty_report = {
        "enrichment_strategy_profile": story_mix_profile,
        "brand_accent_profile": brand_profile_name,
        "book_idea": book_idea,
        "book_motif": book_motif,
        "supported_underfilled_budget_by_class": {},
        "capability_gaps": {},
        "supply_provenance_by_class": {},
        "assignment_diagnostics_by_class": {},
        "legacy_planner": True,
    }
    if sum(accent_budget.values()) <= 0:
        return AccentPlanResult(
            accent_budget=accent_budget,
            story_mix_profile=story_mix_profile,
            flat_rows=[],
            signature=compute_accent_signature([], accent_budget=accent_budget),
            chapter_assignments={},
            strategy_report=empty_report,
            alignment_report={"status": "PASS", "supported_underfilled_budget_by_class": {}, "legacy_planner": True},
        )

    locale_cluster = locale_to_cluster(locale or getattr(enriched, "locale", None))
    composite_mode = not teacher_mode and not enriched.teacher_id
    _legacy_commentary_pool, _legacy_disclosure_pool = _author_commentary_and_disclosure_pools(
        persona_id, topic_id, author_id or "ravi_chandra", locale_cluster, repo_root
    )
    pools = {
        "EXTERNAL_STORY": _load_external_stories(topic_id, locale_cluster, repo_root),
        "CITED_EVIDENCE": _load_cited_evidence(topic_id, repo_root),
        "WISDOM_ESSENCE": _load_wisdom_essence(topic_id, repo_root),
        "AUTHOR_COMMENTARY": _legacy_commentary_pool,
        "AUTHOR_DISCLOSURE": _legacy_disclosure_pool,
        "ENCOURAGEMENT": _load_encouragement_pool(persona_id, topic_id, repo_root),
    }

    used_ids: set[str] = set()
    chapter_assignments: Dict[int, List[AccentBeat]] = {}
    flat_rows: List[Dict[str, Any]] = []
    anchor_chapters: List[int] = []

    for accent_class, budget in accent_budget.items():
        if budget <= 0 or not pools.get(accent_class):
            continue
        candidates = [
            ch.number
            for ch in enriched.chapters
            if _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch.number)
        ]
        prefer = [c for c in candidates if c in anchor_chapters]
        pick_from = prefer if prefer else candidates
        picked = _spread_chapters(pick_from, budget, seed, accent_class)
        if not picked and candidates:
            picked = _spread_chapters(candidates, budget, seed, accent_class)
        for ch_num in picked:
            ch = next((c for c in enriched.chapters if c.number == ch_num), None)
            if ch is None:
                continue
            if any(b.class_ == accent_class for b in chapter_assignments.get(ch_num, [])):
                continue
            position = _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch_num)
            if not position:
                continue
            entry = _select_entry(
                pools[accent_class],
                accent_class=accent_class,
                topic_id=topic_id,
                locale_cluster=locale_cluster,
                composite_mode=composite_mode,
                seed=seed,
                chapter_number=ch_num,
                position=position,
                used_ids=used_ids,
            )
            if not entry:
                continue
            accent_id, body = _resolve_body(accent_class, entry, position=position, composite_mode=composite_mode, locale_cluster=locale_cluster)
            if not body or not _composite_body_safe(body, composite_mode=composite_mode):
                continue
            used_ids.add(accent_id)
            beat = AccentBeat(accent_class, accent_id, position, body, {"topic_id": topic_id, "persona_id": persona_id})
            chapter_assignments.setdefault(ch_num, []).append(beat)
            flat_rows.append(
                {
                    "chapter": ch_num,
                    "class": accent_class,
                    "accent_id": accent_id,
                    "position": position,
                    "keys": dict(beat.keys),
                }
            )
            if ch_num not in anchor_chapters:
                anchor_chapters.append(ch_num)

    total_chapters = max(1, len(enriched.chapters))
    if share_cap > 0 and flat_rows:
        max_chapters = max(1, int(total_chapters * share_cap))
        trim_order = ["WISDOM_ESSENCE", "AUTHOR_COMMENTARY", "ENCOURAGEMENT", "CITED_EVIDENCE", "EXTERNAL_STORY"]
        beats_by_id = {b.accent_id: b for beats in chapter_assignments.values() for b in beats}

        def _chapter_count(rows: List[Dict[str, Any]]) -> int:
            return len({int(r["chapter"]) for r in rows})

        while flat_rows and _chapter_count(flat_rows) > max_chapters:
            removed = False
            for cls in trim_order:
                for i in range(len(flat_rows) - 1, -1, -1):
                    if flat_rows[i]["class"] == cls:
                        flat_rows.pop(i)
                        removed = True
                        break
                if removed:
                    break
            if not removed:
                flat_rows.pop()
        chapter_assignments = {}
        for row in flat_rows:
            beat = beats_by_id.get(str(row["accent_id"]))
            if beat:
                chapter_assignments.setdefault(int(row["chapter"]), []).append(beat)

    signature = compute_accent_signature(flat_rows, accent_budget=accent_budget)
    strategy_report = dict(empty_report)
    strategy_report["accent_budget"] = dict(accent_budget)
    strategy_report["assignment_counts"] = _assignment_counts(flat_rows)
    alignment_report = {
        "status": "PASS",
        "story_mix_profile": story_mix_profile,
        "book_idea": book_idea,
        "book_motif": book_motif,
        "supported_underfilled_budget_by_class": {},
        "legacy_planner": True,
    }
    return AccentPlanResult(
        accent_budget=accent_budget,
        story_mix_profile=story_mix_profile,
        flat_rows=flat_rows,
        signature=signature,
        chapter_assignments=chapter_assignments,
        strategy_report=strategy_report,
        alignment_report=alignment_report,
    )


def plan_accent_beats_for_book(
    enriched: EnrichedBook,
    *,
    brand_id: str = "phoenix",
    author_id: Optional[str] = None,
    seed: str = "",
    locale: Optional[str] = None,
    teacher_mode: bool = False,
    repo_root: Path = REPO_ROOT,
) -> AccentPlanResult:
    if not enrichment_contract_v1_enabled(enriched.spine_context):
        return _plan_accent_beats_for_book_legacy(
            enriched,
            brand_id=brand_id,
            author_id=author_id,
            seed=seed,
            locale=locale,
            teacher_mode=teacher_mode,
            repo_root=repo_root,
        )
    persona_id, topic_id = enriched.persona_id, enriched.topic
    _contract_v1 = enrichment_contract_v1_enabled(enriched.spine_context)
    accent_budget, brand_profile_name, share_cap = resolve_accent_budget(
        brand_id,
        persona_id=persona_id,
        topic_id=topic_id,
        enrichment_contract_v1=_contract_v1,
        repo_root=repo_root,
    )
    story_mix_profile = resolve_story_mix_profile(
        brand_id,
        persona_id=persona_id,
        topic_id=topic_id,
        repo_root=repo_root,
    )
    mix_profile = _story_mix_profile_data(story_mix_profile, repo_root)
    max_accents_per_chapter = int(mix_profile.get("max_accents_per_chapter") or 2)
    book_idea = _book_idea(enriched.spine_context)
    book_motif = _book_motif(enriched.spine_context)

    empty_report = {
        "enrichment_strategy_profile": story_mix_profile,
        "brand_accent_profile": brand_profile_name,
        "book_idea": book_idea,
        "book_motif": book_motif,
        "supported_underfilled_budget_by_class": {},
        "capability_gaps": {},
        "supply_provenance_by_class": {},
        "assignment_diagnostics_by_class": {},
    }
    if sum(accent_budget.values()) <= 0:
        return AccentPlanResult(
            accent_budget=accent_budget,
            story_mix_profile=story_mix_profile,
            flat_rows=[],
            signature=compute_accent_signature([], accent_budget=accent_budget),
            chapter_assignments={},
            strategy_report=empty_report,
            alignment_report=_build_alignment_report(
                story_mix_profile=story_mix_profile,
                accent_budget=accent_budget,
                flat_rows=[],
                book_idea=book_idea,
                book_motif=book_motif,
                strategy_report=empty_report,
                repo_root=repo_root,
            ),
        )

    locale_cluster = locale_to_cluster(locale or getattr(enriched, "locale", None))
    composite_mode = not teacher_mode and not enriched.teacher_id
    pools, supply_provenance = _build_pools_with_provenance(
        persona_id=persona_id,
        topic_id=topic_id,
        author_id=author_id or "ravi_chandra",
        locale_cluster=locale_cluster,
        repo_root=repo_root,
    )

    used_ids: set[str] = set()
    chapter_assignments: Dict[int, List[AccentBeat]] = {}
    flat_rows: List[Dict[str, Any]] = []
    total_chapters = max(1, len(enriched.chapters))
    used_story_types: List[str] = []

    for accent_class in ACCENT_SELECTION_ORDER:
        budget = int(accent_budget.get(accent_class, 0))
        if budget <= 0 or not pools.get(accent_class):
            continue
        candidates = [
            ch.number
            for ch in enriched.chapters
            if _chapter_can_host_accents(ch)
            and _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch.number)
        ]
        ranked = sorted(
            candidates,
            key=lambda ch: _score_chapter_for_class(
                next(c for c in enriched.chapters if c.number == ch),
                accent_class,
                chapter_count=total_chapters,
                seed=seed,
            ),
            reverse=True,
        )
        picked = _spread_chapters(ranked, budget, seed, accent_class)
        for ch_num in picked:
            ch = next((c for c in enriched.chapters if c.number == ch_num), None)
            if ch is None:
                continue
            if not _chapter_can_host_accents(ch):
                continue
            if any(b.class_ == accent_class for b in chapter_assignments.get(ch_num, [])):
                continue
            if len(chapter_assignments.get(ch_num, [])) >= max_accents_per_chapter:
                continue
            position = _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch_num)
            if not position:
                continue
            entry = _select_entry_scored(
                pools[accent_class],
                accent_class=accent_class,
                topic_id=topic_id,
                locale_cluster=locale_cluster,
                composite_mode=composite_mode,
                chapter_number=ch_num,
                chapter_count=total_chapters,
                position=position,
                book_idea=book_idea,
                book_motif=book_motif,
                seed=seed,
                used_ids=used_ids,
                persona_id=persona_id,
                story_mix_profile_data=mix_profile,
                used_story_types=used_story_types,
            )
            if not entry:
                continue
            accent_id, body = _resolve_body(accent_class, entry, position=position, composite_mode=composite_mode, locale_cluster=locale_cluster)
            if not body or not _composite_body_safe(body, composite_mode=composite_mode):
                continue
            used_ids.add(accent_id)
            prov = supply_provenance.get(accent_class, "authored_bank")
            if accent_class in ("REFLECTION_QUESTION", "TROUBLESHOOTING"):
                prov = supply_provenance.get(accent_class, entry.get("provenance") or "authored_bank")
            beat_keys = {
                "topic_id": topic_id,
                "persona_id": persona_id,
                "supply_provenance": prov,
                "surface_bucket": accent_class_bucket(accent_class),
                "count_unit": count_unit_for_surface(accent_class),
                "preferred_positions": preferred_positions_for_surface(accent_class),
                "disallowed_positions": disallowed_positions_for_surface(accent_class),
            }
            story_type = str(entry.get("story_type") or entry.get("type") or entry.get("external_story_type") or "")
            if story_type:
                beat_keys["story_type"] = story_type
                used_story_types.append(story_type)
            truth_metadata = _truth_metadata_for_entry(accent_class, entry)
            if truth_metadata:
                beat_keys["truth_metadata"] = truth_metadata
            if accent_class == "EXTERNAL_STORY":
                story_function, story_function_source = _external_story_function(entry)
                beat_keys["story_function"] = story_function
                beat_keys["story_function_source"] = story_function_source
            beat = AccentBeat(
                accent_class,
                accent_id,
                position,
                body,
                beat_keys,
            )
            chapter_assignments.setdefault(ch_num, []).append(beat)
            flat_rows.append(
                {
                    "chapter": ch_num,
                    "class": accent_class,
                    "accent_id": accent_id,
                    "position": position,
                    "supply_source": prov,
                    "keys": dict(beat.keys),
                }
            )

    flat_rows, chapter_assignments = _apply_share_cap_with_refill(
        flat_rows,
        chapter_assignments,
        accent_budget=accent_budget,
        pools=pools,
        enriched=enriched,
        locale_cluster=locale_cluster,
        composite_mode=composite_mode,
        book_idea=book_idea,
        book_motif=book_motif,
        seed=seed,
        share_cap=share_cap,
        max_accents_per_chapter=max_accents_per_chapter,
        topic_id=topic_id,
        used_ids=used_ids,
        supply_provenance=supply_provenance,
        story_mix_profile_data=mix_profile,
    )

    signature = compute_accent_signature(flat_rows, accent_budget=accent_budget)
    strategy_report = _build_strategy_report(
        accent_budget=accent_budget,
        flat_rows=flat_rows,
        pools=pools,
        supply_provenance=supply_provenance,
        story_mix_profile=story_mix_profile,
        brand_profile_name=brand_profile_name,
        book_idea=book_idea,
        book_motif=book_motif,
        share_cap=share_cap,
        max_accents_per_chapter=max_accents_per_chapter,
        chapter_count=total_chapters,
        persona_id=persona_id,
        topic_id=topic_id,
        locale_cluster=locale_cluster,
        repo_root=repo_root,
    )
    alignment_report = _build_alignment_report(
        story_mix_profile=story_mix_profile,
        accent_budget=accent_budget,
        flat_rows=flat_rows,
        book_idea=book_idea,
        book_motif=book_motif,
        strategy_report=strategy_report,
        repo_root=repo_root,
    )
    return AccentPlanResult(
        accent_budget=accent_budget,
        story_mix_profile=story_mix_profile,
        flat_rows=flat_rows,
        signature=signature,
        chapter_assignments=chapter_assignments,
        strategy_report=strategy_report,
        alignment_report=alignment_report,
    )


def attach_accent_plan(
    enriched: EnrichedBook,
    *,
    brand_id: str = "phoenix",
    author_id: Optional[str] = None,
    seed: str = "",
    locale: Optional[str] = None,
    teacher_mode: bool = False,
    repo_root: Path = REPO_ROOT,
) -> EnrichedBook:
    plan = plan_accent_beats_for_book(
        enriched,
        brand_id=brand_id,
        author_id=author_id,
        seed=seed,
        locale=locale,
        teacher_mode=teacher_mode,
        repo_root=repo_root,
    )
    new_chapters = []
    for ch in enriched.chapters:
        beats = plan.chapter_assignments.get(ch.number, [])
        new_chapters.append(
            replace(
                ch,
                accent_beats=[b.to_plan_dict() for b in beats],
                accent_bodies={b.accent_id: b.body for b in beats},
            )
        )
    spine_context = dict(enriched.spine_context or {})
    spine_context.update(
        {
            "accent_budget": dict(plan.accent_budget),
            "accent_signature": plan.signature,
            "story_mix_profile": plan.story_mix_profile,
            "accent_assignments": list(plan.flat_rows),
            "enhancement_contract_v21": dict(
                (plan.strategy_report.get("enhancement_contract_v21") or {})
            ),
            "brand_id": brand_id,
            "book_idea": plan.strategy_report.get("book_idea"),
            "book_motif": plan.strategy_report.get("book_motif"),
        }
    )
    audit = dict(enriched.enrichment_audit or {})
    audit["accent_planner"] = {
        "accent_budget": dict(plan.accent_budget),
        "accent_signature": plan.signature,
        "story_mix_profile": plan.story_mix_profile,
        "assignment_count": len(plan.flat_rows),
        "enhancement_contract_v21": dict(
            (plan.strategy_report.get("enhancement_contract_v21") or {})
        ),
    }
    audit["enrichment_strategy_report"] = dict(plan.strategy_report)
    audit["bestseller_alignment_report"] = dict(plan.alignment_report)
    return replace(enriched, chapters=new_chapters, spine_context=spine_context, enrichment_audit=audit)


def validate_accent_plan(enriched: EnrichedBook, *, strict: bool = False) -> List[str]:
    errors: List[str] = []
    ctx = enriched.spine_context or {}
    budget = ctx.get("accent_budget") or {}
    assignments = ctx.get("accent_assignments") or []
    counts: Dict[str, int] = {}
    chapters_with: set[int] = set()
    for row in assignments:
        cls = str(row.get("class") or "")
        counts[cls] = counts.get(cls, 0) + 1
        chapters_with.add(int(row.get("chapter") or 0))

    for cls, cap in budget.items():
        if counts.get(cls, 0) > int(cap):
            errors.append(f"accent_budget exceeded for {cls}: {counts.get(cls, 0)} > {cap}")

    total = max(1, len(enriched.chapters))
    _, _, share_cap = resolve_accent_budget(
        str(ctx.get("brand_id") or "phoenix"),
        persona_id=enriched.persona_id,
        topic_id=enriched.topic,
        enrichment_contract_v1=enrichment_contract_v1_enabled(ctx),
    )
    if share_cap > 0 and len(chapters_with) / total > share_cap + 1e-9:
        errors.append(f"accent chapter share {len(chapters_with)/total:.2f} exceeds cap {share_cap}")

    audit_root = enriched.enrichment_audit or {}
    strategy_report = audit_root.get("enrichment_strategy_report") or {}
    if not strategy_report:
        audit = audit_root.get("accent_planner") or {}
        strategy_report = audit.get("enrichment_strategy_report") or {}
    underfilled = strategy_report.get("supported_underfilled_budget_by_class") or {}
    capability_gaps = strategy_report.get("capability_gaps") or {}
    for cls, deficit in underfilled.items():
        if int(deficit) > 0:
            errors.append(
                f"supported_underfilled_budget_by_class: {cls} underfilled by {deficit} "
                f"(assigned {counts.get(cls, 0)}, budget {budget.get(cls, 0)})"
            )
    for cls, reason in capability_gaps.items():
        if int(budget.get(cls, 0)) > 0:
            errors.append(f"capability_gap for {cls}: {reason} with budget {budget.get(cls, 0)}")

    if strict and errors:
        raise ValueError("; ".join(errors))
    return errors
