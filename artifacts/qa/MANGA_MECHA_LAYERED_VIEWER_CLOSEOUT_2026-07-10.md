# Mecha Layered Viewer Closeout — 2026-07-10

**Lane:** mecha layered proof-viewer packet (Pearl_Dev)  
**Project:** `proj_manga_first_ship_20260425`  
**Acceptance layer:** system working (exact panel-level L0+L2 hero; not PROVEN-AT-BAR)

---

## Discovery report

| Check | Result |
|---|---|
| `origin/main` SHA | `4067366556fedfd99913fbd3806d78af53d32b5a` |
| Open PR overlap | **CLEAR** — no open PR owns mecha layered packet lane |
| Bank images (real bytes) | **ALL PRESENT** after LFS checkout — L0×2, L2×2, L3×2 |
| Assembled strip | **PRESENT** — `ep_001_from_continuity_strip.jpg` (2,931,382 bytes) |
| `_provenance.json` panel mapping | **YES** — exact per-panel layer records for all 8 panels |
| Hero candidate | **ep001_003** — L0 `cockpit_interior` + L2 `seated_cockpit` (2-layer stack) |
| Prior packet path | None for mecha; stillness packet at `manga_reading_packets_2026-07-09/` is separate lane |
| Artifact-only lane | **YES** — no pipeline code touched |

## Hero mapping type

**exact_panel_level** — provenance JSON + assembly manifest agree on L0+L2 sources for `ep001_003`.

## Source files shown in packet

- `image_bank/L0/cockpit_interior.png`
- `image_bank/L2/seated_cockpit.png`
- `assembled/ep_001_human_readability_proof/ep001_003.png`
- `assembled/ep_001_human_readability_proof/ep_001_from_continuity_strip.jpg`
- All 8 proof panels + 6 bank reference plates

## Cleanup ledger

| Item | Action |
|---|---|
| LFS checkout side effect | Local working tree had LFS smudge skip; `git lfs checkout` run for build only — not committed |
| Temp build script | Inline Python only; no temp files left |
| Branch scope | Packet artifacts only under `artifacts/qa/` |
