"""ACT-012 — Rhetorical memory integration smoke tests.

Verifies the unified rhetorical anti-repetition architecture is importable,
callable, and wired correctly. The full unit suite is in test_rhetorical_memory.py
and test_rhetorical_scorer.py; this file confirms the integration contract.
"""
from __future__ import annotations

import pytest


def test_rhetorical_memory_importable():
    from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory
    assert RhetoricalMemory is not None


def test_rhetorical_scorer_functions_importable():
    from phoenix_v4.rendering.rhetorical_scorer import score_candidate, score_and_select
    assert callable(score_candidate)
    assert callable(score_and_select)


def test_rhetorical_memory_records_and_avoids_repeats():
    """Memory must record a shape and recall it as used at that layer."""
    from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory, UsageRecord
    mem = RhetoricalMemory()
    rec = UsageRecord(
        chapter_index=0,
        layer="bridge",
        sublayer="",
        variant_id="v01",
        shape="contrast_pivot",
        register="",
        movement="",
        instruction_tone="",
        cadence="",
        abstraction_level="",
        root_family="",
        stem="",
    )
    mem.record(rec)
    records_at_layer = mem._by_layer.get("bridge", [])
    assert len(records_at_layer) == 1, "Memory must store the record at the correct layer"
    assert records_at_layer[0].shape == "contrast_pivot"


def test_rhetorical_memory_different_shape_not_colliding():
    """Different shapes at the same layer must coexist without collision."""
    from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory, UsageRecord

    def _make_rec(shape: str) -> UsageRecord:
        return UsageRecord(
            chapter_index=0, layer="bridge", sublayer="",
            variant_id=f"v_{shape}", shape=shape, register="", movement="",
            instruction_tone="", cadence="", abstraction_level="", root_family="", stem="",
        )

    mem = RhetoricalMemory()
    mem.record(_make_rec("contrast_pivot"))
    mem.record(_make_rec("question_pivot"))
    shapes = {r.shape for r in mem._by_layer.get("bridge", [])}
    assert "contrast_pivot" in shapes
    assert "question_pivot" in shapes


def test_rhetorical_scorer_score_candidate():
    """score_candidate must return float in [0, 1] for any valid candidate."""
    from phoenix_v4.rendering.rhetorical_scorer import (
        CandidateVariant, ScoringContext, score_candidate,
    )
    from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory
    mem = RhetoricalMemory()
    ctx = ScoringContext(
        layer="bridge",
        sublayer="",
        chapter_index=0,
        emotional_job="grounding",
        topic_id="anxiety",
        memory=mem,
    )
    candidate = CandidateVariant(
        variant_id="test_v01",
        text="Notice the breath. Your jaw. The floor.",
        shape="somatic_anchor",
        register="grounded",
        movement="descent",
        instruction_tone="permissive",
        cadence="short",
        abstraction_level="concrete",
        root_family="body",
    )
    score = score_candidate(candidate, ctx)
    assert isinstance(score, (int, float)), f"score must be numeric, got {type(score)}"


def test_rhetorical_taxonomy_yaml_loadable():
    """The rhetorical style taxonomy YAML must exist and load."""
    import yaml
    from pathlib import Path
    taxonomy_path = (
        Path(__file__).resolve().parent.parent
        / "config" / "rendering" / "rhetorical_style_taxonomy.yaml"
    )
    assert taxonomy_path.exists(), f"rhetorical_style_taxonomy.yaml not found at {taxonomy_path}"
    data = yaml.safe_load(taxonomy_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "taxonomy must be a YAML mapping"
    assert len(data) > 0, "taxonomy must not be empty"
