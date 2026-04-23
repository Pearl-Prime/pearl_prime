"""Resolve injection markers in legacy template text.

Markers handled:
  [STORY_INJECTION_POINT]       — 3rd-person named-character arc story
  [EXERCISE_INJECTION_POINT]    — Pearl Prime structured exercise
  [SCENE_INJECTION_POINT]       — 2nd-person "you" situational scene (reader sees themselves)
  [INTEGRATION_SCENE_POINT]     — 2nd-person release scene, placed after exercise sections

Variety enforcement: pass a BookSlotTracker instance through compose_section_packet()
→ resolve_injections() to enforce collision-family dedup and no-repeat variant selection
across all 12 chapters of a single book assembly. See docs/RECOGNITION_BANK_SPEC.md.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from phoenix_v4.planning.registry_resolver import _deterministic_index, _load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_STORY_MARK = "[STORY_INJECTION_POINT]"
_EX_MARK = "[EXERCISE_INJECTION_POINT]"
_SCENE_MARK = "[SCENE_INJECTION_POINT]"
_INTEG_SCENE_MARK = "[INTEGRATION_SCENE_POINT]"

# Scene bank paths (relative to repo root).
_SCENE_RECOGNITION_BANK = "config/content_banks/anxiety_genz_scene_recognition_bank.yaml"
_SCENE_ANCHOR_BANK = "config/content_banks/global_scene_anchor_bank.yaml"

# Exercise registry cache — kept for clear_exercise_registry_cache() test helper.
_EXERCISE_REGISTRY_BY_ROOT: Dict[str, Dict[str, Any]] = {}

# Scene bank cache — loaded once per repo_root.
_SCENE_BANK_CACHE: Dict[str, List[Dict[str, Any]]] = {}


class BookSlotTracker:
    """
    Book-level variety tracker for content bank slot picks.

    Attach one instance per book assembly run (one tracker for all 12 chapters).
    Pass it to resolve_injections() via the `slot_tracker` parameter.

    Enforces two rules within a single book:
      1. Hard no-repeat: a variant_id already used in this book cannot be picked again.
      2. Collision-family spread: when choosing between eligible variants, prefer those
         whose collision_family has been used least so far in this slot_type.

    Fallback: if all variants have already been used (e.g. pool < chapter count),
    falls back to the least-used-family variant to avoid silent content gap.

    Usage (pilot script):
        tracker = BookSlotTracker()
        for ch in chapters:
            for sec in sections:
                compose_section_packet(..., slot_tracker=tracker)
    """

    def __init__(self) -> None:
        # variant_id → number of times used (non-zero = already used)
        self._used_ids: Set[str] = set()
        # collision_family → count of uses across entire book
        self._family_counts: Dict[str, int] = defaultdict(int)
        # slot_type → [ordered list of collision families used]
        self._slot_history: Dict[str, List[str]] = defaultdict(list)

    def pick(
        self,
        variants: List[Dict[str, Any]],
        seed: str,
        slot_type: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Deterministically pick a variant with variety enforcement.

        Selection priority:
          1. Variants whose variant_id has not been used in this book (hard exclude used IDs).
          2. Among eligible variants, prefer those with the least-used collision_family.
          3. Within same family-count tier, use SHA256-based deterministic offset from
             hash(seed) so the same book always produces the same sequence.
          4. Fallback: if all variant_ids are used, pick least-used family (no hard exclude).

        Returns the chosen variant dict, or None if variants is empty.
        """
        if not variants:
            return None

        start_idx = _deterministic_index(seed, len(variants))

        # ── Pass 1: exclude already-used IDs ───────────────────────────────────
        eligible = [
            (i, v) for i, v in enumerate(variants)
            if str(v.get("variant_id") or i) not in self._used_ids
        ]

        if not eligible:
            # All variants exhausted — fall back to full pool, soft-prefer least-used family
            eligible = list(enumerate(variants))

        # ── Pass 2: score by collision_family usage count + deterministic tiebreak ──
        n_variants = len(variants)  # capture once; _score is called N·logN times per pick

        def _score(idx_v: tuple) -> tuple:
            i, v = idx_v
            fam = str(v.get("collision_family") or "")
            fam_count = self._family_counts.get(fam, 0) if fam else 0
            # deterministic tiebreak: distance from start_idx (closer = same seed intention)
            det_offset = (i - start_idx) % n_variants
            return (fam_count, det_offset)

        eligible.sort(key=_score)
        chosen_i, chosen_v = eligible[0]

        # ── Record the pick ────────────────────────────────────────────────────
        vid = str(chosen_v.get("variant_id") or chosen_i)
        fam = str(chosen_v.get("collision_family") or "")
        self._used_ids.add(vid)
        if fam:
            self._family_counts[fam] += 1
            if slot_type:
                self._slot_history[slot_type].append(fam)

        return chosen_v

    def record(
        self,
        variant_id: str,
        collision_family: str = "",
        slot_type: str = "",
    ) -> None:
        """Manually record a pick that happened outside pick() (e.g. story_planner picks)."""
        self._used_ids.add(variant_id)
        if collision_family:
            self._family_counts[collision_family] += 1
            if slot_type:
                self._slot_history[slot_type].append(collision_family)

    def families_used(self, slot_type: str = "") -> List[str]:
        """Return ordered list of collision families used for a slot_type."""
        return list(self._slot_history.get(slot_type, []))

    def variant_used(self, variant_id: str) -> bool:
        return variant_id in self._used_ids


def _hash_pick(seed: str, n: int) -> int:
    return _deterministic_index(seed, n)


def _strip_known_marks(text: str) -> str:
    return (
        text
        .replace(_STORY_MARK, "")
        .replace(_EX_MARK, "")
        .replace(_SCENE_MARK, "")
        .replace(_INTEG_SCENE_MARK, "")
    )


# Locale token fallbacks — loaded lazily from config/content_banks/loc_var_render.yaml
# so packet-stage output matches book_renderer resolution (one source of truth).
# Covers both flat tokens ({street_name}) and dotted tokens ({location.digital_space}).
_LOCALE_FALLBACKS_CACHE: Optional[Dict[str, str]] = None

# Hardcoded last-resort fallbacks used if loc_var_render.yaml is missing/unreadable.
_LOCALE_HARDCODED = {
    "street_name":              "the street below",
    "weather_detail":           "soft daylight along the sill",
    "transit_line":             "the train",
    "location.digital_space":   "a quiet moment",
    "location.daily_space":     "the kitchen table",
    "location.high_stakes_space": "the meeting room",
    "location.learning_space":  "the quiet room",
    "location.memory_space":    "the place where they used to be",
    "location.social_gathering": "the gathering",
}


def _load_locale_fallbacks() -> Dict[str, str]:
    global _LOCALE_FALLBACKS_CACHE
    if _LOCALE_FALLBACKS_CACHE is not None:
        return _LOCALE_FALLBACKS_CACHE
    path = REPO_ROOT / "config" / "content_banks" / "loc_var_render.yaml"
    merged = dict(_LOCALE_HARDCODED)
    if path.is_file():
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            merged.update({str(k): str(v) for k, v in (data.get("fallbacks") or {}).items()})
        except Exception:
            pass
    _LOCALE_FALLBACKS_CACHE = merged
    return merged


import re as _re
_LOC_SENTENCE_START_RE = _re.compile(r'(^|[.!?]\s+|\n\s*)(\{[A-Za-z_][A-Za-z_0-9.]*\})')


def _fill_locale_tokens(text: str) -> str:
    """Replace locale tokens with sentence-start capitalization.

    Handles flat tokens ({street_name}), dotted tokens ({location.digital_space}),
    and title-case variants ({Weather_detail}). Tokens at sentence start are
    capitalized so ". {street_name}" → ". The street below" (not ". the street below").
    """
    tokens = _load_locale_fallbacks()

    def _lookup(name: str) -> Optional[str]:
        if name in tokens:
            return tokens[name]
        # title-case variant → lowercase lookup
        alt = name[0].lower() + name[1:]
        return tokens.get(alt)

    def _cap_start(m) -> str:
        prefix, token_braced = m.group(1), m.group(2)
        name = token_braced[1:-1]
        value = _lookup(name)
        if not value:
            return m.group(0)
        return f"{prefix}{value[0].upper()}{value[1:]}"

    text = _LOC_SENTENCE_START_RE.sub(_cap_start, text)

    # Mid-sentence replacements (lowercase value).
    for name, value in tokens.items():
        text = text.replace(f"{{{name}}}", value)
        if name and name[0].islower():
            title = name[0].upper() + name[1:]
            text = text.replace(f"{{{title}}}", value)
    return text


# ── Mechanism token resolver ──────────────────────────────────────────────────
# Fills {selected_mechanism} and {selected_signal} in REFLECTION atoms.
# Source: config/content_banks/selected_mechanism_resolver.yaml
# Picks deterministically by (persona, topic, token, chapter_index) so the
# same book always gets the same mechanism; different seeds produce variety.

_MECHANISM_RESOLVER_PATH = "config/content_banks/selected_mechanism_resolver.yaml"
_mechanism_resolver_cache: Optional[Dict[str, Any]] = None


def _load_mechanism_resolver(repo_root: Path) -> Dict[str, Any]:
    global _mechanism_resolver_cache
    if _mechanism_resolver_cache is not None:
        return _mechanism_resolver_cache
    path = repo_root / _MECHANISM_RESOLVER_PATH
    if not path.is_file():
        _mechanism_resolver_cache = {}
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _mechanism_resolver_cache = data.get("resolver") or {}
    except Exception:
        _mechanism_resolver_cache = {}
    return _mechanism_resolver_cache


def _fill_mechanism_tokens(
    text: str,
    persona_id: str,
    topic: str,
    seed: str,
    repo_root: Path,
) -> str:
    """Replace {selected_mechanism} and {selected_signal} using the resolver config.

    Only fires when both tokens exist in text AND a resolver entry exists for
    this persona × topic. Silently skips if config is missing (text passes
    through unchanged; _strip_placeholders will warn about leftover tokens).
    """
    if "{selected_mechanism}" not in text and "{selected_signal}" not in text:
        return text

    resolver = _load_mechanism_resolver(repo_root)
    persona_data = resolver.get(persona_id, {})
    topic_data = persona_data.get(topic, {})
    if not topic_data:
        return text  # no resolver entry — leave for _strip_placeholders to flag

    for token_name in ("selected_mechanism", "selected_signal"):
        if f"{{{token_name}}}" not in text:
            continue
        pool = topic_data.get(token_name) or []
        if not pool:
            continue
        pick_seed = f"{seed}:{persona_id}:{topic}:{token_name}"
        idx = _deterministic_index(pick_seed, len(pool))
        text = text.replace(f"{{{token_name}}}", pool[idx])

    return text


def _story_words(text: str) -> int:
    return len(text.split()) if text else 0


# Arc position names ordered by book phase (4-chapter bands for a 12-chapter book).
_ARC_POSITIONS = ("recognition", "mechanism_proof", "turning_point", "embodiment")

# Default engine search order — first engine with atoms wins.
_DEFAULT_STORY_ENGINES = [
    "overwhelm", "shame", "spiral", "comparison", "false_alarm", "grief", "watcher"
]


def _chapter_to_arc_position(chapter_index: int) -> str:
    """Map 1-based chapter index to arc_position name using 4-chapter bands."""
    phase = max(0, min((chapter_index - 1) // 3, len(_ARC_POSITIONS) - 1))
    return _ARC_POSITIONS[phase]


def _find_story_atoms_content(
    persona_id: str,
    topic: str,
    chapter_index: int,
    seed: str,
    repo_root: Path,
) -> Optional[Dict[str, str]]:
    """Load a rich story atom from story_atoms/{persona}/anchored/{topic}/{engine}/{arc_pos}/micro/.

    Character persistence: all chapters in the same 4-chapter band use the same variant
    index (same 'character'), giving 2-4 characters per book without cross-call state.
    """
    persona = (persona_id or "").strip()
    top = (topic or "").strip()
    if not persona or not top:
        return None

    arc_pos = _chapter_to_arc_position(chapter_index)
    # Strip the per-section `:inject:{ch}:{sec}` suffix added by the composer so that
    # every SCENE in the same 4-chapter band picks the same character variant.
    book_seed = seed.split(":inject:")[0] if ":inject:" in seed else seed
    phase = max(0, min((chapter_index - 1) // 3, len(_ARC_POSITIONS) - 1))
    char_seed = f"{book_seed}:char_phase:{phase}"

    base = repo_root / "story_atoms" / persona / "anchored" / top
    if not base.is_dir():
        return None

    for engine in _DEFAULT_STORY_ENGINES:
        micro_dir = base / engine / arc_pos / "micro"
        if not micro_dir.is_dir():
            continue
        files = sorted(micro_dir.glob("*.txt"))
        if not files:
            continue
        idx = _deterministic_index(char_seed, len(files))
        text = files[idx].read_text(encoding="utf-8").strip()
        if text and _story_words(text) > 20:
            return {
                "text": text,
                "source": f"injection:story_atoms:{engine}:{arc_pos}:{files[idx].stem}",
            }

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
    # story_atoms is the primary character-arc narrative system: named characters
    # (Tariq, Marcus, Zoë, Maya) carry across 4-chapter phase bands. Teacher STORY
    # bank is a fallback — teachers inject their voice via the teacher_atom enrichment
    # layer, not by overriding the protagonist character arc.
    atoms_hit = _find_story_atoms_content(persona_id, topic, chapter_index, seed, repo_root)
    if atoms_hit:
        return atoms_hit

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


def _load_scene_bank(
    topic: str,
    persona_id: str,
    repo_root: Path,
    bank_type: str = "recognition",
) -> List[Dict[str, Any]]:
    """Load scene variants from the topic-persona bank or the global anchor bank.

    bank_type: "recognition" → anxiety_genz_scene_recognition_bank.yaml
               "anchor"      → global_scene_anchor_bank.yaml
    """
    cache_key = f"{repo_root}:{topic}:{persona_id}:{bank_type}"
    if cache_key in _SCENE_BANK_CACHE:
        return _SCENE_BANK_CACHE[cache_key]

    variants: List[Dict[str, Any]] = []

    if bank_type == "recognition":
        bank_path = repo_root / _SCENE_RECOGNITION_BANK
        if bank_path.is_file():
            try:
                raw = yaml.safe_load(bank_path.read_text(encoding="utf-8")) or {}
                top = (topic or "").strip().lower()
                per = (persona_id or "").strip().lower()
                # Try topic+persona key first (e.g. anxiety_genz_scene_recognition)
                for key, val in raw.items():
                    if not isinstance(val, list):
                        continue
                    for item in val:
                        if not isinstance(item, dict):
                            continue
                        ta = item.get("topic_allowlist") or []
                        pa = item.get("persona_allowlist") or []
                        # Accept if lists are empty (global) or topic/persona matches.
                        topic_ok = not ta or top in [t.lower() for t in ta]
                        persona_ok = not pa or per in [p.lower() for p in pa]
                        if topic_ok and persona_ok:
                            variants.append(item)
            except Exception:
                pass

    if bank_type == "anchor" or not variants:
        bank_path = repo_root / _SCENE_ANCHOR_BANK
        if bank_path.is_file():
            try:
                raw = yaml.safe_load(bank_path.read_text(encoding="utf-8")) or {}
                # Global bank may be a flat list or dict with a list value.
                if isinstance(raw, list):
                    variants = raw
                else:
                    for val in raw.values():
                        if isinstance(val, list):
                            variants.extend(val)
                            break
            except Exception:
                pass

    _SCENE_BANK_CACHE[cache_key] = variants
    return variants


def _find_scene_content(
    topic: str,
    persona_id: str,
    seed: str,
    repo_root: Path,
    bank_type: str = "recognition",
    slot_tracker: Optional["BookSlotTracker"] = None,
) -> Optional[Dict[str, str]]:
    """Pick a 2nd-person scene atom from the appropriate bank.

    If ``slot_tracker`` is provided, uses variety-aware selection:
    - Hard-excludes variant_ids already used in this book.
    - Prefers variants from least-used collision_family.
    Falls back to plain SHA256 pick when no tracker is present.

    Returns dict with 'text' and 'source', or None if no bank found.
    """
    variants = _load_scene_bank(topic, persona_id, repo_root, bank_type)
    if not variants:
        return None

    slot_type = f"scene_{bank_type}"
    if slot_tracker is not None:
        item = slot_tracker.pick(variants, f"{seed}:scene:{bank_type}", slot_type=slot_type)
        if item is None:
            return None
    else:
        idx = _deterministic_index(f"{seed}:scene:{bank_type}", len(variants))
        item = variants[idx]

    body = str(item.get("body") or item.get("text") or "").strip()
    if not body or len(body.split()) < 5:
        return None
    vid = str(item.get("variant_id") or "")
    return {"text": body, "source": f"injection:scene_{bank_type}:{vid}"}


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
            return {"text": composed.strip(), "source": "injection:practice_library_311"}
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
    story_schedule: Optional[Any] = None,
    slot_tracker: Optional["BookSlotTracker"] = None,
) -> dict:
    """
    Replace [STORY_INJECTION_POINT] / [EXERCISE_INJECTION_POINT] with real content.

    Priority — story:
      1. story_schedule (pre-planned full-arch stories from StoryPlanner)
      2. story_atoms/ per-call fallback (arc-position aware, character persistent)
      3. teacher STORY bank
      4. persona STORY / engine CANONICAL
      5. registry variant

    Exercise: teacher EXERCISE atoms → practice_library_311 → registry variant.

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
        story = None
        # 1. Pre-planned story schedule (highest priority for character arc continuity).
        if story_schedule is not None:
            slot = story_schedule.get(chapter_index, section_index)
            if slot is not None and slot.text and len(slot.text.split()) > 20:
                story = {"text": slot.text, "source": slot.source}
        # 2. Fallback: per-call story_atoms / teacher bank / persona atoms / registry.
        if story is None:
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

    if _SCENE_MARK in result["text"]:
        # 2nd-person recognition scene: reader sees themselves in the situation.
        # Uses the topic+persona scene bank; falls back to global anchor bank.
        scene = _find_scene_content(
            topic, persona_id, seed, root,
            bank_type="recognition",
            slot_tracker=slot_tracker,
        )
        if scene:
            result["text"] = result["text"].replace(_SCENE_MARK, scene["text"])
            result["injections_resolved"].append("SCENE_INJECTION_POINT")
            result["sources_used"].append(scene["source"])
        else:
            result["text"] = result["text"].replace(_SCENE_MARK, "")
            result["injections_failed"].append("SCENE_INJECTION_POINT")

    if _INTEG_SCENE_MARK in result["text"]:
        # Post-exercise integration scene: a moment of release or noticing.
        # Uses global anchor bank (neutral, body-based, no topic-specific trigger).
        integ = _find_scene_content(
            topic, persona_id, f"{seed}:post_ex", root,
            bank_type="anchor",
            slot_tracker=slot_tracker,
        )
        if integ:
            result["text"] = result["text"].replace(_INTEG_SCENE_MARK, integ["text"])
            result["injections_resolved"].append("INTEGRATION_SCENE_POINT")
            result["sources_used"].append(integ["source"])
        else:
            result["text"] = result["text"].replace(_INTEG_SCENE_MARK, "")
            result["injections_failed"].append("INTEGRATION_SCENE_POINT")

    result["text"] = _strip_known_marks(result["text"])
    # Fill mechanism tokens ({selected_mechanism}, {selected_signal}) before locale tokens.
    result["text"] = _fill_mechanism_tokens(
        result["text"], persona_id, topic, seed, root
    )
    result["text"] = _fill_locale_tokens(result["text"])
    return result


def clear_exercise_registry_cache() -> None:
    """Test helper — reset lazy registry cache."""
    _EXERCISE_REGISTRY_BY_ROOT.clear()
    _SCENE_BANK_CACHE.clear()
