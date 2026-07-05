"""brand_admin_weekly_os_data.json lane routing + zh market truth."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "brand-wizard-app" / "public" / "brand_admin_weekly_os_data.json"


def _load() -> dict:
    assert DATA.is_file(), f"missing {DATA} — run gen_brand_admin_weekly_os_data.py"
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_lane_to_market_zh_tw_and_cn():
    data = _load()
    lane = data["lane_to_market"]
    assert lane["zh_tw"] == "zh_tw"
    assert lane["zh_cn"] == "zh_cn"
    assert lane["ja_jp"] == "ja_jp"
    assert lane["en_us"] == "en_us"


def test_zh_tw_readmoo_planned_not_ready_upload():
    data = _load()
    tw = data["markets"]["zh_tw"]
    readmoo = next(s for s in tw["setup"] if s["id"] == "readmoo")
    assert readmoo["status"] == "planned"
    assert "readmoo" in (readmoo.get("planned_note") or "").lower()
    u_readmoo = next(u for u in tw["uploads"] if u["id"] == "u_readmoo")
    assert u_readmoo["status"] == "planned"


def test_zh_cn_ximalaya_planned():
    data = _load()
    cn = data["markets"]["zh_cn"]
    x = next(s for s in cn["setup"] if s["id"] == "ximalaya")
    assert x["status"] == "planned"


def test_zh_tw_week_prioritizes_google_play_before_kdp():
    data = _load()
    week = data["markets"]["zh_tw"]["week"]
    tue = next(d for d in week if d["day"] == "TUE")
    task_text = " ".join(t["t"] for t in tue["tasks"]).lower()
    assert "google play" in task_text
    assert "kobo" in task_text
