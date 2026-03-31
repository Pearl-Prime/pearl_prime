"""ITE (Implicit Therapeutic Engine) heuristic scorer.
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §12
Computes 4 visual-therapeutic dimension scores + composite ITE_score
from chapter artifacts (panel_prompts, style_bible, genre_blueprint, soundtrack_config).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import re


WEIGHTS = {
    "vt_parasympathetic": 0.30,
    "vt_processing": 0.25,
    "vt_somatic": 0.25,
    "vt_stealth": 0.20,
}

FORBIDDEN_TERMS_DEFAULT = [
    "therapy", "mindfulness", "grounding", "breathing exercise",
    "meditation", "wellness", "self-care", "healing journey",
    "inner peace", "mental health", "calm down", "relax your body",
    "take a breath",
]

PENALTY_WEIGHT = 100


@dataclass
class ITEScores:
    vt_parasympathetic: float = 0.0
    vt_processing: float = 0.0
    vt_somatic: float = 0.0
    vt_stealth: float = 1.0
    ite_score: float = 0.0

    def compute_composite(self) -> float:
        self.ite_score = round(
            self.vt_parasympathetic * WEIGHTS["vt_parasympathetic"]
            + self.vt_processing * WEIGHTS["vt_processing"]
            + self.vt_somatic * WEIGHTS["vt_somatic"]
            + self.vt_stealth * WEIGHTS["vt_stealth"],
            4,
        )
        return self.ite_score

    def to_dict(self) -> dict:
        return {
            "vt_parasympathetic": round(self.vt_parasympathetic, 3),
            "vt_processing": round(self.vt_processing, 3),
            "vt_somatic": round(self.vt_somatic, 3),
            "vt_stealth": round(self.vt_stealth, 3),
            "ite_score": round(self.ite_score, 3),
        }


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def score_parasympathetic(panels: list[dict], breath_seqs: list[dict]) -> float:
    if not panels:
        return 0.0
    total = len(panels)
    # Fractal density in resolution (65-85%)
    resolution = [p for p in panels if 65 <= p.get("chapter_pct", 0) <= 85]
    fractal_in_res = sum(
        1 for p in resolution
        if p.get("fractal_target", {}).get("fd_range", [0, 0])[0] >= 1.3
    )
    fractal_ratio = fractal_in_res / max(len(resolution), 1)

    # Cool palette in final 25%
    final_quarter = [p for p in panels if p.get("chapter_pct", 0) >= 75]
    cool_count = sum(
        1 for p in final_quarter
        if p.get("color_temperature", {}).get("temp_k", 5000) >= 5500
    )
    cool_ratio = cool_count / max(len(final_quarter), 1)

    # Large panel ratio (splash/bleed = >30% page)
    large = sum(1 for p in panels if p.get("size_pct", 20) >= 30)
    large_ratio = large / total

    # Breath sequence count normalized
    breath_norm = min(len(breath_seqs) / 2.0, 1.0)

    score = (fractal_ratio * 0.3 + cool_ratio * 0.3 + large_ratio * 0.2 + breath_norm * 0.2)
    return _clamp(score)


def score_processing(panels: list[dict], sabido_map: dict | None) -> float:
    if not panels:
        return 0.0
    # Gutter compliance: check processing/therapeutic after high-band
    high_band = [p for p in panels if p.get("emotional_band", 0) >= 4]
    compliant = sum(
        1 for p in high_band
        if p.get("gutter_after", "standard") in ("processing", "therapeutic", "breath")
    )
    gutter_score = compliant / max(len(high_band), 1)

    # Sabido completeness
    sabido_score = 0.0
    if sabido_map:
        roles = 0
        if sabido_map.get("positive_model"):
            roles += 1
        if sabido_map.get("negative_model"):
            roles += 1
        if sabido_map.get("transitional"):
            roles += 1
        sabido_score = roles / 3.0

    score = gutter_score * 0.6 + sabido_score * 0.4
    return _clamp(score)


def score_somatic(panels: list[dict], breath_seqs: list[dict], soundtrack: dict) -> float:
    components = []

    # Breath validity
    valid_seqs = sum(
        1 for s in breath_seqs
        if all(k in s.get("phase_panels", {}) for k in ("inhale", "hold", "exhale"))
    )
    components.append(min(valid_seqs / max(len(breath_seqs), 1), 1.0) if breath_seqs else 0.0)

    # Color arc monotonicity in resolution
    resolution = sorted(
        [p for p in panels if 10 <= p.get("chapter_pct", 0) <= 85],
        key=lambda p: p.get("chapter_pct", 0),
    )
    if len(resolution) >= 2:
        monotonic = all(
            resolution[i].get("color_temperature", {}).get("saturation_pct", 50)
            <= resolution[i - 1].get("color_temperature", {}).get("saturation_pct", 50) + 5
            for i in range(1, len(resolution))
        )
        components.append(1.0 if monotonic else 0.3)
    else:
        components.append(0.5)

    # Fractal in hold panels
    hold_panels_with_fractal = 0
    hold_total = 0
    for seq in breath_seqs:
        holds = seq.get("phase_panels", {}).get("hold", [])
        hold_total += len(holds)
    components.append(1.0 if hold_total == 0 else (hold_panels_with_fractal / hold_total))

    # Soundtrack tempo compliance
    sections = soundtrack.get("sections", [])
    calming = [s for s in sections if s.get("type") in ("calming", "release", "resolve", "resolution")]
    if calming:
        avg_tempo = sum(s.get("tempo_bpm", 66) for s in calming) / len(calming)
        tempo_score = _clamp(1.0 - max(0, avg_tempo - 72) / 20)
        components.append(tempo_score)
    else:
        components.append(0.5)

    # Silence compliance
    total_dur = soundtrack.get("total_duration_sec", 300)
    total_silence = soundtrack.get("total_silence_sec", 0)
    if total_dur > 0:
        per_5min = total_silence / (total_dur / 300)
        components.append(_clamp(per_5min / 8.0))
    else:
        components.append(0.5)

    return _clamp(sum(components) / len(components)) if components else 0.0


def score_stealth(dialogue_text: str, forbidden: list[str] | None = None) -> float:
    if forbidden is None:
        forbidden = FORBIDDEN_TERMS_DEFAULT
    if not dialogue_text:
        return 1.0
    tokens = dialogue_text.lower().split()
    total_tokens = max(len(tokens), 1)
    explicit_count = 0
    text_lower = dialogue_text.lower()
    for term in forbidden:
        explicit_count += len(re.findall(r'\b' + re.escape(term) + r'\b', text_lower))
    score = 1.0 - (explicit_count / total_tokens) * PENALTY_WEIGHT
    return _clamp(score)


def score_chapter(
    panels: list[dict],
    breath_seqs: list[dict],
    sabido_map: dict | None,
    soundtrack: dict,
    dialogue_text: str,
    forbidden_terms: list[str] | None = None,
) -> ITEScores:
    scores = ITEScores()
    scores.vt_parasympathetic = score_parasympathetic(panels, breath_seqs)
    scores.vt_processing = score_processing(panels, sabido_map)
    scores.vt_somatic = score_somatic(panels, breath_seqs, soundtrack)
    scores.vt_stealth = score_stealth(dialogue_text, forbidden_terms)
    scores.compute_composite()
    return scores
