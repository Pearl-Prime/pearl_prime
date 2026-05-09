# Marketing volume SSOT — discovery report (2026-05-09)

**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
**Program:** WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 (PR #964 ratified)  
**Surface:** P0 Surface 6 — Marketing volume SSOT (audit PR #961; `artifacts/qa/go_live_readiness_audit_2026-05-08.md`)  
**Agent:** Pearl_PM (discovery + scoping only; no implementation)

---

## STARTUP_RECEIPT

- **Authority read:** `artifacts/qa/go_live_readiness_audit_2026-05-08.md` Surface 6 (lines 220–247): consolidated `brand × surface × weekly target` registry **missing**; operator Table 6 cannot be filled from one SSOT file; status **RED**.
- **Baseline:** Branch `agent/marketing-volume-ssot-discovery-20260509` from `origin/main` (see commit SHA in CLOSEOUT after merge).
- **Scope:** Locate existing volume-related configs; classify vs operator intent (“per-brand weekly volumes: series, book, manga, podcast, video” + shorts/locale in program spec); pick outcome A/B/C; bind follow-up workstreams.

---

## Phase 1 — Discovery (read-only)

### Commands executed (repo root)

Per program instructions, the following discovery passes were run (paths under `phoenix_omega`; `.claude/*` and `*_wt/*` exclusions applied where noted):

- `find … -name '*.yaml' -path '*marketing*' -not -path '*/.claude/*'`
- `find … -type f -name '*.tsv' -path '*marketing*'`
- `find … -path '*marketing_deep_research*' | head`
- `find … -name '*volume*' -not -path '*/.claude/*' | head`
- `find … -name '*velocity*' -not -path '*/.claude/*' | head`
- `find config/release_velocity -type f`
- `ls config/marketing`
- `ls marketing_deep_research` (if present)

**Representative findings (non-exhaustive but sufficient for classification):**

| Path | Role / summary | Marketing “per-brand × surface × week” SSOT? |
|------|----------------|-----------------------------------------------|
| `config/marketing/marketing_assumptions.yaml` | Funnel / conversion / LTV **assumptions** for projections and dashboards (header declares SSOT for funnel models). | **No** — not production volume targets by surface. |
| `config/release_velocity/safe_velocity.yaml` | **Platform** imprint min/max **per_week** bands (e.g. Google Play, Findaway, Ximalaya). | **No** — regulatory/cap layer, not marketing’s brand×surface matrix. |
| `config/release_velocity/velocity_ramp.yaml` | Aspirational **70–84 books/week/brand** at steady state; phased ramp; explicitly **capped** by `safe_velocity.yaml`. | **No** — long-term book throughput band, not full surface set (manga/podcast/video/shorts) per brand. |
| `config/catalog/weekly_queue_config.yaml` | Global `titles_per_brand_per_week: 15` + **weekly_mix** splits + **lane_weekly_mix** per locale (manga vs ebook counts summing to 15). **Podcast** block additive (episodes/micro/sleep) with pointers to other YAMLs. | **Partial** — encodes **one** canonical “15 titles/week” production story and locale lane splits; **not** operator’s unified six-surface marketing table; podcast/video not expressed as one row per brand×surface×locale. |
| `config/video/upload_schedule.yaml` | Upload cadence; `weekly_production` assumes **15 books/week** → derived **videos_per_week** (75) and per-platform math. | **Partial** — derives video load from book assumption; not per-brand marketing SSOT. |
| `config/podcast/platform_distribution.yaml` | Per-brand-type knobs e.g. `episodes_per_brand_per_week`, `micro_episodes_per_brand_per_week`. | **Partial** — podcast slice only; overlaps with `weekly_queue_config.yaml` podcast_weekly. |
| `config/manga/japan_dual_track_config.yaml` | `weekly_cap: 8` (JP ebook cap) and dual-track ebook/manga counts. | **Partial** — regional pipeline cap, not global marketing matrix. |
| `config/manga/korea_webtoon_config.yaml` | Various `weekly_cap` / per-brand ebook counts. | **Partial** — lane/medium specific. |
| `config/catalog_planning/brand_teacher_matrix.yaml` (+ locale variants) | Teacher / catalog planning spacing and caps (often **monthly** framing). | **No** — planning matrix, not marketing weekly volume SSOT. |
| `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md` | Promotion routing / lanes. | **No** — rules, not numeric weekly volume SSOT (audit agrees). |
| `brand-wizard-app/public/brand_admin.html` (and related) | Static “15 titles/week” style promise **without** cited repo SSOT in-page (audit cites lines ~421, 500–502). | **Evidence of drift risk**, not SSOT. |
| `marketing_deep_research/` (when present) | Research notes / inputs. | **No** — not ratified operational SSOT unless explicitly promoted (none found as such). |

**Conclusion of Phase 1:** There is **no** single checked-in artifact that matches the operator table: **per-brand × per-surface (ebooks, audiobooks, manga, podcast, video, shorts) × weekly targets with explicit locale breakdown and governance metadata**.

---

## Phase 2 — Gap analysis and outcome

### Conflicts / overlaps (why this is not outcome A)

- **“15 titles/week”** appears as a **global** production anchor (`weekly_queue_config.yaml`, `upload_schedule.yaml`, brand admin copy) while **`velocity_ramp.yaml`** asserts a very different **aspirational 70–84 books/week** band for mature channels (then clamped by platforms).
- **Podcast** weekly counts appear in both **`weekly_queue_config.yaml`** (`podcast_weekly`) and **`platform_distribution.yaml`** (per-distribution type) — same concern, two homes.
- **Regional/manga** caps (`japan_dual_track_config.yaml`, `korea_webtoon_config.yaml`) add **third** and **fourth** “weekly” semantics (caps vs mix vs marketing intent).

### Outcome selected: **OUTCOME-B**

**Multiple candidate docs encode overlapping or conflicting “weekly volume” semantics, but none is the canonical marketing SSOT** described by the operator and required by Surface 6. The correct response is to **propose one canonical file + supersession rules** (see `docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md`) and run a dedicated **authoring** workstream to populate it, then **consumer wiring** (Pearl_Dev) after the file exists.

*(If the operator later collapses all numbers into one existing file without contradiction, a future amendment could reclassify to OUTCOME-A; current evidence supports B.)*

---

## Phase 3 — Deliverables and follow-ups

| Deliverable | Path |
|-------------|------|
| Binding schema + consumer contract (proposed) | `docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md` |
| Coordination | `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — `ws_worldwide_gl_s06_marketing_volume_ssot_20260508` → **in_progress**; **open** `ws_worldwide_gl_s06_authoring_followup_20260509` (**proposed**) |

**Follow-up workstream names**

1. **`ws_worldwide_gl_s06_authoring_followup_20260509`** — Pearl_Marketing: author `config/marketing/weekly_volumes_per_brand.yaml` (or path ratified in spec); reconcile legacy knobs.
2. **Consumer wire (post-YAML)** — track under program Surfaces 2/3/8 or a future Pearl_Dev row: dashboards and packaging read **only** the new SSOT for operator-visible targets.

**HANDOFF_TO:** **Pearl_Marketing** (author canonical YAML per spec). **Pearl_Dev** after SSOT file lands (wire consumers; no code in this PR).

---

## References

- `artifacts/qa/go_live_readiness_audit_2026-05-08.md` — Surface 6  
- `docs/PEARL_PM_STATE.md`; `docs/PEARL_ARCHITECT_STATE.md` — program caps + amendments  
- `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` — ratified program scope  
