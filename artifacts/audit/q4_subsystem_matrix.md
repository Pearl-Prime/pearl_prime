# Q4 — Subsystem Readiness Matrix

**Date:** 2026-04-29  •  Synthesis of the three cluster audits: [`q4_book_cluster.md`](./q4_book_cluster.md), [`q4_manga_cluster.md`](./q4_manga_cluster.md), [`q4_ops_cluster.md`](./q4_ops_cluster.md).

## Master matrix — 22 subsystems

22 = 18 from `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` + 4 proposed (lora_pipeline, freebie, storefront_distribution, character_consistency). `freebie` already has spec at `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` so is partially-canonized.

| # | subsystem | owner | %  | shipping_today | top_blocker | phase |
|---|---|---|---:|---|---|---|
| 1 | core_pipeline | Pearl_Prime | 70 | partial — chapter prose produced | EPUB packager missing | 1 |
| 2 | pearl_prime | Pearl_Prime | 65 | partial — Workers preview live | sentinel evidence absent (`artifacts/sentinel/` empty); spec-739 phase 3 strict-runtime not landed | 2 |
| 3 | teacher_mode | Pearl_Editor | 60 | partial — 14 teacher banks present; teacher_showcase active | format-grid overhaul (PR #798) not merged | 2 |
| 4 | manga_pipeline | Pearl_Dev | 35 | NO | renders not bound to chapter scripts; GATE-OP-1/2 operator-side | 3 |
| 5 | manga_catalog | Pearl_Architect | 80 | YES — 1,350 series + 18,900 books + 8 markets | overproduction vs render throughput (18,900:0) | 3 |
| 6 | pearl_news | Pearl_News | 75 | YES — LIVE on WordPress, 81 articles | daily cron at 57% pass rate; 2 failures 2026-04-28 | 4 |
| 7 | translation | Pearl_Localization | 60 | partial — zh_TW 92% / ja_JP 89% / zh_CN ~30% | zh_CN ~2,200 atoms pending | 5 |
| 8 | video_pipeline | Pearl_Video | 75 | partial — only test renders | locale-aware book-video render path | 2 |
| 9 | ei_v2 | Pearl_Research | 70 | advisory — 18 modules, 21 tests | promotion gate not exercised; learned_params ≈ seed | 0 |
| 10 | trend_feeds | Pearl_Int | 70 | partial — `research_feeds_ingest.yml` runs | output destination → consumer pipeline not wired | 4 |
| 11 | recommendations | Pearl_PM | 15 | NO — `backlog` per authority map | no producer; 1 test | 6 |
| 12 | brand_admin | Pearl_Prez | 55 | partial — landing shell present, per-brand authoring just unblocked | 0 tests; per-brand content pipe missing | 4 |
| 13 | ite | Pearl_Dev | 75 | partial — pipeline code exists | depends on manga_pipeline render output | 3 |
| 14 | character_consistency (proposed) | Pearl_Dev | 45 | NO | 12 of 37 brands have LoRA plans; LoRA training VRAM blocked (PR #623) | 3 |
| 15 | lora_pipeline (proposed) | Pearl_Dev | 15 | NO | hardware decision pending: GPU upgrade ≥24GB / cloud $600-1500 / IP-Adapter | 3 |
| 16 | integrations | Pearl_Int | 80 | partial — registry mostly current | INTEGRATION_CREDENTIALS_REGISTRY drift: missing DeepSeek, Google AI Studio, R2_* | 0 |
| 17 | pearl_devops | Pearl_DevOps | 85 | YES — 75 workflows, governance ruleset live | required-check drift: ruleset only requires `Verify governance` not the 4 named in spec; 0 required reviewers; bypass actor `bypass_mode: always` | 0 |
| 18 | audiobook_pipeline | Pearl_Dev | 35 | partial — 13 ch1 mp3 only | full-book TTS path not exercised; `audiobook-regression.yml` is dry-run-only | 2 |
| 19 | marketing | Pearl_Marketing | 20 | partial — 1 funnel of ~26 | no funnel-builder, no automation | 4 |
| 20 | podcast_pipeline | Pearl_Prime | 30 | NO — 1 pilot only | `pearl_news/research/podcast/` doesn't exist; `config/integrations/podcast_credentials.yaml` doesn't exist | 5 |
| 21 | dashboard | Pearl_Brand | 30 | partial — `docs/PIPELINE_DASHBOARD_INDEX.md` is a doc, not interactive | per-brand dashboard not built; series_description card swap pending (PR #581) | 4 |
| 22 | freebie | Pearl_Marketing | 35 | partial — 42 EN breathwork apps live | JP LINE funnel paper-only (PR #801); no LIFF, no scheduler | 4 |
| **+** | **storefront_distribution** (gap, proposed) | n/a | 15 | NO | KDP comics + WEBTOON Canvas package builders exist (manual-paste); zero books-to-KDP, zero Apple Books, zero LINE Manga, zero podcast feeds | 1 |

## Cluster averages

- **Book cluster** (core, pearl_prime, teacher_mode, audiobook, video, ei_v2, translation, podcast): 57.5% mean
- **Manga cluster** (manga_pipeline, manga_catalog, ite, character_consistency, lora_pipeline): 50% mean
- **Ops cluster** (pearl_news, trend_feeds, integrations, pearl_devops, brand_admin, dashboard, marketing, freebie, recommendations, storefront): 47% mean
- **All-22 weighted**: ~50%

## Dependency map (who-blocks-whom)

```
storefront_distribution ←─ pearl_prime + audiobook + manga_pipeline + podcast
                            (no consumer = no shipped product)
ei_v2 (Phase 0 quality net) ←─ EVERY content subsystem
translation ←─ books + manga + audiobook + podcast (multi-locale)
integrations ←─ EVERY subsystem with API calls
pearl_devops ←─ EVERY subsystem (CI gates)
lora_pipeline ←─ character_consistency ←─ manga_pipeline render
GATE-OP-1/2 (operator) ←─ manga_pipeline first-ship
```

The two highest-leverage fixes by dependency degree:

1. **storefront_distribution** — unblocks 4 content producers
2. **ei_v2 promotion** — quality safety net for everything

## Phase tag rollup

| phase | subsystem count | high-level theme |
|---:|---:|---|
| 0 (foundation) | 3 | ei_v2, integrations, pearl_devops |
| 1 (catalog → storefront) | 2 | core_pipeline, storefront_distribution |
| 2 (Pearl Prime book pipeline) | 4 | pearl_prime, teacher_mode, video, audiobook |
| 3 (manga pipeline) | 5 | manga_pipeline, manga_catalog, ite, character_consistency, lora_pipeline |
| 4 (surfaces & ops) | 5 | pearl_news, brand_admin, dashboard, marketing, trend_feeds, freebie |
| 5 (multi-locale + podcast) | 2 | translation, podcast_pipeline |
| 6 (full automation) | 1 | recommendations |

See [`../../docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md`](../../docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md) for the chronological pathway.
