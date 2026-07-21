# Prompt Pack — Pearl Prime Perfect Books, WAVE 2 (offline; content-quality track)

Program goal: advance the Perfect Books spec from Wave-1 (enforcement gates landed)
to the **actual register lever** — bank fill (C1–C4) + flagship line-edit (L1–L4) —
and earn the first true **`system working`** Layer-3 artifacts, then prep the
operator blind-10. All offline while GitHub is blocked. This wave does NOT and
CANNOT reach Layer-4 `bestseller register` — that is the operator's blind read.

## Authority (read before authoring anything)

- **Spec (governing):** `artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md` — §2 ownership split, §3 C/D/G/L/B mechanisms, §5 sequencing, §6 non-goals.
- **Wave-1 closeout:** `artifacts/qa/pearl_prime_100book_analysis_20260718/IMPLEMENTATION_CLOSEOUT.md` (`SIGNAL=pearl-prime-perfect-spec-impl=PARTIAL`) + handoff `artifacts/coordination/handoffs/pearl_prime_perfect_books_wave1_2026-07-18.md`.
- **100-book analysis:** `.../ANALYSIS_REPORT.md` + `MATRIX.tsv` (ship-matrix + register-fail findings — the cell-selection SSOT).
- **Line-edit lane scaffold (EXTEND, do not recreate):** `artifacts/qa/flagship_line_edit/README.md`.
- **Doctrine (binding):** CLAUDE.md "Bestseller Quality Anti-Drift Doctrine" (composer is NOT the flagship lever; gate-PASS ≠ bestseller; claim language gated G-CLAIM/G-LAYER); `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md`; `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`.
- **Blind-10 protocol:** `docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md`; `docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md`.

## Live truth anchor (router-verified 2026-07-18)

- **GitHub: BLOCKED** (`ls-remote origin` → 403 account-suspended). Every writing lane lands OFFLINE per the recipe below; re-probe at run time.
- **PearlStar offline remote REACHABLE** (`pearlstar_offline`); oldchats7 refs already landed there (`offline/oldchats7-final-audit-20260718`).
- **Wave-1 branch `agent/pearl-prime-perfect-books-wave1` = LOCAL-ONLY**, tip `9056df3354df6a84755fb47a38da2793f141efa9` (gates `16c431bb38`). NOT on the offline remote → **durability gap; Lane 01 preserves it first.** (It also carries `9e9b9e60 (#5696)` Harbor `production_files_ready` fix — unrelated to Wave-2, just present in the branch.)
- **Flagship goldens FROZEN — do not edit:** `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt`, `CANONICAL_FLAGSHIP_BOOK.txt`. gen_z_professionals×anxiety is already PROVEN-AT-BAR; the line-edit lane picks OTHER designated flagship cells.
- Local checkout is the dirty shared tree — READ surface only, never a commit substrate. `timeout(1)` absent on this macOS host (use ssh `ConnectTimeout` / git `http.lowSpeed*`).

## Source request

Operator (2026-07-18, router chat): with GitHub down, keep moving offline; the
single highest-leverage next track is "Wave-2 flagship line-edit + bank fill — the
one that actually moves 'are they great?'". "say the word" → said.

## Files

| File | Owner | Wave | Signal token |
|------|-------|------|--------------|
| `00_MASTER_DISPATCH_PROMPT.md` | Pearl_PM_Dispatcher | — | `perfect-books-wave2-dispatcher=PASS\|PARTIAL` |
| `01_Pearl_DevOps_durability_substrate_lock.md` | Pearl_DevOps | 0 | `perfect-books-wave2-substrate=<github\|pearlstar_offline>` + `perfect-books-wave1-preserved=<ref@sha>` |
| `02_Pearl_Editor_bank_fill_c1_c4.md` | Pearl_Editor | 1 | `perfect-books-wave2-bankfill=<sha>` |
| `03_Pearl_Editor_flagship_line_edit_l1_l4.md` | Pearl_Editor | 1.5 (gated on 02) | `perfect-books-wave2-lineedit=<sha>` |
| `04_Pearl_Dev_deferred_ci_gates.md` | Pearl_Dev | 1 | `perfect-books-wave2-cigates=<sha>` |
| `05_Pearl_PM_blind10_operator_prep.md` | Pearl_PM | 2 (gated on 03) | `perfect-books-wave2-blind10-prep=<sha>` |
| `06_Pearl_PM_final_audit_closeout.md` | Pearl_PM | 4 | `perfect-books-wave2-final=PASS\|PARTIAL` |

## Wave order + dependencies (SIGNAL checks, not narrative)

**Gate-check convention:** a signal "exists" when `grep` finds its literal token on
its surface. Wave-0 signals live in
`artifacts/qa/perfect_books_wave2_20260718/SUBSTRATE_LOCK.md`; every other lane's
signal lives in its handoff under `artifacts/coordination/handoffs/`.

- **Wave 0 (serial):** Lane 01 — preserve the Wave-1 branch offline + lock substrate. Nothing launches before `perfect-books-wave2-substrate=…`.
- **Wave 1 (parallel):** Lane 02 (bank fill, Pearl_Editor) + Lane 04 (deferred CI gates, Pearl_Dev). Disjoint surfaces (atom banks vs CI scripts).
- **Wave 1.5 (serial after 02):** Lane 03 (line-edit) gates on `perfect-books-wave2-bankfill=<sha>`. **Serial, not parallel, with Lane 02** — both write atom banks (SOURCE_OF_TRUTH); parallel edits collide. Same Pearl_Editor owner ideally.
- **Wave 2:** Lane 05 (blind-10 prep) gates on `perfect-books-wave2-lineedit=<sha>` (needs the rendered `system working` cells).
- **Wave 4 (serial, last):** Lane 06, gated on ALL terminal signals. Sole writer of hot coordination files.

## Hot-file collision map

- `docs/PROGRAM_STATE.md`, `ACTIVE_WORKSTREAMS.tsv`, `operator_decisions_log.tsv`, `docs/DOCS_INDEX.md`, `PEARL_PRIME_PERFECT_BOOKS_SPEC.md` §8 checkboxes: **Lane 06 ONLY**.
- Atom-bank surfaces (`atoms/**`, `SOURCE_OF_TRUTH/**`): **Lanes 02 then 03, serial** (03 gates on 02). Never parallel.
- CI/gate scripts (`scripts/ci/`, `phoenix_v4/quality/`, `.github/workflows/drift-detectors.yml`, `scripts/run_production_readiness_gates.py`): **Lane 04 ONLY**. Note: Lane 04 must NOT touch `register_gate.py`'s F16 (G-WRAP, Wave-1) or the enrichment DEF4 path — additive gates only.
- `artifacts/qa/flagship_line_edit/`: **Lane 03 ONLY** (extends the scaffold README).
- `handoffs/`: one file per lane, append-only.

## Offline landing recipe (this pack's MERGED-equivalent while GitHub is blocked)

Same as the oldchats7 pack — temp-index plumbing off the base tree, explicit paths
only, poison-protocol diff-stat gate, push to `offline/<lane-slug>-20260718`:

```bash
# disk precheck (df -g / ≥20GB) → else BLOCKED
export GIT_INDEX_FILE=$(mktemp -d)/idx
BASE=<origin/main, or agent/pearl-prime-perfect-books-wave1 for lanes building on Wave-1>
git read-tree "$BASE^{tree}"
GIT_LFS_SKIP_SMUDGE=1 git add -f -- <explicit intended paths only>   # never -A / never .
TREE=$(git write-tree)
git diff --stat "$BASE" "$TREE"                                       # THE GATE: exact file list
COMMIT=$(git commit-tree "$TREE" -p "$BASE" -m "<msg>")
git push pearlstar_offline "$COMMIT:refs/heads/offline/<lane-slug>-20260718"
unset GIT_INDEX_FILE
git -c core.sshCommand="ssh -o ConnectTimeout=8 -o BatchMode=yes" ls-remote pearlstar_offline | grep <lane-slug>
```

**GitHub-path rule:** if `perfect-books-wave2-substrate=github`, replace the recipe
with golden-branch-from-origin/main → explicit-path stage → push → PR → required
checks green → **squash-merge same turn** (G-CLAIM/G-LAYER are required checks — a
closeout using `bestseller`/`system working` without the matching acceptance-layer
term/artifact BLOCKS; comply, don't weaken). PR-open is never terminal.

## Acceptance-layer honesty (every closeout, per §0 + G-CLAIM)

Label every result: `structurally clear` (L1) / `authored candidate` (L2) /
`system working` (L3, needs `ONTGP_VERDICT.md` PASS) / `bestseller register` (L4,
operator blind-10 only). This wave's honest ceiling = **`system working` on the
line-edited cells**; the SYSTEM stays `authored candidate` until the operator runs
blind-10. No lane may write `bestseller`/`shippable`/`production-ready` without the
matching proof — G-CLAIM will (and should) block it.

## Operator-tier items carried by this pack

- **Q-W2-CELLS-01 (default from analysis):** Lane 03 picks the 3 designated flagship
  cells from `MATRIX.tsv` — default recommendation: `corporate_managers×burnout×overwhelm`
  (the #1923-proven shipping cell) + 2 more machine-clean cells from distinct
  personas (avoid the frozen gen_z×anxiety). Operator may override the 3.
- **B1 blind-10 is operator-only** — Lane 05 PREPARES the packet; the Layer-4 read
  is never agent-executed or agent-claimed.

## Terminal state

Every lane LANDED-OFFLINE / MERGED / BLOCKED-with-evidence + handoff + cleanup
ledger. Lane 06 verifies, checks the spec §8 "Done when" boxes it can honestly
check (≥3 `system working` cells iff `ONTGP_VERDICT.md`=PASS exist), updates
coordination + PROGRAM_STATE (offline-pending note, not on-main), and `open`s the
blind-10 packet + ONTGP verdicts for the operator.
