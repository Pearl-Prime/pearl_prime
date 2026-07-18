"""
Stage 1 Catalog Planner.
Produces BookSpec from config/catalog_planning/ (domain_definitions, series_templates, capacity_constraints).
Contract: specs/OMEGA_LAYER_CONTRACTS.md — BookSpec required and identity fields.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class AtomsModel(str, Enum):
    """Legacy vs cluster atoms layout. Policy: legacy_personas → legacy; else cluster."""
    LEGACY = "legacy"
    CLUSTER = "cluster"

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
CONFIG_LOCALIZATION = REPO_ROOT / "config" / "localization"
CONFIG_AUTHORING = REPO_ROOT / "config" / "authoring"
CONFIG_ANGLES = REPO_ROOT / "config" / "angles"
MASTER_ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
RENDER_LOCATION_PROFILES = CONFIG_LOCALIZATION / "render_location_profiles.yaml"

_LOG = logging.getLogger(__name__)


class AngleResolutionError(RuntimeError):
    """Raised when ``angle_strict=True`` and neither registry nor series heuristics yield an angle."""


def _angle_registry_default_path() -> Path:
    return CONFIG_ANGLES / "angle_registry.yaml"


def _normalize_location_key(value: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower()).strip("_")


def load_render_location_profiles(path: Optional[Path] = None) -> dict[str, dict[str, Any]]:
    location_path = path or RENDER_LOCATION_PROFILES
    if not location_path.exists() or yaml is None:
        return {}
    data = yaml.safe_load(location_path.read_text(encoding="utf-8")) or {}
    profiles = data.get("profiles") or {}
    return {
        str(profile_id): (profile or {})
        for profile_id, profile in profiles.items()
        if isinstance(profile, dict)
    }


def _norm_trend_match_key(value: Optional[str]) -> str:
    """Normalize topic/slug/keyword for matching catalog topic_id to trend_score payloads."""
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def load_structured_trend_score(path: Optional[Path]) -> Optional[dict[str, Any]]:
    """Load canonical ``trend_score_{date}.json`` dict, or None if missing/unreadable."""
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(raw, dict):
        return None
    return raw


def trend_heat_for_topic_id(topic_id: str, trend_payload: Optional[dict[str, Any]]) -> Optional[float]:
    """
    Derive a bounded heat score (0–100) from structured trend output for ``topic_id``.
    Uses ``top_signals`` and ``confirmed_topics`` only; returns None when no match.
    """
    if not trend_payload or not topic_id:
        return None
    key = _norm_trend_match_key(topic_id)
    if not key:
        return None
    best: Optional[float] = None

    for row in trend_payload.get("confirmed_topics") or []:
        if not isinstance(row, dict):
            continue
        t = row.get("topic")
        if t is None:
            continue
        if _norm_trend_match_key(str(t)) != key:
            continue
        try:
            growth = float(row.get("et_growth_pct") or 0)
        except (TypeError, ValueError):
            growth = 0.0
        score = 45.0 + min(55.0, max(0.0, growth) * 0.275)
        best = max(best or 0.0, score)

    for sig in trend_payload.get("top_signals") or []:
        if not isinstance(sig, dict):
            continue
        kind = sig.get("kind")
        if kind == "exploding_topics":
            t = sig.get("topic")
            if t is None or _norm_trend_match_key(str(t)) != key:
                continue
            try:
                growth = float(sig.get("growth_pct") or 0)
            except (TypeError, ValueError):
                growth = 0.0
            score = 40.0 + min(60.0, max(0.0, growth) * 0.3)
            best = max(best or 0.0, score)
        elif kind == "google_trends_serpapi":
            kw = sig.get("keyword")
            if kw is None or _norm_trend_match_key(str(kw)) != key:
                continue
            spike = bool(sig.get("spike"))
            try:
                pc = float(sig.get("pct_change_7d") or 0)
            except (TypeError, ValueError):
                pc = 0.0
            score = 70.0 if spike else 35.0 + min(35.0, max(0.0, pc) * 0.7)
            best = max(best or 0.0, score)

    if best is None:
        return None
    return round(min(100.0, best), 4)


def resolve_location_profile_id(location_id: Optional[str], path: Optional[Path] = None) -> Optional[str]:
    """Resolve a caller-supplied location key against render location profiles and aliases."""
    if not location_id:
        return None
    normalized_requested = _normalize_location_key(location_id)
    if not normalized_requested:
        return None
    profiles = load_render_location_profiles(path)
    for profile_id, profile in profiles.items():
        if _normalize_location_key(profile_id) == normalized_requested:
            return profile_id
        aliases = profile.get("aliases") or []
        for alias in aliases:
            if _normalize_location_key(str(alias)) == normalized_requested:
                return profile_id
    available = ", ".join(sorted(profiles.keys())) or "none"
    raise ValueError(
        f"location '{location_id}' not found in render_location_profiles.yaml. "
        f"Available location profiles: {available}"
    )


@dataclass
class BookSpec:
    """Stage 1 output. Stage 2 consumes required; identity passed through to Stage 3.
    author_id / author_positioning_profile: Layer 2 Identity (Writer Spec §24).
    If author_id present, author_positioning_profile is required and must match registry."""
    topic_id: str
    persona_id: str
    series_id: Optional[str]
    installment_number: Optional[int]
    teacher_id: str
    brand_id: str
    angle_id: str
    domain_id: str
    seed: str
    locale: str = "en-US"
    territory: str = "US"
    requested_location_id: Optional[str] = None
    resolved_location_id: Optional[str] = None
    teacher_mode: bool = False
    author_id: Optional[str] = None
    author_positioning_profile: Optional[str] = None
    narrator_id: Optional[str] = None
    atoms_model: Optional[AtomsModel] = None
    # Companion workbook type: "full" | "light_guide" | None (no workbook).
    # Resolved by freebie_planner from domain_id + book_duration_minutes.
    # Authority: specs/COMPANION_WORKBOOK_CATALOG_SPEC.md §2
    # EI V2 uses this to calibrate EXERCISE slot density and reflection prompt depth.
    companion_workbook_type: Optional[str] = None
    # Experience layer fields (EXPERIENCE_LAYER_ANTI_SPAM_SPEC §3).
    delivery_experience: Optional[str] = None
    reader_intent: Optional[str] = None
    pacing_model: Optional[str] = None
    outcome_type: Optional[str] = None
    engagement_depth: Optional[str] = None
    transformation_speed: Optional[str] = None
    perceived_positioning: Optional[str] = None
    experience_hash: Optional[str] = None
    ai_disclosure_status: Optional[str] = None
    story_mix_profile: Optional[str] = None
    # Optional: populated when ``produce_single`` / ``produce_wave`` is given a readable
    # structured trend_score JSON path (docs/TREND_PIPELINE_TRUTH_AND_AUTOMATION_DEV_SPEC.md PR 3).
    trend_heat_score: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        out = {
            "topic_id": self.topic_id,
            "persona_id": self.persona_id,
            "series_id": self.series_id,
            "installment_number": self.installment_number,
            "teacher_id": self.teacher_id,
            "brand_id": self.brand_id,
            "angle_id": self.angle_id,
            "domain_id": self.domain_id,
            "seed": self.seed,
            "locale": self.locale,
            "territory": self.territory,
            "teacher_mode": self.teacher_mode,
        }
        if self.requested_location_id is not None:
            out["requested_location_id"] = self.requested_location_id
        if self.resolved_location_id is not None:
            out["resolved_location_id"] = self.resolved_location_id
        if self.author_id is not None:
            out["author_id"] = self.author_id
        if self.author_positioning_profile is not None:
            out["author_positioning_profile"] = self.author_positioning_profile
        if self.narrator_id is not None:
            out["narrator_id"] = self.narrator_id
        if self.atoms_model is not None:
            out["atoms_model"] = self.atoms_model.value
        if self.companion_workbook_type is not None:
            out["companion_workbook_type"] = self.companion_workbook_type
        for experience_field in (
            "delivery_experience",
            "reader_intent",
            "pacing_model",
            "outcome_type",
            "engagement_depth",
            "transformation_speed",
            "perceived_positioning",
            "experience_hash",
            "ai_disclosure_status",
        ):
            value = getattr(self, experience_field, None)
            if value is not None:
                out[experience_field] = value
        if self.trend_heat_score is not None:
            out["trend_heat_score"] = self.trend_heat_score
        if self.story_mix_profile is not None:
            out["story_mix_profile"] = self.story_mix_profile
        return out


class CatalogPlanner:
    """Produces BookSpec(s) from catalog config. Deterministic when seed is fixed."""

    def __init__(
        self,
        domain_path: Optional[Path] = None,
        series_path: Optional[Path] = None,
        capacity_path: Optional[Path] = None,
        brands_path: Optional[Path] = None,
        locale_registry_path: Optional[Path] = None,
        author_registry_path: Optional[Path] = None,
        positioning_profiles_path: Optional[Path] = None,
        angle_registry_path: Optional[Path] = None,
    ):
        domain_path = domain_path or (CONFIG_CATALOG / "domain_definitions.yaml")
        series_path = series_path or (CONFIG_CATALOG / "series_templates.yaml")
        capacity_path = capacity_path or (CONFIG_CATALOG / "capacity_constraints.yaml")
        brands_path = brands_path or (CONFIG_LOCALIZATION / "brand_registry_locale_extension.yaml")
        locale_registry_path = locale_registry_path or (CONFIG_LOCALIZATION / "locale_registry.yaml")
        author_registry_path = author_registry_path or (REPO_ROOT / "config" / "author_registry.yaml")
        positioning_profiles_path = positioning_profiles_path or (CONFIG_AUTHORING / "author_positioning_profiles.yaml")
        self._domains = self._load_yaml(domain_path)
        self._series = self._load_yaml(series_path)
        self._capacity = self._load_yaml(capacity_path)
        brands_data = self._load_yaml(brands_path)
        self._brands = brands_data.get("brands") or {}
        self._locale_registry_path = locale_registry_path
        self._locale_registry: Optional[dict] = None
        self._author_registry_path = author_registry_path
        self._positioning_profiles_path = positioning_profiles_path
        self._author_registry: Optional[dict] = None
        self._positioning_profiles: Optional[dict] = None
        self._angle_registry_path = angle_registry_path or _angle_registry_default_path()
        self._angle_registry_data: Optional[dict] = None
        self._last_angle_resolution_meta: dict[str, Any] = {}
        self._arc_personas_by_topic: Optional[dict[str, list[str]]] = None

    @staticmethod
    def _load_yaml(p: Path) -> dict:
        if not p.exists() or yaml is None:
            return {}
        with open(p) as f:
            return yaml.safe_load(f) or {}

    def _load_locale_registry(self) -> dict:
        if self._locale_registry is not None:
            return self._locale_registry
        self._locale_registry = self._load_yaml(self._locale_registry_path)
        return self._locale_registry

    def _load_author_registry(self) -> dict:
        if self._author_registry is not None:
            return self._author_registry
        self._author_registry = self._load_yaml(self._author_registry_path)
        return self._author_registry

    def _load_positioning_profiles(self) -> dict:
        if self._positioning_profiles is not None:
            return self._positioning_profiles
        self._positioning_profiles = self._load_yaml(self._positioning_profiles_path)
        return self._positioning_profiles

    def _load_angle_registry(self) -> dict:
        if self._angle_registry_data is not None:
            return self._angle_registry_data
        self._angle_registry_data = self._load_yaml(self._angle_registry_path)
        return self._angle_registry_data

    def _load_arc_personas_by_topic(self) -> dict[str, list[str]]:
        if self._arc_personas_by_topic is not None:
            return self._arc_personas_by_topic
        by_topic: dict[str, set[str]] = {}
        if MASTER_ARCS_ROOT.exists():
            for arc_path in MASTER_ARCS_ROOT.glob("*.yaml"):
                parts = arc_path.stem.split("__")
                if len(parts) < 4:
                    continue
                topic_id = parts[-3]
                persona_id = "__".join(parts[:-3])
                by_topic.setdefault(topic_id, set()).add(persona_id)
        self._arc_personas_by_topic = {
            topic_id: sorted(personas)
            for topic_id, personas in by_topic.items()
        }
        return self._arc_personas_by_topic

    def last_angle_resolution_meta(self) -> dict[str, Any]:
        """Metadata from the most recent ``_derive_angle`` call (empty if derive was not used)."""
        return dict(self._last_angle_resolution_meta)

    def _resolve_persona_for_topic(
        self,
        topic_id: str,
        preferred_personas: list[str],
        offset: int,
    ) -> str:
        available = self._load_arc_personas_by_topic().get(topic_id) or []
        for persona_id in preferred_personas:
            if persona_id in available:
                return persona_id
        if available:
            return available[offset % len(available)]
        if preferred_personas:
            return preferred_personas[offset % len(preferred_personas)]
        return "nyc_exec"

    def _resolve_author_positioning(
        self,
        author_id: Optional[str],
        brand_id: str,
        caller_positioning: Optional[str],
    ) -> Optional[str]:
        """Resolve author_positioning_profile. FAIL if author_id present but mismatch or missing."""
        profiles = self._load_positioning_profiles()
        profile_keys = set((profiles.get("profiles") or {}).keys())
        default_by_brand = (profiles.get("default_by_brand") or {})
        if author_id:
            authors = (self._load_author_registry().get("authors") or {})
            author_cfg = authors.get(author_id)
            if not author_cfg:
                raise ValueError(f"author_id '{author_id}' not found in author_registry.yaml")
            registry_profile = author_cfg.get("positioning_profile")
            if not registry_profile:
                raise ValueError(
                    f"author_id '{author_id}' has no positioning_profile in author_registry.yaml. "
                    "Required by Writer Spec §24."
                )
            if registry_profile not in profile_keys:
                raise ValueError(
                    f"author_id '{author_id}' positioning_profile '{registry_profile}' not found in "
                    "config/authoring/author_positioning_profiles.yaml"
                )
            if caller_positioning is not None and caller_positioning != registry_profile:
                raise ValueError(
                    f"BookSpec author_positioning_profile '{caller_positioning}' does not match "
                    f"author_registry for author_id '{author_id}' (expected '{registry_profile}')."
                )
            return registry_profile
        # No author_id: use default_by_brand for this brand when available
        return default_by_brand.get(brand_id)

    def produce_single(
        self,
        topic_id: str,
        persona_id: str,
        teacher_id: str = "default_teacher",
        brand_id: str = "phoenix",
        seed: str = "default_seed",
        series_id: Optional[str] = None,
        installment_number: Optional[int] = None,
        angle_id: Optional[str] = None,
        domain_id: Optional[str] = None,
        locale: Optional[str] = None,
        territory: Optional[str] = None,
        requested_location_id: Optional[str] = None,
        resolved_location_id: Optional[str] = None,
        teacher_mode: bool = False,
        author_id: Optional[str] = None,
        author_positioning_profile: Optional[str] = None,
        narrator_id: Optional[str] = None,
        atoms_model: Optional[AtomsModel] = None,
        trend_score_path: Optional[Path] = None,
        angle_strict: bool = False,
    ) -> BookSpec:
        """Produce one BookSpec. Required: topic_id, persona_id.

        angle_strict: when True, missing registry + series angle resolution raises
            ``AngleResolutionError`` instead of ``{topic_id}_general`` fallback.

        atoms_model: optional; caller sets (e.g. from legacy_personas). Planner does not infer.
        locale resolution: 1) caller-supplied 2) brand_registry[brand_id].locale 3) en-US.
        territory resolution: 1) caller-supplied 2) brand_registry[brand_id].territory 3) US.
        teacher_mode: when True, Stage 3 uses teacher_banks/<teacher_id>/approved_atoms/ for pools.
        requested_location_id: user-facing location key for render/naming grounding (e.g. nyc_grand_central).
        resolved_location_id: canonical profile id from config/localization/render_location_profiles.yaml.
        author_id: when set, author_positioning_profile is resolved from author_registry (mandatory there).
        author_positioning_profile: if supplied with author_id, must match registry or Stage 1 fails.
        narrator_id: optional; when set, validated against narrator_registry (Writer Spec §23.5).
        trend_score_path: optional path to structured ``trend_score_*.json``; when missing or invalid,
            ``trend_heat_score`` is left None (no crash).
        """
        if not topic_id or not persona_id:
            raise ValueError("BookSpec requires topic_id and persona_id")
        self._last_angle_resolution_meta = {}
        positioning = self._resolve_author_positioning(author_id, brand_id, author_positioning_profile)
        trend_payload = load_structured_trend_score(trend_score_path) if trend_score_path else None
        trend_heat = trend_heat_for_topic_id(topic_id, trend_payload)

        if requested_location_id and resolved_location_id is None:
            resolved_location_id = resolve_location_profile_id(requested_location_id)
        elif resolved_location_id:
            resolved_location_id = resolve_location_profile_id(resolved_location_id)

        series_cfg = self._series.get("series") or {}
        brand_cfg = self._brands.get(brand_id) or {}

        # Locale and territory from brand when not supplied
        if locale is None:
            locale = brand_cfg.get("locale") or "en-US"
        if territory is None:
            territory = brand_cfg.get("territory") or "US"

        # Validate locale exists in registry when registry is present
        if self._locale_registry_path and self._locale_registry_path.exists():
            locale_reg = self._load_locale_registry()
            locales = locale_reg.get("locales") or {}
            if locale not in locales:
                raise ValueError(
                    f"locale '{locale}' not found in locale_registry.yaml. "
                    "Add it there before using it in a BookSpec."
                )

        # Path 1: Series-based angle resolution
        if series_id and not angle_id:
            s = series_cfg.get(series_id) or {}
            angles = s.get("angles") or []
            if angles:
                angle_id = angles[0]

        # Path 2: Series-based domain resolution
        if series_id and not domain_id:
            s = series_cfg.get(series_id) or {}
            domain_id = s.get("domain") or domain_id

        # Path 3: Derive angle from topic + persona when series absent
        if not angle_id:
            angle_id = self._derive_angle(topic_id, persona_id, series_cfg, strict=angle_strict)

        if not domain_id:
            domain_id = self._topic_to_domain(topic_id)

        try:
            from phoenix_v4.planning.accent_planner import resolve_story_mix_profile

            story_mix_profile = resolve_story_mix_profile(
                brand_id, persona_id=persona_id, topic_id=topic_id
            )
        except ImportError:
            story_mix_profile = None

        return BookSpec(
            topic_id=topic_id,
            persona_id=persona_id,
            series_id=series_id,
            installment_number=installment_number,
            teacher_id=teacher_id,
            brand_id=brand_id,
            angle_id=angle_id,
            domain_id=domain_id or "default_domain",
            seed=seed,
            locale=locale,
            territory=territory,
            requested_location_id=requested_location_id,
            resolved_location_id=resolved_location_id,
            teacher_mode=teacher_mode,
            author_id=author_id,
            author_positioning_profile=positioning,
            narrator_id=narrator_id,
            atoms_model=atoms_model,
            trend_heat_score=trend_heat,
            story_mix_profile=story_mix_profile,
        )

    def _derive_angle(
        self,
        topic_id: str,
        persona_id: str,
        series_cfg: dict,
        *,
        strict: bool = False,
    ) -> str:
        """Derive angle_id using ``config/angles/angle_registry.yaml`` SSOT, then series heuristics.

        Order (FEATURE-KNOB-CATALOG-VARIATION-V1-01 P0-2):
        1. ``catalog_planner_resolution.topic_angle_map`` → angle must exist under ``angles:``.
        2. Legacy series/domain/persona_affinity heuristic (unchanged).
        3. If still unresolved: ``{topic_id}_general`` unless ``strict`` is True (then raise).

        Side effect: ``self._last_angle_resolution_meta`` documents the winning path.
        """
        meta: dict[str, Any] = {
            "source": None,
            "registry_hit": False,
            "registry_angle_id": None,
            "series_heuristic_used": False,
            "heuristic_general_fallback": False,
            "angle_id": None,
        }

        reg = self._load_angle_registry()
        angles_root = reg.get("angles") or {}
        res_block = reg.get("catalog_planner_resolution") or {}
        topic_map = res_block.get("topic_angle_map") or {}
        mapped = topic_map.get(topic_id)
        if mapped is not None:
            aid = str(mapped)
            if aid in angles_root:
                meta["registry_hit"] = True
                meta["registry_angle_id"] = aid
                meta["source"] = "angle_registry.topic_angle_map"
                meta["angle_id"] = aid
                self._last_angle_resolution_meta = meta
                return aid
            _LOG.warning(
                "catalog angle registry: topic_angle_map maps topic_id=%r to angle_id=%r "
                "but that angle_id is not declared under angles: — treating as registry miss",
                topic_id,
                mapped,
            )

        topic_to_domain = {
            "relationship_anxiety": "anxiety_cluster",
            "grief": "grief_cluster",
            "shame": "shame_cluster",
            "self_worth": "shame_cluster",
        }
        target_domain = topic_to_domain.get(topic_id)

        best_series = None
        best_score = -1

        for series_id, s_cfg in series_cfg.items():
            angles = s_cfg.get("angles") or []
            if not angles:
                continue

            series_domain = s_cfg.get("domain")
            if target_domain and series_domain != target_domain:
                continue

            affinity = s_cfg.get("persona_affinity") or {}
            high = affinity.get("high") or []
            medium = affinity.get("medium") or []

            if persona_id in high:
                score = 2
            elif persona_id in medium:
                score = 1
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_series = s_cfg

        if best_series:
            angles = best_series.get("angles") or []
            if angles:
                chosen = angles[0]
                meta["series_heuristic_used"] = True
                meta["source"] = "series_template_domain_persona"
                meta["angle_id"] = chosen
                self._last_angle_resolution_meta = meta
                return chosen

        if strict:
            meta["source"] = "unresolved_strict"
            self._last_angle_resolution_meta = meta
            raise AngleResolutionError(
                f"No angle for topic_id={topic_id!r}: registry miss, no series heuristic match, "
                "and angle_strict=True (no topic_general fallback)."
            )

        fallback = f"{topic_id}_general"
        meta["heuristic_general_fallback"] = True
        meta["source"] = "topic_general_fallback"
        meta["angle_id"] = fallback
        self._last_angle_resolution_meta = meta
        _LOG.warning(
            "catalog angle: registry + series miss for topic_id=%r persona_id=%r — "
            "using heuristic fallback %r (declare topic in catalog_planner_resolution.topic_angle_map "
            "or supply series angles to avoid this)",
            topic_id,
            persona_id,
            fallback,
        )
        return fallback

    def _topic_to_domain(self, topic_id: str) -> str:
        """Map topic_id to domain_id. Inverse of _domain_to_topic / _series_to_topic."""
        m = {
            "anxiety": "anxiety_cluster",
            "relationship_anxiety": "anxiety_cluster",
            "social_anxiety": "anxiety_cluster",
            "sleep_anxiety": "anxiety_cluster",
            "grief": "grief_cluster",
            "shame": "shame_cluster",
            "overthinking": "cognitive_cluster",
            "burnout": "energy_cluster",
            "compassion_fatigue": "energy_cluster",
            "boundaries": "relational_cluster",
            "depression": "mood_cluster",
            "self_worth": "identity_cluster",
            "imposter_syndrome": "identity_cluster",
            "financial_anxiety": "practical_cluster",
            "financial_stress": "practical_cluster",
            "courage": "growth_cluster",
            "somatic_healing": "body_cluster",
        }
        return m.get(topic_id, "default_domain")

    def _series_to_topic(self, series_id: str, domain_id: str) -> str:
        """Resolve a compileable topic_id for a planned series row."""
        explicit = {
            "social_anxiety_arc": "social_anxiety",
            "panic_response_arc": "anxiety",
            "acute_loss_arc": "grief",
            "ambiguous_loss_arc": "grief",
            "social_shame_arc": "imposter_syndrome",
            "body_shame_arc": "self_worth",
        }
        if series_id in explicit:
            return explicit[series_id]
        if series_id in {
            "anxiety",
            "overthinking",
            "burnout",
            "boundaries",
            "depression",
            "self_worth",
            "imposter_syndrome",
            "financial_anxiety",
            "financial_stress",
            "sleep_anxiety",
            "compassion_fatigue",
            "courage",
            "somatic_healing",
        }:
            return series_id
        return self._domain_to_topic(domain_id)

    def produce_wave(
        self,
        n: int,
        seed: str = "wave_seed",
        teacher_id: str = "default_teacher",
        brand_id: str = "phoenix",
        locale: Optional[str] = None,
        territory: Optional[str] = None,
        teacher_mode: bool = False,
        trend_score_path: Optional[Path] = None,
    ) -> list[BookSpec]:
        """Produce n BookSpecs from series/angles. Deterministic given n and seed.
        locale/territory default from brand config when not supplied.
        teacher_mode: when True, Stage 3 uses teacher_banks/<teacher_id>/approved_atoms/.
        trend_score_path: optional structured trend JSON; heat computed per topic when readable.
        """
        series_cfg = self._series.get("series") or {}
        if not series_cfg:
            return []
        brand_cfg = self._brands.get(brand_id) or {}
        wave_locale = locale or brand_cfg.get("locale") or "en-US"
        wave_territory = territory or brand_cfg.get("territory") or "US"
        trend_payload = load_structured_trend_score(trend_score_path) if trend_score_path else None
        series_ids = list(series_cfg.keys())
        h = hashlib.sha256(f"{seed}:{n}".encode()).digest()
        specs: list[BookSpec] = []
        for i in range(n):
            s_idx = (int.from_bytes(h[:4], "big") + i) % len(series_ids)
            series_id = series_ids[s_idx]
            s = series_cfg[series_id]
            angles = s.get("angles") or ["default_angle"]
            a_idx = (int.from_bytes(h[4:8], "big") + i) % len(angles)
            angle_id = angles[a_idx]
            domain_id = s.get("domain") or "default_domain"
            topic_id = self._series_to_topic(series_id, domain_id)
            persona_affinity = s.get("persona_affinity") or {}
            preferred_personas = list(dict.fromkeys((persona_affinity.get("high") or []) + (persona_affinity.get("medium") or [])))
            if not preferred_personas:
                preferred_personas = ["nyc_exec"]
            persona_id = self._resolve_persona_for_topic(topic_id, preferred_personas, i)
            inst = (i // (len(angles) * max(len(preferred_personas), 1))) + 1
            spec_seed = hashlib.sha256(f"{seed}:{i}:{series_id}:{angle_id}".encode()).hexdigest()[:24]
            positioning = self._resolve_author_positioning(None, brand_id, None)
            wave_heat = trend_heat_for_topic_id(topic_id, trend_payload)
            specs.append(BookSpec(
                topic_id=topic_id,
                persona_id=persona_id,
                series_id=series_id,
                installment_number=inst,
                teacher_id=teacher_id,
                brand_id=brand_id,
                angle_id=angle_id,
                domain_id=domain_id,
                seed=spec_seed,
                locale=wave_locale,
                territory=wave_territory,
                teacher_mode=teacher_mode,
                author_id=None,
                author_positioning_profile=positioning,
                trend_heat_score=wave_heat,
            ))
        return specs

    def generate_for_brand(
        self,
        brand_id: str,
        n: int,
        seed: str = "brand_wave",
        teacher_id: str = "default_teacher",
        *,
        trend_score_path: Optional[Path] = None,
        repo_root: Optional[Path] = None,
    ) -> list[BookSpec]:
        """Produce up to ``n`` ``BookSpec`` rows for ``brand_id``.

        When ``brand_id`` is listed in ``config/music/music_brand_registry.yaml``,
        applies the §4 music-mode-only slice: ``default_teacher``, ``teacher_mode=False``,
        and post-filters any hybrid/composite-tagged rows. Path X brands and all
        others use the same wave planner path as :meth:`produce_wave` with matching
        arguments (no music-only filter).
        """
        from scripts.catalog.music_mode_branch import (
            CatalogBranch,
            filter_to_music_mode_book_specs,
            resolve_catalog_branch,
        )

        root = repo_root or REPO_ROOT
        branch = resolve_catalog_branch(brand_id, repo_root=root)
        wave_teacher = "default_teacher" if branch is CatalogBranch.MUSIC_ONLY else teacher_id
        specs = self.produce_wave(
            n,
            seed=seed,
            teacher_id=wave_teacher,
            brand_id=brand_id,
            teacher_mode=False,
            trend_score_path=trend_score_path,
        )
        if branch is CatalogBranch.MUSIC_ONLY:
            return filter_to_music_mode_book_specs(specs)
        return specs

    def _domain_to_topic(self, domain_id: str) -> str:
        """Map domain to a topic slug used by Stage 2 / atoms."""
        m = {
            "anxiety_cluster": "anxiety",
            "grief_cluster": "grief",
            "shame_cluster": "self_worth",
            "cognitive_cluster": "overthinking",
            "energy_cluster": "burnout",
            "relational_cluster": "boundaries",
            "mood_cluster": "depression",
            "identity_cluster": "self_worth",
            "practical_cluster": "financial_anxiety",
            "growth_cluster": "courage",
            "body_cluster": "somatic_healing",
        }
        return m.get(domain_id, "anxiety")


def book_spec_digest(spec: BookSpec) -> str:
    """Stable digest for determinism checks."""
    payload = json.dumps(spec.to_dict(), sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
