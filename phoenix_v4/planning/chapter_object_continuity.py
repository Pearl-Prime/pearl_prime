"""
12-shape object/character continuity selector + validation gates.

Authority: docs/12SHAPE_CONTINUITY_WIRING.md
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLAN_DIR = REPO_ROOT / "config" / "source_of_truth" / "twelve_shape_chapter_plans"

BANK_EMPTY_PREFIX = "[BANK EMPTY:"
CONTINUITY_CONNECTIVE_SLOTS = frozenset(
    {"HOOK", "SCENE", "PIVOT", "INTEGRATION", "TAKEAWAY", "THREAD"}
)

_OBJECT_ALIASES: dict[str, tuple[str, ...]] = {
    "after_send_reply_anxiety": (
        "after-send",
        "after_send",
        "reply anxiety",
        "post-send",
        "message sent",
        "message delivered",
        "11pm",
        "11:47",
        "phone face-down",
        "Slack",
    ),
}

_FORBIDDEN_OBJECT_DRIFT = (
    r"one-on-one",
    r"demo morning",
    r"lunch block",
)


_VALID_DOCTRINE_NUMS = frozenset(range(1, 6))


def validate_twelve_shape_plan(chapters: list[dict[str, Any]]) -> list[str]:
    """Fail-closed planner reconciliation checks for 12-shape flagship builds."""
    errors: list[str] = []
    if len(chapters) != 12:
        errors.append(f"expected 12 chapters, got {len(chapters)}")
    characters: set[str] = set()
    for entry in chapters:
        if not isinstance(entry, dict):
            continue
        ch = int(entry.get("chapter") or 0)
        char = str(entry.get("character") or "").strip()
        if char:
            characters.add(char)
        if not str(entry.get("exercise_id") or "").strip():
            errors.append(f"ch{ch}: missing exercise_id (5-layer slot required)")
        raw_doc = str(entry.get("doctrine_id") or "").strip()
        m = re.match(r"COMPOSITE_DOCTRINE v(\d{2})", raw_doc, re.I)
        if m and int(m.group(1)) not in _VALID_DOCTRINE_NUMS:
            errors.append(f"ch{ch}: phantom doctrine {raw_doc} (pool is v01–v05)")
    if len(characters) > 1:
        errors.append(
            f"character soup: {sorted(characters)} — flagship requires one anchored character"
        )
    return errors


def assert_twelve_shape_plan(chapters: list[dict[str, Any]]) -> None:
    errors = validate_twelve_shape_plan(chapters)
    if errors:
        raise AssertionError("twelve_shape plan invalid: " + "; ".join(errors))


@dataclass
class ChapterContinuityContext:
    chapter_number: int  # 1-based
    character: str
    anxiety_object: str
    doctrine_id: str = ""
    exercise_id: str = ""
    angle_id: str = ""
    practice_target: str = ""
    doctrine_target: str = ""
    forbidden_names: tuple[str, ...] = ("Hana", "Min", "Yuki")
    expected_doctrine_snippet: str = ""


@dataclass
class ContinuityGateResult:
    name: str
    passed: bool
    detail: str


@dataclass
class ContinuityBeat:
    slot: str
    atom_id: str
    prose: str
    story_arc: str = ""


def is_twelve_shape_continuity_active(spine_context: Optional[dict[str, Any]]) -> bool:
    if not spine_context:
        return False
    if spine_context.get("twelve_shape_continuity"):
        return True
    return bool(spine_context.get("chapter_continuity_plan"))


def _plan_path(persona_id: str, topic_id: str) -> Path:
    return PLAN_DIR / f"{persona_id}_{topic_id}.yaml"


def load_chapter_continuity_plan(
    persona_id: str,
    topic_id: str,
    repo_root: Optional[Path] = None,
) -> list[dict[str, Any]]:
    path = (repo_root or REPO_ROOT) / _plan_path(persona_id, topic_id).relative_to(REPO_ROOT)
    if not path.exists():
        return []
    try:
        import yaml
    except ImportError:
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    chapters = data.get("chapters") or []
    return [c for c in chapters if isinstance(c, dict)]


def chapter_context_from_spine(
    spine_context: dict[str, Any],
    chapter_index0: int,
) -> Optional[ChapterContinuityContext]:
    plan = spine_context.get("chapter_continuity_plan")
    if not isinstance(plan, list) or not plan:
        return None
    ch_num = chapter_index0 + 1
    entry = next((c for c in plan if int(c.get("chapter") or 0) == ch_num), None)
    if not entry:
        return None
    return ChapterContinuityContext(
        chapter_number=ch_num,
        character=str(entry.get("character") or "").strip(),
        anxiety_object=str(entry.get("object") or entry.get("anxiety_object") or "").strip(),
        doctrine_id=str(entry.get("doctrine_id") or "").strip(),
        exercise_id=str(entry.get("exercise_id") or "").strip(),
        angle_id=str(entry.get("angle_id") or "").strip(),
        practice_target=str(entry.get("practice_target") or "").strip(),
        doctrine_target=str(entry.get("doctrine_target") or "").strip(),
        expected_doctrine_snippet=str(entry.get("expected_doctrine_snippet") or "").strip(),
    )


def _meta_object(atom: dict) -> str:
    meta = atom.get("metadata") or {}
    if not isinstance(meta, dict):
        return ""
    return str(meta.get("object") or "").strip()


def _meta_character(atom: dict) -> str:
    meta = atom.get("metadata") or {}
    if not isinstance(meta, dict):
        return ""
    raw = meta.get("character")
    if raw is None:
        return ""
    return str(raw).strip()


def _object_matches(atom_object: str, chapter_object: str) -> bool:
    if not atom_object or not chapter_object:
        return False
    if atom_object == chapter_object:
        return True
    aliases = _OBJECT_ALIASES.get(chapter_object, ())
    combined = f"{atom_object} {chapter_object}".lower()
    return any(a.lower() in combined for a in aliases)


def filter_connective_pool(
    pool: list[dict],
    slot: str,
    ctx: ChapterContinuityContext,
) -> list[dict]:
    """Filter persona atoms to object/character continuity matches."""
    if slot not in CONTINUITY_CONNECTIVE_SLOTS:
        return pool
    tagged = [a for a in pool if _meta_object(a)]
    if not tagged:
        return pool
    out: list[dict] = []
    for atom in pool:
        obj = _meta_object(atom)
        if not _object_matches(obj, ctx.anxiety_object):
            continue
        if slot == "SCENE":
            ch = _meta_character(atom)
            if ctx.character and ch and ch != ctx.character:
                continue
        out.append(atom)
    if slot == "SCENE" and not out:
        # Fallback: 2nd-person SCENE with matching object (character null/empty)
        for atom in pool:
            obj = _meta_object(atom)
            if not _object_matches(obj, ctx.anxiety_object):
                continue
            ch = _meta_character(atom)
            if ch:
                continue
            out.append(atom)
    return out


def continuity_bank_empty(slot: str, ctx: ChapterContinuityContext) -> str:
    char = ctx.character or "null"
    return f"{BANK_EMPTY_PREFIX} {slot} — needs object={ctx.anxiety_object} character={char}]"


def pick_continuity_index(pool: list[dict], seed_key: str) -> int:
    if not pool:
        return 0
    h = hashlib.sha256(seed_key.encode()).hexdigest()
    return int(h[:8], 16) % len(pool)


def pick_continuity_atom(
    pool: list[dict],
    slot: str,
    ctx: ChapterContinuityContext,
    seed_key: str,
) -> Optional[dict]:
    filtered = filter_connective_pool(pool, slot, ctx)
    if not filtered:
        return None
    idx = pick_continuity_index(filtered, seed_key)
    return filtered[idx]


def assert_chapter_continuity(
    beats: list[ContinuityBeat],
    ctx: ChapterContinuityContext,
    *,
    require_no_placeholders: bool = True,
) -> None:
    results = run_continuity_gates(beats, ctx, require_no_placeholders=require_no_placeholders)
    failures = [r for r in results if not r.passed]
    if failures:
        detail = "; ".join(f"{r.name}: {r.detail}" for r in failures)
        raise AssertionError(f"chapter continuity gates failed: {detail}")


def run_continuity_gates(
    beats: list[ContinuityBeat],
    ctx: ChapterContinuityContext,
    *,
    require_no_placeholders: bool = True,
) -> list[ContinuityGateResult]:
    full = "\n\n".join(
        b.prose.strip()
        for b in beats
        if b.prose and BANK_EMPTY_PREFIX not in b.prose
    )
    results: list[ContinuityGateResult] = []

    forbidden = [n for n in ctx.forbidden_names if re.search(rf"\b{n}\b", full)]
    char_present = bool(ctx.character and re.search(rf"\b{re.escape(ctx.character)}\b", full))
    results.append(
        ContinuityGateResult(
            "ONE CHARACTER",
            char_present and not forbidden,
            f"{ctx.character} present={char_present}; forbidden={forbidden or 'none'}",
        )
    )

    drift = [p for p in _FORBIDDEN_OBJECT_DRIFT if re.search(p, full, re.I)]
    alias_hits = sum(
        1 for a in _OBJECT_ALIASES.get(ctx.anxiety_object, ()) if re.search(a, full, re.I)
    )
    results.append(
        ContinuityGateResult(
            "ONE OBJECT",
            not drift and alias_hits >= 3,
            f"alias_hits={alias_hits}; drift={drift or 'none'}",
        )
    )

    scene = next((b for b in beats if b.slot == "SCENE"), None)
    rec = next((b for b in beats if b.story_arc == "recognition"), None)
    if scene and rec:
        sim = SequenceMatcher(None, scene.prose.lower(), rec.prose.lower()).ratio()
        dup = [
            p
            for p in ("four minutes", "typo in the second paragraph", "11:47pm")
            if p in scene.prose.lower() and p in rec.prose.lower()
        ]
        results.append(
            ContinuityGateResult(
                "NO DUPLICATION",
                sim < 0.45 and not dup,
                f"similarity={sim:.2f}; shared={dup or 'none'}",
            )
        )

    if ctx.expected_doctrine_snippet:
        has_doc = ctx.expected_doctrine_snippet.lower() in full.lower()
        results.append(
            ContinuityGateResult(
                "ONE DOCTRINE",
                has_doc,
                f"expected snippet present={has_doc}",
            )
        )

    if ctx.exercise_id:
        has_ex = any(b.slot == "EXERCISE" and ctx.exercise_id in b.atom_id for b in beats)
        results.append(
            ContinuityGateResult("PRACTICE FIT", has_ex, f"exercise={ctx.exercise_id} present={has_ex}")
        )

    integration = next((b for b in beats if b.slot == "INTEGRATION"), None)
    if ctx.anxiety_object == "after_send_reply_anxiety" and integration:
        fit = "11pm" in integration.prose.lower() and "slack" in integration.prose.lower()
        results.append(
            ContinuityGateResult(
                "INTEGRATION FIT",
                fit,
                "11pm Slack-off" if fit else "missing integration anchor",
            )
        )

    angle = next((b for b in beats if b.slot == "ANGLE_DEFINITION"), None)
    thread = next((b for b in beats if b.slot == "THREAD"), None)
    if angle and thread:
        seeded = bool(
            re.search(r"tomorrow|monday|sunday", angle.prose, re.I)
            and re.search(r"sunday|monday", thread.prose, re.I)
        )
        results.append(
            ContinuityGateResult(
                "THREAD SEEDING",
                seeded,
                "ANGLE→THREAD seed ok" if seeded else "seed missing",
            )
        )

    if require_no_placeholders:
        gaps = [b.slot for b in beats if BANK_EMPTY_PREFIX in (b.prose or "")]
        results.append(
            ContinuityGateResult(
                "NO PLACEHOLDERS",
                not gaps,
                f"empty slots={gaps or 'none'}",
            )
        )

    results.append(
        ContinuityGateResult(
            "NO SCAFFOLDING",
            not re.search(r"\[SLOT:|atom HOOK v|angle journey", full, re.I),
            "reader prose clean",
        )
    )
    return results
