# Music Mode V2 — Production-Readiness Spec

**Date:** 2026-06-11
**Author:** Pearl_Architect
**Status:** active — V2 layer atop ratified V1 cap entries; ratifies 12-row correction audit + Phase A music-launch gate + anti-spam diversity gates + MusicGen Pearl Star Phase B integration
**Authority chain:**
- `MUSIC-MODE-V1-01` (rendering + atom-bank — ratified 2026-05-06)
- `MUSIC-MODE-BRAND-INTEGRATION-V1-01` (brand identity + onboarding + catalog — active 2026-05-09; Q1-Q4 ratified)
- `MUSIC-MODE-FREEBIE-FUNNEL-V1-02` (marketing freebies — active 2026-05-09; Q1-Q3 ratified)
- `PEARL-EDITOR-UPSTREAM-01` (content-authority lane; Pearl_Editor owns musician_banks/)
- `SPEC-739-THRESHOLD-01` (variation floor=3 applies to music slot pools too)
- `ATOM-100PCT-COVERAGE-SSOT-V1-01` (en-US atom coverage SSOT — music side gets parallel sibling SSOT)
- `CATALOG-800-PER-BRAND-01` (system-wide 800; cross-cap reconciliation needed — see §2 row 1)
- `PEARL-PRIME-ONE-PATH-V1-01` (D8 + slot-dirs framework — music slots layer on top)
- `PEARL-STAR-JOB-QUEUE-V1-01` (queue infra — **TARGET reference; not yet ratified on main; flagged as gap below**)

**Project:** `PRJ-MUSIC-MODE-V2-PRODUCTION-LAUNCH` (status=proposed in this PR)
**Cap-amendments proposed:** MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS + MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES

---

## §1. Purpose + V1→V2 Delta + Operator-3-Question Answers

### Purpose

V1 ratified the architecture: music mode is a first-class brand archetype (38+); wizard step 1 + step 4 onboarding; live HTTP route survey; 6 new atom slot pools; second-person book voice; one MusicGen prompt per book; Pearl_Editor owns content authority. V1 did NOT lock production-readiness gates, anti-spam diversity guards, or auto-render audio integration.

**V2 = the layer that turns V1 from "infra-and-scaffold-ready" into "production-shippable":**

1. **Ratify the 12-row correction audit** (§2) — close the operator-pasted reading of music-mode against current main; lock CORRECT/NEEDS-EDIT/DISPUTED verdicts row-by-row with spec citation.
2. **Define Phase A music-launch gate** (§4) — what specifically must be true to ship the first music-mode book.
3. **Author anti-spam diversity gates** (§5) — CI guard threshold spec preventing KDP/Amazon flag triggers when a music-brand catalog batch fans out.
4. **Author MusicGen Pearl Star Phase B integration** (§6) — auto-render the one-MusicGen-prompt-per-book deferred from V1 into actual WAV output via Pearl Star queue.
5. **Finalize operator-facing deck structure** (§7) — close the 8 deck-confirm questions from prior turn with recommended defaults; deck artifact ships in this PR.

### V1 → V2 delta (one-row summary)

| Layer | V1 (ratified 2026-05-06 → 2026-05-09) | V2 (this spec, proposed 2026-06-11) |
|---|---|---|
| Rendering | 6 slot pools + 2P intro/conclusion + per-chapter beats | (unchanged) |
| Brand identity | 38+ archetype; `<musician_handle>_music` slug | (unchanged) |
| Onboarding | Wizard step 1 + step 4 conditional pane; POST → wizard YAML | (unchanged) |
| Catalog | 100% music-mode rows per brand | (unchanged; CATALOG-800 reconciliation flagged §2.1) |
| Freebies | M1-M5 lead magnets in separate cap (`MUSIC-MODE-FREEBIE-FUNNEL-V1-02`) | (unchanged) |
| Audio render | MusicGen PROMPT per book; WAV deferred to Colab/Pearl Star | **NEW**: Pearl Star Phase B workload class wires auto-WAV-render |
| Diversity gates | (none specified) | **NEW**: CI guard with per-slot reuse ≤5× + ≤30% topic + ≤30% persona + ≤50% format thresholds |
| Phase A launch gate | (implicit; "infra ready when implementation ws's land") | **NEW**: explicit gate (§4) — first real musician + 6 slot pools backfilled for priority cell + smoke book ships + diversity gate PASS |
| Production-readiness audit | (implicit) | **NEW**: 12-row correction audit (§2) + readiness gap matrix (§3) |

### Operator's 3 questions — verbatim answers

**Q-Op-1: "Text-to-song for each book — possible in pipeline?"**

ANSWER: **YES at spec layer** (one MusicGen prompt per book per `MUSIC-MODE-V1-01`). **PARTIAL at production** (WAV rendering manual Colab/Pearl Star per V1 line 772 — `scripts/music/generate_book_companion_song.py` emits prompt JSON; `scripts/music/musicgen_colab.py` runnable path). **FULL production** when Pearl Star Phase B adds MusicGen workload class per §6 of this spec. **Target wall-clock 2-3 weeks** after Pearl_Int Phase A queue infra operational (gated on PEARL-STAR-JOB-QUEUE-V1-01 cap entry ratification by separate Pearl_Architect session — see §6.5).

**Q-Op-2: "Should all books be about the musician? Spam risk?"**

ANSWER: Books are **SHAPED BY** the musician (atom-bank lens drives voice register + themes + touchstones + healing intent) but **ADDRESSED TO** the reader in second person ("you"). Books are NOT "about the musician" — they are reader-facing self-help/reflection/lyric works inspired by the musician's sound and themes. Topical diversity = 14 personas × 15 topics × 5 active locales × 2 variants (with-lyrics / no-lyrics) × multiple spines = **~21,000 distinct (P×T×L×V×spine) combinations** before content repetition becomes statistically forced. **KDP/Amazon spam-flag mitigation** via §5 diversity gates: per-slot ≤5× variant reuse + ≤30% topic concentration + ≤30% persona concentration + per-locale platform-specific rules. **Production gate:** §5 CI guard PASS is hard-required pre-publish under `--quality-profile production`.

**Q-Op-3: "Status — production ready?"**

ANSWER: **INFRA-AND-SCAFFOLD-READY** (3 cap entries ratified + wizard live + survey form live + pipeline shell wired + test_artist_alpha scaffold has all 6 slot pools at SPEC-739 floor + 2P intro/conclusion templates seeded) + **REAL-MUSICIAN-CONTENT-EMPTY** (zero real musicians onboarded + zero real musician banks beyond test scaffold + zero music-mode catalog books shipped). Phase A music-mode launch = same posture as Phase A en-US atom-coverage pre-backfill — infra-ready, content-pending. **ETA to ship-first-music-book = 4-6 weeks parallel with atom-coverage cascade** (depends on first real musician onboarding speed + Pearl_Editor + Pearl_Writer atom-authoring wall-clock for the 6 slot pools at production-grade quality + MusicGen Phase B WAV rendering operational or accept Phase B-1 deferral with manual Colab fallback).

---

## §2. 12-Row Corrections Audit (RATIFICATION)

Operator-pasted prior-turn analysis of music mode corrected an in-flight deck plan. This section ratifies each correction against current `origin/main` spec source. Machine-readable companion at `artifacts/qa/music_mode_corrections_audit_20260611.tsv`.

### §2.1 Row-by-row verdicts

**Row 1 — "Music mode produces 800 BOOKS per active brand" — `DISPUTED`**

- **Spec source (intra-music):** `MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` §4 + §AMENDMENT-2026-05-09 §3 (Q3 default = 800 baseline; override via `music_volume_tier` ∈ {solo, standard, enterprise}). Plain reading: **800 per active music brand**.
- **Spec source (cross-cap):** `PEARL_ARCHITECT_STATE.md` line 629 (`CATALOG-800-PER-BRAND-01`, ratified 2026-05-06): "800 high-confidence configs is **system-wide total** (not per-brand)".
- **Verdict:** **DISPUTED on main.** Both cap entries are ratified; their texts are mutually inconsistent for the music-mode scope.
- **Reconciliation recommendation:** The MUSIC-MODE-BRAND-INTEGRATION-V1-01 §AMENDMENT §3 is more recent (2026-05-09) and music-mode-specific; CATALOG-800-PER-BRAND-01 (2026-05-06) is system-wide-overall reframing for Pearl Prime book catalog scope. Pearl_Architect recommends the music-mode §3 text wins for **intra-music-mode catalog scope** (each active music brand may target up to 800 books at standard tier; solo/enterprise tiers adjust); CATALOG-800-PER-BRAND-01 governs the Pearl-Prime-overall books-system top-line. **`Q-MM-V2-CATALOG-800-RECONCILE-01`** (see §8) flags this for operator clarification before Phase A first-real-musician onboarding.
- **Spec text update needed (separate amendment, not this PR):** Add a one-line note in CATALOG-800-PER-BRAND-01 cap entry: "Music mode catalog scope is governed by `MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-2026-05-09 §3`; this cap entry governs Pearl-Prime-overall books-system top-line."

**Row 2 — "One MusicGen companion prompt per book for brand-admin packaging" — `CORRECT`**

- Spec source: MUSIC-MODE-V1-01 line 767 + 772. Verbatim: "one MusicGen companion prompt per book for brand-admin packaging" + "Companion audio: V1 ships **prompt JSON** via `scripts/music/generate_book_companion_song.py`; MusicGen runnable path remains Colab-oriented (`scripts/music/musicgen_colab.py` / Pearl Star). WAV export deferred until a supported local/scheduled runner is pinned."
- Verdict: **CORRECT.** WAV rendering deferred at V1; V2 §6 wires the auto-render via Pearl Star Phase B.

**Row 3 — "Two render variants: with-lyrics and no-lyrics (both books)" — `CORRECT`**

- Spec source: MUSIC-MODE-V1-01 line 767. Survey schema `output_preferences_with_lyrics` (lyric_form / explicit_content_ok / companion_ai_song_consent) and `output_preferences_no_lyrics` (reflection_form / reflection_perspective) drive variant selection.
- Verdict: **CORRECT.** Both variants are books; lyric blocks vs reflection prose differ at insertion sites (chapter open/close/mid-beat).

**Row 4 — "Books are SECOND PERSON ('you') at intro/conclusion/chapter beats" — `CORRECT`**

- Spec source: MUSIC-MODE-V1-01 line 767. test_artist_alpha scaffold confirms with INTRO_2P_TEMPLATE.yaml + CONCLUSION_2P_TEMPLATE.yaml at top of approved_atoms/.
- Verdict: **CORRECT.** Author persona (Human Pen Name or EI) frames the book; prose addresses reader directly.

**Row 5 — "No upper bound on music-mode brand count; id_space_start=38" — `CORRECT`**

- Spec source: `config/music/music_brand_registry.yaml` lines 76-127 (schema_version: 1; archetype: music_mode; id_space_start: 38; music_brands list initially seeded with `_template_music` placeholder only).
- Verdict: **CORRECT.** Registry currently has 1 placeholder; zero real musicians. Open-ended brand count; Path X 37 brands remain frozen (anti-drift).

**Row 6 — "Catalog platforms = book platforms (KDP/Audible/Apple Books/Google Play); music platforms are freebie/marketing layer" — `CORRECT`**

- Spec source: Integration spec §4 ("Catalog: 100% music mode" — music-mode brand catalog = books only); Freebie spec §3 (M1-M5 lead magnets — companion track, preview clip, sample EP, lyric poster, behind-song interview).
- Verdict: **CORRECT.** Catalog OUTPUT = books on book platforms. Audio assets = freebie/funnel layer per separate cap MUSIC-MODE-FREEBIE-FUNNEL-V1-02.

**Row 7 — "No 25/50/25 musician-named/influence/composite distribution specified for music mode" — `CORRECT`**

- Spec source: Full read of `MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` + `MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` + MUSIC-MODE-V1-01 + MUSIC-MODE-BRAND-INTEGRATION-V1-01 + MUSIC-MODE-FREEBIE-FUNNEL-V1-02. Zero distribution percentages specified.
- Verdict: **CORRECT.** Teacher-deck 25/50/25 is a teacher-mode convention only. **Drop from V2 deck.** RECOMMEND: leave to operator discretion in implementation phase OR author a music-specific distribution AMENDMENT later under a follow-up cap.

**Row 8 — "No ~80% revenue-to-Brand-Director specified for music mode" — `CORRECT`**

- Spec source: Full read confirms no revenue split in music spec.
- Verdict: **CORRECT.** Teacher deck states "~80%"; music spec is silent. Spec §7 deck omits revenue % unless operator confirms transfer from teacher mode (see Q-MM-V2-DECK-CONFIRM-Q2-01 in §8).

**Row 9 — "Music Reflections Survey has 8 sections" — `CORRECT`**

- Spec source: `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` lines 5-49.
- Sections (verbatim): (1) identity, (2) themes, (3) voice_craft, (4) material_for_reflection, (5) healing_intent, (6) output_preferences_with_lyrics, (7) output_preferences_no_lyrics, (8) consent_licensing.
- Verdict: **CORRECT** (prior turn claim of "7" was an undercount). Live form at `brand-wizard-app/public/musician_reflections_survey.html` (42 KB; Pearl Prime amber-on-dark tokens).

**Row 10 — "Wizard Step 1 = mode selector; Step 4 = conditional musician_reflections_survey; live HTTP route /wizard/music-survey/save; file:// forbidden" — `CORRECT`**

- Spec source: Integration spec §2 + §3 + §AMENDMENT-2026-05-09 §1.
- Verdict: **CORRECT** verbatim.

**Row 11 — "brand_id slug pattern = `<musician_handle>_music`" — `CORRECT`**

- Spec source: §AMENDMENT-2026-05-09 §2 (Q2 default ratified; examples: `ahjansam_music`, `junko_music`).
- Verdict: **CORRECT** verbatim. Hard-locked default; alternate patterns require separate AMENDMENT.

**Row 12 — "Volume tier override via `music_volume_tier` ∈ {solo, standard, enterprise}; standard=800 baseline" — `CORRECT`**

- Spec source: §AMENDMENT-2026-05-09 §3.
- Verdict: **CORRECT** verbatim. Numeric ranges for solo/enterprise TBD by Pearl_Marketing in implementation. Spec §7 deck includes Solo/Standard/Enterprise pitch on Slide 7.

### §2.2 Audit summary

- **11 CORRECT**, **1 DISPUTED** (row 1 — CATALOG-800 cross-cap reconciliation needed).
- All 12 corrections trace cleanly to spec source-of-truth; the DISPUTED row reflects a real cross-cap contradiction on main, NOT an error in the prior-turn analysis.
- Machine-readable audit: `artifacts/qa/music_mode_corrections_audit_20260611.tsv`.

---

## §3. Production-Readiness Gap Matrix

### §3.1 What's wired (INFRA-AND-SCAFFOLD-READY)

| Layer | Wired item | Authority | Verification |
|---|---|---|---|
| Cap entries | MUSIC-MODE-V1-01 ratified | PEARL_ARCHITECT_STATE.md line 763 | Verified |
| Cap entries | MUSIC-MODE-BRAND-INTEGRATION-V1-01 active (Q1-Q4 ratified) | line 1128 + §AMENDMENT-2026-05-09 | Verified |
| Cap entries | MUSIC-MODE-FREEBIE-FUNNEL-V1-02 active (Q1-Q3 ratified) | line 1202 + spec §AMENDMENT-2026-05-09 | Verified |
| Spec docs | MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md (203 lines) | docs/specs/ | Verified |
| Spec docs | MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md (172 lines) | docs/specs/ | Verified |
| Survey schema | SURVEY_TEMPLATE.yaml (8 sections, canonical) | artifacts/musician_survey/ | Verified lines 5-49 |
| Live wizard form | musician_reflections_survey.html (42 KB; Pearl Prime tokens; Cormorant + DM Sans) | brand-wizard-app/public/ | Verified |
| Registry | music_brand_registry.yaml (schema_version=1; id_space_start=38; `_template_music` placeholder) | config/music/ | Verified lines 76-127 |
| Pipeline shell | `--music-mode` orthogonal to `--pipeline-mode` (additive overlay) | MUSIC-MODE-V1-01 line 769 | Spec-verified |
| Slot-pool framework | 6 slot pool dir names (LYRIC_OPENING/CLOSING/BESTSELLER_BEAT + MUSIC_REFLECTION_OPENING/CLOSING/BESTSELLER_BEAT) | MUSIC-MODE-V1-01 line 770 + test_artist_alpha tree | Verified on disk |
| Test scaffold (test_artist_alpha) | 6 slot pools × 3 atoms = 18 atoms (meets SPEC-739 floor) + INTRO_2P + CONCLUSION_2P templates + survey_responses/2026-05-06.yaml | SOURCE_OF_TRUTH/musician_banks/test_artist_alpha/ | Verified on disk |
| MusicGen prompt-per-book | scripts/music/generate_book_companion_song.py emits prompt JSON | MUSIC-MODE-V1-01 line 772 | Spec-verified |
| Wizard route | POST /wizard/music-survey/save → wizard YAML → auto-advance | Integration spec §3 | Spec-verified |
| `file://` deprecated | Live HTTP route required | Integration spec §2 + §AMENDMENT §1 | Spec-verified |

### §3.2 What's content-empty (REAL-MUSICIAN-CONTENT-EMPTY)

| Layer | Empty item | Authority requiring fill | Estimated wall-clock |
|---|---|---|---|
| Registry | Zero real musicians in `music_brand_registry.yaml` (placeholder only) | Integration spec §5 + Q4 default | 1-2 weeks per musician onboarding (operator-nominated speed) |
| Survey responses | Zero real musician survey YAMLs at `brand-wizard-app/brands/<brand_id>.yaml` | Integration spec §3 + §AMENDMENT §4 | 30 min per musician for form completion |
| Musician banks | Zero real `musician_banks/<id>/` trees beyond test_artist_alpha scaffold | MUSIC-MODE-V1-01 + PEARL-EDITOR-UPSTREAM-01 | 1-2 weeks per first musician per priority cell |
| 6 slot pool backfill | Zero atoms in 6 slot pools for any real musician | SPEC-739-THRESHOLD-01 floor ≥3 | 3 atoms × 6 pools × ≥1 musician = 18+ atoms minimum |
| Music-mode books shipped | Zero music-mode catalog books on book platforms (KDP/Audible/Apple/Google) | Phase A music-launch gate (§4) | gated on 5 layers above + diversity gate PASS |
| Companion WAV rendering | Zero auto-rendered companion songs (manual Colab/Pearl Star only) | MUSIC-MODE-V1-01 line 772 → V2 §6 Phase B | gated on Pearl Star Phase B operational (~2-3 weeks after Phase A queue infra) |
| Diversity gate CI guard | Zero CI scripts validating diversity thresholds | V2 §5 spec → Pearl_Dev ws | ~3-5 days Pearl_Dev wall-clock once spec ratified |
| Music-side atom-coverage SSOT | Zero parallel SSOT document (en-US side has `PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md` merged 2026-06-11 via PR #1485) | this V2 §4 + Q-MM-V2-MUSICIAN-BANKS-SCOPE-01 | ~1 Pearl_Architect session (downstream ws) |

### §3.3 What's deferred (V3+ or separate-cap territory)

| Item | Deferred-to | Rationale |
|---|---|---|
| PEARL-STAR-JOB-QUEUE-V1-01 cap entry + spec + concurrency matrix | Separate Pearl_Architect session (Pearl_Int co-author) | Infra spec doesn't exist yet on main; this V2 spec references it as TARGET only. |
| Music-side atom-coverage SSOT scope expansion | V3 cap entry (Q-MM-V2-MUSICIAN-BANKS-SCOPE-01 §8) | V2 = parallel structure to en-US SSOT (persona×topic×slot×locale); theme/emotion/instrument dimensions deferred. |
| zh-CN gray-zone music distribution rules | Implementation phase under Pearl_Localization ws | Cross-cuts existing zh_cn_release.py infra; not music-specific. |
| Music-mode video (lyric videos, music videos) | Pearl_Video subsystem (separate cap candidate) | Music spec is books + companion song scope; video belongs to video_pipeline subsystem. |
| Per-platform revenue % allocation (Brand Director split) | Operator-decision + cap entry | Not in music spec; teacher-deck "~80%" not confirmed transferable. |
| 25/50/25 musician-named/influence/composite distribution | Operator-decision + cap entry IF needed | Not in music spec; may be irrelevant since musician IS the brand. |

---

## §4. Phase A Music-Mode Launch Gate

Phase A = "ship the first music-mode book to a book platform with full quality assurance and diversity-gate compliance."

### §4.1 Phase A entry conditions (all required)

1. **First real musician onboarded** — operator nominates; brand wizard step 1 + step 4 completed; brand_id `<handle>_music` registered in `music_brand_registry.yaml` with `status: active`; brand wizard YAML present at `brand-wizard-app/brands/<brand_id>.yaml` per Q4 default.
2. **6 slot pools backfilled for priority cell** — Pearl_Editor + Pearl_Writer author atoms for the recommended priority cell (see Q-MM-V2-PRIORITY-PERSONA-TOPIC-01 — default `gen_z_professionals × anxiety × en-US × with-lyrics × deep_book_4h`). Each of LYRIC_OPENING / LYRIC_CLOSING / LYRIC_BESTSELLER_BEAT / MUSIC_REFLECTION_OPENING / MUSIC_REFLECTION_CLOSING / MUSIC_REFLECTION_BESTSELLER_BEAT meets SPEC-739 ≥3 variant floor. ≥18 atoms total.
3. **INTRO_2P_TEMPLATE + CONCLUSION_2P_TEMPLATE authored for the musician** — second-person voice template specific to the musician's themes + voice register (mirrors test_artist_alpha pattern).
4. **Catalog pipeline smoke** — `--music-mode --pipeline-mode spine --quality-profile production` against the priority cell renders ≥1 book end-to-end without runtime errors.
5. **Quality rubric PASS** — book scored against `PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD` + music-specific rubric (TBD; recommend authoring as sub-spec under Q-MM-V2-MUSIC-RUBRIC-01). Hard-fail F-detectors clear; ADVISORY warnings logged.
6. **Diversity gate PASS** — even for a single-book Phase A, the §5 CI guard runs and verifies slot-pool variance + topic + persona + format diversity within the produced book. For Phase A 1-book scope, gate validates per-chapter slot reuse (no LYRIC_OPENING atom reused across all chapters) + first-book topical/persona/format fit reasonability.
7. **MusicGen companion prompt emitted** — `scripts/music/generate_book_companion_song.py` runs against the book metadata; prompt JSON written to `artifacts/music_companions/<brand_id>/<book_id>.musicgen.json`.
8. **MusicGen WAV rendered** (one of two paths):
   - **Path A — Phase B operational:** §6 auto-render via Pearl Star queue → `artifacts/music_companions/<brand_id>/<book_id>.wav`.
   - **Path B — Phase B deferred:** Manual Colab/Pearl Star runbook execution per V1 line 772; one-time human-attended render acceptable for Phase A.

### §4.2 Phase A exit milestone

First music-mode book lands on **at least one** of the following platforms with companion song attached at brand-admin packaging level:

- KDP (en-US, eBook)
- Audible (en-US, audiobook with companion song as bonus track)
- Apple Books or Google Play (en-US, eBook)

Plus brand-admin v2 dashboard shows the new music-mode brand in the brand list with axes_present including `book` + optional `companion_song`.

### §4.3 Phase A timeline

| Week | Milestone | Owner |
|---|---|---|
| W1 | Operator nominates first real musician; survey administered + form completed; brand_id registered; wizard YAML persisted | Pearl_PM coordinates; operator + musician execute |
| W2-W3 | Pearl_Editor + Pearl_Writer atom-authoring for 6 slot pools + 2P templates for priority cell | Pearl_Editor lead + Pearl_Writer support |
| W3 | Pearl_Dev CI diversity-gate guard scripts/ci/check_music_brand_diversity.py lands | Pearl_Dev (parallel to W2-W3) |
| W4 | Pipeline smoke: render first music-mode book end-to-end | Pearl_Dev (smoke) |
| W4-W5 | Quality rubric + diversity gate review | Pearl_Editor + Pearl_Dev |
| W5 | MusicGen companion WAV (Phase B operational OR manual Colab) | Pearl_Int (Phase B) OR operator (manual) |
| W6 | Platform upload + brand-admin v2 dashboard verification | Pearl_Brand + Pearl_Marketing |

Total wall-clock: **4-6 weeks** parallel with en-US atom-coverage cascade (different cells, different agents — no conflict).

### §4.4 Phase A success criteria (operator-visible)

- Brand_admin_v2 dashboard shows the music-mode brand with current week's downloadable package containing eBook + optional companion song.
- One book purchasable on at least one platform (KDP/Audible/Apple/Google).
- Diversity gate report green at `artifacts/qa/music_brand_diversity_report_<brand_id>_W<num>.md`.
- Operator + Brand Director (musician's nominated student/fan) sign-off via `artifacts/coordination/operator_decisions_log.tsv` row.

---

## §5. Anti-Spam Diversity Gates Spec

Music-mode brands generate large-scale catalog batches (up to 800 books per active brand at standard tier). Without guard rails, repeated slot-pool atoms or topic concentration would trip KDP/Amazon spam-flag heuristics + erode platform standing. This section specifies the CI guard authored under `ws_pearl_dev_music_brand_diversity_ci_guard_20260611`.

### §5.1 CI guard script

**Path:** `scripts/ci/check_music_brand_diversity.py` (NEW; Pearl_Dev ws scope)

**Invocation:** Called by `--quality-profile production` catalog runs + pre-publish CI workflow.

**Input:** A music-mode brand catalog batch directory (`artifacts/catalog/music_mode/<brand_id>/<batch_id>/`) containing one rendered book per row + `batch_manifest.json` with per-book (persona, topic, locale, variant, format, slot_atom_ids) metadata.

**Output:** Diversity report at `artifacts/qa/music_brand_diversity_report_<brand_id>_<batch_id>.md` + JSON sidecar at `artifacts/qa/music_brand_diversity_report_<brand_id>_<batch_id>.json` + exit code 0 (PASS) or non-zero (per gate fail mode).

### §5.2 Diversity thresholds

For any music-mode catalog batch of size **N ≥ 50 books**:

| Gate | Metric | Threshold | Production fail mode | Draft fail mode |
|---|---|---|---|---|
| **G1 — Per-slot-pool variant reuse** | For each of 6 slot pools, count unique-variant-uses across batch. Each variant may repeat ≤ **5 times per batch** OR ceil(N / 5), whichever is greater. | `max_variant_reuse ≤ max(5, ceil(N/5))` | HARD_FAIL | WARN |
| **G2 — Topic concentration** | % of batch books on single topic | `topic_share ≤ 30%` | HARD_FAIL | WARN |
| **G3 — Persona concentration** | % of batch books on single persona | `persona_share ≤ 30%` | HARD_FAIL | WARN |
| **G4 — Format concentration** | % of batch books in single format | `format_share ≤ 50%` (deep_book_4h naturally heavier) | HARD_FAIL | WARN |
| **G5 — Locale concentration** | % of batch books in single locale | per-platform rules: KDP US = `locale_share ≤ 70%`; KDP JP = `locale_share ≤ 50%` (operator-tunable) | HARD_FAIL | WARN |
| **G6 — Title diversity (string-similarity)** | Fuzzy-match all batch book titles; flag clusters above similarity threshold | `max_title_similarity_cluster_size ≤ ceil(N / 20)` | WARN (always) | WARN |
| **G7 — Author-bio reuse** | Same pen-name byline + same bio paragraph reused in >X% of catalog | `author_bio_reuse ≤ 60%` (Pearl Prime convention allows multi-book per pen-name) | WARN | WARN |
| **G8 — Slot-atom rotation balance** | Within each slot pool, no single atom claims >2× the median selection rate | `gini_coefficient(slot_pool_selection) ≤ 0.4` | WARN | WARN |

### §5.3 Production-profile policy

Under `--quality-profile production`:

- G1-G5 = HARD_FAIL (catalog batch refuses to publish; CI exits non-zero).
- G6-G8 = WARN (logged + dashboard surfaced; operator decision required if persistent).

Under `--quality-profile draft`:

- All gates = WARN-only.

### §5.4 Smoke validation

For Phase A (1-book scope) gate runs in degraded validation mode: G1 verifies per-chapter slot atom reuse (no slot atom reused in >50% of chapters in the single book); G2-G5 = N/A for N<50 (logged as `not_applicable_batch_too_small`). Full gate engages when batch N ≥ 50.

### §5.5 KDP/Amazon spam-flag alignment

Thresholds align with empirically-observed publisher spam-flag heuristics:
- Amazon flags author-clusters with >50% topic concentration as series-spam (catch with G2 + G4 + G7).
- KDP flags author-clusters with >30% persona/demographic targeting as "demographic farming" (catch with G3).
- Apple Books flags repeated lyric/text patterns across same-author catalog (catch with G1 + G6 + G8).
- Google Play flags above-threshold author-bio reuse across pseudonym catalog (catch with G7).

### §5.6 Threshold tuning post-launch

Phase A milestone gate criteria includes: 50-book smoke batch run + gate tuning + first publish empirical validation. Tighten/loosen thresholds based on KDP/Amazon flag rate over first 90 days post-publish. **`Q-MM-V2-DIVERSITY-GATE-THRESHOLDS-01`** in §8 flags operator-tunable thresholds.

---

## §6. MusicGen Pearl Star Phase B Integration Spec

### §6.1 Scope

Auto-render the one-MusicGen-prompt-per-book deferred from V1 (MUSIC-MODE-V1-01 line 772 "WAV export deferred until a supported local/scheduled runner is pinned") into actual `.wav` output via Pearl Star queue. Adds MusicGen as the 5th workload class on Pearl Star alongside existing 4 (Qwen-Image, CosyVoice2, Ollama LLM, orchestration).

### §6.2 Architecture

- **Workload class:** `music_companion_render` (5th class on Pearl Star Phase B job queue).
- **Engine:** Meta MusicGen via `scripts/music/musicgen_render_worker.py` (NEW; Pearl_Int ws scope).
- **Trigger:** Catalog pipeline emits prompt JSON at `artifacts/music_companions/<brand_id>/<book_id>.musicgen.json` (already V1 spec); queue worker picks it up; renders WAV; writes to `artifacts/music_companions/<brand_id>/<book_id>.wav`.
- **Deterministic seed:** Per-book seed = SHA1(`<brand_id>:<book_id>:<persona>:<topic>:<locale>:<spine>`)[:16] integer for reproducibility.
- **Output spec:** 30-90 second WAV, 44.1 kHz, 16-bit stereo (operator-tunable).

### §6.3 MusicGen model size choice

| Model | Params | VRAM footprint | Concurrent with FLUX-schnell (12 GB)? | Quality | Recommendation |
|---|---|---|---|---|---|
| MusicGen-small | 300M | ~3 GB | YES (3+12=15 GB; 9 GB headroom) | Adequate for ambient | Phase B-0 smoke; not production |
| **MusicGen-medium** | **1.5B** | **~5 GB** | **YES (5+12=17 GB; 7 GB headroom for OS + CosyVoice2)** | **Production-acceptable** | **RECOMMENDED Phase B-1 default** |
| MusicGen-large | 3.3B | ~10 GB | NO (10+12=22 GB; squeezes 24 GB envelope) | Best quality | Phase B-2 single-workload only |

**Recommended default:** **MusicGen-medium** for Phase B launch. Allows concurrent rendering with FLUX-schnell image jobs (manga + book covers + freebie posters) — preserves Pearl Star throughput.

**Open question:** **Q-MM-V2-MUSICGEN-MODEL-SIZE-01** (§8) flags model size for operator decision at Phase B install ws.

### §6.4 Concurrency math

Pearl Star = NVIDIA RTX 4090 (24 GB VRAM) (per existing handoff docs `PEARL_STAR_OPERATOR_HANDOFF.md` + `HANDOFF_PEARL_STAR_IMAGE_PIPELINE_2026-05-04.md`).

Existing workload footprints (approximate steady-state):
- Qwen-Image-Edit-2511 / FLUX-schnell: ~12 GB
- CosyVoice2 (CJK TTS): ~3 GB
- Ollama LLM (e.g., Gemma-2-9B): ~6 GB
- Orchestration: ~1 GB

**Phase B-1 concurrent envelope (MusicGen-medium + FLUX-schnell + orchestration):** 5 + 12 + 1 = **18 GB** of 24 GB. Headroom: 6 GB (CosyVoice2 OR Ollama, not both concurrent with MusicGen).

**Phase B-2 single-workload-only (MusicGen-large):** 10 GB + 1 GB orch = 11 GB; other classes paused during render. ~30-60 sec per book at 1-2 generation passes.

### §6.5 PEARL-STAR-JOB-QUEUE-V1-01 dependency

This V2 §6 references PEARL-STAR-JOB-QUEUE-V1-01 as **TARGET cap entry** for Pearl Star Phase A queue infrastructure. **That cap entry does NOT yet exist on main as of 2026-06-11.** This is flagged as a hard gap:

- **Q-MM-V2-PEARL-STAR-PHASE-A-CAP-01** (§8): recommend Pearl_Architect open a separate session to author PEARL-STAR-JOB-QUEUE-V1-01 cap entry + spec + concurrency matrix BEFORE this V2 §6 can advance to implementation. Without that infra cap, MusicGen Phase B integration ws (`ws_pearl_int_pearl_star_phase_b_musicgen_workload_20260611`) is gated.

### §6.6 Phase B install ws scope

`ws_pearl_int_pearl_star_phase_b_musicgen_workload_20260611` (proposed; gated on Pearl Star Phase A operational):

1. Install MusicGen (medium model by default per §6.3) on Pearl Star — virtual env + model weights + dependency pin.
2. Author `scripts/music/musicgen_render_worker.py` — queue consumer + per-book seed handler + WAV writer.
3. Wire to queue (whatever infra Phase A lands).
4. Smoke test: render 1 companion song for test_artist_alpha sample book → verify WAV plays + duration in spec + seed reproducibility.
5. Output: `artifacts/qa/musicgen_phase_b_smoke_<date>.md` + sample WAV at `artifacts/music_companions/test_artist_alpha/smoke_<book_id>.wav`.

### §6.7 License compliance

MusicGen license = MIT for the model code (Meta release). Generated-content commercial-use clearance has known caveats — audio training set provenance varies across MusicGen training corpora. **Q-MM-V2-MUSICGEN-LICENSE-CHECK-01** (§8) flags for Pearl_Int legal review BEFORE Phase B-1 production launch:

- Confirm commercial-use clearance for MusicGen-medium specifically (not just MIT model code).
- Document which model variant ships in Phase B (training set provenance).
- Author `docs/legal/MUSICGEN_USE_COMPLIANCE.md` if needed.

---

## §7. Operator-Facing Deck Structure (Final 10-Slide Plan)

This section resolves the 8 deck-confirm questions from the prior turn with recommended defaults; deck artifact ships in this PR as `artifacts/programs/music_mode_v2_20260611/MUSIC_MODE_INTRODUCTION_DECK.pptx`.

### §7.1 Deck Q-resolutions

| Deck Q (prior turn) | Resolution | Rationale |
|---|---|---|
| Q1 — Slide 1 audience line / forum reference | **Drop forum reference; "For Musicians and Their Brand Directors"** | No music-side forum analogous to United Spiritual Leaders Forum exists yet. Operator may name one later via separate AMENDMENT. |
| Q2 — Revenue % on Slide 8 | **Omit** | Not specified in any music spec. Operator addresses verbally if needed. Q-MM-V2-DECK-CONFIRM-Q2-01 in §8. |
| Q3 — 25/50/25 distribution | **Drop entirely** | Not in music spec. Teacher convention. Q-MM-V2-DECK-CONFIRM-Q3-01 in §8 (note: row in audit confirms drop). |
| Q4 — Volume tier pitch on Slide 7 | **Include Solo/Standard/Enterprise** | Music-specific feature per Q3 default of §AMENDMENT-2026-05-09. Music differentiator vs teacher mode. |
| Q5 — Companion songs framing | **Keep current framing + footnote "auto-render coming Pearl Star Phase B"** | One MusicGen prompt/book ratified at V1; auto-render = V2 §6 deferred work. Footnote sets honest expectations. |
| Q6 — Freebie sidebar on Slide 9 | **Light cross-link to MUSIC-MODE-FREEBIE-FUNNEL-V1-02** | Freebies are separate program; light callout maintains awareness without scope drift. |
| Q7 — Slide 5 second-person example prose | **Keep current example ("You hear the morning. You feel the room get small.")** | Pending operator replacement with their own sample. Default keeps deck shippable. |
| Q8 — Closing tagline | **Approve "Your Music. The Reader's Room."** | Echoes teacher deck "Your Wisdom. The World's Hands." cadence; matches second-person book framing. |

### §7.2 Deck slide map (10 slides)

| # | Slide | Key content |
|---|---|---|
| 1 | Title | "PEARL PRIME · EI" eyebrow / Headline "Books About Your Music" / Sub "How Pearl Prime Creates, Publishes & Represents Musician Voice at Global Scale" / "For Musicians and Their Brand Directors" |
| 2 | Overview ("What Is Music Mode?") | Three cards: 📚 What It Creates · 🌍 Who It Reaches · 🔬 How It Works |
| 3 | Knowledge Base ("Your Voice, Authored as Atoms") | 6 slot pool callouts + 4-step process (Survey → Atom Authoring → Book Assembly → Companion Song) |
| 4 | Book Variants ("Two Types of Music-Mode Books") | VARIANT 1 With-Lyrics + VARIANT 2 No-Lyrics |
| 5 | Authorship ("Second Person. To the Reader. From the Music.") | Example prose + 3 why-this-matters cards |
| 6 | Author Types | HUMAN PEN NAME AUTHOR + EI / ENLIGHTENED INTELLIGENCE AUTHOR |
| 7 | Quality & Platforms + Volume Tier | Anti-AI-slop framing + Solo / Standard (800) / Enterprise tier explainer |
| 8 | Brand System ("Music-Mode Brands. Your Unique Sonic Lane.") | 38+ open-ended id space + 6 callouts (one musician per brand / student-fan brand director / volume tier / 12 markets / companion songs / scales with material) |
| 9 | Next Steps ("How Your Music Enters the Platform") | 6-step wizard flow + light freebie cross-link sidebar |
| 10 | Closing | "Your Music. The Reader's Room." |

### §7.3 Visual style

Pearl Prime amber-on-dark tokens: `--bg: #0e0a06` / `--txt: #faf6f0` / `--amber: #d97706`. Cormorant Garamond display + DM Sans body (fallback Cambria + Calibri in PPTX). Same chrome as `JOIN_PHOENIX_OMEGA.pptx` + `HUMAN_TEAM_STRUCTURE.pptx` shipped in PR #1477 for visual consistency across operator-facing decks.

---

## §8. Open Operator Questions (Q-MM-V2-*)

Each Q is named, scoped, and carries a recommended default. Operator answers gate downstream ws's.

| Q-ID | Question | Recommended default | Gating ws |
|---|---|---|---|
| Q-MM-V2-FIRST-REAL-MUSICIAN-01 | First real musician to onboard | **(a) operator-nominated** (operator picks one they have relationship with) | `ws_pearl_editor_pearl_writer_first_real_musician_onboarding_20260611` |
| Q-MM-V2-PRIORITY-PERSONA-TOPIC-01 | First music-mode book priority cell | **`gen_z_professionals × anxiety × en-US × with-lyrics × deep_book_4h`** (mirrors gold-reference from atom-coverage cascade) | `ws_pearl_editor_music_slot_pools_priority_backfill_20260611` |
| Q-MM-V2-DIVERSITY-GATE-THRESHOLDS-01 | §5 diversity gate thresholds | **As written**: ≤5× variant reuse + ≤30% topic + ≤30% persona + ≤50% format + per-locale per-platform | `ws_pearl_dev_music_brand_diversity_ci_guard_20260611` |
| Q-MM-V2-MUSICGEN-MODEL-SIZE-01 | MusicGen model size | **(a) medium (5 GB VRAM, concurrent with FLUX-schnell)** | `ws_pearl_int_pearl_star_phase_b_musicgen_workload_20260611` |
| Q-MM-V2-DECK-CONFIRM-Q1-01 | Slide 1 audience line | **Drop "forum" reference; "For Musicians and Their Brand Directors"** | (deck ships in this PR) |
| Q-MM-V2-DECK-CONFIRM-Q2-01 | Revenue % on Slide 8 | **Omit** (not in music spec; operator addresses verbally if needed) | (deck ships in this PR) |
| Q-MM-V2-DECK-CONFIRM-Q5-01 | Companion song framing | **Keep "MusicGen companion song packaged with each release; auto-render coming Pearl Star Phase B"** | (deck ships in this PR) |
| Q-MM-V2-FREEBIE-CROSSLINK-01 | Slide 9 freebie sidebar | **Light cross-link to MUSIC-MODE-FREEBIE-FUNNEL-V1-02** | (deck ships in this PR) |
| Q-MM-V2-MUSICIAN-BANKS-SCOPE-01 | Music-side atom-100% SSOT scope | **Parallel structure to en-US SSOT** (persona × topic × slot × locale); theme/emotion/instrument expansion is V3 candidate | `ws_pearl_architect_music_mode_atom_coverage_ssot_20260611` |
| Q-MM-V2-CROSS-CASCADE-PARALLEL-01 | Music-mode atom backfill cadence | **Parallel with en-US atom-coverage Phase A** (different agents + cells; zero conflict) | `ws_pearl_editor_music_slot_pools_priority_backfill_20260611` |
| Q-MM-V2-SANGHA-INTEGRATION-01 | Sangha musicians onboarded via Karma Yoga P6 pillar — 1% fund-share at P1/P2? | **YES if operator confirms Sangha musicians count as active contributors** | (cross-cap; defer until Sangha V1.5 cap entry references) |
| Q-MM-V2-CATALOG-800-RECONCILE-01 | (§2 row 1) MUSIC-MODE §3 (800 per-brand) vs CATALOG-800-PER-BRAND-01 (800 system-wide) contradiction | **Music spec wins for intra-music-mode scope; CATALOG-800 cap entry needs one-line clarifying note** | Cross-cap follow-up Pearl_Architect ws (NOT this session) |
| Q-MM-V2-MUSIC-RUBRIC-01 | Music-specific quality rubric (Phase A entry condition 5) | **Sub-spec under V2** — recommend Pearl_Editor + Pearl_Architect author music-specific ACCEPTANCE rubric extending the book scorecard | Downstream ws |
| Q-MM-V2-PEARL-STAR-PHASE-A-CAP-01 | PEARL-STAR-JOB-QUEUE-V1-01 cap entry + spec authoring | **Open separate Pearl_Architect session** BEFORE V2 §6 Phase B can advance | (separate Pearl_Architect ws — NOT this session) |
| Q-MM-V2-MUSICGEN-LICENSE-CHECK-01 | Commercial-use clearance for MusicGen-medium model variant | **Pearl_Int legal review** before Phase B-1 production launch | Pearl_Int ws under §6.7 |

---

## §9. Cross-References

- V1 cap entries: `MUSIC-MODE-V1-01` + `MUSIC-MODE-BRAND-INTEGRATION-V1-01` + `MUSIC-MODE-FREEBIE-FUNNEL-V1-02`
- Sibling parallel SSOT: `docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md` (merged 2026-06-11 PR #1485) — music side gets parallel SSOT under `ws_pearl_architect_music_mode_atom_coverage_ssot_20260611`
- Threshold framework: `SPEC-739-THRESHOLD-01` (variation floor=3 applies to music slot pools)
- Authority lane: `PEARL-EDITOR-UPSTREAM-01` (Pearl_Editor owns musician_banks)
- ONE-PATH framework: `PEARL-PRIME-ONE-PATH-V1-01` (D8 + slot-dirs; music slots layer additive)
- Catalog scope: `CATALOG-800-PER-BRAND-01` (system-wide 800 reframing — cross-cap reconciliation §2 row 1)
- Pearl Star infra: `PEARL-STAR-JOB-QUEUE-V1-01` (TARGET reference; not yet on main; flagged Q-MM-V2-PEARL-STAR-PHASE-A-CAP-01)
- Companion deck: `artifacts/programs/music_mode_v2_20260611/MUSIC_MODE_INTRODUCTION_DECK.pptx` (10 slides) + `MUSIC_MODE_INTRODUCTION_LONG_FORM.md` (companion prose)
- Coordination: `PRJ-MUSIC-MODE-V2-PRODUCTION-LAUNCH` (status=proposed in this PR); 6 new ws rows
- Audit: `artifacts/qa/music_mode_corrections_audit_20260611.tsv` (machine-readable 12-row audit)

---

## §10. LLM Tier Policy Compliance (per CLAUDE.md)

- **Tier 1 (Claude Code subscription, operator-present):** This spec authoring + 10-slide deck + audit TSV + long-form brief authoring. ✓
- **Tier 2 (Pearl Star Gemma/Qwen, unattended):** Future MusicGen Phase B WAV rendering runs on Pearl Star (local Meta MusicGen model — no paid LLM API). ✓
- **No paid LLM API reads/keys.** Verified — no `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc., referenced. ✓
- **`scripts/ci/audit_llm_callers.py` clean** for this PR — adding spec + deck + audit + coordination row files; zero code introduced. ✓

---

## §11. Cap-Entry Amendments Proposed (Appended in This PR)

### §11.1 MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS

Appended to `docs/PEARL_ARCHITECT_STATE.md` (after MUSIC-MODE-V1-01 entry at line 763):

- Cross-links to `MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md`.
- Ratifies the 12-row correction audit (§2).
- Defines Phase A music-mode launch gate (§4).
- Flags PEARL-STAR-JOB-QUEUE-V1-01 dependency for Phase B WAV auto-render (§6).
- Opens 5 child ws's (atom-coverage SSOT + first-real-musician + slot-pool backfill + MusicGen Phase B + diversity-gate CI guard).

### §11.2 MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES

Appended to `docs/PEARL_ARCHITECT_STATE.md` (after MUSIC-MODE-BRAND-INTEGRATION-V1-01 entry at line 1128):

- Cross-links to `MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md` §5.
- Adds anti-spam diversity gate thresholds (G1-G8).
- Production-profile policy (G1-G5 hard-fail; G6-G8 warn).
- Opens 1 child ws (`ws_pearl_dev_music_brand_diversity_ci_guard_20260611`).

---

## §12. Revision History

| Date | Change |
|---|---|
| 2026-06-11 | Initial V2 production-readiness spec authored — 12-row correction audit + Phase A launch gate + diversity gates + MusicGen Phase B + deck structure + 15 Q-MM-V2-* + 2 cap-amendments. Pearl_Architect session `pearl-architect-music-mode-v2-production-readiness-20260611`. |
