# Mecha-Native Blocker Audit — 2026-07-09

> **SUPERSEDED (partial) — 2026-07-10:** Native bank + proof lane live per
> `artifacts/qa/MANGA_MECHA_HUMAN_READABILITY_PROOF_CLOSEOUT_2026-07-10.md`.
> Stale claims: zero L0 sidecars, zero L2/L3 REAL, `NOT READY` verdict.

**Lane:** mecha-native blocker audit (read-only + artifact authoring; not proof; not render)  
**Agent:** Pearl_Research  
**Project:** `proj_manga_first_ship_20260425`  
**Series:** `warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening`  
**Acceptance layer:** authored candidate — audit only; not system-working  
**Authority:** `MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` §6.2 mecha overlay; `MANGA_HALFPERSON_RULE_CLOSEOUT_2026-07-09.md`; `manga_asset_gap_map_2026-07-09.json`  
**Companion JSON:** `artifacts/qa/manga_mecha_native_blockers_2026-07-09.json`

---

## Scope and lane purpose

This audit answers one question for the later human-readability **proof** lane:

> What exact **native mecha** prerequisites are still missing before a rules-compliant mecha proof packet can be run honestly?

This lane does not render, repair assets, or modify pipeline code. It inventories native vs borrowed vs invalid proof surfaces against the human-readability rule families (crop legality, room grounding, eye-flow, occluder legality, speech-bubble ordering, action-density).

---

## Current mecha proof status

| Surface | Status | Honest label |
|---|---|---|
| Cross-genre composition mix | **INVALID_PROOF** | Quarantined — stillness busts on mecha L0 via `bbox_legacy` |
| M5 wiring proof | **INTERIM only** | Pipeline wiring demo — not presentable, not rules proof |
| L0 REAL plates (hangar, cockpit) | **EXECUTED-REAL bytes** | Background plates only — insufficient alone for proof |
| Native L2/L3 bank | **ABSENT** | Zero REAL character/object cutouts on disk |
| Rules-compliant manifest | **ABSENT** | No `ep_001_from_continuity.yaml` equivalent |
| Rules-compliant assembly | **ABSENT** | No canonical assembled strip from native bank |

**Verdict:** `NOT READY` for later human-readability proof lane.

---

## Valid vs invalid proof surfaces

### Invalid (must not cite as mecha readiness)

| Path | Why invalid |
|---|---|
| `artifacts/qa/invalid_proof/mecha/mecha_real_layer_proof_mix_2026-07-09.yaml` | HR-F12 cross-genre salvage — stillness iyashikei bust L2 pasted onto mecha hangar/cockpit L0 with `bbox_legacy`; quarantined in `invalid_proof/registry.json` |
| `artifacts/manga/warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening/assembled/mecha_real_layer_proof_mix_2026-07-09/` | Assembled outputs from invalid manifest; gate_report shows WARN-only `bbox_legacy` path (G1–G8 not fail-closed) |
| Any stillness L2 asset used under mecha series_id | Borrowed — violates HR-GEN-MC01 / HR-F12 |

### Not invalid but not proof

| Path | Why not proof |
|---|---|
| `assembly_manifests/m5_prep_wiring_proof_INTERIM.yaml` | All layers `provenance: INTERIM` — wiring demo per contract §4 |
| `assembled/m5_prep_wiring_proof_INTERIM/` | INTERIM sprites only — explicitly labeled NOT final art |
| `artifacts/manga/image_bank/warrior_calm/` (legacy brand bank) | Separate path tree (anchor_panels, character/master_wu/poses) — not wired as series `image_bank/L2` layered bank; not composition-meta annotated for grammar path |

### Valid reference (stillness — not mecha proof)

Stillness canonical proof path for comparison:

- Manifest: `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/ep_001_from_continuity.yaml`
- Assembly: `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/ep_001_from_continuity_final/`

Mecha has **no parallel canonical path**.

---

## Native asset inventory found

### Present (native REAL)

| Asset class | Path | Bytes | Native? | Notes |
|---|---|---:|---|---|
| L0 hangar establishing | `…/image_bank/L0/hangar_pre_dawn.png` | 2,842,149 | **YES** | Ledger `mecha:L0:hangar_pre_dawn` status `usable` |
| L0 cockpit interior | `…/image_bank/L0/cockpit_interior.png` | 3,394,620 | **YES** | Ledger `mecha:L0:cockpit_interior` status `usable` |
| L0 hangar duplicate | `…/image_bank/L0/hangar_pre_dawn__job527.png` | 2,747,005 | **YES** | Second render variant; no sidecar |
| Authored chapter script | `artifacts/manga/chapter_scripts/…/ep_001.yaml` | — | **YES** | 35 panels; no stub markers |
| Panel prompts | `artifacts/manga/panel_prompts/…/ep_001.panel_prompts.json` | — | **YES** | 35 prompts |
| Bank contracts (SPECCED) | `bank_contracts/scene_inventory.yaml`, `character_pose_inventory.yaml` | — | **YES** | CONFIG-EXISTS; poses `seated_cockpit`, `threshold_stand` |

### Present but insufficient for proof

| Asset class | Path | Issue |
|---|---|---|
| INTERIM sprites | `image_bank_sprites/L0_plate_INTERIM.png`, `L2_character_INTERIM.png`, `L3_object_INTERIM.png` | INTERIM — never presentable as proof |
| Legacy brand bank | `artifacts/manga/image_bank/warrior_calm/character/master_wu/` | Not in series layered bank path; no `.composition.json`; not enqueue-ledger REAL L2 |

### Missing (native REAL count = 0)

| Asset class | Expected path | Ledger / contract | Blocker |
|---|---|---|---|
| L2 seated_cockpit | `…/image_bank/L2/seated_cockpit.png` | `mecha:L2:seated_cockpit` — `status: requested`, `last_error: missing_output` | **HARD** — cockpit dialogue HR-GEN-MC02 |
| L2 threshold_stand | `…/image_bank/L2/threshold_stand.png` | `mecha:L2:threshold_stand` — `status: requested`, `last_error: missing_output` | **HARD** — hangar threshold beats |
| L3 glove_pad | `…/image_bank/L3/glove_pad.png` | `mecha:L3:glove_pad` — missing | **SOFT** — insert_object beats (script panels 2, 8, …) |
| L3 telemetry_panel | `…/image_bank/L3/telemetry_panel.png` | `mecha:L3:telemetry_panel` — missing | **SOFT** — cockpit insert beats |
| L2 full_figure hangar | (not specced in contract) | gap_map `room_full_figure: 0` | **HARD** — establishing + scale panels with pilot visible |
| L2 cockpit diegetic_pair | (not on disk) | no diegetic_pair metadata | **HARD** — legal cockpit bust without cross-genre borrow |
| L2 abstract-stage bust (mecha register) | (not on disk) | no clean mecha defocus dialogue pool | **HARD** — defocus dialogue after establishing |
| L2 cockpit occluder pose | (not specced/rendered) | HR-GEN-MC02 | **HARD** — console occluder + seated anchor |

**On-disk check:** `image_bank/L2/` and `image_bank/L3/` directories exist but are **empty** (0 PNG files).

---

## Metadata gaps

| Metadata field / artifact | Mecha state | Stillness reference | Impact |
|---|---|---|---|
| L0 `.composition.json` sidecar | **0 files** on mecha L0 | e.g. `L0_2b9283d4c387.composition.json` with `bg_class`, `camera`, `anchor_slots`, `ground_plane`, `light` | G2/G3/G4/G8 grammar gates WARN-only (`bbox_legacy`); room grounding not enforceable |
| L0 `anchor_slots[]` | **ABSENT** | `seat_at_table`, `abstract_dialogue_stage` slots on kitchen L0 | Cannot assign cockpit seat / console occluder anchors |
| L0 `occluder_crop_bbox_pct` | **ABSENT** | Present on stillness kitchen slot | HR-U04 / HR-GEN-MC02 cockpit occluder legality blocked |
| L2 `.composition.json` | **0 files** (no L2 assets) | 24 L2 sidecars on stillness ep_001 | No crop_class, room_capable, abstract_stage_eligible, diegetic_pair |
| L2 `genre` / series binding | N/A | stillness L2 paths under stillness series tree | Cross-genre paste is the only current “character” path — invalid |
| Manifest `shot_type` on proof mix | **empty** in gate_report | stillness continuity manifest sets shot_type | Chapter validator §6.2 cannot run on mecha |

---

## Canonical path gaps

| Step | Stillness (ready reference) | Mecha (current) | Gap |
|---|---|---|---|
| 1. Authored script | `chapter_scripts/…/ep_001.yaml` ✓ | `chapter_scripts/…/ep_001.yaml` ✓ (35 panels) | — |
| 2. REAL L0 bank + sidecars | v4_render_cache L0 + `.composition.json` ✓ | L0 PNG only; **no sidecars** | **BLOCKER** |
| 3. REAL L2 bank + sidecars | 21 L2 with legality metadata ✓ | **0 L2** | **BLOCKER** |
| 4. Manifest generation | `ep_001_from_continuity.yaml` ✓ | **missing** — only `m5_prep_wiring_proof_INTERIM.yaml` | **BLOCKER** |
| 5. Planning audit pass | 35/35 panels complete | not runnable without L2 | **BLOCKER** |
| 6. Assembly | `assembled/ep_001_from_continuity_final/` ✓ | only invalid cross-genre mix + INTERIM wiring | **BLOCKER** |
| 7. Human-readability proof JSON | stillness cases in `run_human_readability_proof.py` | mecha case `bad_cross_genre_mecha` **expects FAIL** | Proof lane correctly blocks today |

**Canonical mecha path when ready (target — not present today):**

```
artifacts/manga/warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening/
  assembly_manifests/ep_001_from_continuity.yaml          ← MISSING
  assembled/ep_001_human_readability_proof/               ← MISSING
  image_bank/L0/*.png + *.composition.json                ← sidecars MISSING
  image_bank/L2/*.png + *.composition.json                ← entire class MISSING
```

---

## Human-readability rule blockers by rule family

| Rule family | Mecha requirement (from rules §6.2) | Current state | Blocker severity |
|---|---|---|---|
| **Crop legality (G1)** | No bust/waist on readable hangar/cockpit without occluder or diegetic pair | Only cross-genre stillness busts available → FAIL HR-F12 | **HARD** |
| **Room grounding (G3/G4/G5)** | Horizon scale + contact shadow + console occluder on cockpit | L0 lacks `composition.json`; no native grounded L2 | **HARD** |
| **Eye-flow (HR-U15, §5.2)** | Focal subject upper-third; establishing before abstract | Script authored; cannot assemble honest panels without L2 | **HARD** (downstream) |
| **Occluder legality (HR-GEN-MC02)** | Cockpit dialogue requires console occluder + seated anchor | `seated_cockpit` L2 not rendered; no occluder metadata on L0 | **HARD** |
| **Speech-bubble ordering (HR-U21–U26)** | Locale-correct zones; no face occlusion | No rules-compliant assembled panels to letter | **SOFT** (blocked by asset gap first) |
| **Action-density layouts** | Cockpit = low density; battle exterior separate profile | ep_001 is cockpit/hangar register — N/A for battle overlay | **N/A** this episode |
| **Cross-genre (HR-F12 / HR-GEN-MC01)** | Native mecha bank only | Invalid proof mix is exactly this violation | **HARD** |
| **Provenance (HR-U14)** | REAL layers only in presentable proof | Invalid mix uses REAL stillness L2 under mecha series — genre lie | **HARD** |
| **Chapter grammar (§6.2)** | Establish before abstract; re-establish triggers | Validator exists but no mecha manifest to validate | **HARD** (no input) |

---

## Blocker matrix

| Prerequisite | Current state | Proof path or missing path | Severity | Owning next lane |
|---|---|---|---|---|
| Native L2 seated_cockpit | **MISSING** — ledger `requested`, file absent | Need: `…/image_bank/L2/seated_cockpit.png` + sidecar | HARD | Pearl_Int — dispatch `enqueue_crossgenre_real_layers.py` / Pearl Star |
| Native L2 threshold_stand | **MISSING** | Need: `…/image_bank/L2/threshold_stand.png` + sidecar | HARD | Pearl_Int |
| Native L3 inserts (glove, telemetry) | **MISSING** | Need: `…/image_bank/L3/glove_pad.png`, `telemetry_panel.png` | SOFT | Pearl_Int |
| L0 composition sidecars | **MISSING** (0 files) | Need: `hangar_pre_dawn.composition.json`, `cockpit_interior.composition.json` with anchor_slots | HARD | Pearl_Dev — annotate after L0 review |
| Cockpit anchor_slot + occluder bbox | **MISSING** | Need: slot on cockpit L0 per HR-GEN-MC02 | HARD | Pearl_Dev + Pearl_Author |
| Mecha diegetic_pair (optional fast-path) | **MISSING** | Need: paired L2↔L0 or seated_cockpit with `diegetic_pair` meta | SOFT | Pearl_Dev post-render |
| Native abstract-stage bust pool (mecha) | **MISSING** | Need: defocus dialogue L2 with `abstract_stage_eligible: true`, genre=mecha | HARD | Pearl_Int render + annotate |
| Full-figure / knees-up hangar pose | **MISSING** (not in bank contract) | Need: expand contract + render for scale panels | HARD | Pearl_Author contract + Pearl_Int |
| Canonical manifest | **MISSING** | Need: `assembly_manifests/ep_001_from_continuity.yaml` | HARD | Pearl_Dev — after bank lands |
| Rules-compliant assembly | **MISSING** | Need: `assembled/ep_001_human_readability_proof/` | HARD | Pearl_Dev proof lane |
| Valid proof manifest | **QUARANTINED** | Do not use: `invalid_proof/mecha/mecha_real_layer_proof_mix_2026-07-09.yaml` | HARD | — |
| Authored script + prompts | **PRESENT** | `chapter_scripts/…/ep_001.yaml`, `panel_prompts/…/ep_001.panel_prompts.json` | — | (done) |
| REAL L0 hangar + cockpit plates | **PRESENT** | `image_bank/L0/hangar_pre_dawn.png`, `cockpit_interior.png` | — | Pearl_Dev — annotate only |

---

## Exact next implementation / asset lane

**Order (serial):**

1. **Pearl_Int — mecha native layer render:** Dispatch ledger requests `mecha:L2:seated_cockpit`, `mecha:L2:threshold_stand`, `mecha:L3:glove_pad`, `mecha:L3:telemetry_panel` (already enqueued in `request_ledger.json`; status `requested` / `missing_output`).
2. **Pearl_Dev — L0 composition annotation:** Run L0 sidecar authoring on hangar + cockpit plates (`bg_class: full_render`, `anchor_slots` for cockpit seat/console occluder, hangar scale anchors).
3. **Pearl_Dev — L2 annotation:** After render lands, `annotate_l2_composition_legal.py` with `pose_context: seated_cockpit`, `room_capable`, occluder flags; verify no stillness cross-borrow in manifest gen.
4. **Pearl_Author — bank contract extension:** Add `full_figure_hangar`, `knees_up_threshold` (or equivalent) to `character_pose_inventory.yaml` for script panels requiring visible pilot at scale.
5. **Pearl_Dev — mecha human-readability proof lane:** Generate `ep_001_from_continuity.yaml` → assemble → run `run_human_readability_proof.py` + chapter validator with **native paths only**.

---

## Verdict

### `NOT READY`

The later human-readability **proof** lane cannot run honestly on mecha today. Native REAL assets stop at **two L0 background plates**. All character/object layers are missing. The only executed “real layer” assembly uses **quarantined cross-genre stillness busts** and is explicitly invalid under HR-F12.

**Primary blocker:** zero native mecha L2 REAL assets on disk (`image_bank/L2/` empty) plus zero L0/L2 `composition.json` sidecars for grammar fail-closed assembly.

---

## Closeout tags

```
manga-mecha-blocker-audit=artifacts/qa/MANGA_MECHA_NATIVE_BLOCKER_AUDIT_2026-07-09.md
manga-mecha-blocker-json=artifacts/qa/manga_mecha_native_blockers_2026-07-09.json
manga-mecha-native-status=not_ready
manga-mecha-native-present=L0_hangar_pre_dawn_REAL,L0_cockpit_interior_REAL,chapter_script_ep_001_35p,panel_prompts_35,bank_contracts_SPECCED
manga-mecha-native-missing=L2_seated_cockpit,L2_threshold_stand,L3_glove_pad,L3_telemetry_panel,L0_composition_sidecars,L2_composition_sidecars,cockpit_anchor_slots,mecha_diegetic_pair,mecha_abstract_bust_pool,full_figure_hangar_pose,ep_001_from_continuity_manifest,rules_compliant_assembly
manga-mecha-native-invalid-proof=artifacts/qa/invalid_proof/mecha/mecha_real_layer_proof_mix_2026-07-09.yaml,artifacts/manga/warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening/assembled/mecha_real_layer_proof_mix_2026-07-09/
manga-mecha-native-next-action=Dispatch mecha L2/L3 renders from request_ledger; annotate mecha L0/L2 composition sidecars; then Pearl_Dev mecha ep_001_from_continuity proof lane
manga-mecha-native-blocker=zero native mecha L2 REAL assets + zero L0 composition sidecars — cross-genre proof quarantined
```
