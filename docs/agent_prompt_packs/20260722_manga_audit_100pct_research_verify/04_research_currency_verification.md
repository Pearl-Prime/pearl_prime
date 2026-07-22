```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_QA (research-currency auditor) for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_QA
- LANE=manga_research_currency_verify_20260722
- EXECUTION_MODE=local_fallback
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local checkout
- PERSISTENCE_SURFACES=branch/PR/artifact
- RESUME_SURFACE=artifacts/qa/manga_research_currency_audit_2026-07-22.md (new)

READ FIRST:
- docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md (V5.1 — CANONICAL current
  render authority per DOCS_INDEX; the baseline "best available technique"
  claim to verify against)
- artifacts/research/manga_genre_prompting_system_2026-07-10.json (#5488,
  research_sha 12799deabe) — the authority genre_prompt_cookbook.yaml v3
  claims to be built from
- config/manga/genre_prompt_cookbook.yaml (schema_version 1.0, dated
  2026-07-09, `authority: MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10`,
  `research_sha: 12799deabe294baf1d9da00305c2a3d43620d946`)
- config/manga/genre_prompt_cookbook_v2.yaml (dated 2026-05-19 — pre-dates
  the #5488 research by ~7 weeks)
- scripts/manga/cookbook_v2_compose_prompt.py (imports v2 by name — the
  specific question this lane must resolve: is this script reachable from
  any live render/production entry point, or is it dead code?)
- scripts/manga/prompt_authority.py, phoenix_v4/manga/genre_tradition.py
  (the code paths PROGRAM_STATE claims are "Qwen-primary" per the 2026-07-10
  prompt-builder-v3 wave — confirm they read the v3 cookbook, not v2)
- config/manga/drawing_tradition_per_genre.yaml (H_token_mapping per
  base_model — confirm the model choices per genre match what V5.1 and the
  prompt cookbook actually specify as current, not a stale model reference)

LIVE STATE RECONCILIATION:
- `git fetch origin`; this is a point-in-time grep-and-trace audit — re-run
  every grep below against current main, do not reuse any cached result
  from this prompt's authoring.
- Enumerate every manga render/production entry point (grep
  `run_manga_chapter.py`, `run_chapter_production.py`,
  `run_chapter_visual.py`, `queue_panel_renders.py`,
  `assemble_from_bank.py`, and anything under `scripts/pearl_star/worker/`
  that dispatches manga jobs) and trace, for each, which genre-prompt
  config file it actually imports/loads at runtime — not which file it
  mentions in a comment or docstring.

PRE-REQUISITE CHECKS:
- none — this is a read/trace lane, dispatchable immediately.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- every distinct "genre prompting" or "drawing tradition" config file under
  config/manga/, with its authorship date and whether it cites a research
  artifact;
- for `scripts/manga/cookbook_v2_compose_prompt.py` specifically: full
  callsite trace (`grep -rn "cookbook_v2_compose_prompt" .` across
  scripts/, phoenix_v4/, tests/, config/pipeline_registry.yaml, any CI
  workflow) — is it called by anything reachable from a real chapter build,
  or only by its own tests / nothing at all;
- same trace for genre_prompt_cookbook_v2.yaml directly (who reads this
  path string, independent of the compose script);
- same trace for the H_token_mapping base_model choices in
  drawing_tradition_per_genre.yaml vs the model roster actually named in
  MANGA_V5_LAYERED_ARCHITECTURE.md's current (not superseded) architecture
  section — flag any genre block still pointing at a model V5.1 no longer
  treats as primary.

PROVENANCE:
- research: artifacts/research/manga_genre_prompting_system_2026-07-10.json
  (#5488) is the research artifact whose currency you are checking against
  code — do not treat it as something to re-derive, only to verify against.
- documents: docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md,
  docs/DOCS_INDEX.md manga rows (which docs it names CANONICAL vs
  ASPIRATIONAL)
- builds_on: existing config/manga/ files — this lane reads and reports, it
  does not invent new research.
- inventory: UNCHANGED unless Deliverables below require a fix, in which
  case EXTENDS (retire dead code / mark stale config, never silently
  delete without a decommission note).

MISSION:
Determine definitively whether the manga render pipeline's live code path
uses the current research-backed genre-prompting artifact
(genre_prompt_cookbook.yaml / #5488) everywhere, or whether any reachable
production entry point still reads the pre-research
genre_prompt_cookbook_v2.yaml / cookbook_v2_compose_prompt.py — and produce
an honest verdict with a full callsite trace, not an inference from file
dates. Extend the same method to base-model choices (qwen_image vs
flux_schnell vs animagine_xl_4_0) per genre against the V5.1 architecture
doc's current guidance, to confirm no genre is pinned to a model the
research/architecture docs have since superseded.

DELIVERABLES:
- `artifacts/qa/manga_research_currency_audit_2026-07-22.md` — full
  callsite trace results, a clear verdict per file (LIVE / DEAD /
  UNREACHABLE-BUT-IMPORTED-SOMEWHERE / UNCLEAR-see-evidence), and for any
  file found to be genuinely on a live path while reading stale research: a
  concrete, scoped fix recommendation (point it at the v3 cookbook, or
  formally decommission it) — do NOT make the fix yourself in this lane
  unless it is a one-line import-path change with a passing test; if it
  touches render behavior, hand it off as a named follow-on item instead of
  editing production render code inside a verification lane.
- If `scripts/manga/cookbook_v2_compose_prompt.py` is confirmed dead
  (zero reachable callsites from any production/test entry point): add a
  header comment marking it `# STATUS: unwired/legacy — see
  artifacts/qa/manga_research_currency_audit_2026-07-22.md` per the
  unwired-config-as-working CI gate's own convention (`check_manga_wiring.py`
  requires a `status: unwired` marker or non-test consumer) — do not delete
  it without operator sign-off; flag deletion as a separate optional
  follow-on if you're confident it's safe.
- Update `config/manga/genre_prompt_cookbook_v2.yaml` header with a
  `status: unwired` or `superseded_by: genre_prompt_cookbook.yaml` note if
  the trace confirms it has no live consumer — same convention.

SMALLEST SAFE BATCH:
- smoke: trace ONE entry point (run_manga_chapter.py, the canonical chapter
  DAG per DOCS_INDEX) end-to-end to its genre-config import.
- pilot: trace the remaining entry points listed above.
- scale: n/a — this is a single audit document; the "scale" step is only
  the optional header-marker edits, which are small and mechanical.

HANG PREVENTION:
- poll interval: n/a (this lane is grep/read-bound, not long-running-job
  bound) — if any step does require a build/test run over a minute, poll
  every 10 minutes.
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED after three unchanged polls
- max window: 2 hours

TESTS/PROOFS:
- `grep -rn` trace outputs pasted into the audit doc as evidence (exact
  commands + output, not paraphrased)
- if `check_manga_wiring.py` exists and runs, run it and include its output
  as corroborating evidence
- proof root: artifacts/qa/manga_research_currency_audit_2026-07-22.md

DO NOT:
- no gate weakening;
- no stale metrics;
- no fake proof — every LIVE/DEAD verdict must show the grep/trace command
  and its actual output;
- no local-only finish;
- do not delete genre_prompt_cookbook_v2.yaml or cookbook_v2_compose_prompt.py
  outright in this lane — mark/flag only, per the unwired-config convention;
  deletion is an operator call if the file has any ambiguous history.

LANDING CONTRACT:
- MERGED: PR opened (audit doc + any header-marker edits), required checks
  green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, pushed remote branch if useful, handoff
  written.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/manga_research_currency_verify_2026-07-22.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_QA
- LANE: manga_research_currency_verify_20260722
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL:
- PROOF_ROOT:
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
