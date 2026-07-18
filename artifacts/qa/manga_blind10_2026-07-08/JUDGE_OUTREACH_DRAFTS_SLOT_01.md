# M6 — Judge Outreach Drafts (slot_01 pilot)

**Status:** `drafted` — **not sent**  
**Variant:** A (pilot, 1 episode)  
**Run ID:** `manga_blind10_2026-07-08`  
**Operator action:** Replace `[brackets]`, add prospect names, send from operator email.

---

## Variant A — filled pilot copy (send-ready after personalization)

**Subject:** Paid blind manga craft review — 1 iyashikei episode (~35 panels)

```
Hi [Name],

I'm running a paid blind craft review for an unreleased vertical manga episode
(iyashikei / wellness-adjacent register, en_US market). I'm looking for a
working manga or webtoon professional to score one full episode against two
published comparators on an 8-axis rubric (panel flow, lettering, genre fluency,
etc.).

What you'd receive:
- One candidate episode (35 panels, vertical read order)
- Two genre-matched published excerpts for calibration:
  • Yotsuba&! Vol 1, Chapter 1, pages 5–8
  • Barakamon Vol 1, Chapter 1, pages 6–10
- Rubric + blank scorecard (scores 1–5 per axis; ~30–45 min)

Requirements:
- Professional serialized manga or EN webtoon editorial, lettering, or art credits
- Blind review — no researching the candidate's origin during scoring
- NDA on unreleased work

Compensation: $75–125 USD for the pilot session (single episode).
Timeline: between July 15 and July 29, 2026 — flexible on exact date.

If interested, reply with a one-line credential summary and I'll send the NDA
and packet.

Thanks,
[Operator name]
```

---

## Follow-up — filled (after prospect says yes)

**Subject:** NDA + blind review packet — slot_01 pilot

```
Hi [Name],

Attached: NDA (please sign and return), blind review instructions, rubric, and
blank scorecard.

The candidate episode and comparator excerpts (Yotsuba&! + Barakamon chapters)
will be in a password-protected folder once NDA is returned.

Presentation order is randomized — score only the slot marked "Candidate" on the
cover sheet. Return completed scorecard to [operator email] by [date + 7 days].

Questions on rubric anchors only — not on candidate origin.

Thanks,
[Operator name]
```

---

## Internal send log (operator — do not email)

| Prospect # | Name | Profile | Date drafted | Date sent | Response |
|---|---|---|---|---|---|
| 1 | | | 2026-07-08 | | |
| 2 | | | 2026-07-08 | | |
| 3 | | | 2026-07-08 | | |
| 4 | | | 2026-07-08 | | |
| 5 | | | 2026-07-08 | | |
| 6 | | | 2026-07-08 | | |
| 7 | | | 2026-07-08 | | |
| 8 | | | 2026-07-08 | | |

After each send: increment `SOURCING_TRACKER.yaml` → `judges.locale_lanes.en_US.prospects_contacted`.  
After NDA + confirm: append to `judges.recruited[]` with `status: confirmed`.
