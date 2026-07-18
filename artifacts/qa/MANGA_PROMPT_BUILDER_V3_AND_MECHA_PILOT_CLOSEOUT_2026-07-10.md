# Manga Prompt Builder V3 + Mecha Layered Pilot Closeout — 2026-07-10

**Agent:** Pearl_Dev  
**Lane:** `ws_manga_prompt_builder_v3_20260710`  
**Project:** `proj_manga_first_ship_20260425`  
**Acceptance layer:** system working (cookbook wired + blob gate v2 + Qwen pilot EXECUTED-REAL; not PROVEN-AT-BAR)

---

## Discovery receipt

| Check | Result |
|---|---|
| Open PR overlap | None on prompt-builder v3 / blob gate / mecha rerender write scope |
| Active workstream overlap | None active; prior mecha lanes completed |
| Research SHA on `origin/main` | `12799deabe294baf1d9da00305c2a3d43620d946` CONFIRMED (#5488) |
| `genre_prompt_cookbook.yaml` pre-lane | MISSING — authored from JSON |
| Strip proof (`ep_001_from_continuity_strip.jpg`) | LFS pointer locally; prior strip claim SUPERSEDED |
| `seated_cockpit.png` pre-lane | Real bytes but stipple blob (v1 gate PASS, visual FAIL) |

---

## Landed capability

| Deliverable | Path / evidence |
|---|---|
| Manga-panel cookbook (26 genres) | `config/manga/genre_prompt_cookbook.yaml` |
| Prompt authority v3 (5-slot, Qwen-primary) | `scripts/manga/prompt_authority.py` |
| Genre tradition cookbook hooks | `phoenix_v4/manga/genre_tradition.py` |
| Blob gate v2 (stipple white-plate heuristic) | `scripts/manga/bank_layer_blob_gate.py` |
| Regression fixtures | `tests/fixtures/manga/blob_gate/` |
| Blob gate proof JSON | `artifacts/qa/manga_blob_gate_regression_proof_2026-07-10.json` |
| Qwen queue worker (was stub) | `scripts/pearl_star/worker/qwen_manga_worker.py` |
| Direct Qwen ComfyUI helper | `scripts/manga/comfyui_qwen_panel_render.py` |
| Mecha layered pilot | `artifacts/qa/manga_layered_visual_proof_2026-07-10/mecha_master_wu_pilot/` |
| Bank layer replacement | L0 cockpit_interior, L2 seated_cockpit, L3 telemetry_panel — blob gate PASS |

---

## Visual pilot receipt

Operator visual inspect of `composite.png` (2026-07-10): readable seinen mecha cockpit interior, pilot in harness, orange HUD/console lighting, mecha line-art in upper register — **not** stipple noise. Acceptance: EXECUTED-REAL honest layered proof.

| File | Bytes | Blob gate |
|---|---:|---|
| L0.png | 3,614,713 | PASS (small_edge=19.83) |
| L2.png | 2,413,257 | PASS (small_edge=18.50) |
| L3.png | 2,881,567 | PASS (small_edge=18.24) |
| composite.png | 2,354,481 | PASS |

Render path: Qwen-Image ComfyUI @ `http://100.92.68.74:8188`, prompt-builder v3 scaffolds, seed 4242.

---

## Preserved bad blob

Quarantined before rerender: `image_bank/L2/_BLOB_FAIL/seated_cockpit__pre_rerender.png`  
Regression fixture: `tests/fixtures/manga/blob_gate/seated_cockpit_stipple_blob_20260708.png` — **FAIL** under v2 gate (`stipple_white_plate`).

---

## Tests

```
pytest tests/manga/test_prompt_authority.py tests/manga/test_bank_layer_blob_gate.py tests/manga/test_genre_tradition_wiring.py — 17 passed
```

---

## Cleanup ledger

| Item | Action |
|---|---|
| Branch | `agent/manga-prompt-builder-v3-20260710` |
| Workstream TSV | register at startup → close completed at merge |
| Stash | `research-lane-temp-stash` on prior branch — operator may pop |
| Queued jobs 586–588 | Enqueued pre-worker-fix; redeploy worker on Pearl Star to drain |
| Temp | none retained beyond proof + fixture paths |

---

## Tags

```
manga-prompt-builder-v3=<merge-sha>
manga-genre-cookbook=config/manga/genre_prompt_cookbook.yaml
manga-blob-gate-proof=artifacts/qa/manga_blob_gate_regression_proof_2026-07-10.json
manga-mecha-layered-pilot=artifacts/qa/manga_layered_visual_proof_2026-07-10/mecha_master_wu_pilot/
manga-mecha-layered-composite=artifacts/qa/manga_layered_visual_proof_2026-07-10/mecha_master_wu_pilot/composite.png
manga-mecha-layered-closeout=artifacts/qa/MANGA_PROMPT_BUILDER_V3_AND_MECHA_PILOT_CLOSEOUT_2026-07-10.md
manga-mecha-layered-blocker=none
```
