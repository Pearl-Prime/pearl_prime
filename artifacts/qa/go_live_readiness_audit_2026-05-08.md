# Go-Live Readiness Audit — WORLDWIDE-CATALOG-GO-LIVE-V1

**Audit date:** 2026-05-08  
**Agent:** Pearl_PM (read-only audit)  
**PROJECT_ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
**Worktree:** `/Users/ahjan/phoenix_omega_qi_foundation_recon_wt`  
**Commit (pre-write, `origin/main`):** `f7c8915cc52e456664ed4cb44329e459241d6b30`  

**STARTUP_RECEIPT (session)**  
AGENT: Pearl_PM  
TASK: Worldwide catalog go-live V1 — program audit + gap matrix + disk notes (no implementation)  
PROJECT_ID: PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
SUBSYSTEM: pearl_pm coordination + cross-cutting surfaces below  
AUTHORITY_DOCS: Read: `docs/SESSION_UNITY_PROTOCOL.md`; `docs/PEARL_PM_STATE.md`; `docs/PEARL_ARCHITECT_STATE.md`; `docs/DOCS_INDEX.md`; `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` (header/purpose); `specs/PHOENIX_V4_5_WRITER_SPEC.md` (indexed via DOCS_INDEX); `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` (cross-ref); `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`; `BRAND_ADMIN_CANONICAL_PACKAGE.md`; `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`  
READ_PATH_COMPLETE: yes (targeted reads + file evidence for each surface; no subagents)  
WRITE_SCOPE: Exactly the five files declared in the operator packet (program spec, architect cap + program TSV + ws TSV, this audit)  
OUT_OF_SCOPE: Code, config edits, LLM calls, PR merge  
BLOCKERS: none  
READY_STATUS: ready  

This document is the **per-surface gap matrix** (Phase A), **phased roadmap** (Phase B), and **operator decision card** (Phase D). The ratified **program cap** lives in `docs/PEARL_ARCHITECT_STATE.md` → `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` (Phase C).

---

## Audit method

- Repo evidence read from the clean worktree above (branch `agent/worldwide-catalog-go-live-v1-program-audit-20260508` tracking `origin/main` after `git fetch`).
- Claims cite **existing** path and line ranges as observed.
- **37 brands** appears in repo as **manga canon** (`config/manga/canonical_brand_list.yaml` — **37** `brands:` keys, verified via Python load in this audit). **Pearl Prime book-script catalogs** use **fewer distinct `brand` values per locale** (12–19) per `artifacts/catalog/pearl_prime_book_script_catalogs/README.md` — this is intentional **Path X** separation per `BRAND_ADMIN_CANONICAL_PACKAGE.md`.

---

## Phase A — Per-surface gap matrix (surfaces 1–10)

### Surface 1 — Worldwide catalog planning (37 × 4 locales)

**Discover (what exists)**

- Pearl Prime **book-script** catalogs (queue rows, not manuscripts):  

```17:21:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/artifacts/catalog/pearl_prime_book_script_catalogs/README.md
| `en_US_catalog.csv`      | English-global Pearl Prime book script catalog (12 brands, primary tier)   |
| `ja_JP_catalog.csv`      | Japanese Pearl Prime book script catalog (12 brands, primary tier)         |
| `zh_TW_catalog.csv`      | Traditional Chinese (Taiwan) catalog (19 brands incl. `bright_presence_tw`) |
| `zh_CN_catalog.csv`      | Simplified Chinese (mainland) catalog (18 brands)                          |
| `catalog_summary.json`   | Aggregated row counts, status breakdown, source file SHA-256 fingerprints  |
```

- Aggregated row counts (`catalog_summary.json`):  

```4:37:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/artifacts/catalog/pearl_prime_book_script_catalogs/catalog_summary.json
  "totals": {
    "en_US": {
      "rows": 1478,
      ...
    },
    "ja_JP": {
      "rows": 1478,
      ...
    },
    "zh_TW": {
      "rows": 2818,
      "ready": 2658,
      "blocked": 160,
...
    },
    "zh_CN": {
      "rows": 2630,
```

- **`runtime_format`** is **`standard_book`** in the Pearl Prime structural lock:

```37:39:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/artifacts/catalog/pearl_prime_book_script_catalogs/README.md
| `pipeline_route`       | `scripts/run_pipeline.py --pipeline-mode spine`          |
| `runtime_format`       | `standard_book` (default; from `config/format_selection/format_registry.yaml`) |
```

- Plan-side YAML inputs exist under `config/catalog_planning/` (35 YAML files enumerated in audit; e.g. `teacher_brand_archetypes.yaml`, `canonical_topics.yaml`).
- **Manga** locale CSVs under `artifacts/catalog/manga/` — row counts verified in-session:  
  **en_US 170 rows / 12 brands; ja_JP 166/12; zh_TW 275/19; zh_CN 269/18** (`*_manga_catalog.csv`).
- Manga **37-brand** registry file: **37** keys under `brands:` in `config/manga/canonical_brand_list.yaml` (Python `yaml.safe_load` count in this audit).

**Compare to operator target “37 brands × 4 locales”**

- **Manga axis:** 37 canonical manga brands exist in config, but **locale CSV brand coverage remains 12–19 brands**, not 37 per locale — **gap** vs a literal “all 37 in every locale plan row” interpretation.
- **Pearl Prime book axis:** README explicitly documents **12–19 brands**, not 37 — aligned with Path X (**not** a failure of README; **failure vs operator wording** unless scope is tightened to Path X).

**Per locale (book-script CSV) — operator rubric**

| Locale | Rows | Distinct brands (`brand` column) | `teacher_id` spread | `runtime_format` | vs 37-brand target |
|--------|-----:|--------------------------------:|---------------------|-------------------|-------------------|
| en_US  | 1478 | 12 | 12 non-empty | `standard_book` (schema) | **not Planned for 37** per README |
| ja_JP  | 1478 | 12 | 12 non-empty | same | same |
| zh_TW  | 2818 | 19 | 13 non-empty | same | same |
| zh_CN  | 2630 | 18 | 12 non-empty | same | same |

**Per locale — status vs rubric**

- **en_US / ja_JP (Pearl Prime book queue):** `ready_for_assembly` **for declared scope** (`ready`=row count per `catalog_summary.json`); **partial** vs “37 brands” wording.  
- **zh_TW:** **partial** (`blocked_score` **160** rows per `catalog_summary.json`).  
- **zh_CN:** **ready_for_assembly** for declared Row count.all ready.  
- **Manga CSVs:** **partial** vs “37 × 4” — brand coverage **below 37** in all four audited locale files.

- **Status:** **red**  
- **Owner agent (remediation):** Pearl_Architect + Pearl_Brand (registry/plan reconciliation)  
- **Recommended cap entry name:** WORLDWIDE-CATALOG-COVERAGE-V1-01  
- **Estimated effort:** **XL**  
- **Dependencies:** Path X scope ratification (book vs manga axis) from operator Q1–Q2  

---

### Surface 2 — Brand dashboard (existing)

**Discover**

- Root `brand_admin.html` — **static** operator checklist UI; **Phase 3 “Weekly”** exists but **locked until prior phases** (lines **162–182** show nav + weekly rhythm label).
- **Upload / platform** surfaces include KDP, Apple, **WEBTOON**, Kobo, **TikTok**, **YouTube** in the `UPLOADS` array (e.g. **283–286**).
- **Weekly cadence copy** claims **“15 titles”** and **“8 ebooks + 4 manga + 3 micro”** (**421**, **500–502**).
- Canonical package lists dashboard HTML paths:

```75:79:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/BRAND_ADMIN_CANONICAL_PACKAGE.md
**Pearl_Brand also owns dashboard surfaces** under DASH-02 (operator decision 2026-04-27, ratified in `docs/PEARL_ARCHITECT_STATE.md`). Dashboard surfaces governed by Pearl_Brand: `brand_admin.html`, `brand_admin_weekly_os.html`, `brand-wizard-app/public/brand_admin.html`, and the `dashboard/` subsystem itself.
```

- **`dashboard/` subsystem path:** **not present** as a directory at repo root in this `origin/main` checkout (path check: **no files** — this **is** a finding vs the canonical package line above).

**Checklist vs operator ask**

| Operator surface | Present in `brand_admin.html`? |
|------------------|----------------------------------|
| eBook scripts planned | **partial** (upload checklist + weekly copy; not a live catalog grid) |
| Audiobook scripts planned | **partial** (same UI; no separate audiobook queue) |
| Manga / illustrated planned | **partial** (WEBTOON + weekly copy) |
| Podcasts planned | **missing** (no podcast row in_upload array lines **280–286**) |
| Videos planned | **partial** (TikTok + YouTube) |
| Short-form planned | **partial** (“micro” copy **421** / **500**) |
| Per-week production volume | **partial** (static “15 titles” **421**) |
| Status done / not done per piece | **missing** (localStorage-driven checklists, not repo-backed production truth) |
| Per-locale breakdown | **missing** as a first-class dashboard dimension in this file |

**Active vs static**

- **Static HTML + local browser state** — **not** “served production app” in-repo; Cloudflare / hosting is **out of scope** for this audit — **treat as static-only** unless operator provides deploy URL + auth.

- **Status:** **yellow**  
- **Owner agent:** Pearl_Brand + Pearl_Dev (data binding)  
- **Recommended cap entry name:** BRAND-DASHBOARD-PRODUCTION-BINDING-V1-01  
- **Estimated effort:** **L**  
- **Dependencies:** Surface 6 (volume SSOT), Surface 1 (catalog truth)  

---

### Surface 3 — Brand admin weekly download packaging

**Discover**

- `scripts/release/build_admin_packets.py` documents **weekly platform-specific download packets** and output tree (**lines 1–24**).
- **Hardcoded main-repo path** fallback:

```41:43:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/scripts/release/build_admin_packets.py
_WORKTREE = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_REPO_ROOT = _MAIN_REPO if _MAIN_REPO.exists() else _WORKTREE
```

- **No** `.github/workflows` match for `build_admin_packets` (search in `/.github/workflows` for **`build_admin_packets`**: **0** hits) — automation **not** wired in CI in this checkout.
- Supporting script reference from executive dashboard (**Surface 8**): `python3 scripts/release/build_admin_packets.py --all --week current --dry-run` (**`brand-wizard-app/public/exec_catalog_dashboard.html` lines 389–390, 619–621**).

**Platform rubric**

- **KDP / Audible / reader platforms:** **wired in code** (`amazon_kdp`, `audible`, `apple_books`, etc. caps **56–63**).
- **WEBTOON / TikTok / YouTube:** **not** enumerated as platforms in **`PLATFORM_WEEKLY_CAPS`** (**56–63**) — weekly bundling for those channels **not represented** in this builder’s platform map (UI handles upload elsewhere — **disconnect**).

- **Notification / download link:** **no** workflow or mail integration found in-repo in this audit pass.

- **Status:** **yellow**  
- **Owner agent:** Pearl_Dev + Pearl_DevOps  
- **Recommended cap entry name:** WEEKLY-ADMIN-PACKETS-AUTO-V1-01  
- **Estimated effort:** **M**  
- **Dependencies:** Surface 2 (what admins see), Surface 6 (targets)  

---

### Surface 4 — Active vs inactive brand classification (“brand wizard YAML”)

**Discover**

- `brand-wizard-app/` contains **zero** `.yaml` files (**glob `brand-wizard-app/**/*.yaml`**: **0** hits on `origin/main`).
- `config/brand_registry.yaml` — **Python count: 26** top-level brands under **`brands:`** (audit script; file starts at **lines 10–26** showing multiple brand keys).

**Interpretation**

- Operator hypothesis “wizard YAML canonical for active brands” — **unsupported on `origin/main`** (no persisted wizard outputs discovered in wizard app tree).
- **Path X authority** explicitly separates book vs manga registries (**`BRAND_ADMIN_CANONICAL_PACKAGE.md` lines 13–20**).

- **Status:** **red**  
- **Owner agent:** Pearl_Brand (+ Pearl_Dev if exporter must persist YAML)  
- **Recommended cap entry name:** ACTIVE-BRAND-SSOT-V1-01  
- **Estimated effort:** **M**  
- **Dependencies:** Operator confirmation of canon (Surface D Q4)  

---

### Surface 5 — Per-brand author/teacher coverage (6–12 authors + bios)

**Discover**

- `config/brand_author_assignments.yaml` carries **explicit author pools** — example **stillness_press** lists **12** `author_pool` entries (**lines 14–27**).
- Bios / profiles are expected under authoring config per subsystem history (`config/authoring/pen_name_teacher_profiles.yaml` referenced across docs; file **exists** — not fully audited row-by-row in this session).
- **Coverage gap:** YAML structure shows **heavy** authoring for **`stillness_press`** at file head; full **37-brand × 12-author** conformance was **not** verified (would require scripted matrix against `canonical_brand_list.yaml`).

- **Status:** **yellow**  
- **Owner agent:** Pearl_Editor + Pearl_Writer  
- **Recommended cap entry name:** BRAND-AUTHOR-BIO-MATRIX-V1-01  
- **Estimated effort:** **L**  
- **Dependencies:** Surface 4 (which brands are active)  

---

### Surface 6 — Marketing-driven weekly volumes

**Discover**

- **Platform velocity caps** exist — not per-brand marketing matrix:

```27:36:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/config/release_velocity/safe_velocity.yaml
google_play_books:
  new_imprint:
    per_week: [10, 20]      # min, max
    per_month: [40, 60]
    per_year: [400, 600]
  established_imprint:
    per_week: [25, 50]
```

- `brand_admin.html` marketing-style promise **15 titles/week** (**421**, **500–502**) **without** a cited repo SSOT in that HTML.
- `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md` routes promotion lanes — **no** per-brand weekly production matrix table for all surfaces (**lines 1–38** are rules + candidate list, not volume SSOT).

**Operator table (Table 6)**

- **Cannot be filled honestly from a single SSOT file** — **missing** consolidated `brand × surface × weekly target` registry linked to dashboard.

- **Status:** **red**  
- **Owner agent:** Pearl_Marketing + Pearl_PM  
- **Recommended cap entry name:** MARKETING-WEEKLY-VOLUME-SSOT-V1-01  
- **Estimated effort:** **M**  
- **Dependencies:** Surface 1 (what’s buildable)  

---

### Surface 7 — Spine pipeline performance (CLI vs chat)

**Discover**

- Canonical spine invocation documented:

```571:577:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic <topic> --persona <persona> \
  --arc <arc.yaml> --pipeline-mode spine \
  --runtime-format <format> \
  --quality-profile flagship \
  --no-job-check --render-book \
```

- Entry point file header confirms CLI surface (`scripts/run_pipeline.py` **lines 1–7**).
- **Architect state** documents **SCENE slot consumption gap** vs pilot (`docs/PEARL_ARCHITECT_STATE.md` **BG-PR-09** narrative around **lines 114–118** in file ) — explains **why “fast pilot” vs “canonical CLI”** can diverge in **quality**, not just **wall time**.

**Timings**

- **No end-to-end benchmark** was run in this audit session (Tier-1 no long runs). **Cannot** state actual wall-clock — **gap**.

**Slow path vs fast path (documentary)**

- **Fast path (operator-direct):** use **`scripts/run_pipeline.py`** as documented above + pre-resolved arc/atoms; avoid chat wrappers that re-load large context.  
- **Slow path:** conversational agents rehydrate specs + repo context each turn; chat is not pinned to **`REPO_ROOT`** the way the CLI’s `run_pipeline.py` **`Path(__file__).resolve()`** pattern implies.

- **Status:** **yellow**  
- **Owner agent:** Pearl_Dev  
- **Recommended cap entry name:** SPINE-PERF-BASELINE-V1-01  
- **Estimated effort:** **S** (benchmark + report)  
- **Dependencies:** None for measurement; BG-PR-09 Phase 2 wiring for parity  

---

### Surface 8 — Executive view dashboard

**Discover**

- `brand-wizard-app/public/exec_catalog_dashboard.html` — title **“Executive Catalog Dashboard”** (**lines 4–6**).
- Loads **repo artifact JSON** via **relative fetch**:

```673:673:/Users/ahjan/phoenix_omega_qi_foundation_recon_wt/brand-wizard-app/public/exec_catalog_dashboard.html
      const resp = await fetch("../../artifacts/pipeline_last_run.json");
```

(similar **`atom_coverage_matrix.json`** fetch **752**).

**Interpretation**

- **Executive rollup exists** as a **local static page + artifact pulls**.  
- **Auto-update:** only if **`artifacts/*.json`** is regenerated by pipelines / ops — **no** proof in this audit of continuous refresh.
- KPI blocks include **marketing-style `MARKETS[]` block** (**lines 630–644**) embedding **brand_count** literals — drift risk vs live registries.

- **Status:** **yellow**  
- **Owner agent:** Pearl_Brand + Pearl_Dev  
- **Recommended cap entry name:** EXEC-DASHBOARD-LIVE-WIRE-V1-01  
- **Estimated effort:** **M**  
- **Dependencies:** Surfaces 1, 6, 7 artifact producers  

---

### Surface 9 — Phoenix Command UI / CLI connections

**Discover**

- `exec_catalog_dashboard.html` embeds multiple **`python3 scripts/...`** command strings (**387–390**, **618–621**, **`runHandoffExport` / clipboard flows** elsewhere in same file — pattern: **documents** CLI; does **not** invoke Python from browser sandbox).
- Referenced **`scripts/manga/manga_asset_estimator.py`** and **`scripts/manga/build_manga_catalog.py`** — **both exist** (`scripts/manga/` glob).
- **Risk:** dashboards can **cite stale** commands vs renamed flags — mitigated only by pairing UI work with **`scripts/catalog/`** generators that match **`DOCS_INDEX.md`** (**line 62–63** references `generate_full_catalog` bundle).

- **Status:** **yellow**  
- **Owner agent:** Pearl_Dev + Pearl_GitHub  
- **Recommended cap entry name:** COMMAND-UI-CLI-SYNC-V1-01  
- **Estimated effort:** **S**  
- **Dependencies:** Stable script list from Surface 7 owners  

---

### Surface 10 — Uncommitted disk audit (worktrees + main)

**Method limits**

- Full enumeration of **every** `phoenix_omega_*_wt` path within 60–90 min wall target: **not completed**. **Sampled** clean states:
  - `phoenix_omega_qi_foundation_recon_wt` — **0** `git status --short` lines; branch **`agent/worldwide-catalog-go-live-v1-program-audit-20260508`**
  - `phoenix_omega_catalog_v2_isolation_wt` — **0** lines; **`agent/catalog-800-v2-isolation-clean-20260508`**
  - `phoenix_omega_phase_c_isolation_wt` — **0** lines; **`agent/manga-phase-c-prompt-builder-isolation-20260508`**
- **Primary workspace** `/Users/ahjan/phoenix_omega`: operator reported **corrupted index**; session **start** `git status` showed **large** dirty trees (audio, manga fixtures, coordination handoffs, etc.) — **not re-run** here to avoid blocking the audit.

**Table 10 (partial)**

| Worktree / path | Uncommitted (sample) | Likely surface | Recommendation |
|-----------------|--------------------|----------------|----------------|
| `/Users/ahjan/phoenix_omega` (session snapshot) | Many `M`/`??` artifacts per initial status | mixed: manga, audio, coordination | **review-with-operator** + fix index before bulk commit |
| `*_qi_foundation_recon_wt` (pre-change) | clean | — | — |
| `*_catalog_v2_isolation_wt` | clean | catalog / research | — |
| `*_phase_c_isolation_wt` | clean | manga pipeline | — |
| Other `phoenix_omega_*` dirs | **not sampled** | unknown | **unknown-need-review** (run scripted inventory) |

- **Status:** **yellow**  
- **Owner agent:** Pearl_GitHub  
- **Recommended cap entry name:** WORKTREE-DIRT-INVENTORY-V1-01  
- **Estimated effort:** **S**  
- **Dependencies:** Healthy `git` on main workspace  

---

## Phase A — Scoreboard

| Surface | Status |
|---------|--------|
| 1 Catalog planning | **red** |
| 2 Brand dashboard | **yellow** |
| 3 Weekly packaging | **yellow** |
| 4 Active/inactive brands | **red** |
| 5 Author/bio coverage | **yellow** |
| 6 Marketing volumes SSOT | **red** |
| 7 Spine / CLI performance | **yellow** |
| 8 Executive dashboard | **yellow** |
| 9 Command UI ↔ CLI | **yellow** |
| 10 Disk / worktree audit | **yellow** |

**Counts:** **green = 0**, **yellow = 7**, **red = 3**

---

## Phase B — Phased roadmap (entry / exit / ws)

**Phase 1 — Visibility unlock**  
- **Surfaces:** **2, 6, 8** (dashboard + executive view + marketing SSOT seed **must** exist to interpret greens truthfully).  
- **Entry:** This audit merged + operator Q1–Q5 answered.  
- **Exit:** (a) Executive dashboard reads **non-stale** artifacts with documented refresh owner; (b) marketing volume SSOT **authored** (YAML/TSV) and linked from dashboard; (c) brand dashboard shows **locale + per-surface targets** for active brands.  
- **Ws rows (this program):** `ws_worldwide_gl_s02_*`, `ws_worldwide_gl_s06_*`, `ws_worldwide_gl_s08_*` (see `ACTIVE_WORKSTREAMS.tsv`).

**Phase 2 — Active-brand wiring**  
- **Surfaces:** **3, 4, 7, 9** (weekly packets + active classification + CLI perf truth + UI command sync).  
- **Exit:** Weekly packet build runs on **CI or scheduled runner**; active brand list **published**; benchmark doc for spine; UI commands **verified** against `main`.

**Phase 3 — Catalog completion**  
- **Surfaces:** **1, 5** (37×4 interpretation locked + author matrix).  
- **Exit:** Locale catalogs match **ratified** brand list per axis; author/bio matrix complete for **active** brands.

**Phase 4 — Production go-live**  
- **Surfaces:** **10 + all** (clean worktrees; no orphan artifacts; monitoring).  
- **Exit:** `git status` clean on operator golden paths; go-live checklist signed (`docs/GO_LIVE_FINAL_CHECKLIST.md` cross-ref as needed).

---

## Phase D — Operator decision card (verbatim)

**Q1:** Phase priority order — does the proposed Phase **1→4** sequence match your intent (visibility → wiring → catalog → go-live)?  

**Q2:** Which surfaces are **P0 (this week)**, **P1 (next 2 weeks)**, **P2 (later)**?  

**Q3:** For each **uncommitted disk** finding in **Table 10** (and the broader `/Users/ahjan/phoenix_omega` snapshot) — **commit-now**, **abandon**, or **review-with-operator**?  

**Q4:** For **active-brand classification** — confirm **`brand_wizard` YAML** (or another path) as **canonical SSOT**, or specify an **override** file?  

**Q5:** For **weekly download cadence** — what **day of week**; **email + file** delivery, or **file-only**?  

---

## Related artifacts

- Program spec: `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md`  
- Cap entry: `docs/PEARL_ARCHITECT_STATE.md` → `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01`  
- Registry rows: `artifacts/coordination/ACTIVE_PROJECTS.tsv`, `ACTIVE_WORKSTREAMS.tsv`  

---

*END AUDIT — implementation intentionally out of scope.*
