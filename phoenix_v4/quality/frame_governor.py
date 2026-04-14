"""
Warn-only frame governance: somatic-first vs spiritual-first language balance.
Phrase-list v1 (no LLM detection).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRAME_REGISTRY_PATH = REPO_ROOT / "config" / "source_of_truth" / "frame_registry.yaml"

ABSOLUTE_CLAIM_PATTERNS: tuple[str, ...] = (
    r"every\s+organ",
    r"disease\s+is",
    r"love\s+melts\s+all",
    r"\bkarma\b",
    r"frequency\s+of",
    r"vibration\s+of",
    r"soul\s+contract",
)
_ABSOLUTE_RES = tuple(re.compile(p, re.IGNORECASE) for p in ABSOLUTE_CLAIM_PATTERNS)

SPIRITUAL_LEXICON: tuple[str, ...] = (
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
)


def _line_has_spiritual(line: str) -> bool:
    low = line.lower()
    return any(tok in low for tok in SPIRITUAL_LEXICON)


@dataclass
class FrameGovernanceResult:
    violations: list[dict[str, Any]] = field(default_factory=list)
    spiritual_density: float = 0.0
    frame_compliant: bool = True


def load_frame_registry(path: Optional[Path] = None) -> dict[str, Any]:
    p = path or FRAME_REGISTRY_PATH
    if not p.exists() or yaml is None:
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def frame_governance_check(
    text: str,
    frame: str,
    chapter_index: int,
    frame_registry: dict[str, Any],
) -> FrameGovernanceResult:
    if not (text or "").strip():
        return FrameGovernanceResult(frame_compliant=True)

    if frame == "spiritual_first":
        return FrameGovernanceResult(violations=[], spiritual_density=0.0, frame_compliant=True)

    if not frame_registry:
        return FrameGovernanceResult(frame_compliant=True)

    frames = frame_registry.get("frames") or {}
    cfg = frames.get(frame) or frames.get("somatic_first") or {}
    spiritual_min = int(cfg.get("spiritual_entry_chapter_min") or 0)
    density_max = float(cfg.get("spiritual_density_max") or 1.0)
    ban_absolutes = bool(cfg.get("absolute_claim_ban", False))

    violations: list[dict[str, Any]] = []
    lines = text.splitlines()
    total_words = max(len(text.split()), 1)
    spiritual_word_weight = 0

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        wc = len(stripped.split())

        if ban_absolutes:
            for rx in _ABSOLUTE_RES:
                if rx.search(stripped):
                    violations.append(
                        {
                            "type": "absolute_claim",
                            "pattern": rx.pattern,
                            "line": lineno,
                            "excerpt": stripped[:120],
                        }
                    )

        if _line_has_spiritual(stripped):
            spiritual_word_weight += wc
            if chapter_index < spiritual_min:
                violations.append(
                    {
                        "type": "spiritual_before_entry_chapter",
                        "line": lineno,
                        "detail": f"spiritual lexicon before chapter_index >= {spiritual_min}",
                        "excerpt": stripped[:120],
                    }
                )

    spiritual_density = min(1.0, spiritual_word_weight / float(total_words))
    if spiritual_density > density_max + 1e-6:
        violations.append(
            {
                "type": "spiritual_density",
                "detail": f"density {spiritual_density:.3f} > max {density_max:.3f}",
            }
        )

    return FrameGovernanceResult(
        violations=violations,
        spiritual_density=spiritual_density,
        frame_compliant=len(violations) == 0,
    )
