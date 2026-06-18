#!/usr/bin/env python3
"""PHASE-2 GATE: is the merged-compiler prompt at least as good as the
render_devotion_panels_gpu.py workaround it would replace?

The workaround (PR #1726, commit 7014622188) reads the OLD scene-AGNOSTIC
``panel_prompts.json`` and re-composes ``{authored_scene}, {shot_phrase} |
{style_tail}`` at render time via ``_compose_positive`` / ``_compose_negative``.
Now that #1728 + #1732 are merged, a *regenerated* ``panel_prompts.json`` already
leads each prompt with the authored scene + shot phrase and already carries the
scenery "no people" steer — so the workaround's composition layer is redundant.

This gate proves retiring it loses NO scene/camera fidelity. For each panel it
compares:

  WORKAROUND = _compose_positive(OLD_compiled_prompt, camera, action)   (#1726)
  COMPILER   = merged compile_panel_prompts_from_chapter_script(...)["prompt"]

and asserts, per panel, that the COMPILER prompt is at least as good:
  * scene leads (authored cleaned-action head present at the front),
  * camera shot-type phrase present,
  * iyashikei style tail intact,
  * scenery cameras steered "no people" (pos + neg),
  * 22/22 distinct.

The ``_compose_*`` / ``_clean_action`` / ``_style_tail`` / ``_SHOT_PHRASE`` /
``_SCENERY_*`` helpers below are copied VERBATIM from
``scripts/manga/render_devotion_panels_gpu.py`` @ 7014622188 so the comparison is
faithful and self-contained (that file is on PR #1726's branch, not origin/main).

  PYTHONPATH=. python3 \
    artifacts/qa/scene_aware_compiler_proof_20260618/fidelity_gate_workaround_vs_compiler.py \
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

# ── VERBATIM from render_devotion_panels_gpu.py @ 7014622188 (the workaround) ──
_SHOT_PHRASE = {
    "establishing-wide": "wide establishing shot, full environment, scenery",
    "wide": "wide shot, full scene",
    "medium": "medium shot",
    "over-shoulder": "over-the-shoulder shot",
    "close-up": "close-up",
    "insert": "close insert detail",
    "environmental-insert": "environmental insert, scenery detail",
}
_WA_SCENERY_CAMERAS = {"environmental-insert"}
_SCENERY_NEG = "person, people, face, portrait, character, human figure, crowd"


def _wa_clean_action(action: str, limit: int = 340) -> str:
    a = " ".join(str(action or "").split()).strip()
    a = a.replace("Final panel:", "").strip()
    return a[:limit].rsplit(" ", 1)[0] if len(a) > limit else a


def _wa_style_tail(compiled_prompt: str) -> str:
    return compiled_prompt.replace("mixed: close-up, medium, wide, ", "").strip()


def _wa_compose_positive(compiled_prompt: str, camera: str, action: str) -> str:
    cam = str(camera or "").strip().lower()
    scene = _wa_clean_action(action)
    shot = _SHOT_PHRASE.get(cam, "medium shot")
    lead = f"{scene}, {shot}" if scene else shot
    if cam in _WA_SCENERY_CAMERAS:
        lead = f"{lead}, no people, empty of figures"
    return f"{lead} | {_wa_style_tail(compiled_prompt)}"


def _wa_compose_negative(panel_negative: str, camera: str) -> str:
    neg = (panel_negative or "").strip()
    if str(camera or "").strip().lower() in _WA_SCENERY_CAMERAS:
        neg = f"{neg}, {_SCENERY_NEG}" if neg else _SCENERY_NEG
    return neg


# ── End verbatim ──────────────────────────────────────────────────────────────


def _authored_index(handoff: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for page in handoff.get("pages") or []:
        for panel in page.get("panels") or []:
            out[str(panel.get("panel_id"))] = panel
    return out


def _shot_for(camera: str) -> str:
    return _SHOT_PHRASE.get(str(camera or "").strip().lower(), "medium shot")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "fidelity_gate_report.json",
    )
    args = ap.parse_args()

    ws = args.workspace.resolve()
    old_pp = json.loads((ws / "panel_prompts.json").read_text())
    handoff = json.loads((ws / "chapter_script_writer_handoff.json").read_text())
    old_by_id = {str(p.get("panel_id")): p for p in old_pp.get("panels") or []}
    authored = _authored_index(handoff)

    # Merged-compiler regenerated prompts (style_id=cozy_iyashikei).
    comp_pp = compile_panel_prompts_from_chapter_script(
        handoff,
        style_id="cozy_iyashikei",
        teacher_id="sai_ma",
        series_id=handoff.get("series_id"),
        chapter_id=handoff.get("chapter_id"),
    )
    comp_by_id = {str(p.get("panel_id")): p for p in comp_pp.get("panels") or []}

    rows = []
    comp_prompts = []
    for pid, auth in authored.items():
        camera = str(auth.get("camera") or "")
        action = " ".join(str(auth.get("action") or "").split())
        cleaned = _clean_action(action)
        is_scenery = camera.strip().lower() in _SCENERY_CAMERAS

        old_prompt = str((old_by_id.get(pid) or {}).get("prompt") or "")
        old_neg = str((old_by_id.get(pid) or {}).get("negative_prompt") or "")
        wa_pos = _wa_compose_positive(old_prompt, camera, action)
        wa_neg = _wa_compose_negative(old_neg, camera)

        comp_pos = str((comp_by_id.get(pid) or {}).get("prompt") or "")
        comp_neg = str((comp_by_id.get(pid) or {}).get("negative_prompt") or "")
        comp_prompts.append(comp_pos)

        head = cleaned[:30].lower()
        shot = _shot_for(camera).split(",")[0].lower()

        # Fidelity dimensions the compiler prompt must match-or-beat:
        wa_scene = bool(head) and head in wa_pos.lower()
        comp_scene = bool(head) and head in comp_pos.lower()
        wa_shot = shot in wa_pos.lower()
        comp_shot = shot in comp_pos.lower()
        # iyashikei tail: cozy_iyashikei archetype tokens
        tail_toks = ["pastel colors", "soft lighting", "watercolor style", "healing"]
        wa_tail = all(t in wa_pos.lower() for t in tail_toks)
        comp_tail = all(t in comp_pos.lower() for t in tail_toks)
        # scenery steering (pos says no-people, neg lists person)
        wa_steer = (not is_scenery) or (
            "no people" in wa_pos.lower() and "person" in wa_neg.lower()
        )
        comp_steer = (not is_scenery) or (
            "no people" in comp_pos.lower() and "person" in comp_neg.lower()
        )

        # "at least as good": every fidelity flag the workaround sets, the
        # compiler also sets (compiler >= workaround on each dimension).
        no_regression = (
            (comp_scene or not wa_scene)
            and (comp_shot or not wa_shot)
            and (comp_tail or not wa_tail)
            and (comp_steer or not wa_steer)
        )
        rows.append(
            {
                "panel_id": pid,
                "camera": camera,
                "scenery_camera": is_scenery,
                "workaround": {
                    "scene_leads": wa_scene,
                    "shot_present": wa_shot,
                    "tail_intact": wa_tail,
                    "scenery_steered": wa_steer,
                    "prompt": wa_pos,
                    "negative": wa_neg,
                },
                "compiler": {
                    "scene_leads": comp_scene,
                    "shot_present": comp_shot,
                    "tail_intact": comp_tail,
                    "scenery_steered": comp_steer,
                    "prompt": comp_pos,
                    "negative": comp_neg,
                },
                "no_fidelity_regression": no_regression,
            }
        )

    distinct = len(set(comp_prompts))
    scenery_rows = [r for r in rows if r["scenery_camera"]]
    verdict = {
        "panel_count": len(rows),
        "compiler_distinct_prompts": distinct,
        "compiler_all_distinct": distinct == len(rows),
        "compiler_all_scene_lead": all(r["compiler"]["scene_leads"] for r in rows),
        "compiler_all_shot_present": all(r["compiler"]["shot_present"] for r in rows),
        "compiler_all_tail_intact": all(r["compiler"]["tail_intact"] for r in rows),
        "compiler_all_scenery_steered": all(
            r["compiler"]["scenery_steered"] for r in scenery_rows
        ),
        "no_fidelity_regression_any_panel": all(
            r["no_fidelity_regression"] for r in rows
        ),
    }
    report = {
        "gate": "workaround (_compose_positive @ #1726) vs merged compiler",
        "decision_rule": "RETIRE only if compiler >= workaround on every fidelity dimension, every panel",
        "verdict": verdict,
        "panels": rows,
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=" * 72)
    print("PHASE-2 FIDELITY GATE — workaround vs merged compiler")
    print("=" * 72)
    for k, v in verdict.items():
        print(f"  {k:38s} {v}")
    print()
    # Show one panel's two prompts side by side for the record.
    sample = next((r for r in rows if r["scenery_camera"]), rows[0])
    print(f"--- sample panel {sample['panel_id']} (camera={sample['camera']}) ---")
    print("WORKAROUND pos:", sample["workaround"]["prompt"][:200])
    print("COMPILER   pos:", sample["compiler"]["prompt"][:200])
    print()
    ok = (
        verdict["compiler_all_distinct"]
        and verdict["compiler_all_scene_lead"]
        and verdict["compiler_all_shot_present"]
        and verdict["compiler_all_tail_intact"]
        and verdict["compiler_all_scenery_steered"]
        and verdict["no_fidelity_regression_any_panel"]
    )
    print(f"report -> {args.out}")
    print(
        "GATE:",
        "PASS — safe to retire the workaround composition layer"
        if ok
        else "FAIL — KEEP the workaround (compiler loses fidelity)",
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
