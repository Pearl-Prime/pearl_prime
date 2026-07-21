# Mecha Layered Proof Packet v1

**Status:** system working (native bank REAL + assembly + provenance mapping; not PROVEN-AT-BAR)  
**Series:** `warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening`  
**Episode:** ep_001 human-readability proof (8 exemplar panels)  
**Date:** 2026-07-10  
**Agent:** Pearl_Dev

## Acceptance layer

| Layer | Claim |
|---|---|
| CONFIG-EXISTS | assembly manifest + image bank sidecars |
| CODE-WIRED | `assemble_from_bank.py` + validators |
| EXECUTED-REAL | 8 assembled panels + continuity strip on disk |
| **This packet** | **system working** — operator can inspect exact layer stack for hero panel |
| PROVEN-AT-BAR | **NOT claimed** — no blind-judge certification |

## Hero panel — exact panel-level mapping

| Field | Value |
|---|---|
| Final panel | `assembled/ep_001_human_readability_proof/ep001_003.png` (packet copy: `hero_final_panel.png`) |
| Panel ID | `ep001_003` |
| Archetype | `character_quiet_face` / `dialogue_bust` |

### Exact source layers

| z | Class | Source file | Bytes | Provenance |
|---|---|---|---|---|
| 0 | L0 | `image_bank/L0/cockpit_interior.png` | 3,581,417 | REAL |
| 20 | L2 | `image_bank/L2/seated_cockpit.png` | 3,548,619 | REAL |

### How provenance established the mapping

1. **`assembled/ep_001_human_readability_proof/_provenance.json`** — records two entries for `panel_id: ep001_003`:
   - L0 → `cockpit_interior.png` at z=0
   - L2 → `seated_cockpit.png` at z=20
2. **`assembly_manifests/ep_001_from_continuity.yaml`** — panel block `ep001_003` lists the same assets with `anchor_slot: seated_cockpit`, `bbox_pct: [24, 18, 52, 62]`, and L0 `derivation: defocus`.
3. **Byte verification** — provenance byte counts match hydrated LFS objects on `origin/main`.

## What this packet proves

- Native mecha image bank REAL assets (L0/L2/L3) exist and assemble.
- At least one panel (`ep001_003`) has an **exact, auditable** L0+L2 layer stack.
- The continuity strip and 8 proof panels are viewable without pipeline rerender.

## What this packet does NOT prove

- Blind-read or PROVEN-AT-BAR quality bar.
- Full 35-panel continuity export (manifest is 8-panel exemplar only).
- That toggling L0+L2 in the HTML viewer pixel-matches the assembler output (viewer shows source plates; final toggle shows the real assembled PNG).

## Artifacts in this folder

| File | Role |
|---|---|
| `index.html` | Operator viewer with layer toggles |
| `layer_manifest.json` | Machine-readable layer stack + claim boundaries |
| `hero_final_panel.png` | Assembled ep001_003 |
| `hero_layer_stack.png` | L0 \| L2 \| => final visual proof sheet |
| `contact_sheet.png` | 4×2 grid of all 8 proof panels |
| `proof_grid.png` | Strip + hero stack explanation grid |
| `continuity_strip.jpg` | Full 8-panel strip |
| `layers/` | Hero source layer copies |
| `panels/` | All 8 assembled panel copies |
| `bank/` | Full native bank reference copies |

## Open locally

```bash
open artifacts/qa/manga_reading_packets_2026-07-10/mecha_layered_packet_v1/index.html
```

## Authority

- `artifacts/qa/MANGA_MECHA_HUMAN_READABILITY_PROOF_CLOSEOUT_2026-07-10.md`
- `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md`
- `assembled/ep_001_human_readability_proof/_provenance.json`
