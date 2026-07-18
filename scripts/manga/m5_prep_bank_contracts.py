#!/usr/bin/env python3
"""M5-prep — author bank contracts, INTERIM dry-run assembly, Pearl Star job-lists.

No GPU. Pearl Star assumed down. Proves manifest → assemble_from_bank wiring
using REAL anchors (stillness) + labeled INTERIM stand-ins (all pilots).

Pilot set (Q-M5P-01 default = 3):
  1. stillness_press (iyashikei) — REAL L0/L2 + INTERIM L1/L3/L4
  2. warrior_calm mecha — all INTERIM (wiring proof)
  3. cognitive_clarity psych thriller — all INTERIM (wiring proof)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]

PILOTS = [
    {
        "key": "stillness",
        "series_id": "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying",
        "brand_id": "stillness_press",
        "genre": "iyashikei",
        "topic": "anxiety",
        "template": "stillness_en_01",
        "has_real_layers": True,
        "existing_manifest": (
            "artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/"
            "assembly_manifests/demo_alarm_metaphor_6p.yaml"
        ),
    },
    {
        "key": "warrior",
        "series_id": "warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening",
        "brand_id": "warrior_calm_cultivation",
        "genre": "mecha",
        "topic": "burnout",
        "template": None,
        "has_real_layers": False,
        "scenes": [
            ("hangar_pre_dawn", "Pre-dawn hangar. Matte slate chassis, amber cockpit lamp."),
            ("cockpit_interior", "Cockpit interior. Telemetry glow, oatmeal glove pad."),
        ],
        "objects": [
            ("glove_pad", "Hand-knit oatmeal glove pad on left palm."),
            ("telemetry_panel", "Cockpit telemetry strip, amber LEDs."),
        ],
        "poses": [
            ("seated_cockpit", "Pilot seated, jaw set, hands on controls."),
            ("threshold_stand", "Pilot at cockpit threshold, half in machine breath."),
        ],
    },
    {
        "key": "cognitive",
        "series_id": "cognitive_clarity__en_US__psychological_thriller__series01",
        "brand_id": "cognitive_clarity",
        "genre": "psychological_thriller",
        "topic": "overthinking",
        "template": None,
        "has_real_layers": False,
        "scenes": [
            ("office_after_hours", "Dim office after hours. Dual monitors, empty chairs."),
            ("archive_corridor", "Archive corridor. File labels, cool fluorescent light."),
        ],
        "objects": [
            ("clicking_pen", "Pen clicked in threes — overthinking tell."),
            ("risk_model_printout", "Printed risk model with one impossible prediction."),
        ],
        "poses": [
            ("at_desk_tense", "Analyst at desk, shoulders high, eyes on screen."),
            ("reading_shoulders", "Colleague reads shoulders, not slides."),
        ],
    },
]


def _write_inventory(path: Path, kind: str, series_id: str, brand_id: str,
                     genre: str, items: list[tuple[str, str]]) -> None:
    key = {"scene": "scenes", "object": "objects", "pose": "poses"}[kind]
    id_key = {"scene": "scene_id", "object": "object_id", "pose": "pose_id"}[kind]
    rows = []
    for iid, desc in items:
        rows.append({
            id_key: iid,
            "description": desc,
            "render_resolution": [1080, 1920],
            "provenance_target": "REAL",  # Pearl Star will produce REAL
            "status": "specced_awaiting_gpu",
        })
    doc = {
        "schema_version": "1.0.0",
        "series_id": series_id,
        "brand_id": brand_id,
        "locale": "en_US",
        "genre": genre,
        "authority_spec": "docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md",
        "m5_prep": True,
        "notes": (
            "M5-prep bank contract (no-GPU). Layers are SPECCED; REAL renders "
            "await Pearl Star via RESUME_COMMANDS.sh (Q-MANGA-03 envelope)."
        ),
        key: rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _interim_plate(path: Path, color: tuple[int, int, int], label: str) -> None:
    """Solid-color INTERIM L0 plate with label (never final art)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGBA", (1080, 1920), color + (255,))
    dr = ImageDraw.Draw(im)
    dr.rectangle([40, 40, 1040, 120], outline=(255, 255, 0, 255), width=4)
    dr.text((60, 60), f"INTERIM L0 — {label}", fill=(255, 255, 0, 255))
    im.save(path)
    path.with_suffix(".provenance.json").write_text(json.dumps({
        "provenance": "INTERIM",
        "kind": "solid_color_stand_in",
        "label": label,
        "note": "M5-prep wiring proof only — replace via Pearl Star L0 render",
    }, indent=2) + "\n")


def _interim_cutout(path: Path, color: tuple[int, int, int], label: str,
                    size: tuple[int, int] = (400, 600)) -> None:
    """Simple opaque cutout INTERIM L2/L3 sprite."""
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse([10, 10, size[0] - 10, size[1] - 10], fill=color + (255,))
    dr.text((20, size[1] // 2), f"INTERIM\n{label}", fill=(255, 255, 0, 255))
    im.save(path)
    path.with_suffix(".provenance.json").write_text(json.dumps({
        "provenance": "INTERIM",
        "kind": "procedural_cutout_stand_in",
        "label": label,
        "note": "M5-prep wiring proof only — replace via Pearl Star L2/L3 render",
    }, indent=2) + "\n")


def author_contracts(pilot: dict) -> Path:
    series = pilot["series_id"]
    base = REPO / "artifacts" / "manga" / series / "bank_contracts"
    base.mkdir(parents=True, exist_ok=True)
    if pilot.get("template"):
        src = REPO / "config" / "source_of_truth" / "manga_profiles" / "series"
        for kind in ("scene_inventory", "object_inventory", "character_pose_inventory"):
            s = src / f"{pilot['template']}.{kind}.yaml"
            d = base / f"{kind}.yaml"
            if s.is_file():
                shutil.copy2(s, d)
            else:
                raise SystemExit(f"missing template {s}")
    else:
        _write_inventory(base / "scene_inventory.yaml", "scene",
                         series, pilot["brand_id"], pilot["genre"], pilot["scenes"])
        _write_inventory(base / "object_inventory.yaml", "object",
                         series, pilot["brand_id"], pilot["genre"], pilot["objects"])
        _write_inventory(base / "character_pose_inventory.yaml", "pose",
                         series, pilot["brand_id"], pilot["genre"], pilot["poses"])
    return base


def build_interim_manifest(pilot: dict) -> Path:
    """Build a 6-panel INTERIM-only assembly manifest for wiring proof."""
    series = pilot["series_id"]
    sprites = REPO / "artifacts" / "manga" / series / "image_bank_sprites"
    sprites.mkdir(parents=True, exist_ok=True)
    l0 = sprites / "L0_plate_INTERIM.png"
    l2 = sprites / "L2_character_INTERIM.png"
    l3 = sprites / "L3_object_INTERIM.png"
    colors = {
        "warrior": ((40, 45, 55), (180, 160, 120), (100, 120, 140)),
        "cognitive": ((30, 35, 45), (120, 140, 160), (200, 180, 80)),
    }
    c0, c2, c3 = colors[pilot["key"]]
    _interim_plate(l0, c0, pilot["key"])
    _interim_cutout(l2, c2, "char", (420, 700))
    _interim_cutout(l3, c3, "obj", (280, 280))

    panels = []
    for i in range(1, 7):
        panels.append({
            "panel_id": f"wire_p{i}",
            "archetype": "wiring_proof",
            "layers": [
                {"layer_class": "L0", "asset": str(l0.relative_to(REPO)),
                 "provenance": "INTERIM",
                 "provenance_note": "M5-prep solid-color stand-in — NOT final art"},
                {"layer_class": "L2", "asset": str(l2.relative_to(REPO)),
                 "bbox_pct": [20 + i, 25, 50, 65],
                 "provenance": "INTERIM",
                 "provenance_note": "M5-prep procedural cutout — NOT final art"},
                {"layer_class": "L3", "asset": str(l3.relative_to(REPO)),
                 "bbox_pct": [55, 50 + i, 28, 22],
                 "z_order": "above_L2",
                 "provenance": "INTERIM",
                 "provenance_note": "M5-prep procedural cutout — NOT final art"},
            ],
            "narrator_caption": f"[WIRING PROOF panel {i} — INTERIM layers only]",
        })

    manifest = {
        "schema_version": "1.0.0",
        "series_id": series,
        "episode_id": "ep_001",
        "manifest_id": "m5_prep_wiring_proof_INTERIM",
        "notes": (
            "M5-prep WIRING PROOF — all layers INTERIM. Do NOT present as finished "
            "layered webtoon. Real layers await Pearl Star (RESUME_COMMANDS.sh)."
        ),
        "canvas": {"width": 1080, "height": 1920, "background_hex": "#FFFFFF"},
        "panels": panels,
    }
    mpath = REPO / "artifacts" / "manga" / series / "assembly_manifests" / "m5_prep_wiring_proof_INTERIM.yaml"
    mpath.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    mpath.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return mpath


def run_assemble(manifest: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(REPO / "scripts" / "manga" / "assemble_from_bank.py"),
        "--manifest", str(manifest),
        "--out-dir", str(out_dir),
        "--strip",
    ]
    env = {"PYTHONPATH": str(REPO)}
    r = subprocess.run(cmd, cwd=REPO, env={**dict(**{k: v for k, v in __import__("os").environ.items()}), **env},
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        raise SystemExit(f"assemble failed for {manifest}: {r.returncode}")
    print(r.stdout.strip() or f"assembled {out_dir}")


def write_resume(pilot: dict) -> Path:
    series = pilot["series_id"]
    path = REPO / "artifacts" / "manga" / series / "assembled" / "m5_prep_wiring_proof_INTERIM" / "RESUME_COMMANDS.sh"
    path.parent.mkdir(parents=True, exist_ok=True)
    n_scenes = 2 if not pilot.get("has_real_layers") else 8
    n_objects = 2 if not pilot.get("has_real_layers") else 6
    n_poses = 2 if not pilot.get("has_real_layers") else 6
    total = n_scenes + n_objects + n_poses
    # ~20s/image → hours
    gpu_h = round(total * 20 / 3600, 2)
    path.write_text(f"""#!/usr/bin/env bash
# M5-prep Pearl Star resume — {series}
# WIRING PROOF used INTERIM stand-ins. This script enqueues REAL bank layers.
#
# GPU envelope: Q-MANGA-03 / OPD-20260704-007 — LOW priority, ~2–4 GPU-h pilot.
# This series estimate: ~{total} images × ~20s ≈ {gpu_h} GPU-h (within envelope if
# batched with other pilots under the 2–4h cap; CJK atom lane always preempts).
#
# RAP: queue-first via pscli. Never call ComfyUI directly.
# Pearl Star was UNREACHABLE at M5-prep authoring (no pscli / box down).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "Preflight: Pearl Star queue must be RUNNING"
# ssh ahjan108@100.92.68.74 '… pscli status'   # enable when box is up

BANK="artifacts/manga/{series}/image_bank"
mkdir -p "$BANK/L0" "$BANK/L2" "$BANK/L3"

# Example enqueue (1 image per job — RAP). Expand from bank_contracts/*.yaml.
# PYTHONPATH=. python3 -c "
# from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job
# enqueue_panel_job(task='t2i_qwen_image', prompt='<from scene_inventory>',
#                   width=1080, height=1920, priority='LOW',
#                   out_path='$BANK/L0/<scene_id>.png')
# "

echo "After REAL layers land: re-run assemble_from_bank.py with provenance: REAL"
echo "  PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \\\\
echo "    --manifest artifacts/manga/{series}/assembly_manifests/<real_manifest>.yaml \\\\
echo "    --out-dir artifacts/manga/{series}/assembled/<real_name>/ --strip --bubbles"
""", encoding="utf-8")
    path.chmod(0o755)
    return path


def write_template_generator() -> Path:
    path = REPO / "scripts" / "manga" / "generate_bank_contracts_from_script.py"
    path.write_text('''#!/usr/bin/env python3
"""Generate bank-contract inventory stubs from an M3 chapter_script ep_001.

Mechanical procedure for the remaining M3 flagship series (after the 3-pilot
M5-prep set). Reads panel `scene` text, emits minimal scene/object/pose
inventory YAMLs under artifacts/manga/<series_id>/bank_contracts/.

Does NOT invent art — only the contract. REAL layers require Pearl Star.

Usage:
    PYTHONPATH=. python3 scripts/manga/generate_bank_contracts_from_script.py \\
        --chapter-script artifacts/manga/<series>/ep_001.yaml
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter-script", type=Path, required=True)
    args = ap.parse_args()
    data = yaml.safe_load(args.chapter_script.read_text())
    series_id = data["series_id"]
    brand_id = data.get("brand_id", series_id.split("__")[0])
    genre = data.get("genre", "iyashikei")
    # Crude scene buckets from first words of panel scenes
    scenes, objects, poses = [], [], []
    for page in data.get("pages") or []:
        for panel in page.get("panels") or []:
            scene = str(panel.get("scene") or "")
            words = re.findall(r"[A-Za-z]{4,}", scene)[:4]
            if words:
                sid = "_".join(w.lower() for w in words[:3])
                if sid and sid not in {s[0] for s in scenes}:
                    scenes.append((sid, scene[:200]))
            if "hand" in scene.lower() or "cup" in scene.lower() or "phone" in scene.lower():
                oid = "prop_" + str(len(objects))
                objects.append((oid, scene[:120]))
            if panel.get("dialogue_lines") or "face" in scene.lower():
                poses.append((f"pose_{len(poses)}", "Character pose derived from panel"))
    # Floor: at least 2 of each (Q-M5P-02 contract minimum)
    while len(scenes) < 2:
        scenes.append((f"scene_{len(scenes)}", "TODO: author from script"))
    while len(objects) < 2:
        objects.append((f"object_{len(objects)}", "TODO: author from script"))
    while len(poses) < 2:
        poses.append((f"pose_{len(poses)}", "TODO: author from script"))

    out = REPO / "artifacts" / "manga" / series_id / "bank_contracts"
    out.mkdir(parents=True, exist_ok=True)
    for kind, key, idk, items in (
        ("scene_inventory", "scenes", "scene_id", scenes[:8]),
        ("object_inventory", "objects", "object_id", objects[:8]),
        ("character_pose_inventory", "poses", "pose_id", poses[:8]),
    ):
        doc = {
            "schema_version": "1.0.0",
            "series_id": series_id,
            "brand_id": brand_id,
            "genre": genre,
            "m5_prep": True,
            "generated_from": str(args.chapter_script),
            key: [{idk: i, "description": d, "status": "specced_awaiting_gpu",
                   "render_resolution": [1080, 1920]} for i, d in items],
        }
        (out / f"{kind}.yaml").write_text(
            yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        print("wrote", out / f"{kind}.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")
    path.chmod(0o755)
    return path


def main() -> int:
    evidence = REPO / "artifacts" / "qa" / "manga_m5_prep_evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    coverage = ["series\tscenes\tobjects\tposes\treal_layers\tinterim_layers\tassembly_proof\tresume\n"]

    # Stillness: reuse existing demo as primary REAL+INTERIM proof
    stillness = PILOTS[0]
    author_contracts(stillness)
    # Re-run existing demo manifest (REAL+INTERIM)
    demo_m = REPO / stillness["existing_manifest"]
    demo_out = REPO / "artifacts" / "manga" / stillness["series_id"] / "assembled" / "m5_prep_stillness_REAL_INTERIM_proof"
    if demo_m.is_file():
        # Prefer existing assembled strip if present; else assemble
        existing_strip = REPO / "artifacts" / "manga" / stillness["series_id"] / "assembled" / "demo_alarm_metaphor_6p"
        if (existing_strip / "demo_alarm_metaphor_6p_strip.jpg").is_file():
            demo_out.mkdir(parents=True, exist_ok=True)
            # Copy proof pointer
            (demo_out / "PROOF_IS_EXISTING_DEMO_ALARM_METAPHOR_6P.txt").write_text(
                f"WIRING PROOF (REAL L0/L2 + INTERIM L1/L3/L4).\n"
                f"Canonical strip: {existing_strip}/demo_alarm_metaphor_6p_strip.jpg\n"
                f"Provenance: {existing_strip}/_provenance.md\n"
                f"Manifest: {demo_m}\n"
                f"DO NOT present as finished layered webtoon — INTERIM layers remain.\n",
                encoding="utf-8",
            )
            shutil.copy2(existing_strip / "demo_alarm_metaphor_6p_strip.jpg",
                         demo_out / "WIRING_PROOF_REAL_INTERIM_strip.jpg")
            shutil.copy2(existing_strip / "_provenance.md", demo_out / "_provenance.md")
            print("stillness: reused existing demo_alarm_metaphor_6p as wiring proof")
        else:
            run_assemble(demo_m, demo_out)
    resume_s = write_resume(stillness)
    # count from template inventories
    import yaml
    bc = REPO / "artifacts" / "manga" / stillness["series_id"] / "bank_contracts"
    sc = len(yaml.safe_load((bc / "scene_inventory.yaml").read_text()).get("scenes") or [])
    ob = len(yaml.safe_load((bc / "object_inventory.yaml").read_text()).get("objects") or [])
    po = len(yaml.safe_load((bc / "character_pose_inventory.yaml").read_text()).get("poses") or [])
    coverage.append(
        f"{stillness['series_id']}\t{sc}\t{ob}\t{po}\t"
        f"L0+L2 REAL (demo)\tL1+L3+L4 INTERIM\t{demo_out}\t{resume_s}\n"
    )

    for pilot in PILOTS[1:]:
        author_contracts(pilot)
        manifest = build_interim_manifest(pilot)
        out_dir = REPO / "artifacts" / "manga" / pilot["series_id"] / "assembled" / "m5_prep_wiring_proof_INTERIM"
        run_assemble(manifest, out_dir)
        # Loud label
        (out_dir / "NOT_FINAL_ART_INTERIM_WIRING_PROOF_ONLY.txt").write_text(
            "All layers INTERIM. Wiring proof only. Not a finished layered webtoon.\n",
            encoding="utf-8",
        )
        resume = write_resume(pilot)
        bc = REPO / "artifacts" / "manga" / pilot["series_id"] / "bank_contracts"
        sc = len(yaml.safe_load((bc / "scene_inventory.yaml").read_text())["scenes"])
        ob = len(yaml.safe_load((bc / "object_inventory.yaml").read_text())["objects"])
        po = len(yaml.safe_load((bc / "character_pose_inventory.yaml").read_text())["poses"])
        coverage.append(
            f"{pilot['series_id']}\t{sc}\t{ob}\t{po}\t0\tall INTERIM\t{out_dir}\t{resume}\n"
        )

    gen = write_template_generator()
    cov_path = evidence / "MANIFEST_COVERAGE.tsv"
    cov_path.write_text("".join(coverage), encoding="utf-8")
    (evidence / "README.md").write_text(
        "# M5-prep evidence\n\n"
        "Pearl Star was **unreachable** at authoring (no pscli). "
        "This lane authored bank contracts, proved assembly wiring on "
        "REAL+INTERIM (stillness) and INTERIM-only (warrior, cognitive), "
        "and emitted RESUME_COMMANDS.sh job-lists within Q-MANGA-03 envelope.\n\n"
        "**Never present INTERIM strips as finished art.**\n\n"
        f"Generator for remaining series: `{gen.relative_to(REPO)}`\n",
        encoding="utf-8",
    )
    (evidence / "ONE_SHOT_ON_PEARL_STAR_RETURN.md").write_text(
        "# One-shot when Pearl Star returns\n\n"
        "```bash\n"
        "# 1. Confirm queue RUNNING (RAP)\n"
        "pscli status   # or ssh … pscli status\n\n"
        "# 2. Enqueue REAL layers (LOW priority, CJK preempts)\n"
        "bash artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/"
        "assembled/m5_prep_stillness_REAL_INTERIM_proof/../demo_alarm_metaphor_6p/RESUME_COMMANDS.sh\n"
        "# (or per-series RESUME under assembled/m5_prep_wiring_proof_INTERIM/)\n\n"
        "# 3. After REAL assets land, re-assemble with provenance: REAL\n"
        "PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \\\n"
        "  --manifest artifacts/manga/<series>/assembly_manifests/<real>.yaml \\\n"
        "  --out-dir artifacts/manga/<series>/assembled/<real>/ --strip --bubbles\n"
        "```\n\n"
        "Budget: OPD-20260704-007 — ~2–4 GPU-h LOW-priority pilot total.\n",
        encoding="utf-8",
    )
    print("coverage:", cov_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
