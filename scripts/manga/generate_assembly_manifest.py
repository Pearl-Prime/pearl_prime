#!/usr/bin/env python3
"""Generate assembly manifests from continuity_state + bank assets (M5 lane).

Closes the OPD-135 Milestone C gap between continuity_state_generator.py
(panel YAMLs) and assemble_from_bank.py (offline compositing). Reuses the
V4 unique-render hash logic so panel→L0/L2 keys match v4_render_cache paths.

Pipeline:
    continuity_state/<episode>/*.yaml
        + profile configs (scene_inventory, iyashikei templates)
        + v4_render_cache/<episode>/L0|L2 (REAL when on disk)
        → assembly_manifests/<episode>_from_continuity.yaml
        → assembly_manifests/<episode>_bank_gaps.json

Fail-closed: panels with missing REAL bank assets are listed in bank_gaps.json
and omitted from the manifest unless --include-gaps (emits INTERIM placeholders
for wiring tests only — never presentable as final art).

Tier 1. No LLM. No network. No paid APIs.

Usage:
    PYTHONPATH=. python3 scripts/manga/generate_assembly_manifest.py \\
        --series stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \\
        --profile stillness_en_01 \\
        --episode ep_001 \\
        [--out artifacts/manga/<series>/assembly_manifests/ep_001_from_continuity.yaml] \\
        [--dry-run] [--include-gaps]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402
from composition_grammar import load_composition_meta  # noqa: E402
from render_v4_episode import build_render_manifest, load_configs, load_panel_states  # noqa: E402

# MANGA_COMPOSITION_GRAMMAR_SPEC.md §6.3 archetype → shot_type lookup
ARCHETYPE_SHOT_TYPE: dict[str, str] = {
    "sparse_establishing_wide": "establishing",
    "morning_routine_sequence": "re_establish",
    "walking_in_thought_medium": "re_establish",
    "character_quiet_face": "reaction_emotion",
    "character_face_micro_tension": "reaction_emotion",
    "chest_breath_micro": "dialogue_bust",
    "tea_beat_close_up": "insert_object",
    "hand_table_micro": "insert_object",
    "dappled_light_hand": "insert_object",
    "phone_notification_macro": "insert_object",
    "food_preparation_overhead": "insert_object",
    "kettle_steam_macro": "insert_object",
    "seasonal_anchor_object": "insert_object",
    "window_light_threshold": "diegetic_cu",
    "pet_companion_micro": "insert_object",
    "long_drop_decompression": "pillow_ma",
    "miyazaki_ma_pause": "pillow_ma",
    "character_at_table_medium": "establishing",
    "shared_scene_medium": "establishing",
    "pendulation_pair_visual_rhyme": "closure_breath",
}

PANEL_ID_RE = re.compile(r"^ep\d{3}_\d{3}$")
MIN_REAL_BYTES = 50_000  # matches check_render_progress_bytes.py stub-as-done floor


def _load_panel_states_filtered(artifacts_series_id: str, episode_id: str) -> list[dict]:
    """Load continuity panels, excluding beatsheet sidecars."""
    raw = load_panel_states(artifacts_series_id, episode_id)
    return [p for p in raw if PANEL_ID_RE.match(str(p.get("panel_id", "")))]


def _archetype_bbox(configs: dict[str, Any], archetype: str | None) -> list[float] | None:
    if not archetype:
        return None
    arch = (configs.get("panel_templates") or {}).get("archetypes") or {}
    row = arch.get(archetype) or {}
    bbox = row.get("subject_placement_bbox")
    if isinstance(bbox, list) and len(bbox) == 4:
        return [float(v) for v in bbox]
    return None


def _shot_type(archetype: str | None) -> str | None:
    if not archetype:
        return None
    return ARCHETYPE_SHOT_TYPE.get(archetype)


def _l0_derivation(shot: str | None, *, l0_meta: dict | None = None,
                   l2_meta: dict | None = None) -> dict[str, Any] | None:
    if shot in ("dialogue_bust", "reaction_emotion"):
        return {"type": "defocus"}
    if shot == "pillow_ma":
        return {"type": "tone_gradient"}
    # G1 legality: bust/waist_up L2 over full_render L0 requires derived BG
    if l0_meta and l2_meta:
        bg = l0_meta.get("bg_class", "full_render")
        crop = l2_meta.get("crop_class", "")
        if bg == "full_render" and crop in ("bust", "waist_up", "diegetic_cu"):
            return {"type": "defocus"}
    return None


def _resolve_cache_asset(cache_dir: Path, layer_class: str, layer_id: str) -> Path | None:
    if layer_class == "L0":
        p = cache_dir / "L0" / f"{layer_id}.png"
    elif layer_class == "L2":
        p = cache_dir / "L2" / f"{layer_id}_alpha.png"
        if not p.is_file():
            p = cache_dir / "L2" / f"{layer_id}.png"
    else:
        return None
    return p if p.is_file() and p.stat().st_size >= MIN_REAL_BYTES else None


def _provenance_for(path: Path | None) -> tuple[str, str]:
    if path is None:
        return "INTERIM", "bank gap — asset not on disk or below byte floor"
    return "REAL", ""


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def generate(
    *,
    series_id: str,
    profile_id: str,
    episode_id: str,
    include_gaps: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    configs = load_configs(profile_id)
    panel_states = _load_panel_states_filtered(series_id, episode_id)
    if not panel_states:
        raise ValueError(f"no continuity panels under {series_id}/{episode_id}")

    render_manifest = build_render_manifest(panel_states, configs)
    cache_dir = REPO / "artifacts" / "manga" / series_id / "v4_render_cache" / episode_id

    panels_out: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    stats = {"panels_total": len(panel_states), "panels_complete": 0,
             "layers_real": 0, "layers_interim": 0, "layers_missing": 0}

    for panel in panel_states:
        pid = panel["panel_id"]
        mapping = render_manifest["panel_to_layers"].get(pid, {})
        archetype = mapping.get("archetype") or panel.get("archetype")
        shot = _shot_type(archetype)
        bbox = _archetype_bbox(configs, archetype)

        layers: list[dict[str, Any]] = []
        panel_gaps: list[str] = []

        l0_id = mapping.get("L0")
        l2_id = mapping.get("L2")
        l0_path = _resolve_cache_asset(cache_dir, "L0", l0_id) if l0_id else None
        l2_path = _resolve_cache_asset(cache_dir, "L2", l2_id) if l2_id else None
        l0_meta = load_composition_meta(l0_path) if l0_path else None
        l2_meta = load_composition_meta(l2_path) if l2_path else None

        if l0_id:
            prov, note = _provenance_for(l0_path)
            if prov == "REAL":
                stats["layers_real"] += 1
                layer: dict[str, Any] = {
                    "layer_class": "L0",
                    "asset": _rel(l0_path),
                    "provenance": "REAL",
                }
                deriv = _l0_derivation(shot, l0_meta=l0_meta, l2_meta=l2_meta)
                if deriv:
                    layer["derivation"] = deriv
                layers.append(layer)
            else:
                stats["layers_missing"] += 1
                panel_gaps.append(f"L0:{l0_id}")
                if include_gaps:
                    stats["layers_interim"] += 1
                    layers.append({
                        "layer_class": "L0",
                        "asset": f"artifacts/manga/{series_id}/image_bank_sprites/L0_MISSING_{l0_id}.png",
                        "provenance": "INTERIM",
                        "provenance_note": f"bank gap — enqueue L0 render for {l0_id}",
                    })

        if l2_id:
            prov, note = _provenance_for(l2_path)
            if prov == "REAL":
                stats["layers_real"] += 1
                l2_layer: dict[str, Any] = {
                    "layer_class": "L2",
                    "asset": _rel(l2_path),
                    "provenance": "REAL",
                }
                l0_has_deriv = any(
                    lyr.get("derivation") for lyr in layers if lyr.get("layer_class") == "L0"
                )
                if shot in ("establishing", "re_establish") and l0_meta and not l0_has_deriv:
                    l2_layer["anchor_slot"] = "seat_at_table"
                    l2_layer["grounding"] = {"contact_shadow": True, "occluder": True}
                # dialogue_bust/reaction_emotion: omit anchor_slot — assembler resolves
                # via panel shot_type → DEFAULT_ABSTRACT_STAGE_SLOT (§6.4 wiring)
                if bbox:
                    l2_layer["bbox_pct"] = bbox
                layers.append(l2_layer)
            else:
                stats["layers_missing"] += 1
                panel_gaps.append(f"L2:{l2_id}")
                if include_gaps and bbox:
                    stats["layers_interim"] += 1
                    layers.append({
                        "layer_class": "L2",
                        "asset": f"artifacts/manga/{series_id}/image_bank_sprites/L2_MISSING_{l2_id}.png",
                        "bbox_pct": bbox,
                        "provenance": "INTERIM",
                        "provenance_note": f"bank gap — enqueue L2 render for {l2_id}",
                    })

        if not layers:
            gaps.append({"panel_id": pid, "archetype": archetype, "gaps": panel_gaps or ["no_layers"]})
            continue

        if panel_gaps and not include_gaps:
            gaps.append({"panel_id": pid, "archetype": archetype, "gaps": panel_gaps})
            continue

        entry: dict[str, Any] = {"panel_id": pid, "layers": layers}
        if archetype:
            entry["archetype"] = archetype
        if shot:
            entry["shot_type"] = shot
        if panel.get("beat_type"):
            entry["beat_type"] = panel["beat_type"]
        panels_out.append(entry)
        if not panel_gaps:
            stats["panels_complete"] += 1

    manifest = {
        "schema_version": "1.0.0",
        "series_id": series_id,
        "episode_id": episode_id,
        "manifest_id": f"{episode_id}_from_continuity",
        "notes": (
            "Auto-generated from continuity_state via generate_assembly_manifest.py. "
            "REAL layers resolved from v4_render_cache when on disk. "
            "Panels with bank gaps are listed in the companion bank_gaps.json."
        ),
        "canvas": {"width": 1080, "height": 1920, "background_hex": "#FFFFFF"},
        "panels": panels_out,
    }

    gap_report = {
        "series_id": series_id,
        "episode_id": episode_id,
        "profile_id": profile_id,
        "cache_dir": _rel(cache_dir),
        "stats": stats,
        "unique_L0": len(render_manifest["L0"]),
        "unique_L2": len(render_manifest["L2"]),
        "panels_with_gaps": gaps,
        "render_queue_hint": (
            "Enqueue missing L0/L2 via Pearl Star (LOW priority, RAP/pscli). "
            "Re-run this generator after REAL assets land."
        ),
    }
    return manifest, gap_report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--series", required=True, help="artifacts/manga/<series_id>")
    ap.add_argument("--profile", required=True, help="config profile id (e.g. stillness_en_01)")
    ap.add_argument("--episode", default="ep_001")
    ap.add_argument("--out", type=Path, help="manifest output path (default: auto under series)")
    ap.add_argument("--include-gaps", action="store_true",
                    help="emit INTERIM placeholders for missing layers (wiring only)")
    ap.add_argument("--dry-run", action="store_true", help="print stats only; no files written")
    args = ap.parse_args(argv)

    manifest, gaps = generate(
        series_id=args.series,
        profile_id=args.profile,
        episode_id=args.episode,
        include_gaps=args.include_gaps,
    )

    errors = afb.validate_manifest(manifest)
    if errors and manifest["panels"]:
        print("manifest validation errors:", file=sys.stderr)
        for e in errors[:10]:
            print(f"  - {e}", file=sys.stderr)
        return 1

    out_manifest = args.out or (
        REPO / "artifacts" / "manga" / args.series
        / "assembly_manifests" / f"{args.episode}_from_continuity.yaml"
    )
    out_gaps = out_manifest.with_name(f"{args.episode}_bank_gaps.json")

    print(json.dumps(gaps["stats"], indent=2))
    print(f"unique L0={gaps['unique_L0']} L2={gaps['unique_L2']} "
          f"panels_complete={gaps['stats']['panels_complete']}/{gaps['stats']['panels_total']} "
          f"gap_panels={len(gaps['panels_with_gaps'])}")

    if args.dry_run:
        return 0

    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    out_gaps.write_text(json.dumps(gaps, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_manifest}")
    print(f"wrote {out_gaps}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
