"""
V1.1 allocation → ``batch_runner --activate`` markdown plan generator.

Spec: ``docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`` §2.1
Cap entry: ``CONDUCTOR-V3-DISPATCH-BRIDGE-V1-01``

Joins:
  - allocation TSV (``artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv``)
  - series themes YAML (``artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml``)
  - brand style canon (``_CATALOG_BRAND_STYLE_CANON`` in ``generate_manga_catalog.py``)
  - LoRA plans (``config/manga/brand_lora_plans.yaml``)
  - cover authoring rules + text-free negative prompt (``config/catalog_planning/brand_cover_art_specs.yaml``)

Emits one markdown file per locale at
``artifacts/manga/conductor_v3_<run_id>/plan_<locale>.md`` containing
` ```batch ` blocks consumed by ``scripts/image_generation/batch_runner.py``.

Cover prompts are TEXT-FREE per ``feedback_cover_text_overlay_two_stage``:
literal series titles MUST NOT appear in the positive_prompt — PIL composites
typography downstream from the cover_text_overlay stage.

CLI:
    python3 scripts/catalog/v1_1_allocation_to_batch_plan.py \\
        --run-id <id> \\
        --output-dir <path> \\
        [--locale en_US|ja_JP|zh_TW|zh_CN] \\
        [--allocation-tsv <path>] \\
        [--series-themes <path>] \\
        [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog.v1_1_brand_allocation_loader import (  # noqa: E402
    default_allocation_tsv_path,
    load_v1_1_brand_allocation_plan,
)

DEFAULT_SERIES_THEMES = (
    REPO_ROOT
    / "artifacts"
    / "marketing"
    / "v1_1_25_brand_series_themes_2026-05-11.yaml"
)
DEFAULT_V1_2_THEMES_GLOB = "artifacts/marketing/v1_2_themes_*_cluster_*.yaml"
DEFAULT_LORA_PLANS = REPO_ROOT / "config" / "manga" / "brand_lora_plans.yaml"
DEFAULT_COVER_SPECS = (
    REPO_ROOT / "config" / "catalog_planning" / "brand_cover_art_specs.yaml"
)

# Mirror of ``_CATALOG_BRAND_STYLE_CANON`` from
# ``scripts/catalog/generate_manga_catalog.py``. Imported via attribute lookup
# at runtime so a divergence raises rather than silently shadows.
_DEFAULT_STYLE_CANON: dict[str, str] = {
    "sleep_repair": "sleep_restoration",
    "panic_first_aid": "stabilizer",
    "gen_z_grounding": "digital_ground",
    "grief_companion": "body_memory",
    "inner_security": "relational_calm",
    "bright_presence": "stillness_press",
}

LOCALE_BCP47: dict[str, str] = {
    "en_US": "en-US",
    "ja_JP": "ja-JP",
    "zh_TW": "zh-TW",
    "zh_CN": "zh-CN",
}

WORKFLOW_BY_SURFACE: dict[str, str] = {
    "cover": "flux_txt2img_manga.json",
    "panel": "qwen_image_txt2img_manga.json",
}

DISPATCH_BY_SURFACE: dict[str, str] = {
    # AMENDMENT-2026-05-10-PATH-BY-WORKFLOW: FLUX cover → Pearl Star;
    # Qwen panel → RunComfy.
    "cover": "pearl_star",
    "panel": "runcomfy",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing input YAML: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_v1_2_series_themes(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Load the 20 V1.2 cluster YAML files and re-shape into the V1.1 contract.

    V1.2 cluster files are flat per (locale, cluster):
        schema_version: "1.2"
        locale: <locale>
        cluster: <cluster>
        series:
          - series_id: <brand>__<locale>__<slug>
            brand_id: <brand>
            locale: <locale>
            series_title: ...
            series_logline: ...
            series_description: ...
            magical_register: ...
            serial_engine: ...
            ...

    V1.1 contract expected by ``_series_for`` is nested:
        brands:
          <brand>:
            series:
              <locale>:
                - series_title: ...
                  arc_shape: ...
                  emotional_throughline: ...
                  surface_priority: ...

    Mapping:
      series_title          -> series_title (passthrough)
      serial_engine         -> arc_shape   (the long-arc structural pattern)
      series_logline        -> emotional_throughline (1-sentence feel hook)
      reading_platform_fit  -> surface_priority (webtoon_vertical | manga_traditional | both)

    Additional V1.2 metadata (magical_register, portal_mechanic, persona_archetype,
    long_arc_spine, opening_5_volume_arc, etc.) is preserved on the per-series
    dict so downstream consumers can pick it up if desired.

    Glob pattern: ``DEFAULT_V1_2_THEMES_GLOB`` (artifacts/marketing/v1_2_themes_*_cluster_*.yaml).
    Expects 20 files (5 clusters × 4 locales). Missing files do NOT raise — the
    bridge will fall back to synthetic concepts per ``_series_for`` for any
    (brand, locale) pair without a V1.2 entry.
    """
    out: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = {"brands": {}}
    file_count = 0
    for path in sorted(repo_root.glob(DEFAULT_V1_2_THEMES_GLOB)):
        file_count += 1
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for series in data.get("series", []) or []:
            brand_id = series.get("brand_id")
            locale = series.get("locale") or data.get("locale")
            if not brand_id or not locale:
                continue
            v1_1_shape = {
                "series_title": series.get("series_title", ""),
                "arc_shape": series.get("serial_engine", ""),
                "emotional_throughline": series.get("series_logline", ""),
                "surface_priority": series.get("reading_platform_fit", "balanced"),
                # V1.2 passthrough metadata (preserved for downstream consumers):
                "_v1_2": {
                    "series_id": series.get("series_id"),
                    "series_description": series.get("series_description"),
                    "magical_register": series.get("magical_register"),
                    "serial_engine": series.get("serial_engine"),
                    "portal_mechanic": series.get("portal_mechanic"),
                    "daily_life_anchor": series.get("daily_life_anchor"),
                    "episodic_frame_per_volume": series.get("episodic_frame_per_volume"),
                    "persona_archetype": series.get("persona_archetype"),
                    "long_arc_spine": series.get("long_arc_spine"),
                    "volume_runway_target": series.get("volume_runway_target"),
                    "opening_5_volume_arc": series.get("opening_5_volume_arc"),
                    "genre_family": series.get("genre_family"),
                    "comp_titles": series.get("comp_titles"),
                    "reader_promise": series.get("reader_promise"),
                    "marketing_angle": series.get("marketing_angle"),
                    "emotional_engine": series.get("emotional_engine"),
                    "audience": series.get("audience"),
                    "source_version": "v1.2",
                    "source_path": str(path.relative_to(repo_root)),
                },
            }
            brand_block = out["brands"].setdefault(brand_id, {"series": {}})
            brand_block["series"].setdefault(locale, []).append(v1_1_shape)
    out["_meta"] = {
        "source_version": "v1.2",
        "files_loaded": file_count,
        "glob_pattern": DEFAULT_V1_2_THEMES_GLOB,
    }
    return out


def _load_style_canon() -> dict[str, str]:
    """Load ``_CATALOG_BRAND_STYLE_CANON`` from the catalog generator.

    Falls back to ``_DEFAULT_STYLE_CANON`` if the import path changes — this
    keeps the bridge testable without importing the full generator's heavy
    deps tree.
    """
    try:
        from scripts.catalog import generate_manga_catalog as _gmc
        canon = getattr(_gmc, "_CATALOG_BRAND_STYLE_CANON", None)
        if isinstance(canon, dict) and canon:
            return dict(canon)
    except Exception:
        pass
    return dict(_DEFAULT_STYLE_CANON)


def _strip_locale_suffix(brand: str) -> str:
    for suf in ("_tw", "_cn", "_hk", "_sg"):
        if brand.endswith(suf):
            return brand[: -len(suf)]
    return brand


def _resolve_style_lora(
    brand: str,
    style_loras: dict[str, Any],
    canon: dict[str, str],
) -> str:
    if brand in style_loras:
        return f"brand_lora_plans.brand_style_loras.{brand}"
    base = _strip_locale_suffix(brand)
    if base in style_loras:
        return f"brand_lora_plans.brand_style_loras.{base}"
    canon_key = canon.get(base)
    if canon_key and canon_key in style_loras:
        return f"brand_lora_plans.brand_style_loras.{canon_key}"
    return ""


def _resolve_character_lora(
    brand: str,
    cover_specs: dict[str, Any],
    char_loras: dict[str, Any],
) -> str:
    """Use cover_specs to find the brand's character_lora trigger word, then
    map back to the trigger_word entry under brand_lora_plans.character_loras.
    """
    base = _strip_locale_suffix(brand)
    spec = (cover_specs.get("brands") or {}).get(base) or {}
    trigger = (spec.get("character_lora") or "").strip()
    if not trigger:
        return ""
    for tname, t in (char_loras or {}).items():
        if isinstance(t, dict) and t.get("trigger_word") == trigger:
            return f"brand_lora_plans.character_loras.{tname}"
    return ""


def _batch_id(
    brand: str,
    locale: str,
    source_surface: str,
    surface: str,
    sidx: int,
    eidx: int,
) -> str:
    """Deterministic batch id for one render unit.

    ``source_surface`` is the allocation-row surface (``ebook`` | ``manga``)
    that produced this batch. ``surface`` is the render surface (``cover`` |
    ``panel``). Both segments participate in the hash so an ebook→cover and
    a manga→cover for the SAME (brand, locale, series_idx, episode_idx)
    receive distinct batch_ids — preventing the 724 duplicate batches per
    full plan that Pearl_Conductor v3 (run_id ``..._t0103``) caught at
    checkpoint init. See AMENDMENT-2026-05-12-COVER-UNIQUENESS in
    ``docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md``.
    """
    raw = f"{brand}|{locale}|{source_surface}|{surface}|{sidx}|{eidx}".encode("utf-8")
    return "v3_" + hashlib.sha1(raw).hexdigest()[:14]


def _normalize_neg_prompt(text: str) -> str:
    return " ".join((text or "").split())


def _series_for(
    brand: str,
    locale: str,
    series_themes: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return the per-locale series concept list for ``brand``.

    Series themes YAML covers only the 25 V1.1 brands. For the 12 V1.0 teacher
    brands not in the YAML, returns a synthetic single concept so the bridge
    still emits a batch (allocation TSV is the source of truth for cell
    inclusion; missing themes are NOT a join failure for V1.0 cells).
    """
    brand_block = (series_themes.get("brands") or {}).get(brand) or {}
    series_by_locale = (brand_block.get("series") or {})
    out = series_by_locale.get(locale)
    if isinstance(out, list) and out:
        return out
    # synthetic fallback for V1.0 brands or missing locale entries
    return [
        {
            "series_title": f"{brand}_series",
            "arc_shape": "default arc",
            "emotional_throughline": "brand throughline (themes YAML not present)",
            "surface_priority": "balanced",
        }
    ]


def _cover_positive_prompt(
    brand: str,
    cover_specs: dict[str, Any],
    series_concept: dict[str, Any],
) -> str:
    """Author cover prompt WITHOUT literal series titles.

    Per ``feedback_cover_text_overlay_two_stage``: FLUX renders imagery only.
    Title text is composited downstream by PIL. We strip the title and inject
    the emotional throughline + arc_shape as compositional cues.
    """
    base = _strip_locale_suffix(brand)
    spec = (cover_specs.get("brands") or {}).get(base) or {}
    template = (spec.get("prompt_template") or "").strip()
    throughline = str(series_concept.get("emotional_throughline") or "").strip()
    arc = str(series_concept.get("arc_shape") or "").strip()
    # NEVER include series_title here — covered by tests.
    composition_cue = " ".join(p for p in (arc, throughline) if p)
    if template:
        # template uses {format} {title_area} {colophon_area} placeholders;
        # render with format=manga_cover and empty typography slots so FLUX
        # leaves the title region as negative space for PIL overlay.
        rendered = template.format(
            format="manga cover",
            title_area="upper third reserved as clear negative space for typography overlay",
            colophon_area="bottom edge reserved for brand colophon overlay",
        )
        return _normalize_neg_prompt(f"{rendered}, compositional cue: {composition_cue}")
    return _normalize_neg_prompt(
        f"manga cover for {base} brand, vertical 800x1200 composition, "
        f"compositional cue: {composition_cue}, "
        f"upper third reserved as clear negative space for typography overlay, "
        f"bottom edge reserved for brand colophon overlay"
    )


def _panel_positive_prompt(
    brand: str,
    locale: str,
    series_concept: dict[str, Any],
    episode_idx: int,
) -> str:
    """Panel prompts may carry concept + locale-tonal cues; titles still NOT
    embedded (panels render imagery, not cover typography)."""
    throughline = str(series_concept.get("emotional_throughline") or "").strip()
    arc = str(series_concept.get("arc_shape") or "").strip()
    return _normalize_neg_prompt(
        f"vertical webtoon panel, {brand} brand visual identity, "
        f"locale {locale} tonal register, episode {episode_idx} beat, "
        f"arc context: {arc}, throughline: {throughline}"
    )


def build_batches_for_cell(
    *,
    brand: str,
    locale: str,
    surface: str,
    series_count: int,
    episodes_per_series: int,
    priority_phase: str,
    series_themes: dict[str, Any],
    cover_specs: dict[str, Any],
    style_loras: dict[str, Any],
    char_loras: dict[str, Any],
    canon: dict[str, str],
    run_id: str,
) -> list[dict[str, Any]]:
    """Expand one allocation cell into the per-unit batch dicts.

    For each series_idx:
      - 1 cover batch (always — every series needs a cover)
      - For ``surface == 'manga'``: ``episodes_per_series`` panel batches
      - For ``surface == 'ebook'``: 0 panel batches (ebook ships cover only
        through this bridge; ebook chapter prose is a separate Tier 2 path)
    """
    batches: list[dict[str, Any]] = []
    series_list = _series_for(brand, locale, series_themes)
    bcp47 = LOCALE_BCP47.get(locale, locale)
    style_lora = _resolve_style_lora(brand, style_loras, canon)
    char_lora = _resolve_character_lora(brand, cover_specs, char_loras)
    neg = _normalize_neg_prompt(cover_specs.get("text_free_negative_prompt", "") or "")
    out_root = (
        f"artifacts/manga/conductor_v3_{run_id}/{locale}"
    )

    # source_surface tags the allocation row (ebook|manga) so cover batches
    # for the SAME brand+locale+series_idx but different source surfaces
    # diverge — one cover per surface row. Without this segment, an ebook
    # cover and a manga cover for (brand, locale, sidx=0) collide on
    # batch_id and output_path. See AMENDMENT-2026-05-12-COVER-UNIQUENESS.
    for sidx in range(series_count):
        concept = series_list[sidx % len(series_list)]
        # --- cover batch ---
        cover_id = _batch_id(brand, locale, surface, "cover", sidx, 0)
        batches.append({
            "batch_id": cover_id,
            "brand_id": brand,
            "locale": bcp47,
            "surface": "cover",
            "source_surface": surface,
            "dispatch_path": DISPATCH_BY_SURFACE["cover"],
            "workflow_template": WORKFLOW_BY_SURFACE["cover"],
            "asset_type": "manga_cover" if surface == "manga" else "kdp_cover",
            "positive_prompt": _cover_positive_prompt(brand, cover_specs, concept),
            "negative_prompt": neg,
            "style_lora": style_lora,
            "character_lora": char_lora,
            "output_path": f"{out_root}/{surface}/{cover_id}.png",
            "series_idx": sidx,
            "episode_idx": 0,
            "priority_phase": priority_phase,
            "sequence": sidx * 100,
        })
        # --- panel batches (manga surface only) ---
        if surface == "manga":
            for eidx in range(1, episodes_per_series + 1):
                # Defensive: include source_surface segment for symmetry with
                # cover batch_ids even though episode_idx already disambiguates
                # panels (no ebook→panel rows exist today, but this prevents
                # future surface additions from re-introducing collisions).
                panel_id = _batch_id(brand, locale, surface, "panel", sidx, eidx)
                batches.append({
                    "batch_id": panel_id,
                    "brand_id": brand,
                    "locale": bcp47,
                    "surface": "panel",
                    "source_surface": surface,
                    "dispatch_path": DISPATCH_BY_SURFACE["panel"],
                    "workflow_template": WORKFLOW_BY_SURFACE["panel"],
                    "asset_type": "manga_panel",
                    "positive_prompt": _panel_positive_prompt(brand, locale, concept, eidx),
                    "negative_prompt": neg,
                    "style_lora": style_lora,
                    "character_lora": char_lora,
                    "output_path": f"{out_root}/{surface}/{panel_id}.png",
                    "series_idx": sidx,
                    "episode_idx": eidx,
                    "priority_phase": priority_phase,
                    "sequence": sidx * 100 + eidx,
                })
    return batches


def batches_to_markdown(batches: list[dict[str, Any]], *, locale: str, run_id: str) -> str:
    """Serialize batches to the ` ```batch ` markdown format.

    Order of fields is stable for diffability. Values that contain commas are
    NOT split downstream because batch_runner.load_plan only splits when a
    raw value contains a comma AND the key is not a known scalar; we therefore
    quote nothing and trust load_plan's per-key parsing.
    """
    lines: list[str] = [
        f"# Pearl_Conductor v3 dispatch plan — locale {locale}",
        "",
        f"**run_id:** `{run_id}`",
        f"**locale:** `{locale}`",
        f"**batch_count:** {len(batches)}",
        "",
        "Spec: `docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`",
        "",
        "---",
        "",
    ]
    field_order = (
        "batch_id", "brand_id", "locale", "surface", "source_surface",
        "dispatch_path", "workflow_template", "asset_type", "positive_prompt",
        "negative_prompt", "style_lora", "character_lora", "output_path",
        "series_idx", "episode_idx", "priority_phase", "sequence",
    )
    for b in batches:
        lines.append("```batch")
        for k in field_order:
            if k not in b:
                continue
            v = b[k]
            lines.append(f"{k}: {v}")
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_plans(
    *,
    run_id: str,
    output_dir: Path,
    locale_filter: str | None = None,
    allocation_tsv: Path | None = None,
    series_themes_path: Path | None = None,
    cover_specs_path: Path | None = None,
    lora_plans_path: Path | None = None,
    dry_run: bool = False,
    use_v1_2_themes: bool = False,
) -> dict[str, Any]:
    alloc = load_v1_1_brand_allocation_plan(
        allocation_tsv or default_allocation_tsv_path(REPO_ROOT)
    )
    if use_v1_2_themes:
        series_themes = _load_v1_2_series_themes(REPO_ROOT)
    else:
        series_themes = _load_yaml(series_themes_path or DEFAULT_SERIES_THEMES)
    cover_specs = _load_yaml(cover_specs_path or DEFAULT_COVER_SPECS)
    lora_plans = _load_yaml(lora_plans_path or DEFAULT_LORA_PLANS)
    style_loras = lora_plans.get("brand_style_loras") or {}
    char_loras = lora_plans.get("character_loras") or {}
    canon = _load_style_canon()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    by_locale: dict[str, list[dict[str, Any]]] = {}
    for (brand, locale, surface), cell in alloc.items():
        if locale_filter and locale != locale_filter:
            continue
        cell_batches = build_batches_for_cell(
            brand=brand,
            locale=locale,
            surface=surface,
            series_count=int(cell["series_count"]),
            episodes_per_series=int(cell["episodes_per_series"]),
            priority_phase=str(cell["priority_phase"]),
            series_themes=series_themes,
            cover_specs=cover_specs,
            style_loras=style_loras,
            char_loras=char_loras,
            canon=canon,
            run_id=run_id,
        )
        by_locale.setdefault(locale, []).extend(cell_batches)

    written: list[str] = []
    summary: dict[str, Any] = {
        "run_id": run_id,
        "dry_run": dry_run,
        "output_dir": str(output_dir),
        "locales": {},
        "total_batches": 0,
        "total_cells": len(alloc) if not locale_filter else sum(
            1 for k in alloc if k[1] == locale_filter
        ),
    }
    for locale in sorted(by_locale):
        batches = by_locale[locale]
        md = batches_to_markdown(batches, locale=locale, run_id=run_id)
        out_path = output_dir / f"plan_{locale}.md"
        out_path.write_text(md, encoding="utf-8")
        written.append(str(out_path))
        cover_count = sum(1 for b in batches if b["surface"] == "cover")
        panel_count = sum(1 for b in batches if b["surface"] == "panel")
        summary["locales"][locale] = {
            "plan_path": str(out_path),
            "batch_count": len(batches),
            "cover_count": cover_count,
            "panel_count": panel_count,
        }
        summary["total_batches"] += len(batches)
    summary["plan_files"] = written
    return summary


def _cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="V1.1 allocation → batch_runner --activate plan generator",
    )
    p.add_argument("--run-id", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument(
        "--locale",
        choices=["en_US", "ja_JP", "zh_TW", "zh_CN"],
        default=None,
    )
    p.add_argument("--allocation-tsv", default=None)
    p.add_argument("--series-themes", default=None)
    p.add_argument("--cover-specs", default=None)
    p.add_argument("--lora-plans", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--v1-2",
        action="store_true",
        dest="use_v1_2_themes",
        help="Load themes from the 20 V1.2 cluster YAML files instead of the V1.1 themes YAML.",
    )
    args = p.parse_args(argv)
    try:
        summary = generate_plans(
            run_id=args.run_id,
            output_dir=Path(args.output_dir),
            locale_filter=args.locale,
            allocation_tsv=Path(args.allocation_tsv) if args.allocation_tsv else None,
            series_themes_path=Path(args.series_themes) if args.series_themes else None,
            cover_specs_path=Path(args.cover_specs) if args.cover_specs else None,
            lora_plans_path=Path(args.lora_plans) if args.lora_plans else None,
            dry_run=args.dry_run,
            use_v1_2_themes=args.use_v1_2_themes,
        )
    except FileNotFoundError as e:
        print(f"ERROR (input): {e}", file=sys.stderr)
        return 2
    except (KeyError, ValueError) as e:
        print(f"ERROR (join): {e}", file=sys.stderr)
        return 3
    json.dump(summary, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli(sys.argv[1:]))
