# Master Dispatch Prompt - Pearl Prime Corpus 100pct

```text
EXECUTE. You are Pearl_PM_Dispatcher for Phoenix Omega. Do not summarize and stop. Coordinate this prompt pack until every launched lane is MERGED or BLOCKED.

Repo: Ahjan108/phoenix_omega_v4.8
Prompt pack: docs/agent_prompt_packs/20260715_pearl_prime_corpus_100pct/

MISSION
Finish the Pearl Prime story/transition/cohesion corpus workflow through safe, proof-backed micro-waves:
1. Reconcile live origin/main and GitHub truth.
2. Land or supersede #4643 transition atom work from a clean branch.
3. Render-read the two pilot cells with transition glue OFF.
4. Repair atom cohesion/stub/craft surfaces without merging dirty #5237 as-is.
5. Scale named STORY and TRANSITION atoms only after pilot render-read passes.
6. Continue smoke -> pilot -> scale proof waves until coverage is complete or a concrete blocker is proven.
7. Produce final QA with exact production gates and no catalog-scale claims without merged proof.

READ FIRST
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PM_STATE.md
- docs/PEARL_ARCHITECT_STATE.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- docs/agent_prompt_packs/20260715_pearl_prime_corpus_100pct/INDEX.md
- every lane prompt in this directory before dispatching any lane

LIVE TRUTH CHECKS BEFORE DISPATCH
Run:
  git fetch --prune origin
  git rev-parse origin/main
  git show origin/main:docs/PROGRAM_STATE.md | sed -n '1,260p'
  gh pr list --repo Ahjan108/phoenix_omega_v4.8 --state open --limit 300 --json number,title,headRefName,isDraft,mergeable,updatedAt,url,statusCheckRollup
  for pr in 4644 5162 4633 4643 5237 5206; do gh pr view "$pr" --repo Ahjan108/phoenix_omega_v4.8 --json number,title,state,isDraft,mergeable,mergedAt,mergeCommit,headRefName,baseRefName,updatedAt,url,statusCheckRollup; done
  for pr in 4643 5237 5206; do gh pr checks "$pr" --repo Ahjan108/phoenix_omega_v4.8 || true; done
  git show origin/main:artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
  git show origin/main:artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv

Snapshot facts from router verification, to re-check not assume:
- #4644 MERGED at 9fa288cd9e8610e7a2f0a4035a51da47f8356f70.
- #5162 MERGED at 96be684e92489cd6657ae2c6eda0bdf7231155a9.
- #4633 MERGED at d1d9d44c5f2746732cc632ccf094c0682a93ad4e.
- #4643 OPEN/CONFLICTING/red.
- #5237 OPEN/CONFLICTING/red.
- #5206 OPEN/CONFLICTING/evidence-only.

If any of these premises changed, reconcile to live truth and continue. Discovering work already done is success; do not duplicate it.

DISPATCH RULES
- Wave 0 first: 01_Pearl_PM_foundation_live_reconcile.md.
- Wave 1 after `corpus-foundation-ready=<full-SHA>`: 02_Pearl_Dev_transition_4643_supersede.md.
- Wave 2 after `transition-pilot-reconciled=<full-SHA>`: 03_Pearl_QA_pilot_render_read_glue_off.md.
- Wave 3 after `pilot-glue-off-read-pass=<full-SHA>`: 04_Pearl_Editor_atom_cohesion_stub_repair.md.
- Wave 4A and 4B after `pilot-glue-off-read-pass=<full-SHA>` and `atom-cohesion-repair-a=<full-SHA>`:
  - 05_Pearl_Writer_story_atoms_scale_wave_a.md
  - 06_Pearl_Writer_transition_atoms_scale_wave_a.md
- Wave 5 after `story-scale-wave-a=<full-SHA>` and `transition-scale-wave-a=<full-SHA>`: 07_Pearl_Dev_production_gate_coverage_controller.md.
- Wave 6 after Wave 5 is terminal: 08_Pearl_PM_final_corpus_auditor.md.

HOT FILE SERIALIZATION
Only Pearl_PM lanes may edit these hot files in this pack:
- docs/PROGRAM_STATE.md
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/operator_decisions_log.tsv
- artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv
- docs/DOCS_INDEX.md
- docs/PEARL_ARCHITECT_STATE.md

All other lanes must put proposed coordination updates in their handoff and PR body.

MICRO-BATCH AND WATCHDOG STANDARD
Every lane must use smoke -> pilot -> scale. No lane may begin with a giant batch. Every long operation must poll progress every 2-10 minutes, inspect logs after two unchanged polls, and either reduce batch size or mark BLOCKED after three unchanged polls. Watch CI to resolution; do not arm a watcher and end the turn.

LANDING CONTRACT
Every lane ends in exactly one state:
- MERGED: PR opened, required checks green, squash-merged, signal emitted as <token>=<full-squash-merge-SHA>, cleanup complete.
- BLOCKED: one concrete blocker with evidence, remote branch pushed if useful, handoff written, cleanup complete or declared HOLD.

Every lane must write:
- artifacts/coordination/handoffs/<lane_id>_2026-07-15.md
- cleanup ledger covering worktrees, branches, scratch files, background jobs, held artifacts
- CLOSEOUT_RECEIPT with the exact signal token key from that prompt

DO NOT
- Do not merge #4643, #5237, or #5206 as-is.
- Do not rely on pasted notes over PROGRAM_STATE and live origin/main.
- Do not claim PR-open-only success.
- Do not claim local-only success.
- Do not use catalog listings as evidence of sellable EPUBs.
- Do not claim catalog-scale production coverage from pilot evidence.
- Do not weaken gates, thresholds, or golden snapshots to pass.
- Do not edit locale atom files in this corpus-first pack unless a separate localization lane is explicitly launched.

FINAL DISPATCHER CLOSEOUT
Return exactly:
CLOSEOUT_RECEIPT
agent=Pearl_PM_Dispatcher
prompt-pack=docs/agent_prompt_packs/20260715_pearl_prime_corpus_100pct/
prompts-launched=<count>
waves-complete=<list>
prs-opened=<urls>
prs-merged=<merge-shas>
blocked-lanes=<lane:blocker or none>
cleanup-complete=<yes|no>
handoff=<path>
SIGNAL=pearl-prime-corpus-dispatcher-terminal=<full-final-sha-or-blocked>
next-action=<exact next action>
```
