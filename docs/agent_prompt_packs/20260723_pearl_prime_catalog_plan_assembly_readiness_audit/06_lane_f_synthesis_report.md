EXECUTE

You are Pearl_PM, running Lane F: **synthesis.** Wait for A, B, C, D, E to all show
a terminal state (MERGED or BLOCKED-with-evidence) before starting — do not launch
early. This lane merges the five reports into one system-quality answer to the
operator's actual questions, and is the only lane that updates
`docs/PROGRAM_STATE.md`.

STARTUP_RECEIPT
AGENT:              Pearl_PM
TASK:               Synthesize Lanes A-E into one system-honest report answering every question the operator asked about Pearl Prime catalog planning + assembly quality
PROJECT_ID:         none — ws_pp_catalog_audit_lane_f_20260723
SUBSYSTEM:          pearl_pm coordination
AUTHORITY_DOCS:     docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md; CLAUDE.md Bestseller Quality Anti-Drift Doctrine (§ "memory is recall, not enforcement"); docs/agent_brief.txt §14-16
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_f_synthesis/**; docs/PROGRAM_STATE.md (append one new dated section, do not rewrite existing rows); artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (all 6 lane rows → completed)
OUT_OF_SCOPE:       any code file; any content atom; any live marketing/GHL write
PROVENANCE:         research: lane_a_plan_inventory, lane_b_editor_sequencing, lane_c_assembly_readiness, lane_d_marketing_mix, lane_e_ei_v2_gap (all five, merged) | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md | builds_on: pearl_prime_pipeline_audit_20260722 (this whole pack extends it to catalog scale + 3 new axes) | inventory: EXTENDS
BLOCKERS:           gated on all five lane signals
READY_STATUS:       gated

## Prerequisite gate check

Confirm all five exist before writing a single finding:
`lane-a-plan-inventory-merged=<sha>`, `lane-b-editor-sequencing-merged=<sha>`,
`lane-c-assembly-readiness-merged=<sha>`, `lane-d-marketing-mix-merged=<sha>`,
`lane-e-ei-v2-gap-merged=<sha>`. For any lane that shows BLOCKED instead, read its
pushed-branch evidence and handoff, and synthesize from that with an explicit
"Lane X blocked on Y — synthesized from partial evidence" caveat rather than
silently treating it as complete.

## Mission

Produce `artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_f_synthesis/REPORT.md`
structured as direct answers to the operator's own questions (quote each question,
answer it, cite the lane + evidence path):

1. "What's the plan for the US market, across all brands?" → Lane A's inventory,
   condensed to one table + the reconciled true per-brand target (not the 800/
   brand assumption unless Lane A confirmed it).
2. "Is the Pearl_Editor agent getting in the process at the right point? Is the
   contract created and seen through before catalog approval?" → Lane B's verdict.
3. "Is our plan and assembly working — bestseller stuff, cohesive flow, enrichment
   — done, catalog-wide?" → Lane C's rollup numbers (fraction of planned catalog
   at each predicted ceiling) + Lane A/B/07-22-audit context.
4. "Are we making the majority of books to make money, with a spread to help — on
   purpose?" → Lane D's verdict.
5. "Is EI v2 genuinely in the system?" → Lane E's verdict + recommended wiring
   option.
6. **Cross-axis synthesis** (new — not just five separate answers): where do these
   interact? E.g., if Lane B finds content-authority enters only at render time,
   and Lane C finds most of the catalog predicts to "structurally-clear-only,"
   those are the same structural cause seen from two angles — say so explicitly.
   If Lane D finds no documented revenue-mix strategy AND Lane A finds most
   planned volume concentrates in a few personas, is that concentration
   explainable by planning-order accident (per Lane A) rather than deliberate
   strategy (per Lane D) — connect the dots.
7. **Prioritized fix roadmap**: every fix candidate from Lanes A-E, ranked, each
   labeled: acceptance-layer-honest (what layer it would move the system to, not
   "fixes everything"), and whether it's executable-default (a normal next
   engineering lane) or operator-tier (needs a ratified cap entry / Q-gate,
   name the exact Q-ID convention e.g. `Q-CATALOG-AUDIT-01`).
8. **What this pack did NOT cover** (be as honest as the 07-22 audit's own
   "What this turn did NOT cover" section — e.g. locale catalogs beyond en_US,
   any actual render/parity verification, manga/audiobook/music catalog axes).

## PROGRAM_STATE.md update

Append (do not rewrite) a new dated section under the appropriate track, or a new
`### Catalog plan + assembly readiness audit (2026-07-23)` subsection, summarizing
the headline verdicts + linking to this report. Follow the existing glossary
discipline (listing ≠ EPUB; gate-PASS ≠ bestseller). Update the `LAST VERIFIED`
line at the top only if you are the last writer in this session — check for
in-flight collisions first (git fetch immediately before this edit).

## Cap-entry candidates (do not self-ratify)

If Lane B or Lane E surfaced a concrete cap-entry-candidate (e.g., a plan-time
content-authority gate, or an EI v2 wiring-level decision), list them here as
`Q-CATALOG-AUDIT-NN` with a recommended default each — do not add them to
`PEARL_ARCHITECT_STATE.md` yourself; that requires a separate Pearl_Architect
ratification pass.

## DO NOT

- Do not launch before all five lanes are terminal.
- Do not rewrite existing PROGRAM_STATE.md rows — append only.
- Do not claim any book or the catalog is "bestseller" or "100% ready" — use the
  scorecard's four layers throughout, exactly as the 07-22 audit modeled.

## Landing contract

MERGED (branch `agent/pp-catalog-audit-lane-f-20260723`, PR, checks green, squash,
signal `lane-f-synthesis-merged=<sha>`, branch deleted) or BLOCKED with evidence +
handoff + NEXT_ACTION.

## Cleanup ledger

No worktree. Branch deleted after merge. Confirm all 6 `ACTIVE_WORKSTREAMS.tsv`
rows for this pack show terminal status before closing.

## Handoff

`artifacts/coordination/handoffs/pp-catalog-audit-lane_f_2026-07-23.md` — this is
the pack's final handoff; it should be readable standalone by the operator as the
answer to their original ask.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM
TASK:           Lane F — synthesis of Pearl Prime catalog plan + assembly readiness audit
COMMIT_SHA:     <full SHA>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_f_synthesis/REPORT.md; docs/PROGRAM_STATE.md (appended section)
FILES_READ:     <all 5 lane reports + their evidence>
PROVENANCE:     research: lanes A-E (all merged) | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md | builds_on: pearl_prime_pipeline_audit_20260722 | inventory: EXTENDS
STATUS:         <completed / partial / blocked>
HANDOFF_TO:     operator
NEXT_ACTION:    <the single next paste-ready action, if any fix lane should follow>
SIGNAL:         lane-f-synthesis-merged=<sha>
```
