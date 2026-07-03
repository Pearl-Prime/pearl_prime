"""SCENE-kill: generate_variants routes SCENE to Qwen and never splices {location.*}."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
MOD_PATH = REPO / "scripts" / "registry" / "generate_topic_registry.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("generate_topic_registry", MOD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _load_mod()


def test_scene_bypasses_persona_pool_and_uses_qwen(gen, monkeypatch):
    calls: list[dict] = []

    def fake_qwen(**kwargs):
        calls.append(kwargs)
        return (
            "You open the banking app. The balance is lower than last Tuesday. "
            "Your thumb hovers over the transfer button and does not move."
        )

    monkeypatch.setattr(gen, "qwen_generate", fake_qwen)
    monkeypatch.setattr(gen, "_load_cached", lambda *a, **k: None)
    monkeypatch.setattr(gen, "_save_cache", lambda *a, **k: None)
    monkeypatch.setattr(gen, "_track", lambda *a, **k: None)

    robotic = (
        "The rain continues outside the window as the statistics scroll by "
        "and the notification badge ticks upward without mercy or pause."
    )
    variants, prov = gen.generate_variants(
        topic="financial_stress",
        ch_key="chapter_01",
        sec_key="section_02",
        sec_spec={
            "seq": 2,
            "type": "SCENE",
            "scene_type": "digital",
            "location_aware": True,
            "min_variants": 2,
        },
        sec_id="ch01_sec02",
        section_purpose="Phone-bank balance check at 11pm",
        chapter_title="The Number That Won't Sit Still",
        arc_role="recognition",
        skin={},
        persona_atoms={"SCENE": [robotic, robotic, robotic]},
        teacher_atoms={},
        min_variants=2,
        dry_run=False,
        resume=False,
    )

    assert len(variants) == 2
    assert prov["qwen_generated"] == 2
    assert prov["atom_pool"] == 0
    assert len(calls) == 2
    assert all(c["section_purpose"] == "Phone-bank balance check at 11pm" for c in calls)
    assert all(c["location_token"] is None for c in calls)
    for v in variants:
        assert "rain continues" not in v["content"]
        assert "{location." not in v["content"]
        assert "{weather_detail}" not in v["content"]
        assert v["_provenance"] == "qwen_generated"


def test_hook_still_uses_persona_pool(gen, monkeypatch):
    monkeypatch.setattr(
        gen,
        "qwen_generate",
        lambda **k: (_ for _ in ()).throw(AssertionError("HOOK must not call Qwen when pool is full")),
    )
    monkeypatch.setattr(gen, "_load_cached", lambda *a, **k: None)
    monkeypatch.setattr(gen, "_save_cache", lambda *a, **k: None)
    monkeypatch.setattr(gen, "_track", lambda *a, **k: None)

    hook = "You notice the jaw clench before the meeting starts and the room goes quiet." * 3
    variants, prov = gen.generate_variants(
        topic="anxiety",
        ch_key="chapter_01",
        sec_key="section_01",
        sec_spec={
            "seq": 1,
            "type": "HOOK",
            "scene_type": None,
            "location_aware": False,
            "min_variants": 1,
        },
        sec_id="ch01_sec01",
        section_purpose="Opening recognition",
        chapter_title="Chapter 1",
        arc_role="recognition",
        skin={},
        persona_atoms={"HOOK": [hook]},
        teacher_atoms={},
        min_variants=1,
        dry_run=False,
        resume=False,
    )
    assert prov["atom_pool"] == 1
    assert variants[0]["_provenance"] == "atom_pool"
