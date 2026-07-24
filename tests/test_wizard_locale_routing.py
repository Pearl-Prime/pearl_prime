"""14-market wizard entry + locale routing invariants.

Static guards over the brand-wizard-app source so a dropped lane, a missing
locale loader, or a re-introduced US fallback fails CI — coverage beyond the
original TW/CN/JA/EN lanes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APP = REPO / "brand-wizard-app"

CANONICAL_LANES = [
    "en_US", "ja_JP", "ko_KR", "zh_TW", "zh_CN", "zh_HK", "zh_SG",
    "es_US", "es_ES", "fr_FR", "de_DE", "it_IT", "hu_HU", "pt_BR",
]
# new wizard string files (hk→tw, sg→zh reuse Traditional/Simplified by design)
NEW_LOCALE_FILES = ["ko", "es", "es_es", "fr", "de", "it", "hu", "pt"]


def _read(rel: str) -> str:
    return (APP / rel).read_text(encoding="utf-8")


def test_entry_screen_has_all_14_lanes_including_brazil():
    # pearl_prime_entry.html's 3-screen picker was replaced by a single-screen
    # flag grid on index.html (#166); each lane is a flag-card calling
    # enterWizard(code) directly rather than populated from a JS LANES object.
    html = _read("public/index.html")
    for code in CANONICAL_LANES:
        assert f"enterWizard('{code}')" in html, f"entry screen missing lane {code}"
    assert "enterWizard('pt_BR')" in html, "Brazil (pt_BR) missing from entry screen"


def test_entry_screen_routes_every_lane_to_a_localized_wizard():
    html = _read("public/index.html")
    wizard = re.search(r"var LANE_WIZARD = \{(.+?)\};", html, re.S).group(1)
    market = re.search(r"var LANE_MARKET = \{(.+?)\};", html, re.S).group(1)
    for code in CANONICAL_LANES:
        assert re.search(rf"\b{code}\s*:", wizard), f"LANE_WIZARD missing {code}"
        assert re.search(rf"\b{code}\s*:", market), f"LANE_MARKET missing {code}"
    # non-English lanes must NOT point at the bare English wizard
    for code in CANONICAL_LANES:
        if code == "en_US":
            continue
        val = re.search(rf"{code}\s*:\s*\"([^\"]+)\"", wizard).group(1)
        assert val != "wizard.html", f"{code} routes to US-English wizard.html"


def test_entry_screen_preserves_weekly_operations_link():
    html = _read("public/index.html")
    assert 'href="brand_admin_weekly_os.html"' in html, (
        "split entry must preserve access to weekly brand operations"
    )


def test_brandmatch_maps_every_lane_to_itself():
    js = _read("src/brandMatch.js")
    block = re.search(r"LANE_FROM_MARKET = \{(.+?)\};", js, re.S).group(1)
    lane_map = dict(re.findall(r'(\w+)\s*:\s*"(\w+)"', block))
    for code in CANONICAL_LANES:
        low = code.lower()
        assert lane_map.get(low) == low, f"brandMatch lane {low} != itself ({lane_map.get(low)})"
    # the countries the old map dropped (would fall to en_us)
    for word, lane in [("france", "fr_fr"), ("germany", "de_de"), ("italy", "it_it"), ("hungary", "hu_hu")]:
        assert lane_map.get(word) == lane, f"brandMatch {word} -> {lane_map.get(word)} (expected {lane})"


def test_i18n_has_loaders_for_all_locales():
    js = _read("src/i18n.jsx")
    block = re.search(r"LOCALE_LOADERS = \{(.+?)\};", js, re.S).group(1)
    for key in ["en", "ja", "zh", "tw", "ko", "es", "es_es", "fr", "de", "it", "hu", "pt"]:
        assert re.search(rf"\b{re.escape(key)}\s*:", block), f"i18n LOCALE_LOADERS missing {key}"


def test_new_locale_string_files_present_and_parse():
    en_keys = _keyset(json.loads(_read("src/strings-en.json")))
    for loc in NEW_LOCALE_FILES:
        p = APP / "src" / f"strings-{loc}.json"
        assert p.is_file(), f"missing strings-{loc}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        ks = _keyset(data)
        assert ks == en_keys, f"strings-{loc}.json key drift vs en (missing {len(en_keys-ks)}, extra {len(ks-en_keys)})"


def test_public_i18n_no_us_fallback_for_italy_or_spanish():
    js = _read("public/assets/i18n.js")
    block = re.search(r"LANE_TO_LOCALE = \{(.+?)\};", js, re.S).group(1)
    lane_loc = dict(re.findall(r'(\w+)\s*:\s*"([\w-]+)"', block))
    assert lane_loc.get("it_IT") == "it-IT", "it_IT must not fall back to en-US"
    assert lane_loc.get("es_US") == "es-US"
    assert lane_loc.get("es_ES") == "es-ES"
    # zh-HK / zh-SG intentionally reuse Traditional / Simplified chrome (same script)
    assert lane_loc.get("zh_HK") == "zh-TW"
    assert lane_loc.get("zh_SG") == "zh-CN"


def _keyset(d, p=""):
    s = set()
    for k, v in d.items():
        kk = f"{p}.{k}" if p else k
        if isinstance(v, dict):
            s |= _keyset(v, kk)
        else:
            s.add(kk)
    return s
