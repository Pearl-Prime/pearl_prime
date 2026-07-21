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
from panel_planning_rules import shot_type_for_archetype  # noqa: E402
from render_v4_episode import build_render_manifest, load_configs, load_panel_states  # noqa: E402
from validate_chapter_composition_grammar import validate_chapter_composition_grammar  # noqa: E402

# Gap-render L2 assets (Pearl Star stillness lane 2026-07-09)
NAMED_GAP_L2 = {
    "hands_wrapping_cup": "L2_hands_wrapping_cup_clean_v2",
    "seated_kitchen_knees_up": "L2_seated_kitchen_knees_up_v1",
    "full_figure_kitchen_standing": "L2_full_figure_kitchen_standing_v1",
    "clean_bust_calm": "L2_clean_bust_calm_v2",
}
KITCHEN_L0_STEM = "L0_2b9283d4c387"
INSERT_OBJECT_ARCHETYPES = frozenset({
    "tea_beat_close_up",
    "hand_table_micro",
    "dappled_light_hand",
    "phone_notification_macro",
    "food_preparation_overhead",
    "kettle_steam_macro",
    "seasonal_anchor_object",
    "pet_companion_micro",
})
RE_ESTABLISH_ARCHETYPE = "shared_meal_table_medium"
ROOM_ESTABLISH_ARCHETYPE = "character_at_table_medium"

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
    return shot_type_for_archetype(archetype)


def _l0_derivation(shot: str | None, *, l0_meta: dict | None = None,
                   l2_meta: dict | None = None) -> dict[str, Any] | None:
    if shot == "insert_object":
        return {"type": "tone_gradient"}
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


def _resolve_named_l2(cache_dir: Path, stem: str) -> Path | None:
    """Resolve gap-render L2 assets named L2_<id>_alpha.png on disk."""
    layer_id = stem if stem.startswith("L2_") else f"L2_{stem}"
    return _resolve_cache_asset(cache_dir, "L2", layer_id)


def _select_insert_object_l2(cache_dir: Path, archetype: str | None) -> Path | None:
    if archetype in INSERT_OBJECT_ARCHETYPES:
        return _resolve_named_l2(cache_dir, NAMED_GAP_L2["hands_wrapping_cup"])
    return None


def _select_abstract_stage_l2(cache_dir: Path, shot: str | None) -> Path | None:
    if shot in ("reaction_emotion", "dialogue_bust"):
        return _resolve_named_l2(cache_dir, NAMED_GAP_L2["clean_bust_calm"])
    return None


def _maybe_override_room_l2(
    *,
    shot: str | None,
    l0_path: Path | None,
    l2_path: Path | None,
    cache_dir: Path,
) -> Path | None:
    """Route room-capable gap L2 onto establishing / re_establish kitchen plates."""
    if shot not in ("establishing", "re_establish") or not l0_path:
        return l2_path
    if KITCHEN_L0_STEM not in l0_path.name:
        return l2_path
    if shot == "re_establish":
        return _resolve_named_l2(cache_dir, NAMED_GAP_L2["seated_kitchen_knees_up"]) or l2_path
    if shot == "establishing":
        return _resolve_named_l2(cache_dir, NAMED_GAP_L2["full_figure_kitchen_standing"]) or l2_path
    return l2_path


def _kitchen_l0_path(cache_dir: Path) -> Path | None:
    p = cache_dir / "L0" / f"{KITCHEN_L0_STEM}.png"
    return p if p.is_file() and p.stat().st_size >= MIN_REAL_BYTES else None


def _build_re_establish_panel(
    *,
    panel: dict[str, Any],
    cache_dir: Path,
    configs: dict[str, Any],
) -> None:
    """Rewrite a panel as HR-U16 re_establish on kitchen full_render + room L2."""
    kitchen_l0 = _kitchen_l0_path(cache_dir)
    seated_l2 = _resolve_named_l2(cache_dir, NAMED_GAP_L2["seated_kitchen_knees_up"])
    if not kitchen_l0 or not seated_l2:
        return
    bbox = _archetype_bbox(configs, RE_ESTABLISH_ARCHETYPE) or [25, 28, 56, 66]
    panel["shot_type"] = "re_establish"
    panel["archetype"] = RE_ESTABLISH_ARCHETYPE
    panel["layers"] = [
        {
            "layer_class": "L0",
            "asset": _rel(kitchen_l0),
            "provenance": "REAL",
        },
        {
            "layer_class": "L2",
            "asset": _rel(seated_l2),
            "provenance": "REAL",
            "anchor_slot": "seat_at_table",
            "grounding": {"contact_shadow": True, "occluder": True},
            "bbox_pct": bbox,
        },
    ]


def _maybe_add_room_l2_on_establishing(
    *,
    entry: dict[str, Any],
    shot: str | None,
    l0_path: Path | None,
    cache_dir: Path,
    configs: dict[str, Any],
) -> None:
    """Add room-capable full-figure L2 to kitchen establishing panels that are L0-only."""
    if shot != "establishing" or not l0_path or KITCHEN_L0_STEM not in l0_path.name:
        return
    if any(lyr.get("layer_class") == "L2" for lyr in entry.get("layers") or []):
        return
    full_l2 = _resolve_named_l2(cache_dir, NAMED_GAP_L2["full_figure_kitchen_standing"])
    if not full_l2:
        return
    bbox = _archetype_bbox(configs, ROOM_ESTABLISH_ARCHETYPE) or [22, 18, 60, 78]
    entry["layers"].append({
        "layer_class": "L2",
        "asset": _rel(full_l2),
        "provenance": "REAL",
        "anchor_slot": "seat_at_table",
        "grounding": {"contact_shadow": True, "occluder": True},
        "bbox_pct": bbox,
    })
    entry["archetype"] = entry.get("archetype") or ROOM_ESTABLISH_ARCHETYPE


def _enforce_hr_u16_re_establish(
    *,
    panels: list[dict[str, Any]],
    cache_dir: Path,
    configs: dict[str, Any],
    series_id: str,
    manifest_dir: Path,
) -> None:
    """Patch first HR-U16 failure panel per abstract run into re_establish."""
    for _ in range(8):
        manifest_stub = {"series_id": series_id, "panels": panels}
        fails = [
            f for f in validate_chapter_composition_grammar(manifest_stub, manifest_dir)
            if f.rule_id == "HR-U16" and f.severity == "FAIL"
        ]
        if not fails:
            return
        target_pid = fails[0].panel_id
        for panel in panels:
            if panel.get("panel_id") == target_pid:
                _build_re_establish_panel(panel=panel, cache_dir=cache_dir, configs=configs)
                break


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
        if shot == "insert_object" and archetype in INSERT_OBJECT_ARCHETYPES:
            gap_l2 = _select_insert_object_l2(cache_dir, archetype)
            if gap_l2:
                l2_path = gap_l2
        abstract_l2 = _select_abstract_stage_l2(cache_dir, shot)
        if abstract_l2:
            l2_path = abstract_l2
        l2_path = _maybe_override_room_l2(
            shot=shot, l0_path=l0_path, l2_path=l2_path, cache_dir=cache_dir,
        )
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

        if l2_id or l2_path:
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
                if bbox:
                    l2_layer["bbox_pct"] = bbox
                layers.append(l2_layer)
            elif l2_id:
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
        _maybe_add_room_l2_on_establishing(
            entry=entry,
            shot=shot,
            l0_path=l0_path,
            cache_dir=cache_dir,
            configs=configs,
        )
        panels_out.append(entry)
        if not panel_gaps:
            stats["panels_complete"] += 1

    manifest_dir = REPO / "artifacts" / "manga" / series_id / "assembly_manifests"
    _enforce_hr_u16_re_establish(
        panels=panels_out,
        cache_dir=cache_dir,
        configs=configs,
        series_id=series_id,
        manifest_dir=manifest_dir,
    )

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
