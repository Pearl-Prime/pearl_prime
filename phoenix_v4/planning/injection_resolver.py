"""Resolve [STORY_INJECTION_POINT] / [EXERCISE_INJECTION_POINT] in legacy template text."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from phoenix_v4.planning.exercise_registry_loader import load_exercise_registry
from phoenix_v4.planning.registry_resolver import _deterministic_index, _load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_STORY_MARK = "[STORY_INJECTION_POINT]"
_EX_MARK = "[EXERCISE_INJECTION_POINT]"

# Map exercise_metadata_registry `type` → approved exercise YAML stem under exercises_v4/approved/.
_TYPE_TO_APPROVED_STEM: Dict[str, str] = {
    "somatic_scan": "02_body_awareness_scan",
    "tracking": "02_body_awareness_scan",
    "breath": "00_breath_regulation",
    "somatic_hold": "07_self_contact_touch",
    "grounding": "01_grounding_orientation",
}

_EXERCISE_REGISTRY_BY_ROOT: Dict[str, Dict[str, Any]] = {}


def _exercise_registry(repo_root: Path) -> Dict[str, Any]:
    key = str(repo_root.resolve())
    if key not in _EXERCISE_REGISTRY_BY_ROOT:
        _EXERCISE_REGISTRY_BY_ROOT[key] = load_exercise_registry(repo_root=repo_root)
    return _EXERCISE_REGISTRY_BY_ROOT[key]


def _hash_pick(seed: str, n: int) -> int:
    return _deterministic_index(seed, n)


def _strip_known_marks(text: str) -> str:
    return text.replace(_STORY_MARK, "").replace(_EX_MARK, "")


def _story_words(text: str) -> int:
    return len(text.split()) if text else 0


def _exercise_prose_from_yaml(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    inner = data.get("content")
    if isinstance(inner, dict):
        parts: List[str] = []
        for key in ("intro", "guided_practice", "aha_noticing", "integration"):
            block = inner.get(key)
            if isinstance(block, str) and block.strip():
                parts.append(block.strip())
        if parts:
            return "\n\n".join(parts)
    for key in ("body", "description_full", "description"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    if isinstance(inner, str) and inner.strip():
        return inner.strip()
    return ""


def _resolve_approved_exercise_path(exercise_id: str, ex_dir: Path, repo_root: Path) -> Optional[Path]:
    eid = (exercise_id or "").strip()
    if not eid:
        return None
    for ext in (".yaml", ".yml"):
        direct = ex_dir / f"{eid}{ext}"
        if direct.is_file():
            return direct
    reg = _exercise_registry(repo_root)
    defn = reg.get(eid)
    if defn is None:
        return None
    stem = _TYPE_TO_APPROVED_STEM.get(defn.type)
    if not stem:
        return None
    for ext in (".yaml", ".yml"):
        p = ex_dir / f"{stem}{ext}"
        if p.is_file():
            return p
    return None


def _pick_registry_variant_for_slot(
    topic: str,
    chapter_index: int,
    section_index: int,
    seed: str,
    repo_root: Path,
    min_words: int,
) -> Optional[Dict[str, str]]:
    """Same chapter/section row as the somatic template (section_01 … section_10)."""
    top = (topic or "").strip()
    if not top:
        return None
    reg_path = repo_root / "registry" / f"{top}.yaml"
    if not reg_path.is_file():
        return None
    try:
        from phoenix_v4.planning.registry_resolver import load_registry

        reg = load_registry(top, registry_path=reg_path)
    except Exception:
        return None
    ch_key = f"chapter_{chapter_index:02d}"
    sec_key = f"section_{section_index:02d}"
    ch_data = (reg.get("sections") or {}).get(ch_key)
    if not isinstance(ch_data, dict):
        return None
    inner = ch_data.get("sections") or {}
    sec_data = inner.get(sec_key)
    if not isinstance(sec_data, dict):
        return None
    variants = sec_data.get("variants") or []
    if not variants:
        return None
    vi = _deterministic_index(f"{seed}:registry_variant", len(variants))
    var = variants[vi]
    if not isinstance(var, dict):
        return None
    content = str(var.get("content") or "").strip()
    if not content or len(content.split()) < min_words:
        return None
    vid = str(var.get("variant_id") or f"v{vi}")
    st = str(sec_data.get("type") or "")
    return {"text": content, "source": f"injection:registry:{st}:{vid}"}


def _find_story_content(
    topic: str,
    persona_id: str,
    teacher_id: Optional[str],
    chapter_index: int,
    section_index: int,
    seed: str,
    repo_root: Path,
) -> Optional[Dict[str, str]]:
    if teacher_id:
        tid = teacher_id.strip()
        teacher_stories = (
            repo_root
            / "SOURCE_OF_TRUTH"
            / "teacher_banks"
            / tid
            / "approved_atoms"
            / "STORY"
        )
        if teacher_stories.is_dir():
            atoms = sorted(teacher_stories.glob("*.yaml")) + sorted(teacher_stories.glob("*.yml"))
            if atoms:
                idx = _hash_pick(f"{seed}:story:{chapter_index}", len(atoms))
                data = _load_yaml(atoms[idx])
                text = ""
                if isinstance(data, dict):
                    text = str(data.get("body") or data.get("content") or "").strip()
                if text and _story_words(text) > 20:
                    return {
                        "text": text,
                        "source": f"injection:teacher_story:{atoms[idx].stem}",
                    }

    persona = (persona_id or "").strip()
    top = (topic or "").strip()
    if persona and top:
        persona_story = repo_root / "atoms" / persona / top / "STORY" / "CANONICAL.txt"
        if persona_story.is_file():
            text = persona_story.read_text(encoding="utf-8").strip()
            if text and _story_words(text) > 20:
                return {"text": text, "source": "injection:persona_story"}

        topic_dir = repo_root / "atoms" / persona / top
        if topic_dir.is_dir():
            for engine_dir in sorted(topic_dir.iterdir()):
                if not engine_dir.is_dir() or engine_dir.name.isupper():
                    continue
                canonical = engine_dir / "CANONICAL.txt"
                if canonical.is_file():
                    text = canonical.read_text(encoding="utf-8").strip()
                    if text and _story_words(text) > 20:
                        return {
                            "text": text,
                            "source": f"injection:persona_engine:{engine_dir.name}",
                        }

    reg_hit = _pick_registry_variant_for_slot(
        topic, chapter_index, section_index, seed, repo_root, min_words=20
    )
    if reg_hit:
        return reg_hit

    return None


def _find_exercise_content(
    topic: str,
    persona_id: str,
    teacher_id: Optional[str],
    chapter_index: int,
    section_index: int,
    exercise_phase: Optional[dict],
    seed: str,
    repo_root: Path,
) -> Optional[Dict[str, str]]:
    if exercise_phase:
        exercise_id = str(exercise_phase.get("exercise_id") or "").strip()
        if exercise_id:
            ex_dir = repo_root / "SOURCE_OF_TRUTH" / "exercises_v4" / "approved"
            path = _resolve_approved_exercise_path(exercise_id, ex_dir, repo_root)
            if path is not None:
                data = _load_yaml(path)
                text = _exercise_prose_from_yaml(data)
                if text and len(text.split()) > 10:
                    return {
                        "text": text,
                        "source": f"injection:exercise_journey:{exercise_id}",
                    }

    if teacher_id:
        tid = teacher_id.strip()
        teacher_ex = (
            repo_root
            / "SOURCE_OF_TRUTH"
            / "teacher_banks"
            / tid
            / "approved_atoms"
            / "EXERCISE"
        )
        if teacher_ex.is_dir():
            atoms = sorted(teacher_ex.glob("*.yaml")) + sorted(teacher_ex.glob("*.yml"))
            if atoms:
                idx = _hash_pick(f"{seed}:exercise:{chapter_index}:{section_index}", len(atoms))
                data = _load_yaml(atoms[idx])
                text = ""
                if isinstance(data, dict):
                    text = str(data.get("body") or data.get("content") or "").strip()
                if text and len(text.split()) > 10:
                    return {
                        "text": text,
                        "source": f"injection:teacher_exercise:{atoms[idx].stem}",
                    }

    try:
        from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter

        composed = get_exercise_for_chapter(
            chapter_index - 1,
            topic,
            persona_id or "",
            seed,
        )
        if composed and len(composed.split()) > 10:
            return {"text": composed.strip(), "source": "injection:practice_library"}
    except Exception:
        pass

    reg_hit = _pick_registry_variant_for_slot(
        topic, chapter_index, section_index, seed, repo_root, min_words=10
    )
    if reg_hit:
        return reg_hit

    return None


def resolve_injections(
    template_text: str,
    *,
    chapter_index: int,
    section_index: int,
    section_type: str,
    topic: str,
    persona_id: str,
    teacher_id: Optional[str],
    exercise_phase: Optional[dict],
    seed: str,
    repo_root: Optional[Path] = None,
) -> dict:
    """
    Replace [STORY_INJECTION_POINT] / [EXERCISE_INJECTION_POINT] with real content.

    Priority — story: teacher STORY atoms → persona STORY / engine CANONICAL → registry
    variant for the same chapter/section row. Exercise: journey-approved YAML → teacher
    EXERCISE → practice library → registry variant for that row.

    Returns:
        text, injections_resolved, injections_failed, sources_used
    """
    del section_type  # reserved for beat-aware routing (layer vs registry type)
    root = repo_root or REPO_ROOT
    result: Dict[str, Any] = {
        "text": template_text,
        "injections_resolved": [],
        "injections_failed": [],
        "sources_used": [],
    }

    if _STORY_MARK in result["text"]:
        story = _find_story_content(
            topic, persona_id, teacher_id, chapter_index, section_index, seed, root
        )
        if story:
            result["text"] = result["text"].replace(_STORY_MARK, story["text"])
            result["injections_resolved"].append("STORY_INJECTION_POINT")
            result["sources_used"].append(story["source"])
        else:
            result["text"] = result["text"].replace(_STORY_MARK, "")
            result["injections_failed"].append("STORY_INJECTION_POINT")

    if _EX_MARK in result["text"]:
        exercise = _find_exercise_content(
            topic,
            persona_id,
            teacher_id,
            chapter_index,
            section_index,
            exercise_phase,
            seed,
            root,
        )
        if exercise:
            result["text"] = result["text"].replace(_EX_MARK, exercise["text"])
            result["injections_resolved"].append("EXERCISE_INJECTION_POINT")
            result["sources_used"].append(exercise["source"])
        else:
            result["text"] = result["text"].replace(_EX_MARK, "")
            result["injections_failed"].append("EXERCISE_INJECTION_POINT")

    result["text"] = _strip_known_marks(result["text"])
    return result


def clear_exercise_registry_cache() -> None:
    """Test helper — reset lazy registry cache."""
    _EXERCISE_REGISTRY_BY_ROOT.clear()
