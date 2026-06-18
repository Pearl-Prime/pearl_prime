#!/usr/bin/env python3
"""PROOF (no GPU): the merged scene-aware visual compiler fixes the
devotion_en_01 identical-panel repro at the PROMPT level.

Context
-------
PR #1728 (compiler v3) + #1732 (v1/v2 caller) are merged to origin/main
(tip d22ca05192). This script drives the *merged* compiler over
devotion_en_01's authored panels (``chapter_script_writer_handoff.json``) with
``style_id=cozy_iyashikei`` and shows the panel prompts go from the original
near-identical repro -> one distinct, scene-bearing prompt per panel, with the
iyashikei style tail intact and environmental-insert cameras steered
"no people".

It mutates NOTHING on disk except this proof artifact. The repro inputs are
read-only:

  * BEFORE = the committed ``panel_prompts.json`` from the repro workspace
    (scene-agnostic — 1 style portrait repeated, varying only by mood block).
  * AFTER  = freshly compiled in-memory from the authored handoff via the
    merged ``compile_panel_prompts_from_chapter_script`` (the same v1/v2 entry
    the real pipeline calls), style_id=cozy_iyashikei, teacher=sai_ma.

No GPU, no paid API, no workspace mutation.

  PYTHONPATH=. python3 \
    artifacts/qa/scene_aware_compiler_proof_20260618/prove_scene_aware_compiler.py \
    --workspace /Users/ahjan/phoenix_omega/artifacts/manga/devotion_en_01_run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from phoenix_v4.manga.chapter.visual_from_script import (
    compile_panel_prompts_from_chapter_script,
)
from phoenix_v4.manga.visual_prompt_compiler import _SCENERY_CAMERAS, _clean_action

# Authored scene tokens we expect to surface as per-panel LEADS once the prompt
# is scene-aware. Each is a substring of one authored beat's action; presence in
# the compiled positive prompt proves the authored scene now leads the prompt.
SCENE_MARKERS = {
    "dawn garden": ["dawn over the hospice garden", "mist sits low"],
    "corridor clip": ["moves down the corridor"],
    "hands / blanket insert": ["blanket squared at the corners"],
    "bedside vigil": ["bedside", "vigil", "sits"],
    "plum blossom": ["plum", "blossom", "branch"],
}

# The iyashikei style tail that must remain present in every compiled prompt
# (style_id=cozy_iyashikei). These tokens come from the style archetype, NOT the
# authored scene, so they prove the style tail survives the scene-lead rewrite.
IYASHIKEI_TAIL_TOKENS = ["pastel colors", "soft lighting", "watercolor style", "healing"]


def _load_panels(pp: dict) -> list[dict]:
    return list(pp.get("panels") or [])


def _authored_index(handoff: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for page in handoff.get("pages") or []:
        for panel in page.get("panels") or []:
            out[str(panel.get("panel_id"))] = panel
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "scene_aware_before_after.json",
    )
    args = ap.parse_args()

    ws = args.workspace.resolve()
    old_pp = json.loads((ws / "panel_prompts.json").read_text())
    handoff = json.loads((ws / "chapter_script_writer_handoff.json").read_text())

    # ── BEFORE: the committed repro ──────────────────────────────────────────
    before_panels = _load_panels(old_pp)
    before_prompts = [str(p.get("prompt") or "") for p in before_panels]
    before_unique = len(set(before_prompts))

    # ── AFTER: drive the MERGED compiler over the authored handoff ───────────
    # cozy_iyashikei is the Devotion render style (project_manga_gpu_render_path:
    # NEVER let it fall back to dark_psychological/ahjan). sai_ma is the authored
    # teacher for this PROOF only — Phase-1 proves the engine emits scene-aware
    # prompts; byline/composite-mode governance (Sai-Maa-never-author) is a
    # delivery concern handled in the Waystream composite rebuild, not here.
    after_pp = compile_panel_prompts_from_chapter_script(
        handoff,
        style_id="cozy_iyashikei",
        teacher_id="sai_ma",
        series_id=handoff.get("series_id"),
        chapter_id=handoff.get("chapter_id"),
    )
    after_panels = _load_panels(after_pp)
    after_prompts = [str(p.get("prompt") or "") for p in after_panels]
    after_unique = len(set(after_prompts))

    authored = _authored_index(handoff)

    # ── Per-panel evidence rows ──────────────────────────────────────────────
    rows = []
    for ap_panel in after_panels:
        pid = str(ap_panel.get("panel_id"))
        auth = authored.get(pid, {})
        camera = str(auth.get("camera") or "")
        prompt = str(ap_panel.get("prompt") or "")
        neg = str(ap_panel.get("negative_prompt") or "")
        is_scenery = camera.strip().lower() in _SCENERY_CAMERAS
        # The authored action's opening clause should now lead the positive prompt.
        # Compare against the *cleaned* action (the compiler strips the
        # "Final panel:" production aside via _clean_action so it never becomes
        # art), so this check mirrors what the compiler actually emits.
        action = " ".join(str(auth.get("action") or "").split())
        cleaned = _clean_action(action)
        lead_clause = cleaned[:60].lower()
        scene_leads = bool(lead_clause) and lead_clause.split(",")[0][:30] in prompt.lower()
        tail_ok = all(tok in prompt.lower() for tok in IYASHIKEI_TAIL_TOKENS)
        scenery_steered = (not is_scenery) or (
            "no people" in prompt.lower() and "person" in neg.lower()
        )
        rows.append(
            {
                "panel_id": pid,
                "camera": camera,
                "mood": auth.get("mood"),
                "authored_action_head": action[:90],
                "cleaned_action_head": cleaned[:90],
                "scene_leads_prompt": scene_leads,
                "iyashikei_tail_intact": tail_ok,
                "scenery_camera": is_scenery,
                "scenery_no_people_steered": scenery_steered,
                "before_prompt": before_prompts[
                    [p.get("panel_id") for p in before_panels].index(pid)
                ]
                if pid in [p.get("panel_id") for p in before_panels]
                else None,
                "after_prompt": prompt,
                "after_negative": neg,
            }
        )

    # ── Scene-marker coverage across the chapter ─────────────────────────────
    joined = " || ".join(after_prompts).lower()
    marker_hits = {
        name: any(m in joined for m in markers) for name, markers in SCENE_MARKERS.items()
    }

    scenery_rows = [r for r in rows if r["scenery_camera"]]
    summary = {
        "panel_count": len(after_panels),
        "before_distinct_prompts": before_unique,
        "before_total_prompts": len(before_prompts),
        "after_distinct_prompts": after_unique,
        "after_total_prompts": len(after_prompts),
        "all_after_distinct": after_unique == len(after_prompts),
        "all_scene_lead": all(r["scene_leads_prompt"] for r in rows),
        "all_iyashikei_tail_intact": all(r["iyashikei_tail_intact"] for r in rows),
        "scenery_camera_count": len(scenery_rows),
        "all_scenery_steered_no_people": all(
            r["scenery_no_people_steered"] for r in scenery_rows
        ),
        "scene_marker_coverage": marker_hits,
        "all_scene_markers_present": all(marker_hits.values()),
    }

    proof = {
        "proof": "merged scene-aware visual compiler fixes devotion_en_01 repro (no GPU)",
        "merged_prs": ["#1728 compiler v3", "#1732 v1/v2 caller"],
        "origin_main_tip": "d22ca05192",
        "workspace": str(ws),
        "style_id": "cozy_iyashikei",
        "teacher_id": "sai_ma",
        "summary": summary,
        "panels": rows,
    }
    args.out.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")

    # ── Console verdict ──────────────────────────────────────────────────────
    print("=" * 72)
    print("SCENE-AWARE COMPILER PROOF (no GPU) — devotion_en_01")
    print("=" * 72)
    print(f"BEFORE: {before_unique}/{len(before_prompts)} distinct prompts (repro)")
    print(f"AFTER : {after_unique}/{len(after_prompts)} distinct prompts (merged compiler)")
    print()
    print(f"  all 22 distinct after .......... {summary['all_after_distinct']}")
    print(f"  every prompt scene-leads ....... {summary['all_scene_lead']}")
    print(f"  iyashikei tail intact (all) .... {summary['all_iyashikei_tail_intact']}")
    print(
        f"  scenery cameras steered no-ppl . {summary['all_scenery_steered_no_people']}"
        f" ({summary['scenery_camera_count']} scenery panels)"
    )
    print(f"  scene markers present .......... {summary['all_scene_markers_present']}")
    for name, hit in marker_hits.items():
        print(f"      - {name:24s} {'OK' if hit else 'MISS'}")
    print()
    print("--- sample BEFORE (p_1_0) ---")
    print("   ", before_prompts[0][:200])
    print("--- sample AFTER (p_1_0, dawn garden establishing-wide) ---")
    print("   ", after_prompts[0][:240])
    print()
    print(f"proof artifact -> {args.out}")

    ok = (
        summary["all_after_distinct"]
        and summary["all_scene_lead"]
        and summary["all_iyashikei_tail_intact"]
        and summary["all_scenery_steered_no_people"]
        and summary["all_scene_markers_present"]
    )
    print("VERDICT:", "PASS — repro fixed at prompt level" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
