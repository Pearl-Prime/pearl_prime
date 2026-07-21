"""Music-mode catalog branch: registry resolution + BookSpec filtering."""
from __future__ import annotations

import logging
from pathlib import Path

import pytest

from phoenix_v4.planning.catalog_planner import BookSpec, CatalogPlanner
from scripts.catalog import music_mode_branch as mmb


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_resolve_music_brand_is_music_only():
    assert mmb.resolve_catalog_branch("_template_music", repo_root=REPO_ROOT) is mmb.CatalogBranch.MUSIC_ONLY


def test_resolve_path_x_brand_is_standard():
    assert mmb.resolve_catalog_branch("stillness_press", repo_root=REPO_ROOT) is mmb.CatalogBranch.STANDARD


def test_overlap_music_precedence_logs_warning(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)

    def fake_music(_root: Path) -> set[str]:
        return {"collision_brand"}

    def fake_path_x(_root: Path) -> set[str]:
        return {"collision_brand"}

    monkeypatch.setattr(mmb, "load_music_brand_ids", fake_music)
    monkeypatch.setattr(mmb, "load_path_x_brand_ids", fake_path_x)

    assert mmb.resolve_catalog_branch("collision_brand", repo_root=REPO_ROOT) is mmb.CatalogBranch.MUSIC_ONLY
    assert any("music_mode precedence" in r.getMessage() for r in caplog.records)


def test_filter_drops_teacher_mode_and_composite_tags():
    specs = [
        BookSpec(
            topic_id="grief",
            persona_id="nyc_exec",
            series_id=None,
            installment_number=None,
            teacher_id="default_teacher",
            brand_id="_template_music",
            angle_id="grief_general",
            domain_id="grief_cluster",
            seed="a",
            teacher_mode=False,
        ),
        BookSpec(
            topic_id="shame",
            persona_id="nyc_exec",
            series_id=None,
            installment_number=None,
            teacher_id="t1",
            brand_id="_template_music",
            angle_id="shame_general",
            domain_id="shame_cluster",
            seed="b",
            teacher_mode=True,
        ),
    ]
    filtered = mmb.filter_to_music_mode_book_specs(specs)
    assert len(filtered) == 1
    assert filtered[0].seed == "a"


def test_filter_dict_rows_teacher_mode_string():
    rows = [
        {"brand_id": "x", "teacher_mode": "false"},
        {"brand_id": "x", "teacher_mode": "true"},
    ]
    assert len(mmb.filter_catalog_entry_dicts_music_mode(rows)) == 1


def test_generate_for_brand_music_is_all_non_teacher_mode():
    planner = CatalogPlanner()
    specs = planner.generate_for_brand("_template_music", 12, seed="music_seed", repo_root=REPO_ROOT)
    assert specs
    assert all(not s.teacher_mode for s in specs)
    assert all(s.brand_id == "_template_music" for s in specs)


def test_generate_for_brand_path_x_matches_produce_wave():
    planner = CatalogPlanner()
    brand_id = "stillness_press"
    n = 8
    seed = "parity_seed"
    a = planner.generate_for_brand(brand_id, n, seed=seed, repo_root=REPO_ROOT)
    b = planner.produce_wave(n, seed=seed, brand_id=brand_id, teacher_mode=False)
    assert [x.to_dict() for x in a] == [x.to_dict() for x in b]


def test_resolve_music_args_for_brand_ahjan_music_defaults_with_lyrics():
    # ahjan_music is the one real active registry entry today; its survey has
    # output_preferences_with_lyrics.companion_ai_song_consent: true.
    assert mmb.resolve_music_args_for_brand("ahjan_music", repo_root=REPO_ROOT) == (
        "with-lyrics",
        "ahjan",
    )


def test_resolve_music_args_for_brand_inactive_registry_row_is_none():
    # _template_music is a schema-only placeholder (status: inactive) — must not
    # auto-trigger a music-mode render.
    assert mmb.resolve_music_args_for_brand("_template_music", repo_root=REPO_ROOT) is None


def test_resolve_music_args_for_brand_path_x_brand_is_none():
    assert mmb.resolve_music_args_for_brand("stillness_press", repo_root=REPO_ROOT) is None


def test_resolve_music_args_for_brand_unregistered_brand_is_none():
    assert mmb.resolve_music_args_for_brand("no_such_brand", repo_root=REPO_ROOT) is None


def test_resolve_music_args_for_brand_respects_survey_consent_false(tmp_path: Path):
    (tmp_path / "config" / "music").mkdir(parents=True)
    (tmp_path / "artifacts" / "musician_survey").mkdir(parents=True)
    (tmp_path / "config" / "music" / "music_brand_registry.yaml").write_text(
        """
music_brands:
  - brand_id: no_consent_music
    musician_handle: no_consent_artist
    status: active
    survey_yaml_pointer: artifacts/musician_survey/no_consent_survey.yaml
""",
        encoding="utf-8",
    )
    (tmp_path / "artifacts" / "musician_survey" / "no_consent_survey.yaml").write_text(
        """
output_preferences_with_lyrics:
  companion_ai_song_consent: false
""",
        encoding="utf-8",
    )
    assert mmb.resolve_music_args_for_brand("no_consent_music", repo_root=tmp_path) == (
        "no-lyrics",
        "no_consent_artist",
    )


def test_apply_auto_detected_music_args_fills_both_when_absent():
    # Mirrors argparse defaults: music_mode="none", musician_id=None (no CLI flags passed).
    assert mmb.apply_auto_detected_music_args(
        "ahjan_music",
        explicit_music_mode="none",
        explicit_musician_id=None,
        repo_root=REPO_ROOT,
    ) == ("with-lyrics", "ahjan")


def test_apply_auto_detected_music_args_explicit_flags_are_never_overridden():
    # Explicit --music-mode no-lyrics --musician-id ahjan on the same brand_id must win,
    # even though auto-detection for ahjan_music would resolve to with-lyrics.
    assert mmb.apply_auto_detected_music_args(
        "ahjan_music",
        explicit_music_mode="no-lyrics",
        explicit_musician_id="ahjan",
        repo_root=REPO_ROOT,
    ) == ("no-lyrics", "ahjan")


def test_apply_auto_detected_music_args_partial_explicit_still_autofills_other_field():
    # Operator explicitly names the musician but leaves music_mode to auto-detect.
    assert mmb.apply_auto_detected_music_args(
        "ahjan_music",
        explicit_music_mode=None,
        explicit_musician_id="ahjan",
        repo_root=REPO_ROOT,
    ) == ("with-lyrics", "ahjan")


def test_apply_auto_detected_music_args_non_music_brand_is_noop():
    # A Path X brand_id must not trigger any music branch: no flags in, no flags out.
    assert mmb.apply_auto_detected_music_args(
        "stillness_press",
        explicit_music_mode=None,
        explicit_musician_id=None,
        repo_root=REPO_ROOT,
    ) == ("none", None)


def test_apply_auto_detected_music_args_unregistered_brand_preserves_explicit_values():
    assert mmb.apply_auto_detected_music_args(
        "no_such_brand",
        explicit_music_mode="with-lyrics",
        explicit_musician_id="someone",
        repo_root=REPO_ROOT,
    ) == ("with-lyrics", "someone")


def test_generate_for_brand_topics_match_master_arc_inventory():
    planner = CatalogPlanner()
    specs = planner.generate_for_brand("stillness_press", 16, seed="arc_alignment", repo_root=REPO_ROOT)
    arc_pairs = set()
    for path in (REPO_ROOT / "config" / "source_of_truth" / "master_arcs").glob("*.yaml"):
        parts = path.stem.split("__")
        if len(parts) < 4:
            continue
        arc_pairs.add(("__".join(parts[:-3]), parts[-3]))

    missing = [(s.persona_id, s.topic_id) for s in specs if (s.persona_id, s.topic_id) not in arc_pairs]
    assert not missing, f"generate_for_brand produced non-arc-backed pairs: {missing[:5]}"
