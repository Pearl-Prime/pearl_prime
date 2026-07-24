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

  4. Arc-storyboard consumption (MANGA_ARC_STORYBOARD_CONTRACT.md
     §"Storyboard consumption") — when an ``arc_storyboard_plan`` mapping is
     passed, the storyboard is the page/panel authority: its page map and panel
     order drive panel count + ordering, and each panel's
     ``story_move`` / ``visual_proof`` / ``information_delta`` + composition
     intents drive the prompt scaffold (``visual_proof`` leads the positive
     prompt as the scene beat; the chapter script still supplies dialogue).
     Divergence rule (OPD-154 precedent: panel descriptions > writer notes):
     when storyboard and script disagree on panel count for a page/beat, the
     storyboard wins and a WARN row is emitted into
     ``storyboard_divergences[]`` on the artifact. With no storyboard passed,
     the legacy script-only path is byte-identical (regression-tested).
"""

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path
from typing import Any, Mapping

# Byte floor for a bank asset to count as REAL — mirrors
# scripts/ci/check_render_progress_bytes.py stub-as-done floor and
# scripts/manga/generate_assembly_manifest.py MIN_REAL_BYTES.
MIN_REAL_ASSET_BYTES = 50_000

# Manifest layer fields carried verbatim from a storyboard layer pick into an
# assembly-hint layer entry (subset of schemas/manga/assembly_manifest.schema.json
# layer properties; provenance is handled separately and never upgraded).
_LAYER_PICK_CARRY_FIELDS = (
    "bbox_pct",
    "anchor_slot",
    "z_order",
    "z_override",
    "blend",
    "flip_h",
    "opacity",
    "grounding",
    "shot_type",
    "structural_node_id",
    "provenance_note",
)

_LAYER_CLASSES = frozenset({"L0", "L1", "L2", "L3", "L4"})

from phoenix_v4.manga.genre_tradition import genre_tradition_tokens
from phoenix_v4.manga.ite_pipeline import ite_prompt_suffix
from phoenix_v4.manga.visual_prompt_compiler import VisualPromptRequest, compile_visual_prompt

logger = logging.getLogger(__name__)

# Which scene-aware request fields the compiler accepts. PR #1728 added optional
# ``action`` + ``camera`` to ``VisualPromptRequest`` so the authored scene beat +
# camera shot-type LEAD the positive prompt (FLUX weights leading tokens most),
# making each panel render its own beat instead of one scene-agnostic style
# portrait. We forward those fields **only when the dataclass supports them**, so
# this v1/v2 caller is merge-order-independent with #1728: byte-identical to the
# legacy output until #1728 lands, scene-aware the instant it does. The camera →
# shot-type mapping + scene-lead composition live in the compiler (the canonical
# owner) — this caller forwards the raw authored strings and never forks a table.
_REQUEST_FIELDS = frozenset(f.name for f in dataclasses.fields(VisualPromptRequest))
_REQUEST_SUPPORTS_SCENE = {"action", "camera"} <= _REQUEST_FIELDS

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


# ── Arc-storyboard consumption (MANGA_ARC_STORYBOARD_CONTRACT.md) ────────────


def _script_dialogue_texts(panel: Mapping[str, Any], default_locale: str | None) -> list[str]:
    """Normalize script dialogue to a list of plain strings.

    Supports the legacy writer-handoff ``dialogue`` list (strings or dicts with
    ``text``) and the localized ``dialogue_lines`` form
    (``text_by_locale[default_locale]`` else ``text``). Storyboard-path only —
    the legacy no-storyboard path keeps its verbatim ``dialogue`` handling.
    """
    raw = panel.get("dialogue")
    if isinstance(raw, list) and raw:
        out = []
        for item in raw:
            if isinstance(item, Mapping):
                out.append(str(item.get("text") or ""))
            else:
                out.append(str(item))
        return [t for t in out if t.strip()]
    lines = panel.get("dialogue_lines")
    if isinstance(lines, list) and lines:
        out = []
        for line in lines:
            if not isinstance(line, Mapping):
                continue
            by_locale = line.get("text_by_locale")
            text = ""
            if isinstance(by_locale, Mapping) and by_locale:
                if default_locale and default_locale in by_locale:
                    text = str(by_locale[default_locale])
                else:
                    text = str(next(iter(by_locale.values())))
            if not text:
                text = str(line.get("text") or "")
            if text.strip():
                out.append(text)
        return out
    return []


def _storyboard_page_counts(arc_storyboard: Mapping[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for panel in arc_storyboard.get("panels") or []:
        page_id = str(panel.get("page_id") or "")
        counts[page_id] = counts.get(page_id, 0) + 1
    return counts


def _script_page_counts(chapter_script: Mapping[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for page in chapter_script.get("pages") or []:
        page_id = str(page.get("page_id") or "")
        counts[page_id] = counts.get(page_id, 0) + len(page.get("panels") or [])
    return counts


def compute_storyboard_divergences(
    arc_storyboard: Mapping[str, Any],
    chapter_script: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """WARN rows where storyboard and script disagree. Storyboard wins every row.

    OPD-154 precedent: panel descriptions outrank writer notes — the board's
    page map is the authority; the script labels the already-visible move.
    """
    rows: list[dict[str, Any]] = []
    sb_panels = list(arc_storyboard.get("panels") or [])
    sb_ids = [str(p.get("panel_id") or "") for p in sb_panels]
    sb_id_set = set(sb_ids)
    script_panels = iter_panels_from_chapter_script(chapter_script)
    script_ids = [str(p.get("panel_id") or "") for p in script_panels]
    script_id_set = set(script_ids)

    sb_counts = _storyboard_page_counts(arc_storyboard)
    sc_counts = _script_page_counts(chapter_script)
    for page_id in sorted(set(sb_counts) | set(sc_counts)):
        sb_n = sb_counts.get(page_id, 0)
        sc_n = sc_counts.get(page_id, 0)
        if sb_n != sc_n:
            rows.append({
                "severity": "WARN",
                "type": "page_panel_count_mismatch",
                "page_id": page_id,
                "storyboard_count": sb_n,
                "script_count": sc_n,
                "resolution": "storyboard_wins",
            })
    for pid in script_ids:
        if pid not in sb_id_set:
            rows.append({
                "severity": "WARN",
                "type": "script_panel_not_in_storyboard",
                "panel_id": pid,
                "resolution": "dropped — storyboard page map wins (OPD-154)",
            })
    for pid in sb_ids:
        if pid not in script_id_set:
            rows.append({
                "severity": "WARN",
                "type": "storyboard_panel_missing_from_script",
                "panel_id": pid,
                "resolution": "scaffolded from storyboard; no script dialogue",
            })
    return rows


def _storyboard_block(sb_panel: Mapping[str, Any]) -> dict[str, Any]:
    """Per-panel storyboard provenance carried onto the panel_prompts panel doc."""
    block: dict[str, Any] = {}
    for key in (
        "page_id",
        "story_function",
        "story_move",
        "visual_proof",
        "information_delta",
        "beat_role",
        "action_intensity",
        "silence",
        "dialogue_allowed",
        "archetype",
        "scene_template_id",
    ):
        value = sb_panel.get(key)
        if value is not None:
            block[key] = value
    return block


def _merge_storyboard_panel(
    sb_panel: Mapping[str, Any],
    script_panel: Mapping[str, Any] | None,
    *,
    default_locale: str | None,
    divergences: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the request-facing panel dict: storyboard drives the scaffold,
    script supplies dialogue (and camera/mood/expression when present)."""
    merged: dict[str, Any] = dict(script_panel or {})
    merged["panel_id"] = sb_panel.get("panel_id")
    # visual_proof is what the picture must prove — it LEADS the positive
    # prompt as the authored scene beat (PR #1728 scene-aware compiler).
    visual_proof = str(sb_panel.get("visual_proof") or "").strip()
    if visual_proof:
        merged["action"] = visual_proof
    dialogue = _script_dialogue_texts(script_panel or {}, default_locale)
    if dialogue and sb_panel.get("dialogue_allowed") is False:
        divergences.append({
            "severity": "WARN",
            "type": "dialogue_disallowed_by_storyboard",
            "panel_id": str(sb_panel.get("panel_id") or ""),
            "resolution": "dialogue excluded from prompt scaffold — storyboard wins",
        })
        dialogue = []
    if dialogue:
        merged["dialogue"] = dialogue
    else:
        merged.pop("dialogue", None)
    return merged


def build_assembly_layer_hints(
    arc_storyboard: Mapping[str, Any],
    *,
    repo_root: Path | str,
    series_id: str | None = None,
    arc_storyboard_ref: str | None = None,
    min_real_bytes: int = MIN_REAL_ASSET_BYTES,
) -> dict[str, Any]:
    """Emit assembly-manifest layer-selection hints from a storyboard's layer picks.

    Storyboard panels may carry ``layer_picks[]`` (manga-storyboarder skill
    flow; legal via the arc-storyboard schema's ``additionalProperties``):
    ``{layer_class, asset, provenance?, bbox_pct?, anchor_slot?, ...}``.
    Each pick becomes a manifest ``layers[]`` entry with provenance carried
    through — a pick whose asset is byte-real (≥ ``min_real_bytes`` on disk)
    keeps its declared provenance (INTERIM is never upgraded to REAL); a pick
    whose asset is missing or below the byte floor becomes a **flagged INTERIM
    placeholder row** (never silently dropped) and a demand-gap row in the
    ``panels_with_gaps`` format consumed by the bank demand rollup
    (generate_assembly_manifest.py ``bank_gaps.json`` convention).
    """
    root = Path(repo_root)
    sid = str(series_id or arc_storyboard.get("series_id") or "")
    chapter_id = str(arc_storyboard.get("chapter_id") or "")
    bank_contract_dir = root / "artifacts" / "manga" / sid / "bank_contracts"
    bank_contract_present = bank_contract_dir.is_dir() and any(bank_contract_dir.iterdir())

    panels_out: list[dict[str, Any]] = []
    gap_panels: list[dict[str, Any]] = []
    stats = {
        "panels_total": 0,
        "panels_with_picks": 0,
        "layers_real": 0,
        "layers_interim": 0,
        "layers_gap": 0,
    }
    for sb_panel in arc_storyboard.get("panels") or []:
        stats["panels_total"] += 1
        picks = sb_panel.get("layer_picks")
        if not isinstance(picks, list) or not picks:
            continue
        stats["panels_with_picks"] += 1
        pid = str(sb_panel.get("panel_id") or "")
        layers: list[dict[str, Any]] = []
        panel_gaps: list[str] = []
        for pick in picks:
            if not isinstance(pick, Mapping):
                continue
            layer_class = str(pick.get("layer_class") or "")
            if layer_class not in _LAYER_CLASSES:
                panel_gaps.append(f"?:{pick.get('asset') or pick.get('asset_key') or 'unknown'}")
                stats["layers_gap"] += 1
                continue
            asset = str(pick.get("asset") or pick.get("asset_key") or "")
            asset_path = Path(asset)
            resolved = asset_path if asset_path.is_absolute() else root / asset_path
            byte_real = (
                bool(asset)
                and resolved.is_file()
                and resolved.stat().st_size >= min_real_bytes
            )
            declared = str(pick.get("provenance") or "").upper()
            entry: dict[str, Any] = {"layer_class": layer_class, "asset": asset}
            for key in _LAYER_PICK_CARRY_FIELDS:
                if pick.get(key) is not None:
                    entry[key] = pick[key]
            if byte_real:
                # Provenance carried through — never upgrade a declared INTERIM.
                entry["provenance"] = "INTERIM" if declared == "INTERIM" else "REAL"
                if entry["provenance"] == "INTERIM":
                    stats["layers_interim"] += 1
                else:
                    stats["layers_real"] += 1
            else:
                entry["provenance"] = "INTERIM"
                entry.setdefault(
                    "provenance_note",
                    f"bank gap — {layer_class} asset not on disk or below "
                    f"{min_real_bytes}-byte floor; enqueue render for {asset or '<unset>'}",
                )
                stats["layers_interim"] += 1
                stats["layers_gap"] += 1
                panel_gaps.append(f"{layer_class}:{asset or '<unset>'}")
            layers.append(entry)
        panel_entry: dict[str, Any] = {"panel_id": pid, "layers": layers}
        block = _storyboard_block(sb_panel)
        if block:
            panel_entry["storyboard"] = block
        panels_out.append(panel_entry)
        if panel_gaps:
            gap_panels.append({"panel_id": pid, "gaps": panel_gaps})

    doc: dict[str, Any] = {
        "schema_version": "1.0.0",
        "artifact_type": "assembly_layer_hints",
        "series_id": sid,
        "chapter_id": chapter_id,
        "bank_contract_present": bank_contract_present,
        "panels": panels_out,
        "gaps": {
            "series_id": sid,
            "episode_id": chapter_id,
            "stats": stats,
            "panels_with_gaps": gap_panels,
        },
    }
    if arc_storyboard_ref:
        doc["arc_storyboard_ref"] = str(arc_storyboard_ref)
    return doc


def _panel_to_request(
    panel: Mapping[str, Any],
    *,
    style_id: str,
    teacher_id: str,
) -> VisualPromptRequest:
    action = str(panel.get("action") or "")
    camera = str(panel.get("camera") or "")
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
    kwargs: dict[str, Any] = dict(
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
    # Forward the authored scene beat + camera so the compiler can lead the
    # positive prompt with this panel's own scene (PR #1728). Gated on dataclass
    # support so the legacy assembly stays byte-identical until #1728 merges.
    if _REQUEST_SUPPORTS_SCENE:
        kwargs["action"] = action
        kwargs["camera"] = camera
    return VisualPromptRequest(**kwargs)


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
    arc_storyboard: Mapping[str, Any] | None = None,
    arc_storyboard_ref: str | None = None,
) -> dict[str, Any]:
    """Build a panel_prompts artifact dict (validate with schema stem ``panel_prompts``).

    New (LANE D) keyword args are all optional and default to the legacy behavior:

    brand_id / genre_id / secondary_genre / market_demo / color_mode / use_reference
        Drive engine routing + character individuation. When ``genre_id`` (or a
        resolvable ``market_demo``) is supplied, the panel prompts get a recorded
        ``render_routing`` decision and — if a ``character_design`` exists for
        ``series_id`` — axis-specific character tokens folded into each prompt.

    arc_storyboard / arc_storyboard_ref (storyboard consumption)
        When an ``arc_storyboard_plan`` mapping is supplied, the storyboard is
        the page/panel authority (MANGA_ARC_STORYBOARD_CONTRACT.md §"Storyboard
        consumption"): its panel order + page map drive panel count and
        ordering; per-panel ``visual_proof`` leads the prompt scaffold; the
        script supplies dialogue. Count divergences emit WARN rows into
        ``storyboard_divergences[]`` (storyboard wins — OPD-154). Omitted →
        legacy script-only path, byte-identical.
    """
    # ── 0. Storyboard authority resolution (optional; legacy path untouched) ──
    storyboard_divergences: list[dict[str, Any]] = []
    if arc_storyboard is not None:
        if arc_storyboard.get("artifact_type") != "arc_storyboard_plan":
            raise ValueError(
                "arc_storyboard must be an arc_storyboard_plan artifact "
                f"(got artifact_type={arc_storyboard.get('artifact_type')!r})"
            )
        sb_series = str(arc_storyboard.get("series_id") or "")
        sc_series = str(chapter_script.get("series_id") or series_id or "")
        if sb_series and sc_series and sb_series != sc_series:
            raise ValueError(
                f"arc_storyboard series_id {sb_series!r} does not match "
                f"chapter script series_id {sc_series!r}"
            )
        sb_chapter = str(arc_storyboard.get("chapter_id") or "")
        sc_chapter = str(chapter_script.get("chapter_id") or chapter_id or "")
        if sb_chapter and sc_chapter and sb_chapter != sc_chapter:
            raise ValueError(
                f"arc_storyboard chapter_id {sb_chapter!r} does not match "
                f"chapter script chapter_id {sc_chapter!r}"
            )
        storyboard_divergences = compute_storyboard_divergences(arc_storyboard, chapter_script)
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

    # ── Panel iteration source: storyboard page map when present (count +
    # ordering authority), else the script pages verbatim (legacy). ──
    panel_iter: list[tuple[dict[str, Any], dict[str, Any] | None]]
    if arc_storyboard is not None:
        script_by_id = {
            str(p.get("panel_id") or ""): p
            for p in iter_panels_from_chapter_script(chapter_script)
        }
        default_locale = chapter_script.get("default_locale") or chapter_script.get("locale")
        panel_iter = []
        for sb_panel in arc_storyboard.get("panels") or []:
            sb_pid = str(sb_panel.get("panel_id") or "")
            merged = _merge_storyboard_panel(
                sb_panel,
                script_by_id.get(sb_pid),
                default_locale=str(default_locale) if default_locale else None,
                divergences=storyboard_divergences,
            )
            panel_iter.append((merged, _storyboard_block(sb_panel)))
        for row in storyboard_divergences:
            logger.warning(
                "storyboard divergence [%s] %s: storyboard wins (%s)",
                row.get("type"),
                row.get("panel_id") or row.get("page_id"),
                row.get("resolution"),
            )
    else:
        panel_iter = [
            (panel, None) for panel in iter_panels_from_chapter_script(chapter_script)
        ]

    panels_out: list[dict[str, Any]] = []
    for panel, sb_block in panel_iter:
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
        # Storyboard provenance: the panel scaffold was driven by the arc
        # storyboard (story_move/visual_proof/information_delta carried for
        # downstream assembly + audit; absent on the legacy path).
        if sb_block is not None:
            panel_doc["storyboard"] = sb_block
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
    # Storyboard-consumption provenance (only when a storyboard drove the build).
    if arc_storyboard is not None:
        out["storyboard_driven"] = True
        if arc_storyboard_ref:
            out["arc_storyboard_ref"] = str(arc_storyboard_ref)
        out["storyboard_divergences"] = storyboard_divergences
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
