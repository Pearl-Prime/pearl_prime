from __future__ import annotations

import json
from pathlib import Path

from scripts.ci.check_variation_manifest import check_manifest
from scripts.inventory.surface_inventory import build_surface_inventory, parse_canonical_variants
from scripts.qa.variation_manifest import build_variation_manifest


def _write_atom(root: Path, surface: str, text: str) -> Path:
    path = root / "atoms" / "nurses" / "anxiety" / surface / "CANONICAL.txt"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_canonical_variants_counts_real_bodies(tmp_path):
    path = _write_atom(
        tmp_path,
        "STORY",
        """## STORY v01
---
MECHANISM_DEPTH: 2
---
Mara woke on Tuesday and realized the old alarm was still running after the meeting.
---

## STORY v02
---
MECHANISM_DEPTH: 2
---
Jon stood in the room, but the cost stayed with him after the door closed.
---
""",
    )

    variants = parse_canonical_variants(path, fallback_surface="STORY")

    assert len(variants) == 2
    assert variants[0].surface_key == "STORY"
    assert variants[0].word_count > 8


def test_surface_inventory_and_variation_checker_are_warn_only(tmp_path):
    _write_atom(
        tmp_path,
        "STORY",
        """## STORY v01
---
MECHANISM_DEPTH: 2
---
Mara woke on Tuesday, but the cost stayed with her after she left the room.
---
""",
    )

    manifest = build_surface_inventory(repo_root=tmp_path)
    variation = build_variation_manifest(manifest)
    code, warnings = check_manifest(variation, strict=False)
    strict_code, strict_warnings = check_manifest(variation, strict=True)

    assert manifest["stats"]["cells"] == 1
    assert variation["rows"][0]["status"] == "WARN"
    assert code == 0
    assert warnings
    assert strict_code == 1
    assert strict_warnings
