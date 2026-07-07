# M5 Footprint Audit + Scale-Up Memo — 2026-07-08

**Verified branch:** `agent/manga-m6-blind10-protocol-20260708` (main + M6 protocol commit; M5 work lands atop)
**Layer claim:** M5 remains **PARTIAL** — pilot footprint only, not catalog scale.

---

## 1. What M5 can do now (EXECUTED-REAL)

| Capability | Status | Evidence |
|---|---|---|
| Bank contracts (3 pilot series) | CONFIG-EXISTS | `artifacts/manga/*/bank_contracts/{scene,object,character_pose}_inventory.yaml` |
| Offline assembly (`assemble_from_bank.py`) | CODE-WIRED + EXECUTED-REAL | composition grammar pilot, demo_alarm_metaphor_6p (INTERIM L1/L3/L4) |
| **Continuity → manifest generator** | **CODE-WIRED + EXECUTED-REAL (this session)** | `scripts/manga/generate_assembly_manifest.py` |
| **35-panel ep_001 bank assembly (0 INTERIM)** | **EXECUTED-REAL (this session)** | `assembled/ep_001_from_continuity/` — 35 PNGs, `_provenance.json` layers_interim=0 |
| PuLID face-lock pilot (Mira Aoki) | EXECUTED-REAL | 3 poses + reference sheet; `qa_face_distance_report.json` gate_pass=true (max 0.31 ≤ 0.4) |
| Composition grammar gates G1–G6 | EXECUTED-REAL | `assembled/composition_grammar_pilot/gate_report.json` |
| Continuity state generator (Milestone C) | CODE-WIRED | ep_001 35 YAMLs; ep_002 beatsheet extracted |
| M5-prep wiring proofs (warrior, cognitive) | EXECUTED-REAL (INTERIM only) | `m5_prep_wiring_proof_INTERIM/` — not final art |

### Pilot assembly footprint (not “at scale”)

| Series | Bank contracts | REAL bank layers | Assembled output | INTERIM count |
|---|---|---|---|---|
| stillness_press (iyashikei) | ✓ (template copy) | L2 PuLID 3 poses + v4_render_cache L0×5 L2×21 | **ep_001 35-panel 0-INTERIM** + 6p demo (INTERIM L1/L3/L4) | demo 6p only |
| warrior_calm (mecha) | ✓ (M5-prep) | 0 REAL | INTERIM wiring proof 6p | all 18 layers |
| cognitive_clarity (psych thriller) | ✓ (M5-prep) | 0 REAL | INTERIM wiring proof 6p | all 18 layers |

**Unique render dedup (stillness ep_001):** 5 L0 + 21 L2 → 35 panels (from `ep_001_bank_gaps.json`).

---

## 2. What still blocks scale

| Blocker | Severity | Detail |
|---|---|---|
| **M5-BLK-001 Pearl Star / #3075** | HARD | GPU bank renders for 34 remaining M3 flagships; pscli queue dispatch |
| **M5-BLK-002 Bank REAL coverage** | HARD | Only stillness has REAL L0/L2 cache; warrior/cognitive = INTERIM only |
| **M5-BLK-003 L1/L3/L4 bank gap** | HARD | demo_alarm_metaphor_6p still uses INTERIM sprites for kettle/alarm/steam |
| **M5-BLK-004 ep_002+ continuity gate** | HARD | OPD-135: ep_002+ dispatch requires forward-gen continuity round-trip |
| **M5-BLK-005 Strip export limit** | SOFT | 35×1920px vertical strip exceeds JPEG 65500px height — use webtoon_compose for full episodes |
| **M5-BLK-006 PuLID at series scale** | SOFT | 1 character proven; LoRA fallback per Q-MANGA-04 not exercised |

M6 blind-10 blocked on ≥4 genres × 0-INTERIM assembled episodes — stillness ep_001_from_continuity is the first 0-INTERIM full episode but single-genre pilot only.

---

## 3. Next exact execution step

**On Pearl Star return (operator or unattended LOW queue):**

```bash
# 1. Confirm RAP queue (do not bypass ComfyUI)
pscli status

# 2. Enqueue stillness L1/L3/L4 REAL layers from bank_contracts/object_inventory.yaml
#    (RESUME_COMMANDS.sh under assembled/demo_alarm_metaphor_6p/)
bash artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/demo_alarm_metaphor_6p/RESUME_COMMANDS.sh

# 3. Re-generate manifest + assemble (0 INTERIM target for metaphor scene)
PYTHONPATH=. python3 scripts/manga/generate_assembly_manifest.py \
  --series stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --profile stillness_en_01 --episode ep_001
PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
  --manifest artifacts/manga/.../assembly_manifests/ep_001_from_continuity.yaml \
  --out-dir artifacts/manga/.../assembled/ep_001_from_continuity/ --bubbles

# 4. Scale bank contracts to next M3 flagship (no GPU):
PYTHONPATH=. python3 scripts/manga/generate_bank_contracts_from_script.py \
  --chapter-script artifacts/manga/<series>/chapter_scripts/ep_001.yaml
```

**Parallel (no GPU):** run `generate_assembly_manifest.py --dry-run` on ep_002 after continuity forward-gen to surface bank gaps before enqueue.

---

## 4. Key paths

| Artifact | Path |
|---|---|
| Manifest generator | `scripts/manga/generate_assembly_manifest.py` |
| ep_001 auto manifest | `artifacts/manga/stillness_press__.../assembly_manifests/ep_001_from_continuity.yaml` |
| Bank gap report | `.../assembly_manifests/ep_001_bank_gaps.json` |
| 0-INTERIM assembly | `.../assembled/ep_001_from_continuity/` |
| Face-distance gate | `.../image_bank/L2/mira_aoki/qa_face_distance_report.json` |
| M5-prep evidence | `artifacts/qa/manga_m5_prep_evidence/` |
| M6 blockers (downstream) | `artifacts/qa/manga_blind10_2026-07-08/BLOCKERS.md` |

---

## 5. Machine summary

```
manga-m5-status=PARTIAL
manga-m5-pilot-series=3
manga-m5-real-bank-series=1
manga-m5-zero-interim-episodes=1
manga-m5-panel-footprint=35
manga-m5-at-scale=NO
```
