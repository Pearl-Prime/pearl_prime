"""Tests for cumulative VoiceProfile clamping (onboarding TTS)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "onboarding" / "generate_briefing_narration.py"
_MOD_NAME = "generate_briefing_narration_testmod"


@pytest.fixture(scope="module")
def gen_mod():
    spec = importlib.util.spec_from_file_location(_MOD_NAME, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MOD_NAME] = mod
    spec.loader.exec_module(mod)
    return mod


def test_voice_profile_clamp_high(gen_mod) -> None:
    p = gen_mod.VoiceProfile(stability=0.99)
    p.clamp({"stability": [0.22, 0.78]})
    assert p.stability == pytest.approx(0.78)


def test_voice_profile_clamp_low(gen_mod) -> None:
    p = gen_mod.VoiceProfile(prosody_rate_percent=80.0)
    p.clamp({"prosody_rate_percent": [86.0, 118.0]})
    assert p.prosody_rate_percent == pytest.approx(86.0)


def test_apply_mapping_delta(gen_mod) -> None:
    p = gen_mod.VoiceProfile(style=0.1)
    gen_mod._apply_mapping_delta(p, {"style": 0.05, "unknown": 999})
    assert p.style == pytest.approx(0.15)
