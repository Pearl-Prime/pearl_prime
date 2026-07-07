# M6 Blind-10 — Judge Outreach Templates

**Use:** Copy, personalize, send from operator email. Do not mention Phoenix Omega or repo paths in judge-facing text.

---

## Variant A — Pilot (slot_01 only)

**Subject:** Paid blind manga craft review — 1 iyashikei episode (~35 panels)

**Filled draft (slot_01):** `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` — status **drafted**, not sent.

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

## Variant B — Full blind-10 (10 episodes)

**Subject:** Paid blind manga craft review — 10-episode panel study

```
Hi [Name],

I'm assembling a blind craft panel for an unreleased en_US vertical manga catalog
(10 full episodes across 8 genres). I need ≥ 3 independent manga professionals
to score candidate episodes against published comparators on an 8-axis rubric.

Scope per judge:
- 10 blind sessions (one episode each) OR batched delivery over [N] weeks
- Each session: candidate episode + 2 genre-matched published excerpts + scorecard
- Estimated [X] hours total; compensation [RATE] for the full set

Requirements:
- Serialized manga editor, lettering lead, or credited manga artist (EN or JP
  market experience OK if fluent in EN rubric)
- Blind protocol — no cross-judge discussion until submissions complete
- NDA

Timeline: first packet available [DATE]; full run complete by [DATE].

Reply with credentials and availability if interested.

Thanks,
[Operator name]
```

---

## Follow-up (after yes)

**Subject:** NDA + blind review packet — [slot_id]

```
Hi [Name],

Attached: NDA (please sign and return), blind review instructions, rubric, and
blank scorecard.

The candidate episode and comparator excerpts are in [secure link / password].

Presentation order is randomized — score only the slot marked "Candidate" on the
cover sheet. Return completed scorecard to [email] by [date].

Questions on rubric anchors only — not on candidate origin.

Thanks,
[Operator name]
```

---

## Internal checklist (operator — do not send)

- [ ] Judge ID assigned (`judge_XX`) in `SOURCING_TRACKER.yaml`
- [ ] NDA signed and filed (local secure storage — not git)
- [ ] `presentation_seed` recorded per session in scorecard
- [ ] Scorecard filed to `scorecards/judge_<id>_slot_<NN>.yaml`
