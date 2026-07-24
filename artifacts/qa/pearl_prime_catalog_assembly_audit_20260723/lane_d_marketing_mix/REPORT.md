# Lane D — Marketing / Revenue-Mix Audit of the Planned en_US Catalog

**Date:** 2026-07-23
**Agent:** Pearl_Marketing (Lane D, Pearl Prime Catalog Plan + Assembly Readiness Audit)
**Scope:** Read-only audit. No marketing copy, campaign content, or GHL config was written or modified.

## Operator's question (verbatim intent)

"Are we making the majority of books to make money on the market, while still keeping a spread to help people — is that happening on purpose, by design, or by accident?"

## Bottom line

A real, well-researched revenue/demand strategy document exists
(`docs/GLOBAL_PERSONA_MARKETING_PLAN.md`). It is **not wired to catalog-generation
code** — zero script references to it, its title list, or the one demand-weighting
file built to operationalize it (`config/catalog_planning/market_topic_fit.yaml`,
which documents its own non-wiring in its own header). The catalog that actually
gets planned is shaped by a **teacher-voice-fit scorer** (craft/register match, not
revenue) and by **production sequencing** (which persona/brand combinations got
built out first), not by any revenue-vs-access split the marketing plan defines.
The mix is real, but it's an accident of build order, not a designed allocation.

## 1. The actual planned mix

`artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv` (1,478 rows
— active build queue, each row has readiness_status/composite score/pipeline
route):

| Persona | Count | ready | blocked_arc_missing |
|---|---|---|---|
| millennial_women_professionals | 150 | 128 | 22 |
| tech_finance_burnout | 143 | 121 | 22 |
| gen_z_professionals | 140 | 118 | 22 |
| healthcare_rns | 140 | 130 | 10 |
| educators | 136 | 11 | 125 |
| working_parents | 133 | 114 | 19 |
| first_responders | 129 | 112 | 17 |
| gen_x_sandwich | 127 | 117 | 10 |
| corporate_managers | 123 | 103 | 20 |
| entrepreneurs | 117 | 98 | 19 |
| gen_z_student | 96 | 33 | 63 |
| gen_alpha_students | 44 | 42 | 2 |

Topics: `burnout` (125) and `self_worth` (124) lead; `financial_anxiety`/
`financial_stress` (34 each) trail ~3.5x. This slice is fairly even (44-150) —
nothing suggests deliberate revenue loading. `educators`/`gen_z_student` stand out
for being heavily `blocked_arc_missing` — a production gap, not a strategic
downweight.

`config/source_of_truth/book_plans_en_us/` (32,401 files — the full
mechanically-generated listing scaffold, ~800/brand):

| Persona | Count |
|---|---|
| corporate_managers | 3,743 |
| gen_x_sandwich | 3,734 |
| tech_finance_burnout | 3,723 |
| working_parents | 3,711 |
| millennial_women_professionals | 3,709 |
| gen_z_professionals | 3,707 |
| entrepreneurs | 3,696 |
| healthcare_rns | 3,685 |
| gen_alpha_students | 2,425 |
| **first_responders** | **182** |
| gen_z_student | 82 |
| nyc_executives | 2 |
| educators | 2 |

**Sharpest finding:** `first_responders` — which `GLOBAL_PERSONA_MARKETING_PLAN.md`
ranks as market gap **#4** ("near-zero supply... Empty" supply level) and scores
24/25 (tied for the single highest S6 score in the whole plan) — is represented at
**182 files vs. ~3,700 for core personas, roughly 5% of their density.** If the
marketing plan's stated priorities drove this catalog, first_responders should be
over-represented, not 20x under-represented. Checking brand coverage: only 14 of 39
brands even have a first_responders tuple, each with 2-7 variants, vs. ~20+ tuples
x 800 files for core personas. Same pattern for `gen_z_student` (82),
`nyc_executives`/`educators` (2 each) — all added to
`teacher_topic_persona_scores.yaml` in a "P0/P1 backfill 2026-04-29" dated well
after the original persona roster's brand buildout, and never got the full
fan-out.

## 2. Is there a documented strategy behind the mix?

**Yes, a real one exists — but it doesn't reach the code.**

`docs/GLOBAL_PERSONA_MARKETING_PLAN.md` is genuinely thorough: TAM figures ($53B
self-improvement + $19.35B manga), a ranked top-10 market-gap table with
addressable size and supply level, and — most relevant — an **S6 Content
Prioritization matrix** scoring 30 candidate titles on 5 dimensions including an
explicit **Revenue Potential (1-5)** column. This is exactly the artifact the
operator's question is asking about.

But confirmed by direct grep across `scripts/`, `phoenix_v4/`, `config/`: **zero
references** to the filename `GLOBAL_PERSONA_MARKETING_PLAN`, or to any of the S6
table's specific titles ("Overthinking Cure for Professional Women," "The First
Responder's Body," "996 Detox").

The closest operationalized version is
`config/catalog_planning/market_topic_fit.yaml` — a well-built per-market x
per-topic demand-fit registry with fit scores, tiers, and a `hero_threshold`. **It
documents its own non-wiring in its own header:**

> "TODAY (the problem): ... `description_templates.yaml::market_topic_weights` ...
> is LOADED-AND-UNUSED in `scripts/catalog/generate_full_catalog.py` ... every
> topic is effectively AVAILABLE EVERYWHERE at neutral weight. There is no
> per-market topic gate at all. ... Wiring it ... is a CODE change, governed
> separately — this is the data SSOT."

It's also US-neutral anyway (`us:` entry: "No suppression; no net-new local topics
needed"), so it wouldn't explain the persona skew even if wired.

**What the code actually uses:**
`scripts/catalog/generate_pearl_prime_book_script_catalog.py::composite_score()`
reads `config/catalog_planning/teacher_topic_persona_scores.yaml`, which is
explicit: *"Teacher x topic and teacher x persona fit scores... scores guide
volume and format."* This is a **narrative/voice-fit signal**, not revenue or
demand — no `revenue`, `monetiz*`, `TAM`, or `market size` term anywhere in that
file or the scoring path.

**Conclusion:** the revenue-vs-access mix is not steered by any strategy code
actually reads. It's emergent from (a) original teacher/brand roster timing and
(b) voice-fit scoring. The marketing plan is real research that was never
connected to a lever.

## 3. What would "on purpose" require?

**Option A (recommended) — wire a revenue-priority signal, scoped small:** Add a
`revenue_weight` field (seeded from S6's Revenue Potential column) parallel to the
existing voice-fit scores in `teacher_topic_persona_scores.yaml`; feed it into
`composite_score()` as a third term; actually wire `market_topic_fit.yaml` per its
own documented contract; add an explicit **access-floor quota** (e.g., "no persona
drops below N% of core-persona density regardless of revenue score") so a persona
like first_responders becomes a *deliberate* commitment rather than a backfill
accident. This is genuinely bounded — one new/extended YAML, one function
signature change.

**Option B — treat this as operator-tier, not planner input:** Auto-weighting
toward "predicted revenue" risks the same drift this repo already warns against
elsewhere (plan not equal to structural proxy, register-PASS not equal to
bestseller) — `market_topic_fit.yaml`'s own confidence tags show much of even the
unwired data is inferred, not measured. Under this view, revenue allocation should
be a manual, operator-ratified quota reviewed against actual sales, not baked into
an automated score.

This audit leans Option A (the strategy doc already exists and was clearly meant
to inform selection — leaving it disconnected is the real accident), but any
weight table should carry the same `high`/`med`/`low` confidence tagging
`market_topic_fit.yaml` uses and get operator ratification before going live.

## 4. The "spread to help" half

**No evidence of a deliberate access/help allocation exists.**

- Free vs. paid is a **technical gate**, not a persona/topic strategy: per
  `docs/PROGRAM_STATE.md`'s GHL row, "paid items gate on real attached asset...
  free items on asset-exists... free-content-first — paid auto-promotes on
  attach." This is purely "does a file exist yet," not a revenue-mix decision —
  the two claims must stay separate.
- Freebies attach to **every** book uniformly
  (`specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md`) — selection logic governs *which
  exercise* per persona style (structured vs. interactive), not *whether* a book
  gets an access track.
- The one persona that reads as genuinely under-monetized — first_responders — is
  under-*built*, not deliberately free/cheap; nothing marks it as an intentional
  lower-revenue access play.

**Quantification:** not possible from the data — no field in the catalog schema
encodes "this exists for access reasons at accepted lower revenue." The honest
finding is negative: not "a small deliberate spread exists" but "the mechanism to
declare one doesn't exist yet."

## Answer to the operator's question

**Accident, not design — but not for lack of thinking.** Real research exists and
explicitly scores revenue potential and flags first_responders as exactly the
underserved-but-high-opportunity case the operator is asking about. That research
was never wired into the code that builds the catalog. What ships is shaped by
production sequencing — which personas got a full brand buildout early vs. bolted
on later at ~5% density. There's also no mechanism, deliberate or accidental,
marking any part of the catalog "built for access despite lower revenue."

## What this lane did NOT cover

- Locale catalogs beyond en_US.
- Any actual render/parity verification.
- Manga/audiobook/music catalog axes.
- Whether Option A's proposed `revenue_weight` wiring would itself produce a
  correct or safe revenue signal (its inputs — the S6 table — are marketing
  research estimates, not measured sales data).

## Evidence

- `evidence/en_us_catalog_csv_distribution.txt` — persona x readiness_status counts
  from `en_US_catalog.csv` (1,478 rows).
- `evidence/book_plans_en_us_distribution.txt` — persona counts from
  `config/source_of_truth/book_plans_en_us/` (32,401 files).

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Marketing
TASK:           Lane D — marketing / revenue-mix audit of the planned catalog
COMMIT_SHA:     <filled in by dispatcher at commit time>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_d_marketing_mix/REPORT.md + evidence/
FILES_READ:     docs/GLOBAL_PERSONA_MARKETING_PLAN.md (full); docs/FREEBIE_MARKETING_PLAN.md (full); specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md (grepped, relevant sections); config/catalog_planning/market_topic_fit.yaml (full); config/catalog_planning/capacity_constraints.yaml (full); config/catalog_planning/teacher_topic_persona_scores.yaml (relevant sections); phoenix_v4/planning/catalog_planner.py (relevant sections); docs/PROGRAM_STATE.md (GHL row); artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv (all 1,478 rows, programmatic); config/source_of_truth/book_plans_en_us/ (all 32,401 filenames, programmatic); scripts/catalog/generate_pearl_prime_book_script_catalog.py (composite_score, relevant sections)
PROVENANCE:     research: NONE beyond existing marketing plan docs (absence-of-strategy-in-code IS the finding) | documents: GLOBAL_PERSONA_MARKETING_PLAN.md, FREEBIE_MARKETING_PLAN.md, market_topic_fit.yaml, PROGRAM_STATE.md | builds_on: existing en_US_catalog.csv + book_plans_en_us/ + PROGRAM_STATE.md GHL row as evidence, no new funnel | inventory: EXTENDS (read-only, no writes to inventory)
STATUS:         completed
HANDOFF_TO:     Lane F (synthesis)
NEXT_ACTION:    Section 3 Option A is a real, scoped follow-up: wire GLOBAL_PERSONA_MARKETING_PLAN.md's revenue-potential signal + market_topic_fit.yaml into composite_score(), with an explicit access-floor quota for first_responders/gen_z_student. Needs operator ratification before implementation (see Section 3).
SIGNAL:         lane-d-marketing-mix-merged=<sha>
```
