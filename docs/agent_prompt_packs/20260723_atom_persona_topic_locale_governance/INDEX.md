# Atom / Persona×Topic×Locale Governance Prompt Pack

## Program

- Goal: stop "are we 100%?" from ever again being answered off a gameable proxy.
  Today `scripts/inventory/atom_coverage_audit.py` reports **100%** CANONICAL
  presence — but only on **13 personas × 15 "core production topics"**; against
  the repo's own full topic list it is **29.8% (221/741)**. Separately, having a
  `CANONICAL.txt` file is not the same as a book being buildable for that cell:
  only **6 personas / 9 persona×topic cells** anywhere in the repo have a real
  anchored `story_atoms` bank that lets `research_fit` actually bind (source:
  `docs/PROGRAM_STATE.md` "Atom coverage (en_US)" section, re-verified this
  session; `docs/agent_prompt_packs/20260721_bestseller_atom_flow/INDEX.md`
  ground-truth section). This is the literal mechanism behind the operator's
  complaint: a coverage tool says 100% against its own narrow proxy list, then a
  real book run discovers "no stories for this persona/topic."
- This pack does **not** re-solve the bestseller-register problem (that's
  `20260721_bestseller_atom_flow`, merged as PR #9, `280597dacf`, 2026-07-21 —
  it already wired `check_research_fit_honesty.py` / `check_book_story_authored.py`
  as the honesty signal for "does this cell actually bind"). This pack **extends**
  that lineage in two directions the operator asked for: (a) a true persona×topic
  requirement matrix for English, at the REAL topic-list size, not the 15-topic
  proxy; (b) the same matrix crossed with every locale in
  `config/localization/locale_registry.yaml`, distinguishing authored-real from
  stub/corrupted/missing (not file-existence, per
  `project_translation_bar_is_stub_contaminated.md`); (c) a durable CI
  registration hook so a new atom type / metadata field can never again go
  ungoverned — porting the exact pattern `scripts/ci/check_manga_wiring.py`
  already proved for manga configs (CLAUDE.md's Manga Vision-Conformance
  Doctrine names this as a gap never ported to books/atoms); (d) one
  single-command report that answers "are we 100%" per cell, per locale, with
  its acceptance layer named — never a bare "100%."
- Source request: operator asked (verbally, transcribed) for "prompts... to
  create a very robust system of atom governance" after repeatedly being told
  "yes we're 100%" and then discovering missing persona/topic stories mid-run;
  same rigor requested for every other language; and a durable rule that any
  future atom/metadata addition that ends up in book prose gets accounted for
  automatically, not manually re-audited.
- Router date: 2026-07-23.
- Live origin/main: fetched fresh this session — tip `f5b9acfcbd` (current
  checked-out branch `agent/bestseller-atom-flow-lanes-20260721` is 146 ahead /
  5 behind this tip; **branch fresh off `origin/main`, never off the current
  checkout**). `docs/PROGRAM_STATE.md`'s recorded "LAST VERIFIED" SHA
  (`a08b8af17b`) is now behind the live fetched tip — treat every number in this
  pack as a snapshot, re-verify before acting (Router Operating Principle §11).
  `gh pr list` succeeded this session (no 403) — the account-suspension blocker
  recorded in the 07-21/07-22 packs has cleared; do not assume it is still
  blocked.
- Prompt count: 4 (01–04) + final audit folded into Lane 04's closeout.
- Master dispatcher: `00_MASTER_DISPATCH_PROMPT.md`

## Confirmed ground truth (do not re-derive — verify freshness, don't re-litigate)

- `scripts/inventory/atom_coverage_audit.py` walks `atoms/<persona>/<topic>/` for
  `CANONICAL.txt` presence only — it cannot see whether `story_atoms/<persona>/
  anchored/<topic>/<engine>/` exists, which is the directory `research_fit`
  actually reads (`phoenix_v4/planning/story_planner.py:254`,
  `build_story_schedule()` ~line 665). A cell can be "100%" by this tool's count
  and still render `research_fit: {}` / `skip_reason: no_story_atoms`.
- `config/source_of_truth/topic_registry.yaml` lists 15 topics (anxiety,
  boundaries, burnout, compassion_fatigue, courage, depression,
  financial_anxiety, financial_stress, grief, imposter_syndrome, overthinking,
  self_worth, sleep_anxiety, social_anxiety, somatic_healing). This is almost
  certainly the source of the tool's "15 core production topics" — it is
  **not** the same list PROGRAM_STATE cites as "57-topic" (that list resolves
  from `atom_coverage_audit.py`'s own fallback chain: `canonical_topics.yaml` →
  `catalog_generation_config.yaml` topics → atoms/ dir scan). Two different
  topic universes are in play under one tool; this is the proxy-narrowing the
  operator is catching. Lane 01 must reconcile which is authoritative, not
  silently keep scoring against the smaller one.
- Only 6 personas have ANY `story_atoms/anchored/` bank today: educators,
  first_responders, gen_z_professionals, healthcare_rns,
  millennial_women_professionals, working_parents — 9 persona×topic cells total
  (`anxiety/overwhelm`, `anxiety/watcher`, `burnout/overwhelm`,
  `financial_anxiety/spiral`, `financial_stress/overwhelm`, plus `courage` added
  for `millennial_women_professionals×false_alarm` by PR #9). Every other
  persona×topic combination in the catalog — including any combination a book
  run might pick — has zero anchored bank, regardless of what
  `atom_coverage_audit.py` reports.
- `scripts/ci/check_manga_wiring.py` is the exact pattern to port: a new
  `config/manga/*.yaml` must have a non-test code consumer, OR declare
  `status: unwired` in its own body, OR sit in a `KNOWN_UNWIRED` allowlist with
  a reason — a new unwired config with none of these cannot merge. No
  equivalent exists for atoms/story_atoms/metadata fields today.
- Translation coverage today (`scripts/ci/report_translation_coverage.py`) counts
  `CANONICAL.txt` file existence per locale — the same file-existence proxy
  problem, one layer down. Confirmed by `artifacts/qa/
  atom_authoring_backlog_20260722.tsv` (650 rows, commit `386bf02bef`, landed
  **yesterday**): rows flagged `EN_ALSO_CORRUPTED` were passing file-existence
  coverage while the English source itself was corrupt, with 203/650 rows
  independently already flagged by ja-JP/zh-CN locale audits. This is a live,
  fresh instance of exactly the "coverage bar is stub-contaminated" failure
  mode the operator described, not a hypothetical.
- Live locale pilot numbers in `docs/PROGRAM_STATE.md` (post-#5497 depth fix):
  ja-JP ~84%, zh-TW ~96% (elsewhere logged 99.87% post-#5693), zh-CN ~43%,
  ko-KR ~6% — **pilot cells only**, file-existence basis, zero locale-native
  sellable EPUBs at catalog scale.
- Three OPEN PRs right now are live instances of this exact gap — do not
  requeue their fixes, cross-reference them:
  - **#211** `docs(zh-TW): first zh-TW book attempt — cell selected, production
    build BLOCKED (EXERCISE-BANK-RESOLUTION-01 English-only classifier)` —
    branch `agent/zhtw-first-book-20260723`.
  - **#208** `fix(zh-cn): author missing gen_x_sandwich compassion_fatigue EN
    source variants` — branch `claude/laughing-hawking-vslpdv` (DRAFT) — an EN
    coverage gap discovered while trying to build a locale, the exact "gate
    said green, run said missing" pattern for a different persona/topic.
  - **#93** `docs(qa): zh-TW register-rewrite lane scope correction (0/1242 —
    bucket is untranslated, not register)` — a coverage tool mis-bucketing
    "never translated" as "register issue," inflating a different metric.
- `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` has **no row** for
  `atom_coverage_audit.py`, `topic_registry.yaml`, or
  `report_translation_coverage.py` today — these are load-bearing canonical
  tools with no reuse-first registry entry. Lane 01 adds the missing rows
  (`edit_not_recreate: YES`) rather than leaving them undocumented.
- Prior lineage, do not duplicate: `20260718_atom_deepening_100pct_rewrite`,
  `20260718_atom_deepening_structure_plan_from_csv`, `20260717_atom_job_deep_audit`,
  `20260721_bestseller_atom_flow` (merged, PR #9), `20260715_pearl_translator_14_locale_100pct`,
  `20260716_pearl_translator_source_stub_unblock`, `20260720_cjk_translation_native_audit`,
  `20260718_translation_real_levers`, `20260721_zh_tw_translation_quality_program`.
  Each lane below must check these packs' closeouts/handoffs at startup and
  stand down on any overlapping in-flight work rather than re-run it.

## Wave Order

- Wave 0: none (research complete above; Lane 01 starts immediately)
- Wave 1: Lane 01 (true EN matrix) — foundation; everything else depends on its
  output schema (field names, 3-state classification, topic-list reconciliation)
- Wave 2 (after Lane 01 lands): Lane 02 (registration CI gate) and Lane 03
  (locale-matrix extension) run in parallel — disjoint files
  (`scripts/ci/check_atom_registration.py` vs `scripts/ci/
  report_translation_coverage.py`)
- Wave 3 (after Lane 01 + Lane 03 land): Lane 04 (single "are we 100%" report +
  claim-honesty gate + PROGRAM_STATE reconciliation)

## Lane Matrix

| Prompt | Agent | Lane | Substrate | Depends on | Output tags | Hot files |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | Pearl_Architect | atom-matrix-true-topics | local_fallback | none | 3-state EN matrix, registry rows, PR/branch | `scripts/inventory/atom_coverage_audit.py`, `config/source_of_truth/topic_registry.yaml`, `artifacts/inventory/atom_coverage_matrix.json`, `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` |
| 02 | Pearl_Architect | ci-atom-registration-gate | github_actions | 01 | new gate, PR/branch | `scripts/ci/check_atom_registration.py` (new), `scripts/run_production_readiness_gates.py`, `.github/workflows/*.yml` |
| 03 | Pearl_Localization | locale-matrix-authored-vs-stub | local_fallback | 01 | per-locale 3-state matrix, PR/branch | `scripts/ci/report_translation_coverage.py`, `config/localization/locale_registry.yaml` (read-only), `artifacts/qa/atom_authoring_backlog_20260722.tsv` (consumed, not edited) |
| 04 | Pearl_Architect | atom-governance-single-report | local_fallback + github_actions | 01, 03 | report script, claim-honesty gate, PROGRAM_STATE update, PR/branch | `scripts/inventory/atom_governance_report.py` (new), `docs/PROGRAM_STATE.md`, `scripts/run_production_readiness_gates.py` |

## Deconfliction

- Open PRs checked this session: `gh pr list --state open --limit 50` succeeded
  (no 403). ~30 open PRs exist; the three named above (#211, #208, #93) directly
  overlap this pack's subject matter — read them, do not duplicate their fixes,
  cite them as live evidence.
- Active workstreams / prior packs: see "prior lineage" list above. Lane 01 in
  particular must confirm PR #9's `check_research_fit_honesty.py` /
  `check_book_story_authored.py` are still on `origin/main` and unmodified by
  any other in-flight PR before wiring them as a signal source.
- Shared files: `scripts/run_production_readiness_gates.py` is a hot file also
  touched by manga and bestseller-atom-flow lanes — diff-check before editing,
  add a new numbered gate, never renumber/reorder existing gates.
  `docs/PROGRAM_STATE.md` is a hot coordination file — Lane 04 is the ONLY lane
  in this pack authorized to write to it, and only after Lane 01+03 have
  landed; serialize against any other session editing it concurrently.
- One actor per resource: if another session is mid-edit on
  `atom_coverage_audit.py` or `report_translation_coverage.py` when a lane
  starts, that lane posts a STAND DOWN claim comment and waits/re-routes rather
  than parallel-editing.

## Evidence Requirements

- Tests: `pytest` for every new/extended check script; `python3
  scripts/run_production_readiness_gates.py` full run after each gate wiring
  with no unrelated regressions.
- Proof roots: `artifacts/inventory/atom_coverage_matrix.json` (Lane 01, 3-state
  schema), `artifacts/qa/locale_atom_governance_<date>/` (Lane 03 output),
  `artifacts/qa/atom_governance_report_<date>/` (Lane 04 output) — each must be
  a real generated artifact, not a hand-written summary.
- Mutation test (router §14): Lane 02's gate must be proven RED under a
  deliberately unregistered new atom type, then the fix applied, then GREEN —
  a gate that stays green under mutation is not accepted.
- Operator approvals: whether Lane 02's registration gate is advisory (WARN,
  default) or a hard merge-block is an operator-tier threshold call — ship
  advisory by default (mirrors the 07-21 pack's precedent for
  `check_research_fit_honesty.py`), surface the hard-block option to the
  operator, do not decide it silently.
- Final audit (Lane 04's closeout): re-run the single "are we 100%" report
  against at least one EN cell known-anchored (e.g.
  `millennial_women_professionals × anxiety × overwhelm`) and one EN cell
  known-missing (e.g. any cell outside the 9 anchored ones), plus one locale
  cell known-stub-contaminated (an EN_ALSO_CORRUPTED row from the 650-row
  backlog) — confirm the report labels all three correctly, not just that it
  runs without error.

## Cleanup Requirements

Every lane reports: worktree removed or HOLD path/reason; local branch deleted
or HOLD reason; remote branch deleted after merge or HOLD reason; scratch files
removed or committed as proof; background jobs stopped or declared; handoff
file path.

## Final Status

- Status: pack authored, not yet dispatched.
- Blockers: none known — GitHub access confirmed working this session; verify
  again at dispatch time regardless (Router Operating Principle §11).
- Next action: paste `00_MASTER_DISPATCH_PROMPT.md` into the lead agent, or run
  each lane prompt directly in dependency order (01, then 02+03 parallel, then
  04).
