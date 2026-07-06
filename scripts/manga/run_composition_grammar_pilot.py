#!/usr/bin/env python3
"""Composition grammar pilot — 4-panel strip + control (spec §10).

Assembles grammar-compliant panels from annotated April assets and a control
panel demonstrating G1/G3/G4 failures on the legacy compositor path.

Usage:
    PYTHONPATH=. python3 scripts/manga/run_composition_grammar_pilot.py

Outputs:
    artifacts/manga/<series>/assembled/composition_grammar_pilot/
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402
from composition_grammar import (  # noqa: E402
    AssemblyReport,
    GateResult,
    GateSeverity,
    apply_contact_shadow,
    bbox_legacy_paste,
    derive_defocus,
    derive_tone_gradient,
    dialogue_bust_paste,
    g1_crop_bg_legality,
    g3_horizon_scale_check,
    g4_shadow_applied,
    g6_defringe_applied,
    horizon_scale_paste,
    load_composition_meta,
    paste_occluder_from_slot,
    run_combination_gates,
)

SERIES = REPO / (
    "artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
)
CANVAS = (1080, 1920)
OUT = SERIES / "assembled" / "composition_grammar_pilot"

L0_KITCHEN = SERIES / "v4_render_cache/ep_001/L0/L0_2b9283d4c387.png"
L2_ESTABLISH = SERIES / "v4_render_cache/ep_001/L2/L2_3210c57437fb_alpha.png"
L2_WAIST = SERIES / "image_bank/L2/mira_aoki/front_portrait_seated_calm_cutout.png"
L0_STOVE = SERIES / "v4_render_cache/ep_001/L0/L0_stove_macro_crop.png"


def _new_canvas() -> Image.Image:
    return Image.new("RGBA", CANVAS, "#FFFFFF")


def assemble_p1_establishing() -> tuple[Image.Image, AssemblyReport]:
    """P1 establishing — thigh_up at anchor slot + shadow + occluder."""
    report = AssemblyReport("p1_establishing", "establishing")
    l0_meta = load_composition_meta(L0_KITCHEN)
    l2_meta = load_composition_meta(L2_ESTABLISH)
    assert l0_meta and l2_meta

    report.gates.extend(run_combination_gates(l2_meta, l0_meta))
    slot = l0_meta["anchor_slots"][0]

    plate = Image.open(L0_KITCHEN).convert("RGBA")
    canvas = plate.resize(CANVAS, Image.LANCZOS)
    cutout = Image.open(L2_ESTABLISH).convert("RGBA")

    canvas, target_h, contact_bbox = horizon_scale_paste(
        canvas, cutout, l2_meta, l0_meta, slot,
    )
    report.ops_applied.extend(["G3_horizon_scale", "G6_defringe"])
    report.gates.append(g3_horizon_scale_check(l0_meta, slot, CANVAS[1], target_h))

    canvas = apply_contact_shadow(
        canvas, contact_bbox, (l0_meta.get("light") or {}).get("azimuth", "camera_left"),
    )
    report.ops_applied.append("G4_contact_shadow")
    report.gates.append(g4_shadow_applied(True))

    canvas = paste_occluder_from_slot(canvas, plate, slot)
    report.ops_applied.append("G5_occluder_BOOK")
    report.gates.append(g6_defringe_applied(True))

    return canvas, report


def assemble_p2_dialogue_bust() -> tuple[Image.Image, AssemblyReport]:
    """P2 dialogue_bust — waist_up over defocus derived from same kitchen plate."""
    report = AssemblyReport("p2_dialogue_bust", "dialogue_bust")
    l0_src_meta = load_composition_meta(L0_KITCHEN)
    l2_meta = load_composition_meta(L2_WAIST)
    assert l0_src_meta and l2_meta

    l0_meta = {**l0_src_meta, "bg_class": "defocus_derived"}
    report.gates.extend(run_combination_gates(l2_meta, l0_meta))

    plate = Image.open(L0_KITCHEN).convert("RGBA")
    bg = derive_defocus(plate.resize(CANVAS, Image.LANCZOS))
    canvas = bg.copy()
    cutout = Image.open(L2_WAIST).convert("RGBA")
    canvas = dialogue_bust_paste(canvas, cutout)
    report.ops_applied.extend(["derive_defocus", "G6_defringe", "VN_stage_paste"])
    report.gates.append(g6_defringe_applied(True))

    return canvas, report


def assemble_p3_insert() -> tuple[Image.Image, AssemblyReport]:
    """P3 insert_object — stove macro crop (L0-only, no figure)."""
    report = AssemblyReport("p3_insert_object", "insert_object")
    img = Image.open(L0_STOVE).convert("RGBA").resize(CANVAS, Image.LANCZOS)
    report.ops_applied.append("L0_plate_crop")
    report.gates.append(GateResult("G1", GateSeverity.PASS, "insert — no L2 combination"))
    return img, report


def assemble_p4_reaction() -> tuple[Image.Image, AssemblyReport]:
    """P4 reaction_emotion — bust over tone gradient."""
    report = AssemblyReport("p4_reaction_emotion", "reaction_emotion")
    l2_meta = load_composition_meta(L2_WAIST)
    assert l2_meta
    l0_meta = {"bg_class": "tone_gradient", "asset_id": "derived_tone"}
    report.gates.extend(run_combination_gates(l2_meta, l0_meta))

    canvas = derive_tone_gradient(CANVAS)
    cutout = Image.open(L2_WAIST).convert("RGBA")
    canvas = dialogue_bust_paste(canvas, cutout)
    report.ops_applied.extend(["derive_tone_gradient", "G6_defringe"])
    report.gates.append(g6_defringe_applied(True))
    return canvas, report


def assemble_control_illegal() -> tuple[Image.Image, AssemblyReport]:
    """Control — waist_up × full_render via legacy §10 bbox (must FAIL G1/G4)."""
    report = AssemblyReport("control_illegal_waist_on_room", "control")
    l0_meta = load_composition_meta(L0_KITCHEN)
    l2_meta = load_composition_meta(L2_WAIST)
    assert l0_meta and l2_meta

    report.gates.append(g1_crop_bg_legality(l2_meta, l0_meta))
    report.gates.append(g4_shadow_applied(False))
    report.gates.append(
        GateResult("G3", GateSeverity.FAIL, "bbox_legacy — no horizon-ratio grounding"),
    )

    plate = Image.open(L0_KITCHEN).convert("RGBA")
    canvas = plate.resize(CANVAS, Image.LANCZOS)
    cutout = Image.open(L2_WAIST).convert("RGBA")
    canvas = bbox_legacy_paste(canvas, cutout, [24, 28, 56, 66])
    report.ops_applied.append("bbox_legacy_§10")

    return canvas, report


def render_strip(panel_paths: list[Path], out_path: Path, gutter_px: int = 80) -> None:
    afb.render_strip(panel_paths, out_path, gutter_px=gutter_px)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reports: list[AssemblyReport] = []
    grammar_paths: list[Path] = []

    builders = [
        assemble_p1_establishing,
        assemble_p2_dialogue_bust,
        assemble_p3_insert,
        assemble_p4_reaction,
    ]
    for fn in builders:
        img, report = fn()
        out = OUT / f"{report.panel_id}.png"
        img.save(out)
        grammar_paths.append(out)
        reports.append(report)
        fails = [g for g in report.gates if g.severity == GateSeverity.FAIL]
        status = "PASS" if not fails else "FAIL"
        print(f"  {report.panel_id} ({report.shot_type}): {status} "
              f"— {len(report.ops_applied)} ops, {len(fails)} gate failures")

    control_img, control_report = assemble_control_illegal()
    control_path = OUT / f"{control_report.panel_id}.png"
    control_img.save(control_path)
    reports.append(control_report)
    g1_fail = any(g.gate == "G1" and g.severity == GateSeverity.FAIL
                  for g in control_report.gates)
    print(f"  {control_report.panel_id}: G1_FAIL={g1_fail} (expected True)")

    strip_grammar = OUT / "composition_grammar_pilot_strip.jpg"
    render_strip(grammar_paths, strip_grammar)
    print(f"  grammar strip: {strip_grammar} ({strip_grammar.stat().st_size:,} bytes)")

    strip_control = OUT / "composition_grammar_control_strip.jpg"
    render_strip([control_path], strip_control)
    print(f"  control strip: {strip_control} ({strip_control.stat().st_size:,} bytes)")

    gate_log = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "spec": "MANGA_COMPOSITION_GRAMMAR_SPEC.md §10",
        "panels": [
            {
                "panel_id": r.panel_id,
                "shot_type": r.shot_type,
                "passed": r.passed,
                "ops_applied": r.ops_applied,
                "gates": [
                    {"gate": g.gate, "severity": g.severity.value, "message": g.message}
                    for g in r.gates
                ],
            }
            for r in reports
        ],
    }
    (OUT / "gate_report.json").write_text(json.dumps(gate_log, indent=2))

    min_bytes = 50_000
    for p in grammar_paths + [control_path, strip_grammar]:
        sz = p.stat().st_size
        if sz < min_bytes:
            print(f"WARN: {p.name} only {sz:,} bytes (< {min_bytes:,})")
        else:
            print(f"  byte check OK: {p.name} ({sz:,})")

    all_grammar_pass = all(r.passed for r in reports[:4])
    control_fails_g1 = g1_fail
    print(f"\nPilot verdict: grammar_panels_pass={all_grammar_pass} "
          f"control_g1_fail={control_fails_g1}")
    return 0 if all_grammar_pass and control_fails_g1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
