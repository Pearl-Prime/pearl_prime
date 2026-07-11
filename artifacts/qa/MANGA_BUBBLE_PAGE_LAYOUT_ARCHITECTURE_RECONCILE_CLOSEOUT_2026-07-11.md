# Manga Bubble + Page Layout Architecture Reconcile — Closeout

**Date:** 2026-07-11  
**Agent:** Pearl_Architect  
**Workstream:** `ws_manga_bubble_page_grammar_reconcile_20260711`  
**Project:** `proj_manga_first_ship_20260425`  
**Subsystem:** `manga_pipeline`

| Tag | Value |
|---|---|
| `LANE_STATUS` | `completed` |
| `WORKSTREAM_STATUS` | `in_review` |
| `ACCEPTANCE_LAYER` | `authored candidate` |
| `TERMINAL_STATE` | `PR_OPEN` (recorded at closeout authoring; final head SHA is in PR body / terminal receipt) |

## Identities

| Identity | Value |
|---|---|
| PR | [#5537](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/5537) |
| Branch | `agent/manga-bubble-page-grammar-reconcile-20260711` |
| Verified base | `origin/main` @ `2edff5f3cfbd8dcc028a575e88b720a7091dbe88` |
| `CANDIDATE_CONTENT_SHA` | `582da89b46684a30b0890b3b2b011407e8f15553` |
| `CLOSEOUT_PARENT_SHA` | `582da89b46684a30b0890b3b2b011407e8f15553` |
| Writable remote | `origin` → `https://github.com/Ahjan108/phoenix_omega_v4.8.git` |
| Repository | `Ahjan108/phoenix_omega_v4.8` |

> `FINAL_PR_HEAD_SHA` is **not** required inside this committed artifact; it is recorded in the PR body and terminal `CLOSEOUT_RECEIPT` after the closeout commit is pushed.

## Non-repository research inputs

| Absolute path | SHA-256 | Bytes | Descriptor |
|---|---|---|---|
| `/Users/ahjan/Downloads/deep-research-report.md` | `d54e84faf1dd08056dc24dc30d4c546c2373cda2858543ac1f3c9835547fcec1` | 13459 | Deep research: panel-first bubbles + page-aware correction; reading-path page grammar |
| `/Users/ahjan/phoenix_omega/docs/manga_word_bubbles_page_layouts.txt` | `425f83116c08920e1231faf8ee03ed85429e719e3c7e3ec767bdd742b970c23f` | 120278 | **Untracked / non-repository** genre-by-genre bubble & layout essay under checkout path |
| `/Users/ahjan/.codex/attachments/c0d18864-48cb-49cd-b913-55fce257db6d/pasted-text.txt` | `1f517b8310df9df768e476eb9d67c38541f976dc19ac099bb7891add14187295` | 9528 | Operator architecture critique: soften `+`/measurements/genre; add spreads, graphs, Pass B, JLREQ, SFX, reflow, visual review |

## Tracked research / authority inputs (verified base-branch blobs)

| Repo path | Base blob SHA (`origin/main`) |
|---|---|
| `artifacts/research/webtoon_compositing_lettering_2026-04-25.md` | `fd16ed0062d52a6da4f72f766d45f3974677cc93` |
| `artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` | `55378b7ad4118ab212747a8b0eeb1ee3c0ebe011` |
| `specs/LETTERING_AGENT_SPEC.md` (pre-reconcile) | `d71496f68d082a91918a0726956b8502cdb394c6` |
| `specs/MANGA_LAYOUT_AGENT_SPEC.md` (pre-reconcile) | `d2fedbf11e3ed03803c90524ff68dea690b04a07` |

## Singleton decision

**Edit in place** — no superseding third doctrine doc. Lineage RETAIN (`docs/MANGA_RENDER_LINEAGE_DECISION_2026-05-29.md`) keeps LETTERING + LAYOUT as the post-render text/composition shells. SpiritualTech production fiction demoted to Appendix H in both specs.

**Doctrine status after this PR:** one canonical authority chain for bubble+page grammar (two singletons with explicit interfaces). Remaining split is **implementation lag** (LIVE vs SPECCED/FUTURE), not competing doctrine docs.

## What changed in the canonical specs

### `specs/LETTERING_AGENT_SPEC.md`

- Replaced SpiritualTech agent-as-orchestrator framing with LIVE binding to `bubble_render_v2` / genre YAML / FONT_REGISTRY.
- Added primary sections for D1/D10 two-pass solver, D9 semantics vs appearance, D8 bubble graphs, D12 JLREQ matrix, D13 SFX pipeline, D14 reflow ladder, D5/D17 heuristics, D15 gates.
- Superseded “never consumes images” claim.
- Retained silence/end-hook craft as SPECCED, not falsely LIVE.
- Demoted old schemas/prompts to Appendix H.

### `specs/MANGA_LAYOUT_AGENT_SPEC.md`

- Removed `Status: Production` as live claim; demoted overlay-render / Comic Sans ownership.
- Added format families D4 + `self_help_illustrated` D16 mode gates.
- Added reading-path grammar D2, panel graphs D8, junction ambiguity lint D6, spreads D7, narrative beats D11, Pass B host D1/D10, measurement heuristics D5/D17, gates D15.
- Bound LIVE truth to `page_frame`, `page_grid_templates.yaml`, `webtoon_compose`, series_plan schema.
- Appendix H records historical 600px vs LIVE 60px gutter conflict as non-law.

## Decision traceability (all 17 required)

| ID | Decision | Primary spec | Primary section | Cross-ref | Enforcement class | Impl map IDs |
|---|---|---|---|---|---|---|
| D1 | Panel-first candidates; page-aware final correctness | LETTERING | §3 (Pass A) + interface §3.3 | LAYOUT §3.2 | SPECCED/FUTURE (Pass A partial LIVE) | BUBBLE-001, BUBBLE-005, BUBBLE-006, LAYOUT-001 |
| D2 | Reading-path-driven page grammar | LAYOUT | §4 | LETTERING §4 | SPECCED/FUTURE (bbox LIVE baseline) | LAYOUT-001, LAYOUT-002, LAYOUT-011 |
| D3 | Genre biases; does not outrank override/beat/format/locale | LETTERING | §2 | LAYOUT §2 | LIVE partial (bubbles); page FUTURE | BUBBLE-002, LAYOUT-002 |
| D4 | Webtoon vs print separate families + mode gates | LAYOUT | §1.1–§1.2 | LETTERING §10 | LIVE composers + schema | LAYOUT-003, LAYOUT-004, LAYOUT-007, LAYOUT-009 |
| D5 | Measurements = profile defaults unless technical constraints | LETTERING | §8 | LAYOUT §9 | Doctrine now; config labeling FUTURE | LAYOUT-002, BUBBLE-001 |
| D6 | `+` junctions ambiguity-scored lint | LAYOUT | §6 | HR-F13 | FUTURE (UNENFORCED today) | LAYOUT-013, GATE-001 |
| D7 | Spread composition (recto/verso, turn, binding, DPS) | LAYOUT | §7 | LETTERING §10 | FUTURE (geometry scaffold only LIVE) | SPREAD-001..005 |
| D8 | Panel + bubble reading graphs | LAYOUT §5 (panels); LETTERING §4 (bubbles) | §5 / §4 | mutual | FUTURE | LAYOUT-012, BUBBLE-001 |
| D9 | Bubble semantics ≠ appearance | LETTERING | §5 | — | SPECCED (LIVE fused) | BUBBLE-004 |
| D10 | Two-pass bubble solver | LETTERING | §3 | LAYOUT §3.2 | FUTURE Pass B | BUBBLE-005, BUBBLE-006 |
| D11 | Narrative-beat semantics for layout | LAYOUT | §8 | LETTERING density | LIVE partial (webtoon gutters) | BEAT-001, BEAT-002 |
| D12 | JLREQ-grade typography | LETTERING | §7 | — | LIVE partial; matrix FUTURE | JLREQ-001..003 |
| D13 | SFX own pipeline | LETTERING | §6 | LAYOUT §11.2 | FUTURE (interim stamp LIVE) | SFX-001..005 |
| D14 | Localization reflow ladder | LETTERING | §9 | — | FUTURE (shrink LIVE) | LOCALE-001 |
| D15 | Machine gates vs mandatory visual review | LETTERING §11; LAYOUT §10 | §11 / §10 | mutual | Doctrine; harness FUTURE | GATE-001, GATE-002 |
| D16 | `self_help_illustrated` third family | LAYOUT | §1.3 | LETTERING §10 | CONFIG/routing LIVE; grammar FUTURE | LAYOUT-008, LAYOUT-009 |
| D17 | Research heuristics labeled defaults | LETTERING §8; LAYOUT §9 | §8 / §9 | mutual | Doctrine | RESEARCH-002..004, LAYOUT-002 |

No required decision is marked merely “covered generally.”

## Live file authority summary

| Path | Map status |
|---|---|
| `bubble_render_v2.py` | partial (Pass A) / misleading for SFX |
| `genre_bubble_styles.yaml` | aligned |
| `FONT_REGISTRY.yaml` | aligned |
| `page_frame.py` | partial |
| `page_grid_templates.yaml` | partial |
| `page_compose.py` | aligned |
| `webtoon_compose.py` | aligned (separate family) |
| `panel_layout_templates/*.yaml` | partial (routing) |
| `self_help_illustrated.yaml` | partial (third family boundary) |
| `series_plan.schema.json` | aligned (tighten later for spreads) |
| Spread planner/validator | missing |
| Reading graph / junction validate | missing |
| JLREQ full matrix | missing |
| Independent SFX modules | missing |
| HR July 9 rules | aligned — **not weakened** |

## Local validation (tied to `CANDIDATE_CONTENT_SHA`)

| Check | Result |
|---|---|
| Required paths exist | PASS |
| Implementation map columns + status/action coherence (43 rows) | PASS |
| All 17 decisions have primary homes + cross-refs where required | PASS |
| Spec contradiction scan (render ownership, Comic Sans as law, Status:Production as live) | PASS (only historical/supersession mentions remain) |
| Write scope limited to allowed paths for candidate commit | PASS |
| July 9 HR rules untouched | PASS |
| No runtime/config/test edits | PASS |

## Remote checks

Remote-check observations for `FINAL_PR_HEAD_SHA` are recorded in the PR body and terminal receipt **after** the closeout push, with timestamp. This closeout does not claim pending CI passed.

## Downstream coordination (out of this lane)

- Do **not** update `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` here; if registry rows for the new QA artifacts are desired, schedule a coordination follow-up.
- Do not edit `docs/PROGRAM_STATE.md` / `docs/PEARL_ARCHITECT_STATE.md` in this lane.

## Next clean implementation lane (Pearl_Dev)

**Do not reopen research.** Implement against the map, priority order:

1. `bubble_page_validate.py` Pass B hosted after `page_frame` / `webtoon_compose`.
2. Split SFX out of `bubble_render_v2` into `sfx_plan` / `sfx_render`.
3. `page_reading_graph.py` + junction ambiguity lint (HR-F13 semantics).
4. Spread planner fields + `spread_validate` for print family.
5. JLREQ matrix items beyond vertical+ruby; locale reflow ladder profiles.
6. Explicit `self_help_illustrated` composer/route (not manga grid alias).

## Cleanup ledger

- Probe branch dry-run name was not left on remote (delete failed as already absent).
- Work performed in clean worktree: `/Users/ahjan/phoenix_omega_worktrees/manga-bubble-page-grammar-reconcile-20260711`.
- Dirty primary checkout on unrelated branch was not used for edits.
