# Teacher × Manga 30s — Style Spread Confirming Review

**Date:** 2026-05-08
**Reviewer:** Pearl_Editor
**Project:** PRJ-TEACHER-MANGA-30S-VIDEO-V1
**Subsystem:** teacher_mode (with manga_pipeline + video_pipeline awareness)
**Action item:** §13b in `docs/specs/TEACHER_MANGA_30S_VIDEO_V1_SPEC.md`
**Operator gate cleared:** Q2 = approve (6 / 3 / 2 / 1 distribution accepted as-is)

## Inputs read

- `CLAUDE.md`
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/specs/TEACHER_MANGA_30S_VIDEO_V1_SPEC.md` — full spec, with focus on §6 STYLE SPREAD, §5 BRAND BINDING, §7 LOCALE LOCK, §11 ANTI-DRIFT, §15 D1/D2/D3, §16 Q1–Q4
- `artifacts/qa/teacher_manga_30s_locale_brand_matrix_2026-05-08.tsv` — all 13 rows; rationale column read for every row
- `config/authoring/pen_name_teacher_profiles.yaml` — citation-anchor stub (no per-teacher voice tags; relied on `brand_lora_plans.character_loras.<teacher>.notes` + audiobook anchor topic for voice signal)
- `config/manga/canonical_brand_list.yaml` — demographic per brand (37-brand canon)
- `config/manga/brand_lora_plans.yaml` — `brand_suffixes` + `character_loras.<teacher>.{style_ref, notes}`

## Methodology

For each of the 12 V1 teachers I confirmed three things, in this order:

1. **Voice fit.** Does the proposed style mode hold the teacher's signature register (drawn from the `character_loras.<teacher>.notes` somatic/bearing line + the audiobook chapter-1 topic anchor + the spec's signature-problem mapping in §5)?
2. **Demographic fit.** Does the proposed style mode honor the brand's canonical demographic (per `canonical_brand_list.yaml`) at the audience-target level — separate from the teacher's own MC identity, which §4 keeps locked across all modes?
3. **Sensory hook.** Does the style mode give the 30-second arc (HOOK → STRUGGLE → RELEASE per §2) a concrete, embodied imagery vocabulary — not a rhetorical one (per the §2 / `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` requirement)?

A row gets **SIGN-OFF** only if all three hold. **FLAG-FOR-OPERATOR** is reserved for rows where at least one of the three is genuinely false or where I would silently re-allocate if the matrix were mine to mutate.

I did not re-derive the distribution. The 6 / 3 / 2 / 1 is operator-approved per Q2; my job is confirmation, not redesign.

## Adi_da (row 13) explicitly out of V1 scope for this review

Spec §16 Q1 default is **(b) defer**; operator has not overridden. Adi_da's row remains on the matrix as a 13th-deliverable candidate but is not part of the V1 fan-out. I therefore review the 12 V1 rows only. If operator later picks Q1=(a), a one-row addendum to this review will be needed (separate cap follow-up).

---

## Per-teacher review

### 1. ahjan — `stillness_press` / josei / **pure_manga** / en-US

`character_loras.ahjan.notes`: "South Asian male, warm expression, contemplative bearing; forest-refuge scenes use same face with earth-tone wardrobe." Audiobook anchor = `ahjan_anxiety_ch1.txt`. **Voice fit:** the contemplative-bearing register lives most cleanly inside breath-paced josei iyashikei manga linework — pure_manga is the obvious holding container for "the alarm is lying" anxiety transformation; any fantasy/painterly drift would dilute the contemplative-bearing signature into mood-piece prettiness. **Demographic fit:** stillness_press is the josei anxiety flagship per `canonical_brand_list.yaml`; pure_manga is the canonical genre vocabulary for josei iyashikei — exact match, no audience translation tax. **Sensory hook:** screentone for held-breath panels, soft ambient framing for forest-refuge, beat-pause panel grammar for the alarm-quiet realization in the RELEASE — all idiomatic to the form and embodied (lengthening exhale, drop of shoulders) rather than rhetorical. **Verdict: SIGN-OFF.**

### 2. joshin — `cognitive_clarity` / seinen / **pure_manga** / ja-JP / PILOT

`character_loras.joshin.notes`: "Japanese-American female, precise gaze, zen authority." Brand-style note: "High contrast monochrome with selective warmth." Audiobook anchor = `joshin_anxiety_ch1.txt`; spec §5 anchor problem = overthinking. **Voice fit:** the precise-gaze + zen-authority register is exactly what pure_manga seinen monochrome ink renders cleanest — overthinking-as-loop reads as repeating-thought-tile panels collapsing to one held frame; no other style on the matrix would carry that legibility better. **Demographic fit:** cognitive_clarity is the seinen overthinking flagship; high-contrast monochrome IS the canonical seinen visual grammar — the brand-style note and the demographic agree without translation. **Sensory hook:** thought-tile fragmentation in HOOK 0–6s, escalating loop-density in STRUGGLE, single-panel snap-to-stillness in RELEASE — embodied (gaze coming to rest) not rhetorical. Pilot designation reinforced: brand-2 manga assets and ja-JP TTS maturity make this the lowest-risk render for V1 pilot. **Verdict: SIGN-OFF.**

### 3. miki — `digital_ground` / manhwa / **pure_manga** / ja-JP

`character_loras.miki.notes`: "Japanese-American female, Gen Z bearing, digital native energy." Brand-style: "Digital-native flat aesthetic with rounded forms." Audiobook anchor = `miki_imposter_syndrome_ch1.txt`. **Voice fit:** Gen Z digital-native energy is *natively* manhwa/webtoon — a vertical-scrolling visual grammar holds the imposter-syndrome scrolling-feed-rot register more honestly than any landscape manga traditional layout would. **Demographic fit:** digital_ground is the manhwa burnout flagship; manhwa is operator-coded inside the spec's `pure_manga` style mode (§6 row 1 is "Genre-canonical manga linework + screentone, faithful to brand demographic" — and manhwa-flat is the genre-canonical answer for this brand's demographic). 9:16 short-form vertical is the manhwa-native aspect ratio, doubling the format-fit. **Sensory hook:** scroll-feed pile-up and notification-glow as the STRUGGLE visual grammar; phone-down + soft daylight as the RELEASE — embodied (eye softening off the screen) not rhetorical. **Verdict: SIGN-OFF.**

### 4. junko — `relational_calm` / josei / **pure_manga** / ja-JP

`character_loras.junko.notes`: "Japanese female, wabi-sabi simplicity, radical acceptance presence." Brand-style: "Wabi-sabi minimalism, maximum negative space." Audiobook anchor = `junko_overthinking_ch1.txt`; canonical primary = social_anxiety. **Voice fit:** wabi-sabi simplicity + radical-acceptance presence is a maximum-negative-space register — pure_manga josei iyashikei holds this with a single-figure / large-empty-panel grammar that any fantasy-overlay or painterly mode would clutter. **Demographic fit:** relational_calm is core josei iyashikei (canonical: `relational_calm_iyashikei`, demographic josei); pure_manga is the canonical visual vocabulary, and the brand-style note ("maximum negative space") tells you the brand has already chosen it for itself. **Sensory hook:** held interpersonal still-frame in HOOK, stiffening posture as relational tension lands in STRUGGLE, exhale-into-large-empty-panel as RELEASE — embodied. **Verdict: SIGN-OFF.**

### 5. omote — `body_memory` / josei / **pure_manga** / ja-JP

`character_loras.omote.notes`: "Japanese male, Noh-influenced bearing, grief held in body." Audiobook anchor = `omote_sleep_anxiety_ch1.txt`; canonical = `body_memory_shojo` (josei, somatic_healing primary). **Voice fit:** Noh-influenced bearing + grief-held-in-body is a body-as-instrument register; pure_manga shojo/josei somatic linework holds the embodied register without abstraction drift, exactly per the matrix rationale. Note: omote (the teacher / MC) is male while the brand demographic is josei — this is correctly a *teacher-MC vs brand-audience* distinction, not a mismatch. Spec §4 explicitly preserves teacher identity as MC across the brand's audience-targeted visual world; this row honors that boundary. **Demographic fit:** body_memory_shojo is canonical josei somatic-healing; pure_manga shojo linework is the demographic-faithful container. **Sensory hook:** body-pattern recoil micro-panel in HOOK, muscle-memory tightening in STRUGGLE, single body-line release (jaw unclench, hand-uncurl) in the RELEASE — embodied, not rhetorical. **Verdict: SIGN-OFF.**

### 6. master_wu — `warrior_calm` / shonen / **pure_manga** / zh-TW

`character_loras.master_wu.notes`: "Chinese male, martial composure, controlled power in stillness." Brand-style: "Dynamic martial ink with controlled stillness." Audiobook anchor = `master_wu_courage_ch1.txt`; canonical = `warrior_calm_cultivation` (shonen, primary burnout, secondary courage). **Voice fit:** martial composure + controlled-power-in-stillness IS the shonen cultivation visual grammar; pure_manga shonen ink (action lines pulled into a held-pose frame) is the only style on the matrix that carries this register without genre dissonance. **Demographic fit:** shonen-cultivation is the canonical demographic; the brand-style note and §5 demographic agree; pure_manga is the genre-faithful answer. **Sensory hook:** shonen ink-burst HOOK, escalating force in STRUGGLE, controlled-stillness final-pose RELEASE (shoulders down, gaze level) — embodied courage moment, not rhetorical. **Verdict: SIGN-OFF.**

### 7. master_feung — `qi_foundation` / seinen-cultivation (proposed) / **manga_fantasy_hybrid** / zh-CN

`character_loras.master_feung.notes`: "Chinese male, elder presence, qigong practitioner posture." Brand-style: "Traditional Chinese brushwork influence." Audiobook anchor = `master_feung_burnout_ch1.txt`. **Voice fit:** elder-presence + qigong-practitioner posture wants a register that can hold mountainscape, ink-wash mist, qi-flow brushwork — pure_manga's tighter linework would flatten the qi-flow signature; full painterly fantasy would lose the manga grammar that anchors it to the cohort. Manga_fantasy_hybrid is the right midpoint, which is precisely the matrix rationale ("ink-wash mist . . . without dropping linework grammar"). **Demographic fit:** qi_foundation IS present in `canonical_brand_list.yaml` as `qi_foundation_cultivation` (demographic = seinen, primary = somatic_healing). The matrix's "seinen_cultivation_proposed" therefore aligns with canonical demographic; the spec's §15 D1 ("qi_foundation NOT present in canonical_brand_list.yaml") is *partially incorrect* — the long id exists; the gap is that the short id `qi_foundation` (used in `brand_suffixes` and `brand_lora_plans.character_loras.master_feung.style_ref`) doesn't have an explicit alias entry. This is a **binding-naming reconciliation** for Pearl_Architect (already in flight per existing worktree `agent/qi-foundation-canonical-reconciliation-20260508`); it does NOT alter the style sign-off here, since the demographic is now confirmed seinen. **Sensory hook:** mountainscape opening, qi-flow brush trail tracking the breath through STRUGGLE, mist-clearing into open-mountain vista in RELEASE — embodied (the hands moving qi) not rhetorical. **Verdict: SIGN-OFF.** *(Informational note: D1 wording in spec §15 should be reconciled — long id exists; short-id alias is the actual gap.)*

### 8. master_sha — `sleep_restoration` / josei / **manga_fantasy_hybrid** / en-US

`character_loras.master_sha.notes`: "Chinese male, healing presence, luminous calm." Audiobook anchor = `master_sha_grief_ch1.txt`; canonical = `sleep_restoration_iyashikei` (josei, primary sleep, secondary grief). **Voice fit:** luminous-calm + healing-presence + grief on a sleep-iyashikei brand wants a dream-fold visual grammar that pure_manga linework can't quite carry without going dry, and that pure painterly_fantasy would over-warm into prettiness. Manga_fantasy_hybrid keeps iyashikei pacing and panel discipline while letting dream-symbolism breathe — the matrix rationale ("manga linework + dream-fantasy palette") matches. **Demographic fit:** sleep_restoration_iyashikei is canonical josei; iyashikei pacing under hybrid mode preserves the demographic register at the audience-target level. **Sensory hook:** sleep-state dream-fold HOOK, grief-figure surfacing in dream-light STRUGGLE, dawn-light return-to-body RELEASE (eyes opening, slow first inhale) — embodied. **Verdict: SIGN-OFF.**

### 9. ra — `solar_return` / shonen / **manga_fantasy_hybrid** / en-US

`character_loras.ra.notes`: "Ambiguous ethnicity, post-burnout rebirth energy, ember warmth." Audiobook anchor = `ra_self_worth_ch1.txt`; canonical = `solar_return_isekai` (shonen, primary self_worth, secondary courage). **Voice fit:** isekai is *literally manga + fantasy hybrid by genre definition*; ember-warmth + post-burnout-rebirth maps directly to isekai's portal/return imagery vocabulary. Pure_manga would pin the brand to a slice-of-life feel that contradicts the isekai genre tag; full painterly_fantasy would lose the shonen action-line momentum that drives the rebirth beat. Manga_fantasy_hybrid is the genre-correct answer, not an aesthetic preference. **Demographic fit:** solar_return_isekai is canonical shonen; manga_fantasy_hybrid is the canonical visual grammar for shonen isekai. **Sensory hook:** portal-cross HOOK, ember-trail through inter-dimensional STRUGGLE, solar-return self-worth ember-light RELEASE (chest opening to light) — embodied. **Verdict: SIGN-OFF.**

### 10. pamela_fellows — `somatic_wisdom` / josei / **cinematic_painterly_fantasy** / en-US

`character_loras.pamela_fellows.notes`: "Caucasian female, clinical warmth, somatic awareness posture." Brand-style: "Clean modern clinical warmth." Audiobook anchor = `pamela_fellows_burnout_ch1.txt`; canonical = `somatic_wisdom_shojo` (josei, primary somatic_healing). **Voice fit:** clinical-warmth + somatic-awareness register is *already* painterly-leaning by the brand-style note's own admission ("clean modern clinical warmth" is closer to illustrated-novel-cover than to manga ink); pure_manga would feel stylistically over-stylized and undercut the mass-clinical legibility the brand needs. Cinematic_painterly_fantasy is the register her voice naturally belongs to. **Demographic fit:** somatic_wisdom_shojo is canonical josei somatic-healing; the brand-style note explicitly tilts away from manga-stylized toward illustrated-cover legibility — cinematic_painterly_fantasy is the brand-faithful answer at the audience-target level (mass-clinical / wellness-adjacent reader). **Sensory hook:** warm brushwork tracking breath up the spine in HOOK, body-tension visible in shoulder/jaw painterly mass in STRUGGLE, shoulder-drop against gold light in RELEASE — embodied (literal somatic sensation), not rhetorical. **Verdict: SIGN-OFF.**

### 11. sai_ma — `devotion_path` / shonen / **cinematic_painterly_fantasy** / en-US

`character_loras.sai_ma.notes`: "Indian female, bhakti devotion radiance, flowing presence." Audiobook anchor = `sai_ma_grief_ch1.txt`; canonical = `devotion_path_shonen` (shonen, primary courage, secondary self_worth + grief). **Voice fit:** bhakti-devotion-radiance + flowing-presence is a brushwork-and-lamp-light register; manga linework — even shonen ink — would feel mechanically clean against a devotional grief beat. Cinematic_painterly_fantasy (illustrated-novel-cover, brushwork) is the register her voice belongs to. The matrix rationale ("Devotional grief register reads richer in classical-painterly mode") is right. **Demographic fit:** this is the closest call in the spread. `devotion_path_shonen` carries a shonen demographic tag, and the spread anchors painterly-fantasy in §6 to "warm, brushwork, mass-clinical legibility" — a register that doesn't typically default to shonen. The reconciliation: shonen on this brand is genre/courage-arc shonen (not action-shonen); the brand pairs `courage` (primary) + `grief` (secondary), and the audiobook anchor lands on grief — i.e. the actual narrative register the 30s carries is the *grief-into-courage-through-devotion* arc, which painterly-fantasy carries far more honestly than shonen ink. The shonen audience-target absorbs the painterly devotional reading provided the courage beat lands inside the RELEASE — that's renderable in painterly mode (palms-opening, light-restoring) without losing demographic faithfulness. So: not a flag, but the highest-tension fit on the matrix. **Pilot evidence note:** if the pilot reveals shonen-demographic resistance to painterly-devotional reading, V1.1 should re-test this row with pure_manga shonen as a backup pose; do NOT pre-flag now since the matrix rationale is sound and Q2 is approved. **Sensory hook:** brushwork unfurling cloth + lamp-light HOOK, grief-figure tightening into bhakti-still-pose STRUGGLE, opened-palms light-restoring RELEASE — embodied (palms, breath, gaze lifting) not rhetorical. **Verdict: SIGN-OFF.** *(Informational note: closest-call row on the matrix; flag for pilot-evidence revisit in V1.1, NOT for operator decision now.)*

### 12. maat — `heart_balance` / josei / **experimental** / en-US

`character_loras.maat.notes`: "Egyptian-coded female, regal bearing, shadow work intensity." Brand-style: "Bold geometric Egyptian-influenced motifs." Audiobook anchor = **MISSING** (`maat_*_ch1.txt` does not exist under `artifacts/audiobook_samples/_prose/`); D2 is open. Canonical = `heart_balance_shojo` (josei, primary social_anxiety). **Voice fit (style only):** regal-bearing + shadow-work-intensity + Egyptian-symbolic geometry is genuinely outside the manga-realism vocabulary; the brand-style note already declares its motif language to be non-manga ("bold geometric Egyptian-influenced"). The experimental slot — operator-swappable across motion-comic, webtoon-realism, 3D-illustrated, Egyptian-symbolic motion — is where this voice can render without compression. **Demographic fit:** heart_balance_shojo is canonical josei; experimental is the operator-designated swap-mode for the 12th row in §6 (range demonstration); audience-target absorption depends on which experimental sub-mode operator selects at render time, which the spec preserves as a downstream decision. **Sensory hook (style only):** glyph-fold and scale-of-the-heart imagery as the STRUGGLE visual grammar, shadow-into-light geometric motion as the RELEASE — embodied (hand on heart, spine straightening) not rhetorical. **Style assignment verdict: SIGN-OFF.** **D2 blocker (downstream):** without the audiobook prose anchor, Pearl_Localization cannot derive the 30s script, so the row is *render-blocked* regardless of style — but D2 is already operator-acknowledged in spec §15 and currently in flight in worktree `agent/maat-audiobook-ch1-prose-20260508`. D2 is NOT a flag against the style mode and does NOT need re-escalation through this review.

---

## Summary

| Row | Teacher | Style mode | Verdict |
|---|---|---|---|
| 1 | ahjan | pure_manga | SIGN-OFF |
| 2 | joshin (PILOT) | pure_manga | SIGN-OFF |
| 3 | miki | pure_manga | SIGN-OFF |
| 4 | junko | pure_manga | SIGN-OFF |
| 5 | omote | pure_manga | SIGN-OFF |
| 6 | master_wu | pure_manga | SIGN-OFF |
| 7 | master_feung | manga_fantasy_hybrid | SIGN-OFF (info note: D1 wording) |
| 8 | master_sha | manga_fantasy_hybrid | SIGN-OFF |
| 9 | ra | manga_fantasy_hybrid | SIGN-OFF |
| 10 | pamela_fellows | cinematic_painterly_fantasy | SIGN-OFF |
| 11 | sai_ma | cinematic_painterly_fantasy | SIGN-OFF (info note: closest call; pilot-evidence revisit in V1.1 if needed) |
| 12 | maat | experimental | SIGN-OFF on style; D2 blocker downstream (acknowledged) |

**Counts**

- SIGN-OFF: **12 / 12**
- FLAG-FOR-OPERATOR: **0 / 12**
- Distribution preserved: 6 pure_manga / 3 manga_fantasy_hybrid / 2 cinematic_painterly_fantasy / 1 experimental ✓
- Matrix TSV mutations made by this review: **0** (out-of-scope; no flag escalated)

## Informational notes (for the record, NOT operator escalations)

1. **D1 wording reconciliation (master_feung row).** `qi_foundation_cultivation` IS present in `config/manga/canonical_brand_list.yaml` (demographic = seinen, primary_topic = somatic_healing). Spec §15 D1 should be amended in a follow-up cap: the gap is the missing short-id alias `qi_foundation` (used in `brand_suffixes` and `character_loras.master_feung.style_ref`), not the absence of the brand from canonical. This strengthens — does not weaken — master_feung's SIGN-OFF, since the demographic is now confirmed seinen rather than "proposed." Reconciliation is already in flight in worktree `agent/qi-foundation-canonical-reconciliation-20260508`.
2. **sai_ma demographic-style tension (highest-tension row in the spread).** SIGN-OFF stands per matrix rationale and Q2 approval; recommend Pearl_Video record a comparison still in pure_manga shonen during pilot QA so V1.1 can re-test if the painterly-devotional reading resists the shonen audience target. NOT a flag now.
3. **D2 (maat audiobook prose anchor missing).** Render-blocking but acknowledged in spec §15 and in flight in worktree `agent/maat-audiobook-ch1-prose-20260508`. NOT a style-mode flag.
4. **Adi_da (row 13).** Out of V1 scope per Q1 default = defer; not reviewed here. If operator picks Q1=(a) include later, a one-row addendum to this review will be filed.

## Sign-off

The §6 STYLE SPREAD distribution and per-teacher assignments are **voice-coherent and brand-demographic-coherent for all 12 V1 deliverables**. No row requires REVISION. The matrix TSV is **not modified** by this review.

— Pearl_Editor, 2026-05-08

---

## Appendix A: Session notes (added 2026-05-08, post-review)

This appendix is operational-only — it does NOT change any sign-off above. It exists so future sessions inherit context about how this review was actually produced.

### A.1 Inputs not on local branch

The spec (`docs/specs/TEACHER_MANGA_30S_VIDEO_V1_SPEC.md`) and matrix (`artifacts/qa/teacher_manga_30s_locale_brand_matrix_2026-05-08.tsv`) were absent from the agent's starting local branch. Both are present in `origin/main` via PR #940 (merge commit `046a988e2a`, original commit `a33fe534eb`). They were extracted via `git show 046a988e2a:<path>` for the review pass. No changes to either file were made.

### A.2 Worktree topology used

A sparse-cone worktree was used at `/Users/ahjan/phoenix_omega_style_review_wt` (branch `agent/teacher-30s-style-review-20260508`) because a full checkout of the LFS-heavy 55k-file repo was killed by an environment watchdog at ~24% completion. Sparse cone: `scripts/{git,ci}`, `artifacts/{qa,coordination}`, `docs/specs`, `config/{manga,authoring,localization,video}`, `.github`. LFS smudge skipped via `GIT_LFS_SKIP_SMUDGE=1`. The committed diff was pre-verified to contain exactly one file before push.

### A.3 Cross-references

- **Session handoff (full debrief):** `docs/HANDOFF_PEARL_EDITOR_TEACHER_30S_STYLE_REVIEW_2026-05-08.md`
- **Environment-issues runbook (corrupt index, watchdog, sparse-checkout pitfall, health_check timeout):** `docs/SESSION_ENV_ISSUES_2026-05-08.md`
- **PR:** https://github.com/Ahjan108/phoenix_omega_v4.8/pull/953

### A.4 Open environment items (not blockers for this review)

- Main worktree (`/Users/ahjan/phoenix_omega`) has a corrupt index. Repair: `cd /Users/ahjan/phoenix_omega && rm .git/index && git reset`.
- `scripts/git/health_check.sh` stale-branch loop hangs on this repo state; recommend timeout patch.
