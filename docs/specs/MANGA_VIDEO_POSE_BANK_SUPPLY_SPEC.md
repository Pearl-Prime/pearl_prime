# Manga Video Pose-Bank Supply Spec (V-Bank V1)

**Status:** SPECCED (authority for the video-capture → bank supply lane)  
**Schema version:** 1.0.0  
**Date:** 2026-07-24  
**Owners:** Pearl_Architect (contract) · Pearl_Dev (Lane 04 tooling)  
**Subsystem:** `manga_pipeline`  
**Acceptance layer:** SPECCED — not CODE-WIRED, not EXECUTED-REAL, not PROVEN-AT-BAR  
**NEW-ARTIFACT-JUSTIFIED:** bank SUPPLY lane needs a singleton authority separate from V5 architecture (registry `NO-without-ratification` on `MANGA_V5_LAYERED_ARCHITECTURE.md`). This doc is that singleton.

**Gate inputs (verified at authoring):**
- `dashscope-free-media-landed=1a683254959710ec85033dce0a164ee18ace4cb2` (PR #310)
- `manga-video-capability-research-merged=763439e36e0ffa6bbeb2898fd1aa5a954c120018` (PR #341)

**Research cite (Lane 02 RECOMMENDATIONS — binding):**
1. Pilot engine = cloud free quota **`wan2.7-i2v` + canonical external still**
2. Skip **r2v** unless free seconds proven on account
3. Scale = **VACE-1.3B Apache** on Pearl Star (off-manga RAP windows)
4. DashScope free-quota outputs = **INTERIM**; Apache Wan/VACE = **REAL-eligible** after gates
5. Sunset free-media planning hard-stop **2026-10-18**

**Cross-refs (read-only unless noted):**
- Layer/bank contract: `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §4 / §4.6 / §9 / §12.3 / §15.A / **§19** (pointer — edited in place this lane)
- Continuity cardinality (formerly §6.8): `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md` §8
- Composition sidecars: `docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md` + `schemas/manga/composition_meta.schema.json`
- Assembly ingress: `schemas/manga/assembly_manifest.schema.json` (assembler **not** modified)
- Identity: `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` (read-only; ladder amendment ratified Lane 06)
- Research: `docs/research/MANGA_VIDEO_POSE_BANK_CAPABILITY_RESEARCH_2026-07-24.md`
- INTERIM sprite precedent: `scripts/manga/make_object_sprite.py`
- Demand rollup (when landed): uplift Lane 09 `series_demand_rollup.yaml`

**Builds on / EXTENDS (no forks):** `manga_bank_assembler`, `assembly_manifest.schema`, `generate_bank_contracts_from_script.py`, `character_pose_inventory` convention.

**OUT OF SCOPE:** V5 architecture doc edits; assembler; `config/manga/`; `gate_registry`; numbered production gates (Lane 04 validators = scripts+tests; gate promotion is a follow-on).

---

## 1. Purpose

Stand up a **video-capture supply lane** that:

1. Compiles **demanded** pose coverage into a **character capture manifest** (one per character × outfit).
2. Captures short, identity-anchored clips (pilot: same-anchor i2v).
3. Harvests frames through an **ordered reject-on-fail gate chain**.
4. Registers curated cutouts into the existing image bank / pose inventory for **deterministic assembly** via existing `assembly_manifest` layer objects.

This is a **bank supply** lane, not an architecture variant. Panels still assemble from L0–L4 bank assets. Motion-source artifacts (clips, contact sheets) claim the reserved **A0–A9** animation namespace; extracted still layers remain ordinary **L2/L3**.

---

## 2. Demand → capture compilation

### 2.1 Inputs (signal-gated)

| Priority | Signal / condition | Input artifacts |
|----------|--------------------|-----------------|
| **Primary** | `manga-bank-demand-rollup-merged=<sha>` present | `artifacts/manga/<series>/bank_contracts/series_demand_rollup.yaml` (uplift Lane 09) |
| **Fallback (LIVE DEFAULT)** | Uplift 09/11 **not** started — use this path | Per-episode `artifacts/manga/<series>/bank_contracts/character_pose_inventory.yaml` ∪ series master-plan golden (when `manga-series-master-plan-contract-merged` exists; else stillness golden / authored inventories only) |

**Compiler MUST NOT invent fixed-12 / hardcoded pose lists.** Only **DEMANDED** `pose_id`s drive clip prompts and curation targets.

### 2.2 Output

One **character capture manifest** per `(character_id, outfit_id)` conforming to:

`schemas/manga/character_capture_manifest.schema.json`

Path convention (Lane 04 implements):

```text
artifacts/manga/<series>/video_bank/capture_manifests/<character_id>__<outfit_id>.json
```

### 2.3 Action families

Each manifest lists `capture_sets[]` grouped into families:

| Family | Typical demanded poses | Clip intent |
|--------|------------------------|-------------|
| `dialogue` | bust / CU emotional beats | Head+torso micro-motion; anticipation → settle |
| `locomotion` | walk / stand / turn | Full-body weight shift; locked camera |
| `seated` | seated MS / three-quarter | Seated posture cycle; hands optional only if demanded |
| `genre_pack` | series-specific demanded extras | Only when rollup/inventory marks demand |

**Cardinality (both ends):** Continuity state §8 / formerly layer-contract §6.8 — empirical caching, never cartesian product. At capture time: **one short clip per family entry**; at curation: **smallest sufficient set** of frames covering demanded `pose_id`s — never "keep all frames."

### 2.4 Clip prompt contract (comic-readable keys)

Every `capture_sets[].prompt` MUST encode:

1. Staged **anticipation → impact/contact → follow-through/settle** (Lane 02 C11)
2. **Locked camera** (no handheld drift)
3. **Full body in frame** for locomotion/seated families; dialogue may be MCU/CU only when demanded poses are face/bust
4. **Flat neutral high-contrast background** (cutout success; see §9 cutout contract)
5. **Single character**; **no props** unless a demanded pose_id requires an attached prop already in inventory
6. Outfit + identity locked to manifest `outfit_id` / `identity_version`

Pilot duration recipe: **5 s** preferred (Lane 02 sampling table). i2v API range 2–15 s — longer clips burn free seconds faster and increase near-duplicate flood.

### 2.5 Golden example (mutually consistent with schema)

```json
{
  "schema_version": "1.0.0",
  "manifest_id": "stillness_en_01__mira_aoki__cream_sweater__capture_v1",
  "series_id": "stillness_en_01",
  "character_id": "mira_aoki",
  "identity_version": "pulid_sheet_v1",
  "outfit_id": "cream_sweater",
  "demand_source": {
    "mode": "bank_contracts_fallback",
    "bank_contracts_glob": "artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/bank_contracts/character_pose_inventory.yaml",
    "signal_note": "manga-bank-demand-rollup-merged absent — uplift Lane 09 not started; compile from demanded pose_ids in character_pose_inventory only."
  },
  "anchor": {
    "asset_path": "artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/image_bank/L2/mira_aoki_pulid_reference.png",
    "source_class": "pulid_reference",
    "outfit_id": "cream_sweater",
    "identity_version": "pulid_sheet_v1"
  },
  "capture_sets": [
    {
      "family": "seated",
      "clip_id": "mira_cream_seated_cycle_01",
      "a_namespace_id": "A0",
      "prompt": "Single character full body seated at table, cream sweater, locked camera, flat neutral high-contrast backdrop, no props, staged anticipation then settle, comic-readable key poses, anime still-frame clarity",
      "duration_s": 5,
      "engine": "wan2.7-i2v",
      "anchor_mode": "i2v",
      "demanded_pose_ids": [
        "front_portrait_seated_calm",
        "medium_seated_three_quarter"
      ],
      "sampling_recipe": {
        "candidate_keyed_samples": 10,
        "bank_keep_target": 5
      }
    },
    {
      "family": "dialogue",
      "clip_id": "mira_cream_dialogue_micro_01",
      "a_namespace_id": "A1",
      "prompt": "Single character MCU bust, cream sweater, locked camera, flat neutral high-contrast backdrop, subtle brow/jaw tension cycle anticipation to settle, no props, comic-readable keys",
      "duration_s": 5,
      "engine": "wan2.7-i2v",
      "anchor_mode": "i2v",
      "demanded_pose_ids": [
        "front_portrait_seated_calm",
        "front_portrait_seated_tense"
      ],
      "sampling_recipe": {
        "candidate_keyed_samples": 10,
        "bank_keep_target": 4
      }
    }
  ],
  "quota_budget": {
    "engine_lane": "dashscope_free_i2v",
    "planned_seconds": 10,
    "reserve_seconds": 10,
    "sunset_date": "2026-10-18",
    "notes": "Lane 02: skip r2v unless burn_summary proves seconds; re-verify ~50s i2v remaining before Lane 05 burn."
  },
  "provenance_default": "INTERIM",
  "notes": "Q-VBANK-02 default pilot character mira_aoki; anchors from existing PuLID machinery — zero cloud still-quota."
}
```

Validate (operator / Lane 04 CI):

```bash
python3 -c '
import json, pathlib
from jsonschema import Draft7Validator
root = pathlib.Path(".")
schema = json.loads(root.joinpath("schemas/manga/character_capture_manifest.schema.json").read_text())
# paste or load golden from this section / fixture
example = json.loads(pathlib.Path("/tmp/golden_capture_manifest.json").read_text())
Draft7Validator(schema).validate(example)
print("OK")
'
```

Lane 03 self-check: schema + example both `json.load`-parse and are mutually consistent (see closeout).

---

## 3. Anchor policy

**Canonical anchors come from existing identity machinery only:**

| Allowed | Disallowed |
|---------|------------|
| PuLID reference sheets | DashScope / Wan **still** free-quota for anchors |
| Model sheets / character design renders | Paid unattended still APIs |
| Pearl Star Qwen-Image (or approved panel crop) renders | Fresh t2i just to "spend still quota" |

**Rules:**

1. Every clip names the same manifest `anchor.asset_path` (+ optional `public_url` / base64 for i2v `media[]`).
2. Identity is anchored **per-clip**: pilot = **i2v** from that anchor; scale = **VACE** reference; **r2v** only if Lane 02 free-seconds preflight proves remaining seconds (otherwise skip).
3. Cloud still-quota is **not** part of this supply lane's economics table for anchors.
4. Outfit conformance: `anchor.outfit_id` MUST equal manifest `outfit_id`.

---

## 4. Frame pipeline gate chain (ordered)

A frame that fails **any** gate is **REJECTED**. No downstream repair. No silent demotion.

| Step | Gate name | Spec / tool | Pass rule (summary) |
|------|-----------|-------------|---------------------|
| 1 | `extract_candidates` | Lane 02 sampling | Prefer keyed anticipation/impact/follow-through picks. 5 s → **8–12** candidates; **not** uniform every-Nth dump |
| 2 | `near_duplicate_cluster` | Lane 04 tooling | Collapse near-dup clusters; keep best representative |
| 3 | `pose_phase_classify` | Lane 04 tooling | Label rest / anticipation / impact / follow-through / turn; map toward demanded `pose_id`s |
| 4 | `cutout` | ToonOut / rembg (`manga_cutout_toonout.py` / existing backends) | RGBA subject cutout per §9 |
| 5 | `class_a_l2_gates` | §12.3 | `rembg_clean_alpha` · `character_extraction_coverage` · `background_bleed_check` · safe-zone bbox inheritance (§5) |
| 6 | `bank_layer_blob_gate` | `scripts/manga/bank_layer_blob_gate.py` | Reject blob / empty / under-byte layers |
| 7 | `qa_face_distance` | `qa_face_distance` vs **anchor** | Same-character bar per M5 roadmap: pairwise distance **≤ 0.4** vs anchor |
| 8 | `outfit_conformance` | vs outfit reference | Hard-fail clothing mutation (sleeve length, button count, color) across cuts |
| 9 | `curate_to_demanded_pose_ids` | inventory cardinality | Keep smallest set covering demanded ids; drop extras |
| 10 | `sidecars_write` | provenance + composition | See §4.1 |
| 11 | `pose_inventory_register` | EXTEND `character_pose_inventory` | Register banked asset paths; do not invent undemanded pose_ids |

### 4.1 Sidecars (mandatory for bank admission)

**`.provenance.json`** (pattern: `make_object_sprite.py`):

- `provenance`: `INTERIM` | `REAL`
- `source_clip` + `frame_index`
- `extraction_command` (exact replay)
- `real_replacement` path/command when INTERIM (self-hosted VACE/Wan enqueue via RAP / `pscli`)
- DashScope-derived: filename **`_INTERIM` suffix** + `provenance_note`

**`.composition.json`** (aligns with composition grammar / `composition_meta.schema.json`):

- Required for L2 bank admission intent: `anchor.y_px` (or equivalent feet/anchor slot fields) + `figure_height_m` (or `expected_figure_h_pct` when using grammar slots)
- `layer_class`: `L2` (extracted character still) — never stamp A* on still layers

### 4.2 Sampling recipe (Lane 02 → Lane 04 default)

| Clip length | Extract candidates | Keep after QA |
|-------------|--------------------|---------------|
| 5 s @ 24–30 fps | 8–12 keyed | 4–6 banked cutouts |
| 10 s | 12–16 keyed | 6–8 |

Reject classes (bank filters): hands/fingers failure; occlusion-reveal hallucination; clothing mutation; background bleed; mid-clip identity morph (keep early stable segment only).

---

## 5. Provenance rules (Q-VBANK-03 default)

| Source | Provenance | Bank / panel policy |
|--------|------------|---------------------|
| DashScope free-quota video → frames | **INTERIM permanently** | `_INTERIM` suffix + provenance_note; never present as final art |
| Self-hosted Apache-2.0 Wan / **VACE-1.3B** after full gate chain | **REAL-eligible** | May stamp `REAL` only after gates 1–11 pass |
| FLUX.1-Kontext-dev / LTX-2.3 community cliff / Wan2GP wrapper-only | **INTERIM** (license) | Do not treat as REAL-eligible without operator counsel |

**Ingress rule:** Assets enter panels **ONLY** via `assembly_manifest.schema.json` layer objects (`layer_class` L0–L4 + mandatory `provenance`). The assembler is **not** modified by this lane. INTERIM layers require `provenance_note` naming REAL replacement.

---

## 6. Namespace claim (A0–A9)

Per layer-contract §4.6 + §19:

| Artifact | Namespace |
|----------|-----------|
| Source clips, contact sheets, motion derivatives | **A0–A9** (`animation_layer`) — claim IDs; update §4.6 purpose examples |
| Extracted still pose cutouts | **L2** (character) or **L3** if object-only crops |
| Panel composites | Existing L0–L4 stack only |

No ad-hoc layer IDs. Motion artifacts do **not** bypass the still-layer gate chain to enter panels.

---

## 7. Identity-ladder draft (ratify in Lane 06)

**Draft posture (this lane SPECCES; Lane 06 amends cap docs):**

1. **Primary:** PuLID reference sheets / model sheets + **capture-bank** poses (this supply lane)
2. **Last-resort:** per-character LoRA — **not planned** as the default path; only if PuLID + capture-bank fail identity bars on a flagship after pilot verdict

### 7.1 Implied §15.A.1 / §15.A.2 wording change (draft for Lane 06)

**Current §15.A.1** treats identity lock as `{PuLID-active OR per-character-LoRA-trained}` precondition.

**Draft replacement intent:**

> Identity lock for L2 is evaluable when **PuLID-active** (or equivalent commercial-clean face lock) **OR** (capture-bank L2 assets for character X pass `qa_face_distance` ≤ 0.4 vs the canonical anchor across the demanded pose set). Per-character LoRA remains an **optional last-resort** behind that primary ladder — not a launch prerequisite when PuLID + capture-bank clear the bar.

**§15.A.2** (extraction reliability) is unchanged by this ladder — cutout/class-A gates still apply to capture-bank frames identically to rendered L2s.

Lane 06 owns the actual §15.A.1 text edit + roadmap M5 / brand_lora_plans banner after pilot verdict (`method_better|method_worse|inconclusive`).

---

## 8. Quota + sunset economics

### 8.1 Cloud free-quota pilot (Lane 05)

| Bucket | Planning assumption (re-verify live) | Policy |
|--------|--------------------------------------|--------|
| `wan2.7-i2v` | ~50 s remaining on `ahjansamvara` | **Primary burn** — same-anchor i2v |
| `wan2.7-t2v` | ~45 s remaining | Smoke / style only; weak cross-clip identity |
| `wan2.7-r2v` | DOC-ONLY 50 s catalog; **account-unconfirmed** | **Skip** unless `burn_summary` / Free Quota preflight proves seconds |
| Still models | Separate image buckets | **Do not spend on anchors** |

**Spend order (Lane 02 #2):** re-verify → 2–3× same-anchor i2v @5 s → optional one first+last pair → at most one short continuation → stop with **≥10 s reserve** for retakes.

**Hard sunset:** **2026-10-18** (CLAUDE.md free-media exception). After sunset, cloud free lane is closed; scale = Pearl Star only.

Operator gates: `PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1` + `DASHSCOPE_FREE_QUOTA_API_KEY` — operator-present only; never cron.

### 8.2 Self-hosted scale posture

| Rank | Engine | Provenance path | Scheduling |
|------|--------|-----------------|------------|
| 1 | **VACE-1.3B** (~8 GB, Apache-2.0) | REAL-eligible after gates | RAP queue-first (`pscli`); **off-manga** windows only |
| 2 | Wan 2.2 5B / quantized Wan | REAL-eligible if Apache weights | Same |
| 3 | 14B GGUF | Only if needed | Same |
| 4 | LTX-2.3 / Kontext-dev | INTERIM / license-gated | Do not mix into REAL bank |

**Hard constraint:** Pearl Star manga already peaks ~10.76 GB / ~25 min/panel. Video jobs **must not** inline inside panel render jobs.

### 8.3 Manifest `quota_budget` fields

Required on every capture manifest: `engine_lane`, `planned_seconds`, `reserve_seconds`; recommended `sunset_date` for cloud burns.

---

## 9. Extension points (DISCOVERY — verified 2026-07-24)

| Extension | Status | This lane's action |
|-----------|--------|--------------------|
| `series_demand_rollup.yaml` | Uplift 09 **not started** | Spec fallback to `bank_contracts` + master-plan golden |
| `character_pose_inventory.yaml` | EXISTS (stillness, warrior_calm, cognitive_clarity) | EXTEND registration only; demand-derived |
| `assembly_manifest.schema.json` | L0–L4 + provenance | Consume as-is; no schema fork |
| `make_object_sprite.py` INTERIM sidecars | EXISTS | Pattern for video-frame INTERIM |
| `bank_layer_blob_gate` | EXISTS | Named gate in chain |
| `qa_face_distance` | EXISTS (individuation + M5 same-char ≤0.4) | Named gate vs anchor |
| §4.6 A0–A9 | Reserved | Claim motion-source; table updated |
| V5 architecture doc | NO-without-ratification | **Not edited** |
| `gate_registry.yaml` | Owned by uplift | **No numbered gate** this pack |

---

## 10. Lane handoff contracts

| Lane | Consumes this spec to… |
|------|-------------------------|
| **04** | Implement `scripts/manga/video_bank/` compiler, capture runner (import exempt client only), extractor, validators + tests; fixture from §2.5 golden |
| **05** | Operator burn one character×outfit; INTERIM bank slice; consistency scorecard |
| **06** | Ratify identity-ladder + §15.A.1 wording + LoRA disposition after verdict |
| **07** | Registry rows (REQUEST below), PROGRAM_STATE, honest acceptance layers |

---

## 11. Registry REQUEST rows (Lane 07 — do not edit TSV here)

| Artifact | Kind | Notes |
|----------|------|-------|
| `docs/specs/MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md` | NEW singleton | This file |
| `schemas/manga/character_capture_manifest.schema.json` | NEW schema | Draft-07 |
| `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §19 + §4.6 claim | EDIT in place | Surgical pointer |
| `artifacts/coordination/handoffs/manga_video_pose_bank_lane03_2026-07-24.md` | Handoff | Coordination |

---

## 12. Non-goals

- No assembler changes; no `config/manga/` wiring; no `check_manga_wiring` surface
- No V5 ratification; no fixed pose atlases; no treating DashScope frames as REAL
- No standing DashScope pipeline — one-time free-quota pilot only, then Pearl Star scale

— end of MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC v1.0.0 —
