# M6 Blind-10 — Scheduling Memo (operator-ready)

**Run ID:** `manga_blind10_2026-07-08`  
**Date:** 2026-07-08  
**Verified HEAD:** `2ca947a9fa85a9793f3f097cf10bfdcf5ef31f66` (origin/main)  
**Layer:** SPECCED — scheduling lane **advanced**; **PROVEN-AT-BAR:** none  
**Status:** `partial` — pilot lane schedulable; full blind-10 blocked

---

## Executive summary

| Lane | Can start now? | Evidence |
|---|---|---|
| Slot_01 pre-screen (Qwen2.5-VL) | **Yes** — when Pearl Star Ollama online | `CANDIDATE_SET.tsv` slot 01 `prescreen_only`; legacy `composed_v3_qwen` 35p |
| Slot_01 comparator acquisition | **Yes** — operator action | 0/2 P0 PDFs on disk; validator exits 1 |
| Slot_01 judge outreach | **Yes** — draft only, not sent | `JUDGE_OUTREACH_DRAFTS_SLOT_01.md`; 0 contacted |
| Slot_01 human judge packet | **No** | Needs P0 comparators + ≥3 judges + pre-screen pass |
| Slot_02 M5 assembly (ep_001_from_continuity) | **Partial** | 35p, 0-INTERIM on main; **ep001_029 undersized** (12,741 B) |
| Full blind-10 (10 slots) | **No** | M6-BLK-001: 1/10 prescreen_only, 9 blocked |

---

## What can run now vs blocked

### Runnable today (no new code)

| # | Action | Owner | Prerequisite | Unblocks |
|---|---|---|---|---|
| A1 | Buy Yotsuba&! Vol 1 + Barakamon Vol 1 | Operator | Licensed retail budget | M6-BLK-004 pilot |
| A2 | Scan 2 P0 PDFs → `comparators/` | Operator | A1 | Validator `--require-p0` |
| A3 | Run comparator validator | Operator | A2 | Registry sha256 closeout |
| A4 | Personalize + send judge outreach (8–10 prospects) | Operator | None (parallel with A1) | M6-BLK-002 pilot |
| A5 | Run slot_01 pre-screen on Pearl Star | Operator + Pearl Star | Ollama `qwen2.5vl:7b` online | Pre-screen archive |
| A6 | Order P1 comparator volumes (slots 02–04) | Operator | Budget | P1 ready when M5 lands |

### Blocked — do not schedule

| ID | Blocks | Until |
|---|---|---|
| M6-BLK-001 | Full blind-10 human run | ≥8 render-ready slots in `CANDIDATE_SET.tsv` |
| M6-BLK-002 | PROVEN-AT-BAR claim | ≥3 confirmed judges in `SOURCING_TRACKER.yaml` |
| M6-BLK-003 | M5 scale renders + pre-screen if offline | Pearl Star GPU queue (#3075) online |
| M6-BLK-004 | Judge packet distribution | P0 comparators validated on disk |
| M6-BLK-005 | Slot_02 human packet | Re-render `ep001_029` ≥99,690 B (0-INTERIM path) |

---

## Pilot vs full blind-10 timeline

All dates are **targets** — adjust before outreach send. Nothing is scheduled until operator confirms.

### Phase P — Pilot slot_01 (iyashikei / stillness ep_001)

| Week | Dates | Milestone | Gate |
|---|---|---|---|
| P0 | **2026-07-08 – 07-14** | Comparator acquisition + judge outreach send | 2 P0 PDFs validated; 8–10 emails sent |
| P1 | **2026-07-15 – 07-18** | Judge recruitment + pre-screen | ≥3 judges confirmed + NDA signed; pre-screen JSON archived |
| P2 | **2026-07-19 – 07-22** | Pilot packet assembly | Pre-screen median ≥75; comparators ACQUIRED |
| P3 | **2026-07-23 – 07-29** | Pilot judge sessions | ≥3 scorecards returned |
| P4 | **2026-07-30** | Pilot closeout | Update `VERDICT.md` pilot section — still **not** PROVEN-AT-BAR |

**Pilot candidate render:** slot_01 uses legacy `composed_v3_qwen` (`prescreen_only`).  
**Upgrade path:** when slot_02 (`ep_001_from_continuity`) clears byte gate, prefer M5 bank assembly for any follow-on human review.

### Phase F — Full blind-10 (10 slots)

| Week | Dates | Milestone | Gate |
|---|---|---|---|
| F0 | **2026-07-08 – 07-31** | M5 render recovery (parallel) | Pearl Star online; slots 02–05 E2E |
| F1 | **2026-08-01 – 08-14** | Comparator P1+P2 acquisition | 20/20 PDFs validated |
| F2 | **2026-08-15 – 08-28** | Full judge recruitment | ≥3 en_US pros confirmed |
| F3 | **2026-09-01 – 09-15** | Full blind-10 sessions | ≥8 slots `blind10_eligible=yes` |
| F4 | **2026-09-16** | `VERDICT.md` full run | Median rubric scores filed |

**Full blind-10 earliest realistic start:** **2026-09-01** (assuming M5 delivers ≥8 slots by 2026-08-15).

---

## Judge scheduling — targets and calendar

| Parameter | Pilot (slot_01) | Full blind-10 |
|---|---|---|
| Minimum confirmed | **3** | **3** (same pool; reuse if available) |
| Ideal headcount | **5** | **5** |
| Prospects to contact | **8–10** | **10–15** |
| Compensation (pilot) | **$75–125** / session | — |
| Compensation (full) | — | **$150–400** / judge (operator-set) |
| Calendar window | **2026-07-15 – 07-29** | **2026-09-01 – 09-15** (tentative) |
| NDA | Required before packet | Required |
| Packet distribution | After P0 comparators + ≥3 confirmed | After all slot comparators for scheduled slots |

**Send checklist:** `JUDGE_OUTREACH_SEND_CHECKLIST.md`  
**Draft copy:** `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` (Variant A — **not sent**)

---

## Comparator acquisition — scan delivery

**Pilot P0 (blocks slot_01 packet):**

| ID | Title | Output file | Pages | ISBN |
|---|---|---|---|---|
| comp_01_a | Yotsuba&! | `comparators/yotsuba_v1_ch1_pages_5-8.pdf` | 5–8 | 978-0-7595-0410-5 |
| comp_01_b | Barakamon | `comparators/barakamon_v1_ch1_pages_6-10.pdf` | 6–10 | 978-0-316-36217-6 |

**Operator checklist:** `COMPARATOR_SCAN_DELIVERY_CHECKLIST.md`  
**Execution sheet:** `PILOT_SLOT_01_ACQUISITION_EXECUTION.md`

**Validation (after PDFs land):**

```bash
cd /Users/ahjan/phoenix_omega
python3 scripts/qa/validate_manga_blind10_comparators.py \
  --run-id manga_blind10_2026-07-08 \
  --require-p0
# Expected: exit 0, pilot_ready: true, acquired: 2
python3 scripts/qa/validate_manga_blind10_comparators.py --require-p0 --json
```

---

## Slot_01 prescreen path (stillness ep_001)

**Best current candidate:** slot_01 (`prescreen_only`) — only blind-10-eligible queue entry.

| Check | Slot 01 (legacy v3) | Slot 02 (M5 ep_001_from_continuity) |
|---|---|---|
| Panels | 35 | 35 |
| INTERIM layers | legacy path (not bank) | **0** |
| Byte floor | All ≥99,690 | **34/35 pass** — ep001_029 = 12,741 B |
| blind10_eligible | `prescreen_only` | `no` (byte gate) |
| Pre-screen | **Run now** on `composed_v3_qwen` | Withhold until panel 29 fixed |
| Human packet | Discouraged until M5 upgrade | Preferred path once byte gate clears |

**Pre-screen command:** `pre_screen/PRESCREEN_RUNBOOK.md`  
**Do not use:** `demo_alarm_metaphor_6p` (6p, INTERIM, G1 grammar blocked)

---

## Prerequisites matrix (pilot packet assembly)

All must be true before distributing `judge_packets/slot_01_stillness_ep001/`:

- [ ] `validate_manga_blind10_comparators.py --require-p0` → exit 0
- [ ] `COMPARATOR_REGISTRY.yaml` comp_01_a/b → `ACQUIRED` + sha256
- [ ] `SOURCING_TRACKER.yaml` → `judges.recruited` ≥3 confirmed
- [ ] NDAs signed (local storage, not git)
- [ ] Pre-screen JSON archived; median ≥75; no ≥3 panels below 50
- [ ] Operator acknowledges slot_01 is legacy v3 (`prescreen_only`)

---

## Machine readiness outputs

```
manga-m6-blind10-ready=partial
manga-m6-scheduling-blockers=M6-BLK-001,M6-BLK-002,M6-BLK-003,M6-BLK-004,M6-BLK-005
manga-m6-scheduling-next=Operator: acquire 2 P0 comparator PDFs + send 8–10 judge outreach emails (parallel)
```

---

## File map

| Artifact | Path |
|---|---|
| **This memo** | `artifacts/qa/manga_blind10_2026-07-08/BLIND10_SCHEDULING_MEMO.md` |
| Sourcing tracker | `artifacts/qa/manga_blind10_2026-07-08/SOURCING_TRACKER.yaml` |
| Candidate queue | `artifacts/qa/manga_blind10_2026-07-08/CANDIDATE_SET.tsv` |
| Blockers | `artifacts/qa/manga_blind10_2026-07-08/BLOCKERS.md` |
| Judge send checklist | `artifacts/qa/manga_blind10_2026-07-08/JUDGE_OUTREACH_SEND_CHECKLIST.md` |
| Comparator scan checklist | `artifacts/qa/manga_blind10_2026-07-08/COMPARATOR_SCAN_DELIVERY_CHECKLIST.md` |
| Comparator validator | `scripts/qa/validate_manga_blind10_comparators.py` |
