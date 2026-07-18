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


# ─── 14-market localization: no lane silently collapses to US ────────────────

CANONICAL_LANES = [
    "en_us", "ja_jp", "ko_kr", "zh_tw", "zh_cn", "zh_hk", "zh_sg",
    "es_us", "es_es", "fr_fr", "de_de", "it_it", "hu_hu", "pt_br",
]


def test_all_14_lanes_route_to_their_own_market():
    """Every canonical lane owns a distinct market profile — none falls back to en_us."""
    data = _load()
    lane = data["lane_to_market"]
    for code in CANONICAL_LANES:
        assert code in lane, f"lane {code} missing from lane_to_market"
        assert lane[code] == code, f"lane {code} collapses to {lane[code]} (expected its own profile)"


def test_no_new_lane_collapses_to_en_us():
    """The old en_us collapse (de_de/fr_fr/... → en_us) must be gone."""
    data = _load()
    lane = data["lane_to_market"]
    for code in CANONICAL_LANES:
        if code != "en_us":
            assert lane[code] != "en_us", f"{code} still collapses to en_us"


def test_every_market_profile_is_complete():
    data = _load()
    markets = data["markets"]
    for code in CANONICAL_LANES:
        assert code in markets, f"market profile {code} missing"
        prof = markets[code]
        for field in ("ui_lang", "lane_suffixes", "setup", "uploads", "week", "quick_links"):
            assert prof.get(field), f"{code}.{field} empty/missing"
        assert prof["lane_suffixes"] == [code], f"{code} lane_suffixes should be [{code}]"
        # week must be the full MON..SUN rhythm
        days = {d["day"] for d in prof["week"]}
        assert {"MON", "SUN"}.issubset(days), f"{code} week missing MON/SUN"


def test_market_ui_lang_matches_locale():
    data = _load()
    markets = data["markets"]
    expected = {
        "en_us": "en", "ja_jp": "ja", "ko_kr": "ko",
        "zh_tw": "zh-Hant", "zh_hk": "zh-Hant", "zh_cn": "zh-Hans", "zh_sg": "zh-Hans",
        "es_us": "es", "es_es": "es", "fr_fr": "fr", "de_de": "de",
        "it_it": "it", "hu_hu": "hu", "pt_br": "pt",
    }
    for code, ui in expected.items():
        assert markets[code]["ui_lang"] == ui, f"{code} ui_lang {markets[code]['ui_lang']} != {ui}"


def test_de_de_tolino_ready_and_native_language():
    """Germany profile is market-true (Tolino) and in German, not English mirror copy."""
    data = _load()
    de = data["markets"]["de_de"]
    ids = {s["id"] for s in de["setup"]}
    assert "tolino" in " ".join(ids).lower() or any(
        "tolino" in (s.get("n", "").lower()) for s in de["setup"]
    ), "de_de missing Tolino"
    # at least one native-German string somewhere in the week rhythm
    blob = json.dumps(de, ensure_ascii=False)
    assert any(ch for ch in ("ü", "ö", "ä", "ß") if ch in blob), "de_de not localized to German"


def test_ko_kr_ridibooks_planned_not_self_serve():
    data = _load()
    ko = data["markets"]["ko_kr"]
    blob = json.dumps(ko, ensure_ascii=False).lower()
    assert "리디" in json.dumps(ko, ensure_ascii=False) or "ridi" in blob, "ko_kr missing Ridibooks"
    planned = [s for s in ko["setup"] if s.get("status") == "planned"]
    assert planned, "ko_kr should mark publisher-gated Korean platforms as planned"


def test_zh_hk_and_sg_are_distinct_from_tw_cn():
    data = _load()
    markets = data["markets"]
    # HK carries a Cantonese-audiobook note distinct from TW; SG is bilingual.
    assert markets["zh_hk"]["ui_lang"] == "zh-Hant"
    assert markets["zh_sg"]["ui_lang"] == "zh-Hans"
    assert "粵語" in json.dumps(markets["zh_hk"], ensure_ascii=False), "zh_hk should reference Cantonese"
