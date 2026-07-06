from phoenix_v4.planning.legacy_template_loader import resolve_template_library


def test_somatic_gen_z_standard():
    # Twelve-shape continuity plan routes all formats to spine_only for this cell.
    assert resolve_template_library("anxiety", "gen_z_professionals", "standard_book") == "spine_only"


def test_somatic_professional_standard():
    assert resolve_template_library("burnout", "burned_out_professional", "standard_book") == "v2_somatic"


def test_cognitive_falls_to_spine():
    assert resolve_template_library("overthinking", "gen_z_professionals", "standard_book") == "spine_only"


def test_relational_falls_to_spine():
    assert resolve_template_library("boundaries", "nyc_executives", "standard_book") == "spine_only"


def test_unknown_topic_fallback():
    assert resolve_template_library("unknown_topic", "gen_z_professionals", "standard_book") == "spine_only"


def test_unknown_persona_fallback():
    assert resolve_template_library("anxiety", "unknown_persona", "standard_book") == "spine_only"


def test_missing_config_fallback():
    assert resolve_template_library(
        "anxiety",
        "gen_z_professionals",
        "standard_book",
        routing_config_path="config/templates/nonexistent.yaml",
    ) == "spine_only"


# OPD-106 (2026-05-18): long runtimes (extended_book_2h, deep_book_4h, deep_book_6h)
# must route to v2_somatic for somatic topics, matching standard_book behaviour and
# their SOMATIC_FULL_RUNTIME_FORMATS membership in phoenix_v4/planning/beatmap_compile.py.
def test_somatic_gen_z_deep_book_6h():
    assert resolve_template_library("anxiety", "gen_z_professionals", "deep_book_6h") == "spine_only"


def test_somatic_gen_z_extended_book_2h():
    assert resolve_template_library("anxiety", "gen_z_professionals", "extended_book_2h") == "spine_only"


def test_somatic_gen_z_deep_book_4h():
    assert resolve_template_library("anxiety", "gen_z_professionals", "deep_book_4h") == "spine_only"


def test_somatic_professional_deep_book_6h():
    assert resolve_template_library("burnout", "burned_out_professional", "deep_book_6h") == "v2_somatic"


def test_somatic_executive_deep_book_6h():
    # Executive voice at deep depths routes to v2_somatic — register collision only
    # affects compact formats (short_book_30 stays spine_only for executive).
    assert resolve_template_library("anxiety", "nyc_executives", "deep_book_6h") == "v2_somatic"


def test_cognitive_deep_book_6h_falls_to_spine():
    # Long runtimes for non-somatic families still fall to spine_only (no template bank).
    assert resolve_template_library("overthinking", "gen_z_professionals", "deep_book_6h") == "spine_only"
