# M6 Sourcing — Operator Memo (judges + comparators)

**Date:** 2026-07-08 · **Run ID:** `manga_blind10_2026-07-08`  
**Layer:** SPECCED — acquisition + scheduling lanes **advanced**; nothing PROVEN-AT-BAR yet
**Scheduling:** `BLIND10_SCHEDULING_MEMO.md` — pilot Jul 15–29; full blind-10 earliest Sep 2026

---

## Executive summary

M6 protocol is landed (PR #4725, `9f70a3d6ec`). Judge recruitment and comparator sourcing were **blocked on missing operator materials** — this memo closes that gap. Judges are **not recruited**. Comparators are **not acquired**. Outreach and acquisition can start **in parallel** with M5 renders.

---

## Judges — who, how many, what to do

| Item | Value |
|---|---|
| **Status** | `ready-to-recruit` — Variant A **drafted** (not sent); zero confirmed |
| **Minimum** | 3 en_US manga professionals |
| **Ideal** | 5 (redundancy) |
| **Profiles** | Serialized editor, lettering lead, credited artist, or webtoon editor |
| **Brief** | `JUDGE_RECRUITMENT_BRIEF.md` |
| **Outreach** | `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` (filled draft) · template: `JUDGE_OUTREACH_TEMPLATE.md` |
| **Tracker** | `SOURCING_TRACKER.yaml` → `judges.recruited[]` |

### Exact next actions (judges)

1. Execute `JUDGE_OUTREACH_SEND_CHECKLIST.md` — prospect criteria + send order.
2. Personalize `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` for 8–10 prospects; send Variant A.
3. On yes: NDA → assign `judge_XX` ID → log in `SOURCING_TRACKER.yaml`.
4. **Do not distribute packets** until slot_01 comparators are on disk.
5. When ≥ 3 confirmed: note in `BLOCKERS.md` M6-BLK-002 as "scheduled" (still not PROVEN-AT-BAR).

---

## Comparators — titles needed, where files go

| Item | Value |
|---|---|
| **Status** | `ready-to-source` — slot_01 **ready_to_acquire** (2 PDFs); zero on disk |
| **Total** | 20 excerpts (2 per slot × 10 slots) |
| **Pilot P0** | Slot 01: **Yotsuba&!** Vol 1 Ch1 pp 5–8 + **Barakamon** Vol 1 Ch1 pp 6–10 |
| **Checklist** | `COMPARATOR_ACQUISITION_CHECKLIST.md` (all slots + purchase shortcuts) |
| **Registry** | `COMPARATOR_REGISTRY.yaml` (machine assignments) |
| **Asset path** | `artifacts/qa/manga_blind10_2026-07-08/comparators/*.pdf` (gitignored) |
| **Tracker** | `SOURCING_TRACKER.yaml` → flip `asset_status` + `sha256` |

### Exact next actions (comparators)

1. Execute `COMPARATOR_SCAN_DELIVERY_CHECKLIST.md` (ISBNs, URLs, scan spec).
2. Scan PDFs → `comparators/yotsuba_v1_ch1_pages_5-8.pdf` + `comparators/barakamon_v1_ch1_pages_6-10.pdf`.
3. Run `python3 scripts/qa/validate_manga_blind10_comparators.py --require-p0`.
4. Record sha256; flip registry + tracker to `ACQUIRED`.
5. Order P1 titles (slots 02–04) while M5 renders progress.

---

## Pilot dispatch order (slot_01 only)

```
Pearl Star online
  → pre_screen/PRESCREEN_RUNBOOK.md (Qwen2.5-VL)
  → comparators P0 acquired (2 PDFs)
  → ≥ 3 judges confirmed
  → assemble judge_packets/slot_01_stillness_ep001/
  → distribute blind → collect scorecards → scorecards/
```

Slot_01 remains `prescreen_only` in `CANDIDATE_SET.tsv` — pilot human review is **discouraged** until M5 bank re-render at 0 INTERIM (slot_02 `ep_001_from_continuity` when ep001_029 byte gate clears), but pre-screen + comparator/judge prep can proceed now.

---

## Active blockers (unchanged)

| ID | Blocks | Sourcing lane impact |
|---|---|---|
| M6-BLK-001 | Full blind-10 | Slots 02–10 not render-ready |
| M6-BLK-002 | PROVEN-AT-BAR | Judges not recruited — **outreach ready** |
| M6-BLK-003 | M5 scale + pre-screen | Pearl Star GPU queue |
| M6-BLK-004 | Judge packet distribution | Comparators not on disk — **checklist ready** |
| M6-BLK-005 | M5 upgrade path | ep001_029 undersized on ep_001_from_continuity |

---

## File map

| Artifact | Path |
|---|---|
| **Scheduling memo** | `artifacts/qa/manga_blind10_2026-07-08/BLIND10_SCHEDULING_MEMO.md` |
| Judge send checklist | `artifacts/qa/manga_blind10_2026-07-08/JUDGE_OUTREACH_SEND_CHECKLIST.md` |
| Comparator scan checklist | `artifacts/qa/manga_blind10_2026-07-08/COMPARATOR_SCAN_DELIVERY_CHECKLIST.md` |
| Judge brief | `artifacts/qa/manga_blind10_2026-07-08/JUDGE_RECRUITMENT_BRIEF.md` |
| Outreach templates | `artifacts/qa/manga_blind10_2026-07-08/JUDGE_OUTREACH_TEMPLATE.md` |
| Comparator checklist | `artifacts/qa/manga_blind10_2026-07-08/COMPARATOR_ACQUISITION_CHECKLIST.md` |
| Sourcing tracker | `artifacts/qa/manga_blind10_2026-07-08/SOURCING_TRACKER.yaml` |
| Comparator registry | `artifacts/qa/manga_blind10_2026-07-08/COMPARATOR_REGISTRY.yaml` |
| This memo | `artifacts/qa/manga_blind10_2026-07-08/SOURCING_OPERATOR_MEMO.md` |
| **Pilot execution sheet** | `artifacts/qa/manga_blind10_2026-07-08/PILOT_SLOT_01_ACQUISITION_EXECUTION.md` |
| Judge drafts (not sent) | `artifacts/qa/manga_blind10_2026-07-08/JUDGE_OUTREACH_DRAFTS_SLOT_01.md` |
| Comparator validator | `scripts/qa/validate_manga_blind10_comparators.py` |
| Comparator PDFs (local) | `artifacts/qa/manga_blind10_2026-07-08/comparators/` |
