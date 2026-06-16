"""
Lane C — cross-persona bleed isolation regression
(COMPOSER_FRONTIER_FIX_SPEC_20260614 DEFECT 4).

Defect:
    The topic-keyed registry/{topic}.yaml was authored 100% from one persona
    (label "Gen Z" == persona_id "gen_z_professionals"). The registry read path
    in phoenix_v4/planning/enrichment_select.py had NO persona filter, so
    corporate_managers books rendered gen_z-authored HOOK content (verified
    pilot books 04/05: 12 foreign-persona hook lines each, the foreign string
    NOT present in the corp_mgr atom file — the registry was the vector).

Fix:
    Make the registry read persona-aware at every entry point:
      * _registry_type_lists(ch_data, persona_id=...) — the single chokepoint
        feeding _try_registry_variant / _peek_registry_variant /
        _extra_registry_variant_bodies (both call sites in select_enrichment and
        peek_registry_content_for_beatmap_slot).
      * the standalone "registry_variant" depth resolver in _load_depth_content,
        which iterates sections directly (not via _registry_type_lists).
    Plus a placeholder guard so unauthored "[Persona-specific hook for ...]"
    stubs never render regardless of persona.

INVARIANT UNDER TEST: a registry variant authored for persona X must NEVER be
selected when building for persona Y.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from phoenix_v4.planning import enrichment_select as es


# ---------------------------------------------------------------------------
# Synthetic registry chapter — one HOOK section authored for "Gen Z", with one
# real (>20 word) variant and one unauthored placeholder stub variant.
# ---------------------------------------------------------------------------

_GEN_Z_REAL_HOOK = (
    "You finish the task and immediately open the next one. There is no pause "
    "between them. The list simply continues, and you have stopped noticing "
    "that it never actually ends or lets you rest at all."
)
_PLACEHOLDER_STUB = "[Persona-specific hook for gen_z_professionals × burnout]"


def _gen_z_chapter_dict() -> dict:
    """A chapter['sections'] dict shaped like the real registry, persona=Gen Z."""
    return {
        "sections": {
            "section_01": {
                "section_id": "ch01_sec01",
                "type": "HOOK",
                "metadata": {"persona": "Gen Z", "topic": "burnout", "section_type": "HOOK"},
                "variants": [
                    {
                        "variant_id": "ch01_sec01_hook_f2",
                        "variant_family": "F2",
                        "content": _GEN_Z_REAL_HOOK,
                    },
                    {
                        "variant_id": "ch01_sec01_hook_f3",
                        "variant_family": "F3",
                        "content": _PLACEHOLDER_STUB,
                    },
                ],
            }
        }
    }


# ---------------------------------------------------------------------------
# 1. Persona-match helper: the normalization + alias rules from the spec.
# ---------------------------------------------------------------------------


def test_persona_match_genz_label_resolves_to_gen_z_professionals():
    # The exact spec mandate: 'Gen Z' -> 'gen_z_professionals'.
    assert es._registry_persona_matches("Gen Z", "gen_z_professionals") is True


def test_persona_match_genz_label_does_not_bleed_into_corporate_managers():
    # The core defect: a Gen Z variant must NOT match a corporate_managers book.
    assert es._registry_persona_matches("Gen Z", "corporate_managers") is False


def test_persona_match_genz_professionals_distinct_from_gen_z_student():
    # gen_z_professionals and gen_z_student share a 'gen_z' prefix but are
    # distinct personas; a 'Gen Z' (== professionals) section must not leak into
    # a gen_z_student book.
    assert es._registry_persona_matches("Gen Z", "gen_z_student") is False


def test_persona_match_absent_label_is_allowed():
    # Absence cannot be proven foreign — unlabeled sections are retained.
    assert es._registry_persona_matches("", "corporate_managers") is True
    assert es._registry_persona_matches(None, "corporate_managers") is True


def test_persona_match_blank_spine_allows_anything():
    # No spine persona to compare against -> cannot filter.
    assert es._registry_persona_matches("Gen Z", "") is True


# ---------------------------------------------------------------------------
# 2. _registry_type_lists chokepoint — drops foreign-persona sections.
# ---------------------------------------------------------------------------


def test_type_lists_keeps_section_for_matching_persona():
    ch = _gen_z_chapter_dict()
    reg = es._registry_type_lists(ch, persona_id="gen_z_professionals")
    assert len(reg.get("HOOK", [])) == 1


def test_type_lists_drops_section_for_foreign_persona():
    # THE REGRESSION: a Gen Z section must vanish from a corporate_managers build.
    ch = _gen_z_chapter_dict()
    reg = es._registry_type_lists(ch, persona_id="corporate_managers")
    assert reg.get("HOOK", []) == []


def test_type_lists_no_persona_arg_is_backward_compatible():
    # Legacy callers (no persona_id) get every section, unchanged behavior.
    ch = _gen_z_chapter_dict()
    reg = es._registry_type_lists(ch)
    assert len(reg.get("HOOK", [])) == 1


# ---------------------------------------------------------------------------
# 3. _try_registry_variant / _peek_registry_variant — placeholder rejection,
#    and that a foreign-persona book gets NOTHING from the registry layer.
# ---------------------------------------------------------------------------


def test_try_registry_variant_rejects_placeholder_only_section():
    # A section that resolves to the placeholder stub returns None (fall-through).
    placeholder_only = {
        "sections": {
            "section_01": {
                "type": "HOOK",
                "metadata": {"persona": "Gen Z"},
                "variants": [
                    {"variant_id": "v1", "variant_family": "F1", "content": _PLACEHOLDER_STUB},
                ],
            }
        }
    }
    reg = es._registry_type_lists(placeholder_only, persona_id="gen_z_professionals")
    counters = {k: 0 for k in reg}
    hit = es._try_registry_variant(reg, "HOOK", counters, "seed:ch1:slot0")
    assert hit is None


def test_foreign_persona_gets_no_registry_hit_end_of_chokepoint():
    # Composed invariant: build the corp_mgr reg_lists from a gen_z chapter, then
    # try to pull a HOOK — the layer is empty, so selection returns None and the
    # caller falls through to persona_atom/teacher (no foreign text emitted).
    ch = _gen_z_chapter_dict()
    reg = es._registry_type_lists(ch, persona_id="corporate_managers")
    from collections import defaultdict

    counters: dict = defaultdict(int)
    hit = es._try_registry_variant(reg, "HOOK", counters, "seed:ch1:slot0")
    assert hit is None


# ---------------------------------------------------------------------------
# 4. End-to-end depth resolver (_load_depth_content "registry_variant") — reads
#    a real on-disk registry YAML; foreign persona must get None.
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_registry_root(tmp_path: Path) -> Path:
    """Write registry/burnout.yaml under a tmp repo_root, persona=Gen Z."""
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    registry = {
        "sections": {
            "chapter_01": {
                "chapter": 1,
                "sections": {
                    # A DEPTH section (so the depth-resolver section_types match)
                    # authored for Gen Z, with one long real variant.
                    "section_05": {
                        "section_id": "ch01_sec05",
                        "type": "REFLECTION",
                        "metadata": {"persona": "Gen Z", "topic": "burnout"},
                        "variants": [
                            {
                                "variant_id": "ch01_sec05_refl_f2",
                                "variant_family": "F2",
                                "content": _GEN_Z_REAL_HOOK + " " + _GEN_Z_REAL_HOOK,
                            },
                        ],
                    },
                },
            }
        }
    }
    (reg_dir / "burnout.yaml").write_text(
        yaml.safe_dump(registry, sort_keys=False), encoding="utf-8"
    )
    return tmp_path


def _depth_source() -> dict:
    return {
        "type": "registry_variant",
        "section_types": ["REFLECTION"],
        "variant_preference": ["F2", "F3", "F4"],
    }


def test_depth_resolver_returns_genz_content_for_genz_spine(tmp_registry_root: Path):
    # Positive control: the gen_z section IS reachable for a gen_z build.
    out = es._load_depth_content(
        _depth_source(),
        topic="burnout",
        teacher_id=None,
        persona_id="gen_z_professionals",
        chapter_number=1,
        seed="seed",
        repo_root=tmp_registry_root,
    )
    assert out is not None
    assert "open the next one" in out


def test_depth_resolver_blocks_genz_content_for_foreign_spine(tmp_registry_root: Path):
    # THE REGRESSION: a corporate_managers build must NOT receive the gen_z
    # registry content — the section is skipped, resolver returns None.
    out = es._load_depth_content(
        _depth_source(),
        topic="burnout",
        teacher_id=None,
        persona_id="corporate_managers",
        chapter_number=1,
        seed="seed",
        repo_root=tmp_registry_root,
    )
    assert out is None


def test_depth_resolver_rejects_placeholder_even_same_persona(tmp_path: Path):
    # Placeholder guard: a same-persona stub still must not render.
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    registry = {
        "sections": {
            "chapter_01": {
                "sections": {
                    "section_05": {
                        "type": "REFLECTION",
                        "metadata": {"persona": "Gen Z"},
                        "variants": [
                            {
                                "variant_id": "v_stub",
                                "variant_family": "F2",
                                # >20 words but a bracketed editorial stub.
                                "content": "[Persona-specific reflection placeholder for "
                                "gen_z_professionals burnout that is padded out to exceed "
                                "the twenty word minimum so only the stub guard can reject it]",
                            },
                        ],
                    }
                }
            }
        }
    }
    (reg_dir / "burnout.yaml").write_text(
        yaml.safe_dump(registry, sort_keys=False), encoding="utf-8"
    )
    out = es._load_depth_content(
        _depth_source(),
        topic="burnout",
        teacher_id=None,
        persona_id="gen_z_professionals",
        chapter_number=1,
        seed="seed",
        repo_root=tmp_path,
    )
    assert out is None


# ---------------------------------------------------------------------------
# 5. Placeholder regex direct check — matches the exact pilot bleed string.
# ---------------------------------------------------------------------------


def test_placeholder_regex_matches_pilot_bleed_string():
    assert es._REGISTRY_PLACEHOLDER_RE.match(_PLACEHOLDER_STUB)
    # The foreign-persona variant that bled into book 04/05 (× = multibyte).
    foreign = "[Persona-specific hook for gen_z_professionals × burnout]"
    assert es._REGISTRY_PLACEHOLDER_RE.match(foreign)


def test_placeholder_regex_does_not_match_real_prose():
    assert not es._REGISTRY_PLACEHOLDER_RE.match(_GEN_Z_REAL_HOOK)
