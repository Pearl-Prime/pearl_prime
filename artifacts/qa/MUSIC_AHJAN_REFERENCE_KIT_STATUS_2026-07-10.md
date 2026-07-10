# Music Mode Phase A — Ahjan Reference Song-Kit — Status Note (2026-07-10)

**Authority:** `docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md` §4 (cap `MUSIC-ONBOARDING-SONG-KIT-V1-01`).
**Lane:** content-only reference-kit authoring (not the first-real-musician launch — see §4.3 below).

## What was authored (verified present on `origin/main`, 2026-07-10)

The Ahjan zeroth/reference song-kit is **already fully authored and live on `main`** — this note
documents and closes out that state; no new bank content was needed this session.

- `artifacts/musician_survey/ahjan_survey.yaml` — survey conforming verbatim to
  `SURVEY_TEMPLATE.yaml`, `synthetic: false`, both `output_preferences_with_lyrics` and
  `output_preferences_no_lyrics` forks populated, sourced from Ahjan's real corpus (2019 Budapest
  "Spiritual Music" Dharma talk + `TEACHER_DOCTRINE` atoms + `doctrine.yaml`/`signature_vibe.yaml`).
- `SOURCE_OF_TRUTH/musician_banks/ahjan/` bank — `profile.yaml`, `themes.yaml`, `voice_profile.yaml`,
  `survey_responses/2026-06-12.yaml`, `INTRO_2P_TEMPLATE.yaml`, `CONCLUSION_2P_TEMPLATE.yaml`. Voice
  locked to `signature_vibe.yaml` (observational, plain-spoken, show-don't-tell; non-devotional,
  non-cathartic; forbidden words `manifest`/`guaranteed`/`breakthrough`/`amazing`).
- **6 slot pools, 3 atoms × 3 variants each = 9 variants/pool** — `LYRIC_OPENING`, `LYRIC_CLOSING`,
  `LYRIC_BESTSELLER_BEAT`, `MUSIC_REFLECTION_OPENING`, `MUSIC_REFLECTION_CLOSING`,
  `MUSIC_REFLECTION_BESTSELLER_BEAT`. This is **3× the `SPEC-739` ≥3-variants/pool floor**.
  `MUSIC_REFLECTION_*` atoms carry `musicgen_mood_instruction` **text only** (no-lyrics fork; no
  audio render, per spec §1.4). Spot-checked for craft/non-placeholder content — confirmed authored,
  body-anchored, healing-oriented prose consistent with Ahjan's teacher-bank voice.
- `config/music/music_brand_registry.yaml` — `ahjan_music` entry, `status: active`,
  `survey_yaml_pointer` resolves, slug per Q2 convention (`<handle>_music`).

**Where it lives in git history:** the source PR (**#1547**, ws `ws_ahjan_reference_song_kit_20260612`)
was authored and merged as commit `e3b555be6c68e016b9df7a8df5079d5b972649da` on 2026-06-17, but that
commit is **not** an ancestor of the current `origin/main` tip — the content reached `main` via the
`#4486` Waystream-EPUB-wave mega-commit (`321379f8f8`, `git log -- SOURCE_OF_TRUTH/musician_banks/ahjan/profile.yaml`
on `origin/main` resolves to that commit). Content is verified byte-present and internally consistent
on `main` today regardless of which commit chain carried it.

**Governance note (flag, not a blocker):** PR #1547's own title was
`[DO-NOT-MERGE] feat(music): Ahjan zeroth/reference song-kit ...` — an explicit operator-review draft
marker — yet GitHub shows it as `MERGED`. The content itself is self-verified ALL-GREEN per the PR's
own verifier (schema-valid, ≥3 variants/pool, template-var set, survey↔derivation parity, voice
guardrails clean) and matches the ratified spec exactly, so this note does not re-litigate the
content — it flags the DO-NOT-MERGE-but-merged provenance for operator awareness only.

## What remains (Phase-2 / Phase-B build lanes — NOT content gaps)

1. **Survey → generator engine** (spec §3) — not built; today's 6 pools are hand-authored per
   musician (Pearl_Editor/Pearl_Writer), same as `test_artist_alpha`. Ahjan is the reference exemplar
   this future engine is measured against, not evidence the engine exists.
2. **Diversity-gate CI script** `scripts/ci/check_music_brand_diversity.py` (G1–G8) — gate is
   ratified in spec, script is an unbuilt Phase-2 target (`ws_pearl_dev_music_brand_diversity_ci_guard_20260611`).
3. **5-ceiling backfill** — current 3-atom/pool authoring is the strong floor (9 variants after
   ×3-variant fanout); the optional 5-atom ceiling is iterative, not required for Phase A.
4. **YouTube → freebie bridge** (spec §5) — schema/config only, no live wiring.
5. **Audio render** — Phase-B-gated on Pearl Star MusicGen + job-queue dependency; V1 is text-only
   by design (spec §1.4), not a gap.
6. **V2's open `Q-MM-V2-FIRST-REAL-MUSICIAN-01`** (operator-nominated first *real* external musician)
   stays **OPEN and uncollapsed** by this kit — Ahjan is internal gold reference only, per spec §4.3 /
   `Q-MSK-AHJAN-VS-V2-FIRST-01` (FLAGGED, operator-only).

## Honest blockers for this content-only lane

**None.** The reference-kit deliverable this prompt asked for was already authored, registered, and
live on `origin/main` before this session started. This session's only action was authoring this
closeout note (no bank/atom/registry edits were needed or made).
