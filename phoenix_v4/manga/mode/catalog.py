"""Catalog-to-production contract for teacher- and music-mode manga.

This module is the single boundary between brand identity and manga production:
catalog planners call :func:`apply_brand_mode`, while series/chapter production
calls :func:`build_mode_source_packet`.  The contract is deliberately fail-closed
when a mode is declared: a teacher series needs a real teacher bank and a music
series needs an active music brand with a real musician bank.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

import yaml

from .validator import assert_mode_xor

REPO_ROOT = Path(__file__).resolve().parents[3]
MUSIC_REGISTRY = Path("config/music/music_brand_registry.yaml")
TEACHER_BANKS = Path("SOURCE_OF_TRUTH/teacher_banks")
MUSICIAN_BANKS = Path("SOURCE_OF_TRUTH/musician_banks")


class ModeSourceError(ValueError):
    """A declared mode cannot be backed by a valid identity/source bank."""


def _root(repo_root: Path | None) -> Path:
    return Path(repo_root) if repo_root is not None else REPO_ROOT


def _yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ModeSourceError(f"required mode source is missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ModeSourceError(f"mode source must be a mapping: {path}")
    return data


def active_music_brands(repo_root: Path | None = None) -> dict[str, str]:
    """Return active ``brand_id -> musician_id`` bindings from the music SSOT."""
    root = _root(repo_root)
    registry = _yaml(root / MUSIC_REGISTRY)
    out: dict[str, str] = {}
    for row in registry.get("music_brands") or []:
        if not isinstance(row, dict) or row.get("status") != "active":
            continue
        brand_id = str(row.get("brand_id") or "").strip()
        musician_id = str(row.get("musician_handle") or "").strip()
        if brand_id and musician_id:
            out[brand_id] = musician_id
    return out


def apply_brand_mode(
    plan: Mapping[str, Any], *, repo_root: Path | None = None
) -> dict[str, Any]:
    """Resolve a catalog row to legacy, teacher, or music mode.

    Active music registry membership wins only when ``teacher_id`` is empty.
    Any non-empty ``teacher_id`` makes the row teacher-mode.  Explicit fields are
    checked for consistency instead of silently rewritten.
    """
    out = dict(plan)
    brand_id = str(out.get("brand_id") or "").strip()
    teacher_id = str(out.get("teacher_id") or "").strip()
    explicit_musician = str(out.get("musician_id") or "").strip()

    if teacher_id:
        if explicit_musician or out.get("mode") == "music":
            assert_mode_xor(out)
        out["mode"] = out.get("mode") or "teacher"
        out["musician_id"] = None
    else:
        registered_musician = active_music_brands(repo_root).get(brand_id, "")
        musician_id = explicit_musician or registered_musician
        if not musician_id:
            if out.get("mode"):
                assert_mode_xor(out)
            return out
        if out.get("mode") == "teacher":
            candidate = dict(out)
            candidate["musician_id"] = musician_id
            assert_mode_xor(candidate)
        out["mode"] = out.get("mode") or "music"
        out["teacher_id"] = None
        out["musician_id"] = musician_id

    assert_mode_xor(out)
    return out


def _stable_pick(paths: list[Path], seed: str, count: int) -> list[Path]:
    if not paths or count <= 0:
        return []
    ranked = sorted(
        paths,
        key=lambda p: hashlib.sha256(f"{seed}|{p.as_posix()}".encode()).hexdigest(),
    )
    return ranked[:count]


def _atom_text(doc: Mapping[str, Any]) -> str:
    body = doc.get("body")
    if isinstance(body, str) and body.strip():
        return body.strip()
    variants = doc.get("variants") or []
    if variants and isinstance(variants[0], dict):
        return str(variants[0].get("body") or "").strip()
    return ""


def _clean_source(text: str, identity_id: str, limit: int = 1200) -> str:
    """Keep packets compact and prevent template/name leakage into fiction."""
    cleaned = " ".join(text.split())
    cleaned = cleaned.replace("{{musician_name}}", "the music")
    cleaned = cleaned.replace(identity_id, "the source voice")
    cleaned = cleaned.replace(identity_id.title(), "the source voice")
    return cleaned[:limit].rstrip()


def build_mode_source_packet(
    series_plan: Mapping[str, Any],
    *,
    topic: str = "",
    seed: str = "",
    repo_root: Path | None = None,
) -> dict[str, Any] | None:
    """Load a compact, deterministic, writer-safe source packet.

    Teacher packets contain approved doctrine prose for dramatization. Music
    packets contain the musician profile/themes plus opening, pivot, and closing
    atoms. Source paths remain internal metadata; the teacher/musician must never
    be named as a fictional character unless a separate disclosure contract says so.
    """
    plan = apply_brand_mode(series_plan, repo_root=repo_root)
    mode = plan.get("mode")
    if not mode:
        return None
    root = _root(repo_root)
    identity_id = str(plan["teacher_id"] if mode == "teacher" else plan["musician_id"])
    packet_seed = seed or str(plan.get("series_id") or identity_id)

    if mode == "teacher":
        bank = root / TEACHER_BANKS / identity_id / "approved_atoms"
        candidates = [p for p in bank.rglob("*.yaml") if p.is_file()]
        selected = _stable_pick(candidates, f"{packet_seed}|{topic}|teacher", 3)
        excerpts = []
        for path in selected:
            text = _clean_source(_atom_text(_yaml(path)), identity_id)
            if text and "placeholder" not in text.lower():
                excerpts.append(text)
        if not excerpts:
            raise ModeSourceError(f"teacher {identity_id!r} has no usable approved atoms")
        return {
            "mode": "teacher",
            "identity_id": identity_id,
            "topic": topic,
            "contract": "dramatize_doctrine_never_lecture",
            "source_refs": [str(p.relative_to(root)) for p in selected],
            "doctrine_excerpts": excerpts,
        }

    bank = root / MUSICIAN_BANKS / identity_id
    profile = _yaml(bank / "profile.yaml")
    themes = _yaml(bank / "themes.yaml")
    slot_names = ("LYRIC_OPENING", "LYRIC_BESTSELLER_BEAT", "LYRIC_CLOSING")
    motif: dict[str, str] = {}
    refs = [bank / "profile.yaml", bank / "themes.yaml"]
    for slot in slot_names:
        paths = sorted((bank / "approved_atoms" / slot).glob("*.yaml"))
        picked = _stable_pick(paths, f"{packet_seed}|{topic}|{slot}", 1)
        if not picked:
            raise ModeSourceError(f"musician {identity_id!r} missing required slot {slot}")
        refs.extend(picked)
        motif[slot.lower()] = _clean_source(_atom_text(_yaml(picked[0])), identity_id)
    return {
        "mode": "music",
        "identity_id": identity_id,
        "topic": topic,
        "contract": "transform_motif_never_explain",
        "source_refs": [str(p.relative_to(root)) for p in refs],
        "sound_identity": {
            "primary_genre": profile.get("primary_genre"),
            "primary_themes": themes.get("primary_themes") or [],
            "avoided_themes": themes.get("avoided_themes") or [],
            "listener_hope": themes.get("listener_hope_one"),
        },
        "motif_atoms": motif,
    }
