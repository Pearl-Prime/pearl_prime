# Content-History Forensics — was a deeper story bank / 300 exercises / 700 books deleted?

> ## ⚠️ CORRECTION (2026-07-03, later same day) — the "depth = 3 cells" line is WRONG (the rest stands)
>
> The history verdicts below are correct: nothing was deleted-and-not-restored; current main is the all-time peak; "700+ Waystream" = listings not books; #245 was fully restored. **BUT one line repeated the flawed proxy from the deep-content doc:** *"named-character DEPTH: character_roster.yaml = 3 → depth is aspirational."*
>
> **Corrected:** story **DEPTH** is authored across **216/218 STORY pools (99%)** with **unnamed** protagonists (content-measured, 2,792 deep variants) — it renders to output post-#4591. Only **NAMING** is scarce (22 named / 196 unnamed pools). Depth was measured by name-grep, which was the error. Depth is NOT aspirational — it is authored catalog-wide as shared per-topic story spines (persona noun-swapped). See memory `project_story_depth_mismeasured` and the CORRECTION banner in `DEEP_CONTENT_OUTPUT_VERIFICATION_2026-07-03.md`.

---

**Author:** Pearl_Architect (git-history forensics, deterministic; no LLM)
**Date:** 2026-07-03
**Method:** dig the FULL history including deleted files (`--diff-filter=D`), count content at anchor SHAs, reconcile the #245 mass-deletion. Current origin/main treated as the FLOOR to disprove — not assumed to be the peak.

---

## TL;DR — nothing bestseller was lost; current `main` IS the all-time peak on every content axis

The known #245 mass-deletion (20,006 files) was **real** but **fully restored** (#250 + #252 + a later #8ca997492a), and the banks then **grew ~3×**. Across ALL history, current origin/main holds the **maximum** count of atoms, story atoms, exercise files, rendered `book.txt`, and EPUBs ever committed. There is **no richer historical state to `git checkout`.**

| element | peak count | peak SHA | current main | verdict |
|---|---|---|---|---|
| atoms (total) | **18,380** | origin/main (now) | 18,380 | **AT PEAK** — not lost |
| STORY atoms | **1,642** | origin/main (now) | 1,642 | **AT PEAK** — not lost |
| named-character rosters (depth) | **3** | origin/main (= pre-injector) | 3 | **ASPIRATIONAL** — never >3 in any commit |
| exercise files | **1,262** | origin/main (now) | 1,262 | **AT PEAK** — not lost (>300) |
| rendered `book.txt` | **191** | origin/main (now) | 191 | **AT PEAK** — never 700+ |
| EPUB | **138** | origin/main (now) | 138 | **AT PEAK** — not lost |
| Waystream RENDERED books | **27** | origin/main (now) | 27 | **LISTINGS-not-books** (5,519 listings) |

**Counts at anchor SHAs (`git ls-tree -r`):**

| SHA | atoms | STORY | exercise | book.txt | epub |
|---|---|---|---|---|---|
| origin/main (now) | 18,380 | 1,642 | 1,262 | 191 | 138 |
| pre-injector (`365fd19cc3^`) | 17,784 | 1,586 | 1,250 | 176 | 110 |
| pre-#245 (`8be0ab75dc`) | 6,435 | 989 | 639 | 31 | 0 |
| post-#245 delete (`bba889f140`) | 1,234 | 378 | 0 | 20 | 0 |
| post-restore #252 (`022f890c46`) | 6,435 | 989 | 639 | 31 | 0 |

Monotonic growth 6,435 → 18,380 atoms after restoration. Current main is the ceiling, not a diluted floor.

---

## The #245 reconciliation (the known lead — chased, closed)

- **Deletion:** `bba889f140` "Tighten Brand Admin Media Generation Contract (**#245**)" — an innocuous title that **deleted 20,006 files**, collapsing the tree to a skeleton (atoms 6,435→1,234; exercises 639→**0**; story 989→378).
- **Restores:** `36b952b91e` (#250, 36 workflows) + `022f890c46` (#252, **restore 19,948 files**) + `8ca997492a` (2026-06-09, **recover 187 more** files #245 missed).
- **Completeness for BESTSELLER content:** post-#252 counts **equal** pre-#245 exactly — atoms 6,435 = 6,435, STORY 989 = 989, exercise 639 = 639. **The story/exercise/atom restoration was complete.**
- **The 7,359 #245-deleted files still absent from main are NOT bestseller content:** 136 are `SOURCE_OF_TRUTH/teacher_banks/*` intermediate **`_mined.yaml` candidate** atoms (109 ahjan) — superseded by **approved** atoms (the ahjan bank has **556** files / **109** approved QUOTE+TEACHING on main today, i.e. the approved versions exist); the rest are `.claude/worktrees/` backup snapshots, status `.txt` reports, and files removed by later legitimate refactors. Note: "absent from main" over-counts the #245 loss because it also captures anything removed by any later commit — even so, zero of it is story/exercise/atom bank content (those dirs show 0–2 never-restored).

**Verdict on #245:** a genuine scare (20k files gone for real), fully reversed. It is the likely source of the operator's "we had it and it vanished" memory — but the vanish was temporary and the restore was complete + subsequently surpassed.

---

## Per-element verdicts (SHA-backed)

### 1. DEEP STORY BANK — **NOT lost; at all-time peak. Depth = aspirational, never authored at scale.**
- STORY atoms: peak = **1,642** (current main) > pre-injector 1,586 > post-restore 989. Never higher than now.
- Named-character **individuation** (`character_roster.yaml`): **3** on main, **3** pre-injector, **0** pre-#245, **0** post-restore. The rosters were authored *after* #245; the count **never exceeded 3 in any commit in history**. The rich per-cell depth the operator remembers was **never** authored beyond 3 anxiety cells — this is an authoring gap (confirmed at output level in `DEEP_CONTENT_OUTPUT_VERIFICATION_2026-07-03.md`), **not a deletion**. No SHA to restore from.

### 2. 300+ EXERCISES — **NOT lost; at all-time peak (1,262 > 300).**
- Exercise files: peak = **1,262** (current main) > pre-injector 1,250 > post-restore 639; #245 dropped to **0**, #252 restored to 639, then grew to 1,262. On main: **11 function-typed approved exercises** + `aha_noticing_phoenix_standard.yaml` + `integration_phoenix_standard.yaml` canon (the intro/guide/aha/integration layers). The "300+" is met and exceeded by count; layer completeness is intact. No loss.

### 3. 700+ WAYSTREAM BOOKS — **LISTINGS, not rendered books. Never 700+ rendered in any commit.**
- Peak rendered `book.txt` across ALL history = **191** (current main, all cells) — never 700+. Waystream specifically: **5,519 listing files** (yaml/csv/json catalog metadata) vs **27 rendered** book.txt/EPUB on main. The "700+ Waystream" was **always catalog listings**, never rendered books. This matches memory `[[project_waystream_800_first_and_rerender_doctrine]]` (assemble 800 listings first) and `[[project_storefront_v1_real_state]]` (72-SKU sample, 1 EPUB). SHA-backed: listings ≠ books.

---

## Restore paths

**None required.** No bestseller-content axis is lost-restorable — current main is the peak. The one recurring gap (rich per-cell named-character depth) has **no SHA to restore**; it was never authored at scale. The lever is **authoring** (Pearl_Writer / Claude-writes), per `DEEP_CONTENT_OUTPUT_VERIFICATION_2026-07-03.md`.

Optional low-value cleanup (NOT a restore): the 136 superseded `_mined.yaml` teacher candidates remain only in history — intentional, leave them.

---

## Why the prior audits didn't find "more"

Because **there is no more.** #4572 (wiring), the bestseller verification, and #4590 (quality drift) all read current origin/main — and current main is the **richest state that has ever existed** on every content axis. They weren't missing a deleted peak; they were reading the peak. The felt "it's gone" is two true things braided together: (a) #245 *did* delete ~20k files (real, temporary, fully restored), and (b) the rich per-cell story **depth** was never authored beyond 3 cells in any commit — aspirational, not deleted.

## NEXT_ACTION
No git restore. Route to the **depth-authoring lane** (Pearl_Writer): author cell-matched 3-layer rosters/story atoms flagship-first, then catalog-widen. This is the same lever named in the deep-content output verification — now confirmed by history to be authoring, not recovery.

## Reproduce
```bash
git show --stat bba889f140 | tail -1                       # #245: 20,006 deletions
git ls-tree -r --name-only origin/main | grep -cE '(^|/)atoms/'   # 18,380 (peak)
for s in origin/main 8be0ab75dc 022f890c46 '365fd19cc3^'; do
  echo "$s STORY=$(git ls-tree -r --name-only $s | grep -icE 'STORY.*\.(yaml|txt)$|story_atom')"; done
git ls-tree -r --name-only origin/main | grep -iE 'waystream' | grep -cE 'book\.txt$|\.epub$'  # 27 rendered
```
