# M6 — Judge Outreach Send Checklist (slot_01 pilot)

**Run ID:** `manga_blind10_2026-07-08`  
**Status:** `drafted` — **not sent** (0 prospects contacted)  
**Variant:** A (single iyashikei episode)  
**Calendar window:** 2026-07-15 – 2026-07-29 (confirm before send)

---

## Headcount targets

| Metric | Floor | Ideal |
|---|---|---|
| Prospects contacted | 8 | 10 |
| Confirmed judges | **3** | 5 |
| Scorecards required (pilot) | 3 | 5 |

---

## Pre-send (operator)

- [ ] Read `JUDGE_RECRUITMENT_BRIEF.md` — profile criteria + disqualifiers
- [ ] Open `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` — Variant A copy
- [ ] Set compensation in draft: **$75–125 USD** (adjust if needed)
- [ ] Set timeline window in draft: **2026-07-15 – 2026-07-29**
- [ ] Prepare NDA template (local — not in git)
- [ ] Build prospect list (8–10 names) — **local spreadsheet, not git**

### Prospect criteria (must meet ≥1)

1. Serialized manga editor / associate editor (Viz, Yen Press, Kodansha USA, Seven Seas)
2. Lettering / localization lead (EN manga or webtoon)
3. Credited manga artist or assistant (published volume credits)
4. EN vertical-scroll / webtoon editor (Line Webtoon, Tapas, Webtoon Unscrolled)

### Disqualifiers — do not contact

- No professional serialized or collected manga / webtoon credits
- Active Phoenix Omega contractor on manga renders
- Hobbyist / fan translator without publisher credits

---

## Send loop (per prospect)

- [ ] Replace `[Name]` and `[Operator name]` in Variant A body
- [ ] Send from operator email (not automated)
- [ ] Log in local send table (see `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` § Internal send log)
- [ ] Increment `SOURCING_TRACKER.yaml` → `judges.outreach.prospects_contacted` (after send)

---

## Post-response (per yes)

- [ ] Send NDA (follow-up template in drafts)
- [ ] On NDA returned: assign `judge_XX` ID
- [ ] Append to `SOURCING_TRACKER.yaml` → `judges.recruited[]`:
  ```yaml
  - id: judge_01
    credentials: "<one-line summary>"
    contract_date: "2026-07-XX"
    status: confirmed  # confirmed | scheduled | declined
  ```
- [ ] **Do not send judge packet** until P0 comparators pass validation

---

## Packet distribution gate (all must be true)

- [ ] `python3 scripts/qa/validate_manga_blind10_comparators.py --require-p0` → exit 0
- [ ] ≥3 judges `status: confirmed` in tracker
- [ ] Pre-screen JSON archived; median ≥75 (`pre_screen/PRESCREEN_RUNBOOK.md`)
- [ ] Assemble per `judge_packets/slot_01_stillness_ep001/PACKET.md`

---

## Tracker updates (after send batch)

Edit `SOURCING_TRACKER.yaml`:

```yaml
judges:
  status: recruiting  # was ready_to_recruit
  outreach:
    status: sent  # was drafted — ONLY after operator sends email
  locale_lanes:
    en_US:
      prospects_contacted: <N>  # actual count sent
```

**Do not** set `status: sent` or increment `prospects_contacted` until emails are actually sent.

---

## Full blind-10 note

Pilot judges may be reused for the full run if available. Full run needs separate calendar window (**2026-09-01 – 09-15** tentative) and ≥8 render-ready slots — see `BLIND10_SCHEDULING_MEMO.md`.
