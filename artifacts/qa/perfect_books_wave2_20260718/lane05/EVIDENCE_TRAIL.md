# Lane 05 (Pearl_PM) — Evidence Trail for the Blind-10 Packet

**Date:** 2026-07-18 (run 2026-07-19 local)
**Agent:** Pearl_PM lane 05
**Acceptance-layer honesty:** this document is packet-assembly evidence, not a
book read. No book content was scored/ranked/opined-on by this lane.

## Gate check (verified before starting)

`perfect-books-wave2-lineedit=4356fb0dea205510e7c82a5afad0a629c9117d25` present
in `artifacts/coordination/handoffs/perfect_books_wave2_lineedit_2026-07-18.md`
— PASS. Also confirmed via `git ls-remote pearlstar_offline` that
`offline/perfect-books-wave2-lineedit-20260718` is at that exact SHA.

## Why the Wave-2 designated cells are excluded from the packet

Lane 03's handoff (`artifacts/coordination/handoffs/perfect_books_wave2_lineedit_2026-07-18.md`)
reports `SYSTEM_WORKING=0/3` — all 3 `ONTGP_VERDICT.md` are real, evidenced
FAILs:

| Cell | Verdict |
|---|---|
| corporate_managers × burnout × overwhelm | FAIL |
| tech_finance_burnout × burnout × overwhelm | FAIL (weakest) |
| healthcare_rns × burnout × overwhelm | FAIL (closest to PASS) |

Per the dispatcher's explicit instruction ("Prefer recent real production
ships over FAIL-verdict cells" / "Do NOT pad with draft/ineligible books to
hit N"), these 3 manuscripts are **not** included in the blind-10 packet.
They remain available as a labeled "authored candidate / structurally clear
sample" set if a future lane wants them for a different purpose, but not
folded into this Layer-4 read.

## Why `artifacts/pearl_prime/pilot_10/` is also excluded

Found and inspected this pre-existing 10-book pilot batch
(`artifacts/pearl_prime/pilot_10/`, dated 2026-06-14,
`PILOT_10_REVIEW_PACKAGE.md` + `pilot_10_scorecard.csv`). Excluded for two
independent reasons:

1. **Register gate HARD_FAIL on 9/9 rendered books** (`pilot_10_scorecard.csv`:
   every row `register_gate_verdict=HARD_FAIL`). Register gate is a Layer-1
   hard gate — these books do not clear even `structurally clear`, let alone
   anything higher. They predate the Wave-1 register-gate hardening
   (`docs/PROGRAM_STATE.md` "F1/F4 + F2/F7 precision" — PR #1919 — landed
   *after* this pilot).
2. **Already spoiled for blind reading.** `PILOT_10_REVIEW_PACKAGE.md` §"Per-book
   detail" contains a full editorial read of every book — direct quotes,
   named characters, plot beats, hook lines — published in the repo. Anyone
   (operator or agent) who has seen this doc is no longer blind to these 10
   books per the operator guide's explicit rule ("Don't reread a book after
   seeing its gate report... you're not blind anymore").

Also excluded: the flagship `gen_z_professionals × anxiety` book
(`docs/PROGRAM_STATE.md` "PROVEN-AT-BAR", `OPD-20260707-FLAGSHIP-L4`) — this
book already has its own dedicated operator Layer-4 approval on record, its
goldens are explicitly frozen ("do not edit" per
`docs/agent_prompt_packs/20260718_pearl_prime_perfect_books_wave2/INDEX.md`),
and the operator has already read it (not blind for a fresh read).

## What's IN the packet: 10 real production-ship EPUBs (brand `way_stream_sanctuary`)

All 10 are tracked in git history (verified `git merge-base --is-ancestor` —
both landing commits are ancestors of the current `HEAD`), `--quality-profile
production` chord, brand-consistent (`way_stream_sanctuary`) per the
protocol's "one brand only" rule.

### Books 1–4: individually re-verified this lane (strongest evidence tier)

Landed by PR #1923 (`4e6320b19c`, "fix(waystream): first gate-passing EPUB —
corporate_managers×burnout + 3-cell generalization"). For each, this lane
directly opened and parsed the per-book `register_gate_report.json`-equivalent
at `artifacts/qa/waystream_epub_20260625/<topic>__<engine>__register.json`:

```
anxiety__false_alarm__register.json    -> verdict=PASS persona=corporate_managers topic=anxiety   words=14786 profile=production
boundaries__comparison__register.json  -> verdict=PASS persona=corporate_managers topic=boundaries words=14054 profile=production
boundaries__shame__register.json       -> verdict=PASS persona=corporate_managers topic=boundaries words=14872 profile=production
burnout__overwhelm__register.json      -> verdict=PASS persona=corporate_managers topic=burnout    words=13759 profile=production
```

Cross-checked `burnout__overwhelm` word count (13,759) and file size class
against `docs/PROGRAM_STATE.md`'s own claim ("13,759 words, 1.7 MB") — exact
match, confirming this is genuinely the documented #1923 ship, not a
coincidentally-named artifact.

### Books 5–10: batch-attested + independently structure-checked this lane

Landed by PR #4486 (`321379f8f8`, "feat(release): Waystream EPUB wave — land
57 register-PASS EPUBs"). Confirmed via `git log -1 -- <path>` (single-file,
cheap lookup — the full-commit diff for #4486 was computationally
prohibitive in this sandbox, see Method Note below) that each of these 6
files was introduced by that exact commit:

```
way_stream_sanctuary__entrepreneurs__anxiety__overwhelm.epub                 -> 321379f8f8
way_stream_sanctuary__first_responders__burnout__grief.epub                  -> 321379f8f8
way_stream_sanctuary__gen_x_sandwich__compassion_fatigue__watcher.epub       -> 321379f8f8
way_stream_sanctuary__healthcare_rns__compassion_fatigue__watcher.epub       -> 321379f8f8
way_stream_sanctuary__millennial_women_professionals__burnout__overwhelm.epub -> 321379f8f8
way_stream_sanctuary__tech_finance_burnout__courage__false_alarm.epub        -> 321379f8f8
```

No standalone per-book `register_gate_report.json` exists on disk for these 6
(only the commit-level claim "57 register-PASS EPUBs" in the commit message).
To avoid resting solely on a commit message, this lane additionally unzipped
each EPUB directly (`python3 zipfile` + tag-stripped word count) and confirmed
all 6 are genuine, complete, 12-chapter books in the same ~13.7k–15.1k word
band as the 4 individually-verified ones — i.e. structurally consistent with
"real production ship," not a stub/corrupt/placeholder artifact:

```
entrepreneurs__anxiety__overwhelm            -> 12 chapters, ~13756 words
first_responders__burnout__grief             -> 12 chapters, ~14209 words
gen_x_sandwich__compassion_fatigue__watcher   -> 12 chapters, ~14955 words
healthcare_rns__compassion_fatigue__watcher   -> 12 chapters, ~14736 words
millennial_women_professionals__burnout__overwhelm -> 12 chapters, ~14304 words
tech_finance_burnout__courage__false_alarm    -> 12 chapters, ~15099 words
```

**Honest gap:** this lane did not re-run the register gate itself against
these 6 (out of scope / would require the full pipeline environment); the
PASS claim for books 5–10 rests on the landing commit's own message plus this
lane's independent structural check, not a freshly-executed gate run. Labeled
as "batch-attested" in `MANIFEST.tsv`, distinct from books 1–4's
individually-inspected JSON evidence.

## Method note: git perf in this sandbox

`git show --stat` / `git show --name-only` on the two large historical merge
commits (`321379f8f8`, `4e6320b19c`) hung for minutes in this sandboxed
checkout (likely repo-size + sandbox FS overhead) and in one case had to be
killed. Single-file `git log -1 -- <path>` lookups were reliable and fast
(~2–6s each) and are what this lane relied on for per-file provenance instead
of full commit diffs.

## Disk precheck

`df -g .` at start of this lane: **21 GB available** on the data volume — above
the 20GB "else BLOCKED" floor in the INDEX.md offline-landing recipe, but
close to it. No large files were created by this lane (packet is text/markdown
+ one shell script; no EPUB copies were committed — `make_blind_copies.sh`
writes to `/tmp`, outside the repo).
