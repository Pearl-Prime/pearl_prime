from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_assemble_podcast_episode_outputs_json():
    out = REPO_ROOT / "artifacts" / "podcast_pilot" / "_test_assemble"
    out.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/podcast/assemble_podcast_episode.py"),
            "--book-dir",
            str(REPO_ROOT / "artifacts/pipeline_examples/ahjan"),
            "--brand-id",
            "stillness_press",
            "--locale",
            "es-US",
            "--format",
            "podcast_episode",
            "--week",
            "2026-W15",
            "--output-dir",
            str(out),
            "--no-job-check",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    js = list(out.glob("assembly_*.json"))
    assert len(js) == 1
    data = json.loads(js[0].read_text(encoding="utf-8"))
    assert data.get("format") == "podcast_episode"
    segs = data.get("segments") or []
    assert len(segs) >= 3
    assert data.get("voice_config", {}).get("edge_fallback")


def test_generate_podcast_feed_xml_structure():
    from scripts.podcast.generate_podcast_feed import build_feed

    episodes = [
        {
            "guid": "urn:test:1",
            "episode_id": "ep1",
            "title": "Test",
            "description": "Desc",
            "pub_date_rfc2822": "Thu, 09 Apr 2026 00:00:00 GMT",
            "enclosure_url": "https://example.com/e.mp3",
            "enclosure_length_bytes": 1234,
            "duration_s": 120,
            "episode_number": 1,
            "season_number": 1,
            "explicit": "no",
        }
    ]
    tree = build_feed(episodes, "stillness_press", "social_anxiety_arc", "https://cdn.example.com", {})
    root = tree.getroot()
    assert root.tag == "rss"
    ch = root.find("channel")
    assert ch is not None
    titles = ch.findall("title")
    assert titles and titles[0].text
    dur = ch.findall(".//item/{http://www.itunes.com/dtds/podcast-1.0.dtd}duration")
    assert len(dur) >= 1


def test_render_dry_run_cli():
    out_dir = REPO_ROOT / "artifacts" / "podcast_pilot" / "_test_assemble"
    js = list(out_dir.glob("assembly_*.json"))
    assert js, "run test_assemble first or share fixture"
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/podcast/render_podcast_audio.py"),
            "--assembly",
            str(js[0]),
            "--output",
            str(REPO_ROOT / "artifacts/podcast_pilot/_dry.mp3"),
            "--dry-run",
            "--no-job-check",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0
