EXECUTE

You are Pearl_Prime, running Lane A of the Pearl Prime Catalog Plan + Assembly
Readiness Audit: **catalog plan inventory, en_US market, all brands.** This is a
read-only discovery + inventory lane. Do not summarize state and stop, do not
produce a plan-of-work and stop — the turn ends only when your PR is merged (or
BLOCKED with evidence and a pushed branch). Do not assemble, render, or build any
book. Do not stop at "here's what I found in the first three brands I checked" —
cover all brands or explicitly enumerate which you could not reach and why.

STARTUP_RECEIPT
AGENT:              Pearl_Prime
TASK:               Inventory the true en_US catalog PLAN (not listings, not EPUBs) across every brand — what's actually planned, how planning works mechanically, and where/whether a bestseller contract is captured at plan time
PROJECT_ID:         none — new audit lane; log as ws_pp_catalog_audit_lane_a_20260723 in ACTIVE_WORKSTREAMS.tsv on start
SUBSYSTEM:          core_pipeline; pearl_prime; catalog_planning
AUTHORITY_DOCS:     docs/PROGRAM_STATE.md; docs/PEARL_ARCHITECT_STATE.md (CATALOG-800-PER-BRAND-01, BESTSELLER-INJECTIONS-MANDATORY-01, PEARL-EDITOR-UPSTREAM-01, TEMPLATE-UNIVERSAL-01); artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/**
OUT_OF_SCOPE:       config/source_of_truth/** (read-only — do not edit plan YAMLs); phoenix_v4/planning/** (read-only — do not edit code); any render/assembly invocation
PROVENANCE:         research: artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md §3.2-3.3 (bank-vs-consumed distinction — carry this discipline into plan inventory) | documents: docs/PEARL_ARCHITECT_STATE.md CATALOG-800-PER-BRAND-01 ("800 high-confidence configs is system-wide total, NOT per-brand" — verify this against what you find; the operator's framing assumes literal 800/brand, reconcile honestly) | builds_on: existing catalog_planner.py / generate_catalog.py pipeline (do not fork a parallel inventory script — read the real one) | inventory: EXTENDS (read-only report; zero code touched)
BLOCKERS:           none known; re-verify live
READY_STATUS:       ready

## Live-state reconciliation (do first, before any finding)

`git fetch origin`; re-derive current `origin/main` tip — this prompt's authoring
anchor was `244955eaa01ddd9093001d184b41ba71e2a84a2b` (2026-07-23), that may already
be behind. Do not trust any number in this prompt as current; re-derive every count
live.

## DISCOVERY REPORT (required before writing findings)

1. What generates a catalog plan mechanically? You already have candidate entry
   points from prior discovery — verify and trace the real one(s):
   `scripts/generate_catalog.py`, `phoenix_v4/planning/catalog_planner.py`,
   `scripts/catalog/gen_brand_catalog_plan_csv.py`,
   `scripts/catalog/catalog_plan_csv_to_plan_yaml.py`. Which is canonical/current
   vs legacy? Read `docs/DOCS_INDEX.md` and `SUBSYSTEM_AUTHORITY_MAP.tsv`'s
   `pearl_prime` row for the authority doc, and read that doc.
2. Where do the actual PLAN artifacts live for en_US? Confirmed location:
   `config/source_of_truth/book_plans_en_us/` (40 top-level entries found at
   authoring time — re-verify). What does one plan file actually contain (fields:
   persona, topic, engine, format/chapter-count tier, teacher assignment, thesis/
   positioning, target reader promise)? Read 3-5 representative plan YAMLs in full.
3. What is the full brand roster for en_US? `config/brand_registry.yaml` (verify
   its real shape — a `git show` at authoring time returned a top-level dict with
   only 6 keys, which does NOT match "26 brands + Waystream" from PROGRAM_STATE —
   resolve this discrepancy; the brands may be nested under one of those 6 keys,
   or brand_registry.yaml may not be the catalog-brand list at all. Cross-check
   `config/manga/canonical_brand_list.yaml` if that's book-relevant, and
   `artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv`).
4. What is each brand's actual TARGET plan volume? The operator's framing is
   "800 books per brand × 37 brands." Live docs say something more nuanced:
   Waystream = 800 distinct titles (its own brand); `CATALOG-800-PER-BRAND-01` cap
   says 800 is a **system-wide** total, not per-brand; PROGRAM_STATE cites
   "1,519 listings across 26 brands + Waystream(800)" and separately "12,138
   plannable" post arc-seeding. Reconcile these numbers against what you actually
   count on disk — do not just repeat one of them. State the true current
   per-brand target (or "no per-brand target exists, only a system-wide figure")
   as a finding, not an assumption.

## Mission

Produce `artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/REPORT.md`
answering, with evidence paths for every claim:

1. **Inventory table**: brand × count-of-planned-books (en_US) × count with a
   distinct thesis/positioning field populated at plan time × count that are
   "listing only" (title/subtitle/description but no persona×topic×engine cell
   resolved) vs "plannable" (arc + listing exist) vs "spine-buildable" (passes
   tuple-viability preflight — cite `check_tuple_viability` / the 4-cell rebuild
   pattern from PROGRAM_STATE if you can run it read-only against a sample; do NOT
   render).
2. **Does a plan artifact capture a bestseller contract at plan time?** Concretely:
   for the plan YAMLs you read in step 2 of discovery, is there a field that
   states what the book promises the reader / its market thesis / its emotional
   arc target — BEFORE the book enters the render queue? Or is "thesis" purely a
   render-time lookup (`config/planning/chapter_thesis_bank.yaml`, keyed
   `intent→engine`, per the 07-22 audit §2.2) that the plan artifact has no
   awareness of? This is the load-bearing finding for Lane B and Lane F — be
   precise and cite line numbers/file paths.
3. **Per-brand plan-volume reality vs the operator's 800/brand assumption** — the
   reconciled number from discovery step 4, brand by brand, with a one-line
   "why" for any brand that's far from 800 (e.g. never seeded, arc-limited,
   deliberately smaller).
4. **Sample size discipline**: read every brand's plan directory listing (cheap —
   just `find`/`ls`/count), but only deep-read 3-5 representative plan YAMLs per
   distinct brand *archetype* (not all 26-40) for the thesis-field question — name
   which brands you deep-read and why they're representative, and which you only
   counted.

## Tests / proofs

- `find config/source_of_truth/book_plans_en_us -maxdepth 1 -type d | wc -l` (or
  equivalent) reproduced in evidence.
- Any script you run (`atom_coverage_audit.py` etc., if used for cross-reference)
  must be run in its existing read-only/report mode — capture stdout to
  `evidence/`.

## DO NOT

- Do not invoke `run_pipeline.py`, `build_epub.py`, or any renderer. <!-- CI-ALLOWLIST: legacy-registry-ok — prose prohibition, not a production invocation -->
- Do not edit any file under `config/source_of_truth/`.
- Do not claim "N books are bestseller-ready" from plan inventory alone — plan
  existence is at most `listing`/`plannable`, never higher on the acceptance
  taxonomy.

## Landing contract

MERGED: branch `agent/pp-catalog-audit-lane-a-20260723` from clean `origin/main`,
PR opened, checks green, squash-merged, signal
`lane-a-plan-inventory-merged=<sha>` emitted, branch deleted. Or BLOCKED with
evidence pushed + handoff + NEXT_ACTION.

## Cleanup ledger

No worktree created (docs/qa-only write scope). Local branch deleted after merge.

## Handoff

`artifacts/coordination/handoffs/pp-catalog-audit-lane_a_2026-07-23.md`

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Prime
TASK:           Lane A — catalog plan inventory (en_US, all brands)
COMMIT_SHA:     <full SHA>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/REPORT.md + evidence/
FILES_READ:     <authority docs + plan YAMLs actually opened>
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722 | documents: CATALOG-800-PER-BRAND-01, PEARL-EDITOR-UPSTREAM-01, BESTSELLER-INJECTIONS-MANDATORY-01 | builds_on: catalog_planner.py / generate_catalog.py (whichever verified canonical) | inventory: EXTENDS
STATUS:         <completed / partial / blocked>
HANDOFF_TO:     Lane C (assembly-readiness prediction) + Lane F (synthesis)
NEXT_ACTION:    <specific>
SIGNAL:         lane-a-plan-inventory-merged=<sha>
```
