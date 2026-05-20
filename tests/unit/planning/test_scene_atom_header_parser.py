"""OPD-114 Phase B: SCENE atom header metadata parser."""
from __future__ import annotations

from phoenix_v4.planning.registry_resolver import _parse_canonical_txt
from phoenix_v4.planning.scene_atom_header_parser import (
    attach_scene_metadata,
    parse_scene_atom_header,
    scene_atom_from_dict,
)


def test_parse_scene_header_with_archetype_and_depth() -> None:
    h = parse_scene_atom_header("## SCENE v02 [archetype: elevator_morning, depth_level: 3]")
    assert h.atom_id == "SCENE v02"
    assert h.archetype == "elevator_morning"
    assert h.depth_level == 3


def test_parse_scene_header_back_compat_defaults() -> None:
    h = parse_scene_atom_header("## SCENE v01")
    assert h.atom_id == "SCENE v01"
    assert h.archetype is None
    assert h.depth_level == 1


def test_attach_scene_metadata_on_atom_dict() -> None:
    atom = attach_scene_metadata(
        {"atom_id": "SCENE v05", "content": "Body text.", "metadata": {}},
        "## SCENE v05 [archetype: kitchen_fluorescent, depth_level: 2]",
    )
    assert atom["metadata"]["archetype"] == "kitchen_fluorescent"
    assert atom["metadata"]["depth_level"] == 2
    sa = scene_atom_from_dict(atom)
    assert sa.depth_level == 2
    assert sa.archetype == "kitchen_fluorescent"


def test_parse_canonical_txt_scene_blocks_get_metadata(tmp_path) -> None:
    path = tmp_path / "CANONICAL.txt"
    path.write_text(
        "## SCENE v01 [archetype: lobby_entry, depth_level: 1]\n"
        "---\n---\n"
        "First scene body.\n"
        "---\n"
        "## SCENE v02\n"
        "---\n---\n"
        "Second scene without metadata.\n"
        "---\n",
        encoding="utf-8",
    )
    blocks = _parse_canonical_txt(path, slot_type="SCENE")
    assert len(blocks) == 2
    assert blocks[0]["metadata"]["archetype"] == "lobby_entry"
    assert blocks[0]["metadata"]["depth_level"] == 1
    assert blocks[1]["metadata"]["archetype"] is None
    assert blocks[1]["metadata"]["depth_level"] == 1
