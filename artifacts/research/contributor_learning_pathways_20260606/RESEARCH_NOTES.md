# Contributor Learning Pathways — Google × Pearl Prime × Job Market

**Author:** Pearl_Research
**Date:** 2026-06-09
**Branch:** `agent/pearl-research-contributor-learning-pathways-20260606`
**Scope:** Research notes grounding the operator-facing PowerPoint (`CONTRIBUTOR_LEARNING_PATHWAYS.pptx`) and long-form Markdown companion (`CONTRIBUTOR_LEARNING_PATHWAYS.md`) in the same directory.
**Operator question:** "What do people need to learn, how does it help Pearl Prime, and what does it mean for their career?"

---

## Table of Contents

1. [Pearl Prime tech stack inventory](#1-pearl-prime-tech-stack-inventory)
2. [Google learning surfaces inventory](#2-google-learning-surfaces-inventory)
3. [Fit map — course × Pearl Prime utility × subsystem × Pearl agent](#3-fit-map)
4. [Job market table — salary × progression × posting volume × hot factor](#4-job-market-table)
5. [Gap analysis — hot in market, NOT in Pearl Prime today](#5-gap-analysis)
6. [Integration roadmap proposal](#6-integration-roadmap)
7. [Tier-policy guardrails](#7-tier-policy-guardrails)
8. [Recommended sequencing — 30 / 90 / 180 days](#8-recommended-sequencing)
9. [Citations — primary and secondary sources](#9-citations)
10. [Verification flags and uncertainty register](#10-verification-flags)

---

## 1. Pearl Prime tech stack inventory

Pearl Prime is a **deterministic, YAML-driven, Python-first therapeutic content publishing system** with 19 governed subsystems. Inventory is grounded in `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`, `CLAUDE.md`, the canonical specs, `scripts/run_pipeline.py`, `brand-wizard-app/package.json`, and `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`.

### Subsystem → tech-stack mapping

**core_pipeline (Pearl_Prime owner)** — Pure Python 3.11+ with YAML configs. Entrypoint `scripts/run_pipeline.py` implements arc-first 3-stage flow (catalog → format selector → assembly compiler) reading `config/source_of_truth/master_arcs/`, `config/identity_aliases.yaml`, atoms under `atoms/<persona>/<topic>/<engine>/CANONICAL.txt`. PyYAML, asyncio, pathlib, argparse. No database; filesystem-only state. Authority: `specs/PHOENIX_V4_5_WRITER_SPEC.md` (v1.3) + `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`. Six atom types (HOOK / SCENE / STORY / REFLECTION / EXERCISE / INTEGRATION); 20-chapter Pearl Prime structural upgrade adds PIVOT / TAKEAWAY / THREAD / PERMISSION slots. TTS-first prose constraints: ≤12-word teaching sentences, no rhetorical questions, body anchors required, paragraph breaks as breath. Target catalog ~800 high-confidence configs.

**pearl_prime (Pearl_Prime owner)** — Bestseller writing overlay on top of core_pipeline. `phoenix_v4/quality/chapter_flow_gate.py`, `phoenix_v4/qa/book_pass_gate.py`, `chapter_composer`, `bestseller_editor` (per PR #74). Chapter contract: **Orient / Name / Turn / Give / Pull** (5 reader-experience moves). Canonical CLI shape per OVERLAY_SPEC §570-577: spine + production + `--exercise-journeys`.

**teacher_mode (Pearl_Editor owner)** — `SOURCE_OF_TRUTH/teacher_banks/` + `config/authoring/pen_name_teacher_profiles.yaml`. 13 teachers. Teacher pool semantics first-match-deterministic. Atom migration patterns: TEACHER_DOCTRINE / COMPRESSION / REFLECTION.

**manga_pipeline (Pearl_Dev owner)** — V5.1 Qwen-Image-Layered single-render decompose architecture. **Multi-model stack:** Qwen-Image (faces), FLUX.1-dev (backgrounds, 28 steps/3.5 CFG dpmpp_2m karras), Animagine XL 4.0 (B&W panels), PuLID-FLUX-FaceNet (face-lock), ai-toolkit LoRA (12-14 named-cast LoRAs, NOT 200+ catalog). 7-agent pipeline: Visual Identity → Genre → Story Architect → Chapter Writer → Visual → Lettering → Layout → QC. JSON-driven artifacts (style_bible.json, panel_prompts.json, lettering_spec.json, series_memory.json). Path X SSOT: 1,350 series × 5 locales × 18,900 episodes. ComfyUI 0.18.1 + PyTorch 2.11.0+cu130. Cover art = two-stage (FLUX renders imagery only; PIL composites text).

**pearl_news (Pearl_News owner)** — WordPress + Newspaper theme; civic journalism for United Spiritual Leaders Forum. 4-layer blend (News + Youth + Spiritual + SDG). LLM expansion stack: Groq → xAI Grok → Together AI → Qwen/DashScope. Quality gates: `pearl_news/pipeline/quality_gates.py`; editorial firewall YAML; prompts under `pearl_news/prompts/`.

**translation (Pearl_Localization owner)** — `config/localization/locale_registry.yaml` + `config/localization/quality_contracts/`. Qwen 2.5 via Ollama on Pearl Star (default) or DashScope cloud (fallback only). 12 locales total; CJK6 = ja_JP / zh_TW / zh_CN / ko_KR. Golden translation regression + native_prompts_eval_learn.

**video_pipeline (Pearl_Video owner)** — Metadata-driven 11-stage pipeline. JSON schemas under `schemas/video/`. YAML configs under `config/video/` (pacing/captions/motion/music/aspect_ratio_presets/color_grade). FormatAdapter outputs 16:9 / 9:16 / 1:1 from one ShotPlan. Image Bank retrieval-first; generation only on cache miss. R2 upload via wrangler. FFmpeg underneath.

**ei_v2 (Pearl_Research owner)** — Quality engine in `phoenix_v4/quality/ei_v2/`: learner.py, dimension_gates.py, hybrid_selector.py, marketing_lexicons.py, research_lexicons.py. Calibration via `scripts/ci/run_ei_v2_catalog_calibration.py`. Config `config/quality/ei_v2_config.yaml` with research_kb + marketing_sources blocks. **This is Pearl_Research's formal subsystem.**

**trend_feeds (Pearl_Int owner)** — RSS bundle (6 feeds) + SerpApi Google Trends (free tier 250/mo) + Exploding Topics browser scrape (daily scheduled 9:04 AM). 58 keywords, 4-tier system, budget guard at `scripts/feeds/budget_guard.py`.

**recommendations (Pearl_PM owner)** — Phoenix Recommender package (backlog). Phase 1 rules-based scoring; Phase 3 LightGBM ranking when performance data accumulates.

**brand_admin (Pearl_Prez owner)** — `brand_admin.html` + `brand_admin_weekly_os.html` + `brand-wizard-app/`. **Frontend: React 18.3 + react-dom 18.3 + lucide-react + Vite 6.0 + Tailwind 3.4 + PostCSS 8.4 + autoprefixer.** Pure client-side render; no server-side framework. Deployed via GitHub Actions to Cloudflare Pages project `brand-admin-onboarding`.

**ite (Pearl_Dev owner)** — Implicit Therapeutic Engine; `phoenix_v4/manga/ite_pipeline.py`. Gate registry shared at `config/manga/gate_registry.yaml`.

**integrations (Pearl_Int owner)** — Cloud stack: **Cloudflare Pages + Workers + R2 + Workers AI + Tailscale.** Deploy path: PR → merge to main → GitHub Actions → wrangler-action@v3 → live in ~3 min. Secrets in macOS Keychain (operator local) + GitHub repo secrets (CI). Messaging: LINE Messaging API (TW + JP), iMessage, SendGrid/SMTP, GoHighLevel. Trend feeds + SerpApi + RSS.

**pearl_devops (Pearl_DevOps owner)** — GitHub Actions workflows across CI/CD: preflight, push-guard, governance, llm-policy-enforcement, marketing-continuous, marketing-briefs-and-proposals, catalog-book-pipeline, change-impact. Scripts under `scripts/ci/`, `scripts/git/push_guard.py`, `scripts/git/health_check.sh`. Self-hosted runner on Pearl Star. Branch protection ruleset.

**audiobook_pipeline (Pearl_Dev owner)** — Fully automated Qwen comparator loop. Python asyncio with 24 concurrent API calls; 5 hard + 4 scored gates; manual review queue surfaces in PhoenixControl. TTS: CosyVoice2 (CJK6 on Pearl Star :9880) + ElevenLabs (EN paid) + Edge-TTS (free CJK fallback). No Claude at runtime per spec §1.

**marketing (Pearl_Marketing owner)** — `funnel/`, `platform_marketing/`, `somatic_exercise_freebee_apps/`. Freebie + Proof-Loop emails. `config/marketing/consumer_language_by_topic.yaml`. GoHighLevel push. Marketing closed-loop research pipeline (Phase 1 ingest only; promotion artifact-only until gate).

**podcast_pipeline (Pearl_Prime owner, proposed)** — `docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md` + `scripts/podcast/`. Proposed status.

**dashboard (Pearl_Brand owner)** — `brand_admin_v2.html` + `brand-wizard-app/public/exec_catalog_dashboard.html` (4-axis composite: book + manga + podcast + audiobook). Same React + Vite + Tailwind stack as brand_admin.

**music_mode (Pearl_Editor owner)** — `SOURCE_OF_TRUTH/musician_banks/` + `artifacts/musician_survey/SURVEY_TEMPLATE.yaml`. Ride-existing-pipeline architecture. `config/music/music_brand_registry.yaml`. brand_wizard YAML SSOT.

### Cross-cutting tech

- **Languages:** Python 3.11+ (≈90% of repo), JavaScript / JSX, Bash / Zsh, YAML (configs), JSON (artifacts), Markdown (specs)
- **Cloud:** Cloudflare suite (Pages + Workers + R2 + Workers AI; D1 + KV proposed)
- **CI/CD:** GitHub Actions (self-hosted on Pearl Star + GitHub-hosted)
- **Local AI server:** Pearl Star (Ubuntu 24.04, RTX 5070 Ti 16 GB VRAM, 64 GB RAM)
- **AI on Pearl Star:** ComfyUI 0.18.1 + FLUX.1-dev + Qwen-Image + Ollama (qwen2.5:14b + gemma3:27b) + CosyVoice2
- **AI cloud (free/limited tiers only):** Groq + xAI Grok + Together AI + DashScope (CJK fallback)
- **TTS:** ElevenLabs (EN paid) + CosyVoice2 (CJK local) + Edge-TTS (free fallback)
- **Frontend:** React 18 + Vite 6 + Tailwind 3 + lucide-react (no Redux, no Next.js)
- **Secrets:** macOS Keychain (operator) + GitHub repo secrets (CI)
- **Architecture pattern:** YAML SSOT + JSON artifacts + Python deterministic compilers + Path X axis-separation

### LLM Tier Policy (CLAUDE.md — MANDATORY)

- **Tier 1:** Claude Code subscription (operator-present)
- **Tier 2:** Gemma (EN) / Qwen (CJK6) on Pearl Star via Ollama (free, unattended)
- **BANNED in repo code:** `ANTHROPIC_API_KEY` / `CLAUDE_API_KEY` reads, OpenAI cloud, **Google AI cloud (Vertex AI / Gemini API)**, DashScope cloud (for direct repo use), Together cloud, Replicate, Perplexity, Cohere, Mistral paid. Violations are blocked by `.github/workflows/llm-policy-enforcement.yml`. This is the critical constraint that shapes the gap analysis below.

### Gap detected

- `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` referenced in the prompt **does not exist in repo as of 2026-06-09.** No Snipcart / Stripe storefront spec authored yet. Treat as future stack.

---

## 2. Google learning surfaces inventory

Every cited URL was accessed 2026-06-09 unless otherwise noted. Where uncertain, flagged `[verify]`.

### A. Google Career Certificates (Coursera-hosted)

Pricing pattern: **$49 USD/month after 7-day free trial in U.S./Canada**, or included in Coursera Plus ($59/month or $399/year). Most certificates complete in 3-6 months at ~10 hr/week (~120-180 hr total). Credential = badge on Credly + ACE® college credit recommendation (up to 15 credits). 70 %+ of graduates report a positive career outcome within 6 months; aggregate median salary across fields cited at $102K +; 1.7 M+ job postings referenced; 150+ Employer Consortium members.

#### Foundational (6)

1. **Google Data Analytics Certificate** — `coursera.org/google-certificates/data-analytics-certificate` — 3-6 mo / ~180 hr — 4.8★ / 159K reviews — skills: data collection, transformation, visualization, SQL, R, Tableau
2. **Google IT Support Certificate** — `coursera.org/google-certificates/it-support-certificate` — 3-6 mo / ~180 hr — 4.8★ / 188K reviews — skills: troubleshooting, networks, sysadmin
3. **Google Project Management Certificate** — `coursera.org/google-certificates/project-management-certificate` — 3-6 mo / ~180 hr — 4.9★ / 121K reviews — skills: agile, scrum, stakeholder mgmt
4. **Google UX Design Certificate** — `coursera.org/google-certificates/ux-design-certificate` — 3-6 mo / ~180 hr — 4.8★ / 85K reviews — skills: Figma, user research, prototyping
5. **Google Cybersecurity Certificate** — `coursera.org/google-certificates/cybersecurity-certificate` — 3-6 mo / ~180 hr — 4.8★ / 47K reviews — skills: SIEM, Python, Linux, threat investigation; cited median salary $102K +
6. **Google Digital Marketing & E-commerce Certificate** — `coursera.org/google-certificates/digital-marketing-certificate` — 3-6 mo / ~180 hr — 4.8★ / 35K reviews — skills: SEO, paid ads, e-commerce platforms, analytics

#### Advanced / specialized (3)

7. **Google Advanced Data Analytics Certificate** — 1-3 mo (post-foundational) — Python, statistical inference, R, regression, ML modeling
8. **Google Business Intelligence Certificate** — 1-3 mo (post-foundational) — BigQuery, Tableau, dashboards
9. **Google IT Automation with Python Certificate** — 1-3 mo (post-IT-Support) — Python scripting, automation, debugging, Git

#### AI track (3)

10. **Google AI Professional Certificate** — `coursera.org/professional-certificates/google-ai` — 7-module program, ~10 hr fast-completion / 3-6 mo for ~10 hr/wk — **Feb 2026 launch**, 635K + enrollees, 4.8★ / 1,174 reviews — includes 3 mo free Google AI Pro — skills: AI fluency, hands-on with Gemini, building AI-powered solutions, AI agents
11. **Google AI Essentials Certificate** — `coursera.org/google-certificates/ai-essentials-google` — <5 hr — skills: gen AI fundamentals, prompt engineering, responsible AI, productivity workflows
12. **Accelerate Your Job Search with AI Specialization** — `coursera.org/google-specializations/google-accelerate-your-job-search-with-ai` — <10 hr — skills: Gemini + NotebookLM job search, skills assessment, interview prep

#### Industry stack-ons (5)

13. **Data Analytics: Finance** (Gies College of Business)
14. **Data Analytics: Public Sector with R** (University of Michigan)
15. **IT Support: Healthcare** (Johns Hopkins)
16. **Project Management: Construction** (Columbia Engineering)
17. **Project Management: Sustainability** (Arizona State)

### B. Google Cloud Certifications (cloud.google.com/learn/certification)

Verified subagent dive 2026-06-09. **Pricing pattern: Foundational $99 / Associate $125 / Professional $200.** Validity: Foundational and Associate = 3 yrs; Professional = 2 yrs. Exam length 120 min (Foundational + Generative AI Leader = 90 min). Prep on Google Cloud Skills Boost (`skills.google` — formerly `cloudskillsboost.google`, 308-redirected as of 2026-06-09).

#### Foundational (2)

18. **Cloud Digital Leader** — 90 min / $99 — digital transformation, AI innovation, infra/app modernization, trust & security
19. **Generative AI Leader** — 90 min / $99 — 50-60 MCQ, 75% pass — Gen AI fundamentals, Google Cloud gen AI offerings, business strategies for gen AI

#### Associate (3)

20. **Associate Cloud Engineer** — 120 min / $125 — set up environment, plan & implement, configure access & security
21. **Associate Data Practitioner** (new 2025) — 120 min / $125 — prepare & ingest data, analyze, orchestrate pipelines, manage data
22. **Associate Google Workspace Administrator** (new; replaces retired Professional Workspace Admin) — 120 min / $125 — users, services, governance, security, endpoints

#### Professional (9)

23. **Professional Cloud Architect** — 120 min / $200 — cloud architecture design, security, compliance, operations
24. **Professional Data Engineer** — 120 min / $200 — design systems, ingest & process, store, prepare, automate
25. **Professional Cloud Developer** — 120 min / $200 — scalable cloud-native apps, GCP service integration including gen AI APIs
26. **Professional Cloud DevOps Engineer** — 120 min / $200 — SRE, CI/CD, observability, performance + cost optimization
27. **Professional Cloud Security Engineer** — 120 min / $200 — access, secure communications, data protection, AI workload security
28. **Professional Cloud Network Engineer** — 120 min / $200 — VPC, managed services, hybrid/multi-cloud, network security
29. **Professional Cloud Database Engineer** — 120 min / $200 — HA DBs, migration, cost-effective DB design
30. **Professional Machine Learning Engineer** — 120 min / $200 — low-code AI architecture, cross-team data/model mgmt, MLOps, AI monitoring
31. **Professional ChromeOS Administrator** — 180 min (90 MCQ + 90 hands-on labs) / $125 — Google Admin Console, ChromeOS fleet deployment, security; hosted at `chromeoscertification.com`, not under cloud.google.com

#### Retired

- **Professional Google Workspace Administrator** — retired Dec 31, 2024; replaced by Associate variant

### C. Google Cloud Skills Boost paths (skills.google)

Free tier (subject to monthly credit cap) + Google Cloud Innovators / Cloud Study Jam offers free access. Major learning paths:

32. AI / ML path
33. Agents path (Vertex AI Agent Builder)
34. Data path
35. Dev Tools path
36. Infrastructure path
37. Productivity path
38. Security path

Plus per-cert prep paths: Cloud Digital Leader (Path 9), Associate Cloud Engineer (Path 11), Pro Cloud Architect (Path 12), Pro Cloud Developer (Path 19), Pro Cloud DB Engineer (Path 22), Workspace Admin (Path 24), Data Practitioner (Path 1336), Generative AI Leader (Path 1951).

Notable: **"Build with Vertex AI" Technical Expert Badge** + **"Intelligent Search Technical Expert Badge"** scheduled to be **retired 2026-06-01**, with new credentials replacing.

### D. Google AI / ML free training (developers.google.com / ai.google)

39. **Machine Learning Crash Course** — `developers.google.com/machine-learning/crash-course` — free, no formal credential — modules: ML models (regression / classification) → data → advanced models (NNs / embeddings / LLM intro) → real-world ML & fairness
40. **Generative AI Learning Path** — Google Cloud Skills Boost — free path covering Vertex AI Gemini, Imagen, prompt design
41. **Google AI hub** — `ai.google/learn-ai-skills/` — landing for Google's free AI training

### E. Skillshop (skillshop.withgoogle.com) — free product certs

42. **Google Ads Search Certification** — free / 75 min exam / 80% pass / 12-month validity
43. **Google Ads Display Certification** — same format
44. **Google Ads Video Certification** — same format
45. **Google Ads Shopping Certification** — same format
46. **Google Ads Measurement Certification** — same format
47. **Google Ads Apps Certification** — same format
48. **Google Ads Creative Certification** — same format
49. **Google Ads AI-Powered Performance Certification** — newer, ties to Performance Max
50. **Google Analytics (GA4) Certification** — same format
51. **Fundamentals of Digital Marketing** (formerly Google Digital Garage flagship) — 40 hr / 17 modules / free / now hosted on Skillshop

### F. Google for Education / Teacher Center

Free indefinitely as of 2026 (new Level 1 & 2; Gemini certifications always free; legacy Level 1/2 fee-based program currently unavailable). Performance-based labs re-introduced in 2026.

52. **Google Certified Educator Level 1** — 25-35 MCQ + performance labs / free / classroom productivity foundations
53. **Google Certified Educator Level 2** — advanced features
54. **Google Certified Trainer** — train other educators on Google for Education
55. **Google Certified Innovator** — high-impact innovation project
56. **Gemini for Educators Certification** — free / Gemini fluency
57. **Generative AI for Educators** — `grow.google/ai-for-educators/` — free

### G. Grow with Google segmented programs (free or low-cost)

58. **AI for Students** — `grow.google/students` — free / AI literacy + skill-building
59. **AI for Small Businesses** — `grow.google/ai-for-small-businesses/` — free / Gemini + Google Workspace for small biz
60. **Google Workspace with Gemini Specialization** — Coursera — paid via $49/mo subscription
61. **Applied Digital Skills** — free curriculum for educators + students (digital literacy + Workspace skills)

**Total Google learning surfaces inventoried: 61** (12 Career Certs + 5 industry stack-ons + 14 Cloud certs + 7+ Skills Boost paths + 3 free AI / ML training surfaces + 10 Skillshop product certs + 6 educator certs + 4 segmented programs).

---

## 3. Fit map

Scoring scale 0-5 for Pearl Prime direct utility:

- **5** = Skill is in active daily use across multiple Pearl Prime subsystems
- **4** = Skill is directly used in one major subsystem
- **3** = Skill is adjacent / supports a Pearl Prime subsystem; trainee could shadow productively
- **2** = Skill teaches general fluency but specific tool not in Pearl Prime stack
- **1** = Tangential — only useful for cross-functional collaboration
- **0** = Banned by Tier policy OR architecture mismatch; learn for career only

Skill-level abbreviations: **NS** = no-skill, **EN** = entry, **IN** = intermediate, **AD** = advanced.

| # | Course / Certificate | Skill level | Utility (0-5) | Hours | Cost | Subsystem served | Pearl agent shadowed | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | Google IT Support Certificate | NS→EN | **3** | ~180 hr | $49/mo | integrations, pearl_devops | Pearl_Int, Pearl_DevOps | Linux fluency + troubleshooting are foundational for Pearl Star ops, Tailscale, Cloudflare wrangler |
| 2 | Google IT Automation with Python | EN→IN | **5** | ~120 hr | $49/mo | core_pipeline, manga_pipeline, audiobook_pipeline, pearl_devops | Pearl_Dev, Pearl_DevOps | **Direct hit.** ~90% of Pearl Prime repo is Python; this is the single highest-utility course |
| 3 | Google Project Management Certificate | NS→EN | **4** | ~180 hr | $49/mo | repo coordination, marketing, brand_admin | Pearl_PM, Pearl_Architect | Workstream tracking maps 1:1 onto `artifacts/coordination/ACTIVE_PROJECTS.tsv` + `ACTIVE_WORKSTREAMS.tsv` |
| 4 | Google Data Analytics Certificate | NS→EN | **3** | ~180 hr | $49/mo | ei_v2, recommendations, trend_feeds | Pearl_Research, Pearl_Int | SQL + Tableau are not in stack, but data-thinking transfers to ei_v2 + trend signal interpretation |
| 5 | Google Advanced Data Analytics | EN→IN | **4** | ~120 hr | $49/mo | ei_v2, recommendations | Pearl_Research | Python + statistical inference + regression directly applicable to ei_v2 calibration |
| 6 | Google Business Intelligence | EN→IN | **2** | ~120 hr | $49/mo | dashboard, brand_admin | Pearl_Brand | BigQuery + Tableau not in stack today; concepts apply to brand_admin exec dashboards |
| 7 | Google UX Design Certificate | NS→EN | **4** | ~180 hr | $49/mo | brand_admin, dashboard | Pearl_Prez, Pearl_Brand | Figma + user research directly support brand-wizard-app + onboarding flow |
| 8 | Google Cybersecurity Certificate | NS→EN | **3** | ~180 hr | $49/mo | pearl_devops, integrations | Pearl_DevOps, Pearl_Int | Secrets hygiene, push-guard, branch-protection thinking applies; SIEM/Python tooling transferable |
| 9 | Google Digital Marketing & E-commerce | NS→EN | **3** | ~180 hr | $49/mo | marketing, pearl_news | Pearl_Marketing | Funnel + SEO + e-commerce platform thinking applies; tool-specific knowledge less so |
| 10 | Google AI Essentials | NS | **3** | <5 hr | $49/mo (or free trial) | all subsystems (general fluency) | any Pearl agent | Universal AI literacy primer — recommended for every new contributor |
| 11 | Google AI Professional Certificate | EN→IN | **4** | ~60 hr | $49/mo | core_pipeline, manga_pipeline, video_pipeline | Pearl_Dev, Pearl_Editor | Hands-on Gemini + AI agent building — concepts apply, but **see Tier-policy note** below |
| 12 | Accelerate Your Job Search with AI | NS | **1** | <10 hr | $49/mo | n/a | n/a | Career-only; flag for trainees but no Pearl Prime utility |
| 13 | Cloud Digital Leader | NS→EN | **3** | ~30 hr prep | $99 + prep | integrations, pearl_devops | Pearl_Int, Pearl_DevOps | Cloud-vendor mental model; Cloudflare is primary cloud, GCP is **not** in stack today |
| 14 | Generative AI Leader | NS→EN | **2** | ~30 hr prep | $99 + prep | n/a | n/a | Business / strategy focus; banned APIs limit direct Pearl Prime utility |
| 15 | Associate Cloud Engineer (GCP) | EN→IN | **0** | ~80 hr prep | $125 + prep | n/a | n/a | **Tier-policy gap:** GCP not in Pearl Prime stack; Cloudflare is. Career-only |
| 16 | Associate Data Practitioner (GCP) | EN→IN | **0** | ~80 hr prep | $125 + prep | n/a | n/a | Same as #15 |
| 17 | Associate Google Workspace Administrator | EN→IN | **2** | ~80 hr prep | $125 + prep | brand_admin, integrations | Pearl_Int | Operator does use Google Workspace; admin fluency adds value at the operator-tooling tier |
| 18 | Professional Cloud Architect (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Tier-policy gap; career value high, repo value none |
| 19 | Professional Data Engineer (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Same |
| 20 | Professional Cloud Developer (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Same |
| 21 | Professional Cloud DevOps Engineer (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Same; **note** — concepts (SRE, CI/CD, observability) DO transfer to Pearl Prime's GitHub-Actions + Cloudflare stack |
| 22 | Professional Cloud Security Engineer (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Same; concepts transferable |
| 23 | Professional Cloud Network Engineer (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Same |
| 24 | Professional Cloud Database Engineer (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Same |
| 25 | Professional Machine Learning Engineer (GCP) | AD | **0** | ~150 hr prep | $200 + prep | n/a | n/a | Tier-policy gap; ML engineering concepts (MLOps, model monitoring) transferable as theory |
| 26 | ML Crash Course | EN→IN | **3** | ~40 hr (self-paced) | Free | ei_v2 (concepts) | Pearl_Research | Foundational ML literacy; no credential, but free + no Tier-policy risk because it's pedagogy not API usage |
| 27 | Skills Boost: AI/ML path | EN→AD | **2** | varies | Free tier | n/a | n/a | Vertex AI focus; not in stack, but free hands-on practice useful for ML literacy |
| 28 | Skills Boost: Agents path | EN→AD | **3** | varies | Free tier | manga_pipeline (7-agent architecture) | Pearl_Dev | Agent orchestration patterns are highly relevant to Pearl Prime's 14-agent architecture |
| 29 | Skills Boost: Security path | EN→AD | **2** | varies | Free tier | pearl_devops | Pearl_DevOps | Cloud-security concepts transfer |
| 30 | Google Ads Search Certification | EN | **3** | ~15 hr | Free | marketing, pearl_news | Pearl_Marketing | Operator does run paid ads; cert holders can directly contribute |
| 31 | Google Ads Video Certification | EN | **3** | ~10 hr | Free | marketing, video_pipeline | Pearl_Marketing, Pearl_Video | YouTube ad fluency supports video distribution |
| 32 | Google Analytics (GA4) Certification | EN | **3** | ~15 hr | Free | marketing, dashboard | Pearl_Marketing, Pearl_Brand | Operator-tier analytics dashboards; cert holders can wire conversion tracking |
| 33 | Fundamentals of Digital Marketing | NS→EN | **2** | ~40 hr | Free | marketing | Pearl_Marketing | Broad foundation; specific tools may not align |
| 34 | Certified Educator L1 | EN | **2** | ~10 hr | Free | n/a | n/a | If the contributor is also a teacher / facilitator, useful; not Pearl Prime utility per se |
| 35 | Certified Educator L2 | EN→IN | **2** | ~15 hr | Free | n/a | n/a | Same |
| 36 | Generative AI for Educators | NS | **2** | ~5 hr | Free | n/a | n/a | Useful primer for AI-curious educators (Nihala's audience overlap) |
| 37 | AI for Small Businesses | NS | **2** | ~5 hr | Free | marketing | Pearl_Marketing | Operator-tier business audience overlap |
| 38 | Applied Digital Skills | NS | **1** | varies | Free | n/a | n/a | K-12 + adult literacy; not Pearl Prime work |

**Highest-utility Pearl Prime fits (utility ≥ 4):** rows 2 (IT Automation w/ Python = **5**), 3 (PM = 4), 5 (Adv Data Analytics = 4), 7 (UX = 4), 11 (AI Professional = 4).

---

## 4. Job market table

US 2026 entry salary medians anchored to BLS OOH May 2024 OEWS where authoritative; Glassdoor / Levels.fyi / Indeed crowd-sourced where BLS does not track standalone titles.

Hot-factor scale: **BLAZING** (1.3 M new global AI roles per LinkedIn, top 25 fastest-growing) → **HOT** (resilient + growing) → **WARM** (stable, +5-10 % yoy) → **COOL** (flat-to-softening, AI displacement risk) → **DECLINING** (BLS negative-projection).

| # | Skill area / Google cert | US entry salary band 2026 | 3-yr progression + ceiling | Posting volume trend | Hot factor | AI displacement risk |
|---|---|---|---|---|---|---|
| 1 | Data Analyst (entry) / Data Analytics Cert | $49.8K-$80.6K (median entry ~$63K) | Sr Data Analyst $95-120K → Analytics Mgr $125-160K | Flat-softening at junior | **WARM** (was HOT pre-2024) | **HIGH** (SQL / Excel basics being absorbed by GPT-class tools) |
| 2 | IT Support Specialist / IT Support Cert | $40K-$78K (BLS median $60,340) | Sys Admin $75-95K → IT Mgr $120K+ or pivot to Cloud/Sec | BLS −3% 2024-2034; 50.5K openings/yr from churn | **COOL** (entry) / WARM (pivoted) | **HIGH** (chatbots displacing tier-1 help desk) |
| 3 | Project Manager (entry) / PM Cert | $58K-$130K (BLS median $100,750) | PM $95-120K → Sr PM $130-165K (PMP adds +20%) | BLS +6% 2024-2034; 78.2K openings/yr | **WARM** | **MEDIUM** (tech-PM softer, healthcare / construction PM steady) |
| 4 | UX Designer (entry) / UX Cert | $55K-$95K junior (BLS Web & Digital Interface Designer median $98,090) | Sr UX $110-140K → Lead $150-200K or UX Mgr | Softening at junior; recovering mid-level | **COOL** (junior) / WARM (mid+ with AI fluency) | **HIGH** at junior (Figma + Generate plugins eating wireframe work) |
| 5 | Cybersecurity Analyst (SOC T1) / Cybersecurity Cert | $69K-$130K (BLS Info Security Analyst median **$124,910**) | SOC T2 / Threat Hunter $115-145K → Security Eng $150-200K | BLS +29% 2024-2034 (16K openings/yr); Indeed +124% YoY | **HOT** | **LOW** (AI augments, doesn't replace) |
| 6 | Digital Marketer / Digital Marketing Cert | $42K-$85K entry (BLS Market Research Analyst median $76,950) | Sr Specialist $80-100K → Mgr $110-140K | BLS +7% 2024-2034 for market research | **COOL** (entry) / WARM (AI-fluent) | **HIGH** (copy / SEO basic work being absorbed) |
| 7 | Senior Data Analyst / Adv Data Analytics Cert | $80K-$130K mid (median ~$108K) | Analytics Mgr $125-160K → Director $165-220K | Stronger than entry-analyst | **WARM** | **LOW** (Python + storytelling adds resilience) |
| 8 | Business Intelligence Analyst / BI Cert | $93K-$150K (Glassdoor median **$116,488**) | Sr BI $125-155K → BI Mgr / Analytics Eng $140-180K | BLS Computer Systems Analyst proxy +9% 2024-2034 | **WARM / stable** | **LOW** (dbt / Looker / Power BI demand steady) |
| 9 | IT Automation (Python) / Jr DevOps / IT Automation Cert | $75K-$130K entry (overlap DevOps entry $81K-$95K) | DevOps $110-135K → Sr DevOps $150-200K | Indeed cloud / automation postings resilient | **WARM-to-HOT** | **LOW** (ops-coded roles holding; junior dev market softer) |
| 10 | Cloud Engineer (entry) / Associate Cloud Engineer | $101K-$130K entry (Glassdoor all-level avg **$151,612**) | Sr Cloud $150-185K → Cloud Architect $180-230K | Indeed: cloud / infra resilient; 600K+ data-center jobs from AI build-out | **HOT** | **LOW** |
| 11 | Cloud Architect (mid-senior) / Pro Cloud Architect | $165K-$210K (Google L5-L6 $200-296K median per Levels.fyi) | Principal / Staff $230-300K+ → VP / CTO | GCP PCA carries $10-20K salary premium | **HOT** | **LOW** |
| 12 | Data Engineer / Pro Data Engineer | Glassdoor GCP DE avg **$165,557** (n=27 [low-n flag]); 25-75 pctl $135.7K-$204.7K | Sr DE $165-205K → Staff $210-280K | Indeed AI / ML / data eng postings +85% YoY | **HOT** | **LOW (AI INCREASES demand)** |
| 13 | ML Engineer / Pro ML Engineer | $128.8K entry; mid-senior $150-220K; MLOps premium +25-40%; frontier-lab $300K-500K+ TC | Sr MLE $180-240K → Staff / Applied Scientist $250-400K+ | Indeed ML eng postings +85% YoY; BLS data scientist +34% 2024-2034 | **BLAZING** | **NEGATIVE** (AI creates demand) |
| 14 | Cloud Security Engineer / Pro Cloud Security | Glassdoor median **$152,773**; 90th pctl $205K; SF median $201K | Sr CSE $175-220K → Security Architect $210-280K | Cybersec demand + cloud-native overlap | **BLAZING** | **NEGATIVE** |
| 15 | Cloud DevOps / SRE / Pro Cloud DevOps Engineer | Glassdoor SRE / DevOps avg **$162,440**; SRE avg $171,708 | Sr DevOps $150-185K → Staff SRE / Platform Lead $200-260K | Sustained demand in down market | **HOT** | **LOW** |
| 16 | GenAI / Prompt Engineering / AI Professional Cert + AI Essentials | Prompt Eng median **$129,538**; 25-75 pctl $102K-$166.3K | AI Eng / Solutions Eng $150-220K → AI Lead $200-350K+ | LinkedIn AI Eng = top US fastest-growing role 2026; 275K+ US AI postings in Jan 2026 | **BLAZING** | **NEGATIVE** (caveat: "Prompt Eng" title may compress into "AI Eng") |
| 17 | GenAI Strategy / AI Product Lead / Generative AI Leader | AI PM Glassdoor avg **$196,459**; 25-75 pctl $163K-$242K | Sr AI PM $210-260K → Head of AI $260-400K+ | Every Fortune 500 hiring AI strategy in 2026 | **BLAZING** | **NEGATIVE** |
| 18 | Google Ads / PPC Specialist / Skillshop Ads certs | Google Ads Specialist avg **$79,642**; 25-75 pctl $59.7K-$110.5K | Sr Specialist $75-100K → Paid Media Mgr $95-130K → Director $150K+ | Heavy AI automation of bidding / copy (Performance Max eats analyst tasks) | **COOL** | **HIGH** |
| 19 | EdTech Specialist / Certified Educator | $59K-$102K wide variance; PayScale $59K-$69K K-12 representative | Coordinator $75-95K → Director Digital Learning $110-140K | District-level budgets constrained; corp L&D / edtech vendor warmer | **COOL** (K-12) / WARM (corp + vendor) | **MEDIUM** |

**Key takeaways:**

1. **HOT/BLAZING skills (rows 5, 10-17):** Cybersecurity, cloud engineering, cloud architecture, data engineering, ML engineering, cloud security, cloud DevOps, GenAI engineering, AI product management. Aggregate salary band $125K-$400K +; resilient or growing through 2026 AI compute build-out.
2. **WARM-stable skills (rows 3, 7, 8, 9):** PM, senior data analytics, BI, IT automation. $90K-$180K with steady progression.
3. **COOL-to-DECLINING (rows 1, 2, 4, 6, 18, 19):** Entry data analyst, IT support tier 1, junior UX, junior digital marketer, PPC specialist, K-12 EdTech. AI displacement risk **HIGH at junior tier**; certificates alone are no longer sufficient — portfolio + AI fluency required.

---

## 5. Gap analysis

### "Hot in market but NOT in Pearl Prime today"

Each item ↓ gets an integration-feasibility verdict: **YES (architecture-fit, in-Tier-policy)**, **PARTIAL (concepts transfer, vendor doesn't)**, or **NO (Tier-policy banned or architecture mismatch)**.

| Hot market skill | Verdict | Why / proposed scope |
|---|---|---|
| **GCP Cloud Architecture (Associate + Professional Cloud Architect)** | **NO** | Pearl Prime's cloud is Cloudflare, not GCP. Trainees should NOT migrate Pearl Prime to GCP. Career-only learning. **However, concepts (region planning, IAM, autoscaling, cost optimization) transfer 1:1 to Cloudflare Workers + Pages + R2 design.** Recommend: trainee learns GCP concepts, applies them to Pearl Prime's Cloudflare stack. |
| **GCP Data Engineering (Pro Data Engineer)** | **PARTIAL** | Pearl Prime is filesystem + YAML-driven, not warehouse-driven. BigQuery / Dataflow / Pub-Sub not in stack. **However**, if Pearl Prime were to centralize the catalog SSOT into a query-able store (`config/source_of_truth/manga_series_plans/` × 1,350 series + 18,900 episodes is at the limit of grep-able filesystem), a data engineer could materially help. **Scope if pursued:** introduce DuckDB or SQLite over YAML SSOT for catalog queries, NOT BigQuery (avoid GCP vendor lock-in per Tier policy). |
| **GCP ML Engineering (Pro ML Engineer)** | **NO** | Vertex AI = Google AI cloud = **BANNED** in repo code per CLAUDE.md `llm-policy-enforcement.yml`. Trainees can learn MLOps concepts (model versioning, monitoring, drift detection), but Pearl Prime uses local Ollama (Qwen + Gemma3) on Pearl Star — no Vertex AI integration. **Career-only.** |
| **GCP Cloud Security (Pro Cloud Security Engineer)** | **PARTIAL** | Pearl Prime's security surface is Cloudflare + GitHub repo secrets + macOS Keychain + push-guard. GCP IAM / Cloud Armor / Cloud KMS specific tools not in stack. **However**, security thinking (least-privilege, secrets rotation, supply-chain hygiene, branch protection) directly transfers. **Scope if pursued:** trainee could harden Pearl Prime's existing secret-handling, push-guard, and CI ruleset enforcement. |
| **GCP Cloud DevOps / SRE (Pro Cloud DevOps Engineer)** | **PARTIAL→YES** | Cloud Build / Cloud Deploy / Cloud Monitoring not in stack; **but** GitHub Actions + Cloudflare + Pearl Star runner is essentially a custom DevOps stack. SRE concepts (SLO / SLI / error budgets / blameless postmortems / runbooks) are **directly applicable** to Pearl Prime's incident-response practice (`docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md`). **Scope if pursued:** trainee authors SLO / SLI definitions for Pearl Prime's main workflows. |
| **Vertex AI Agent Builder / Vertex AI Studio (Skills Boost: Agents path)** | **NO** | Vertex AI banned. **However**, agent-orchestration patterns (planner → executor → tool-calling, state management, error-handling) are **directly applicable** to Pearl Prime's 14-agent architecture (`config/agents/agent_registry.yaml`). Trainee learns Vertex AI patterns, applies them to Pearl Prime's existing Claude-orchestration via Tier 1. |
| **GenAI Engineer / Prompt Engineering (Google AI Professional Cert)** | **YES (with constraint)** | AI Professional Cert teaches Gemini hands-on; Gemini API is **BANNED in repo code**. **However**, prompt engineering as a craft transfers 1:1 to Tier 2 Ollama prompts (Qwen + Gemma3) and Tier 1 Claude prompts. Trainee learns Gemini patterns, ships Ollama-equivalent prompts to Pearl Prime. **Scope:** prompt iteration on `pearl_news/prompts/`, `prompts/draft_audiobook_v2.txt`, manga writer / editor system prompts. |
| **AI Product Management / AI Strategy (Generative AI Leader)** | **YES** | Strategy-level cert; no API integration risk. Operator-tier value: an AI PM trainee can author the Pearl Prime AI-feature roadmap, evaluate Tier-2 vs Tier-1 tradeoffs, design EI v2 dimension priorities. **Scope:** trainee author quarterly AI-roadmap reviews, contribute to `docs/PEARL_PM_STATE.md`. |
| **BigQuery / Snowflake / dbt / Power BI / Tableau (BI cert)** | **NO** | Pearl Prime has no warehouse. **However**, if dashboard / exec-reporting needs grow, the same trainee could ship a DuckDB-on-YAML solution. |
| **Generative AI for Search (Skills Boost: Intelligent Search)** | **NO** | Vertex AI Search banned. Concepts apply to RAG-style retrieval over `atoms/` + `pearl_news/` content, but vendor banned. |

**Total gap-list items: 10.** Integration-feasible (PARTIAL or YES): **7.** Pure career-only (NO): **3.**

---

## 6. Integration roadmap

If Pearl Prime were to absorb the top-2 most-feasible "hot but missing" capabilities, here is the proposed scope:

### Integration #1 — DuckDB over YAML SSOT (data-engineering capability absorption)

- **Subsystem touched:** manga_pipeline, core_pipeline, dashboard
- **Scope:** Wrap `config/source_of_truth/manga_series_plans/{locale}/` (1,350 YAMLs × 5 locales) + `manga_book_plans/{series_id}/ep_NN.yaml` (18,900 YAMLs) in a DuckDB read-only view materialized at startup. Add `scripts/catalog/duckdb_view.py` that materializes the view; export query examples in `docs/CATALOG_QUERY_GUIDE.md`. No external vendor; pure embedded SQL.
- **Effort:** 2-3 weeks Pearl_Dev + Pearl_Research
- **Why this works:** YAML-as-source-of-truth preserved; SQL-as-query-interface added. Aligns with Path X axis-separation (no master catalog plan). Trainee with Pearl_Research / Pearl_Dev shadowing can ship this.
- **Why NOT BigQuery / Snowflake:** Tier policy. No cloud vendor lock-in. Free.

### Integration #2 — SRE-style SLO definitions + GitHub Actions observability uplift (cloud DevOps capability absorption)

- **Subsystem touched:** pearl_devops, all major pipelines
- **Scope:** Author `docs/SLO_REGISTRY.md` with SLO / SLI / error-budget definitions for: weekly manga rollout (success rate ≥ 95% over 4-week window); audiobook comparator loop (manual-review queue depth < 10% of throughput); Pearl News daily publish (no missed days ≥ 7 days). Add `.github/workflows/slo-report.yml` that publishes weekly SLO compliance to `artifacts/observability/slo_report_<date>.md`. No external vendor; pure GitHub Actions.
- **Effort:** 1-2 weeks Pearl_DevOps + Pearl_PM
- **Why this works:** Already aligned with existing `change-impact.yml` + `marketing-continuous.yml` pattern. Operator-tier value: visible health dashboard.
- **Why NOT Datadog / New Relic:** Cost. Pearl Prime's CI already emits structured logs; SLO computation is grep + jq, not paid-vendor.

### Items NOT recommended for integration

- Vertex AI / Gemini API integration — Tier-policy banned. Stay with Ollama on Pearl Star.
- BigQuery / Snowflake — vendor lock-in. DuckDB is sufficient.
- Datadog / New Relic — cost; existing observability sufficient.

---

## 7. Tier-policy guardrails

Per `CLAUDE.md`, the following Google APIs / clouds are **BANNED in repo code**:

- **Vertex AI** (cloud Gemini, cloud Imagen, Vertex AI Search, Vertex AI Agent Builder)
- **Gemini API** (direct cloud calls via `google.generativeai` Python SDK)
- **Google AI Studio** (cloud surface)

Trainees who complete the **Google AI Professional Certificate**, **Generative AI Leader**, **Skills Boost: Agents path**, **Skills Boost: AI/ML path**, or **Pro Machine Learning Engineer** will learn skills that they **CANNOT directly ship to Pearl Prime repo code**. Their options:

1. **Apply concepts to Pearl Prime's local-LLM stack** (Ollama Qwen + Gemma3 on Pearl Star) — recommended.
2. **Apply concepts to Tier-1 Claude orchestration** (Claude Code subscription, operator-present only) — recommended.
3. **Use skill for personal career value** (job market salaries cited in §4 are real even if Pearl Prime can't directly ship that vendor) — recommended.

This is NOT a reason to skip those courses. AI fluency is the most valuable career skill of 2026. The constraint is on **API integration into Pearl Prime repo code**, not on **what trainees learn**.

The `.github/workflows/llm-policy-enforcement.yml` workflow + `scripts/ci/audit_llm_callers.py` actively blocks PRs that introduce banned API usage. Trainees should run `python3 scripts/ci/audit_llm_callers.py` before pushing.

---

## 8. Recommended sequencing

For each contributor profile, here is a phased onboarding curriculum.

### Profile A — No-skill / generalist contributor (helps operator with day-to-day)

- **Day 1-30 (orientation):** Google AI Essentials (<5 hr) + Google AI for Small Businesses (~5 hr) + read `docs/DOCS_INDEX.md` + `CLAUDE.md` + `SYSTEM_OWNER_VISION.md`. Shadow Pearl_PM via `artifacts/coordination/`.
- **Day 31-90 (skill build):** Google Project Management Certificate (~180 hr at 10 hr/wk = 4-5 mo, but start). Pair with operator on weekly workstream creation.
- **Day 91-180 (specialization):** Skillshop Google Ads + GA4 Certifications (~30 hr combined, free). Trainee owns marketing-content + freebie-funnel work alongside Pearl_Marketing.

### Profile B — Entry-level technical contributor (helps ship Pearl Prime code)

- **Day 1-30:** Google AI Essentials + read `scripts/run_pipeline.py` + `specs/PHOENIX_V4_5_WRITER_SPEC.md`. Pair-program with Pearl_Dev on smallest open ws.
- **Day 31-90:** **Google IT Automation with Python Certificate** (~120 hr at 10 hr/wk = 3-4 mo). **This is the single highest-utility course** — ~90 % of Pearl Prime repo is Python. Complete it.
- **Day 91-180:** Google AI Professional Certificate (~60 hr). Apply learnings to Pearl Prime prompts in `pearl_news/prompts/`, `prompts/draft_audiobook_v2.txt`, manga writer system prompts. **Strictly Tier 2 (Ollama) or Tier 1 (Claude) — no Gemini API calls in repo code.**

### Profile C — Intermediate contributor (technical with prior coding)

- **Day 1-30:** Skim `specs/AI_MANGA_PIPELINE_SUMMARY.md` + `docs/AUDIOBOOK_PIPELINE_SPEC.md` + `docs/VIDEO_PIPELINE_SPEC.md`. Run a manga ep_001 end-to-end on Pearl Star.
- **Day 31-90:** Google ML Crash Course (~40 hr, free, no banned-API risk). Pearl_Research shadow on EI v2 calibration.
- **Day 91-180:** Skills Boost: Agents path (free) + apply patterns to Pearl Prime's 14-agent registry. Optionally: Generative AI Leader cert ($99, ~30 hr prep) for AI-strategy fluency.

### Profile D — Advanced contributor (senior engineer)

- **Day 1-30:** Read all 19 subsystem authority docs. Author DISCOVERY REPORT pattern for first non-trivial PR (per `~/.claude/memory/feedback_discover_before_acting.md`).
- **Day 31-90:** Pick one integration roadmap item (§6) and ship it. Suggested: DuckDB over YAML SSOT.
- **Day 91-180:** Optional GCP Pro cert ($200) — career value high, repo value via concept-transfer. Pair with author of `docs/SLO_REGISTRY.md` (Integration #2).

---

## 9. Citations

All URLs accessed **2026-06-09** unless otherwise noted.

### Primary sources — Google official

1. Google Career Certificates landing: https://grow.google/certificates/
2. Google Data Analytics Cert: https://www.coursera.org/google-certificates/data-analytics-certificate
3. Google IT Support Cert: https://www.coursera.org/google-certificates/it-support-certificate
4. Google Project Management Cert: https://www.coursera.org/google-certificates/project-management-certificate
5. Google UX Design Cert: https://www.coursera.org/google-certificates/ux-design-certificate
6. Google Cybersecurity Cert: https://www.coursera.org/google-certificates/cybersecurity-certificate
7. Google Digital Marketing & E-commerce Cert: https://www.coursera.org/google-certificates/digital-marketing-certificate
8. Google AI Professional Certificate: https://www.coursera.org/professional-certificates/google-ai
9. Google AI Essentials: https://www.coursera.org/google-certificates/ai-essentials-google
10. Cloud Digital Leader: https://cloud.google.com/learn/certification/cloud-digital-leader
11. Generative AI Leader: https://cloud.google.com/learn/certification/generative-ai-leader
12. Associate Cloud Engineer: https://cloud.google.com/learn/certification/cloud-engineer
13. Associate Data Practitioner: https://cloud.google.com/learn/certification/data-practitioner
14. Associate Google Workspace Administrator: https://cloud.google.com/learn/certification/associate-google-workspace-administrator
15. Professional Cloud Architect: https://cloud.google.com/learn/certification/cloud-architect
16. Professional Data Engineer: https://cloud.google.com/learn/certification/data-engineer
17. Professional Cloud Developer: https://cloud.google.com/learn/certification/cloud-developer
18. Professional Cloud DevOps Engineer: https://cloud.google.com/learn/certification/cloud-devops-engineer
19. Professional Cloud Security Engineer: https://cloud.google.com/learn/certification/cloud-security-engineer
20. Professional Cloud Network Engineer: https://cloud.google.com/learn/certification/cloud-network-engineer
21. Professional Cloud Database Engineer: https://cloud.google.com/learn/certification/cloud-database-engineer
22. Professional Machine Learning Engineer: https://cloud.google.com/learn/certification/machine-learning-engineer
23. Google Cloud Skills Boost paths: https://www.skills.google/paths
24. Google ML Crash Course: https://developers.google.com/machine-learning/crash-course
25. Google AI hub: https://ai.google/learn-ai-skills/
26. Skillshop home: https://skillshop.withgoogle.com/
27. Google Ads Search Cert: https://skillshop.docebosaas.com/learn/courses/8692/google-ads-search-certification
28. Fundamentals of Digital Marketing: https://skillshop.exceedlms.com/student/collection/1830706-fundamentals-of-digital-marketing
29. Google for Education certifications: https://edu.google.com/intl/ALL_us/learning-center/certifications/
30. Google for Education home: https://educertifications.google/

### Secondary sources — job market

31. BLS Computer Support Specialists OOH: https://www.bls.gov/ooh/computer-and-information-technology/computer-support-specialists.htm
32. BLS Data Scientists OOH: https://www.bls.gov/ooh/math/data-scientists.htm
33. BLS Information Security Analysts OOH: https://www.bls.gov/ooh/computer-and-information-technology/information-security-analysts.htm
34. BLS Project Management Specialists OOH: https://www.bls.gov/ooh/business-and-financial/project-management-specialists.htm
35. BLS Web Developers & Digital Designers OOH: https://www.bls.gov/ooh/computer-and-information-technology/web-developers.htm
36. BLS Market Research Analysts OOH: https://www.bls.gov/ooh/business-and-financial/market-research-analysts.htm
37. BLS Computer Systems Analysts OOH: https://www.bls.gov/ooh/computer-and-information-technology/computer-systems-analysts.htm
38. BLS Employment Projections 2024-2034: https://www.bls.gov/news.release/pdf/ecopro.pdf
39. Indeed Hiring Lab Jan 2026: https://www.hiringlab.org/2026/01/22/january-labor-market-update-jobs-mentioning-ai-are-growing-amid-broader-hiring-weakness/
40. Indeed 2026 US Jobs & Hiring Trends Report: https://www.hiringlab.org/2025/11/20/indeed-2026-us-jobs-hiring-trends-report/
41. LinkedIn 2026 Jobs on the Rise: https://www.linkedin.com/pulse/linkedin-jobs-rise-2026-25-fastest-growing-roles-us-linkedin-news-dlb1c
42. World Economic Forum / LinkedIn — 1.3M AI jobs: https://www.weforum.org/stories/2026/01/ai-has-already-added-1-3-million-new-jobs-according-to-linkedin-data/
43. CompTIA State of the Tech Workforce 2026: https://www.comptia.org/en-us/blog/state-of-the-tech-workforce-2026-trends-job-growth-and-future-opportunities/
44. Glassdoor Data Analyst Entry: https://www.glassdoor.com/Salaries/entry-level-data-analyst-salary-SRCH_KO0,24.htm
45. Glassdoor BI Analyst: https://www.glassdoor.com/Salaries/business-intelligence-analyst-salary-SRCH_KO0,29.htm
46. Glassdoor Cloud Engineer: https://www.glassdoor.com/Salaries/cloud-engineer-salary-SRCH_KO0,14.htm
47. Glassdoor GCP Data Engineer: https://www.glassdoor.com/Salaries/gcp-data-engineer-salary-SRCH_KO0,17.htm
48. Glassdoor ML Engineer: https://www.glassdoor.com/Salaries/machine-learning-engineer-salary-SRCH_KO0,25.htm
49. Glassdoor Cloud Security Engineer: https://www.glassdoor.com/Salaries/cloud-security-engineer-salary-SRCH_KO0,23.htm
50. Glassdoor SRE/DevOps Engineer: https://www.glassdoor.com/Salaries/sre-devops-engineer-salary-SRCH_KO0,19.htm
51. Glassdoor Prompt Engineer: https://www.glassdoor.com/Salaries/prompt-engineer-salary-SRCH_KO0,15.htm
52. Glassdoor AI PM: https://www.glassdoor.com/Salaries/ai-product-manager-salary-SRCH_KO0,18.htm
53. Glassdoor Google Ads Specialist: https://www.glassdoor.com/Salaries/google-ads-specialist-salary-SRCH_KO0,21.htm
54. Levels.fyi Google Cloud Architect: https://www.levels.fyi/companies/google/salaries/solution-architect/title/cloud-architect
55. ZipRecruiter Entry Level Cloud Engineer: https://www.ziprecruiter.com/Salaries/Entry-Level-Cloud-Engineer-Salary
56. StationX Cybersecurity Job Market 2026: https://app.stationx.net/articles/cybersecurity-job-market-statistics
57. NN/g State of UX 2026: https://www.nngroup.com/articles/state-of-ux-2026/
58. UX Design Institute Job Market 2026: https://www.uxdesigninstitute.com/blog/the-ux-job-market-in-2026-2/
59. Google Cloud cert cost guide: https://certempire.com/gcp-certification-cost/
60. Coursera GCP guide 2026: https://www.coursera.org/articles/google-cloud-certification

**Total citation count: 60.**

### Repo-internal references (grounded the Pearl Prime stack inventory)

- `CLAUDE.md` (LLM Tier policy)
- `docs/DOCS_INDEX.md`
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- `config/agents/agent_registry.yaml`
- `specs/PHOENIX_V4_5_WRITER_SPEC.md`
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`
- `specs/AI_MANGA_PIPELINE_SUMMARY.md`
- `docs/MANGA_IMPLEMENTATION_OUTLINE.md`
- `docs/VIDEO_PIPELINE_SPEC.md`
- `docs/AUDIOBOOK_PIPELINE_SPEC.md`
- `docs/PEARL_NEWS_WRITER_SPEC.md`
- `skills/pearl-int/SKILL.md`
- `skills/pearl-int/references/cloudflare_pages_deploy.md`
- `skills/pearl-int/references/integration_registry.md`
- `brand-wizard-app/package.json`
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`
- `scripts/run_pipeline.py`

---

## 10. Verification flags

Items where uncertainty remains; surfaced honestly per `~/.claude/memory/feedback_discover_before_acting.md`.

- **[verify]** Hours estimate for Google AI Professional Cert: the operator-facing "10 hr fast-completion" figure conflicts with the "3-6 months at ~10 hr/wk" Coursera default. Used `~60 hr total` as midpoint — actual completion time depends on prior experience.
- **[verify]** Google Cloud Generative AI Leader prep-path hours: not officially specified; community estimates 20-40 hr.
- **[verify]** Glassdoor GCP Data Engineer median ($165,557) has n=27 — low sample size; treat as directional, not authoritative.
- **[verify]** Some Coursera URLs (Advanced Data Analytics, BI, IT Automation) were inferred via search result mention, not directly fetched on 2026-06-09. The course names + cost pattern are stable; the exact URL slugs may differ.
- **[verify]** `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` referenced in prompt does not exist in repo. The READ-FIRST list is otherwise complete.
- **[verify]** "Build with Vertex AI" Technical Expert Badge + "Intelligent Search" Technical Expert Badge retirement date 2026-06-01 — found in search; not directly verified on Skills Boost page.
- **[verify]** Skillshop exam exact-question counts vary slightly by exam (50-75 questions reported across sources); using "75 min / 80% pass" as canonical.
- **[verify]** Industry stack-on URLs (Finance, Public Sector, Healthcare, Construction, Sustainability) inferred from grow.google/certificates listing; not individually fetched.

**Total `[verify]` count: 8.**

---

## Appendix — Pearl Prime onboarding pairing matrix (operator quick-reference)

| If contributor is interested in… | Recommended Google course | Pair with Pearl agent | First small task |
|---|---|---|---|
| Writing code daily | **IT Automation with Python** | Pearl_Dev | Add a new gate check to `scripts/ci/` |
| Coordinating projects | **Project Management Cert** | Pearl_PM | Add a workstream to `ACTIVE_WORKSTREAMS.tsv` |
| Designing UI / dashboards | **UX Design Cert** | Pearl_Prez, Pearl_Brand | Audit `brand_admin_v2.html` for usability |
| Marketing / paid ads | **Skillshop Google Ads + GA4** | Pearl_Marketing | Wire conversion tracking on freebie funnel |
| Data analysis / EI v2 | **Advanced Data Analytics** | Pearl_Research | Run an EI v2 calibration pass |
| AI / prompt engineering | **AI Professional Cert** | Pearl_Dev, Pearl_Editor | Iterate a manga writer system prompt (Tier 2 Ollama) |
| Cloud / infra | **IT Automation w/ Python** (NOT GCP Pro) | Pearl_DevOps, Pearl_Int | Improve Cloudflare deploy workflow |
| AI strategy / leadership | **Generative AI Leader** | Pearl_PM | Author AI-feature roadmap review |
| Cybersecurity | **Cybersecurity Cert** | Pearl_DevOps | Audit push-guard + branch protection |

---

**End RESEARCH_NOTES.md**
