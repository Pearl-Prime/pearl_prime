"""Genre-native story engine gate — blocks generic spines with correct shell metadata."""
from __future__ import annotations

from typing import Any, Mapping

from phoenix_v4.manga.story_engine_loader import (
    is_engine_governed,
    resolve_engine_genre,
    validate_chapter_script_engine,
)


def evaluate_genre_engine(
    chapter_script: Mapping[str, Any],
    *,
    genre_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return BLOCKER findings for structurally generic governed-genre output."""
    declared = str(
        genre_id
        or chapter_script.get("genre")
        or chapter_script.get("genre_id")
        or ""
    ).strip()
    if not declared:
        return [{
            "issue_code": "GENRE_ENGINE_UNDECLARED",
            "gate_id": "MANGA.BESTSELLER.GENRE_ENGINE",
            "severity": "BLOCKER",
            "stage_owner": "chapter_qc",
            "description": "Commercial chapter missing declared genre for engine validation",
        }]

    if is_engine_governed(declared) and declared.lower() in ("iyashikei", "healing"):
        pass  # iyashikei not in governed set

    violations = validate_chapter_script_engine(chapter_script, declared)
    findings: list[dict[str, Any]] = []
    for v in violations:
        findings.append({
            "issue_code": "GENRE_ENGINE_GENERIC_SPINE",
            "gate_id": "MANGA.BESTSELLER.GENRE_ENGINE",
            "severity": "BLOCKER",
            "stage_owner": "chapter_qc",
            "description": v,
        })

    # Cross-shell iyashikei leakage on governed commercial shells (non-iyashikei).
    canon = resolve_engine_genre(declared)
    if is_engine_governed(canon) and canon != "iyashikei":
        try:
            from phoenix_v4.manga.qc.genre_shell import _iyashikei_leakage
        except ImportError:
            _iyashikei_leakage = None  # type: ignore[misc, assignment]
        if _iyashikei_leakage is not None:
            vessel = str(chapter_script.get("vessel") or "")
            craft = str(chapter_script.get("craft_notes") or "")
            leak = _iyashikei_leakage(canon, vessel, craft, "")
            if leak:
                findings.append({
                    "issue_code": "GENRE_ENGINE_IYASHIKEI_LEAK",
                    "gate_id": "MANGA.BESTSELLER.GENRE_ENGINE",
                    "severity": "BLOCKER",
                    "stage_owner": "chapter_qc",
                    "description": leak,
                })

    return findings
