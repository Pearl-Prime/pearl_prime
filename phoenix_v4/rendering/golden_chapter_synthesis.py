"""
Golden-chapter synthesis layer (spine / enrichment path).

Selected atoms and registry depth modules are *inputs*. This module aggregates
slot bodies into backbone narrative roles, then calls ``compose_chapter_prose``
so the chapter reads as authored argument flow—not a linear fragment stack.

Beat model authority: ``docs/GOLDEN_CHAPTER_WORKFLOW.md`` (derived from the
20-title corpus in ``docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md`` +
``docs/BESTSELLER_GAP_AUDIT.md`` §research scope).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from phoenix_v4.planning.enrichment_select import EnrichedChapter, EnrichedSlot

# Canonical beat ids (stable API for reports and tests)
BEAT_RECOGNITION_HOOK = "recognition_hook"
BEAT_EMBODIED_SCENE = "embodied_scene"
BEAT_HIDDEN_MECHANISM = "hidden_mechanism"
BEAT_STORY_PROOF = "story_proof"
BEAT_AHA_TURN = "aha_turn"
BEAT_CONCRETE_PRACTICE = "concrete_practice"
BEAT_PERMISSION = "permission"
BEAT_FORWARD_THREAD = "forward_thread"

GOLDEN_BEATS: tuple[str, ...] = (
    BEAT_RECOGNITION_HOOK,
    BEAT_EMBODIED_SCENE,
    BEAT_HIDDEN_MECHANISM,
    BEAT_STORY_PROOF,
    BEAT_AHA_TURN,
    BEAT_CONCRETE_PRACTICE,
    BEAT_PERMISSION,
    BEAT_FORWARD_THREAD,
)

_PLACEHOLDER_LINE = re.compile(r"^\[(?:Placeholder|Missing|Silence|CONTENT GAP)", re.I)
# Leakage audit: any occurrence fails (not only line-anchored --- / headers).
_ARTIFACT_PATTERN_DEFS: tuple[tuple[str, str], ...] = (
    ("content_gap", r"\[CONTENT GAP"),
    ("raw_markdown_dash_run", r"---"),
    ("slot_section_header", r"##\s+(HOOK|SCENE|STORY|REFLECTION|PIVOT|EXERCISE|INTEGRATION|THREAD|TAKEAWAY)\b"),
    ("unresolved_curly_placeholder", r"\{[A-Za-z_][A-Za-z0-9_]*\}"),
    ("python_dict_repr", r"\{['\"][^'\"]+['\"]\s*:\s*"),
    ("python_list_of_dict_repr", r"\[\s*\{\s*['\"]"),
    ("yamlish_family_line", r"^family:"),
    ("yamlish_voice_mode_line", r"^voice_mode:"),
    ("yamlish_mode_line", r"^mode:"),
    ("yamlish_reframe_line", r"^reframe_type:"),
)
# Multiple variant headers mean CANONICAL multi-block dumps leaked into reader text.
_CANONICAL_VARIANT_HEADER_RE = re.compile(r"##\s+(?:HOOK|SCENE)\s+v\d+", re.I)


_ENV_FALLBACK_PATH = Path(__file__).resolve().parents[2] / "config" / "rendering" / "environment_fallback_families.yaml"
_ENV_FAMILY_CACHE: Optional[dict[str, Any]] = None
_BROKEN_STREET_MERGE_RE = re.compile(
    r"(?i)(?:\{street_name\}\s+)?(?:the\s+street\s+)?(?:below\s+)?is\s+there\s+below",
)
_FALLBACK_PLACEHOLDER_RE = re.compile(r"\{weather_detail\}|\{street_name\}|\{transit_line\}")
_PHASE_DEFAULTS: tuple[tuple[int, tuple[str, ...]], ...] = (
    (3, ("object_grounding", "light_ambient", "window_reference")),
    (8, ("object_grounding", "outside_sound", "interior_building")),
    (12, ("interior_building", "window_reference", "outside_sound")),
)
_PLACEHOLDER_FAMILY_MAP: dict[str, tuple[str, ...]] = {
    "{weather_detail}": ("light_ambient",),
    "{street_name}": ("outside_sound", "window_reference"),
    "{transit_line}": ("motion_transit",),
}
_CONTEXT_FAMILY_HINTS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("desk", "keyboard", "screen", "monitor", "cursor"), ("object_grounding", "light_ambient")),
    (("window", "glass", "outside"), ("window_reference", "outside_sound")),
    (("hallway", "elevator", "office", "carpet", "room"), ("interior_building",)),
    (("ride", "doors", "platform", "movement"), ("motion_transit",)),
)
_BROKEN_MERGE_REPAIRS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\bthrough the window through the window\b"), "through the window"),
    (re.compile(r"(?i)\bat the window through the window\b"), "at the window"),
    (re.compile(r"(?i)\bvisible through the glass visible\b"), "visible through the glass"),
)
_DEFAULT_ENV_FALLBACKS: dict[str, Any] = {
    "families": {
        "light_ambient": {
            "entries": [
                {
                    "text": "Muted light settles by the window.",
                    "shape": "sentence",
                    "roots": ["light", "window"],
                    "scene_bias": ["window", "glass"],
                    "intensity": "low",
                },
                {
                    "text": "with muted light along the glass",
                    "shape": "embedded_clause",
                    "roots": ["light", "glass"],
                    "scene_bias": ["window", "glass"],
                    "intensity": "low",
                },
            ],
        },
        "outside_sound": {
            "entries": [
                {
                    "text": "soft outside noise below the window",
                    "shape": "fragment",
                    "roots": ["outside", "sound"],
                    "scene_bias": ["outside", "window"],
                    "intensity": "low",
                },
                {
                    "text": "Outside noise drifts in without detail.",
                    "shape": "sentence",
                    "roots": ["outside", "sound"],
                    "scene_bias": ["outside", "window"],
                    "intensity": "low",
                },
            ],
        },
        "interior_building": {
            "entries": [
                {
                    "text": "The hallway hum stays steady behind the door.",
                    "shape": "sentence",
                    "roots": ["room", "hallway"],
                    "scene_bias": ["hallway", "office"],
                    "intensity": "low",
                }
            ],
        },
        "motion_transit": {
            "entries": [
                {
                    "text": "Route motion keeps a quiet pulse nearby.",
                    "shape": "sentence",
                    "roots": ["movement", "transit"],
                    "scene_bias": ["ride", "platform"],
                    "intensity": "medium",
                }
            ],
        },
        "object_grounding": {
            "entries": [
                {
                    "text": "the cursor waiting where you left it",
                    "shape": "fragment",
                    "roots": ["object", "desk"],
                    "scene_bias": ["desk", "screen"],
                    "intensity": "low",
                },
                {
                    "text": "The mug handle stays warm against your palm.",
                    "shape": "object_led",
                    "roots": ["object", "desk"],
                    "scene_bias": ["desk", "screen"],
                    "intensity": "low",
                },
            ],
        },
        "window_reference": {
            "entries": [
                {
                    "text": "a pale reflection at the glass edge",
                    "shape": "fragment",
                    "roots": ["window", "glass"],
                    "scene_bias": ["window", "outside"],
                    "intensity": "low",
                }
            ],
        },
    }
}


def _load_environment_fallback_families() -> dict[str, Any]:
    global _ENV_FAMILY_CACHE
    if _ENV_FAMILY_CACHE is not None:
        return _ENV_FAMILY_CACHE
    loaded: dict[str, Any] | None = None
    try:
        import yaml  # type: ignore[import-untyped]

        parsed = yaml.safe_load(_ENV_FALLBACK_PATH.read_text(encoding="utf-8"))
        if isinstance(parsed, dict) and isinstance(parsed.get("families"), dict):
            loaded = parsed
    except Exception:
        loaded = None
    if loaded is None:
        loaded = _DEFAULT_ENV_FALLBACKS
    _ENV_FAMILY_CACHE = loaded
    return loaded


def _environment_shape_bonus(shape: str, chapter_index: int) -> float:
    if chapter_index <= 2 and shape in {"object_led", "motion_led"}:
        return 0.7
    if 3 <= chapter_index <= 7 and shape in {"fragment", "sentence"}:
        return 0.5
    if chapter_index >= 8 and shape in {"environment_led", "embedded_clause"}:
        return 0.9
    return 0.0


def _context_family_bias(context: str, chapter_index: int) -> tuple[str, ...]:
    low = context.lower()
    hinted: list[str] = []
    for tokens, families in _CONTEXT_FAMILY_HINTS:
        if any(tok in low for tok in tokens):
            for fam in families:
                if fam not in hinted:
                    hinted.append(fam)
    phase_bias: list[str] = []
    for max_idx, families in _PHASE_DEFAULTS:
        if chapter_index <= max_idx:
            phase_bias.extend(families)
            break
    return tuple(dict.fromkeys(hinted + phase_bias))


@dataclass
class EnvironmentPhraseMemory:
    """Tracks phrase usage across chapter and book scope for anti-reuse."""

    used_phrases_book: set[str] = field(default_factory=set)
    used_phrases_by_chapter: dict[int, set[str]] = field(default_factory=dict)
    family_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    shape_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    root_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    family_usage_by_paragraph: dict[tuple[int, int], dict[str, int]] = field(default_factory=dict)

    def _chapter_map(self, store: dict[int, dict[str, int]], chapter_index: int) -> dict[str, int]:
        return store.setdefault(chapter_index, {})

    def _chapter_phrases(self, chapter_index: int) -> set[str]:
        return self.used_phrases_by_chapter.setdefault(chapter_index, set())

    def register(
        self,
        *,
        chapter_index: int,
        paragraph_index: int,
        family: str,
        shape: str,
        phrase: str,
        roots: list[str],
    ) -> None:
        normalized = phrase.strip().lower()
        if not normalized:
            return
        self.used_phrases_book.add(normalized)
        self._chapter_phrases(chapter_index).add(normalized)
        fam_map = self._chapter_map(self.family_usage_by_chapter, chapter_index)
        fam_map[family] = fam_map.get(family, 0) + 1
        shape_map = self._chapter_map(self.shape_usage_by_chapter, chapter_index)
        shape_map[shape] = shape_map.get(shape, 0) + 1
        root_map = self._chapter_map(self.root_usage_by_chapter, chapter_index)
        for root in roots:
            r = root.strip().lower()
            if not r:
                continue
            root_map[r] = root_map.get(r, 0) + 1
        para_key = (chapter_index, paragraph_index)
        para_map = self.family_usage_by_paragraph.setdefault(para_key, {})
        para_map[family] = para_map.get(family, 0) + 1

    def phrase_seen_book(self, phrase: str) -> bool:
        return phrase.strip().lower() in self.used_phrases_book

    def phrase_seen_chapter(self, chapter_index: int, phrase: str) -> bool:
        return phrase.strip().lower() in self._chapter_phrases(chapter_index)

    def family_count_recent_chapters(self, family: str, chapter_index: int, window: int = 2) -> int:
        total = 0
        for idx in range(max(0, chapter_index - window), chapter_index + 1):
            total += self.family_usage_by_chapter.get(idx, {}).get(family, 0)
        return total

    def root_count_recent_chapters(self, root: str, chapter_index: int, window: int = 3) -> int:
        total = 0
        for idx in range(max(0, chapter_index - window), chapter_index + 1):
            total += self.root_usage_by_chapter.get(idx, {}).get(root, 0)
        return total

    def recent_shape_count(self, shape: str, chapter_index: int, window: int = 1) -> int:
        total = 0
        for idx in range(max(0, chapter_index - window), chapter_index + 1):
            total += self.shape_usage_by_chapter.get(idx, {}).get(shape, 0)
        return total

    def family_seen_adjacent_paragraph(self, family: str, chapter_index: int, paragraph_index: int) -> bool:
        prev_key = (chapter_index, max(0, paragraph_index - 1))
        return self.family_usage_by_paragraph.get(prev_key, {}).get(family, 0) > 0

    def score_candidate(
        self,
        *,
        chapter_index: int,
        paragraph_index: int,
        family: str,
        shape: str,
        phrase: str,
        roots: list[str],
        context_bonus: float,
        family_rank: int,
    ) -> float:
        score = 0.0
        if self.phrase_seen_book(phrase):
            score -= 40.0
        if self.phrase_seen_chapter(chapter_index, phrase):
            score -= 20.0
        family_recent = self.family_count_recent_chapters(family, chapter_index, window=2)
        if family_recent >= 2:
            score -= 5.0 + family_recent
        else:
            score += 2.0 - family_recent
        if self.family_seen_adjacent_paragraph(family, chapter_index, paragraph_index):
            score -= 4.0
        shape_recent = self.recent_shape_count(shape, chapter_index, window=1)
        if shape_recent >= 2:
            score -= 3.5
        else:
            score += 1.4
        score += _environment_shape_bonus(shape, chapter_index)
        for root in roots:
            seen = self.root_count_recent_chapters(root, chapter_index, window=3)
            if seen >= 3:
                score -= 2.2
            elif seen == 0:
                score += 0.8
        score += context_bonus
        score += max(0.0, 2.0 - family_rank)
        return score


def _choose_environment_entry(
    *,
    families_payload: dict[str, Any],
    family_candidates: tuple[str, ...],
    context_text: str,
    chapter_index: int,
    paragraph_index: int,
    memory: EnvironmentPhraseMemory,
) -> dict[str, Any]:
    phase_families = _context_family_bias(context_text, chapter_index)
    seen = set()
    ordered_families: list[str] = []
    for fam in (*family_candidates, *phase_families):
        if fam in families_payload and fam not in seen:
            seen.add(fam)
            ordered_families.append(fam)
    if not ordered_families:
        ordered_families = [f for f in families_payload.keys()]

    best: dict[str, Any] | None = None
    best_score = -10**9
    for family_rank, fam in enumerate(ordered_families):
        entries = families_payload.get(fam, {}).get("entries", [])
        if not isinstance(entries, list):
            continue
        fam_context_bonus = 2.0 if fam in phase_families[:2] else (0.9 if fam in phase_families else 0.0)
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            phrase = str(entry.get("text", "")).strip()
            if not phrase:
                continue
            shape = str(entry.get("shape", "fragment")).strip() or "fragment"
            roots = [str(r).strip().lower() for r in entry.get("roots", []) if str(r).strip()]
            if not roots:
                roots = ["object"]
            score = memory.score_candidate(
                chapter_index=chapter_index,
                paragraph_index=paragraph_index,
                family=fam,
                shape=shape,
                phrase=phrase,
                roots=roots,
                context_bonus=fam_context_bonus,
                family_rank=family_rank,
            )
            if score > best_score:
                best_score = score
                best = {"family": fam, "shape": shape, "text": phrase, "roots": roots}
            elif score == best_score and best is not None:
                tie_key = f"{chapter_index}:{paragraph_index}:{phrase}".encode("utf-8")
                tie_hash = int(hashlib.sha256(tie_key).hexdigest()[:8], 16)
                if tie_hash % 2 == 0:
                    best = {"family": fam, "shape": shape, "text": phrase, "roots": roots}
    if best is None:
        return {
            "family": "object_grounding",
            "shape": "fragment",
            "text": "the cursor waiting where you left it",
            "roots": ["object", "desk"],
        }
    return best


def _resolve_location_placeholders(
    text: str,
    *,
    phrase_memory: EnvironmentPhraseMemory | None = None,
    chapter_index: int = 0,
) -> str:
    """Fill location placeholders with ambient family phrases and anti-reuse memory."""
    t = text or ""
    if not t:
        return t
    chapter_index = max(0, int(chapter_index))
    families_payload = _load_environment_fallback_families().get("families", {})
    if not isinstance(families_payload, dict):
        families_payload = _DEFAULT_ENV_FALLBACKS["families"]
    memory = phrase_memory or EnvironmentPhraseMemory()
    t = _BROKEN_STREET_MERGE_RE.sub("{street_name}", t)
    paragraph_index = 0

    while True:
        match = _FALLBACK_PLACEHOLDER_RE.search(t)
        if not match:
            break
        start = max(0, match.start() - 220)
        end = min(len(t), match.end() + 220)
        context = t[start:end]
        paragraph_index = context.count("\n\n")
        family_candidates = _PLACEHOLDER_FAMILY_MAP.get(match.group(0), ("object_grounding",))
        chosen = _choose_environment_entry(
            families_payload=families_payload,
            family_candidates=family_candidates,
            context_text=context,
            chapter_index=chapter_index,
            paragraph_index=paragraph_index,
            memory=memory,
        )
        memory.register(
            chapter_index=chapter_index,
            paragraph_index=paragraph_index,
            family=str(chosen["family"]),
            shape=str(chosen["shape"]),
            phrase=str(chosen["text"]),
            roots=[str(r) for r in chosen.get("roots", [])],
        )
        t = t[: match.start()] + str(chosen["text"]) + t[match.end() :]

    for pattern, repl in _BROKEN_MERGE_REPAIRS:
        t = pattern.sub(repl, t)
    t = re.sub(r"(?i)\bis there below\b", "is audible outside", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"[ \t]+\.[ \t]+", ". ", t)
    t = re.sub(r"([.!?])\1+", r"\1", t)
    t = re.sub(r"\s+,", ",", t)
    t = re.sub(r"\(\s+", "(", t)
    t = re.sub(r"\s+\)", ")", t)
    return t.strip()



def _extract_single_body_from_depth_canonical_dump(text: str) -> str:
    """
    Depth modules sometimes ship multi-variant CANONICAL dumps (## HOOK v01 --- --- ...).
    Pick one clean prose body for composition; never forward the full dump.
    """
    raw = (text or "").strip()
    if not raw:
        return ""
    if not _CANONICAL_VARIANT_HEADER_RE.search(raw) and "---" not in raw:
        return _resolve_location_placeholders(raw)

    chunks: list[str] = []

    # CANONICAL dumps often arrive as one long inline string:
    # ``## SCENE v01 --- --- body --- ## SCENE v02 --- --- body``.
    # Split on variant headers first so we choose one body instead of forwarding
    # an accidental scene montage.
    variant_parts = re.split(
        r"##\s+(?:HOOK|SCENE|STORY|REFLECTION|PIVOT|EXERCISE|INTEGRATION|THREAD|TAKEAWAY)\s+v\d+\b",
        raw,
        flags=re.I,
    )
    candidate_blob = "\n\n".join(p for p in variant_parts if p.strip())
    if not candidate_blob.strip():
        candidate_blob = raw

    # Drop any leftover line-anchored headers from less compact dumps.
    stripped_headers: list[str] = []
    for line in candidate_blob.splitlines():
        if re.match(r"^\s*##\s+(HOOK|SCENE|STORY|REFLECTION|PIVOT|EXERCISE|INTEGRATION|THREAD|TAKEAWAY)\b", line, re.I):
            continue
        stripped_headers.append(line)
    joined = "\n".join(stripped_headers).strip()
    joined = re.sub(r"\s*-{3,}\s*", "\n\n", joined)
    for block in re.split(r"\n{2,}", joined):
        for piece in re.split(r"\s*-{3,}\s*", block):
            p = piece.strip()
            if len(p) < 40:
                continue
            if re.match(r"^##\s+", p):
                continue
            chunks.append(p)
    if not chunks:
        cleaned = re.sub(r"\s-{3,}\s", " ", raw)
        cleaned = _CANONICAL_VARIANT_HEADER_RE.sub("", cleaned)
        cleaned2 = re.sub(r"-{3,}", " ", cleaned)
        cleaned2 = re.sub(r"[ \t]{2,}", " ", cleaned2).strip()
        return _resolve_location_placeholders(cleaned2)[:2400]

    def score(c: str) -> tuple[int, int, int]:
        low = c.lower()
        bad = low.count("{") + low.count("##")
        # Prefer concrete scene/hook prose over title-like fragments.
        words = len(re.findall(r"[a-zA-Z']+", c))
        return (-bad, -words, -len(c))

    chunks.sort(key=score)
    picked = chunks[0][:2400].strip()
    picked = re.sub(r"-{3,}", " ", picked)
    picked = re.sub(r"[ \t]{2,}", " ", picked)
    return _resolve_location_placeholders(picked)


def _strip_slot_artifacts(
    text: str,
    *,
    phrase_memory: EnvironmentPhraseMemory | None = None,
    chapter_index: int = 0,
) -> str:
    from phoenix_v4.rendering.book_renderer import _scrub_inline_leaked_slot_markers

    t = _resolve_location_placeholders(
        (text or "").strip(),
        phrase_memory=phrase_memory,
        chapter_index=chapter_index,
    )
    if not t:
        return ""
    lines_out: list[str] = []
    for line in t.splitlines():
        if _PLACEHOLDER_LINE.match(line.strip()):
            continue
        lines_out.append(_scrub_inline_leaked_slot_markers(line))
    joined = "\n".join(lines_out).strip()
    joined = re.sub(r"\s-{3,}\s", "\n\n", joined)
    return joined


def _dedupe_paragraphs(
    blocks: list[str],
    *,
    phrase_memory: EnvironmentPhraseMemory | None = None,
    chapter_index: int = 0,
) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for b in blocks:
        chunk = _strip_slot_artifacts(
            b,
            phrase_memory=phrase_memory,
            chapter_index=chapter_index,
        )
        if not chunk:
            continue
        for para in re.split(r"\n\s*\n+", chunk):
            p = para.strip()
            if len(p) < 24:
                continue
            key = re.sub(r"\s+", " ", p.lower())[:220]
            if key in seen:
                continue
            seen.add(key)
            out.append(p)
    return "\n\n".join(out)


def _dedupe_hook_scene(hook: str, scene: str) -> tuple[str, str]:
    h, s = (hook or "").strip(), (scene or "").strip()
    if not h or not s:
        return h, s
    h_low, s_low = h.lower(), s.lower()
    # Drop scene lead when it largely repeats the hook open (fragment-assembler tell).
    h_prefix = h_low[: min(180, len(h_low))]
    if len(h_prefix) > 40 and s_low.startswith(h_prefix[:60]):
        s = s[len(h_prefix[:60]) :].lstrip(" \n—-")
    elif s_low[:120] in h_low or h_low[:120] in s_low:
        sents = re.split(r"(?<=[.!?])\s+", s)
        if len(sents) > 1 and sents[0].lower().strip() in h_low:
            s = " ".join(sents[1:]).strip()
    return h, s


def _bucket_slots(slots: list["EnrichedSlot"]) -> dict[str, list[str]]:
    core: dict[str, list[str]] = {k: [] for k in (
        "HOOK", "SCENE", "STORY", "REFLECTION", "PIVOT", "EXERCISE",
        "INTEGRATION", "THREAD", "TAKEAWAY", "PERMISSION", "COMPRESSION",
        "TEACHER_DOCTRINE",
    )}
    depth_story: list[str] = []
    depth_mech: list[str] = []
    for slot in slots:
        st = str(slot.slot_type or "").strip().upper()
        raw = slot.content or ""
        if not raw.strip() or raw.strip().startswith("[CONTENT GAP"):
            continue
        if st.startswith("DEPTH_"):
            cleaned = _extract_single_body_from_depth_canonical_dump(raw)
            cleaned = _strip_slot_artifacts(cleaned)
            if not cleaned:
                continue
            if "STORY" in st or "SCENE" in st:
                depth_story.append(cleaned)
            else:
                depth_mech.append(cleaned)
            continue
        body = _strip_slot_artifacts(raw)
        if not body:
            continue
        if st in core:
            core[st].append(body)
    return {"_depth_story": depth_story, "_depth_mech": depth_mech, **core}


def _first_or_join(
    parts: list[str],
    *,
    phrase_memory: EnvironmentPhraseMemory | None = None,
    chapter_index: int = 0,
) -> str:
    cleaned: list[str] = []
    for p in parts:
        fixed = _strip_slot_artifacts(
            p,
            phrase_memory=phrase_memory,
            chapter_index=chapter_index,
        )
        if fixed:
            cleaned.append(fixed)
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    return _dedupe_paragraphs(cleaned)


def _collapse_chapter_one_story_stack(story: str) -> str:
    """Opening chapter: one embodied narrative beat, not a stitched montage."""
    s = (story or "").strip()
    if not s:
        return s
    pieces = re.split(r"\s-{3,}\s", s)
    pieces = [p.strip() for p in pieces if len(p.strip()) > 50]
    if len(pieces) > 1:
        return pieces[0]
    blocks = [p.strip() for p in re.split(r"\n{2,}", s) if len(p.strip()) > 50]
    if len(blocks) > 1:
        return blocks[0]
    return s


def build_virtual_slot_streams(
    slots: list["EnrichedSlot"],
    *,
    chapter_index0: int = 0,
) -> tuple[list[str], list[str]]:
    """
    Map enriched beatmap slots → parallel (slot_types, slot_proses) for
    ``compose_chapter_prose`` (one prose string per canonical slot type).
    """
    b = _bucket_slots(slots)
    hook, scene = _dedupe_hook_scene(_first_or_join(b["HOOK"]), _first_or_join(b["SCENE"]))
    reflection = _first_or_join(b["REFLECTION"])
    if b["_depth_mech"]:
        extra = _dedupe_paragraphs(b["_depth_mech"])
        reflection = "\n\n".join(x for x in (reflection, extra) if x)
    story = _first_or_join(b["STORY"])
    if b["_depth_story"]:
        extra_s = _dedupe_paragraphs(b["_depth_story"])
        story = "\n\n".join(x for x in (story, extra_s) if x)
    if chapter_index0 == 0 and story.strip():
        story = _collapse_chapter_one_story_stack(story)
    pivot = _first_or_join(b["PIVOT"])
    exercise = _first_or_join(b["EXERCISE"])
    integration = _first_or_join(b["INTEGRATION"])
    thread = _first_or_join(b["THREAD"])
    takeaway = _first_or_join(b["TAKEAWAY"])
    permission = _first_or_join(b["PERMISSION"])
    compression = _first_or_join(b["COMPRESSION"])
    doctrine = _first_or_join(b["TEACHER_DOCTRINE"])

    # Order matches compose_chapter_prose consumption (opening → … → thread).
    types_: list[str] = []
    proses: list[str] = []
    pairs = [
        ("HOOK", hook),
        ("SCENE", scene),
        ("REFLECTION", reflection),
        ("STORY", story),
        ("PIVOT", pivot),
        ("COMPRESSION", compression),
        ("TEACHER_DOCTRINE", doctrine),
        ("EXERCISE", exercise),
        ("PERMISSION", permission),
        ("INTEGRATION", integration),
        ("TAKEAWAY", takeaway),
        ("THREAD", thread),
    ]
    for st, prose in pairs:
        if prose:
            types_.append(st)
            proses.append(prose)
    if not types_:
        return [], []
    return types_, proses


@dataclass
class GateResult:
    status: str  # PASS | WARN | FAIL
    detail: str = ""


@dataclass
class GoldenChapterReadiness:
    """Automated preflight for a golden chapter (human read is explicit manual gate)."""

    artifact_leakage: GateResult
    repeated_scene_furniture: GateResult
    voice_coherence: GateResult
    mechanism_clear: GateResult
    aha_moment: GateResult
    exercise_tied_to_tension: GateResult
    ending_bridge: GateResult
    human_read: dict[str, str]
    automated_overall: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_leakage": {"status": self.artifact_leakage.status, "detail": self.artifact_leakage.detail},
            "repeated_scene_furniture": {
                "status": self.repeated_scene_furniture.status,
                "detail": self.repeated_scene_furniture.detail,
            },
            "voice_coherence": {"status": self.voice_coherence.status, "detail": self.voice_coherence.detail},
            "mechanism_clear": {"status": self.mechanism_clear.status, "detail": self.mechanism_clear.detail},
            "aha_moment": {"status": self.aha_moment.status, "detail": self.aha_moment.detail},
            "exercise_tied_to_tension": {
                "status": self.exercise_tied_to_tension.status,
                "detail": self.exercise_tied_to_tension.detail,
            },
            "ending_bridge": {"status": self.ending_bridge.status, "detail": self.ending_bridge.detail},
            "human_read": dict(self.human_read),
            "automated_overall": self.automated_overall,
            "notes": list(self.notes),
        }


def collect_artifact_leakage_labels(text: str) -> list[str]:
    """Human-readable leakage labels for audits and tests."""
    t = text or ""
    hits: list[str] = []
    for label, pat in _ARTIFACT_PATTERN_DEFS:
        if re.search(pat, t, flags=re.MULTILINE):
            hits.append(label)
    if len(_CANONICAL_VARIANT_HEADER_RE.findall(t)) >= 2:
        hits.append("repeated_canonical_variant_headers")
    return hits


def _scan_artifacts(text: str) -> tuple[str, str]:
    hits = collect_artifact_leakage_labels(text)
    if not hits:
        return "PASS", ""
    return "FAIL", "; ".join(hits[:12])


def _repeated_furniture(text: str) -> tuple[str, str]:
    """Flag over-repeated 4-word n-grams (cheap proxy for repeated scene furniture)."""
    low = re.sub(r"\s+", " ", (text or "").lower())
    words = re.findall(r"[a-z0-9']+", low)
    if len(words) < 16:
        return "WARN", "chapter too short for furniture scan"
    counts: dict[str, int] = {}
    for i in range(0, len(words) - 3):
        ng = " ".join(words[i : i + 4])
        counts[ng] = counts.get(ng, 0) + 1
    worst = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    bad = [(g, c) for g, c in worst if c >= 4 and g not in {"the the the the"}]
    if not bad:
        return "PASS", ""
    return "WARN", f"4-grams repeated >=4x: {bad[0][0]!r} ({bad[0][1]}x)"


def _voice_heuristic(text: str) -> tuple[str, str]:
    low = (text or "").lower()
    crutch = sum(low.count(w) for w in (" actually ", " just ", " really ", " literally "))
    if crutch >= 14:
        return "WARN", f"intensifiers/crutches high ({crutch})"
    if low.count(" i have noticed that ") + low.count(" what i have come to understand"):
        return "WARN", "academic hedging phrases present"
    return "PASS", ""


def _mechanism_heuristic(text: str) -> tuple[str, str]:
    low = (text or "").lower()
    if "mechanism" in low or "nervous system" in low or "pattern" in low:
        if "point is" in low or "here is what" in low or "what is happening" in low:
            return "PASS", ""
    if "because" in low and ("brain" in low or "body" in low):
        return "PASS", ""
    return "WARN", "weak explicit mechanism / model language"


def _aha_heuristic(text: str) -> tuple[str, str]:
    low = (text or "").lower()
    if "the point is" in low and ("not" in low or "actually" in low or "instead" in low):
        return "PASS", ""
    if re.search(r"\b(oh,|wait—|but here|the reversal|what shifts)\b", low):
        return "PASS", ""
    return "WARN", "no strong aha / reversal signal in prose"


def _exercise_heuristic(text: str, thesis_hint: str = "") -> tuple[str, str]:
    low = (text or "").lower()
    has_timed = bool(
        re.search(
            r"\b(?:for|over)\s+(?:the\s+next\s+)?(?:one|two|three|sixty|\d+)\s+(?:second|minute|minutes|seconds)\b",
            low,
        )
    )
    has_steps = (
        bool(re.search(r"(?:^|\n)\s*\d+\.\s+\S", text))
        or "try this" in low
        or "for three minutes" in low
        or has_timed
    )
    if not has_steps:
        return "FAIL", "no concrete step / timed practice detected"
    tension_tokens = (
        "scan",
        "scanning",
        "prediction",
        "alarm",
        "false",
        "fact",
        "nervous",
        "body",
        "threat",
    )
    if any(w in low for w in tension_tokens):
        return "PASS", ""
    if thesis_hint:
        th = thesis_hint.lower()[:120]
        if th and any(tok in low for tok in th.split() if len(tok) > 5):
            return "PASS", ""
    return "WARN", "exercise present; tie to chapter tension not keyword-verified"


def _bridge_heuristic(text: str) -> tuple[str, str]:
    tail = (text or "")[-900:].lower()
    if any(
        x in tail
        for x in (
            "what remains",
            "next",
            "tomorrow",
            "the next chapter",
            "before the next",
            "?",
        )
    ):
        return "PASS", ""
    return "WARN", "ending may lack forward pull / question"


def evaluate_golden_chapter_readiness(
    chapter_prose: str,
    *,
    chapter_thesis: str = "",
    working_title: str = "",
) -> GoldenChapterReadiness:
    art = _scan_artifacts(chapter_prose)
    furn = _repeated_furniture(chapter_prose)
    voice = _voice_heuristic(chapter_prose)
    mech = _mechanism_heuristic(chapter_prose)
    aha = _aha_heuristic(chapter_prose)
    ex = _exercise_heuristic(chapter_prose, thesis_hint=chapter_thesis)
    br = _bridge_heuristic(chapter_prose)

    checks = [art, furn, voice, mech, aha, ex, br]
    if any(s == "FAIL" for s, _ in checks):
        overall = "FAIL"
    elif any(s == "WARN" for s, _ in checks):
        overall = "WARN"
    else:
        overall = "PASS"

    return GoldenChapterReadiness(
        artifact_leakage=GateResult(art[0], art[1]),
        repeated_scene_furniture=GateResult(furn[0], furn[1]),
        voice_coherence=GateResult(voice[0], voice[1]),
        mechanism_clear=GateResult(mech[0], mech[1]),
        aha_moment=GateResult(aha[0], aha[1]),
        exercise_tied_to_tension=GateResult(ex[0], ex[1]),
        ending_bridge=GateResult(br[0], br[1]),
        human_read={
            "status": "REQUIRED_MANUAL",
            "prompt": (
                "Read aloud once. Pass only if the chapter feels authored: one clear mechanism, "
                "one credible turn, one exercise that fits the tension, no 'stitched fragments' smell."
            ),
            "chapter_thesis": chapter_thesis,
            "working_title": working_title,
        },
        automated_overall=overall,
    )


def compose_golden_spine_chapter(
    chapter: "EnrichedChapter",
    *,
    chapter_index0: int,
    total_chapters: int,
    topic_id: str,
    persona_id: str,
    book_seed: str,
    frame: str = "somatic_first",
    governance_report: Optional[dict[str, Any]] = None,
    mechanism_memory: Any = None,
    exercise_memory: Any = None,
) -> tuple[str, dict[str, Any]]:
    """
    Returns (chapter body without ``Chapter N`` heading, synthesis_meta).
    Caller wraps with chapter heading + title for gate splitters.
    """
    from phoenix_v4.planning.chapter_planner import assign_chapter_purpose_contracts
    from phoenix_v4.quality.frame_governor import (
        FrameEnforcementContext,
        apply_frame_enforcement,
        load_frame_registry,
    )
    from phoenix_v4.rendering.chapter_composer import compose_chapter_prose

    slot_types, slot_proses = build_virtual_slot_streams(chapter.slots, chapter_index0=chapter_index0)
    meta: dict[str, Any] = {
        "virtual_slot_types": slot_types,
        "beat_model": list(GOLDEN_BEATS),
        "working_title": chapter.working_title,
        "thesis": chapter.thesis,
    }
    if not slot_types:
        return "", {**meta, "error": "no_slot_content"}

    contracts = assign_chapter_purpose_contracts(total_chapters, None)
    contract = contracts[chapter_index0] if chapter_index0 < len(contracts) else contracts[-1]
    emotional_role = str(getattr(contract, "emotional_job", "") or "")

    composed = compose_chapter_prose(
        slot_types,
        slot_proses,
        chapter_index=chapter_index0,
        total_chapters=total_chapters,
        topic_id=topic_id,
        persona_id=persona_id,
        emotional_role=emotional_role,
        book_seed=book_seed,
        mechanism_memory=mechanism_memory,
        exercise_memory=exercise_memory,
    )

    has_doctrine = any(
        str(s.slot_type or "").strip().upper() == "TEACHER_DOCTRINE" for s in chapter.slots
    )
    frame_registry = load_frame_registry()
    fe_ctx = FrameEnforcementContext(
        chapter_index=chapter_index0,
        frame=frame,
        doctrine_chapter=has_doctrine,
        allow_early_spiritual=bool(contract.allow_early_spiritual),
        emotional_job=str(contract.emotional_job or ""),
    )
    ch_body, fg = apply_frame_enforcement(composed, fe_ctx, frame_registry)
    meta["frame_governance"] = {
        "violations": fg.violations,
        "softened": len(fg.softened_sentences),
        "stripped": len(fg.stripped_sentences),
    }
    if governance_report is not None:
        if isinstance(governance_report.get("frame_softened_sentences"), list):
            governance_report["frame_softened_sentences"].extend(fg.softened_sentences)
        if isinstance(governance_report.get("frame_stripped_sentences"), list):
            governance_report["frame_stripped_sentences"].extend(fg.stripped_sentences)
        if isinstance(governance_report.get("frame_hard_fail_reasons"), list):
            governance_report["frame_hard_fail_reasons"].extend(fg.hard_fail_reasons)
        if isinstance(governance_report.get("frame_governance_chapters"), list):
            if (
                fg.violations
                or fg.softened_sentences
                or fg.stripped_sentences
                or fg.hard_fail_reasons
                or not fg.frame_compliant
            ):
                governance_report["frame_governance_chapters"].append(
                    {
                        "chapter": int(getattr(chapter, "number", chapter_index0 + 1)),
                        "chapter_index": chapter_index0,
                        "violations": fg.violations,
                        "softened": fg.softened_sentences,
                        "stripped": fg.stripped_sentences,
                        "hard_fail": fg.hard_fail_reasons,
                        "frame_compliant": fg.frame_compliant,
                        "spiritual_density": fg.spiritual_density,
                    },
                )

    return ch_body.strip(), meta


# --- Post-compose sanitizer (stopgap + spine strengthener offset) -----------------

_SCENE_FURNITURE_ALTS: tuple[str, ...] = (
    "muted light at the window",
    "a thin band of daylight on the desk",
    "the room holds its ordinary quiet",
    "air from the vent, cool and steady",
    "a coffee ring drying on the coaster",
    "the hallway hum beyond the door",
    "keyboard light in a dim corner",
    "the chair creaks once when you shift",
)

_SECULAR_BLOCKLIST = (
    "buddha",
    "buddhist",
    "bodhi",
    "dharma",
    "dharmakaya",
    "nirvana",
    "sangha",
    "zen master",
    "enlightenment",
    "waking up to what you've always been",
    "you're waking up to what you've always been",
    "you are waking up to what you've always been",
    "what you've always known",
    "you're remembering what you've always known",
    "loving kindness",
    "open awareness",
    "complete integration",
    "this is complete integration",
    "bring together everything you've practiced",
    "you're not learning something new",
    "insight. it's all here",
    "let it all be present",
)

_SECULAR_INTEGRATION_REGEX: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"bring together everything you'?ve practiced[\s\S]{0,220}loving kindness",
        re.I,
    ),
    re.compile(
        r"breath awareness[\s\S]{0,120}open awareness[\s\S]{0,120}loving kindness",
        re.I,
    ),
)


def _strip_markdown_dividers(text: str) -> str:
    lines: list[str] = []
    for line in (text or "").splitlines():
        if re.match(r"^\s*---\s*$", line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _strip_python_repr_lines(text: str) -> str:
    """Drop lines that look like Python dict/list repr leaked into prose."""
    out: list[str] = []
    for line in (text or "").splitlines():
        s = line.strip()
        if not s:
            out.append(line)
            continue
        if s.startswith("{'") or s.startswith('{"') or s.startswith("[{'") or s.startswith('[{"'):
            continue
        if len(s) > 12 and s.startswith("{") and ("': " in s or '":' in s) and s.endswith("}"):
            continue
        if len(s) > 12 and s.startswith("[") and s.endswith("]") and ("': " in s or '":' in s):
            continue
        out.append(line)
    joined = "\n".join(out)
    joined = re.sub(r"\s*\{['\"][^'\"]+['\"]\s*:\s*[^}]+\}\s*", " ", joined)
    return joined.strip()


def _fix_double_articles(text: str) -> str:
    t = re.sub(r"\bThe\s+the\b", "The", text, flags=re.IGNORECASE)
    t = re.sub(r"\bthe\s+the\b", "the", t, flags=re.IGNORECASE)
    return t


def _strip_secular_violation_paragraphs(text: str, topic_id: str) -> str:
    if (topic_id or "").strip().lower() != "anxiety":
        return text
    paras: list[str] = []
    for block in re.split(r"\n{2,}", (text or "").strip()):
        low = block.lower()
        if any(tok in low for tok in _SECULAR_BLOCKLIST):
            continue
        if any(rx.search(block) for rx in _SECULAR_INTEGRATION_REGEX):
            continue
        paras.append(block.strip())
    return "\n\n".join(paras).strip()


def post_compose_sanitize_chapter(
    text: str,
    *,
    topic_id: str = "",
    phrase_memory: EnvironmentPhraseMemory | None = None,
    chapter_index: int = 0,
) -> str:
    """Deterministic cleanup after chapter composition (not a substitute for rewrite)."""
    t = _resolve_location_placeholders(
        (text or "").strip(),
        phrase_memory=phrase_memory,
        chapter_index=chapter_index,
    )
    if not t:
        return t
    # Inline spine/template joins often leak triple-dash runs inside a paragraph.
    t = re.sub(r"\s-{3,}\s", "\n\n", t)
    t = re.sub(r"-{3,}", " ", t)
    t = _strip_markdown_dividers(t)
    lines_nc = []
    for ln in t.splitlines():
        if re.match(r"^\s*##\s+(HOOK|SCENE|STORY|REFLECTION|PIVOT|EXERCISE|INTEGRATION|THREAD|TAKEAWAY)\b", ln, re.I):
            continue
        lines_nc.append(ln)
    t = "\n".join(lines_nc)
    t = _strip_python_repr_lines(t)
    t = _fix_double_articles(t)
    t = _CANONICAL_VARIANT_HEADER_RE.sub("", t)
    t = _strip_secular_violation_paragraphs(t, topic_id)
    t = "\n".join(re.sub(r"[ \t]{2,}", " ", ln).rstrip() for ln in t.splitlines())
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _limit_case_insensitive_phrase_occurrences(
    text: str,
    phrase: str,
    keep: int,
    replacements: tuple[str, ...],
) -> tuple[str, int]:
    """Replace occurrences beyond ``keep`` with rotating alternates. Returns (new_text, replaced_n)."""
    if not text or not phrase:
        return text, 0
    pat = re.compile(re.escape(phrase), re.IGNORECASE)
    replaced = 0
    n = 0
    parts: list[str] = []
    pos = 0
    for m in pat.finditer(text):
        parts.append(text[pos : m.start()])
        n += 1
        if n <= keep:
            parts.append(m.group(0))
        else:
            alt = replacements[(n - keep - 1) % len(replacements)] if replacements else ""
            parts.append(alt)
            replaced += 1
        pos = m.end()
    parts.append(text[pos:])
    return "".join(parts), replaced


def dedupe_scene_furniture_book(
    text: str,
    *,
    max_each: int = 2,
) -> tuple[str, list[str]]:
    """
    After ``strengthen_chapter_flow_for_delivery``, generic lighting normalization can
    repeat the same phrase across many chapters. Cap each known signature string book-wide.

    Extra occurrences are removed (single space) rather than swapped for alternate imagery,
    to avoid breaking grammar when the phrase sits inside a longer broken clause.
    """
    notes: list[str] = []
    work = text or ""
    signatures = (
        "soft daylight along the sill",
        "muted light along the window",
        "soft traffic noise from outside",
        "outside noise drifts in without detail",
        "a hallway hum carries through the corridor",
        "route motion keeps the rhythm nearby",
        "the cursor waits where you left it",
        "a coffee ring stays on the coaster",
        "your badge stays in your pocket",
        "a pale reflection at the glass edge",
        "a shifting reflection at the window",
        "the street below is visible through the glass",
        "the street below is visible",
        "the street below is",
        "gray light through the window",
    )
    for sig in signatures:
        work, n = _limit_case_insensitive_phrase_occurrences(work, sig, max_each, ())
        if n:
            notes.append(f"removed_extra_occurrences: {sig!r} x{n}")
    work = re.sub(r"[ \t]{2,}", " ", work)
    work = re.sub(r"\n{3,}", "\n\n", work)
    return work.strip(), notes


def audit_artifact_leakage(text: str) -> dict[str, Any]:
    hits = collect_artifact_leakage_labels(text or "")
    return {"status": "PASS" if not hits else "FAIL", "patterns_matched": hits}


def audit_repeated_phrases(text: str, *, min_words: int = 4, warn_at: int = 4) -> dict[str, Any]:
    low = re.sub(r"\s+", " ", (text or "").lower())
    words = re.findall(r"[a-z0-9']+", low)
    if len(words) < min_words + 4:
        return {"status": "PASS", "worst": [], "note": "too_short"}
    counts: dict[str, int] = {}
    for i in range(0, len(words) - min_words + 1):
        ng = " ".join(words[i : i + min_words])
        counts[ng] = counts.get(ng, 0) + 1
    worst = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    bad = [(g, c) for g, c in worst if c >= warn_at]
    return {
        "status": "PASS" if not bad else "WARN",
        "worst": [{"phrase": g, "count": c} for g, c in bad],
    }


def audit_rmttp_contract(text: str) -> dict[str, str]:
    """Heuristic R-M-T-P-P map for pilot reporting (not a gate substitute)."""
    t = (text or "").strip()
    if len(t) < 80:
        return {k: "FAIL" for k in ("recognition", "mechanism", "turn", "practice", "pull")}
    head = t[:500].lower()
    recognition = (
        "WARN"
        if re.match(r"^\s*anxiety\s+is\b", head)
        or re.match(r"^\s*this chapter\b", head)
        else "PASS"
    )
    low = t.lower()
    mechanism = "PASS" if any(x in low for x in ("because", "nervous system", "alarm", "pattern", "prediction")) else "WARN"
    turn = "PASS" if "the point is" in low and ("not " in low or "instead" in low) else "WARN"
    practice = "PASS" if re.search(r"(?:^|\n)\s*\d+\.\s+\S", t) or "try this" in low else "WARN"
    tail = t[-500:].lower()
    pull = "PASS" if "?" in tail or "next" in tail or "tomorrow" in tail else "WARN"
    return {
        "recognition": recognition,
        "mechanism": mechanism,
        "turn": turn,
        "practice": practice,
        "pull": pull,
    }


def build_golden_chapter_report_payload(
    *,
    chapter_number: int,
    working_title: str,
    thesis: str,
    chapter_prose: str,
    selected_fragments: list[dict[str, Any]],
    readiness: GoldenChapterReadiness,
    prose_before_sanitize: str = "",
    repair_notes: Optional[list[str]] = None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "stage": "golden_chapter_pilot",
        "chapter_number": chapter_number,
        "working_title": working_title,
        "chapter_thesis": thesis,
        "word_count": len(chapter_prose.split()),
        "selected_source_fragments": selected_fragments,
        "prose_before_sanitize_excerpt": (prose_before_sanitize or "")[:800],
        "synthesized_chapter_excerpt": chapter_prose[:1200],
        "repair_notes": repair_notes or [],
        "artifact_leakage_audit": audit_artifact_leakage(chapter_prose),
        "repeated_phrase_audit": audit_repeated_phrases(chapter_prose),
        "golden_readiness": readiness.to_dict(),
        "rmttp_heuristic": audit_rmttp_contract(chapter_prose),
        "acceptance_note": (
            "Do not claim bestseller readiness. Evaluate: golden path, source gaps, or leakage."
        ),
    }


def write_golden_chapter_pilot_artifacts(
    *,
    manuscript_text: str,
    enriched: Any,
    chapter_number_1based: int,
    out_dir: Path,
    topic_id: str,
) -> Path:
    """Write golden_chapter_report.json + golden_chapter_N.txt for spine pilot review."""
    out_dir.mkdir(parents=True, exist_ok=True)
    from phoenix_v4.rendering.book_renderer import _extract_rendered_chapters

    bodies = _extract_rendered_chapters(manuscript_text)
    ch_map = {num: body for num, body in bodies}
    if chapter_number_1based not in ch_map:
        raise ValueError(f"chapter {chapter_number_1based} not found in manuscript ({list(ch_map)})")
    raw_chapter = ch_map[chapter_number_1based]
    ch_idx = chapter_number_1based - 1
    if ch_idx < 0 or ch_idx >= len(enriched.chapters):
        raise ValueError("chapter index out of range for enriched book")
    ech = enriched.chapters[ch_idx]
    repair_notes: list[str] = []
    before = raw_chapter
    phrase_memory = EnvironmentPhraseMemory()
    cleaned = post_compose_sanitize_chapter(
        raw_chapter,
        topic_id=topic_id,
        phrase_memory=phrase_memory,
        chapter_index=ch_idx,
    )
    if cleaned != before:
        repair_notes.append("applied_post_compose_sanitize_chapter")
    deduped, furn = dedupe_scene_furniture_book(cleaned, max_each=2)
    if furn:
        repair_notes.extend(furn)
    final = deduped
    readiness = evaluate_golden_chapter_readiness(
        final,
        chapter_thesis=ech.thesis,
        working_title=ech.working_title,
    )
    frags: list[dict[str, Any]] = []
    for slot in ech.slots:
        body = (slot.content or "").strip()
        if not body or body.startswith("[CONTENT GAP"):
            continue
        frags.append(
            {
                "slot_type": slot.slot_type,
                "source": slot.source,
                "source_id": slot.source_id,
                "excerpt": body[:400],
            },
        )
    payload = build_golden_chapter_report_payload(
        chapter_number=chapter_number_1based,
        working_title=ech.working_title,
        thesis=ech.thesis,
        chapter_prose=final,
        selected_fragments=frags,
        readiness=readiness,
        prose_before_sanitize=before,
        repair_notes=repair_notes,
    )
    report_path = out_dir / "golden_chapter_report.json"
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / f"golden_chapter_{chapter_number_1based}.txt").write_text(
        final.strip() + "\n",
        encoding="utf-8",
    )
    return report_path
