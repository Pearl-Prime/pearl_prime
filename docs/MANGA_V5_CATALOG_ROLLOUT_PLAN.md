# Manga V5.1 Catalog Rollout Plan

**Status:** PLAN (operator-reviewable; pre-execution)
**Author:** Pearl_PM + Pearl_Architect
**Date:** 2026-05-22
**Decision context:** Operator question (2026-05-22): *"do we have all the plans to do this for all the genres and styles?"* Honest answer: **no — V5.1 architecture proven on 1 series; ~364 series unauthored to V5.1 dispatch readiness.** This doc inventories the gap + proposes ordered milestones.

---

## 1. Reference targets

- **Operator memory target:** ~800 high-confidence catalog configurations (`artifacts/research/full_content_audit.md:65`) — brand × topic × primary persona × proven format × top 5 locales. These drive 80% of catalog value.
- **Manga catalog scope:** Per `config/manga/manga_brand_series_plan.yaml` — 13 brands declared, 41 active-series target, 53 new-series-per-year capacity, 2.8 chapters/series/month avg.
- **Profile inventory:** 365 series profile files exist on disk in `config/source_of_truth/manga_profiles/`.
- **Genre taxonomy:** 26 canonical genres declared in `config/manga/drawing_tradition_per_genre.yaml`.

The gap between "365 series profiles exist" and "365 series can render via V5.1" is the subject of this plan.

---

## 2. What we have (proven)

### 2.1 Architecture
- **V5.1 2-stage pipeline** validated end-to-end on stillness_press__ahjan__en_US__anxiety series ep_001
  - Stage 1: base Qwen-Image render (preserves V3.1/V4 painterly style + character consistency)
  - Stage 2: Qwen-Image-Layered Image-to-Layers decompose → 3 RGBA outputs (composite + background + alpha-cut subject)
  - Empirical: 10.32 GB peak VRAM on RTX 5070 Ti 16 GB; ~25 min per panel; validator PASS on V4 class-A gates
  - Authority: `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` v1.1.0 (PR #1276)
  - Operator approval (2026-05-21): "layer_00 perfect, layer_02 perfect, layer_01 has soft outline of subject (acceptable forensic artifact)"

### 2.2 Infrastructure
- **Pearl Star ComfyUI** with Qwen-Image-Layered fp8mixed (20.5 GB), text encoder, VAE all on disk + warm
- **Parallel HF downloader** productionized at `scripts/utils/parallel_hf_download.py` (PR #1271) — 49 KB/s WAN → 12.9 MB/s aggregate via 16-thread byte-range chunks
- **V5 orchestrator** at `scripts/manga/render_v5_episode.py` (V5.0 path) + V5.1 driver pattern at `/tmp/v51_pearlstar_dispatch.py` (Pearl-Star-side, self-contained, no Phoenix-repo deps)
- **Per-series telemetry** (panel-level dispatch time, VRAM peak, cache key, layer count, validation result)
- **Phase 1 ToonOut** cutout_engine extension shipped (PR #1262 + #1268) — interim V4.x cutout improvement path if V5 fails on a specific series

### 2.3 Content (single-series)
- `stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying`: full ep_001 continuity_state authored (35 panel YAMLs), V3.1 panels for ep_001–ep_010 already rendered at `panels_v3_qwen/` (used as stage-1 inputs for V5.1)

---

## 3. The gap — what's missing for 364 other series

| Asset | Authored | Missing | Authoring cost per unit |
|---|---|---|---|
| **Panel templates** (`config/manga/panel_templates/<genre>.yaml`) | 1 of 26 genres (iyashikei) | **25 genres** | ~3-5 days authoring + iteration each; analog to `artifacts/research/manga_quality_bar/01_iyashikei_craft_study.md` |
| **Per-series style states** (`<series>.style_state.yaml`) | 1 of 365 series | **364 series** | ~20-60 min each if generalizing per-genre defaults; ~4-8h if bespoke per series |
| **Continuity state YAMLs** (per-panel per-episode) | 35 panels (1 series × 1 episode) | **~127,000 panel YAMLs** (assuming 35 panels × 10 episodes × 365 series) | ~10-30 min per panel if manual = infeasible at scale. **Requires generator tooling.** |
| **Stage-1 source renders** (base Qwen-Image panels) | ~350 panels (1 series × 10 episodes via V3.1) | thousands | ~25 min compute per panel on Pearl Star fp8 |
| **Per-genre LoRA decisions** | 4 of 26 genres (April audit: mecha, dark_fantasy, fantasy_adventure, healing) | **22 genres** | Pearl_Research scout per genre (~1-2 days each) + smoke test (~1h compute) |
| **Per-genre §11 acceptance criteria** | 1 genre (iyashikei via V5 spec §11) | **25 genres** | Operator-tier — what counts as "shippable mecha panel" vs "shippable romance panel" |
| **Per-locale aesthetic deltas** | en_US default | ja_JP / ko_KR / zh_TW / zh_CN / fr_FR / de_DE overrides probably needed | Per-locale style_state override file |

### 3.1 Catalog distribution (where the 365 series actually live)

Top-10 by genre (from `subgenre` field in profiles):
| Series | Genre | Panel template? | Continuity state? |
|---|---|---|---|
| 77 | slice_of_life | ❌ | ❌ |
| 63 | healing | ✓ (1 series) | ✓ (1 series × 1 episode) |
| 41 | workplace | ❌ | ❌ |
| 33 | supernatural_everyday | ❌ | ❌ |
| 18 | sports | ❌ | ❌ |
| 15 | mystery | ❌ | ❌ |
| 10 | fantasy | ❌ | ❌ |
| 9 | school | ❌ | ❌ |
| 8 | romance | ❌ | ❌ |
| 6 | thriller | ❌ | ❌ |

Locales declared in profiles: 1 en_US, 18 ja_JP, 3 ko_KR, **343 "unknown"** (most profiles don't declare a locale; the registry knows from brand). Per the 800-config target, top-5 locales are en-US, de-DE, ja-JP, ko-KR, fr-FR.

### 3.2 Critical path: continuity_state generator

**127,000 panel YAMLs manually authored is infeasible.** The 35 YAMLs that exist for ep_001 took multiple sessions of manual operator + agent authoring per `artifacts/manga/.../continuity_state/ep_001/ep001_*.yaml`. Estimated 30 min per panel = 63,500 person-hours to author the full catalog by hand. That's ~30 person-years of authoring.

**Continuity_state must be GENERATED from higher-level beatsheets**, not authored panel-by-panel. The generator inputs a series_profile + chapter_intent + character_design + episode_structure and emits the 35 continuity_state YAMLs per episode automatically. Operator + Pearl_Author iterate the beatsheet, not the panel YAMLs.

This generator is the **non-negotiable prerequisite** for scale beyond 5-10 series.

---

## 4. Ordered milestones

Milestones are gated — each completes before the next starts. Compute on Pearl Star is sequential (one ComfyUI dispatch at a time on the single RTX 5070 Ti).

### Milestone A — Prove V5.1 at single-series scale (in flight now)

**Scope:** Finish stillness_press__ahjan__en_US ep_001 V5.1 re-render (in flight, 18/35 remaining on Pearl Star, ~7-8h). Operator §11 acceptance review.

**Exit criteria:**
- All 35 V5.1 composites in `composed_v51_qwen/ep_001/`
- Operator §11 verdict: ≥31/35 shippable + ≥30/35 visually better than V4 baseline
- Validator class-A gates green on all 35
- Run summary committed; failure analysis if <31/35

**Cost:** ~8h compute (no new authoring; V3.1 inputs + ep_001 continuity_state already exist)

**Owner:** dispatch driver running autonomously on Pearl Star; operator review at completion

### Milestone B — Prove V5.1 at episode-series scale (same genre, same series)

**Scope:** V5.1 re-render of ep_002–ep_010 of the same series (~350 more composites, all-on-Pearl-Star). Operator review confirms identity consistency holds across 10 episodes + character continuity is visible.

**Prerequisite:** Milestone A acceptance verdict ≥31/35.

**Exit criteria:**
- All 350 V5.1 composites rendered
- Cross-episode identity consistency check: same Mira across all 10 episodes (operator visual; programmatic `qa_face_distance.py` ≤ 0.55 cosine on 95% of L2 panels)
- Style consistency: no visible drift between ep_001 and ep_010
- Series-level operator approval to ship as stillness_press__ahjan__en_US__anxiety v1.0

**Cost:** ~75h Pearl Star compute (9 episodes × 35 panels × ~25 min) + ~4h operator review

**Owner:** dispatch driver (extended from ep_001), no new authoring required (continuity_state for ep_002-010 needs authoring — see prerequisite below)

**Hidden cost:** **Continuity state for ep_002-010 of this series is NOT YET AUTHORED.** Even though V3.1 panels exist, the V5.1 dispatch needs per-panel continuity_state YAMLs that we don't have for ep_002+. Either (a) author them manually (10 episodes × 35 panels × 30 min = ~175h person-time), or (b) build the generator (Milestone C) first.

### Milestone C — Build the continuity_state generator (the unlock)

**Scope:** Pearl_Author skill that takes (series_profile, episode_index, chapter_beatsheet, character_design, style_state) → emits 35 continuity_state YAMLs per episode. Generator deterministic from a single operator-authored beatsheet per episode.

**Authoring inputs the generator needs from the operator (per episode):**
- High-level beat structure (opening anchor → 4 acts → closing decompression)
- Character pose progression (which archetypes appear in which order)
- Scene state evolution (kitchen → window → garden, etc.)
- Light rig changes per beat
- ~30-60 min per episode operator authoring (vs ~17h per episode manual panel authoring)

**Exit criteria:**
- Generator emits valid continuity_state YAMLs that pass `scripts/manga/validate_continuity_invariants.py`
- Round-trip test: regenerate ep_001 from a beatsheet derived from existing 35 YAMLs; output matches existing within tolerance
- Documentation at `docs/PEARL_AUTHOR_CONTINUITY_STATE_GENERATOR.md`

**Cost:** ~1 week build + iteration

**Owner:** Pearl_Author (new skill); operator authors first 1-2 beatsheets to validate generator

### Milestone D — Generalize to 4 top genres (cross-genre proof)

**Scope:** Author panel_template + run V5.1 on 1 series each in: slice_of_life, workplace, supernatural_everyday, sports. Healing/iyashikei already done.

**Per-genre work:**
- Genre craft study (analog to `artifacts/research/manga_quality_bar/01_iyashikei_craft_study.md`): 1-2 days research per genre
- Authoring `config/manga/panel_templates/<genre>.yaml` with N archetypes per genre: ~3-5 days each
- Per-series style_state for the pilot series: ~4h each
- Operator-authored beatsheet for ep_001 of the pilot series: ~1h each (via Milestone C generator)
- V5.1 dispatch + operator review: ~10h Pearl Star compute + ~2h review each

**Exit criteria:**
- 4 new genre templates committed
- 4 new pilot series ship V5.1 ep_001 (35 panels each) with operator §11 approval (≥31/35)
- Cross-genre style consistency: each genre has distinct, identifiable aesthetic matching its declared `drawing_tradition_per_genre.yaml` entry

**Cost:** ~3-4 weeks total (parallel authoring; sequential Pearl Star dispatch)

**Owner:** Pearl_Author (continuity_state) + Pearl_Architect (panel templates) + operator (genre-specific §11 acceptance criteria)

### Milestone E — Per-genre LoRA Phase 2 (close the April audit gap)

**Scope:** Pearl_Research scout + smoke test for the 22 genres deferred in `artifacts/research/community_lora_roster_2026-04-29.yaml` Phase 2. Now under V5.1 Qwen-Image-Layered constraints (different LoRA universe than April's SDXL focus).

**Per-genre work:**
- Pearl_Research scout (~1 day): commercial-clean LoRAs on HF/Civitai/GitHub for that genre's aesthetic, compatible with Qwen-Image
- Smoke test on Pearl Star: 1-image dispatch with candidate LoRA → operator visual verdict (~1h compute + ~30 min review)
- Decision: adopt / pivot to base model / train Phoenix LoRA

**Exit criteria:**
- LoRA decision file `artifacts/research/v51_lora_roster_<genre>_2026-MM-DD.md` per genre
- Adopted LoRAs licensed + smoke-tested before any production dispatch
- Updated community_lora_roster.yaml to v2

**Cost:** ~22 days research + ~22h compute total (parallel scout, sequential dispatch)

**Owner:** Pearl_Research per genre

### Milestone F — Locale aesthetic deltas

**Scope:** Per-locale style_state overrides for the top-5 locales (en-US, ja-JP, ko-KR, fr-FR, de-DE). E.g., ja-JP iyashikei may want stronger natural-light bias; fr-FR may want softer pastel palette.

**Per-locale work:**
- Locale style audit: ~2 days per locale (collaborate with a native-fluent reviewer if possible)
- Authoring per-locale style_state override file
- Smoke test: 1 panel × 1 series re-rendered with locale override → operator verdict

**Cost:** ~3 weeks

**Owner:** Pearl_Architect + operator + locale-fluent reviewers

### Milestone G — Catalog scale-up (~800 high-confidence configs target)

**Scope:** With Milestones A-F in place, the catalog scales: each new series needs only (1) operator beatsheet (~1h/episode via Milestone C generator), (2) Pearl Star compute (~13h/episode at 35 panels × 25 min), (3) operator §11 review (~30 min/episode).

**Throughput math (per series, 10 episodes):**
- Operator authoring: ~10h beatsheets
- Pearl Star compute: ~130h continuous
- Operator review: ~5h
- Total: ~145h per series end-to-end

**For 100 series (subset of 800 high-confidence):** ~14,500h compute = ~600 days serial on a single GPU. Implication: multi-GPU or hosted-inference rollout required before reaching catalog scale. **This is a Milestone H / infrastructure-scaling problem, NOT a Milestone G problem.**

**Exit criteria:**
- Top 10 series per top 4 genres shipped V5.1 (40 series × 10 episodes = 400 episodes operator-approved)
- Operator validates catalog-scale workflow before further scale

**Cost:** ~6 months wallclock at current Pearl Star throughput; ~6 weeks at 8-GPU parallel

**Owner:** Pearl_PM coordinates; Pearl_Author drives content; Pearl_Star drives compute

### Milestone H — Compute infrastructure scaling (out of plan scope; depends on Milestone G validation)

**Scope:** When Milestone G validates the workflow, scale compute beyond single-GPU Pearl Star. Options: additional Pearl Star nodes, RunComfy hosted inference (commercial flag check required), local cluster build. Out of scope for THIS plan.

---

## 5. Critical-path identification

The hardest dependency is **Milestone C — continuity_state generator**. Without it:
- Milestone B (ep_002-010) requires ~175h manual authoring
- Milestone D (4 genres × 1 pilot series) requires ~700h manual authoring
- Milestone G (catalog scale) is mathematically infeasible

With Milestone C:
- Operator authors beatsheet in ~1h/episode
- Generator emits 35 valid continuity_state YAMLs deterministically
- Authoring bottleneck disappears; compute becomes the bottleneck
- Compute scaling is a known problem (Milestone H)

**Therefore Milestone C is the highest-leverage item in this plan.** Recommend prioritizing Milestone C immediately after Milestone A acceptance.

---

## 6. Recommended sequencing

| Order | Milestone | Gated on | Wallclock estimate |
|---|---|---|---|
| 1 | A — ep_001 acceptance | (in flight, ~7-8h compute remaining) | ~1 day |
| 2 | C — continuity_state generator build | A acceptance | ~1 week |
| 3 | B — ep_002-010 dispatch (uses C output) | C validated on round-trip | ~1 week (mostly compute) |
| 4 | D — 4 top-genre pilots (parallel authoring + sequential compute) | C validated | ~3-4 weeks |
| 5 | E — Phase 2 LoRA scout for 22 genres (parallel) | D underway | ~3-4 weeks (parallel with D) |
| 6 | F — Locale aesthetic deltas (parallel) | D underway | ~2-3 weeks (parallel) |
| 7 | G — Scale to top 10 × top 4 genres = 40 series | D acceptance + E adopt-or-skip per genre | ~6 months serial / ~6 weeks at 8x compute |
| 8 | H — Compute infrastructure scaling | G validated workflow | TBD; separate plan |

Total wallclock from today to first 40-series catalog ship: ~7-9 months at single-GPU Pearl Star throughput; can compress with parallel compute investment.

---

## 7. What this plan does NOT decide

- **Compute infrastructure choice** (Pearl Star scaling vs hosted vs local cluster) — Milestone H, separate plan
- **Specific genre § 11 acceptance criteria** — operator-tier per genre when each pilot ships
- **Per-locale fluent reviewer recruitment** — Milestone F prerequisite
- **Pearl_Author skill design specifics** — Milestone C will produce its own design doc
- **LoRA training infrastructure** — only invoked if Phase 2 scout finds no commercial-clean candidate (per April audit thesis: "for genres well-covered by anime base models, no LoRA is needed")
- **Bubble/lettering pipeline integration** — V5.1 produces composites; bubble lettering (per `agent/manga-lettering-v2-20260507` PR #945) is a downstream concern

---

## 8. Open uncertainties

1. **V5.1 architectural robustness at episode scale** — Milestone A is N=1. Milestone B (10 episodes) is the first real test. If V5.1 breaks down on a panel type not represented in ep_001 (e.g., archetypes with multiple characters in frame), authoring may need a per-archetype workaround.
2. **Per-panel compute cost stability** — currently ~25 min/panel via Image-to-Layers. If Qwen-Image-Layered model updates change this materially (faster or slower), Milestone G economics shift.
3. **Pearl_Author beatsheet authoring throughput** — operator authoring ~1h/episode is the estimate. If reality is ~3h/episode, scale economics worsen significantly.
4. **Cross-genre style transfer reliability** — V5.1 Image-to-Layers preserves V3.1 style perfectly on iyashikei. Whether it preserves a sports / mecha / horror style equally well is empirically untested.
5. **Identity drift across decomposed layers in non-iyashikei genres** — V5.1 inherits stage-1 base Qwen's identity consistency. If base Qwen has different identity behavior on action / multi-character scenes, that's a Milestone D risk.

---

## 9. Decision points for operator

1. **Approve plan sequencing as written, or reorder?** Specifically: prioritize Milestone C (generator build) immediately after Milestone A, or push it to after Milestone B manual ep_002-010 dispatch?
2. **Acceptance criteria for Milestone B** — same as ep_001 (≥31/35 shippable per episode) or different for downstream episodes?
3. **Genre selection for Milestone D** — slice_of_life / workplace / supernatural_everyday / sports per catalog distribution, or different priority based on commercial intent?
4. **Per-locale rollout order** — ja-JP first (18 series in catalog), or en-US first (Milestone A series's locale)?
5. **Milestone H pre-planning** — start scoping compute infrastructure scaling NOW (in parallel with Milestone B), or defer until Milestone G validates the workflow?

---

## 10. Authority

This plan is reviewable / amendable by:
- Operator (final approval per milestone gate)
- Pearl_PM (scheduling + cross-workstream coordination)
- Pearl_Architect (architectural decisions)
- Pearl_Author (continuity_state + content authoring; once Milestone C ships)

Source-of-truth cross-references:
- `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` v1.1.0
- `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` (V4 spec; V5.1 reuses §5/§6/§5.9/§12/§14.F)
- `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md` (the schema Milestone C must generate)
- `artifacts/research/full_content_audit.md` (800 high-confidence configs definition)
- `artifacts/research/community_lora_roster_2026-04-29.yaml` (April Phase 1 LoRA audit)
- `artifacts/research/iyashikei_style_lora_scout_2026-05-21.md` (May Qwen-Image LoRA scout)
- `artifacts/research/manga_quality_bar/01_iyashikei_craft_study.md` (the genre craft study template; Milestone D produces 25 more like this)
- `config/manga/manga_brand_series_plan.yaml` (brand/series throughput targets)
- `config/manga/drawing_tradition_per_genre.yaml` (genre taxonomy + style axes)

— end of plan —
