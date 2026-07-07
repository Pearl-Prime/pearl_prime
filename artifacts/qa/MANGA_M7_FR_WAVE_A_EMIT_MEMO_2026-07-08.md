# M7 fr_FR Wave A Emit Memo — 2026-07-08

**M7 status:** PARTIAL (plans lane only; grid not green)
**Locale:** fr_FR (`fr_bd_manga` lane)
**Branch:** `agent/manga-m7-fr-wave-a-batch1-20260708`
**Base:** `origin/main` @ 9f70a3d6ec (PR #4725 — `run_m7_wave_a.py` + fr_FR routing)

---

## 1. Readiness audit (verified this session)

| Check | Result | Evidence |
|---|---|---|
| `locale_genre_allocations.yaml` fr_FR block | **PASS** | `fr_bd_manga` lane; 10 genres; shares sum 100 |
| `format_routing.yaml` fr_FR block | **PASS** | `defaults_by_locale_genre`, platforms, connector, pending partners |
| Generator consumption | **PASS** | `generate_catalog_plan_from_strategic.py` VALID_LOCALES includes `fr_FR` |
| `run_m7_wave_a.py` wired | **PASS** | allocation-derived 70/30 blend; schema v2.4.0 validation |
| Existing fr_FR plans on main | **0** | `config/source_of_truth/manga_series_plans/fr_FR/` absent pre-emit |
| Dry-run (fresh) | **390 plans, 0 schema failures** | 1 brand skipped (`bright_presence_tw_seinen` manga_locales) |

---

## 2. Commands run

### Preflight / dry-run

```bash
cd /Users/ahjan/phoenix_omega
git checkout -b agent/manga-m7-fr-wave-a-batch1-20260708 origin/main

PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR --dry-run
# → allocation-derived series: 390, schema failures: 0
```

### Batch 1 emit (this PR)

```bash
PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \
  --max-files 180 \
  --out-root config/source_of_truth/manga_series_plans
# → wrote 180 files to config/source_of_truth/manga_series_plans/fr_FR/
```

### Batch 2 (after batch 1 merged)

```bash
PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \
  --skip 180 --max-files 180 \
  --out-root config/source_of_truth/manga_series_plans
# → 180 files; starts optimizer_workplace__fr_FR__dark_fantasy__series01
#   ends hormone_reset_healing__fr_FR__school_coming_of_age__series01
```

### Batch 3 (after batch 2 merged)

```bash
PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \
  --skip 360 --max-files 180 \
  --out-root config/source_of_truth/manga_series_plans
# → 30 files (remainder); qi_foundation_cultivation through calm_student_school
```

### Post-all-batches (operator, not this PR)

```bash
# Regenerate fr_FR catalog CSV (2X.5) + conformance TSV re-run after batch 3 merged
```

---

## 3. Batch status

| Batch | Plans | Files | Status | Boundary (emission order) |
|---|---:|---:|---|---|
| **1** | 1–180 | 180 | **LANDED (this PR)** | `stillness_press__fr_FR__iyashikei__series01` → `optimizer_workplace__fr_FR__iyashikei__series01` |
| 2 | 181–360 | 180 | pending | `optimizer_workplace__fr_FR__dark_fantasy__series01` → `hormone_reset_healing__fr_FR__school_coming_of_age__series01` |
| 3 | 361–390 | 30 | pending | `qi_foundation_cultivation__fr_FR__iyashikei__series01` → `calm_student_school__fr_FR__school_coming_of_age__series01` |

**Total derived:** 390 plans across 36 brands (37 canonical − 1 `bright_presence_tw_seinen` manga_locales skip).

**Batch 1 brands (17 partial/full):** stillness_press (partial), body_memory_shojo, career_lift_workplace, cognitive_clarity, digital_ground, executive_calm_workplace, gentle_growth_healing, healing_ground_healing, high_performer_workplace, minimal_mind_healing, morning_momentum_workplace, night_reset_healing, optimizer_workplace (partial), relational_calm_iyashikei, sleep_restoration_iyashikei, somatic_wisdom_shojo, stabilizer_healing.

**Top genres (full 390):** workplace_drama=39, dark_fantasy=38, psychological_horror=38, iyashikei=37, supernatural_mystery=37.

---

## 4. Blockers for other locales

| Locale | Blocker |
|---|---|
| pt_BR, de_DE, es_ES, es_US, it_IT, hu_HU, zh_SG | `format_routing.yaml` missing `defaults_by_locale_genre` block |
| zh_HK | format routing missing + CJK deferral (operator confirm HK platform routing) |
| ko_KR | Q-MANGA-05 hold (plans exist; ship-gated) |
| Wave B | blocked on M3 story-authored lane |
| Wave C | blocked on M5 banks + assembly |

---

## 5. Machine summary

```
manga-m7-status=PARTIAL
manga-m7-fr-fr-derived-count=390
manga-m7-fr-fr-emitted-batch1=180
manga-m7-fr-fr-remaining=210
manga-m7-fr-batch-status=batch-1-of-3-landed
manga-m7-fr-blockers=none-for-fr_FR;other-locales-format_routing_missing_8;ko_KR_hold
manga-m7-grid-green=NO
```
