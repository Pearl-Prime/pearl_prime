"""Lyric / mood-instruction engine scaffold (Phase-2 build for the song-kit).

Authority chain
---------------
- Cap (governing):  ``MUSIC-ONBOARDING-SONG-KIT-V1-01`` in ``docs/PEARL_ARCHITECT_STATE.md``
- Spec (governing): ``docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md`` (esp. §3, §6)
- Families SSOT:    ``config/music/song_kit_topic_families.yaml`` (the 8 additive families, §2)
- Atom bank shape:  ``MUSIC-MODE-V1-01`` — 6 slot pools, atom = ``atom_id`` + ``variants[].body``
- LLM policy:       ``CLAUDE.md`` Tier policy + ``scripts/ci/audit_llm_callers.py``

What this module is
-------------------
The *pluggable engine* that ``song_kit_generator`` calls (spec §3). It turns a
musician's derived survey context into a first **kit** of DRAFT atoms:

* **with-lyrics fork** → draft ``LYRIC_OPENING`` / ``LYRIC_CLOSING`` /
  ``LYRIC_BESTSELLER_BEAT`` variant bodies (plus the paired ``MUSIC_REFLECTION_*``
  pools), honoring ``voice_profile`` register/pacing + the family
  ``lyric_register_hint`` + ``output_preferences_with_lyrics.lyric_form``.
* **no-lyrics fork** → draft ``MUSIC_REFLECTION_OPENING`` / ``CLOSING`` /
  ``BESTSELLER_BEAT`` bodies **and** a MusicGen mood-instruction TEXT line
  (no audio is rendered in V1 — spec §1.4).

Tier routing (spec §6 — NO paid LLM API)
----------------------------------------
The LLM call is abstracted behind a small ``TierRouter`` so callers choose the
Tier without this module ever importing a paid client:

* ``Tier.T1_PEARL_WRITER``  — English lyrics/reflections, operator-present.
  Pearl_Writer = Claude subagents. This module does **not** import the unattended
  router for human-run prose (that router's own docstring forbids it); instead the
  orchestrator/Pearl_Editor injects a ``pearl_writer_fn`` callable.
* ``Tier.T2_QWEN_CJK``      — CJK6 register → ``phoenix_v4.llm.router.route_llm``
  (Qwen on Pearl Star via Ollama). The router is the *canonical* Tier-2 artifact
  (the only file exempted for the OpenAI-as-Ollama client); this module reuses it
  by name, it does not re-implement an Ollama client.
* ``Tier.T2_GEMMA_UNATTENDED`` — unattended English fallback → same ``route_llm``
  (Gemma on Pearl Star via Ollama).

When no callable / router is available (offline, CI, tests) the engine falls back
to a **deterministic template** so it always produces a runnable kit. The fallback
draws on the on-main exemplar bodies' grammar (``test_artist_alpha`` atoms) and the
family hints — it is intentionally plain so a human reviewer (Pearl_Editor) promotes
or rewrites it. Drafts are PROPOSED, never auto-shipped to a catalog run (spec §3.3).

Output shape (unchanged — spec §3.3)
------------------------------------
Atoms are emitted as ``{"atom_id": ..., "variants": [{"body": ...}, ...]}`` matching
the on-main shape (see ``…/LYRIC_OPENING/lo_01.yaml``). Bodies use the established
template vars: ``{{musician_name}}``, ``{{topic_anchor}}``, ``{{theme}}``,
``{{genre}}``, ``{{persona_anchor}}`` (lyric pools) plus ``{{healing_intent}}``
(reflection pools). The engine invents NO new pools / schema / template vars.
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence

# ---------------------------------------------------------------------------
# Slot-pool taxonomy (per MUSIC-MODE-V1-01 — fixed; the engine never invents pools)
# ---------------------------------------------------------------------------
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

# The atom template variables that bodies may reference (per on-main atom shape).
# Lyric pools use the first five; reflection pools additionally use healing_intent.
TEMPLATE_VARS: tuple[str, ...] = (
    "musician_name",
    "topic_anchor",
    "theme",
    "genre",
    "persona_anchor",
    "healing_intent",
)

# SPEC-739-THRESHOLD-01: a pool is "complete for a cell" at >=3 variants (5 ceiling).
SPEC_739_FLOOR: int = 3
SPEC_739_CEILING: int = 5


class Tier(enum.Enum):
    """Which Tier-routed backend drafts the prose (spec §6).

    No member maps to a paid API. T1 is an injected Claude-subagent callable;
    the two T2 members route to local Ollama via ``phoenix_v4.llm.router``.
    """

    T1_PEARL_WRITER = "t1_pearl_writer"          # English, operator-present (Claude subagent)
    T2_QWEN_CJK = "t2_qwen_cjk"                  # CJK6 register → Qwen/Ollama
    T2_GEMMA_UNATTENDED = "t2_gemma_unattended"  # unattended English → Gemma/Ollama
    TEMPLATE_FALLBACK = "template_fallback"      # deterministic, offline/CI


# A Pearl_Writer callable: (prompt, system) -> drafted text. Injected by the
# orchestrator when an operator-present Claude subagent is available. Kept as a
# plain Callable so this module imports no paid client.
PearlWriterFn = Callable[[str, Optional[str]], str]


@dataclass
class TierRouter:
    """Resolves a Tier to a text-drafting backend without importing a paid client.

    Parameters
    ----------
    pearl_writer_fn:
        Optional injected callable for ``Tier.T1_PEARL_WRITER`` (Claude subagent /
        Pearl_Writer). If ``None``, T1 degrades to the deterministic fallback.
    allow_tier2_router:
        If ``True`` (default), the CJK / unattended tiers call
        ``phoenix_v4.llm.router.route_llm`` (local Ollama). Set ``False`` in tests
        / offline to force the deterministic fallback for every tier.
    """

    pearl_writer_fn: Optional[PearlWriterFn] = None
    allow_tier2_router: bool = True

    def draft(
        self,
        tier: Tier,
        prompt: str,
        *,
        system: Optional[str] = None,
        language: str = "en",
    ) -> Optional[str]:
        """Return drafted text for ``tier``, or ``None`` to signal fallback.

        Never raises on a missing backend — a ``None`` return tells the engine to
        use its deterministic template (so the engine always yields a kit).
        """
        if tier is Tier.T1_PEARL_WRITER:
            if self.pearl_writer_fn is None:
                return None
            try:
                out = self.pearl_writer_fn(prompt, system)
            except Exception:
                return None
            return out if isinstance(out, str) and out.strip() else None

        if tier in (Tier.T2_QWEN_CJK, Tier.T2_GEMMA_UNATTENDED):
            if not self.allow_tier2_router:
                return None
            return self._route_via_local_ollama(tier, prompt, system, language)

        # TEMPLATE_FALLBACK (or anything unexpected): deterministic path.
        return None

    @staticmethod
    def _route_via_local_ollama(
        tier: Tier,
        prompt: str,
        system: Optional[str],
        language: str,
    ) -> Optional[str]:
        """Call the canonical Tier-2 router (local Ollama). Import is lazy + by
        name so this module carries no paid-client import and stays audit-clean."""
        try:
            # Reuse the canonical Tier-2 artifact (the only file exempted for the
            # OpenAI-as-Ollama client). We import the function by name only.
            from phoenix_v4.llm import router as _tier2_router
        except Exception:
            return None
        # CJK tier forces a CJK language hint so the router selects Qwen; the
        # unattended English tier selects Gemma.
        lang = "zh-CN" if tier is Tier.T2_QWEN_CJK else (language or "en")
        try:
            result = _tier2_router.route_llm(
                prompt=prompt, system=system, language=lang, stream=False
            )
        except Exception:
            return None
        if isinstance(result, str) and result.strip():
            return result
        return None


# ---------------------------------------------------------------------------
# Engine inputs / outputs
# ---------------------------------------------------------------------------
@dataclass
class EngineContext:
    """The conditioning context the engine drafts from (spec §3.1).

    These fields mirror what ``phoenix_v4.musician.survey_derivation`` already
    produces (profile / themes / voice dicts) + the matched family hints from
    ``song_kit_topic_families.yaml``. The engine consumes them; it does NOT
    re-parse the raw survey.
    """

    musician_id: str
    profile: Mapping[str, Any] = field(default_factory=dict)        # survey_to_profile_dict()
    theme: str = ""                                                 # one surveyed primary theme
    family_id: str = ""                                             # matched song_kit family
    topic_anchor: str = ""                                          # canonical topic_id (⊂ family)
    persona_anchor: str = ""                                        # persona cell label
    genre: str = ""                                                 # primary_genre
    healing_intent: str = ""                                        # healing_intent_summary
    voice_profile: Mapping[str, Any] = field(default_factory=dict)  # survey_to_voice_yaml()
    lyric_register_hint: str = ""                                   # family hint (with-lyrics)
    instrumental_mood_hint: str = ""                                # family hint (no-lyrics)
    lyric_form: str = "free_verse"                                  # from output_preferences_with_lyrics
    reflection_form: str = "mixed"                                  # from output_preferences_no_lyrics
    reflection_perspective: str = "musician"                        # from output_preferences_no_lyrics

    def __post_init__(self) -> None:
        # Backfill scalar fields from the derived profile so callers can pass a
        # profile dict and let the engine fill blanks (additive, never overwrites).
        if not self.genre:
            self.genre = str(self.profile.get("primary_genre") or "")
        if not self.healing_intent:
            self.healing_intent = str(self.profile.get("healing_intent_summary") or "")

    @property
    def musician_name(self) -> str:
        return str(self.profile.get("display_name") or self.musician_id)


@dataclass
class Atom:
    """A draft atom in the on-main shape (``atom_id`` + ``variants[].body``)."""

    atom_id: str
    variants: list[dict[str, str]] = field(default_factory=list)
    slot_pool: str = ""
    tier_used: str = ""  # provenance: which Tier drafted it (for review/audit)

    def to_atom_yaml_dict(self) -> dict[str, Any]:
        """Exact on-main serialization (``atom_id`` + ``variants: [{body}]``)."""
        return {
            "atom_id": self.atom_id,
            "variants": [{"body": v["body"]} for v in self.variants],
        }

    @property
    def variant_count(self) -> int:
        return len(self.variants)

    @property
    def meets_spec_739(self) -> bool:
        return self.variant_count >= SPEC_739_FLOOR


@dataclass
class KitResult:
    """The drafted kit for one (musician, theme, family, topic, persona) cell."""

    musician_id: str
    fork: str  # "with-lyrics" | "no-lyrics"
    atoms: dict[str, Atom] = field(default_factory=dict)  # slot_pool -> Atom
    mood_instruction: str = ""  # MusicGen mood-instruction TEXT (no-lyrics fork only)
    tier_used: str = ""

    @property
    def pools_meeting_floor(self) -> list[str]:
        return [p for p, a in self.atoms.items() if a.meets_spec_739]

    @property
    def complete(self) -> bool:
        """A cell is complete when EVERY targeted pool meets the SPEC-739 floor."""
        return bool(self.atoms) and all(a.meets_spec_739 for a in self.atoms.values())


# ---------------------------------------------------------------------------
# Prompt construction (used for the LLM tiers; the fallback ignores the prompt)
# ---------------------------------------------------------------------------
def _format_voice(voice: Mapping[str, Any]) -> str:
    bits = []
    for k in ("voice_person", "register", "pacing"):
        v = voice.get(k)
        if v:
            bits.append(f"{k}={v}")
    devices = voice.get("signature_devices") or []
    if isinstance(devices, (list, tuple)) and devices:
        bits.append("signature_devices=" + "; ".join(str(d) for d in devices))
    return ", ".join(bits)


def build_prompt(ctx: EngineContext, slot_pool: str, n_variants: int) -> str:
    """Build the drafting prompt for an LLM tier. Pure text; deterministic."""
    is_lyric = slot_pool in LYRIC_POOLS
    hint = ctx.lyric_register_hint if is_lyric else ctx.instrumental_mood_hint
    kind = "lyric block" if is_lyric else "music-reflection passage"
    form = ctx.lyric_form if is_lyric else f"{ctx.reflection_form}/{ctx.reflection_perspective}"
    allowed = "{{musician_name}}, {{topic_anchor}}, {{theme}}, {{genre}}, {{persona_anchor}}"
    if not is_lyric:
        allowed += ", {{healing_intent}}"
    return (
        f"Draft {n_variants} distinct {kind} variants for the '{slot_pool}' slot pool "
        f"of musician '{ctx.musician_name}' (genre: {ctx.genre or 'unspecified'}).\n"
        f"Theme: {ctx.theme or 'unspecified'}. Topic anchor: {ctx.topic_anchor or 'unspecified'}. "
        f"Song-kit family: {ctx.family_id or 'unspecified'}.\n"
        f"Form: {form}.\n"
        f"Voice profile: {_format_voice(ctx.voice_profile) or 'plain, honest'}.\n"
        f"Register/mood guidance: {hint or 'understated, honest, non-saccharine'}.\n"
        f"Healing intent: {ctx.healing_intent or 'gentle, non-dramatizing'}.\n"
        f"Rules: keep each variant 1-3 short lines; you MAY use these template "
        f"placeholders verbatim where natural: {allowed}. Return one variant per line, "
        f"no numbering, no commentary."
    )


def build_mood_instruction_prompt(ctx: EngineContext) -> str:
    """Build the prompt for the per-cell MusicGen mood-instruction TEXT (no-lyrics)."""
    return (
        f"Write ONE MusicGen mood-instruction line (a single sentence of instrumental "
        f"direction, no lyrics, no audio) for musician '{ctx.musician_name}' "
        f"(genre: {ctx.genre or 'unspecified'}), theme '{ctx.theme}', "
        f"family '{ctx.family_id}'. Anchor it to this mood hint: "
        f"{ctx.instrumental_mood_hint or 'warm, unhurried, non-climactic'}. "
        f"Describe instrumentation, tempo feel, and emotional arc. One line only."
    )


# ---------------------------------------------------------------------------
# Deterministic template fallback (offline / CI / no-LLM)
# ---------------------------------------------------------------------------
# Per-pool body templates. Grammar mirrors the on-main exemplar atoms
# (test_artist_alpha) so a reviewer recognizes the shape; the {{...}} vars are the
# established template variables and stay UNRESOLVED (the injection planner /
# renderer resolves them downstream).
_LYRIC_TEMPLATES: dict[str, tuple[str, ...]] = {
    "LYRIC_OPENING": (
        "Morning comes in plain —\n{{musician_name}} names {{theme}} before {{persona_anchor}} can brace for it.",
        "{{theme}} sits at the table;\n{{musician_name}} keeps it {{genre}}-quiet for a {{topic_anchor}} day.",
        "You count the exits, {{musician_name}} counts the breath —\nno hurry in how {{theme}} is said.",
        "Thin light on the sill;\n{{musician_name}} lets {{topic_anchor}} be small enough to hold.",
        "Before the chapter runs, {{musician_name}} opens slow —\n{{theme}} as invitation, not instruction, for {{persona_anchor}}.",
    ),
    "LYRIC_BESTSELLER_BEAT": (
        "Here is the hinge — {{musician_name}} leans in:\n{{theme}} as proof, not poster, for {{persona_anchor}} spines.",
        "Mid-chapter weather: {{topic_anchor}} thickens;\n{{musician_name}} offers {{genre}} air, steady as a held note.",
        "Not a climax — a clearer frequency:\n{{musician_name}} tunes {{theme}} until the shoulders listen.",
        "The turn arrives plain;\n{{musician_name}} keeps {{theme}} honest where {{topic_anchor}} wants to rush.",
        "One true line at the center:\n{{musician_name}} sets {{theme}} down so {{persona_anchor}} can pick it up.",
    ),
    "LYRIC_CLOSING": (
        "Leave the door cracked for quiet —\n{{musician_name}} already set {{theme}} on the sill.",
        "Tomorrow can wait its turn;\n{{musician_name}} ends in {{genre}} hush for {{persona_anchor}} bones.",
        "{{topic_anchor}} still knocks; you answered once —\n{{musician_name}} marks that, gentle and unforced.",
        "No verdict tonight;\n{{musician_name}} lets {{theme}} stay available, not urgent.",
        "Close the chapter soft;\n{{musician_name}} leaves {{theme}} where {{persona_anchor}} can find it again.",
    ),
}

_REFLECTION_TEMPLATES: dict[str, tuple[str, ...]] = {
    "MUSIC_REFLECTION_OPENING": (
        "{{musician_name}} opens {{topic_anchor}} with {{persona_anchor}} honesty — {{theme}} as invitation, not instruction. Let this reflection widen the chapter without rushing the body.",
        "Listen for {{musician_name}}'s {{genre}} restraint: {{theme}} arrives as room to breathe, especially when the day narrows.",
        "A short pause before the chapter runs: {{musician_name}} reminds you that {{healing_intent}} can sound like understatement.",
        "{{musician_name}} begins quietly with {{theme}} — no performance of calm, only a place to set {{topic_anchor}} down.",
        "Before reading on, {{musician_name}} offers {{persona_anchor}} a slower breath; {{theme}} is allowed to be plain.",
    ),
    "MUSIC_REFLECTION_BESTSELLER_BEAT": (
        "Bestseller beat: {{musician_name}} steadies {{theme}} while {{topic_anchor}} tries to speed-read the nervous system — stay with the proof the body already felt.",
        "Here {{genre}} craft meets {{persona_anchor}} reality: {{musician_name}} asks you to notice one bodily shift worth keeping.",
        "{{healing_intent}} — repeated on purpose at the hinge, because {{musician_name}} knows doubt returns mid-chapter.",
        "At the turn, {{musician_name}} holds {{theme}} still; {{topic_anchor}} loosens its grip by a measurable degree.",
        "Mid-chapter, {{musician_name}} keeps {{theme}} honest for {{persona_anchor}} — not louder, just clearer.",
    ),
    "MUSIC_REFLECTION_CLOSING": (
        "{{musician_name}} closes the chapter door softly: {{theme}} stays available, not urgent, for {{persona_anchor}} readers.",
        "Carry {{topic_anchor}} without a verdict — {{musician_name}}'s {{genre}} ethic favors return visits over one-night catharsis.",
        "If the body is tired from trying, {{musician_name}} names {{theme}} as permission to stop auditioning for calm.",
        "{{musician_name}} leaves {{theme}} where {{persona_anchor}} can return to it; {{healing_intent}} keeps, it does not expire.",
        "End in {{genre}} hush: {{musician_name}} lets {{topic_anchor}} rest without forcing it shut.",
    ),
}


def _dedupe_keep_order(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        norm = it.strip()
        key = norm.lower()
        if norm and key not in seen:
            seen.add(key)
            out.append(norm)
    return out


def _fallback_bodies(slot_pool: str, n: int) -> list[str]:
    """Deterministic template bodies for a pool (>= n, capped to available)."""
    table = _LYRIC_TEMPLATES if slot_pool in LYRIC_POOLS else _REFLECTION_TEMPLATES
    pool = list(table.get(slot_pool, ()))
    return pool[: max(n, SPEC_739_FLOOR)]


def _parse_llm_variants(raw: str, n: int) -> list[str]:
    """Split LLM output into variant bodies (one per line; strip numbering)."""
    out: list[str] = []
    for line in (raw or "").splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", s)  # strip bullet/number prefixes
        s = s.strip().strip('"').strip()
        if s:
            out.append(s)
    out = _dedupe_keep_order(out)
    return out[:n] if n else out


def _atom_id(musician_id: str, slot_pool: str, index: int) -> str:
    """On-main id convention: ``<musician_id>_<SLOT_POOL>_<NN>``."""
    return f"{musician_id}_{slot_pool}_{index:02d}"


# ---------------------------------------------------------------------------
# Core drafting
# ---------------------------------------------------------------------------
def _draft_pool_bodies(
    ctx: EngineContext,
    slot_pool: str,
    router: TierRouter,
    tier: Tier,
    n_variants: int,
) -> tuple[list[str], str]:
    """Draft >= n_variants bodies for one pool; return (bodies, tier_used_label).

    Tries the requested tier; if it returns nothing (no backend / offline / error),
    falls back to the deterministic template so the pool always reaches the floor.
    """
    n = max(n_variants, SPEC_739_FLOOR)
    tier_used = Tier.TEMPLATE_FALLBACK.value
    bodies: list[str] = []

    if tier is not Tier.TEMPLATE_FALLBACK:
        prompt = build_prompt(ctx, slot_pool, n)
        system = (
            "You are Pearl_Writer drafting therapeutic music atoms for human review. "
            "Honor the voice profile; never dramatize pain; keep it plain and honest."
        )
        raw = router.draft(tier, prompt, system=system, language="en")
        if raw:
            bodies = _parse_llm_variants(raw, n)
            if len(bodies) >= SPEC_739_FLOOR:
                tier_used = tier.value

    if len(bodies) < SPEC_739_FLOOR:
        # Backfill (or fully fall back) with deterministic templates.
        for b in _fallback_bodies(slot_pool, n):
            if b not in bodies:
                bodies.append(b)
        bodies = _dedupe_keep_order(bodies)
        if tier_used == Tier.TEMPLATE_FALLBACK.value:
            pass  # pure fallback
        # else: partial LLM + template backfill keeps the LLM tier label.

    return bodies[:n], tier_used


def _draft_mood_instruction(
    ctx: EngineContext, router: TierRouter, tier: Tier
) -> tuple[str, str]:
    """Draft the per-cell MusicGen mood-instruction TEXT line (no-lyrics fork)."""
    if tier is not Tier.TEMPLATE_FALLBACK:
        raw = router.draft(
            tier,
            build_mood_instruction_prompt(ctx),
            system="You write a single instrumental MusicGen mood-instruction line. No lyrics.",
            language="en",
        )
        if raw and raw.strip():
            line = raw.strip().splitlines()[0].strip()
            if line:
                return line, tier.value
    # Deterministic fallback: compose from the family mood hint + genre/theme.
    hint = ctx.instrumental_mood_hint or "warm, unhurried, non-climactic"
    theme = ctx.theme or "stillness"
    genre = ctx.genre or "ambient"
    line = (
        f"Instrumental {genre} mood for '{theme}': {hint} "
        f"No vocals; let space carry the feeling (MusicGen text-only, no audio rendered in V1)."
    )
    return line, Tier.TEMPLATE_FALLBACK.value


def _resolve_tier(fork_language: str, operator_present: bool, router: TierRouter) -> Tier:
    """Pick a Tier per the policy (spec §6).

    * CJK6 register → Qwen (T2).
    * English + operator-present + a Pearl_Writer callable wired → T1 (Claude subagent).
    * English + unattended (or no T1 callable) → Gemma (T2).
    * No router backend at all → deterministic fallback is reached anyway (draft() → None).
    """
    if fork_language and fork_language.lower() not in ("en", "english"):
        return Tier.T2_QWEN_CJK
    if operator_present and router.pearl_writer_fn is not None:
        return Tier.T1_PEARL_WRITER
    return Tier.T2_GEMMA_UNATTENDED


def generate_kit(
    ctx: EngineContext,
    *,
    fork: str,
    router: Optional[TierRouter] = None,
    operator_present: bool = True,
    fork_language: str = "en",
    variants_per_pool: int = SPEC_739_FLOOR,
) -> KitResult:
    """Generate one draft kit for a (musician, theme, family, topic, persona) cell.

    Parameters
    ----------
    fork:
        ``"with-lyrics"`` → lyric pools + paired reflection pools;
        ``"no-lyrics"``   → reflection pools + a MusicGen mood-instruction line.
    router:
        A ``TierRouter``. If ``None``, a router with no backend is used → the engine
        runs fully on the deterministic template (offline / test default).
    operator_present:
        Whether an operator is present (selects Tier-1 Pearl_Writer when a callable
        is wired and the fork is English).
    fork_language:
        ``"en"`` (Gemma/Pearl_Writer) or a CJK6 code (``zh-CN`` etc. → Qwen).
    variants_per_pool:
        Target variants per pool. Floored at SPEC-739 (>=3); ceiling 5 (spec §3.5).

    Returns
    -------
    KitResult with one ``Atom`` per targeted pool (>=3 variants each) and, on the
    no-lyrics fork, a ``mood_instruction`` TEXT line. NO audio is rendered (spec §1.4).
    """
    if fork not in ("with-lyrics", "no-lyrics"):
        raise ValueError(f"fork must be 'with-lyrics' or 'no-lyrics', got {fork!r}")
    if router is None:
        router = TierRouter()  # no backend → deterministic fallback everywhere
    n = min(max(int(variants_per_pool), SPEC_739_FLOOR), SPEC_739_CEILING)

    tier = _resolve_tier(fork_language, operator_present, router)
    result = KitResult(musician_id=ctx.musician_id, fork=fork, tier_used=tier.value)

    target_pools = ALL_POOLS if fork == "with-lyrics" else REFLECTION_POOLS

    for slot_pool in target_pools:
        bodies, tier_used = _draft_pool_bodies(ctx, slot_pool, router, tier, n)
        atom = Atom(
            atom_id=_atom_id(ctx.musician_id, slot_pool, 1),
            variants=[{"body": b} for b in bodies],
            slot_pool=slot_pool,
            tier_used=tier_used,
        )
        result.atoms[slot_pool] = atom

    if fork == "no-lyrics":
        result.mood_instruction, _mood_tier = _draft_mood_instruction(ctx, router, tier)

    return result


__all__ = [
    "Tier",
    "TierRouter",
    "PearlWriterFn",
    "EngineContext",
    "Atom",
    "KitResult",
    "LYRIC_POOLS",
    "REFLECTION_POOLS",
    "ALL_POOLS",
    "TEMPLATE_VARS",
    "SPEC_739_FLOOR",
    "SPEC_739_CEILING",
    "build_prompt",
    "build_mood_instruction_prompt",
    "generate_kit",
]
