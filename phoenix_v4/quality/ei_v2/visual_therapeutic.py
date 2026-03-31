"""
Visual / implicit-therapeutic EI v2 dimensions for manga and related artifacts.

Scores are heuristic 0.0–1.0 from structured artifacts + dialogue text.
vt_stealth: 0.0 if any configured forbidden term appears (case-insensitive).
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from phoenix_v4.quality.ei_v2.config import ei_v2_repo_root, load_ei_v2_config

try:
    import yaml
except ImportError:
    yaml = None


def _deep_get(d: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, Mapping) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _load_merged_terms(cfg: Mapping[str, Any] | None) -> list[str]:
    vt = (cfg or {}).get("visual_therapeutic") or {}
    dims = vt.get("dimensions") or {}
    stealth = dims.get("vt_stealth") or {}
    terms = list(stealth.get("forbidden_terms") or [])
    if terms:
        return [str(t).lower() for t in terms]
    # Fallback: manga ite_config stealth list
    root = ei_v2_repo_root()
    p = root / "config" / "manga" / "ite_config.yaml"
    if p.is_file() and yaml is not None:
        try:
            y = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            st = y.get("stealth") or {}
            return [str(t).lower() for t in (st.get("forbidden_therapy_terms") or [])]
        except Exception:
            pass
    return [
        "therapy", "mindfulness", "grounding", "breathing exercise", "meditation",
        "wellness", "self-care", "healing journey", "inner peace", "mental health",
        "calm down", "relax your body", "take a breath",
    ]


def _collect_all_text_from_artifacts(artifacts: Mapping[str, Any]) -> str:
    parts: list[str] = []
    ch = artifacts.get("chapter") or artifacts.get("chapter_enriched")
    if isinstance(ch, dict):
        for page in ch.get("pages") or []:
            for panel in page.get("panels") or []:
                dlg = panel.get("dialogue")
                if isinstance(dlg, list):
                    parts.extend(str(x) for x in dlg)
                elif isinstance(dlg, str):
                    parts.append(dlg)
                parts.append(str(panel.get("action") or ""))
                parts.append(str(panel.get("caption") or ""))
    raw = " ".join(parts)
    extra = str(artifacts.get("extra_text") or "")
    return f"{raw} {extra}".strip()


def vt_stealth(
    text: str,
    *,
    cfg: Mapping[str, Any] | None = None,
    forbidden_terms: list[str] | None = None,
) -> float:
    """Implicit-explicit ratio proxy: 1.0 if clean; 0.0 if any forbidden substring."""
    blob = (text or "").lower()
    terms = [t.lower() for t in forbidden_terms] if forbidden_terms else _load_merged_terms(cfg)
    for t in terms:
        if not t:
            continue
        if t in blob:
            return 0.0
        # word-boundary-ish for single tokens
        if " " not in t and re.search(rf"\b{re.escape(t)}\b", blob):
            return 0.0
    # instructional phrases (stealth)
    instructional = [
        r"\b(?:take|take a)\s+(?:a\s+)?deep\s+breath",
        r"\byou\s+(?:should|need to)\s+(?:relax|calm down)\b",
        r"\blet(?:'s| us)\s+(?:do\s+)?(?:a\s+)?(?:breathing|meditation)\b",
    ]
    for pat in instructional:
        if re.search(pat, blob):
            return 0.0
    return 1.0


def vt_parasympathetic(artifacts: Mapping[str, Any], *, cfg: Mapping[str, Any] | None = None) -> float:
    """
    Breath sequences, cool/warm color in final segment, nature-style panels.
    """
    breath_doc = artifacts.get("breath") or artifacts.get("panel_breath") or {}
    sequences = breath_doc.get("breath_sequences") or []
    n_seq = len(sequences)
    pages = breath_doc.get("pages") or []
    total_panels = 0
    natureish = 0
    for page in pages:
        for panel in page.get("panels") or []:
            total_panels += 1
            cat = str(panel.get("background_category") or panel.get("category") or "").lower()
            if cat in {"nature", "arboreal", "aquatic", "atmospheric", "geological", "landscape"}:
                natureish += 1
            elif panel.get("breath_phase") == "hold":
                natureish += 1

    color_doc = artifacts.get("color_arc") or {}
    panels_ca = list(color_doc.get("panels") or [])
    n = len(panels_ca)
    final_n = max(1, int(max(1, round(0.15 * n))))
    tail = panels_ca[-final_n:] if panels_ca else []
    coolish = sum(
        1
        for p in tail
        if float(p.get("color_temp_target") or p.get("color_temp_k") or 5000) >= 5200
    )
    cool_ratio = (coolish / len(tail)) if tail else 0.0

    breath_score = min(1.0, n_seq / 2.0) if n_seq else 0.0
    nature_score = min(1.0, natureish / max(3, total_panels // 3 or 1))
    color_score = cool_ratio

    return round(max(0.0, min(1.0, 0.45 * breath_score + 0.35 * color_score + 0.20 * nature_score)), 3)


def vt_processing(artifacts: Mapping[str, Any], *, cfg: Mapping[str, Any] | None = None) -> float:
    """Gutter distribution, transition / silence scaffolding."""
    gutter_doc = artifacts.get("gutter") or artifacts.get("gutter_therapy") or {}
    transitions = gutter_doc.get("transitions") or gutter_doc.get("gutter_transitions") or []
    if not transitions:
        pages = gutter_doc.get("pages") or (artifacts.get("chapter_enriched") or {}).get("pages") or []
        for page in pages:
            for panel in page.get("panels") or []:
                gc = panel.get("gutter_class")
                if gc:
                    transitions.append({"gutter_class": gc})

    if not transitions:
        return 0.35

    classes = [str(t.get("gutter_class") or t.get("class") or "standard").lower() for t in transitions]
    wide_like = sum(1 for c in classes if c in {"wide", "breath", "page_break", "processing", "therapeutic"})
    wide_ratio = wide_like / len(classes)

    # transition panels: breath_phase changes or explicit transition flag
    trans_panels = 0
    prev_phase = None
    for page in (artifacts.get("breath") or {}).get("pages") or []:
        for panel in page.get("panels") or []:
            ph = panel.get("breath_phase")
            if ph and ph != prev_phase:
                trans_panels += 1
            prev_phase = ph

    transition_score = min(1.0, trans_panels / max(4, len(classes)))
    silence_hints = 0
    for page in (artifacts.get("chapter") or {}).get("pages") or []:
        for panel in page.get("panels") or []:
            if panel.get("silence_beat") or str(panel.get("mood") or "").lower() in {"calm", "quiet"}:
                silence_hints += 1
    silence_score = min(1.0, silence_hints / max(2, (sum(len(p.get("panels") or []) for p in (artifacts.get("chapter") or {}).get("pages") or []) or 2) // 4))

    return round(max(0.0, min(1.0, 0.5 * wide_ratio + 0.3 * transition_score + 0.2 * silence_score)), 3)


def vt_somatic(artifacts: Mapping[str, Any], *, cfg: Mapping[str, Any] | None = None) -> float:
    """Breath structure validity, fractal FD band, color tempo arc monotonicity proxy."""
    breath_doc = artifacts.get("breath") or {}
    sequences = breath_doc.get("breath_sequences") or []
    valid_cycles = 0
    for seq in sequences:
        phases = seq.get("phases_present") or []
        if isinstance(phases, list) and {"inhale", "hold", "exhale", "pause"}.issubset(set(phases)):
            valid_cycles += 1
        elif seq.get("valid"):
            valid_cycles += 1

    cycle_score = min(1.0, len(sequences) * 0.35) if sequences else 0.0
    if sequences:
        cycle_score = max(cycle_score, min(1.0, valid_cycles / max(1, len(sequences))))

    frac_doc = artifacts.get("fractal") or artifacts.get("fractal_report") or {}
    panels_f = list(frac_doc.get("panels") or [])
    if not panels_f:
        fd_score = 0.5
    else:
        in_band = sum(
            1
            for p in panels_f
            if p.get("compliant")
            or (
                _deep_get(p, "fd_estimate") is not None
                and 1.3 <= float(p.get("fd_estimate", 0)) <= 1.5
            )
        )
        fd_score = in_band / len(panels_f)

    color_doc = artifacts.get("color_arc") or {}
    temps = [float(p.get("color_temp_target") or p.get("color_temp_k") or 0) for p in (color_doc.get("panels") or [])]
    arc_score = 0.6
    if len(temps) >= 4:
        mid = len(temps) // 3
        early = sum(temps[:mid]) / mid
        late = sum(temps[-mid:]) / mid
        # reward arc movement (not flat); direction flexible (genre may invert cool/warm)
        spread = abs(late - early) / max(early, 1.0)
        arc_score = min(1.0, spread * 2.0)

    return round(max(0.0, min(1.0, 0.4 * cycle_score + 0.35 * fd_score + 0.25 * arc_score)), 3)


def compute_visual_therapeutic_scores(
    artifacts: Mapping[str, Any],
    *,
    dialogue_text: str | None = None,
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, float]:
    """Return the four vt_* dimension scores plus composite ITE_score."""
    if cfg is None:
        cfg = load_ei_v2_config()
    text = dialogue_text if dialogue_text is not None else _collect_all_text_from_artifacts(artifacts)
    vp = vt_parasympathetic(artifacts, cfg=cfg)
    vproc = vt_processing(artifacts, cfg=cfg)
    vs = vt_somatic(artifacts, cfg=cfg)
    vst = vt_stealth(text, cfg=cfg)

    vt = cfg.get("visual_therapeutic") or {}
    dims = vt.get("dimensions") or {}
    w_p = float((dims.get("vt_parasympathetic") or {}).get("weight") or 0.30)
    w_r = float((dims.get("vt_processing") or {}).get("weight") or 0.25)
    w_s = float((dims.get("vt_somatic") or {}).get("weight") or 0.25)
    w_t = float((dims.get("vt_stealth") or {}).get("weight") or 0.20)
    wsum = w_p + w_r + w_s + w_t
    if wsum <= 0:
        wsum = 1.0
    ite = (vp * w_p + vproc * w_r + vs * w_s + vst * w_t) / wsum
    return {
        "vt_parasympathetic": vp,
        "vt_processing": vproc,
        "vt_somatic": vs,
        "vt_stealth": vst,
        "ite_score": round(max(0.0, min(1.0, ite)), 3),
    }
