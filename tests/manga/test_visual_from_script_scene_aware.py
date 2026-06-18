"""Regression guard: the v1/v2 production compiler is SCENE-AWARE.

Companion to ``tests/manga/test_visual_prompt_scene_aware.py`` (which guards the
v3 / writer-handoff path + the low-level ``compile_visual_prompt``). This file
guards the *older v1/v2 production entry point*
``phoenix_v4.manga.chapter.visual_from_script.compile_panel_prompts_from_chapter_script``
— the path that ``run_chapter_visual`` / ``chapter_runner`` actually drive.

The defect: ``_panel_to_request`` read each panel's authored ``action`` only as
``atom_text`` (which never enters the prompt) and dropped the authored
``camera`` entirely, so the positive prompt was the scene-agnostic style/teacher
archetype. Panels that share a mood collapsed to byte-identical prompts and a
real FLUX backend rendered the chapter as ~N near-identical portraits.

The fix forwards the authored ``action`` + ``camera`` into ``VisualPromptRequest``
so the compiler leads each panel's positive prompt with that panel's own beat.

Merge-order note: the scene-aware ``action``/``camera`` fields on
``VisualPromptRequest`` are added by the sibling PR #1728 (which owns the v3
compiler + ``visual_prompt_compiler``). This v1/v2 caller forwards them
*fail-open* — only when the dataclass supports them — so it is byte-identical to
the legacy output until #1728 lands and scene-aware the instant it does. The
strong divergence assertion is therefore gated on
``_REQUEST_SUPPORTS_SCENE`` (True once #1728 is on the branch); the
non-regression assertions run unconditionally.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.visual_from_script import (  # type: ignore
    _REQUEST_SUPPORTS_SCENE,
    compile_panel_prompts_from_chapter_script,
)

# Four panels with clearly distinct authored beats + camera framings. Two share
# the "calm" mood (panels 0 and 3) — under the old scene-agnostic assembly those
# two collapsed to one byte-identical prompt, so 4 panels yielded < 4 unique.
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
        "action": "Amara moves down the corridor at a clip, chart tucked under one arm.",
        "mood": "tense",
    },
    {
        "panel_id": "p_2_0",
        "camera": "close-up",
        "action": "Close on her hands squaring a blanket at the corners, each motion clean.",
        "mood": "calm",
    },
    {
        "panel_id": "p_2_1",
        "camera": "over-shoulder",
        "action": "Over her shoulder: an old man at the window watching the first light.",
        "mood": "tense",
    },
]


def _chapter_script(panels: list[dict]) -> dict:
    return {"pages": [{"page_number": 1, "panels": panels}]}


def _prompts() -> list[str]:
    doc = compile_panel_prompts_from_chapter_script(
        _chapter_script(_PANELS),
        style_id="cozy_iyashikei",
        teacher_id="sai_ma",
        genre_id="healing",
    )
    assert len(doc["panels"]) == len(_PANELS)
    return [str(p["prompt"]) for p in doc["panels"]]


@pytest.mark.skipif(
    not _REQUEST_SUPPORTS_SCENE,
    reason="scene-aware action/camera fields land with PR #1728; v1/v2 caller is "
    "byte-identical until then",
)
def test_v1v2_diverges_per_panel_action() -> None:
    """Distinct authored actions -> distinct positive prompts (the core guard).

    Before the fix these 4 panels produced < 4 unique prompts (the two "calm"
    panels collided). After the fix every panel renders its own beat.
    """
    prompts = _prompts()
    assert len(set(prompts)) == len(prompts) == 4
    # Each panel's authored action text must appear in its own prompt …
    for panel, prompt in zip(_PANELS, prompts):
        assert panel["action"][:24] in prompt
    # … and lead it (FLUX weights leading tokens most).
    assert prompts[0].startswith("Dawn over the hospice garden")
    # The camera shot-type rides right behind the authored beat.
    assert "wide establishing shot" in prompts[0]


@pytest.mark.skipif(
    not _REQUEST_SUPPORTS_SCENE,
    reason="scene-aware action/camera fields land with PR #1728",
)
def test_v1v2_keeps_iyashikei_style_tail() -> None:
    """No style-id regression: the cozy_iyashikei tail still rides every panel."""
    for prompt in _prompts():
        low = prompt.lower()
        # The genre-tradition / style tail (iyashikei register) survives the
        # scene-lead — the prompt is not just the bare authored action.
        assert any(
            k in low for k in ("watercolor", "cozy", "iyashikei", "gentle", "soft")
        )


def test_v1v2_every_panel_has_a_prompt_no_regression() -> None:
    """Unconditional: a multi-panel v1/v2 chapter compiles one prompt per panel.

    Runs in BOTH regimes (with and without #1728). Guards the fail-open contract:
    forwarding action/camera never drops, empties, or duplicates panel coverage,
    and never raises for scriptless callers.
    """
    prompts = _prompts()
    assert len(prompts) == len(_PANELS)
    assert all(p.strip() for p in prompts)
