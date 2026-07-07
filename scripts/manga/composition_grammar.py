"""Composition grammar ops for layered manga assembly.

Implements MANGA_COMPOSITION_GRAMMAR_SPEC.md gates G1–G6 and §8 derivations.
Imported by `scripts/manga/assemble_from_bank.py` for grammar-aware assembly.

Tier 1. No LLM. No network. PIL only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

# Camera height hints (m) — spec §5 G3
CAMERA_HEIGHT_M = {
    "standing": 1.55,
    "seated": 1.15,
    "low": 0.45,
    "overhead": 2.5,
}

# G1 legality: crop_class × bg_class → LEGAL | ILLEGAL | LEGAL+ops | WARN
G1_MATRIX: dict[str, dict[str, str]] = {
    "full_figure": {
        "full_render": "LEGAL+ops",
        "partial_motif": "LEGAL+ops",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "WARN",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "knees_up": {
        "full_render": "LEGAL+ops",
        "partial_motif": "LEGAL+ops",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "LEGAL",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "thigh_up": {
        "full_render": "LEGAL+ops",
        "partial_motif": "LEGAL+ops",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "LEGAL",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "waist_up": {
        "full_render": "ILLEGAL",
        "partial_motif": "LEGAL",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "LEGAL",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "bust": {
        "full_render": "ILLEGAL",
        "partial_motif": "LEGAL",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "LEGAL",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "face_cu": {
        "full_render": "ILLEGAL",
        "partial_motif": "WARN",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "LEGAL",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "ecu_fragment": {
        "full_render": "ILLEGAL",
        "partial_motif": "WARN",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "LEGAL",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "hands": {
        "full_render": "ILLEGAL",
        "partial_motif": "WARN",
        "defocus_derived": "LEGAL",
        "tone_gradient": "LEGAL",
        "manpu_emotion": "LEGAL",
        "white_void": "LEGAL",
        "black_void": "LEGAL",
    },
    "silhouette": {k: "LEGAL" for k in (
        "full_render", "partial_motif", "defocus_derived", "tone_gradient",
        "manpu_emotion", "white_void", "black_void",
    )},
}

ABSTRACT_BG = {
    "defocus_derived", "tone_gradient", "manpu_emotion",
    "white_void", "black_void",
}

# Default abstract-stage slot for dialogue/reaction bust placement (spec §7).
DEFAULT_ABSTRACT_STAGE_SLOT: dict[str, Any] = {
    "slot_id": "abstract_dialogue_stage",
    "kind": "seat",
    "feet_y_pct": 82,
    "center_x_pct": 50,
    "expected_figure_h_pct": 48,
}


class GateSeverity(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


@dataclass
class GateResult:
    gate: str
    severity: GateSeverity
    message: str


@dataclass
class AssemblyReport:
    panel_id: str
    shot_type: str
    gates: list[GateResult] = field(default_factory=list)
    ops_applied: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(g.severity == GateSeverity.FAIL for g in self.gates)


def composition_meta_path(asset_path: Path) -> Path:
    return asset_path.with_suffix(".composition.json")


def load_composition_meta(asset_path: Path) -> dict[str, Any] | None:
    sidecar = composition_meta_path(asset_path)
    if not sidecar.is_file():
        return None
    return json.loads(sidecar.read_text())


def g1_crop_bg_legality(
    l2_meta: dict[str, Any],
    l0_meta: dict[str, Any],
    *,
    diegetic_match: bool = False,
) -> GateResult:
    crop = l2_meta["crop_class"]
    bg = l0_meta["bg_class"]
    if diegetic_match or (
        l2_meta.get("diegetic_pair")
        and l2_meta["diegetic_pair"] == l0_meta.get("asset_id")
    ):
        return GateResult("G1", GateSeverity.PASS, "diegetic pair — legality auto-pass")
    verdict = G1_MATRIX.get(crop, {}).get(bg, "ILLEGAL")
    if verdict == "ILLEGAL":
        return GateResult(
            "G1", GateSeverity.FAIL,
            f"{crop} × {bg} is ILLEGAL (no diegetic pair)",
        )
    if verdict == "WARN":
        return GateResult("G1", GateSeverity.WARN, f"{crop} × {bg} is WARN")
    return GateResult("G1", GateSeverity.PASS, f"{crop} × {bg} → {verdict}")


def g2_angle_bucket(l2_meta: dict[str, Any], l0_meta: dict[str, Any]) -> GateResult:
    bg = l0_meta.get("bg_class", "")
    if bg in ABSTRACT_BG:
        return GateResult("G2", GateSeverity.PASS, "abstract BG — angle exempt")
    l0_angle = (l0_meta.get("camera") or {}).get("angle_bucket")
    l2_angle = (l2_meta.get("implied_camera") or {}).get("angle_bucket")
    if l0_angle == l2_angle:
        return GateResult("G2", GateSeverity.PASS, f"angle_bucket match ({l0_angle})")
    return GateResult(
        "G2", GateSeverity.FAIL,
        f"angle_bucket mismatch: L2={l2_angle!r} L0={l0_angle!r}",
    )


def g8_light_azimuth(l2_meta: dict[str, Any], l0_meta: dict[str, Any]) -> GateResult:
    l0_az = (l0_meta.get("light") or {}).get("azimuth", "ambient")
    l2_az = (l2_meta.get("light") or {}).get("azimuth", "ambient")
    if l0_az == l2_az or l0_az == "ambient" or l2_az == "ambient":
        return GateResult("G8", GateSeverity.PASS, f"light azimuth compatible ({l2_az}/{l0_az})")
    return GateResult(
        "G8", GateSeverity.FAIL,
        f"light azimuth conflict: L2={l2_az} L0={l0_az}",
    )


def g3_horizon_scale_check(
    l0_meta: dict[str, Any],
    slot: dict[str, Any],
    canvas_h: int,
    scaled_figure_h_px: float,
) -> GateResult:
    y_horizon = canvas_h * (l0_meta.get("camera") or {}).get("eye_level_y_pct", 42) / 100
    y_feet = canvas_h * slot["feet_y_pct"] / 100
    if y_feet <= y_horizon:
        return GateResult("G3", GateSeverity.FAIL, "feet at or above horizon")
    expected_pct = slot.get("expected_figure_h_pct")
    if expected_pct is not None and expected_pct > 0:
        actual_pct = scaled_figure_h_px / canvas_h * 100
        delta = abs(actual_pct - expected_pct) / expected_pct
        if delta > 0.15:
            return GateResult(
                "G3", GateSeverity.FAIL,
                f"figure height {actual_pct:.1f}% vs slot expected {expected_pct}% "
                f"(delta {delta:.0%} > 15%)",
            )
    return GateResult("G3", GateSeverity.PASS, "horizon-ratio scale within tolerance")


def g4_shadow_applied(applied: bool) -> GateResult:
    if applied:
        return GateResult("G4", GateSeverity.PASS, "contact shadow rendered")
    return GateResult("G4", GateSeverity.FAIL, "contact shadow missing")


def g6_defringe_applied(applied: bool) -> GateResult:
    if applied:
        return GateResult("G6", GateSeverity.PASS, "defringe applied")
    return GateResult("G6", GateSeverity.WARN, "defringe skipped")


def run_combination_gates(
    l2_meta: dict[str, Any] | None,
    l0_meta: dict[str, Any] | None,
    *,
    require_l2: bool = True,
) -> list[GateResult]:
    if l0_meta is None:
        return [GateResult("meta", GateSeverity.WARN, "L0 composition_meta absent — legacy mode")]
    if require_l2 and l2_meta is None:
        return [GateResult("meta", GateSeverity.WARN, "L2 composition_meta absent — legacy mode")]
    if not require_l2 or l2_meta is None:
        return []
    return [
        g1_crop_bg_legality(l2_meta, l0_meta),
        g2_angle_bucket(l2_meta, l0_meta),
        g8_light_azimuth(l2_meta, l0_meta),
    ]


# ── §8 derived backgrounds ───────────────────────────────────────────────────


def derive_defocus(
    plate: Image.Image,
    *,
    radius_px: float = 10,
    darken_pct: float = 8,
    desaturate_pct: float = 15,
) -> Image.Image:
    out = plate.convert("RGBA")
    rgb = out.convert("RGB").filter(ImageFilter.GaussianBlur(radius=radius_px))
    rgb = ImageEnhance.Color(rgb).enhance(1.0 - desaturate_pct / 100)
    rgb = ImageEnhance.Brightness(rgb).enhance(1.0 - darken_pct / 100)
    return rgb.convert("RGBA")


def derive_tone_gradient(
    size: tuple[int, int],
    top_hex: str = "#F5F0E8",
    bottom_hex: str = "#E8DFD0",
) -> Image.Image:
    top = _hex_to_rgb(top_hex)
    bot = _hex_to_rgb(bottom_hex)
    w, h = size
    grad = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(grad)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] * (1 - t) + bot[0] * t)
        g = int(top[1] * (1 - t) + bot[1] * t)
        b = int(top[2] * (1 - t) + bot[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return grad.convert("RGBA")


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def alpha_tight_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    """Tight bbox from alpha channel only (ignores RGB under transparent pixels)."""
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    return alpha.getbbox()


# ── grounding ops ──────────────────────────────────────────────────────────────


def defringe_cutout(img: Image.Image, px: int = 1) -> Image.Image:
    """G6: shrink alpha 1px to kill white/AA halo."""
    if px <= 0:
        return img
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    for _ in range(px):
        alpha = alpha.filter(ImageFilter.MinFilter(3))
    rgba.putalpha(alpha)
    return rgba


def plan_horizon_scale_paste(
    cutout: Image.Image,
    l2_meta: dict[str, Any],
    l0_meta: dict[str, Any],
    slot: dict[str, Any],
    *,
    canvas_size: tuple[int, int],
) -> tuple[Image.Image | None, tuple[int, int], float, tuple[int, int, int, int]]:
    """G3 plan: scaled layer + paste coords without mutating canvas."""
    W, H = canvas_size
    cutout = defringe_cutout(cutout)
    tight = alpha_tight_bbox(cutout)
    if tight is None:
        return None, (0, 0), 0.0, (0, 0, 0, 0)

    y_horizon = H * (l0_meta.get("camera") or {}).get("eye_level_y_pct", 42) / 100
    y_feet = H * slot["feet_y_pct"] / 100
    if y_feet <= y_horizon:
        return None, (0, 0), 0.0, (0, 0, 0, 0)

    layer_tight = cutout.crop(tight)
    anchor_y = l2_meta["anchor"]["y_px"]
    anchor_in_tight = anchor_y - tight[1]
    if anchor_in_tight <= 0:
        return None, (0, 0), 0.0, (0, 0, 0, 0)

    cam_h_key = (l0_meta.get("camera") or {}).get("camera_height", "seated")
    camera_height_m = CAMERA_HEIGHT_M.get(cam_h_key, 1.15)
    figure_height_m = l2_meta.get("figure_height_m", 1.62)

    target_figure_h = (figure_height_m / camera_height_m) * (y_feet - y_horizon)
    if target_figure_h <= 0:
        return None, (0, 0), 0.0, (0, 0, 0, 0)

    scale = target_figure_h / anchor_in_tight
    new_w = max(1, int(layer_tight.width * scale))
    new_h = max(1, int(layer_tight.height * scale))
    scaled = layer_tight.resize((new_w, new_h), Image.LANCZOS)

    center_x = int(W * slot["center_x_pct"] / 100)
    paste_x = center_x - new_w // 2
    paste_y = int(y_feet - anchor_in_tight * scale)
    bbox = (paste_x, paste_y, paste_x + new_w, paste_y + new_h)
    return scaled, (paste_x, paste_y), target_figure_h, bbox


def horizon_scale_paste(
    canvas: Image.Image,
    cutout: Image.Image,
    l2_meta: dict[str, Any],
    l0_meta: dict[str, Any],
    slot: dict[str, Any],
) -> tuple[Image.Image, float, tuple[int, int, int, int]]:
    """G3: scale from horizon-ratio law and paste anchored at slot."""
    scaled, dest, target_h, bbox = plan_horizon_scale_paste(
        cutout, l2_meta, l0_meta, slot, canvas_size=canvas.size,
    )
    if scaled is None:
        return canvas, 0.0, (0, 0, 0, 0)
    canvas.alpha_composite(scaled, dest=dest)
    return canvas, target_h, bbox


def bbox_legacy_paste(
    canvas: Image.Image,
    cutout: Image.Image,
    bbox_pct: list[float],
) -> Image.Image:
    """Contract spec §10 min-fit centered paste (control path)."""
    W, H = canvas.size
    x_pct, y_pct, w_pct, h_pct = bbox_pct
    target_x = int(W * x_pct / 100)
    target_y = int(H * y_pct / 100)
    target_w = int(W * w_pct / 100)
    target_h = int(H * h_pct / 100)
    tight_box = alpha_tight_bbox(cutout)
    if tight_box is None:
        return canvas
    layer_tight = cutout.crop(tight_box)
    scale = min(target_w / layer_tight.width, target_h / layer_tight.height)
    new_size = (max(1, int(layer_tight.width * scale)),
                max(1, int(layer_tight.height * scale)))
    layer_scaled = layer_tight.resize(new_size, Image.LANCZOS)
    paste_x = target_x + (target_w - new_size[0]) // 2
    paste_y = target_y + (target_h - new_size[1]) // 2
    canvas.alpha_composite(layer_scaled, dest=(paste_x, paste_y))
    return canvas


def _shadow_rgb_from_floor(
    floor_sample: Image.Image | None,
) -> tuple[int, int, int]:
    if floor_sample is not None and floor_sample.getbbox():
        rgb = floor_sample.convert("RGB")
        pixels = list(rgb.getdata())
        r = sorted(p[0] for p in pixels)[len(pixels) // 4]
        g = sorted(p[1] for p in pixels)[len(pixels) // 4]
        b = sorted(p[2] for p in pixels)[len(pixels) // 4]
        return max(0, r - 30), max(0, g - 30), max(0, b - 30)
    return 80, 75, 70


def render_contact_shadow_layer(
    canvas_size: tuple[int, int],
    contact_bbox: tuple[int, int, int, int],
    light_azimuth: str = "camera_left",
    floor_sample: Image.Image | None = None,
) -> Image.Image:
    """G4: RGBA shadow layer composited between L0 and L2 (under subject)."""
    x0, y0, x1, y1 = contact_bbox
    W, H = canvas_size
    if x1 <= x0 or y1 <= y0:
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))

    contact_y = y1
    subj_w = x1 - x0
    subj_h = y1 - y0
    shadow_rgb = _shadow_rgb_from_floor(floor_sample)

    offset_x = int(subj_w * 0.08) if light_azimuth == "camera_left" else -int(subj_w * 0.08)
    cx = (x0 + x1) // 2 + offset_x
    cy = contact_y

    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow_layer)

    core_w = int(subj_w * 0.9)
    core_h = max(3, int(core_w * 0.2))
    amb_w = int(core_w * 1.45)
    amb_h = max(4, int(core_h * 1.3))

    for w, h, opacity in ((amb_w, amb_h, 90), (core_w, core_h, 200)):
        draw.ellipse(
            (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2),
            fill=(*shadow_rgb, opacity),
        )

    return shadow_layer.filter(ImageFilter.GaussianBlur(radius=max(2, subj_h * 0.02)))


def apply_contact_shadow(
    canvas: Image.Image,
    contact_bbox: tuple[int, int, int, int],
    light_azimuth: str = "camera_left",
) -> Image.Image:
    """G4 legacy whole-canvas path — prefer render_contact_shadow_layer + paste order."""
    W, H = canvas.size
    x0, y0, x1, y1 = contact_bbox
    floor = canvas.crop((
        max(0, x0), max(0, y1 - 20), min(W, x1), min(H, y1 + 5),
    ))
    shadow = render_contact_shadow_layer(
        (W, H), contact_bbox, light_azimuth, floor_sample=floor,
    )
    canvas.alpha_composite(shadow)
    return canvas


def paste_occluder_from_slot(
    canvas: Image.Image,
    l0_plate: Image.Image,
    slot: dict[str, Any],
) -> Image.Image:
    """G5: BOOK layer — crop occluder region from L0 plate, paste above L2."""
    bbox_pct = slot.get("occluder_crop_bbox_pct")
    if not bbox_pct:
        return canvas
    W, H = canvas.size
    x_pct, y_pct, w_pct, h_pct = bbox_pct
    x0 = int(W * x_pct / 100)
    y0 = int(H * y_pct / 100)
    x1 = int(W * (x_pct + w_pct) / 100)
    y1 = int(H * (y_pct + h_pct) / 100)
    plate = l0_plate.resize((W, H), Image.LANCZOS)
    occluder = plate.crop((x0, y0, x1, y1))
    canvas.alpha_composite(occluder, dest=(x0, y0))
    return canvas


def resolve_anchor_slot(
    l0_meta: dict[str, Any],
    *,
    anchor_slot: str | None = None,
    shot_type: str | None = None,
) -> dict[str, Any]:
    """Resolve placement slot from L0 meta, manifest anchor_slot, or abstract default."""
    if anchor_slot and l0_meta.get("anchor_slots"):
        for slot in l0_meta["anchor_slots"]:
            if slot.get("slot_id") == anchor_slot:
                return slot
        raise ValueError(f"anchor_slot {anchor_slot!r} not found in L0 composition_meta")
    if shot_type in ("dialogue_bust", "reaction_emotion"):
        return DEFAULT_ABSTRACT_STAGE_SLOT
    slots = l0_meta.get("anchor_slots") or []
    if slots:
        return slots[0]
    raise ValueError("grammar path requires anchor_slot or L0 anchor_slots")


def effective_l0_meta(
    l0_meta: dict[str, Any],
    derivation: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return L0 meta with bg_class overridden when manifest derivation is set."""
    if not derivation:
        return l0_meta
    dtype = derivation.get("type")
    mapping = {
        "defocus": "defocus_derived",
        "tone_gradient": "tone_gradient",
        "void": "white_void" if derivation.get("void", "white") == "white" else "black_void",
    }
    bg = mapping.get(dtype)
    if bg:
        return {**l0_meta, "bg_class": bg}
    return l0_meta


def dialogue_bust_paste(
    canvas: Image.Image,
    cutout: Image.Image,
    l2_meta: dict[str, Any] | None = None,
    slot: dict[str, Any] | None = None,
) -> Image.Image:
    """Stage waist_up/bust on abstract BG using anchor_slot metadata."""
    W, H = canvas.size
    cutout = defringe_cutout(cutout)
    tight = alpha_tight_bbox(cutout)
    if tight is None:
        return canvas
    layer_tight = cutout.crop(tight)

    slot = slot or DEFAULT_ABSTRACT_STAGE_SLOT
    bottom_y_pct = slot.get("bust_bottom_y_pct", slot.get("feet_y_pct", 82))
    height_pct = slot.get("expected_figure_h_pct", 48)
    center_x_pct = slot.get("center_x_pct", 50)

    target_h = int(H * height_pct / 100)
    scale = target_h / layer_tight.height
    new_w = max(1, int(layer_tight.width * scale))
    new_h = max(1, int(layer_tight.height * scale))
    scaled = layer_tight.resize((new_w, new_h), Image.LANCZOS)

    paste_x = int(W * center_x_pct / 100) - new_w // 2
    paste_y = int(H * bottom_y_pct / 100) - new_h

    if l2_meta and "eye_y_px" in l2_meta and "eye_align_y_pct" in slot:
        eye_in_tight = l2_meta["eye_y_px"] - tight[1]
        if eye_in_tight > 0:
            scaled_eye_y = int(eye_in_tight * scale)
            target_eye_y = int(H * slot["eye_align_y_pct"] / 100)
            paste_y = target_eye_y - scaled_eye_y

    canvas.alpha_composite(scaled, dest=(paste_x, paste_y))
    return canvas
