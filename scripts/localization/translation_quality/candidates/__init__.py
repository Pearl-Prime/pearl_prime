"""Candidate translation-client wrappers for the translation-quality pipeline.

Each module exposes a `translate(text, *, source_locale, target_locale,
**kwargs) -> CandidateResult` function with a uniform return shape so
calibration_harness.py can call any candidate interchangeably.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CandidateResult:
    candidate_id: str  # e.g. "ollama_qwen2.5:14b", "dashscope_qwen-mt"
    text: str
    meta: dict[str, Any] = field(default_factory=dict)
