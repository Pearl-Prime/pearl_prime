# M6 Blind-10 — Judge Recruitment Brief

**Run ID:** `manga_blind10_2026-07-08`  
**Layer:** SPECCED — recruitment **not started** (no judges contracted yet)  
**Authority:** `PROTOCOL.md` §5 · `BLOCKERS.md` M6-BLK-002

---

## Requirement (hard)

| Parameter | Rule |
|---|---|
| Minimum judges | **≥ 3 per locale lane** |
| Locale lanes in this run | **en_US only** (all 10 `CANDIDATE_SET.tsv` rows are `en_US`) |
| Scoring rule | Per-axis **median** across judges; min 3 scores per axis |
| Delegation | **Operator-tier only** — agents cannot substitute for human pros |

**Target headcount:** recruit **3–5** en_US manga professionals (3 is floor; 5 gives redundancy if one drops).

---

## Who to recruit (profile)

Seek **working professionals** with serialized manga or vertical-webtoon experience — not hobbyists, not AI-art reviewers.

### Primary profiles (ranked)

1. **Serialized manga editor or associate editor** — has line-edited or acquired weekly/monthly chapters; can score panel flow, page-turn rhythm, dialogue register.
2. **Lettering / localization lead** — professional experience on EN-market manga or webtoon localization; can score A4 lettering and A8 dialogue register.
3. **Published manga artist or assistant** — credited on a serialized or collected volume; can score A3 consistency, A6 anatomy, A7 tone.
4. **Webtoon vertical-scroll editor** (EN market) — Line Webtoon, Tapas, or publisher vertical imprint; can score scroll rhythm and genre fluency.

### Disqualifiers

- No professional serialized or collected manga / webtoon credits
- Active conflict of interest with Phoenix Omega operator (employee, paid contractor on Phoenix manga renders)
- Cannot commit to blind review (will research candidate origin mid-session)

---

## Compensation and logistics

| Item | Operator decision |
|---|---|
| Rate | Set per judge; typical blind craft review: $150–400 USD per judge for 10 slots (or pilot rate for slot_01 only) |
| NDA | Required — candidate is unreleased Phoenix work presented blind |
| Delivery | Password-protected PDF or secure folder per slot; one session or batched |
| Timeline | Pilot slot_01 can run **before** full blind-10 if pre-screen passes; full run needs ≥ 8 render-ready slots |

Record each recruited judge in `SOURCING_TRACKER.yaml` → `judges.recruited[]` with `id`, `credentials`, `contract_date`, `status`.

---

## Recruitment sequence (operator)

```
1. Identify 8–10 prospects (2× cushion over floor of 3)
2. Send JUDGE_OUTREACH_TEMPLATE.md variant A (pilot) or B (full run)
3. On yes → NDA + schedule → add to SOURCING_TRACKER.yaml
4. When ≥ 3 confirmed → flip M6-BLK-002 to SOFT (scheduled) in BLOCKERS.md
5. Distribute packets only after comparators acquired for that slot
```

---

## Pilot vs full run

| Mode | Slots | When |
|---|---|---|
| **Pilot** | slot_01 only (stillness ep_001) | After Qwen2.5-VL pre-screen PASS; comparators comp_01_a/b acquired |
| **Full blind-10** | slots 01–10 | After M5 delivers ≥ 8 render-ready episodes (M6-BLK-001 cleared) |

Do **not** claim judges recruited until `SOURCING_TRACKER.yaml` shows ≥ 3 with `status: confirmed`.
