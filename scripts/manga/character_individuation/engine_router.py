"""Engine router — V2 manga pipeline Phase B.7.

Selects (base_model, workflow_path, sampler_config) per (character_design,
brand, genre, color_mode) tuple. Bridges Phase A's prompt builder to
Phase B's three workflow templates.

Routing rules (commercial-clean stack per audit license_risk_register
2026-04-29 + average_face_problem_eval 2026-05-02):

  seinen + psychological / contemplative-realistic register
      → Qwen-Image (weakest 'average face' attractor; natural-language
        prompt strength)
  josei + healing / iyashikei / slice_of_life-soft
      → Animagine XL 4.0 (anime-tuned; shojo-soft cluster IS the
        register)
  shonen + battle / sports / action
      → Animagine XL 4.0 (shonen-soft cluster is its native register)
  color webtoon (any genre) — explicit color_mode
      → FLUX-schnell + ColorManga LoRA (Phase C territory; this phase
        falls back to FLUX-schnell baseline)
  B&W manga panel default
      → Animagine XL 4.0 + manga lineart LoRA stack (Phase C territory;
        this phase falls back to Animagine baseline)
  fallback (no clear match)
      → FLUX-schnell at 4/1.0/euler/simple (the V1 brand-2 ship config)

Reference-image conditioning (PuLID) is enabled when the caller passes
`use_reference=True` AND a reference_image path is supplied. PuLID adds
~0.5-1 GiB inference VRAM headroom per render.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BRAND_LIST_PATH = REPO_ROOT / "config" / "manga" / "canonical_brand_list.yaml"
DEFAULT_WORKFLOWS_DIR = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows"


# ── Engine identifiers ───────────────────────────────────────────────────────

ENGINE_QWEN = "qwen_image"
ENGINE_ANIMAGINE = "animagine_xl_4_0"
ENGINE_FLUX_SCHNELL = "flux_schnell"

# Workflow files per engine + reference-image mode
WORKFLOW_FILES = {
    (ENGINE_QWEN, False): "qwen_image_txt2img_manga.json",
    (ENGINE_QWEN, True): "qwen_image_txt2img_manga.json",   # same file; reference slot conditional
    (ENGINE_ANIMAGINE, False): "animagine_xl_txt2img_manga.json",
    (ENGINE_ANIMAGINE, True): "animagine_xl_txt2img_manga.json",
    (ENGINE_FLUX_SCHNELL, False): "flux_txt2img_manga.json",        # back-compat brand-2 V1 path
    (ENGINE_FLUX_SCHNELL, True): "flux_txt2img_manga_pulid.json",   # PuLID variant
}

# Sampler defaults per engine (mirror the workflow JSON KSampler nodes)
SAMPLER_CONFIG = {
    ENGINE_QWEN:        {"steps": 24, "cfg": 4.0, "sampler": "euler", "scheduler": "simple",
                         "width": 1080, "height": 1920},
    ENGINE_ANIMAGINE:   {"steps": 28, "cfg": 6.0, "sampler": "euler", "scheduler": "normal",
                         "width": 1024, "height": 1280},
    ENGINE_FLUX_SCHNELL:{"steps": 4, "cfg": 1.0, "sampler": "euler", "scheduler": "simple",
                         "width": 1080, "height": 1920},
}


@dataclass
class EngineSelection:
    engine: str
    workflow_path: Path
    sampler: dict
    reference_enabled: bool
    reasoning: str
    fallback_used: bool = False
    fallback_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "workflow_path": str(self.workflow_path),
            "sampler": dict(self.sampler),
            "reference_enabled": self.reference_enabled,
            "reasoning": self.reasoning,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
        }


# ── Brand demographic lookup ─────────────────────────────────────────────────

def load_brand_list(path: Path | None = None) -> dict:
    p = Path(path) if path else DEFAULT_BRAND_LIST_PATH
    return yaml.safe_load(p.read_text())


def _lookup_brand_demographic(brand_list: dict, brand_id: str) -> str | None:
    brands = (brand_list or {}).get("brands") or {}
    if isinstance(brands, dict):
        b = brands.get(brand_id) or {}
        return b.get("demographic")
    if isinstance(brands, list):
        for b in brands:
            if b.get("brand_id") == brand_id or b.get("id") == brand_id:
                return b.get("demographic")
    return None


# ── Routing engine ───────────────────────────────────────────────────────────

# Genres that pull toward Animagine's anime-soft attractor (it's the right
# register, not a defect there)
_ANIMAGINE_GENRES = {
    "healing", "iyashikei", "slice_of_life", "school", "family",
    "comedy", "fantasy_adventure", "romance", "supernatural_everyday",
    "sports", "battle", "food",
}

# Genres that benefit from Qwen-Image's weak attractor (character-distinctness
# matters more than register tightness)
_QWEN_GENRES = {
    "essay", "memoir", "social_issue", "graphic_medicine", "workplace",
    "battle_internal", "psychological_horror", "mystery", "procedural",
    "horror",
}

# Demographics that lean Animagine
_ANIMAGINE_DEMOGRAPHICS = {"shojo", "kodomomuke"}

# Demographics that lean Qwen for character-distinctness
_QWEN_DEMOGRAPHICS = {"seinen", "josei", "mature"}


def select_engine(
    *,
    brand_id: str | None = None,
    genre: str | None = None,
    market_demo: str | None = None,
    color_mode: str = "bw",        # "bw" | "color"
    use_reference: bool = False,
    brand_list: dict | None = None,
    workflows_dir: Path | None = None,
    available_engines: set[str] | None = None,
) -> EngineSelection:
    """Select base model + workflow + sampler per inputs.

    Priority order:
      1. Explicit color_mode=color → FLUX-schnell baseline (Phase C wires
         ColorManga LoRA atop)
      2. Genre-driven match (genre is more specific than demographic)
      3. Demographic-driven match
      4. Fallback to FLUX-schnell (the V1 brand-2 ship config)

    If ``available_engines`` is provided, the chosen engine is checked
    against the install-time runtime registry; if the chosen engine isn't
    installed yet (e.g. Qwen-Image deferred per Phase B Path B), we
    degrade to FLUX-schnell with explicit ``fallback_used=True`` +
    reasoning so callers can log the degradation. ``available_engines=None``
    means "trust the routing rules" (the unit-test default and the
    pre-runtime-registry behavior).
    """
    workflows_dir = workflows_dir or DEFAULT_WORKFLOWS_DIR

    if brand_list is None:
        brand_list = load_brand_list()

    # If demographic not given, look up via brand
    if market_demo is None and brand_id:
        market_demo = _lookup_brand_demographic(brand_list, brand_id)

    reasoning_bits: list[str] = []
    engine: str | None = None

    if color_mode == "color":
        engine = ENGINE_FLUX_SCHNELL
        reasoning_bits.append("color_mode=color → FLUX-schnell baseline (Phase C ColorManga LoRA)")
    elif genre and genre in _QWEN_GENRES:
        engine = ENGINE_QWEN
        reasoning_bits.append(f"genre={genre} → Qwen-Image (weak attractor for character-distinctness)")
    elif genre and genre in _ANIMAGINE_GENRES:
        engine = ENGINE_ANIMAGINE
        reasoning_bits.append(f"genre={genre} → Animagine 4.0 (attractor matches register)")
    elif market_demo and market_demo in _ANIMAGINE_DEMOGRAPHICS:
        engine = ENGINE_ANIMAGINE
        reasoning_bits.append(f"market_demo={market_demo} → Animagine 4.0")
    elif market_demo and market_demo in _QWEN_DEMOGRAPHICS:
        engine = ENGINE_QWEN
        reasoning_bits.append(f"market_demo={market_demo} → Qwen-Image")

    fallback_used = engine is None
    fallback_reason = ""
    if fallback_used:
        engine = ENGINE_FLUX_SCHNELL
        fallback_reason = (
            f"no genre / demographic match (brand={brand_id}, genre={genre}, "
            f"market_demo={market_demo}); fallback to FLUX-schnell"
        )
        reasoning_bits.append(fallback_reason)

    # Phase B Path B fallback: if the chosen engine isn't actually installed
    # on Pearl Star yet (Qwen-Image deferred to a focused operator session
    # per artifacts/qa/pearl_star_v2_install_log_2026-05-07.md), degrade to
    # FLUX-schnell rather than silently routing to a missing checkpoint.
    if available_engines is not None and engine not in available_engines:
        original_engine = engine
        engine = ENGINE_FLUX_SCHNELL
        fallback_used = True
        fallback_reason = (
            f"chosen engine {original_engine!r} not in available_engines "
            f"({sorted(available_engines)}); degrading to FLUX-schnell"
        )
        reasoning_bits.append(fallback_reason)

    workflow_filename = WORKFLOW_FILES.get((engine, use_reference))
    if workflow_filename is None:
        # Reference-mode mismatch fallback: take the no-reference path
        workflow_filename = WORKFLOW_FILES[(engine, False)]
        reasoning_bits.append("reference-mode workflow not found; using non-reference variant")

    workflow_path = workflows_dir / workflow_filename

    return EngineSelection(
        engine=engine,
        workflow_path=workflow_path,
        sampler=dict(SAMPLER_CONFIG[engine]),
        reference_enabled=use_reference and engine in (ENGINE_FLUX_SCHNELL, ENGINE_QWEN, ENGINE_ANIMAGINE),
        reasoning="; ".join(reasoning_bits),
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )
