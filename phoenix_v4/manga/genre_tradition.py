"""Genre drawing-tradition tokens for the production panel-prompt compiler.

The repo carries a deep, per-genre drawing-tradition cookbook
(``config/manga/drawing_tradition_per_genre.yaml`` — A_line / B_ink /
C_expression / D_framing / E_palette / F_forbidden / G_mangaka / H_token_mapping)
plus a cross-genre blend registry (``config/manga/cross_genre_blending_rules.yaml``).
Until now that knowledge was consumed **only** by the standalone character-
individuation prompt builder (``scripts/manga/character_individuation/
prompt_builder.py``), and even there only as a side-effect of axis-based
character individuation. The production chapter-DAG compiler
(``phoenix_v4.manga.chapter.visual_from_script.compile_panel_prompts_from_chapter_script``)
folded those tokens in **only** when a series ``character_design`` resolved —
so a Devotion/healing chapter with no resolvable character design rendered in
the bare ``style_id`` archetype (default ``dark_psychological``) with **zero**
iyashikei tradition tokens. That is the "healing rendered like the wrong
tradition" failure (its mirror: "horror rendered like slice-of-life").

This module makes the genre drawing-tradition a **first-class** prompt input,
decoupled from character individuation: given a ``genre_id`` it returns the
render-ready positive/negative tradition tokens for the routed engine. The
production compiler folds them into **every** panel whenever a genre is known —
whether or not a character_design exists.

Token source priority (positive):
    1. ``H_token_mapping[base_model].positive`` — the operator-curated,
       render-ready, engine-specific string (e.g. healing/flux_schnell =
       "serene watercolor manga page, sparse pen-and-ink, soft pastel wash…").
       This is the richest signal and was previously unused.
    2. Fallback when no H mapping for that engine: synthesise from
       ``A_line_tradition`` (line_weight_profile / ink_density), a palette
       register key, and the first ``G_mangaka_exemplars`` name.

Negatives:
    * ``H_token_mapping[base_model].negative`` when present, else
      ``F_forbidden_drift_patterns`` — the per-genre anti-drift list (e.g.
      psychological_horror forbids "iyashikei white space, soft lighting").

Cross-genre: when a ``secondary_genre`` differs from the primary, the
``cross_genre_blending_rules`` ``blend_signature`` (or ``token_qualifier``) is
appended to the positives.

Everything is fail-open: missing config, an unknown genre, or a
``deferred_phase2`` genre block yields empty token lists so the caller keeps
its legacy prompt verbatim.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRADITION_PATH = REPO_ROOT / "config" / "manga" / "drawing_tradition_per_genre.yaml"
DEFAULT_BLENDING_PATH = REPO_ROOT / "config" / "manga" / "cross_genre_blending_rules.yaml"
DEFAULT_CANONICAL_GENRES_PATH = REPO_ROOT / "config" / "manga" / "canonical_genre_list.yaml"
DEFAULT_COOKBOOK_PATH = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook.yaml"

# engine_router / builder base_model ids that may key into H_token_mapping.
# These mirror the keys used in drawing_tradition_per_genre.yaml H_token_mapping.
_H_ENGINE_KEYS = ("flux_schnell", "qwen_image", "animagine_xl_4_0", "animagine")


@lru_cache(maxsize=1)
def _genre_aliases() -> dict[str, str]:
    """Inbound alias map from canonical_genre_list.yaml (fail-open)."""
    data = _load_yaml(str(DEFAULT_CANONICAL_GENRES_PATH))
    raw = data.get("aliases") or {}
    out: dict[str, str] = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            if isinstance(key, str) and isinstance(value, str):
                out[key.strip().lower()] = value.strip().lower()
    return out


def _normalize_genre_id(genre_id: str | None) -> str | None:
    if not genre_id:
        return None
    key = str(genre_id).strip().lower().replace("-", "_").replace(" ", "_")
    return key or None


def resolve_canonical_genre(genre_id: str | None) -> str | None:
    """Map inbound genre ids to canonical taxonomy/pacing ids."""
    key = _normalize_genre_id(genre_id)
    if not key:
        return None
    return _genre_aliases().get(key, key)


def resolve_tradition_genre(genre_id: str | None) -> str | None:
    """Return the genre id that owns a deep drawing-tradition block, else canonical."""
    key = _normalize_genre_id(genre_id)
    if not key:
        return None
    tradition = _load_yaml(str(DEFAULT_TRADITION_PATH))
    genres = tradition.get("genres")
    if isinstance(genres, dict):
        block = genres.get(key)
        if isinstance(block, dict) and block.get("status") != "deferred_phase2":
            return key
    canonical = resolve_canonical_genre(genre_id)
    if canonical and cookbook_entry(canonical):
        return canonical
    return canonical


def cookbook_entry(
    genre_id: str | None,
    *,
    cookbook_path: Path | None = None,
) -> dict[str, Any] | None:
    """Return the manga-panel cookbook block for *genre_id*, or None (fail-open)."""
    key = resolve_canonical_genre(genre_id) or _normalize_genre_id(genre_id)
    if not key:
        return None
    doc = _load_yaml(str(cookbook_path or DEFAULT_COOKBOOK_PATH))
    genres = doc.get("genres")
    if not isinstance(genres, dict):
        return None
    block = genres.get(key)
    return block if isinstance(block, dict) else None


def locale_overlay_tokens(
    locale: str | None,
    *,
    cookbook_path: Path | None = None,
) -> tuple[str | None, list[str]]:
    """Return (register_add, avoid_list) for a locale overlay from the cookbook."""
    if not locale:
        return None, []
    doc = _load_yaml(str(cookbook_path or DEFAULT_COOKBOOK_PATH))
    overlays = doc.get("locale_overlays")
    if not isinstance(overlays, dict):
        return None, []
    block = overlays.get(str(locale).strip())
    if not isinstance(block, dict):
        return None, []
    reg = block.get("register_add")
    register_add = reg.strip() if isinstance(reg, str) and reg.strip() else None
    avoid_raw = block.get("avoid") or []
    avoid: list[str] = []
    if isinstance(avoid_raw, list):
        for item in avoid_raw:
            if isinstance(item, str) and item.strip():
                avoid.append(item.strip())
    return register_add, avoid


def preferred_panel_model(genre_id: str | None) -> str:
    """Preferred base-model id from the manga-panel cookbook (Qwen-primary default)."""
    entry = cookbook_entry(genre_id)
    if entry:
        model = entry.get("preferred_model")
        if isinstance(model, str) and model.strip():
            return model.strip()
    doc = _load_yaml(str(DEFAULT_COOKBOOK_PATH))
    default = doc.get("default_panel_model")
    if isinstance(default, str) and default.strip():
        return default.strip()
    return "qwen_image"


@lru_cache(maxsize=4)
def _load_yaml(path_str: str) -> dict[str, Any]:
    """Load + cache a YAML config; return {} on any failure (fail-open)."""
    try:
        data = yaml.safe_load(Path(path_str).read_text())
        return data if isinstance(data, dict) else {}
    except Exception as exc:  # pragma: no cover - I/O / parse guard
        logger.debug("genre_tradition: could not load %s (%s)", path_str, exc)
        return {}


def _h_token_positive_negative(block: dict[str, Any], base_model: str) -> tuple[str | None, str | None]:
    """Return (positive, negative) from H_token_mapping for the given engine.

    Tries the exact base_model key first, then the ``animagine`` short alias for
    ``animagine_xl_4_0`` (the config uses both ``animagine_xl_4_0`` and the
    ``animagine_starter`` short form across genres). Returns (None, None) when
    no usable mapping exists for this engine.
    """
    h = block.get("H_token_mapping")
    if not isinstance(h, dict):
        return None, None
    candidate_keys = [base_model]
    if base_model == "animagine_xl_4_0":
        candidate_keys.append("animagine")
    for key in candidate_keys:
        entry = h.get(key)
        if isinstance(entry, dict):
            pos = entry.get("positive")
            neg = entry.get("negative")
            pos = pos.strip() if isinstance(pos, str) and pos.strip() else None
            neg = neg.strip() if isinstance(neg, str) and neg.strip() else None
            if pos or neg:
                return pos, neg
        elif isinstance(entry, str) and entry.strip():
            # Some genres carry a bare "<engine>_starter: <string>" positive.
            return entry.strip(), None
    # Bare "<engine>_starter" positive strings (e.g. animagine_starter, qwen_starter).
    for key, val in h.items():
        if isinstance(val, str) and val.strip() and base_model.split("_")[0] in str(key):
            return val.strip(), None
    return None, None


def _synth_positive_from_blocks(block: dict[str, Any]) -> list[str]:
    """Fallback positive tokens when no H_token_mapping exists for the engine.

    Mirrors the standalone prompt_builder._genre_tokens heuristic: line
    tradition + ink density + a palette register key + first mangaka exemplar.
    """
    out: list[str] = []
    line = block.get("A_line_tradition")
    if isinstance(line, dict):
        lwp = line.get("line_weight_profile")
        if isinstance(lwp, str):
            out.append(f"{lwp.replace('_', ' ')} line work")
        ink = line.get("ink_density")
        if isinstance(ink, str):
            out.append(f"{ink.replace('_', ' ')} inking")
    for key in ("E_color_treatment", "D_palette", "E_palette", "palette"):
        pal = block.get(key)
        if isinstance(pal, dict):
            for sub in ("register", "palette", "dominant_value", "tonal_range"):
                v = pal.get(sub)
                if isinstance(v, str):
                    out.append(v.replace("_", " "))
                    break
            break
    exemplars = block.get("G_mangaka_exemplars") or block.get("mangaka_exemplars") or []
    if isinstance(exemplars, list) and exemplars:
        first = exemplars[0]
        if isinstance(first, dict) and first.get("name"):
            out.append(f"in the style of {first['name']}")
        elif isinstance(first, str):
            out.append(f"in the style of {first}")
    return out


def _forbidden_from_block(block: dict[str, Any]) -> list[str]:
    """F_forbidden_drift_patterns → flat negative-token list (fail-open)."""
    items = block.get("F_forbidden_drift_patterns") or block.get("forbidden_drift_patterns") or []
    out: list[str] = []
    if isinstance(items, list):
        for it in items:
            if isinstance(it, str) and it.strip():
                out.append(it.strip())
    return out


def _blend_signature(blending_config: dict[str, Any], primary: str, secondary: str | None) -> str | None:
    """Cross-genre blend qualifier (blend_signature / token_qualifier), or None."""
    if not secondary or secondary == primary:
        return None
    pairs = blending_config.get("pairs")
    if not isinstance(pairs, dict):
        return None
    for key in (f"{primary}_plus_{secondary}", f"{secondary}_plus_{primary}"):
        rule = pairs.get(key)
        if isinstance(rule, dict):
            qualifier = rule.get("blend_signature") or rule.get("token_qualifier")
            if isinstance(qualifier, str) and qualifier.strip():
                return qualifier.strip()
    return None


def genre_tradition_tokens(
    genre_id: str | None,
    *,
    secondary_genre: str | None = None,
    base_model: str = "qwen_image",
    tradition_path: Path | None = None,
    blending_path: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Return ``(positive_tokens, negative_tokens)`` for a genre's drawing tradition.

    Fail-open: returns ``([], [])`` when ``genre_id`` is empty, the config is
    missing/unparseable, the genre is unknown, or the genre block is
    ``deferred_phase2``. ``base_model`` selects the H_token_mapping engine
    variant (one of flux_schnell / qwen_image / animagine_xl_4_0).
    """
    if not genre_id:
        return [], []
    tradition = _load_yaml(str(tradition_path or DEFAULT_TRADITION_PATH))
    genres = tradition.get("genres")
    if not isinstance(genres, dict):
        return [], []
    block = genres.get(genre_id)
    if not isinstance(block, dict) or block.get("status") == "deferred_phase2":
        return [], []

    positive: list[str] = []
    negative: list[str] = []

    h_pos, h_neg = _h_token_positive_negative(block, base_model)
    if h_pos:
        positive.append(h_pos)
    else:
        positive.extend(_synth_positive_from_blocks(block))
    if h_neg:
        negative.append(h_neg)
    else:
        negative.extend(_forbidden_from_block(block))

    blending = _load_yaml(str(blending_path or DEFAULT_BLENDING_PATH))
    blend = _blend_signature(blending, genre_id, secondary_genre)
    if blend:
        positive.append(blend)

    return positive, negative
