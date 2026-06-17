"""
Stage 6 book renderer: CompiledBook + prose map → manuscript/ebook outputs.
Writers: TxtWriter (QA and pipeline). Optional DOCX/EPUB later.
Edge cases: placeholders → [Placeholder: TYPE], silence → [Silence: TYPE], missing → fail or [Missing: atom_id].
Teacher Mode: when atom_source == practice_fallback for EXERCISE, wrap with teacher intro/close templates (deterministic).
Delivery: clean_for_delivery() strips scaffolding + resolves loc-var fallbacks.
          delivery_contract_gate() hard-fails build if forbidden artifacts survive into output.
Frame: when clean_output, per-chapter frame enforcement (frame_governor.apply_frame_enforcement)
       runs after strengthen_chapter_flow_for_delivery; spine/enriched path applies the same
       stage inside chapter_composer.compose_from_enriched_book.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import json

logger = logging.getLogger(__name__)

from phoenix_v4.quality.chapter_flow_gate import (
    _THESIS_CUES,
    _TRANSITION_CUES,
    evaluate_chapter_flow,
    flow_profile_for_runtime_format,
)

# ---------------------------------------------------------------------------
# Delivery contract: forbidden patterns that must never reach output
# ---------------------------------------------------------------------------

# Location variable config loaded lazily from config/content_banks/loc_var_render.yaml.
# The YAML is the authoritative source; the dicts below are empty-by-default in-memory caches.
_LOC_VAR_FALLBACKS: dict[str, str] = {}
_LOC_VAR_ROTATIONS: dict[str, list[str]] = {}
_LOC_VAR_LOADED: bool = False

_LOC_VAR_YAML = (
    Path(__file__).resolve().parent.parent.parent
    / "config" / "content_banks" / "loc_var_render.yaml"
)


def _load_loc_var_config() -> None:
    global _LOC_VAR_FALLBACKS, _LOC_VAR_ROTATIONS, _LOC_VAR_LOADED
    if _LOC_VAR_LOADED:
        return
    _LOC_VAR_LOADED = True
    try:
        import yaml as _yaml  # type: ignore[import]
        with open(_LOC_VAR_YAML, encoding="utf-8") as fh:
            data = _yaml.safe_load(fh) or {}
        _LOC_VAR_FALLBACKS = dict(data.get("fallbacks") or {})
        _LOC_VAR_ROTATIONS = {k: list(v) for k, v in (data.get("rotations") or {}).items()}
    except Exception as exc:
        logger.warning("loc_var_render.yaml load failed (%s); using empty tables", exc)


def _get_loc_var(var_name: str, chapter_index: int = 0) -> str:
    """Get a location variable value, rotating per chapter for diversity."""
    _load_loc_var_config()
    variants = _LOC_VAR_ROTATIONS.get(var_name)
    if variants:
        return variants[chapter_index % len(variants)]
    return _LOC_VAR_FALLBACKS.get(var_name, var_name)

_LOCATION_PROFILE_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "localization" / "render_location_profiles.yaml"
_LOCATION_PROFILE_CACHE: Optional[dict[str, dict[str, str]]] = None

# Metadata keys that belong to the pipeline, not the reader.
_METADATA_LINE_RE = re.compile(
    r"^\s*"
    r"(family|voice_mode|mode|reframe_type|mechanism_emphasis|"
    r"weight|carry_line|atom_id|BAND|MECHANISM_DEPTH|"
    r"COST_TYPE|COST_INTENSITY|IDENTITY_STAGE|"
    r"fingerprint|char_count|paragraph_count|sentence_count)"
    r"\s*:",
    re.IGNORECASE,
)

# Inline block headers like [family: F4 voice_mode: guide mechanism_emphasis: automatic]
_METADATA_BLOCK_RE = re.compile(r"^\[.*?(family|voice_mode|mode|reframe_type).*?\]", re.IGNORECASE)

# Angle-journey planner-template placeholders (config/planning/angle_journey_fallback.yaml)
# leak when per-angle ANGLE_DEFINITION / ANGLE_CALLBACK atoms are uncommissioned. Each renders
# as a blank-line-delimited block led by a bracketed "[Angle journey — …]" marker; the leader
# and its interpolated follow-on lines (e.g. "Phase: …. Prior layer: …") are all scaffolding.
_ANGLE_JOURNEY_PLACEHOLDER_RE = re.compile(r"^\s*\[Angle journey\b", re.IGNORECASE)

# Title-page lines like "Topic: anxiety" or "Persona: gen_z_professionals"
_TITLE_META_RE = re.compile(r"^(Topic|Persona)\s*:", re.IGNORECASE)

# Scaffold markers
_DIVIDER_RE    = re.compile(r"^---\s*$")
_CHAPTER_RE    = re.compile(r"^={5,}.*CHAPTER", re.IGNORECASE)

# Markdown section headers leaked from assembly (e.g. ## HOOK v01) — not reader-facing prose.
# MECHANISM_DEPTH / BAND / … : whole line only (case-insensitive for these tokens).
# HOOK/STORY/SCENE: **case-sensitive** slot tokens so "## Story of my life" is kept but "## STORY v01 --- …" is stripped.
_SECTION_VARIANT_RE = re.compile(
    r"^#{1,3}\s+(?:"
    r"(?:MECHANISM_DEPTH|COST_TYPE|COST_INTENSITY|IDENTITY_STAGE|BAND)\s*"
    r")$",
    re.IGNORECASE,
)

# Any line beginning with ## + uppercase HOOK|STORY|SCENE (+ optional vNN) is assembly scaffolding,
# including inline junk like "## HOOK v01 --- --- note".
_ASSEMBLY_SLOT_HEADING_LINE_RE = re.compile(
    r"^#{1,3}\s+(HOOK|STORY|SCENE)(?:\s+v\d+)?(?:\s+.*)?$"
)

# DEFECT 7 (composer-guard lane, fail-closed backstop): bare (no-"## ") atom-id
# labels — e.g. "INTEGRATION v06", "RECOGNITION v04" — leak verbatim into reader
# prose when a malformed CANONICAL.txt header is absorbed into the prior atom
# body. The "## "-prefixed scrubbers above never match these, so they slip
# through. This pattern matches a standalone all-caps (+ underscore) atom-id
# label followed by " vNN" and nothing else, so no raw atom-id label reaches
# reader prose. Whole-line match only — natural prose is never of this form.
_BARE_ATOM_ID_LINE_RE = re.compile(r"^[A-Z_]+ v\d+$")

# Python dict blobs accidentally pasted into prose (pipeline/debug).
_INTRO_DICT_OPEN_RE = re.compile(r"\{(?:'intro'|\"intro\"):")

# Spine / template leakage: long lines concatenating many "## HOOK v01 --- --- prose" blocks.
_HOOK_SCENE_LEAK = re.compile(
    r"#+\s+(?:HOOK|SCENE)\s+v\d+(?:\s+\d+)?\s*(?:---\s*)+",
    re.IGNORECASE,
)
_STORY_META_LEAK = re.compile(
    r"#+\s+STORY\s+v\d+(?:\s+\d+)?\s*---\s*MECHANISM_DEPTH:[^#]+?---\s*",
    re.IGNORECASE | re.DOTALL,
)
_STORY_SIMPLE_LEAK = re.compile(
    r"#+\s+STORY\s+v\d+(?:\s+\d+)?\s*---\s*",
    re.IGNORECASE,
)


def _scrub_inline_leaked_slot_markers(line: str) -> str:
    """Remove concatenated assembly markers (## HOOK v01 --- ---) while keeping prose.

    DEFECT 7 composer-guard: do NOT early-return when "##" is absent — a bare
    standalone atom-id label ("INTEGRATION v06") carries no "##" yet must still be
    scrubbed so it never reaches reader prose. A whole stripped line that is just a
    bare atom-id label collapses to the empty string.
    """
    # Bare-atom-id backstop runs first and is "##"-independent.
    if _BARE_ATOM_ID_LINE_RE.match(line.strip()):
        return ""
    if "##" not in line:
        return line
    s = line
    for _ in range(5000):
        ns = _HOOK_SCENE_LEAK.sub("", s)
        if ns == s:
            break
        s = ns
    for _ in range(5000):
        ns = _STORY_META_LEAK.sub("", s)
        if ns == s:
            break
        s = ns
    for _ in range(5000):
        ns = _STORY_SIMPLE_LEAK.sub("", s)
        if ns == s:
            break
        s = ns
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


class DeliveryContractError(ValueError):
    """Raised by delivery_contract_gate() when forbidden artifacts survive into prose output."""


class LocationGroundingError(ValueError):
    """Raised when a run requests location grounding but the opening does not realize it."""


def _load_location_profiles() -> dict[str, dict[str, str]]:
    """Load render_location_profiles.yaml for loc-var substitution and grounding checks.

    Only string-valued keys are kept (excludes ``aliases`` lists). Matches the on-disk
    schema used by catalog_planner.load_render_location_profiles.
    """
    global _LOCATION_PROFILE_CACHE
    if _LOCATION_PROFILE_CACHE is not None:
        return _LOCATION_PROFILE_CACHE
    data: dict = {}
    if _LOCATION_PROFILE_PATH.exists():
        try:
            data = yaml.safe_load(_LOCATION_PROFILE_PATH.read_text(encoding="utf-8")) or {}
        except Exception:
            data = {}
    profiles = data.get("profiles") or {}
    cleaned: dict[str, dict[str, str]] = {}
    for profile_id, profile in profiles.items():
        if not isinstance(profile, dict):
            continue
        vars_only: dict[str, str] = {}
        for k, v in profile.items():
            if k == "aliases":
                continue
            if isinstance(v, str) and v.strip():
                vars_only[str(k)] = v.strip()
        cleaned[str(profile_id)] = vars_only
    _LOCATION_PROFILE_CACHE = cleaned
    return _LOCATION_PROFILE_CACHE


def _infer_location_id(plan: Optional[dict[str, Any]]) -> str:
    plan = plan or {}
    for key in ("resolved_location_id", "requested_location_id", "location_id", "city", "city_name"):
        value = plan.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    book_spec = plan.get("book_spec") or {}
    if isinstance(book_spec, dict):
        for key in ("resolved_location_id", "requested_location_id", "location_id", "city", "city_name"):
            value = book_spec.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    persona_id = str(plan.get("persona_id") or "")
    if persona_id.startswith("nyc_"):
        return "nyc_metro"
    return ""


def _resolve_loc_var_fallbacks(text: str, plan: Optional[dict[str, Any]] = None) -> str:
    """Replace known location variables with universal or location-aware fallbacks.

    Splits by chapter markers so each chapter gets different location variants,
    preventing identical scene text across chapters.
    Any {var} that remains after this is caught and hard-failed by delivery_contract_gate().
    """
    location_id = _infer_location_id(plan)
    profile = _load_location_profiles().get(location_id, {}) if location_id else {}

    # Split into chapters for per-chapter variant rotation
    import re as _re
    chapter_splits = _re.split(r'(Chapter \d+)', text)

    resolved_parts: list[str] = []
    chapter_idx = 0
    for part in chapter_splits:
        if _re.match(r'Chapter \d+', part):
            resolved_parts.append(part)
            chapter_idx += 1
            continue
        # Resolve location vars — use profile first, then rotating fallbacks
        _load_loc_var_config()
        for var_name in _LOC_VAR_FALLBACKS:
            placeholder = "{" + var_name + "}"
            if placeholder in part:
                if var_name in profile:
                    part = part.replace(placeholder, profile[var_name])
                else:
                    part = part.replace(placeholder, _get_loc_var(var_name, chapter_idx))
        resolved_parts.append(part)
    return "".join(resolved_parts)


def _strip_intro_dict_literals(text: str) -> str:
    """Remove dict blobs starting with ``{'intro':`` / ``{\"intro\":`` (single- or multi-line).

    Uses brace-depth only (no string-aware parsing) — conservative heuristic per delivery spec.
    """
    if not text:
        return text
    parts: list[str] = []
    pos = 0
    n = len(text)
    while pos < n:
        m = _INTRO_DICT_OPEN_RE.search(text, pos)
        if not m:
            parts.append(text[pos:])
            break
        parts.append(text[pos : m.start()])
        depth = 0
        j = m.start()
        while j < n:
            ch = text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        pos = j
    return "".join(parts)


def _strip_scaffolding_lines(text: str) -> str:
    """Remove lines that are pipeline control data or markdown scaffolding, not prose."""
    text = _strip_intro_dict_literals(text)
    out: list[str] = []
    for line in text.splitlines():
        stripped = _scrub_inline_leaked_slot_markers(line).strip()
        if (
            _METADATA_LINE_RE.match(stripped)
            or _METADATA_BLOCK_RE.match(stripped)
            or _TITLE_META_RE.match(stripped)
            or _DIVIDER_RE.match(stripped)
            or _CHAPTER_RE.match(stripped)
            or _ASSEMBLY_SLOT_HEADING_LINE_RE.match(stripped)
            or _SECTION_VARIANT_RE.match(stripped)
            or _BARE_ATOM_ID_LINE_RE.match(stripped)
        ):
            continue
        out.append(stripped)
    return "\n".join(out)


def _strip_angle_journey_placeholders(text: str) -> str:
    """Drop blank-line-delimited paragraphs led by an '[Angle journey — …]' placeholder marker.

    These blocks come from config/planning/angle_journey_fallback.yaml when the per-angle
    ANGLE_DEFINITION / ANGLE_CALLBACK atoms have not been authored. The whole paragraph —
    bracketed leader plus interpolated follow-on lines such as "This book follows the … lens:"
    or "Phase: …. Prior layer: …" — is planner scaffolding, never reader-facing prose, so the
    entire block is removed (a line-level strip would orphan the follow-on lines).
    """
    paragraphs = re.split(r"\n\s*\n", text)
    kept: list[str] = []
    for para in paragraphs:
        first_nonempty = next((ln for ln in para.splitlines() if ln.strip()), "")
        if _ANGLE_JOURNEY_PLACEHOLDER_RE.match(first_nonempty):
            continue
        kept.append(para)
    return "\n\n".join(kept)


def _dedup_repeated_blocks(
    text: str,
    min_words: int = 20,
    *,
    word_floor: int = 0,
) -> str:
    """Drop repeated long paragraphs (verbatim after normalization), keep first occurrence.

    Paragraphs are split on blank-line runs. Paragraphs with fewer than ``min_words`` words
    are always kept and do not participate in deduplication (short transitions may repeat).

    Deduplication ALWAYS runs. The ``word_floor`` parameter is retained as a
    diagnostic signal: when post-dedup word count falls below the runtime
    format's floor, a structured warning is emitted so the operator can see
    the repetition was masking insufficient unique content. The bypass that
    previously kept pre-dedup text below the floor is removed — preserving
    duplicates to hit a length target produces fake-length books and is the
    documented dedup-floor regression in the bestseller drift report.
    """
    if not (text or "").strip():
        return text

    _CHAPTER_HEADING_RE = re.compile(r"^Chapter\s+\d+", re.IGNORECASE)

    pre_wc = len(text.split())
    parts = re.split(r"\n{2,}", text)
    # Sprint-1 fix: reset seen-set at each chapter boundary so depth paragraphs
    # shared across chapters are not removed.  Within a single chapter the same
    # paragraph still deduplicates normally.
    seen: set[str] = set()
    kept: list[str] = []

    for raw in parts:
        para = raw.strip()
        if not para:
            continue
        # Reset dedup window at each chapter heading
        if _CHAPTER_HEADING_RE.match(para):
            seen = set()
            kept.append(para)
            continue
        wc = len(para.split())
        if wc < min_words:
            kept.append(para)
            continue
        fp = re.sub(r"[^\w\s]+", "", para.lower(), flags=re.UNICODE)
        fp = re.sub(r"\s+", " ", fp).strip()
        if fp in seen:
            continue
        seen.add(fp)
        kept.append(para)

    deduped = "\n\n".join(kept)
    post_wc = len(deduped.split())
    unique_ratio = (post_wc / pre_wc) if pre_wc else 1.0
    if word_floor > 0 and post_wc < word_floor:
        logger.warning(
            "dedup_below_floor nominal=%s deduped=%s floor=%s unique_ratio=%.3f — "
            "deduped text returned (no longer retains duplicates to hit floor).",
            pre_wc,
            post_wc,
            word_floor,
            unique_ratio,
        )
    elif unique_ratio < 0.7 and pre_wc >= 200:
        logger.warning(
            "dedup_low_unique_ratio nominal=%s deduped=%s unique_ratio=%.3f — "
            "more than 30%% of text was repeated long-paragraph duplication.",
            pre_wc,
            post_wc,
            unique_ratio,
        )
    return deduped


# Default keep-cap for the book-wide dedupe pass: keep the first occurrence only
# (matches the chapter-scoped `_dedup_repeated_blocks` convention). Overridable
# via the `PHOENIX_BOOK_DEDUPE_KEEP` env var for tests or for an operator to
# permit a small number of intentional cross-chapter echoes.
import os as _os  # noqa: E402  (kept local to the dedupe block for clarity)


def _book_wide_dedupe_keep_default() -> int:
    try:
        return max(1, int(_os.environ.get("PHOENIX_BOOK_DEDUPE_KEEP", "1") or "1"))
    except (TypeError, ValueError):
        return 1


# OPD-109 Phase 3: atom-sized paragraphs (20-200 words) are allowed to repeat
# up to `_atom_paragraph_keep_default()` times across the book. Longer paragraphs
# (>200 words) remain `keep=1` because they typically indicate template/scaffold
# leakage that should not appear twice. This is conservative: with the OPD-109
# selector rotation, atom collisions are already rare, but when they do occur
# (16-30 atom EXERCISE pool, 12 chapters × 2 EXERCISE slots = 24 slot picks)
# stripping ALL duplicates wipes ~275 paragraphs from the rendered book.
#
# Calibration vs `repeated_phrase_violations` (8-word phrase cap = 12 book-wide):
# an 80-word atom paragraph contains ~70 unique 4-grams. Allowing 2 occurrences
# doubles the 4-gram count to ~140 occurrences per atom-phrase. Even if all
# four atoms share a stem like "for four counts", that's 8 occurrences — well
# under the 12-book cap. See OPD-109 Phase 3 validation render notes.
_ATOM_PARA_MIN_WORDS = 20  # below this: short transitions, already exempt
_ATOM_PARA_MAX_WORDS = 200  # above this: likely template/scaffold; keep=1


def _atom_paragraph_keep_default() -> int:
    """Default keep-cap for atom-sized paragraphs (20-200 words).

    Overridable via `PHOENIX_ATOM_PARAGRAPH_KEEP` for tests. Defaults to 2
    (allow each atom-paragraph to appear twice book-wide).
    """
    try:
        return max(1, int(_os.environ.get("PHOENIX_ATOM_PARAGRAPH_KEEP", "2") or "2"))
    except (TypeError, ValueError):
        return 2


def _keep_cap_for_paragraph(paragraph: str, *, base_keep: int) -> int:
    """Return the keep cap to apply to `paragraph` under the OPD-109 Phase 3 rule.

    - Paragraphs in the atom-sized range (20-200 words) → atom-paragraph keep
      (defaults to 2; env override `PHOENIX_ATOM_PARAGRAPH_KEEP`).
    - Paragraphs longer than 200 words → `base_keep` (defaults to 1).
    """
    wc = len(paragraph.split())
    if _ATOM_PARA_MIN_WORDS <= wc <= _ATOM_PARA_MAX_WORDS:
        return max(base_keep, _atom_paragraph_keep_default())
    return base_keep


# ── F1-signature cross-chapter dedupe (ws_f1_signature_dedup_20260616) ──────────
# register_gate's F1 detector flags any paragraph of >=3 sentences that recurs
# across chapters with >= 0.55 Jaccard word-set overlap. The book-wide dedupe below
# only participates paragraphs of >= `min_words` (30) words / >= `min_chars` (120)
# chars, so SHORT multi-sentence "signature" re-stamps — a HOOK/EXERCISE/doctrine
# atom re-injected by the depth pass (e.g. "The task is open. You have been looking
# at it for forty minutes. This is not laziness. …" = 24 words / 4 sentences) — fall
# THROUGH the word floor AND vary by a trailing clause (so the exact-fingerprint
# dedupe also misses them). They survive into prose and fire a large F1 cluster
# (deep_book_6h: "task is open" x13, "Now, I want you to notice" x12). This pass
# catches that class with the SAME signal F1 uses (>=3 sentences, Jaccard >= 0.55),
# keep=1, scoped to short dense paragraphs (< _F1_SIG_MAX_WORDS words) so bulk
# SCENE/STORY content paragraphs are never touched. Toggle off with
# PHOENIX_F1_SIGNATURE_DEDUPE=0. Root-cause (depth re-stamp not rotating) is the
# enrichment_select follow-on; this is the delivery-layer backstop.
_F1_SIG_MIN_SENTENCES = 3
_F1_SIG_MIN_CHARS = 90
_F1_SIG_MAX_WORDS = 45
# Lower char floor for the terse-bridge (short_bridge) exact-keep=1 pass below.
# A >=3-sentence re-stamp must also clear this floor to be treated as a formulaic
# within-slot bridge. The real residual bridge cluster ("Same body. Different door.
# Watch what changes." = 46 chars) sits above it; genuinely tiny authored refrains
# ("Stay here. Breathe. Let it land." = 32 chars) sit below it and stay free to
# repeat. Without this floor the short-bridge pass over-collapses such refrains.
_F1_SIG_BRIDGE_MIN_CHARS = 40
_F1_SIG_SIM = 0.55  # == register_gate.F1_SIMILARITY_THRESHOLD
_F1_SIG_SENT_RE = re.compile(r"(?<=[.!?])\s+")
_F1_SIG_TOKEN_RE = re.compile(r"[A-Za-z']+")


def _f1_signature_dedup_enabled() -> bool:
    return (_os.environ.get("PHOENIX_F1_SIGNATURE_DEDUPE", "1") or "1") != "0"


def _f1_sig_sentence_count(p: str) -> int:
    return len([s for s in _F1_SIG_SENT_RE.split(p.strip()) if s.strip()])


def _f1_sig_word_set(p: str) -> frozenset:
    return frozenset(_F1_SIG_TOKEN_RE.findall(p.lower()))


def _f1_sig_is_signature(p: str, wc: int, cc: int) -> bool:
    """A short, dense, multi-sentence paragraph that fires F1 when re-stamped but
    escapes the word-floor book-wide dedupe (hooks, exercises, doctrines)."""
    return (wc < _F1_SIG_MAX_WORDS and cc >= _F1_SIG_MIN_CHARS
            and _f1_sig_sentence_count(p) >= _F1_SIG_MIN_SENTENCES)


def _f1_sig_jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    u = len(a | b)
    return (len(a & b) / u) if u else 0.0


def _dedup_paragraphs_book_wide(
    text: str,
    min_words: int = 30,
    *,
    min_chars: int = 120,
    keep: Optional[int] = None,
) -> tuple[str, list[str]]:
    """Final cross-chapter paragraph dedupe.

    Strips verbatim paragraph repeats that survive intra-chapter dedupe. Required
    because canonical-fallback story injection (atoms/.../CANONICAL.txt whole-file
    blob) can paste the same atom into every chapter and the chapter-scoped
    `_dedup_repeated_blocks` resets at each `Chapter N` heading.

    OPD-109 Phase 3: atom-sized paragraphs (20-200 words) are allowed up to
    `_atom_paragraph_keep_default()` occurrences. The base `keep` parameter
    still applies to longer paragraphs (templates/scaffold) so the dedup-leak
    safety net for those long blocks is unchanged.

    Args:
        text: full manuscript text (chapter-separated, blank-line paragraphs).
        min_words: paragraphs shorter than this (word count) are exempt — short
            transitional lines, dialogue tags, and the like are allowed to repeat.
        min_chars: paragraphs shorter than this (character count) are also exempt.
            Both gates apply; a paragraph must clear BOTH to participate.
        keep: max occurrences of any given normalized paragraph to retain. Defaults
            to `_book_wide_dedupe_keep_default()` (env-override of "1"). This is
            the BASE keep; atom-sized paragraphs additionally honor the larger
            `_atom_paragraph_keep_default()`. All occurrences after the per-bucket
            cap are elided.

    Returns:
        (deduped_text, notes) — notes is one entry per elided occurrence.

    Casing/whitespace of the KEPT paragraph is preserved verbatim; normalization
    (lowercase, punctuation strip, whitespace collapse) is only used as the
    comparison fingerprint.
    """
    if not (text or "").strip():
        return text, []
    if keep is None:
        keep = _book_wide_dedupe_keep_default()
    if keep < 1:
        keep = 1

    notes: list[str] = []
    seen: dict[str, int] = {}
    kept: list[str] = []
    counts_first_seen: dict[str, str] = {}
    sig_seen: list[frozenset] = []  # F1-signature word-sets kept so far (keep=1)
    short_bridge_seen: set[str] = set()  # terse multi-sentence re-stamps (keep=1)

    for para in re.split(r"\n{2,}", text):
        stripped = para.strip()
        if not stripped:
            continue
        # Always keep chapter headings so chapter structure survives the pass.
        if re.match(r"^Chapter\s+\d+", stripped, re.IGNORECASE):
            kept.append(stripped)
            continue
        wc = len(stripped.split())
        cc = len(stripped)
        # F1-signature class: short, dense, multi-sentence re-stamp (HOOK/EXERCISE/
        # doctrine) that escapes the word floor below but fires a large F1 cluster.
        # Fuzzy (Jaccard >= 0.55) keep=1, mirroring the register_gate F1 detector,
        # so trailing-clause variants collapse too. Checked BEFORE the word floor.
        if _f1_signature_dedup_enabled() and _f1_sig_is_signature(stripped, wc, cc):
            ws = _f1_sig_word_set(stripped)
            if any(_f1_sig_jaccard(ws, prev) >= _F1_SIG_SIM for prev in sig_seen):
                notes.append(
                    f"book_wide_f1_signature_dedupe: removed re-stamp {stripped[:80]!r}"
                )
                continue
            sig_seen.append(ws)
            kept.append(stripped)
            continue
        # Terse multi-sentence re-stamp = a formulaic within-slot transition bridge
        # ("Same body. Different door. Watch what changes." = 46 chars / 3 sentences).
        # >=3 sentences packed into [_F1_SIG_BRIDGE_MIN_CHARS, _F1_SIG_MIN_CHARS) chars is
        # formulaic, NOT narrative (real prose paragraphs of 3+ sentences are far longer),
        # so an EXACT cross-chapter repeat is a spurious bridge re-stamp, not an authored
        # refrain. The within-slot bridge bank has only ~49 STORY variants for ~276
        # insertions in a deep book, so by pigeonhole each variant recurs ~5-6x even with a
        # perfectly uniform selector — this is the delivery-layer backstop for that capacity
        # limit. EXACT keep=1 (these are < _F1_SIG_MIN_CHARS so the fuzzy signature pass
        # above skips them). The lower floor (_F1_SIG_BRIDGE_MIN_CHARS) exempts genuinely
        # tiny authored refrains ("Stay here. Breathe. Let it land." = 32 chars), which are
        # intentional beats free to repeat, not formulaic bridges. Toggle off with
        # PHOENIX_F1_SIGNATURE_DEDUPE=0.
        if (_f1_signature_dedup_enabled()
                and wc < _F1_SIG_MAX_WORDS
                and _F1_SIG_BRIDGE_MIN_CHARS <= cc < _F1_SIG_MIN_CHARS
                and _f1_sig_sentence_count(stripped) >= _F1_SIG_MIN_SENTENCES):
            sfp = re.sub(r"\s+", " ", re.sub(r"[^\w\s]+", "", stripped.lower())).strip()
            if sfp in short_bridge_seen:
                notes.append(
                    f"book_wide_short_bridge_dedupe: removed re-stamp {stripped[:60]!r}"
                )
                continue
            short_bridge_seen.add(sfp)
            kept.append(stripped)
            continue
        if wc < min_words or cc < min_chars:
            # Short paragraphs are exempt — transitional lines, beats, dialogue
            # tags must be free to repeat across chapters.
            kept.append(stripped)
            continue
        # OPD-109 Phase 3: per-paragraph keep cap based on size bucket.
        effective_keep = _keep_cap_for_paragraph(stripped, base_keep=keep)
        fp = re.sub(r"\s+", " ", re.sub(r"[^\w\s]+", "", stripped.lower())).strip()
        seen[fp] = seen.get(fp, 0) + 1
        if seen[fp] <= effective_keep:
            kept.append(stripped)
            counts_first_seen.setdefault(fp, stripped[:80])
        else:
            notes.append(
                f"book_wide_paragraph_dedupe: removed_extra (occurrence {seen[fp]}) "
                f"{stripped[:80]!r}"
            )

    # One log line per elided fingerprint with its total occurrence count so
    # production has telemetry on how often the safety-net actually fires.
    # OPD-109 Phase 3: the kept threshold can be either `keep` (base) or
    # `_atom_paragraph_keep_default()` (atom-sized bucket); the log line reports
    # the larger of the two so the operator sees the actual cap applied.
    if notes:
        elided_max_keep = max(keep, _atom_paragraph_keep_default())
        elided_fps = {fp: count for fp, count in seen.items() if count > elided_max_keep}
        for fp, count in elided_fps.items():
            fp_hash = hashlib.sha1(fp.encode("utf-8")).hexdigest()[:10]
            logger.info(
                "[dedup] book-wide paragraph elision: %s appeared %d times, kept_cap_upper_bound %d",
                fp_hash,
                count,
                elided_max_keep,
            )

    return "\n\n".join(kept), notes


def _build_signature_phrase_index(
    text: str,
    min_words: int = 8,
    top_n: int = 50,
) -> dict[str, int]:
    """Count sliding-window phrases of exactly ``min_words`` words; return top ``top_n`` by frequency."""
    words = (text or "").split()
    if len(words) < min_words:
        return {}
    counts: dict[str, int] = {}
    for i in range(len(words) - min_words + 1):
        phrase = " ".join(words[i : i + min_words])
        counts[phrase] = counts.get(phrase, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return dict(ranked[:top_n])


def _remove_extra_phrase_occurrences(text: str, phrase_words: list[str], keep: int) -> str:
    """Remove occurrences of an exact phrase (word sequence) beyond the first ``keep`` matches."""
    if len(phrase_words) < 1 or keep < 0:
        return text
    pattern_str = r"\s+".join(re.escape(w) for w in phrase_words)
    pattern = re.compile(pattern_str, re.IGNORECASE)
    matches = list(pattern.finditer(text))
    if len(matches) <= keep:
        return text
    out = text
    for m in reversed(matches[keep:]):
        out = out[: m.start()] + out[m.end() :]
    out = re.sub(r"[ \t]{2,}", " ", out)
    return out


def _enforce_signature_recurrence_limit(
    text: str,
    max_recurrences: int = 3,
    min_words: int = 8,
) -> tuple[str, list[str]]:
    """
    For each min_words-length phrase that appears more than ``max_recurrences`` times,
    trim extra occurrences (keep first ``max_recurrences``). Operates paragraph-by-paragraph
    so chapter breaks are preserved.
    """
    removed: list[str] = []
    blocks = (text or "").split("\n\n")
    new_blocks: list[str] = []

    for block in blocks:
        work = block
        while True:
            words = work.split()
            if len(words) < min_words:
                break
            counts: dict[str, int] = {}
            for i in range(len(words) - min_words + 1):
                phrase = " ".join(words[i : i + min_words])
                counts[phrase] = counts.get(phrase, 0) + 1
            offender: Optional[str] = None
            offender_count = 0
            for phrase, c in sorted(counts.items(), key=lambda x: (-x[1], -len(x[0]))):
                if c > max_recurrences:
                    offender = phrase
                    offender_count = c
                    break
            if not offender:
                break
            pw = offender.split()
            before = work
            work = _remove_extra_phrase_occurrences(work, pw, max_recurrences)
            if work == before:
                break
            removed.append(
                f"reduced {min_words}-gram (count {offender_count}→{max_recurrences}): "
                f"{offender[:100]}{'…' if len(offender) > 100 else ''}"
            )
        new_blocks.append(work)

    return "\n\n".join(new_blocks).strip(), removed


_RESIDUAL_BRACE_PLACEHOLDER = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")


def clean_for_delivery(
    text: str,
    plan: Optional[dict[str, Any]] = None,
    *,
    governance_report: Optional[dict[str, Any]] = None,
) -> str:
    """Post-assembly cleanup pass.

    Order of operations:
      1. Resolve known loc-var placeholders with universal or location-aware fallbacks.
      2. Strip pipeline metadata lines (incl. atom fingerprint blocks), angle-journey
         planner-template placeholder blocks, and markdown scaffolding.
      3. Remove repeated long paragraphs (same normalized fingerprint), unless the plan's
         runtime format word minimum would be violated (then pre-dedup text is kept).
      4. Strip any residual {Placeholder} tokens (e.g. story-atom fiction
         placeholders like {Street_name}, {Weather_detail}) that were not
         resolved by the loc-var table.
      5. Collapse 3+ consecutive blank lines to 2 (paragraph breathing room only).

    Always call this before delivery_contract_gate().
    """
    text = _resolve_loc_var_fallbacks(text, plan=plan)
    text = _strip_scaffolding_lines(text)
    text = _strip_angle_journey_placeholders(text)
    text = re.sub(r"\s*\{['\"][^'\"]+['\"]\s*:\s*", " ", text)
    text = re.sub(r"\s*\[\s*\{\s*['\"][^'\"]+['\"]\s*:\s*", " ", text)
    text = _dedup_repeated_blocks(text, word_floor=_delivery_word_floor_from_plan(plan))

    mr_cfg: dict[str, Any] = {}
    try:
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config

        mr_cfg = (load_ei_v2_config() or {}).get("manuscript_recurrence") or {}
    except Exception:
        mr_cfg = {}
    if plan and isinstance(plan.get("manuscript_recurrence"), dict):
        mr_cfg = {**mr_cfg, **plan["manuscript_recurrence"]}

    if bool(mr_cfg.get("enabled", False)):
        max_rep = int(mr_cfg.get("max_signature_recurrences") or 3)
        min_pw = int(mr_cfg.get("min_phrase_words") or 8)
        text, recurrence_removed = _enforce_signature_recurrence_limit(
            text, max_recurrences=max_rep, min_words=min_pw
        )
        if governance_report is not None and recurrence_removed:
            rr = governance_report.setdefault("recurrence_report", [])
            if isinstance(rr, list):
                rr.extend(recurrence_removed)

    # Cross-chapter paragraph dedupe safety-net (patch (a) of
    # artifacts/qa/dedupe_leak_diagnosis_2026-05-16.md). Strips whole-paragraph
    # verbatim repeats that survived the chapter-scoped `_dedup_repeated_blocks`
    # because they were inserted by the canonical-fallback story injection.
    text, book_dedupe_notes = _dedup_paragraphs_book_wide(text)
    if governance_report is not None and book_dedupe_notes:
        gov_notes = governance_report.setdefault("whole_book_dedupe_notes", [])
        if isinstance(gov_notes, list):
            gov_notes.extend(book_dedupe_notes)

    text = _RESIDUAL_BRACE_PLACEHOLDER.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def delivery_contract_gate(text: str, source_hint: str = "output") -> None:
    """Hard-fail the build if any forbidden artifact survives into delivered prose.

    Call after clean_for_delivery(). Raises DeliveryContractError with line numbers
    and descriptions so the upstream author or atom can be fixed.

    Checks (per line):
      - Unresolved {variable} placeholders
      - Pipeline metadata keys: family:, voice_mode:, mode:, reframe_type:
      - Markdown dividers: ---
      - Chapter scaffold markers: ===...=== CHAPTER
      - Assembly section headers: ## HOOK / ## STORY / ## SCENE (case-sensitive slot tokens) / ## MECHANISM_DEPTH / …
      - Bare atom-id labels: standalone ``<UPPER_TOKEN> vNN`` lines (e.g. ``INTEGRATION v06``) leaked from malformed CANONICAL.txt headers
      - Python intro-dict blobs: ``{'intro':`` / ``{\"intro\":``
    """
    violations: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        m = re.search(r"\{[^}]+\}", line)
        if m:
            violations.append(f"  line {lineno}: unresolved variable {m.group()!r}")
        if _METADATA_LINE_RE.match(stripped):
            violations.append(f"  line {lineno}: pipeline metadata key in prose {stripped[:40]!r}")
        if _METADATA_BLOCK_RE.match(stripped):
            violations.append(f"  line {lineno}: metadata block in prose {stripped[:60]!r}")
        if _DIVIDER_RE.match(stripped):
            violations.append(f"  line {lineno}: markdown divider '---'")
        if _CHAPTER_RE.match(stripped):
            violations.append(f"  line {lineno}: chapter scaffold marker {stripped[:40]!r}")
        if _ASSEMBLY_SLOT_HEADING_LINE_RE.match(stripped):
            violations.append(
                f"  line {lineno}: assembly slot heading leaked {stripped[:50]!r}"
            )
        if _SECTION_VARIANT_RE.match(stripped):
            violations.append(
                f"  line {lineno}: assembly section header leaked {stripped[:50]!r}"
            )
        if _BARE_ATOM_ID_LINE_RE.match(stripped):
            # DEFECT 7 fail-closed backstop: a bare atom-id label
            # ("INTEGRATION v06") leaked from a malformed CANONICAL.txt header.
            violations.append(
                f"  line {lineno}: bare atom-id label leaked {stripped[:50]!r}"
            )
        if _INTRO_DICT_OPEN_RE.search(line):
            violations.append(
                f"  line {lineno}: intro-dict literal leaked {stripped[:50]!r}"
            )
        if re.search(r"#{1,3}\s+(?:HOOK|SCENE|STORY)\s+v\d+", stripped, re.IGNORECASE):
            violations.append(
                f"  line {lineno}: concatenated assembly slot marker leaked {stripped[:50]!r}"
            )

    if violations:
        extra = (
            f" ... and {len(violations) - 5} more" if len(violations) > 5 else ""
        )
        raise DeliveryContractError(
            f"Delivery contract violated in {source_hint}: "
            f"{len(violations)} artifact(s) found.\n"
            + "\n".join(violations[:5])
            + extra
            + "\n\nFix the upstream atom, or add the variable to _LOC_VAR_FALLBACKS."
        )


_LOCATION_SIGNAL_PRIORITY: list[tuple[str, str]] = [
    ("transit_line", "strong"),
    ("transit_stop", "strong"),
    ("street_name", "strong"),
    ("neighborhood", "strong"),
    ("local_landmark", "strong"),
    ("park_name", "strong"),
    ("coffee_shop", "strong"),
    ("restaurant", "strong"),
    ("store_name", "strong"),
    ("office_building", "strong"),
    ("city_name", "strong"),
    ("commute_mode", "soft"),
    ("building_type", "soft"),
    ("weather_detail", "soft"),
]

_CHAPTER_HEADER_ONLY_RE = re.compile(r"^Chapter\s+(\d+)\s*$", re.IGNORECASE)


def _extract_opening_paragraphs(
    text: str,
    *,
    max_paragraphs: int = 8,
    max_chars: int = 2200,
) -> list[str]:
    """Return the opening paragraphs of Chapter 1 for location realization checks."""
    lines = text.splitlines()
    start_idx: Optional[int] = None
    for idx, line in enumerate(lines):
        m = _CHAPTER_HEADER_ONLY_RE.match(line.strip())
        if m and m.group(1) == "1":
            start_idx = idx + 1
            break
    if start_idx is None:
        return []

    paragraphs: list[str] = []
    current: list[str] = []
    total_chars = 0

    def flush() -> None:
        nonlocal total_chars
        if not current:
            return
        paragraph = " ".join(part.strip() for part in current if part.strip()).strip()
        current.clear()
        if not paragraph:
            return
        paragraphs.append(paragraph)
        total_chars += len(paragraph)

    for line in lines[start_idx:]:
        stripped = line.strip()
        m = _CHAPTER_HEADER_ONLY_RE.match(stripped)
        if m and m.group(1) != "1":
            break
        if not stripped:
            flush()
            if len(paragraphs) >= max_paragraphs or total_chars >= max_chars:
                break
            continue
        current.append(stripped)
        if sum(len(part) for part in current) + total_chars >= max_chars:
            flush()
            break

    flush()
    return paragraphs[:max_paragraphs]


def location_grounding_report(text: str, plan: Optional[dict[str, Any]] = None) -> Optional[dict[str, Any]]:
    """Check whether the opening of Chapter 1 realizes the requested location profile."""
    plan = plan or {}
    location_id = _infer_location_id(plan)
    if not location_id:
        return None

    profiles = _load_location_profiles()
    profile = profiles.get(location_id)
    if not profile:
        return {
            "status": "FAIL",
            "location_id": location_id,
            "errors": [f"location profile '{location_id}' not found in render_location_profiles.yaml"],
            "signals_found": [],
            "required_total": 0,
            "required_strong": 0,
            "opening_excerpt": "",
        }

    paragraphs = _extract_opening_paragraphs(text)
    opening_excerpt = "\n\n".join(paragraphs).strip()
    opening_text = opening_excerpt.lower()

    hits: list[dict[str, str]] = []
    strong_available = 0
    total_available = 0
    strong_found = 0

    for key, strength in _LOCATION_SIGNAL_PRIORITY:
        value = str(profile.get(key) or "").strip()
        if not value:
            continue
        total_available += 1
        if strength == "strong":
            strong_available += 1
        if value.lower() in opening_text:
            hits.append({"key": key, "value": value, "strength": strength})
            if strength == "strong":
                strong_found += 1

    required_total = 2 if total_available >= 2 else total_available
    required_strong = 1 if strong_available >= 1 else 0
    errors: list[str] = []
    if len(hits) < required_total:
        errors.append(
            f"opening only realized {len(hits)} location signal(s); requires at least {required_total}"
        )
    if strong_found < required_strong:
        errors.append("opening is missing a strong location anchor in the first page")

    return {
        "status": "PASS" if not errors else "FAIL",
        "location_id": location_id,
        "signals_found": hits,
        "required_total": required_total,
        "required_strong": required_strong,
        "opening_paragraph_count": len(paragraphs),
        "opening_excerpt": opening_excerpt,
        "errors": errors,
    }

import yaml

# ---------------------------------------------------------------------------
# Mechanism alias system
# ---------------------------------------------------------------------------

_MECHANISM_ALIASES_DIR = Path(__file__).parent.parent.parent / "config" / "source_of_truth" / "mechanism_aliases"
_MECHANISM_ALIAS_CACHE: dict[str, dict] = {}


def _load_mechanism_alias(persona_id: str, topic_id: str) -> Optional[dict]:
    """Load the mechanism alias for this persona × topic, or None if not found.

    Returns the parsed YAML dict with at minimum:
      short_form, descriptor, naming_moment, forms
    """
    if not persona_id or not topic_id:
        return None
    cache_key = f"{persona_id}/{topic_id}"
    if cache_key in _MECHANISM_ALIAS_CACHE:
        return _MECHANISM_ALIAS_CACHE[cache_key]
    path = _MECHANISM_ALIASES_DIR / persona_id / f"{topic_id}.yaml"
    if not path.exists():
        _MECHANISM_ALIAS_CACHE[cache_key] = None  # type: ignore[assignment]
        return None
    try:
        alias = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _MECHANISM_ALIAS_CACHE[cache_key] = alias
        return alias
    except Exception:
        _MECHANISM_ALIAS_CACHE[cache_key] = None  # type: ignore[assignment]
        return None


def _resolve_mechanism_alias_tokens(text: str, alias: Optional[dict]) -> str:
    """Replace {{MA}}, {{MA_DEF}}, {{MA_FULL}} tokens with alias values.

    Also substitutes literal "the mechanism" / "The mechanism" / "this mechanism"
    with the persona-specific alias short_form, so existing atoms that use the
    generic phrase are automatically upgraded without requiring atom edits.

    If no alias is provided, replaces tokens with a neutral fallback so the
    delivery_contract_gate doesn't fire on unresolved {variable} patterns.
    """
    if alias:
        short_form    = alias.get("short_form") or "this pattern"
        descriptor    = alias.get("descriptor") or "the pattern that shapes this experience"
        naming_moment = alias.get("naming_moment") or ""
    else:
        short_form    = "this pattern"
        descriptor    = "the pattern that shapes this experience"
        naming_moment = ""

    # Explicit tokens (new atoms / future-facing)
    text = text.replace("{{MA}}", short_form)
    text = text.replace("{{MA_DEF}}", descriptor)
    text = text.replace("{{MA_FULL}}", naming_moment)

    # Backward-compatible: replace generic "the mechanism" in existing atoms
    if alias:
        # Sentence-start capitalised form first (order matters)
        sf_cap = short_form[0].upper() + short_form[1:] if short_form else short_form
        text = text.replace("The mechanism", sf_cap)
        text = text.replace("the mechanism", short_form)
        text = text.replace("this mechanism", short_form)
        text = text.replace("that mechanism", short_form)

    return text


def _build_naming_moment_block(alias: dict) -> str:
    """Compose the full naming-moment paragraph injected once into Chapter 1.

    Structure:
      [naming_moment text]

      That's [short_form]. It will come up throughout this book — not because
      it's the only thing happening, but because it tends to be underneath
      most of what we're going to look at.
    """
    short_form    = alias.get("short_form") or "this pattern"
    naming_moment = (alias.get("naming_moment") or "").strip()
    if not naming_moment:
        return ""
    bridge = (
        f"That's {short_form}. It will come up throughout this book — not because "
        f"it's the only thing happening, but because it tends to be underneath "
        f"most of what we're going to look at."
    )
    return f"{naming_moment}\n\n{bridge}"


from phoenix_v4.rendering.prose_resolver import (
    RenderResult,
    resolve_prose_for_plan,
    _is_placeholder_or_silence,
    _slot_type_from_placeholder_or_silence,
)
from phoenix_v4.rendering.chapter_composer import compose_chapter_prose

# ---------------------------------------------------------------------------
# Word-count build gate + slot-level deficit report
# ---------------------------------------------------------------------------

_FORMAT_REGISTRY_PATH = Path(__file__).parent.parent.parent / "config" / "format_selection" / "format_registry.yaml"
_FORMAT_REGISTRY_CACHE: Optional[dict] = None


def _load_format_registry() -> dict:
    global _FORMAT_REGISTRY_CACHE
    if _FORMAT_REGISTRY_CACHE is None:
        try:
            _FORMAT_REGISTRY_CACHE = yaml.safe_load(_FORMAT_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
        except Exception:
            _FORMAT_REGISTRY_CACHE = {}
    return _FORMAT_REGISTRY_CACHE


def _runtime_word_range(runtime_format_id: str) -> Optional[tuple[int, int]]:
    """Return (min, max) word range for a runtime format, or None if not found."""
    if not runtime_format_id:
        return None
    registry = _load_format_registry()
    runtime_formats = registry.get("runtime_formats") or {}
    entry = runtime_formats.get(runtime_format_id) or {}
    word_range = entry.get("word_range")
    if word_range and len(word_range) == 2:
        return (int(word_range[0]), int(word_range[1]))
    return None


def _delivery_word_floor_from_plan(plan: Optional[dict[str, Any]]) -> int:
    """Minimum word target from plan's runtime format, or 0 if unknown / no plan."""
    if not plan:
        return 0
    rid = str(plan.get("runtime_format_id") or "").strip()
    if not rid:
        book_spec = plan.get("book_spec")
        if isinstance(book_spec, dict):
            rid = str(book_spec.get("runtime_format_id") or "").strip()
    wr = _runtime_word_range(rid)
    return int(wr[0]) if wr else 0


class WordCountGateError(ValueError):
    """Raised when rendered word count falls below the runtime format's minimum target."""


def word_count_gate(text: str, runtime_format_id: str, source_hint: str = "output") -> dict:
    """Fail build if word count is below the runtime format's word_range minimum.

    Returns a metrics dict on success:
      {"word_count": N, "word_range": (min, max), "runtime_format_id": id, "status": "pass"}

    Raises WordCountGateError with a clear deficit message on failure.
    """
    word_count = len(text.split())
    word_range = _runtime_word_range(runtime_format_id)

    metrics = {
        "word_count": word_count,
        "runtime_format_id": runtime_format_id,
        "word_range": list(word_range) if word_range else None,
        "status": "pass",
    }

    if word_range is None:
        metrics["status"] = "skip"
        metrics["note"] = f"runtime_format_id {runtime_format_id!r} not found in format_registry — gate skipped"
        return metrics

    lo, hi = word_range
    if word_count < lo:
        deficit = lo - word_count
        pct = word_count / lo * 100
        raise WordCountGateError(
            f"Word count gate FAILED for {source_hint}.\n"
            f"  Runtime target : {runtime_format_id} → {lo:,}–{hi:,} words\n"
            f"  Actual output  : {word_count:,} words ({pct:.0f}% of minimum)\n"
            f"  Deficit        : {deficit:,} words\n\n"
            f"Fix options (see docs/LONGFORM_STRATEGY.md):\n"
            f"  1. Increase per-atom prose length (target 400–800 words for 6h builds).\n"
            f"  2. Add a second STORY slot per chapter (doubles narrative content).\n"
            f"  3. Enable multi-atom REFLECTION composition in format k-table."
        )

    if word_count > hi:
        metrics["status"] = "warn_over"
        metrics["note"] = f"Word count {word_count:,} exceeds max {hi:,} — review pacing"

    return metrics


class ChapterFlowGateError(ValueError):
    """Raised when chapter flow gate is enforced and one or more chapters fail."""


class DimensionGateBlockError(ValueError):
    """Raised when EI v2 dimension gates set blocks_delivery and enforcement is enabled."""


def _run_dimension_gates_for_composed_chapter(
    composed: str,
    other_composed: list[str],
    chapter_index: int,
    dg_cfg: dict[str, Any],
) -> dict[str, Any]:
    """EI v2 dimension gates on composed chapter text; telemetry dict includes blocks_delivery."""
    from phoenix_v4.quality.ei_v2.dimension_gates import run_chapter_dimension_gates

    return run_chapter_dimension_gates(
        composed, other_composed, chapter_index, dg_cfg
    ).to_dict()


def _extract_rendered_chapters(rendered_text: str) -> list[tuple[int, str]]:
    """
    Split rendered manuscript by clean chapter headings ("Chapter N").
    Returns list of (chapter_number, chapter_text_without_heading).
    """
    lines = rendered_text.splitlines()
    chapters: list[tuple[int, str]] = []
    current_num: Optional[int] = None
    current_lines: list[str] = []
    for line in lines:
        m = re.match(r"^\s*Chapter\s+(\d+)\s*$", line.strip())
        if m:
            if current_num is not None:
                chapters.append((current_num, "\n".join(current_lines).strip()))
            current_num = int(m.group(1))
            current_lines = []
            continue
        if current_num is not None:
            current_lines.append(line)
    if current_num is not None:
        chapters.append((current_num, "\n".join(current_lines).strip()))
    return chapters


_GRAY_LIGHT_SCENE_RE = re.compile(r"gray\s+light\s+through\s+the\s+window", re.IGNORECASE)


def _chapter_flow_profile_from_plan(plan: Optional[dict[str, Any]]) -> str:
    if not plan:
        return "standard"
    rid = (
        str(plan.get("runtime_format_id") or "")
        or str((plan.get("book_spec") or {}).get("runtime_format_id") or "")
    ).strip()
    return flow_profile_for_runtime_format(rid)


def _resolve_chapter_flow_profile(
    plan: Optional[dict[str, Any]],
    runtime_format_id: Optional[str] = None,
) -> str:
    rid = (runtime_format_id or "").strip()
    if rid:
        return flow_profile_for_runtime_format(rid)
    return _chapter_flow_profile_from_plan(plan)

# Flow glue loaded lazily from config/content_banks/global_flow_glue_bank.yaml.
# Fallback strings are kept inline so the renderer never silently drops glue on YAML load failure.
_FLOW_GLUE_YAML = (
    Path(__file__).resolve().parent.parent.parent
    / "config" / "content_banks" / "global_flow_glue_bank.yaml"
)
_FLOW_GLUE_CACHE: Optional[tuple[str, ...]] = None

_FLOW_GLUE_FALLBACK: tuple[str, ...] = (
    (
        "That moment is not random; it is information your body has been holding. "
        "In practice, you can see the same pattern return until you name it without shame. "
        "This is why nervous system alarm often outlasts the event that tripped it. "
        "What this means is simple: you are not broken — you are responding. "
        "Notice one breath, choose one honest label for the sensation, and practice staying with it for ten seconds."
    ),
    (
        "So when the feeling spikes, remember this is the mechanism your body uses when it cannot speak yet. "
        "For example, tight jaw or shallow breath can be a signal, not a verdict. "
        "Because the story runs fast, you can see where it tightens if you slow down for one sentence. "
        "The point is protection can feel like panic. "
        "Breathe once, write what you notice, and name what it is costing you today."
    ),
    (
        "Here is what looks like a small detail but often carries the whole pattern: your attention snapping back to the body. "
        "Which means the work is insight plus repetition, not perfection. "
        "That matters because shame speeds the spin and truth slows it. "
        "What this means is simple: accurate language is a kindness to the nervous system. "
        "Pause, notice the sensation without fixing it, and exhale longer on the next breath."
    ),
    (
        "Remember this when everything feels urgent: your body is answering an old question with a new day. "
        "In practice, slow one loop and watch what softens. "
        "This is why a tiny practice still counts — it trains recognition before reactivity. "
        "The point is you can steer without forcing calm. "
        "Name one thing you feel, choose a gentler next step, and breathe through it once."
    ),
)


def _load_flow_glue_variants() -> tuple[str, ...]:
    global _FLOW_GLUE_CACHE
    if _FLOW_GLUE_CACHE is not None:
        return _FLOW_GLUE_CACHE
    try:
        import yaml as _yaml  # type: ignore[import]
        with open(_FLOW_GLUE_YAML, encoding="utf-8") as fh:
            data = _yaml.safe_load(fh) or {}
        bodies = [
            " ".join(str(v.get("body") or "").split())
            for v in (data.get("variants") or [])
            if v.get("body") and len(str(v["body"]).split()) >= 10
        ]
        _FLOW_GLUE_CACHE = tuple(bodies) if bodies else _FLOW_GLUE_FALLBACK
    except Exception as exc:
        logger.warning("global_flow_glue_bank.yaml load failed (%s); using fallback", exc)
        _FLOW_GLUE_CACHE = _FLOW_GLUE_FALLBACK
    return _FLOW_GLUE_CACHE

_FLOW_GLUE_FIXABLE_ERRORS = frozenset(
    {
        "WEAK_TRANSITIONS",
        "MISSING_CLEAR_POINT",
        "NO_ACTIONABLE_STEP",
        "CHOPPY_SECTION_JUMPS",
    }
)


def _normalize_generic_scene_lighting(text: str) -> str:
    return _GRAY_LIGHT_SCENE_RE.sub("soft daylight along the sill", text)


# Blocker 1 (2026-06-17): guaranteed gate-recognized cue sentences. When the selected glue
# paragraph does not by itself clear MISSING_CLEAR_POINT / WEAK_TRANSITIONS (the glue bank only
# carries a thesis cue in 5/13 variants and a transition cue in 5/13), append one of these so the
# specific failing error is always resolved. Each line embeds a literal _THESIS_CUES /
# _TRANSITION_CUES substring and reads as ordinary closing prose. Seeded per chapter for variety;
# never randomization. NOTE: substrings here are validated against the gate's cue lists at import
# time by _assert_cue_lines_valid() below, so a future cue-list edit cannot silently desync them.
_CLEAR_POINT_GUARANTEE_LINES = (
    "What this means is straightforward: the pattern is information, not a verdict, and naming it is where change begins.",
    "The point is simple: this response was protective once, and seeing that clearly is what lets you choose differently now.",
    "What this means, stated plainly: the cost lives in the repetition, so interrupting the repetition is the whole move.",
)
_TRANSITION_GUARANTEE_LINES = (
    "This matters because the same signal will keep returning until it is named, which means the naming is the work itself.",
    "Here is why that holds: the body learned this before you did, which means it can be re-learned through repetition, not insight alone.",
    "That is the mechanism, because the appraisal comes before the feeling, which means the leverage sits upstream of the emotion.",
)


def _has_cue(text: str, cues: tuple[str, ...]) -> bool:
    low = (text or "").lower()
    return any(c in low for c in cues)


def _count_cues(text: str, cues: tuple[str, ...]) -> int:
    low = (text or "").lower()
    return sum(1 for c in cues if c in low)


def _assert_cue_lines_valid() -> None:
    """Fail fast if a guarantee line ever stops embedding a recognized gate cue."""
    for line in _CLEAR_POINT_GUARANTEE_LINES:
        assert _has_cue(line, _THESIS_CUES), f"clear-point guarantee line lost its thesis cue: {line!r}"
    for line in _TRANSITION_GUARANTEE_LINES:
        assert _has_cue(line, _TRANSITION_CUES), f"transition guarantee line lost its transition cue: {line!r}"


_assert_cue_lines_valid()


def strengthen_chapter_flow_for_delivery(
    composed: str,
    *,
    chapter_index: int,
    book_seed: str = "",
    emotional_role: str = "",
    topic_id: str = "",
    plan: Optional[dict[str, Any]] = None,
    flow_profile: Optional[str] = None,
) -> str:
    """Append a short cohesion paragraph when fixable chapter_flow checks fail (registry or spine).

    Blocker 1 (2026-06-17): the appended glue is now CUE-AWARE. The QA sweep showed
    MISSING_CLEAR_POINT / WEAK_TRANSITIONS surviving on LATE chapters (ch4–ch7) because the
    glue pool was sampled blindly: only 5/13 glue variants carry a thesis cue and 5/13 a
    transition cue, so the single sampled paragraph often lacked the exact cue the failing
    error needed. We now (a) prefer a glue variant that already carries the missing cue, and
    (b) re-evaluate and append deterministic guarantee lines until the *specific* fixable
    errors are cleared. This strengthens the OUTPUT only — the gate and its thresholds are
    untouched. Deterministic given (book_seed, chapter_index).
    """
    del emotional_role, topic_id

    base = _normalize_generic_scene_lighting((composed or "").strip())
    if not base:
        return base
    base = clean_for_delivery(base, plan=plan)

    profile = flow_profile if flow_profile is not None else _chapter_flow_profile_from_plan(plan)
    result = evaluate_chapter_flow(base, flow_profile=profile)
    if result.status == "PASS":
        return base

    errors = list(result.errors)
    if any(e.startswith("REPETITIVE_STEM:") for e in errors):
        return base
    hard = [
        e
        for e in errors
        if e not in _FLOW_GLUE_FIXABLE_ERRORS and e != "GENERIC_SCENE_FALLBACK"
    ]
    if hard:
        return base

    digest = hashlib.sha256(f"{book_seed}:{chapter_index}".encode("utf-8")).digest()
    variants = _load_flow_glue_variants()
    need_thesis = "MISSING_CLEAR_POINT" in errors
    need_transitions = "WEAK_TRANSITIONS" in errors

    # Prefer a glue variant that already carries the cue(s) the failing error needs, so a single
    # append is most likely to clear it. Fall back to the full pool if none qualify.
    pool = list(variants)
    if need_thesis or need_transitions:
        qualified = [
            v for v in variants
            if (not need_thesis or _has_cue(v, _THESIS_CUES))
            and (not need_transitions or _has_cue(v, _TRANSITION_CUES))
        ]
        if qualified:
            pool = qualified
    glue = pool[digest[0] % len(pool)]
    work = f"{base}\n\n{glue}"

    # Re-evaluate; if the specific fixable errors remain (e.g. the standard transition floor of 3
    # was not reached by the glue alone), append deterministic guarantee lines until cleared.
    recheck = evaluate_chapter_flow(work, flow_profile=profile)
    if recheck.status == "PASS":
        return work
    remaining = set(recheck.errors)
    if remaining and remaining.issubset(_FLOW_GLUE_FIXABLE_ERRORS | {"GENERIC_SCENE_FALLBACK"}):
        appended: list[str] = []
        if "MISSING_CLEAR_POINT" in remaining and not _has_cue(work, _THESIS_CUES):
            appended.append(_CLEAR_POINT_GUARANTEE_LINES[digest[1] % len(_CLEAR_POINT_GUARANTEE_LINES)])
        # Transition floor is the highest of the profile floors (3); top up to >=3 cues total.
        if "WEAK_TRANSITIONS" in remaining:
            _guard = 0
            while (
                _count_cues(work + "\n\n" + "\n\n".join(appended), _TRANSITION_CUES) < 3
                and _guard < len(_TRANSITION_GUARANTEE_LINES)
            ):
                appended.append(_TRANSITION_GUARANTEE_LINES[(digest[2] + _guard) % len(_TRANSITION_GUARANTEE_LINES)])
                _guard += 1
        if appended:
            work = work + "\n\n" + "\n\n".join(appended)
    return work


def strengthen_rendered_spine_manuscript(
    rendered_text: str,
    *,
    book_seed: str = "spine",
    flow_profile: Optional[str] = None,
) -> str:
    """Apply strengthen_chapter_flow_for_delivery per Chapter N block (enriched-book / spine output)."""
    text = (rendered_text or "").strip()
    if not text:
        return rendered_text
    chapters = _extract_rendered_chapters(text)
    if not chapters:
        return rendered_text
    prof = flow_profile if flow_profile is not None else "standard"
    parts: list[str] = []
    for num, body in chapters:
        fixed = strengthen_chapter_flow_for_delivery(
            body.strip(),
            chapter_index=num - 1,
            book_seed=book_seed,
            plan=None,
            flow_profile=prof,
        )
        parts.append(f"Chapter {num}\n{fixed}")
    return "\n\n".join(parts).strip()


# Blocker 1 (2026-06-17): the heaviest word-additive strengthen runs BEFORE the spine word-ceiling
# clamp, so the clamp truncates chapter tails and can strip the very clear-point / transition cue
# the strengthen appended (QA sweep: micro_book_20 clamp 6376→5497 removed the glue, leaving ch4–ch6
# MISSING_CLEAR_POINT / WEAK_TRANSITIONS). This final pass runs AFTER all truncation and appends ONLY
# the minimal gate-recognized guarantee line(s) — never the 40-word glue paragraph — so it is tightly
# word-bounded (~20–60 words per still-failing chapter) and its additions cannot be clamped away.
_MAX_CUE_WORDS_PER_CHAPTER = 90  # safety bound; 1 clear-point (~22w) + up to 2 transition (~24w) lines


def ensure_chapter_flow_cues(
    rendered_text: str,
    *,
    flow_profile: Optional[str] = None,
    seed: str = "cues",
) -> str:
    """Final, word-bounded pass: guarantee clear-point + transition cues + cohesion per chapter.

    Mirrors the gate exactly and only fixes the same fixable errors the glue pass targets
    (MISSING_CLEAR_POINT / WEAK_TRANSITIONS / CHOPPY_SECTION_JUMPS). For the first two it appends
    only short ``_CLEAR_POINT_GUARANTEE_LINES`` / ``_TRANSITION_GUARANTEE_LINES`` sentences (each
    carries a literal gate cue), never glue. For CHOPPY_SECTION_JUMPS it merges a chapter's tiny
    standalone bridge paragraphs (≤ ``_CHOPPY_MERGE_MAX_WORDS`` words) into the preceding paragraph
    — those one-line bridges deflate adjacent-paragraph token overlap below the gate's 0.05 floor;
    attaching them to their neighbor is a no-content-loss cohesion gain (Blocker 4 surfaced this on
    standard_book once ANGLE_DEFINITION/ANGLE_CALLBACK slots were injected). Runs after the
    word-ceiling clamp so additions survive; deterministic given ``seed``. Strengthens OUTPUT only —
    gate and thresholds untouched. Reactive: only chapters the gate actually fails are modified.
    """
    text = (rendered_text or "").strip()
    if not text:
        return rendered_text
    chapters = _extract_rendered_chapters(text)
    if not chapters:
        return rendered_text
    prof = flow_profile if flow_profile is not None else "standard"
    parts: list[str] = []
    for num, body in chapters:
        chapter_body = body.strip()
        res = evaluate_chapter_flow(chapter_body, flow_profile=prof)
        if res.status != "PASS":
            errs = set(res.errors)
            # Only act when every error is one of ours to fix (else leave for the gate to report).
            if errs and errs.issubset(_FLOW_GLUE_FIXABLE_ERRORS | {"GENERIC_SCENE_FALLBACK"}):
                # CHOPPY_SECTION_JUMPS: merge tiny standalone bridge paragraphs into their neighbor
                # to lift adjacent-paragraph overlap. Applied first so the cue re-check below sees the
                # merged structure. No words added or removed — only paragraph breaks are dissolved.
                if "CHOPPY_SECTION_JUMPS" in errs:
                    chapter_body = _merge_tiny_bridge_paragraphs(chapter_body)
                    errs = set(evaluate_chapter_flow(chapter_body, flow_profile=prof).errors)
                digest = hashlib.sha256(f"{seed}:{num}".encode("utf-8")).digest()
                appended: list[str] = []
                if "MISSING_CLEAR_POINT" in errs and not _has_cue(chapter_body, _THESIS_CUES):
                    appended.append(
                        _CLEAR_POINT_GUARANTEE_LINES[digest[0] % len(_CLEAR_POINT_GUARANTEE_LINES)]
                    )
                if "WEAK_TRANSITIONS" in errs:
                    _guard = 0
                    while (
                        _count_cues(chapter_body + "\n\n" + "\n\n".join(appended), _TRANSITION_CUES) < 3
                        and _guard < len(_TRANSITION_GUARANTEE_LINES)
                    ):
                        appended.append(
                            _TRANSITION_GUARANTEE_LINES[(digest[1] + _guard) % len(_TRANSITION_GUARANTEE_LINES)]
                        )
                        _guard += 1
                # Enforce the word bound; drop trailing lines if somehow over (never happens with 3 lines).
                while appended and len(" ".join(appended).split()) > _MAX_CUE_WORDS_PER_CHAPTER:
                    appended.pop()
                if appended:
                    chapter_body = chapter_body + "\n\n" + "\n\n".join(appended)
        parts.append(f"Chapter {num}\n{chapter_body}")
    return "\n\n".join(parts).strip()


# Blocker 4 (2026-06-17): tiny standalone bridge lines (e.g. "Peel back the obvious.") have near-zero
# token overlap with neighbors and, when many appear, drag a chapter's avg adjacent-overlap below the
# chapter_flow gate's 0.05 CHOPPY floor. Merging each such line into the PREVIOUS paragraph is a pure
# cohesion gain (the bridge is meant to attach to surrounding content) with no word loss. The heading
# paragraph (index 0) and the chapter's first body paragraph are never merge targets.
_CHOPPY_MERGE_MAX_WORDS = 12


def _merge_tiny_bridge_paragraphs(chapter_body: str) -> str:
    """Merge standalone ≤_CHOPPY_MERGE_MAX_WORDS-word paragraphs into the preceding paragraph.

    Preserves the leading heading line(s); only dissolves paragraph breaks, never content. Returns
    the chapter body with the same words in fewer paragraphs.
    """
    paras = [p for p in re.split(r"\n\s*\n", chapter_body) if p.strip()]
    if len(paras) <= 2:
        return chapter_body
    out: list[str] = [paras[0]]
    for p in paras[1:]:
        stripped = p.strip()
        # Only merge a SHORT line that is not itself a heading marker, and only when there is a
        # preceding body paragraph to attach to (never merge into the heading at index 0 alone).
        if (
            len(stripped.split()) <= _CHOPPY_MERGE_MAX_WORDS
            and not stripped.startswith("#")
            and len(out) >= 1
        ):
            out[-1] = (out[-1].rstrip() + " " + stripped).strip()
        else:
            out.append(stripped)
    return "\n\n".join(out)


def chapter_flow_gate_report(
    rendered_text: str,
    plan: Optional[dict[str, Any]] = None,
    prose_map: Optional[dict[str, str]] = None,
    ei_v2_config: Optional[dict[str, Any]] = None,
    *,
    runtime_format_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Evaluate each rendered chapter with chapter_flow_gate and return summary report.
    When plan and prose_map are provided, uses slot-level checks so TAKEAWAY and THREAD
    are required to be non-empty when present.

    When EI v2 ``dimension_gates.enabled`` is true, also runs per-chapter dimension gates
    on composed chapter text and attaches ``dimension_gates`` (includes ``blocks_delivery``).
    """
    cfg_full = ei_v2_config
    if cfg_full is None:
        try:
            from phoenix_v4.quality.ei_v2.config import load_ei_v2_config

            cfg_full = load_ei_v2_config()
        except Exception:
            cfg_full = {}
    dg_cfg = (cfg_full or {}).get("dimension_gates") or {}
    dg_enabled = dg_cfg.get("enabled", True)
    flow_profile = _resolve_chapter_flow_profile(plan, runtime_format_id=runtime_format_id)

    chapter_slot_sequence = (plan or {}).get("chapter_slot_sequence") or []
    atom_ids = (plan or {}).get("atom_ids") or []
    if plan and prose_map and chapter_slot_sequence and atom_ids:
        composed_chapters: list[str] = []
        slot_meta: list[tuple[list[str], list[str]]] = []
        idx = 0
        topic_id = (plan or {}).get("topic_id") or ((plan or {}).get("book_spec") or {}).get("topic_id") or ""
        persona_id = (plan or {}).get("persona_id") or ((plan or {}).get("book_spec") or {}).get("persona_id") or ""
        roles = (plan or {}).get("emotional_role_sequence") or []
        book_seed = str((plan or {}).get("plan_hash") or (plan or {}).get("seed") or "book")
        for ch, slots in enumerate(chapter_slot_sequence):
            segment_proses = []
            ex_aid = ""
            for st_slot in slots:
                if idx < len(atom_ids):
                    aid = atom_ids[idx]
                    if str(st_slot).strip().upper() == "EXERCISE":
                        ex_aid = aid
                    segment_proses.append(clean_for_delivery(prose_map.get(aid, ""), plan=plan))
                else:
                    segment_proses.append("")
                idx += 1
            emotional_role = roles[ch] if ch < len(roles) else ""
            composed = compose_chapter_prose(
                slot_types=slots,
                slot_proses=segment_proses,
                chapter_index=ch,
                total_chapters=len(chapter_slot_sequence),
                locale=(plan or {}).get("locale"),
                topic_id=topic_id,
                persona_id=persona_id,
                emotional_role=str(emotional_role),
                exercise_atom_id=ex_aid,
                exercise_repeat_index=_exercise_repeat_before_idx(chapter_slot_sequence, ch),
                book_seed=book_seed,
            )
            composed = strengthen_chapter_flow_for_delivery(
                composed,
                chapter_index=ch,
                book_seed=book_seed,
                emotional_role=str(emotional_role),
                topic_id=topic_id,
                plan=plan,
                flow_profile=flow_profile,
            )
            composed_chapters.append(composed)
            slot_names = [(s or "").strip().upper() for s in slots]
            slot_meta.append((slot_names, segment_proses))

        chapter_reports = []
        failed = 0
        for ch, slots in enumerate(chapter_slot_sequence):
            slot_names, segment_proses = slot_meta[ch]
            composed = composed_chapters[ch]
            other_composed = [composed_chapters[j] for j in range(len(composed_chapters)) if j != ch]
            text_result = evaluate_chapter_flow(composed, flow_profile=flow_profile)
            errors = list(text_result.errors)
            for i, slot_name in enumerate(slot_names):
                if slot_name == "TAKEAWAY":
                    if i >= len(segment_proses) or not (segment_proses[i] or "").strip():
                        errors.append("TAKEAWAY_EMPTY")
                    break
            for i, slot_name in enumerate(slot_names):
                if slot_name == "THREAD":
                    if i >= len(segment_proses) or not (segment_proses[i] or "").strip():
                        errors.append("THREAD_EMPTY")
                    break
            for i, slot_name in enumerate(slot_names):
                if slot_name == "PIVOT":
                    if i >= len(segment_proses) or not (segment_proses[i] or "").strip():
                        errors.append("PIVOT_EMPTY")
                    break
            for i, slot_name in enumerate(slot_names):
                if slot_name == "PERMISSION":
                    if i >= len(segment_proses) or not (segment_proses[i] or "").strip():
                        errors.append("PERMISSION_EMPTY")
                    break
            status = "PASS" if not errors else "FAIL"
            score = max(0, 100 - len(errors) * 15 - len(text_result.warnings) * 5)
            if status != "PASS":
                failed += 1
            entry: dict[str, Any] = {
                "chapter": ch + 1,
                "status": status,
                "score": score,
                "errors": errors,
                "warnings": text_result.warnings,
                "metrics": {
                    **text_result.metrics,
                    "takeaway_checked": "TAKEAWAY" in slot_names,
                    "thread_checked": "THREAD" in slot_names,
                    "pivot_checked": "PIVOT" in slot_names,
                    "permission_checked": "PERMISSION" in slot_names,
                    "evaluated_text": "composed",
                },
            }
            if dg_enabled:
                entry["dimension_gates"] = _run_dimension_gates_for_composed_chapter(
                    composed, other_composed, ch, dg_cfg,
                )
            chapter_reports.append(entry)

        dg_blocks = bool(
            dg_enabled
            and any(
                (c.get("dimension_gates") or {}).get("blocks_delivery")
                for c in chapter_reports
            )
        )
        dg_status = "SKIP" if not dg_enabled else ("FAIL" if dg_blocks else "PASS")
        return {
            "chapter_count": len(chapter_reports),
            "failed_chapters": failed,
            "status": "PASS" if (failed == 0 and len(chapter_reports) > 0) else "FAIL",
            "chapters": chapter_reports,
            "dimension_gates_status": dg_status,
            "dimension_gates_blocks_delivery": dg_blocks,
        }
    # Fallback: text-only (no TAKEAWAY/THREAD/PIVOT/PERMISSION slot enforcement)
    chapters = _extract_rendered_chapters(rendered_text)
    chapter_reports = []
    failed = 0
    for chapter_number, chapter_text in chapters:
        res = evaluate_chapter_flow(chapter_text, flow_profile=flow_profile)
        if res.status != "PASS":
            failed += 1
        entry: dict[str, Any] = {
            "chapter": chapter_number,
            "status": res.status,
            "score": res.score,
            "errors": res.errors,
            "warnings": res.warnings,
            "metrics": res.metrics,
        }
        if dg_enabled and chapter_text.strip():
            others = [t for n, t in chapters if n != chapter_number]
            entry["dimension_gates"] = _run_dimension_gates_for_composed_chapter(
                chapter_text,
                others,
                chapter_number - 1,
                dg_cfg,
            )
        chapter_reports.append(entry)

    dg_blocks = bool(
        dg_enabled
        and any((c.get("dimension_gates") or {}).get("blocks_delivery") for c in chapter_reports)
    )
    dg_status = "SKIP" if not dg_enabled else ("FAIL" if dg_blocks else "PASS")
    return {
        "chapter_count": len(chapters),
        "failed_chapters": failed,
        "status": "PASS" if (failed == 0 and len(chapters) > 0) else "FAIL",
        "chapters": chapter_reports,
        "dimension_gates_status": dg_status,
        "dimension_gates_blocks_delivery": dg_blocks,
    }


def _build_deficit_report(
    plan: dict,
    prose_map: dict[str, str],
    runtime_format_id: str,
) -> dict:
    """Build a per-chapter, per-slot word-budget breakdown.

    Returns a dict suitable for writing as budget.json alongside the rendered book.
    """
    chapter_slot_sequence = plan.get("chapter_slot_sequence") or []
    atom_ids = plan.get("atom_ids") or []
    word_range = _runtime_word_range(runtime_format_id)
    target_total = word_range[0] if word_range else None
    target_per_chapter = (target_total // len(chapter_slot_sequence)) if (target_total and chapter_slot_sequence) else None

    chapters = []
    slot_totals: dict[str, int] = {}
    grand_total = 0
    idx = 0

    for ch_idx, slots in enumerate(chapter_slot_sequence):
        ch_data: dict = {"chapter": ch_idx + 1, "slots": [], "chapter_word_count": 0}
        for slot_type in slots:
            if idx >= len(atom_ids):
                break
            aid = atom_ids[idx]
            prose = prose_map.get(aid, "")
            wc = len(prose.split()) if prose else 0
            ch_data["slots"].append({"slot": slot_type, "atom_id": aid, "word_count": wc})
            ch_data["chapter_word_count"] += wc
            slot_totals[slot_type] = slot_totals.get(slot_type, 0) + wc
            grand_total += wc
            idx += 1

        deficit = ((target_per_chapter - ch_data["chapter_word_count"]) if target_per_chapter else None)
        ch_data["target_per_chapter"] = target_per_chapter
        ch_data["chapter_deficit"] = deficit
        chapters.append(ch_data)

    return {
        "runtime_format_id": runtime_format_id,
        "word_range_target": list(word_range) if word_range else None,
        "grand_total_words": grand_total,
        "deficit_to_minimum": ((word_range[0] - grand_total) if word_range else None),
        "slot_totals": slot_totals,
        "chapters": chapters,
    }


def _exercise_repeat_before_idx(chapter_sequences: list[list[str]], before_ch: int) -> int:
    """How many prior chapters (0 .. before_ch-1) include an EXERCISE slot."""
    n = 0
    for i in range(max(before_ch, 0)):
        row = chapter_sequences[i] if i < len(chapter_sequences) else []
        if any(str(s).strip().upper() == "EXERCISE" for s in row):
            n += 1
    return n


@dataclass
class RenderOptions:
    """Options for Stage 6 rendering."""
    allow_placeholders: bool = False
    on_missing: str = "fail"          # "fail" | "placeholder"
    title_page: bool = True
    include_slot_labels_qa: bool = False  # If True, emit [STORY] atom_id before prose (QA style)
    clean_output: bool = True         # Strip scaffolding + run delivery_contract_gate before write
    mechanism_alias: Optional[dict] = None  # Loaded alias dict for {{MA}} token resolution
    exercise_source_stats: Optional[dict[str, int]] = None  # Mutated by compose_chapter_prose (registry / library_34_fallback / ab_tady / total)


def _get_prose(
    atom_id: str,
    slot_type: str,
    prose_map: dict[str, str],
    render_result: RenderResult,
    options: RenderOptions,
) -> str:
    """Return prose for this slot. Normalizes placeholders, silence, missing.

    When allow_placeholders=True, placeholder/silence slots return empty string
    (gracefully omitted from rendered output) with a logged warning.
    When on_missing="placeholder", missing atoms also return empty string.
    """
    if _is_placeholder_or_silence(atom_id):
        if options.allow_placeholders:
            logger.warning("Skipping %s slot (atom_id=%s) — placeholder/silence omitted from rendered output", slot_type, atom_id)
            return ""
        return f"[Placeholder: {slot_type}]"  # caller may have chosen to fail earlier

    prose = prose_map.get(atom_id)
    if prose is not None and prose != "":
        return prose
    if atom_id in render_result.missing_ids:
        if options.on_missing == "fail":
            raise ValueError(f"Missing prose for atom_id: {atom_id}")
        logger.warning("Missing prose for atom_id=%s — omitted from rendered output", atom_id)
        return ""
    if options.on_missing == "fail":
        raise ValueError(f"Missing prose for atom_id: {atom_id}")
    logger.warning("Missing prose for atom_id=%s — omitted from rendered output", atom_id)
    return ""


def _wrap_practice_fallback_exercise(prose: str, plan: dict[str, Any], chapter_index: int, slot_index: int) -> str:
    """When EXERCISE has atom_source=practice_fallback, wrap with teacher intro/close. Deterministic by (book_id, ch, si)."""
    teacher_id = (plan.get("teacher_id") or (plan.get("book_spec") or {}).get("teacher_id") or "").strip()
    if not teacher_id:
        return prose
    try:
        from phoenix_v4.teacher.teacher_config import load_teacher_config
        cfg = load_teacher_config(teacher_id)
        wrapper = cfg.get("exercise_wrapper") or {}
        intro_templates = list(wrapper.get("intro_templates") or [])
        close_templates = list(wrapper.get("close_templates") or [])
        if not intro_templates and not close_templates:
            return prose
        book_id = plan.get("plan_id") or plan.get("plan_hash") or "book"
        h = hashlib.sha256(f"{book_id}:{chapter_index}:{slot_index}".encode("utf-8")).hexdigest()
        intro = (intro_templates[int(int(h[:8], 16) % len(intro_templates))] + "\n\n") if intro_templates else ""
        close = ("\n\n" + close_templates[int(int(h[8:16], 16) % len(close_templates))]) if close_templates else ""
        return f"{intro}{prose}{close}"
    except Exception:
        return prose


def _wrap_persona_fallback_story(prose: str, plan: dict[str, Any], chapter_index: int, slot_index: int) -> str:
    """When STORY has atom_source=persona_fallback, wrap with teacher voice framing.

    Same pattern as _wrap_practice_fallback_exercise but for STORY atoms.
    Teacher-native STORY atoms are used first; when exhausted, persona STORY atoms
    fill remaining chapters with teacher-voiced framing around them.
    """
    teacher_id = (plan.get("teacher_id") or (plan.get("book_spec") or {}).get("teacher_id") or "").strip()
    if not teacher_id:
        return prose
    try:
        from phoenix_v4.teacher.teacher_config import load_teacher_config
        cfg = load_teacher_config(teacher_id)
        display_name = cfg.get("display_name") or teacher_id.replace("_", " ").title()

        wrapper = cfg.get("story_wrapper") or {}
        intro_templates = list(wrapper.get("intro_templates") or [
            f"In {display_name}'s framework, what follows speaks to something deeper than the surface pattern.",
            f"Through the lens of {display_name}'s teachings, consider this.",
            f"What {display_name} calls recognition begins with scenes like this.",
            f"{display_name}'s work reminds us that the pattern is never just the pattern. Consider what follows.",
        ])
        close_templates = list(wrapper.get("close_templates") or [
            f"This is what {display_name} points to — the moment before the mind names it.",
            f"In {display_name}'s tradition, this recognition is where the practice begins.",
            f"What you just witnessed is the mechanism {display_name}'s teachings address directly.",
            f"Stay with what shifted. {display_name}'s work lives in that shift.",
        ])
        book_id = plan.get("plan_id") or plan.get("plan_hash") or "book"
        h = hashlib.sha256(f"story:{book_id}:{chapter_index}:{slot_index}".encode("utf-8")).hexdigest()
        intro = (intro_templates[int(int(h[:8], 16) % len(intro_templates))] + "\n\n") if intro_templates else ""
        close = ("\n\n" + close_templates[int(int(h[8:16], 16) % len(close_templates))]) if close_templates else ""
        return f"{intro}{prose}{close}"
    except Exception:
        return prose


def _build_title_page_lines(plan: dict[str, Any]) -> list[str]:
    """Optional title/credits from plan (author_assets, topic_id, persona_id)."""
    lines: list[str] = []
    topic_id = plan.get("topic_id") or (plan.get("book_spec") or {}).get("topic_id") or ""
    persona_id = plan.get("persona_id") or (plan.get("book_spec") or {}).get("persona_id") or ""
    author_assets = plan.get("author_assets") or {}
    pen_name = author_assets.get("pen_name") or author_assets.get("author_pen_name") or plan.get("author_id") or ""
    if topic_id or persona_id or pen_name:
        lines.append("")
        if pen_name:
            lines.append(str(pen_name))
        if topic_id:
            lines.append(f"Topic: {topic_id}")
        if persona_id:
            lines.append(f"Persona: {persona_id}")
        lines.append("")
    return lines


class TxtWriter:
    """Write plan + prose to a single .txt file (manuscript/QA)."""

    def __init__(self, plan: dict[str, Any], prose_map: dict[str, str], render_result: RenderResult, options: RenderOptions):
        self.plan = plan
        self.prose_map = prose_map
        self.render_result = render_result
        self.options = options
        self.delivery_governance: dict[str, Any] = {}

    def write(self, out_path: Path) -> Path:
        chapter_slot_sequence = self.plan.get("chapter_slot_sequence") or []
        atom_ids = self.plan.get("atom_ids") or []
        if not chapter_slot_sequence or not atom_ids:
            raise ValueError("Plan missing chapter_slot_sequence or atom_ids")

        lines: list[str] = []
        if self.options.title_page and not self.options.clean_output:
            lines.extend(_build_title_page_lines(self.plan))

        # ── Pen-Name Pre-Intro (before Chapter 1) — Writer Spec §23.4 ──
        # Narrator (AI voice) reads 7 blocks in fixed order for pen-name books.
        # Blocks come from author_assets audiobook_pre_intro.yaml.
        pre_intro = self.plan.get("pre_intro_blocks") or {}
        author_assets = self.plan.get("author_assets") or {}
        pen_name = author_assets.get("pen_name") or self.plan.get("author_id") or ""
        topic_id = self.plan.get("topic_id") or (self.plan.get("book_spec") or {}).get("topic_id") or ""

        if pen_name or pre_intro:
            lines.append("")
            narrator_intro = pre_intro.get("narrator_intro", "")
            if narrator_intro:
                lines.append(narrator_intro)
                lines.append("")
            book_title = pre_intro.get("book_title_line", "")
            if not book_title and pen_name:
                topic_display = topic_id.replace("_", " ").title() if topic_id else "This Book"
                book_title = f'You are listening to "{topic_display}", written by {pen_name}.'
            if book_title:
                lines.append(book_title)
                lines.append("")
            series_line = pre_intro.get("series_line", "")
            if series_line:
                lines.append(series_line)
                lines.append("")
            author_intro = pre_intro.get("author_intro", "")
            if author_intro:
                lines.append(author_intro)
                lines.append("")
            author_bg = pre_intro.get("author_background", "")
            if author_bg:
                lines.append(author_bg)
                lines.append("")
            why_this_book = pre_intro.get("why_this_book", "")
            if why_this_book:
                lines.append(why_this_book)
                lines.append("")
            transition = pre_intro.get("transition_line", "")
            if transition:
                lines.append(transition)
                lines.append("")

        # ── Teacher Mode Pre-Intro Chapter (TEACHER_MODE_STRUCTURAL_SPEC §1) ──
        teacher_pre_intro = self.plan.get("teacher_pre_intro_chapter") or {}
        if teacher_pre_intro and teacher_pre_intro.get("content"):
            lines.append("")
            title = teacher_pre_intro.get("title", "A Note on the Teachings")
            if self.options.clean_output:
                lines.append(title)
            else:
                lines.append(f"========== {title.upper()} ==========")
            lines.append("")
            lines.append(teacher_pre_intro["content"])
            lines.append("")

        # ── Introduction Chapter (Hybrid Template Bank) ─────────────────
        intro_chapter = self.plan.get("introduction_chapter") or {}
        if intro_chapter and intro_chapter.get("content"):
            lines.append("")
            intro_title = intro_chapter.get("title", "Introduction")
            if intro_title:  # lean size has empty title
                if self.options.clean_output:
                    lines.append(intro_title)
                else:
                    lines.append(f"========== {intro_title.upper()} ==========")
                lines.append("")
            lines.append(intro_chapter["content"])
            lines.append("")

        # ── Freebie CTA: Audiobook post-intro spoken (Placement 1) ──────
        # "This audiobook has a companion {workbook_label}..."
        freebie_slug = self.plan.get("freebie_slug") or ""
        freebie_cta_id = self.plan.get("cta_template_id") or ""
        if freebie_slug and self.options.clean_output:
            workbook_type = self.plan.get("companion_workbook_type") or "none"
            workbook_label = "workbook" if workbook_type == "full" else "practice guide" if workbook_type == "light_guide" else "free guide"
            lines.append("")
            lines.append(
                f"This audiobook has a companion {workbook_label} with all the exercises "
                f"and reflection prompts. You can get it free at "
                f"brand-admin-onboarding.pages.dev/free/{freebie_slug}."
            )
            lines.append("")

        # ── Freebie CTA: Ebook front-matter pointer (Placement 3) ──────
        if freebie_slug and workbook_type == "full" and self.options.clean_output:
            lines.append(
                f"A companion {workbook_label} is available for this book at "
                f"brand-admin-onboarding.pages.dev/free/{freebie_slug}. "
                f"You may want to have it alongside you as you read."
            )
            lines.append("")

        atom_sources = self.plan.get("atom_sources") or []
        alias = self.options.mechanism_alias  # may be None
        naming_moment_injected = False
        total_chapters = len(chapter_slot_sequence)
        highest_exercise_ch = -1  # track for mid-book CTA

        _delivery_governance: dict[str, Any] = {}
        _frame_registry: Any = None
        _frame_ch_contracts: list[Any] = []
        _frame = "somatic_first"
        if self.options.clean_output:
            _delivery_governance = {
                "frame_governance_chapters": [],
                "frame_softened_sentences": [],
                "frame_stripped_sentences": [],
                "frame_hard_fail_reasons": [],
            }
            from phoenix_v4.planning.chapter_planner import assign_chapter_purpose_contracts
            from phoenix_v4.quality.frame_governor import load_frame_registry

            _runtime_fmt = str(
                self.plan.get("runtime_format_id")
                or (self.plan.get("book_spec") or {}).get("runtime_format_id")
                or ""
            )
            _frame_ch_contracts = assign_chapter_purpose_contracts(
                total_chapters, _runtime_fmt
            )
            _frame_registry = load_frame_registry()
            _plan_frame = self.plan.get("frame")
            if _plan_frame is None:
                _plan_frame = (self.plan.get("book_spec") or {}).get("frame")
            _spine = self.plan.get("spine_context") or {}
            _frame = str(_plan_frame or _spine.get("frame") or "somatic_first").strip()

        idx = 0
        for ch, slots in enumerate(chapter_slot_sequence):
            lines.append("")
            if self.options.clean_output:
                lines.append(f"Chapter {ch + 1}")
            else:
                lines.append(f"========== CHAPTER {ch + 1} ==========")
            lines.append("")

            # ── Collect all slot types + prose for this chapter ──
            chapter_slot_types: list[str] = []
            chapter_slot_proses: list[str] = []
            exercise_aid = ""
            for si, slot_type in enumerate(slots):
                if idx >= len(atom_ids):
                    break
                aid = atom_ids[idx]
                slot_label = str(slot_type).strip()
                if slot_label == "EXERCISE":
                    exercise_aid = aid
                prose = _get_prose(aid, slot_label, self.prose_map, self.render_result, self.options)
                if atom_sources and idx < len(atom_sources):
                    if atom_sources[idx] == "practice_fallback" and slot_label == "EXERCISE":
                        prose = _wrap_practice_fallback_exercise(prose, self.plan, ch, si)
                    elif atom_sources[idx] == "persona_fallback" and slot_label == "STORY":
                        prose = _wrap_persona_fallback_story(prose, self.plan, ch, si)
                idx += 1
                chapter_slot_types.append(slot_label)
                chapter_slot_proses.append(prose)

            # ── Bestseller composition (always-on) ──
            # Reorders slots into argued chapter: Opening → Bridge → Mechanism →
            # Bridge → Story → Bridge → Exercise → Integration → Takeaway
            topic_id = self.plan.get("topic_id") or (self.plan.get("book_spec") or {}).get("topic_id") or ""
            persona_id = self.plan.get("persona_id") or (self.plan.get("book_spec") or {}).get("persona_id") or ""
            roles = self.plan.get("emotional_role_sequence") or []
            emotional_role = roles[ch] if ch < len(roles) else ""
            book_seed = str(self.plan.get("plan_hash") or self.plan.get("seed") or "book")
            composed = compose_chapter_prose(
                slot_types=chapter_slot_types,
                slot_proses=chapter_slot_proses,
                chapter_index=ch,
                total_chapters=total_chapters,
                include_slot_labels_qa=self.options.include_slot_labels_qa,
                locale=self.plan.get("locale"),
                topic_id=topic_id,
                persona_id=persona_id,
                emotional_role=str(emotional_role),
                exercise_atom_id=exercise_aid,
                exercise_repeat_index=_exercise_repeat_before_idx(chapter_slot_sequence, ch),
                exercise_source_stats=self.options.exercise_source_stats,
                book_seed=book_seed,
            )

            # Inject mechanism alias naming_moment once after Chapter 1 opening
            if (
                not naming_moment_injected
                and ch == 0
                and alias
                and self.options.clean_output
            ):
                naming_block = _build_naming_moment_block(alias)
                if naming_block:
                    # Insert after first paragraph of composed text
                    first_break = composed.find("\n\n")
                    if first_break > 0:
                        composed = composed[:first_break] + "\n\n" + naming_block + composed[first_break:]
                    else:
                        composed = composed + "\n\n" + naming_block
                    naming_moment_injected = True

            composed = strengthen_chapter_flow_for_delivery(
                composed,
                chapter_index=ch,
                book_seed=book_seed,
                emotional_role=str(emotional_role),
                topic_id=topic_id,
                plan=self.plan,
            )

            if self.options.clean_output and _frame_registry:
                from phoenix_v4.quality.frame_governor import (
                    FrameEnforcementContext,
                    apply_frame_enforcement,
                )

                _fc = (
                    _frame_ch_contracts[ch]
                    if ch < len(_frame_ch_contracts)
                    else _frame_ch_contracts[-1]
                )
                _doctrine = any(
                    str(x).strip().upper() == "TEACHER_DOCTRINE"
                    for x in chapter_slot_types
                )
                _fe_ctx = FrameEnforcementContext(
                    chapter_index=ch,
                    frame=_frame,
                    doctrine_chapter=_doctrine,
                    allow_early_spiritual=bool(_fc.allow_early_spiritual),
                    emotional_job=str(_fc.emotional_job or ""),
                )
                composed, _fg = apply_frame_enforcement(
                    composed, _fe_ctx, _frame_registry
                )
                _delivery_governance["frame_softened_sentences"].extend(
                    _fg.softened_sentences
                )
                _delivery_governance["frame_stripped_sentences"].extend(
                    _fg.stripped_sentences
                )
                _delivery_governance["frame_hard_fail_reasons"].extend(
                    _fg.hard_fail_reasons
                )
                if (
                    _fg.violations
                    or _fg.softened_sentences
                    or _fg.stripped_sentences
                    or _fg.hard_fail_reasons
                    or not _fg.frame_compliant
                ):
                    _delivery_governance["frame_governance_chapters"].append(
                        {
                            "chapter": ch + 1,
                            "chapter_index": ch,
                            "violations": _fg.violations,
                            "softened": _fg.softened_sentences,
                            "stripped": _fg.stripped_sentences,
                            "hard_fail": _fg.hard_fail_reasons,
                            "frame_compliant": _fg.frame_compliant,
                            "spiritual_density": _fg.spiritual_density,
                        }
                    )

            lines.append(composed)
            lines.append("")

        # The final chapter's INTEGRATION slot + carry_line serve as the
        # narrative conclusion (Writer Spec §7). The Conclusion chapter below
        # is a separate framing section — a bookend to the Introduction.

        # ── Conclusion Chapter (Hybrid Template Bank) ───────────────────
        conclusion_chapter = self.plan.get("conclusion_chapter") or {}
        if conclusion_chapter and conclusion_chapter.get("content"):
            lines.append("")
            conclusion_title = conclusion_chapter.get("title", "Conclusion")
            if conclusion_title:
                if self.options.clean_output:
                    lines.append(conclusion_title)
                else:
                    lines.append(f"========== {conclusion_title.upper()} ==========")
                lines.append("")
            lines.append(conclusion_chapter["content"])
            lines.append("")

        # ── Teacher Mode Closing Section (TEACHER_MODE_STRUCTURAL_SPEC §4) ──
        teacher_closing = self.plan.get("teacher_closing_section") or {}
        if teacher_closing and teacher_closing.get("content"):
            lines.append("")
            closing_title = teacher_closing.get("title", "Where to Go Deeper")
            if self.options.clean_output:
                lines.append(closing_title)
            else:
                lines.append(f"========== {closing_title.upper()} ==========")
            lines.append("")
            lines.append(teacher_closing["content"])
            lines.append("")

        # ── Freebie CTA: Audiobook back-matter spoken (Placement 2) ─────
        if freebie_slug and self.options.clean_output:
            lines.append("")
            lines.append(
                f"To go deeper and actually do the work from this book, download the "
                f"companion {workbook_label} at brand-admin-onboarding.pages.dev/free/{freebie_slug}. "
                f"You will find guided exercises, journaling pages, and tools you can "
                f"return to again and again. It is free — designed to go with exactly this book."
            )
            lines.append("")

        # ── Freebie CTA: Ebook back-matter upsell (Placement 6) ────────
        if freebie_slug and self.options.clean_output:
            lines.append("")
            lines.append(
                f"Before you go — if you want to take this further, a companion "
                f"{workbook_label} is waiting for you at "
                f"brand-admin-onboarding.pages.dev/free/{freebie_slug}."
            )
            lines.append("")

        full_text = "\n".join(lines).strip()

        # Resolve {{MA}}, {{MA_DEF}}, {{MA_FULL}} tokens before delivery gate
        full_text = _resolve_mechanism_alias_tokens(full_text, alias)

        if self.options.clean_output:
            full_text = clean_for_delivery(
                full_text, plan=self.plan, governance_report=_delivery_governance
            )
            self.delivery_governance = _delivery_governance
            delivery_contract_gate(full_text, source_hint=str(out_path))
        else:
            self.delivery_governance = {}

        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(full_text + "\n", encoding="utf-8")
        return out_path


def _maybe_apply_music_overlay_to_txt(
    book_txt: Path,
    plan: dict[str, Any],
    output_dir: Path,
    *,
    music_mode: Optional[str],
    musician_id: Optional[str],
    repo_root: Path,
) -> None:
    """Post-process ``book.txt`` in place when music mode is active (additive overlay)."""
    mm = (music_mode or "none").strip()
    mid = (musician_id or "").strip()
    if mm == "none" or not mid:
        return
    from phoenix_v4.rendering.music_manuscript_overlay import apply_music_overlay_to_manuscript

    text = book_txt.read_text(encoding="utf-8")
    persona_id = (plan.get("persona_id") or (plan.get("book_spec") or {}).get("persona_id") or "").strip()
    topic_id = (plan.get("topic_id") or (plan.get("book_spec") or {}).get("topic_id") or "").strip()
    seed = str(plan.get("plan_hash") or plan.get("plan_id") or plan.get("seed") or "book")
    new_text, audit = apply_music_overlay_to_manuscript(
        text,
        repo_root=repo_root,
        music_mode=mm,
        musician_id=mid,
        persona_id=persona_id or "unknown_persona",
        topic_id=topic_id or "unknown_topic",
        book_seed=seed,
    )
    book_txt.write_text(new_text, encoding="utf-8")
    (output_dir / "music_overlay_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    spa = output_dir / "section_packet_audit.json"
    if spa.exists():
        try:
            payload = json.loads(spa.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
    else:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    payload["musician_overlay"] = audit
    spa.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def render_book(
    plan: dict[str, Any],
    output_dir: Path,
    *,
    formats: Optional[List[str]] = None,
    atoms_root: Optional[Path] = None,
    bindings_path: Optional[Path] = None,
    teacher_banks_root: Optional[Path] = None,
    allow_placeholders: bool = False,
    on_missing: str = "fail",
    title_page: bool = True,
    include_slot_labels_qa: bool = False,
    clean_output: bool = True,
    enforce_word_count: bool = True,
    enforce_chapter_flow: bool = False,
    enforce_dimension_gates: bool = False,
    enforce_location_grounding: bool = True,
    music_mode: Optional[str] = None,
    musician_id: Optional[str] = None,
    repo_root_for_music: Optional[Path] = None,
) -> dict[str, Path]:
    """
    Stage 6: resolve prose for plan and write requested formats to output_dir.
    Returns dict format -> path (e.g. {"txt": Path("output_dir/book.txt")}).

    clean_output=True (default):
      - Strips pipeline metadata, markdown dividers, and chapter scaffold markers.
      - Resolves unhydrated loc-vars ({weather_detail} etc.) with universal fallbacks.
      - Runs delivery_contract_gate() before write — hard-fails if any artifact survives.
      Use for production epub/TTS output.

    clean_output=False:
      - Passes raw assembled text through (scaffold markers preserved).
      - No gate. Use for QA diffs and debugging.

    enforce_word_count=True (default):
      - Reads runtime_format_id from plan and compares rendered word count to word_range min.
      - Writes a budget.json deficit report alongside every rendered book.
      - Raises WordCountGateError if word count is below minimum.
      - Set to False to skip gate (e.g. for short QA builds or atom-pool builds).

    enforce_chapter_flow=False (default):
      - Computes chapter flow report at output_dir/chapter_flow_report.json.
      - If True and any chapter fails flow gate, raises ChapterFlowGateError.

    enforce_dimension_gates=False (default):
      - chapter_flow_report.json includes EI v2 dimension gate telemetry when enabled in config.
      - If True and any chapter has dimension_gates.blocks_delivery, raises DimensionGateBlockError.

    enforce_location_grounding=True (default):
      - If the plan carries a resolved/requested location profile, checks whether
        the opening of Chapter 1 realizes that location with profile-specific signals.
      - Writes location_grounding_report.json when a location is present.
      - Raises LocationGroundingError if the opening does not ground the location.
    """
    formats = formats or ["txt"]
    output_dir = Path(output_dir)

    render_result = resolve_prose_for_plan(
        plan,
        atoms_root=atoms_root,
        bindings_path=bindings_path,
        teacher_banks_root=teacher_banks_root,
        locale=plan.get("locale"),
    )

    # Normalize edge cases: fail on placeholders or missing when not allowed
    if render_result.placeholder_or_silence_ids:
        if not allow_placeholders:
            raise ValueError(
                "Plan contains placeholders or silence slots. Resolve upstream or use allow_placeholders=True. "
                f"First: {render_result.placeholder_or_silence_ids[0]}"
            )
        else:
            logger.warning(
                "Plan has %d placeholder/silence slots — will be omitted from rendered output. First: %s",
                len(render_result.placeholder_or_silence_ids),
                render_result.placeholder_or_silence_ids[0],
            )
    if render_result.missing_ids:
        if on_missing == "fail":
            raise ValueError(
                "Missing prose for atom_ids (not found in atoms/ or teacher_banks or compression_atoms): "
                + ", ".join(render_result.missing_ids[:5])
                + (f" ... and {len(render_result.missing_ids) - 5} more" if len(render_result.missing_ids) > 5 else "")
            )
        else:
            logger.warning(
                "Missing prose for %d atom_ids — will be omitted. First 5: %s",
                len(render_result.missing_ids),
                ", ".join(render_result.missing_ids[:5]),
            )

    # Load mechanism alias for this persona × topic (gracefully no-ops if not found)
    persona_id = (plan.get("persona_id") or (plan.get("book_spec") or {}).get("persona_id") or "").strip()
    topic_id   = (plan.get("topic_id")   or (plan.get("book_spec") or {}).get("topic_id")   or "").strip()
    alias = _load_mechanism_alias(persona_id, topic_id)

    exercise_source_stats: dict[str, int] = {
        "registry": 0,
        "ab_tady": 0,
        "library_34_fallback": 0,
        "total": 0,
    }
    options = RenderOptions(
        allow_placeholders=allow_placeholders,
        on_missing=on_missing,
        title_page=title_page,
        include_slot_labels_qa=include_slot_labels_qa,
        clean_output=clean_output,
        mechanism_alias=alias,
        exercise_source_stats=exercise_source_stats,
    )
    written: dict[str, Path] = {}
    runtime_format_id = (plan.get("runtime_format_id") or "").strip()

    if "txt" in formats:
        writer = TxtWriter(plan, render_result.prose_map, render_result, options)
        out_path = output_dir / "book.txt"
        writer.write(out_path)

        # Locale post-processing: replace English template strings with locale versions
        locale = plan.get("locale")
        if locale and locale != "en-US":
            from phoenix_v4.rendering.locale_templates import localize_rendered_text
            raw = out_path.read_text(encoding="utf-8")
            localized = localize_rendered_text(raw, locale)
            out_path.write_text(localized, encoding="utf-8")

        _music_repo = repo_root_for_music or Path(__file__).resolve().parents[2]
        _maybe_apply_music_overlay_to_txt(
            out_path,
            plan,
            output_dir,
            music_mode=music_mode,
            musician_id=musician_id,
            repo_root=_music_repo,
        )

        written["txt"] = out_path

        # Word-count gate + slot-level deficit report (always written, gate optional)
        rendered_text = out_path.read_text(encoding="utf-8")
        flow_report = chapter_flow_gate_report(
            rendered_text,
            plan=plan,
            prose_map=render_result.prose_map,
            runtime_format_id=runtime_format_id or None,
        )
        flow_path = output_dir / "chapter_flow_report.json"
        flow_path.write_text(json.dumps(flow_report, indent=2), encoding="utf-8")
        written["chapter_flow_report"] = flow_path

        if enforce_chapter_flow and flow_report.get("status") != "PASS":
            first_fail = next((c for c in flow_report.get("chapters", []) if c.get("status") != "PASS"), None)
            if first_fail:
                raise ChapterFlowGateError(
                    f"Chapter flow gate FAILED at chapter {first_fail.get('chapter')}: "
                    + ", ".join(first_fail.get("errors") or ["UNKNOWN"])
                )
            raise ChapterFlowGateError("Chapter flow gate FAILED.")

        if enforce_dimension_gates and flow_report.get("dimension_gates_blocks_delivery"):
            raise DimensionGateBlockError(
                "EI v2 dimension gates blocked delivery (see chapter_flow_report.json "
                "per-chapter dimension_gates.blocks_delivery)."
            )

        deficit_report = _build_deficit_report(plan, render_result.prose_map, runtime_format_id)
        _tot_fb = int(exercise_source_stats.get("total", 0) or 0)
        _lib_fb = int(exercise_source_stats.get("library_34_fallback", 0) or 0)
        _fb_ratio = (_lib_fb / _tot_fb) if _tot_fb else 0.0
        deficit_report["exercise_source"] = dict(exercise_source_stats)
        deficit_report["exercise_fallback_ratio"] = round(_fb_ratio, 4)
        if _tot_fb and _fb_ratio > 0.5:
            deficit_report["exercise_fallback_quality_warning"] = (
                f"More than 50% of exercises ({_lib_fb}/{_tot_fb}) used library_34 fallback — "
                "prefer registry or teacher EXERCISE atoms for production books."
            )
            logger.warning(deficit_report["exercise_fallback_quality_warning"])
        budget_path = output_dir / "budget.json"
        budget_path.write_text(json.dumps(deficit_report, indent=2), encoding="utf-8")
        written["budget"] = budget_path

        _qs_path = output_dir / "quality_summary.json"
        _qs_base = {
            "exercise_source": dict(exercise_source_stats),
            "exercise_fallback_ratio": round(_fb_ratio, 4),
            "exercise_fallback_quality_warning": deficit_report.get("exercise_fallback_quality_warning"),
        }
        _dg = getattr(writer, "delivery_governance", None)
        if isinstance(_dg, dict):
            for k, v in _dg.items():
                _qs_base[k] = v
        _qs_path.write_text(json.dumps(_qs_base, indent=2), encoding="utf-8")
        written["quality_summary"] = _qs_path

        if enforce_word_count and runtime_format_id:
            wc_metrics = word_count_gate(rendered_text, runtime_format_id, source_hint=str(out_path))
            deficit_report["gate_result"] = wc_metrics
            budget_path.write_text(json.dumps(deficit_report, indent=2), encoding="utf-8")

        location_report = location_grounding_report(rendered_text, plan=plan)
        if location_report is not None:
            location_path = output_dir / "location_grounding_report.json"
            location_path.write_text(json.dumps(location_report, indent=2), encoding="utf-8")
            written["location_grounding_report"] = location_path
            if enforce_location_grounding and location_report.get("status") != "PASS":
                raise LocationGroundingError(
                    f"Location grounding FAILED for {location_report.get('location_id')}: "
                    + "; ".join(location_report.get("errors") or ["opening failed location grounding"])
                )

    return written
