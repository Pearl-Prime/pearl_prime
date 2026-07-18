# Manga July 8 Local Salvage — Reconcile Closeout (2026-07-10)

**Workstream:** `ws_manga_july8_local_salvage_reconcile_20260710`  
**Agent:** Pearl_Dev  
**Authority date:** 2026-07-10  
**Live `origin/main` at audit:** `01bbca9d4ba6edd79b2b83bf7ee0a0ed5b5772f9`  
**July 8 audit anchor:** PR #4861 / `5ee01b44d9` (best-path enforcement — claims, not code authority)  
**Acceptance layer:** `CONFIG-EXISTS` / documentation truth only — **not** EXECUTED-REAL, **not** PROVEN-AT-BAR

> **Verdict:** No July 8 code delta survives as salvageable bytes against July 10 `origin/main`.
> Five of six claims are **already_on_main** or **superseded_by_later_lane**. One claim
> (`assemble_from_bank` → `bubble_render_v2`) never existed as a local/main patch and is
> **explicitly superseded** here: production lettering already uses v2 via `chapter_runner`;
> bank-assembler optional `--bubbles` remains on v1 by current main design. No operator
> deploy script from July 8 exists on disk or in git history — treat as **superseded**.

---

## Discovery report (pre-edit)

| Check | Result |
|---|---|
| Live `origin/main` SHA | `01bbca9d4ba6edd79b2b83bf7ee0a0ed5b5772f9` |
| Working tree | Extremely dirty (shared tree); July 8 claims treated as CLAIMS only |
| Current branch at session start | `agent/ws-manga-true-layered-webtoon-proof-20260710` (unrelated; not used as base) |
| Open-PR overlap on candidate files | **none** (no open PR owns assemble/style_resolution/qwen/crossgenre salvage deltas) |
| SSOT agreement (July 9–10 manga lanes) | `docs/PROGRAM_STATE.md` + `ACTIVE_WORKSTREAMS.tsv` mark completed: `ws_mecha_native_render_dispatch_20260709` (#5482), `ws_mecha_native_human_readability_proof_20260710` (#5486), `ws_manga_prompt_builder_v3_20260710` |
| `operator_deploy_crossgenre_rerender.sh` | **ABSENT** on `origin/main` and local working tree; no git history for path |
| `phoenix_v4/manga/style_resolution.py` | **ABSENT** on `origin/main` and local |
| `assemble_from_bank.py` bubble path on main | still imports `bubble_render` (v1); `bubble_render_v2` used by `chapter_runner` |
| `t2i_flux_dev_h1a` default-task fix | **superseded** — main default is `t2i_qwen_image` |
| Material local diffs vs main on candidates | Local is **behind** main (would delete later-lane content); **not** salvage |

### Candidate file status vs `origin/main`

| Path | On main? | Local material salvage? |
|---|---|---|
| `phoenix_v4/manga/genre_tradition.py` | yes (`resolve_tradition_genre`) | no (local older) |
| `scripts/manga/prompt_authority.py` | yes (v3 Qwen-primary) | no (local older) |
| `scripts/manga/enqueue_crossgenre_real_layers.py` | yes (default `t2i_qwen_image`) | no |
| `scripts/manga/bank_layer_blob_gate.py` | yes (v2 stipple) | no (local older) |
| `scripts/manga/assemble_from_bank.py` | yes (v1 bubbles) | identical to main — no v2 patch |
| `phoenix_v4/manga/style_resolution.py` | **absent** | **absent** |
| `scripts/pearl_star/worker/qwen_manga_worker.py` | yes (real `t2i_qwen_image`) | no (local older) |
| `scripts/pearl_star/install/02_procrastinate.sh` | yes (installs qwen worker) | trivial/non-salvage |
| `scripts/manga/operator_deploy_crossgenre_rerender.sh` | **absent** | **absent** |
| July 8 claim closeouts (`manga_*_closeout_2026-07-08.md`, `OPERATOR_CROSSGENRE_*`) | **absent** | **absent** |

---

## Claim-by-claim disposition matrix

| # | July 8 claim | Disposition | Evidence on `origin/main` |
|---|---|---|---|
| 1 | drawing-tradition backfill wave 2 (`wave_2_deep`) + `resolve_tradition_genre()` wiring | **already_on_main** | `resolve_tradition_genre` in `phoenix_v4/manga/genre_tradition.py`; consumed by `prompt_authority.py`. Live YAML uses `status: top_8_deep` (not the literal label `wave_2_deep`) + `deferred_phase2` stubs. Landed via #5482 / prompt-builder v3 chain. |
| 2 | real Qwen Pearl Star worker | **already_on_main** | `scripts/pearl_star/worker/qwen_manga_worker.py` implements `t2i_qwen_image`; installed by `02_procrastinate.sh`. Merged with `ws_manga_prompt_builder_v3_20260710`. |
| 3 | `assemble_from_bank.py` modernized to use `bubble_render_v2` | **superseded_by_later_lane** | No local/main patch ever landed for assemble→v2. Production chapter lettering already uses `bubble_render_v2` via `phoenix_v4/manga/runner/chapter_runner.py`. Bank assembler optional `--bubbles` remains on v1 — intentional current main design; any future assemble→v2 wire is a **new** lane, not July 8 salvage. |
| 4 | style default removal via `style_resolution.py` | **superseded_by_later_lane** | Module never existed on main. Intent absorbed by prompt-builder v3: `DEFAULT_PANEL_TASK = "t2i_qwen_image"`, tradition/cookbook style slots, explicit ban on silent FLUX-schnell default. HR rules mark `style_resolution.py` as orthogonal / not readability enforcement. |
| 5 | `operator_deploy_crossgenre_rerender.sh` + `OPERATOR_CROSSGENRE_RERENDER_2026-07-08.md` | **superseded_by_later_lane** | Neither file exists in git or working tree. Crossgenre path on main is `enqueue_crossgenre_real_layers.py` + `prompt_authority` + blob gate (mecha native + v3). July 8 operator script claim is stale/dangerous if reconstructed from memory — **do not revive**. |
| 6 | `enqueue_crossgenre_real_layers.py` default `t2i_flux_schnell` → `t2i_flux_dev_h1a` | **superseded_by_later_lane** | Main default is now `t2i_qwen_image` (choices still include `t2i_flux_dev_h1a` / `t2i_flux_schnell`). July 8 h1a fix was an intermediate step absorbed by v3 Qwen-primary. |

**Summary counts:** already_on_main=2 · superseded=4 · survives_locally_and_should_land=0 · blocked_needs_separate_lane=0

---

## Operator command

**July 8 claimed operator deploy script:** `superseded` (file never on main; do not run reconstructed variants).

**Current replacement (on main — dry-run first):**

```bash
PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py --dry-run --series mecha
PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py --series mecha
# default --task is t2i_qwen_image; override only with explicit intent:
#   --task t2i_flux_dev_h1a
```

Post-land: run `bank_layer_blob_gate` — queue COMPLETED + bytes ≥50KB is not usability proof.

**This lane does not re-run Pearl Star renders.**

---

## Landing slices

| Slice | Needed? | Action |
|---|---|---|
| A crossgenre deploy/runbook | no code | superseded banner in this closeout only |
| B style/drawing authority | no code | already on main / superseded by v3 |
| C bank assembler v2 wire | no salvage bytes | superseded (chapter_runner owns v2); optional future lane only |
| D reconciliation artifact | **yes** | this file |

---

## Provenance

```
research:  artifacts/research/MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md;
           artifacts/research/manga_genre_prompting_system_2026-07-10.json;
           artifacts/qa/MANGA_BLOB_PREVENTION_CLOSEOUT_2026-07-10.md;
           PR #4861 / 5ee01b44d9 (July 8 best-path audit anchor — claims only)
documents: docs/PROGRAM_STATE.md; docs/SESSION_UNITY_PROTOCOL.md;
           docs/PEARL_ARCHITECT_STATE.md; specs/AI_MANGA_PIPELINE_SUMMARY.md;
           docs/MANGA_IMPLEMENTATION_OUTLINE.md;
           docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md
builds_on: ws_mecha_native_render_dispatch_20260709 (#5482);
           ws_mecha_native_human_readability_proof_20260710 (#5486);
           ws_manga_prompt_builder_v3_20260710
inventory: EXTENDS documentation truth only; code inventory UNCHANGED (no silent REDUCED)
```

---

## Cleanup ledger

| Item | Action |
|---|---|
| July 8 local claim closeouts (named in brief) | never present — N/A |
| `operator_deploy_crossgenre_rerender.sh` | mark superseded (this doc); do not recreate |
| `style_resolution.py` | mark superseded (this doc); do not invent module |
| Hot coordination TSVs / PROGRAM_STATE | **not touched** (no sole-driver; doc-only reconcile) |
| Workstream `ws_manga_july8_local_salvage_reconcile_20260710` | complete on merge of this artifact; Pearl_PM may append TSV row in serialized pass |
| Shared dirty tree candidate files | left untouched (behind main; not authority) |

---

## CLOSEOUT_RECEIPT

```
AGENT: Pearl_Dev
TASK: ws_manga_july8_local_salvage_reconcile_20260710
STATUS: complete (documentation reconciliation; zero code salvage)
ORIGIN_MAIN_AUDITED: 01bbca9d4ba6edd79b2b83bf7ee0a0ed5b5772f9
BLOCKER: none
```
