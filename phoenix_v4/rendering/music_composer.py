"""Select and hydrate music atoms from ``SOURCE_OF_TRUTH/musician_banks``."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]


def _deterministic_index(seed: str, pool_size: int) -> int:
    if pool_size <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % pool_size


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_musician_profile(repo_root: Path, musician_id: str) -> dict[str, Any]:
    base = repo_root / "SOURCE_OF_TRUTH" / "musician_banks" / musician_id
    profile = _load_yaml(base / "profile.yaml")
    themes = _load_yaml(base / "themes.yaml")
    voice = _load_yaml(base / "voice_profile.yaml")
    out = {**profile, "themes_file": themes, "voice_profile": voice}
    return out


def list_atom_files(repo_root: Path, musician_id: str, pool_key: str) -> list[Path]:
    d = repo_root / "SOURCE_OF_TRUTH" / "musician_banks" / musician_id / "approved_atoms" / pool_key
    if not d.is_dir():
        return []
    return sorted(p for p in d.glob("*.yaml") if p.is_file())


def _flatten_variants(doc: dict[str, Any]) -> list[str]:
    """Support ``variants: [{body: ...}]`` or legacy single ``body``."""
    variants = doc.get("variants")
    if isinstance(variants, list) and variants:
        texts: list[str] = []
        for item in variants:
            if isinstance(item, dict):
                t = item.get("body") or item.get("text") or ""
                if isinstance(t, str) and t.strip():
                    texts.append(t.strip())
            elif isinstance(item, str) and item.strip():
                texts.append(item.strip())
        if texts:
            return texts
    body = doc.get("body")
    if isinstance(body, str) and body.strip():
        return [body.strip()]
    return []


def compose_atom_text(
    repo_root: Path,
    musician_id: str,
    pool_key: str,
    *,
    chapter_index: int,
    book_seed: str,
    persona_id: str,
    topic_id: str,
    substitutions: dict[str, str],
) -> str:
    """Pick one YAML file from the pool, then one variant, hydrate ``{{keys}}``."""
    files = list_atom_files(repo_root, musician_id, pool_key)
    if not files:
        return f"[Music atom pool empty: {musician_id}/{pool_key}]"

    f_idx = _deterministic_index(f"{book_seed}|{pool_key}|ch{chapter_index}", len(files))
    doc = _load_yaml(files[f_idx])
    texts = _flatten_variants(doc)
    if not texts:
        return f"[Music atom missing body: {files[f_idx].name}]"

    v_idx = _deterministic_index(
        f"{book_seed}|{pool_key}|ch{chapter_index}|v|{persona_id}|{topic_id}",
        len(texts),
    )
    raw = texts[v_idx]
    for k, v in substitutions.items():
        raw = raw.replace("{{" + k + "}}", v)
    return raw


def build_substitutions(profile: dict[str, Any], persona_id: str, topic_id: str) -> dict[str, str]:
    name = str(profile.get("display_name") or profile.get("musician_id") or "the artist")
    themes = profile.get("themes") or (profile.get("themes_file") or {}).get("themes") or []
    if isinstance(themes, list):
        theme_str = ", ".join(str(t) for t in themes[:5])
    else:
        theme_str = str(themes)
    genre = str(profile.get("primary_genre") or "indie")
    healing = str(profile.get("healing_intent_summary") or profile.get("healing_intent") or "")
    return {
        "musician_name": name,
        "theme": theme_str,
        "persona_anchor": persona_id.replace("_", " "),
        "topic_anchor": topic_id.replace("_", " "),
        "genre": genre,
        "healing_intent": healing,
    }
