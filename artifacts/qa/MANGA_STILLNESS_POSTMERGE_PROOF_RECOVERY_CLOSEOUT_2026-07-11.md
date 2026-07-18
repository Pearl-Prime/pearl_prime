# MANGA STILLNESS POST-MERGE PROOF RECOVERY CLOSEOUT — 2026-07-11

**Workstream:** `ws_stillness_postmerge_proof_recovery_20260711`  
**Agent:** Pearl_Dev  
**Live `origin/main` audited:** `1f4c3155d83f63042611b6598e0b01d26c9a4427` (session start also saw `2236c03a23f04f2689ef8c0fdb0f1ebec4f98df2` pre-#5525; branch base = post-#5525 tip)  
**July 8 salvage authority:** MERGED `#5524` / `210f5e73c4` (`ws_manga_july8_local_salvage_reconcile_20260710`) — disposition: zero code salvage; docs truth only  
**Acceptance layer reached:** RESEARCHED / audited recovery — **not** EXECUTED-REAL, **not** system working, **not** PROVEN-AT-BAR

> **Verdict:** **BLOCKED.** Honest bank-path stillness post-merge proof cannot run.  
> Local discovery **updated** the 2026-07-10 blocked closeout: bank `v4_render_cache` L0/L2 hash-named PNGs are now **materialized REAL** locally (not LFS pointers), and four semantic-gap filenames exist as large RGB files — but those four **fail `bank_layer_blob_gate`** (ghost/blob plates, not character cutouts) and must **not** be promoted as bank REAL. Validator modules remain **absent** from `origin/main` and all salvage surfaces.

---

## STARTUP / pre-requisite checks

| Check | Result |
|-------|--------|
| Live `origin/main` | `1f4c3155d83f63042611b6598e0b01d26c9a4427` |
| `docs/PROGRAM_STATE.md` next manga blocker | **yes** — "stillness post-merge proof re-run (local-only artifacts must not be reported as landed)" |
| Open-PR overlap on stillness bank / validators / proof packet | **none** (open "stillness" hits are catalog skeleton batches only) |
| `ws_manga_july8_local_salvage_reconcile_20260710` | **merged** `#5524` — treat as authority; no July 8 code delta to revive |
| Hot coordination files touched | **no** (no sole-driver milestone land) |

---

## Mandated discovery matrix (pre-edit)

| Item | Live state 2026-07-11 |
|------|------------------------|
| `scripts/manga/panel_planning_rules.py` on `origin/main` | **ABSENT** (also absent locally; **never** in `git log --all`) |
| `scripts/manga/validate_chapter_composition_grammar.py` on `origin/main` | **ABSENT** (also absent locally; never in history) |
| `scripts/manga/annotate_l2_composition_legal.py` | **ABSENT** main + local + history |
| `scripts/manga/generate_assembly_manifest.py` | **present** main+local — **import fails** (`ModuleNotFoundError: panel_planning_rules`) |
| `scripts/manga/assemble_from_bank.py` | **present** main+local — module imports; `load_manifest()` **hard-fails** missing validators |
| Continuity manifest | **present** main+local: `.../assembly_manifests/ep_001_from_continuity.yaml` (35 panels) |
| `ep001_008` binding | L2 → `.../L2/L2_seated_kitchen_knees_up_v1_alpha.png` + L0 `L0_2b9283d4c387.png` |
| `ep001_013` binding | L2 → `.../L2/L2_full_figure_kitchen_standing_v1_alpha.png` + L0 `L0_2b9283d4c387.png` |
| Room-capable composition sidecars on main | **yes** (`*.composition.json` for seated + full_figure; `room_capable: true`) |
| Hash-named `v4_render_cache/ep_001` L0/L2 PNGs locally | **REAL** (L0: 6 PNG magic; L2: 46 PNG magic; room L0 `L0_2b9283d4c387.png` = 1,935,875 bytes) — July 10 "132-byte pointer" claim **superseded for local materialization** |
| Same hash-named PNGs on `origin/main` | LFS **pointers** in git (expected); objects smudge locally |
| Four semantic-gap L2 paths on `origin/main` | **ABSENT** (PNG binaries never landed; sidecars only for room pair) |
| Four semantic-gap L2 paths locally | **files exist** as RGB ≥1.2MB each — see byte/blob proof below |
| `assembly_manifests/ep_001_bank_gaps.json` | on main+local with `layers_missing: 0` — **stale vs continuity bindings** (gap filenames unbound as REAL cutouts) |
| Local `assembled/ep_001_postmerge_proof_2026-07-10/` | 29/35 real PNGs — **not** authority; incomplete; must not be reported as landed proof |
| Honest packet root `artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/` | **ABSENT** (not built) |

### Exact byte / blob proof — previously "missing" semantic gap L2s

| File | Local bytes | Mode | On `origin/main` | `bank_layer_blob_gate.is_blob_png` | Notes |
|------|------------:|------|------------------|------------------------------------|-------|
| `L2_clean_bust_calm_v2_alpha.png` | 1,420,281 | RGB | ABSENT | **True** (FAIL `small_edge=1.29<3.0`) | ghost plate; not cutout |
| `L2_hands_wrapping_cup_clean_v2_alpha.png` | 1,337,666 | RGB | ABSENT | **True** (FAIL `small_edge=0.45<3.0`) | ghost plate |
| `L2_seated_kitchen_knees_up_v1_alpha.png` | 1,270,030 | RGB | ABSENT | **True** (FAIL `small_edge=0.32<3.0`) | room-capable binding target; blob |
| `L2_full_figure_kitchen_standing_v1_alpha.png` | 1,245,446 | RGB | ABSENT | **True** (FAIL `small_edge=0.32<3.0`) | room-capable binding target; blob |
| Reference good bank cutout `L2_054c9bbfde93_alpha.png` | 1,770,276 | RGBA | LFS on main | **False** (PASS) | opaque_frac≈0.57 |

**Rembg promotion attempt (canonical `render_v4_episode.apply_cutout`, isnet-general-use):** opaque_frac ≈ 0 for all four — cutouts unusable. **Do not land** these four files as bank REAL.

---

## Exact blocker (one)

```
BLOCKED: scripts/manga/panel_planning_rules.py and scripts/manga/validate_chapter_composition_grammar.py are absent from origin/main and every local salvage surface (git history empty for both paths); scripts/manga/annotate_l2_composition_legal.py likewise absent. generate_assembly_manifest cannot import; assemble_from_bank.load_manifest hard-fails. Concurrent asset bar: the four local semantic-gap L2 PNGs bound by ep_001_from_continuity.yaml (incl. room-capable ep001_008 / ep001_013) are blob-gate FAIL RGB ghost plates — not bank-legal RGBA cutouts — and must not be promoted.
```

Missing module paths (exact):

1. `scripts/manga/panel_planning_rules.py`
2. `scripts/manga/validate_chapter_composition_grammar.py`
3. `scripts/manga/annotate_l2_composition_legal.py` (mandated annotate step)

---

## What was NOT done (by design)

- No fake validator stubs
- No `composed_v4_qwen` proof path
- No promotion of blob-FAIL gap PNGs into the bank
- No re-render wave (operator/GPU lane; out of scope once blob bar failed on salvage bytes)
- No edits to `ACTIVE_WORKSTREAMS.tsv` / `PROGRAM_STATE.md` / other hot coordination files

---

## Provenance

```
research:  artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md;
           artifacts/research/MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md;
           artifacts/qa/MANGA_BLOB_PREVENTION_CLOSEOUT_2026-07-10.md
documents: docs/PROGRAM_STATE.md; docs/SESSION_UNITY_PROTOCOL.md;
           docs/PEARL_ARCHITECT_STATE.md; specs/AI_MANGA_PIPELINE_SUMMARY.md;
           docs/MANGA_IMPLEMENTATION_OUTLINE.md;
           docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md
builds_on: ws_manga_human_readability_rules_20260709;
           ws_manga_prompt_builder_v3_20260710;
           ws_mecha_native_human_readability_proof_20260710;
           ws_manga_july8_local_salvage_reconcile_20260710 (#5524)
inventory: EXTENDS stillness proof audit truth only; bank inventory UNCHANGED
           (blob gap PNGs explicitly NOT promoted)
```

---

## Required tags

```
manga-stillness-postmerge-recovery=blocked
manga-stillness-postmerge-manifest=artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml
manga-stillness-postmerge-assembly=blocked
manga-stillness-postmerge-packet-root=blocked
manga-stillness-postmerge-packet-html=blocked
manga-stillness-postmerge-contact-sheet=blocked
manga-stillness-postmerge-room-proof=blocked
manga-stillness-postmerge-closeout=artifacts/qa/MANGA_STILLNESS_POSTMERGE_PROOF_RECOVERY_CLOSEOUT_2026-07-11.md
manga-stillness-postmerge-blocker=scripts/manga/panel_planning_rules.py + scripts/manga/validate_chapter_composition_grammar.py (+ annotate_l2_composition_legal.py) absent on origin/main/history; four local semantic-gap L2 PNGs blob-gate FAIL (not bank-legal cutouts for ep001_008/ep001_013)
```

---

## Exact next action (if blocked)

1. Land **real** canonical modules (not stubs): `panel_planning_rules.py`, `validate_chapter_composition_grammar.py`, `annotate_l2_composition_legal.py` — restore from the human-readability rules implementation lane or re-author to the GOVERNED contracts in `MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md`.
2. Re-render (Pearl Star / RAP) four semantic-gap L2s to **blob-gate PASS** RGBA cutouts with usable opaque coverage; replace local ghost plates; keep room-capable sidecars.
3. Then: `annotate_l2_composition_legal.py` → `generate_assembly_manifest.py` → `assemble_from_bank.py` → honest packet under `artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/`.

---

## Cleanup ledger

| Item | Action |
|------|--------|
| Local blob-FAIL gap RGB PNGs | left untracked; **not** staged |
| Local incomplete `assembled/ep_001_postmerge_proof_2026-07-10` | left local-only; not authority |
| `/tmp/stillness_gap_cutouts_20260711` rembg experiments | disposable scratch |
| Hot coordination TSVs / PROGRAM_STATE | untouched |
| This closeout | land via PR |

---

## CLOSEOUT_RECEIPT

```
AGENT: Pearl_Dev
TASK: ws_stillness_postmerge_proof_recovery_20260711
STATUS: blocked (salvage = audit closeout only)
ORIGIN_MAIN_AUDITED: 1f4c3155d83f63042611b6598e0b01d26c9a4427
BLOCKER: missing validator/annotate modules on origin/main; gap L2 locals blob-FAIL
```
