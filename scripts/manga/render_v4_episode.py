#!/usr/bin/env python3
"""V4 episode render orchestrator — Phase D entry.

Reads ep_NNN continuity_state YAMLs + all V4 configs, builds the unique-render
manifest (L0 scenes × temporal × rig; L2 character poses × state), dispatches
each unique render once to Pearl Star, applies rembg cutouts per archetype
cutout_policy, composites each panel per archetype subject_placement_bbox,
and validates end-to-end.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §13.4.

Architecture (operator-directed):
  L0 first (unique scenes), L2 second (unique poses/states), composite last.
  Don't dispatch all 35 panels as independent jobs — that would re-render the
  same kitchen 15 times and lose the architectural efficiency win.

V4.0 MVP scope:
  - L0 + L2 layers (skip L3 standalone; props are rendered as part of L2's
    scene context per v0.6.1+ per-archetype scene_context_clause)
  - alpha_matting cutout per archetype.cutout_policy
  - Composite via §10 math (deterministic paste + 0px feather)
  - validate_layer.py on the cutout AND the composite
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))
import contract_to_prompt_compiler as ctpc  # noqa: E402
import validate_layer as vl  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# config loaders
# ─────────────────────────────────────────────────────────────────────────────


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text())


def load_configs(profile_id: str) -> dict[str, Any]:
    """profile_id is the short series identifier used for config files
    (e.g., 'stillness_en_01' — NOT the long artifacts-path id)."""
    series_dir = REPO / "config" / "source_of_truth" / "manga_profiles" / "series"
    # series_profile is optional — falls back to hardcoded character base
    # if the file doesn't exist (V4.0: Mira's render_base is fixed string)
    series_profile_path = series_dir / f"{profile_id}.yaml"
    fallback_profile_path = series_dir / "stillness_press_anxiety_vol1.yaml"
    if series_profile_path.is_file():
        series_profile = _load_yaml(series_profile_path)
    elif fallback_profile_path.is_file():
        series_profile = _load_yaml(fallback_profile_path)
    else:
        series_profile = {"character_design": {}}
    return {
        "series_profile": series_profile,
        "scene_inventory": _load_yaml(series_dir / f"{profile_id}.scene_inventory.yaml"),
        "object_inventory": _load_yaml(series_dir / f"{profile_id}.object_inventory.yaml"),
        "character_pose_inventory": _load_yaml(series_dir / f"{profile_id}.character_pose_inventory.yaml"),
        "style_state": _load_yaml(series_dir / f"{profile_id}.style_state.yaml"),
        "light_rigs": _load_yaml(REPO / "config/manga/light_rigs/iyashikei.yaml"),
        "scene_context": _load_yaml(REPO / "config/manga/panel_templates/iyashikei.scene_context.yaml"),
        "compiled_safe_zones": _load_yaml(REPO / "config/manga/compiled/safe_zones.yaml"),
        "panel_templates": _load_yaml(REPO / "config/manga/panel_templates/iyashikei.yaml"),
    }


def load_panel_states(artifacts_series_id: str, episode_id: str) -> list[dict]:
    """artifacts_series_id is the long-form identifier used for artifact paths."""
    cont_dir = REPO / "artifacts/manga" / artifacts_series_id / "continuity_state" / episode_id
    return [_load_yaml(p) for p in sorted(cont_dir.glob("*.yaml"))]


# ─────────────────────────────────────────────────────────────────────────────
# unique-render manifest construction
# ─────────────────────────────────────────────────────────────────────────────


def _stable_hash(parts: tuple) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:12]


def build_render_manifest(panel_states: list[dict], configs: dict) -> dict:
    """Return {'L0': {key: meta}, 'L2': {key: meta}, 'panel_to_layers': {...}}."""
    L0: dict[str, dict] = {}
    L2: dict[str, dict] = {}
    panel_to_layers: dict[str, dict] = {}
    scene_ctx = configs["scene_context"]["archetypes"]

    for panel in panel_states:
        pid = panel["panel_id"]
        ss = panel.get("scene_state") or {}
        l0_key_parts = (ss.get("scene_id"), ss.get("temporal"), ss.get("light_rig_id"))
        l0_id = f"L0_{_stable_hash(l0_key_parts)}"
        if l0_id not in L0:
            L0[l0_id] = {
                "scene_id": ss.get("scene_id"),
                "temporal": ss.get("temporal"),
                "light_rig_id": ss.get("light_rig_id"),
                "representative_panel": pid,
                "panels": [],
            }
        L0[l0_id]["panels"].append(pid)

        # L2 (only if archetype has character subject_type)
        archetype = panel.get("archetype")
        arch_ctx = scene_ctx.get(archetype, {}) if archetype else {}
        subject_type = arch_ctx.get("subject_type")
        cutout_policy = arch_ctx.get("cutout_policy")
        l2_id = None
        if subject_type and "character_" in str(subject_type) and cutout_policy:
            chars = panel.get("character_state") or {}
            for cid, cstate in chars.items():
                rel_field = panel.get("relational_field") or {}
                # Only render L2 if the character is on-frame
                active = rel_field.get("active_entities") or []
                on_frame = next((e.get("on_frame", True) for e in active if e.get("id") == cid), True)
                if not on_frame:
                    continue
                dial = cstate.get("expression_dial", 0.0)
                dial_bucket = round(float(dial), 1)
                l2_key_parts = (
                    cid, archetype, cstate.get("pose_id"), cstate.get("emotional"),
                    dial_bucket, cstate.get("gaze_direction"), cstate.get("hand_state"),
                    ss.get("scene_id"), ss.get("temporal"), ss.get("light_rig_id"),
                )
                l2_id = f"L2_{_stable_hash(l2_key_parts)}"
                if l2_id not in L2:
                    L2[l2_id] = {
                        "character_id": cid,
                        "archetype": archetype,
                        "subject_type": subject_type,
                        "pose_id": cstate.get("pose_id"),
                        "emotional": cstate.get("emotional"),
                        "expression_dial": dial,
                        "gaze_direction": cstate.get("gaze_direction"),
                        "hand_state": cstate.get("hand_state"),
                        "breath_phase": cstate.get("breath_phase"),
                        "scene_id": ss.get("scene_id"),
                        "temporal": ss.get("temporal"),
                        "light_rig_id": ss.get("light_rig_id"),
                        "representative_panel": pid,
                        "panels": [],
                    }
                L2[l2_id]["panels"].append(pid)
                break  # V4.0: single character per panel; multi-character defers per §15.B.1

        panel_to_layers[pid] = {"L0": l0_id, "L2": l2_id, "archetype": archetype}

    return {"L0": L0, "L2": L2, "panel_to_layers": panel_to_layers}


# ─────────────────────────────────────────────────────────────────────────────
# prompt compilation per layer
# ─────────────────────────────────────────────────────────────────────────────


def _build_l0_contract_inputs(l0: dict, configs: dict) -> dict:
    scene_id = l0["scene_id"]
    scene = next(s for s in configs["scene_inventory"]["scenes"] if s["scene_id"] == scene_id)
    rig = next(r for r in configs["light_rigs"]["light_rigs"]
               if r["light_rig_id"] == l0["light_rig_id"])
    style = configs["style_state"]["prompt_clauses"]
    # Genre clauses
    genre_drawing = "iyashikei watercolor register, painterly continuity, Yokohama Kaidashi Kiko aesthetic"
    genre_forbidden = "no speed lines, no dutch angles, no exaggerated reactions, no sweatdrops, no concentration lines"
    return {
        "scene": {
            "description": scene["description"],
            "subject_bbox_region_clause": scene["subject_bbox_region_clause"],
            "scene_specific_composition_clause": scene["scene_specific_composition_clause"],
            "forbidden_objects_clause": scene["forbidden_objects_clause"],
        },
        "light_rig": {"prompt_clause": rig["prompt_clause"]},
        "style_state": style,
        "genre": {
            "drawing_tradition_clause": genre_drawing,
            "forbidden_grammar_clause": genre_forbidden,
        },
        "resolution": {"width": 1080, "height": 1920},
    }


def _build_l2_contract_inputs(l2: dict, configs: dict) -> dict:
    archetype = l2["archetype"]
    arch_ctx = configs["scene_context"]["archetypes"][archetype]
    safe_zone_key = (f"subject={arch_ctx['subject_type']}"
                     f"|framing={arch_ctx.get('cutout_policy', {}).get('framing_row', 'CU')}"
                     f"|genre=healing")
    # Look up framing from subject_contract; default to CU for face archetypes
    # The cutout_policy doesn't carry framing_row; compute from arch_ctx subject_type's safe_zone
    # Try the most common framing for this subject
    framing_for_subject = {
        "character_face_only": "CU",
        "character_silhouette_back": "CU",
        "character_full_figure": "MS",
        "character_full_figure_walking": "MS",
        "character_hand_only": "ECU",
        "character_hands_and_arms": "ECU",
        "character_hands_only": "ECU",  # alias
        "character_chest_partial": "MCU",
        "character_pet_only": "ECU",
    }
    framing_row = framing_for_subject.get(arch_ctx["subject_type"], "CU")
    safe_zone_key = f"subject={arch_ctx['subject_type']}|framing={framing_row}|genre=healing"
    # Some subject_types alias (character_hands_only is not in safe_zones; map to character_hands_and_arms)
    if safe_zone_key not in configs["compiled_safe_zones"]["compiled"]:
        if "character_hands_only" in safe_zone_key:
            safe_zone_key = safe_zone_key.replace("character_hands_only", "character_hands_and_arms")
    safe_zone_row = configs["compiled_safe_zones"]["compiled"][safe_zone_key]

    rig = next(r for r in configs["light_rigs"]["light_rigs"]
               if r["light_rig_id"] == l2["light_rig_id"])
    style = configs["style_state"]["prompt_clauses"]

    # Character render base from series profile axes
    char_design = configs["series_profile"]["character_design"]
    axes = char_design.get("axes", {})
    def _v(ax):
        v = axes.get(ax, {}).get("value")
        return v if isinstance(v, str) else ""
    render_base = (
        f"Front-facing portrait of Mira Aoki — early 30s East-Asian-coded woman with "
        f"soft round face, medium almond eyes with double eyelids, "
        f"long brown hair side-left parted with side-swept fringe, "
        f"cream knit sweater with warm cardigan, small jade pendant on slim leather cord."
    )
    neg_base = (
        "shojo sparkle, plastic skin, uncanny valley, bow mouth, extra-large eyes, "
        "heavy decorative eyelashes, photorealistic, 3d render"
    )

    # Pose clause from character_pose_inventory
    pose_id = l2.get("pose_id") or ""
    pose_entry = next(
        (p for p in configs["character_pose_inventory"]["characters"]["mira_aoki"]["poses"]
         if p["pose_id"] == pose_id),
        None,
    )
    pose_clause = (
        pose_entry["description"].strip().replace("\n", " ")
        if pose_entry else f"pose {pose_id}"
    )

    gaze = (l2.get("gaze_direction") or "").replace("_", " ")
    hand = (l2.get("hand_state") or "").replace("_", " ")
    emotional = (l2.get("emotional") or "").replace("_", " ")
    expr = float(l2.get("expression_dial") or 0.2)
    breath = l2.get("breath_phase") or ""

    return {
        "character": {
            "render_prompt_base": render_base,
            "negative_prompt_base": neg_base,
            "wardrobe_override": "",
        },
        "continuity": {
            "pose_clause": pose_clause,
            "gaze_clause": f"gaze {gaze}" if gaze else "gaze relaxed",
            "hand_state_clause": hand if hand else "relaxed",
            "emotional_clause": emotional,
            "expression_dial": f"{expr:.1f}",
            "breath_phase_clause": breath.replace("_", " ") if breath else "",
        },
        "safe_zone": {
            "framing_clause": f"{framing_row}",
            "subject_zone_pct_str": (f"{safe_zone_row['subject_zone_pct'][0]}% x "
                                     f"{safe_zone_row['subject_zone_pct'][1]}%")
            if safe_zone_row.get("subject_zone_pct") else "n/a",
            "margin": safe_zone_row.get("margin", {"top": 5, "bottom": 5, "left": 5, "right": 5}),
            "shoulder_margin_clause": (
                f"both shoulders fully inside the frame with at least "
                f"{safe_zone_row.get('margin', {}).get('left', 5)}% empty space on left and right, "
                f"forehead with at least {safe_zone_row.get('margin', {}).get('top', 5)}% empty space"
            ),
        },
        "archetype": {
            "scene_context_clause": arch_ctx["scene_context_clause"],
            "attached_props_clause": arch_ctx["attached_props_clause"],
        },
        "light_rig": {"prompt_clause": rig["prompt_clause"]},
        "style_state": style,
        "genre": {"forbidden_grammar_clause": (
            "no speed lines, no dutch angles, no exaggerated reactions, "
            "no sweatdrops, no concentration lines"
        )},
        "resolution": {"width": 1080, "height": 1920},
    }, safe_zone_row, arch_ctx


# ─────────────────────────────────────────────────────────────────────────────
# dispatch to Pearl Star
# ─────────────────────────────────────────────────────────────────────────────


def dispatch_render(panel_id: str, prompt: str, negative_prompt: str,
                    out_dir: Path, comfy_url: str) -> Path:
    """Submit a single render job to Pearl Star, return path to produced PNG."""
    prompts_json = out_dir / f"{panel_id}_prompts.json"
    prompts_json.parent.mkdir(parents=True, exist_ok=True)
    prompts_json.write_text(json.dumps({
        "schema_version": "1.0.0",
        "artifact_type": "panel_prompts",
        "render_target": "1080x1920",
        "prompts": [{
            "panel_id": panel_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "beat_type": "micro",
            "engine_routing": "qwen_image_no_pulid",
        }],
    }, indent=2))

    cmd = [
        sys.executable, str(REPO / "scripts/manga/queue_panel_renders.py"),
        "--panel-prompts", str(prompts_json),
        "--output-dir", str(out_dir),
        "--workflow-path", str(REPO / "scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json"),
        "--comfy-url", comfy_url,
    ]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    elapsed = time.time() - t0
    img_path = out_dir / f"{panel_id}.png"
    if r.returncode != 0 or not img_path.is_file():
        raise RuntimeError(f"render failed for {panel_id}: rc={r.returncode}; stderr={r.stderr[-500:]}")
    return img_path


# ─────────────────────────────────────────────────────────────────────────────
# cutout + composite
# ─────────────────────────────────────────────────────────────────────────────


def apply_cutout(rendered_png: Path, cutout_policy: dict, out_path: Path) -> Path:
    """Apply rembg cutout per archetype.cutout_policy."""
    from rembg import remove, new_session
    model_name = cutout_policy["model"]
    session = new_session(model_name)
    kwargs = {}
    if cutout_policy.get("alpha_matting"):
        kwargs["alpha_matting"] = True
        kwargs["alpha_matting_foreground_threshold"] = cutout_policy.get(
            "alpha_matting_foreground_threshold", 240)
        kwargs["alpha_matting_background_threshold"] = cutout_policy.get(
            "alpha_matting_background_threshold", 10)
    rgba = remove(Image.open(rendered_png), session=session, **kwargs)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out_path)
    return out_path


def composite_panel(panel: dict, manifest: dict, cache_dir: Path,
                    archetype_metadata: dict, out_path: Path) -> Path:
    """Composite L0 + L2_cutout for one panel. Per spec §10 math."""
    pid = panel["panel_id"]
    layers = manifest["panel_to_layers"][pid]
    l0_id = layers["L0"]
    l2_id = layers.get("L2")

    # L0 is the base canvas
    l0_png = cache_dir / "L0" / f"{l0_id}.png"
    canvas = Image.open(l0_png).convert("RGBA")
    W, H = canvas.size

    if l2_id:
        l2_cutout = cache_dir / "L2" / f"{l2_id}_alpha.png"
        layer = Image.open(l2_cutout).convert("RGBA")
        # Use archetype's subject_placement_bbox to position
        bbox_pct = archetype_metadata.get("subject_placement_bbox") or [10, 10, 80, 80]
        x_pct, y_pct, w_pct, h_pct = bbox_pct
        target_x = int(W * x_pct / 100)
        target_y = int(H * y_pct / 100)
        target_w = int(W * w_pct / 100)
        target_h = int(H * h_pct / 100)

        # Tight-crop the cutout to its alpha bbox
        bbox = layer.getbbox()
        if bbox:
            layer = layer.crop(bbox)

        # Scale to fit target box
        scale = min(target_w / max(layer.width, 1), target_h / max(layer.height, 1))
        new_size = (max(int(layer.width * scale), 1), max(int(layer.height * scale), 1))
        layer = layer.resize(new_size, Image.LANCZOS)

        # Center inside target box
        paste_x = target_x + (target_w - new_size[0]) // 2
        paste_y = target_y + (target_h - new_size[1]) // 2
        canvas.alpha_composite(layer, dest=(paste_x, paste_y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path, "PNG")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# orchestration
# ─────────────────────────────────────────────────────────────────────────────


def run_episode(profile_id: str, artifacts_series_id: str, episode_id: str, comfy_url: str,
                limit_l0: int | None, limit_l2: int | None,
                limit_panels: int | None) -> dict:
    configs = load_configs(profile_id)
    panel_states = load_panel_states(artifacts_series_id, episode_id)
    manifest = build_render_manifest(panel_states, configs)

    cache_dir = REPO / "artifacts/manga" / artifacts_series_id / "v4_render_cache" / episode_id
    composed_dir = REPO / "artifacts/manga" / artifacts_series_id / "composed_v4_qwen" / episode_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    composed_dir.mkdir(parents=True, exist_ok=True)

    telemetry = {
        "profile_id": profile_id, "artifacts_series_id": artifacts_series_id, "episode_id": episode_id,
        "L0_total": len(manifest["L0"]), "L0_rendered": 0, "L0_failed": 0,
        "L2_total": len(manifest["L2"]), "L2_rendered": 0, "L2_failed": 0,
        "panels_composited": 0, "panels_failed": 0,
        "validations_pass": 0, "validations_fail": 0,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    print(f"=== V4 episode render: profile={profile_id} artifacts={artifacts_series_id} episode={episode_id} ===")
    print(f"  L0 unique: {len(manifest['L0'])} | L2 unique: {len(manifest['L2'])} | panels: {len(panel_states)}")

    # ── L0 dispatch ─────────────────────────────────────────────────────
    l0_dir = cache_dir / "L0"
    l0_items = list(manifest["L0"].items())[:limit_l0] if limit_l0 else manifest["L0"].items()
    for i, (l0_id, l0_meta) in enumerate(l0_items):
        target = l0_dir / f"{l0_id}.png"
        if target.is_file() and target.stat().st_size > 0:
            print(f"  [L0 {i+1}/{len(l0_items)}] {l0_id} -> CACHED")
            telemetry["L0_rendered"] += 1
            continue
        try:
            ci = _build_l0_contract_inputs(l0_meta, configs)
            bundle = ctpc.compile_prompt("L0", ci)
            print(f"  [L0 {i+1}/{len(l0_items)}] {l0_id} {l0_meta['scene_id']}/{l0_meta['temporal']} dispatching...")
            dispatch_render(l0_id, bundle.positive, bundle.negative, l0_dir, comfy_url)
            telemetry["L0_rendered"] += 1
        except Exception as e:
            print(f"  [L0 {i+1}/{len(l0_items)}] {l0_id} FAILED: {e}")
            telemetry["L0_failed"] += 1

    # ── L2 dispatch (+ cutout + validate) ───────────────────────────────
    l2_dir = cache_dir / "L2"
    l2_items = list(manifest["L2"].items())[:limit_l2] if limit_l2 else manifest["L2"].items()
    for i, (l2_id, l2_meta) in enumerate(l2_items):
        target = l2_dir / f"{l2_id}.png"
        cutout_target = l2_dir / f"{l2_id}_alpha.png"
        try:
            ci, safe_zone_row, arch_ctx = _build_l2_contract_inputs(l2_meta, configs)
            cutout_policy = arch_ctx["cutout_policy"]
            if target.is_file() and target.stat().st_size > 0:
                print(f"  [L2 {i+1}/{len(l2_items)}] {l2_id} -> render CACHED")
            else:
                bundle = ctpc.compile_prompt("L2", ci)
                print(f"  [L2 {i+1}/{len(l2_items)}] {l2_id} {l2_meta['character_id']}|{l2_meta['pose_id']}|{l2_meta['emotional']} dispatching...")
                dispatch_render(l2_id, bundle.positive, bundle.negative, l2_dir, comfy_url)
            if not (cutout_target.is_file() and cutout_target.stat().st_size > 0):
                print(f"            -> cutout via {cutout_policy['model']}...")
                apply_cutout(target, cutout_policy, cutout_target)
            # validate
            inp = vl.LayerValidationInput(
                image_path=target, layer_type="L2",
                safe_zone_row=safe_zone_row,
                cutout_image_path=cutout_target,
                cutout_policy=cutout_policy,
                archetype_metadata={"subject_placement_bbox": [10, 10, 80, 80]},
            )
            results = vl.validate_layer(inp)
            ok = vl.all_class_a_passed(results)
            fails = [r.check_id for r in results if not r.passed and not r.skipped]
            print(f"            -> validate: {'PASS' if ok else 'FAIL ' + str(fails)}")
            if ok:
                telemetry["validations_pass"] += 1
            else:
                telemetry["validations_fail"] += 1
            telemetry["L2_rendered"] += 1
        except Exception as e:
            print(f"  [L2 {i+1}/{len(l2_items)}] {l2_id} FAILED: {e}")
            telemetry["L2_failed"] += 1

    # ── composite per panel ─────────────────────────────────────────────
    archetype_meta_map = {
        a: t for a, t in configs["panel_templates"].get("archetypes", {}).items()
    } if configs["panel_templates"].get("archetypes") else {}

    panels_to_composite = panel_states[:limit_panels] if limit_panels else panel_states
    for panel in panels_to_composite:
        pid = panel["panel_id"]
        archetype = panel.get("archetype")
        try:
            arch_meta = archetype_meta_map.get(archetype, {})
            out = composed_dir / f"{pid}.png"
            composite_panel(panel, manifest, cache_dir, arch_meta, out)
            telemetry["panels_composited"] += 1
            print(f"  composited {pid} ({archetype}) -> {out.name}")
        except Exception as e:
            print(f"  composite FAILED {pid}: {e}")
            telemetry["panels_failed"] += 1

    telemetry["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (composed_dir / "_run_telemetry.json").write_text(json.dumps(telemetry, indent=2))
    print(f"\n=== telemetry summary ===")
    print(json.dumps(telemetry, indent=2))
    return telemetry


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-id", default="stillness_en_01",
                    help="short series identifier used for config files (e.g., stillness_en_01)")
    ap.add_argument("--artifacts-series-id",
                    default="stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying",
                    help="long series identifier used for artifacts/ paths")
    ap.add_argument("--episode-id", default="ep_001")
    ap.add_argument("--comfy-url", default="http://100.92.68.74:8188")
    ap.add_argument("--limit-l0", type=int, help="cap L0 unique renders (smoke test)")
    ap.add_argument("--limit-l2", type=int, help="cap L2 unique renders (smoke test)")
    ap.add_argument("--limit-panels", type=int, help="cap composite panels (smoke test)")
    ap.add_argument("--manifest-only", action="store_true",
                    help="print unique-layer manifest and exit (no dispatch)")
    args = ap.parse_args(argv)

    configs = load_configs(args.profile_id)
    panel_states = load_panel_states(args.artifacts_series_id, args.episode_id)
    manifest = build_render_manifest(panel_states, configs)

    if args.manifest_only:
        print(f"=== profile={args.profile_id} artifacts={args.artifacts_series_id} {args.episode_id} manifest ===")
        print(f"L0 unique: {len(manifest['L0'])}")
        for k, v in manifest["L0"].items():
            print(f"  {k}: {v['scene_id']}/{v['temporal']}/{v['light_rig_id']} -> {len(v['panels'])} panels")
        print(f"\nL2 unique: {len(manifest['L2'])}")
        for k, v in manifest["L2"].items():
            print(f"  {k}: {v['archetype']}|{v['pose_id']}|{v['emotional']}|{v['expression_dial']} -> {len(v['panels'])} panels")
        return 0

    run_episode(args.profile_id, args.artifacts_series_id, args.episode_id, args.comfy_url,
                args.limit_l0, args.limit_l2, args.limit_panels)
    return 0


if __name__ == "__main__":
    sys.exit(main())
