"""Resolve file $ref targets under schemas/manga."""

from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.models.validation import manga_schemas_dir, repo_root


def _collect_refs(obj, out: list[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                out.append(v)
            else:
                _collect_refs(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_refs(item, out)


def test_manga_schema_file_refs_resolve() -> None:
    root = manga_schemas_dir()
    for schema_path in sorted(root.glob("*.schema.json")):
        doc = json.loads(schema_path.read_text(encoding="utf-8"))
        refs: list[str] = []
        _collect_refs(doc, refs)
        for ref in refs:
            if ref.startswith("https://") or ref.startswith("http://"):
                continue
            file_part = ref.split("#", 1)[0]
            if not file_part:
                continue
            target = root / file_part
            assert target.is_file(), f"Missing ref target {file_part} from {schema_path.name}"


def test_paths_constants_use_expected_suffixes() -> None:
    import re

    text = (repo_root() / "phoenix_v4" / "manga" / "models" / "paths.py").read_text(
        encoding="utf-8"
    )
    _path_const_re = re.compile(r"^([A-Z][A-Z0-9_]*) = \"([^\"]+)\"$")
    for line in text.splitlines():
        m = _path_const_re.match(line.strip())
        if not m:
            continue
        val = m.group(2)
        assert ".." not in val
