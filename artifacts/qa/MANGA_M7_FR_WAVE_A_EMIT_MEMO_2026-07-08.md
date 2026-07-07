# M7 fr_FR Wave A Emit Memo — 2026-07-08

**M7 status:** PARTIAL (plans lane only; grid not green)
**Locale:** fr_FR (`fr_bd_manga` lane)
**Base:** `origin/main` @ 23dec52f174 (PR #4727 — batch 1 merged)

---

## 1. Readiness audit (verified this session)

| Check | Result | Evidence |
|---|---|---|
| `locale_genre_allocations.yaml` fr_FR block | **PASS** | `fr_bd_manga` lane; 10 genres; shares sum 100 |
| `format_routing.yaml` fr_FR block | **PASS** | `defaults_by_locale_genre`, platforms, connector, pending partners |
| Generator consumption | **PASS** | `generate_catalog_plan_from_strategic.py` VALID_LOCALES includes `fr_FR` |
| `run_m7_wave_a.py` wired | **PASS** | allocation-derived 70/30 blend; schema v2.4.0 validation |
| Existing fr_FR plans on main | **180** | batch 1 merged (PR #4727) |
| Dry-run (fresh) | **390 plans, 0 schema failures** | 1 brand skipped (`bright_presence_tw_seinen` manga_locales) |

---

## 2. Commands run

### Batch 1 (merged PR #4727 @ 23dec52f174)

```bash
PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \
  --max-files 180 \
  --out-root config/source_of_truth/manga_series_plans
# → wrote 180 files
```

### Batch 2 (PR #4729 @ 73021d28ee)

```bash
git checkout -b agent/manga-m7-fr-wave-a-batch2-20260708 origin/main

PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \
  --skip 180 --max-files 180 \
  --out-root config/source_of_truth/manga_series_plans
# → wrote 180 files; 0 schema failures
```

### Batch 3 (PR #4730 @ 0092d31b84)

```bash
git checkout -b agent/manga-m7-fr-wave-a-batch3-20260708 origin/main

PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \
  --skip 360 --max-files 180 \
  --out-root config/source_of_truth/manga_series_plans
# → wrote 30 files (remainder); 0 schema failures
```

### Post-all-batches (operator, after batch 3 merged)

```bash
# Regenerate fr_FR catalog CSV (2X.5) + conformance TSV re-run
```

---

## 3. Batch status

| Batch | Plans | Files | Status | PR | Boundary (emission order) |
|---|---:|---:|---|---|---|
| **1** | 1–180 | 180 | **MERGED** | #4727 | `stillness_press__fr_FR__iyashikei__series01` → `optimizer_workplace__fr_FR__iyashikei__series01` |
| **2** | 181–360 | 180 | **OPEN** | #4729 | `optimizer_workplace__fr_FR__dark_fantasy__series01` → `hormone_reset_healing__fr_FR__school_coming_of_age__series01` |
| **3** | 361–390 | 30 | **OPEN** | #4730 | `qi_foundation_cultivation__fr_FR__iyashikei__series01` → `calm_student_school__fr_FR__school_coming_of_age__series01` |

**Total derived:** 390 plans across 36 brands (37 canonical − 1 `bright_presence_tw_seinen` manga_locales skip).

**Merge order:** batch 2 → batch 3 (sequential; no filename overlap).

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
manga-m7-fr-fr-emitted-batch2=180
manga-m7-fr-fr-emitted-batch3=30
manga-m7-fr-fr-remaining=0
manga-m7-fr-batch-status=batch-2-and-3-open-awaiting-merge
manga-m7-fr-batch2-pr=4729
manga-m7-fr-batch3-pr=4730
manga-m7-fr-blockers=none-for-fr_FR;other-locales-format_routing_missing_8;ko_KR_hold
manga-m7-grid-green=NO
```
