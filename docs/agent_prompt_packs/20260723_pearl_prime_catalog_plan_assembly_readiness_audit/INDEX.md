# Pearl Prime Catalog Plan + Assembly Readiness Audit — 2026-07-23

## Program goal

The operator is planning the true en_US catalog (all brands, ~800-scale per brand
target where applicable) and wants a **read-only** audit — look at what's already
**planned**, and predict/audit what **assembly** would do with those plans, WITHOUT
assembling/rendering any new books. Six questions drive it: is a bestseller
contract/thesis established before a book is okayed for catalog; is Pearl_Editor's
content-authority landing at the right pipeline stage; is cohesive flow real at
catalog scale; is enrichment/atom utilization real; is EI v2 actually in the loop;
and is the planned catalog mix profit-weighted the way the business needs while
still keeping a help/access spread.

**This is an audit-only pack. No lane renders, assembles, or ships a book.**

## Live truth anchor

`origin/main` @ `244955eaa01ddd9093001d184b41ba71e2a84a2b` (2026-07-23). Every lane
re-fetches and re-derives this live — treat the SHA above as a snapshot, not truth.
`docs/PROGRAM_STATE.md`'s own cited SHA (`a08b8af17b…`, 2026-07-22) is already one
day stale relative to this anchor.

## Do not duplicate — build on this instead

`artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md` (merged, on
`origin/main`) already ran a rigorous 3-axis audit (bestseller register / cohesive
flow / atom utilization) — but only on the **flagship golden + 3 sample cells**, not
catalog-scale, and it does not touch Pearl_Editor sequencing, EI v2 wiring, or the
marketing/revenue mix question. **Read it first in every lane.** Do not re-derive its
Axis 1–3 findings; cite and extend them. Its "single highest-leverage next fix" —
author `story_atoms` for EPUB workhorse cells (`corporate_managers` has **zero**) —
is standing context every lane should carry forward, not re-discover.

Also open (do not treat as duplicate, but be aware): PR **#56** —
`docs(piper): Pearl Prime pipeline audit prompt` — is the prompt pack that produced
the 07-22 report; it is a docs-only artifact, not a competing audit.

## Source request

Operator (verbatim, condensed): run a robust test of the Pearl Prime planner +
assembly pipeline. Look at the plans that already exist for the US market across
all brands (catalog-scale, ~800/brand where that's the real target). Do **not**
assemble. Audit what assembly *would* do with those plans. Ask every question about
whether the pipeline is actually producing bestseller-quality, cohesive,
therapeutic/enriched books — and whether it's tilted toward revenue vs a helpful
spread on purpose or by accident. Get EI v2 genuinely wired into the system, not
just referenced.

## Prompt count + wave order

6 lane prompts + 1 dispatcher.

| Wave | Lane | Depends on | Parallel-safe |
|---|---|---|---|
| 1 | A — Catalog plan inventory | none | yes |
| 1 | B — Pearl_Editor / content-authority sequencing | none | yes |
| 1 | D — Marketing / revenue-mix audit | none (re-derives its own distribution) | yes |
| 1 | E — EI v2 integration-gap audit | none | yes |
| 2 | C — Assembly-readiness prediction (catalog-scale) | A merged (needs the plan inventory to sample from) | after A |
| 3 | F — Synthesis + system report | A, B, C, D, E all merged | last |

## Owners / subsystem authority

- Lane A, C: `core_pipeline` / `pearl_prime` → Pearl_Prime (per
  `SUBSYSTEM_AUTHORITY_MAP.tsv`).
- Lane B: content-authority sequencing question is `pearl_prime` + the
  `PEARL-EDITOR-UPSTREAM-01` cap → route as Pearl_Architect-adjacent audit (Pearl_PM
  may run it directly; it is read-only doc/code archaeology, not a Pearl_Editor
  content-authoring session).
- Lane D: `marketing` → Pearl_Marketing (audit only; no live copy/campaign writes).
- Lane E: `ei_v2` → Pearl_Research (per `SUBSYSTEM_AUTHORITY_MAP.tsv` row 9).
- Lane F + dispatcher: Pearl_PM (final coordination/state per
  `PROMPT_ROUTER_OPERATING_MANUAL.md` §12).

## Substrate

Every lane branches fresh from `origin/main` (standard golden-branch pattern — no
worktree needed; these lanes write only new files under `artifacts/qa/` and
`docs/agent_prompt_packs/…/reports/`, never touch hot coordination files directly
except the dispatcher's own `ACTIVE_WORKSTREAMS.tsv` row and `PROGRAM_STATE.md`
milestone update in Lane F). Disk at authoring time: 74 GiB free — no worktree
hazard, but still `GIT_LFS_SKIP_SMUDGE=1` on any fresh clone/checkout per repo
convention.

## Expected outputs

- `artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/<lane>/REPORT.md` +
  `evidence/` per lane.
- One PR per lane (or the dispatcher may batch A+B+D+E into a combined PR if all
  four land clean in the same session — do not force this, four separate PRs is
  fine and safer for review).
- Lane F additionally updates `docs/PROGRAM_STATE.md` with a dated summary row (new
  entry, not a rewrite of the 07-22 audit's rows) and appends a
  `docs/PEARL_ARCHITECT_STATE.md` cap-entry-candidate ONLY if Lane F's findings
  require a new enforced gate (per `agent_brief.txt` §14 — memory is recall, not
  enforcement).

## Hot-file conflict notes

Lane F is the only lane touching `docs/PROGRAM_STATE.md`. Lanes A–E must NOT edit
it. If two lanes finish near-simultaneously, Lane F is the single serial writer;
sequence it last (Wave 3) specifically to avoid this collision.

## Required signal tokens

- `lane-a-plan-inventory-merged=<sha>`
- `lane-b-editor-sequencing-merged=<sha>`
- `lane-c-assembly-readiness-merged=<sha>`
- `lane-d-marketing-mix-merged=<sha>`
- `lane-e-ei-v2-gap-merged=<sha>`
- `lane-f-synthesis-merged=<sha>`

## Cleanup and handoff

Every lane writes `artifacts/coordination/handoffs/pp-catalog-audit-<lane>_2026-07-23.md`.
Local branches deleted after merge; no worktrees created so nothing to prune.

## Final audit lane

Lane F is the final audit/synthesis lane — it does not run until A–E all show a
merge SHA.

## Paste-ready next action

Paste `00_MASTER_DISPATCH_PROMPT.md` into the lead agent chat. It fans out Wave 1
(A, B, D, E) in parallel, then Wave 2 (C), then Wave 3 (F).
