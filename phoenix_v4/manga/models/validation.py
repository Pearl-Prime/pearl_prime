"""Load and validate manga JSON artifacts (jsonschema Draft 2020-12)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_REPO_ROOT: Path | None = None


def repo_root() -> Path:
    global _REPO_ROOT
    if _REPO_ROOT is None:
        here = Path(__file__).resolve()
        _REPO_ROOT = here.parents[3]
    return _REPO_ROOT


def manga_schemas_dir() -> Path:
    return repo_root() / "schemas" / "manga"


def _schema_store() -> dict[str, dict[str, Any]]:
    root = manga_schemas_dir()
    return {
        p.name: json.loads(p.read_text(encoding="utf-8"))
        for p in root.glob("*.schema.json")
    }


def load_schema(schema_stem: str) -> dict[str, Any]:
    path = manga_schemas_dir() / f"{schema_stem}.schema.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def validator_for(schema_stem: str):
    import jsonschema

    root = manga_schemas_dir().resolve()
    schema = load_schema(schema_stem)
    store = _schema_store()
    resolver = jsonschema.RefResolver(
        base_uri=root.as_uri() + "/",
        referrer=schema,
        store=store,
    )
    return jsonschema.Draft202012Validator(schema, resolver=resolver)


def validate_instance(data: dict[str, Any], schema_stem: str) -> None:
    v = validator_for(schema_stem)
    v.validate(data)


def load_and_validate(path: Path, schema_stem: str) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise TypeError(f"Expected object at root in {path}")
    validate_instance(data, schema_stem)
    return data


def iter_instance_schema_stems() -> list[str]:
    stems = []
    for p in sorted(manga_schemas_dir().glob("*.schema.json")):
        name = p.name[: -len(".schema.json")]
        if name == "manga_common":
            continue
        stems.append(name)
    return stems
