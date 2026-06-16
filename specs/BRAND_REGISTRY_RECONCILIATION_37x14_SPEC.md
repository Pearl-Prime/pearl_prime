# Brand Registry Reconciliation — 39 brands × 14 lanes (unified book + manga%)

**Status:** DRAFT for operator review · 2026-06-15 · author: Pearl_Dev
**Decisions locked by operator (this session):** canonical-37 names win · manga is a per-lane % (not a standalone brand set).

## 0. DECISIONS LOCKED (2026-06-15)

1. **Corp / publication name = the imprint name** — these are nonprofit **publication** corps, so the name must carry "Press" / "Books" / "Publishing" / "Editions" (NOT "Fellowship"). Source = `brand_display_names.yaml` (canonical-keyed; e.g. `stillness_press`→"Stillness Press", `cognitive_clarity`→"Clear Seeing Books", `optimizer`→"Daybreak Editions"). The `corporate_structure.yaml` "{display} Fellowship" church rule is **superseded**.
2. **adi_da + joshin are ADDED** → roster is **39 brands/lane** (15 teacher + 24 standard). `awakening_press` (adi_da) keeps its name; `still_forest` (joshin) needs an imprint name with Press/Books (proposed: **"Still Forest Press"** — operator may rename).
3. **14th lane = `pt_BR`** (Brazil). Lanes = the 13 in `global_brand_registry` + `pt_BR` = 14. Needs a `pt_BR` `lane_content_mix` (manga %).
4. **`cognitive_clarity` (kenjin) = INACTIVE** — kenjin is an unactivated teacher (makes no books yet). Carry it in the registry with `lifecycle: inactive`; **do NOT build out** its deep fields. (So active build-out = the 13 thin *standard* brands only.)

**Net count:** 39 brands/lane × 14 lanes = **546** brand_ids; 1 inactive (`cognitive_clarity`), 38 active/lane.
**Do NOT change any config from this spec until approved** — this is the plan, not the migration.

---

## 1. Problem — there is no single source of truth for "the brands"

Four registries disagree on *what the brands are*, *how many*, and *what they're named*:

| Registry | Count | Naming | Depth (corp/topics/personas/mission) | Role today |
|---|---|---|---|---|
| `config/catalog_planning/teacher_brand_archetypes.yaml` (13) + `brand_archetype_registry.yaml` (24) | **37 / lane** | **canonical** (`stillness_press`, `cognitive_clarity`, …) | shallow (gtm/topics, no corp) | identity SSOT (PR #682) |
| `config/catalog_planning/teacher_brand_lane_assignments.yaml` | 37 / lane × **12 lanes** | canonical | lane/platform/market data | "master" lane map |
| `config/manga/canonical_brand_list.yaml` | **37** (manga axis) | canonical base ids (+ genre suffix) | tier/demographic/topic | manga catalog canon (Path X) |
| `config/brand_management/global_brand_registry.yaml` | **25 / lane × 13 lanes** (325) | **DIFFERENT** (`inner_light_press`, …) | **deep** (corp.name, primary_topics, personas, mission, teacher) | what `brand_admin_users.yaml` roster + brand_admin director actually use |
| `config/catalog_planning/brand_display_names.yaml` | 36 | base ids | imprint display names only | reader-facing names |

The deep data (corp, topics, personas, mission) lives **only** in `global_brand_registry`, but it has **25** brands under **different names** than the canonical 37 — they were never reconciled. Lane count is 12 / 13 / (target) 14.

**Goal:** ONE registry — **37 brands × 14 lanes**, canonically named, each brand deep (corp + topics + personas + mission + teacher) **and** carrying a per-lane manga% — that every consumer (wizard match, brand_admin director, roster, catalog generator) reads.

---

## 2. Canonical decisions (locked)

1. **Names:** the **canonical-37** ids win (`stillness_press`, `somatic_wisdom`, `qi_foundation`, `devotion_path`, …). The deep-25's rich data is **ported onto** these ids (mapped by `teacher_id`, see §4).
2. **Lanes:** **14** (the 13 in `global_brand_registry` + one more — see §6, needs the 14th named).
3. **Manga:** **not a standalone brand set.** Manga is a **per-lane content %** (`catalog_generation_config.yaml::lane_content_mix`) applied to every brand. `canonical_brand_list.yaml` (manga-37) is the *manga-axis series plan* for the same 37 brands, not a separate roster.

---

## 3. The canonical 37 (per lane)

**13 teacher brands** (1 teacher each):
`stillness_press`(ahjan), `cognitive_clarity`(kenjin), `somatic_wisdom`(pamela_fellows), `qi_foundation`(master_feung), `digital_ground`(miki), `heart_balance`(maat), `relational_calm`(miyuki), `warrior_calm`(master_wu), `sleep_restoration`(master_sha), `body_memory`(omote), `solar_return`(ra), `devotion_path`(sai_ma), `heart_transmission`(junko).

**24 standard brands:**
`adhd_forge`, `bio_flow`, `calm_student`, `career_lift`, `confidence_core`, `creative_unfold`, `executive_calm`, `focus_sprint`, `gentle_growth`, `healing_ground`, `high_performer`, `hormone_reset`, `legacy_builder`, `longevity_lab`, `minimal_mind`, `morning_momentum`, `night_reset`, `optimizer`, `relationship_clarity`, `resilient_parent`, `spiritual_ground`, `stabilizer`, `stoic_edge`, `trauma_path`.

---

## 4. Rename map — port deep-25 data onto canonical ids (by teacher)

| teacher | DEEP id (data source) | → CANONICAL id (winner) | corp.name (from deep) |
|---|---|---|---|
| ahjan | inner_light_press | **stillness_press** | Inner Light Fellowship → rename to Stillness * |
| pamela_fellows | body_wisdom | **somatic_wisdom** | Body Wisdom Fellowship → * |
| master_feung | vitality_path | **qi_foundation** | Vitality Path Fellowship → * |
| miki | gen_spark | **digital_ground** | Gen Spark Fellowship → * |
| miyuki | zen_clarity | **relational_calm** | Zen Clarity Fellowship → * |
| master_wu | iron_will | **warrior_calm** | Iron Will Fellowship → * |
| master_sha | soul_repair | **sleep_restoration** | Soul Repair Fellowship → * |
| maat | truth_compass | **heart_balance** | Truth Compass Fellowship → * |
| ra | cosmic_edge | **solar_return** | Cosmic Edge Fellowship → * |
| omote | gentle_wave | **body_memory** | Gentle Wave Fellowship → * |
| sai_ma | healing_ground_press | **devotion_path** | Healing Ground Fellowship → * |
| junko | heart_transmission | **heart_transmission** ✅ | Heart Transmission Fellowship (no change) |

\* **OPEN: corp/display name.** The deep `corp.name` ("Inner Light Fellowship") is keyed to the *deep* identity. When the id becomes `stillness_press`, do we keep the deep corp name, or regenerate as "{canonical display} Fellowship" (e.g. "Stillness Fellowship")? `brand_display_names.yaml` already has imprint names for canonical ids ("Stillness Press", etc.). **Recommend:** canonical display = `brand_display_names.yaml`; corp = "{display} Fellowship" per `corporate_structure.yaml` US rule. (Operator confirm.)

**Deep-only teachers (NOT in canonical 37):** `adi_da`→awakening_press, `joshin`→still_forest. **OPEN:** drop, or add as brands 38–39 (would break "37"). Recommend: park as out-of-scope until the 37 is settled.

---

## 5. Build-out list — the thin ones (no deep data)

**14 canonical brands have NO deep record** and must be built out (corp, primary_topics, primary_personas, mission, tradition):

- **Teacher (1):** `cognitive_clarity` (kenjin) — has identity in `teacher_brand_archetypes` but no `global_brand_registry` deep entry.
- **Standard (13):** `bio_flow`, `calm_student`, `focus_sprint`, `gentle_growth`, `healing_ground`, `high_performer`, `hormone_reset`, `longevity_lab`, `minimal_mind`, `morning_momentum`, `spiritual_ground`, `stoic_edge`, `trauma_path`.

**23 brands have portable deep data:** 12 teacher (via §4 rename) + 11 standard (`adhd_forge`, `career_lift`, `confidence_core`, `creative_unfold`, `executive_calm`, `legacy_builder`, `night_reset`, `optimizer`, `relationship_clarity`, `resilient_parent`, `stabilizer`).

> Source material for build-out exists: `teacher_brand_archetypes.yaml` + `brand_archetype_registry.yaml` carry gtm_identity/topics for all 37; `canonical_brand_list.yaml` carries manga primary/secondary topics. The thin brands need the *deep* fields (corp, personas, mission) synthesized from those + topic/persona research.

---

## 6. Lanes — 13 known, 14th TBD

Current 13 (`global_brand_registry`): `en_US, zh_TW, zh_HK, zh_CN, zh_SG, ja_JP, ko_KR, es_US, es_ES, fr_FR, de_DE, it_IT, hu_HU`.
`teacher_brand_lane_assignments` carries only 12. **OPEN: name the 14th lane** (candidate: `pt_BR` — Brazil is a top manga market; or `pt_PT`/`id_ID`/`vi_VN`). Need operator's 14-lane list to reconcile all configs up to it.

---

## 7. Manga % (per-lane content mix)

SSOT = `config/catalog/catalog_generation_config.yaml::lane_content_mix` (operative; `market_catalog_registry.yaml::content_mix` is stale). Each lane sets manga vs ebook vs micro shares applied to **all 37 brands** in that lane. Examples: `ja_JP` ≈ 70% manga (40 series + 20 standalone + 10 micro), `ko_KR` ≈ 50%, `en_US` ≈ 20%. The unified registry should **reference** the lane mix (not duplicate it), so each brand's catalog = lane manga% × brand topics.

---

## 8. Unified registry — proposed schema (per brand, per lane)

```yaml
<canonical_brand_id>_<lane>:        # e.g. stillness_press_en_us
  brand_id: <id>_<lane>
  brand_archetype_id: <canonical_id>   # stillness_press
  lane_id: en_US
  display_name: "Stillness Press"      # from brand_display_names.yaml
  corp: { entity_type, name, alignment }   # deep (renamed) OR "{display} Fellowship"
  teacher_id / teacher_mode
  tradition / brand_focus
  primary_topics: [...]                # deep OR built-out
  primary_personas: [...]
  content_families: [...]
  manga_axis: { ref: canonical_brand_list.yaml#<id>, lane_manga_pct: <from lane_content_mix> }
  music_axis: { ref: music_brand_registry.yaml }   # if applicable
  lifecycle / admin_id / mission
```

---

## 9. Migration plan (after approval)

1. **Generate** `global_brand_registry.yaml` at **37 × 14** under canonical names (extend `generate_global_registry.py`): port the 23, build out the 14, attach lane manga% + manga_axis ref.
2. **Re-key** `brand_admin_users.yaml` roster to `<canonical_id>_<lane>` (currently deep names).
3. **Align** `brand_display_names.yaml` (already canonical-keyed; fill any gaps incl. the 14 thin).
4. **Reconcile** `teacher_brand_lane_assignments.yaml` 12 → 14 lanes.
5. **Keep** `canonical_brand_list.yaml` (manga axis) + `catalog_generation_config.yaml` (manga%) as-is (already canonical/operative); cross-link.
6. **Deprecate** the 25-brand shape + the stale `market_catalog_registry.yaml::content_mix`.
7. **Validator** (CI): assert all consumers resolve the same 37 × 14 ids; no orphan names.

---

## 10. Downstream impact (gated on this)

- **Brand wizard** match → assign → log (this session's open work): the wizard must match to the unified 37 and assign a `<canonical_id>_<lane>` that IS a roster entry. **Gated** — do not finalize the wizard match/persist until the registry is unified.
- **brand_admin director + brand_index** (`brand_admin_public.py`) read the unified registry.
- **Roster** (`brand_admin_users.yaml`) assignment keys come from the unified registry.

---

## 11. Open decisions for operator (blockers to migration)

1. **Corp/display naming** for the 12 renamed brands — keep deep `corp.name`, or regenerate "{canonical display} Fellowship"? (§4)
2. **adi_da / joshin** (deep-only teachers) — drop, or add as 38–39? (§4)
3. **The 14th lane** — which locale? (§6)
4. **cognitive_clarity** corp/persona build-out source (kenjin) — research or operator-provided? (§5)
