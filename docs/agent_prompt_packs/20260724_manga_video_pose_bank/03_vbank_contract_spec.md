# Lane 03 — Pearl_Architect + Pearl_Dev — Video-Capture→Bank contract (spec + schemas)

EXECUTE. The turn ends only on `manga-video-pose-bank-spec-merged=<full merge SHA>` or one
concrete BLOCKER with pushed work.

GATE CHECK (verifiable signals, not narrative): `dashscope-free-media-landed=<sha>` AND
`manga-video-capability-research-merged=<sha>` both exist on merged PRs/handoffs. If either is
missing, STOP and surface — do not start early.

STARTUP_RECEIPT: AGENT=Pearl_Architect(+Pearl_Dev), SUBSYSTEM=manga_pipeline,
WRITE_SCOPE=`docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` (new § — edit in place, singleton),
`schemas/manga/character_capture_manifest.schema.json` (NEW),
`docs/specs/MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md` (NEW — the supply-lane spec), handoff.
OUT_OF_SCOPE=`docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (registry NO-without-ratification —
NOT edited; this is a bank SUPPLY lane, not an architecture variant), all code, gate_registry.
PROVENANCE: research=Lane 02 doc + `old_chat_specs/Untitled 411.txt` (verified subset only);
documents=MANGA_LAYER_RENDER_CONTRACT_SPEC v0.7.2, MANGA_COMPOSITION_GRAMMAR_SPEC,
CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02 (read-only); builds_on=manga_bank_assembler,
manga_assembly_manifest_schema, manga_bank_contract_generator, character_pose_inventory
convention (registry concept keys — all EXTEND in place); inventory=EXTENDS.

## Read first
`docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` (§4 layer taxonomy + §4.6 namespace rule —
animation derivatives claim A0–A9 IDs; §5 safe zones; §6.3.A + §6.8 pose inventory + cardinality
budget; §9 cutout policy; §12.3 class-A gates; §15.A.2 identity gate);
`schemas/manga/assembly_manifest.schema.json` + `composition_meta.schema.json`;
`scripts/manga/make_object_sprite.py` (the INTERIM-sprite precedent — your ingest pattern);
`scripts/manga/generate_bank_contracts_from_script.py`;
`docs/agent_prompt_packs/20260724_manga_process_uplift/09_bank_demand_rollup.md` (the
`series_demand_rollup.yaml` contract this spec's compiler consumes);
Lane 02's research doc RECOMMENDATIONS; the pack INDEX grounding table.

## Mission — spec the whole supply lane so Lane 04 implements without design decisions

**1. `MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md`** (the authority for this lane), covering:
- **Demand→capture compilation:** input = `series_demand_rollup.yaml` (uplift Lane 09) when
  `manga-bank-demand-rollup-merged` exists; fallback input = per-episode
  `bank_contracts/character_pose_inventory.yaml` + the series master plan golden. Output = a
  **character capture manifest** (one per character × outfit): action families (dialogue /
  locomotion / seated / genre pack), one short clip per family entry, each clip prompt built for
  comic-readable key poses (staged anticipation/impact/follow-through, locked camera, full body
  in frame, flat neutral high-contrast background, single character, no props unless demanded).
  Only DEMANDED pose_ids drive clips — §6.8 cardinality budget applies at the OTHER end too:
  curation selects the smallest sufficient set, never "keep all frames".
- **Anchor policy:** canonical anchors come from the EXISTING identity machinery (PuLID reference
  sheets / model_sheets / Pearl Star Qwen-Image renders) — cloud still-quota is NOT spent on
  anchors. Every clip in a capture manifest names its anchor asset + outfit_id; identity is
  anchored per-clip (i2v from the same anchor; r2v/VACE-reference when available per Lane 02).
- **Frame pipeline gate chain (ordered, each a named gate):** extract candidates (sampling rate
  per Lane 02) → near-duplicate cluster/dedup → pose-phase classification → cutout (ToonOut/
  rembg per existing backends) → class-A §12.3 gates (rembg_clean_alpha, coverage, bleed,
  safe-zone) → `bank_layer_blob_gate` → `qa_face_distance` vs anchor (pairwise ≤0.4 per M5 bar) →
  outfit-conformance check vs outfit reference → curation to demanded pose_ids → sidecars
  (`.provenance.json` naming source clip + frame index + extraction command + REAL-replacement
  path; `.composition.json` with anchor.y_px + figure_height_m) → pose-inventory registration.
  A frame that fails any gate is REJECTED, never repaired downstream.
- **Provenance rules (Q-VBANK-03 default):** DashScope-derived assets = INTERIM permanently,
  `_INTERIM` suffix + provenance_note per the make_object_sprite pattern; self-hosted
  Apache-2.0-weights output = REAL-eligible after the full gate chain. Assets enter panels ONLY
  via `assembly_manifest.schema.json` layer objects — the assembler is NOT modified.
- **Namespace claim:** motion-source artifacts (clips, contact sheets) claim IDs in the reserved
  A0–A9 animation namespace per §4.6 and the table is updated; extracted still layers remain
  ordinary L2/L3 assets.
- **Identity-ladder draft** (ratified in Lane 06, drafted here): PuLID + capture-bank = primary;
  per-character LoRA = last-resort, not planned. State the §15.A.2 wording change this implies.
- **Quota + sunset economics:** cloud budget table (seconds per family, reserve), self-hosted
  scale posture per Lane 02's matrix, RAP queue-first for all Pearl Star work.

**2. `character_capture_manifest.schema.json`** — JSON Schema for the manifest: character_id,
identity_version, outfit_id, anchor asset paths, capture_sets[] (family, clip_id, prompt,
duration_s, engine, anchor_mode i2v|r2v|vace|t2v, demanded_pose_ids[]), quota_budget. Validate
the golden example you include in the spec against it in CI-runnable form (a tests/ fixture is
Lane 04's job; here the schema + example must at least `python -c json.load`-parse and be
mutually consistent).

**3. New § in `MANGA_LAYER_RENDER_CONTRACT_SPEC.md`** — a compact cross-reference section
(supply-lane pointer, A-namespace claim, provenance rules) that DEFERS to the new supply spec.
Edit in place; do not renumber existing sections; keep the diff surgical.

DISCOVERY REPORT before writing (verify every extension point still looks as described — the
uplift program is moving fast). Reuse-first: every artifact above is either a registry singleton
edited in place or a genuinely new file carrying `NEW-ARTIFACT-JUSTIFIED` + its own registry row
REQUEST in your closeout (Lane 07 lands registry rows — do not edit the registry TSV yourself).

## DO NOT
- No code, no configs under `config/manga/` (avoids check_manga_wiring surface entirely).
- No edits to V5 architecture doc, gate_registry, assembler, or any uplift-pack deliverable.
- No fixed-12 / hardcoded pose lists — everything demand-derived.

## Landing contract
MERGED (docs+schema PR via plumbing; staged-diff gate; checks named) or BLOCKED with pushed
branch. Cleanup ledger. Handoff:
`artifacts/coordination/handoffs/manga_video_pose_bank_lane03_2026-07-24.md`.
CLOSEOUT_RECEIPT + `SIGNAL: manga-video-pose-bank-spec-merged=<full merge SHA>`.
