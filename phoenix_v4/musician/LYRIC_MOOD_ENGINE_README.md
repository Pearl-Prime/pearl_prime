# Lyric / Mood-Instruction Engine (song-kit scaffold)

`phoenix_v4/musician/lyric_mood_engine.py`

The pluggable engine the **song-kit generator** calls (spec
`docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md`, esp. §3 and §6; cap
`MUSIC-ONBOARDING-SONG-KIT-V1-01`). It turns a musician's derived survey context into
a first **kit** of *draft* atoms for human review — it never auto-ships atoms to a
catalog run (spec §3.3, drafts are PROPOSED + Pearl_Editor-reviewed).

> **Phase-2 first-increment.** This is the engine scaffold + deterministic fallback +
> tier-router interface + tests. The Tier-1 (Pearl_Writer / Claude-subagent) callable is
> *injected* by the orchestrator at call time and is not wired here; offline / CI runs
> use the deterministic template. No audio is rendered in V1 (the no-lyrics fork emits
> MusicGen mood-instruction **TEXT** only — spec §1.4).

---

## What it produces

Given an `EngineContext` (the musician's derived `profile` / `themes` / `voice` dicts
from `survey_derivation.py` + the matched family hints from
`config/music/song_kit_topic_families.yaml`):

| Fork | Output |
|---|---|
| `with-lyrics` | Draft variant bodies for all 6 pools: `LYRIC_OPENING`, `LYRIC_BESTSELLER_BEAT`, `LYRIC_CLOSING` + the paired `MUSIC_REFLECTION_*` pools. |
| `no-lyrics` | Draft `MUSIC_REFLECTION_OPENING` / `BESTSELLER_BEAT` / `CLOSING` bodies **and** one MusicGen **mood-instruction TEXT line** (no audio). |

Each atom is emitted in the **exact on-main shape** (`atom_id` + `variants: [{body}]`,
matching `…/LYRIC_OPENING/lo_01.yaml`) via `Atom.to_atom_yaml_dict()`. Bodies use only
the established template variables — `{{musician_name}}`, `{{topic_anchor}}`,
`{{theme}}`, `{{genre}}`, `{{persona_anchor}}` (lyric pools) plus `{{healing_intent}}`
(reflection pools). The engine invents **no** new pools, atom schema, or template vars
(reuse-not-greenfield; the injection planner `phoenix_v4/planning/music_overlay.py`
consumes these pools unchanged — spec §3.4).

**SPEC-739 floor.** Every targeted pool is drafted to **≥3 variants** (`SPEC_739_FLOOR`;
ceiling 5, `SPEC_739_CEILING`). `KitResult.complete` is `True` only when every pool meets
the floor (spec §3.5). Diversity across those variants is checked by the **existing**
G1–G8 gate (spec §3.6) — the engine authors no parallel diversity gate.

---

## Tier routing (spec §6 — NO paid LLM API)

The LLM call is abstracted behind `TierRouter` so the engine **never imports a paid
client**. Tiers map to backends as follows:

| `Tier` | When | Backend |
|---|---|---|
| `T1_PEARL_WRITER` | English lyrics/reflections, **operator present** | Injected `pearl_writer_fn` callable (Pearl_Writer = Claude subagents). |
| `T2_QWEN_CJK` | CJK6 register | `phoenix_v4.llm.router.route_llm(language="zh-CN", …)` → Qwen on Pearl Star (Ollama). |
| `T2_GEMMA_UNATTENDED` | Unattended / scheduled English | `phoenix_v4.llm.router.route_llm(language="en", …)` → Gemma on Pearl Star (Ollama). |
| `TEMPLATE_FALLBACK` | Offline / CI / no backend wired | Deterministic in-module templates. |

### Why Tier-1 is injected, not imported

`phoenix_v4/llm/router.py` is the **canonical Tier-2 (unattended) router**; its own
docstring says *do not import it from ad-hoc scripts a human runs*. So for the
operator-present Tier-1 English path the orchestrator **injects** a Pearl_Writer callable
(`PearlWriterFn = Callable[[str, Optional[str]], str]`) into `TierRouter(pearl_writer_fn=…)`.
The engine carries no Claude/Anthropic import at all — it only holds a plain callable
slot. The two Tier-2 members reuse `route_llm` **by lazy import of the module name**, so
no `from openai import OpenAI` text appears in this file and the
`scripts/ci/audit_llm_callers.py` scan stays clean even though this path is not on any
exempt list.

### Tier resolution (`_resolve_tier`)

```
CJK6 language              → T2_QWEN_CJK         (Qwen)
English + operator + fn    → T1_PEARL_WRITER     (Claude subagent)
English + unattended/no-fn → T2_GEMMA_UNATTENDED (Gemma)
```

If the resolved tier has no live backend (no callable, router unreachable, exception),
`TierRouter.draft()` returns `None` and the engine **falls back to the deterministic
template** — it never raises on a missing backend, so a kit is always produced.

### Provenance

- `KitResult.tier_used` — the **resolved** tier (what was selected / attempted).
- `Atom.tier_used` — what **actually drafted** that pool's bodies (e.g. an LLM tier may
  be selected but, with no backend, individual pools come from `template_fallback`).

---

## Usage

```python
from phoenix_v4.musician.lyric_mood_engine import EngineContext, TierRouter, Tier, generate_kit

ctx = EngineContext(
    musician_id="ahjan",
    profile=profile_dict,            # survey_to_profile_dict(...)
    voice_profile=voice_dict,        # survey_to_voice_yaml(...)
    theme="quiet courage",
    family_id="quiet_courage",       # matched song_kit family
    topic_anchor="courage",          # canonical topic_id (⊂ family)
    persona_anchor="anxious_seeker",
    lyric_register_hint=family["lyric_register_hint"],
    instrumental_mood_hint=family["instrumental_mood_hint"],
    lyric_form="free_verse",         # output_preferences_with_lyrics.lyric_form
)

# Offline / CI (deterministic — no LLM, no network):
kit = generate_kit(ctx, fork="with-lyrics")           # router=None → fallback

# Operator-present English (Tier-1, inject a Pearl_Writer / Claude-subagent callable):
router = TierRouter(pearl_writer_fn=my_claude_subagent_call)
kit = generate_kit(ctx, fork="with-lyrics", router=router, operator_present=True)

# CJK6 (Tier-2 Qwen via the canonical router):
kit = generate_kit(ctx, fork="no-lyrics", router=TierRouter(), fork_language="zh-CN")

for pool, atom in kit.atoms.items():
    yaml_dict = atom.to_atom_yaml_dict()              # {"atom_id":…, "variants":[{"body":…}]}
if kit.fork == "no-lyrics":
    print(kit.mood_instruction)                       # MusicGen mood-instruction TEXT (no audio)
```

`pearl_writer_fn` signature: `fn(prompt: str, system: str | None) -> str` (return the
drafted text; one variant per line). Build prompts with `build_prompt(ctx, slot_pool, n)`
and `build_mood_instruction_prompt(ctx)` if you want to inspect them.

---

## Tests & self-verification

`tests/test_lyric_mood_engine.py` (22 tests, fully offline — no LLM, no network):

- both forks fill the right pools; SPEC-739 floor + ceiling; on-main atom shape +
  `atom_id` convention; template-vars stay within the allowed set; dedupe;
- tier resolution (T1 injected callable used; CJK→Qwen; English-unattended→Gemma;
  no-callable → fallback without crashing); `draft()` swallows backend errors → `None`;
- mood-instruction TEXT line on the no-lyrics fork; prompt builders; context backfill.

Run:

```bash
python3 -m pytest tests/test_lyric_mood_engine.py -q
```

LLM-policy self-check (must report 0 violations):

```bash
python3 scripts/ci/audit_llm_callers.py --roots phoenix_v4/musician/lyric_mood_engine.py
```

---

## Boundaries (what this scaffold does NOT do)

- **No audio.** MusicGen WAV render is Phase-B-gated (`MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS`
  §6 + `PEARL-STAR-JOB-QUEUE-V1-01`); V1 emits mood-instruction text only.
- **No survey parsing.** Consumes the derived dicts from `survey_derivation.py`; does not
  re-parse the raw survey (spec §3.1).
- **No family loading / canonical-topic validation here.** Family hints arrive on the
  `EngineContext`; the load-time mapping-integrity check lives with the
  `song_kit_generator` that loads `song_kit_topic_families.yaml` (spec §2).
- **No new diversity gate, no new freebie types, no catalog SSOT edits** (spec §1.4, §3.6).
- **No paid LLM API** anywhere (CLAUDE.md Tier policy; passes `audit_llm_callers.py`).

## Remaining work (handed to sibling / follow-on ws)

- The `song_kit_generator` caller that loads `song_kit_topic_families.yaml`, maps surveyed
  `themes.primary_themes` → `family_id` + `topic_anchor` + `persona_anchor`, builds the
  `EngineContext`, writes atoms to `SOURCE_OF_TRUTH/musician_banks/<id>/approved_atoms/<POOL>/`,
  and runs the load-time mapping-integrity check.
- Wiring the real Tier-1 Pearl_Writer (Claude-subagent) callable + Tier-2 round-trip
  against a live Pearl Star Ollama (requires Pearl Star reachable; out of scope offline).
- Routing generated atoms through the ratified G1–G8 diversity gate once
  `scripts/ci/check_music_brand_diversity.py` lands.
