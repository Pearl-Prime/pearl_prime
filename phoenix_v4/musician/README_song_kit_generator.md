# Song-Kit survey → generator orchestrator (Phase-2, first increment)

**Cap (governing):** `MUSIC-ONBOARDING-SONG-KIT-V1-01` (`docs/PEARL_ARCHITECT_STATE.md`)
**Spec (governing):** `docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md` (esp. §3)
**Workstream:** `ws_pearl_editor_song_kit_generator_20260612`
**Status:** `first-increment` — orchestrator scaffold + pluggable-engine interface + deterministic
offline stub + tests. The **real** lyric/mood generation engine is the sibling workstream
`ws_pearl_dev_lyric_mood_instruction_engine_20260612` (not built here).

---

## What this delivers

| File | Repo destination | Role |
|---|---|---|
| `song_kit_generator.py` | `phoenix_v4/musician/song_kit_generator.py` | The orchestrator (NEW module) |
| `test_song_kit_generator.py` | `tests/test_song_kit_generator.py` | Offline deterministic tests (27) |
| `README_song_kit_generator.md` | `phoenix_v4/musician/README_song_kit_generator.md` | This doc |

The orchestrator turns a completed musician survey into a **draft song-kit**: draft atoms emitted
into the existing 6 slot pools, grouped by the 8-family taxonomy, gated to the SPEC-739 ≥3-variants/
pool floor, and routed (when present) through the ratified G1–G8 diversity gate.

## Pipeline (spec §3)

```
survey dict (SURVEY_TEMPLATE.yaml-conformant)
   │
   ├─ survey_derivation.survey_to_{profile,themes,voice}_*   ← consumed, not re-parsed (§3.1)
   ├─ match_families(primary_themes, 8-family SSOT)          ← config/music/song_kit_topic_families.yaml (§2)
   ├─ select_fork(survey)                                    ← output_preferences_* fork (§3.2)
   │     with-lyrics → LYRIC_* + MUSIC_REFLECTION_* atoms
   │     no-lyrics   → MUSIC_REFLECTION_* MusicGen MOOD-INSTRUCTION TEXT only (no audio; §1.4)
   │     both        → all 6 pools
   ├─ engine.generate(GenerationRequest) per variant         ← PLUGGABLE (interface only here)
   ├─ SPEC-739 verdict: every targeted pool ≥ floor (3)      ← SPEC-739-THRESHOLD-01 (§3.5)
   └─ run_diversity_gate(kit)                                ← imports canonical G1-G8 (§3.6)
         → KitResult (per-pool DraftAtoms + verdicts + notes)
```

## Reuse-not-greenfield (anti-drift)

This module **extends** the existing music-mode subsystem; it authors **no** parallel artifact:

- **Derivation:** imports `phoenix_v4.musician.survey_derivation` (`survey_to_profile_dict` /
  `survey_to_themes_yaml` / `survey_to_voice_yaml`) — consumed, never re-implemented.
- **Slot pools:** the 6 pool names come from `phoenix_v4.planning.music_overlay`; the constructor
  asserts they stay in lockstep with `plan_music_injection` (a pool rename there raises, never
  silently desyncs).
- **Atom shape:** `DraftAtom.to_atom_yaml_obj()` emits exactly the on-main 2-key shape
  (`atom_id` + `variants: [{body: ...}]`) — same as
  `SOURCE_OF_TRUTH/musician_banks/test_artist_alpha/.../LYRIC_OPENING/lo_01.yaml`. No new pools,
  schema, or template vars; the established `{{musician_name}}` / `{{topic_anchor}}` / `{{theme}}` /
  `{{genre}}` / `{{persona_anchor}}` vars are preserved verbatim in bodies.
- **Diversity gate:** `run_diversity_gate` **imports** `scripts/ci/check_music_brand_diversity.py`
  (the canonical G1–G8 gate built by `ws_pearl_dev_music_brand_diversity_ci_guard_20260611`) and
  calls its entry point. That script is **not yet on main**, so the adapter reports
  `status="skipped"` with a clear note — it **never re-implements** the G1–G8 thresholds.
- **Taxonomy:** `load_topic_families` reads `config/music/song_kit_topic_families.yaml` (the SSOT);
  it does not mint families or topic_ids.

## Pluggable engine + LLM-tier compliance (spec §6, CLAUDE.md)

The actual LLM lyric/mood-instruction generation is a **pluggable engine call** — `LyricMoodEngine`
(a `Protocol`) is the **interface only**. The orchestrator never calls an LLM directly; all
generation flows through the injected engine.

- **Real engine** (sibling ws `ws_pearl_dev_lyric_mood_instruction_engine_20260612`) MUST route:
  - **English** lyrics/reflections → **Pearl_Writer / Claude subagent** (Tier 1, operator-present)
  - **CJK6** register → **Qwen** (Pearl Star via Ollama)
  - **unattended / scheduled** → **Gemma (EN) / Qwen (CJK6)** on Pearl Star via Ollama
  - **NO paid LLM API** anywhere. `GenerationRequest.locale` is the routing hint the engine reads.
- **Default engine here** = `DeterministicStubEngine`: zero network, zero LLM, no RNG/clock/I/O.
  It ships **no real lyrics** — it exists only so the orchestrator runs end-to-end offline and CI
  never reaches for a model.

Verified: the module passes the real `scripts/ci/audit_llm_callers.py` with **0 violations**
(banned-pattern regexes match API call shapes; `tests/` is globally exempt per
`config/governance/banned_llm_patterns.yaml`).

## Drafts are PROPOSED (spec §3.3)

Every atom has `status="draft"`. Output is a draft kit Pearl_Editor reviews and promotes (Tier-1).
The orchestrator does **not** ship atoms to a catalog run, and it renders **no audio** — the
no-lyrics fork emits MusicGen mood-instruction **TEXT** only (WAV render is Phase-B-gated,
`PEARL-STAR-JOB-QUEUE-V1-01`).

## Offline self-test

```bash
PYTHONPATH=. python3 -m pytest tests/test_song_kit_generator.py -q   # 27 passed, fully offline
```

Quick smoke (build a kit skeleton for a sample survey, no network/LLM):

```python
from phoenix_v4.musician.song_kit_generator import build_kit_skeleton

survey = {
    "identity": {"display_name": "River Vale", "primary_genre": "indie folk"},
    "themes": {"primary_themes": ["recovery", "the slow work of repair"]},
    "voice_craft": {"voice_person": "first_person", "register": "plain_spoken"},
    "output_preferences_with_lyrics": {"lyric_form": "free_verse", "companion_ai_song_consent": True},
}
kit = build_kit_skeleton(survey, "river_vale")   # DeterministicStubEngine by default
assert kit.complete                              # all 6 pools meet the SPEC-739 floor
print(kit.summary())                             # JSON-serializable audit summary
```

The default stub makes `build_kit_skeleton` runnable with zero infra. To dry-run with a custom
engine, pass `engine=YourEngine()` (any object with `.generate(GenerationRequest) -> str`).

## Public surface

`build_kit_skeleton`, `SongKitGenerator`, `KitResult`, `DraftAtom`, `GenerationRequest`,
`LyricMoodEngine`, `DeterministicStubEngine`, `load_topic_families`, `match_families`,
`run_diversity_gate`, plus the `LYRIC_POOLS` / `REFLECTION_POOLS` / `ALL_POOLS` / `SPEC_739_FLOOR`
constants.

## Remaining work (next increments — out of scope for this ws)

1. **Real lyric/mood engine** — `ws_pearl_dev_lyric_mood_instruction_engine_20260612` implements the
   two Tier-1 generation paths behind `LyricMoodEngine`.
2. **Bank writer** — serialize `KitResult` → `SOURCE_OF_TRUTH/musician_banks/<id>/approved_atoms/
   <SLOT_POOL>/<atom_id>.yaml`. A `DraftAtom.to_atom_yaml_obj()` producing the canonical 2-key shape
   is provided; the on-disk write + `survey_responses/` persistence is the Ahjan-first-kit ws's step.
3. **G1–G8 wiring** — once `scripts/ci/check_music_brand_diversity.py` lands, confirm the adapter's
   probed entry-point name matches the gate's final signature (the adapter already tries
   `evaluate_kit` / `check_kit` / `evaluate_atoms` / `run_gate` / `evaluate`).
4. **Ahjan reference kit** — `ws_pearl_editor_pearl_writer_ahjan_first_reference_kit_20260612` runs
   this orchestrator against an Ahjan survey, seeded from `teacher_banks/ahjan/`.
