"""Serialize a completed song-kit to ``SOURCE_OF_TRUTH/musician_banks/<id>/``.

Cap (governing): ``MUSIC-ONBOARDING-SONG-KIT-V1-01`` (``docs/PEARL_ARCHITECT_STATE.md``)
Spec (governing): ``docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md`` §3.3

This is "Remaining work" item 2 from ``README_song_kit_generator.md``: the on-disk
write that turns a ``song_kit_generator.KitResult`` (in-memory, ``DraftAtom.status ==
"draft"``) into files under ``SOURCE_OF_TRUTH/musician_banks/<musician_id>/``.

Convention match (verified against ``SOURCE_OF_TRUTH/musician_banks/{ahjan,
test_artist_alpha}/`` on main, 2026-07-21): both reference banks store every atom
under ``approved_atoms/<SLOT_POOL>/<atom_id>.yaml`` in the canonical 2-key shape
(``atom_id`` + ``variants: [{body: ...}]``) — neither has a ``draft_atoms/`` split,
and neither atom file carries a ``status`` field on disk. ``DraftAtom.status`` is
in-memory bookkeeping the writer intentionally does NOT serialize (the 2-key shape
via ``to_atom_yaml_obj()`` already drops it). This writer matches that existing
convention exactly rather than inventing a third pattern: "drafts are PROPOSED, human-
reviewed" is honored by NOT auto-promoting anywhere else in the pipeline (catalog
runs never read an unreviewed bank without an explicit opt-in), not by a directory
split that doesn't exist in either reference bank today.
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

from phoenix_v4.musician.song_kit_generator import KitResult
from phoenix_v4.musician.survey_derivation import (
    survey_to_profile_dict,
    survey_to_themes_yaml,
    survey_to_voice_yaml,
)


def _dump(obj: Any) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


def write_kit_to_bank(
    kit: KitResult,
    musician_id: str,
    repo_root: Path,
    *,
    survey: dict[str, Any] | None = None,
    survey_date: str | None = None,
) -> list[Path]:
    """Write every ``DraftAtom`` in ``kit`` to ``approved_atoms/<POOL>/<atom_id>.yaml``.

    When ``survey`` is given, also (re-using ``survey_derivation`` — never re-derived
    by hand) writes ``profile.yaml`` / ``themes.yaml`` / ``voice_profile.yaml`` and
    persists the raw survey to ``survey_responses/<survey_date>.yaml`` (default:
    today, UTC date).

    Returns every path written, in write order. Raises ``RuntimeError`` if PyYAML is
    unavailable (matches ``survey_derivation.write_bank_from_survey``'s contract).
    """
    if yaml is None:
        raise RuntimeError("PyYAML required")

    bank_dir = Path(repo_root) / "SOURCE_OF_TRUTH" / "musician_banks" / musician_id
    atoms_dir = bank_dir / "approved_atoms"
    written: list[Path] = []

    for pool, atoms in kit.pools.items():
        pool_dir = atoms_dir / pool
        pool_dir.mkdir(parents=True, exist_ok=True)
        for atom in atoms:
            path = pool_dir / f"{atom.atom_id}.yaml"
            path.write_text(_dump(atom.to_atom_yaml_obj()), encoding="utf-8")
            written.append(path)

    if survey is not None:
        bank_dir.mkdir(parents=True, exist_ok=True)
        (bank_dir / "profile.yaml").write_text(
            _dump(survey_to_profile_dict(survey, musician_id)), encoding="utf-8"
        )
        written.append(bank_dir / "profile.yaml")
        (bank_dir / "themes.yaml").write_text(
            _dump(survey_to_themes_yaml(survey)), encoding="utf-8"
        )
        written.append(bank_dir / "themes.yaml")
        (bank_dir / "voice_profile.yaml").write_text(
            _dump(survey_to_voice_yaml(survey)), encoding="utf-8"
        )
        written.append(bank_dir / "voice_profile.yaml")

        responses_dir = bank_dir / "survey_responses"
        responses_dir.mkdir(parents=True, exist_ok=True)
        date_stamp = survey_date or _dt.datetime.now(_dt.timezone.utc).date().isoformat()
        resp_path = responses_dir / f"{date_stamp}.yaml"
        resp_path.write_text(_dump(dict(survey)), encoding="utf-8")
        written.append(resp_path)

    return written


__all__ = ["write_kit_to_bank"]
