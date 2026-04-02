# Experience Layer Anti-Spam Spec

**Purpose:** Prevent the catalog and release waves from looking like "same product, different label" to platform algorithms and human reviewers — even when content, structure, and metadata are technically unique.

**Status:** Canonical (planning + gate layer)

**Authority:** This spec. Subordinate to [DUPE_EVAL_SPEC.md](./DUPE_EVAL_SPEC.md) (structural CTSS), [TEACHER_PORTFOLIO_PLANNING_SPEC.md](./TEACHER_PORTFOLIO_PLANNING_SPEC.md) (portfolio anti-spam), [../docs/CATALOG_ARCHITECTURE_AT_SCALE.md](../docs/CATALOG_ARCHITECTURE_AT_SCALE.md) (catalog shape), [../docs/VIDEO_PIPELINE_SPEC.md](../docs/VIDEO_PIPELINE_SPEC.md) §15 (channel isolation).

**Problem this solves:** Existing gates (CTSS, wave density, structural entropy, CTA caps, release velocity) compare books against books on content and structure dimensions. They do not check whether a wave or catalog region delivers the **same reader experience** repeatedly — same product feel, same reader intent, same consumption pattern, same outcome promise. Platforms flag this as "functionally identical" even when text differs. At 24 brands × high weekly volume, this is the remaining detection surface.

**Scope:** Planning-layer only. No content modification, no prose scoring. Adds fields to compiled plans and wave checks; extends existing gates rather than creating a parallel gate chain.

---

## 1. What "experience" means (defined narrowly)

Experience = the combination of **how the reader consumes the book**, **what they use it for**, and **what it feels like as a product**. Two books can be textually unique and structurally diverse but still deliver the same experience (e.g. both are passive-reading ebooks aimed at calming anxiety with a single-sitting pacing model).

Experience is **not** content, structure, metadata, or release timing — those are already covered by existing gates. Experience is the layer above: the product-level signal that platforms and reviewers perceive when they look at a batch.

---

## 2. Experience dimensions

Seven dimensions, each with a controlled vocabulary. Values are assigned at planning time (BookSpec / compiled plan) and carried through the pipeline.

### 2.1 `delivery_experience`

How the reader physically interacts with the product. Not the same as `format_id` (which is internal structure); this is the **reader-facing product feel**.

| Value | Description |
|-------|-------------|
| `passive_reading` | Traditional book: read start-to-finish or browse chapters |
| `guided_program` | Structured multi-day/multi-week program with progression |
| `exercise_workbook` | Reader actively writes, fills in, completes exercises |
| `audio_immersion` | Designed for audio-first consumption (eyes-free, ambient) |
| `daily_practice` | Short daily units; designed for habitual return |
| `reference_toolkit` | Dip-in reference; reader looks up frameworks, applies tools |
| `narrative_journey` | Story-led; reader follows a through-line (case study, memoir-style teaching) |

### 2.2 `reader_intent`

The job-to-be-done the reader hires this book for.

| Value | Description |
|-------|-------------|
| `calm_down` | Immediate emotional regulation, relief, soothing |
| `understand_self` | Self-insight, pattern recognition, "why do I do this" |
| `build_skill` | Acquire a repeatable capability (habit, technique, practice) |
| `take_action` | Make a decision, execute a plan, change behavior now |
| `shift_identity` | Rethink who they are; life transition, reinvention |
| `deepen_practice` | Already have a practice; go further, refine, commit |
| `find_meaning` | Existential, philosophical, spiritual seeking |

### 2.3 `pacing_model`

Expected consumption pattern.

| Value | Description |
|-------|-------------|
| `single_sitting` | Designed to be consumed in one session (1–3 hours) |
| `multi_day` | 3–7 day arc; daily sessions building on each other |
| `extended_program` | 2–6 week structured program |
| `ongoing_ritual` | No end; daily/weekly return indefinitely |
| `dip_in` | No sequence; reader enters at any point |

### 2.4 `outcome_type`

What the reader walks away with.

| Value | Description |
|-------|-------------|
| `emotional_shift` | Feels differently (calmer, lighter, more hopeful) |
| `cognitive_clarity` | Thinks differently (new framework, reframed problem) |
| `behavioral_change` | Does differently (new habit, new routine, new practice) |
| `skill_acquired` | Can do something they couldn't before |
| `decision_made` | Resolved an open question; knows what to do next |
| `worldview_expanded` | Sees reality from a new angle (philosophical, spiritual) |

### 2.5 `engagement_depth`

How much the book asks of the reader.

| Value | Description |
|-------|-------------|
| `light` | Easy read; low effort; comfort/inspiration |
| `moderate` | Requires attention but not active work |
| `intensive` | Demands active participation: writing, exercises, daily commitment |

### 2.6 `transformation_speed`

How quickly the book promises results.

| Value | Description |
|-------|-------------|
| `immediate` | "Feel better now" — single session relief |
| `gradual` | Weeks of practice → cumulative shift |
| `long_arc` | Months/years; identity-level or practice-level depth |

### 2.7 `perceived_positioning`

How the book presents itself to the market — the external promise visible in title, subtitle, description, and cover. Two books can have identical experience tuples but different positioning (or vice versa). This dimension catches **marketing-surface sameness** that the other six miss.

| Value | Description |
|-------|-------------|
| `quick_fix` | "Fix this fast" — urgency-driven, immediate relief promise |
| `deep_work` | "Do the real work" — serious, effortful, no shortcuts |
| `spiritual_path` | "Walk the path" — devotional, contemplative, tradition-rooted |
| `practical_system` | "Here's the system" — frameworks, steps, structured method |
| `reflective_insight` | "Understand why" — introspective, meaning-making, wisdom |
| `scientific_guide` | "Here's what research says" — evidence-framed, credibility-led |
| `narrative_companion` | "Walk with me" — story-led, relational, personal voice |

**Why 7 dimensions, not 6:** Platforms cluster not just by what a product *is* but by what it *looks like* externally. Ten books all positioned as "calm your anxiety fast" cluster as duplicates even if their experience tuples differ. Perceived positioning is the marketing fingerprint that titles, descriptions, and covers project — the last surface reviewers and algorithms evaluate before flagging.

---

## 3. How dimensions are assigned

### 3.1 Planning time

The portfolio planner or catalog planner assigns experience dimensions when creating a BookSpec. Inputs:

- **Engine** → strong default for `delivery_experience` (e.g. a somatic-exercise engine defaults to `exercise_workbook`; a narrative engine defaults to `narrative_journey`).
- **Topic × persona** → strong default for `reader_intent` (e.g. anxiety × overwhelmed parent → `calm_down`; productivity × executive → `take_action`).
- **Arc** → informs `pacing_model` and `transformation_speed` (e.g. a 3-chapter arc → `single_sitting` + `immediate`; a 12-chapter progressive arc → `extended_program` + `gradual`).
- **Format** → informs `engagement_depth` (e.g. workbook format → `intensive`; standard book → `moderate`).

Defaults are in config (§4). Planners can override per-book.

### 3.2 Resolution priority

1. Explicit override in wave plan or BookSpec (highest)
2. `config/experience/experience_defaults.yaml` mapping (engine, topic, persona, arc, format → experience dimensions)
3. Fallback: `delivery_experience: passive_reading`, `reader_intent: understand_self`, `pacing_model: single_sitting`, `outcome_type: cognitive_clarity`, `engagement_depth: moderate`, `transformation_speed: gradual`, `perceived_positioning: reflective_insight`

### 3.3 Experience assignment guide (consistency rules)

To prevent subjective drift in assignment, these rules are deterministic and must be followed by planners (human or automated). The goal is that two planners looking at the same BookSpec assign the same tuple.

**`delivery_experience` — determined by format + engine:**

- Format is workbook or engine has >50% exercise slots → `exercise_workbook`
- Engine is narrative/story-first → `narrative_journey`
- Engine is somatic/body-practice → `guided_program`
- Audio-only format (no text companion) → `audio_immersion`
- Chapter count ≤5 and each chapter is a standalone unit → `daily_practice` or `reference_toolkit` (use `daily_practice` if sequential, `reference_toolkit` if non-sequential)
- Otherwise → `passive_reading`

**`reader_intent` — determined by topic + persona:**

- Topic is anxiety/stress/panic + persona is in acute distress → `calm_down`
- Topic involves self-analysis (shame, overthinking, patterns) → `understand_self`
- Topic is skill-based (productivity, discipline, habits) → `build_skill`
- Topic requires decision/action (career change, life reset) → `take_action`
- Topic involves spiritual/philosophical seeking → `find_meaning`
- Topic extends existing practice (advanced meditation, deeper discipline) → `deepen_practice`
- Topic involves identity/life transition → `shift_identity`

**`perceived_positioning` — determined by title/subtitle angle:**

- Title emphasizes speed/ease/relief → `quick_fix`
- Title emphasizes effort/mastery/depth → `deep_work`
- Title references tradition/devotion/spirit → `spiritual_path`
- Title emphasizes method/system/framework → `practical_system`
- Title emphasizes understanding/insight/wisdom → `reflective_insight`
- Title emphasizes evidence/research/science → `scientific_guide`
- Title emphasizes story/journey/companion → `narrative_companion`

The remaining dimensions (`pacing_model`, `outcome_type`, `engagement_depth`, `transformation_speed`) are resolved from arc structure and format — see §4.1 defaults. Override only when the default clearly misrepresents the product.

### 3.4 Carried through pipeline

Experience fields live on the compiled plan JSON alongside existing fields (`arc_id`, `engine_id`, `format_id`, `program_id`, `worldview_id`, `angle_id`). They are **not** used during content generation — only for wave checks, similarity index, and dashboards.

---

## 4. Config

### 4.1 `config/experience/experience_defaults.yaml`

Maps existing planning keys to experience dimension defaults.

```yaml
experience_defaults:
  # Engine → delivery_experience
  by_engine:
    somatic_exercise: { delivery_experience: exercise_workbook, engagement_depth: intensive }
    narrative_transformation: { delivery_experience: narrative_journey, engagement_depth: moderate }
    practical_system: { delivery_experience: guided_program, engagement_depth: moderate }
    spiritual_reflection: { delivery_experience: audio_immersion, engagement_depth: light }
    rational_framework: { delivery_experience: reference_toolkit, engagement_depth: moderate }
    # ... one entry per engine_id

  # Topic × reader_intent + perceived_positioning (soft default; persona can modify)
  by_topic:
    anxiety: { reader_intent: calm_down, outcome_type: emotional_shift, perceived_positioning: quick_fix }
    overthinking: { reader_intent: understand_self, outcome_type: cognitive_clarity, perceived_positioning: reflective_insight }
    burnout: { reader_intent: calm_down, outcome_type: behavioral_change, perceived_positioning: practical_system }
    productivity: { reader_intent: build_skill, outcome_type: skill_acquired, perceived_positioning: practical_system }
    grief: { reader_intent: find_meaning, outcome_type: worldview_expanded, perceived_positioning: narrative_companion }
    relationships: { reader_intent: understand_self, outcome_type: behavioral_change, perceived_positioning: reflective_insight }
    shame: { reader_intent: understand_self, outcome_type: emotional_shift, perceived_positioning: deep_work }
    discipline: { reader_intent: build_skill, outcome_type: behavioral_change, perceived_positioning: practical_system }
    presence: { reader_intent: deepen_practice, outcome_type: worldview_expanded, perceived_positioning: spiritual_path }
    identity: { reader_intent: shift_identity, outcome_type: worldview_expanded, perceived_positioning: deep_work }
    # ... one entry per canonical topic

  # Arc length → pacing + transformation_speed
  by_arc_chapter_count:
    short:   # 3–5 chapters
      pacing_model: single_sitting
      transformation_speed: immediate
    medium:  # 6–10 chapters
      pacing_model: multi_day
      transformation_speed: gradual
    long:    # 11+ chapters
      pacing_model: extended_program
      transformation_speed: long_arc
```

### 4.2 `config/experience/experience_wave_controls.yaml`

Wave-level and sliding-window caps for experience dimensions. Extends (does not replace) `release_wave_controls.yaml`.

```yaml
experience_wave_controls:

  # Threshold ramp: start with launch thresholds; tighten after confidence builds.
  # Switch to "established" after 3 clean waves (no platform flags, no manual reviews).
  threshold_tier: launch   # launch | established

  # Per-wave caps (same week)
  # Two tiers: "launch" (first 3 waves — looser to avoid forcing unnatural distribution)
  # and "established" (after 3 clean waves — tighten toward target).
  weekly_caps:
    launch:
      max_same_delivery_experience: 0.50
      max_same_reader_intent: 0.50
      max_same_pacing_model: 0.55
      max_same_outcome_type: 0.55
      max_same_engagement_depth: 0.60
      max_same_transformation_speed: 0.60
      max_same_perceived_positioning: 0.45   # Positioning clusters fast; tighter even at launch
    established:
      max_same_delivery_experience: 0.40
      max_same_reader_intent: 0.40
      max_same_pacing_model: 0.50
      max_same_outcome_type: 0.50
      max_same_engagement_depth: 0.55
      max_same_transformation_speed: 0.55
      max_same_perceived_positioning: 0.35

  # Composite experience similarity (Jaccard on 7-field tuple)
  experience_similarity:
    # Two books with identical experience tuple = 1.0
    # Compare: within wave, and against recent catalog window
    wave_max_identical_experience_tuple: 3    # No more than 3 books in a wave share exact same 7-field experience tuple
    catalog_window_weeks: 8                   # Look back 8 weeks
    catalog_max_same_experience_per_brand: 6  # Per brand, no more than 6 books with identical experience tuple in window
    # O(1) dedup: compute experience_hash = sha256(sorted tuple) at plan time; store in similarity index
    use_experience_hash: true

  # Anti-homogeneity contribution
  # These weights are added to release_wave_controls.yaml anti_homogeneity.weights
  # when experience fields are present on plans. If absent, ignored (graceful degrade).
  # Note: delivery_experience and reader_intent are weighted heaviest because they drive
  # nearly all "same product" flags on platforms.
  anti_homogeneity_weights:
    delivery_experience_diversity: 0.10
    reader_intent_diversity: 0.10
    perceived_positioning_diversity: 0.05
    # These reduce existing weights proportionally so total still = 1.0
    # Implementation: normalize all weights (existing + new) to sum 1.0
```

---

## 5. Gate integration (extend, don't duplicate)

**No new gate scripts.** Experience checks are added to existing gates.

### 5.1 `check_wave_density.py` — add experience caps

When experience fields are present on plans in the wave:

- Check `weekly_caps` from `experience_wave_controls.yaml` (same logic as existing arc/band/slot caps: count, compute share, FAIL if over threshold).
- Check `wave_max_identical_experience_tuple` (group plans by 7-field experience tuple; FAIL if any group > cap).
- If experience fields are missing (legacy plans): WARN and skip experience checks. Controlled by `release_wave_controls.allow_legacy_plans`.

### 5.2 `check_release_wave` anti-homogeneity score — add experience diversity

When experience fields are present:

- Add `delivery_experience_diversity` and `reader_intent_diversity` to the existing anti-homogeneity weights.
- Normalize all weights to sum 1.0 (so existing weights shrink proportionally; no manual rebalancing needed).
- Diversity for each experience dimension = 1 - HHI (Herfindahl–Hirschman Index) of value distribution in the wave.

### 5.3 `check_platform_similarity.py` — optional experience in CTSS

**Not in CTSS by default.** CTSS compares structural fingerprints; experience is a planning/product dimension, not a structural one. However, if `experience_in_ctss: true` is set in config, add a low-weight experience component:

- Experience match = 1.0 if identical 6-field tuple, 0.0 if all different. Weighted at 0.05 (lowest component). This is a soft signal, not a primary discriminator.
- Default: `experience_in_ctss: false`. Enable only when catalog is large enough (500+ books) that experience clustering becomes a real risk.

### 5.4 Similarity index

`artifacts/catalog_similarity/index.jsonl` rows gain 7 optional fields (`delivery_experience`, `reader_intent`, `pacing_model`, `outcome_type`, `engagement_depth`, `transformation_speed`, `perceived_positioning`). Existing rows without these fields are valid (backward compatible).

### 5.5 `run_prepublish_gates.py`

No change. Experience checks run inside existing gate scripts (wave density, anti-homogeneity). No new gate step.

---

## 6. Dashboard / observability

### 6.1 Drift signals (for editorial)

Add to the existing drift dashboard:

- **Experience distribution** — pie charts of `delivery_experience`, `reader_intent`, `pacing_model` across recent waves and full catalog.
- **Experience tuple clustering** — top 10 most-reused experience tuples and their book counts. Alert when any tuple exceeds `catalog_max_same_experience_per_brand`.
- **Experience diversity score** — rolling 4-week mean of (1 - HHI) per experience dimension. Trend line.

### 6.2 Composite risk score (observability only, not a gate)

A single 0–1 number per book/wave for editorial dashboards. **Not a blocking gate** — the individual gates (CTSS, wave density, entropy, experience caps) remain the hard blocks.

```yaml
composite_risk_score:
  purpose: "Dashboard KPI only. Not a gate. Individual gates block; this number shows 'how close to the edge.'"

  # Default weights (platform-agnostic)
  weights:
    content_similarity_ctss: 0.22
    structural_entropy: 0.12
    wave_density: 0.12
    experience_homogeneity: 0.18   # 1 - experience diversity score for the wave
    metadata_similarity: 0.10
    release_pattern: 0.10
    cta_density: 0.05
    author_velocity: 0.05
    perceived_positioning_homogeneity: 0.06

  # Platform-specific weight overrides (apply when wave targets a primary platform)
  platform_weights:
    amazon_kdp:
      reader_intent_boost: 0.05       # Amazon cares most about search relevance / intent clustering
      content_similarity_ctss: 0.25
    google_play:
      delivery_experience_boost: 0.05  # Google flags same product type repeated
      metadata_similarity: 0.15
    findaway_spotify:
      pacing_model_boost: 0.05        # Listener retention patterns
      release_pattern: 0.15
    apple_books:
      perceived_positioning_homogeneity: 0.10  # Apple editorial curation
      experience_homogeneity: 0.20

  interpretation:
    safe: "<0.50"
    elevated: "0.50–0.65"
    high: "0.65–0.80"
    critical: ">0.80"
```

### 6.3 First-of-kind alerts

When a brand publishes a book with an experience tuple it has **never used before**, flag it for editorial review. This catches brand drift — where a brand slowly becomes a different publisher without anyone noticing.

- **Trigger:** Book's 7-field experience tuple does not appear in that brand's catalog history (similarity index, filtered by brand_id).
- **Action:** WARN (not FAIL). Dashboard highlights the book with "NEW EXPERIENCE FOR BRAND" label.
- **Value:** Prevents a calm-meditation brand from quietly becoming a productivity-systems brand over 6 months of incremental drift.
- **Implementation:** Checked in `check_wave_density.py` when experience fields and brand_id are present. Query similarity index for that brand's historical tuples.

---

## 7. Per-brand experience profile (soft constraint)

Each brand should have a **dominant experience profile** — not a hard lock, but a center of gravity that makes the brand feel like a distinct publisher.

### 7.1 Config: `config/experience/brand_experience_profiles.yaml`

```yaml
brand_experience_profiles:
  stillness_press:
    primary_delivery: [passive_reading, audio_immersion]
    primary_intent: [calm_down, find_meaning]
    primary_pacing: [single_sitting, ongoing_ritual]
    primary_positioning: [spiritual_path, reflective_insight]
    # Soft constraint: ≥60% of brand output should align with primary values
    alignment_target: 0.60
    # Hard constraint: no single delivery_experience > 70% of brand output
    max_single_experience_share: 0.70

  cognitive_clarity:
    primary_delivery: [reference_toolkit, guided_program]
    primary_intent: [understand_self, build_skill]
    primary_pacing: [dip_in, multi_day]
    primary_positioning: [scientific_guide, practical_system]
    alignment_target: 0.60
    max_single_experience_share: 0.70

  # ... one entry per brand
```

### 7.2 Brand-relative threshold overrides

Brands with narrow focus (e.g. Stillness Press is *supposed* to be calm-down + passive-reading) should not be penalized for doing their job. Brand profiles can override per-dimension wave caps for that brand only:

```yaml
  stillness_press:
    # ... primary_delivery, primary_intent, etc. (as above)
    weekly_cap_overrides:
      max_same_delivery_experience: 0.65   # Stillness IS the passive-reading brand; allow higher
      max_same_reader_intent: 0.60         # calm_down is their lane
    # All other caps inherit from experience_wave_controls.yaml
```

Implementation: `check_wave_density.py` loads brand profiles. For per-brand checks, it uses the brand override if present; otherwise falls back to global caps. **Network-level caps (§8) are never overridden** — a brand can be internally concentrated but the network must still look diverse.

### 7.3 Enforcement

- **Planning time:** Portfolio planner checks candidate allocation against brand profile. WARN (not FAIL) if alignment drops below `alignment_target`.
- **Wave check:** `check_wave_density.py` checks `max_single_experience_share` per brand within the wave (using brand overrides if present). FAIL if exceeded.
- **Advisory:** Dashboard shows brand × experience heatmap so editorial can see drift.

---

## 8. Cross-brand experience isolation (network level)

At 24 brands, the aggregate network must not look like "one system generating the same experience under different labels."

### 8.1 Network-level caps

```yaml
network_experience_caps:
  # Across ALL brands in a release window:
  max_same_experience_tuple_share: 0.15   # No more than 15% of all books across all brands share identical experience tuple
  min_distinct_delivery_experiences: 4     # At least 4 different delivery_experience values represented
  min_distinct_reader_intents: 4           # At least 4 different reader_intent values represented
```

### 8.2 Enforcement

- Checked in `check_wave_density.py` when `--network-mode` flag is set (runs across all brands in the wave, not per-brand).
- FAIL if caps violated. This is the highest-level anti-spam check: "does the network look like one factory?"

---

## 9. Platform-specific notes

Experience dimensions are platform-agnostic by design. However, platform-specific enforcement differs:

| Platform | Primary detection surface | Experience dimension that matters most |
|----------|--------------------------|---------------------------------------|
| Google Play Books | Metadata clustering, content similarity | `delivery_experience` (same product type repeated) |
| Amazon KDP / ACX | Near-duplicate content, keyword permutations | `reader_intent` (same job-to-be-done across many books) |
| Findaway / Spotify | Voice fingerprint, description patterns | `pacing_model` (same listening pattern) |
| Apple Books | Category concentration, editorial curation | `outcome_type` (same promise across catalog) |

No platform-specific thresholds in this spec. Use `safe_velocity.yaml` for per-platform volume caps. Experience checks apply uniformly; the per-platform variance is in what triggers human review, not in our gate logic.

---

## 10. What this spec does NOT do

- Does not modify content, prose, or structure.
- Does not replace CTSS, wave density, structural entropy, CTA caps, or release velocity gates — extends them.
- Does not simulate platform algorithms or claim to know how platforms score internally.
- Does not hard-lock brands to single experience profiles (soft constraint with overrides).
- Does not add a new gate script or new pipeline step — all checks live in existing gates.
- Does not require experience fields to be present for legacy plans to pass (graceful degrade).
- AI disclosure is handled as a hard gate in §14.6, not as an operational checklist. See `docs/audiobook_ops_manual.md` for disclosure policy details.
- Does not guarantee platform outcomes. This is a risk-reduction framework, not a compliance certification.

---

## 11. Implementation order

### Phase 1: MVP (close the gap)

1. **Config:** Create `config/experience/experience_defaults.yaml`, `config/experience/experience_wave_controls.yaml`, `config/experience/brand_experience_profiles.yaml`, `config/experience/risky_combos.yaml`.
2. **Planning:** Add experience resolution to portfolio planner / catalog planner — resolve from defaults (§3, §4), write all 7 fields + `experience_hash` to BookSpec and compiled plan.
3. **Wave density:** Extend `check_wave_density.py` to read experience fields and enforce weekly_caps (tiered: launch/established), tuple clustering, risky combo caps, and novel clustering alerts (§13.5).
4. **Assignment guide:** Document §3.3 rules in planner code and editorial onboarding.
5. **AI disclosure gate:** Add `ai_disclosure_status` field to compiled plan; enforce as FAIL in `run_prepublish_gates.py` (§14.6).
6. **Experience–metadata consistency:** Implement WARN-level check (§16) at plan time. (Moved to Phase 1 per review feedback — catches "garbage in" before it enters the system.)

### Phase 2: Hardening (after 3 clean waves)

7. **Anti-homogeneity:** Extend `check_release_wave` to include experience diversity weights (delivery + intent + positioning).
8. **Similarity index:** Add 7 optional experience fields + `experience_hash` to index.jsonl rows.
9. **Brand profiles:** Implement brand-relative threshold overrides (§7.2) and first-of-kind alerts (§6.3).
10. **Network mode:** Add `--network-mode` to wave density for cross-brand checks (§8).
11. **Pre-commit validation:** Implement tuple consistency check against historical patterns (§16.2).
12. **Natural variance:** Implement controlled imperfection logic in soft-cap enforcement (§15.4).

### Phase 3: Observability + scale (after 6 waves)

13. **Dashboard:** Add experience distribution, tuple clustering, first-of-kind alerts, entropy slope tracking, override rate monitoring to drift dashboard.
14. **Composite score:** Add as dashboard-only KPI with platform-specific weights (§6.2).
15. **Novelty injection:** WARN when wave lacks rare experience tuples (§15.1).
16. **Feedback loop:** Begin tracking platform outcome signals; manual threshold review; entropy slope alerts + diversity restoration protocol (§15.2, §15.3).
17. **Velocity governance:** Implement cadence irregularity checks and metadata velocity gate (§14).
18. **Threshold ramp:** Switch from `launch` to `established` tier when platform signals are clean.

Phase 1 closes 90% of the experience-level gap. Phase 2 makes it robust. Phase 3 makes it self-correcting.

---

## 12. Relationship to existing system

| Existing layer | What it catches | What experience layer adds |
|----------------|-----------------|---------------------------|
| CTSS (DupEval) | Structural fingerprint clones | "Same structure" ≠ "same product feel"; experience catches same-feel with different structure |
| Wave density | Same arc/band/slot/ex clustering | Same product *type* clustering (all passive-reading, all calm-down intent) + risky combo caps |
| Structural entropy | Single-family dominance per book | Single-experience dominance per wave/brand/network |
| CTA / freebie density | Same offer repeated | (No overlap — CTA is about marketing, not product experience) |
| Release velocity | Too many books too fast | Cadence irregularity + cross-brand desynchronization (§14) |
| Teacher portfolio | Same teacher flooding one topic | Same *experience* flooding one brand (different teachers, same product feel) |
| Editorial program / worldview | Catalog shape and intellectual lens | Experience is orthogonal to worldview — two worldviews can deliver same experience |
| Metadata diversity | Same title/description pattern | Experience–metadata consistency check (§16) + metadata velocity gate (§14.4) |
| (none) | — | Perceived positioning (§2.7): marketing-surface sameness invisible to other layers |
| (none) | — | Novelty injection (§15.1): forces genuinely unfamiliar tuples into every wave |
| (none) | — | Feedback loop (§15.2): self-correcting thresholds from real platform signals |

The experience layer fills the gap between "structurally different" and "feels like a different product." The velocity governance and feedback layers ensure the system adapts to enforcement changes over time.

---

## 13. Risky combination caps

Individual dimension caps catch single-axis clustering. But certain **combinations** of values form high-risk product archetypes that platforms flag even when each dimension alone is within threshold.

### 13.1 Problem

Example: `reader_intent: calm_down` + `transformation_speed: immediate` + `pacing_model: single_sitting` = "anxiety quick-fix product." Three books with this combo in one wave may pass all per-dimension caps but still read as "same product" to a reviewer.

### 13.2 Config: `config/experience/risky_combos.yaml`

```yaml
risky_combos:
  # Each entry: a combination of dimension values that, when concentrated, signals "same product cluster."
  # max_share: maximum share of wave that may have this exact combo.
  # max_per_brand_per_window: max books with this combo per brand in catalog_window_weeks.

  - combo:
      reader_intent: calm_down
      transformation_speed: immediate
      pacing_model: single_sitting
    label: "anxiety_quick_fix"
    max_share: 0.20
    max_per_brand_per_window: 3

  - combo:
      reader_intent: build_skill
      delivery_experience: guided_program
      perceived_positioning: practical_system
    label: "productivity_program"
    max_share: 0.25
    max_per_brand_per_window: 4

  - combo:
      reader_intent: calm_down
      perceived_positioning: quick_fix
      engagement_depth: light
    label: "comfort_content"
    max_share: 0.20
    max_per_brand_per_window: 3

  - combo:
      reader_intent: find_meaning
      delivery_experience: audio_immersion
      perceived_positioning: spiritual_path
    label: "spiritual_audio"
    max_share: 0.25
    max_per_brand_per_window: 4

  # Add combos as real wave data reveals new clustering patterns.
  # Seed list above covers the highest-risk archetypes for self-help publishing.
```

### 13.3 Enforcement

- Checked in `check_wave_density.py` alongside per-dimension caps.
- For each risky combo: count books in wave that match **all** specified dimensions → compute share → FAIL if over `max_share`.
- For catalog window: count books per brand matching combo in last `catalog_window_weeks` → FAIL if over `max_per_brand_per_window`.
- Risky combos are **additive to** per-dimension caps, not a replacement. A wave can pass all dimension caps and still fail a combo cap.

### 13.4 Maintenance

- Review and update combos quarterly based on actual wave data and platform feedback.
- The combo list is intentionally short (4–8 entries). If it grows beyond 12, the taxonomy may need revision.

### 13.5 Novel clustering alert (proactive combo discovery)

Do not wait for quarterly reviews to discover new risky combos. When 3+ books in a wave share a dimension-combo that has never appeared in the risky_combos list *and* has never been seen more than twice in catalog history, flag it as a **potential new risky combo** for human review.

- **Trigger:** 3+ books in wave share identical values on 3+ dimensions, AND that combo is not in `risky_combos.yaml`, AND combo appeared ≤2 times in catalog history.
- **Action:** WARN. Dashboard shows "NOVEL CLUSTER DETECTED: [dimension values]. Consider adding to risky_combos.yaml."
- **Value:** Catches emergent archetypes between quarterly review cycles. If a new pattern appears (e.g. `narrative_journey` + `shift_identity` + `long_arc` suddenly clusters on Apple Books), you catch it in-wave instead of after 8 weeks of exposure.

---

## 14. Velocity governance and account behavioral fingerprint

Experience differentiation protects product-level diversity. But at 24 brands × high volume, the **account behavioral pattern** is an independent detection surface. Amazon, Google, and Apple flag publishing operations by submission velocity, cadence regularity, and cross-account synchronization — even when content and experience are perfectly diverse.

### 14.1 What this section adds (and doesn't)

This section **does not replace** `safe_velocity.yaml`, `release_scheduler.yaml`, or `velocity_ramp.yaml` — those handle per-platform caps and ramp phases. This section adds **behavioral fingerprint awareness**: making the release pattern look like independent publishers, not a coordinated network.

**Placement note:** These checks are behavioral anti-spam, not experience-layer concerns. They live here because they complete the detection-surface coverage, but implementation belongs in `generate_weekly_schedule.py` and `release_scheduler.yaml`, not in `check_wave_density.py`. The exception is the metadata velocity gate (§14.4), which extends wave density.

### 14.2 Behavioral signals platforms detect (heuristic, not confirmed policy)

| Signal | What triggers suspicion | Your existing mitigation | Gap |
|--------|------------------------|--------------------------|-----|
| Submission velocity spike | Many books from one account in short burst | `safe_velocity.yaml` per-platform caps | None — covered |
| Clock-like regularity | Exactly N books every M days, zero variance | `release_scheduler.yaml` variance: ±40% | Weak — variance is applied but cadence shape may still look periodic |
| Cross-account synchronization | Multiple accounts publish same day / same cadence | `same_day_cross_brand_max: 3` | Partially covered — needs per-week cross-brand cadence diversity |
| AI disclosure | Undisclosed AI-generated content | Operational policy | Not in this spec — operational, not gate |
| Metadata velocity | Many new titles with similar metadata patterns in short window | No dedicated gate | **Gap**: metadata pattern + velocity combo not checked |

### 14.3 Cadence irregularity enforcement

Add to `release_scheduler.yaml` or as a check in `generate_weekly_schedule.py`:

```yaml
cadence_irregularity:
  # Prevent clock-like publishing patterns per brand.
  # Measure: coefficient of variation (CV = stdev / mean) of books-per-week over sliding window.
  # Higher CV = more irregular = more human-looking.
  min_cv_per_brand_8_week: 0.30          # CV < 0.30 over 8 weeks = too regular → WARN
  min_cv_per_brand_8_week_fail: 0.20     # CV < 0.20 = machine-like → FAIL (tightened from 0.15; a CV of 0.15 still looks periodic to human reviewers)

  # Cross-brand desynchronization: no two brands should have correlated weekly patterns.
  # Measure: Pearson correlation of books-per-week between any two brands over 8 weeks.
  max_cross_brand_correlation: 0.60      # r > 0.60 = synchronized → WARN
  max_cross_brand_correlation_fail: 0.80 # r > 0.80 → FAIL

  # "Burst + silence" requirement: at least 1 week in every 8 with zero or near-zero releases per brand.
  min_quiet_weeks_per_8: 1               # At least 1 week with ≤1 book per brand in any 8-week window
```

### 14.4 Metadata velocity gate

Check that metadata patterns (title template families, description frameworks, subtitle structures) are not concentrated in time:

```yaml
metadata_velocity:
  # Per brand, per week: max share of books using same title_template_family or description_framework.
  max_same_title_template_per_brand_per_week: 0.50
  max_same_description_framework_per_brand_per_week: 0.50
  # Per network, per week: max books with same title_template_family across all brands.
  max_same_title_template_network_per_week: 0.25
```

This extends the metadata diversity guidance in `CATALOG_ARCHITECTURE_AT_SCALE.md` §5 item 2 (title/description template similarity) from operational audit to enforceable gate.

### 14.5 Cross-wave sequence detection (fragmented series spam)

Platforms detect not just within-wave clustering but **cross-wave narrative sequences** — a progressive thematic arc spread across multiple waves that forms an implicit series without series labeling. Example: 8 books over 6 weeks on the same topic with escalating depth, all from the same brand, but never declared as a series. To a reviewer, this looks like a fragmented series designed to game recommendation algorithms.

```yaml
cross_wave_sequence_detection:
  # Max books forming a progressive arc on same topic + same persona in a rolling window.
  # "Progressive" = same topic AND pacing_model escalates (single_sitting → multi_day → extended_program)
  # OR transformation_speed escalates (immediate → gradual → long_arc).
  max_thematic_sequence_length: 4    # No more than 4 books in 6 weeks forming a progressive arc on same topic/persona
  window_weeks: 6
  enforcement: warn
  # If the sequence is an INTENTIONAL series (series_id present), exempt it — declared series are legitimate.
  exempt_if_series_id_present: true
```

Implementation: Checked in `check_wave_density.py` when experience fields and topic/persona are present. For each brand, scan the catalog window for books sharing topic + persona where pacing or transformation dimensions escalate in publication order. Exempt books with explicit `series_id`. WARN if sequence length exceeds cap — editorial can then either declare a series or redistribute.

### 14.6 AI disclosure gate

Amazon KDP requires disclosure of AI-generated content at the point of publishing each new book. At 1,200+ book scale, a single missed disclosure triggers account-level review — which is a higher-severity risk than any individual content or experience flag.

```yaml
ai_disclosure:
  # Every compiled plan must declare ai_disclosure_status before entering prepublish.
  required_field: ai_disclosure_status   # enum: disclosed | not_applicable | pending
  # FAIL if status is "pending" or missing at prepublish.
  enforcement: fail
  # WARN if status is "not_applicable" for any book generated by the pipeline (should be "disclosed").
  warn_if_not_applicable_and_pipeline_generated: true
```

Implementation: Checked in `run_prepublish_gates.py`. The field is set during planning (default: `disclosed` for pipeline-generated books) and must be confirmed before release. This elevates AI disclosure from an operational checklist to a hard gate.

### 14.7 Implementation

- **Cadence irregularity:** Checked by `generate_weekly_schedule.py` when building multi-week schedules. If the generated schedule violates CV or correlation thresholds, the scheduler must reshuffle (add variance, swap brand-days, insert quiet weeks).
- **Metadata velocity:** Checked in `check_wave_density.py` when `title_template_family` and `description_framework` fields are present on plans. Graceful degrade when absent.
- **Cross-wave sequence detection:** Checked in `check_wave_density.py` when experience fields and topic/persona are present. WARN only; exempt declared series.
- **AI disclosure:** Checked in `run_prepublish_gates.py`. Hard FAIL if `ai_disclosure_status` is missing or `pending`.

---

## 15. Novelty injection and feedback loop

### 15.1 Novelty injection

Controlling distribution prevents clustering. But passive diversity management trends toward a stable equilibrium where the system produces "safely different" content that still feels samey over time. Novelty injection forces **genuinely unfamiliar experience tuples** into every wave.

```yaml
novelty_injection:
  # "Rare" = experience tuple that appeared in <10% of books in last catalog_window_weeks.
  rare_threshold_pct: 10
  # Every wave must include at least N books with a rare experience tuple.
  min_rare_per_wave: 2
  # Enforcement: WARN (not FAIL) — this is a creative health signal, not a hard spam gate.
  enforcement: warn
```

When the planner builds a wave, it checks the catalog window for tuple frequency. If the candidate wave has fewer than `min_rare_per_wave` books with rare tuples, it WARNs editorial to consider swapping in less-common experience profiles.

This creates visible freshness in the catalog and generates algorithmic exploration signals (platforms reward novelty in recommendations).

### 15.2 Feedback loop (post-launch learned priors)

After the first 3 release waves, real platform outcome signals become available. Use them to recalibrate thresholds.

```yaml
feedback_loop:
  # Signals to track per book/wave (operational, not automated initially):
  signals:
    - review_removals           # Books removed or flagged by platform review
    - manual_review_rate        # % of wave that triggered manual platform review
    - rejection_rate            # % of submissions rejected
    - ctr_variance_by_brand     # Click-through rate variance across brands (low variance = same product)
    - read_through_by_experience # Read-through rate segmented by experience tuple

  # Threshold adjustment protocol:
  # After 3 waves: review signals. If any signal is elevated:
  #   1. Identify which experience dimension or combo correlated with the flag.
  #   2. Tighten that dimension's cap by 0.05 (or combo's max_share by 0.05).
  #   3. Re-run wave density on next wave with new thresholds.
  # If all signals are clean after 6 waves:
  #   1. Switch threshold_tier from "launch" to "established" (§4.2).
  #   2. Optionally loosen novelty_injection.enforcement to "info" (advisory only).

  # Long-term: weighted entropy slope detection.
  # Track rolling 8-week entropy (1 - HHI) per dimension.
  # If entropy slope is negative (diversity declining) for 3 consecutive windows → WARN editorial.
  entropy_slope_alert:
    window_weeks: 8
    consecutive_declining_windows: 3
    enforcement: warn
```

### 15.3 Diversity restoration protocol

When the entropy slope alert fires (§15.2), editorial needs a concrete response — not just a warning. Without a protocol, the alert gets ignored and diversity continues to decline.

**When entropy slope is negative for 3 consecutive windows:**

1. The next wave **must** include at least 2 books with experience tuples from the bottom 20% of historical frequency (the rarest combos). This is a hard requirement, not a suggestion.
2. The planner **must** annotate the wave plan with a written justification: "Diversity is declining because [seasonal focus / series completion / deliberate brand strategy]." If no justification is provided, the wave is held for editorial review.
3. The composite risk score threshold for "elevated" is **temporarily lowered by 0.05** for the affected brand, forcing earlier attention in the dashboard.
4. If entropy continues declining for a 4th consecutive window despite the protocol, escalate to **wave hold** (FAIL) until diversity is manually restored.

### 15.4 Natural variance (controlled imperfection)

A perfectly balanced, perfectly diverse release pattern is itself a synthetic signal. Real publishers are messy — they cluster sometimes, they have quiet weeks, they over-index on a hot topic. Perfect diversity looks like an algorithm.

```yaml
natural_variance:
  # Allow a small percentage of waves to slightly exceed soft caps (weekly_caps).
  # This prevents "too clean" distribution patterns.
  allow_minor_violation_rate: 0.05   # 5% of waves may exceed soft caps by up to 10%
  max_overshoot_pct: 0.10            # e.g. if cap is 0.40, allow up to 0.44 in 5% of waves
  # Does NOT apply to: network-level caps (§8), risky combo caps (§13), or FAIL thresholds.
  # Only applies to per-dimension weekly_caps in launch/established tiers.
  applies_to: weekly_caps_only
```

Implementation: When `check_wave_density.py` detects a soft cap violation within `max_overshoot_pct`, it checks the rolling violation rate. If <5% of recent waves have used this allowance, it downgrades FAIL to WARN. If ≥5% have already used it, it remains FAIL.

**Variance abuse guard:** To prevent teams from relying on the variance allowance as a crutch, no brand may use the variance allowance in more than 2 consecutive waves. If a brand triggers the variance allowance in a 3rd consecutive wave, it is treated as a FAIL regardless of the rolling rate. This prevents slow boundary-pushing where "just this once" becomes the norm.

```yaml
  # Abuse prevention: no brand may use variance more than N consecutive waves.
  max_consecutive_variance_uses_per_brand: 2
```

### 15.5 Implementation

- **Novelty injection:** Added to portfolio planner and checked in `check_wave_density.py` (WARN only).
- **Feedback loop:** Operational for the first 6 waves (manual threshold review). Automated entropy slope tracking added to drift dashboard. Full automation (auto-adjust thresholds) is a future extension, not MVP.
- **Diversity restoration protocol:** Enforced by wave check when entropy slope alert is active. Requires planner annotation.
- **Natural variance:** Implemented in `check_wave_density.py` soft-cap enforcement logic. Hard caps (network, risky combos) are never subject to variance.

---

## 16. Experience–metadata consistency check

Experience dimensions describe what the product *is*. Metadata (title, subtitle, description, cover) describes what the product *looks like*. If these diverge — e.g. a book with `perceived_positioning: deep_work` but a title that screams "Calm Your Anxiety in 5 Minutes!" — the experience layer is gaming its own gates.

### 16.1 Consistency rules

```yaml
experience_metadata_consistency:
  # Validate that perceived_positioning aligns with metadata surface signals.
  # Not a full NLP classifier — lightweight keyword/pattern check on title + description.
  rules:
    - positioning: quick_fix
      title_must_not_contain: ["master", "journey", "deep", "advanced", "year-long"]
      description_should_contain_one_of: ["fast", "quick", "now", "today", "minutes", "relief", "instant"]

    - positioning: deep_work
      title_must_not_contain: ["fast", "quick", "instant", "minutes", "easy"]
      description_should_contain_one_of: ["practice", "work", "commit", "discipline", "effort", "depth"]

    - positioning: spiritual_path
      title_must_not_contain: ["hack", "system", "framework", "productivity"]
      description_should_contain_one_of: ["path", "practice", "spirit", "sacred", "devotion", "tradition"]

  enforcement: warn   # Advisory — flags misalignment for editorial review, not a hard block
```

### 16.2 Pre-commit tuple validation

Before a wave is finalized, validate that assigned experience dimensions are internally consistent with historical patterns. This catches assignment drift — where planners unconsciously shift how they interpret the taxonomy.

```yaml
pre_commit_validation:
  # For each book in wave: check if reader_intent matches the most common intent
  # historically assigned to that topic. If it deviates, flag for review.
  check_intent_topic_consistency: true
  # Threshold: if <20% of historical books with this topic used this intent, flag.
  historical_minority_threshold_pct: 20
  enforcement: warn
  # Also check: if delivery_experience doesn't match any historical assignment for this engine_id.
  check_delivery_engine_consistency: true
```

Implementation: Checked at plan finalization (before wave submission). Queries similarity index for historical topic → intent and engine → delivery_experience distributions. WARN if the assignment is a historical outlier. This is the "garbage in" defense — ensuring the 7-field tuple reflects reality before it enters the gate system.

### 16.3 Implementation

- Checked at plan time (when title/description drafts exist) or at prepublish (when final metadata is available).
- WARN only — the planner may have good reasons for creative divergence. This is a sanity check, not a gate.
- Extends the metadata diversity audit in `CATALOG_ARCHITECTURE_AT_SCALE.md` §5 item 2.

---

## 17. Caveats (same stance as CATALOG_ARCHITECTURE_AT_SCALE.md)

- Experience dimensions and thresholds are **internal heuristics**, not confirmed platform policy.
- Do **not** claim that platforms use these exact categories or scoring.
- Use as **defensive design and audit triggers**, not as guaranteed compliance.
- "Lower risk if differentiation is real" — experience diversity makes differentiation real at the product level.
- Review and recalibrate thresholds after the first 3 release waves; initial values are informed estimates.
- The feedback loop (§15.2) is the mechanism for evolving thresholds over time — do not treat launch values as permanent.
- Risky combos (§13) should be updated quarterly as real platform enforcement patterns are observed.
- Brand-relative overrides (§7.2) must not be used to circumvent network-level caps (§8).
- Natural variance (§15.4) applies only to soft caps — hard caps (network, risky combos, AI disclosure) are never subject to variance allowances.

---

## 18. Future extensions (not in MVP)

These are real detection surfaces identified during review but deferred because they require infrastructure not yet in place.

**Semantic cluster cap (title embeddings).** Different experience tuples and different positioning can still produce titles with the same *semantic promise* (e.g. "Stop Overthinking Fast," "Calm Your Racing Thoughts Now," "Break Mental Loops Instantly" — different words, same meaning). At 5,000+ titles, platforms may cluster by embedding similarity. Future extension: embed title + subtitle at plan time, cluster via cosine similarity or k-means, cap cluster size per wave (e.g. `max_same_semantic_cluster_per_wave: 0.30`). Does not require full NLP — lightweight sentence embeddings (e.g. via local model or API call) are sufficient.

**Voice fingerprint variation.** Even with diverse experience tuples, if the prose tone, sentence cadence, and narrative rhythm are too similar across books (especially on audio platforms), the catalog can cluster by voice. Future extension: `min_distinct_voice_signatures_per_wave: 4` — where "voice signature" is derived from existing narrator/TTS voice IDs and optional prose style metrics. The video pipeline already has per-channel TTS isolation (§15 of VIDEO_PIPELINE_SPEC); extending this to book narrators is a natural step.

**Assignment override rate monitoring.** The §3.3 assignment guide is deterministic, but planners can override. If the override rate exceeds 10–15%, the defaults may need recalibration (topics shifted, new engines added). Track override rate in the drift dashboard; WARN if >15% of a wave's books had manual experience overrides.

---

## 19. Operational governance

This spec defines *what* the system checks. This section defines *who* operates it and *when* they act. Without operational governance, the feedback loop goes unreviewed, thresholds stagnate, and the system slowly drifts from the catalog reality.

### 19.1 Spam-response lead

Assign one person (or a small rotating team) as the **spam-response lead**. This role owns:

- Monthly review of feedback loop signals (§15.2): rejection rates, manual review rates, CTR variance, read-through by experience.
- Quarterly risky combo review (§13.4): update `risky_combos.yaml` based on wave data and platform feedback.
- Threshold ramp decision: when to switch from `launch` to `established` tier (§4.2).
- Diversity restoration protocol activation: when entropy slope alerts fire (§15.3), the lead decides whether the justification is acceptable or the wave should be held.
- Variance monitoring: review which brands are using the natural variance allowance and whether caps need adjustment.

This is not a full-time role. It's a 2–4 hour/month commitment that ensures the system stays calibrated.

### 19.2 Quarterly tuple audit

Every quarter, a senior editor reviews a random sample of 20 books from the most recent waves:

1. Read the book's assigned 7-field experience tuple.
2. Read the book's title, description, and first chapter.
3. Answer: "Does this tuple accurately describe the product I'm looking at?"
4. If >3 of 20 books have mismatched tuples, the assignment defaults (§4.1) need recalibration.

This catches drift that no automated check can see — where the *meaning* of a topic or engine has shifted but the taxonomy hasn't kept up. Document results in a brief audit log (date, sample size, mismatch count, action taken).

### 19.3 Override reason review

When planner override rate exceeds 15% of a wave's books (tracked in drift dashboard per §18):

1. Collect the override reasons (if logged) or interview the planner.
2. If overrides cluster on one dimension (e.g. 80% of overrides change `reader_intent`), that dimension's defaults for the affected topics are likely stale.
3. Update `experience_defaults.yaml` to reflect the new reality. This is a config change, not a spec change.

### 19.4 Governance cadence summary

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Feedback loop signal review | Monthly | Spam-response lead |
| Risky combo update | Quarterly | Spam-response lead |
| Tuple audit (20-book sample) | Quarterly | Senior editor |
| Override reason review | When override rate >15% | Spam-response lead + planner |
| Threshold tier ramp decision | After 3 clean waves | Spam-response lead |
| Entropy slope response | When alert fires | Spam-response lead (immediate) |
| Natural variance review | Monthly | Spam-response lead |
