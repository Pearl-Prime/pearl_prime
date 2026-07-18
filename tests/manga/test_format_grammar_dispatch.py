"""Tests for format adaptation grammar dispatch (dag_order.get_compositor_for_format)."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from phoenix_v4.manga.runner.dag_order import get_compositor_for_format

FORMAT_YAML = Path("config/manga/format_adaptation_grammars.yaml")


@pytest.fixture(scope="module")
def grammar_data() -> dict:
    with open(FORMAT_YAML) as f:
        return yaml.safe_load(f)


def test_grammar_yaml_exists():
    assert FORMAT_YAML.is_file(), f"{FORMAT_YAML} not found"


def test_grammar_yaml_has_all_formats(grammar_data):
    formats = grammar_data.get("formats", {})
    required = {"print", "webtoon", "motion_comic", "vertical_short_teaser"}
    assert required.issubset(set(formats.keys())), (
        f"Missing formats: {required - set(formats.keys())}"
    )


def test_dispatch_known_formats():
    assert get_compositor_for_format("print") == "PrintCompositor"
    assert get_compositor_for_format("webtoon") == "WebtoonCompositor"
    assert get_compositor_for_format("motion_comic") == "MotionComicCompositor"
    assert get_compositor_for_format("vertical_short_teaser") == "VerticalTeaserCompositor"


def test_dispatch_unknown_format_raises():
    with pytest.raises(ValueError, match="Unknown format_id"):
        get_compositor_for_format("holographic_billboard")


def test_dispatch_and_yaml_compositor_names_agree(grammar_data):
    """compositor_class in YAML matches what dag_order dispatch returns."""
    formats = grammar_data.get("formats", {})
    for format_id, entry in formats.items():
        yaml_compositor = entry.get("compositor_class")
        code_compositor = get_compositor_for_format(format_id)
        assert yaml_compositor == code_compositor, (
            f"Format '{format_id}': YAML says compositor_class={yaml_compositor!r} "
            f"but dag_order dispatch returns {code_compositor!r}"
        )


def test_all_formats_have_required_fields(grammar_data):
    required = {"format_id", "reading_direction", "export", "compositor_class"}
    for fmt_id, entry in grammar_data.get("formats", {}).items():
        missing = required - set(entry.keys())
        assert not missing, f"Format '{fmt_id}' missing fields: {missing}"


def test_webtoon_has_no_spreads(grammar_data):
    webtoon = grammar_data["formats"]["webtoon"]
    assert webtoon.get("spread_enabled") is False, "Webtoon must have spread_enabled: false"


def test_print_supports_spreads(grammar_data):
    print_fmt = grammar_data["formats"]["print"]
    assert print_fmt.get("spread_enabled") is True, "Print must have spread_enabled: true"


def test_vertical_teaser_has_duration(grammar_data):
    vst = grammar_data["formats"]["vertical_short_teaser"]
    export = vst.get("export", {})
    assert "duration_target_seconds" in export, "vertical_short_teaser export must have duration_target_seconds"
