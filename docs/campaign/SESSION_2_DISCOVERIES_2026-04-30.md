# Session 2 Discoveries — Phoenix Omega 100% Production Campaign

**Date:** 2026-04-30
**Session:** 2 (operator authorized after Session 1 prerequisites merged)

This file captures findings that emerged during Session 2 work and need
operator decisions before Session 3.

---

## D-1.2 EPUB packager — state correction

The pathway doc ([docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md](PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md))
calls D-1.2 `scripts/publish/build_epub.py` and lists it as **MISSING**. In
fact:

- `scripts/release/build_epub.py` **already exists** (458 lines, ebooklib-based,
  produces working EPUBs)
- `artifacts/epub/*.epub` already contains 13 shipped EPUBs from previous runs

Path discrepancy: the audit/pathway doc names `scripts/publish/build_epub.py`,
but the live builder is at `scripts/release/build_epub.py`.

### What was actually missing

**EPUB validation.** No KDP-readiness check existed before this PR — meaning
the 13 shipped EPUBs were never validated against KDP submission requirements.

### What this PR ships

`scripts/publish/validate_epub.py` (new, ~340 LoC) + `tests/test_publish_validate_epub.py`
(8 tests). Validates:

- STRUCTURE — NAV, NCX, spine references resolve
- METADATA — title / language (BCP47) / uid / author present
- COVER — image present, dimensions ≥ 1000×1600 (KDP minimum), warn below 1600×2560 (KDP ideal)
- CHAPTERS — at least one real chapter, cover wrapper excluded
- SIZE — under KDP's 650MB cap
- WORDCOUNT — informational, warns below 5000
- EPUBCHECK — optional, runs the official W3C/IDPF validator if `EPUBCHECK_JAR` env var is set

### Real signal from running the validator on existing artifacts

```
$ python3 scripts/publish/validate_epub.py --batch artifacts/epub/
[exit 1, 13 ERRORs]
13/13 EPUBs flagged: cover_below_kdp_min — all use 1024×1024 covers (square),
                     KDP requires ≥1000×1600 (portrait, 1.6:1 ratio).
3/13 also flagged: word_count_low — under 5000 words (master_feung, master_sha, sai_ma).
```

**This is a load-bearing finding:** all 13 shipped EPUBs would be rejected on
KDP submission. They need cover regeneration at portrait dimensions before
D-1.4 (first KDP submission test) can succeed.

### Operator decisions for Session 3

1. **Cover regeneration:** queue a job to regen all 13 covers at 1600×2560 (FLUX, single batch). Estimate: ~$0.40, blocked on RunComfy deployment re-sync per Session 1 finding.
2. **Path consolidation:** decide whether to (a) move `scripts/release/build_epub.py` → `scripts/publish/build_epub.py` to match pathway doc, or (b) update pathway doc to reflect actual path. Either is fine; pick one.
3. **Word-count threshold:** is the 5000-word warn threshold right? master_sha_grief at 4944 words is borderline; KDP allows shorter books but lower-priced.

---

## D-2.1 pipeline-mode default flip — DEFERRED to operator decision

The pathway doc ([docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md](PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md))
deliverable D-2.1 says:

> Flip `scripts/run_pipeline.py` default to `--pipeline-mode spine` (currently `registry`)

But **a prior data report disagrees**:

[`artifacts/pilot/DEFINITIVE_PIPELINE_COMPARISON.md`](../../artifacts/pilot/DEFINITIVE_PIPELINE_COMPARISON.md):107
> Ship spine as an **explicit opt-in** (`--pipeline-mode spine`) for experiments
> and parity measurement **until composition and length targets are met**.
> Rationale: chapter flow fails everywhere in spine mode with the current
> composer, and no topic hit the 9000–11000 word band.

These two authoritative docs **point in opposite directions**. The pathway doc
is newer (2026-04-29) but the pilot report has actual measurement data behind
its conclusion.

### What needs to happen before D-2.1 can land

Either:

- **(a)** Verify the composition + length issues from the pilot report have been
  fixed since 2026-04-22-ish (the timestamp implied by the report). If yes,
  the pilot doc's caveat is stale and D-2.1 can flip the default.
- **(b)** Land the composition + length fixes first, then flip.

Until one of those happens, **flipping the default would break book renders**
that omit `--pipeline-mode`. This PR does NOT change the default — it surfaces
the conflict for operator decision.

### Operator decision for Session 3

Choose A or B:

- **A:** I confirm composition + length issues are fixed; flip the default.
- **B:** Composition + length are still broken; defer D-2.1 until they're fixed (which Phase 2 — D-2.x — addresses anyway).

If A, Session 3 starts with the 1-line flip + a CI check verifying spine-mode
chapter flow + word count gates.

---

## P0.1 / P0.2 — still in other worktrees

Per Session 1 findings, P0.1 (stillness_press multi-genre migration) and P0.2
(native locale templates) were uncommitted in worktrees other than this one.
Confirmed via `git ls-tree origin/main` 2026-04-30: those files are still NOT
on main. Status: **owner-of-other-worktree must commit + open PR**, or operator
re-assigns the work.

This blocks P0.5 (Pearl Prime catalog regen) per Session 1 dependency mapping.

---

## What did NOT happen in Session 2

- **No image renders** (RunComfy deployment still not re-synced; would burn
  budget on a no-op per Session 1 finding)
- **No KDP submission scaffold** (D-1.3) — operator's stated priority list put
  EPUB packager + validator first; D-1.3 is the natural Session 3 marquee
- **No P0.5 work** — blocked on P0.2

---

## Session 2 closeout summary

| Item | Result |
|------|--------|
| D-1.2 EPUB packager | Validator scaffold landed (PR pending), found 13/13 shipped EPUBs fail KDP cover gate |
| D-2.1 pipeline-mode flip | Deferred — pathway-vs-pilot doc conflict surfaced |
| P0.5 catalog regen | Blocked — P0.2 native locale templates still off main |
| Path discrepancy | Documented above; operator picks consolidation direction |

**Session 3 starts when:** operator decides on D-2.1 (A or B above), KDP cover regen is queued, and either P0.2 lands or operator waives P0.5.
