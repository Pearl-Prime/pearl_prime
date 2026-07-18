from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.canonical_atom_blocks import (
    DuplicateAtomIdError,
    parse_canonical_blocks,
)
from phoenix_v4.planning.assembly_compiler import (
    _parse_canonical_txt as parse_assembly_canonical_txt,
)


def test_integration_is_first_class_and_real_body_is_not_empty(tmp_path: Path):
    path = tmp_path / "atoms/p/t/INTEGRATION/CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        """## INTEGRATION v26
---
stage: pearl_writer_stage_3
mode: BODY_LANDED
carry_line: "One small change."
---
The manager closes one meeting by asking how the person actually is.

The real integration continues beyond the metadata and must not resolve empty.
---
""",
        encoding="utf-8",
    )
    blocks = parse_canonical_blocks(
        path,
        persona="corporate_managers",
        topic="burnout",
        slot_type="INTEGRATION",
    )
    assert len(blocks) == 1
    assert blocks[0].atom_id == "corporate_managers_burnout_INTEGRATION_v26"
    assert blocks[0].word_count > 10
    assert "must not resolve empty" in blocks[0].prose


def test_placeholder_integration_is_excluded(tmp_path: Path):
    path = tmp_path / "atoms/p/t/INTEGRATION/CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        """## INTEGRATION v01
---
mode: STILL-HERE
[Integration content for corporate_managers × burnout]
---
## INTEGRATION v02
---
mode: BODY_LANDED
---
Your shoulders have been giving you the report that the dashboard cannot.
---
""",
        encoding="utf-8",
    )
    blocks = parse_canonical_blocks(
        path, persona="p", topic="t", slot_type="INTEGRATION"
    )
    assert [block.version for block in blocks] == ["02"]


def test_duplicate_integration_ids_fail_loudly(tmp_path: Path):
    path = tmp_path / "atoms/p/t/INTEGRATION/CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        """## INTEGRATION v18
---
mode: BODY_LANDED
---
First real body.
---
## INTEGRATION v18
---
mode: QUESTION_OPEN
---
Second real body that must not overwrite the first.
---
""",
        encoding="utf-8",
    )
    with pytest.raises(DuplicateAtomIdError, match="Duplicate atom ID"):
        parse_canonical_blocks(
            path,
            persona="p",
            topic="t",
            slot_type="INTEGRATION",
            require_unique_ids=True,
        )


def test_duplicate_ids_are_legacy_compatible_unless_strict(tmp_path: Path):
    path = tmp_path / "atoms/p/t/INTEGRATION/CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        """## INTEGRATION v18
---
mode: BODY_LANDED
---
First real body.
---
## INTEGRATION v18
---
mode: QUESTION_OPEN
---
Second real body that remains visible to legacy runtime readers.
---
""",
        encoding="utf-8",
    )
    blocks = parse_canonical_blocks(
        path, persona="p", topic="t", slot_type="INTEGRATION"
    )
    assert [block.version for block in blocks] == ["18", "18"]
    assert "Second real body" in blocks[1].prose


def test_assembly_parser_duplicate_ids_are_legacy_compatible_unless_strict(tmp_path: Path):
    path = tmp_path / "atoms/p/t/INTEGRATION/CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        """## INTEGRATION v18
---
mode: BODY_LANDED
---
First real body.
---
## INTEGRATION v18
---
mode: QUESTION_OPEN
---
Second real body that keeps the legacy bank parseable.
---
""",
        encoding="utf-8",
    )
    atoms = parse_assembly_canonical_txt(path)
    assert [atom["atom_id"] for atom in atoms] == [
        "p_t_INTEGRATION_INTEGRATION_v18",
        "p_t_INTEGRATION_INTEGRATION_v18",
    ]
    with pytest.raises(ValueError, match="duplicate atom ID"):
        parse_assembly_canonical_txt(path, require_unique_ids=True)


def test_legacy_single_delimiter_metadata_plus_prose_parses(tmp_path: Path):
    path = tmp_path / "atoms/p/t/INTEGRATION/CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        """## INTEGRATION v03
---
mode: BODY_LANDED
The body reports the accumulated cost before the spreadsheet does.
---
""",
        encoding="utf-8",
    )
    blocks = parse_canonical_blocks(
        path, persona="p", topic="t", slot_type="INTEGRATION"
    )
    assert blocks[0].metadata["mode"] == "BODY_LANDED"
    assert blocks[0].prose.startswith("The body reports")
