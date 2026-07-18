from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "video" / "run_voice_synthesis.py"


def test_run_voice_synthesis_help():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "Stage 14b" in r.stdout
    # The help must advertise the free/local providers as the only choices and
    # promise ElevenLabs is down-routed (never an active path).
    assert "edge_tts" in r.stdout and "cosyvoice2" in r.stdout
    assert "down-routed" in r.stdout


def test_run_voice_synthesis_importable():
    """Module must import without side effects (caller relies on this)."""
    r = subprocess.run(
        [sys.executable, "-c", "import scripts.video.run_voice_synthesis as m; assert hasattr(m, 'synthesize_plan')"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr


def test_run_voice_synthesis_dry_run_en(tmp_path):
    """Dry-run over a minimal soundtrack_plan emits plan_with_audio and never uses ElevenLabs."""
    plan = {
        "plan_id": "plan-test-voice-001",
        "channel_id": "ch_001",
        "narration_segments": [
            {"segment_id": "seg-1", "text": "Breathing in, I notice the floor.", "start_time_s": 0.0, "end_time_s": 3.0},
            {"segment_id": "seg-2", "text": "", "start_time_s": 3.0, "end_time_s": 4.0},
        ],
    }
    plan_path = tmp_path / "soundtrack_plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    out_dir = tmp_path / "audio"

    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "-o", str(out_dir),
         "--locale", "en-US", "--dry-run"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    out_plan = out_dir / "soundtrack_plan_with_audio.json"
    assert out_plan.exists()
    doc = json.loads(out_plan.read_text(encoding="utf-8"))
    vs = doc["voice_synthesis"]
    assert vs["elevenlabs_used"] is False
    # EN must down-route to a free provider, never elevenlabs/openai.
    assert vs["provider"] in ("edge_tts", "cosyvoice2")
    # The empty-text segment is marked, the real one is scheduled.
    statuses = {s["segment_id"]: s.get("audio_status") for s in doc["narration_segments"]}
    assert statuses["seg-1"] == "dry_run"
    assert statuses["seg-2"] == "empty_text"


def test_run_voice_synthesis_dry_run_cjk(tmp_path):
    """CJK locale routes to CosyVoice2 (free Pearl Star path)."""
    plan = {
        "plan_id": "plan-test-voice-cjk",
        "channel_id": "ch_001",
        "narration_segments": [
            {"segment_id": "seg-1", "text": "息を吸って、床に気づく。", "start_time_s": 0.0, "end_time_s": 3.0},
        ],
    }
    plan_path = tmp_path / "soundtrack_plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    out_dir = tmp_path / "audio"
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "-o", str(out_dir),
         "--locale", "ja-JP", "--dry-run"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    doc = json.loads((out_dir / "soundtrack_plan_with_audio.json").read_text(encoding="utf-8"))
    assert doc["voice_synthesis"]["provider"] == "cosyvoice2"
    assert doc["voice_synthesis"]["elevenlabs_used"] is False
