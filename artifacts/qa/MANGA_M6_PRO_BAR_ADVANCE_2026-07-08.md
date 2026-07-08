# M6 Pro-Bar Operations — Advance Memo — 2026-07-08

**Lane:** M6 blind-10 pilot pro-bar readiness  
**Layer claim:** **PARTIAL** — P0 comparators validated (`29c8edce1d`); judges not recruited; slot_01 pre-screen in flight  
**NOT claimed:** PROVEN-AT-BAR, blind-10 PASS, manga-100pct, M6 complete

---

## 1. Live state verified

| Check | Result | Evidence |
|---|---|---|
| Blind-10 run status | **NOT_RUN** | `VERDICT.md` empty |
| P0 comparators on disk | **YES** | `comparators/yotsuba_v1_ch1_pages_5-8.pdf` (2.1 MB), `barakamon_v1_ch1_pages_6-10.pdf` (2.3 MB) |
| Registry ACQUIRED | **YES** | `COMPARATOR_REGISTRY.yaml` slot 01 — both entries ACQUIRED + sha256 |
| Validator `--require-p0` | **exit 0** | `pilot_ready: true`, `acquired: 2` |
| Acquisition method | **OFFICIAL_PREVIEW** | Licensed retail preview pages |
| slot_02 byte gate | **CLEARED** | Post-#4740: 35/35 panels pass; ep001_029 = 2,093,369 B |
| Judges recruited | **0** | `SOURCING_TRACKER.yaml` → `recruited: []` |
| Pre-screen | **pending** | `slot_01_prescreen_results.json` not archived yet; run in flight |
| Comparator closeout PR | **pending merge** | Branch `agent/m6-pilot-comparator-closeout` @ `29c8edce1d` |

---

## 2. Comparator closeout (commit `29c8edce1d`)

| Path | Action |
|---|---|
| `COMPARATOR_REGISTRY.yaml` | P0 entries → `ACQUIRED` + sha256 + `OFFICIAL_PREVIEW` |
| `SOURCING_TRACKER.yaml` | `comparators.acquired: 2`, `status: pilot_ready`, validator closeout |
| `BLOCKERS.md` | M6-BLK-004 pilot subset CLEARED; M6-BLK-005 CLEARED; M6-BLK-003 softened (Ollama online) |
| `JUDGE_PROSPECT_LIST_SLOT_01.md` | 10 named prospects, ready-to-send packet |
| `COMPARATOR_SCAN_DELIVERY_CHECKLIST.md` | P0 current state → `acquired: 2`, `pilot_ready: true` |

---

## 3. Pilot packet distributability

| Gate | Status |
|---|---|
| P0 comparators validated | **PASS** |
| ≥3 judges confirmed | **FAIL** (0/3) |
| Pre-screen archived | **PENDING** (in flight; no JSON yet) |
| Judge packet assembly | **BLOCKED** until judges + pre-screen |

---

## 4. Handoff — next lanes

| Lane | Action |
|---|---|
| **slot_01 pre-screen watcher** | Await `pre_screen/slot_01_prescreen_results.json`; see `pre_screen/PRESCREEN_RUNBOOK.md` |
| **Judge outreach** | Send `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` Variant A to prospects in `JUDGE_PROSPECT_LIST_SLOT_01.md` |

```bash
# Verify comparators (should pass on closeout branch)
PYTHONPATH=. python3 scripts/qa/validate_manga_blind10_comparators.py --require-p0
```

---

## 5. Machine summary

```
manga-m6-closeout-commit=29c8edce1d
manga-m6-comparators=pass
manga-m6-prescreen=pending
manga-m6-judges=0
manga-m6-next-action=await slot_01 prescreen archive and send judge outreach
manga-m6-blocker=M6-BLK-002 judges not recruited
```
