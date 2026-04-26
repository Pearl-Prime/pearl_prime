"""Smoke tests for scripts/manga/generate_catalog_plan_from_strategic.py.

Per Phase 2X.1, the generator script must run cleanly against the live
strategic-tier docs on main without writing the catalog plan output.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "manga" / "generate_catalog_plan_from_strategic.py"


def _import_module():
    spec = importlib.util.spec_from_file_location("gcp_strategic", SCRIPT)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["gcp_strategic"] = mod  # required for dataclass type resolution on py3.9
    spec.loader.exec_module(mod)
    return mod


def test_module_imports():
    """Module must import without error and expose the parser API."""
    mod = _import_module()
    assert hasattr(mod, "VALID_GENRES")
    assert hasattr(mod, "VALID_LOCALES")
    assert hasattr(mod, "parse_genre_portfolio")
    assert hasattr(mod, "parse_locale_formats")
    assert hasattr(mod, "emit_catalog_plan")


def test_valid_genres_matches_spec_4_1():
    """VALID_GENRES must contain exactly 15 entries per spec §4.1.

    Drift here means the generator and the planner allow-list have diverged;
    Phase 2X.4 atomic merge would fail validation.
    """
    mod = _import_module()
    assert len(mod.VALID_GENRES) == 15, mod.VALID_GENRES
    expected = {
        "iyashikei", "dark_fantasy", "psychological_horror", "supernatural_mystery",
        "isekai", "sci_fi_cyberpunk", "psychological_thriller", "romance_josei_drama",
        "workplace_drama", "action_battle", "sports_competition", "historical_period",
        "cultivation_martial", "school_coming_of_age", "mecha",
    }
    assert set(mod.VALID_GENRES) == expected


def test_valid_locales_includes_kr_per_d_18():
    """VALID_LOCALES must include ko_KR per spec D-18 (5-locale matrix)."""
    mod = _import_module()
    assert "ko_KR" in mod.VALID_LOCALES
    assert len(mod.VALID_LOCALES) == 5


def test_dry_run_against_live_strategic_docs():
    """Dry run on the live strategic docs on main must succeed.

    This is the smoke test that catches parser regressions when the strategic
    plans get edited.
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert proc.returncode == 0, (
        f"--dry-run failed (returncode={proc.returncode}):\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    assert "parsed" in proc.stdout.lower()


def test_brand_metadata_affinity_picks_up_brand_id_tags():
    """warrior_calm_cultivation must pick up `cultivation` tag from brand_id."""
    mod = _import_module()
    tags = mod.derive_brand_tags("Burnout · Inner Peace · Shonen", "warrior_calm_cultivation")
    assert "cultivation" in tags
    assert "warrior" in tags
    assert "burnout" in tags
    assert "shonen" in tags


def test_distribute_with_spread_flagship_covers_all_15_genres():
    """Flagship target=16 must produce 1 series in every genre + 1 surplus.

    Under pure-market-share distribution (operator directive 2026-04-26), the
    surplus goes to the highest combined-weight genre — typically a mega-tier
    market genre (mecha, action_battle, dark_fantasy) rather than the brand's
    strategic-allocation primary.
    """
    mod = _import_module()
    strategic = {"iyashikei": 30.0, "dark_fantasy": 25.0, "psychological_horror": 20.0}
    affinity = {g: 0.5 for g in mod.VALID_GENRES}
    affinity["iyashikei"] = 1.0  # primary
    counts = mod.distribute_with_spread(
        target_series=16, strategic_alloc=strategic,
        metadata_affinity=affinity, tier="flagship",
    )
    assert sum(counts.values()) == 16
    nonzero = sum(1 for c in counts.values() if c > 0)
    assert nonzero == 15, f"expected all 15 genres represented; got {nonzero}"
    # Surplus goes to a mega-tier market genre (action_battle, mecha,
    # dark_fantasy, or isekai) under pure-market-share distribution.
    surplus_winners = {g for g, c in counts.items() if c >= 2}
    mega_tier = {"action_battle", "mecha", "dark_fantasy", "isekai"}
    assert surplus_winners & mega_tier, (
        f"expected surplus to land on a mega-tier genre; got winners {surplus_winners}"
    )


def test_distribute_with_spread_niche_concentrates_to_top_5():
    """Niche target=5 should distribute to the top-5 genres by combined weight."""
    mod = _import_module()
    strategic = {"action_battle": 35.0, "historical_period": 30.0}
    affinity = {g: 0.0 for g in mod.VALID_GENRES}
    affinity["action_battle"] = 1.0
    affinity["historical_period"] = 0.8
    affinity["dark_fantasy"] = 0.5
    counts = mod.distribute_with_spread(
        target_series=5, strategic_alloc=strategic,
        metadata_affinity=affinity, tier="niche",
    )
    assert sum(counts.values()) == 5
    nonzero = sum(1 for c in counts.values() if c > 0)
    assert nonzero == 5, f"niche target=5 should fill exactly 5 genres; got {nonzero}"
    # Top weight should be in the primary genre
    assert counts["action_battle"] >= 1


def test_emit_against_fixtures():
    """Generator must emit a catalog plan with the auto-generated banner header."""
    mod = _import_module()

    fixture_portfolio = """
### Flagship Brands (14–18 series target)

#### `stillness_press` — Anxiety · Somatic · Sleep · Josei adult women

| Genre | % | Series (of 16) | Primary Wellness Embed |
|---|---|---|---|
| Iyashikei / Slice | 30% | 5 | Somatic healing |
| Dark Fantasy | 25% | 4 | Grief |

### Niche / Focused Brands (4–6 series target)

#### `legacy_builder_memoir` — Self-Worth · Purpose · Seinen

| Genre | % | Series (of 5) | Primary Wellness Embed |
|---|---|---|---|
| Historical / Period | 60% | 3 | Legacy |
| Iyashikei / Slice | 40% | 2 | Daily worth |
"""
    fixture_cjk = """
| Locale | Format | Art Style | Platform |
|---|---|---|---|
| **JP** | Traditional B&W manga | Iyashikei minimalism | LINE Manga |
| **KR** | Vertical-scroll webtoon | Korean beauty | Naver Webtoon |
| **TW** | Hybrid manga page | Muted literary | LINE Comics TW |
| **CN** | Vertical-scroll tiáomàn | Soft pastels | Kuaikan |
| **US** | Manga digest 5x7.5 | Iyashikei minimalism | Bookstores |
"""
    brands = mod.parse_genre_portfolio(fixture_portfolio)
    assert len(brands) == 2, [b.brand_id for b in brands]
    assert brands[0].brand_id == "stillness_press"
    assert brands[0].tier == "flagship"
    assert brands[0].target_series == 16
    assert brands[0].genre_pct.get("iyashikei") == 30.0
    assert brands[0].genre_pct.get("dark_fantasy") == 25.0
    assert brands[1].brand_id == "legacy_builder_memoir"
    assert brands[1].tier == "niche"

    locales = mod.parse_locale_formats(fixture_cjk)
    assert set(locales.keys()) == set(mod.VALID_LOCALES)
    assert locales["ko_KR"].distribution_status == "hold_pending_market_clearance"
    assert locales["zh_CN"].distribution_status == "gray_zone_disclosed"
    assert locales["en_US"].distribution_status == "distributed"

    output = mod.emit_catalog_plan(brands, locales)
    assert "AUTO-GENERATED" in output
    assert "do not hand-edit" in output
    assert "stillness_press" in output
    assert "legacy_builder_memoir" in output
    assert "ko_KR" in output
    assert "hold_pending_market_clearance" in output
    assert "gray_zone_disclosed" in output
