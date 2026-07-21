#!/usr/bin/env python3
"""Chapter-level composition grammar validator (spec §6.2 / HR-U16).

Implements scene-level invariants from MANGA_COMPOSITION_GRAMMAR_SPEC.md §6.2
and MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md (HR-U01, HR-U16, HR-U17,
HR-F11 / inv.6).

Consumed by:
  - generate_assembly_manifest._enforce_hr_u16_re_establish (HR-U16 FAIL loop)
  - assemble_from_bank.load_manifest (any severity==FAIL blocks assembly)

Provenance: authored from §6.2 invariants; never present in git history (ABSENT per
HR rules drift table). Finding shape matches assemble_from_bank / generate_assembly_manifest
callsite contracts (rule_id, severity, panel_id, message).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from composition_grammar import load_composition_meta

Severity = Literal["FAIL", "WARN", "INFO"]

ABSTRACT_BG = frozenset({
    "defocus_derived",
    "tone_gradient",
    "manpu_emotion",
    "white_void",
    "black_void",
    "speedlines_focus",
})
LONG_SHOT_TYPES = frozenset({"establishing", "re_establish", "pillow_ma", "closure_breath"})
ABSTRACT_STREAK_LIMIT = 6  # >6 consecutive abstract → require re_establish


@dataclass(frozen=True)
class ChapterGrammarFinding:
    rule_id: str
    severity: Severity
    panel_id: str
    message: str


def _resolve(path_str: str, manifest_dir: Path) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    cand = (manifest_dir / p).resolve()
    if cand.is_file():
        return cand
    repo = Path(__file__).resolve().parents[2]
    cand = (repo / p).resolve()
    return cand if cand.is_file() else (repo / p)


def _l0_layer(panel: dict[str, Any]) -> dict[str, Any] | None:
    for ly in panel.get("layers") or []:
        if ly.get("layer_class") == "L0":
            return ly
    return None


def _has_l2(panel: dict[str, Any]) -> bool:
    return any(ly.get("layer_class") == "L2" for ly in (panel.get("layers") or []))


def _effective_bg_class(panel: dict[str, Any], manifest_dir: Path) -> str:
    l0 = _l0_layer(panel)
    if not l0:
        return "unknown"
    deriv = l0.get("derivation") or {}
    dtype = (deriv.get("type") or deriv.get("op") or "").lower()
    if dtype in ("defocus", "defocus_derived"):
        return "defocus_derived"
    if dtype in ("tone_gradient", "tone_flat", "gradient", "tone"):
        return "tone_gradient"
    if dtype in ("manpu", "manpu_emotion"):
        return "manpu_emotion"
    if dtype in ("void", "white_void"):
        return "white_void"
    if dtype == "black_void":
        return "black_void"
    asset = str(l0.get("asset", ""))
    meta = load_composition_meta(_resolve(asset, manifest_dir)) if asset else None
    if meta and meta.get("bg_class"):
        return str(meta["bg_class"])
    shot = panel.get("shot_type")
    if shot in ("dialogue_bust", "reaction_emotion", "insert_object", "realization"):
        return "tone_gradient" if shot == "insert_object" else "defocus_derived"
    return "full_render"


def _is_abstract_panel(panel: dict[str, Any], manifest_dir: Path) -> bool:
    shot = panel.get("shot_type")
    if shot in ("establishing", "re_establish", "diegetic_cu"):
        bg = _effective_bg_class(panel, manifest_dir)
        return bg in ABSTRACT_BG
    bg = _effective_bg_class(panel, manifest_dir)
    return bg in ABSTRACT_BG


def validate_chapter_composition_grammar(
    manifest: dict[str, Any],
    manifest_dir: Path | str,
) -> list[ChapterGrammarFinding]:
    """Return chapter grammar findings (FAIL/WARN/INFO)."""
    manifest_dir = Path(manifest_dir)
    panels = list(manifest.get("panels") or [])
    findings: list[ChapterGrammarFinding] = []
    if not panels:
        return findings

    first = panels[0]
    first_shot = first.get("shot_type")
    first_bg = _effective_bg_class(first, manifest_dir)
    if first_shot not in ("establishing", "diegetic_cu") or first_bg in ABSTRACT_BG:
        findings.append(
            ChapterGrammarFinding(
                rule_id="HR-U01",
                severity="FAIL",
                panel_id=str(first.get("panel_id", "panels[0]")),
                message=(
                    f"scene must open with establishing full_render "
                    f"(got shot_type={first_shot!r} bg_class={first_bg!r})"
                ),
            )
        )

    streak = 0
    for panel in panels:
        pid = str(panel.get("panel_id", "<unknown>"))
        shot = panel.get("shot_type")
        abstract = _is_abstract_panel(panel, manifest_dir)
        if shot in ("re_establish", "establishing") and not abstract:
            streak = 0
            continue
        if abstract:
            streak += 1
            if streak > ABSTRACT_STREAK_LIMIT:
                findings.append(
                    ChapterGrammarFinding(
                        rule_id="HR-U16",
                        severity="FAIL",
                        panel_id=pid,
                        message=(
                            f"re_establish required after >{ABSTRACT_STREAK_LIMIT} "
                            f"consecutive abstract-BG panels (streak={streak})"
                        ),
                    )
                )
        else:
            streak = 0

    if not any(p.get("shot_type") in LONG_SHOT_TYPES for p in panels):
        findings.append(
            ChapterGrammarFinding(
                rule_id="HR-U17",
                severity="WARN",
                panel_id=str(panels[0].get("panel_id", "panels[0]")),
                message=(
                    "chapter has no long-shot panel "
                    "(establishing/re_establish/pillow_ma/closure_breath)"
                ),
            )
        )

    for panel in panels:
        if panel.get("shot_type") == "pillow_ma" and _has_l2(panel):
            findings.append(
                ChapterGrammarFinding(
                    rule_id="HR-F11",
                    severity="FAIL",
                    panel_id=str(panel.get("panel_id", "<unknown>")),
                    message="pillow_ma panels must contain zero figure layers",
                )
            )

    return findings
