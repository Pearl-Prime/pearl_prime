"""Load and validate manga_profile YAML documents.

Profiles live in: config/source_of_truth/manga_profiles/
Schema: config/source_of_truth/manga_profiles/schema.yaml (reference doc — not a JSON Schema)
Validation: checks required fields are present and enum values are valid.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML required: pip install pyyaml") from exc

from phoenix_v4.manga.models.validation import repo_root

# Enum values mirroring schema.yaml — update here when schema changes.
VALID_MARKET_DEMOS = frozenset(["shonen", "shojo", "seinen", "josei", "kodomo"])
VALID_GENRE_FAMILIES = frozenset([
    "battle", "romance", "mystery", "healing", "horror", "sports", "school",
    "workplace", "historical", "fantasy", "sci_fi", "delinquent", "gag",
    "essay", "memoir", "food", "club_hobby", "procedural",
    "supernatural_everyday", "survival", "revenge", "social_issue",
    # taxonomy-derived additions
    "slice_of_life", "fantasy_adventure", "family", "historical", "comedy",
])
VALID_EMOTIONAL_ENGINES = frozenset([
    "aspiration", "catharsis", "tenderness", "dread", "obsession",
    "wonder", "grief", "cozy_restoration", "rivalry", "longing",
    # taxonomy-derived additions
    "conviction", "emotional_recognition", "emotional_truth", "identity_rebuild",
    "restoration", "quiet_recognition", "team_belonging", "comfort", "craft_pride",
    "play", "absurdity", "release", "helplessness", "curiosity", "responsibility",
    "competence", "becoming", "emotional_misread", "suspicion",
])
VALID_SERIALIZATION_ENGINES = frozenset([
    "cliffhanger_driven", "episodic", "arc_based", "mood_based",
    "quest_based", "ensemble_progression", "monster_of_week",
    "tournament_ladder", "relationship_escalation",
    # taxonomy-derived additions
    "cliffhanger_escalation", "slow_burn_relationship", "emotional_misread_chain",
    "episodic_comfort", "quest_progression", "ensemble_rotation",
    "mystery_reveal_chain", "procedural_case_loop", "ritual_daily_life",
    "training_payoff_cycle", "dread_escalation", "reflective_progression",
    "political_escalation", "gag_reset_loop",
])
VALID_CHAPTER_HOOK_FAMILIES = frozenset([
    "revelation", "interruption", "betrayal", "vow", "arrival",
    "almost_confession", "new_rival", "hidden_truth_glimpse",
    "ominous_image", "emotional_rupture", "ambiguous_line",
    # taxonomy-derived additions
    "confession_almost_happened", "what_did_that_mean", "impossible_task",
])
VALID_VISUAL_GRAMMARS = frozenset([
    "kinetic_shonen", "soft_shojo_decorative", "polished_seinen",
    "grounded_josei_realism", "iyashikei_minimalism", "chibi_deformation",
    "horror_contrast", "retro_gekiga", "sports_clarity", "fantasy_ornate",
    # taxonomy-derived additions
    "kinetic_action", "impact_contrast", "decorative_romance", "intimate_realism",
    "grounded_realism", "sparse_atmosphere", "dread_contrast",
    "body_horror_expressionism", "sports_motion_clarity", "ornate_fantasy",
    "sensory_closeup", "everyday_warmth", "symbolic_reflection",
    "healing_iyashikei",
    # digital-native / platform styles
    "social_media_simulacra",
])
REQUIRED_FIELDS = (
    "title_id", "brand_id", "market_demo", "genre_family",
    "emotional_engine", "reader_promise", "serialization_engine",
    "chapter_hook_family", "visual_grammar",
)


@dataclass(frozen=True)
class MangaProfile:
    title_id: str
    brand_id: str
    market_demo: str
    genre_family: str
    subgenre: str
    emotional_engine: str
    reader_promise: str
    serialization_engine: str
    chapter_hook_family: str
    visual_grammar: str
    # pacing
    words_per_page_target: int = 80
    silent_panel_ratio: float = 0.15
    reaction_shot_frequency: str = "medium"
    spread_frequency: str = "rare"
    narration_tolerance: str = "moderate"
    # other
    line_weight_profile: str = "medium"
    black_fill_ratio: float = 0.15
    screentone_profile: str = "minimal"
    adaptation_targets: tuple = field(default_factory=tuple)
    # raw doc for forward-compat
    _raw: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def profile_seed(self) -> str:
        """Stable 12-char hex seed derived from title_id + brand_id."""
        return hashlib.sha256(f"{self.title_id}|{self.brand_id}".encode()).hexdigest()[:12]


def _validate(data: dict[str, Any]) -> None:
    for f in REQUIRED_FIELDS:
        if f not in data:
            raise ValueError(f"manga_profile missing required field: {f!r}")
    if data["market_demo"] not in VALID_MARKET_DEMOS:
        raise ValueError(f"invalid market_demo: {data['market_demo']!r}")
    if data["genre_family"] not in VALID_GENRE_FAMILIES:
        raise ValueError(f"invalid genre_family: {data['genre_family']!r}")
    if data["emotional_engine"] not in VALID_EMOTIONAL_ENGINES:
        raise ValueError(f"invalid emotional_engine: {data['emotional_engine']!r}")
    if data["serialization_engine"] not in VALID_SERIALIZATION_ENGINES:
        raise ValueError(f"invalid serialization_engine: {data['serialization_engine']!r}")
    if data["chapter_hook_family"] not in VALID_CHAPTER_HOOK_FAMILIES:
        raise ValueError(f"invalid chapter_hook_family: {data['chapter_hook_family']!r}")
    if data["visual_grammar"] not in VALID_VISUAL_GRAMMARS:
        raise ValueError(f"invalid visual_grammar: {data['visual_grammar']!r}")


def load_profile(path: Path) -> MangaProfile:
    """Load and validate a manga_profile YAML file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    _validate(data)
    # Support both flat fields (used by example profiles) and nested pacing/visual_identity blocks
    pacing = data.get("pacing") or {}
    visual_identity = data.get("visual_identity") or {}
    return MangaProfile(
        title_id=data["title_id"],
        brand_id=data["brand_id"],
        market_demo=data["market_demo"],
        genre_family=data["genre_family"],
        subgenre=str(data.get("subgenre") or ""),
        emotional_engine=data["emotional_engine"],
        reader_promise=str(data.get("reader_promise") or ""),
        serialization_engine=data["serialization_engine"],
        chapter_hook_family=data["chapter_hook_family"],
        visual_grammar=data["visual_grammar"],
        words_per_page_target=int(
            pacing.get("words_per_page_target")
            or data.get("words_per_page_target")
            or 80
        ),
        silent_panel_ratio=float(
            pacing.get("silent_panel_ratio")
            or data.get("silent_panel_ratio")
            or 0.15
        ),
        reaction_shot_frequency=str(
            pacing.get("reaction_shot_frequency")
            or data.get("reaction_shot_frequency")
            or "medium"
        ),
        spread_frequency=str(
            pacing.get("spread_frequency")
            or data.get("spread_frequency")
            or "rare"
        ),
        narration_tolerance=str(
            data.get("narration_tolerance") or "moderate"
        ),
        line_weight_profile=str(
            visual_identity.get("line_weight_profile")
            or data.get("line_weight_profile")
            or "medium"
        ),
        black_fill_ratio=float(
            visual_identity.get("black_fill_ratio")
            or data.get("black_fill_ratio")
            or 0.15
        ),
        screentone_profile=str(
            visual_identity.get("screentone_profile")
            or data.get("screentone_profile")
            or "minimal"
        ),
        adaptation_targets=tuple(data.get("adaptation_targets") or []),
        _raw=data,
    )


def find_profile_for_brand_genre(
    brand_id: str,
    genre_family: str,
    profiles_dir: Path | None = None,
) -> MangaProfile | None:
    """Find the brand-genre lane template profile. Returns None if not found."""
    root = repo_root()
    brands_dir = (profiles_dir or (root / "config" / "source_of_truth" / "manga_profiles")) / "brands"
    if not brands_dir.is_dir():
        return None
    for p in brands_dir.glob("*.yaml"):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            if (str(data.get("brand_id") or "") == brand_id and
                    str(data.get("genre_family") or "") == genre_family):
                return load_profile(p)
        except Exception:
            continue
    return None


def find_profile_for_series(series_id: str, profiles_dir: Path | None = None) -> MangaProfile | None:
    """Search profiles_dir for a profile with matching title_id. Returns None if not found."""
    root = repo_root()
    d = profiles_dir or (root / "config" / "source_of_truth" / "manga_profiles")
    for p in d.glob("*.yaml"):
        if p.name.startswith("schema"):
            continue
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            if str(data.get("title_id") or "") == series_id:
                return load_profile(p)
        except Exception:
            continue
    # also check examples/
    examples = d / "examples"
    if examples.is_dir():
        for p in examples.glob("*.yaml"):
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                if str(data.get("title_id") or "") == series_id:
                    return load_profile(p)
            except Exception:
                continue
    return None
