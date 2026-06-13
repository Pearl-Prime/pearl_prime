# Phoenix Omega — Human Team Structure

## Endless-Team Roster × Lean-Team Roster × Subsystem × Skill-Level × Pearl-Agent Pairing

**Date:** 2026-06-09
**Author:** Pearl_Architect
**Session:** `pearl-architect-human-team-structure-20260606`
**Companion artifacts:**
- `SUBSYSTEM_HEALTH_AUDIT.md` (audit feeding role-design)
- `HUMAN_TEAM_STRUCTURE.pptx` (operator-facing deck)
- `[pending cross-ref]` `artifacts/research/contributor_learning_pathways_20260606/` (Pearl_Research parallel ws — Google course recommendations per role)

---

## §0. Operator framing

Two questions, one analysis:

1. **Endless team.** "If we had a team of endless people, of all skill levels, what roles do we need?" → Answer: 16 roles spanning no-skill → staff+, mapped to 19 subsystems + the 14-agent Pearl roster (+ 4 emerging agents observed in workstreams but absent from `agent_registry.yaml`).
2. **Lean team.** "What is the leanest team? Like one PM, one senior developer, two QA, one marketer." → Answer: **5.5-6.0 FTE** (PM, Senior Dev, 2 QA, Marketer, half-FTE Research/Editor) covering ~80-83% of sustain demand; hire-order ladder back toward endless explicitly named.

---

## §1. Subsystem health summary (link to A)

See `SUBSYSTEM_HEALTH_AUDIT.md` for the full 19-row table. Headline:

- **Tier 1 (load-bearing, 65-85 hr/wk):** core_pipeline, manga_pipeline
- **Tier 2 (program-critical, 90-115 hr/wk):** pearl_prime, brand_admin, teacher_mode, video_pipeline, pearl_devops, pearl_news
- **Tier 3 (steady-state, 70-100 hr/wk):** marketing, integrations, translation, audiobook_pipeline, podcast_pipeline, music_mode, ei_v2, dashboard
- **Tier 4 (reactive, 16-28 hr/wk):** recommendations, ite, trend_feeds (subsumed)

**Aggregate:** 240-310 hr/wk just to sustain. Add 120-160 hr/wk for active Phase A/B programs.

---

## §2. Endless-team role roster — 16 roles

Each role uses the 9-field hiring-brief shape:

```
Role title
├─ Skill-level entry point
├─ Subsystem ownership (1-3)
├─ Reports-to
├─ Pearl agent counterpart
├─ Top 5 responsibilities
├─ Top 5 required skills
├─ Top 5 nice-to-have skills
├─ Recommended Google course / certificate  [pending cross-ref]
└─ First 30-day deliverable shape
```

### Role 1 — Project Manager (overall, single-platform owner)

> Operator-named: *"a real project manager for all projects"*

- **Skill-level entry point:** Senior
- **Subsystem ownership:** Coordination across all 19 (special)
- **Reports-to:** Operator (Ahjan)
- **Pearl agent counterpart:** Pearl_PM (primary) + Pearl_Architect (advisor)
- **Top 5 responsibilities:**
  1. Own `ACTIVE_PROJECTS.tsv` + `ACTIVE_WORKSTREAMS.tsv` row-by-row; reconcile weekly
  2. Routing: every operator ask → correct lane within 24h with a STARTUP_RECEIPT brief
  3. Weekly merge train: gate Phase A/B/C ship items; track open-PR backlog
  4. Operator-proxy: in-envelope decisions per `docs/PEARL_OPERATOR_PROXY_SPEC.md`; escalate out-of-envelope
  5. Cross-team standup synthesis; blockers + dependency unblocking
- **Top 5 required skills:** Program management at 50+ in-flight workstreams; technical literacy across ML/content/CI; conflict mediation; stakeholder-comms; written brief discipline
- **Top 5 nice-to-have:** Publishing/content ops background; AI/ML pipeline familiarity; Notion/Linear/GitHub fluency; YAML/TSV editing comfort; Japanese culture awareness (CJK locales)
- **Recommended Google course:** `Google Project Management: Professional Certificate` (Coursera) `[pending cross-ref]`
- **First 30-day deliverable:** Weekly ops cadence stood up (standup + merge train + retro); 2 stale ws's closed; 1 program tracker (storefront or manga V2) on a green path

### Role 2 — Manga Tech Lead

> Operator-named: *"manga by itself needs a lot of attention; needs someone very techy"*

- **Skill-level entry point:** Staff+
- **Subsystem ownership:** manga_pipeline, ite
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Dev (manga share) + Pearl_Author + Pearl_Architect (V2 spec)
- **Top 5 responsibilities:**
  1. Manga V2 layered pipeline phases A-E (constraint solver → base models + PuLID → LoRA training → anatomical correction → re-render smoke)
  2. ep_002 V5.1 (and forward) render dispatch + ja_JP/zh_TW/zh_CN locale parity
  3. Character individuation: model_sheets.json + brand_lora_plans.yaml (12-14 LoRAs, not 200+)
  4. 37-brand × 4-locale × 2-surface matrix (KDP paperback + WEBTOON) weekly cron health
  5. RunComfy + Pearl Star compute economics; Tier-2 unattended pipeline ownership
- **Top 5 required skills:** ComfyUI / FLUX / Qwen-Image / Animagine XL deep ops; PyTorch + LoRA training (ai-toolkit); Python pipeline orchestration; image-quality eyeball + measurable scoring; multi-locale Asian-market aesthetics
- **Top 5 nice-to-have:** PuLID + FaceNet familiarity; webtoon-format lettering; manga industry knowledge (LINE Manga, Pixiv); Cloudflare R2 + GitHub Actions; budget guardrails
- **Recommended Google course:** `Google IT Automation with Python` (foundation) + external `Practical Deep Learning for Coders` (fast.ai) `[pending cross-ref]`
- **First 30-day deliverable:** ep_002 V5.1 shipped end-to-end + Phase A constraint-solver scaffold + RunComfy spend dashboard read

### Role 3 — Video Productionization Lead

> Operator-named: *"we have all this video stuff but it really needs to be productionized"*

- **Skill-level entry point:** Senior
- **Subsystem ownership:** video_pipeline, podcast_pipeline (shared with Audiobook Voice + Mix)
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Video + Pearl_Audio (proposed) + Pearl_Dev (shared)
- **Top 5 responsibilities:**
  1. Teacher × manga 30s video V1 — 12-13 deliverables × locale × style spread
  2. Audiobook video format pipeline (CJK narration wiring; ambient soundtrack hardening)
  3. Soundtrack-engine config: 11labs → CosyVoice/Edge migration; loudness/ID3 validation
  4. R2 upload + Cloudflare CDN; WEBTOON Canvas + YouTube Reels output validation
  5. Format spec maintenance (`config/video/format_specs.yaml`, `render_params.yaml`)
- **Top 5 required skills:** FFmpeg + ML video tooling; TTS pipelines + voice cloning (CosyVoice2, ElevenLabs); Python pipeline orchestration; YouTube/WEBTOON/Reels platform specs; cross-locale audio
- **Top 5 nice-to-have:** ComfyUI video workflow; AfterEffects/Resolve for QA; loudness normalization (EBU R128); subtitle/caption ops
- **Recommended Google course:** `Google IT Automation with Python` + external Coursera `Adobe / Avid post-production` `[pending cross-ref]`
- **First 30-day deliverable:** Teacher × manga 30s V1 pilot shipped (1 teacher × 1 locale); CJK narration wiring smoke green; format_specs.yaml audited

### Role 4 — Senior Engineer (core_pipeline)

- **Skill-level entry point:** Senior
- **Subsystem ownership:** core_pipeline, pearl_prime, recommendations (lean), ei_v2 (advisor)
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Prime + Pearl_Dev (core share)
- **Top 5 responsibilities:**
  1. Bestseller pipeline Phase 2 (build_story_schedule + slot_tracker wiring into compose_from_enriched_book)
  2. Register-gate F1-F12 + ship-readiness aggregator + acceptance scorecard
  3. Spine-pipeline default flip; auto-plan SSOT refactor
  4. Teacher-mode wrapper semantics (HOOK / SCENE / STORY substance vs voice routing)
  5. Catalog scale fan-out (800 high-confidence configs; Move 4/5/6 sweeps)
- **Top 5 required skills:** Python + YAML pipelines; pytest + property-based testing; spec → code translation (PHOENIX_V4_5_WRITER_SPEC, PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC); LLM prompt engineering (Tier-1 Claude); content gate design
- **Top 5 nice-to-have:** Editorial sensibility; recommender systems; CJK localization; performance/optimization for batch runs; CI gate authoring
- **Recommended Google course:** `Google IT Automation with Python` + `Cloud Engineer Professional` (catalog scale) `[pending cross-ref]`
- **First 30-day deliverable:** Phase-2 build_story_schedule wired; 1 single-sample smoke proving bestseller-grade output on canonical CLI; ship-readiness aggregator v0

### Role 5 — Senior Engineer (integrations)

- **Skill-level entry point:** Senior
- **Subsystem ownership:** integrations, trend_feeds, podcast_pipeline (shared)
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Int + Pearl_DevOps (shared)
- **Top 5 responsibilities:**
  1. Credential rotation + `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` upkeep; macOS Keychain ↔ env vars
  2. RunComfy spend ledger + budget guard; Tier-2 compute economics
  3. Cloudflare R2 + Workers Builds + Snipcart wiring (storefront V1 dep)
  4. CJK platform connectors (LINE Manga Indies, Pixiv, Comico, Ximalaya)
  5. Trend-feed RSS health + budget guard regression
- **Top 5 required skills:** HTTP/OAuth credential ops; Cloudflare ecosystem; Python integration code; secret-rotation hygiene; multi-platform API contracts
- **Top 5 nice-to-have:** AWS/GCP cross-pollination; SOC2 baseline awareness; Pearl Star SSH + Ollama familiarity; CJK platform business norms
- **Recommended Google course:** `Google Cybersecurity Professional Certificate` + `Cloud Engineer Professional` `[pending cross-ref]`
- **First 30-day deliverable:** Single Keychain → env-var pipeline working for all 19 tracked names; RunComfy spend ledger live; HF token rotation runbook

### Role 6 — Senior Engineer (brand_admin)

- **Skill-level entry point:** Intermediate–Senior
- **Subsystem ownership:** brand_admin, dashboard
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Prez + Pearl_Brand (emerging) + Pearl_Dev (shared)
- **Top 5 responsibilities:**
  1. brand-admin v2 weekly cron (Monday 9am UTC) + per-platform download route maintenance
  2. brand_admin_v2.html axes_present field + 37-brand × 4-axis matrix freshness
  3. Per-platform ZIP packaging + manifest.json schema
  4. Teacher_showcase.html + brand_onboarding_hub.html + Navigate-tab wiring
  5. Cap-entry compliance (BR-CANON-01 Path X 37; BR-CANON-02 global brand identity)
- **Top 5 required skills:** Python web + GitHub Actions cron; HTML/CSS/JS frontend; YAML schema design; CI debugging; cross-brand data modeling
- **Top 5 nice-to-have:** Cloudflare Pages; Snipcart cart embedding; brand-design sensibility; Notion/Linear/Asana cross-tool fluency
- **Recommended Google course:** `Google UX Design Professional Certificate` (cross-train) + `Cloud Engineer` `[pending cross-ref]`
- **First 30-day deliverable:** Weekly cron 2026-Wxx fully shipped (4 axes × 37 brands); v2 dashboard zero-staleness for 1 week; teacher_showcase parity audited

### Role 7 — QA / Verification (prose quality)

- **Skill-level entry point:** Entry–Intermediate
- **Subsystem ownership:** core_pipeline (QA), pearl_prime (QA), teacher_mode (atom QA)
- **Reports-to:** Senior Engineer (core_pipeline) + Project Manager
- **Pearl agent counterpart:** Pearl_Editor (shared) + Pearl_Research (advisor)
- **Top 5 responsibilities:**
  1. Read sample books across 12-spine × persona × topic; score per `PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` (ONTGP per chapter)
  2. Flag register-gate edge cases for F11/F12 detector calibration
  3. HOOK / SCENE / STORY pattern drift audits across atom corpus (211 HOOK atoms baseline)
  4. Read first/last chapter on every storefront-eligible book before ship
  5. EI v2 score sanity-check against eyeball
- **Top 5 required skills:** Close-reading + craft sensibility; spec literacy (writer spec, bestseller overlay, register gate); structured note-taking; pattern recognition; tolerance for repetitive content
- **Top 5 nice-to-have:** English literature degree or MFA-adjacent; second-language CJK reading; familiarity with self-help / therapy register; book-review writing
- **Recommended Google course:** `Google Career Certificate` foundation + Coursera `Editing for Writers` (UC Boulder) `[pending cross-ref]`
- **First 30-day deliverable:** 10 books scored on ACCEPTANCE_SCORECARD; 3 calibration findings filed for register-gate F-detectors; 1 HOOK atom audit pass

### Role 8 — QA / Verification (manga panel review)

- **Skill-level entry point:** Entry–Intermediate
- **Subsystem ownership:** manga_pipeline (QA), video_pipeline (manga 30s QA)
- **Reports-to:** Manga Tech Lead + Project Manager
- **Pearl agent counterpart:** Pearl_Dev (manga share) + Pearl_Editor (shared)
- **Top 5 responsibilities:**
  1. Per-panel review against `CHARACTER_INDIVIDUATION_PIPELINE_SPEC` (same-brand / cross-brand distinctness)
  2. Face-lock + character-design consistency across panels of an episode (PuLID validation)
  3. Pose / framing / silence-map review per `MANGA_LAYER_RENDER_CONTRACT_SPEC`
  4. Locale parity check (ja_JP vs zh_TW vs en_US per same panel)
  5. WEBTOON vertical-scroll + KDP paperback PDF QA before brand-admin v2 ZIP build
- **Top 5 required skills:** Visual review at speed; manga reading fluency (esp. iyashikei / cultivation / battle genres); image-defect recognition (anatomical correction targets); JSON/YAML metadata literacy; pattern-drift detection
- **Top 5 nice-to-have:** Japanese / Mandarin / Cantonese reading; previous editor experience at a manga publisher; ComfyUI hands-on; Pixiv / WEBTOON awareness
- **Recommended Google course:** `Google Career Certificate` foundation + external `Visual Storytelling for Manga` (any reputable) `[pending cross-ref]`
- **First 30-day deliverable:** ep_002 V5.1 full-episode QA pass; 1 per-brand same-character cross-panel distinctness audit; 1 anatomical correction edge case filed

### Role 9 — QA / Verification (audiobook listening + storefront smoke)

> Combined at endless tier with a clear split if cohort grows.

- **Skill-level entry point:** Entry–Intermediate
- **Subsystem ownership:** audiobook_pipeline (QA), podcast_pipeline (QA), storefront (purchase smoke)
- **Reports-to:** Audiobook Voice + Mix Lead + Senior Engineer (brand_admin) (storefront half)
- **Pearl agent counterpart:** Pearl_Audio (emerging) + Pearl_Prez (storefront share)
- **Top 5 responsibilities:**
  1. Listen-through sample of every audiobook + podcast before brand-admin v2 ZIP ship
  2. Loudness (EBU R128) + ID3-tag + chapter-marker validation
  3. Storefront purchase smoke (Cloudflare Worker + Snipcart) end-to-end weekly
  4. Refund-rate review; flag refund-rate spikes per locale × platform
  5. Voice-consistency audit across multi-book series under same brand
- **Top 5 required skills:** Ear for audio defects (clicks, sibilance, loudness); checkout flow testing; CJK comprehension (at least 1 locale); structured bug-filing; multi-platform audio (Audible, Apple Books, Google Play, Spotify, Ximalaya)
- **Top 5 nice-to-have:** Audio engineering basics; e-commerce QA background; Snipcart / Stripe / Razorpay familiarity; refund-policy literacy
- **Recommended Google course:** `Google IT Support Professional Certificate` + foundation Coursera `Audio Engineering` `[pending cross-ref]`
- **First 30-day deliverable:** 1 full multi-locale audiobook QA pass; 1 storefront-purchase smoke runbook stood up; refund-rate baseline established

### Role 10 — Marketing / Brand Ops

- **Skill-level entry point:** Entry–Intermediate
- **Subsystem ownership:** marketing, brand_admin (ops share), dashboard (share), music_mode (curation share)
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Marketing + Pearl_Brand (emerging) + Pearl_Prez (shared)
- **Top 5 responsibilities:**
  1. 25-brand themes + 48 Social CTA registry maintenance
  2. Funnel ops: freebie → email seq → book CTA; GHL + GA4 wiring
  3. Brand-admin v2 weekly weekly_packages directory shepherding (operator-facing)
  4. CTA cutover ops (per `feedback_message_terseness` for messaging discipline)
  5. Music mode brand integration V1 freebie funnel + first-real-artist seed
- **Top 5 required skills:** Email marketing tooling (GHL); GA4/GTM; CTA copywriting (channel-specific); brand voice consistency; YAML/JSON config editing
- **Top 5 nice-to-have:** SEO; SQL for funnel-metrics queries; Figma; influencer/content-creator outreach; cross-locale marketing
- **Recommended Google course:** `Google Digital Marketing & E-commerce Professional Certificate` `[pending cross-ref]`
- **First 30-day deliverable:** 5 brand themes authored; 1 funnel end-to-end smoke (freebie → email → book); 48 Social CTA inventory audited

### Role 11 — Business Analyst

> Operator-named: *for catalog economics, 800-config decisions, pricing strategy.*

- **Skill-level entry point:** Intermediate–Senior
- **Subsystem ownership:** recommendations (decision-support), brand_admin (economics), marketing (pricing)
- **Reports-to:** Project Manager (with operator visibility)
- **Pearl agent counterpart:** Pearl_PM + Pearl_Research (catalog economics share)
- **Top 5 responsibilities:**
  1. 800 high-confidence configs decision-modeling (brand × topic × persona × format × locale)
  2. Per-platform economics: KDP vs WEBTOON vs Audible vs Spotify margin + payout dynamics
  3. Pricing strategy + price-experiment design
  4. Pearl_News + Pearl_Prime revenue projector calibration (revenue_forecast_2026)
  5. Catalog allocation: 37-brand × 4-axis × locale matrix economic ranking
- **Top 5 required skills:** SQL + Python data analysis; spreadsheet modeling; pricing-elasticity intuition; KDP/Audible/Apple/Google self-publishing economics; written brief discipline
- **Top 5 nice-to-have:** R/statsmodels; A/B test design; Tableau/Looker; international royalties (CJK/EU); Pearl_Research artifact familiarity
- **Recommended Google course:** `Google Data Analytics Professional Certificate` + `Advanced Data Analytics Professional Certificate` `[pending cross-ref]`
- **First 30-day deliverable:** 800-config catalog economic ranking v0 (top 50 configs identified); 1 pricing-experiment proposal; per-platform margin spreadsheet

### Role 12 — Research / Editor

- **Skill-level entry point:** Intermediate
- **Subsystem ownership:** teacher_mode, ei_v2, pearl_news (research share), atom authoring
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Editor + Pearl_Research + Pearl_Writer (shared)
- **Top 5 responsibilities:**
  1. Teacher_banks/<teacher>/doctrine.yaml maintenance + atom authoring under HOOK-SCENE-FIRST-01 + TEACHER-MODE-WRAPPER-SEMANTICS-01
  2. Citation-gap closing (RESEARCH_CITATION_GAP_DEV_SPEC; ~18 §A items still open)
  3. EI v2 KB activation + learner-feedback queue health
  4. Pearl News research seam — find 4-layer source provenance per article (news + youth + teacher + SDG)
  5. Atom-bank curation: QUOTE/REFLECTION/INTEGRATION orphan migration; HOOK P0/P1/P2 batches
- **Top 5 required skills:** Research methodology + source verification; editorial QA across genres; YAML atom-bank editing; LLM prompt engineering (Claude subagents via Pearl_Writer); cross-cultural literacy
- **Top 5 nice-to-have:** Citation-management tools; Japanese / Mandarin / Cantonese reading; academic publishing familiarity; bibliographic norms; teacher_bank doctrine literacy
- **Recommended Google course:** `Google Career Certificate` foundation + Coursera `Library Research` / `Editing for Writers` `[pending cross-ref]`
- **First 30-day deliverable:** 5 citation gaps closed; 1 teacher_bank doctrine pass on an undersourced teacher; 20 HOOK atom scene-first rewrites queued

### Role 13 — Localization (per-locale)

> ja_JP / zh_TW / zh_CN / ko_KR — at endless tier this is 1.5-2.0 FTE split per-locale; at lean tier this becomes contractor-per-batch.

- **Skill-level entry point:** Intermediate (native speaker required) + Senior at lead
- **Subsystem ownership:** translation, pearl_news (translation share)
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_Localization + Pearl_News (translation share)
- **Top 5 responsibilities:**
  1. Per-locale atom translation (Qwen2.5 baseline + human polish for cultural register)
  2. Locale-12 expansion regen-check (dry-run mode per PR #1369)
  3. ja_JP-specific battle/cultivation/iyashikei register coexistence
  4. zh_CN gray-zone distribution scripts/publish/zh_cn_release.py + AI-disclosure gating
  5. CJK6 cultural-register QA for manga lettering + audiobook narration scripts
- **Top 5 required skills:** Native-level locale reading + writing; cultural register intuition; YAML editing; manga genre literacy in locale; collaboration with Pearl Star (Qwen) baseline output
- **Top 5 nice-to-have:** Japanese manga industry contacts; Mandarin literary register depth; ko_KR market awareness; Cantonese as second locale; localization tooling (Crowdin / Smartling)
- **Recommended Google course:** `Google Project Management` (coordination) + Coursera `Localization Project Management` `[pending cross-ref]`
- **First 30-day deliverable:** 1 full ja_JP atom locale pass; 1 zh_TW pose-library translation pass; locale parity gap audit

### Role 14 — Generalist / Reader-Reviewer (no-skill entry)

> Operator-named: *"no skills, so they're going to have to get a certificate course, but they can definitely help with like reading books, doing QA, basic marketing"*

- **Skill-level entry point:** **No-skill** (course-required onramp)
- **Subsystem ownership:** None primary; rotating QA across pearl_prime, manga_pipeline, audiobook_pipeline, marketing
- **Reports-to:** Project Manager (with rotation through specialist leads)
- **Pearl agent counterpart:** Cross-rotational — supports Pearl_Editor, Pearl_Brand, Pearl_Author
- **Top 5 responsibilities:**
  1. Read 1-2 books / week + file structured feedback in ACCEPTANCE_SCORECARD shape
  2. Light QA passes (smoke check audiobook chapter markers; download a brand-admin v2 ZIP)
  3. Social-CTA basic posting + scheduling support
  4. Cataloging: tag artwork, organize image banks, sample brand identity assets
  5. Earn certificate within first 90 days → migrate to specialist track
- **Top 5 required skills:** Reading comprehension; English fluency; written-feedback discipline; willingness to learn; reliability
- **Top 5 nice-to-have:** Second language; design sensibility; spreadsheet basics; Discord / Slack fluency; book-blogging or book-club presence
- **Recommended Google course:** Choice of `Google Career Certificate` (any track) — IT Support, Data Analytics, UX Design, Digital Marketing, or Project Management. Operator-funded. `[pending cross-ref]`
- **First 30-day deliverable:** 4 books read + scored; 1 course enrolled-in (within Google Career Certificate); 1 brand-admin v2 weekly smoke pass

### Role 15 — DevOps / CI / Governance

- **Skill-level entry point:** Intermediate–Senior
- **Subsystem ownership:** pearl_devops, integrations (CI share)
- **Reports-to:** Project Manager
- **Pearl agent counterpart:** Pearl_DevOps (emerging) + Pearl_GitHub (shared)
- **Top 5 responsibilities:**
  1. Push-guard + preflight + branch-protection-ruleset upkeep per `BRANCH_PROTECTION_REQUIREMENTS.md`
  2. CI baseline (Core tests + Release gates + Verify governance + cover_art); LFS health
  3. PR governance review automation (`scripts/ci/pr_governance_review.py`) + Pearl_PM + Pearl_Architect gate
  4. Weekly cron health (brand-admin v2 + podcast-weekly + audiobook); GitHub Actions runner contention
  5. Audit_llm_callers + Tier policy enforcement (no paid API keys in repo per `CLAUDE.md`)
- **Top 5 required skills:** GitHub Actions + workflows; Cloudflare Pages + Workers; Python CI tooling; LFS + repo-size hygiene; security-baseline awareness
- **Top 5 nice-to-have:** Pearl Star SSH + Ollama; self-hosted runner ops; Snipcart + Stripe webhook validation; SOC2 baseline; Kubernetes (for any cloud migration)
- **Recommended Google course:** `Google Cloud DevOps Engineer` + `Cybersecurity Professional Certificate` `[pending cross-ref]`
- **First 30-day deliverable:** Branch protection extension landed; 1 stale ws closed; weekly cron green for 1 consecutive week

### Role 16 — Audiobook Voice + Mix Lead

- **Skill-level entry point:** Intermediate–Senior (and/or contractor at lean tier)
- **Subsystem ownership:** audiobook_pipeline, podcast_pipeline (shared)
- **Reports-to:** Video Productionization Lead + Project Manager
- **Pearl agent counterpart:** Pearl_Audio (emerging) + Pearl_Video (shared)
- **Top 5 responsibilities:**
  1. CosyVoice2 + Edge TTS + ElevenLabs ops; voice clone reference library curation
  2. ECAPA verification + 480-narrator slot maintenance; voice-diversity matrix upkeep
  3. M4B + chapter marker authoring; mp3 + ID3 + loudness normalization
  4. Per-locale narration style guides (en-US, ja_JP, zh_TW, zh_CN, ko_KR)
  5. CJK CosyVoice2 live smoke on Pearl Star
- **Top 5 required skills:** Voice direction; multi-locale audio; FFmpeg + sox; voice-clone tooling; loudness/EBU R128
- **Top 5 nice-to-have:** Native CJK speaker; ProTools/Logic familiarity; audiobook production background; ID3 + DRM platform-specific norms
- **Recommended Google course:** `Google IT Automation with Python` + external `Audio Engineering Society` resources `[pending cross-ref]`
- **First 30-day deliverable:** 1 audiobook full pipeline shipped (en-US); 1 CJK CosyVoice2 smoke green; voice-diversity matrix audited

---

## §3. Lean-team roster — 5.5-6.0 FTE minimum-viable

> Operator framing: *"What is the leanest team? Like one PM, one senior developer, two QA, one marketer."*

### Headcount (totals 5.5-6.0 FTE)

| # | Role | FTE | Subsystem coverage (allocation %) | Pearl agent shadows |
|--:|------|----:|---------------------------------|---------------------|
| 1 | **Project Manager** | 1.0 | coordination 60% / business-analyst 25% / storefront ops 15% | Pearl_PM, Pearl_Architect, Pearl_Prez (storefront share) |
| 2 | **Senior Developer (full-stack)** | 1.0 | core_pipeline 30% / manga_pipeline 25% / integrations 20% / pearl_devops 15% / brand_admin 10% | Pearl_Prime, Pearl_Dev, Pearl_Int, Pearl_DevOps, Pearl_GitHub |
| 3 | **QA Lead (prose + audio)** | 1.0 | core_pipeline+pearl_prime QA 50% / audiobook+podcast QA 30% / teacher_mode atom QA 20% | Pearl_Editor (shared), Pearl_Audio (shared) |
| 4 | **QA Lead (manga + storefront smoke)** | 1.0 | manga_pipeline QA 50% / storefront purchase smoke 25% / brand-admin v2 ZIP QA 25% | Pearl_Author (shared), Pearl_Brand (shared) |
| 5 | **Marketer (Brand Ops + Funnel)** | 1.0 | marketing 50% / brand_admin ops 25% / dashboard 15% / music_mode curation 10% | Pearl_Marketing, Pearl_Brand, Pearl_Prez (shared) |
| 6 | **Research/Editor (half-FTE)** | 0.5 | teacher_mode 60% / ei_v2 25% / pearl_news translation 15% | Pearl_Editor, Pearl_Research, Pearl_Writer, Pearl_News |

**Localization & Audiobook Voice:** **contractor-per-batch** at lean tier. ja_JP / zh_TW / zh_CN spot-engaged when locale launch fires. Audiobook voice clone reference library + ElevenLabs polish via contractor when production push.

### Per-week calendar sketch (lean team)

#### Project Manager
- **Mon AM:** Operator standup + week's merge train queue; review `ACTIVE_WORKSTREAMS.tsv`
- **Mon PM:** Storefront ops + cap-entry routing decisions
- **Tue:** Brand-admin v2 weekly cron QA + 800-config catalog economic decision modeling
- **Wed:** Cross-team standup with all 5 leads + blocker unblocking
- **Thu:** Pricing / per-platform economics + business-analyst mode
- **Fri:** Retro + next-week prep + ws-closure pass + open-PR backlog review

#### Senior Developer
- **Mon:** Core_pipeline bestseller pipeline Phase 2 wiring
- **Tue:** Manga_pipeline V2 layered render dispatch + ep dispatch
- **Wed:** Integrations (credential rotation, RunComfy spend, CF + Snipcart)
- **Thu:** Pearl_DevOps CI gate maintenance + governance enforcement
- **Fri:** Brand_admin v2 cron + per-platform download route + tech-debt batch

#### QA Lead (prose + audio)
- **Mon:** Read 2 sample books per ACCEPTANCE_SCORECARD; file 3 register-gate edge cases
- **Tue:** Listen-through 2 audiobook samples; file loudness/ID3/chapter-marker findings
- **Wed:** Teacher_mode atom QA pass (HOOK / TEACHER_DOCTRINE / REFLECTION batches)
- **Thu:** Podcast (MP3 + show notes) QA across 3 brands
- **Fri:** Bug-triage with Senior Dev; aggregate weekly QA verdict for the Friday retro

#### QA Lead (manga + storefront smoke)
- **Mon:** Read latest manga episodes (en_US + 1 CJK locale) per panel-review checklist
- **Tue:** Character-individuation + face-lock distinctness audit (3 brands)
- **Wed:** Storefront purchase smoke end-to-end (CF + Snipcart + checkout flow + refund path)
- **Thu:** Brand-admin v2 ZIP QA across 4 axes × sample brands
- **Fri:** Refund-rate review + bug triage + Friday retro

#### Marketer
- **Mon:** 25-brand themes authoring (1-2 brands/week)
- **Tue:** Funnel ops + GHL email seq health + GA4 tracking
- **Wed:** 48 Social CTA registry maintenance + cross-platform posting
- **Thu:** Brand-admin v2 weekly_packages shepherding (operator-facing)
- **Fri:** Music_mode curation + first-real-artist work + retro

#### Research/Editor (0.5 FTE — Mon/Wed/Fri)
- **Mon:** Citation-gap closure + EI v2 KB pass
- **Wed:** Teacher_bank doctrine maintenance (1 teacher/week deep pass)
- **Fri:** Pearl News research seam (4-layer source provenance) + atom batch curation

### What's GIVEN UP at lean-team headcount

- **Video productionization slows.** No dedicated Video Lead → Teacher × manga 30s video V1 ships at 1 deliverable / 2 weeks vs 1 / week endless. CJK narration wiring is a 2-quarter project not a 1-quarter.
- **Localization becomes batch-only.** ja_JP / zh_TW / zh_CN launches happen contractually per batch (4-6 week lead time); no continuous locale-12 expansion. zh_CN gray-zone distribution defers.
- **Pearl News slips to weekly cadence (not daily).** No dedicated News Editor → Pearl_News covers only top stories; deep-research engine runs every other day.
- **Music_mode stays single-musician.** First-real-artist seed lands; 38-brand catalog stays in registry but no per-brand campaign execution.
- **Recommendations stays reactive.** No active scoring-weight evolution; recommender promotion is on-demand only.
- **Manga tech depth is the single Senior Dev's bandwidth.** Manga V2 Phase D-E (anatomical correction + re-render smoke) slips to operator-attended Pearl Star sessions only; weekly 37-brand fan-out caps at ~10 episodes / week vs 37+ endless.
- **No business analyst formalism.** 800-config decisions stay PM-eyeballed not economically modeled.
- **No no-skill onramp cohort.** Reader-reviewer track is contractor-per-book or community-volunteer only.
- **Phase A storefront launch risk:** lean team can ship Phase A (storefront V1 smoke + brand-admin v2 1 axis) but Phase B (37-brand × 4-axis full storefront) needs +2 FTE before promise to operator.

### Hire-order ladder (lean → endless)

When the lean team grows, hire in this order:

1. **Manga Tech Lead** (Staff+). Unblocks 49-ws Pearl_Dev surface area; halves Senior Dev's load; enables Manga V2 Phase D-E.
2. **Video Productionization Lead** (Senior). Productionizes the video stuff that "needs to be productionized."
3. **Localization (ja_JP first)** (Intermediate, native). CJK6 locale launches become continuous not batch.
4. **Research/Editor → full FTE (1.0)**. Citation gaps close at sustainable rate; teacher_bank doctrine pass weekly.
5. **Marketer → +1 (additional FTE)**. 25-brand themes authoring stays ahead of catalog scale; funnel ops splits from brand-admin v2 ops.
6. **DevOps / CI / Governance Lead** (Senior). Splits CI/governance burden out of Senior Dev's bandwidth; releases weekly cron green for 4-week streaks.
7. **Business Analyst** (Intermediate–Senior). 800-config economic modeling becomes data-driven; pricing experiments formalized.
8. **Audiobook Voice + Mix Lead** (Senior or contractor). Continuous voice + mix ops; CJK CosyVoice2 live; refund-rate stays trended.
9. **Pearl News Editor + Translator pair** (Intermediate). Daily cadence restored; CJK translation seam continuous.
10. **Generalist / Reader-Reviewer cohort** (no-skill, 1-3 contributors). Operator-funded course onramp; QA cohort doubles; basic marketing scaled.

By hire #10, the team is at **~12-13 FTE**, which is the lower bound of the endless-team realistic floor.

---

## §4. Org-chart sketches

### Endless team (16 roles, ~15-20 FTE)

```
Operator (Ahjan)
└─ Project Manager (1.0)
   ├─ Manga Tech Lead (1.0)        ── QA (manga, 0.5-1.0) ── Localization-ja_JP (1.0)
   ├─ Video Productionization Lead (0.5-1.0) ── Audiobook Voice + Mix (1.0)
   ├─ Senior Engineer (core_pipeline, 1.5-2.0) ── QA (prose, 0.5-1.0) ── Research/Editor (1.0-1.5)
   ├─ Senior Engineer (integrations, 0.5-1.0)
   ├─ Senior Engineer (brand_admin + dashboard, 0.5-1.0) ── QA (audiobook + storefront, 0.5)
   ├─ Marketer (Brand Ops + Funnel, 1.0-1.5) ── Music Mode Curation (0.5)
   ├─ DevOps / CI / Governance (1.0)
   ├─ Business Analyst (0.5-1.0)
   ├─ Pearl News Editor + Translator (1.0-1.5)
   ├─ Localization-zh_TW (0.5)
   ├─ Localization-zh_CN (0.5)
   └─ Generalist / Reader-Reviewer cohort (1.0-2.0, no-skill onramp)
```

### Lean team (5.5-6.0 FTE)

```
Operator (Ahjan)
└─ Project Manager (1.0)
   ├─ Senior Developer (full-stack, 1.0)
   ├─ QA Lead (prose + audio, 1.0)
   ├─ QA Lead (manga + storefront smoke, 1.0)
   ├─ Marketer (Brand Ops + Funnel, 1.0)
   └─ Research/Editor (0.5)

Contractors (per-batch):
   ├─ Localization (ja_JP / zh_TW / zh_CN per-launch)
   └─ Audiobook Voice + Mix (per push)
```

---

## §5. Skill-level entry-point mosaic

| Entry point | Roles | Headcount target (endless) | Upgrade path (Google Career Certificate or course → next tier) |
|------------|-------|---------------------------:|-------------------------------------------------------------|
| **No-skill** | Generalist / Reader-Reviewer | 1-3 (cohort) | Google Career Certificate (any track) → Intermediate role in same track |
| **Entry** | QA (prose), QA (manga), QA (audiobook + storefront), Generalist (post-cert) | 2-3 | Coursera `Editing for Writers` or `Audio Engineering` → QA Lead (Intermediate) |
| **Intermediate** | Marketer, Research/Editor, Localization, QA Leads, Senior Engineer (brand_admin) starting tier | 4-6 | Google Digital Marketing + 2 years experience → Senior Marketer / Brand Ops Lead |
| **Senior** | PM, Sr Engineer (core / integrations / brand_admin), Video Productionization Lead, DevOps, Audiobook Voice + Mix Lead | 5-7 | Google Cloud Engineer + spec-authoring practice → Staff+ |
| **Staff+** | Manga Tech Lead | 1 | External `Practical Deep Learning for Coders` (fast.ai) + ML papers → Principal |

**Operator quote anchor:** *"low skill to high skill"* — the mosaic spans no-skill (course-onramp) → staff+ (Manga Tech Lead) across the 16 endless-team roles.

---

## §6. Pearl agent ↔ human role pairing table

> Every Pearl_* agent maps to ≥1 human role; every human role pairs to ≥1 Pearl agent. Some Pearls are covered by 2+ humans; some humans cover 2+ Pearls.

| Pearl agent | Primary human role | Secondary human role(s) | Notes |
|-------------|-------------------|------------------------|-------|
| Pearl_PM | Project Manager | Business Analyst (decision-support) | Operator-named PM role |
| Pearl_Architect | Project Manager (advisor) | Senior Engineer (core_pipeline) for spec-translation | Cap-entry authoring is PM-Architect joint |
| Pearl_Prime | Senior Engineer (core_pipeline) | QA (prose), Research/Editor | Multi-spec ownership; pearl_prime + core_pipeline + podcast_pipeline |
| Pearl_Dev | Senior Engineer (core_pipeline) at lean; Manga Tech Lead at endless | Senior Engineer (integrations), Senior Engineer (brand_admin) | Pearl_Dev's 49-ws load splits 3-way at endless |
| Pearl_Writer | Research/Editor | Generalist (reading-QA share) | Atom authoring + ad-hoc prose |
| Pearl_Editor | Research/Editor | QA (prose) | Teacher_mode + music_mode |
| Pearl_News | Pearl News Editor + Translator (endless); Research/Editor (lean) | Localization (translation share) | Daily cadence at endless; weekly at lean |
| Pearl_Prez | Marketer (Brand Ops) | Senior Engineer (brand_admin) | Brand admin canonical package upkeep |
| Pearl_Video | Video Productionization Lead | Senior Developer (lean rolls in) | Productionizes the video pipeline |
| Pearl_Localization | Localization (per-locale) | Pearl News Editor + Translator (share) | ja_JP first; zh_TW, zh_CN, ko_KR ladder |
| Pearl_Marketing | Marketer (Brand Ops + Funnel) | Generalist (basic marketing share) | Funnel ops; CTA registries |
| Pearl_Int | Senior Engineer (integrations) | DevOps (credential rotation share) | API + credential surface |
| Pearl_Research | Research/Editor | Business Analyst (citation share) | EI v2 + citation gaps |
| Pearl_GitHub | DevOps / CI / Governance | Senior Developer (lean rolls in) | Push-guard + preflight + ruleset |
| **Pearl_DevOps** *(emerging)* | DevOps / CI / Governance | Senior Engineer (integrations) | Not in agent_registry.yaml; observed in 9 ws's; cap-entry candidate |
| **Pearl_Brand** *(emerging)* | Marketer (Brand Ops) | Senior Engineer (brand_admin) | Not in agent_registry.yaml; observed in 9 ws's; dashboard owner per DASH-02 |
| **Pearl_Author** *(emerging)* | Manga Tech Lead (manga authoring share) | Research/Editor (book authoring share) | Not in agent_registry.yaml; observed in manga + book ws's |
| **Pearl_Audio** *(emerging)* | Audiobook Voice + Mix Lead | QA (audiobook share) | Not in agent_registry.yaml; observed in 2 audiobook + 1 podcast ws |

**Multiplicity examples:**
- *One human covers multiple Pearls (lean):* Senior Developer covers Pearl_Prime + Pearl_Dev + Pearl_Int + Pearl_DevOps + Pearl_GitHub (5 Pearls in 1.0 FTE).
- *One Pearl needs multiple humans (endless):* Pearl_Dev splits across Manga Tech Lead + Senior Engineer (core_pipeline) + Senior Engineer (brand_admin) + Senior Engineer (integrations).

---

## §7. Open questions for operator

Numbered for operator answer-by-row.

1. **Q1 — agent_registry.yaml amendment.** Pearl_DevOps, Pearl_Brand, Pearl_Author, Pearl_Audio appear in 20+ workstreams collectively but are absent from `config/agents/agent_registry.yaml` (14-agent canon). Promote to the registry? Hold as emerging? *(Recommendation: promote; route via Pearl_Architect AMENDMENT after this session.)*
2. **Q2 — storefront subsystem amendment.** 7+ in-flight storefront branches but no row in `SUBSYSTEM_AUTHORITY_MAP.tsv` and no `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md`. Add subsystem row? Author spec? *(Recommendation: yes, both; route via separate Pearl_Architect AMENDMENT.)*
3. **Q3 — FTE vs contractor preference.** Lean team assumes Localization + Audiobook Voice are contractor-per-batch. Is that operator-acceptable, or is FTE preferred for locale stability and voice continuity?
4. **Q4 — Remote vs hybrid.** Pearl Star sits in operator's location (ComfyUI runs require SSH proximity for some manga ops). Is the team fully remote, hybrid Asia-aligned (for CJK locale leads), or operator-collocated for ≥2 roles?
5. **Q5 — Salary band targets.** Need operator's band-by-tier (no-skill, entry, intermediate, senior, staff+) before recruiting can run. US-equivalent? Adjusted-by-region?
6. **Q6 — Equity / part-time options for no-skill onramp contributors.** Operator's quote re. course-required Generalists implies an apprenticeship-style structure. Is operator-funded course + part-time stipend acceptable, or salaried-only?
7. **Q7 — Manga Tech Lead recruiting reality.** Staff+ ML/ComfyUI/PuLID/LoRA-training depth is a thin labor market. Recruit from manga industry (visual editor migrating into ML)? AI/ML community (Anime AI Twitter sphere)? Or contract a senior consultant for 6 months until in-house grows? *(Recommendation: 6-month consultant + in-parallel intermediate hire who shadows.)*
8. **Q8 — Lean team Phase A storefront promise.** Operator should confirm: is lean-team Phase A (storefront V1 smoke + brand-admin v2 1 axis) the merge promise, or does operator want Phase B (37-brand × 4-axis full storefront) at lean tier? If Phase B, +2 FTE required.
9. **Q9 — Onboarding curriculum.** Should onboarding be operator-authored or Pearl_Architect-routed? Cross-link to `[pending cross-ref]` Pearl_Research contributor-learning-pathways ws output once landed.
10. **Q10 — Pearl_News operating mode at lean tier.** Lean team puts Pearl_News work on Research/Editor's 0.5 FTE shoulders → daily cadence becomes weekly. Operator-acceptable? Or hire Pearl News Editor first ahead of other ladder steps?

---

## §8. Cross-references to existing cap entries / governance docs

- `docs/PEARL_ARCHITECT_STATE.md` — cap-entry index (BR-CANON-01, BR-CANON-02, DASH-02, MUSIC-MODE-V1-01, MANGA-LAYERED-PIPELINE-V2-01, WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01, etc.)
- `docs/PEARL_PM_STATE.md` — Phase 1 → Phase 2 P0 snapshot (2026-05-10)
- `docs/AGENT_SYSTEM_AUDIT_2026_04.md` — prior 14-agent analysis (extended here to human counterparts)
- `docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md` — proposed subsystem rows (github_operations, consumer_marketing, repo_coordination)
- `docs/OWNERSHIP_MATRIX.md` — repo and path-family ownership boundaries
- `docs/SESSION_UNITY_PROTOCOL.md` — STARTUP_RECEIPT / CLOSEOUT_RECEIPT discipline
- `docs/SYSTEMS_V4.md` — systems-level overview
- `BRAND_ADMIN_CANONICAL_PACKAGE.md` — brand admin authority
- `CLAUDE.md` — Tier policy (Tier 1 Claude Code for operator-present; Tier 2 Gemma/Qwen for unattended)
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` — 19-row subsystem source of truth
- `artifacts/coordination/ACTIVE_PROJECTS.tsv` — 12 active projects
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — 210 ws's (116 completed)
- `config/agents/agent_registry.yaml` — 14-agent canonical roster (Q1 amendment candidate)
- `SUBSYSTEM_HEALTH_AUDIT.md` (this dir) — companion audit driving role demand
- `HUMAN_TEAM_STRUCTURE.pptx` (this dir) — operator-facing deck
- `[pending cross-ref]` `artifacts/research/contributor_learning_pathways_20260606/` — Pearl_Research parallel ws (Google course recommendations per role)

---

## Closing notes

This document is **analysis + planning only.** No cap entries authored. No `agent_registry.yaml` changes. No subsystem rows added. Any role that requires cap-entry change → Q1-Q2 in §7 above; route via separate Pearl_Architect AMENDMENT session after operator approval.

The endless-team roster is sized to **15-20 FTE** spanning no-skill → staff+. The lean-team roster is sized to **5.5-6.0 FTE**, covers ~80% of sustain demand, and is **explicitly insufficient for Phase B storefront launch** without +2 FTE.

Operator next actions:
- Review the 16 endless-team JDs + lean-team allocation
- Answer Q1-Q10 in §7
- If endless / lean approved: route Pearl_PM ws to wire lean-team first-hire JDs into a recruiting pipeline + cross-link to Pearl_Research contributor-learning-pathways deck
