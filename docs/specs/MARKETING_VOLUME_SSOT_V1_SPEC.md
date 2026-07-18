# Marketing volume SSOT — V1 specification (binding template)

**Status:** Proposed (Pearl_PM discovery 2026-05-09; **OUTCOME-B** — canonical file not yet authored)  
**Program:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 / WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01  
**Related audit:** PR #961 — `artifacts/qa/go_live_readiness_audit_2026-05-08.md` Surface 6  
**Discovery artifact:** `artifacts/qa/marketing_volume_ssot_discovery_2026-05-09.md`

This document is the **binding template** for the first marketing weekly volume SSOT. **Do not** treat legacy scattered YAMLs as authoritative for operator-facing “Table 6” numbers once this file exists.

---

## 1. Canonical SSOT location

**Proposed path (canonical once authored):** `config/marketing/weekly_volumes_per_brand.yaml`

**Rationale:** Keeps marketing-owned numeric policy under `config/marketing/`, distinct from platform caps (`config/release_velocity/safe_velocity.yaml`) and pipeline mix mechanics (`config/catalog/weekly_queue_config.yaml`).

---

## 2. Schema (normative)

### 2.1 Document envelope

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | yes | e.g. `"1.0"` |
| `last_updated` | ISO-8601 date | yes | Calendar date of last marketing-approved change |
| `owner_agent` | string | yes | e.g. `Pearl_Marketing` |
| `source` | string | yes | Human-readable provenance (e.g. “2026-05 operator weekly targets sheet v3”) |
| `status` | enum | yes | `draft` \| `active` \| `deprecated` — only `active` may drive production UIs without a warning banner |
| `notes` | string | no | Freeform reconciliation notes (e.g. supersession of legacy 15/week display) |

### 2.2 Row grain

Each **volume row** is uniquely identified by:

- `brand_id` — must exist in brand registry / canonical brand list used by the program.
- `locale` — BCP-47 style tag (e.g. `en_US`, `ja_JP`) or program-approved locale key; `default` allowed only when marketing explicitly declares one row applies to all locales for that brand.
- `surface` — one of: `ebook` | `audiobook` | `manga` | `podcast` | `video` | `shorts`

**Cells:**

- `weekly_target` — non-negative integer; marketing’s **committed** weekly output target for that surface (interpretation: “ship-ready units per week” unless `unit` overrides).
- `unit` (optional) — e.g. `titles` | `episodes` | `uploads` | `chapters`; default `titles` for ebook/audiobook/manga if omitted.
- `series_installments_weekly` (optional) — when marketing splits “series cadence” vs “standalone” explicitly; if present, consumers must document how it rolls into dashboards.

### 2.3 Status per row (optional refinement)

If marketing needs per-brand rollout without a second file:

- `row_status`: `active` | `inactive` | `planned`

**Interaction with brand activity (program Surface 4):** Only brands classified **active** by `ws_worldwide_gl_s04_active_brand_ssot_20260508` (PR #972 lineage) **consume** volume rows for scheduling and UI. **Inactive** brands: rows may remain for planning but **must be ignored** by consumers (no promises on brand admin / exec dashboard).

### 2.4 Verbatim YAML shape (template — values illustrative only)

```yaml
schema_version: "1.0"
last_updated: "2026-05-09"
owner_agent: "Pearl_Marketing"
source: "REPLACE: operator marketing sheet ID / version"
status: "draft"

notes: >
  REPLACE: reconciliation summary vs legacy 15/week display and velocity_ramp
  aspirational band.

volumes:
  - brand_id: "example_brand_us"
    locale: "en_US"
    surface: "ebook"
    weekly_target: 0
    unit: "titles"
    row_status: "planned"
  - brand_id: "example_brand_us"
    locale: "en_US"
    surface: "audiobook"
    weekly_target: 0
    unit: "titles"
  - brand_id: "example_brand_us"
    locale: "en_US"
    surface: "manga"
    weekly_target: 0
    unit: "titles"
  - brand_id: "example_brand_us"
    locale: "en_US"
    surface: "podcast"
    weekly_target: 0
    unit: "episodes"
  - brand_id: "example_brand_us"
    locale: "en_US"
    surface: "video"
    weekly_target: 0
    unit: "uploads"
  - brand_id: "example_brand_us"
    locale: "en_US"
    surface: "shorts"
    weekly_target: 0
    unit: "uploads"
```

---

## 3. Supersession rule (OUTCOME-B)

When `config/marketing/weekly_volumes_per_brand.yaml` is **`active`**:

1. **Operator-facing targets** (exec catalog dashboard, brand admin weekly panels, weekly packaging summaries) **must** read weekly numbers from this file (joined with active-brand classifier), **not** from `weekly_queue_config.yaml` headline counts, `velocity_ramp.yaml` aspirational bands, or HTML literals.
2. **Platform caps** in `config/release_velocity/safe_velocity.yaml` remain **hard constraints** — schedulers and release tooling **clamp** effective throughput; if a marketing target exceeds a platform cap, the **consumer** surfaces both numbers (target vs cap) or fails validation in CI (policy choice for Pearl_Dev).
3. **Pipeline mix** files (`weekly_queue_config.yaml`, manga lane YAMLs, `upload_schedule.yaml`) remain **mechanical** “how to compose the 15-title basket” until refactored; their numeric **promises** must **align** to the SSOT after a reconciliation pass (authoring WS), or carry explicit `deprecated_in_favor_of: marketing_volume_ssot_v1` comments in a follow-up PR.

---

## 4. Consumer integration pattern (non-code contract)

**Producers:** Pearl_Marketing (author); Pearl_PM (governance / program alignment).

**Consumers (future Pearl_Dev wiring):**

| Consumer | Expected read |
|----------|----------------|
| `brand-wizard-app/public/exec_catalog_dashboard.html` (Surface 8) | Fetch or embed build artifact generated **from** SSOT + registry join; **no** hard-coded `MARKETS[]` weekly literals for targets. |
| `brand_admin.html` / weekly OS surfaces (Surface 2) | Locale grid + per-surface columns from SSOT join. |
| `scripts/release/build_admin_packets.py` and weekly packaging (Surface 3) | Include SSOT slice in operator bundle JSON/markdown. |
| Catalog planners / queue builders | Treat SSOT as **upper intent**; enforce `safe_velocity` and regional caps as **downstream** constraints. |

**Join keys:** `brand_id`, `locale`, `surface`, plus **active** flag from Surface 4 SSOT.

---

## 5. Authoring workflow

1. **Owner:** Pearl_Marketing fills `weekly_volumes_per_brand.yaml` from the operator ratified sheet.
2. **Cadence:** Update on program cadence (weekly marketing review) or when operator revises Table 6; bump `last_updated` every edit.
3. **Validation (recommended checks for a future CI script, not implemented here):**
   - Every `brand_id` ∈ canonical brand list for the program scope.
   - No duplicate (`brand_id`, `locale`, `surface`) triples.
   - `weekly_target` non-negative integers; `unit` valid for `surface`.
   - Optional: cross-check sum of ebook+manga+… against `safe_velocity` min/max for dominant platform lane — **warn** on exceed, **error** if program chooses hard gate.
4. **Promotion:** `status: draft` → `active` only after Pearl_PM + operator acknowledgment in program amendment or PR comment.

---

## 6. Cap registry name (informational)

Audit suggested cap name **MARKETING-WEEKLY-VOLUME-SSOT-V1-01**. This spec file may be referenced by that cap once ratified in `docs/PEARL_ARCHITECT_STATE.md`.
