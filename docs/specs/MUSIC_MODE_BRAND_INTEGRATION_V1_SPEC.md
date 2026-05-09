# Music mode brand integration — V1 spec

**Status:** ACTIVE — operator Q1–Q4 ratified 2026-05-09 (see §16 + §AMENDMENT-2026-05-09)  
**Cap entry:** `MUSIC-MODE-BRAND-INTEGRATION-V1-01` in `docs/PEARL_ARCHITECT_STATE.md`  
**Project:** `PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1` in `artifacts/coordination/ACTIVE_PROJECTS.tsv`  
**Owner (ratification):** Pearl_Architect  
**Primary implementation agents:** Pearl_Brand; Pearl_Dev; Pearl_PM (coordination)  
**Subsystems:** brand_admin (primary) · music_pipeline · core_pipeline · cross-cutting  

**Authority docs:**

- `docs/PEARL_ARCHITECT_STATE.md` (cap `MUSIC-MODE-BRAND-INTEGRATION-V1-01`; cross-ref `MUSIC-MODE-V1-01`)
- `docs/SESSION_UNITY_PROTOCOL.md`
- `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` (survey field schema reference)
- `config/manga/canonical_brand_list.yaml` (Path X **37** brands — **read-only** boundary for this program)
- `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` / `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md` (active/inactive brand SSOT alignment)

---

## §1. First-class archetype + brands 38+

Music mode is a **first-class brand archetype**, not a bolt-on flag on teacher brands. **New music-mode brands start at id space 38+** and are recorded in **`config/music/music_brand_registry.yaml`** (new registry file reserved by this spec). **Path X** retains exactly **37** keys in `config/manga/canonical_brand_list.yaml`; **no** music-only rows are appended there (anti-drift: avoids canonical_brand_list contamination).

---

## §2. Wizard flow + live survey route

The **brand wizard** owns onboarding for music-mode brands end-to-end.

| Step | Purpose |
|------|---------|
| **1** | **Mode selector** — operator chooses archetype path; includes **music mode** vs non-music paths. |
| **4** | **Conditional pane** — when music mode is selected, render **`musician_reflections_survey`** inline (same wizard chrome). |

**Live route requirement:** The survey UI MUST load on a **normal wizard HTTP route** (same app origin as the wizard, e.g. `/wizard/...` or the repo’s established static-server route pattern). **`file://` URLs MUST NOT** be used for the survey surface (deprecated for this program — breaks persistence, security context, and CI reproducibility).

**Live-embed addendum:** If the survey is authored as static HTML fragments, the wizard MUST **embed** them via **server or bundler inclusion** into the live route, not by opening local files in the browser.

---

## §3. Save button + persistence + advance

The survey exposes **exactly one primary Save action** at the **bottom** of the survey pane.

**Contract (normative):**

1. User completes survey fields (schema aligned with `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` and program deltas tracked in implementation PRs).  
2. User clicks **Save**.  
3. Client issues **POST** to the wizard backend (exact path TBD in `ws_music_brand_survey_save_post_yaml_advance_20260509`).  
4. Server **persists** answers into the **wizard YAML** SSOT for that brand session (no “save only to localStorage”).  
5. On **success**, server response triggers **auto-advance** to the next wizard step.

---

## §4. Catalog: 100% music mode

Any **catalog slice** labeled as a **music-mode brand catalog** MUST contain **only** books produced under the **music-mode pipeline** contract for that brand. **Forbidden:** composite “teacher + music” hybrid rows; **forbidden:** teacher-mode books listed under a music-mode brand id.

---

## §5. Brand registry architecture

**`config/music/music_brand_registry.yaml`** is the **authoritative index** of music-mode brands (38+). It **references** wizard output keys / paths; it does not silently mint brands without wizard YAML backing.

**Active vs inactive (default Q4):** An **active** music-mode brand is one whose **brand wizard YAML** exists per the same SSOT rule as `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` Q4 (wizard YAML presence). **Inactive** brands remain represented in wizard persistence (default) rather than deleted silently.

---

## §6. Compatibility

- **37 canonical brands** and their existing **teacher / Path X** contracts remain **frozen** for this program’s ratification PR.  
- **`music_pipeline`** tooling and **`MUSIC-MODE-V1-01`** (`--music-mode` overlay, `musician_banks/`, six slot pools) remain **unchanged** unless a future implementation PR carries an explicit **AMENDMENT** to this cap.

---

## §7. Anti-drift

1. **No** edits to `canonical_brand_list.yaml` for music-mode-only brands.  
2. **No** `file://` survey hosting.  
3. **Server-backed** survey persistence only (POST → wizard YAML).  
4. **Pearl_Architect** owns cap/spec text; **Pearl_Dev** owns route + POST implementation under named ws rows.

---

## §8. Workstreams (six rows in `ACTIVE_WORKSTREAMS.tsv`)

| `workstream_id` | Intent |
|-----------------|--------|
| `ws_music_brand_wizard_step1_step4_survey_pane_20260509` | Wizard UX: step 1 mode selector + step 4 conditional `musician_reflections_survey` pane. |
| `ws_music_brand_survey_save_post_yaml_advance_20260509` | Save at bottom → POST → wizard YAML persist → auto-advance. |
| `ws_music_brand_registry_music_brand_registry_yaml_20260509` | Author `config/music/music_brand_registry.yaml` (+ join to wizard outputs). |
| `ws_music_brand_catalog_generator_100pct_music_mode_20260509` | Catalog generator: **100% music-mode** rows per §4. |
| `ws_music_brand_wizard_live_embed_routing_20260509` | Live wizard HTTP routes for survey embed; **`file://` deprecated**. |
| `ws_music_brand_freebie_funnel_followup_cap_20260509` | Placeholder — freebie/funnel music-mode = **separate follow-up cap** (no V1 implementation). |

---

## §9. Budget

- **Tier 1:** operator-present **design, ratification, Q-card** (this PR).  
- **Tier 2:** unattended **catalog regen** batches **after** Q1–Q4 lock + registry file lands.

---

## §10. Status

Program + cap are **`active`** as of **2026-05-09**. Operator **Q1–Q4** defaults are recorded in §16 and locked verbatim in **§AMENDMENT-2026-05-09**. Coordination rows: **`PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1`** **`proposed` → `active`**; six `ws_music_brand_*` rows **`proposed` → `runnable`**.

---

## §16. Operator decision card (verbatim)

Answer inline below each question (operator).

### Q1 — UX flow placement

**Question:** UX flow placement (default: mode selector at wizard step 1)

**Pearl_Architect default if no answer:** mode selector at wizard step 1.

*Operator answer:* **Accepted — Pearl_Architect default (2026-05-09 ratification).**

### Q2 — brand_id slug rule

**Question:** brand_id slug rule (default: `<musician_handle>_music`)

**Pearl_Architect default if no answer:** `<musician_handle>_music`.

*Operator answer:* **Accepted — Pearl_Architect default (2026-05-09 ratification).**

### Q3 — catalog volume tier default

**Question:** catalog volume tier default (default: 800 baseline)

**Pearl_Architect default if no answer:** 800 baseline.

*Operator answer:* **Accepted — Pearl_Architect default (2026-05-09 ratification).**

### Q4 — inactive brand path

**Question:** inactive brand path (default: same brand_wizard YAML SSOT)

**Pearl_Architect default if no answer:** same brand_wizard YAML SSOT.

*Operator answer:* **Accepted — Pearl_Architect default (2026-05-09 ratification).**

---

## §AMENDMENT-2026-05-09 — Operator Q1–Q4 defaults (binding)

This section mirrors the cap-entry amendment in `docs/PEARL_ARCHITECT_STATE.md` (**MUSIC-MODE-BRAND-INTEGRATION-V1-01 — AMENDMENT — 2026-05-09**).

1. **UX FLOW (Q1=default):**
   - Mode selector at brand wizard step 1 with options: [Standard book brand] [Manga/illustrated brand] [Music mode brand] [Hybrid (advanced — reserved)]
   - Music mode flow inserts musician reflections survey as conditional Step 4 (live wizard pane, NOT file:// URL).
   - **Anti-drift:** any UX placement change (mid-wizard, end-of-wizard, popup) requires separate AMENDMENT.

2. **BRAND_ID SLUG (Q2=default):**
   - Music mode brand_id = `<musician_handle>_music` (e.g., ahjansam_music, junko_music).
   - **Anti-drift:** alternate naming patterns (vanity slug, numeric, etc.) require separate AMENDMENT.

3. **CATALOG VOLUME TIER (Q3=default):**
   - Default tier = 800 baseline (matches Path X canonical brand volume).
   - Override via survey field `music_volume_tier` ∈ {solo, standard, enterprise}; solo<800, standard=800, enterprise>800 (specific numeric ranges TBD by Pearl_Marketing in implementation).
   - **Anti-drift:** changing the default 800 baseline requires separate AMENDMENT.

4. **INACTIVE BRAND PATH (Q4=default):**
   - Music mode brand active/inactive classification follows the same brand_wizard YAML SSOT defined in WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 + ws_worldwide_gl_s04 classifier (PR #972).
   - Music mode brands MUST appear in `config/music/music_brand_registry.yaml` AND have a brand_wizard YAML at `brand-wizard-app/brands/<brand_id>.yaml` to be active.
   - **Anti-drift:** any music-mode-specific archive/retention rule (vs Path X) requires separate AMENDMENT.

5. **STATUS TRANSITIONS:**
   - Cap entry **MUSIC-MODE-BRAND-INTEGRATION-V1-01**: status **proposed → active**.
   - **6 ws rows**: **proposed → runnable** (per `ACTIVE_WORKSTREAMS.tsv` update).
   - **PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1**: status **proposed → active**.
   - **Implementation ownership** (named, not authored here):
     - **a.** `ws_music_brand_wizard_step1_step4_survey_pane_20260509` → **Pearl_Brand**
     - **b.** `ws_music_brand_survey_save_post_yaml_advance_20260509` → **Pearl_Dev**
     - **c.** `ws_music_brand_registry_music_brand_registry_yaml_20260509` → **Pearl_Dev**
     - **d.** `ws_music_brand_catalog_generator_100pct_music_mode_20260509` → **Pearl_Dev**
     - **e.** `ws_music_brand_wizard_live_embed_routing_20260509` → **Pearl_Dev**
     - **f.** `ws_music_brand_freebie_funnel_followup_cap_20260509` → **Pearl_Architect** (authors separate cap **MUSIC-MODE-FREEBIE-FUNNEL-V1-02**)

---

## §17. Out of scope (V1 ratification PR)

- Any production wizard code change (lands under ws rows post-merge).  
- Freebie / funnel music-mode integration (tracked only under `ws_music_brand_freebie_funnel_followup_cap_20260509` as a **future cap**).  
- Changes to `MUSIC-MODE-V1-01` rendering semantics.  
- Modifying `canonical_brand_list.yaml`.

---

## §18. References

- `docs/PEARL_ARCHITECT_STATE.md` — `MUSIC-MODE-BRAND-INTEGRATION-V1-01`  
- `artifacts/coordination/ACTIVE_PROJECTS.tsv` — `PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1`  
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — six `ws_music_brand_*` rows  
- `docs/PEARL_ARCHITECT_STATE.md` — `MUSIC-MODE-V1-01` (overlay / musician_banks)  
- `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` — active brand = wizard YAML presence (Q4 alignment)
