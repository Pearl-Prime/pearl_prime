"""Tests for phoenix_v4.planning.injection_resolver."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from phoenix_v4.planning import injection_resolver as ir
from phoenix_v4.planning.injection_resolver import clear_exercise_registry_cache, resolve_injections


@pytest.fixture(autouse=True)
def _clear_reg_cache():
    clear_exercise_registry_cache()
    yield
    clear_exercise_registry_cache()


def test_story_injection_replaced():
    text = "Intro\n\n[STORY_INJECTION_POINT]\n\nOutro"
    out = resolve_injections(
        text,
        chapter_index=1,
        section_index=2,
        section_type="SCENE",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id="ahjan",
        exercise_phase=None,
        seed="test_story_injection_replaced:inject:1:2",
    )
    assert "[STORY_INJECTION_POINT]" not in out["text"]
    assert "STORY_INJECTION_POINT" in out["injections_resolved"]
    assert any("injection:teacher_story:" in s for s in out["sources_used"])
    assert len(out["text"].split()) > 20


def test_exercise_injection_replaced(monkeypatch):
    monkeypatch.setattr(
        "phoenix_v4.exercises.practice_library_loader.get_exercise_for_chapter",
        lambda **kw: None,
    )
    text = "Warm-up\n\n[EXERCISE_INJECTION_POINT]\n\nClose"
    out = resolve_injections(
        text,
        chapter_index=3,
        section_index=4,
        section_type="EXERCISE",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id="ahjan",
        exercise_phase=None,
        seed="test_exercise_injection:inject:3:4",
    )
    assert "[EXERCISE_INJECTION_POINT]" not in out["text"]
    assert "EXERCISE_INJECTION_POINT" in out["injections_resolved"]
    assert any("injection:teacher_exercise:" in s for s in out["sources_used"])


def test_no_injection_no_change():
    body = "Plain scaffold " + " ".join(f"w{i}" for i in range(15))
    out = resolve_injections(
        body,
        chapter_index=1,
        section_index=1,
        section_type="HOOK",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id=None,
        exercise_phase=None,
        seed="no_inj",
    )
    assert out["text"] == body
    assert out["injections_resolved"] == []
    assert out["injections_failed"] == []
    assert out["sources_used"] == []


def test_missing_story_atom_strips(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ir, "REPO_ROOT", tmp_path)
    text = "[STORY_INJECTION_POINT]"
    out = resolve_injections(
        text,
        chapter_index=1,
        section_index=1,
        section_type="SCENE",
        topic="nope_topic",
        persona_id="nope_persona",
        teacher_id="nope_teacher",
        exercise_phase=None,
        seed="missing_story",
        repo_root=tmp_path,
    )
    assert out["text"].strip() == ""
    assert "STORY_INJECTION_POINT" in out["injections_failed"]


def test_missing_exercise_strips(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(ir, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        "phoenix_v4.exercises.practice_library_loader.get_exercise_for_chapter",
        lambda **kw: None,
    )
    text = "[EXERCISE_INJECTION_POINT]"
    out = resolve_injections(
        text,
        chapter_index=1,
        section_index=1,
        section_type="EXERCISE",
        topic="void",
        persona_id="void",
        teacher_id="void",
        exercise_phase=None,
        seed="missing_ex",
        repo_root=tmp_path,
    )
    assert "[EXERCISE_INJECTION_POINT]" not in out["text"]
    assert "EXERCISE_INJECTION_POINT" in out["injections_failed"]


def test_teacher_priority_over_persona(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ir, "REPO_ROOT", tmp_path)
    root = tmp_path
    teacher_dir = root / "SOURCE_OF_TRUTH" / "teacher_banks" / "t1" / "approved_atoms" / "STORY"
    teacher_dir.mkdir(parents=True)
    long_teacher = " ".join(["TEACHER_MARKER_AAA"] + [f"t{i}" for i in range(25)])
    (teacher_dir / "a.yaml").write_text(yaml.safe_dump({"body": long_teacher}), encoding="utf-8")
    pdir = root / "atoms" / "p1" / "topic_x" / "STORY"
    pdir.mkdir(parents=True)
    long_persona = " ".join(["PERSONA_MARKER_BBB"] + [f"p{i}" for i in range(25)])
    (pdir / "CANONICAL.txt").write_text(long_persona, encoding="utf-8")

    out = resolve_injections(
        "[STORY_INJECTION_POINT]",
        chapter_index=1,
        section_index=1,
        section_type="SCENE",
        topic="topic_x",
        persona_id="p1",
        teacher_id="t1",
        exercise_phase=None,
        seed="teacher_priority",
        repo_root=root,
    )
    assert "TEACHER_MARKER_AAA" in out["text"]
    assert "PERSONA_MARKER_BBB" not in out["text"]


def test_exercise_journey_priority_over_teacher(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(ir, "REPO_ROOT", tmp_path)
    root = tmp_path
    cfg = root / "config" / "exercises"
    cfg.mkdir(parents=True)
    (cfg / "exercise_metadata_registry.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "exercises": {
                    "body_scan_v1": {"type": "somatic_scan"},
                },
            }
        ),
        encoding="utf-8",
    )
    approved = root / "SOURCE_OF_TRUTH" / "exercises_v4" / "approved"
    approved.mkdir(parents=True)
    journey_body = " ".join(["JOURNEY_MARKER_ZZZ"] + [f"j{i}" for i in range(20)])
    (approved / "02_body_awareness_scan.yaml").write_text(
        yaml.safe_dump({"content": {"intro": journey_body}}),
        encoding="utf-8",
    )
    tex = root / "SOURCE_OF_TRUTH" / "teacher_banks" / "t1" / "approved_atoms" / "EXERCISE"
    tex.mkdir(parents=True)
    teach_ex = " ".join(["TEACHER_EX_MARKER"] + [f"e{i}" for i in range(20)])
    (tex / "x.yaml").write_text(yaml.safe_dump({"body": teach_ex}), encoding="utf-8")

    clear_exercise_registry_cache()
    out = resolve_injections(
        "[EXERCISE_INJECTION_POINT]",
        chapter_index=1,
        section_index=4,
        section_type="EXERCISE",
        topic="anxiety",
        persona_id="p",
        teacher_id="t1",
        exercise_phase={"phase": "awareness", "exercise_id": "body_scan_v1"},
        seed="journey_priority",
        repo_root=root,
    )
    assert "JOURNEY_MARKER_ZZZ" in out["text"]
    assert "TEACHER_EX_MARKER" not in out["text"]
    assert any("exercise_journey" in s for s in out["sources_used"])


def test_different_chapters_different_content():
    t1 = resolve_injections(
        "[STORY_INJECTION_POINT]",
        chapter_index=1,
        section_index=1,
        section_type="SCENE",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id="ahjan",
        exercise_phase=None,
        seed="diff_chapters",
    )
    t2 = resolve_injections(
        "[STORY_INJECTION_POINT]",
        chapter_index=2,
        section_index=1,
        section_type="SCENE",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id="ahjan",
        exercise_phase=None,
        seed="diff_chapters",
    )
    assert t1["text"] != t2["text"]


def test_resolved_audit_fields():
    out = resolve_injections(
        "[STORY_INJECTION_POINT] pad " + " ".join(f"x{i}" for i in range(30)),
        chapter_index=1,
        section_index=1,
        section_type="SCENE",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id="ahjan",
        exercise_phase=None,
        seed="audit_fields",
    )
    assert isinstance(out["injections_resolved"], list)
    assert isinstance(out["injections_failed"], list)
    assert isinstance(out["sources_used"], list)
    assert "STORY_INJECTION_POINT" in out["injections_resolved"]


def test_compose_wires_injection_and_warns_on_failure(monkeypatch, tmp_path: Path):
    from phoenix_v4.rendering.section_packet_composer import compose_section_packet

    monkeypatch.setattr(ir, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        "phoenix_v4.exercises.practice_library_loader.get_exercise_for_chapter",
        lambda **kw: None,
    )
    pad = " ".join(f"leg{i}" for i in range(12))
    legacy = {"text": pad + "\n\n[EXERCISE_INJECTION_POINT]\n\n" + pad}
    out = compose_section_packet(
        chapter_index=1,
        section_index=4,
        section_type="EXERCISE",
        target_words=400,
        spine_context={
            "topic": "void",
            "persona_id": "void",
            "teacher_id": "void",
            "packet_seed": "compose_test",
        },
        beatmap_slot={},
        enrichment_slot={"content": " ".join(f"e{i}" for i in range(12)), "source": "registry"},
        legacy_template_section=legacy,
        exercise_phase="awareness",
    )
    assert "[EXERCISE_INJECTION_POINT]" not in out["text"]
    assert any("injection failed" in w for w in out["warnings"])


def test_no_raw_injection_markers_after_resolve():
    out = resolve_injections(
        "[STORY_INJECTION_POINT]",
        chapter_index=99,
        section_index=99,
        section_type="SCENE",
        topic="nonexistent_topic_xyz",
        persona_id="nonexistent_persona_xyz",
        teacher_id=None,
        exercise_phase=None,
        seed="strip_marks",
    )
    assert "[STORY_INJECTION_POINT]" not in out["text"]
    assert "[EXERCISE_INJECTION_POINT]" not in out["text"]


def test_story_resolves_from_registry_when_no_atoms(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ir, "REPO_ROOT", tmp_path)
    root = tmp_path
    reg = root / "registry"
    reg.mkdir(parents=True)
    long_reg = " ".join(["REGISTRY_STORY_MARK"] + [f"r{i}" for i in range(25)])
    (reg / "t1.yaml").write_text(
        yaml.safe_dump(
            {
                "sections": {
                    "chapter_01": {
                        "sections": {
                            "section_02": {
                                "type": "SCENE",
                                "variants": [{"variant_id": "v1", "content": long_reg}],
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    out = resolve_injections(
        "[STORY_INJECTION_POINT]",
        chapter_index=1,
        section_index=2,
        section_type="SCENE",
        topic="t1",
        persona_id="",
        teacher_id=None,
        exercise_phase=None,
        seed="registry_story",
        repo_root=root,
    )
    assert "REGISTRY_STORY_MARK" in out["text"]
    assert any("injection:registry:" in s for s in out["sources_used"])
    assert "INJECTION_POINT" not in out["text"]


def test_compose_final_text_has_no_injection_point_literal():
    from phoenix_v4.rendering.section_packet_composer import compose_section_packet

    pad = " ".join(f"w{i}" for i in range(12))
    legacy = {"text": f"{pad}\n\n[STORY_INJECTION_POINT]\n\n{pad}"}
    out = compose_section_packet(
        chapter_index=1,
        section_index=2,
        section_type="SCENE",
        target_words=400,
        spine_context={
            "topic": "anxiety",
            "persona_id": "gen_z_professionals",
            "teacher_id": "ahjan",
            "packet_seed": "no_literal_test",
        },
        beatmap_slot={},
        enrichment_slot=None,
        legacy_template_section=legacy,
    )
    assert "INJECTION_POINT" not in out["text"]
