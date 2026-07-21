"""
Music-mode musician survey → brand_wizard YAML persistence (MUSIC-MODE-BRAND-INTEGRATION-V1-01 §3).

Merges POST `survey_responses` into the `musician_reflections` mapping of
``brand-wizard-app/brands/<wizard_session_id>.yaml`` (create file if absent), then
mints/updates the corresponding row in ``config/music/music_brand_registry.yaml`` so the
brand actually exists end-to-end (wizard YAML + registry row), per spec §5 / Q2.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_SLUG_COLLAPSE_RE = re.compile(r"[^a-z0-9]+")


class MusicSurveySaveError(ValueError):
    """Client-visible validation failure (maps to HTTP 422)."""


class MusicBrandRegistryCollisionError(MusicSurveySaveError):
    """brand_id collides with a config/manga/canonical_brand_list.yaml key.

    Path X (37 manga brands) is frozen and read-only for music-mode flows — this is a
    hard reject (maps to HTTP 400 in music_survey_routes.py), never a silent drop.
    """


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


# ═══════════════════════════════════════════════════════════════════════════
# MUSIC-MODE-BRAND-INTEGRATION-V1-01 §3/§5 — music_brand_registry.yaml append/update
#
# Mirrors brand-wizard-app/src/brandMatch.js musicianHandleFromState/
# slugifyMusicianHandle so the client-side preview brand_id (matchBrand/generateYAML)
# and this server-authoritative registry row never disagree for the same signup.
# ═══════════════════════════════════════════════════════════════════════════


def _repo_root() -> Path:
    # brand-wizard-app/server/music_survey_save_handler.py -> repo root is 2 parents up.
    return Path(__file__).resolve().parents[2]


def default_music_registry_path() -> Path:
    return _repo_root() / "config" / "music" / "music_brand_registry.yaml"


def default_canonical_brand_list_path() -> Path:
    return _repo_root() / "config" / "manga" / "canonical_brand_list.yaml"


def slugify_musician_handle(value: Any) -> str:
    s = str(value or "").strip().lower()
    s = _SLUG_COLLAPSE_RE.sub("_", s).strip("_")
    return s[:80] or "musician"


def musician_handle_from_survey(survey_responses: Mapping[str, Any]) -> str:
    raw = survey_responses.get("display_name") or survey_responses.get("musician_handle") or ""
    return slugify_musician_handle(raw)


def _load_yaml_doc_readonly(path: Path) -> dict[str, Any]:
    """Plain (non-comment-preserving) load — only used for read-only inspection
    (canonical_brand_list.yaml collision check). Never written back via this loader."""
    if yaml is None:
        raise RuntimeError("PyYAML is required for music survey save")  # pragma: no cover
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    data = yaml.safe_load(raw)
    return data if isinstance(data, dict) else {}


def _canonical_brand_ids(canonical_brand_list_path: Path) -> set[str]:
    doc = _load_yaml_doc_readonly(canonical_brand_list_path)
    brands = doc.get("brands")
    return set(brands.keys()) if isinstance(brands, dict) else set()


_ENTRY_START_RE = re.compile(r'^  - brand_id:\s*"?([^"\s]+)"?\s*$')
_MUSIC_BRANDS_KEY_RE = re.compile(r"^music_brands:\s*(#.*)?$")


def _find_music_brands_list_span(lines: list[str]) -> tuple[int, int]:
    """Return (body_start, body_end_exclusive) — the line range holding the
    ``music_brands:`` list body (everything after the key line up to the next
    column-0, non-comment, non-blank top-level key, or end of file)."""
    key_idx = next((i for i, ln in enumerate(lines) if _MUSIC_BRANDS_KEY_RE.match(ln)), None)
    if key_idx is None:
        raise MusicSurveySaveError(
            "music_brand_registry.yaml has no top-level `music_brands:` key"
        )
    end = len(lines)
    for i in range(key_idx + 1, len(lines)):
        ln = lines[i]
        if ln.strip() and not ln.startswith(" ") and not ln.startswith("#"):
            end = i
            break
    return key_idx + 1, end


def _find_entry_span(
    lines: list[str], body_start: int, body_end: int, brand_id: str
) -> Optional[tuple[int, int]]:
    """Return (entry_start, entry_end_exclusive) for the existing
    ``  - brand_id: <brand_id>`` entry's OWN field lines within the list body.
    Comment lines immediately preceding the entry are left untouched (not included
    in the span) so entry-level documentation survives an idempotent update."""
    starts = [i for i in range(body_start, body_end) if _ENTRY_START_RE.match(lines[i])]
    for pos, s in enumerate(starts):
        m = _ENTRY_START_RE.match(lines[s])
        if m and m.group(1) == brand_id:
            e = starts[pos + 1] if pos + 1 < len(starts) else body_end
            while e > s + 1 and lines[e - 1].strip() == "":
                e -= 1
            return s, e
    return None


def _yaml_quote(value: str) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _render_registry_entry_lines(entry: Mapping[str, Any]) -> list[str]:
    """Render one ``music_brands`` list entry in the file's existing plain-scalar,
    2-space list-indent style (see the ``_template_music`` / ``ahjan_music`` rows)."""
    lines = [f"  - brand_id: {entry['brand_id']}"]
    for key in ("musician_handle", "archetype", "mode", "status", "survey_yaml_pointer", "created"):
        lines.append(f"    {key}: {entry[key]}")
    notes = entry.get("notes", "")
    if notes:
        lines.append(f"    notes: {_yaml_quote(notes)}")
    return lines


def upsert_music_brand_registry_row(
    *,
    registry_path: Path,
    canonical_brand_list_path: Path,
    brand_id: str,
    musician_handle: str,
    survey_yaml_pointer: str,
    archetype: Optional[str] = None,
    notes: Optional[str] = None,
    today: Optional[str] = None,
) -> dict[str, Any]:
    """
    Append (new brand_id) or update-in-place (idempotent re-save) a row under
    ``music_brands:`` in ``registry_path``, via *text splice* — never a full
    parse+re-dump — so the file's header/schema/anti-drift comments (the schema
    authority for this registry, per its own header) are preserved byte-for-byte
    outside the touched entry.

    Anti-drift invariants enforced here (music_brand_registry.yaml header + spec §5):
      - brand_id colliding with a config/manga/canonical_brand_list.yaml key is a hard
        reject (MusicBrandRegistryCollisionError) — Path X (37) stays frozen, never
        silently dropped.
      - re-saving the same brand_id updates the existing row IN PLACE (idempotent) —
        never appends a duplicate row, and never loses the original `created` date.
    """
    if brand_id in _canonical_brand_ids(canonical_brand_list_path):
        raise MusicBrandRegistryCollisionError(
            f"brand_id '{brand_id}' collides with a config/manga/canonical_brand_list.yaml "
            "key — Path X (37) is frozen and read-only for music-mode brands"
        )
    if not registry_path.exists():
        raise MusicSurveySaveError(f"music brand registry not found at {registry_path}")

    raw = registry_path.read_text(encoding="utf-8")
    trailing_newline = raw.endswith("\n")
    lines = raw.split("\n")
    if trailing_newline:
        lines = lines[:-1]

    body_start, body_end = _find_music_brands_list_span(lines)
    existing_span = _find_entry_span(lines, body_start, body_end, brand_id)
    ts = today or _dt.date.today().isoformat()
    default_notes = f"Wizard survey save via music_survey_save_handler (musician_handle={musician_handle})."

    if existing_span is not None:
        s, e = existing_span
        # Recover the prior row's fields (esp. `created` — never overwritten silently)
        # by loading just that slice through a throwaway single-entry YAML document.
        prior_doc = yaml.safe_load("music_brands:\n" + "\n".join(lines[s:e]) + "\n") if yaml else None
        prior_row = (prior_doc or {}).get("music_brands", [{}])[0] if prior_doc else {}
        entry = {
            "brand_id": brand_id,
            "musician_handle": musician_handle,
            "archetype": archetype or prior_row.get("archetype") or "unspecified",
            "mode": "music",
            "status": "active",
            "survey_yaml_pointer": survey_yaml_pointer,
            "created": prior_row.get("created", ts),
            "notes": notes or default_notes,
        }
        new_lines = _render_registry_entry_lines(entry)
        lines = lines[:s] + new_lines + lines[e:]
        action = "updated"
    else:
        entry = {
            "brand_id": brand_id,
            "musician_handle": musician_handle,
            "archetype": archetype or "unspecified",
            "mode": "music",
            "status": "active",
            "survey_yaml_pointer": survey_yaml_pointer,
            "created": ts,
            "notes": notes or default_notes,
        }
        new_lines = _render_registry_entry_lines(entry)
        insertion: list[str] = []
        if body_end == 0 or (body_end > 0 and lines[body_end - 1].strip() != ""):
            insertion.append("")
        insertion.extend(new_lines)
        lines = lines[:body_end] + insertion + lines[body_end:]
        action = "appended"

    out_text = "\n".join(lines) + ("\n" if trailing_newline else "")
    atomic_write_text(registry_path, out_text)
    return {"action": action, "brand_id": brand_id, "musician_handle": musician_handle}


def save_survey_to_brand_yaml(
    *,
    brands_dir: Path,
    wizard_session_id: str,
    survey_responses: dict[str, Any],
    music_registry_path: Optional[Path] = None,
    canonical_brand_list_path: Optional[Path] = None,
) -> dict[str, Any]:
    """
    Load ``<wizard_session_id>.yaml`` under ``brands_dir``, merge survey into ``musician_reflections``,
    write atomically, then upsert the matching ``config/music/music_brand_registry.yaml`` row
    (§3/§5). Returns API body fields (status, next_step, yaml_path) — response shape is
    unchanged from before the registry-append fix (registry write is a side effect, not a
    response field), so existing callers/tests are unaffected.
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

    # §3/§5: mint/update the registry row. brand_id is ALWAYS derived from the survey's
    # musician handle (Q2: <musician_handle>_music) — never from wizard_session_id, which
    # is caller-supplied and not guaranteed to already be brand_id-shaped.
    handle = musician_handle_from_survey(responses)
    brand_id = f"{handle}_music"
    archetype = responses.get("archetype") or responses.get("primary_genre")
    upsert_music_brand_registry_row(
        registry_path=music_registry_path or default_music_registry_path(),
        canonical_brand_list_path=canonical_brand_list_path or default_canonical_brand_list_path(),
        brand_id=brand_id,
        musician_handle=handle,
        survey_yaml_pointer=rel,
        archetype=archetype,
    )

    return {
        "status": "saved",
        "next_step": "step5",
        "yaml_path": rel,
    }
