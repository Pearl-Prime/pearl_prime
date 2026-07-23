# EXECUTE — Lane 07 (Pearl_Dev, manga): Land stranded manga work, hold the ramp gate

This is an execution prompt, not a planning request. End state: **every stranded
manga branch/PR is MERGED-or-BLOCKED, and scale work is explicitly HELD at the
operator read gate** — held-by-design is this lane's correct terminal state for
scale; "PR open" is not a terminal state for the landings.

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD SHA, `git status --short | head`, `gh auth status`,
  `git fetch origin && git log origin/main -1 --oneline`.
- Claims are from 2026-07-24 authoring — re-verify each branch/PR live. Sibling-
  collision check before every landing (`gh pr list --search`, merged+open).
- Manga doctrine binds (CLAUDE.md): six-layer acceptance labels on every claim;
  the three CI-enforced drift classes (stub-as-done, listing-as-story,
  unwired-config-as-working) — never weaken those gates; layered assembly only
  (assemble_from_bank), INTERIM provenance never presented as final; render path =
  ComfyUI 100.92.68.74:8188, flux1-schnell only; RAP queue-first via pscli for any
  GPU work (>10s) — read `docs/ROBUST_AGENT_PROTOCOL.md` first.
- Branch off origin/main per landing; preflight standard; merge rules standard
  (Rule-0, pre_merge_check live-CI gate after `PIPER100-L02-MAIN-GREEN`,
  governance). Squash-merge pre-authorized when green EXCEPT items marked HOLD.
- Reuse-first: all four landings below are EXISTING work — cherry-pick/rebase,
  never re-author. Drift recovery is git-first.

## Authority reads
`artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md`,
`docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md`,
`docs/sessions/SESSION_HANDOFF_2026-07-23_manga_audit_100pct_teacher_music.md`,
the manga dispatch handoff (3 pilot cells / 37 episodes verified on main via #275),
`artifacts/coordination/handoffs/manga_outfit_object_continuity_2026-07-22.md`.
DISCOVERY REPORT: current state of each item below + what's already on main.

## Landings (verify → land in this order)
1. **Genre-bubble wiring** — Lane 03 opened a PR from cherry-picked `aad5cf2152`
   (composition-grammar spec chain #4688/#4689 lineage). Review it against
   `assemble_from_bank.py`'s current main state (it moved this week), rebase if
   needed, run its tests, merge.
2. **Outfit/object continuity** — branch `agent/outfit-object-continuity`
   (`61f9a8fb85` + handoff commit `f6e40c62be`, 80 tests passing, ~156 behind main).
   Cherry-pick both commits onto a fresh branch off origin/main, re-run the 80
   tests against current main, merge. Its own handoff warns: cherry-pick, don't PR
   the stale base.
3. **`agent/manga-genre-story-only`** (1 commit: ban generic scaffolds/alternate
   authors in the genre-story-only path) — verify against the merged wave-2 work
   (#100 may overlap), cherry-pick the non-duplicate delta, merge.
4. **`offline/en-us-manga-asset-materialize-20260716`** (2 commits) — check whether
   its asset materialization survived the R2 offload waves; land what's still
   novel, byte-verify any asset rows it touches (stub-as-done gate applies to YOU).
5. **From Lane 03, if handed over:** the `fix-ci-two-gates` WIP tar (manga gates
   yaml + register_output_strengthen.py) — assess, land if real, discard with a
   note if superseded.

## HOLD (do not merge — operator quality gate, OPERATOR_ACTIONS.md item E1)
- **PR #245** (zh_TW smoke cell) and **#243** (doc-drift + 48ep program
  registration): the dispatch doctrine forbids merging the smoke cell without an
  operator read. Rebase them green and comment "HELD for operator read
  (pack 20260724)". When the operator says "manga pilot approved", merge both and
  note the approval in the merge commit body.
- **All scale work** (Wave-2 remaining scope beyond #100, 11-genre token-mapping
  fix, historical/cultivation pilot scripts, ja_JP/zh_TW batch branches
  `agent/manga-jajp-*`/`agent/manga-zhtw-*` batches 1–3): inventory them in the
  receipt with a one-line state each; dispatch NOTHING until the operator read.
  These are the next pack's scope.

## Closeout
```
CLOSEOUT_RECEIPT: PIPER100-L07-DONE
landed: <item → PR# + SHA, with acceptance layer each (CODE-WIRED/EXECUTED-REAL)>
held_for_operator: <#243 #245 + scale inventory>
duplicates_found: <what was already on main>
render_state: <pilot cells layer per six-layer taxonomy — expect EXECUTED-REAL, nothing PROVEN-AT-BAR>
NEXT_ACTION: operator read (item E1) → merge #243/#245 → author scale pack
```
Append a dated note to this pack's INDEX.md.
