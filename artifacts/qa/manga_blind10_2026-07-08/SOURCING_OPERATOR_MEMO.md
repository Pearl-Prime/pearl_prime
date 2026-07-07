# M6 Sourcing — Operator Memo (judges + comparators)

**Date:** 2026-07-08 · **Run ID:** `manga_blind10_2026-07-08`  
**Layer:** SPECCED — sourcing lane **ready**; nothing PROVEN-AT-BAR yet

---

## Executive summary

M6 protocol is landed (PR #4725, `9f70a3d6ec`). Judge recruitment and comparator sourcing were **blocked on missing operator materials** — this memo closes that gap. Judges are **not recruited**. Comparators are **not acquired**. Outreach and acquisition can start **in parallel** with M5 renders.

---

## Judges — who, how many, what to do

| Item | Value |
|---|---|
| **Status** | `ready-to-recruit` (materials ready; zero confirmed) |
| **Minimum** | 3 en_US manga professionals |
| **Ideal** | 5 (redundancy) |
| **Profiles** | Serialized editor, lettering lead, credited artist, or webtoon editor |
| **Brief** | `JUDGE_RECRUITMENT_BRIEF.md` |
| **Outreach** | `JUDGE_OUTREACH_TEMPLATE.md` — use **Variant A** for pilot |
| **Tracker** | `SOURCING_TRACKER.yaml` → `judges.recruited[]` |

### Exact next actions (judges)

1. List 8–10 prospects (LinkedIn, former colleagues, EN localization contacts).
2. Send Variant A email — pilot is **1 episode** (~45 min), not full blind-10 yet.
3. On yes: NDA → assign `judge_XX` ID → log in `SOURCING_TRACKER.yaml`.
4. **Do not distribute packets** until slot_01 comparators are on disk.
5. When ≥ 3 confirmed: note in `BLOCKERS.md` M6-BLK-002 as "scheduled" (still not PROVEN-AT-BAR).

---

## Comparators — titles needed, where files go

| Item | Value |
|---|---|
| **Status** | `ready-to-source` (registry complete; zero acquired) |
| **Total** | 20 excerpts (2 per slot × 10 slots) |
| **Pilot P0** | Slot 01: **Yotsuba&!** Vol 1 Ch1 pp 5–8 + **Barakamon** Vol 1 Ch1 pp 6–10 |
| **Checklist** | `COMPARATOR_ACQUISITION_CHECKLIST.md` (all slots + purchase shortcuts) |
| **Registry** | `COMPARATOR_REGISTRY.yaml` (machine assignments) |
| **Asset path** | `artifacts/qa/manga_blind10_2026-07-08/comparators/*.pdf` (gitignored) |
| **Tracker** | `SOURCING_TRACKER.yaml` → flip `asset_status` + `sha256` |

### Exact next actions (comparators)

1. Buy Yen Press **Yotsuba&!** Vol 1 and **Barakamon** Vol 1.
2. Scan/export 5–8 page PDFs → `comparators/yotsuba_v1_ch1_pages_5-8.pdf` and `comparators/barakamon_v1_ch1_pages_6-10.pdf`.
3. Run `sha256sum` on each; update `COMPARATOR_REGISTRY.yaml` slot `01` entries.
4. Set `SOURCING_TRACKER.yaml` → `comparators.acquired: 2`, pilot comparators `ACQUIRED`.
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

Slot_01 remains `prescreen_only` in `CANDIDATE_SET.tsv` — pilot human review is **discouraged** until M5 bank re-render at 0 INTERIM, but pre-screen + comparator/judge prep can proceed now.

---

## Active blockers (unchanged)

| ID | Blocks | Sourcing lane impact |
|---|---|---|
| M6-BLK-001 | Full blind-10 | Slots 02–10 not render-ready |
| M6-BLK-002 | PROVEN-AT-BAR | Judges not recruited — **outreach ready** |
| M6-BLK-003 | M5 scale + pre-screen | Pearl Star GPU queue |
| M6-BLK-004 | Judge packet distribution | Comparators not on disk — **checklist ready** |

---

## File map

| Artifact | Path |
|---|---|
| Judge brief | `artifacts/qa/manga_blind10_2026-07-08/JUDGE_RECRUITMENT_BRIEF.md` |
| Outreach templates | `artifacts/qa/manga_blind10_2026-07-08/JUDGE_OUTREACH_TEMPLATE.md` |
| Comparator checklist | `artifacts/qa/manga_blind10_2026-07-08/COMPARATOR_ACQUISITION_CHECKLIST.md` |
| Sourcing tracker | `artifacts/qa/manga_blind10_2026-07-08/SOURCING_TRACKER.yaml` |
| Comparator registry | `artifacts/qa/manga_blind10_2026-07-08/COMPARATOR_REGISTRY.yaml` |
| This memo | `artifacts/qa/manga_blind10_2026-07-08/SOURCING_OPERATOR_MEMO.md` |
| Comparator PDFs (local) | `artifacts/qa/manga_blind10_2026-07-08/comparators/` |
