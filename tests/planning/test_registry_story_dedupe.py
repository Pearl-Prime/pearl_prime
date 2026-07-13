from __future__ import annotations

from pathlib import Path

import pytest

import phoenix_v4.planning.registry_resolver as rr


def _registry(chapter_count: int) -> dict:
    sections = {}
    for index in range(chapter_count):
        sections[f"chapter_{index + 1:02d}"] = {
            "chapter": index + 1,
            "title": f"Chapter {index + 1}",
            "sections": {
                "section_01": {
                    "section_id": f"ch{index + 1:02d}_story",
                    "type": "STORY",
                    "purpose": "proof",
                    "variants": [{
                        "variant_id": f"registry_{index}",
                        "content": "Registry fallback should not be selected.",
                    }],
                }
            },
        }
    return {"topic": "burnout", "sections": sections}


def _write_story_bank(root: Path, atoms: list[tuple[str, str]]) -> None:
    path = root / "corporate_managers/burnout/STORY/CANONICAL.txt"
    path.parent.mkdir(parents=True)
    chunks = []
    for atom_id, body in atoms:
        chunks.append(
            f"## STORY {atom_id}\n---\nid: {atom_id}\n---\n{body}\n---\n"
        )
    path.write_text("\n".join(chunks), encoding="utf-8")


def test_story_ids_and_bodies_are_unique_book_wide(tmp_path, monkeypatch):
    _write_story_bank(
        tmp_path,
        [
            ("v01", "The first manager story has a distinct human cost."),
            ("v02", "The second manager story reveals a different consequence."),
        ],
    )
    monkeypatch.setattr(rr, "ATOMS_ROOT", tmp_path)
    book = rr.resolve_book(
        _registry(2),
        seed="dedupe-proof",
        persona_id="corporate_managers",
    )
    assert book.selection_audit["status"] == "PASS"
    assert len(set(book.selection_audit["selected_story_atom_ids"])) == 2
    assert not book.selection_audit["duplicate_story_atom_ids"]
    assert not book.selection_audit["duplicate_story_body_hashes"]


def test_story_pool_exhaustion_fails_instead_of_repeating(tmp_path, monkeypatch):
    _write_story_bank(
        tmp_path,
        [("v01", "One authored story cannot silently fill two chapters.")],
    )
    monkeypatch.setattr(rr, "ATOMS_ROOT", tmp_path)
    with pytest.raises(rr.DuplicateSelectedAtomError, match="pool exhausted"):
        rr.resolve_book(
            _registry(2),
            seed="dedupe-proof",
            persona_id="corporate_managers",
        )


def test_different_ids_with_same_body_are_not_both_selected(tmp_path, monkeypatch):
    body = "The exact same STORY body must not silently render twice."
    _write_story_bank(tmp_path, [("v01", body), ("v02", body)])
    monkeypatch.setattr(rr, "ATOMS_ROOT", tmp_path)
    with pytest.raises(rr.DuplicateSelectedAtomError, match="pool exhausted"):
        rr.resolve_book(
            _registry(2),
            seed="dedupe-proof",
            persona_id="corporate_managers",
        )
