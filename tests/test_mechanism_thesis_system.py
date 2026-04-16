from __future__ import annotations

from pathlib import Path

from phoenix_v4.rendering import chapter_composer as cc


def _jobs() -> list[str]:
    return ["recognition", "mechanism", "deepening", "reframe", "practice", "integration", "resolution"]


def test_thesis_varies_by_emotional_job() -> None:
    reflection = "The alarm keeps firing in ordinary meetings."
    outputs = {
        job: cc._derive_thesis(reflection, emotional_job=job, chapter_index=0, thesis_memory=cc.MechanismThesisMemory())
        for job in _jobs()
    }
    assert len(set(outputs.values())) >= 4


def test_thesis_not_stuck_on_point_is_that() -> None:
    reflection = "The nervous system predicts danger before facts."
    outputs = [cc._derive_thesis(reflection, emotional_job=job) for job in _jobs()]
    non_point = [x for x in outputs if not x.lower().startswith("the point is that")]
    assert len(non_point) >= 4


def test_mechanism_varies_by_emotional_job() -> None:
    reflection = "The alarm keeps firing in ordinary meetings."
    thesis = "The alarm fires on prediction, not evidence."
    outputs = {
        job: cc._distill_mechanism(reflection, thesis, emotional_job=job, mechanism_memory=cc.MechanismThesisMemory())
        for job in _jobs()
    }
    assert len(set(outputs.values())) >= 4


def test_exact_thesis_not_reused_in_book() -> None:
    memory = cc.MechanismThesisMemory()
    seen: set[str] = set()
    for idx in range(12):
        job = _jobs()[idx % len(_jobs())]
        phrase = cc._derive_thesis("alarm prediction body evidence", chapter_index=idx, emotional_job=job, thesis_memory=memory)
        assert phrase not in seen
        seen.add(phrase)


def test_exact_mechanism_not_reused_in_book() -> None:
    memory = cc.MechanismThesisMemory()
    seen: set[str] = set()
    for idx in range(12):
        cc._CHAPTER_INDEX_TLS = idx
        job = _jobs()[idx % len(_jobs())]
        phrase = cc._distill_mechanism("alarm prediction body evidence", "The alarm fires on prediction, not evidence.", emotional_job=job, mechanism_memory=memory)
        assert phrase not in seen
        seen.add(phrase)


def test_point_is_that_stem_capped() -> None:
    memory = cc.MechanismThesisMemory()
    out = [
        cc._derive_thesis("alarm prediction body evidence", chapter_index=i, emotional_job=_jobs()[i % 7], thesis_memory=memory)
        for i in range(12)
    ]
    assert sum(1 for x in out if x.lower().startswith("the point is that")) <= 2


def test_banned_mechanism_wrapper_stems_capped() -> None:
    memory = cc.MechanismThesisMemory()
    outputs = []
    for i in range(12):
        cc._CHAPTER_INDEX_TLS = i
        outputs.append(
            cc._distill_mechanism(
                "alarm prediction body evidence",
                "The alarm fires on prediction, not evidence.",
                emotional_job=_jobs()[i % 7],
                mechanism_memory=memory,
            ).lower()
        )
    for stem in ("here is the mechanism", "the pattern underneath", "what drives this"):
        assert sum(1 for x in outputs if stem in x) <= 1


def test_shape_not_overused_in_adjacent_window() -> None:
    memory = cc.MechanismThesisMemory()
    for i in range(12):
        cc._CHAPTER_INDEX_TLS = i
        cc._distill_mechanism(
            "alarm prediction body evidence",
            "The alarm fires on prediction, not evidence.",
            emotional_job="mechanism",
            mechanism_memory=memory,
        )
    for idx in range(2, 12):
        counts = memory.shape_usage_by_chapter.get(idx, {})
        for shape in counts:
            total = sum(memory.shape_usage_by_chapter.get(k, {}).get(shape, 0) for k in range(max(0, idx - 2), idx + 1))
            assert total <= 2


def test_topic_specific_legacy_mechanisms_still_fire() -> None:
    text = cc._distill_mechanism("regret and choice are locked together", "The point is that anxiety predicts regret.")
    assert "anxiety predicts regret" in text.lower()


def test_yaml_missing_falls_back_gracefully(monkeypatch) -> None:
    monkeypatch.setattr(cc, "_MECHANISM_THESIS_CACHE", None)
    monkeypatch.setattr(cc, "_MECHANISM_THESIS_PATH", Path("/tmp/does_not_exist_mechanism.yaml"))
    thesis = cc._derive_thesis("alarm prediction body evidence", emotional_job="recognition", chapter_index=0)
    mech = cc._distill_mechanism("alarm prediction body evidence", thesis, emotional_job="recognition")
    assert thesis
    assert mech


def test_backward_compat_with_empty_emotional_job() -> None:
    thesis = cc._derive_thesis("false alarm and body", emotional_job="")
    mech = cc._distill_mechanism("false alarm and body", thesis, emotional_job="")
    takeaway = cc._fallback_takeaway(thesis, emotional_job="")
    assert thesis and mech and takeaway


def test_fallback_takeaway_varies() -> None:
    memory = cc.MechanismThesisMemory()
    outputs = [
        cc._fallback_takeaway(
            "The alarm fires on prediction, not evidence.",
            emotional_job=job,
            chapter_index=i,
            total_chapters=12,
            mechanism_memory=memory,
        )
        for i, job in enumerate(_jobs())
    ]
    assert len(set(outputs)) >= 4
    assert any(not x.lower().startswith("remember this:") for x in outputs)
