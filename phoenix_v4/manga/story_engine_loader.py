"""Load and validate config/manga/story_engines.yaml — genre-native story engine enforcement."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_REPO: Path | None = None
_CACHE: dict[str, Any] | None = None


class StoryEngineError(RuntimeError):
    """Raised when a governed genre lacks a strategy bank or fails engine validation."""


def _repo_root() -> Path:
    global _REPO
    if _REPO is None:
        _REPO = Path(__file__).resolve().parents[2]
    return _REPO


def load_story_engines_config(repo_root: Path | None = None) -> dict[str, Any]:
    global _CACHE
    root = repo_root or _repo_root()
    if _CACHE is not None and repo_root is None:
        return _CACHE
    path = root / "config" / "manga" / "story_engines.yaml"
    if yaml is None or not path.is_file():
        return {"engines": {}, "legacy_generic_template_markers": []}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if repo_root is None:
        _CACHE = data
    return data


def _alias_map(config: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for canon, block in (config.get("engines") or {}).items():
        out[str(canon).lower()] = str(canon)
        for alias in block.get("aliases") or []:
            out[str(alias).lower()] = str(canon)
    return out


def resolve_engine_genre(genre_id: str, repo_root: Path | None = None) -> str:
    """Map genre_id / alias → canonical engine key."""
    key = (genre_id or "").strip().lower().replace("-", "_").replace(" ", "_")
    config = load_story_engines_config(repo_root)
    return _alias_map(config).get(key, key)


def is_engine_governed(genre_id: str, repo_root: Path | None = None) -> bool:
    canon = resolve_engine_genre(genre_id, repo_root)
    config = load_story_engines_config(repo_root)
    return canon in (config.get("engines") or {})


def engine_spec(genre_id: str, repo_root: Path | None = None) -> dict[str, Any] | None:
    canon = resolve_engine_genre(genre_id, repo_root)
    config = load_story_engines_config(repo_root)
    block = (config.get("engines") or {}).get(canon)
    return block if isinstance(block, dict) else None


def governed_genres(repo_root: Path | None = None) -> list[str]:
    config = load_story_engines_config(repo_root)
    return sorted((config.get("engines") or {}).keys())


def _blob_from_chapters(chapters: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for ch in chapters:
        for beat in ch.get("plot_beats") or []:
            parts.append(str(beat.get("beat_text") or ""))
    return "\n".join(parts).lower()


def _blob_from_chapter_script(chapter_script: Mapping[str, Any]) -> str:
    try:
        from phoenix_v4.manga.qc._script_shape import iter_panels, panel_text
    except Exception:
        return ""
    return "\n".join(panel_text(p).lower() for p in iter_panels(chapter_script))


def _marker_hits(blob: str, markers: list[str]) -> list[str]:
    return [m for m in markers if m.lower() in blob]


def validate_engine_blob(
    blob: str,
    genre_id: str,
    *,
    repo_root: Path | None = None,
) -> list[str]:
    """Return violation messages; empty list means PASS."""
    spec = engine_spec(genre_id, repo_root)
    if not spec:
        return []

    config = load_story_engines_config(repo_root)
    violations: list[str] = []
    canon = resolve_engine_genre(genre_id, repo_root)
    low = blob.lower()

    for group in spec.get("required_marker_groups") or []:
        if not isinstance(group, dict):
            continue
        markers = [str(m) for m in (group.get("markers") or [])]
        min_hits = int(group.get("min_hits") or 1)
        hits = _marker_hits(low, markers)
        if len(hits) < min_hits:
            violations.append(
                f"{canon}: need >={min_hits} engine markers, got {len(hits)} "
                f"(required family: {markers[:4]}...)"
            )

    for phrase in spec.get("generic_failure_avoid") or []:
        if str(phrase).lower() in low:
            violations.append(f"{canon}: generic_failure pattern {phrase!r}")

    for phrase in config.get("legacy_generic_template_markers") or []:
        if str(phrase).lower() in low:
            violations.append(f"{canon}: legacy generic template marker {phrase!r}")

    return violations


def validate_architect_chapters(
    chapters: list[dict[str, Any]],
    genre_id: str,
    *,
    repo_root: Path | None = None,
) -> None:
    """Raise StoryEngineError if architect output fails engine enforcement."""
    if not is_engine_governed(genre_id, repo_root):
        return
    violations = validate_engine_blob(
        _blob_from_chapters(chapters), genre_id, repo_root=repo_root,
    )
    if violations:
        raise StoryEngineError(
            f"story engine validation failed for {resolve_engine_genre(genre_id, repo_root)!r}: "
            + "; ".join(violations)
        )


def validate_chapter_script_engine(
    chapter_script: Mapping[str, Any],
    genre_id: str,
    *,
    repo_root: Path | None = None,
) -> list[str]:
    """Return violation strings for bestseller gate (non-throwing)."""
    declared = str(
        chapter_script.get("genre")
        or chapter_script.get("genre_id")
        or genre_id
        or ""
    )
    if not is_engine_governed(declared, repo_root):
        return []
    return validate_engine_blob(
        _blob_from_chapter_script(chapter_script), declared, repo_root=repo_root,
    )
