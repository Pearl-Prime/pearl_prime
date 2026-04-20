from phoenix_v4.planning.legacy_template_loader import resolve_template_library


def test_somatic_gen_z_standard():
    assert resolve_template_library("anxiety", "gen_z_professionals", "standard_book") == "v2_somatic"


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
