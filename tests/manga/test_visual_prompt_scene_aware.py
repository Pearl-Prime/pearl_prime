"""Regression guard: the manga visual-prompt compilers are SCENE-AWARE.

Before this fix both in-scope compilers emitted a scene-agnostic prompt — the
positive prompt was the pure style archetype, byte-identical across every panel
regardless of its authored ``action`` — so a real FLUX backend rendered a chapter
as ~N near-identical portraits.

These tests compile >= 3 panels with DISTINCT authored actions and assert the
resulting positive prompts DIFFER (the divergence guard), while the iyashikei /
drawing-tradition style tail is still appended (no style-id regression to the
dark_psychological / ahjan defaults).

Covers both compiler entry points:
  * phoenix_v4/manga/visual_prompt_compiler.compile_visual_prompt
    (atom-based path; the production caller feeds it the panel's authored
    action + camera)
  * phoenix_v4/manga/chapter/visual_from_script_v3.compile_v3_panel_prompts
    (v3 chapter-script / writer-handoff path the GPU renderer consumes)
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.visual_from_script_v3 import (  # type: ignore
    compile_v3_panel_prompts,
)
from phoenix_v4.manga.visual_prompt_compiler import (  # type: ignore
    VisualPromptRequest,
    compile_visual_prompt,
)

# Three panels with clearly distinct authored beats + camera framings.
_PANELS = [
    {
        "panel_id": "p_1_0",
        "camera": "establishing-wide",
        "action": "Dawn over the hospice garden; mist sits low over the wet gravel path.",
        "mood": "calm",
    },
    {
        "panel_id": "p_1_1",
        "camera": "medium",
        "action": "Amara moves down the corridor at a clip, chart under one arm.",
        "mood": "tense",
    },
    {
        "panel_id": "p_2_0",
        "camera": "close-up",
        "action": "Close on her hands squaring a blanket at the corners, each task clean.",
        "mood": "calm",
    },
]


def _v3_script(panels: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": "devotion_test",
        "chapter_id": "ep_001",
        "style": "cozy_iyashikei",
        "main_characters": [
            {"id": "amara", "name": "Amara", "visual_anchor": "short dark hair, pale scrubs"}
        ],
        "pages": [{"panels": panels}],
    }


# ─── compile_visual_prompt (atom-based path) ───────────────────────────────


def test_compile_visual_prompt_diverges_per_panel_action() -> None:
    """Distinct authored actions -> distinct positive prompts (the core guard)."""
    prompts = [
        compile_visual_prompt(
            VisualPromptRequest(
                atom_type="STORY",
                style_id="cozy_iyashikei",
                teacher_id="sai_ma",
                action=p["action"],
                camera=p["camera"],
            )
        )["positive"]
        for p in _PANELS
    ]
    # Every panel must produce a unique positive prompt.
    assert len(set(prompts)) == len(prompts) == 3
    # And the authored action text must actually appear in its own prompt.
    for panel, prompt in zip(_PANELS, prompts):
        assert panel["action"][:24] in prompt


def test_compile_visual_prompt_leads_with_authored_scene() -> None:
    """The authored action + camera shot-type LEAD the prompt (FLUX weighting)."""
    out = compile_visual_prompt(
        VisualPromptRequest(
            atom_type="STORY",
            style_id="cozy_iyashikei",
            teacher_id="sai_ma",
            action="Dawn over the hospice garden.",
            camera="establishing-wide",
        )
    )
    pos = out["positive"]
    # Scene action is first; the style archetype no longer hijacks the lead.
    assert pos.startswith("Dawn over the hospice garden")
    assert "wide establishing shot" in pos
    # Style tail (cozy_iyashikei) is still appended — no style-id regression.
    assert "watercolor" in pos.lower() or "cozy" in pos.lower()
    assert out["style_id"] == "cozy_iyashikei"


def test_compile_visual_prompt_no_action_is_legacy_byte_identical() -> None:
    """Fail-open: with no authored scene data the legacy assembly is unchanged."""
    legacy = compile_visual_prompt(VisualPromptRequest(atom_type="STORY"))
    # Still leads with the teacher/style archetype exactly as before the fix.
    assert legacy["positive"].startswith("young woman, dark hair")
    assert legacy["style_id"] == "dark_psychological"


# ─── compile_v3_panel_prompts (writer-handoff path) ────────────────────────


def test_compile_v3_diverges_per_panel_on_writer_handoff() -> None:
    """The v3 path reads the handoff's ``action``/``camera`` and diverges."""
    out = compile_v3_panel_prompts(_v3_script(_PANELS))
    prompts = [p["prompt"] for p in out["panels"]]
    assert out["total_panels"] == 3
    assert len(set(prompts)) == 3  # all distinct — was byte-identical before
    for panel, prompt in zip(_PANELS, prompts):
        assert panel["action"][:24] in prompt
    # iyashikei style tail still present on every panel (no regression).
    for prompt in prompts:
        assert "iyashikei" in prompt.lower()
