"""Character-aware prompt builder — V2 manga pipeline Phase A.2 + A.5.

Reads a series's character_design instance + drawing_tradition_per_genre +
cross_genre_blending_rules + forbidden_tokens_registry and emits a
(positive_prompt, negative_prompt, engine_config) tuple per panel scene
description, adapted to the chosen base model's token-style convention.

Supersedes ad-hoc panel_prompts.json authoring (the old V1 path).

Per CHARACTER_INDIVIDUATION_PIPELINE_SPEC §2.3 token-routing table:
    positive_prompt_axes:   face_shape, eye_geometry, hair, wardrobe_register,
                            age_signaling, accessories, color_signal
    negative_prompt_axes:   mouth_jaw  (express as "no <value>")
    solver_only_axes:       skin_treatment, posture_default, build,
                            nose_construction  (used by solver, not prompt)

Per-base-model adapters:
    animagine_xl_4_0:  Danbooru tag-style ("realistic eye proportions, ...")
    qwen_image:        Natural-language prose ("An adult woman in her late 30s ...")
    flux_schnell:      Front-loaded natural-language; cap at most distinctive axes

panel_prompts.json schema mirrors what queue_panel_renders.py expects (the
brand-2 "prompts" shape from PR #918 / V1 ship): {brand, episode, model,
render_target, prompts: [{panel_id, prompt, negative_prompt, model, width,
height, char_count}, ...]}.

Cookbook note: the panel-targeted genre_prompt_cookbook.yaml does not exist
on origin/main as of cap entry MANGA-LAYERED-PIPELINE-V2-01 ratification.
genre_prompt_cookbook_v2.yaml is KDP-cover-targeted and not adaptable for
panels (per its own preamble). Phase A's prompt builder substitutes
drawing_tradition_per_genre.yaml's per-genre A-H spec (line / ink /
expression / framing / palette / mangaka exemplars) as the panel cookbook
until Phase C authors a proper file. The character_individuation_literature
+ axes vocabulary already provides character-side tokens; drawing_tradition
provides genre-side tokens. The two together substitute cleanly.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_AXES_PATH = REPO_ROOT / "config" / "manga" / "character_design_axes.yaml"
DEFAULT_TRADITION_PATH = REPO_ROOT / "config" / "manga" / "drawing_tradition_per_genre.yaml"
DEFAULT_BLENDING_PATH = REPO_ROOT / "config" / "manga" / "cross_genre_blending_rules.yaml"
DEFAULT_FORBIDDEN_PATH = REPO_ROOT / "config" / "manga" / "forbidden_tokens_registry.yaml"

POSITIVE_PROMPT_AXES = (
    "face_shape", "eye_geometry", "hair", "wardrobe_register",
    "age_signaling", "accessories", "color_signal",
)
NEGATIVE_PROMPT_AXES = ("mouth_jaw",)


# ── Result ──────────────────────────────────────────────────────────────────

@dataclass
class BuiltPrompt:
    panel_id: str
    positive: str
    negative: str
    engine: str
    width: int
    height: int
    char_count_positive: int = 0

    def to_panel_prompt(self) -> dict:
        """Match queue_panel_renders.py "prompts"-key schema."""
        return {
            "panel_id": self.panel_id,
            "prompt": self.positive,
            "negative_prompt": self.negative,
            "model": self.engine,
            "width": self.width,
            "height": self.height,
            "char_count": len(self.positive),
        }


@dataclass
class BuilderConfig:
    base_model: str = "flux_schnell"  # one of: flux_schnell | qwen_image | animagine_xl_4_0
    width: int = 1080
    height: int = 1920
    axes_config: dict = field(default_factory=dict)
    tradition_config: dict = field(default_factory=dict)
    blending_config: dict = field(default_factory=dict)
    forbidden_config: dict = field(default_factory=dict)


def load_builder_config(
    *,
    base_model: str = "flux_schnell",
    width: int = 1080,
    height: int = 1920,
    axes_path: Path | None = None,
    tradition_path: Path | None = None,
    blending_path: Path | None = None,
    forbidden_path: Path | None = None,
) -> BuilderConfig:
    cfg = BuilderConfig(base_model=base_model, width=width, height=height)
    cfg.axes_config = yaml.safe_load((axes_path or DEFAULT_AXES_PATH).read_text())
    cfg.tradition_config = yaml.safe_load((tradition_path or DEFAULT_TRADITION_PATH).read_text())
    cfg.blending_config = yaml.safe_load((blending_path or DEFAULT_BLENDING_PATH).read_text())
    cfg.forbidden_config = yaml.safe_load((forbidden_path or DEFAULT_FORBIDDEN_PATH).read_text())
    return cfg


# ── Axis → token adapters ────────────────────────────────────────────────────

def _axis_value(axis_block: Any, key: str = "value") -> Any:
    if isinstance(axis_block, dict):
        return axis_block.get(key)
    return axis_block


def _axis_tokens_animagine(axis_name: str, axis_block: dict) -> list[str]:
    """Booru-tag style emission — short comma-separated tags."""
    if not isinstance(axis_block, dict):
        return []
    if axis_name == "face_shape":
        v = axis_block.get("value")
        return [f"{v} face"] if v else []
    if axis_name == "eye_geometry":
        size = axis_block.get("size")
        shape = axis_block.get("shape")
        lid = axis_block.get("lid_fold")
        density = axis_block.get("eyelash_density")
        out = []
        if size: out.append(f"{size} eyes")
        if shape: out.append(f"{shape} eye shape")
        if lid and lid != "none_visible": out.append(f"{lid} eyelid")
        if density and density != "moderate": out.append(f"{density} eyelashes")
        return out
    if axis_name == "hair":
        out = []
        for sub in ("length", "parting", "fringe_style", "texture"):
            v = axis_block.get(sub)
            if v:
                out.append(v.replace("_", " ") + (" hair" if sub == "length" else ""))
        cs = axis_block.get("color_signal")
        if cs: out.append(cs.replace("_", " ") + " hair")
        return out
    # generic single-value axis
    v = axis_block.get("value")
    return [f"{v}".replace("_", " ")] if v else []


def _axis_tokens_qwen(axis_name: str, axis_block: dict) -> list[str]:
    """Natural-language prose. Rewrite as descriptive phrases."""
    if not isinstance(axis_block, dict):
        return []
    if axis_name == "face_shape":
        v = axis_block.get("value")
        return [f"a {v.replace('_', '-')}-shaped face"] if v else []
    if axis_name == "eye_geometry":
        parts = []
        size = axis_block.get("size")
        shape = axis_block.get("shape")
        lid = axis_block.get("lid_fold")
        density = axis_block.get("eyelash_density")
        if size and shape:
            parts.append(f"{size} {shape} eyes")
        elif shape:
            parts.append(f"{shape} eyes")
        if lid and lid != "none_visible":
            parts.append(f"{lid.replace('_', ' ')} eyelid")
        if density and density != "moderate":
            parts.append(f"{density.replace('_', ' ')} eyelashes")
        return [" with ".join(parts)] if parts else []
    if axis_name == "hair":
        bits = []
        length = axis_block.get("length")
        parting = axis_block.get("parting")
        fringe = axis_block.get("fringe_style")
        texture = axis_block.get("texture")
        cs = axis_block.get("color_signal")
        if length: bits.append(f"{length.replace('_', ' ')}-length")
        if texture: bits.append(texture)
        if parting and parting not in {"center", "no_part_swept_back"}:
            bits.append(f"{parting.replace('_', ' ')} parting")
        if fringe and fringe != "no_fringe":
            bits.append(f"{fringe.replace('_', ' ')} fringe")
        descr = " ".join(bits)
        if cs:
            descr = f"{cs.replace('_', ' ')} {descr}".strip()
        return [f"{descr} hair"] if descr else []
    v = axis_block.get("value")
    return [v.replace("_", " ")] if v else []


def _axis_tokens_flux(axis_name: str, axis_block: dict) -> list[str]:
    """FLUX-schnell front-loads the most distinctive axes; otherwise terse."""
    # Use Animagine-style tags (terse), then prompt builder front-loads in
    # priority order at compose time.
    return _axis_tokens_animagine(axis_name, axis_block)


_ADAPTERS = {
    "animagine_xl_4_0": _axis_tokens_animagine,
    "qwen_image": _axis_tokens_qwen,
    "flux_schnell": _axis_tokens_flux,
}


# ── Genre tradition lookup ───────────────────────────────────────────────────

def _genre_tokens(tradition_config: dict, genre_family: str | None) -> list[str]:
    """Pull line-tradition + ink + expression + palette tokens from
    drawing_tradition_per_genre.yaml. Top-8 priority genres have full A-H
    blocks; deferred genres have schema-stubs (yield empty)."""
    if not genre_family:
        return []
    genres = (tradition_config or {}).get("genres") or {}
    block = genres.get(genre_family)
    if not block or block.get("status") == "deferred_phase2":
        return []
    out: list[str] = []
    # A_line_tradition: has line_weight_profile and ink_density
    line = block.get("A_line_tradition") or {}
    if isinstance(line, dict):
        if line.get("line_weight_profile"):
            out.append(f"{line['line_weight_profile'].replace('_', ' ')} line work")
        if line.get("ink_density"):
            out.append(f"{line['ink_density'].replace('_', ' ')} inking")
    # E_palette / D_palette varies per genre — try common keys.
    for key in ("D_palette", "E_palette", "palette"):
        pal = block.get(key) or {}
        if isinstance(pal, dict):
            for sub in ("dominant_value", "register", "tonal_range"):
                v = pal.get(sub)
                if isinstance(v, str):
                    out.append(v.replace("_", " "))
                    break
            break
    # mangaka exemplar — pick first
    exemplars = block.get("mangaka_exemplars") or block.get("F_mangaka_exemplars") or []
    if isinstance(exemplars, list) and exemplars:
        first = exemplars[0]
        if isinstance(first, dict) and first.get("name"):
            out.append(f"in the style of {first['name']}")
        elif isinstance(first, str):
            out.append(f"in the style of {first}")
    return out


def _blended_genre_tokens(
    blending_config: dict,
    primary_genre: str,
    secondary_genre: str | None,
) -> list[str]:
    """If the series spans two genres, consult cross_genre_blending_rules and
    return any extra tokens emitted by the rule (typically a register
    qualifier like 'iyashikei tones with dark_fantasy mood'). If no rule,
    return empty."""
    if not secondary_genre or primary_genre == secondary_genre:
        return []
    pairs = (blending_config or {}).get("pairs") or {}
    # Try both directions
    for key in (f"{primary_genre}_plus_{secondary_genre}", f"{secondary_genre}_plus_{primary_genre}"):
        rule = pairs.get(key)
        if rule:
            qualifier = rule.get("blend_signature") or rule.get("token_qualifier")
            if isinstance(qualifier, str):
                return [qualifier]
            # fallback: use the operator-status field as descriptive token
            status = rule.get("operator_status")
            if isinstance(status, str):
                return [status.replace("_", " ")]
    return []


# ── Forbidden tokens lookup ──────────────────────────────────────────────────

def _forbidden_tokens(
    forbidden_config: dict,
    *,
    genre_family: str | None,
    market_demo: str | None,
) -> list[str]:
    out: list[str] = []
    universal = (forbidden_config or {}).get("universal") or {}
    for group in ("quality_floor", "anatomy_floor", "text_lock", "unwanted_modes"):
        items = universal.get(group) or []
        if isinstance(items, list):
            out.extend(items)
    per_genre = ((forbidden_config or {}).get("per_genre") or {}).get(genre_family) or []
    if isinstance(per_genre, list):
        out.extend(per_genre)
    per_demo = ((forbidden_config or {}).get("per_market_demo") or {}).get(market_demo) or []
    if isinstance(per_demo, list):
        out.extend(per_demo)
    # Dedupe preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for t in out:
        if t not in seen:
            deduped.append(t)
            seen.add(t)
    return deduped


def _format_negative_prompt(
    forbidden_tokens: list[str],
    extra_negatives: list[str],
    *,
    base_model: str,
    forbidden_config: dict,
) -> str:
    adapters = (forbidden_config or {}).get("base_model_adapter") or {}
    spec = adapters.get(base_model) or {"join": ", ", "cap_tokens": 30, "style": "comma_tags"}
    join = spec.get("join") or ", "
    cap = int(spec.get("cap_tokens") or 30)
    prefix = spec.get("prefix") or ""
    tokens = list(extra_negatives) + list(forbidden_tokens)
    tokens = tokens[:cap]
    body = join.join(t for t in tokens if t)
    return f"{prefix}{body}".strip(", ")


# ── Public API ───────────────────────────────────────────────────────────────

def build_prompt(
    *,
    panel_id: str,
    scene_description: str,
    character_design: dict,
    primary_genre: str | None,
    secondary_genre: str | None = None,
    builder_config: BuilderConfig | None = None,
) -> BuiltPrompt:
    """Build a panel prompt from a scene description + character design.

    scene_description is the panel-specific context (the existing
    chapter_script.yaml panel.scene field). character_design is a
    pre-validated character_design block (passed solver). Genre comes from
    the series's genre_family + optional secondary genre.
    """
    cfg = builder_config or load_builder_config()
    adapter = _ADAPTERS.get(cfg.base_model, _axis_tokens_flux)

    axes = (character_design or {}).get("axes") or {}
    market_demo = (character_design or {}).get("market_demo")

    # Positive: scene description + character axes (positive set) + genre tokens
    positive_chunks: list[str] = []
    if scene_description:
        positive_chunks.append(scene_description.strip().rstrip("."))

    char_tokens: list[str] = []
    for axis_name in POSITIVE_PROMPT_AXES:
        block = axes.get(axis_name)
        if block:
            char_tokens.extend(adapter(axis_name, block))
    if char_tokens:
        positive_chunks.append(", ".join(t for t in char_tokens if t))

    genre_tokens = _genre_tokens(cfg.tradition_config, primary_genre)
    if genre_tokens:
        positive_chunks.append(", ".join(genre_tokens))

    blend_tokens = _blended_genre_tokens(cfg.blending_config, primary_genre or "", secondary_genre)
    if blend_tokens:
        positive_chunks.append(", ".join(blend_tokens))

    positive = ". ".join(c for c in positive_chunks if c).strip()

    # Negative: solver_only and explicitly negated mouth_jaw + universal +
    # per-genre + per-demo forbidden tokens
    extra_negatives: list[str] = []
    for axis_name in NEGATIVE_PROMPT_AXES:
        block = axes.get(axis_name)
        if not isinstance(block, dict):
            continue
        # mouth_jaw negatives: avoid forbidden lip_shapes for the demo
        lip_shape = block.get("lip_shape")
        if lip_shape == "bow_mouth" and market_demo == "josei":
            extra_negatives.append("bow mouth")  # belt-and-braces with solver

    forbidden = _forbidden_tokens(
        cfg.forbidden_config, genre_family=primary_genre, market_demo=market_demo,
    )
    negative = _format_negative_prompt(
        forbidden, extra_negatives,
        base_model=cfg.base_model, forbidden_config=cfg.forbidden_config,
    )

    return BuiltPrompt(
        panel_id=panel_id,
        positive=positive,
        negative=negative,
        engine=cfg.base_model,
        width=cfg.width,
        height=cfg.height,
        char_count_positive=len(positive),
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Smoke a single panel prompt build from a series YAML.",
    )
    ap.add_argument("--series-yaml", required=True)
    ap.add_argument("--panel-id", default="ch01_p01")
    ap.add_argument("--scene", default="A character at a kitchen table at dawn.")
    ap.add_argument("--base-model", default="flux_schnell",
                    choices=["flux_schnell", "qwen_image", "animagine_xl_4_0"])
    args = ap.parse_args()

    series = yaml.safe_load(Path(args.series_yaml).read_text())
    cd = series.get("character_design")
    if not cd:
        print("No character_design block in series YAML", file=sys.stderr)
        return 1
    cfg = load_builder_config(base_model=args.base_model)
    prompt = build_prompt(
        panel_id=args.panel_id,
        scene_description=args.scene,
        character_design=cd,
        primary_genre=cd.get("genre_family") or series.get("genre_family"),
        secondary_genre=series.get("secondary_genre"),
        builder_config=cfg,
    )
    print(json.dumps(prompt.to_panel_prompt(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
