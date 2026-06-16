"""
Duration Derivation — registry-loader pure functions (DURATION-DERIVATION-01).

Implements docs/DURATION_DERIVATION_SPEC.md §4: a runtime format's advertised
duration is a DERIVED value, single-sourced from the format's word target and a
single WPM constant — never a hand-set label.

    word_target = f(word_range, fill_regime [, cap_word_target])   # §4.1
    audiobook_minutes = round(word_target / tts_wpm)               # §4.2  tts_wpm=150
    ebook_minutes     = round(word_target / ebook_wpm)             # §4.2  ebook_wpm=230

Design principle (§2, mirrors AUTO-PLAN-SSOT-01): the WPM constants are read from
`config/duration_scorecard.yaml` — the SAME constants the read-only adherence
scorecard (`phoenix_v4/ops/duration_adherence_scorecard.py`) already consumes — so
the advertised label and the measurement can never disagree. This module MUST NOT
hard-code 150/230 and MUST NOT re-declare them in `format_registry.yaml`.

Scope (§7): en-US ONLY. CJK locales use character counts at different rates and are
deliberately early-skipped (a separate char-based audit/addendum is required before
any CJK duration claim ships — out of scope here).

Stub-format handling (§8): any runtime format without a `word_range` is SKIPPED
(no word_target ⇒ no derived minutes; no crash, no zero-minute label).

`realistic_words` excludes render_inflation (§4.5): the label is deterministic and
reproducible from config alone. render_inflation is a single-format anchor; for the
`cap` regime, render overshoot is absorbed as cap headroom (the §5 cap raise), not
folded into the advertised minutes.

This module is PURE / read-only: it computes labels from config. It does not mutate
the registry and performs no I/O beyond loading the WPM constants from the scorecard
config (and, optionally, the registry for the convenience batch helper).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Repo root: this file is phoenix_v4/ops/duration_derivation.py → parents[2].
# Mirrors phoenix_v4/ops/duration_adherence_scorecard.py REPO_ROOT convention.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:  # yaml is optional at import time (matches duration_adherence_scorecard.py)
    import yaml
except ImportError:  # pragma: no cover - environment without PyYAML
    yaml = None  # type: ignore[assignment]

# --- defaults (used ONLY as a fallback if the scorecard config can't be read) ---
# The authoritative values live in config/duration_scorecard.yaml; these mirror
# OVERLAY_SPEC §413 (150 WPM TTS) and the audit's 230 WPM reading rate so the
# functions remain usable in import-free unit tests without the YAML on disk.
DEFAULT_TTS_WPM = 150
DEFAULT_EBOOK_WPM = 230

# Locales the English word-count derivation applies to (§7). Everything else
# (ja-JP, zh-TW, zh-CN, ko-KR, ...) is character-based and early-skipped.
EN_LOCALES = frozenset({"en-US", "en"})

# The floor regime overshoots the floor by +4% to clear it deterministically while
# letting the LABEL under-promise rather than over-promise (§3.2). Conservative vs
# the observed ~+10% compose overshoot, by design.
FLOOR_MULTIPLIER = 1.04

VALID_REGIMES = ("cap", "floor", "midpoint")


# --------------------------------------------------------------------------- #
# Config single-sourcing (§4.3)
# --------------------------------------------------------------------------- #
def _load_yaml(p: Path) -> dict:
    """Best-effort YAML load; returns {} if the file is missing or PyYAML absent."""
    if yaml is None or not p.exists():
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def load_wpm_constants(scorecard_config: Optional[dict] = None,
                       repo_root: Optional[Path] = None) -> Tuple[int, int]:
    """Return ``(tts_wpm, ebook_wpm)`` read from ``duration_scorecard.yaml``.

    Single source of truth (§4.3): ``duration_adherence_scorecard.tts_wpm`` and
    ``duration_adherence_scorecard.ebook_wpm``. Falls back to module defaults only
    when a value is absent (e.g. ``ebook_wpm`` on a pre-migration config), so the
    derivation never crashes on a partially-migrated scorecard.

    Pass ``scorecard_config`` to avoid disk I/O (e.g. in tests); otherwise the file
    is loaded from ``<repo_root>/config/duration_scorecard.yaml``.
    """
    if scorecard_config is None:
        root = repo_root or REPO_ROOT
        scorecard_config = _load_yaml(root / "config" / "duration_scorecard.yaml")
    block = (scorecard_config or {}).get("duration_adherence_scorecard", {}) or {}
    tts = block.get("tts_wpm", DEFAULT_TTS_WPM)
    ebook = block.get("ebook_wpm", DEFAULT_EBOOK_WPM)
    return int(tts), int(ebook)


# --------------------------------------------------------------------------- #
# Pure derivation primitives (§4.1, §4.2)
# --------------------------------------------------------------------------- #
def word_target(word_range: Optional[Sequence[int]],
                regime: str,
                cap_word_target: Optional[int] = None) -> Optional[int]:
    """Derive the per-format word target from ``word_range`` + ``fill_regime`` (§4.1).

        cap      -> cap_word_target if declared else word_range[max]
        floor    -> round(word_range[min] * 1.04)
        midpoint -> round((word_range[min] + word_range[max]) / 2)

    Returns ``None`` for a word_range-less (stub) format (§8) — the caller skips it.
    Raises ``ValueError`` for an unknown regime so a typo in the registry fails loud.
    """
    if regime not in VALID_REGIMES:
        raise ValueError(
            f"unknown fill_regime {regime!r}; expected one of {VALID_REGIMES}"
        )
    if word_range is None:
        # Stub format (no word_range) — nothing to derive (§8). Exception: a `cap`
        # regime MAY still carry an explicit cap_word_target with no range.
        if regime == "cap" and cap_word_target is not None:
            return int(cap_word_target)
        return None
    lo, hi = int(word_range[0]), int(word_range[1])
    if regime == "cap":
        return int(cap_word_target) if cap_word_target is not None else hi
    if regime == "floor":
        return round(lo * FLOOR_MULTIPLIER)
    # midpoint
    return round((lo + hi) / 2)


def derive_minutes(words: int, wpm: int) -> int:
    """``round(words / wpm)`` — the single word→minute conversion (§4.2).

    ``wpm`` is supplied by the caller from :func:`load_wpm_constants` (i.e. read
    from the scorecard config); this function never hard-codes a rate.
    """
    if wpm <= 0:
        raise ValueError(f"wpm must be positive, got {wpm}")
    return round(words / wpm)


# --------------------------------------------------------------------------- #
# Per-format convenience (combines the primitives; still pure)
# --------------------------------------------------------------------------- #
def derive_format_minutes(fmt: Dict[str, Any],
                          tts_wpm: int,
                          ebook_wpm: int,
                          locale: str = "en-US") -> Optional[Dict[str, int]]:
    """Derive ``{word_target, audiobook_minutes, ebook_minutes}`` for one format.

    Returns ``None`` when the format is skipped:
      * non-en-US locale (§7 — CJK is character-based, handled elsewhere), or
      * no ``word_range`` and no explicit ``cap_word_target`` (stub format, §8).

    ``fmt`` is a runtime-format mapping from ``format_registry.yaml`` (expects
    optional ``word_range``, ``fill_regime`` [default ``midpoint``], and optional
    ``cap_word_target``).
    """
    if locale not in EN_LOCALES:  # §7 early-skip
        return None
    regime = fmt.get("fill_regime", "midpoint")
    wt = word_target(fmt.get("word_range"), regime, fmt.get("cap_word_target"))
    if wt is None:  # §8 stub skip
        return None
    return {
        "word_target": int(wt),
        "audiobook_minutes": derive_minutes(wt, tts_wpm),
        "ebook_minutes": derive_minutes(wt, ebook_wpm),
    }


def derive_all(registry: Dict[str, Any],
               scorecard_config: Optional[dict] = None,
               repo_root: Optional[Path] = None,
               locale: str = "en-US") -> Dict[str, Dict[str, int]]:
    """Derive minutes for every fully-specced runtime format in ``registry``.

    Skipped formats (stub / non-en) are omitted from the result. WPM constants are
    single-sourced via :func:`load_wpm_constants`. Pure apart from optionally
    loading the scorecard config.
    """
    tts_wpm, ebook_wpm = load_wpm_constants(scorecard_config, repo_root)
    runtime = (registry or {}).get("runtime_formats", {}) or {}
    out: Dict[str, Dict[str, int]] = {}
    for name, fmt in runtime.items():
        if not isinstance(fmt, dict):
            continue
        derived = derive_format_minutes(fmt, tts_wpm, ebook_wpm, locale=locale)
        if derived is not None:
            out[name] = derived
    return out
