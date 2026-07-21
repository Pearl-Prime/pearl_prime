# Pearl Prime Perfect Books Wave-2 — FINAL AUDIT (Lane 06, Pearl_PM)

**Date:** 2026-07-19 (dispatched 2026-07-18)
**Agent:** Pearl_PM (lane 06, final audit + coordination closeout)
**Substrate:** GitHub still 403 account-suspended at time of this audit — every
landing below is OFFLINE on `pearlstar_offline`, none on `origin/main`.
**Acceptance ceiling this wave:** `authored candidate` (banks filled, CI gates
added, ONTGP attempted honestly). **SYSTEM_WORKING_CELLS = 0.** SYSTEM stays
`authored candidate`. **NO bestseller-register claim.**

## 1. Lane × terminal-state × ref × acceptance-layer matrix

| Lane | Owner | Terminal state | Ref @ SHA (verified `ls-remote pearlstar_offline`) | Base | Acceptance layer |
|---|---|---|---|---|---|
| 01 substrate | Pearl_DevOps | LANDED-OFFLINE | `offline/perfect-books-wave2-substrate-20260718@5e648abae1f0841821186bb085a54c7882a21ae7` | n/a (SUBSTRATE_LOCK.md report) | structurally clear (plumbing) |
| Wave-1 preserved | Pearl_DevOps (lane 01) | PRESERVED-OFFLINE | `offline/pearl-prime-perfect-books-wave1-20260718@9056df3354df6a84755fb47a38da2793f141efa9` | n/a | durability only |
| 02 bank fill (C1–C4) | Pearl_Editor | LANDED-OFFLINE | `offline/perfect-books-wave2-bankfill-20260718@d48fbdacacabc21641709f9411af90dd46c3ed27` | Wave-1 tip `9056df3354` | authored candidate (banks filled; C4 NOT fixed) |
| 03 flagship line-edit (L1–L4) | Pearl_Editor | LANDED-OFFLINE | `offline/perfect-books-wave2-lineedit-20260718@4356fb0dea205510e7c82a5afad0a629c9117d25` | bankfill tip `d48fbdac` | structurally clear on the atom fixes; **0/3 `system working`** |
| 04 deferred CI gates | Pearl_Dev | LANDED-OFFLINE | `offline/perfect-books-wave2-cigates-20260718@b2d6761d9d641e53af8f27b91974adaebddef24b` | Wave-1 tip `9056df3354` | structurally clear (enforcement mechanisms, mutation-verified) |
| 05 blind-10 prep | Pearl_PM | LANDED-OFFLINE | `offline/perfect-books-wave2-blind10-prep-20260718@2a7332763db2105a7ff24e7c521699b2fa0dbdc0` | lineedit tip `4356fb0d` | Layer-4 PENDING (packet assembled from Layer-1 books only — 0 Layer-3 inventory existed to build from) |
| 06 final audit (this lane) | Pearl_PM | LANDED-OFFLINE | see CLOSEOUT_RECEIPT in handoff | blind10-prep tip `2a733276` | coordination-class |

All 6 offline refs independently re-verified this lane via:

```
git -c core.sshCommand="ssh -o ConnectTimeout=8 -o BatchMode=yes" ls-remote pearlstar_offline
```

— every SHA above matches the corresponding lane's self-reported `LANDED=` line exactly. No discrepancy found.

## 2. Diff-stat spot-checks (per lane, against claimed base)

Ran `git diff --stat <base> <landed>` for every lane after fetching the offline
refs into local `refs/offline_audit/*`. Every file in every diff matches the
lane handoff's own "Files changed (explicit list)" section — no undeclared
files, no composer/registry/`register_gate.py` edits, no `git add -A` residue.

- **Lane 02 (bankfill) vs Wave-1 tip:** 12 files, all `SOURCE_OF_TRUTH/accent_banks/**` (burnout) + `lane02/` proof docs + handoff. Matches.
- **Lane 04 (cigates) vs Wave-1 tip:** 16 files — 3 new CI scripts, 1 new lexicon config, 3 new test files, `run_production_readiness_gates.py` (additive gates 38–40 only, confirmed by reading the diff hunk — no edits to gates 1–37, no `register_gate.py` touch), 1 new workflow (`accent-supply-preflight.yml`), 9-line addition to `drift-detectors.yml`, `lane04/` proof docs + handoff. Matches.
- **Lane 03 (lineedit) vs Lane 02 tip:** 18 files — 3 `atoms/**/STORY/CANONICAL.txt` edits (24 atoms, insertions only + targeted rewrites, no deletions beyond the leaked-metadata lines) + 3× (`ONTGP_VERDICT.md`+`NOTES.md`+`RENDER_REF.txt`) + `lane03/` proof docs + handoff. No `registry/*.yaml`, no composer code. Matches.
- **Lane 05 (blind10-prep) vs Lane 03 tip:** 9 files — the 6 packet files + `lane05/` proof docs + handoff. No `atoms/**`/`SOURCE_OF_TRUTH/**`/`scripts/ci/**` touched. Matches.

**Drift check result: PASS — no lane fixed register by composer/topology retune.**
Lane 02/03 both explicitly held the banned lever (registry_resolver.py /
enrichment_select.py / registry/*.yaml all confirmed untouched by the diff).
Lane 04 confirmed additive-only against `run_production_readiness_gates.py`
and did not touch `register_gate.py` F16 or the DEF4 detector.

## 3. Acceptance-layer honesty check (the headline check)

- **No lane claims `system working` without a matching `ONTGP_VERDICT.md=PASS`.**
  Lane 03 read all 3 designated cells and reported **FAIL on all 3**, with cited,
  quoted evidence per chapter, and explicitly refused to round FAIL up to PASS
  even though `healthcare_rns × burnout × overwhelm` Ch12 alone scored a clean
  5/5. Verified directly by reading each `ONTGP_VERDICT.md`'s "Overall verdict"
  line: all three say **FAIL** (`healthcare_rns` annotated "closest of the 3 to
  PASS").
- **No lane uses `bestseller`/`shippable`/`production-ready` without matching
  proof.** Lane 02 and Lane 04 both label their own ceiling `authored
  candidate` / `structurally clear` respectively. Lane 05 explicitly labels its
  packet's ceiling **Layer 1 `structurally clear`** for all 10 books (register-gate
  PASS is a Layer-1 hard gate per spec §0, not Layer 3) and states **Layer-4
  PENDING operator read — no register/bestseller claim exists** until the
  operator records a verdict.
- **FINDING: none.** No acceptance-layer honesty violation found in any of the
  5 content/gate lanes' handoffs or landed artifacts. This audit does not need
  to bounce any FINDINGS back to a lane.

## 4. Cleanup / worktree check

`git worktree list` shows ~30 registered worktrees on this host — all
pre-existing, unrelated ongoing workstreams (translation batches, manga
episodes, atom-health backlogs) that predate this pack and were not created by
any Wave-2 lane. **No lane in this pack created a new worktree** (the INDEX
recipe uses `GIT_INDEX_FILE` temp-index plumbing, not `git worktree add`, and
every lane's cleanup ledger confirms `GIT_INDEX_FILE` was unset after its
landing commit). Disk free at audit time: **18 GB** (`df -g /`) — below the
pack's own 20GB precheck threshold; no new large lane commits were made in
this audit turn (plumbing + doc writes only, per hard constraint), so this is
a residual/pre-existing tightness, not something this lane created. Flagged as
a residual blocker below (needs an operator-level disk reclaim before the next
pack in this program can safely stage a fresh worktree-based lane).

## 5. Spec §8 "Done when" — ticked ONLY what is proven this wave

| Box | Ticked? | Evidence |
|---|---|---|
| `≥3 flagship cells have Layer-3 ONTGP_VERDICT.md = PASS` | **NO — stays unticked** | Lane 03: 3/3 cells FAIL, real evidenced reads. `SYSTEM_WORKING_CELLS=0`, not 1–2, not 3. |
| `One operator blind-10 PASS recorded` | **NO — stays unticked** | Lane 05 only prepared the packet (`Layer-4 PENDING`); no operator read has occurred. |
| G-F1H / G-ORIENT / G-ACCENT (new rows added to §8, per §3.B) | **YES — ticked** | Lane 04 landed all 3, 15/15 unit tests pass (re-verified this lane), each ran a mutation check (violating fixture → RED → revert → green, `lane04/MUTATION_CHECKS.md`), wired into `drift-detectors.yml` + readiness gates 38–40. Additive-only confirmed by diff read (gates 1–37 untouched, `register_gate.py` F16/DEF4 untouched). |

Net change to spec: 3 new rows added under §8 (previously these 3 mechanisms
had no explicit checklist line — they were only named in Wave-1's "Deferred"
list); all 3 ticked with cited evidence. The 2 pre-existing unticked rows
(flagship ≥3 PASS, blind-10 PASS) remain unticked — this wave did **not**
newly satisfy them, despite substantial genuine progress (bank fill + honest
ONTGP attempts + a ready blind-10 packet).

## 6. Honest scorecard

- **`system working` cells this wave: 0.** (Lane 03, real ONTGP reads, 3/3 FAIL — no fabricated PASS.)
- **Gates added: 3** (G-F1H, G-ORIENT, G-ACCENT — all shipped, mutation-verified, additive).
- **Banks filled:** `WISDOM_ESSENCE/burnout` (+8 entries, was `no_supply_pool`), `AUTHOR_COMMENTARY/burnout/ravi_chandra` (+8), `AUTHOR_COMMENTARY/burnout/lena_thorne` (+8) — all validated (parse clean, 0 secular-lint violations, real loader smoke-test).
- **Atom-level fixes landed (forward-looking, L4-promoted into reusable banks):** 24 `STORY` atoms across 3 cells' banks (leaked-batch-generation-metadata defect, a real, grep-confirmed catalog-wide-present bug; this pass fixed only the 3 designated cells' own copies).
- **Blind-10 packet: ready, unread.** 10/10 real production `way_stream_sanctuary` EPUBs, non-padded, Layer-1 ceiling honestly labeled. **Blind-10 box NOT ticked.**
- **The one blocking discovery of the wave — G-DEF4 catalog-wide blast radius:**
  14 of 16 checked topic registries (`registry/{topic}.yaml`) are authored
  100% for a single persona label (`Gen Z` for 14 topics, including `burnout`);
  any other persona rendering those topics under the canonical four-piece
  chord hard-stops production with 106 foreign-persona drops — reproduced live,
  independently, by both Lane 02 and Lane 03, on 3 different cells including
  the dispatcher's own default "#1923-proven shipping cell"
  (`corporate_managers × burnout × overwhelm`). **This is why none of the 3
  designated cells could reach a fresh Layer-1 chord render this wave**, and
  it is the most consequential open finding carried into the replay queue
  below — not fixed here (correctly out of scope for a fill/line-edit lane;
  the compliant fix is either a destructive registry reassignment or a
  `registry_resolver.py::load_registry` code change, both banned levers for
  Lanes 02/03).

## 7. Residual blockers (not fixed this wave, carried forward)

1. **G-DEF4 catalog-wide routing blocker** (see §6) — recommend a dedicated,
   explicitly-scoped future lane, Pearl_Dev (code: persona-aware registry
   routing) + Pearl_Editor (content: per-persona registry authoring) co-owned.
   Blocks a clean Layer-1 render for the majority of non-Gen-Z persona × topic
   pairs catalog-wide, not just the 3 Wave-2 cells.
2. **2 renderer-level defects found by Lane 03, documented not fixed:** (a)
   broken `window_reference`/light-detail family in
   `config/rendering/environment_fallback_families.yaml` (malformed doubled-
   predicate `text:` entries, confirmed live in 2/3 cells' manuscripts); (b) a
   mid-sentence truncation bug in the `healthcare_rns` Ch5 render (section-join
   / depth-enrichment boundary defect). `healthcare_rns × burnout × overwhelm`
   is explicitly flagged by Lane 03 as **one clean fix away from a real ONTGP
   PASS** (Ch12 alone already scores a clean 5/5) — this is the catalog's most
   promising near-term path to its first genuine Layer-3 `system working` cell.
3. **Duplicate cross-chapter atom selection** (corporate_managers manuscript
   reuses the same STORY atom verbatim in Ch2 and Ch12) — composer/enrichment-
   selection-adjacent, banned lever for Lanes 02/03, flagged for Pearl_Dev +
   Pearl_Architect per the ONTGP routing table.
4. **Catalog-wide leaked-batch-generation-metadata defect** (`grep -rl
   "Wave2-\|as an lived scene" atoms/`) — confirmed present in hundreds of
   files across nearly every persona/topic bank; only the 3 designated cells'
   24 atoms were fixed this wave. Recommend a dedicated bank-hygiene lane.
5. **14/20 top `MATRIX.tsv` cells have a real accent `no_supply_pool` gap**
   (`WISDOM_ESSENCE`/`AUTHOR_COMMENTARY`/`EXTERNAL_STORY` mostly, non-pilot
   persona×topic pairs) — surfaced by Lane 04's new G-ACCENT preflight, live;
   this is a bank-fill signal for a future Lane 02/03-style pass, not a Lane
   04 defect.
6. **G-ORIENT lexicon SSOT is a v1** (58 words, English-only) — recommend
   widening once a larger authored-candidate corpus exists from a future
   line-edit pass.
7. **Blind-10 operator read itself** — packet ready and unread; this is the
   named next action, not a defect.
8. **Disk headroom (18 GB)** — below the pack's own 20 GB precheck threshold;
   flagged for operator awareness before the next worktree-heavy lane in this
   program.

## 8. GitHub-restore replay queue (in order)

When GitHub access is restored (`ls-remote origin` no longer 403), replay onto
`origin/main` in this exact order (each is a `git fetch pearlstar_offline
refs/heads/<ref>` + golden-branch-from-origin/main + cherry-pick or direct PR,
per each lane's own base chain):

1. `offline/pearl-prime-perfect-books-wave1-20260718@9056df3354df6a84755fb47a38da2793f141efa9` (Wave-1 enforcement: G-CLAIM, G-LAYER, G-WRAP, G-DEF4, D2, D3, L1 scaffold — carries `9e9b9e60 (#5696)` Harbor fix, unrelated but present)
2. `offline/perfect-books-wave2-substrate-20260718@5e648abae1f0841821186bb085a54c7882a21ae7` (SUBSTRATE_LOCK.md report only)
3. `offline/perfect-books-wave2-bankfill-20260718@d48fbdacacabc21641709f9411af90dd46c3ed27` (C1–C3 bank fill, 3 cells, burnout accent banks)
4. `offline/perfect-books-wave2-cigates-20260718@b2d6761d9d641e53af8f27b91974adaebddef24b` (G-F1H/G-ORIENT/G-ACCENT — independent of bankfill/lineedit, can replay in parallel with 3–5)
5. `offline/perfect-books-wave2-lineedit-20260718@4356fb0dea205510e7c82a5afad0a629c9117d25` (24 atom fixes + 3 ONTGP verdicts; stacks on #3)
6. `offline/perfect-books-wave2-blind10-prep-20260718@2a7332763db2105a7ff24e7c521699b2fa0dbdc0` (blind-10 packet; stacks on #5)
7. This lane's own landing (`offline/perfect-books-wave2-final-20260718`, see handoff for exact SHA) — coordination writes + FINAL_AUDIT.md + pack directory itself.

Each replay PR must carry its lane's own acceptance-layer label unchanged
(G-CLAIM/G-LAYER required checks will enforce this on `origin/main`) — do not
upgrade any label during replay.

## 9. ACCEPTANCE_LAYER (final)

**`system working` on 0 cells. SYSTEM remains `authored candidate`. NO
bestseller-register claim.** Genuine progress this wave: 3 CI gates shipped +
mutation-verified, 24 atoms real-fixed and bank-promoted, 3 accent-bank gaps
filled, 1 catalog-wide routing blocker root-caused with live reproducible
evidence, 1 blind-10 packet assembled honestly from a Layer-1-ceiling pool.
None of this crosses into Layer 3 or Layer 4 — reported as such, not rounded up.

**SIGNAL=perfect-books-wave2-final=PARTIAL**
