# Manga Program Strategic Audit — Verdict
**Session:** manga-program-strategic-audit-20260418  
**Auditor:** Pearl_PM + Pearl_Research + Pearl_Architect + Pearl_Editor  
**Date:** 2026-04-18  
**Branch:** agent/manga-strategic-audit-20260418

---

> **3-minute read for operator.** Detailed evidence in 11 workstream files under `artifacts/research/strategic_audit/` and `artifacts/audit/strategic/`.

---

## I. Executive Summary — Traffic Lights

| Question | Verdict | Finding |
|----------|---------|---------|
| Are we building the coolest stuff? | 🟡 YELLOW | White space is real and confirmed. But we're building the wrong format (page manga not webtoon) for the fastest-growing markets. Two high-leverage moves we're NOT doing: vertical scroll and multi-brand crossovers. |
| Are we building it the right way technically? | 🔴 RED | Wrong image model (FLUX vs Illustrious XL). Broken typography (Pillow). LoRAs not trained. IP-Adapter not wired into chapter production. Character drift every panel. |
| Is it sellable in our target markets? | 🟡 YELLOW | Market opportunity is real ($14.84B manga + $8B webtoon, growing). White space confirmed — no competitor owns therapeutic manga at scale. But we have no distribution accounts, no webtoon format, and no ISBNs. Nothing is deployed. |

**The core problem:** Every layer is correct in spec. Nothing is correct in production. The gap between architecture and execution is where all bad output lives.

---

## II. Top 5 Findings (With Citations)

**Finding 1: The white space is real.**  
No competitor simultaneously occupies: manga format + therapeutic content + AI production + multi-market + consumer pricing. Dashtoon raised $17.6M (Fast Company Most Innovative 2024) but is entertainment-only, not wellness. The Manga Guide to X series (No Starch Press, 150K English / 500K WW as of 2015) is STEM-only, no mental health. Dr. Frost (Naver, psychology manhwa) is Korea-only and character-drama, not self-help. The therapeutic manga category at commercial scale is genuinely unoccupied.  
*Source: artifacts/research/strategic_audit/06_competitive_landscape.md, WS6 competitive matrix*

**Finding 2: The bestseller hook is genre, not wellness.**  
The 2024 Circana BookScan Top 20 US manga titles have zero wellness titles. Readers don't search "self-help manga" — they search "iyashikei," "healing manhwa," "essay manga." Phoenix Omega's positioning must lead with genre signals, not the wellness label. *Frieren: Beyond Journey's End* (24M+ copies, Shogakukan, +99% YoY 2024 per Oricon) sells as iyashikei, not as "mindfulness manga." The therapeutic content is the substance; the genre convention is the hook.  
*Source: artifacts/research/strategic_audit/02_bestseller_pattern_decomposition.md*

**Finding 3: FLUX is the wrong model.**  
Multiple 2024-2025 benchmarks confirm FLUX.1-dev is photorealism-biased. Stable Diffusion Art comparison (2025): "SDXL is more accurate for expressionist style; FLUX images are too realistic and polished." Illustrious XL 2.0 (SDXL-derived, fine-tuned on Danbooru2023, 134K+ downloads, native 1536×1536) is purpose-built for anime/manga and runs comfortably on RTX 5070 Ti 16GB. The model swap is the single highest-leverage quality improvement available.  
*Source: artifacts/audit/strategic/07_tech_stack_audit.md, Citations C1-C8*

**Finding 4: The josei mislabeling corrupts three brands.**  
somatic_wisdom, heart_balance, and body_memory are labeled "shojo" in all configs. Their actual content (adult women, burnout, somatic therapy) is josei — a distinct demographic genre with distinct visual conventions. FLUX prompts calibrated to "shojo" generate high-school aesthetics (school uniforms, sparkles, young faces) instead of josei's adult realism. The bestseller evidence is in josei, not shojo: Nagata Kabi's *My Lesbian Experience with Loneliness* (#2 NA debut per Nielsen BookScan) is josei essay manga. This mislabeling is baked into configs, prompts, and LoRA training plans.  
*Source: artifacts/audit/strategic/04_genre_coverage_gap_analysis.md, WS4 Section 2a*

**Finding 5: The pipeline outputs the wrong format for the fastest-growing markets.**  
WEBTOON (US), Naver Canvas (Korea), and Piccoma (Japan) — the three highest-priority distribution channels — all require vertical-scroll format. The current pipeline produces page-format manga only. A format conversion step does not exist. The webtoon market is $7-8.28B (2024) growing at 27.3% CAGR; LINE Manga Japan generated $648.2M in 2024. This format gap blocks the highest-growth channels.  
*Source: artifacts/audit/strategic/11_gtm_channel_audit.md, WS11 vertical scroll finding; global webtoon CAGR from WS1*

---

## III. Portfolio Strategy

### Brand Verdict — Keep / Kill / Add

| Brand | Verdict | Reasoning |
|-------|---------|-----------|
| stillness_press | **KEEP — FLAGSHIP** | Only brand with production artifacts. iyashikei genre, proven commercial category. Ahjan teacher = strongest content foundation. |
| cognitive_clarity | **KEEP** | Seinen psychological manga has commercial precedent (Honey & Clover 12M, Monster). Joshin's direct-pointing method is a differentiated hook. Strong US + France fit. |
| somatic_wisdom | **KEEP — RECLASSIFY as josei** | Content is correct, label is wrong. Re-label josei + essay manga format. Pamela Fellows somatic approach has closest analogue to Nagata Kabi model. |
| qi_foundation | **KEEP — CONDITIONAL** | Cultivation genre is huge in China ($Y market). But wellness cultivation hybridization is UNPROVEN. Keep but do not launch until one specific therapeutic cultivation bestseller is cited in the configs. |
| digital_ground | **KEEP** | Only brand positioned natively for webtoon/manhwa format. miki's digital burnout topics directly serve Korea healing manhwa category. First brand to convert to vertical scroll. |
| heart_balance | **KILL** | Topics (self_worth, compassion_fatigue, boundaries) are identical to somatic_wisdom. Art style (shojo) is identical to somatic_wisdom. No differentiated market position. Zero assets. |
| relational_calm | **KEEP** | Japan-primary brand with junko teacher. iyashikei + social anxiety + karoshi burnout = highest-fit JP market positioning. Keep but do not advance to production until JPN editorial review is budgeted. |
| warrior_calm | **KEEP — CONDITIONAL** | Cultivation × courage × martial arts is differentiable. But cultivation + therapeutic = unproven. Same conditional as qi_foundation: require one cited bestseller before production. |
| sleep_restoration | **KILL** | Third iyashikei brand with sleep_anxiety as primary topic. stillness_press already has sleep_anxiety as series slot. Zero differentiation. Zero assets. Merge series slot into stillness_press. |
| body_memory | **KEEP — RECLASSIFY as josei** | Japan-primary josei brand (omote teacher) covering somatic healing + grief. Strong conceptual differentiation from somatic_wisdom (JP market vs EN market). Reclassify genre. |
| solar_return | **KILL — UNLESS repositioned** | Isekai + therapeutic content has zero commercial precedent. The only unique topic is depression, which is a high-value market topic but doesn't require an isekai genre frame. Either (a) keep as the portfolio's depression brand in a genre with actual evidence, or (b) kill. |
| devotion_path | **KILL** | Shonen + therapeutic narrative conflicts with genre conventions. courage + imposter_syndrome + burnout are already covered by 4+ other brands. No unique topic, no unique market. |

**Cut list (4 to kill):** heart_balance, sleep_restoration, devotion_path, solar_return (unless repositioned)

**Add list (2 with market evidence):**

| Proposed New Brand | Positioning | Evidence |
|--------------------|-------------|----------|
| **grief_work** (English global) | Single-volume essay manga on grief and loss. body_memory is Japan-primary; en_US grief manga lane is empty. | WS3 brand portfolio audit identified grief as portfolio gap. Nagata Kabi model proves single-volume essay manga viability. |
| **neurodivergent_edge** | ADHD/autism/neurodivergent self-advocacy manga. Zero brands in Phoenix Omega cover this. | ADHD audiobook is fastest-growing self-help audio category (WS3 finding). Instagram-comic-to-book pipeline (see Adam J. Kurtz) validates format. No manga competitor owns this. |

### Genre Focus

**Focus on:** iyashikei, josei/essay manga, manhwa/webtoon  
**Retain but validate:** seinen, shonen (devotion_path path if kept), cultivation  
**Suspend:** isekai (pending commercial evidence)  
**Add format type:** essay_manga as explicit single-volume format for stillness_press + somatic_wisdom

### Market Prioritization (Focus on 3-5, Not All 12)

**Tier 1 — Build for these first:**
1. **en_US / English global** — Lowest barriers, KDP 70% royalty, WEBTOON Canvas available, essay manga breakout category, highest per-unit margin
2. **ko_KR** — WEBTOON native, healing manhwa established category, Naver Canvas free entry, digital_ground brand ready to go
3. **fr_FR** — #2 world market outside Japan, $465M, 19.6% CAGR, webtoon viewership +55%, iyashikei + seinen well-received

**Tier 2 — 2027 with some prep:**
4. **ja_JP** — Largest market, but requires JPN editorial review, distribution gatekeeping, cultural tonal calibration. KDP JP + MANGA Plus accessible. Budget $800-1,500/volume editorial.
5. **de_DE** — Large European market, evidence-based positioning required, no cultural blockers

**Defer:** zh_CN (regulatory/MCN complexity), hu_HU (minimal volume), es_US (no iyashikei Spanish-language precedent found)

---

## IV. Tech Stack Verdict

| Layer | Current | Verdict | Recommended Action | Effort |
|-------|---------|---------|-------------------|--------|
| Image model | FLUX.1-dev | **SWAP** | Illustrious XL 2.0 (SDXL manga-native, Danbooru2023) | 3-5 days |
| Character consistency | IP-Adapter (spec-only) | **EVALUATE → IMPLEMENT** | IP-Adapter IS in ComfyUI workflow JSON; wire into `run_chapter_production.py` | 1-2 weeks |
| Character LoRAs | 48 LoRAs planned, 0 trained | **IMPLEMENT** | Requires: collect 20 reference images per teacher → run LoRA training with Kohya-ss | 4-6 weeks |
| Typography | Pillow | **SWAP** | Skia-Python + HarfBuzz (available pip install) | 1-2 weeks |
| LLM (prose/scripts) | Qwen2.5/qwen3:14b 9-14B | **KEEP + UPGRADE** | Qwen2.5-32B Q4 for chapter writing (one `ollama pull`); 14B for translation | 1 day |
| TTS | CosyVoice2 | **KEEP** | Add Kokoro-82M as English-lane secondary (#1 TTS Arena Jan 2026, Apache-2.0) | 2-3 days |
| Orchestration | GHA + self-hosted runner | **KEEP** | Core bottleneck is FLUX latency (fixed by Illustrious XL swap), not orchestration |  — |

**Highest-leverage swap ranking (quality gain per unit effort):**
1. Illustrious XL 2.0 (image model swap) — 3-5 days, eliminates photorealism bias
2. Skia typography (cover quality) — 1-2 weeks, fixes operator's "very bad" typography feedback  
3. Qwen2.5-32B (LLM upgrade) — 1 day, meaningful quality jump for chapter prose
4. IP-Adapter wiring (character consistency) — 1-2 weeks, eliminates per-panel character drift
5. LoRA training for all 13 teachers — 4-6 weeks, locks brand visual identity permanently

---

## V. Methods Upgrades (Ranked by Quality Impact)

| Gap | Impact | Current State | Fix | Effort |
|-----|--------|--------------|-----|--------|
| Character consistency not wired into chapter production | HIGH | IP-Adapter workflow exists but `run_chapter_production.py` calls txt2img only | Wire `flux_ip_adapter_manga.json` into chapter flow; add seed locking per teacher | 1-2 weeks |
| No thumbnail/name stage | HIGH | Pipeline goes script → panel prompts → render with zero compositional planning | Add layout stage: script → panel layout YAML → render | 1-2 weeks |
| No editorial revision loop | HIGH | Generate panels once, ship | Add Pearl_Editor review step with per-panel re-generation flag | 1-2 weeks |
| Research not referenced in prompts | MEDIUM | Bestseller research is in .md files; prompt compiler does not read them | Distill genre visual tokens from WS2 research into YAML config; prompt compiler reads config | 3-5 days |
| Missing character blocks (8 of 13 teachers) | HIGH | `visual_prompt_compiler.py` has hardcoded blocks for only 5 teachers | Extend `DEFAULT_CHARACTER_BLOCKS` dict for all 13 | 1-2 days |
| EMA not wired to manga | LOW now / HIGH at scale | EMA learner implemented for ebook prose only | Define manga panel quality signal → wire to EMA loop | 1-2 weeks |

**Quick wins (< 1 week each):**
- Extend character blocks to all 13 teachers — hours of work, immediate consistency improvement
- Add deterministic seed locking per teacher character — one function, major consistency win
- Distill genre tokens from WS2 into YAML and add to prompt compiler — 3-5 days, eliminates "generic wellness manga" look

---

## VI. "Coolest Stuff" — Top 3 Priorities

**Priority 1: Vertical-scroll / Webtoon format** (build now)
- Global webtoon market: $7-8.28B (2024), 27.3% CAGR to 2030 (vs. 16.21% for manga digital)
- LINE Manga Japan: $648.2M revenue 2024 alone
- WEBTOON pays creators $1M+/month cumulatively; Canvas free entry
- Phoenix Omega's existing pipeline is 2-4 weeks from supporting vertical scroll with canvas resizing
- This unlocks Korea (Naver Canvas), Japan (LINE Manga), and the US webtoon audience simultaneously
- *Source: WS9, WS1 market data*

**Priority 2: Multi-brand crossover events** (build in 2026 H2)
- YLAB's Superstring/Bluestring/Redstring shared universe is commercial proof of concept
- Phoenix Omega's 12 teacher characters are an undeployed shared-universe asset
- One crossover one-shot (e.g., Ahjan + Joshin characters discussing burnout together) costs 1 additional chapter of production but creates marketing value for both brands
- Korean webtoon crossover events (Lookism extended universe) drive measurable subscriber spikes
- *Source: WS9, YLAB model citation*

**Priority 3: AI-narrated audiobook variants with character voices** (build in 2027)
- Each manga volume gets an audiobook companion where the teacher character reads/narrates
- CosyVoice2 is already running; voice cloning per character is a 1-2 day setup per teacher
- Audiobook market: $6.7B (2024), 26% CAGR; manga readers are audio-adjacent (existing audiobook brands)
- No competitor in therapeutic manga has done this — it's unique and on-brand for EI disclosure
- *Source: WS9*

---

## VII. Anti-Recommendations — Stop Doing These

| Anti-Recommendation | Current State | Evidence Against |
|---------------------|--------------|-----------------|
| **STOP building in shojo genre** | 3 brands labeled shojo | Therapeutic adult content in shojo visual frame produces wrong aesthetics (teen-coded art); josei has the bestseller evidence (Nagata Kabi). Continuing to prompt FLUX with "shojo" markers will keep producing wrong output. |
| **STOP building sleep_restoration as separate brand** | Active in configs | sleep_anxiety is already a stillness_press series slot. Zero differentiation from stillness_press. Zero assets. Every hour spent on sleep_restoration is an hour not spent deepening the flagship. |
| **STOP building devotion_path** | Active in configs | Shonen genre conventions actively conflict with therapeutic pacing. Topics fully absorbed by other brands. No unique positioning. |
| **STOP building cultivation × therapeutic content without market evidence** | qi_foundation + warrior_calm planned | Not one specific bestseller found for "cultivation manga + wellness" hybridization across any market. The genre is huge; the hybrid is unproven. Build one proof-of-concept chapter before committing to full series plans. |
| **STOP using Pillow for production typography** | All covers use Pillow | Operator already called it "very bad." Root cause is technical (no HarfBuzz shaping, no sub-pixel hinting, broken RTL/vertical). Skia-Python swap is 1-2 weeks. Every chapter generated with Pillow typography is a quality regression. |
| **STOP submitting to Tapas** | In distribution plan | Tapas banned AI-generated art in January 2023. Submitting will result in account termination, not sales. Remove from GTM plan. |
| **STOP targeting all 12 markets simultaneously** | Active workstreams for all locales | Resource spreading across 12 markets dilutes execution quality. 3 markets (en_US, ko_KR, fr_FR) with high-quality output beats 12 markets with bad output. Depth before breadth. |

---

## VIII. Rebuilt 6-Month Roadmap (Supersedes bestseller_action_plan.md for manga program)

### Month 1 — Fix the Foundation (P0 Quality Fixes)
- [ ] Swap FLUX.1-dev → Illustrious XL 2.0 on Pearl Star ComfyUI
- [ ] Extend `visual_prompt_compiler.py` character blocks to all 13 teachers
- [ ] Add deterministic seed locking per teacher in chapter production
- [ ] Fix genre labels: reclassify somatic_wisdom, heart_balance, body_memory → josei in all configs
- [ ] Kill heart_balance, sleep_restoration, devotion_path configs (prevent future work on dead brands)
- [ ] Set up Amazon KDP account, Apple Books account, Google Play Books account
- [ ] Generate first 5 stillness_press chapters with fixed stack → internal quality review before external release

### Month 2 — Typography + Vertical Scroll
- [ ] Swap Pillow → Skia-Python + HarfBuzz for cover and bubble typography
- [ ] Build vertical-scroll conversion pipeline (canvas resize, panel reflow for webtoon format)
- [ ] Register WEBTOON Canvas account for digital_ground (manhwa/webtoon brand, Korea-native positioning)
- [ ] Upgrade LLM to Qwen2.5-32B Q4 for chapter writing
- [ ] Distill WS2 bestseller patterns into prompt config YAML (genre visual tokens)

### Month 3 — Character Consistency + First Releases
- [ ] Wire IP-Adapter into `run_chapter_production.py` (not just standalone scripts)
- [ ] Collect 20 reference images per teacher (13 teachers × 20 = 260 reference images via fixed Illustrious XL + IP-Adapter)
- [ ] Launch stillness_press on Amazon KDP en_US (first 3 volumes, iyashikei anxiety series)
- [ ] Launch digital_ground on WEBTOON Canvas (vertical scroll format, weekly cadence)
- [ ] Add thumbnail/layout stage before panel render

### Month 4 — LoRA Training + Editorial Loop
- [ ] Train first 5 priority LoRAs (stillness_press, cognitive_clarity, somatic_wisdom, digital_ground, relational_calm) with Kohya-ss on Pearl Star
- [ ] Implement Pearl_Editor panel review loop with per-panel re-generation flag
- [ ] Launch cognitive_clarity on Amazon KDP en_US (seinen psychological burnout series)
- [ ] Submit to Apple Books and Google Play Books (all 3 launched brands)

### Month 5 — France + Japan Preparation
- [ ] Launch stillness_press on Amazon FR + Izneo
- [ ] Begin JPN editorial review budget allocation for relational_calm (Japanese-native prose QA)
- [ ] Train remaining 8 LoRAs
- [ ] First crossover one-shot concept (ahjan × joshin burnout chapter) — internal production test
- [ ] Begin Kokoro-82M voice cloning setup for en_US character audiobook companion

### Month 6 — Japan Soft Launch + Expand
- [ ] Submit 2 relational_calm chapters to MANGA Plus Creators (Shueisha, free open submission)
- [ ] Submit 2 stillness_press chapters to KDP Japan
- [ ] Launch first multi-brand crossover one-shot on WEBTOON Canvas
- [ ] Begin somatic_wisdom (josei, now correctly classified) on Amazon KDP en_US
- [ ] Quality review: if stillness_press KDP rank ≥ 50K in Comics/Manga, continue; if ≥ 200K, diagnose before Month 7

**Milestone gate (end Month 3):** If stillness_press first 3 volumes show ≥ 4.0/5.0 Amazon review average OR ≥ 200 WEBTOON digital_ground subscribers, proceed to Month 4 at full pace. If below threshold, stop new launches and diagnose before expanding.

---

## IX. Deliverables Index

| File | Lines | Workstream | Citation Count |
|------|-------|-----------|----------------|
| artifacts/research/strategic_audit/01_global_manga_market_map.md | 333 | WS1 | ~15 |
| artifacts/research/strategic_audit/02_bestseller_pattern_decomposition.md | 397 | WS2 | ~20 |
| artifacts/research/strategic_audit/06_competitive_landscape.md | 325 | WS6 | ~15 |
| artifacts/audit/strategic/03_brand_portfolio.md | 592 | WS3 | ~12 |
| artifacts/audit/strategic/04_genre_coverage_gap_analysis.md | 162 | WS4 | 8 |
| artifacts/audit/strategic/05_genre_market_fit_matrix.yaml | 374 | WS5 | 10 |
| artifacts/audit/strategic/07_tech_stack_audit.md | 376 | WS7 | 22 |
| artifacts/audit/strategic/08_methods_audit.md | 197 | WS8 | 15 |
| artifacts/audit/strategic/09_differentiation_moves.md | 228 | WS9 | 28 |
| artifacts/audit/strategic/10_japan_deep_dive.md | 230 | WS10 | 42 |
| artifacts/audit/strategic/11_gtm_channel_audit.md | 286 | WS11 | ~15 |
| **MANGA_STRATEGIC_AUDIT_VERDICT.md** | this file | WS12 | synthesis |

**Total citations across audit: ~202 qualified sources**  
**Total words across audit: ~58,000**  
**API spend: $0** (Pearl_Research via WebSearch tool, no external API calls)

---

## CLOSEOUT_RECEIPT

```
session_id:    manga-program-strategic-audit-20260418
branch:        agent/manga-strategic-audit-20260418
base:          origin/main
commit_sha:    [pending — run git commit to generate]
pr_url:        [pending — run gh pr create after commit]

workstream_deliverables:
  WS1  01_global_manga_market_map.md          333 lines  ~15 citations
  WS2  02_bestseller_pattern_decomposition.md 397 lines  ~20 citations
  WS3  03_brand_portfolio.md                  592 lines  ~12 citations
  WS4  04_genre_coverage_gap_analysis.md      162 lines   8 citations
  WS5  05_genre_market_fit_matrix.yaml        374 lines  10 citations
  WS6  06_competitive_landscape.md            325 lines  ~15 citations
  WS7  07_tech_stack_audit.md                 376 lines  22 citations
  WS8  08_methods_audit.md                    197 lines  15 citations
  WS9  09_differentiation_moves.md            228 lines  28 citations
  WS10 10_japan_deep_dive.md                  230 lines  42 citations
  WS11 11_gtm_channel_audit.md                286 lines  ~15 citations
  WS12 MANGA_STRATEGIC_AUDIT_VERDICT.md       this file

executive_verdict:
  building_coolest_stuff:    YELLOW — white space confirmed, but wrong format for fastest-growing markets
  built_right_technically:   RED    — wrong model, broken typography, no character consistency in production
  sellable_in_target_markets: YELLOW — opportunity real, no distribution deployed

brand_keep_list:     [stillness_press, cognitive_clarity, somatic_wisdom(reclassify), qi_foundation(conditional), digital_ground, relational_calm, warrior_calm(conditional), body_memory(reclassify)]
brand_kill_list:     [heart_balance, sleep_restoration, devotion_path, solar_return(unless repositioned)]
brand_add_list:      [grief_work(en_US essay manga), neurodivergent_edge]

genre_focus:         [iyashikei, josei/essay_manga, manhwa/webtoon]
market_priority_t1:  [en_US, ko_KR, fr_FR]
market_priority_t2:  [ja_JP(2027), de_DE(2027)]
market_defer:        [zh_CN, hu_HU, es_US(pending evidence)]

tech_swap_ranking:
  1. FLUX → Illustrious XL 2.0         (3-5 days)
  2. Pillow → Skia + HarfBuzz           (1-2 weeks)
  3. Qwen 14B → 32B Q4                  (1 day)
  4. Wire IP-Adapter into chapter flow  (1-2 weeks)
  5. Train 48 LoRAs                     (4-6 weeks)

top_5_anti_recommendations:
  1. Stop building in shojo genre — reclassify to josei
  2. Stop sleep_restoration as separate brand — absorb into stillness_press
  3. Stop devotion_path — shonen conflicts with therapeutic pacing
  4. Stop cultivation × therapeutic without market evidence
  5. Stop Tapas distribution — AI art banned since Jan 2023

top_3_coolest_priorities:
  1. Vertical scroll / webtoon format ($8B market, 27% CAGR) — 2-4 weeks
  2. Multi-brand crossover events (YLAB model validated) — 2-3 weeks per arc
  3. AI character voice audiobook companions (CosyVoice2 already running) — 2027

citations_total:     ~202 qualified sources
api_spend:           $0

NEXT_ACTION: Operator reads Sections II-VIII above (3 minutes) →
  1. Approve brand kill list (4 brands) → prevents future work on dead positioning
  2. Approve tech stack swaps (Illustrious XL + Skia) → unblocks Month 1 roadmap
  3. Scope Month 1 sprint from P0 quality fixes list → new PR per execution sprint
```
