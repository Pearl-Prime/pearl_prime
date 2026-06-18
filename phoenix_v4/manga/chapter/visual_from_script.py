"""Compile validated chapter_script (writer handoff) into panel_prompts.json artifact.

LANE D (MANGA-RENDER-LINEAGE-01 / CHARACTER_INDIVIDUATION_PIPELINE_SPEC §2.3, §2.5):
this stage now records a *deterministic* render-routing decision and folds
character-individuation axis tokens into each panel's prompt **before render**.

Two additive layers, both fail-open (legacy behavior is preserved verbatim when
the inputs aren't available):

  1. Engine routing — ``scripts.manga.character_individuation.engine_router.select_engine``
     picks the commercial-clean base model + ComfyUI workflow + sampler per
     (brand, genre, market_demo, color_mode) tuple. The decision is written to a
     top-level ``render_routing`` block and mirrored onto every panel so the image
     backend / queue dispatcher can route per-panel without re-deriving it.
     This replaces the implicit "FLUX-schnell for everything" default.

  2. Character individuation — when a ``character_design`` block exists for the
     series (config/source_of_truth/manga_profiles/series/<id>.yaml), the routed
     engine's axis→token adapter (``prompt_builder.build_prompt``) emits
     genre-correct, axis-specific character tokens that are blended into the panel
     positive prompt, and the per-genre / per-demo forbidden tokens are blended
     into the negative. This is what pushes same-brand characters off the
     "average-face attractor" toward solver-distinct renders.

  3. Genre drawing tradition — when a ``genre_id`` is known, the per-genre
     drawing-tradition cookbook (``config/manga/drawing_tradition_per_genre.yaml``
     + ``cross_genre_blending_rules.yaml``) contributes render-ready
     tradition tokens (line / ink / palette / mangaka-anchor or the curated
     ``H_token_mapping`` string) to **every** panel's positive prompt and its
     anti-drift list to the negative. Unlike layer 2 this is **decoupled from
     character individuation**: a Devotion/healing chapter gets iyashikei
     (soft line, gentle screentone, contemplative) tokens even when no
     ``character_design`` resolves. Previously these tokens only rode in as a
     side-effect of layer 2, so genre-correctness silently dropped whenever a
     series had no character design — the "healing rendered like the wrong
     tradition" failure (mirror of "horror rendered like slice-of-life").

If a layer can't resolve its inputs, the panel falls back to the existing
``compile_visual_prompt`` output unchanged — no behavior change for callers that
don't pass brand/genre, and no hard dependency on the individuation catalog.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

from phoenix_v4.manga.genre_tradition import genre_tradition_tokens
from phoenix_v4.manga.ite_pipeline import ite_prompt_suffix
from phoenix_v4.manga.visual_prompt_compiler import VisualPromptRequest, compile_visual_prompt

logger = logging.getLogger(__name__)

# Rough mood → engine mapping for kernel defaults (VISUAL_AGENT will refine).
_MOOD_TO_ENGINE: dict[str, str] = {
    "neutral": "shame",
    "tense": "overwhelm",
    "calm": "false_alarm",
    "dark": "grief",
    "high": "spiral",
}

# engine_router engine id → prompt_builder base_model id (the adapter key)
_ENGINE_TO_BUILDER_BASE: dict[str, str] = {
    "qwen_image": "qwen_image",
    "animagine_xl_4_0": "animagine_xl_4_0",
    "flux_schnell": "flux_schnell",
}


def iter_panels_from_chapter_script(chapter_script: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Flatten pages → panels in document order."""
    out: list[dict[str, Any]] = []
    for page in chapter_script.get("pages") or []:
        for panel in page.get("panels") or []:
            out.append(dict(panel))
    return out


def _panel_to_request(
    panel: Mapping[str, Any],
    *,
    style_id: str,
    teacher_id: str,
) -> VisualPromptRequest:
    action = str(panel.get("action") or "")
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list) and dialogue:
        atom_text = " ".join(str(x) for x in dialogue[:5])
    else:
        atom_text = action
    if not atom_text.strip():
        atom_text = "quiet beat"
    mood = str(panel.get("mood") or "neutral").lower()
    engine_type = _MOOD_TO_ENGINE.get(mood, "shame")
    pexpr = panel.get("panel_expression")
    if not isinstance(pexpr, str) and pexpr is not None:
        pexpr = str(pexpr)
    return VisualPromptRequest(
        atom_type="STORY",
        atom_text=atom_text[:4000],
        style_id=style_id,
        teacher_id=teacher_id,
        mechanism_depth="moderate",
        cost_intensity="medium",
        identity_stage="early",
        engine_type=engine_type,
        panel_expression=pexpr,
    )


def _resolve_engine_selection(
    *,
    brand_id: str | None,
    genre_id: str | None,
    market_demo: str | None,
    color_mode: str,
    use_reference: bool,
) -> dict[str, Any] | None:
    """Run engine_router.select_engine and return its dict form, or None on any failure.

    Fail-open: if the router (or its config) can't load, the caller keeps the
    legacy single-backend path. Routing metadata is advisory + recorded; it never
    blocks the visual stage.

    Returns None when there is no routing signal at all (no brand_id / genre_id /
    market_demo) so legacy callers that pass none get the artifact verbatim.
    """
    if not (brand_id or genre_id or market_demo) and color_mode == "bw" and not use_reference:
        return None
    try:
        from scripts.manga.character_individuation.engine_router import select_engine
    except Exception as exc:  # pragma: no cover - import guard
        logger.debug("engine_router unavailable; skipping render routing: %s", exc)
        return None
    try:
        sel = select_engine(
            brand_id=brand_id,
            genre=genre_id,
            market_demo=market_demo,
            color_mode=color_mode,
            use_reference=use_reference,
        )
        return sel.to_dict()
    except Exception as exc:
        logger.warning("engine_router.select_engine failed (%s); using legacy backend path", exc)
        return None


def _resolve_character_design(series_id: str | None) -> dict[str, Any] | None:
    """Look up the series' character_design block from the manga_profiles catalog.

    Returns None when no series_id, no catalog, or no matching design — in which
    case individuation token blending is skipped (legacy prompt output is kept).
    """
    if not series_id:
        return None
    try:
        from scripts.manga.character_individuation.constraint_solver import load_catalog_designs
    except Exception as exc:  # pragma: no cover - import guard
        logger.debug("constraint_solver unavailable; skipping individuation: %s", exc)
        return None
    try:
        for cd in load_catalog_designs():
            if str(cd.get("_series_id") or "") == str(series_id):
                return cd
    except Exception as exc:
        logger.debug("load_catalog_designs failed; skipping individuation: %s", exc)
    return None


def _build_individuation_config(builder_base: str) -> Any | None:
    """Load a prompt_builder BuilderConfig for the routed engine, or None on failure."""
    try:
        from scripts.manga.character_individuation.prompt_builder import load_builder_config
    except Exception as exc:  # pragma: no cover - import guard
        logger.debug("prompt_builder unavailable; skipping individuation: %s", exc)
        return None
    try:
        return load_builder_config(base_model=builder_base)
    except Exception as exc:
        logger.warning("load_builder_config(%s) failed (%s); skipping individuation", builder_base, exc)
        return None


def _blend_individuation_tokens(
    *,
    panel: Mapping[str, Any],
    character_design: dict[str, Any],
    builder_config: Any,
    primary_genre: str | None,
    secondary_genre: str | None,
    panel_id: str,
    base_positive: str,
    base_negative: str,
) -> tuple[str, str, bool]:
    """Fold axis-specific character tokens (positive) + forbidden tokens (negative)
    into the existing panel prompt. Returns (positive, negative, engaged).

    The scene description seed is the panel's action/dialogue (so the character
    axes attach to *this* panel's beat). De-duped against the base prompt so we
    don't double-append on re-runs.
    """
    try:
        from scripts.manga.character_individuation.prompt_builder import build_prompt
    except Exception:  # pragma: no cover - import guard
        return base_positive, base_negative, False
    action = str(panel.get("action") or "")
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list) and dialogue:
        scene = action or " ".join(str(x) for x in dialogue[:3])
    else:
        scene = action or "quiet character beat"
    try:
        bp = build_prompt(
            panel_id=panel_id,
            scene_description=scene[:2000],
            character_design=character_design,
            primary_genre=primary_genre,
            secondary_genre=secondary_genre,
            builder_config=builder_config,
        )
    except Exception as exc:
        logger.debug("build_prompt failed for panel %s; keeping legacy prompt: %s", panel_id, exc)
        return base_positive, base_negative, False

    char_tokens = (bp.positive or "").strip()
    forbidden = (bp.negative or "").strip()

    out_pos = base_positive
    if char_tokens and char_tokens.lower() not in base_positive.lower():
        out_pos = f"{base_positive.rstrip('. ')}. {char_tokens}".strip()
    out_neg = base_negative
    if forbidden and forbidden.lower() not in base_negative.lower():
        out_neg = f"{base_negative.rstrip(', ')}, {forbidden}".strip(", ")
    return out_pos, out_neg, True


def _fold_genre_tradition(
    *,
    base_positive: str,
    base_negative: str,
    positive_tokens: list[str],
    negative_tokens: list[str],
) -> tuple[str, str]:
    """Fold pre-resolved genre drawing-tradition tokens into one panel prompt.

    De-duped against the existing prompt (case-insensitive substring) so
    re-runs and overlap with the base archetype don't double-append. Pure
    string composition — no I/O — so the caller resolves tokens once per
    chapter and reuses them across panels.
    """
    out_pos = base_positive
    for tok in positive_tokens:
        t = (tok or "").strip()
        if t and t.lower() not in out_pos.lower():
            out_pos = f"{out_pos.rstrip('. ')}. {t}".strip(". ")
    out_neg = base_negative
    for tok in negative_tokens:
        t = (tok or "").strip()
        if t and t.lower() not in out_neg.lower():
            out_neg = f"{out_neg.rstrip(', ')}, {t}".strip(", ")
    return out_pos, out_neg


def compile_panel_prompts_from_chapter_script(
    chapter_script: Mapping[str, Any],
    *,
    schema_version: str = "1.0.0",
    series_id: str | None = None,
    chapter_id: str | None = None,
    config_hash: str = "",
    style_id: str = "dark_psychological",
    teacher_id: str = "ahjan",
    brand_id: str | None = None,
    genre_id: str | None = None,
    secondary_genre: str | None = None,
    market_demo: str | None = None,
    color_mode: str = "bw",
    use_reference: bool = False,
) -> dict[str, Any]:
    """Build a panel_prompts artifact dict (validate with schema stem ``panel_prompts``).

    New (LANE D) keyword args are all optional and default to the legacy behavior:

    brand_id / genre_id / secondary_genre / market_demo / color_mode / use_reference
        Drive engine routing + character individuation. When ``genre_id`` (or a
        resolvable ``market_demo``) is supplied, the panel prompts get a recorded
        ``render_routing`` decision and — if a ``character_design`` exists for
        ``series_id`` — axis-specific character tokens folded into each prompt.
    """
    # ── 1. Resolve the render-routing decision (advisory; recorded on artifact) ──
    routing = _resolve_engine_selection(
        brand_id=brand_id,
        genre_id=genre_id,
        market_demo=market_demo,
        color_mode=color_mode,
        use_reference=use_reference,
    )

    # ── 2. Resolve character individuation inputs (fail-open) ──
    character_design = _resolve_character_design(series_id)
    builder_config = None
    if character_design is not None and routing is not None:
        builder_base = _ENGINE_TO_BUILDER_BASE.get(str(routing.get("engine") or ""), "flux_schnell")
        builder_config = _build_individuation_config(builder_base)

    # ── 2b. Resolve genre drawing-tradition tokens (fail-open; DECOUPLED from
    # character individuation). Whenever a genre is known, every panel carries
    # the per-genre tradition (line/ink/palette/mangaka or curated H_token_mapping)
    # — so e.g. Devotion → iyashikei even with no character_design. Resolved once
    # per chapter; the routed engine (else flux_schnell) selects the token variant.
    tradition_base = _ENGINE_TO_BUILDER_BASE.get(
        str((routing or {}).get("engine") or ""), "flux_schnell"
    )
    genre_pos_tokens, genre_neg_tokens = genre_tradition_tokens(
        genre_id, secondary_genre=secondary_genre, base_model=tradition_base,
    )
    genre_tradition_engaged = bool(genre_pos_tokens or genre_neg_tokens)

    individuation_engaged_any = False

    panels_out: list[dict[str, Any]] = []
    for panel in iter_panels_from_chapter_script(chapter_script):
        pid = panel.get("panel_id")
        if not pid or not str(pid).strip():
            raise ValueError("Every panel must have a non-empty panel_id")
        req = _panel_to_request(panel, style_id=style_id, teacher_id=teacher_id)
        built = compile_visual_prompt(req)
        ite = ite_prompt_suffix()
        pos = str(built.get("positive") or "").rstrip()
        if ite and ite not in pos:
            built["positive"] = f"{pos} {ite}".strip()
        neg = str(built.get("negative") or "").rstrip()
        anti = "geometric grid, digital noise, repeating tile"
        if anti.lower() not in neg.lower():
            built["negative"] = f"{neg}, {anti}".strip(", ")

        # ── Fold individuation tokens into THIS panel's prompt (before render) ──
        panel_individuated = False
        if character_design is not None and builder_config is not None:
            new_pos, new_neg, panel_individuated = _blend_individuation_tokens(
                panel=panel,
                character_design=character_design,
                builder_config=builder_config,
                primary_genre=genre_id,
                secondary_genre=secondary_genre,
                panel_id=str(pid),
                base_positive=str(built["positive"]),
                base_negative=str(built["negative"]),
            )
            built["positive"] = new_pos
            built["negative"] = new_neg
            individuation_engaged_any = individuation_engaged_any or panel_individuated

        # ── Fold genre drawing-tradition tokens into THIS panel (decoupled from
        # individuation; applies whenever a genre resolved). De-duped against the
        # base archetype + any individuation tokens already folded above. ──
        if genre_tradition_engaged:
            g_pos, g_neg = _fold_genre_tradition(
                base_positive=str(built["positive"]),
                base_negative=str(built["negative"]),
                positive_tokens=genre_pos_tokens,
                negative_tokens=genre_neg_tokens,
            )
            built["positive"] = g_pos
            built["negative"] = g_neg

        comp = built.get("composition_notes", "")
        if isinstance(comp, str):
            comp_notes: dict[str, Any] = {"summary": comp}
        elif isinstance(comp, dict):
            comp_notes = comp
        else:
            comp_notes = {"summary": str(comp)}
        panel_doc: dict[str, Any] = {
            "panel_id": str(pid),
            "prompt": built["positive"],
            "negative_prompt": built["negative"],
            "composition_notes": comp_notes,
            "prompt_token_count": int(built.get("prompt_token_count") or 0),
            "negative_token_count": int(built.get("negative_token_count") or 0),
            "continuity_tags": list(built.get("continuity_tags") or []),
            "silence_compliance": bool(built.get("silence_compliance")),
            "atom_type": built.get("atom_type"),
            "engine_type": built.get("engine_type"),
            "style_id": built.get("style_id"),
            "teacher_id": built.get("teacher_id"),
            "panel_function": built.get("panel_function"),
        }
        # Mirror the chapter-level routing decision onto each panel so the image
        # backend / queue dispatcher can render per-panel without re-deriving it.
        if routing is not None:
            panel_doc["render_routing"] = {
                "engine": routing.get("engine"),
                "workflow_path": routing.get("workflow_path"),
                "sampler": routing.get("sampler"),
                "reference_enabled": routing.get("reference_enabled"),
                "individuation_engaged": panel_individuated,
                "genre_tradition_engaged": genre_tradition_engaged,
            }
        panels_out.append(panel_doc)

    out: dict[str, Any] = {
        "schema_version": schema_version,
        "artifact_type": "panel_prompts",
        "panels": panels_out,
    }
    if series_id is not None:
        out["series_id"] = series_id
    if chapter_id is not None:
        out["chapter_id"] = chapter_id
    if config_hash:
        out["config_hash"] = config_hash
    # Chapter-level render-routing provenance (commercial-clean engine selection).
    if routing is not None:
        out["render_routing"] = {
            "engine": routing.get("engine"),
            "workflow_path": routing.get("workflow_path"),
            "sampler": routing.get("sampler"),
            "reference_enabled": routing.get("reference_enabled"),
            "reasoning": routing.get("reasoning"),
            "fallback_used": routing.get("fallback_used"),
            "fallback_reason": routing.get("fallback_reason"),
            "individuation_engaged": individuation_engaged_any,
            "genre_tradition_engaged": genre_tradition_engaged,
        }
    return out
