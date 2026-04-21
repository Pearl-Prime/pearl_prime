# Big View System — Gap Report
Generated: 2026-04-22
Branch: agent/big-view-phase1

Sources audited:
- config/catalog_planning/ (29 files)
- config/catalog/ (4 files)
- config/quality/ (6 files)
- atoms/ (14 persona dirs, 4,592 CANONICAL.txt files)
- scripts/catalog/, scripts/inventory/, scripts/release/
- brand-wizard-app/public/ (12 HTML files)

---

## EXISTS

- **brand_teacher_matrix.yaml** → `config/catalog_planning/brand_teacher_matrix.yaml` — 12 global-west teacher brands with primary teacher assignments
- **brand_teacher_matrix_zh.yaml** → `config/catalog_planning/brand_teacher_matrix_zh.yaml` — 24 CJK brands (6 base × 4 locales: zh-TW, zh-HK, zh-CN, zh-SG)
- **locale_brand_names.yaml** → `config/catalog_planning/locale_brand_names.yaml` — 12 market locale names for all 12 teacher brands (japan, korea, taiwan, china, dach, france, spain, italy, latam, brazil, hungary, english_global)
- **canonical_topics.yaml** → `config/catalog_planning/canonical_topics.yaml` — 15 canonical topics
- **canonical_personas.yaml** → `config/catalog_planning/canonical_personas.yaml` — 11 canonical personas
- **catalog_generation_config.yaml** → `config/catalog/catalog_generation_config.yaml` — 13 locales defined with tiers, pricing multipliers, 17 topics, 13 personas
- **Atom inventory** → `atoms/` — 14 persona dirs, 4,592 CANONICAL.txt files; all 165 canonical persona × topic combos complete
- **generate_full_catalog.py** → `scripts/catalog/generate_full_catalog.py` — has `--lane`, `--brand`, `--all-lanes` flags
- **Quality gates** → `config/quality/` — bestseller_craft_gate.yaml, book_pass_gate_thresholds.yaml, book_quality_gate.yaml, canary_config.yaml, ei_v2_config.yaml, ei_v2_promotion_criteria.yaml
- **Content inventory UI** → `brand-wizard-app/public/content_inventory.html`
- **Market lane matrix UI** → `brand-wizard-app/public/market_lane_matrix.html`
- **Brand admin UI** → `brand-wizard-app/public/brand_admin.html`
- **Manga dashboards** → `brand-wizard-app/public/` — stillness_press, cognitive_clarity, digital_ground (us_eng) manga dashboards
- **Competitive intel APAC** → `config/catalog_planning/competitive_intel_apac_audio.yaml`
- **Scan content inventory script** → `scripts/inventory/scan_content_inventory.py`

---

## PARTIAL

- **Market catalog registry** → MISSING before this PR; `catalog_generation_config.yaml` had locale definitions scattered (not a unified market registry). **Created by this PR**: `config/catalog/market_catalog_registry.yaml`
- **generate_full_catalog.py flags** → has `--lane`/`--brand`/`--all-lanes`; MISSING `--scope all`, `--market` flags for Big View batch operations. Phase 2 item.
- **Teacher mode** → Named-teacher mode fully configured (1 primary teacher per brand). MISSING generalized "teachings-first" variant that doesn't name the teacher. Phase 2 item.
- **Manga system** → 3 brands have manga dashboards (Stillness Press, Cognitive Clarity, Digital Ground). MISSING: character-to-brand linkage for remaining 9 brands, manga asset estimator, background cost calculator. Phase 3 item.
- **Japan dual-track config** → Japan market defined with dual-track in new registry. MISSING: atom-level manga pipeline (manga content currently separate from atom system). Phase 3 item.
- **QA findings registry** → Gate thresholds exist in `config/quality/`. MISSING: findings log / regression memory (artifact tracking what passed/failed over time). Phase 2 item.
- **Atom coverage for catalog_generation_config personas** → 13 personas in catalog config vs 11 in canonical_personas.yaml. `educators` and `midlife_women` are in atoms/ but not in canonical_personas.yaml. Needs reconciliation.
- **Non-canonical topics** → `adhd_focus` and `mindfulness` in catalog_generation_config.yaml topics but not in canonical_topics.yaml. Atom dirs exist (e.g., atoms/corporate_managers/adhd_focus). Needs reconciliation or formal split.

---

## MISSING

- **`config/catalog/market_catalog_registry.yaml`** — unified market registry → **BUILT by this PR**
- **`scripts/inventory/atom_coverage_audit.py`** — topic × persona coverage matrix script → **BUILT by this PR**
- **`artifacts/inventory/atom_coverage_matrix.json`** — machine-readable coverage output → **BUILT by this PR**
- **`artifacts/inventory/atom_coverage_report.md`** — coverage report markdown → **BUILT by this PR**
- **`artifacts/inventory/buildability_dashboard.md`** — per-market, per-persona buildability → **BUILT by this PR**
- **`brand-wizard-app/public/exec_catalog_dashboard.html`** — executive catalog dashboard UI → **BUILT by this PR**
- **`--scope all` / `--market` flags** in generate_full_catalog.py → Phase 2
- **QA findings log** in `artifacts/qa/` → Phase 2
- **Teacher mode generalized variant** → Phase 2
- **Manga asset estimator** → Phase 3
- **Brand-admin handoff polish** → Phase 4
- **312-brand target** — currently 36 brand entities (12 teacher + 24 zh); per-locale brand splits for secondary/tertiary needed to reach 312. Phase 2+

---

## Phase 1 Build List (completed this PR)

- [x] `config/catalog/market_catalog_registry.yaml` — 14-market registry with Japan dual-track
- [x] `scripts/inventory/atom_coverage_audit.py` — topic × persona coverage matrix generator
- [x] `artifacts/inventory/atom_coverage_matrix.json` — live coverage data (165/165 = 100%)
- [x] `artifacts/inventory/atom_coverage_report.md` — human-readable coverage report
- [x] `artifacts/inventory/buildability_dashboard.md` — per-market, per-persona, per-topic buildability
- [x] `artifacts/inventory/big_view_gap_report.md` — this file
- [x] `brand-wizard-app/public/exec_catalog_dashboard.html` — executive catalog dashboard

---

## Phase 2 Requirements

- [ ] `--scope all --market <id> --brand <id>` flags for generate_full_catalog.py
- [ ] Bestseller analysis integrated into catalog build pipeline
- [ ] Teacher mode generalized variant (teachings-based, no named teacher)
- [ ] QA findings registry (`artifacts/qa/findings_log.yaml` or similar)
- [ ] Non-canonical persona/topic reconciliation (educators, midlife_women, adhd_focus, mindfulness)
- [ ] Research signal surface in exec dashboard (catalog_buying_trigger.yaml, competitive_intel_apac_audio.yaml)
- [ ] Path to 312-brand target: per-locale brand splits for secondary/tertiary markets

## Phase 3–5 Requirements

- [ ] Manga maturity system: character-to-brand linkage for all 12 brands
- [ ] Manga asset estimator (background cost, layout estimate)
- [ ] Japan dual-track atom pipeline (manga content vs ebook atom system)
- [ ] Korea webtoon track pipeline
- [ ] Brand-admin handoff polish (exec-facing controls)
- [ ] Full operational UI with live build triggers
