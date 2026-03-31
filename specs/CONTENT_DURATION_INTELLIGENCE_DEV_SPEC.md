# CONTENT DURATION INTELLIGENCE SYSTEM — Dev Spec v1.0

**Date:** 2026-03-31
**Status:** Dev spec — pending review
**Authority scope:** All content formats across all brands, platforms, locales, and personas
**Depends on:** `specs/VIDEO_CONTENT_ENGINE_DEV_SPEC.md`, `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md`, `specs/AI_MANGA_PIPELINE_SUMMARY.md`, `config/quality/ei_v2_config.yaml`, `docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml`, `config/video/channel_registry.yaml`, `config/video/pacing_by_content_type.yaml`
**Research basis:** `research/2026-03-31_optimal-content-durations-global.md` (43 source clusters)

---

## §1 Purpose

This spec defines the **Content Duration Intelligence System (CDIS)** — an automated planning layer that takes `(brand_id, platform, locale, persona, format, therapeutic_intent)` as input and outputs `(recommended_duration, page_count, episode_count, serialization_cadence, duration_fit_score)`.

It prevents two failure modes: **under-dosing** (content too short for therapeutic effect — e.g., a 30-second breathing video when research requires 5 minutes minimum [16]) and **over-running** (content longer than the platform rewards or the persona will consume — e.g., a 20-minute YouTube video for Gen Alpha whose daily reading window is 9 minutes [12]).

---

## §2 Core Concept: Therapeutic Dose x Platform Fit x Persona Attention

Three factors determine optimal duration. The system finds their intersection.

1. **Therapeutic Dose** — minimum exposure for measurable physiological effect. Breathing exercise below 5 min = no HRV change [16]. Guided visualization below 10 min = no parasympathetic activation [17].
2. **Platform Algorithm Fit** — what the platform rewards. YouTube Shorts at 15-30s = 80%+ retention [32]. TikTok at 60-90s = 43% more reach [33].
3. **Persona Attention Budget** — how long each persona actually engages. Gen Alpha: 9 min daily reading [12]. Healthcare RNs: 5-10 min shift breaks.

These factors often conflict. Example: breathing exercise on TikTok for Gen Z needs 5 min therapeutically [16] but TikTok rewards 60-90s [33]. Resolution: micro-dose protocol (60s x 4 daily for 2+ weeks) [42]. The algorithm in §7 resolves all such conflicts.

---

## §3 Duration Registry (Master Table)

14 formats x 5 intents. Representative entries (full registry in `config/duration/duration_registry.yaml`):

| Format | Intent | Min | Optimal | Max | Dose Met | Algo Fit | Ref |
|---|---|---|---|---|---|---|---|
| audiobook | discovery | 1 hr | 2-3 hr | 3 hr | partial | 0.85 | [3][9] |
| audiobook | therapeutic | 5 hr | 5-7 hr | 9 hr | true | 0.90 | [3][16] |
| ebook | therapeutic | 150 pp | 180-230 pp | 300 pp | true | 0.90 | [20] |
| ebook | conversion | 10 pp | 20-40 pp | 60 pp | false | 0.80 | [22] |
| manga_chapter | therapeutic | 30 panels | 40-60 panels | 80 panels | true | 0.95 | [24] |
| webtoon_episode | engagement | 30 panels | 40-60 panels | 80 panels | true | 0.95 | [24][25] |
| webtoon_series | therapeutic | 25 ep | 40-60 ep | 100+ ep | true | 0.90 | [25] |
| video_short | discovery | 10 sec | 15-30 sec | 60 sec | false | 0.95 | [32][34] |
| video_short | therapeutic | 45 sec | 60-90 sec | 3 min | micro [42] | 0.75 | [33] |
| video_mid | therapeutic | 7 min | 10-15 min | 20 min | true | 0.85 | [31][16] |
| video_long | therapeutic | 10 min | 15-20 min | 30 min | true | 0.90 | [31][17] |
| video_lofi | therapeutic | 30 min | 60-90 min | 4 hr | true | 0.90 | [37] |
| exercise_video | therapeutic | 5 min | 10-15 min | 20 min | true | 0.85 | [16][18] |
| podcast_episode | therapeutic | 20 min | 30-40 min | 60 min | true | 0.85 | [38][17] |
| podcast_micro | discovery | 3 min | 5-10 min | 15 min | partial | 0.80 | [38][42] |
| guided_meditation | therapeutic | 5 min | 10-15 min | 30 min | true | 0.95 | [18] |

---

## §4 Platform Duration Profiles

### §4.1 Video Platforms

| Platform | Max | Sweet Spot (Wellness) | Algo Reward Signal | Critical Constraint |
|---|---|---|---|---|
| YouTube Long | 12 hr | 10-20 min | Watch time + session depth; mid-roll at 8+ min [31] | First 8 sec = major drop-off |
| YouTube Shorts | 60 sec | 15-30 sec | 80%+ retention at 15-30s; 22x views at 45-60s vs <10s [32] | Hard cap 60 sec |
| TikTok | 60 min | 60-90 sec | Completion rate #1 signal; <30s = 280% higher completion [33] | First 2 sec = 70% of retention |
| Instagram Reels | 90 sec | 15-30 sec | 3-sec hold >60% = 5-10x reach; Saves > Likes [34] | Wellness: lowest engagement (0.0053%) |
| Bilibili | 10 hr | 7-15 min | Quality > virality; 117M DAU, 102 min/day [35] | Knowledge Zone rewards educational |
| Douyin | 30+ min | 1-3 min | Purchase intent factor; useful > entertaining [36] | Douyin-specific content required |

### §4.2 Audio Platforms

| Platform | Market | Sweet Spot | Key Data |
|---|---|---|---|
| Audible | Global (63.4% share) | 5-7 hr (self-help) | Curates "under 3 hr" collections [9] |
| Spotify | Global | 5-7 hr audiobook; 20-30 min podcast | 15 hr/month included [4] |
| Ximalaya | China (268M MAU) | 10-30 min episodes | 125 min/day avg usage [13] |
| Millie's Library | Korea | 15-30 min summary | Summary audiobooks dominate [15] |
| Headspace / Calm | Global | 10-15 min guided meditation | 10 min daily = 27-30% stress reduction [18] |

### §4.3 Comics / Manga Platforms

| Platform | Market | Panel Sweet Spot | Min Req. | Schedule |
|---|---|---|---|---|
| WEBTOON Canvas | Global | 20-30 panels | Flexible | Creator-set |
| WEBTOON Originals | Global | 40-60 panels | Genre-dependent (Horror: 40, Comedy: 12) [24] | Weekly |
| Kakao Page | Korea | 40-60+ panels | 25-chapter min contract [25] | Weekly |
| Bilibili Comics | China | 30-80 panels | Platform-dependent [26] | Weekly |
| Lezhin | Korea/Global | 70+ panels/ch | Min 24 episodes [24] | Weekly |

### §4.4 Ebook Platforms

| Platform | Market Share | Page Sweet Spot | Price Sweet Spot |
|---|---|---|---|
| KDP | 65-70% global | 150-230 pp | $4.99-$9.99 (70% royalty) [20][22] |
| Readmoo | Taiwan | EPUB; trad. Chinese | Market-specific [23] |
| WeChat Read | China | EPUB/TXT; simp. Chinese | Low-cost market [23] |

---

## §5 Persona Duration Profiles

### §5.1 Per-Persona Attention Budgets

| Persona | Session Budget | Short Video | Audio Tolerance | Reading | Key Constraint |
|---|---|---|---|---|---|
| gen_alpha_students | <3 min/piece | <60 sec | <3 hr audiobook | 30-60 pp | 9 min/day reading [12]; mobile-only |
| gen_z_professionals | 5-15 min | 60-90 sec | 3-5 hr audiobook | 60-150 pp | 73% use audio for self-understanding [10]; 41 min/day audio [6] |
| millennial_women | 10-20 min | 15-30 sec (Reels) | 5-7 hr audiobook | 150-230 pp | Quality over quantity; saves-driven |
| working_parents | 5-15 min | 15-30 sec | 5-7 hr (during chores) | 100-200 pp | Zero free hands; audio-first |
| gen_x_sandwich | 10-20 min | 30-60 sec | 5-9 hr (caregiving) | 150-250 pp | Efficient; no filler tolerance |
| healthcare_rns | **5-10 min micro** | 30-60 sec | 3-5 hr (shift recovery) | 60-150 pp | 12-hr shifts; needs micro-dose |
| first_responders | 5-10 min | 30-60 sec | 3-5 hr | 60-150 pp | High-stress recovery; audio during downtime |
| corporate_managers | 15-30 min | 15-30 sec | 5-7 hr | 150-250 pp | Commute-aligned (20-45 min) |
| tech_finance_burnout | 15-30 min | 30-60 sec | 5-7 hr | 150-230 pp | Lofi during work (60-90 min) [37] |
| entrepreneurs | 10-20 min | 30-60 sec | 5-7 hr | 150-250 pp | Action-oriented; podcast preferred |

### §5.2 Locale Modifiers

| Locale | Modifier | Evidence |
|---|---|---|
| zh-CN | Audio/video tolerance +30-50% | Ximalaya 125 min/day [13]; Bilibili 102 min/day [35] |
| ko-KR | Summary audio preference; manhwa panels +20% | Millie's Library [15]; 60+ panels/ep studios [25] |
| ja-JP | Tankoubon 180-220 pp standard; 15-30 pp/chapter | Iyashikei norms [29] |
| en-US | Baseline (1.0x) | All research baselines US-centric |

---

## §6 Therapeutic Duration Science (Decision Rules)

### §6.1 Minimum Effective Dose by Modality

| Modality | Min Dose | Optimal | Max Useful | Mechanism | Ref |
|---|---|---|---|---|---|
| Breathing exercise | **5 min** | 10-20 min | 20 min 2x/day | HRV increase at 5.5-6 BPM resonance | [16] |
| Guided visualization | **10 min** | 15-20 min | 20 min 2x/day | Parasympathetic via Benson's Relaxation Response | [17] |
| Meditation | **10 min** | 15 min | 60 min | 27% irritability reduction in 10 days | [18] |
| Music therapy | **15 min** | 30 min | 45 min | Autonomic regulation; 60-80 BPM; nonlyrical | [19] |
| Nature exposure | **20 min** | 20-30 min | Diminishing >30 | 21.3%/hr cortisol drop ("nature pill") | [39] |
| Bibliotherapy | Not established | Weekly + reflection | Ongoing | Identification/catharsis/insight (d=0.77) | [30] |
| Micro-mindfulness | **60 sec (4x/day)** | 2 min (4x/day) | Consistent reps | 14% cortisol reduction, 23% attention boost | [42] |
| Panel breath sequence | **~18 sec** (1 cycle) | 3-4 per chapter | 6 max (iyashikei) | ~6 BPM via panel progression | ITE §5 |

### §6.2 Attention Residue

After therapeutic content, effects persist **15-23 minutes** [43]. A 5-minute exercise = 20-25 min total effect. Serialized micro-doses accumulate through residue overlap [42][43].

### §6.3 Decision Rules

- **BLOCKER:** Content below therapeutic minimum for stated intent AND `micro_dose_protocol == false`.
- **Exception:** Micro-dose eligible modalities (breathing, meditation, micro-mindfulness) bypass minimum if `frequency >= 4/day` and `duration >= 14 days`.
- **Panel breath minimum:** Manga/webtoon with therapeutic intent must have >= 1 breath sequence per chapter (ITE §5.2). WARN gate.
- **Afterglow leverage:** Space sequential items 15-23 min apart for residue overlap. INFO gate.

---

## §7 Duration Planner Algorithm

### §7.1 Input/Output Schema

**Input:** `brand_id, platform, locale, persona, format, therapeutic_intent, modality (optional), micro_dose_protocol (bool)`

**Output:** `recommended_duration_sec, recommended_page_count, recommended_panel_count, recommended_episode_count, serialization_cadence, duration_fit_score (0-1), therapeutic_dose_met (bool), platform_compliant (bool), persona_budget_fit (bool), warnings[], blockers[]`

### §7.2 Algorithm

```
1. LOAD base duration from Duration Registry (§3) for (format, intent)
2. APPLY platform hard constraints (§4):
   - Clamp to platform max/min. Log warning if clamped.
3. APPLY persona attention budget (§5) with locale modifier (§5.2):
   - adjusted_budget = persona_budget * locale_modifier
   - Clamp to adjusted_budget if base exceeds it.
4. VALIDATE therapeutic minimum (§6):
   - If intent in [therapeutic, deep_engagement] AND base < therapeutic_min:
     - If micro_dose_protocol: log WARN, mark dose as conditional
     - Else: BLOCKER. Suggest format upgrade or micro-dose switch.
5. SCORE duration_fit:
   - t_score = therapeutic_fit(duration, modality)    [weight: 0.40]
   - p_score = platform_fit(duration, platform)       [weight: 0.35]
   - a_score = attention_fit(duration, persona_budget) [weight: 0.25]
   - duration_fit = (t_score * 0.40) + (p_score * 0.35) + (a_score * 0.25)
6. PLAN serialization for series formats (§8)
```

### §7.3 Conflict Resolution Priority

1. **Platform hard constraints are non-negotiable.** YouTube Shorts = 60 sec max. Period.
2. **Therapeutic minimum > persona budget** when intent is "therapeutic" or "deep_engagement." Switch to micro-dose or upgrade format before cutting below minimum.
3. **Persona budget > therapeutic minimum** when intent is "discovery" or "engagement."
4. **Locale modifiers** apply after persona budget, before therapeutic check.

---

## §8 Serialization Cadence Planner

### §8.1 Episode Count for Therapeutic Arc Completion

| Format | Min Episodes | Optimal | Max | Basis |
|---|---|---|---|---|
| manga_series (iyashikei) | 6 vol (~36 ch) | 8-12 vol (~48-72 ch) | 15+ vol | [29]; wound_honor_cutoff 60% |
| manga_series (shonen) | 10 vol (~60 ch) | 15-25 vol | 50+ vol | Shonen pacing norms |
| webtoon_series | 25 ep (Kakao min) | 40-60 ep | 200+ ep | [25] contract requirements |
| podcast_series | 6 ep | 12-24 ep (1 season) | Ongoing | Quarterly seasons |
| video_series | 4 ep | 8-16 ep (1 season) | Ongoing | YouTube playlist optimization |

### §8.2 Cadence by Platform

| Platform | Cadence | Rationale |
|---|---|---|
| WEBTOON / Kakao / Bilibili Comics | Weekly | Industry standard; reader expectation [24][25][26] |
| YouTube Long | Weekly or biweekly | Session depth algorithm |
| YouTube Shorts / TikTok / Douyin / Reels | Daily (1-3x) | Discovery algo rewards frequency [32][33][34] |
| Podcast | Weekly | Commute alignment; habit formation [38] |
| Podcast (micro) | Daily (M-F) | Micro-dose protocol: frequency > duration [42] |
| Audiobook | Single release or 2-4/year | Catalog building; seasonal alignment |

### §8.3 Video Series Arc Template

```yaml
season: 8-16 episodes
  setup (ep 1-3): discovery intent, character introduction
  build (ep 4-8): engagement intent, conflict deepening, ITE mechanisms
  peak (ep 9-12): therapeutic intent, highest therapeutic density
  resolve (ep 13-16): deep_engagement intent, parasympathetic dominance
between_seasons: 4-8 week gap, 2-3 bridge shorts
```

---

## §9 Manga/Webtoon Page Count Engine

### §9.1 Panel Count by Platform and Genre

| Platform | Genre | Min | Optimal | Max |
|---|---|---|---|---|
| WEBTOON Canvas | Comedy/Slice of Life | 12 | 20-25 | 30 |
| WEBTOON Canvas | Iyashikei/Healing | 20 | 25-30 | 40 |
| WEBTOON Originals | Horror/Crime/Drama | 40 | 50-60 | 80 |
| WEBTOON Originals | Fantasy/Action | 35 | 45-55 | 70 |
| Kakao Page | All genres | 40 | 50-65 | 80+ |
| Bilibili Comics | All genres | 30 | 50-70 | 80+ |
| Lezhin | Contest entries | 70 | 70-90 | 100+ |

### §9.2 Therapeutic Panel Requirements (ITE §5, §8)

| Requirement | Panels Needed | Effect on Episode |
|---|---|---|
| 1 breath sequence (inhale 3-4 + hold 1 + exhale 2-3 + pause) | 6-8 panels | +6-8 per sequence |
| Post-band-4 processing gutter (2x width) | 0 extra | +10% page space |
| Post-band-5 therapeutic gutter (3x width) | 0 extra | +15% page space |
| Resolution breath sequences (1-2 required) | 6-16 panels | In final 25% of chapter |
| Silent page (5-beat protocol) | 5 panels | +1 full page |

**Therapeutic iyashikei WEBTOON Originals episode = 40 (base) + 12 (2 breath sequences) + gutter = ~55-65 panels optimal.**

### §9.3 Iyashikei Density Overrides

| Parameter | Standard | Iyashikei | Basis |
|---|---|---|---|
| Panels per page | 4-6 | 3-4 | Wider = slower = breathing deceleration (ITE §4.2) |
| Splash panels/chapter | 1-2 | 3-5 | More parasympathetic activation |
| Default gutter width | 1.0x | 2.0x (processing) | Continuous emotional space (ITE §8.1) |
| Max breath sequences | 4 | 6 | ITE §5.2 genre override |

---

## §10 Book Duration Engine

### §10.1 Structure (from SOMATIC_BOOK_BLUEPRINT)

- Chapters: 8-14 (min_story_atoms: 8, max: 14)
- Slots per chapter: 10 (10-slot contract)
- Exercise duration: Phase 1 max 300s, Phase 2 max 480s, Phase 3 max 600s
- Emotional bands: min 3 distinct, min 1 at band-5

### §10.2 Audiobook Duration by Persona

| Persona | Target Duration | Chapter Length | Rationale |
|---|---|---|---|
| gen_alpha / gen_z | Under 3-5 hr | 10-15 min | 9-19 min/day reading [12]; Spotify 15 hr/mo [4] |
| healthcare_rns / first_responders | 3-5 hr | 10-15 min | Shift fragments; 5-10 min break alignment |
| working_parents | 5-6 hr | 15-20 min | Chore-aligned; clean chapter breaks |
| millennial_women / gen_x / corporate / tech / entrepreneurs | 5-7 hr | 20-25 min | Commute/session aligned; median bestseller [3] |

### §10.3 Ebook Page Count by Use Case

| Use Case | Pages | Words | Price | Platform |
|---|---|---|---|---|
| Lead magnet | 20-40 pp | 5-12K | Free/$0.99 | KDP, direct |
| Short read | 60-100 pp | 18-30K | $2.99-$4.99 | KDP (70%) |
| Standard self-help | **150-230 pp** | **50-75K** | **$4.99-$9.99** | KDP (70%) |
| Comprehensive guide | 250-400 pp | 75-120K | $9.99+ | KDP (35%) |

---

## §11 EI v2 Integration

### §11.1 New Dimension: `duration_fit`

```yaml
# Addition to config/quality/ei_v2_config.yaml
duration_fit:
  enabled: true
  mode: rule_based
  weights:
    therapeutic_fit: 0.40
    platform_fit: 0.35
    attention_fit: 0.25
  thresholds:
    pass: 0.60    # publish eligible
    warn: 0.45    # warn, still publishable
    fail: 0.44    # block
```

### §11.2 Updated Composite Weights

| Dimension | Current Weight | New Weight |
|---|---|---|
| rerank | 0.35 | 0.30 |
| safety | 0.25 | 0.20 |
| domain_similarity | 0.20 | 0.15 |
| tts_readability | 0.20 | 0.15 |
| **duration_fit** | N/A | **0.20** |

### §11.3 Interaction with Existing Dimensions

- `tts_readability`: Chapters >30 min risk monotone pacing.
- `emotion_arc`: Duration must support 5-phase arc (ITE §6). Short content = truncated arc.
- `somatic_precision`: Exercise durations must meet therapeutic minimums (§6.1).
- `engagement`: Content exceeding persona budget reduces engagement score.

---

## §12 Config Schema

| File | Path | Contents |
|---|---|---|
| Duration Registry | `config/duration/duration_registry.yaml` | Format x intent table (§3) |
| Platform Profiles | `config/duration/platform_duration_profiles.yaml` | Per-platform min/max/sweet-spot (§4) |
| Persona Profiles | `config/duration/persona_duration_profiles.yaml` | Per-persona budgets + locale mods (§5) |
| Therapeutic Rules | `config/duration/therapeutic_dose_rules.yaml` | Min effective durations by modality (§6) |
| Serialization | `config/duration/serialization_cadence.yaml` | Series planning rules (§8) |

Each YAML file is versioned (`version: 1`), machine-validated by `scripts/validate_config.py`, and keyed by the identifiers used in the planner input schema (§7.1).

---

## §13 QC Gates

| Gate ID | Level | Condition |
|---|---|---|
| `DURATION.THERAPEUTIC_MINIMUM` | **BLOCKER** | Below therapeutic min for stated intent, micro_dose_protocol off |
| `DURATION.PLATFORM_MAX` | **BLOCKER** | Exceeds platform hard maximum |
| `DURATION.PLATFORM_MIN` | **BLOCKER** | Below platform hard minimum |
| `DURATION.EXERCISE_MINIMUM` | **BLOCKER** | Exercise video < 5 min (HRV minimum) [16] |
| `DURATION.FIT_SCORE_FAIL` | **BLOCKER** | duration_fit < 0.45 (when fail_mode: block) |
| `DURATION.PLATFORM_SWEET_SPOT` | WARN | Outside platform sweet spot |
| `DURATION.PERSONA_BUDGET` | WARN | Exceeds persona budget by >20% |
| `DURATION.FIT_SCORE_LOW` | WARN | duration_fit < 0.60 |
| `DURATION.BREATH_MISSING` | WARN | Manga/webtoon therapeutic chapter lacks breath sequences |
| `DURATION.CHAPTER_MISMATCH` | WARN | Audiobook chapter length mismatches persona target |
| `DURATION.MICRO_DOSE_NO_FREQ` | WARN | Micro-dose active but no frequency plan attached |
| `DURATION.LOFI_MINIMUM` | WARN | Lofi stream < 30 min |
| `DURATION.SERIALIZATION` | INFO | Series cadence differs from platform recommendation |

**Evaluation order:** BLOCKERs first (any = cannot publish), then WARNs (logged, surfaced), then INFOs (metrics only).

**Remediation:** THERAPEUTIC_MINIMUM: extend, switch to micro-dose, or downgrade intent. PLATFORM_MAX: split into series or platform-specific cut. PERSONA_BUDGET: shorten, split chapters, or re-target persona.

---

## §14 Acceptance Criteria

### Phase 1: Foundation (Weeks 1-4)

| # | Criterion | Verification |
|---|---|---|
| 1 | Duration Registry YAML: all 14 formats x 5 intents = 70 entries | Schema validation passes |
| 2 | Platform Profiles: all 18+ platforms from §4 covered | Cross-ref with channel_registry.yaml |
| 3 | Persona Profiles: 10 personas x 5 locales with modifiers | Cross-ref with canonical_personas.yaml |
| 4 | Therapeutic Rules: 8 modalities from §6.1 encoded | Evidence refs resolve to research doc |
| 5 | Duration Planner: accepts §7.1 input, returns §7.1 output | 20+ unit tests covering all conflict types |
| 6 | QC gates: 13 gates from §13 integrated into pipeline | Gate-level tests with known-violating inputs |

### Phase 2: Integration (Weeks 5-8)

| # | Criterion | Verification |
|---|---|---|
| 7 | EI v2 `duration_fit` dimension in ei_v2_config.yaml | Dimension scores appear in EI v2 output |
| 8 | Planner called automatically during content planning | Pipeline integration test |
| 9 | Serialization Planner outputs for manga, webtoon, podcast, video | 5 series planning scenario tests |
| 10 | Book Duration Engine matches SOMATIC_BOOK_BLUEPRINT constraints | Cross-validation test |
| 11 | VCE reads duration from CDIS instead of hardcoded values | VCE integration test |
| 12 | Batch test: 50 items produce duration_fit scores with 0 BLOCKERs | Batch QC report |

---

*SpiritualTech Systems -- Content Duration Intelligence System -- Dev Spec v1.0 -- Confidential*
