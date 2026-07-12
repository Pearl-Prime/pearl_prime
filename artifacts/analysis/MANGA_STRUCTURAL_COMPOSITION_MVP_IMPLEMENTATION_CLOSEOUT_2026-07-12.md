# MANGA STRUCTURAL COMPOSITION MVP — IMPLEMENTATION CLOSEOUT

**Date:** 2026-07-12  
**Branch:** `agent/manga-structural-composition-mvp`  
**Worktree:** `/Users/ahjan/phoenix_omega_worktrees/manga-structural-composition-mvp`  
**Base:** `origin/main` @ `1529f36839`  
**MVP code HEAD (prior):** `c0fdba35e5`  
**Green-lane turn:** EXECUTED-REAL proof packet + closeout update (this file)

---

## STATUS

**EXECUTED-REAL (structural lane, scoped)** — Runtime remains the separate Structural Composition MVP layer. Real-bank / assembled stillness + mecha assets now have byte-verified plan envelopes + support overlays from the shared `ResolvedTransform` path. Assembler `--structural-plan` **explicitly deferred**. Lettering **not** rewired. Universal horizon-ratio law **not** re-canonized. **Not** PROVEN-AT-BAR. **Not** on `origin/main` until push/PR succeeds (see PR/PUSH STATUS).

---

## OBJECTIVE

Advance structural composition from local CODE-WIRED → honest EXECUTED-REAL on seated_table + standing_room using real bank / catalog assets; decide assembler consume path; report exact push/PR status.

---

## FILES_READ

| Path | Result |
|------|--------|
| Prior MVP closeout + green program board / blocker ledger | read |
| `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md` | exists_live |
| `docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md` | exists_live |
| `config/manga/composition_validation.yaml` | exists_live |
| `config/manga/structural_templates.yaml` | exists_live |
| `config/manga/panel_type_structural_bridge.yaml` | exists_live |
| `scripts/manga/structural_composition.py` | exists_live |
| `scripts/manga/plan_panel_layout.py` | exists_live |
| `scripts/manga/validate_scene_assembly_visual.py` | exists_live |
| `scripts/manga/assemble_from_bank.py` | exists_live — no structural-plan consume; lettering still v1 |
| Stillness honest packet panels (LFS materialized) | EXECUTED-REAL bytes |
| Mecha layered packet bank (LFS materialized) | EXECUTED-REAL bytes |

---

## FILES_WRITTEN (this green turn)

- `artifacts/qa/manga_structural_composition_proof_2026-07-12/` — proof packet root
  - `PROOF.md`, `PROOF_SUMMARY.json`
  - `asset_fingerprints/ASSET_FINGERPRINTS.json`
  - `bundles/*_bundle.json` (seated/standing stillness + mecha + floating control)
  - `runs/*/plan_envelope.json`, `support_overlay.png|.json`, quarantine tree, `RUN_RESULT.json`
- `artifacts/analysis/MANGA_STRUCTURAL_COMPOSITION_MVP_IMPLEMENTATION_CLOSEOUT_2026-07-12.md` (this file)

**Not written:** assembler `--structural-plan` path (deferred).

---

## ACCEPTANCE_LAYER

| Deliverable | Layer |
|-------------|-------|
| Structural configs + schemas | CONFIG-EXISTS |
| Structural runtime (plan / validate / overlay / quarantine) | CODE-WIRED |
| Structural unit/routing tests (synthetic) | CODE-WIRED |
| Bank/assembled seated + standing structural proof | **EXECUTED-REAL** — see proof packet |
| Support overlays from shared resolved transform | **EXECUTED-REAL** (`same_resolved_transform_path: true`) |
| Floating control (ep001_008) | **EXECUTED-REAL** expected `CONTACT_FAIL` |
| Assembler `--structural-plan` consume | **ABSENT** (explicitly deferred) |
| Lettering v2 / compiled safe-zone on assembler | **ABSENT** (honest: not rewired) |
| Merged to `origin/main` | **ABSENT** until push/PR |
| Blind / PROVEN-AT-BAR | **ABSENT** |

---

## PROOF PACKET

**Root:** `artifacts/qa/manga_structural_composition_proof_2026-07-12/`

| Run | Status | Asset bytes (source) | Overlay bytes | plan_hash (prefix) |
|-----|--------|----------------------|---------------|--------------------|
| seated_table_stillness_ep001_016 | pass | 2,633,608 | 8,878 | `fff0f89e2a32` |
| standing_room_stillness_ep001_013 | pass | 2,125,334 | 9,920 | `6c344401931d` |
| seated_table_mecha_cockpit | pass | L0 3,581,417 + L2 3,548,619 | 9,198 | `c2732d17d786` |
| standing_room_mecha_threshold | pass | L0 2,747,005 + L2 2,035,975 | 9,660 | `374ba886a77b` |
| floating_control_stillness_ep001_008 | hard_fail CONTACT_FAIL (expected) | 2,213,671 | — | — |

Machine claim: `PROOF_SUMMARY.json` → `acceptance_layer_claim: EXECUTED-REAL` (4 pass / 1 expected fail / 0 unexpected).

**Sparse-checkout honesty:** source L2 paths under `artifacts/manga/.../v4_render_cache` are declared in the stillness panel manifest but not present in this sparse tree; proof uses materialized QA packet panels + mecha bank layers (all PNG signature + ≥50KB).

---

## ASSEMBLER `--structural-plan` DECISION

**DEFER (explicit).**

Reasons:
1. Lane success condition is EXECUTED-REAL on real assets via the structural CLI path — achieved without assembler rewire.
2. Ambient `test_assemble_from_bank` chapter-grammar fixture failures remain; touching the assembler now risks conflating ambient debt with structural work.
3. Lettering honesty requires leaving `bubble_render` v1 call path untouched until a dedicated rewire+prove lane.
4. Optional per program board; quarantine/plan/overlay path already exercises the same envelope the assembler would later consume.

Next owner: add `--structural-plan` behind an explicit flag that verifies `plan_hash` and uses `render_from_verified_plan` without recomputing placement — do not default-on.

---

## TESTS_RUN

```
PYTHONPATH=scripts/manga python3 -m pytest \
  scripts/manga/tests/test_structural_composition.py \
  scripts/manga/tests/test_scene_visual_acceptance.py -v
→ 17 passed

PYTHONPATH=scripts/manga python3 -m pytest \
  scripts/manga/tests/test_assemble_from_bank.py -q
→ 5 passed, 4 failed, 4 skipped (ambient chapter-grammar fixture debt; assembler not modified)
```

Real proof run: structural plan + overlay + quarantine CLI on stillness seated/standing + mecha bank seated/standing (see proof packet). Pass 4 / expected CONTACT_FAIL 1 / unexpected 0.

---

## KNOWN_LIMITATIONS

- Scope only: `seated_table_scene` + `standing_room_scene`.
- Assembler does **not** consume structural plan envelopes (`--structural-plan` deferred).
- Contact polygons are operator-authored against real panels (not auto-extracted from depth/pose).
- ep001_016 uses structural `seated_table_scene` despite archetype bridge hint to standing — documented in PROOF.md.
- Horizon-ratio G3 unchanged.
- Branch may still lack remote tracking until push succeeds.

---

## OPEN_BLOCKERS

| ID | Severity | Status after this turn |
|----|----------|------------------------|
| SG-01 | HARD | **CLEARED for EXECUTED-REAL packet** — proof root exists |
| SG-02 | HARD | **Still open** until push/PR lands on remote / merges to main |
| SG-03 | MED | **Deferred by decision** — assembler consume optional |
| SG-04 | MED | Lettering still v1 (out of structural green scope) |
| SG-05 | SOFT | Ambient assembler grammar fixture failures |

---

## PR / PUSH STATUS

See live section appended after preflight attempt this turn. Do not invent remote SHAs.

*(placeholder filled by shell preflight results)*

---

## NEXT_ACTION

1. Preserve proof packet on branch (commit if operator/policy requires artifact persistence).
2. Push `agent/manga-structural-composition-mvp` only after push-guard + preflight pass; open PR to `main` when remote exists.
3. Follow-on lane: optional `--structural-plan` assembler flag (explicit, off by default).
4. Do not claim PROVEN-AT-BAR.

---

## Lettering / safe-zone honesty

| Claim | Evidence |
|-------|----------|
| Safe-zone QC exists | `scripts/manga/validate_layer.py` → `check_lettering_safe_zones_clear` |
| Genre-style v2 exists | `phoenix_v4/manga/chapter/bubble_render_v2.py` |
| Live assembler lettering path | `assemble_from_bank.py` → `bubble_render.render_bubbles_onto_panel` (v1) |
| Structural green rewired lettering? | **No** |
