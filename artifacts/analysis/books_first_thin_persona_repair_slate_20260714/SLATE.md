# Books-First Thin-Persona Repair Slate - 2026-07-14

STARTUP_RECEIPT
AGENT:              Pearl_Research
LANE:               thin_persona_repair_slate_20260714
PROJECT_ID:         proj_pearl_prime_bestseller_rebase_20260425
SUBSYSTEM:          pearl_prime;core_pipeline;repo coordination
AUTHORITY_DOCS:     docs/PROGRAM_STATE.md; docs/SESSION_UNITY_PROTOCOL.md; docs/agent_brief.txt; docs/PEARL_PM_STATE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md; specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; specs/PHOENIX_V4_5_WRITER_SPEC.md; artifacts/qa/thin_persona_buildability_2026-07-11/SUMMARY.md; artifacts/analysis/PROPRIME_100PCT_PRODUCTION_AUDIT_2026-07-10/MASTER_AUDIT.md; docs/agent_prompt_packs/20260714_books_first_epub_wave/INDEX.md from dispatcher checkout
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/analysis/books_first_thin_persona_repair_slate_20260714/*; artifacts/coordination/handoffs/thin_persona_repair_slate_20260714_2026-07-14.md
OUT_OF_SCOPE:       atoms/**; scripts/**; phoenix_v4/**; docs/PROGRAM_STATE.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; locale atom files; teacher_banks
PROVENANCE:
  research:  artifacts/analysis/PROPRIME_100PCT_PRODUCTION_AUDIT_2026-07-10/; artifacts/qa/thin_persona_buildability_2026-07-11/SUMMARY.md
  documents: docs/PROGRAM_STATE.md; docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; specs/PHOENIX_V4_5_WRITER_SPEC.md
  builds_on: existing atom gap matrix; existing thin-persona buildability proof; existing Pearl Prime spine path
  inventory: UNCHANGED for runtime/code; EXTENDS analysis only
BLOCKERS:           none
READY_STATUS:       ready

## Gate Signal

- Foundation signal: `foundation-dispatch-ready=7914b45693f9ca846399a659d66c729f35b5cc40`.
- Verified ancestor: `git merge-base --is-ancestor 7914b45693f9ca846399a659d66c729f35b5cc40 origin/main` -> exit 0.
- Current `origin/main`: `7914b45693f9ca846399a659d66c729f35b5cc40`.

## Discovery Report

- #5530 (`2d9ada1e217e5c14ab0e7811425dd4176bac4e6c`) and #5535 (`d8532d2d43874051b90201bda8b07eab5c1ce817`) are ancestors of `origin/main`.
- #5489 (`3c5e1f3b7527902615bc903e682a0401b1452c5c`) already repaired these engine STORY banks:
  - `atoms/educators/imposter_syndrome/false_alarm/CANONICAL.txt`
  - `atoms/nyc_executives/anxiety/spiral/CANONICAL.txt`
  - `atoms/nyc_executives/anxiety/watcher/CANONICAL.txt`
  - `atoms/nyc_executives/imposter_syndrome/false_alarm/CANONICAL.txt`
- #5530 repaired `atoms/educators/imposter_syndrome/REFLECTION/CANONICAL.txt` and removed the stale `false_alarm` contradiction from `config/topic_engine_bindings.yaml`.
- The current parser path for tuple preflight is `phoenix_v4/gates/check_tuple_viability.py`, which loads engine STORY atoms through `phoenix_v4/planning/assembly_compiler.py::_parse_canonical_txt`.
- Live re-scan of all educators/nyc F006 arcs found no legal tuple still failing due to engine-keyed STORY depth or missing required bands.
- The only failures are true governance cells with both `NO_BINDING` and `NO_STORY_POOL`; they are listed in `no_binding_split.tsv` and must not be put in the writer batch.

## Smoke

Known repaired cell:

```
PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py \
  --persona educators --topic imposter_syndrome --engine false_alarm \
  --format F006 --repo . --json
```

Result: exit 0, `TUPLE_VIABLE`.

Current candidate cell previously called out as possibly thin:

```
PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py \
  --persona nyc_executives --topic anxiety --engine false_alarm \
  --format F006 --repo . --json
```

Result: exit 0, `TUPLE_VIABLE`.

## Pilot Slate

The smallest proof batch is four existing legal cells. No atom authoring is required before tuple proof:

| Cell | Tuple preflight | Usable STORY atoms | Bands |
| --- | --- | ---: | --- |
| `educators x imposter_syndrome x false_alarm x F006` | PASS | 16 | 1,2,3,4,5 |
| `educators x imposter_syndrome x shame x F006` | PASS | 33 | 1,2,3,4,5 |
| `nyc_executives x anxiety x false_alarm x F006` | PASS | 29 | 1,2,3,4,5 |
| `nyc_executives x anxiety x watcher x F006` | PASS | 32 | 1,2,3,4,5 |

Machine-readable table: `candidate_cells.tsv`.

## Writer Batch A Decision

Batch A atom-file list: none.

Reason: the current live repository already has enough parser-usable, band-complete engine STORY supply for the four-cell proof batch. Launching a writer authoring lane against these cells would duplicate already-merged work. The next lane should stand down the authoring portion and either emit a no-op writer handoff or proceed directly to tuple proof under PM serialization.

## True NO_BINDING Split

These cells remain out of authoring scope:

| Cell | Live preflight errors | Action |
| --- | --- | --- |
| `educators x boundaries x overwhelm x F006` | `NO_BINDING`, `NO_STORY_POOL` | governance decision before authoring |
| `educators x burnout x shame x F006` | `NO_BINDING`, `NO_STORY_POOL` | governance decision before authoring |
| `educators x compassion_fatigue x shame x F006` | `NO_BINDING`, `NO_STORY_POOL` | governance decision before authoring |
| `nyc_executives x burnout x shame x F006` | `NO_BINDING`, `NO_STORY_POOL` | governance decision before authoring |

Machine-readable table: `no_binding_split.tsv`.

## Open PR / Workstream Overlap

- #5623 touches `atoms/corporate_managers/**/locales/fr-FR/**`; no overlap with this slate.
- #5585 touches accent banks, `phoenix_v4/planning/accent_planner.py`, tests, and `CANONICAL_ARTIFACTS_REGISTRY.tsv`; no overlap with this slate.
- #5237 touches `atoms/corporate_managers/burnout/**` and atom-cohesion evidence; no overlap with the four selected proof cells, but still must not be broadened into Batch A.
- #5206 remains evidence-only and partially stale; no overlap with this analysis artifact.

## Commands Run

- `git fetch --prune origin`
- `git rev-parse origin/main`
- `git merge-base --is-ancestor 7914b45693f9ca846399a659d66c729f35b5cc40 origin/main`
- `git merge-base --is-ancestor 2d9ada1e217e5c14ab0e7811425dd4176bac4e6c origin/main`
- `git merge-base --is-ancestor d8532d2d43874051b90201bda8b07eab5c1ce817 origin/main`
- `gh pr view 5489 --json number,title,state,mergedAt,mergeCommit,files,url`
- `gh pr view 5530 --json number,title,state,mergedAt,mergeCommit,files,url`
- `gh pr view 5623 --json number,title,state,headRefName,files,url`
- `gh pr view 5585 --json number,title,state,headRefName,files,url`
- `PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py --persona educators --topic imposter_syndrome --engine false_alarm --format F006 --repo . --json`
- `PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py --persona nyc_executives --topic anxiety --engine false_alarm --format F006 --repo . --json`
- `PYTHONPATH=. python3 - <<'PY' ... check_tuple_viability scan for all educators/nyc F006 arcs ... PY`

## CLOSEOUT_RECEIPT

AGENT:          Pearl_Research
LANE:           thin_persona_repair_slate_20260714
STATUS:         MERGED-PENDING-PR
BRANCH:         codex/thin-persona-repair-slate-20260714
PR:             pending
MERGE_SHA:      pending squash merge
SIGNAL:         thin-persona-slate-ready=<full squash merge SHA to be emitted on PR merge>
PROOF_ROOT:     artifacts/analysis/books_first_thin_persona_repair_slate_20260714/
TESTS:          commands listed above
CLEANUP:        worktree/local branch/remote branch cleanup after merge
HANDOFF:        artifacts/coordination/handoffs/thin_persona_repair_slate_20260714_2026-07-14.md
NEXT_ACTION:    Stand down writer atom authoring for Batch A; run four-cell tuple proof from `candidate_cells.tsv`.
