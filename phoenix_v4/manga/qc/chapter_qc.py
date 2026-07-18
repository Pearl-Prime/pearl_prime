"""Build ``revision_queue`` from chapter workspace artifacts (deterministic QC)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

from phoenix_v4.manga.chapter.visual_from_script import iter_panels_from_chapter_script
from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models.validation import load_and_validate, validate_instance

if TYPE_CHECKING:
    from phoenix_v4.manga.series.profile_loader import MangaProfile


def _lettering_by_panel(lettering: Mapping[str, Any]) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for row in lettering.get("lettering_panels") or []:
        pid = str(row.get("panel_id") or "")
        if pid:
            out[pid] = bool(row.get("silence_confirmed"))
    return out


def _panel_is_silent(panel: Mapping[str, Any]) -> bool:
    """True when the panel carries no written content at all (true silence).

    Mirrors the lettering builder's ``silence_confirmed`` definition
    (``lettering_from_script.build_lettering_spec_from_chapter_script``): a panel
    is silent only when it has no dialogue text AND no narrator caption/narration
    AND no SFX. A caption-only panel is NOT silent — its caption must be lettered
    — so the lettering-silence cross-check must agree, or caption-bearing
    iyashikei panels (the Devotion/Open Vessel healing register leans on
    observational captions) spuriously trip ``LETTERING_MISMATCH``.
    """
    # Dialogue with text → not silent (handles legacy str list + v2 dict list).
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list):
        for x in dialogue:
            if isinstance(x, str):
                if x.strip():
                    return False
            elif isinstance(x, Mapping):
                if str(x.get("text") or "").strip():
                    return False
            elif x is not None and str(x).strip():
                return False
    # Narrator caption / narration → not silent (needs a caption box).
    if str(panel.get("narrator_caption") or panel.get("caption") or "").strip():
        return False
    if str(panel.get("narration") or "").strip():
        return False
    # SFX → not silent.
    sfx = panel.get("sfx")
    if isinstance(sfx, list) and any(str(s or "").strip() for s in sfx):
        return False
    if isinstance(sfx, str) and sfx.strip():
        return False
    return True


# Back-compat alias (older name referred only to dialogue).
_panel_has_no_dialogue_text = _panel_is_silent


def build_revision_queue_for_chapter(
    workspace: Path,
    *,
    schema_version: str = "1.0.0",
    manga_profile: "MangaProfile | None" = None,
) -> dict[str, Any]:
    """Read chapter + series paths under ``workspace``; return validated revision_queue."""
    ws = Path(workspace).resolve()
    issues: list[dict[str, Any]] = []

    handoff_p = ws / manga_paths.STORY_ARCHITECTURE_HANDOFF
    if not handoff_p.is_file():
        issues.append(
            {
                "issue_code": "MISSING_STORY_HANDOFF",
                "gate_id": "MANGA_GATE_STORY_HANDOFF",
                "severity": "BLOCKER",
                "stage_owner": "transmission_split",
                "description": str(handoff_p),
            }
        )
    else:
        try:
            load_and_validate(handoff_p, "story_architecture_handoff")
        except Exception as e:
            issues.append(
                {
                    "issue_code": "INVALID_STORY_HANDOFF",
                    "gate_id": "MANGA_GATE_STORY_HANDOFF",
                    "severity": "BLOCKER",
                    "stage_owner": "transmission_split",
                    "description": str(e),
                }
            )

    script_p = ws / manga_paths.CHAPTER_SCRIPT_WRITER_HANDOFF
    manifest_p = ws / manga_paths.PANEL_IMAGES_MANIFEST
    lettering_p = ws / manga_paths.LETTERING_SPEC

    if script_p.is_file() and manifest_p.is_file():
        try:
            manifest = json.loads(manifest_p.read_text(encoding="utf-8"))
            validate_instance(manifest, "panel_images_manifest")
            for row in manifest.get("panels") or []:
                if str(row.get("status")) != "ok":
                    issues.append(
                        {
                            "issue_code": "PANEL_NOT_OK",
                            "gate_id": "MANGA_GATE_IMAGES_ALL_OK",
                            "severity": "BLOCKER",
                            "stage_owner": "chapter_image_gen",
                            "description": f"panel {row.get('panel_id')!r} status {row.get('status')!r}",
                        }
                    )
                    break
                if not row.get("path") or not row.get("width") or not row.get("height"):
                    issues.append(
                        {
                            "issue_code": "PANEL_INCOMPLETE",
                            "gate_id": "MANGA_GATE_IMAGES_ALL_OK",
                            "severity": "BLOCKER",
                            "stage_owner": "chapter_image_gen",
                            "description": f"panel {row.get('panel_id')!r} missing path/dimensions",
                        }
                    )
                    break
        except Exception as e:
            issues.append(
                {
                    "issue_code": "MANIFEST_INVALID",
                    "gate_id": "MANGA_GATE_IMAGES_ALL_OK",
                    "severity": "BLOCKER",
                    "stage_owner": "chapter_image_gen",
                    "description": str(e),
                }
            )

    if script_p.is_file() and lettering_p.is_file():
        try:
            script = json.loads(script_p.read_text(encoding="utf-8"))
            lettering = json.loads(lettering_p.read_text(encoding="utf-8"))
            validate_instance(lettering, "lettering_spec")
            by_letter = _lettering_by_panel(lettering)
            for panel in iter_panels_from_chapter_script(script):
                pid = str(panel.get("panel_id") or "")
                if not pid:
                    continue
                silent_panel = _panel_is_silent(panel)
                got = by_letter.get(pid)
                if got is not None and bool(got) != bool(silent_panel):
                    issues.append(
                        {
                            "issue_code": "LETTERING_MISMATCH",
                            "gate_id": "MANGA_GATE_LETTERING_SILENCE",
                            "severity": "BLOCKER",
                            "stage_owner": "chapter_lettering",
                            "description": f"panel {pid!r} silence_confirmed vs dialogue mismatch",
                        }
                    )
                    break
        except Exception as e:
            issues.append(
                {
                    "issue_code": "LETTERING_CHECK_FAILED",
                    "gate_id": "MANGA_GATE_LETTERING_SILENCE",
                    "severity": "BLOCKER",
                    "stage_owner": "chapter_lettering",
                    "description": str(e),
                }
            )

    if script_p.is_file():
        try:
            script = json.loads(script_p.read_text(encoding="utf-8"))
            n_pages = len(script.get("pages") or [])
            comp_dir = ws / manga_paths.FINAL_PAGE_COMPOSITE_DIR
            if n_pages > 0:
                if not comp_dir.is_dir():
                    issues.append(
                        {
                            "issue_code": "MISSING_COMPOSITE_DIR",
                            "gate_id": "MANGA_GATE_LAYOUT_PAGES",
                            "severity": "BLOCKER",
                            "stage_owner": "chapter_layout",
                            "description": str(comp_dir),
                        }
                    )
                else:
                    for i in range(1, n_pages + 1):
                        png = comp_dir / f"page_{i:03d}.png"
                        if not png.is_file():
                            issues.append(
                                {
                                    "issue_code": "MISSING_PAGE_PNG",
                                    "gate_id": "MANGA_GATE_LAYOUT_PAGES",
                                    "severity": "BLOCKER",
                                    "stage_owner": "chapter_layout",
                                    "description": str(png),
                                }
                            )
                            break
        except Exception as e:
            issues.append(
                {
                    "issue_code": "LAYOUT_CHECK_FAILED",
                    "gate_id": "MANGA_GATE_LAYOUT_PAGES",
                    "severity": "BLOCKER",
                    "stage_owner": "chapter_layout",
                    "description": str(e),
                }
            )

    # Profile-dependent gates (only if profile is provided)
    if manga_profile is not None:
        from phoenix_v4.manga.qc.hook_gate import check_chapter_hook
        from phoenix_v4.manga.qc.pacing_gates import check_silence_density, check_genre_authenticity
        if script_p.is_file():
            try:
                script_data = json.loads(script_p.read_text(encoding="utf-8"))
                hook_issue = check_chapter_hook(script_data, manga_profile)
                if hook_issue:
                    issues.append(hook_issue)
            except Exception as exc:
                issues.append({
                    "issue_code": "HOOK_GATE_ERROR",
                    "gate_id": "MANGA.CHAPTER.HOOK",
                    "severity": "MAJOR",
                    "stage_owner": "chapter_qc",
                    "description": f"Hook gate check failed: {exc}",
                })
            try:
                script_data = json.loads(script_p.read_text(encoding="utf-8"))
                lettering_data = json.loads(lettering_p.read_text(encoding="utf-8")) if lettering_p.is_file() else {}
                silence_issue = check_silence_density(script_data, lettering_data, manga_profile)
                if silence_issue:
                    issues.append(silence_issue)
                genre_issue = check_genre_authenticity(script_data, manga_profile)
                if genre_issue:
                    issues.append(genre_issue)
            except Exception as exc:
                issues.append({
                    "issue_code": "PACING_GATE_ERROR",
                    "gate_id": "MANGA.GENRE.AUTHENTICITY",
                    "severity": "MAJOR",
                    "stage_owner": "chapter_qc",
                    "description": f"Pacing gate check failed: {exc}",
                })
            try:
                from phoenix_v4.manga.qc.restraint_gate import check_restraint_over_exposition
                script_data = json.loads(script_p.read_text(encoding="utf-8"))
                restraint_issue = check_restraint_over_exposition(script_data, manga_profile)
                if restraint_issue:
                    issues.append(restraint_issue)
            except Exception:
                pass  # gate errors are non-fatal
            try:
                from phoenix_v4.manga.qc.yearning_gate import check_yearning_pacing
                script_data = json.loads(script_p.read_text(encoding="utf-8"))
                yearning_issue = check_yearning_pacing(script_data, manga_profile)
                if yearning_issue:
                    issues.append(yearning_issue)
            except Exception:
                pass  # gate errors are non-fatal

    blockers = [x for x in issues if x.get("severity") == "BLOCKER"]
    clearance = "pass" if not blockers else "hold"
    doc: dict[str, Any] = {
        "schema_version": schema_version,
        "artifact_type": "revision_queue",
        "chapter_clearance": clearance,
        "issues": issues,
    }
    validate_instance(doc, "revision_queue")
    return doc
