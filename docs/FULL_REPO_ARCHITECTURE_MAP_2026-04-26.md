# Full Repo Architecture Map — 2026-04-26

**Purpose:** visual reference for system architecture at Phoenix Omega's
2026-04-26 baseline (`origin/main` HEAD `1f4f8a28f`).

Diagrams below render in any GitHub markdown viewer or Mermaid-aware tool.

---

## 1. Top-level subsystem graph

```mermaid
flowchart TB
    Operator[Operator + Specialist Agents]
    Coord[Repo Coordination<br/>ACTIVE_PROJECTS.tsv<br/>ACTIVE_WORKSTREAMS.tsv]
    Arch[Pearl_Architect<br/>SUBSYSTEM_AUTHORITY_MAP]

    Operator --> Coord
    Operator --> Arch

    subgraph Authoring
        Prime[Pearl_Prime<br/>books pipeline]
        News[Pearl_News<br/>editorial cycle]
        Manga[Pearl_Manga<br/>visual + lettering + webtoon]
        Audio[Audiobook<br/>MVP]
        Podcast[Podcast<br/>RESEARCH ONLY]
    end

    subgraph Brand_Layer
        Wizard[Brand Wizard<br/>YAML generator]
        Admin[Brand Admin<br/>weekly package]
        Mkt[Marketing<br/>NO platform_marketing/]
    end

    subgraph Infra
        DevOps[Pearl_DevOps<br/>NO authority row]
        Int[Integrations<br/>R2 / B2 / Mac / GitHub LFS]
        TLS[Translation<br/>5 locales]
        Vid[Video / TTS]
        EI[EI v2 quality]
    end

    Coord --> Authoring
    Coord --> Brand_Layer
    Coord --> Infra
    Arch -.canonical map.-> Authoring
    Arch -.canonical map.-> Brand_Layer

    Authoring --> Vid
    Authoring --> TLS
    Authoring --> EI
    Brand_Layer --> Authoring
    Infra --> Authoring
    Infra --> Brand_Layer

    style DevOps fill:#fee
    style Mkt fill:#fee
    style Podcast fill:#fee
```

Red boxes = subsystems with structural gaps surfaced by this audit (DevOps absent
from authority map; Marketing missing `platform_marketing/`; Podcast research-only).

## 2. Pearl Prime book pipeline data flow

```mermaid
flowchart LR
    Research[docs/research/<br/>marketing_deep_research/]
    Brand[config/brand_registry.yaml<br/>config/brand_author_assignments.yaml]
    Teacher[SOURCE_OF_TRUTH/teacher_banks/<br/>config/authoring/pen_name_teacher_profiles.yaml]
    Atoms[atoms/{persona}/{topic}/{engine}/CANONICAL.txt<br/>17090 entries]
    Arcs[config/source_of_truth/master_arcs/]
    Specs[specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md<br/>specs/PHOENIX_V4_5_WRITER_SPEC.md]

    Research --> Brand
    Brand --> Teacher
    Teacher --> Atoms

    Atoms --> CLI{run_pipeline.py<br/>canonical CLI}
    Arcs --> CLI
    Specs -.governs.-> CLI

    CLI --> Slots[Slot grid:<br/>STORY sec 2/5/9<br/>JOURNEY sec 4/8<br/>SCENE]
    Slots --> Compose[compose_section_packet<br/>compose_from_enriched_book]
    Compose --> Audit[section_packet_audit.json<br/>quality_summary.json]
    Audit --> Render[book.txt<br/>render_dir]

    style CLI fill:#ffd
```

Spine path: spec at `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md:570-577`.
Phase 2 wiring (BG-PR-09 update 2026-04-26) is gated on `ws_bestseller_pipeline_default_path_b_20260425`.

## 3. Manga ep_001 ship pipeline (proj_manga_first_ship_20260425)

```mermaid
flowchart LR
    Script[chapter_script.yaml<br/>ep_001 35 panels]
    Trans[translate_chapter_script.py<br/>Tier 2 Qwen]
    Locale[text_by_locale<br/>ja_JP/zh_TW/zh_CN]
    Prompts[panel_prompts.json<br/>FLUX-schnell-fp8]
    PearlStar[Pearl Star<br/>SSH render]
    Bubble[bubble_render.py]
    Webtoon[webtoon_compose.py<br/>vertical strips]
    R2[R2 upload<br/>scripts/artifacts/r2_sync.py]
    WEBTOON[WEBTOON Canvas<br/>publish/webtoon_canvas_upload.py]

    Script --> Trans
    Trans --> Locale
    Script --> Prompts
    Prompts --> PearlStar
    PearlStar --> Bubble
    Locale --> Bubble
    Bubble --> Webtoon
    Webtoon --> R2
    R2 --> WEBTOON

    style PearlStar fill:#fef
```

Pink box = operator-driven Pearl Star Mac (per `proj_manga_first_ship_20260425`
GATE-OP-2). All other steps are repo-driven scripts.

## 4. Pearl News daily editorial flow

```mermaid
flowchart TB
    Trends[Trend Feeds<br/>scripts/feeds/]
    Research[pearl_news/research/<br/>Qwen deep-research]
    Templates[pearl_news/prompts/<br/>v52 templates]
    TeacherSlot[Deterministic teacher slots<br/>per PR #587]

    Trends --> Daily{run_daily_news_cycle.py}
    Research --> Daily
    Templates --> Daily
    TeacherSlot --> Daily

    Daily --> Render[v5.4 sidebar<br/>per PR #592]
    Render --> Publish[Live render]

    PearlStar[Pearl Star<br/>Tier 2 Gemma EN<br/>Qwen CJK6] -.runtime.-> Daily

    style PearlStar fill:#fef
```

## 5. Brand Wizard + Brand Admin flow

```mermaid
flowchart TB
    Seed[config/brand_registry.yaml<br/>28 brands]
    Expanded[config/brand_management/<br/>global_brand_registry.yaml<br/>312 entries]
    Wizard[brand-wizard-app/<br/>React + Vite + Tailwind<br/>committed node_modules: 6984 files]
    Admin[scripts/build_weekly_brand_package.py<br/>2026-04-26 live]
    HTML[brand_admin.html<br/>brand_admin_weekly_os.html<br/>brand-wizard-app/public/brand_admin.html<br/>TRIPLE-MAINTAINED]

    Seed -.fractured canon.-> Expanded
    Seed --> Wizard
    Wizard --> Admin
    Admin --> HTML

    style Seed fill:#fee
    style Expanded fill:#fee
    style Wizard fill:#fee
    style HTML fill:#fee
```

Red boxes = audit-surfaced governance issues (C-1 brand-count canon, C-4 triple
HTML maintenance, brand-wizard-app/node_modules committed).

## 6. Storage layer

```mermaid
flowchart LR
    Code[GitHub<br/>42257 tracked files]
    LFS[GitHub LFS<br/>select binary dirs]
    R2[Cloudflare R2<br/>rendered manga<br/>webtoon strips<br/>video assets<br/>audiobook masters]
    B2[Backblaze B2<br/>pivot in progress]
    Mac[Pearl Star Mac<br/>render workspace<br/>SSH pearlstar.tail7fd910.ts.net]

    Code -.r2_sync.py.-> R2
    Code -.in progress.-> B2
    Code -.GATE-OP-2 marker.-> Mac
    Mac -.uploads.-> R2
    Mac -.uploads.-> B2

    Reg[docs/INTEGRATION_CREDENTIALS_REGISTRY.md] -.governs.-> R2
    Reg -.governs.-> B2

    style B2 fill:#ffe
```

Yellow = pivot in progress.

## 7. Governance + CI

```mermaid
flowchart TB
    PR[Open PR]
    PG[scripts/git/push_guard.py]
    PF[scripts/ci/preflight_push.sh]
    LLMP[.github/workflows/<br/>llm-policy-enforcement.yml<br/>banned paid LLM APIs]
    AUD[scripts/ci/audit_llm_callers.py]
    GOV[scripts/ci/pr_governance_review.py<br/>mass-delete + scope + drift]
    BPR[BRANCH_PROTECTION_REQUIREMENTS.md<br/>4 required checks]
    CI[GitHub Actions<br/>72 workflows]

    PR --> PG
    PG --> PF
    PF --> AUD
    AUD --> GOV
    GOV -.WIRED MANUALLY ONLY.-> CI
    LLMP --> CI
    BPR -.required checks gate.-> CI
    CI --> Merge[Merge if APPROVED]

    style GOV fill:#ffe
```

Yellow = `pr_governance_review.py` exists but is NOT wired to a GitHub workflow;
runs manually via `pre_merge_check.sh`. **GAP-3 in implementation plan.**

## 8. LLM tier routing

```mermaid
flowchart LR
    Op[Operator typing in CLI]
    Sched[Scheduled pipeline cron]

    Op -->|Tier 1| Claude[Claude Code subscription<br/>Opus 4.7 1M ctx<br/>operator-present]
    Sched -->|Tier 2| PearlStar[Pearl Star Ollama<br/>Gemma EN<br/>Qwen CJK6]

    Banned[BANNED:<br/>ANTHROPIC_API_KEY<br/>OpenAI cloud<br/>Google AI<br/>DashScope cloud<br/>Together / Replicate<br/>Perplexity / Cohere<br/>Mistral paid]
    Banned -.enforced by.-> AUD2[audit_llm_callers.py]
    AUD2 -.blocks PR.-> Mergeable

    Claude --> Mergeable
    PearlStar --> Mergeable

    style Banned fill:#fee
    style Claude fill:#efe
    style PearlStar fill:#efe
```

## 9. Workstream lifecycle

```mermaid
stateDiagram-v2
    [*] --> proposed
    proposed --> active: Pearl_PM opens
    active --> blocked: prerequisite ws stalls
    blocked --> active: prereq closes
    active --> completed: deliverable lands
    active --> cancelled: superseded by another decision
    completed --> [*]
    cancelled --> [*]

    proposed: Proposed (next_action only)
    active: Active (current work)
    blocked: Blocked (prereq)
    completed: Completed (PR landed)
    cancelled: Cancelled (superseded)
```

Pearl_PM transitions ws state in `ACTIVE_WORKSTREAMS.tsv`. Audit found 7 schema-
malformed ws rows that need column-shift fix (see `IMPLEMENTATION_GAP_PLAN` GAP-1).

## 10. PR sequence for THIS audit

```mermaid
gitGraph
    commit id: "1f4f8a28f baseline"
    branch agent/full-repo-recon-spec-20260426
    commit id: "PR-1 spec"
    checkout main
    merge agent/full-repo-recon-spec-20260426 tag: "PR-1 merged"
    branch agent/full-repo-recon-tools-20260426
    commit id: "PR-2 4 audit scripts"
    checkout main
    merge agent/full-repo-recon-tools-20260426 tag: "PR-2 merged"
    branch agent/full-repo-recon-inventory-20260426
    commit id: "PR-3 5 inventory CSVs+MD"
    checkout main
    merge agent/full-repo-recon-inventory-20260426 tag: "PR-3 merged"
    branch agent/full-repo-recon-canonical-docs-20260426
    commit id: "PR-4 6 canonical docs"
    checkout main
    merge agent/full-repo-recon-canonical-docs-20260426 tag: "PR-4 merged"
```

After PR-4 lands, operator review gates PR-5+ (deletion buckets D1-D3 + remediation
PRs GAP-1 through GAP-4).

## 11. Documentation graph (where to start)

```mermaid
flowchart TB
    PE[docs/PLAIN_ENGLISH_SYSTEM_OVERVIEW.md] --> Sys[docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md]
    Sys --> Map[docs/FULL_REPO_CANONICAL_SYSTEM_MAP_2026-04-26.md]
    Sys --> Arch[docs/FULL_REPO_ARCHITECTURE_MAP_2026-04-26.md]
    Sys --> Del[docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md]
    Sys --> Gap[docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md]
    Sys -.cites.-> Inv[artifacts/inventory/full_repo_*_2026-04-26.csv]

    PE -.5min orientation.-> Reader[New contributor]
    Sys -.full audit.-> Operator
    Map -.routing decisions.-> Architect[Pearl_Architect]
    Del -.deletion plan.-> GH[Pearl_GitHub]
    Gap -.remediation.-> Specialists[Pearl_<subsystem>]

    style PE fill:#efe
```

Green = fastest entry point.
