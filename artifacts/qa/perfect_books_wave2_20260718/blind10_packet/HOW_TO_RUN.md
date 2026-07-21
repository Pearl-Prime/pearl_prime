# HOW TO RUN — Blind-10 Operator Packet (Wave-2 prep, 2026-07-18)

**Layer-4 pending operator read — no register/bestseller claim exists until the
operator records a verdict.** This packet was assembled by an agent (Pearl_PM
lane 05). No agent has read, scored, ranked, or opined on any of the 10 books.
That is the whole point: an agent reading them would void the blind.

Full governing docs (read these, not just this page, before you start):

- `docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md` — the authoritative step-by-step.
- `docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md` — the 5-axis supplementary rubric.
- `artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md`
  §0 (acceptance contract) + §3.E (B1–B3, the process this packet exists to feed).

## The honest starting condition (read this before you read the books)

- **Zero Layer-3 `system working` cells exist in the catalog right now.** The
  Wave-2 flagship line-edit lane (Lane 03, 2026-07-18) ran a real ONTGP read on
  3 designated cells and got **3/3 FAIL** (one — `healthcare_rns × burnout ×
  overwhelm` — close, Ch12 alone was a clean 5/5). Those 3 FAIL-verdict
  manuscripts are **excluded from this packet** — per the dispatcher's explicit
  instruction, FAIL-verdict cells are not padded in to hit N.
- **This packet is instead built from 10 real, already-shipped production EPUBs**
  (brand `way_stream_sanctuary`, register-gate PASS, `--quality-profile
  production` chord) — the actual output stream the system is producing today.
  Every book's acceptance layer tops out at **Layer 1 (`structurally clear`)**:
  register gate PASS is a Layer-1 hard gate, not a Layer-3 or Layer-4 result.
  Per CLAUDE.md: **gate-PASS ≠ bestseller.** See `MANIFEST.tsv` for the exact
  evidence trail per book (4 of the 10 have a directly-inspected per-book
  `register_gate_report.json`; the other 6 are attested by their landing
  commit's message plus this lane's independent structural re-check — see
  `../lane05/EVIDENCE_TRAIL.md`).
- **BOOKS_IN_PACKET = 10/10** (protocol N met) but with that Layer-1 ceiling —
  this is a `structurally clear`-tier blind-10, not a `system working`-tier
  one. Whatever verdict you record is real Layer-4 evidence either way — the
  blind-10 samples "what the system is actually shipping," which is exactly
  what these 10 books are.

## Step 0 — Make your own anonymized reading copies (do this first)

The EPUB filenames on disk encode persona × topic × engine
(`way_stream_sanctuary__corporate_managers__burnout__overwhelm.epub`), which
breaks the "don't check persona/topic" blind rule the moment you look at a
file browser. Run the provided script to make de-identified local copies
before you start reading:

```bash
cd /Users/ahjan/phoenix_omega
bash artifacts/qa/perfect_books_wave2_20260718/blind10_packet/make_blind_copies.sh
```

This writes `Book_01.epub` … `Book_10.epub` into a **gitignored, local-only**
`/tmp/blind10_reading_copies_20260718/` folder (nothing new is committed — the
script only copies already-tracked files to a scratch path). Read from that
folder. Do **not** open `MANIFEST.tsv` or `KEY_SEALED.md` until Step 4.

## Step 1 — Read order

See `READ_ORDER.md`. Read `Book_01` through `Book_10` in that order (arbitrary
— not a quality ranking, not sorted by recency since on-disk mtimes here are
checkout times, not render times). Per the operator guide: don't re-sort,
don't skip one because you already have a hunch about it.

## Step 2 — Read each book blind

Minimum: Ch1 + Ch5/6 + Ch11/last (~15–20 min/book, ~2.5–4 hrs total for all
10). Don't read `MANIFEST.tsv`, gate reports, or any `NOTES.md` /
`ONTGP_VERDICT.md` anywhere in the repo before finishing all 10 reads.

## Step 3 — Score

Fill in `SCORING_SHEET.md` (blank, one row per `Book_ID`, two yes/no questions
+ 2 free-text per the operator guide §3). Optionally also fill the 5-axis
supplementary table (1–5 scale) from `FIRST_10_BOOKS_EVALUATION_PROTOCOL.md`
if you want the extra granularity — it is not required for the Layer-4 verdict
math, which only uses the two yes/no questions.

## Step 4 — Unseal the key, compute the verdict, commit it

Only now open `KEY_SEALED.md` to map `Book_ID` back to the real persona/topic
for your routing notes (Step 5 of the operator guide — clustering weakest/
strongest dimensions by pattern). Compute:

- `felt_assembled_pass_rate` = (# "yes" on Q1) / 10 — PASS at ≥ 7/10
- `shelf_next_to_trade_pub_pass_rate` = (# "yes" on Q2) / 10 — PASS at ≥ 6/10

Write the verdict as `artifacts/qa/BLIND_10_VERDICT_<YYYY-MM-DD>.md` per the
operator guide's template (Step 6). **Label it honestly**: this run's input
pool is Layer-1 `structurally clear`, so even a full PASS here is evidence
about the production-chord shipping stream, not proof that a `system working`
(Layer-3) flagship cell exists — those are still 0/3 this wave. Route
weakest-dimension clusters per the operator guide's Step 5 table.

## What this lane did NOT do

- Did not read, score, rank, or open any of the 10 EPUBs' content.
- Did not claim `bestseller`, `shippable`, `production-ready`, or any
  Layer-3/4 result.
- Did not pad the packet with the 3 ONTGP-FAIL Wave-2 line-edit manuscripts,
  or with any draft/`--quality-profile draft` output.
- Did not commit any new binary — the 10 EPUBs referenced here were already
  tracked in git before this lane started (PRs #1923 / #4486).
