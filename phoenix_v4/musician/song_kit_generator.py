"""Music Onboarding Song-Kit — survey → generator orchestrator scaffold (V1, Phase-2).

Governing cap:   MUSIC-ONBOARDING-SONG-KIT-V1-01  (docs/PEARL_ARCHITECT_STATE.md)
Governing spec:  docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md  (esp. §3)
Child workstream: ws_pearl_editor_song_kit_generator_20260612 (this module)
Sibling engine ws: ws_pearl_dev_lyric_mood_instruction_engine_20260612 (real engine)
Sibling gate ws:   ws_pearl_dev_music_brand_diversity_ci_guard_20260611 (G1-G8 gate)

WHAT THIS MODULE IS
    The *orchestrator* that turns a completed musician survey into a first DRAFT
    "song-kit": draft atoms emitted into the EXISTING 6 slot pools
    (LYRIC_OPENING/CLOSING/BESTSELLER_BEAT + MUSIC_REFLECTION_OPENING/CLOSING/
    BESTSELLER_BEAT, per MUSIC-MODE-V1-01). It consumes — never re-parses — the
    derived dicts from ``phoenix_v4.musician.survey_derivation`` (profile / themes /
    voice_profile), maps the surveyed ``primary_themes`` onto the 8-family taxonomy
    SSOT (``config/music/song_kit_topic_families.yaml``), runs the survey
    lyrical/instrumental fork, and gates kit completion to the SPEC-739 ≥3-variants/
    pool floor.

WHAT THIS MODULE IS NOT (anti-drift — hard boundaries; spec §3, §6)
    1. NOT the LLM lyric/mood engine. The actual lyric / mood-instruction generation
       is a PLUGGABLE engine call — the ``LyricMoodEngine`` Protocol below is the
       interface ONLY; the real engine is the sibling workstream
       ``ws_pearl_dev_lyric_mood_instruction_engine_20260612``. A deterministic stub
       (``DeterministicStubEngine``) is provided for offline tests. Routing for the
       real engine (enforced by that sibling ws, NOT here): English →
       Pearl_Writer / Claude subagent (Tier 1); CJK6 → Qwen (Pearl Star / Ollama);
       unattended / scheduled → Gemma (EN) / Qwen (CJK6) on Pearl Star via Ollama.
       NO paid LLM API anywhere (CLAUDE.md Tier policy + audit_llm_callers.py).
    2. Does NOT re-implement the G1–G8 diversity gate. It imports the canonical gate
       (``scripts/ci/check_music_brand_diversity.py``, built by the sibling ws
       ``ws_pearl_dev_music_brand_diversity_ci_guard_20260611``) when present and
       degrades to a SKIPPED verdict when that script is not yet on main — it NEVER
       authors a parallel diversity gate (reuse-not-greenfield; spec §3.6).
    3. Does NOT invent new slot pools, atom schema, template vars, or survey fields.
       Atoms keep the on-main shape (``atom_id`` + ``variants: [{body: ...}]``) and the
       established template vars (``{{musician_name}}`` / ``{{topic_anchor}}`` /
       ``{{theme}}`` / ``{{genre}}`` / ``{{persona_anchor}}``). Pool structure is per
       MUSIC-MODE-V1-01.
    4. Does NOT render audio. The no-lyrics fork emits MusicGen mood-instruction TEXT
       only; WAV render is Phase-B-gated (spec §1.4).
    5. Drafts are PROPOSED. Output is a draft kit Pearl_Editor reviews and promotes
       (Tier-1, operator-present). This orchestrator does not ship atoms to a catalog
       run.

OFFLINE SELF-TEST
    ``build_kit_skeleton`` + ``DeterministicStubEngine`` run with zero network / zero
    LLM, producing a full kit skeleton for a sample survey (see the bundled test).
"""
from __future__ import annotations

import importlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, runtime_checkable

# Reuse the on-main derivation helpers (consumed, not re-implemented; spec §3.1).
from phoenix_v4.musician.survey_derivation import (
    survey_to_profile_dict,
    survey_to_themes_yaml,
    survey_to_voice_yaml,
)

try:  # PyYAML is optional at import time (mirrors survey_derivation.py).
    import yaml
except ImportError:  # pragma: no cover - exercised only in yaml-less envs
    yaml = None  # type: ignore[assignment]

__all__ = [
    "LYRIC_POOLS",
    "REFLECTION_POOLS",
    "ALL_POOLS",
    "SPEC_739_FLOOR",
    "SPEC_739_CEILING",
    "GenerationRequest",
    "DraftAtom",
    "LyricMoodEngine",
    "DeterministicStubEngine",
    "SongKitGenerator",
    "KitResult",
    "build_kit_skeleton",
    "load_topic_families",
    "match_families",
    "run_diversity_gate",
]

# --- Slot pools (per MUSIC-MODE-V1-01; identical to music_overlay.atom_pool_key) ----
# Kept in lockstep with phoenix_v4.planning.music_overlay; asserted at runtime below so
# this list can never silently drift from the injection planner's pool names.
LYRIC_POOLS: tuple[str, ...] = (
    "LYRIC_OPENING",
    "LYRIC_BESTSELLER_BEAT",
    "LYRIC_CLOSING",
)
REFLECTION_POOLS: tuple[str, ...] = (
    "MUSIC_REFLECTION_OPENING",
    "MUSIC_REFLECTION_BESTSELLER_BEAT",
    "MUSIC_REFLECTION_CLOSING",
)
ALL_POOLS: tuple[str, ...] = LYRIC_POOLS + REFLECTION_POOLS

# Maps a slot pool to the chapter position it serves (spec §3.4 / music_overlay).
_POOL_POSITION: dict[str, str] = {
    "LYRIC_OPENING": "opening",
    "LYRIC_BESTSELLER_BEAT": "bestseller_beat",
    "LYRIC_CLOSING": "closing",
    "MUSIC_REFLECTION_OPENING": "opening",
    "MUSIC_REFLECTION_BESTSELLER_BEAT": "bestseller_beat",
    "MUSIC_REFLECTION_CLOSING": "closing",
}

# Short atom-id stems matching the on-main convention (lo_/lb_/lc_/ro_/rb_/rc_).
_POOL_STEM: dict[str, str] = {
    "LYRIC_OPENING": "lo",
    "LYRIC_BESTSELLER_BEAT": "lb",
    "LYRIC_CLOSING": "lc",
    "MUSIC_REFLECTION_OPENING": "ro",
    "MUSIC_REFLECTION_BESTSELLER_BEAT": "rb",
    "MUSIC_REFLECTION_CLOSING": "rc",
}

# SPEC-739-THRESHOLD-01 kit-completion floor / optional ceiling (spec §3.5).
SPEC_739_FLOOR: int = 3
SPEC_739_CEILING: int = 5

# Canonical taxonomy SSOT (spec §2). Resolved relative to the repo root by default.
_TOPIC_FAMILIES_REL = "config/music/song_kit_topic_families.yaml"
# Canonical diversity-gate script (built by the sibling ws; spec §3.6). Importable as a
# dotted module path once it lands on main; absent today, so the import is guarded.
_DIVERSITY_GATE_MODULE = "scripts.ci.check_music_brand_diversity"


def _repo_root() -> Path:
    """Repo root = three parents up from this file (phoenix_v4/musician/<file>)."""
    return Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------------
# Engine interface (pluggable) + offline deterministic stub
# ---------------------------------------------------------------------------------
@dataclass(frozen=True)
class GenerationRequest:
    """One unit of work handed to the lyric/mood engine.

    The engine returns the body TEXT for a single atom variant. For ``with-lyrics``
    LYRIC_* pools this is lyric text; for MUSIC_REFLECTION_* pools on the no-lyrics
    fork it is MusicGen mood-instruction TEXT (no audio — spec §1.4).
    """

    musician_id: str
    slot_pool: str
    position: str  # opening | bestseller_beat | closing
    family_id: str
    kind: str  # "lyric" | "mood_instruction"
    variant_index: int  # 0-based; engine should diversify across indices
    # Conditioning context (derived dicts + family hints; spec §3.1/§3.3).
    profile: Mapping[str, Any]
    themes: Mapping[str, Any]
    voice_profile: Mapping[str, Any]
    family: Mapping[str, Any]
    topic_anchor: str
    theme: str
    locale: str = "en_US"  # routing hint for the real engine (EN vs CJK6)
    lyric_form: str | None = None  # free_verse | rhymed | verse_chorus (with-lyrics)
    reflection_form: str | None = None  # essay | journal_entry | meditation | mixed
    reflection_perspective: str | None = None  # musician | listener | critic | mixed


@runtime_checkable
class LyricMoodEngine(Protocol):
    """Pluggable generation engine.

    The REAL implementation is the sibling workstream
    ``ws_pearl_dev_lyric_mood_instruction_engine_20260612`` and MUST route English →
    Pearl_Writer / Claude subagent, CJK6 → Qwen, unattended → Gemma/Qwen-Ollama,
    with NO paid LLM API (CLAUDE.md Tier policy). This orchestrator only depends on
    the interface; it is engine-agnostic.
    """

    def generate(self, request: GenerationRequest) -> str:
        """Return the body text for one atom variant."""
        ...


class DeterministicStubEngine:
    """Offline, network-free, LLM-free stub engine for tests + dry runs.

    It composes deterministic placeholder bodies from the conditioning context and
    the family hints. It is NOT a content engine and ships NO real lyrics — it exists
    so the orchestrator can be exercised end-to-end offline and so CI never reaches
    for an LLM. Real generation is the sibling ws. Deterministic in the math sense:
    identical request → identical output (no RNG, no clock, no I/O).
    """

    name = "deterministic_stub"

    def generate(self, request: GenerationRequest) -> str:
        anchor = request.topic_anchor or "stillness"
        theme = request.theme or "the quiet work"
        if request.kind == "mood_instruction":
            hint = str(request.family.get("instrumental_mood_hint") or "").strip()
            base = (
                f"[STUB mood-instruction · {request.slot_pool} · variant "
                f"{request.variant_index + 1}] MusicGen TEXT for {{{{musician_name}}}}, "
                f"{{{{genre}}}} on a {{{{topic_anchor}}}} ({anchor}) theme — {{{{theme}}}} "
                f"({theme})."
            )
            return f"{base} Mood hint: {hint}" if hint else base
        # lyric kind
        hint = str(request.family.get("lyric_register_hint") or "").strip()
        base = (
            f"[STUB lyric · {request.slot_pool} · variant {request.variant_index + 1}] "
            f"{{{{musician_name}}}} on {{{{topic_anchor}}}} ({anchor});\n"
            f"{{{{persona_anchor}}}} meets {{{{theme}}}} ({theme}) in {{{{genre}}}}."
        )
        return f"{base} Register hint: {hint}" if hint else base


# ---------------------------------------------------------------------------------
# Draft atom model (on-main shape: atom_id + variants:[{body:...}])
# ---------------------------------------------------------------------------------
@dataclass
class DraftAtom:
    """A single draft atom destined for ``approved_atoms/<SLOT_POOL>/<atom_id>.yaml``.

    Matches the on-main atom shape exactly (see
    ``test_artist_alpha/.../LYRIC_OPENING/lo_01.yaml``): an ``atom_id`` plus a
    ``variants`` list of ``{"body": ...}`` dicts. ``status`` and ``provenance`` are
    sidecar bookkeeping the writer drops when serializing the canonical 2-key shape.
    """

    atom_id: str
    slot_pool: str
    variants: list[dict[str, str]] = field(default_factory=list)
    status: str = "draft"  # PROPOSED; Pearl_Editor promotes (spec §3.3)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_atom_yaml_obj(self) -> dict[str, Any]:
        """Canonical on-main atom object (2 keys: atom_id + variants)."""
        return {"atom_id": self.atom_id, "variants": [dict(v) for v in self.variants]}

    def variant_count(self) -> int:
        return len(self.variants)


@dataclass
class KitResult:
    """Outcome of a kit build: per-pool draft atoms + completion verdict."""

    musician_id: str
    brand_id: str
    fork: str  # "with-lyrics" | "no-lyrics" | "both"
    matched_families: list[str]
    pools: dict[str, list[DraftAtom]] = field(default_factory=dict)
    spec739: dict[str, Any] = field(default_factory=dict)
    diversity: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        """True iff every TARGETED pool meets the SPEC-739 ≥3-variants floor."""
        return bool(self.spec739.get("complete"))

    def summary(self) -> dict[str, Any]:
        """Compact JSON-serializable summary for audits / receipts."""
        return {
            "musician_id": self.musician_id,
            "brand_id": self.brand_id,
            "fork": self.fork,
            "matched_families": list(self.matched_families),
            "pool_variant_counts": {
                pool: sum(a.variant_count() for a in atoms)
                for pool, atoms in self.pools.items()
            },
            "spec739": self.spec739,
            "diversity": self.diversity,
            "complete": self.complete,
            "notes": list(self.notes),
        }


# ---------------------------------------------------------------------------------
# Taxonomy loading + family matching (spec §2 / §3.1)
# ---------------------------------------------------------------------------------
def load_topic_families(path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load the 8-family taxonomy SSOT keyed by ``family_id``.

    Returns ``{}`` when PyYAML or the file is unavailable (callers handle the empty
    case; matching then yields no families and the kit is flagged degraded).
    """
    if yaml is None:
        return {}
    fpath = path or (_repo_root() / _TOPIC_FAMILIES_REL)
    if not fpath.exists():
        return {}
    data = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    families = data.get("topic_families") or []
    out: dict[str, dict[str, Any]] = {}
    for fam in families:
        if isinstance(fam, dict) and fam.get("family_id"):
            out[str(fam["family_id"])] = fam
    return out


# Filler words dropped before family matching so a shared "the"/"of"/etc. can never
# link two unrelated families (matching keys on meaningful theme tokens only).
_STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "and", "a", "an", "of", "to", "in", "on", "as", "is", "it", "for",
        "with", "without", "after", "before", "into", "out", "that", "this", "not",
        "be", "are", "or", "but", "small", "one", "what", "work", "thing", "things",
        "meeting", "meet", "your", "you", "no", "never", "always", "more", "less",
    }
)


def _norm(text: str) -> str:
    """Lowercase + collapse non-alnum to single spaces for fuzzy theme matching."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def match_families(
    primary_themes: Iterable[str],
    families: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    """Map surveyed ``primary_themes`` onto one or more ``family_id``s (spec §3.1).

    A family matches when a *meaningful* surveyed theme token overlaps the family's
    content tokens — its ``family_id``, ``display``, ``default_themes`` seeds, or
    ``topic_anchors``. Common stopwords (``the``/``of``/``after`` …) are dropped first
    so a shared filler word never links unrelated families. Order follows the taxonomy
    file (stable). When nothing matches, returns ``[]`` — the caller flags the kit
    degraded rather than silently inventing a family.
    """
    theme_tokens = {
        tok
        for theme in primary_themes
        for tok in _norm(str(theme)).split()
        if tok not in _STOPWORDS and len(tok) > 2
    }
    matched: list[str] = []
    for fam_id, fam in families.items():
        hay_tokens: set[str] = set()
        for chunk in (fam_id, str(fam.get("display") or "")):
            hay_tokens.update(_norm(chunk).split())
        for seed in fam.get("default_themes") or []:
            hay_tokens.update(_norm(str(seed)).split())
        for anchor in fam.get("topic_anchors") or []:
            hay_tokens.update(_norm(str(anchor)).split())
        hay_tokens = {t for t in hay_tokens if t not in _STOPWORDS and len(t) > 2}
        if theme_tokens & hay_tokens:
            matched.append(fam_id)
    return matched


# ---------------------------------------------------------------------------------
# Diversity gate adapter (REUSE the canonical G1–G8 gate; never re-implement)
# ---------------------------------------------------------------------------------
def run_diversity_gate(
    kit: "KitResult",
    *,
    quality_profile: str = "draft",
) -> dict[str, Any]:
    """Route the draft kit through the canonical G1–G8 diversity gate.

    REUSE-NOT-GREENFIELD (spec §3.6): the gate is ``scripts/ci/
    check_music_brand_diversity.py`` (built by ``ws_pearl_dev_music_brand_diversity_
    ci_guard_20260611``). This adapter imports it dynamically and calls its entry
    point if present. If that script is not yet on main (it is a Phase-2 sibling
    build target), the gate is reported ``SKIPPED`` with a clear note — this module
    NEVER re-implements the G1–G8 thresholds.

    The adapter probes a few conventional entry-point names so it stays compatible
    with the sibling ws's final signature without coupling to one spelling.
    """
    result: dict[str, Any] = {
        "status": "skipped",
        "gate": _DIVERSITY_GATE_MODULE,
        "quality_profile": quality_profile,
        "note": (
            "Canonical G1-G8 gate not yet importable on main "
            "(ws_pearl_dev_music_brand_diversity_ci_guard_20260611). "
            "Draft kit NOT independently diversity-checked here; the gate is reused, "
            "never re-implemented (spec §3.6)."
        ),
    }
    try:
        gate_mod = importlib.import_module(_DIVERSITY_GATE_MODULE)
    except Exception:  # noqa: BLE001 - any import failure → graceful skip
        return result

    # Build the per-pool atom-objects view the gate is expected to consume.
    payload = {
        "brand_id": kit.brand_id,
        "musician_id": kit.musician_id,
        "quality_profile": quality_profile,
        "pools": {
            pool: [a.to_atom_yaml_obj() for a in atoms]
            for pool, atoms in kit.pools.items()
        },
    }
    for entry_name in (
        "evaluate_kit",
        "check_kit",
        "evaluate_atoms",
        "run_gate",
        "evaluate",
    ):
        fn = getattr(gate_mod, entry_name, None)
        if callable(fn):
            try:
                verdict = fn(payload)
            except TypeError:
                # Some signatures may take (pools, profile) positionally.
                verdict = fn(payload["pools"], quality_profile)  # type: ignore[misc]
            return {
                "status": "ran",
                "gate": _DIVERSITY_GATE_MODULE,
                "entry_point": entry_name,
                "quality_profile": quality_profile,
                "verdict": verdict,
            }
    result["status"] = "skipped"
    result["note"] = (
        f"Imported {_DIVERSITY_GATE_MODULE} but found no known entry point "
        "(evaluate_kit/check_kit/evaluate_atoms/run_gate/evaluate); gate not run. "
        "No parallel gate authored (spec §3.6)."
    )
    return result


# ---------------------------------------------------------------------------------
# The orchestrator
# ---------------------------------------------------------------------------------
class SongKitGenerator:
    """Survey → draft song-kit orchestrator (spec §3).

    Pipeline:
      1. Derive profile / themes / voice_profile via ``survey_derivation`` (consumed).
      2. Map ``themes.primary_themes`` → family_id(s) over the 8-family taxonomy.
      3. Select the fork from the survey ``output_preferences_*`` blocks.
      4. For each TARGETED pool, ask the pluggable engine for ``floor`` variants and
         assemble one ``DraftAtom`` (on-main shape).
      5. Gate to SPEC-739 (≥``floor`` variants/pool) and route through the canonical
         G1–G8 diversity gate (reused, not re-implemented).

    The orchestrator NEVER calls an LLM directly — all generation flows through the
    injected ``engine`` (default: deterministic stub). The real engine is the sibling
    ws and is responsible for Tier-compliant routing (no paid API).
    """

    def __init__(
        self,
        engine: LyricMoodEngine | None = None,
        *,
        families: Mapping[str, Mapping[str, Any]] | None = None,
        families_path: Path | None = None,
        floor: int = SPEC_739_FLOOR,
    ) -> None:
        self.engine: LyricMoodEngine = engine or DeterministicStubEngine()
        self.families: dict[str, dict[str, Any]] = (
            dict(families) if families is not None else load_topic_families(families_path)
        )
        if floor < 1:
            raise ValueError("SPEC-739 floor must be >= 1")
        self.floor = floor
        # Guard: pool names must stay in lockstep with the injection planner so a
        # rename there can never silently desync the generator (anti-drift).
        self._assert_pools_match_overlay()

    @staticmethod
    def _assert_pools_match_overlay() -> None:
        try:
            from phoenix_v4.planning.music_overlay import plan_music_injection
        except Exception:  # noqa: BLE001 - overlay import optional at construct time
            return
        pool_keys = {
            p.atom_pool_key
            for mode in ("with-lyrics", "no-lyrics")
            for p in plan_music_injection(chapter_count=1, music_mode=mode)
        }
        drift = pool_keys - set(ALL_POOLS)
        if drift:  # pragma: no cover - only trips if music_overlay adds a pool
            raise RuntimeError(
                f"music_overlay emits pools not known to song_kit_generator: {sorted(drift)}. "
                "Update ALL_POOLS in lockstep (anti-drift)."
            )

    # -- fork selection (spec §3.2) -------------------------------------------------
    @staticmethod
    def select_fork(survey: Mapping[str, Any]) -> str:
        """Return 'with-lyrics' | 'no-lyrics' | 'both' from the survey fork blocks.

        Driven purely by presence of ``output_preferences_with_lyrics`` vs
        ``output_preferences_no_lyrics`` (spec §3.2). ``companion_ai_song_consent``
        gates the lyrical branch: a with-lyrics block present but consent explicitly
        False disables the lyric fork.
        """
        with_block = survey.get("output_preferences_with_lyrics")
        no_block = survey.get("output_preferences_no_lyrics")
        has_lyrics = isinstance(with_block, Mapping) and (
            with_block.get("companion_ai_song_consent") is not False
        )
        has_no_lyrics = isinstance(no_block, Mapping)
        if has_lyrics and has_no_lyrics:
            return "both"
        if has_lyrics:
            return "with-lyrics"
        if has_no_lyrics:
            return "no-lyrics"
        # No explicit fork → default to the safer no-lyrics (mood-instruction text).
        return "no-lyrics"

    @staticmethod
    def targeted_pools(fork: str) -> tuple[str, ...]:
        """Pools the generator drafts for a given fork (spec §3.2/§3.3)."""
        if fork == "with-lyrics":
            return ALL_POOLS  # lyric pools + paired reflection pools
        if fork == "both":
            return ALL_POOLS
        return REFLECTION_POOLS  # no-lyrics → reflection (mood-instruction) only

    # -- main entry -----------------------------------------------------------------
    def build_kit(
        self,
        survey: Mapping[str, Any],
        musician_id: str,
        *,
        brand_id: str | None = None,
        run_gate: bool = True,
        quality_profile: str = "draft",
    ) -> KitResult:
        """Build a DRAFT song-kit from an already-loaded survey dict.

        ``survey`` is the parsed ``SURVEY_TEMPLATE.yaml``-conformant response. The
        derivation helpers + family taxonomy are consumed; the engine drafts atom
        bodies; the result is gated to SPEC-739 and routed through G1–G8.
        """
        profile = survey_to_profile_dict(survey, musician_id)
        themes = survey_to_themes_yaml(survey)
        voice_profile = survey_to_voice_yaml(survey)
        resolved_brand = brand_id or f"{musician_id}_music"  # Q2 <handle>_music slug

        primary_themes = themes.get("primary_themes") or profile.get("themes") or []
        if not isinstance(primary_themes, list):
            primary_themes = [str(primary_themes)]
        matched = match_families(primary_themes, self.families)

        fork = self.select_fork(survey)
        with_block = survey.get("output_preferences_with_lyrics") or {}
        no_block = survey.get("output_preferences_no_lyrics") or {}
        lyric_form = with_block.get("lyric_form") if isinstance(with_block, Mapping) else None
        reflection_form = (
            no_block.get("reflection_form") if isinstance(no_block, Mapping) else None
        )
        reflection_perspective = (
            no_block.get("reflection_perspective") if isinstance(no_block, Mapping) else None
        )

        result = KitResult(
            musician_id=musician_id,
            brand_id=resolved_brand,
            fork=fork,
            matched_families=matched,
        )
        if not self.families:
            result.notes.append(
                "Topic-family taxonomy unavailable (PyYAML missing or "
                f"{_TOPIC_FAMILIES_REL} absent); families not matched — kit DEGRADED."
            )
        if not matched:
            result.notes.append(
                "No topic family matched surveyed primary_themes "
                f"({primary_themes!r}); using neutral fallback hints — review required."
            )

        # Choose the family driving content (first match; else a neutral fallback).
        active_family_id = matched[0] if matched else None
        active_family = self.families.get(active_family_id or "", {})
        topic_anchors = active_family.get("topic_anchors") or []
        default_themes = active_family.get("default_themes") or []
        genre = profile.get("primary_genre") or ""
        locale = self._locale_for(profile)

        pools_to_fill = self.targeted_pools(fork)
        for pool in pools_to_fill:
            kind = "lyric" if pool in LYRIC_POOLS else "mood_instruction"
            atom = self._draft_pool_atom(
                musician_id=musician_id,
                pool=pool,
                kind=kind,
                family_id=active_family_id or "unmapped",
                family=active_family,
                profile=profile,
                themes=themes,
                voice_profile=voice_profile,
                topic_anchors=topic_anchors,
                default_themes=default_themes,
                genre=genre,
                locale=locale,
                lyric_form=lyric_form,
                reflection_form=reflection_form,
                reflection_perspective=reflection_perspective,
            )
            result.pools[pool] = [atom]

        result.spec739 = self._spec739_verdict(result, pools_to_fill)
        if run_gate:
            result.diversity = run_diversity_gate(result, quality_profile=quality_profile)
        else:
            result.diversity = {"status": "not_requested"}
        return result

    def build_kit_from_path(
        self,
        survey_path: Path,
        musician_id: str,
        **kwargs: Any,
    ) -> KitResult:
        """Convenience: load a survey YAML from disk, then ``build_kit``."""
        from phoenix_v4.musician.survey_derivation import load_survey

        survey = load_survey(Path(survey_path))
        return self.build_kit(survey, musician_id, **kwargs)

    # -- helpers --------------------------------------------------------------------
    @staticmethod
    def _locale_for(profile: Mapping[str, Any]) -> str:
        """Routing locale hint for the real engine (EN default; CJK6 → Qwen).

        V1 default is en_US (Pearl_Writer). A real engine inspects this to route CJK6
        registers to Qwen per CLAUDE.md Tier policy. The orchestrator only passes the
        hint; it does not itself pick a model (no paid API anywhere).
        """
        loc = profile.get("locale") or profile.get("primary_locale")
        return str(loc) if loc else "en_US"

    def _draft_pool_atom(
        self,
        *,
        musician_id: str,
        pool: str,
        kind: str,
        family_id: str,
        family: Mapping[str, Any],
        profile: Mapping[str, Any],
        themes: Mapping[str, Any],
        voice_profile: Mapping[str, Any],
        topic_anchors: list[Any],
        default_themes: list[Any],
        genre: str,
        locale: str,
        lyric_form: str | None,
        reflection_form: str | None,
        reflection_perspective: str | None,
    ) -> DraftAtom:
        """Assemble one DraftAtom of ``floor`` variants via the pluggable engine."""
        stem = _POOL_STEM[pool]
        atom_id = f"{musician_id}_{pool}_01"
        atom = DraftAtom(
            atom_id=atom_id,
            slot_pool=pool,
            provenance={
                "generator": "song_kit_generator",
                "engine": getattr(self.engine, "name", type(self.engine).__name__),
                "family_id": family_id,
                "kind": kind,
                "spec": "MUSIC-ONBOARDING-SONG-KIT-V1-01",
                "locale": locale,
            },
        )
        for i in range(self.floor):
            anchor = str(topic_anchors[i % len(topic_anchors)]) if topic_anchors else ""
            theme = str(default_themes[i % len(default_themes)]) if default_themes else ""
            request = GenerationRequest(
                musician_id=musician_id,
                slot_pool=pool,
                position=_POOL_POSITION[pool],
                family_id=family_id,
                kind=kind,
                variant_index=i,
                profile=profile,
                themes=themes,
                voice_profile=voice_profile,
                family=family,
                topic_anchor=anchor,
                theme=theme,
                locale=locale,
                lyric_form=lyric_form,
                reflection_form=reflection_form,
                reflection_perspective=reflection_perspective,
            )
            body = self.engine.generate(request)
            atom.variants.append({"body": body})
        # Record the on-main short stem (lo_/lb_/lc_/ro_/rb_/rc_) for discoverability;
        # the canonical atom_id keeps the explicit <musician>_<POOL>_NN form.
        atom.provenance["atom_id_stem"] = stem
        return atom

    def _spec739_verdict(
        self,
        kit: KitResult,
        targeted: Iterable[str],
    ) -> dict[str, Any]:
        """SPEC-739 completion verdict: every targeted pool has ≥ ``floor`` variants."""
        targeted = list(targeted)
        per_pool: dict[str, int] = {}
        for pool in targeted:
            per_pool[pool] = sum(a.variant_count() for a in kit.pools.get(pool, []))
        deficient = {p: c for p, c in per_pool.items() if c < self.floor}
        return {
            "threshold_id": "SPEC-739-THRESHOLD-01",
            "floor": self.floor,
            "ceiling": SPEC_739_CEILING,
            "targeted_pools": targeted,
            "per_pool_variant_count": per_pool,
            "deficient_pools": deficient,
            "complete": not deficient,
        }


# ---------------------------------------------------------------------------------
# Thin functional entry point (offline-friendly)
# ---------------------------------------------------------------------------------
def build_kit_skeleton(
    survey: Mapping[str, Any],
    musician_id: str,
    *,
    engine: LyricMoodEngine | None = None,
    families: Mapping[str, Mapping[str, Any]] | None = None,
    brand_id: str | None = None,
    run_gate: bool = True,
) -> KitResult:
    """One-call helper: build a draft kit skeleton for a survey.

    Defaults to the deterministic stub engine, so this runs fully offline (no LLM, no
    network) — used by the bundled test and by dry-run smoke checks.
    """
    gen = SongKitGenerator(engine=engine, families=families)
    return gen.build_kit(survey, musician_id, brand_id=brand_id, run_gate=run_gate)
