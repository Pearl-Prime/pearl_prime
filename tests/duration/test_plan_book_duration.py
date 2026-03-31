from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration.plan_book_duration import plan_book  # noqa: E402


def test_blueprint_slots():
    d = plan_book("millennial_women_professionals", "audiobook", "therapeutic")
    assert d["chapters_min"] >= 8
    assert d["chapters_max"] <= 20
    assert d["slots_per_chapter"] == 10


def test_gen_z_shorter_audiobook():
    d = plan_book("gen_z_professionals", "audiobook", "therapeutic")
    assert d["audiobook_target_hours"] <= 5.5


def test_ebook_pages():
    d = plan_book("entrepreneurs", "ebook", "therapeutic")
    assert d["ebook_target_pages_min"] >= 150


def test_cli(tmp_path):
    out = tmp_path / "b.json"
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "duration" / "plan_book_duration.py"), "-o", str(out)],
        cwd=REPO_ROOT,
        check=True,
    )
    assert json.loads(out.read_text(encoding="utf-8"))["audiobook_target_hours"]
