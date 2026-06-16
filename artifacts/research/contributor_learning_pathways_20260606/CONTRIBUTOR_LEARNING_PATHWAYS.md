# Contributor Learning Pathways

**Google × Pearl Prime × the 2026 US Job Market**

*Author: Pearl_Research · Date: 2026-06-09*
*Companion to `CONTRIBUTOR_LEARNING_PATHWAYS.pptx` in the same directory*

---

## Executive summary

If we want to bring new contributors onto Pearl Prime, the question is no longer "how do we train them" — it's "which existing free or low-cost training reliably moves a person from no-skill to Pearl-Prime-helpful, while also moving them forward in their own career?"

Google publishes more learning surfaces than any other technology company. As of June 2026, that catalog spans 12 Career Certificates on Coursera, 14 Google Cloud certifications, seven Cloud Skills Boost learning paths, ten Skillshop product certifications, six Google for Education credentials, a free Machine Learning Crash Course, and several segmented programs (AI for Educators, AI for Small Businesses, AI for Students). That's roughly **60 distinct, credentialed learning surfaces** — enough that the choice problem becomes "which course is worth the time?" rather than "is there a course?"

This document answers three questions, in order:

1. **What's in the Google catalog?** A full inventory with cost, hours, credential, and skill area.
2. **Which courses help Pearl Prime, and which Pearl agent should the trainee shadow?** A fit map against the actual Pearl Prime tech stack — Python, Cloudflare, ComfyUI on Pearl Star, YAML SSOT, GitHub Actions, React + Vite + Tailwind, Ollama for local LLMs.
3. **What does each course mean for the trainee's career?** A US 2026 job market table with entry salary, three-year progression, posting volume trend, and AI-displacement risk.

Three operator-actionable conclusions surface from the analysis:

**One — the single highest-utility course is Google IT Automation with Python.** Pearl Prime is ~90 % Python by volume. Any contributor who completes that certificate can immediately help ship code in `scripts/`, `phoenix_v4/`, `pearl_news/pipeline/`, and the audiobook comparator loop. Career value is strong (entry $75-130 K; DevOps progression to $150-200 K), and there is zero tier-policy risk because Python the language carries no vendor lock-in.

**Two — the highest-paying career skills are NOT directly shippable into Pearl Prime.** Cloud architecture, ML engineering, GenAI engineering, AI product management, and cloud security top the 2026 US salary tables at $150-400 K + entry, but the cloud they teach (GCP Vertex AI, Gemini API, BigQuery) is **banned in Pearl Prime repo code** by the Tier-policy guardrails in `CLAUDE.md`. Trainees should still learn these for personal career value; the concepts transfer 1:1 to Pearl Prime's Cloudflare + Ollama stack even when the vendor doesn't.

**Three — entry-level data analyst, IT support tier 1, junior UX, junior digital marketing, and PPC specialist roles are softening fast.** AI displacement at the junior tier is real and broad. Recommend trainees who pursue these courses bundle them with an AI-fluency course (Google AI Essentials minimum; Google AI Professional Cert preferred) and a portfolio project — the cert alone is no longer sufficient as of 2026.

The deck slides walk through these conclusions visually. This document is the archive-grade prose companion.

---

## 1. Pearl Prime tech stack at a glance

Pearl Prime is a deterministic, YAML-driven, Python-first therapeutic content publishing system with 19 governed subsystems. The full subsystem-to-tech mapping lives in `RESEARCH_NOTES.md` §1. Here is the abridged operator view that every new contributor needs to internalize before picking a course.

**The Python core.** Roughly 90 % of the Pearl Prime repo is Python 3.11 +. The book-writing pipeline (`scripts/run_pipeline.py`), the audiobook comparator loop (`scripts/audiobook_script/run_comparator_loop.py`), the manga pipeline (`phoenix_v4/manga/`), the video pipeline (`scripts/video/`), Pearl News expansion (`pearl_news/pipeline/`), the EI v2 quality engine (`phoenix_v4/quality/ei_v2/`), and almost every CI script (`scripts/ci/`) are Python. PyYAML is the universal config loader. `asyncio` powers the audiobook parallel architecture (24 concurrent API calls). There is no database — filesystem is the source of truth.

**YAML is the source of truth.** Every subsystem reads from YAML configs: `config/source_of_truth/master_arcs/`, `config/manga/canonical_brand_list.yaml`, `config/audiobook_script/comparator_config.yaml`, `config/quality/ei_v2_config.yaml`, etc. JSON is the artifact format (manga `panel_prompts.json`, video timelines, audiobook status). Markdown is the spec format.

**Cloudflare is the cloud.** Pages for static sites (`brand-wizard-app/dist/`, `brand_admin.html`), Workers for serverless edge logic, R2 for artifact storage, Workers AI for some image generation. **Google Cloud is not in the stack.** Vertex AI / Gemini API / BigQuery are explicitly banned in repo code by `CLAUDE.md` and enforced by `.github/workflows/llm-policy-enforcement.yml`.

**Pearl Star is the local AI server.** Ubuntu 24.04 + RTX 5070 Ti (16 GB VRAM) + 64 GB RAM. Runs ComfyUI 0.18.1 with FLUX.1-dev, Qwen-Image, Animagine XL 4.0, PuLID-FLUX-FaceNet (for manga); Ollama with qwen2.5:14b + gemma3:27b (for CJK6 + EN fallback LLM); CosyVoice2 (for CJK audiobook TTS). Reached over Tailscale at `pearlstar.tail7fd910.ts.net`. Free, unattended, Tier-2 compliant.

**GitHub Actions is the CI/CD.** Self-hosted runner on Pearl Star + GitHub-hosted runners for non-GPU work. Workflows under `.github/workflows/` cover preflight, push-guard, governance, llm-policy-enforcement, marketing-continuous, marketing-briefs-and-proposals, catalog-book-pipeline, change-impact. Deploy path for Cloudflare Pages is PR → merge to main → wrangler-action@v3 → live in ~3 min.

**Brand wizard is React.** `brand-wizard-app/package.json` declares React 18.3 + Vite 6.0 + Tailwind 3.4 + lucide-react + PostCSS 8.4 + autoprefixer. No Redux. No Next.js. Pure client-side.

**Tier policy frames everything.** Tier 1 = Claude Code subscription, operator-present. Tier 2 = Ollama on Pearl Star, free and unattended. Banned: any paid LLM API (Anthropic cloud, OpenAI cloud, **Google AI cloud**, DashScope cloud, Together cloud, Replicate, Perplexity, Cohere, Mistral paid). This single constraint is the most important context for choosing what to teach trainees.

---

## 2. The Google learning landscape

Google's catalog falls into seven groups, ranked here by Pearl Prime utility (highest first) rather than alphabetically.

**A. Google Career Certificates on Coursera (Pearl Prime utility: HIGH).** Twelve certificates plus five university-partner industry stack-ons. Foundational: Data Analytics, IT Support, Project Management, UX Design, Cybersecurity, Digital Marketing & E-commerce. Advanced: Advanced Data Analytics, Business Intelligence, IT Automation with Python. AI track: AI Professional Certificate (Feb 2026 launch, 635 K + enrolled in four months), AI Essentials (<5 hr), Accelerate Your Job Search with AI. Pricing: $49/month after a 7-day free trial; 3-6 months to complete at ~10 hr/week. Credential is a badge on Credly plus ACE® college credit recommendation (up to 15 credits, equivalent to five bachelor's-level courses). 70 %+ of graduates report a positive career outcome within six months. 150+ employers in Google's Employer Consortium.

**B. Google Cloud certifications (Pearl Prime utility: LOW — career value HIGH).** Fourteen certifications across three tiers, hosted at `cloud.google.com/learn/certification`. Foundational: Cloud Digital Leader ($99), Generative AI Leader ($99). Associate: Associate Cloud Engineer, Associate Data Practitioner, Associate Google Workspace Administrator (each $125). Professional: Cloud Architect, Data Engineer, Cloud Developer, Cloud DevOps Engineer, Cloud Security Engineer, Cloud Network Engineer, Cloud Database Engineer, Machine Learning Engineer (each $200), plus Professional ChromeOS Administrator ($125, hosted separately at `chromeoscertification.com`). Exam length 90-180 minutes; validity 2-3 years; recommended experience 1-3+ years.

These certs are the highest-paying in the catalog: Professional Cloud Architect graduates command $165-210 K + entry per Glassdoor and Levels.fyi, with senior progression to $230-300 K. But the cloud they teach is **not** Pearl Prime's cloud. Trainees should pursue these for career value and apply the architectural concepts to Pearl Prime's Cloudflare stack — the design patterns (region planning, IAM, autoscaling, observability) are vendor-agnostic.

**C. Google Cloud Skills Boost paths (Pearl Prime utility: LOW-to-MEDIUM).** Seven major learning paths at `skills.google` (formerly `cloudskillsboost.google`, redirected as of June 2026): AI/ML, Agents, Data, Dev Tools, Infrastructure, Productivity, Security. Plus per-cert prep paths. Free tier (subject to monthly credit cap); Cloud Innovators and Cloud Study Jam programs offer additional free access. Notable: the "Build with Vertex AI" Technical Expert Badge and the "Intelligent Search Technical Expert Badge" are scheduled to be retired on 2026-06-01, with new credentials replacing.

The Agents path is the standout — its agent-orchestration patterns (planner → executor → tool-calling, state management, error handling) map directly onto Pearl Prime's 14-agent architecture in `config/agents/agent_registry.yaml`.

**D. Google free AI/ML training (Pearl Prime utility: MEDIUM).** Machine Learning Crash Course at `developers.google.com/machine-learning/crash-course` is the most useful free resource in the entire Google catalog. Free, no formal credential, ~40 hours self-paced. Modules: ML models (regression, classification) → data handling → advanced models (neural networks, embeddings, LLM intro) → real-world ML and fairness. No vendor lock-in; pure pedagogy. Generative AI Learning Path on Skills Boost is free and Vertex-AI-flavored but the concepts (prompting, model selection, output improvement) transfer.

**E. Skillshop product certifications (Pearl Prime utility: MEDIUM — operator-tier value).** Ten free certifications focused on Google's ad and analytics products: Google Ads Search, Display, Video, Shopping, Measurement, Apps, Creative, AI-Powered Performance, Google Analytics (GA4), plus Fundamentals of Digital Marketing (17 modules, 40 hr, formerly Google Digital Garage's flagship course). All free. 80 % pass threshold, 75 minutes per exam, 12-month validity. The operator does run paid ads and use GA4; certificate holders can directly help wire conversion tracking, marketing dashboards, and freebie funnel performance attribution.

**F. Google for Education certifications (Pearl Prime utility: LOW — but audience-aligned).** Six credentials, all free as of 2026: Certified Educator Level 1, Level 2, Trainer, Innovator, Gemini for Educators, Generative AI for Educators. New Level 1/2 exams re-introduced performance-based labs in 2026. Useful if the contributor is also a teacher or facilitator — Nihala's audience overlaps with educators. Not Pearl Prime work directly.

**G. Grow with Google segmented programs (Pearl Prime utility: LOW).** AI for Students, AI for Small Businesses, AI for Educators, Google Workspace with Gemini Specialization (Coursera, paid), Applied Digital Skills (free K-12 + adult literacy curriculum). Useful primers; not Pearl Prime work.

The full inventory with URL, cost, hours, and credential is in `RESEARCH_NOTES.md` §2. The full fit map with utility scores is in §3 of that document.

---

## 3. The top three no-skill to entry pathways

For a brand-new contributor with no technical background, the goal is **AI literacy + a structured framework for thinking about how Pearl Prime works**. The three highest-ROI courses, in order:

**#1 — Google AI Essentials (5 hours, $49/month).** This is the universal primer. Every new contributor at every skill level should complete it within their first week. It covers generative AI fundamentals, prompt engineering basics, responsible AI use, and practical applications (drafting, brainstorming, content analysis). The trainee finishes with enough vocabulary to read `CLAUDE.md`, `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`, and `pearl_news/prompts/expansion_system.txt` and understand what they say. Career value: AI fluency is now table-stakes for every white-collar role; 275 K + US job postings reference AI skills in January 2026.

**#2 — Google Project Management Certificate (~180 hours, $49/month).** Project management as a discipline maps 1:1 onto Pearl Prime's workstream coordination patterns (`artifacts/coordination/ACTIVE_PROJECTS.tsv`, `ACTIVE_WORKSTREAMS.tsv`, the STARTUP_RECEIPT / CLOSEOUT_RECEIPT protocol in `docs/SESSION_UNITY_PROTOCOL.md`). A contributor who completes the PM cert can immediately help Pearl_PM open and close workstreams, audit project health, and run weekly governance reviews. Career value: BLS median for Project Management Specialists is **$100,750**, with +6 % growth 2024-2034 and 78,200 openings per year. Three-year progression: PM → Sr PM ($130-165 K) → Program Manager. PMP credential adds ~20 % salary premium.

**#3 — Google UX Design Certificate (~180 hours, $49/month).** Pearl Prime's frontend surfaces are the brand-wizard-app, the executive catalog dashboard (`brand_admin_v2.html`), the brand-admin onboarding flow, and Pearl News on WordPress. A UX-trained contributor pairs with Pearl_Prez and Pearl_Brand to audit usability, design new onboarding flows, and turn rough operator wireframes into shipped React components (the brand wizard uses React + Vite + Tailwind, all of which a UX practitioner can pick up). Career value: BLS Web & Digital Interface Designers median is **$98,090**. Caveat: junior UX is softening — entry-level hiring dropped sharply 2023-2024 — so trainees should bundle the UX cert with the AI Essentials course and a portfolio piece on Pearl Prime's brand-wizard.

---

## 4. The top three entry to intermediate pathways

For contributors with some technical background — a developer, scripter, or someone comfortable in a terminal — the goal is **shipping code or content into Pearl Prime within their first three months.**

**#1 — Google IT Automation with Python Certificate (~120 hours, $49/month).** This is the single highest-utility course in the entire Google catalog for Pearl Prime work. Roughly 90 % of the Pearl Prime repo is Python. A contributor who completes this cert can write CI scripts in `scripts/ci/`, extend the audiobook comparator loop, add a new manga gate to `config/manga/gate_registry.yaml`, refactor a video pipeline stage, or author a new EI v2 dimension gate. They will also learn Git and automation patterns that transfer directly to the GitHub Actions + push-guard + preflight stack Pearl Prime runs on. Career value: entry-level Python developer / Jr DevOps roles pay $75-130 K; three-year progression to DevOps Engineer ($110-135 K) → Senior DevOps / Platform Engineer ($150-200 K). The market is WARM-to-HOT because ops-coded roles are holding up better than junior dev roles in 2026.

**#2 — Google AI Professional Certificate (~60 hours, $49/month).** Launched February 2026 with seven modules and 635 K + enrollees in four months. Hands-on with Gemini, building AI-powered solutions, AI agent architecture, and twenty hands-on activities. The Gemini API itself is banned in Pearl Prime repo code — but **prompt engineering as a craft transfers 1:1 to Tier-2 Ollama prompts** (Qwen + Gemma3 on Pearl Star) and Tier-1 Claude prompts. A trainee can apply AI Professional Cert learnings to `pearl_news/prompts/expansion_system.txt`, `prompts/draft_audiobook_v2.txt`, and the manga writer/editor system prompts. Career value: BLAZING — LinkedIn's AI Engineer is the fastest-growing US role in 2026; Prompt Engineer median is $129,538, 25-75 percentile $102-166 K, with three-year progression to AI Engineer / Forward-Deployed Engineer ($150-220 K) → AI Lead ($200-350 K +).

**#3 — Google Advanced Data Analytics Certificate (~120 hours, $49/month).** Pearl Prime's EI v2 quality engine (`phoenix_v4/quality/ei_v2/`) does emotional-intelligence scoring across multiple dimensions and runs calibration sweeps via `scripts/ci/run_ei_v2_catalog_calibration.py`. A contributor with Advanced Data Analytics training — Python, statistical inference, regression, ML modeling — can directly help Pearl_Research tune dimension gates, audit hybrid_selector scoring, and analyze catalog QA drift. Career value: WARM. Senior Data Analyst median ~$108 K (Glassdoor); three-year progression to Analytics Manager ($125-160 K) → Director of Analytics ($165-220 K). Stronger than entry-level data analyst because Python + storytelling adds AI-displacement resilience.

---

## 5. The top two intermediate to advanced pathways

For senior engineers who already write production code — these pathways are about career value first, Pearl Prime concept-transfer second.

**#1 — Generative AI Leader certification (~30 hours prep, $99 exam).** This is the cert with the lowest cost and highest strategic value. Ninety-minute exam, 50-60 scenario-style multiple-choice questions, no hands-on requirement. It teaches the business and strategy layer of GenAI: when to use which model, how to evaluate vendors, how to design AI-augmented workflows, responsible AI governance, and how to scale AI adoption across an organization. A senior contributor with this cert can author Pearl Prime's AI-feature roadmap reviews, evaluate Tier-2 (Ollama) vs Tier-1 (Claude) tradeoffs for new pipelines, and contribute to `docs/PEARL_PM_STATE.md` AI-strategy entries. Career value: BLAZING. AI Product Manager Glassdoor median is **$196,459**; 25-75 percentile $163-242 K; three-year progression to Head of AI ($260-400 K +). Every Fortune 500 is hiring AI strategy roles in 2026.

**#2 — Google ML Crash Course + Skills Boost Agents path (free, ~60 hours combined).** Free, no Tier-policy risk because it's pedagogy not API integration. The ML Crash Course gives a rigorous foundation in regression, classification, neural networks, embeddings, and production ML systems. The Agents path teaches Vertex AI Agent Builder patterns that map directly onto Pearl Prime's 14-agent architecture — planner / executor / tool-calling / state management / error handling. A senior contributor can pick one of the two integration roadmap items in §6 below and ship it.

Why no Pro Cloud Architect or Pro ML Engineer recommendation here? Because both are Tier-policy-banned for direct repo use, and at the advanced tier the career-value argument is weaker — a senior engineer's career is already strong. Better to ship one integration roadmap item than to add another cert badge.

---

## 6. Hot in the job market but NOT in Pearl Prime

The 2026 US job market is rewarding cloud architecture, ML engineering, GenAI engineering, AI product management, cloud security, and cloud DevOps with salaries that meaningfully exceed the rest of the technology workforce. **None of these capabilities is in Pearl Prime today.** The honest gap analysis:

**GCP Cloud Architecture — NO direct integration.** Pearl Prime runs on Cloudflare, not GCP. Trainees should NOT migrate Pearl Prime to GCP — that would be a multi-quarter effort with no operator-benefit (Cloudflare is faster, cheaper, simpler for Pearl Prime's edge-render use case). **However**, the concepts in Pro Cloud Architect (region planning, IAM, autoscaling, cost optimization) transfer 1:1 to Cloudflare Workers + Pages + R2 design. Verdict: career-only learning; apply concepts to Pearl Prime's existing Cloudflare stack.

**GCP Data Engineering — PARTIAL integration.** Pearl Prime is filesystem + YAML-driven, not warehouse-driven. BigQuery / Dataflow / Pub-Sub are not in stack. **However**, the catalog SSOT is at the limit of grep-able filesystem: 1,350 manga series × 5 locales + 18,900 episode YAMLs. A data engineer could materially help by introducing a query layer. Proposed scope: **DuckDB-over-YAML SSOT** (Integration #1 below).

**GCP ML Engineering — NO direct integration.** Vertex AI = Google AI cloud = banned in repo code per `CLAUDE.md`. Pearl Prime uses local Ollama (Qwen + Gemma3) on Pearl Star. MLOps concepts (model versioning, monitoring, drift detection) transfer as theory; Vertex AI API does not.

**GCP Cloud Security — PARTIAL integration.** Pearl Prime's security surface is Cloudflare + GitHub repo secrets + macOS Keychain + push-guard. GCP-specific tools (Cloud Armor, Cloud KMS, Cloud IAM) are not in stack. Security thinking (least-privilege, secrets rotation, supply-chain hygiene) directly transfers.

**GCP Cloud DevOps / SRE — PARTIAL-to-YES integration.** Cloud Build / Cloud Deploy / Cloud Monitoring are not in stack, **but** GitHub Actions + Cloudflare + Pearl Star runner is essentially a custom DevOps stack. SRE concepts (SLO / SLI / error budgets / blameless postmortems / runbooks) directly apply to Pearl Prime's incident-response practice. Proposed scope: **SRE-style SLO definitions** (Integration #2 below).

**Vertex AI Agent Builder — NO direct integration.** Vertex AI banned. Agent-orchestration patterns transfer to Pearl Prime's 14-agent registry.

**GenAI / Prompt Engineering — YES with constraint.** AI Professional Cert teaches Gemini API; Gemini API banned. Prompt engineering as a craft transfers 1:1 to Tier-2 Ollama and Tier-1 Claude. Trainees can ship Ollama-equivalent prompts to Pearl Prime.

**AI Product Management — YES.** Strategy-level cert, no API integration risk. Operator-tier value: trainee authors quarterly AI-roadmap reviews.

**BigQuery / Snowflake / dbt / Power BI / Tableau — NO.** No warehouse in Pearl Prime; DuckDB-on-YAML is sufficient for catalog queries.

---

## 7. Integration roadmap

If Pearl Prime were to absorb the top-two most-feasible "hot but missing" capabilities — pursued by an intermediate-to-advanced contributor with appropriate cert backing — here is the recommended scope.

### Integration #1: DuckDB over YAML SSOT

**Subsystem touched:** manga_pipeline, core_pipeline, dashboard.

**Scope:** Wrap `config/source_of_truth/manga_series_plans/{locale}/` (1,350 YAMLs × 5 locales) and `config/source_of_truth/manga_book_plans/{series_id}/ep_NN.yaml` (18,900 YAMLs) in a DuckDB read-only view materialized at startup. Add `scripts/catalog/duckdb_view.py` that materializes the view from filesystem; export query examples in a new `docs/CATALOG_QUERY_GUIDE.md`. Use DuckDB Python bindings; pure embedded SQL; no external vendor; no cloud cost.

**Effort:** 2-3 weeks Pearl_Dev + Pearl_Research collaboration.

**Why this works:** YAML-as-source-of-truth is preserved (no migration risk). SQL-as-query-interface is added (no operator-burden). Aligns with Path X axis-separation (no master catalog plan). A trainee with Google Advanced Data Analytics or Pro Data Engineer training can ship this with Pearl_Research and Pearl_Dev shadowing.

**Why NOT BigQuery or Snowflake:** Tier-policy violation (cloud vendor lock-in). DuckDB is sufficient for the data scale (~20 K rows) and runs on the same Pearl Star where Ollama runs.

### Integration #2: SRE-style SLO definitions + GitHub Actions observability uplift

**Subsystem touched:** pearl_devops, all major pipelines.

**Scope:** Author `docs/SLO_REGISTRY.md` with explicit SLO / SLI / error-budget definitions for:

- Weekly manga rollout: success rate ≥ 95 % over a 4-week rolling window.
- Audiobook comparator loop: manual-review queue depth < 10 % of throughput.
- Pearl News daily publish: no missed days in a rolling 7-day window.
- Brand-admin Cloudflare Pages deploy: success rate ≥ 99 % over rolling 30-day window.

Add `.github/workflows/slo-report.yml` that runs weekly, computes SLO compliance from existing structured logs (no paid observability vendor), and publishes a Markdown report to `artifacts/observability/slo_report_<date>.md`.

**Effort:** 1-2 weeks Pearl_DevOps + Pearl_PM collaboration.

**Why this works:** Aligns with existing `change-impact.yml` and `marketing-continuous.yml` patterns. Operator-tier value: a visible health dashboard that shows whether Pearl Prime is reliable. A trainee with Pro Cloud DevOps Engineer training can ship this with Pearl_DevOps shadowing.

**Why NOT Datadog / New Relic:** Cost. Pearl Prime's CI already emits structured logs; SLO computation is grep + jq, not a paid vendor.

---

## 8. Tier-policy guardrails — what trainees can't use, even after learning

Per `CLAUDE.md`, the following Google APIs and clouds are **banned in repo code**:

- Vertex AI (cloud Gemini, cloud Imagen, Vertex AI Search, Vertex AI Agent Builder)
- Gemini API (direct cloud calls via `google.generativeai` Python SDK)
- Google AI Studio (cloud surface)

This means trainees who complete the **Google AI Professional Certificate**, **Generative AI Leader**, **Skills Boost: Agents path**, **Skills Boost: AI/ML path**, or **Professional Machine Learning Engineer** will learn skills they cannot directly ship to Pearl Prime repo code. Three legitimate paths forward for those skills:

1. **Apply concepts to Pearl Prime's local-LLM stack** (Ollama with Qwen + Gemma3 on Pearl Star). Prompt engineering, agent orchestration, model evaluation, and output-quality measurement all transfer. This is the recommended primary path.

2. **Apply concepts to Tier-1 Claude orchestration** (Claude Code subscription, operator-present). Multi-agent patterns, tool-calling design, error-handling, structured-output schemas all transfer.

3. **Use skill for personal career value.** The 2026 US salary tables in §4 of `RESEARCH_NOTES.md` are real even if Pearl Prime can't directly ship that vendor.

This is **not** a reason to skip those courses. AI fluency is the most valuable career skill of 2026. The constraint is on **API integration into Pearl Prime repo code**, not on **what trainees learn**.

The CI workflow `.github/workflows/llm-policy-enforcement.yml` and the audit script `scripts/ci/audit_llm_callers.py` actively block PRs that introduce banned API usage. Trainees should run `python3 scripts/ci/audit_llm_callers.py` before pushing — see `CLAUDE.md` for the canonical preflight sequence.

---

## 9. Recommended sequencing

A 30 / 90 / 180 day onboarding curriculum for each of four contributor profiles.

### Profile A — No-skill / generalist contributor (helps operator with day-to-day)

- **Day 1-30 (orient):** Google AI Essentials (<5 hr) + Google AI for Small Businesses (~5 hr). Read `docs/DOCS_INDEX.md`, `CLAUDE.md`, `SYSTEM_OWNER_VISION.md`. Shadow Pearl_PM via `artifacts/coordination/`.
- **Day 31-90 (skill build):** Begin Google Project Management Certificate (~180 hr at 10 hr/wk = 4-5 mo). Pair with operator on weekly workstream creation. Author your first STARTUP_RECEIPT.
- **Day 91-180 (specialize):** Skillshop Google Ads + GA4 Certifications (~30 hr combined, free). Trainee owns marketing-content + freebie-funnel work alongside Pearl_Marketing. First small ticket: wire a conversion event in `funnel/`.

### Profile B — Entry-level technical contributor (helps ship Pearl Prime code)

- **Day 1-30:** Google AI Essentials. Read `scripts/run_pipeline.py` end-to-end. Read `specs/PHOENIX_V4_5_WRITER_SPEC.md` §1-§5. Pair-program with Pearl_Dev on the smallest open workstream.
- **Day 31-90:** **Google IT Automation with Python Certificate** (~120 hr at 10 hr/wk = 3-4 mo). This is the single highest-utility course — ~90 % of Pearl Prime repo is Python. Complete it fully.
- **Day 91-180:** Google AI Professional Certificate (~60 hr). Apply learnings to a Pearl Prime prompt in `pearl_news/prompts/` or `prompts/draft_audiobook_v2.txt`. Strictly Tier-2 (Ollama on Pearl Star) or Tier-1 (Claude) — no Gemini API calls in repo code.

### Profile C — Intermediate contributor (technical with prior coding background)

- **Day 1-30:** Skim `specs/AI_MANGA_PIPELINE_SUMMARY.md`, `docs/AUDIOBOOK_PIPELINE_SPEC.md`, `docs/VIDEO_PIPELINE_SPEC.md`. Run a manga `ep_001` end-to-end on Pearl Star to verify the toolchain. Read `config/agents/agent_registry.yaml` and understand the 14-agent split.
- **Day 31-90:** Google ML Crash Course (~40 hr, free, no banned-API risk). Pair with Pearl_Research on an EI v2 calibration sweep. Author your first dimension-gate audit.
- **Day 91-180:** Skills Boost: Agents path (free). Apply the agent-orchestration patterns to Pearl Prime's 14-agent registry. Optionally: Generative AI Leader cert ($99, ~30 hr prep) for AI-strategy fluency.

### Profile D — Advanced contributor (senior engineer)

- **Day 1-30:** Read all 19 subsystem authority docs. Author a DISCOVERY REPORT pattern for your first non-trivial PR (per `~/.claude/memory/feedback_discover_before_acting.md`).
- **Day 31-90:** Pick one Integration roadmap item from §7 and ship it. Suggested first item: DuckDB over YAML SSOT (lower coordination cost, higher operator visibility).
- **Day 91-180:** Optional GCP Pro cert ($200, ~150 hr prep) — career value high, repo value via concept-transfer only. Better alternative: pair with the author of `docs/SLO_REGISTRY.md` and ship Integration #2.

---

## 10. Closing

The Google learning catalog is generous enough that Pearl Prime does not need to build its own training program. What Pearl Prime needs is **a selection rubric** — which course, for which contributor, with which Pearl agent shadowing, leading to which first small ticket.

That rubric is in this document. The fit map in `RESEARCH_NOTES.md` §3 is the operator's reference table. The deck (`CONTRIBUTOR_LEARNING_PATHWAYS.pptx`) is the presentation surface for sharing with prospective contributors and onboarding-tier conversations.

The honest signal worth flagging once more: **AI is reshaping the entry-level tech job market in real time**, with sharp softening at junior data analyst, junior UX, junior digital marketing, IT support tier 1, and PPC specialist roles. Recommending those certificates to trainees who want a career boost is no longer sufficient — bundle them with AI fluency, a portfolio piece, and a Pearl Prime contribution.

The single most defensible cert in the catalog right now is **Google IT Automation with Python**. It works for Pearl Prime directly. It works in the job market. It carries no Tier-policy risk. And it pairs naturally with the Pearl_Dev + Pearl_DevOps shadowing flow that already exists in repo.

Operator's question — "what people need to learn, how that helps Pearl Prime, and what it means for their career" — has its answer.

---

*See also: `RESEARCH_NOTES.md` (research log + raw citations + verification flags) and `CONTRIBUTOR_LEARNING_PATHWAYS.pptx` (operator-facing deck) in the same directory.*
