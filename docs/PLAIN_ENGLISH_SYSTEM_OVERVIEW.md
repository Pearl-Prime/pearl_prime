# Plain-English System Overview

**Audience:** new contributors, operator stakeholders, anyone trying to understand
"what is Phoenix Omega in 5 minutes."
**Companion docs:** `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md`, `docs/FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md`, `docs/FULL_REPO_ARCHITECTURE_MAP_2026-04-26.md`.

---

## 1. What is Phoenix Omega?

Phoenix Omega is a content production system that turns research, brand strategy,
and writer specs into shipped books, manga, news, audiobooks, podcasts, and
marketing across **5 locales** (en_US, ja_JP, zh_TW, zh_CN, ko_KR).

It's organized around **brand-attributed teacher-led content**: a brand is a
domain authority (e.g., "anxiety relief"), a teacher is the voice (e.g., "Sarah,
a millennial woman professional"), and the content is the artifact (a book
chapter, a manga panel, a news editorial).

## 2. Who runs it?

A small operator team (Ahjan + Nihala — 2,000 commits across April 2026) plus
a roster of LLM-driven specialist agents:

- **Pearl_Architect** — decides where work belongs (subsystem routing)
- **Pearl_PM** — decides where work continues (active project / workstream)
- **Pearl_Prime** — books pipeline owner
- **Pearl_News** — daily editorial owner
- **Pearl_Manga** — manga pipeline owner
- **Pearl_Brand** — brand wizard + brand admin owner
- **Pearl_DevOps** — CI/CD + storage + infra owner (subsystem identity unresolved as of 2026-04-26)
- **Pearl_GitHub** — repo health + PR landings
- **Pearl_Editor / Pearl_Writer** — content authoring
- **Pearl_Research** — domain-evidence + EI v2

Specialist agents read this overview, then route to their subsystem authority docs.

## 3. The 14 subsystems (and 4 missing/unresolved)

From `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`:

| # | Subsystem | What it owns |
|---|-----------|--------------|
| 1 | core_pipeline | the canonical book-arc system architecture |
| 2 | pearl_prime | book authoring (brand × teacher × topic → chapters) |
| 3 | teacher_mode | teacher banks, pen-name profiles, registry |
| 4 | manga_pipeline | manga generation, lettering, webtoon composition |
| 5 | pearl_news | daily/weekly editorial cycles |
| 6 | translation | locale-specific translation + quality contracts |
| 7 | video_pipeline | FLUX rendering, audiobook style, render params |
| 8 | ei_v2 | quality module (Effortful Imagination v2) |
| 9 | trend_feeds | trend-keyword ingestion + budget guard |
| 10 | recommendations | catalog scoring + hard gates |
| 11 | brand_admin | weekly brand package + canonical brand registry |
| 12 | ite | manga ingestion-and-export |
| 13 | integrations | API credentials + env registry |
| 14 | (implicit) repo coordination | Pearl_PM + Pearl_Architect + Pearl_GitHub |

**Subsystems missing from the authority map (gaps surfaced by this audit):**

- **Pearl_DevOps** — owns 72 CI workflows but has no row
- **Dashboard** — referenced in subsystem field but no entry point exists
- **Audiobook** — has 4 canonical docs (per PR #686 rename) but no subsystem row
- **Podcast** — only research dir; no impl
- **Marketing** — no row (intentionally folded under brand_admin?)

## 4. The data flow (top-down)

1. **Research** → `docs/research/`, `marketing_deep_research/`, `pearl_news/research/`
2. **Brand strategy** → `config/brand_registry.yaml`, `config/brand_management/`
3. **Teacher selection** → `SOURCE_OF_TRUTH/teacher_banks/`, `config/authoring/pen_name_teacher_profiles.yaml`
4. **Story atoms / engine bank** → `atoms/{persona}/{topic}/{engine}/CANONICAL.txt` (17,090 entries; 40% of repo by file count)
5. **Pipeline execution** → `scripts/run_pipeline.py` (canonical CLI), pipeline-specific scripts
6. **Quality gates** → `phoenix_v4/quality/`, `config/quality/`, `phoenix_v4/quality/ei_v2/`
7. **Render** → `scripts/video/`, `phoenix_v4/manga/`, `pearl_news/`
8. **Distribution** → `config/release_velocity/`, R2 storage, KDP / WEBTOON / Apple Books / Spotify / Audible

## 5. The canonical artifact: a book chapter

For Pearl Prime books:
- A book = brand + teacher + topic + locale
- Each book has ~12 chapters
- Each chapter has structured slots: STORY (sec 2/5/9), JOURNEY (sec 4/8), SCENE, etc.
- Slots are filled by either the engine bank (named-character, bestseller-grade)
  or the persona_atom + registry resolver
- See `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` for the slot grid contract

## 6. The canonical artifact: a manga episode

For manga (per PR #682 spec):
- A series = genre × locale × brand
- 12 genre shells × 5 locales × 37 brands = catalog allocation
- Each series has ~12 chapters per Move 1; first chapter ("ep_001") = 32-35 panels
- A chapter has: chapter_script (panel-level YAML) → panel_prompts (FLUX) →
  rendered images → letters/bubbles → webtoon vertical strips → R2 uploads → distribution

## 7. The canonical artifact: a news daily

For Pearl News:
- Daily editorial cycle reads trend feeds + research deep-dives
- Generates a v52-style render with sec-level teacher slots (deterministic per PR #587)
- Live infrastructure runs on Pearl Star (operator's local Mac with Ollama)
- Tier 2 LLMs (Gemma EN / Qwen CJK6) are the runtime per `.github/workflows/llm-policy-enforcement.yml`

## 8. The 5 locales

| Locale | Status |
|--------|--------|
| en_US | full coverage |
| ja_JP | partial (catalog plans exist; some teacher banks; Manga Indies sibling connector pending) |
| zh_TW | strong CJK coverage; 92.1% atoms on main per `ws_cjk_atom_translation_qwen25_20260420` |
| zh_CN | gray-zone distribution per spec OQ-6 with full AI disclosure; ~2,200 atoms pending |
| ko_KR | rendered + held; `distribution_status=hold_pending_market_clearance` |

Each locale has its own quality contract under `config/localization/quality_contracts/`.

## 9. The brand layer (most fractured area in the repo)

Brand is the **content allocation unit**: 37 brands per PR #682, but configs disagree:

- `config/brand_registry.yaml` — 28 brands
- `config/brand_management/global_brand_registry.yaml` — 312 entries (24 archetypes × 13 lanes)
- `BRAND_ADMIN_CANONICAL_PACKAGE.md` — references 36
- PR #682 spec — 37

**This is C-1 in the canonical map. Pearl_Brand reconciliation pending.**

The Brand Wizard (`brand-wizard-app/`) is a React app that generates brand YAMLs.
**88.7% of `brand-wizard-app/` is committed `node_modules/` (6,984 files)** —
PR D1 deletion candidate.

## 10. The teacher layer

12 teachers × 7 engines = 84 profiles per `config/catalog_planning/teacher_brand_lane_assignments.yaml`.

Teachers are pen-name characters (e.g., "Master Wu", "Sarah", "Marcus") authored
across `SOURCE_OF_TRUTH/teacher_banks/`.

For manga, teachers are characters in the story (e.g., the iyashikei protagonist).
For Pearl Prime books, teachers are the implicit narrator-coach.

## 11. Workstream coordination — how work moves

Every active task is tracked in:
- `artifacts/coordination/ACTIVE_PROJECTS.tsv` (5 active rows)
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (~76 rows; 7 schema-malformed per OQ-F)

Pearl_PM resolves overlap. Pearl_Architect resolves authority routing. Pearl_GitHub
lands the PRs. Operator approves anything risky (especially mass deletions, per
`CLAUDE.md` rule 0).

PEARL_PM_STATE.md last_verified is 2026-04-10 (16 days stale — known gap; refresh
PR is GAP-1 in the implementation plan).

## 12. The LLM tier policy

Per `CLAUDE.md`:

- **Tier 1** (Claude Code, operator-present): refactors, features, prose generation
  with human review. **All work in this audit is Tier 1.**
- **Tier 2** (Gemma EN / Qwen CJK6 on Pearl Star, free, unattended):
  scheduled pipelines (weekly manga rollout, nightly regression, Pearl News daily)
- **BANNED**: ANTHROPIC_API_KEY, OpenAI cloud, Google AI, DashScope cloud, Together,
  Replicate, Perplexity, Cohere, Mistral paid. Enforced via
  `.github/workflows/llm-policy-enforcement.yml`.

## 13. Storage architecture

Mixed across 5 backends:
- **GitHub** — code, configs, schemas, docs, story atoms (the 42K tracked files)
- **GitHub LFS** — large binary assets in select dirs
- **Cloudflare R2** — rendered manga panels, webtoon strips, video assets, audiobook masters (per `scripts/artifacts/r2_sync.py`)
- **Backblaze B2** — pivot in progress per session handoffs
- **Local Mac (Pearl Star)** — operator render workspace; SSH'd via `pearlstar.tail7fd910.ts.net`

Credentials registry: `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`.

## 14. Distribution channels

- **Books**: KDP en_US (primary), platform-pending for other locales
- **Manga**: WEBTOON (Canvas en_US first; LINE Manga Indies for ja_JP pending)
- **Audiobooks**: ACX / Audible (en_US live), Apple Books (locales pending)
- **News**: Pearl News Substack-style live render
- **Podcasts**: research only (R-009 missing)
- **Video**: Spotify / TikTok / Reels for marketing

## 15. How to read the rest of this audit

1. **For repo facts** → `artifacts/inventory/full_repo_*_2026-04-26.{csv,md}`
2. **For canonicality decisions** → `docs/FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md`
3. **For deletion plan** → `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md`
4. **For implementation gaps** → `docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md`
5. **For diagrams** → `docs/FULL_REPO_ARCHITECTURE_MAP_2026-04-26.md`
6. **For audit synthesis** → `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md`

For a 5-minute orientation, just this overview + the system audit's §3 health
scorecard is enough.
