"""OPD-115 Phase B: composite doctrine selector vs teacher/persona pools."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning import registry_resolver as rr
from phoenix_v4.planning.beatmap_compile import Beatmap, BeatmapChapter, BeatmapSlot
from phoenix_v4.planning.enrichment_select import (
    EnrichmentRequest,
    _pick_teacher_pool,
    select_enrichment,
)
from phoenix_v4.planning.registry_resolver import (
    _load_composite_doctrine_atoms,
    _pick_composite_pool,
)


def _atom(atom_id: str, body: str) -> dict:
    return {"atom_id": atom_id, "content": body, "metadata": {}}


def _persona_compression_pool(*bodies: str) -> Dict[str, List[dict]]:
    return {
        "COMPRESSION": [
            _atom(f"p_comp_{i}", body) for i, body in enumerate(bodies)
        ],
    }


def _minimal_beatmap(slot_type: str = "COMPRESSION") -> Beatmap:
    slot = BeatmapSlot(
        slot_type=slot_type,
        weight=1.0,
        target_words=200,
        somatic_section_index=4,
        atom_selection_criteria={},
        enrichment_hooks=[],
        emotional_temperature="neutral",
        is_required=True,
    )
    chapter = BeatmapChapter(
        number=1,
        role="opening",
        working_title="Ch1",
        thesis="",
        phase="arrival",
        target_word_count=200,
        slots=[slot],
        slot_definitions=[slot_type],
    )
    return Beatmap(
        schema_version=1,
        stage="compile",
        topic="anxiety",
        family_id="test",
        runtime_format="standard_book",
        total_target_words=200,
        chapters=[chapter],
        compile_audit={},
    )


def _write_canonical(path: Path, body: str, header: str = "COMPOSITE v01") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"## {header}\n---\n---\n{body}\n---\n",
        encoding="utf-8",
    )


def test_teacher_mode_uses_teacher_banks_not_composite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    topic = "anxiety"
    _write_canonical(
        tmp_path / "SOURCE_OF_TRUTH" / "composite_doctrine" / topic / "CANONICAL.txt",
        "Composite doctrine must not win in teacher mode.",
    )
    teacher_atoms = {
        "TEACHER_DOCTRINE": [_atom("t_doctrine", "Teacher bank doctrine wins.")],
    }
    monkeypatch.setattr(es, "_load_teacher_atoms", lambda _tid: teacher_atoms)
    monkeypatch.setattr(es, "load_registry", lambda _t: {"sections": {}})
    monkeypatch.setattr(
        es,
        "_load_persona_atoms",
        lambda *_a, **_k: _persona_compression_pool(
            "Persona one.", "Persona two.", "Persona three.",
        ),
    )

    req = EnrichmentRequest(
        topic_id=topic,
        persona_id="gen_z_professionals",
        teacher_id="ahjan",
        beatmap=_minimal_beatmap("COMPRESSION"),
        seed="teacher_mode_seed",
        publishable_book=False,
    )
    book = select_enrichment(req, repo_root=tmp_path)
    slot = book.chapters[0].slots[0]
    assert "Teacher bank" in slot.content
    assert "Composite doctrine" not in slot.content
    assert "teacher_atom" in slot.source
    assert "composite_doctrine" not in slot.source


def test_non_teacher_mode_prefers_composite_doctrine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    topic = "anxiety"
    _write_canonical(
        tmp_path / "SOURCE_OF_TRUTH" / "composite_doctrine" / topic / "CANONICAL.txt",
        "Composite secular doctrine for anxiety.",
    )
    monkeypatch.setattr(es, "load_registry", lambda _t: {"sections": {}})
    monkeypatch.setattr(
        es,
        "_load_persona_atoms",
        lambda *_a, **_k: _persona_compression_pool(
            "Persona one.", "Persona two.", "Persona three.",
        ),
    )

    req = EnrichmentRequest(
        topic_id=topic,
        persona_id="gen_z_professionals",
        teacher_id=None,
        beatmap=_minimal_beatmap("COMPRESSION"),
        seed="composite_wins",
        publishable_book=False,
    )
    book = select_enrichment(req, repo_root=tmp_path)
    slot = book.chapters[0].slots[0]
    assert "Composite secular doctrine" in slot.content
    assert "Persona compression" not in slot.content
    assert "composite_doctrine" in slot.source
    assert "persona_atom" not in slot.source


def test_empty_composite_falls_back_to_persona_pool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    topic = "anxiety"
    empty = tmp_path / "SOURCE_OF_TRUTH" / "composite_doctrine" / topic / "CANONICAL.txt"
    empty.parent.mkdir(parents=True, exist_ok=True)
    empty.write_text("", encoding="utf-8")

    monkeypatch.setattr(es, "load_registry", lambda _t: {"sections": {}})
    monkeypatch.setattr(
        es,
        "_load_persona_atoms",
        lambda *_a, **_k: _persona_compression_pool(
            "Persona pool used when composite empty.",
            "Persona two.",
            "Persona three.",
        ),
    )

    req = EnrichmentRequest(
        topic_id=topic,
        persona_id="gen_z_professionals",
        teacher_id=None,
        beatmap=_minimal_beatmap("COMPRESSION"),
        seed="persona_fallback",
        publishable_book=False,
    )
    book = select_enrichment(req, repo_root=tmp_path)
    slot = book.chapters[0].slots[0]
    assert slot.content.startswith("Persona")
    assert "persona_atom" in slot.source
    assert "composite_doctrine" not in slot.source


def test_pick_composite_pool_maps_compression_to_doctrine() -> None:
    atoms = {
        "COMPOSITE_TEACHER_DOCTRINE": [_atom("c1", "body")],
    }
    pool = _pick_composite_pool(atoms, "COMPRESSION")
    assert len(pool) == 1
    assert pool[0]["atom_id"] == "c1"


def test_pick_teacher_pool_composite_teacher_doctrine_chain() -> None:
    teacher_atoms: Dict[str, List[dict]] = {
        "TEACHER_DOCTRINE": [_atom("d1", "doctrine")],
        "COMPRESSION": [_atom("c1", "compression")],
    }
    pool = _pick_teacher_pool(teacher_atoms, "COMPOSITE_TEACHER_DOCTRINE")
    assert pool[0]["atom_id"] == "d1"


def test_load_composite_reflection_subdir(tmp_path: Path) -> None:
    topic = "grief"
    _write_canonical(
        tmp_path / "SOURCE_OF_TRUTH" / "composite_doctrine" / topic / "REFLECTION" / "CANONICAL.txt",
        "Composite reflection prose.",
        header="REFLECTION v01",
    )
    loaded = _load_composite_doctrine_atoms(topic, repo_root=tmp_path)
    assert "COMPOSITE_TEACHER_REFLECTION" in loaded
    assert loaded["COMPOSITE_TEACHER_REFLECTION"][0]["content"].startswith("Composite reflection")
