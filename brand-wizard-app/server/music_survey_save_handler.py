"""
Music-mode musician survey → brand_wizard YAML persistence (MUSIC-MODE-BRAND-INTEGRATION-V1-01 §3).

Merges POST `survey_responses` into the `musician_reflections` mapping of
``brand-wizard-app/brands/<wizard_session_id>.yaml`` (create file if absent).
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class MusicSurveySaveError(ValueError):
    """Client-visible validation failure (maps to HTTP 422)."""


def validate_wizard_session_id(wizard_session_id: str) -> str:
    s = (wizard_session_id or "").strip()
    if not s:
        raise MusicSurveySaveError("wizard_session_id is required")
    if not _SESSION_ID_RE.fullmatch(s):
        raise MusicSurveySaveError(
            "wizard_session_id must be 1–128 chars: letters, digits, underscore, hyphen, dot; "
            "must start with alphanumeric"
        )
    if ".." in s or "/" in s or "\\" in s:
        raise MusicSurveySaveError("wizard_session_id contains forbidden path segments")
    return s


def validate_survey_responses(survey_responses: Any) -> dict[str, Any]:
    if survey_responses is None:
        raise MusicSurveySaveError("survey_responses is required")
    if not isinstance(survey_responses, Mapping):
        raise MusicSurveySaveError("survey_responses must be a JSON object")
    # Shallow copy to a plain dict for YAML serialization
    return dict(survey_responses)


def atomic_write_text(target: Path, content: str) -> None:
    """Write ``content`` to ``target`` using write-to-temp + os.replace (same-dir atomic)."""
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = target.parent
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(parent),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(str(tmp_path), str(target))
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        finally:
            raise


def _load_yaml_root(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for music survey save")  # pragma: no cover
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    data = yaml.safe_load(raw)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise MusicSurveySaveError("existing wizard YAML root must be a mapping")
    return data


def _dump_yaml(doc: dict[str, Any]) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML is required for music survey save")  # pragma: no cover
    return yaml.safe_dump(
        doc,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )


def merge_musician_reflections(
    existing: dict[str, Any],
    survey_responses: dict[str, Any],
) -> dict[str, Any]:
    cur = existing.get("musician_reflections")
    if cur is None:
        merged: dict[str, Any] = dict(survey_responses)
    elif isinstance(cur, dict):
        merged = {**cur, **survey_responses}
    else:
        raise MusicSurveySaveError("musician_reflections in YAML must be a mapping or absent")
    out = dict(existing)
    out["musician_reflections"] = merged
    return out


def save_survey_to_brand_yaml(
    *,
    brands_dir: Path,
    wizard_session_id: str,
    survey_responses: dict[str, Any],
) -> dict[str, Any]:
    """
    Load ``<wizard_session_id>.yaml`` under ``brands_dir``, merge survey into ``musician_reflections``,
    write atomically, return API body fields (status, next_step, yaml_path).
    """
    sid = validate_wizard_session_id(wizard_session_id)
    responses = validate_survey_responses(survey_responses)
    yaml_path = (brands_dir / f"{sid}.yaml").resolve()
    try:
        yaml_path.relative_to(brands_dir.resolve())
    except ValueError:
        raise MusicSurveySaveError("invalid brands path resolution") from None

    doc = _load_yaml_root(yaml_path)
    merged_doc = merge_musician_reflections(doc, responses)
    atomic_write_text(yaml_path, _dump_yaml(merged_doc))

    rel = f"brands/{sid}.yaml"
    return {
        "status": "saved",
        "next_step": "step5",
        "yaml_path": rel,
    }
