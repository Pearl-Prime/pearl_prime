"""Second-person music framing (intro / conclusion) from musician bank templates."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

from phoenix_v4.rendering.music_composer import _deterministic_index, _flatten_variants, _load_yaml


def _pick_variant_text(doc: dict[str, Any], seed: str) -> str:
    texts = _flatten_variants(doc)
    if not texts:
        return ""
    idx = _deterministic_index(seed, len(texts))
    return texts[idx]


def render_music_intro_2p(
    repo_root: Path,
    musician_id: str,
    *,
    persona_id: str,
    topic_id: str,
    book_seed: str,
) -> str:
    path = (
        repo_root
        / "SOURCE_OF_TRUTH"
        / "musician_banks"
        / musician_id
        / "approved_atoms"
        / "INTRO_2P_TEMPLATE.yaml"
    )
    doc = _load_yaml(path)
    raw = _pick_variant_text(doc, f"{book_seed}|intro2p|{musician_id}")
    if not raw:
        return ""
    from phoenix_v4.rendering.music_composer import build_substitutions, load_musician_profile

    profile = load_musician_profile(repo_root, musician_id)
    subs = build_substitutions(profile, persona_id, topic_id)
    for k, v in subs.items():
        raw = raw.replace("{{" + k + "}}", v)
    return raw.strip()


def render_music_conclusion_2p(
    repo_root: Path,
    musician_id: str,
    *,
    persona_id: str,
    topic_id: str,
    book_seed: str,
) -> str:
    path = (
        repo_root
        / "SOURCE_OF_TRUTH"
        / "musician_banks"
        / musician_id
        / "approved_atoms"
        / "CONCLUSION_2P_TEMPLATE.yaml"
    )
    doc = _load_yaml(path)
    raw = _pick_variant_text(doc, f"{book_seed}|conclusion2p|{musician_id}")
    if not raw:
        return ""
    from phoenix_v4.rendering.music_composer import build_substitutions, load_musician_profile

    profile = load_musician_profile(repo_root, musician_id)
    subs = build_substitutions(profile, persona_id, topic_id)
    for k, v in subs.items():
        raw = raw.replace("{{" + k + "}}", v)
    return raw.strip()
