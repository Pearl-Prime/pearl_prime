#!/usr/bin/env python3
"""V5 episode render orchestrator — Qwen-Image-Layered single-dispatch decompose.

Supersedes V4's L0+L2 split (`render_v4_episode.py`).

Per docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md §8.

V5 architectural shape (per spec §8):
    for panel in continuity_state(ep_001):
        prompt = contract_to_prompt_compiler(panel)             # reuses V4 unchanged
        layer_paths = dispatch_layered_render(prompt, workflow) # NEW: 1 dispatch, N images
        composite = recompose_layers(layer_paths, archetype)    # NEW: PIL alpha-blend in layer order
        validate(composite)                                     # reuses V4 validate_layer.py
        save(composite, panel_id)

V5 removes V4's L0+L2 unique-render manifest dedup. Every panel is its own dispatch
(2-layer default; per-archetype 3-layer opt-in per V5 spec §7). The Qwen-Image-Layered
model emits layers × batch_size RGBA images via LatentCutToBatch → VAEDecode → SaveImage.

The orchestrator reuses V4 unchanged for:
  - continuity_state YAML loading
  - archetype/scene_context/safe_zone config loading
  - contract_to_prompt_compiler (single full-panel compile per panel; L2 contract inputs
    encode the same subject+scene+light+style fields V5 needs)
  - validate_layer.py + validate_continuity_invariants.py (class-A gates carry forward)
  - safe-zone hierarchical inheritance

What changes:
  - No L0/L2 manifest; single dispatch per panel
  - No rembg cutout (Qwen-Image-Layered emits already-alpha-cut layers)
  - Composite is PIL.Image.alpha_composite of decomposed layer 0 (subject RGBA)
    over layer 1 (background RGB)
  - POLL_TIMEOUT_SEC=1800s (V5 single dispatch 1.5-3 min on Pearl Star fp8mixed)

Tier 1 (operator-present). No LLM calls. Tier-policy compliant: no ANTHROPIC_API_KEY,
no OpenAI/Google/DashScope reads.

Usage:
    # Dry run (validate config + prompt compile, no GPU work):
    python3 scripts/manga/render_v5_episode.py \\
        --profile-id stillness_en_01 \\
        --artifacts-series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \\
        --episode-id ep_001 \\
        --dry-run

    # Render one panel (smoke test):
    python3 scripts/manga/render_v5_episode.py \\
        --profile-id stillness_en_01 \\
        --artifacts-series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \\
        --episode-id ep_001 \\
        --only-panel ep001_006

    # Render full episode with cache:
    python3 scripts/manga/render_v5_episode.py \\
        --profile-id stillness_en_01 \\
        --artifacts-series-id stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \\
        --episode-id ep_001 \\
        --skip-existing

Environment:
    COMFYUI_URL              — defaults to http://192.168.1.112:8188 (Pearl Star)
    COMFYUI_POLL_TIMEOUT_SEC — defaults to 1800 (30 min; V5 may load 20.5GB unet first call)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from shutil import copyfile
from typing import Any, Optional

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

# V4 helpers reused UNCHANGED per V5 spec §9
import contract_to_prompt_compiler as ctpc  # noqa: E402
import render_v4_episode as v4  # noqa: E402  (loaders, _build_l0/l2_contract_inputs)
import structural_composition as sc  # noqa: E402
import validate_layer as vl  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# constants
# ─────────────────────────────────────────────────────────────────────────────

DISPATCHER_VERSION = "1.0.0"
WORKFLOW_VERSION = "qwen_image_layered_decompose@1.0.0"

DEFAULT_WORKFLOW_PATH = (
    REPO
    / "scripts/image_generation/comfyui_workflows/qwen_image_layered_decompose.json"
)
DEFAULT_COMFY_URL = os.environ.get("COMFYUI_URL", "http://192.168.1.112:8188")
DEFAULT_SEED_BASE = 42

POLL_INTERVAL_SEC = 5.0
POLL_TIMEOUT_SEC = float(os.environ.get("COMFYUI_POLL_TIMEOUT_SEC", "1800"))
# 1800s = 30 min. First dispatch loads ~20.5 GB unet from disk + 7 GB clip + 254 MB vae,
# then 50-step Qwen-Image-Layered sampling. Subsequent dispatches on warm cache ~1.5-3 min.

# Per V5 spec §7, default = 2 layers (subject + background); per-archetype 3-layer opt-in.
DEFAULT_LAYER_COUNT = 2

# Subject_type → safe_zone framing_row default (mirrors V4 lookup table).
FRAMING_FOR_SUBJECT = {
    "character_face_only": "CU",
    "character_silhouette_back": "CU",
    "character_full_figure": "MS",
    "character_full_figure_walking": "MS",
    "character_full_figure_x2": "MS",
    "character_ELS_in_L0": "LS",
    "character_hand_only": "ECU",
    "character_hands_and_arms": "ECU",
    "character_hands_only": "ECU",
    "character_chest_partial": "MCU",
    "character_pet_only": "ECU",
}


# ─────────────────────────────────────────────────────────────────────────────
# ComfyUI HTTP helpers (inlined; mirror v5_qwen_layered_feasibility.py)
# ─────────────────────────────────────────────────────────────────────────────


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def _gpu_status(comfy_url: str) -> dict[str, Any]:
    """Read /system_stats from ComfyUI; returns vram_total / vram_free in GB."""
    try:
        stats = _get_json(f"{comfy_url}/system_stats")
    except Exception as e:
        return {"error": str(e)}
    devices = stats.get("devices") or []
    if not devices:
        return {"error": "no devices reported"}
    d = devices[0]
    return {
        "name": d.get("name", "?"),
        "vram_total_gb": round(d.get("vram_total", 0) / 1024**3, 2),
        "vram_free_gb": round(d.get("vram_free", 0) / 1024**3, 2),
        "torch_vram_total_gb": round(d.get("torch_vram_total", 0) / 1024**3, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# workflow JSON substitution (mirrors v5_qwen_layered_feasibility._build_workflow)
# ─────────────────────────────────────────────────────────────────────────────


def _build_workflow(
    template: dict, positive: str, negative: str, seed: int, layers: int
) -> dict:
    """Substitute {{positive_prompt}}/{{negative_prompt}} + seed + layer count.

    Mirrors v5_qwen_layered_feasibility._build_workflow; additionally writes the
    requested `layers` to node 43 (EmptyQwenImageLayeredLatentImage) for per-archetype
    2-vs-3 layer opt-in per V5 spec §7.
    """
    wf: dict = json.loads(json.dumps(template))  # deep copy
    for node_id, node in wf.items():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs", {})
        if not isinstance(inputs, dict):
            continue
        # Prompt substitution
        for k, v in list(inputs.items()):
            if not isinstance(v, str):
                continue
            if "{{positive_prompt}}" in v:
                inputs[k] = v.replace("{{positive_prompt}}", positive)
            if "{{negative_prompt}}" in v:
                inputs[k] = v.replace("{{negative_prompt}}", negative)
        # Seed → KSampler
        if node.get("class_type") == "KSampler" and "seed" in inputs:
            inputs["seed"] = seed
        # Layer count → EmptyQwenImageLayeredLatentImage
        if node.get("class_type") == "EmptyQwenImageLayeredLatentImage" and "layers" in inputs:
            inputs["layers"] = layers
    # ComfyUI /prompt rejects nodes without class_type; strip the _meta sidecar.
    wf = {k: v for k, v in wf.items() if k != "_meta"}
    return wf


# ─────────────────────────────────────────────────────────────────────────────
# dispatch + layer collection
# ─────────────────────────────────────────────────────────────────────────────


class DispatchTimeoutError(RuntimeError):
    pass


class LayerCountMismatchError(RuntimeError):
    pass


def dispatch_layered_render(
    panel_id: str,
    positive: str,
    negative: str,
    seed: int,
    expected_layers: int,
    workflow_template: dict,
    comfy_url: str,
    out_dir: Path,
) -> tuple[list[Path], dict]:
    """Submit one Qwen-Image-Layered dispatch; return (layer_paths, telemetry).

    Returns expected_layers PNG paths written as layer_NN.png under out_dir.

    Raises:
        DispatchTimeoutError      on poll timeout
        LayerCountMismatchError   on N != expected_layers
        RuntimeError              on submit failure or download failure
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    wf = _build_workflow(workflow_template, positive, negative, seed, expected_layers)

    t0 = time.time()
    gpu_before = _gpu_status(comfy_url)

    try:
        submit_resp = _post_json(f"{comfy_url}/prompt", {"prompt": wf})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"submit HTTP {e.code} for {panel_id}: {body[:500]}") from e
    except Exception as e:
        raise RuntimeError(f"submit failed for {panel_id}: {e}") from e

    prompt_id = submit_resp.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"no prompt_id in submit response for {panel_id}: {submit_resp}")

    deadline = time.time() + POLL_TIMEOUT_SEC
    history: Optional[dict] = None
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_SEC)
        try:
            h = _get_json(f"{comfy_url}/history/{prompt_id}")
        except urllib.error.URLError:
            continue
        except Exception:
            continue
        if prompt_id in h:
            history = h
            break

    if history is None:
        raise DispatchTimeoutError(
            f"poll timeout after {POLL_TIMEOUT_SEC:.0f}s for {panel_id} "
            f"(prompt_id={prompt_id})"
        )

    elapsed = time.time() - t0
    gpu_after = _gpu_status(comfy_url)

    outputs = history[prompt_id].get("outputs", {})
    all_images = []
    for node_id, node_outputs in outputs.items():
        for img in node_outputs.get("images", []) or []:
            all_images.append((node_id, img))

    if not all_images:
        raise RuntimeError(
            f"prompt finished but no images for {panel_id}: "
            f"{json.dumps(outputs)[:500]}"
        )

    # EMPIRICAL FINDING (feasibility test 2026-05-20, prompt_id c150b219):
    # Qwen-Image-Layered with `layers=N` emits N+1 SaveImage outputs in this order:
    #   layer_00 = composite full panel (RGBA, 100% opaque) — use directly as panel
    #   layer_01 = background only (RGBA, 100% opaque, subject region inpainted)
    #   layer_02..N = decomposed component layers (RGBA, alpha-cut subject etc.)
    # So expected_outputs = expected_layers + 1 (composite + N decomposed). Validation
    # accepts either expected_layers or expected_layers + 1 to be defensive about
    # archetype configs that may use either convention.
    accepted_counts = (expected_layers, expected_layers + 1)
    if len(all_images) not in accepted_counts:
        raise LayerCountMismatchError(
            f"expected {accepted_counts} outputs for {panel_id}, got {len(all_images)} "
            f"(node distribution: "
            f"{ {nid: sum(1 for n, _ in all_images if n == nid) for nid in {n for n, _ in all_images}} })"
        )

    layer_paths: list[Path] = []
    for idx, (node_id, img) in enumerate(all_images):
        view_url = (
            f"{comfy_url}/view?filename={img['filename']}"
            f"&subfolder={img.get('subfolder', '')}&type={img.get('type', 'output')}"
        )
        try:
            png_bytes = _get_bytes(view_url)
        except Exception as e:
            raise RuntimeError(
                f"layer download failed for {panel_id} idx={idx}: {e}"
            ) from e
        out = out_dir / f"layer_{idx:02d}.png"
        out.write_bytes(png_bytes)
        layer_paths.append(out)

    telemetry = {
        "prompt_id": prompt_id,
        "dispatch_time_sec": round(elapsed, 1),
        "n_layers": len(layer_paths),
        "gpu_before": gpu_before,
        "gpu_after": gpu_after,
        "vram_peak_gb": (
            round(
                max(
                    (gpu_before.get("vram_total_gb", 0) or 0)
                    - (gpu_before.get("vram_free_gb", 0) or 0),
                    (gpu_after.get("vram_total_gb", 0) or 0)
                    - (gpu_after.get("vram_free_gb", 0) or 0),
                ),
                2,
            )
            if "error" not in gpu_after and "error" not in gpu_before
            else None
        ),
        "seed": seed,
    }
    return layer_paths, telemetry


# ─────────────────────────────────────────────────────────────────────────────
# recompose: PIL alpha-blend in layer order
# ─────────────────────────────────────────────────────────────────────────────


def recompose_layers(layer_paths: list[Path], out_path: Path) -> Path:
    """Alpha-blend decomposed layers in reverse-emit order.

    Per V5 spec §7: layer 0 = foreground subject (RGBA), layer 1 = background (RGB),
    higher indices = increasingly background. Composite by painting from back-most
    layer forward (i.e., last layer is canvas, then alpha_composite earlier layers on top).
    """
    if not layer_paths:
        raise ValueError("recompose: no layer paths supplied")

    # Last layer is the back-most; convert to RGBA canvas.
    canvas = Image.open(layer_paths[-1]).convert("RGBA")
    W, H = canvas.size

    # Paint earlier layers (foreground) on top, in reverse from back to front.
    for path in reversed(layer_paths[:-1]):
        layer = Image.open(path).convert("RGBA")
        if layer.size != (W, H):
            # Defensive: model should emit same-size layers; resize if not.
            layer = layer.resize((W, H), Image.LANCZOS)
        canvas.alpha_composite(layer)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Save as RGB PNG for downstream consumers (flat composite has no transparency).
    canvas.convert("RGB").save(out_path, "PNG")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# prompt compilation (reuses V4 contract input builders + ctpc.compile_prompt)
# ─────────────────────────────────────────────────────────────────────────────


def compute_panel_seed(
    seed_base: int,
    panel_index: int,
    character_id: Optional[str],
    seed_by_character: bool,
) -> int:
    """Resolve the ComfyUI seed for one panel.

    Two modes:
      • index-jitter (default / legacy): ``seed_base + panel_index * 1009`` — a
        distinct seed per panel. Good for variety, BAD for cross-panel character
        consistency: the SAME character drifts from panel to panel.
      • per-character (``seed_by_character=True``): ``seed_base + sum(ord(c) for c
        in character_id)`` — the SAME character resolves to the SAME seed across
        every panel it appears in, holding it visually consistent. This mirrors the
        reference-sheet formula (reference_sheet_generator.py:251,
        ``DEFAULT_SEED_BASE + sum(ord(c) for c in teacher_id)``) so panels seed-lock
        to the character's reference sheet. INTERIM consistency win — composes with
        (does NOT replace) the deferred PuLID reference-image pathway (Phase C).

    Per-character mode falls back to index-jitter when a panel has no on-frame
    character (environmental / off-frame archetypes), so scene-only panels still get
    a deterministic, varied seed.
    """
    if seed_by_character and character_id:
        return seed_base + sum(ord(c) for c in character_id)
    return seed_base + (panel_index * 1009)


def _effective_character_subject_type(panel: dict, arch_ctx: dict) -> Optional[str]:
    """Resolve the effective character subject type for a panel.

    Some archetypes are environment-first (`subject_type: null`) but declare an
    additive promotion surface for authored on-frame characters. Those should
    compile through the character contract when operator state explicitly puts a
    character in frame, while remaining L0 scene-only otherwise.
    """
    subject_type = arch_ctx.get("subject_type")
    if subject_type and "character_" in str(subject_type):
        return str(subject_type)

    promoted = arch_ctx.get("on_frame_character_subject_type")
    if not promoted or "character_" not in str(promoted):
        return None

    chars = panel.get("character_state") or {}
    if not chars:
        return None

    rel_field = panel.get("relational_field") or {}
    active = rel_field.get("active_entities") or []
    for cid in chars:
        on_frame = next(
            (e.get("on_frame", True) for e in active if e.get("id") == cid), True
        )
        if on_frame:
            return str(promoted)
    return None


def _resolve_archetype_subject_state(
    panel: dict, arch_ctx: dict
) -> tuple[Optional[str], Optional[dict]]:
    """Pick the on-frame character_state entry for this panel (V4 §15.B.1 single-char)."""
    subject_type = _effective_character_subject_type(panel, arch_ctx)
    if not subject_type:
        return None, None

    chars = panel.get("character_state") or {}
    if not chars:
        return None, None

    rel_field = panel.get("relational_field") or {}
    active = rel_field.get("active_entities") or []
    for cid, cstate in chars.items():
        on_frame = next(
            (e.get("on_frame", True) for e in active if e.get("id") == cid), True
        )
        if on_frame:
            return cid, cstate
    return None, None


def _build_v5_l0_contract_for_panel(panel: dict, configs: dict) -> dict:
    """Adapt V4's _build_l0_contract_inputs to a panel-level (rather than L0-unique-meta) call.

    Used for environmental archetypes (subject_type=None) where there is no character
    to render — V5 still does one dispatch, but the prompt is the L0-equivalent (scene-only).
    """
    ss = panel.get("scene_state") or {}
    l0_meta = {
        "scene_id": ss.get("scene_id"),
        "temporal": ss.get("temporal"),
        "light_rig_id": ss.get("light_rig_id"),
    }
    return v4._build_l0_contract_inputs(l0_meta, configs)


def _build_v5_l2_contract_for_panel(
    panel: dict, configs: dict, character_id: str, cstate: dict, arch_ctx: dict
) -> tuple[dict, dict, str]:
    """Adapt V4's _build_l2_contract_inputs to a panel-level call.

    V4 derived its L2 meta from the manifest dedup pass; V5 builds it inline per panel
    (no manifest). Returns (contract_inputs, safe_zone_row).
    """
    subject_type = _effective_character_subject_type(panel, arch_ctx) or str(
        arch_ctx.get("subject_type") or ""
    )
    ss = panel.get("scene_state") or {}
    l2_meta = {
        "character_id": character_id,
        "archetype": panel.get("archetype"),
        "subject_type": subject_type,
        "pose_id": cstate.get("pose_id"),
        "emotional": cstate.get("emotional"),
        "expression_dial": float(cstate.get("expression_dial", 0.2) or 0.2),
        "gaze_direction": cstate.get("gaze_direction"),
        "hand_state": cstate.get("hand_state"),
        "breath_phase": cstate.get("breath_phase"),
        "scene_id": ss.get("scene_id"),
        "temporal": ss.get("temporal"),
        "light_rig_id": ss.get("light_rig_id"),
    }
    contract_inputs, safe_zone_row, _arch_ctx = v4._build_l2_contract_inputs(
        l2_meta,
        configs,
        subject_type_override=subject_type,
    )
    return contract_inputs, safe_zone_row, subject_type


def _rekey_prompt_bundle(
    bundle: ctpc.PromptBundle,
    *,
    positive: str,
    provenance_updates: Optional[dict[str, Any]] = None,
) -> ctpc.PromptBundle:
    payload = json.dumps(
        {
            "layer_type": bundle.provenance.get("layer_type", "L2"),
            "positive": positive,
            "negative": bundle.negative,
            "parameters": bundle.parameters,
        },
        sort_keys=True,
    )
    provenance = dict(bundle.provenance)
    if provenance_updates:
        provenance.update(provenance_updates)
    return ctpc.PromptBundle(
        positive=positive,
        negative=bundle.negative,
        parameters=bundle.parameters,
        cache_key=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        provenance=provenance,
        warnings=list(bundle.warnings),
    )


def _els_support_clause(archetype: str) -> str:
    """Return the structural grounding rule for wide character establishes."""
    try:
        panel_type_id = sc.bridge_hint_from_archetype(archetype)
        if not panel_type_id:
            raise KeyError("no bridge hint")
        bridge_row = sc.bridge_for_panel_type(panel_type_id)
        template_id = bridge_row.get("structural_template_id")
        templates = (sc.load_templates().get("templates") or {})
        description = ((templates.get(template_id) or {}).get("description") or "").strip()
        if description:
            return description
    except Exception:
        pass
    return "Full standing figure with feet visibly contacting the readable room floor; no floating torso or prop."


def _character_els_placement_clause(
    *,
    archetype: str,
    arch_meta: dict,
) -> Optional[str]:
    bbox = arch_meta.get("character_placement_bbox")
    if not (isinstance(bbox, list) and len(bbox) == 4):
        return None
    x0, y0, x1, y1 = bbox
    width = round(float(x1) - float(x0), 1)
    height = round(float(y1) - float(y0), 1)
    support_clause = _els_support_clause(archetype)
    return (
        "keep the environment primary. Place the full-body figure inside the archetype "
        f"placement box x {x0}-{x1}% / y {y0}-{y1}% (about {width}% of frame width and "
        f"{height}% of frame height), biased to the lower-left region of the frame. "
        "Preserve the upper and right field as breathable negative space. "
        f"Structural grounding: {support_clause}"
    )


def _compile_character_els_bundle(
    panel: dict,
    configs: dict,
    l2_contract_inputs: dict,
    *,
    archetype: str,
    arch_meta: dict,
) -> ctpc.PromptBundle:
    """Compile a promoted wide-character panel with environment-first ordering.

    The stock L2 template is character-first and tends to zoom the figure too
    large for `character_ELS_in_L0`. For these promoted environment-first
    archetypes, compose the prompt from the real L0 scene template plus the L2
    character state and structural placement clause.
    """
    env_contract_inputs = _build_v5_l0_contract_for_panel(panel, configs)
    env_bundle = ctpc.compile_prompt("L0", env_contract_inputs)
    l2_bundle = ctpc.compile_prompt("L2", l2_contract_inputs)
    placement_clause = _character_els_placement_clause(
        archetype=archetype,
        arch_meta=arch_meta,
    )
    if not placement_clause:
        return l2_bundle

    env_positive = env_bundle.positive.replace(
        "No people in scene.\n",
        "A single small character may be present near the window.\n",
    )
    continuity = l2_contract_inputs["continuity"]
    character = l2_contract_inputs["character"]
    expr_line = (
        f"EXPRESSION: {continuity['emotional_clause']} at intensity "
        f"{continuity['expression_dial']}."
    )
    if continuity.get("breath_phase_clause"):
        expr_line = f"{expr_line} {continuity['breath_phase_clause']}"
    character_block = (
        f"CHARACTER: {character['render_prompt_base']}.\n\n"
        f"POSE: {continuity['pose_clause']}.\n"
        f"GAZE: {continuity['gaze_clause']}.\n"
        f"HAND STATE: {continuity['hand_state_clause']}.\n"
        f"{expr_line}\n\n"
        f"CHARACTER PLACEMENT: {placement_clause}"
    )
    if "\n\nLIGHTING:" in env_positive:
        positive = env_positive.replace(
            "\n\nLIGHTING:",
            f"\n\n{character_block}\n\nLIGHTING:",
            1,
        )
    else:
        positive = f"{env_positive}\n\n{character_block}"
    return _rekey_prompt_bundle(
        l2_bundle,
        positive=positive.strip(),
        provenance_updates={"prompt_augmentation": "character_els_env_first_v2"},
    )


def _augment_prompt_for_character_els(
    bundle: ctpc.PromptBundle,
    *,
    archetype: str,
    arch_meta: dict,
) -> ctpc.PromptBundle:
    placement_clause = _character_els_placement_clause(
        archetype=archetype,
        arch_meta=arch_meta,
    )
    if not placement_clause:
        return bundle
    composition_clause = f"COMPOSITION: {placement_clause}"
    positive = bundle.positive.replace(
        "\n\nPortrait orientation",
        f"\n\n{composition_clause}\n\nPortrait orientation",
    )
    return _rekey_prompt_bundle(
        bundle,
        positive=positive,
        provenance_updates={"prompt_augmentation": "character_els_structural_composition_v1"},
    )


def _augment_prompt_for_mecha_clean_layer_decompose(
    bundle: ctpc.PromptBundle,
) -> ctpc.PromptBundle:
    """Make Qwen layered output honor clean mecha L0/L2/L3 roles."""
    if "mecha" not in bundle.positive.lower():
        return bundle
    clause = (
        "V5 MECHA LAYER SEPARATION REQUIREMENT: layer_01 must be an empty "
        "environment/support plate with no pilot, person, foreground subject, or hero "
        "mecha subject. layer_02 must be exactly one alpha-separable pilot OR mecha "
        "subject with no cockpit, hangar, console, background, or environment. Any "
        "layer_03 must be one isolated telemetry/object prop only. Do not bake the "
        "final composite into the individual layers."
    )
    positive = f"{bundle.positive.strip()}\n\n{clause}"
    return _rekey_prompt_bundle(
        bundle,
        positive=positive,
        provenance_updates={"mecha_layer_contract": "mecha_clean_structural_layer_v1"},
    )


def compile_v5_full_panel_prompt(
    panel: dict, configs: dict
) -> tuple[ctpc.PromptBundle, str, Optional[dict], dict]:
    """Compile one full-panel prompt for V5 dispatch.

    Returns (bundle, layer_type_used, safe_zone_row_or_None, arch_ctx).

    For archetypes with a character subject, uses V4's L2 contract template
    (which encodes subject + scene_context + light + style + genre — exactly what V5
    needs for a unified full-panel render).

    For environmental archetypes (subject_type=None), falls back to L0 template
    unless operator-authored on-frame state promotes them through
    on_frame_character_subject_type.
    """
    archetype = panel.get("archetype")
    if not archetype:
        raise ValueError(f"panel {panel.get('panel_id')} has no archetype")
    scene_ctx_table = configs["scene_context"]["archetypes"]
    arch_ctx = scene_ctx_table.get(archetype)
    if arch_ctx is None:
        raise ValueError(
            f"archetype {archetype!r} not declared in iyashikei.scene_context.yaml"
        )
    arch_meta = (
        (configs.get("panel_templates", {}).get("archetypes", {}) or {}).get(archetype, {})
        or {}
    )

    character_id, cstate = _resolve_archetype_subject_state(panel, arch_ctx)

    if character_id and cstate:
        contract_inputs, safe_zone_row, subject_type = _build_v5_l2_contract_for_panel(
            panel, configs, character_id, cstate, arch_ctx
        )
        if subject_type == "character_ELS_in_L0":
            bundle = _compile_character_els_bundle(
                panel,
                configs,
                contract_inputs,
                archetype=archetype,
                arch_meta=arch_meta,
            )
        else:
            bundle = ctpc.compile_prompt("L2", contract_inputs)
        return _augment_prompt_for_mecha_clean_layer_decompose(bundle), "L2", safe_zone_row, arch_ctx

    # Environmental / off-frame: render scene only via L0 template.
    contract_inputs = _build_v5_l0_contract_for_panel(panel, configs)
    bundle = ctpc.compile_prompt("L0", contract_inputs)
    return _augment_prompt_for_mecha_clean_layer_decompose(bundle), "L0", None, arch_ctx


# ─────────────────────────────────────────────────────────────────────────────
# archetype layer-count resolution
# ─────────────────────────────────────────────────────────────────────────────


def resolve_layer_count(archetype: str, panel_templates: dict) -> int:
    """Return per-archetype layer count for V5 dispatch.

    Schema (V5 spec §7): archetype.layer_render_contract.V5_layered_decompose.layers
    is the per-archetype opt-in. Default = 2.

    NOTE: as of V5 spec v1.0.0, no archetypes in iyashikei.yaml carry the
    V5_layered_decompose block yet (block is "schema extension to be added in V5
    orchestrator commit" per spec §7). Default 2 is the current ship; 3-layer opt-in
    lands as a follow-up archetype config edit, no orchestrator change.
    """
    archetypes_table = (panel_templates or {}).get("archetypes", {}) or {}
    arch = archetypes_table.get(archetype, {}) or {}
    lrc = arch.get("layer_render_contract", {}) or {}
    v5_block = lrc.get("V5_layered_decompose", {}) or {}
    layers = v5_block.get("layers", DEFAULT_LAYER_COUNT)
    try:
        layers = int(layers)
    except (TypeError, ValueError):
        layers = DEFAULT_LAYER_COUNT
    return max(1, layers)


# ─────────────────────────────────────────────────────────────────────────────
# cache key (per V5 spec §8)
# ─────────────────────────────────────────────────────────────────────────────


def _sha256_short(s: str, n: int = 12) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def compute_cache_key(
    panel: dict, prompt_bundle: ctpc.PromptBundle, workflow_version: str = WORKFLOW_VERSION
) -> str:
    """Cache key per V5 spec §8: (panel_id, character_design_hash, scene_state_hash,
    light_rig_id, prompt_hash, workflow_version) → sha256."""
    chars = panel.get("character_state") or {}
    character_design_hash = ""
    for _cid, cstate in chars.items():
        if isinstance(cstate, dict):
            character_design_hash = str(cstate.get("character_design_hash", ""))
            break

    scene_state = panel.get("scene_state") or {}
    scene_state_canonical = json.dumps(scene_state, sort_keys=True, default=str)
    scene_state_hash = _sha256_short(scene_state_canonical)
    light_rig_id = scene_state.get("light_rig_id", "")

    payload = json.dumps(
        {
            "panel_id": panel.get("panel_id"),
            "character_design_hash": character_design_hash,
            "scene_state_hash": scene_state_hash,
            "light_rig_id": light_rig_id,
            "prompt_hash": prompt_bundle.cache_key,
            "workflow_version": workflow_version,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def existing_composite_matches_cache(panel_dir: Path, cache_key: str) -> bool:
    """True iff composite.png exists AND _telemetry.json's cache_key matches."""
    composite = panel_dir / "composite.png"
    telem = panel_dir / "_telemetry.json"
    if not (composite.is_file() and composite.stat().st_size > 0):
        return False
    if not telem.is_file():
        return False
    try:
        prev = json.loads(telem.read_text())
    except Exception:
        return False
    return prev.get("cache_key") == cache_key


# ─────────────────────────────────────────────────────────────────────────────
# validation (reuses V4 validate_layer.py)
# ─────────────────────────────────────────────────────────────────────────────


def validate_composite(
    composite_path: Path,
    layer_type_used: str,
    safe_zone_row: Optional[dict],
    arch_ctx: dict,
    arch_meta: dict,
) -> tuple[bool, list[dict]]:
    """Run V4 validate_layer.py class-A gates on the V5 composite.

    V5 composite is post-dispatch flat RGB (no separate cutout RGBA), so several
    L2 gates SKIP (rembg_clean_alpha, character_extraction_coverage, etc.). The gates
    that DO apply: subject_safe_zone, subject_does_not_touch_edge, lettering_safe_zones.

    Per V5 spec §10, V4 L2 cutout gates are recast as V5 layer-0 (subject) gates with
    threshold tuning deferred to v1.0.1; this function applies the V4 gates unchanged.

    Returns (all_passed, [result dicts]).
    """
    # Synthesize a safe_zone_row if validating an environmental archetype with no L2 row
    if safe_zone_row is None:
        safe_zone_row = {
            "subject_zone_pct": None,
            "margin_min_pct_all_sides": 5,
            "backdrop": "pure_white",
            "backdrop_corner_tolerance": 5,
            "subject_must_not_touch_edge": False,
        }

    # Use L2 layer-type so the validator's L2 branch (post-cutout aware) runs the
    # subject_safe_zone / edge checks. Without a cutout_image_path, the V0.6 L2 branch
    # SKIPS post-cutout-specific gates with skip_reason — that's expected for V5.
    inp = vl.LayerValidationInput(
        image_path=composite_path,
        layer_type=layer_type_used,
        safe_zone_row=safe_zone_row,
        cutout_image_path=None,
        cutout_policy=arch_ctx.get("cutout_policy"),
        archetype_metadata={"subject_placement_bbox": arch_meta.get("subject_placement_bbox") or [10, 10, 80, 80]},
    )
    results = vl.validate_layer(inp)
    passed = vl.all_class_a_passed(results)
    return passed, [r.to_dict() for r in results]


# ─────────────────────────────────────────────────────────────────────────────
# OOM-aware error hinting (mirrors V5 spec §11/§5 fallback chain)
# ─────────────────────────────────────────────────────────────────────────────


def _looks_like_oom(err: Exception, gpu_after: Optional[dict]) -> bool:
    """Heuristic: is this dispatch failure VRAM-related?"""
    s = str(err).lower()
    if any(tok in s for tok in ("out of memory", "oom", "cuda out", "cuda error")):
        return True
    if gpu_after and not gpu_after.get("error"):
        total = gpu_after.get("vram_total_gb", 0) or 0
        free = gpu_after.get("vram_free_gb", 0) or 0
        if total > 0 and free / max(total, 1e-9) < 0.05:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# per-panel processing
# ─────────────────────────────────────────────────────────────────────────────


def process_panel(
    panel: dict,
    panel_index: int,
    panel_total: int,
    configs: dict,
    workflow_template: dict,
    comfy_url: str,
    panels_root: Path,
    composed_flat_dir: Path,
    seed_base: int,
    skip_existing: bool,
    dry_run: bool,
    seed_by_character: bool = False,
) -> dict:
    """Render one panel through the V5 pipeline. Returns per-panel summary dict."""
    pid = panel["panel_id"]
    archetype = panel.get("archetype")
    panel_dir = panels_root / pid

    summary = {
        "panel_id": pid,
        "archetype": archetype,
        "outcome": "pending",
        "reason": None,
        "layer_count": None,
        "layer_type_used": None,
        "cache_key": None,
        "dispatch_time_sec": None,
        "vram_peak_gb": None,
        "validation_passed": None,
        "validation_results": None,
    }

    # ── compile prompt ──────────────────────────────────────────────────
    try:
        bundle, layer_type_used, safe_zone_row, arch_ctx = compile_v5_full_panel_prompt(
            panel, configs
        )
    except Exception as e:
        print(f"  [{panel_index}/{panel_total}] {pid} PROMPT_FAIL: {e}")
        summary["outcome"] = "fail"
        summary["reason"] = f"prompt_compile_error: {e}"
        return summary

    summary["layer_type_used"] = layer_type_used
    expected_layers = resolve_layer_count(archetype, configs["panel_templates"])
    summary["layer_count"] = expected_layers
    cache_key = compute_cache_key(panel, bundle)
    summary["cache_key"] = cache_key

    # ── cache check ─────────────────────────────────────────────────────
    if skip_existing and existing_composite_matches_cache(panel_dir, cache_key):
        print(
            f"  [{panel_index}/{panel_total}] {pid} ({archetype}, {layer_type_used}, "
            f"{expected_layers}L) -> CACHED"
        )
        summary["outcome"] = "skip"
        summary["reason"] = "cache_hit"
        # Mirror composite to the operator-flat dir even on cache hit (idempotent copy).
        composite_path = panel_dir / "composite.png"
        if composite_path.is_file():
            composed_flat_dir.mkdir(parents=True, exist_ok=True)
            try:
                copyfile(composite_path, composed_flat_dir / f"{pid}.png")
            except Exception as e:
                print(f"            mirror to flat dir FAILED: {e}")
        return summary

    # ── dry run: stop after compile ────────────────────────────────────
    if dry_run:
        print(
            f"  [{panel_index}/{panel_total}] {pid} ({archetype}, {layer_type_used}, "
            f"{expected_layers}L) DRY_RUN — prompt compiled "
            f"(pos {len(bundle.positive)}b, neg {len(bundle.negative)}b, cache {cache_key[:12]})"
        )
        for w in bundle.warnings:
            print(f"            warn: {w}")
        summary["outcome"] = "dry_run"
        summary["reason"] = "dry_run_mode"
        return summary

    # ── dispatch ────────────────────────────────────────────────────────
    # Seed selection. Default = per-panel index jitter (variety). Opt-in
    # --seed-by-character derives the seed from the on-frame character_id so the
    # SAME character holds consistent across panels (interim cross-panel
    # consistency before PuLID; composes with — does not replace — Phase C).
    seed_character_id = None
    if seed_by_character:
        seed_character_id, _ = _resolve_archetype_subject_state(panel, arch_ctx)
    seed = compute_panel_seed(
        seed_base, panel_index, seed_character_id, seed_by_character
    )
    seed_mode = (
        f"char:{seed_character_id}"
        if (seed_by_character and seed_character_id)
        else "index-jitter"
    )
    print(
        f"            seed {seed} ({seed_mode})"
    )
    print(
        f"  [{panel_index}/{panel_total}] {pid} ({archetype}, {layer_type_used}, "
        f"{expected_layers}L, seed={seed}) dispatching..."
    )
    panel_dir.mkdir(parents=True, exist_ok=True)
    try:
        layer_paths, dispatch_telem = dispatch_layered_render(
            panel_id=pid,
            positive=bundle.positive,
            negative=bundle.negative,
            seed=seed,
            expected_layers=expected_layers,
            workflow_template=workflow_template,
            comfy_url=comfy_url,
            out_dir=panel_dir,
        )
    except DispatchTimeoutError as e:
        print(f"            DISPATCH_TIMEOUT: {e}")
        summary["outcome"] = "fail"
        summary["reason"] = f"dispatch_timeout: {e}"
        return summary
    except LayerCountMismatchError as e:
        print(f"            LAYER_COUNT_MISMATCH: {e}")
        summary["outcome"] = "fail"
        summary["reason"] = f"layer_count_mismatch: {e}"
        return summary
    except Exception as e:
        gpu_after = _gpu_status(comfy_url)
        oom_hint = ""
        if _looks_like_oom(e, gpu_after):
            oom_hint = (
                " [OOM-LIKE — consider fp8_e4m3fn CPU offload via UNETLoader weight_dtype "
                "OR 640x640 fallback per V5 spec §5/§11]"
            )
        print(f"            DISPATCH_FAIL: {e}{oom_hint}")
        summary["outcome"] = "fail"
        summary["reason"] = f"dispatch_error: {e}{oom_hint}"
        return summary

    summary["dispatch_time_sec"] = dispatch_telem.get("dispatch_time_sec")
    summary["vram_peak_gb"] = dispatch_telem.get("vram_peak_gb")

    # ── composite (use model's built-in composite at layer_00) ─────────
    # Per empirical finding (feasibility test 2026-05-20, prompt_id c150b219):
    # Qwen-Image-Layered emits the composite full panel at layer_00 (100% opaque RGBA).
    # No PIL recompose needed — copy layer_00 directly as composite.png. The remaining
    # layer_01+ files (background + decomposed components) are retained at
    # panel_dir/layer_NN.png as forensic / re-edit assets per V5 spec §8.
    import shutil
    composite_path = panel_dir / "composite.png"
    if len(layer_paths) >= 1 and layer_paths[0].is_file():
        shutil.copyfile(layer_paths[0], composite_path)
    else:
        # Fallback: legacy decomposition-only mode (no built-in composite from model)
        try:
            recompose_layers(layer_paths, composite_path)
        except Exception as e:
            print(f"            RECOMPOSE_FAIL: {e}")
            summary["outcome"] = "fail"
            summary["reason"] = f"recompose_error: {e}"
            return summary

    # ── validate ───────────────────────────────────────────────────────
    arch_meta = (
        (configs["panel_templates"].get("archetypes", {}) or {}).get(archetype, {}) or {}
    )
    try:
        val_passed, val_results = validate_composite(
            composite_path, layer_type_used, safe_zone_row, arch_ctx, arch_meta
        )
        summary["validation_passed"] = val_passed
        summary["validation_results"] = val_results
        if not val_passed:
            fails = [
                r["check_id"] for r in val_results
                if not r["passed"] and not r["skipped"]
            ]
            print(f"            validate: FAIL {fails}")
        else:
            print(
                f"            validate: PASS — "
                f"{summary['dispatch_time_sec']}s, "
                f"vram_peak {summary['vram_peak_gb']} GB"
            )
    except Exception as e:
        # Validator failure is logged but does NOT halt the episode (per spec §11 ship-criteria
        # is operator review-driven; validators are signal not gate at V5.0).
        print(f"            validate ERROR: {e}")
        summary["validation_passed"] = False
        summary["validation_results"] = [{"check_id": "_validator_error", "error": str(e)}]

    # ── telemetry sidecar ──────────────────────────────────────────────
    telemetry_sidecar = {
        "panel_id": pid,
        "archetype": archetype,
        "layer_type_used": layer_type_used,
        "layer_count": expected_layers,
        "cache_key": cache_key,
        "prompt_hash": bundle.cache_key,
        "prompt_sha256": hashlib.sha256(bundle.positive.encode("utf-8")).hexdigest(),
        "workflow_version": WORKFLOW_VERSION,
        "dispatcher_version": DISPATCHER_VERSION,
        "seed": seed,
        "dispatch_time_sec": dispatch_telem.get("dispatch_time_sec"),
        "vram_peak_gb": dispatch_telem.get("vram_peak_gb"),
        "gpu_before": dispatch_telem.get("gpu_before"),
        "gpu_after": dispatch_telem.get("gpu_after"),
        "layer_paths": [str(p.relative_to(REPO)) for p in layer_paths],
        "layer_roles": {
            "layer_00.png": "model_composite",
            "layer_01.png": "background",
            "layer_02.png": "foreground_component",
        },
        "composite_path": str(composite_path.relative_to(REPO)),
        "validation_passed": summary["validation_passed"],
        "compiled_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (panel_dir / "_telemetry.json").write_text(json.dumps(telemetry_sidecar, indent=2))

    # ── mirror to operator-facing flat dir ─────────────────────────────
    composed_flat_dir.mkdir(parents=True, exist_ok=True)
    try:
        copyfile(composite_path, composed_flat_dir / f"{pid}.png")
    except Exception as e:
        print(f"            mirror to flat dir FAILED: {e}")

    summary["outcome"] = "success"
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# episode orchestration
# ─────────────────────────────────────────────────────────────────────────────


def run_episode(
    profile_id: str,
    artifacts_series_id: str,
    episode_id: str,
    comfy_url: str,
    workflow_path: Path,
    output_dir: Optional[Path],
    only_panel: Optional[str],
    skip_existing: bool,
    dry_run: bool,
    seed_base: int,
    seed_by_character: bool = False,
) -> dict:
    configs = v4.load_configs(profile_id)
    panel_states = v4.load_panel_states(artifacts_series_id, episode_id)

    if only_panel:
        panel_states = [p for p in panel_states if p.get("panel_id") == only_panel]
        if not panel_states:
            print(f"ERROR: --only-panel {only_panel!r} not found in {episode_id}",
                  file=sys.stderr)
            return {"error": "panel_not_found"}

    if not workflow_path.is_file():
        print(f"ERROR: workflow not at {workflow_path}", file=sys.stderr)
        return {"error": "workflow_missing"}
    workflow_template = json.loads(workflow_path.read_text())

    # Output layout per V5 spec §8 + task spec §7
    if output_dir is None:
        panels_root = (
            REPO / "artifacts/manga" / artifacts_series_id / "panels_v5" / episode_id
        )
    else:
        # Resolve relative output_dir against REPO so .relative_to(REPO) below works
        output_dir = Path(output_dir)
        if not output_dir.is_absolute():
            output_dir = (REPO / output_dir).resolve()
        panels_root = output_dir / episode_id
    panels_root.mkdir(parents=True, exist_ok=True)

    composed_flat_dir = (
        REPO / "artifacts/manga" / artifacts_series_id / "composed_v5_qwen" / episode_id
    )
    composed_flat_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"=== V5 episode render: profile={profile_id} "
        f"artifacts={artifacts_series_id} episode={episode_id} ==="
    )
    print(f"  workflow:           {workflow_path.relative_to(REPO)}")
    print(f"  comfy_url:          {comfy_url}")
    print(f"  panels root:        {panels_root.relative_to(REPO)}")
    print(f"  flat composed dir:  {composed_flat_dir.relative_to(REPO)}")
    print(f"  panels to process:  {len(panel_states)}")
    print(f"  skip_existing:      {skip_existing}")
    print(f"  dry_run:            {dry_run}")
    print(f"  seed_base:          {seed_base}")
    print(f"  seed_by_character:  {seed_by_character}")
    print(f"  dispatcher_version: {DISPATCHER_VERSION}")
    print(f"  workflow_version:   {WORKFLOW_VERSION}")
    print()

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t_episode_start = time.time()
    per_panel_summaries: list[dict] = []

    for i, panel in enumerate(panel_states, start=1):
        per_panel_summaries.append(
            process_panel(
                panel=panel,
                panel_index=i,
                panel_total=len(panel_states),
                configs=configs,
                workflow_template=workflow_template,
                comfy_url=comfy_url,
                panels_root=panels_root,
                composed_flat_dir=composed_flat_dir,
                seed_base=seed_base,
                skip_existing=skip_existing,
                dry_run=dry_run,
                seed_by_character=seed_by_character,
            )
        )

    finished_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    elapsed_sec = round(time.time() - t_episode_start, 1)

    success = sum(1 for s in per_panel_summaries if s["outcome"] == "success")
    fail = sum(1 for s in per_panel_summaries if s["outcome"] == "fail")
    skip = sum(1 for s in per_panel_summaries if s["outcome"] == "skip")
    dry = sum(1 for s in per_panel_summaries if s["outcome"] == "dry_run")
    val_pass = sum(1 for s in per_panel_summaries if s.get("validation_passed") is True)
    val_fail = sum(1 for s in per_panel_summaries if s.get("validation_passed") is False)

    vram_peaks = [
        s["vram_peak_gb"]
        for s in per_panel_summaries
        if isinstance(s.get("vram_peak_gb"), (int, float))
    ]
    peak_vram_gb = max(vram_peaks) if vram_peaks else None
    dispatch_times = [
        s["dispatch_time_sec"]
        for s in per_panel_summaries
        if isinstance(s.get("dispatch_time_sec"), (int, float))
    ]
    mean_dispatch_sec = (
        round(sum(dispatch_times) / len(dispatch_times), 1) if dispatch_times else None
    )

    run_telemetry = {
        "schema_version": "1.0.0",
        "dispatcher_version": DISPATCHER_VERSION,
        "workflow_version": WORKFLOW_VERSION,
        "profile_id": profile_id,
        "artifacts_series_id": artifacts_series_id,
        "episode_id": episode_id,
        "comfy_url": comfy_url,
        "workflow_path": str(workflow_path.relative_to(REPO)),
        "panels_total": len(panel_states),
        "success_count": success,
        "fail_count": fail,
        "skip_count": skip,
        "dry_run_count": dry,
        "validation_pass_count": val_pass,
        "validation_fail_count": val_fail,
        "peak_vram_gb_observed": peak_vram_gb,
        "mean_dispatch_time_sec": mean_dispatch_sec,
        "elapsed_sec": elapsed_sec,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "per_panel": per_panel_summaries,
    }
    # Telemetry persistence per v1.0.1 spec amendment:
    # - Full-episode runs write `_run_telemetry.json` (the canonical episode record)
    # - --only-panel single-panel retries write a timestamped sidecar
    #   `_run_telemetry_<panel_id>_<finished_utc_compact>.json` so they don't
    #   overwrite the full-episode telemetry (empirical 2026-05-21 bug: ep001_001
    #   single-panel retry clobbered the 35-panel run telemetry).
    if only_panel:
        ts_compact = finished_utc.replace(":", "").replace("-", "").replace("T", "_").replace("Z", "Z")
        telem_filename = f"_run_telemetry_{only_panel}_{ts_compact}.json"
    else:
        telem_filename = "_run_telemetry.json"
    telem_path = panels_root / telem_filename
    telem_path.write_text(json.dumps(run_telemetry, indent=2))

    print()
    print(
        f"=== SUMMARY ep={episode_id}: "
        f"success={success} fail={fail} skip={skip} dry_run={dry} | "
        f"val_pass={val_pass} val_fail={val_fail} | "
        f"peak_vram={peak_vram_gb} GB | mean_dispatch={mean_dispatch_sec} s | "
        f"elapsed={elapsed_sec} s ==="
    )
    print(f"  run telemetry: {telem_path.relative_to(REPO)}")
    return run_telemetry


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "V5 episode render orchestrator (Qwen-Image-Layered single-dispatch decompose). "
            "Supersedes V4's L0+L2 split per docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md."
        )
    )
    ap.add_argument(
        "--profile-id",
        default="stillness_en_01",
        help="Short series identifier used for config files (default: stillness_en_01)",
    )
    ap.add_argument(
        "--artifacts-series-id",
        default="stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying",
        help="Long series identifier used for artifacts/ paths",
    )
    ap.add_argument("--series-id", dest="series_id_alias", default=None,
                    help="Alias for --artifacts-series-id (operator convenience)")
    ap.add_argument("--episode-id", default="ep_001")
    ap.add_argument(
        "--workflow-path",
        type=Path,
        default=DEFAULT_WORKFLOW_PATH,
        help=f"Path to V5 workflow JSON (default: {DEFAULT_WORKFLOW_PATH.relative_to(REPO)})",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Per-panel artifact root (default: "
            "artifacts/manga/<artifacts-series-id>/panels_v5/)"
        ),
    )
    ap.add_argument(
        "--comfy-url",
        default=DEFAULT_COMFY_URL,
        help=f"ComfyUI URL (default: {DEFAULT_COMFY_URL})",
    )
    ap.add_argument(
        "--only-panel",
        help="Render only the named panel_id (e.g., ep001_006); skip the rest.",
    )
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="If composite.png + matching cache_key telemetry exist, skip dispatch.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Compile prompts + report per-panel plan; do NOT dispatch to ComfyUI.",
    )
    ap.add_argument(
        "--seed-base",
        type=int,
        default=DEFAULT_SEED_BASE,
        help=f"Seed base; per-panel seed = seed_base + panel_index*1009 "
             f"(default: {DEFAULT_SEED_BASE})",
    )
    ap.add_argument(
        "--seed-by-character",
        action="store_true",
        help=(
            "Derive each panel's seed from its on-frame character_id "
            "(seed_base + sum(ord(c) for c in character_id)) instead of panel-index "
            "jitter, so a character renders consistently across panels (interim "
            "cross-panel consistency before PuLID; panels with no character fall back "
            "to index jitter)."
        ),
    )
    args = ap.parse_args(argv)

    # --series-id is an alias for --artifacts-series-id (task spec mentioned --series-id)
    artifacts_series_id = args.series_id_alias or args.artifacts_series_id

    result = run_episode(
        profile_id=args.profile_id,
        artifacts_series_id=artifacts_series_id,
        episode_id=args.episode_id,
        comfy_url=args.comfy_url,
        workflow_path=args.workflow_path,
        output_dir=args.output_dir,
        only_panel=args.only_panel,
        skip_existing=args.skip_existing,
        dry_run=args.dry_run,
        seed_base=args.seed_base,
        seed_by_character=args.seed_by_character,
    )
    if "error" in result:
        return 2
    return 0 if result.get("fail_count", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
