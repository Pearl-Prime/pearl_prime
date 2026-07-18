"""Profile-aware deterministic variant selector.

Usage:
    selector = ProfileAwareSelector(profile)
    variant = selector.select(role="chapter_hook", candidates=bank_entries, seed_inputs=(topic, persona, arc, chapter_idx))

Backward-compat: candidates without manga_compat are treated as AGNOSTIC (usable by any profile).
Determinism: sha256(seed_inputs + role + title_id)[:8] → index into eligible pool.
"""
from __future__ import annotations

import hashlib
from typing import Any, Protocol, runtime_checkable

from phoenix_v4.manga.series.profile_loader import MangaProfile


@runtime_checkable
class CompatibleVariant(Protocol):
    """Any dict-like with optional 'manga_compat' key."""
    def get(self, key: str, default: Any = None) -> Any: ...


def _is_eligible(candidate: Any, profile: MangaProfile) -> bool:
    """Return True if candidate is compatible with profile. Agnostic if no manga_compat key."""
    if not isinstance(candidate, dict):
        return True
    compat = candidate.get("manga_compat")
    if compat is None:
        return True  # agnostic — usable by any profile
    allowed_demos = compat.get("allowed_market_demos")
    if allowed_demos and profile.market_demo not in allowed_demos:
        return False
    allowed_engines = compat.get("allowed_emotional_engines")
    if allowed_engines and profile.emotional_engine not in allowed_engines:
        return False
    allowed_grammars = compat.get("allowed_visual_grammars")
    if allowed_grammars and profile.visual_grammar not in allowed_grammars:
        return False
    excluded_demos = compat.get("excluded_market_demos")
    if excluded_demos and profile.market_demo in excluded_demos:
        return False
    return True


class ProfileAwareSelector:
    """Deterministic selector that filters a candidate pool by manga_profile compatibility."""

    def __init__(self, profile: MangaProfile) -> None:
        self._profile = profile

    def select(
        self,
        *,
        role: str,
        candidates: list[Any],
        seed_inputs: tuple[Any, ...],
    ) -> Any:
        """Select one candidate deterministically.

        Args:
            role: Selection role label (e.g. "chapter_hook", "opening_beat").
            candidates: List of candidate items (dicts with optional manga_compat).
            seed_inputs: Tuple of hashable inputs (topic, persona, arc, chapter_idx, etc.).

        Returns:
            Selected candidate. Raises ValueError if no eligible candidates.
        """
        eligible = [c for c in candidates if _is_eligible(c, self._profile)]
        if not eligible:
            # Fall back to full pool if profile filtering leaves nothing
            eligible = list(candidates)
        if not eligible:
            raise ValueError(f"Empty candidate pool for role={role!r}")
        raw = "|".join(str(x) for x in seed_inputs)
        seed_str = f"{raw}|{role}|{self._profile.title_id}"
        idx = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16) % len(eligible)
        return eligible[idx]

    def select_many(
        self,
        *,
        role: str,
        candidates: list[Any],
        seed_inputs: tuple[Any, ...],
        count: int,
    ) -> list[Any]:
        """Select ``count`` distinct candidates without replacement (wraps if pool smaller)."""
        eligible = [c for c in candidates if _is_eligible(c, self._profile)]
        if not eligible:
            eligible = list(candidates)
        if not eligible:
            raise ValueError(f"Empty candidate pool for role={role!r}")
        result = []
        seen: set[int] = set()
        for i in range(count):
            raw = "|".join(str(x) for x in seed_inputs)
            seed_str = f"{raw}|{role}|{self._profile.title_id}|slot{i}"
            idx = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16) % len(eligible)
            while idx in seen and len(seen) < len(eligible):
                idx = (idx + 1) % len(eligible)
            seen.add(idx)
            result.append(eligible[idx])
        return result
