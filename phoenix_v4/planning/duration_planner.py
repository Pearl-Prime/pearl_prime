"""
Duration Planner (Stage 0).

Persona-aware duration selection that recommends the best runtime + structural
format combination based on:
  1. Base duration from registry for (structural_format, intent)
  2. Platform hard constraints (clamp)
  3. Persona attention budget x locale modifier (clamp)
  4. Therapeutic minimum validation
  5. Composite scoring: 0.40 therapeutic_fit + 0.35 platform_fit + 0.25 attention_fit

Output: DurationRecommendation with recommended runtime, structural format,
        duration fit score, warnings, and blockers.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DURATION = REPO_ROOT / "config" / "duration"
CONFIG_FORMAT_SELECTION = REPO_ROOT / "config" / "format_selection"


@dataclass
class DurationRecommendation:
    """Output of the duration planner."""
    recommended_runtime_format: str
    recommended_structural_format: str
    recommended_duration_minutes: int
    duration_fit_score: float
    therapeutic_fit: float
    platform_fit: float
    attention_fit: float
    warnings: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


def _load_yaml(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


class DurationPlanner:
    """Persona-aware duration selection engine."""

    def __init__(
        self,
        duration_config_dir: Optional[Path] = None,
        format_registry_path: Optional[Path] = None,
    ):
        config_dir = duration_config_dir or CONFIG_DURATION
        self._registry = _load_yaml(config_dir / "duration_registry.yaml")
        self._persona_profiles = _load_yaml(config_dir / "persona_duration_profiles.yaml")
        self._therapeutic_rules = _load_yaml(config_dir / "therapeutic_dose_rules.yaml")
        self._platform_profiles = _load_yaml(config_dir / "platform_duration_profiles.yaml")
        self._format_registry = _load_yaml(
            format_registry_path or (CONFIG_FORMAT_SELECTION / "format_registry.yaml")
        )
        self._runtime_formats = self._format_registry.get("runtime_formats", {})
        self._structural_formats = self._format_registry.get("structural_formats", {})

    # Map structural format IDs to the content format names used in duration_registry.yaml
    _STRUCTURAL_TO_CONTENT = {
        "F001": "audiobook_deep",      # 90-Day Transformation
        "F002": "audiobook_deep",      # Daily Practice Rituals
        "F003": "audiobook_standard",  # Challenge Series
        "F004": "audiobook_deep",      # Somatic Body Journey
        "F005": "audiobook_micro",     # Scenario Rescue Kit
        "F006": "audiobook_standard",  # Nervous System Ladder
        "F007": "audiobook_standard",  # Shadow Work Series
        "F008": "audiobook_deep",      # Micro-Habits Stacking
        "F009": "audiobook_deep",      # Parts Work (IFS)
        "F010": "audiobook_standard",  # Energy Management
        "F011": "audiobook_standard",  # Relationship Repair
        "F012": "audiobook_micro",     # Permission Slip Collection
        "F013": "audiobook_deep",      # Before/During/After Crisis
        "F014": "audiobook_standard",  # Archetype Transformation
        "F015": "audiobook_micro",     # Sensory Regulation Library
    }

    def _get_base_duration(self, structural_format: str, intent: str) -> Optional[int]:
        """Step 1: Look up base duration from the format x intent matrix."""
        # Try format_intent_matrix first (direct structural ID mapping)
        matrix = self._registry.get("format_intent_matrix", {})
        fmt_entry = matrix.get(structural_format, {})
        if fmt_entry:
            return fmt_entry.get(intent)
        # Fall back to content format name mapping via formats key
        content_fmt = self._STRUCTURAL_TO_CONTENT.get(structural_format)
        if content_fmt:
            formats = self._registry.get("formats", {})
            fmt_data = formats.get(content_fmt, {})
            intent_data = fmt_data.get(intent, {})
            return intent_data.get("optimal") if isinstance(intent_data, dict) else None
        return None

    def _get_platform_constraints(self, platform_id: Optional[str]) -> dict:
        """Get platform min/max/preferred constraints. Converts seconds to minutes."""
        platforms = self._platform_profiles.get("platforms", {})
        default = {"min_minutes": 5, "max_minutes": 720, "preferred_range": [15, 360]}
        if not platform_id or platform_id not in platforms:
            return default
        raw = platforms[platform_id]
        # Config uses hard_min_seconds / hard_max_seconds; convert to minutes
        hard_min_s = raw.get("hard_min_seconds")
        hard_max_s = raw.get("hard_max_seconds")
        sweet_min_s = raw.get("sweet_spot_min_seconds")
        sweet_max_s = raw.get("sweet_spot_max_seconds")
        result = dict(raw)
        result["min_minutes"] = (hard_min_s // 60) if hard_min_s else default["min_minutes"]
        result["max_minutes"] = (hard_max_s // 60) if hard_max_s else default["max_minutes"]
        if sweet_min_s and sweet_max_s:
            result["preferred_range"] = [sweet_min_s // 60, sweet_max_s // 60]
        else:
            result["preferred_range"] = default["preferred_range"]
        return result

    def _get_persona_profile(self, persona_id: str) -> dict:
        """Get persona attention budget and locale modifiers."""
        personas = self._persona_profiles.get("personas", {})
        if persona_id in personas:
            return personas[persona_id]
        return self._persona_profiles.get("default", {"attention_budget_minutes": 55, "preferred_session_minutes": 30, "locale_modifiers": {}})

    def _get_therapeutic_minimum(self, intent: str, topic_id: Optional[str] = None) -> int:
        """Step 4: Get minimum effective dose for this intent/topic."""
        base_mins = self._therapeutic_rules.get("minimum_effective_dose_minutes", {})
        base = base_mins.get(intent, 10)
        if topic_id:
            overrides = self._therapeutic_rules.get("topic_overrides", {})
            topic_override = overrides.get(topic_id, {})
            if intent in topic_override:
                base = max(base, topic_override[intent])
        return base

    def _clamp(self, value: int, lo: int, hi: int) -> int:
        return max(lo, min(hi, value))

    def _closest_runtime(self, target_minutes: int) -> str:
        """Find the runtime format whose duration_minutes is closest to target."""
        best_id = "standard_book"
        best_diff = float("inf")
        for rid, rinfo in self._runtime_formats.items():
            diff = abs(rinfo.get("duration_minutes", 55) - target_minutes)
            if diff < best_diff:
                best_diff = diff
                best_id = rid
        return best_id

    def _compatible_structural_for_runtime(self, runtime_id: str) -> list[str]:
        """Get compatible structural formats for a runtime."""
        rt = self._runtime_formats.get(runtime_id, {})
        return rt.get("compatible_structural_formats", [])

    def _score_platform_fit(self, duration: int, platform: dict) -> float:
        """Score how well duration fits platform constraints. 1.0 = perfect."""
        pmin = platform.get("min_minutes", 5)
        pmax = platform.get("max_minutes", 720)
        pref = platform.get("preferred_range", [15, 360])
        if duration < pmin or duration > pmax:
            return 0.0
        if pref[0] <= duration <= pref[1]:
            return 1.0
        # Partial fit: within hard bounds but outside preferred
        if duration < pref[0]:
            return 0.5 + 0.5 * (duration - pmin) / max(1, pref[0] - pmin)
        return 0.5 + 0.5 * (pmax - duration) / max(1, pmax - pref[1])

    def _score_attention_fit(self, duration: int, persona: dict, locale: Optional[str]) -> float:
        """Score how well duration fits persona attention budget."""
        budget = persona.get("attention_budget_minutes", 55)
        locale_mod = 1.0
        if locale:
            locale_mods = persona.get("locale_modifiers", {})
            locale_mod = locale_mods.get(locale, 1.0)
        effective_budget = budget * locale_mod
        if duration <= effective_budget:
            return 1.0
        # Gradual penalty for exceeding budget
        overshoot = (duration - effective_budget) / max(1, effective_budget)
        return max(0.0, 1.0 - overshoot)

    def _score_therapeutic_fit(self, duration: int, therapeutic_min: int, intent: str) -> float:
        """Score how well duration meets therapeutic requirements."""
        if intent not in ("therapeutic", "deep_engagement"):
            # Non-therapeutic intents: any duration above minimum is fine
            if duration >= therapeutic_min:
                return 1.0
            return max(0.0, duration / max(1, therapeutic_min))
        # Therapeutic: strong penalty for being below minimum
        if duration >= therapeutic_min:
            return 1.0
        ratio = duration / max(1, therapeutic_min)
        return ratio * 0.5  # Harsh penalty

    def plan(
        self,
        *,
        topic_id: str,
        persona_id: str,
        intent: str = "engagement",
        platform_id: Optional[str] = None,
        locale: Optional[str] = None,
        structural_format_hint: Optional[str] = None,
    ) -> DurationRecommendation:
        """
        Run the duration planning algorithm.

        Args:
            topic_id: Topic for the book.
            persona_id: Persona ID for attention budget lookup.
            intent: One of discovery/engagement/therapeutic/deep_engagement/conversion.
            platform_id: Optional platform for hard constraints.
            locale: Optional locale for attention modifier (e.g. zh-CN).
            structural_format_hint: Optional structural format to prefer.

        Returns:
            DurationRecommendation with best runtime + structural combo.
        """
        warnings: list[str] = []
        blockers: list[str] = []

        valid_intents = {"discovery", "engagement", "therapeutic", "deep_engagement", "conversion"}
        if intent not in valid_intents:
            blockers.append(f"Invalid intent '{intent}'. Must be one of: {sorted(valid_intents)}")
            return DurationRecommendation(
                recommended_runtime_format="standard_book",
                recommended_structural_format="F006",
                recommended_duration_minutes=55,
                duration_fit_score=0.0,
                therapeutic_fit=0.0,
                platform_fit=0.0,
                attention_fit=0.0,
                warnings=warnings,
                blockers=blockers,
            )

        platform = self._get_platform_constraints(platform_id)
        persona = self._get_persona_profile(persona_id)
        therapeutic_min = self._get_therapeutic_minimum(intent, topic_id)
        therapeutic_overrides = self._therapeutic_rules.get("therapeutic_floor_overrides_persona", True)

        # Evaluate all structural formats (or just the hinted one)
        candidates_to_eval = [structural_format_hint] if structural_format_hint and structural_format_hint in self._structural_formats else list(self._structural_formats.keys())

        best: Optional[DurationRecommendation] = None
        best_score = -1.0

        for struct_id in candidates_to_eval:
            base_duration = self._get_base_duration(struct_id, intent)
            if base_duration is None:
                continue

            # Step 2: Platform clamp
            p_min = platform.get("min_minutes", 5)
            p_max = platform.get("max_minutes", 720)
            duration = self._clamp(base_duration, p_min, p_max)
            local_warnings: list[str] = []
            if base_duration != duration:
                local_warnings.append(
                    f"Platform clamped {base_duration}min -> {duration}min "
                    f"(platform {platform_id or 'default'}: [{p_min},{p_max}])"
                )

            # Step 3: Persona attention budget x locale
            locale_mod = 1.0
            if locale:
                locale_mod = persona.get("locale_modifiers", {}).get(locale, 1.0)
            effective_budget = persona.get("attention_budget_minutes", 55) * locale_mod

            # Apply persona budget: for therapeutic intent with override, therapeutic
            # minimum wins; otherwise persona budget is the ceiling.
            if intent in ("therapeutic", "deep_engagement") and therapeutic_overrides:
                if duration < therapeutic_min:
                    duration = self._clamp(therapeutic_min, p_min, p_max)
                    if duration < therapeutic_min:
                        local_warnings.append(
                            f"Platform max ({p_max}min) prevents reaching therapeutic "
                            f"minimum ({therapeutic_min}min)"
                        )
            else:
                if duration > effective_budget:
                    duration = self._clamp(int(effective_budget), p_min, p_max)
                    local_warnings.append(
                        f"Persona budget clamped to {int(effective_budget)}min "
                        f"(persona={persona_id}, locale_mod={locale_mod})"
                    )

            # Step 4: Validate therapeutic minimum
            if duration < therapeutic_min:
                local_warnings.append(
                    f"Duration {duration}min below therapeutic minimum "
                    f"{therapeutic_min}min for intent={intent}"
                )

            # Find closest runtime format
            runtime_id = self._closest_runtime(duration)

            # Verify structural compatibility
            compat = self._compatible_structural_for_runtime(runtime_id)
            if compat and struct_id not in compat:
                # Try to find a better runtime that is compatible
                found_compat = False
                for alt_rid, alt_rinfo in self._runtime_formats.items():
                    alt_compat = alt_rinfo.get("compatible_structural_formats", [])
                    if struct_id in alt_compat:
                        alt_dur = alt_rinfo.get("duration_minutes", 55)
                        if abs(alt_dur - duration) <= abs(self._runtime_formats[runtime_id].get("duration_minutes", 55) - duration):
                            runtime_id = alt_rid
                            found_compat = True
                            break
                if not found_compat:
                    local_warnings.append(
                        f"{struct_id} not in compatible_structural_formats "
                        f"for {runtime_id}"
                    )

            # Step 5: Score
            t_fit = self._score_therapeutic_fit(duration, therapeutic_min, intent)
            p_fit = self._score_platform_fit(duration, platform)
            a_fit = self._score_attention_fit(duration, persona, locale)
            score = 0.40 * t_fit + 0.35 * p_fit + 0.25 * a_fit

            if score > best_score:
                best_score = score
                best = DurationRecommendation(
                    recommended_runtime_format=runtime_id,
                    recommended_structural_format=struct_id,
                    recommended_duration_minutes=duration,
                    duration_fit_score=round(score, 4),
                    therapeutic_fit=round(t_fit, 4),
                    platform_fit=round(p_fit, 4),
                    attention_fit=round(a_fit, 4),
                    warnings=list(local_warnings),
                    blockers=[],
                )

        if best is None:
            blockers.append("No valid structural format found for the given parameters")
            return DurationRecommendation(
                recommended_runtime_format="standard_book",
                recommended_structural_format="F006",
                recommended_duration_minutes=55,
                duration_fit_score=0.0,
                therapeutic_fit=0.0,
                platform_fit=0.0,
                attention_fit=0.0,
                warnings=warnings,
                blockers=blockers,
            )

        best.blockers = blockers
        best.warnings.extend(warnings)
        return best


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Stage 0 Duration Planner")
    parser.add_argument("--topic", required=True, help="Topic ID")
    parser.add_argument("--persona", required=True, help="Persona ID")
    parser.add_argument("--intent", default="engagement", help="Intent: discovery/engagement/therapeutic/deep_engagement/conversion")
    parser.add_argument("--platform", default=None, help="Platform ID (e.g. audible, spotify)")
    parser.add_argument("--locale", default=None, help="Locale (e.g. en-US, zh-CN)")
    parser.add_argument("--structural-format", default=None, help="Structural format hint (e.g. F006)")
    args = parser.parse_args()

    planner = DurationPlanner()
    rec = planner.plan(
        topic_id=args.topic,
        persona_id=args.persona,
        intent=args.intent,
        platform_id=args.platform,
        locale=args.locale,
        structural_format_hint=args.structural_format,
    )
    print(json.dumps({
        "recommended_runtime_format": rec.recommended_runtime_format,
        "recommended_structural_format": rec.recommended_structural_format,
        "recommended_duration_minutes": rec.recommended_duration_minutes,
        "duration_fit_score": rec.duration_fit_score,
        "therapeutic_fit": rec.therapeutic_fit,
        "platform_fit": rec.platform_fit,
        "attention_fit": rec.attention_fit,
        "warnings": rec.warnings,
        "blockers": rec.blockers,
    }, indent=2))


if __name__ == "__main__":
    main()
