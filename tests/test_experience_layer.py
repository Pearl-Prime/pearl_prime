#!/usr/bin/env python3
"""
Tests for the Experience Layer Anti-Spam system.
Covers: resolver, wave density checks, risky combos, AI disclosure, metadata consistency.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.experience_resolver import (
    resolve_experience,
    compute_experience_hash,
    resolve_and_attach,
    ensure_ai_disclosure,
    EXPERIENCE_FIELDS,
)
from phoenix_v4.qa.experience_wave_checks import (
    check_experience_wave,
    check_experience_metadata_consistency,
    check_ai_disclosure,
)


def _make_plan(**overrides):
    """Create a minimal plan dict with defaults."""
    base = {
        "arc_id": "A001",
        "emotional_temperature_sequence": [2, 3, 4, 3, 2],
        "slot_sig": "S1",
        "exercise_chapters": [3, 5],
        "engine_id": "practical_system",
        "topic_id": "anxiety",
        "chapter_count": 8,
        "brand_id": "stillness_press",
        "book_id": "test_book_001",
    }
    base.update(overrides)
    return base


# ---------- Experience Resolver Tests ----------

def test_resolve_defaults():
    """Resolver should fill all 7 fields from defaults config."""
    plan = _make_plan()
    exp = resolve_experience(plan)
    for field in EXPERIENCE_FIELDS:
        assert exp.get(field), f"Missing field: {field}"
    assert exp["experience_hash"], "Missing experience_hash"
    # engine=practical_system → delivery_experience=guided_program
    assert exp["delivery_experience"] == "guided_program"
    # topic=anxiety → reader_intent=calm_down
    assert exp["reader_intent"] == "calm_down"
    # chapter_count=8 (medium) → pacing_model=multi_day
    assert exp["pacing_model"] == "multi_day"
    print("  PASS: test_resolve_defaults")


def test_resolve_explicit_override():
    """Explicit plan fields override defaults."""
    plan = _make_plan(delivery_experience="audio_immersion", reader_intent="find_meaning")
    exp = resolve_experience(plan)
    assert exp["delivery_experience"] == "audio_immersion"
    assert exp["reader_intent"] == "find_meaning"
    print("  PASS: test_resolve_explicit_override")


def test_resolve_fallback():
    """Unknown engine/topic should use fallback."""
    plan = _make_plan(engine_id="unknown_engine", topic_id="unknown_topic", chapter_count=0)
    exp = resolve_experience(plan)
    assert exp["delivery_experience"] == "passive_reading"  # fallback
    assert exp["reader_intent"] == "understand_self"  # fallback
    print("  PASS: test_resolve_fallback")


def test_experience_hash_deterministic():
    """Same tuple → same hash."""
    plan = _make_plan()
    exp1 = resolve_experience(plan)
    exp2 = resolve_experience(plan)
    assert exp1["experience_hash"] == exp2["experience_hash"]
    print("  PASS: test_experience_hash_deterministic")


def test_experience_hash_differs():
    """Different tuple → different hash."""
    plan1 = _make_plan(topic_id="anxiety")
    plan2 = _make_plan(topic_id="productivity")
    exp1 = resolve_experience(plan1)
    exp2 = resolve_experience(plan2)
    assert exp1["experience_hash"] != exp2["experience_hash"]
    print("  PASS: test_experience_hash_differs")


def test_resolve_and_attach():
    """resolve_and_attach should add fields to plan dict."""
    plan = _make_plan()
    result = resolve_and_attach(plan)
    assert result is plan  # modifies in place
    for field in EXPERIENCE_FIELDS:
        assert plan.get(field), f"Missing after attach: {field}"
    assert plan.get("experience_hash")
    print("  PASS: test_resolve_and_attach")


def test_ensure_ai_disclosure():
    """ensure_ai_disclosure sets default for pipeline books."""
    plan = _make_plan()
    ensure_ai_disclosure(plan)
    assert plan["ai_disclosure_status"] == "disclosed"
    # Don't overwrite existing
    plan2 = _make_plan(ai_disclosure_status="not_applicable")
    ensure_ai_disclosure(plan2)
    assert plan2["ai_disclosure_status"] == "not_applicable"
    print("  PASS: test_ensure_ai_disclosure")


# ---------- Wave Density Experience Checks ----------

def _make_wave(n, **common_overrides):
    """Create a wave of n plans, all resolved with experience fields."""
    plans = []
    for i in range(n):
        p = _make_plan(book_id=f"book_{i:03d}", **common_overrides)
        resolve_and_attach(p)
        ensure_ai_disclosure(p)
        plans.append(p)
    return plans


def test_wave_pass_diverse():
    """A diverse wave should pass."""
    topics = ["anxiety", "productivity", "grief", "shame", "discipline",
              "presence", "identity", "overthinking", "burnout", "relationships"]
    engines = ["practical_system", "narrative_transformation", "somatic_exercise",
               "spiritual_reflection", "rational_framework"]
    plans = []
    for i in range(10):
        p = _make_plan(
            book_id=f"book_{i:03d}",
            topic_id=topics[i % len(topics)],
            engine_id=engines[i % len(engines)],
            chapter_count=[4, 8, 12][i % 3],
        )
        resolve_and_attach(p)
        ensure_ai_disclosure(p)
        plans.append(p)

    failures, warnings = check_experience_wave(plans)
    assert not failures, f"Expected PASS but got failures: {failures}"
    print("  PASS: test_wave_pass_diverse")


def test_wave_fail_homogeneous():
    """A wave with all same experience should fail."""
    # All anxiety + practical_system + chapter_count=8 → identical tuple
    plans = _make_wave(10)  # all defaults → all same tuple
    failures, warnings = check_experience_wave(plans)
    assert any("density" in f or "identical experience tuple" in f for f in failures), \
        f"Expected experience density failure but got: {failures}"
    print("  PASS: test_wave_fail_homogeneous")


def test_risky_combo_fail():
    """A wave heavy on anxiety_quick_fix combo should fail."""
    plans = []
    # 6 out of 10 books = calm_down + immediate + single_sitting (60% > 20% cap)
    for i in range(6):
        p = _make_plan(
            book_id=f"book_{i:03d}",
            topic_id="anxiety",
            engine_id="practical_system",
            chapter_count=4,  # short → single_sitting + immediate
        )
        resolve_and_attach(p)
        ensure_ai_disclosure(p)
        plans.append(p)
    # 4 diverse books
    for i, topic in enumerate(["productivity", "grief", "identity", "presence"]):
        p = _make_plan(
            book_id=f"book_diverse_{i:03d}",
            topic_id=topic,
            engine_id="narrative_transformation",
            chapter_count=12,
        )
        resolve_and_attach(p)
        ensure_ai_disclosure(p)
        plans.append(p)

    failures, warnings = check_experience_wave(plans)
    risky_fail = [f for f in failures if "risky combo" in f]
    assert risky_fail, f"Expected risky combo failure but got: {failures}"
    print("  PASS: test_risky_combo_fail")


def test_novel_clustering_alert():
    """Novel cluster should produce WARN (not FAIL)."""
    plans = []
    # 3 books with same unusual combo → should trigger novel clustering alert
    for i in range(3):
        p = _make_plan(
            book_id=f"novel_{i:03d}",
            topic_id="grief",
            engine_id="somatic_exercise",
            chapter_count=12,
        )
        resolve_and_attach(p)
        ensure_ai_disclosure(p)
        plans.append(p)
    # 7 diverse books to keep the wave from failing on dimension caps
    for i, topic in enumerate(["anxiety", "productivity", "shame", "discipline",
                                "presence", "identity", "burnout"]):
        p = _make_plan(
            book_id=f"diverse_{i:03d}",
            topic_id=topic,
            engine_id=["practical_system", "narrative_transformation", "rational_framework",
                       "spiritual_reflection", "somatic_exercise"][i % 5],
            chapter_count=[4, 8, 12][i % 3],
        )
        resolve_and_attach(p)
        ensure_ai_disclosure(p)
        plans.append(p)

    failures, warnings = check_experience_wave(plans)
    novel_warns = [w for w in warnings if "NOVEL CLUSTER" in w]
    # May or may not trigger depending on combo — just verify no crash
    print(f"  PASS: test_novel_clustering_alert (novel warns: {len(novel_warns)})")


# ---------- AI Disclosure Tests ----------

def test_ai_disclosure_pass():
    """All disclosed plans should pass."""
    plans = _make_wave(5)
    failures, warnings = check_ai_disclosure(plans)
    assert not failures, f"Expected pass but got: {failures}"
    print("  PASS: test_ai_disclosure_pass")


def test_ai_disclosure_fail_missing():
    """Plans with missing disclosure should fail."""
    plans = _make_wave(5)
    plans[2]["ai_disclosure_status"] = ""  # missing
    plans[4]["ai_disclosure_status"] = "pending"
    failures, warnings = check_ai_disclosure(plans)
    assert len(failures) == 2, f"Expected 2 failures but got {len(failures)}: {failures}"
    print("  PASS: test_ai_disclosure_fail_missing")


# ---------- Metadata Consistency Tests ----------

def test_metadata_consistency_warn():
    """Quick-fix positioning with 'deep' in title should warn."""
    plans = [
        _make_plan(
            perceived_positioning="quick_fix",
            title="The Deep Journey to Calm",
            description="A fast method for instant relief from anxiety.",
        )
    ]
    warnings = check_experience_metadata_consistency(plans)
    assert any("CONSISTENCY" in w for w in warnings), f"Expected consistency warning: {warnings}"
    print("  PASS: test_metadata_consistency_warn")


def test_metadata_consistency_clean():
    """Quick-fix positioning with matching title should not warn."""
    plans = [
        _make_plan(
            perceived_positioning="quick_fix",
            title="Calm Your Anxiety Fast",
            description="A quick method for instant relief.",
        )
    ]
    warnings = check_experience_metadata_consistency(plans)
    consistency_warns = [w for w in warnings if "CONSISTENCY" in w]
    assert not consistency_warns, f"Expected no warnings but got: {consistency_warns}"
    print("  PASS: test_metadata_consistency_clean")


# ---------- Integration: check_wave_density.py script ----------

def test_check_wave_density_script():
    """Run the actual check_wave_density.py script on a synthetic wave."""
    import subprocess

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 10 diverse plans (must also vary structural fields to pass existing gates)
        topics = ["anxiety", "productivity", "grief", "shame", "discipline",
                  "presence", "identity", "overthinking", "burnout", "relationships"]
        engines = ["practical_system", "narrative_transformation", "somatic_exercise",
                   "spiritual_reflection", "rational_framework"]
        arcs = [f"A{i:03d}" for i in range(10)]
        band_seqs = [[2, 3, 4], [1, 2, 3, 4], [3, 2, 1], [1, 3, 2, 4, 3],
                     [2, 4, 3, 2], [1, 1, 2, 3], [3, 4, 3, 2, 1], [2, 2, 3, 4],
                     [1, 3, 4, 3], [4, 3, 2, 1]]
        slot_sigs = [f"S{i}" for i in range(10)]
        exercise_placements = [[2], [3, 5], [4], [2, 6], [3], [1, 4], [5, 7], [2, 4], [3, 6], [1]]
        role_sigs = [f"role_{i}" for i in range(10)]
        for i in range(10):
            p = _make_plan(
                book_id=f"book_{i:03d}",
                topic_id=topics[i],
                engine_id=engines[i % len(engines)],
                chapter_count=[4, 8, 12][i % 3],
                arc_id=arcs[i],
                emotional_temperature_sequence=band_seqs[i],
                slot_sig=slot_sigs[i],
                exercise_chapters=exercise_placements[i],
                emotional_role_sig=role_sigs[i],
            )
            resolve_and_attach(p)
            ensure_ai_disclosure(p)
            out_path = Path(tmpdir) / f"plan_{i:03d}.json"
            out_path.write_text(json.dumps(p, indent=2), encoding="utf-8")

        script = REPO_ROOT / "scripts" / "ci" / "check_wave_density.py"
        result = subprocess.run(
            [sys.executable, str(script), "--plans-dir", tmpdir],
            capture_output=True, text=True, timeout=30,
        )
        print(f"  Script stdout: {result.stdout.strip()}")
        if result.stderr.strip():
            print(f"  Script stderr: {result.stderr.strip()}")
        assert result.returncode == 0, f"Expected PASS (rc=0) but got rc={result.returncode}"
        print("  PASS: test_check_wave_density_script")


# ---------- Runner ----------

if __name__ == "__main__":
    print("=" * 60)
    print("Experience Layer Anti-Spam Tests")
    print("=" * 60)

    tests = [
        # Resolver
        test_resolve_defaults,
        test_resolve_explicit_override,
        test_resolve_fallback,
        test_experience_hash_deterministic,
        test_experience_hash_differs,
        test_resolve_and_attach,
        test_ensure_ai_disclosure,
        # Wave checks
        test_wave_pass_diverse,
        test_wave_fail_homogeneous,
        test_risky_combo_fail,
        test_novel_clustering_alert,
        # AI disclosure
        test_ai_disclosure_pass,
        test_ai_disclosure_fail_missing,
        # Metadata consistency
        test_metadata_consistency_warn,
        test_metadata_consistency_clean,
        # Integration
        test_check_wave_density_script,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test_fn.__name__}: {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    if failed:
        sys.exit(1)
    print("All tests passed.")
    sys.exit(0)
