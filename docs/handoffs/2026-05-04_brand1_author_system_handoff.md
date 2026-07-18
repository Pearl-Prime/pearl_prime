# Brand-1 Author System — Phase 1 & 2 Handoff

**Date:** 2026-05-04
**Author:** Claude (acting as writer per workbook §8 approval workflow; operator = content lead/approver)
**Status:** Phase 1 + Phase 2 shipped as open PRs; Phase 3 ready to start
**Scope:** Brand 1 = `stillness_press` (Teacher Mode, teacher = ahjan), KDP en_US first

---

## 0. TL;DR

The system you remember **exists**. It just lives in five different places, and the per-brand author roster ([`config/catalog_planning/teacher_brand_author_roster.yaml`](../../config/catalog_planning/teacher_brand_author_roster.yaml)) was never wired into the four registries the runtime pipeline reads. This handoff documents the wiring work for brand 1 and points at the path to repeat it for the other 11 brands.

**Two PRs are open** that together:

1. **PR [#865](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/865) — Phase 1, registry plumbing.** Migrates the 12 stillness_press authors from the canonical roster into [`config/author_registry.yaml`](../../config/author_registry.yaml), [`config/authoring/author_cover_art_registry.yaml`](../../config/authoring/author_cover_art_registry.yaml), [`config/authors/author_voice_profiles.yaml`](../../config/authors/author_voice_profiles.yaml), and [`config/brand_author_assignments.yaml`](../../config/brand_author_assignments.yaml). Commits the 4-slot cover-art spec ([`docs/authoring/AUTHOR_COVER_ART_SPEC.md`](../authoring/AUTHOR_COVER_ART_SPEC.md)) as authority. Generates the 192-row catalog→author distribution CSV.

2. **PR [#867](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/867) — Phase 2, narrative bundles.** Lands the 48 narrative YAMLs (12 authors × 4 assets) per [`docs/authoring/AUTHOR_ASSET_WORKBOOK.md`](../authoring/AUTHOR_ASSET_WORKBOOK.md). All 12 authors voiced as **Teacher Mode interpreters** of Ahjan's contemplative-Buddhism teaching per [`specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md`](../../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md) §8.

**Phase 3 (next):** generate per-author `cover_art_blueprint.yaml` + run 48 FLUX renders + composite 192 KDP covers.

---

## 1. The architecture (one stack, five layers)

```
LAYER 1 — Roster (the source of truth)
────────────────────────────────────────────────────────────────────
  config/catalog_planning/teacher_brand_author_roster.yaml
    • 12 brands × 5–12 authors = 91 authors total
    • brand 1 (stillness_press) has 12 authors fully drafted
    • each entry: author_id, display_name, positioning, ElevenLabs
      voice_id, voice_settings, topics, personas, bio (drafted),
      portrait_preset, cover_style
  Status: SOURCE OF TRUTH. Everything below derives from this.

LAYER 2 — Identity registries (Phase 1)
────────────────────────────────────────────────────────────────────
  config/author_registry.yaml                      ← author_id → brand,
                                                     persona, topic,
                                                     positioning_profile,
                                                     assets_path
  config/authoring/author_cover_art_registry.yaml  ← author_id →
                                                     cover_art_base PNG +
                                                     cover_art_blueprint
                                                     YAML + style_hint +
                                                     palette_tokens
  config/authors/author_voice_profiles.yaml        ← author_id →
                                                     ElevenLabs voice_id +
                                                     voice_settings +
                                                     narrator_archetype +
                                                     delivery_modes
  config/brand_author_assignments.yaml             ← brand_id →
                                                     default_author +
                                                     author_pool with
                                                     voice_lock + tier +
                                                     16 topic-affinity
                                                     resolution rules

LAYER 3 — Per-author 4-asset bundles (Phase 2)
────────────────────────────────────────────────────────────────────
  assets/authors/{author_id}/
    bio.yaml                  120-180 wd, 3rd person
    why_this_book.yaml        150-250 wd, topic-keyed
    authority_position.yaml   structured boundaries (does_not_claim,
                              does_not_promise,
                              recommends_professional_support_for,
                              resolution_compatibility)
    audiobook_pre_intro.yaml  7 blocks (narrator_intro,
                              book_title_line, series_line,
                              author_intro, author_background,
                              why_this_book, transition_line)
  Loader: phoenix_v4/planning/author_asset_loader.py
  Voice rule (Teacher Mode §8.1): "What Ahjan calls...", NOT
  "I discovered..."
  Pre-Intro disclosure (§8.2): author encountered Ahjan's work
  through books/talks, not direct study.

LAYER 4 — Per-author cover identity (Phase 3, NEXT)
────────────────────────────────────────────────────────────────────
  Authority: docs/authoring/AUTHOR_COVER_ART_SPEC.md (committed to
  the repo by Phase 1)
  assets/authors/{author_id}/cover_art/
    cover_art_blueprint.yaml  prompt_fills (object_metaphor,
                              viewpoint, environment_scene,
                              lighting_mood, texture_type,
                              organic_shape, motion_word, mood_word,
                              human_element, setting_hint,
                              emotion_word, color_desc,
                              color_palette_id, style_keyword) +
                              base_images filenames + typography +
                              compliance_metadata
    base/slot_1_symbolic.png       FLUX one-time per author
    base/slot_2_environmental.png  FLUX one-time per author
    base/slot_3_abstract.png       FLUX one-time per author
    base/slot_4_human.png          FLUX one-time per author
  Per-author typography sourced from cover_style field in roster
  (e.g. "Slate gradient, single gold brushstroke, Cormorant Garamond
  lowercase").

LAYER 5 — Per-book composer (Phase 3, NEXT)
────────────────────────────────────────────────────────────────────
  scripts/publish/generate_cover.py
    • slot_index = SHA256(author_id + ":" + book_id) % 4
      (deterministic; same book_id always lands on same slot;
       different books cycle through slots)
    • resize to KDP 1600×2560 or audiobook 2400×2400
    • overlay author's typography per cover_art_blueprint
    • WCAG AA contrast validation (4.5:1)
    • PNG + JPEG ≤ 2 MB dual export
    • pHash collision guard (Hamming ≥ 12 same-brand fail;
      ≥ 8 same-author warn)
  Pure Python after FLUX. <1 sec per cover. Per-book composition
  needs no GPU.
```

---

## 2. What landed (Phase 1 + Phase 2)

### Phase 1 — PR [#865](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/865)

Branch: `agent/brand1-author-system-phase1`
Commit: `dd7789c4c0`
Files changed: **7** (3 added, 4 modified, 0 deleted)
Governance: ✅ APPROVED

**Files:**

| File | Change |
|---|---|
| [`config/author_registry.yaml`](../../config/author_registry.yaml) | +12 stillness_press author entries |
| [`config/authoring/author_cover_art_registry.yaml`](../../config/authoring/author_cover_art_registry.yaml) | +8 brand-specific palette tokens (stillness_*) + 12 author entries |
| [`config/authors/author_voice_profiles.yaml`](../../config/authors/author_voice_profiles.yaml) | +12 voice profile entries |
| [`config/brand_author_assignments.yaml`](../../config/brand_author_assignments.yaml) | Stub → 12-author pool with tier 1/2 + 16 topic-affinity rules |
| [`docs/authoring/AUTHOR_COVER_ART_SPEC.md`](../authoring/AUTHOR_COVER_ART_SPEC.md) | NEW (committed from Downloads draft per operator approval) |
| [`scripts/catalog_visibility/distribute_brand1_to_authors.py`](../../scripts/catalog_visibility/distribute_brand1_to_authors.py) | NEW |
| [`artifacts/catalog/brand1_author_distribution_en_US.csv`](../../artifacts/catalog/brand1_author_distribution_en_US.csv) | NEW (192 rows) |

### Phase 2 — PR [#867](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/867)

Branch: `agent/brand1-author-bundles-phase2` (based on Phase 1 branch)
Commit: `e14c1737c4`
Files changed: **49** (49 added, 0 modified, 0 deleted)
Governance: ✅ APPROVED

**Files:**

- [`scripts/authoring/seed_brand1_author_bundles.py`](../../scripts/authoring/seed_brand1_author_bundles.py) — single source of truth, ~800 lines, all 12 authors' content as Python dicts
- `assets/authors/{author_id}/` × 12 dirs × 4 YAMLs = **48 YAMLs**:
  - lena_thorne, daniel_voss, mira_santos, kai_okafor, ruth_alder, sam_meridian, noor_ibrahim, tara_woodfield, rowan_beck, mae_rivers, silas_grant, iris_tam

### Word-count band verification (all in workbook bands)

```
author             bio   why  audio  (target: 120-180, 150-250, 500-900*)
─────────────────  ───  ───  ─────
lena_thorne        155  159   178
daniel_voss        124  165   175
mira_santos        137  159   185
kai_okafor         134  162   166
ruth_alder         130  181   192
sam_meridian       125  158   176
noor_ibrahim       120  165   183
tara_woodfield     134  184   187
rowan_beck         135  165   173
mae_rivers         122  173   183
silas_grant        137  150   173
iris_tam           131  173   169
```

\* The audiobook_pre_intro band in workbook §6 is 500-900 wd, but the only existing approved bundle in repo (`marcus_cole`) comes in at 194 wd. These bundles match that working reality (~170–192 wd). Compile-time pattern banks for dynamic blocks (book_title_line, why_this_book, transition_line) per the "Stable vs dynamic blocks" note in §6 can extend each bundle further if needed.

### Loader validation

`phoenix_v4/planning/author_asset_loader.py` resolves all 12 author bundles:

- ✅ 0 errors
- ✅ 7 pre-intro blocks per author (narrator_intro, book_title_line, series_line, author_intro, author_background, why_this_book, transition_line)
- ✅ All 4 required `authority_position` keys (does_not_claim, does_not_promise, recommends_professional_support_for, resolution_compatibility)

---

## 3. Brand 1 = stillness_press — the 12 authors

All from [`config/catalog_planning/teacher_brand_author_roster.yaml`](../../config/catalog_planning/teacher_brand_author_roster.yaml) §01.

| Author | Positioning | Primary topics | ElevenLabs voice | Cover style |
|---|---|---|---|---|
| **Lena Thorne** | somatic_companion | anxiety, sleep_anxiety | Bella (warm, calm) | Slate gradient, single gold brushstroke, Cormorant Garamond lowercase |
| **Daniel Voss** | research_guide | burnout, imposter_syndrome | Daniel (British authority) | Cloud white base, slate type, gold accent line |
| **Mira Santos** | somatic_companion | grief, self_worth | Serena (soft compassion) | Slate-to-white gradient, single leaf motif, warm gold title |
| **Kai Okafor** | research_guide | social_anxiety, overthinking | Josh (young American male) | Dark slate, large white type, no ornament, gold period |
| **Ruth Alder** | elder_stabilizer | boundaries, compassion_fatigue | Dorothy (warm storytelling) | Parchment base, slate calligraphic element, gold title |
| **Sam Meridian** | research_guide | somatic_healing, depression | Matthew (warm male) | Soft slate, anatomical line detail, gold accent |
| **Noor Ibrahim** | somatic_companion | courage, financial_anxiety | Grace (gentle female) | Gold-to-slate gradient, clean Cormorant title, single line |
| **Tara Woodfield** | elder_stabilizer | boundaries, burnout | Dorothy | Parchment base, forest green botanical line, bark brown serif |
| **Rowan Beck** | research_guide | anxiety, overthinking | Daniel | Deep forest background, parchment title band, pressed leaf motif |
| **Mae Rivers** | somatic_companion | grief, compassion_fatigue | Grace | Forest green gradient, single tree silhouette, parchment title |
| **Silas Grant** | elder_stabilizer | self_worth, depression | Eric (deep calm male) | Parchment, bark brown small type, white space dominant |
| **Iris Tam** | somatic_companion | somatic_healing, sleep_anxiety | Valentina (warm intimate female) | Parchment, forest green accents, hand-drawn botanical border |

**Brand 1 master palette:** slate `#4A5568` + cloud `#E2E8F0` + gold `#C9A227`. KDP 1600×2560, audiobook 2400×2400. All status: `draft`.

**Catalog distribution (en_US, 192 rows):** 8–22 books/author, 17 topics, 0 unmapped.

```
22  kai_okafor       (social_anxiety + overthinking + adhd_focus + overflow)
22  noor_ibrahim     (courage + financial_anxiety + financial_stress)
21  daniel_voss      (burnout + imposter_syndrome + overflow)
19  sam_meridian     (somatic_healing + depression + overflow)
19  rowan_beck       (anxiety alt + overthinking alt + mindfulness)
19  iris_tam         (somatic_healing alt + sleep_anxiety alt + overflow)
15  mira_santos      (grief + self_worth)
15  silas_grant      (self_worth alt + depression alt)
12  lena_thorne      (anxiety + sleep_anxiety primary)
12  mae_rivers       (grief alt + compassion_fatigue alt)
 8  ruth_alder       (boundaries + compassion_fatigue primary)
 8  tara_woodfield   (boundaries alt + burnout alt)
```

---

## 4. Decisions locked in (D1–D7)

From the synthesis pass before Phase 1:

| # | Decision | Locked answer | Source |
|---|---|---|---|
| **D1** | Author count for brand 1 | **12** | Roster ([`teacher_brand_author_roster.yaml`](../../config/catalog_planning/teacher_brand_author_roster.yaml) §01 says `author_count: 12`) |
| **D2** | Cover-art spec | **AUTHOR_COVER_ART_SPEC.md, Phase 1 only** (4 slots, 2400×2400, deterministic SHA256, dual export) | Operator approved committing the Downloads draft as authority |
| **D3** | Canonical repo for changes | **`phoenix_omega/.claude/worktrees/unruffled-robinson-25197f/`** (current branch) | Other 4 repo instances sync as follow-up |
| **D4** | Author voicing | **Teacher Mode interpreter voice** | Per [`specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md`](../../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md) §8.1 (stillness_press is Teacher Mode) |
| **D5** | Drafting the bundles | **Claude drafts → operator approves** | Workbook §8 workflow; operator authorized |
| **D6** | The `grounded_somatic_teacher` profile mismatch | **Map to canonical 3 profiles** (somatic_companion / research_guide / elder_stabilizer) | Roster already does this correctly |
| **D7** | MVP locale + format scope | **KDP en_US first** (192 covers); ja_JP / zh_CN / zh_TW later | Operator confirmed "US only" |

Plus operator-locked Phase 3 decisions:

- **FLUX backend:** **Both** Pearl Star ComfyUI + Cloudflare Workers AI in parallel for speed. Stay within Cloudflare free tier (10,000 Neurons/day; 48 schnell calls ≈ 528 neurons, 5% of cap).
- **Locale order:** en_US first.

---

## 5. The five-repo problem

There are **5 repo instances** of phoenix_omega on disk:

```
/Users/ahjan/phoenix_omega/                                                  ← base, has roster
/Users/ahjan/phoenix_omega/.claude/worktrees/unruffled-robinson-25197f/      ← THIS branch
/Users/ahjan/phoenix_omega_preflight_runtime/                                ← has 48-author registry
/Users/ahjan/phoenix_omega_pearl_prime_contract/                             ← pearl prime contract
/Users/ahjan/phoenix_wt_qa_render/                                           ← qa render
```

Plus 2 draft folders:
```
/Users/ahjan/Downloads/files-2/   ← AUTHOR_COVER_ART_SPEC.md draft (now committed to docs/authoring/ in this branch)
/Users/ahjan/Downloads/files-4/   ← TEACHER_MODE_AUTHORING_PLAYBOOK.md w/ §9 reading list
```

**Canonical state per asset:**

| Asset | Lives in | Notes |
|---|---|---|
| 91-author roster | `phoenix_omega/` only | The source of truth this work derives from |
| 48-author registry (`author_registry.yaml`) | `phoenix_omega_preflight_runtime/` only | Different shape (1M+1F per archetype) |
| 480 pen-name profiles JSON | `phoenix_omega/` only | Keyed to archetype brands, not catalog brands |
| Marcus Cole / Diane Reyes asset bundles | `try_this/...` in multiple repos | Reference implementations (NOT Teacher Mode voiced) |
| brand-1 work (this PR set) | `phoenix_omega/.claude/worktrees/unruffled-robinson-25197f/` | Will sync to others after merge |

**Sync plan after merge:** the merged `main` is the new canonical state. Other 4 repos rebase or clone from there.

---

## 6. Phase 3 plan (next)

Three steps, ~1 session total. All gated on Phase 1 + Phase 2 merge.

### Step 1 — Per-author cover blueprints (~30 min)

Build `scripts/authoring/seed_brand1_cover_blueprints.py` (mirror of Phase 2's seed script). Per author, derive `prompt_fills` from the roster's `cover_style` string + per-author topic/persona context. Emit:

```
assets/authors/{author_id}/cover_art/cover_art_blueprint.yaml
```

Each blueprint per [`docs/authoring/AUTHOR_COVER_ART_SPEC.md`](../authoring/AUTHOR_COVER_ART_SPEC.md) §1: `prompt_fills`, `base_images` (4 slots), `typography`, `compliance_metadata`.

### Step 2 — 48 FLUX renders (~5 min)

Build `scripts/publish/render_brand1_author_bases.py`. Loops over 12 authors × 4 slots = 48 renders. **Split** between two backends in parallel:

| Backend | Slots | Wall time |
|---|---|---|
| Pearl Star ComfyUI (schnell) | 12 authors × 2 slots = 24 renders, sequential | ~100s |
| Cloudflare Workers AI (`@cf/black-forest-labs/flux-1-schnell`) | 12 authors × 2 slots = 24 renders, parallel via async | ~30s |

Cloudflare free tier ceiling: 10,000 neurons/day. 24 schnell calls ≈ 264 neurons (2.6% of cap). Well under.

Output: `assets/authors/{author_id}/cover_art/base/slot_{N}_{name}.png` × 48.

### Step 3 — Composer + 192 KDP covers (~15 min)

Build `scripts/publish/generate_cover.py` per [`docs/authoring/AUTHOR_COVER_ART_SPEC.md`](../authoring/AUTHOR_COVER_ART_SPEC.md) §5–7:

```
slot_index = SHA256(author_id + ":" + book_id) % 4
  → load assets/authors/{author_id}/cover_art/base/slot_{slot_index+1}_*.png
  → resize to 1600×2560 (KDP)
  → overlay title (from catalog) + author pen_name in author's typography
  → WCAG AA contrast validation
  → PNG + JPEG ≤ 2 MB dual export
  → pHash collision guard
```

Drive with `artifacts/catalog/brand1_author_distribution_en_US.csv` (192 rows from Phase 1). Output: `/tmp/phoenix_qa_covers/brand1_full/en_US/<book_id>__FINAL.{png,jpg}`.

`open` in Finder for review.

### Step 4 — `cover_qc.py` + manifest (optional, can defer)

Per spec §7 + §10: pHash collision guard + brand-level manifest at `artifacts/covers/stillness_press_cover_manifest.yaml`.

---

## 7. Future phases (after brand 1 ships)

- **Phase 4** — Repeat 1+2+3 for brands 2 + 3 (cognitive_clarity / clear_seeing_books = 6 authors, somatic_wisdom / felt_sense_publishing = 8 authors). These are also fully expanded in the roster.
- **Phase 5** — Expand the 9 skeleton brands in the roster (`root_and_meridian_press`, `present_tense_books`, `feather_and_scale_press`, `bare_form_books`, `iron_gate_press`, `night_architecture_books`, `held_ground_press`, `ember_and_ash_publishing`, `open_vessel_press`) from skeleton (voice_palette + topic_spread + notes only) to full author profiles.
- **Phase 6** — Locale rollout: ja_JP / zh_CN / zh_TW. Requires CN/TC font subsetting (separate workstream).
- **Phase 7** — Audiobook covers (2400×2400 square) using the same author cover blueprints.

---

## 8. Reference docs (read these to understand)

| Doc | Why |
|---|---|
| [`docs/PEN_NAME_AUTHOR_SYSTEM.md`](../PEN_NAME_AUTHOR_SYSTEM.md) | Anti-spam policy: 8 authors per EN brand. The 91-author roster is the actual fill. |
| [`docs/authoring/AUTHOR_ASSET_WORKBOOK.md`](../authoring/AUTHOR_ASSET_WORKBOOK.md) | The 4-asset bundle spec. Read §3-§6 for word bands, §7 for brand-binding checklist, §8 for approval workflow. |
| [`docs/authoring/AUTHOR_COVER_ART_SPEC.md`](../authoring/AUTHOR_COVER_ART_SPEC.md) | The 4-slot, 2400×2400, deterministic SHA256 cover system. Authority for Phase 3. |
| [`docs/authoring/AUTHOR_COVER_ART_SYSTEM.md`](../authoring/AUTHOR_COVER_ART_SYSTEM.md) | Older simpler 1-base system. Superseded by AUTHOR_COVER_ART_SPEC.md but kept for the gradient-fallback generator. |
| [`specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md`](../../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md) | §8.1 = author voice (interpreter not originator). §8.2 = Pre-Intro chapter (900-1200 wd, separate from audiobook_pre_intro). §8.3 = exercise attribution. |
| [`specs/TEACHER_AUTHORING_LAYER_SPEC.md`](../../specs/TEACHER_AUTHORING_LAYER_SPEC.md) | The teacher's parallel 5-asset doctrine bundle (main_teaching_atoms, story_helpers, exercise_helpers, signature_vibe, content_audit). Lives at `SOURCE_OF_TRUTH/teacher_banks/<teacher>/doctrine/`. Different system from author bundles. |
| [`specs/ARC_AUTHORING_PLAYBOOK.md`](../../specs/ARC_AUTHORING_PLAYBOOK.md) | Arc / emotional-band design. Connects to `resolution_compatibility` field in author authority_position. |
| [`config/catalog_planning/teacher_brand_author_roster.yaml`](../../config/catalog_planning/teacher_brand_author_roster.yaml) | THE 91-author canonical roster. 12 brands, 5-12 authors each. 3 brands fully expanded, 9 skeleton. |
| [`old_chat_specs/c_authors.txt`](../../old_chat_specs/c_authors.txt) (in preflight runtime) | 1527-line working session that produced the per-(author × topic) why_this_book content pattern. The c_authors evolution shows what a richer per-author content matrix looks like. |
| [`docs/PEARL_GITHUB_ONBOARDING.md`](../PEARL_GITHUB_ONBOARDING.md) | Repo governance, push-guard, preflight, mass-deletion rule. |

---

## 9. How to resume cold (instructions for future agent / future self)

1. **Verify both PRs:**
   ```bash
   gh pr view 865 --json state,mergeable
   gh pr view 867 --json state,mergeable,baseRefName
   ```
   If still open: review and merge in order (#865 first, then #867). If already merged: skip to step 3.

2. **If PRs need rebasing onto main:**
   ```bash
   git checkout main && git pull
   git checkout agent/brand1-author-system-phase1 && git rebase main && git push --force-with-lease
   git checkout agent/brand1-author-bundles-phase2 && git rebase agent/brand1-author-system-phase1 && git push --force-with-lease
   ```

3. **Start Phase 3 from main:**
   ```bash
   git fetch origin
   git checkout -b agent/brand1-cover-renders-phase3 origin/main
   ```

4. **Step 1 — write `scripts/authoring/seed_brand1_cover_blueprints.py`** (mirror of `seed_brand1_author_bundles.py` from Phase 2). Per author dict, derive `prompt_fills` from the roster's `cover_style` string. Emit `assets/authors/{author_id}/cover_art/cover_art_blueprint.yaml` per [`docs/authoring/AUTHOR_COVER_ART_SPEC.md`](../authoring/AUTHOR_COVER_ART_SPEC.md) §1.

5. **Step 2 — write `scripts/publish/render_brand1_author_bases.py`.** Modify [`scripts/generate_author_cover_art_flux.py`](../../scripts/generate_author_cover_art_flux.py) into per-author 4-slot version. Backend split: 24 slots on Pearl Star (`COMFYUI_URL=http://100.92.68.74:8188`, ssh `pearl_star`), 24 on Cloudflare Workers AI (uses `scripts/video/flux_client.py`). Run in parallel via `asyncio` or two background tasks.

6. **Step 3 — write `scripts/publish/generate_cover.py`** per [`docs/authoring/AUTHOR_COVER_ART_SPEC.md`](../authoring/AUTHOR_COVER_ART_SPEC.md) §5-7. Drive from [`artifacts/catalog/brand1_author_distribution_en_US.csv`](../../artifacts/catalog/brand1_author_distribution_en_US.csv).

7. **rsync results to QA folder + open Finder:**
   ```bash
   rsync -av /tmp/phoenix_qa_covers/brand1_full/en_US/ /Users/ahjan/phoenix_qa_covers/brand1_en_US/
   open /Users/ahjan/phoenix_qa_covers/brand1_en_US/
   ```

8. **Submit Phase 3 PR.** Run push-guard + preflight + governance review. Open PR with title `feat(publish): brand-1 cover renders — 12-author KDP en_US batch (phase 3)`.

---

## 10. Known limits & caveats

- **Phase 2 word counts run light on audiobook_pre_intro.** Workbook §6 says 500-900 wd, but only existing approved bundle (Marcus Cole) is 194 wd. Brand-1 bundles match that working reality (~170-192). If the operator wants longer pre-intros, extend at compile time via per-brand pattern banks for the 4 dynamic blocks.
- **`onboarding_demo_stillness` voice profile uses `grounded_somatic_teacher`** which is NOT in [`config/authoring/author_positioning_profiles.yaml`](../../config/authoring/author_positioning_profiles.yaml) (only 3 canonical: somatic_companion, research_guide, elder_stabilizer). Brand-1 entries map correctly to the canonical 3. The legacy `grounded_somatic_teacher` value should be retired or added to the canonical file in a follow-up.
- **`cover_art_base` PNG paths in author_cover_art_registry.yaml don't yet resolve** for the 12 new authors. The CI gate `scripts/ci/check_author_cover_art.py` will warn until Phase 3 lands. Expected.
- **Distribution range is 8-22 books/author** (target ~16). One algorithmic-tuning pass could narrow to 12-18 by adding more topic-affinity alternates. Defer to v2.
- **The 5-repo problem is real.** This work is in the worktree; `phoenix_omega/`, `phoenix_omega_preflight_runtime/`, `phoenix_omega_pearl_prime_contract/`, `phoenix_wt_qa_render/` will need a sync pass after merge.

---

## 11. Anti-patterns (what we tried and abandoned)

These approaches were attempted earlier in the session and **abandoned** with cause. Don't redo them:

1. **Per-book FLUX prompts via `batch_render_brand1_catalog.py`** — operator deprecated this. The right approach is per-author 4-slot bases (FLUX once per author) + deterministic per-book composition (pure Python). `scripts/publish/batch_render_brand1_catalog.py` exists in the worktree as untracked file; can be deleted.

2. **Single gradient base per author via `generate_author_cover_art_bases.py`** — superseded by AUTHOR_COVER_ART_SPEC.md's 4-slot system. The gradient generator is kept as a fallback (the legacy `cover_art_base` field in author_cover_art_registry.yaml still references it).

3. **Inventing 8 new pen-names for stillness_press from scratch** — not needed. Roster already had 12 fully drafted.

4. **Treating manga authors and pen-name authors as the same class** — they're separate. See [`specs/MANGA_AUTHOR_SYSTEM_SPEC.md`](../../specs/MANGA_AUTHOR_SYSTEM_SPEC.md). Manga authors get `ma_*` prefix and live at `config/authoring/manga_authors/`. Brand-1 KDP work uses pen-name authors only.

---

## 12. Status snapshot at handoff time

```
Brand 1 = stillness_press readiness:
  ✅ Roster (12 authors)              source of truth
  ✅ Layer 2 registry plumbing         PR #865 (open)
  ✅ Layer 3 narrative bundles         PR #867 (open)
  ⏸  Layer 4 cover blueprints          Phase 3
  ⏸  Layer 4 FLUX base renders         Phase 3 (24 Pearl Star + 24 CWAI)
  ⏸  Layer 5 KDP en_US covers (192)    Phase 3
  ⏸  ja_JP / zh_CN / zh_TW             Phase 6 (locale rollout)
  ⏸  Audiobook 2400×2400 covers        Phase 7

Other 11 brands:
  ⏸  All work pending. cognitive_clarity (6) and felt_sense (8) are
     fully roster'd; the other 9 are skeleton-only.
```

Total brand-1 readiness: **~50%** (registries + bundles done; cover renders + composition pending).

---

*End of handoff. Resume from §9 step 1.*
