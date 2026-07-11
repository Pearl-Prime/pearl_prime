# MANGA CANON SCENE-ASSEMBLY CHECKLIST — CLOSEOUT 2026-07-11

**Agent:** Pearl_Architect
**Workstream:** `ws_manga_canon_scene_assembly_checklist_20260711`
**Project:** `proj_manga_first_ship_20260425`
**Subsystem:** `manga_pipeline`
**Mode:** EXECUTE
**Acceptance layer:** authored candidate (SPECCED) — not system-working / not PROVEN-AT-BAR

---

## Landing identity

| Key | Value |
|-----|-------|
| HEAD_BEFORE | `2d9ada1e217e5c14ab0e7811425dd4176bac4e6c` |
| ORIGIN_MAIN | `98187a46982d758601defa322c273ec459742293` |
| LANDING_COMMIT | *(filled in CLOSEOUT_RECEIPT after land)*
| current branch (operator worktree) | `agent/ws-manga-true-layered-webtoon-proof-20260710` |
| HEAD detached? | no (`refs/heads/agent/ws-manga-true-layered-webtoon-proof-20260710`) |
| expected workstream branch | `agent/ws-manga-canon-scene-assembly-checklist-20260711` |
| branch-authority source | Golden Branch Pattern (`CLAUDE.md` / Pearl_GitHub): new agent lane from `origin/main`; workstream ID absent from `ACTIVE_WORKSTREAMS.tsv` at startup — branch created at `origin/main` |
| direct commit to operator worktree branch authorized? | **no** (unrelated feature branch + dirty-tree poison) |
| landing method | clean branch + index plumbing commit (operator dirty paths untouched) |

---

## Discovery matrix

| Question | Live evidence inspected | Current truth | Conflict or stale claim found | Effect on checklist |
|----------|-------------------------|---------------|-------------------------------|---------------------|
| Canonical singleton exists? | `git ls-tree -r origin/main --name-only` + `git grep` for scene-assembly checklist / `manga-scene-checklist=` under `artifacts/qa`+`docs` | **No** prior checklist singleton on `origin/main` | None | **Author new** `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md` |
| Authority status of 2026-07-09 readability rules? | `git show origin/main:artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` blob `55378b7ad4118ab212747a8b0eeb1ee3c0ebe011`; JSON companion present | Was acting as de-facto scene-assembly prose (HR-U\* / HR-F\*) | **HR-U02** universal horizon-ratio scale conflicts with operator doctrine + `SCALE-001` | **superseded** — preserve file, add pointer to new canon |
| Format currently governing delivery? | `git show origin/main:config/manga/format_routing.yaml` — `master: color_vertical_webtoon` defaults; `bw_page_manga` flatten | Primary **webtoon_vertical**; page-grid is flatten/export | Treating page-grid framing as default would be stale | Checklist `format_mode=both` with webtoon primary + page-grid overlay |
| Open PR owns checklist/closeout/prior? | `gh pr list --search` for canon/HR paths = `[]`; non-catalog open PRs scanned for exact paths = **none** | Clear to land | None | Proceed |
| What code governs planning/assembly/validation? | blobs on `origin/main`: `panel_planning_rules.py` `b273ccac…`, `validate_chapter_composition_grammar.py` `fb390a2e…`, `annotate_l2_composition_legal.py` `36ee0859…`, `assemble_from_bank.py` `c4afb2dd…`, `generate_assembly_manifest.py` `dc2ba8de…`, `composition_grammar.py` `476f89c7…` | Live: G1 half-person planning; G2 angle_bucket; **G3 horizon scale**; G4 contact shadow bool; G8 azimuth; chapter grammar + HR-U16 re-establish | G3 universal horizon ≠ canon SCALE-001 | Document as implementation debt; do not canonize |
| Asset metadata lighting/rendering compatibility? | `annotate_l2_composition_legal.legality_fields` (crop legality only); G8 azimuth in grammar | Partial: azimuth when sidecars; **no** rendering-band schema | Prior prose overclaims tone gates | TONE-001 / LIGHT-001 hybrid; tone schema unbound |
| Manifest contact-shadow solution? | `generate_assembly_manifest` sets `grounding.contact_shadow: True`; assembler `render_contact_shadow_layer` | Boolean + procedural layer — **not** full EDGE-001 inspectable schema | Treating bool as full EDGE-001 machine pass would be stale | EDGE-001 hybrid; schema unbound |
| Scale validation method? | `assemble_from_bank._grammar_l2_composite` → `plan_horizon_scale_paste` / `g3_horizon_scale_check` (eye_level_y_pct horizon math) | **Universal horizon shortcut in code** | Conflicts with SCALE-001 | Canon rejects universal law; next lane retargets grammar |
| Delivery-size readability tested? | rg delivery/thumbnail/360 in assembler/planner — no hits | **Not** automated | None | READ-001 operator until harness |
| Camera compatibility matrix exists? | rg compatibility_matrix / camera_height_class pairings — only `g2_angle_bucket` | **implementation_unbound** | None | CAMERA-001 unbound |
| Thresholds authority-bound vs unbound? | No config keys bound for eye-height tolerance / transform max / tone delta in this lane | Nearly all numeric thresholds **implementation_unbound** | Prior HR-U02 implies tolerances without THRESHOLD-001 | THRESHOLD-001 register in checklist |
| Workstream row present? | `rg ws_manga_canon_scene_assembly_checklist_20260711 artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` | **Absent** | Coordination dirty/operator-owned — not edited this lane | Branch named to workstream ID; registry update deferred (dirty-tree) |
| Positive proof on origin/main? | `git rev-parse origin/main:…/true_L0_L2_L3_composite.png` fails; file exists on disk in operator tree | Local untracked proof packet; operator-accepted | None for checklist authority (path mandated + pixels inspected) | Cite path + SHA-256; status verified |

---

## Positive-anchor visual inspection

**Path:** `artifacts/qa/manga_true_layered_webtoon_proof_2026-07-10/true_L0_L2_L3_composite.png`
**Status:** `verified` (operator verdict + pixel inspection; no material contradiction requiring BLOCKER)

| File | SHA-256 | WxH | Modes inspected |
|------|---------|-----|-----------------|
| `L0_background_source.png` | `3a00081bd0d9c51bf375fee060437c779db4f1dfa8a392aac904cccba3d8b855` | 1024×1536 | full_resolution, delivery_size(400), diagnostic_thumbnail(~27%) |
| `L2_character_keyed.png` | `ff965e999112c43ce1a5d4ac84c212569eff7959a5f6d5b77728f57d2fe1a59f` | 267×860 | full_resolution, delivery, thumb |
| `L3_foreground_keyed.png` | `5595c9b5a4c8a36dc6747154c2582cea7ba9332c08a8d9ea4ca5f3035b295497` | 686×1080 | full_resolution, delivery, thumb |
| `true_L0_L2_L3_composite.png` | `29c4f81ddb485e74aeb7274dc30de6888904648d5a469a3441a14ab5d228129a` | 1024×1536 | full_resolution, delivery, thumb |
| `proof_sheet.png` | `71386292f26ada50ea04aabea93d791108f48dfe07e76efb7401691ac9410121` | 1800×1460 | full_resolution, delivery, thumb |

**Observed:** full-body L2 on readable hangar floor; L3 rail nearer-plane occlusion; soft contact under boots at full-res/proof_sheet; integrated lighting. Delivery-size contact reads softer — recorded under EDGE-001 evaluability, does **not** overturn operator accept.

**ENV-001 classification preview:** operator delivery inspection at ~400px width on proof 1024-wide plate (`implementation_unbound` formal CSS profile).
**READ-001 diagnostic preview:** ~27% thumb (276×414 on composite).

---

## Stillness anchors inspected

| Role | Path | origin/main blob | SHA-256 (bytes) | WxH |
|------|------|------------------|-----------------|-----|
| Accepted establishing | `artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/panels/ep001_016.png` | `5410098cdb152f014bd02d29c4414ef5f3d59d84` | `287dad5a13ce123164a66489356dc5639497c85d89ceacff6e23d4333f2d5e68` | 1080×1920 |
| Rejected floating knees-up | `…/panels/ep001_008.png` | `4a86d38a111c76155ea5a0721658a4731265e626` | `22d60d21f2abbb8b5c4bbf90636a9d996f8d7e1027caf71ee758c48286256a82` | 1080×1920 |
| Rejected bust-over-room | `…/panels/ep001_005.png` | `6d503fdfbb91cacd7fcd73e263b0b3dd96c9effe` | `7aa12a2d9b1a545ff7ca1e11e5066094138e3882459fc523ed9d0521f5aac40a` | 1080×1920 |

All three inspected at full_resolution, delivery(~400×711), and diagnostic thumb(~291×518).

---

## Artifact landing

| Field | Value |
|-------|-------|
| Canonical path | `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md` |
| Mode | **new** |
| Prior authority | `artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` → **superseded** (pointer banner added in place) |
| Closeout | `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST_CLOSEOUT_2026-07-11.md` |
| Format mode tag | `both` |

### Rule IDs authored
PLAN-001, ENV-001, L0-001, L2-001, CAMERA-001, SCALE-001, THRESHOLD-001, CROP-001, CROP-002, CROP-003, CROP-004, GROUND-001, GROUND-002, OCCLUDE-001, LIGHT-001, TONE-001, EDGE-001, TRANSFORM-001, READ-001, ACCEPT-001, SEQ-001, CONT-001, CONT-002, CONT-003, RHYTHM-001, RHYTHM-002, RHYTHM-003, FAIL-LIGHT-001, FAIL-TONE-001, FAIL-EDGE-001, FAIL-SCALE-001

### Gates present
- lighting-gate: **present** (LIGHT-001 / FAIL-LIGHT-001)
- tone-gate: **present** (TONE-001 / FAIL-TONE-001)
- contact-shadow-gate: **present** (EDGE-001 / FAIL-EDGE-001)
- delivery-size-gate: **present** (READ-001)
- camera-matrix: **implementation_unbound**

### Missing thresholds (implementation_unbound)
eye-height tolerance; camera-class adjacency table; lighting-direction slack; rendering-band delta; tone-density tolerance; max uniform scale; max rotation; formal webtoon CSS delivery profile authority.

---

## Next implementation lane

- **First code file:** `scripts/manga/composition_grammar.py` (`g3_horizon_scale_check`, `plan_horizon_scale_paste`)
- **Rule IDs:** SCALE-001, CAMERA-001, THRESHOLD-001, CROP-001, GROUND-001, GROUND-002, EDGE-001
- **First proof packet rerun:** `artifacts/qa/manga_true_layered_webtoon_proof_2026-07-10/` + stillness `ep001_016` / `ep001_008` / `ep001_005`

---

## Evidence appendix

| # | Command/tool | Object | Exact result |
|---|--------------|--------|--------------|
| 1 | `git fetch origin main` | remote main | FETCH_EXIT 0; `origin/main`=`98187a46982d758601defa322c273ec459742293` |
| 2 | `git rev-parse HEAD` | operator worktree | `2d9ada1e217e5c14ab0e7811425dd4176bac4e6c` |
| 3 | `git branch --show-current` | operator worktree | `agent/ws-manga-true-layered-webtoon-proof-20260710` |
| 4 | `git symbolic-ref -q HEAD` | operator worktree | `refs/heads/agent/ws-manga-true-layered-webtoon-proof-20260710` (not detached) |
| 5 | `git status --porcelain` on target paths (pre-write) | checklist/closeout/HR rules | empty / targets absent — **not dirty** |
| 6 | `git ls-files -m` (sample) | operator tree | many operator-owned modified paths (coordination, docs, audio, manga fixtures…) — **untouched** |
| 7 | `git ls-tree -r origin/main` + grep | checklist singleton search | **no** `MANGA_CANON_SCENE_ASSEMBLY` / `manga-scene-checklist=` hits |
| 8 | `git show origin/main:docs/agent_brief.txt` | landing contract §17 | defines MERGED or BLOCKED+push; this lane commits on workstream branch (push/PR per §17 after local land) |
| 9 | `git show origin/main:docs/PROGRAM_STATE.md` | manga track | vision-certified; bank assembly landed; stillness proof historically blocked then gap packet EXECUTED-REAL on main packet paths |
| 10 | `gh pr list --search` + non-catalog file scan | open PR ownership | **no** hits on checklist/closeout/HR rules paths |
| 11 | Read tool on copied PNGs under `/tmp/manga_scene_checklist_inspect_20260711/` | positive+negative pixels | facts recorded in checklist mapping section |
| 12 | `git show origin/main:scripts/manga/assemble_from_bank.py` L189–260 | `_grammar_l2_composite` | uses `plan_horizon_scale_paste` + `render_contact_shadow_layer` |
| 13 | `git show origin/main:scripts/manga/composition_grammar.py` L206–226 | `g3_horizon_scale_check` | horizon-ratio / eye_level_y_pct law |
| 14 | `git show origin/main:config/manga/format_routing.yaml` | defaults | `color_vertical_webtoon` master |
| 15 | Existence | stillness packet panels on `origin/main` | ep001_005/008/016 present (blobs above) |
| 16 | Existence | true layered proof on `origin/main` | **absent**; on-disk local path inspected |

### Revision fingerprints (load-bearing)

| Path | Ref | Blob / content hash |
|------|-----|---------------------|
| `artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` | `origin/main` (pre-edit) | `55378b7ad4118ab212747a8b0eeb1ee3c0ebe011` |
| `scripts/manga/panel_planning_rules.py` | `origin/main` | `b273ccac257fa2236ddfe140009272c3809ff003` |
| `scripts/manga/validate_chapter_composition_grammar.py` | `origin/main` | `fb390a2e99230897d17d009803041ca0ca058753` |
| `scripts/manga/annotate_l2_composition_legal.py` | `origin/main` | `36ee0859efd82b739d3cb3e13e1dfe84fe06e983` |
| `scripts/manga/assemble_from_bank.py` | `origin/main` | `c4afb2dd9396a01d2532a8a4b1c47d2a87032523` |
| `scripts/manga/generate_assembly_manifest.py` | `origin/main` | `dc2ba8dea5530055e0b7b0a0746c3b32cb674cb6` |
| `scripts/manga/composition_grammar.py` | `origin/main` | `476f89c75a8549160e99957e7a9e3d65fc3fd2d2` |
| `artifacts/research/MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md` | `origin/main` | `c4c0b44f80e5ff682f4108ea4a611ceb7310fca9` |
| `artifacts/research/manga_genre_prompting_system_2026-07-10.json` | `origin/main` | `f577d4d2e329a42055fdc7d9a9ce1f3600fd022c` |
| true composite PNG | on-disk inspect | SHA-256 `29c4f81ddb485e74aeb7274dc30de6888904648d5a469a3441a14ab5d228129a` |

---

## Dirty-tree safety ledger

- Pre-write: target checklist/closeout **absent** (not dirty).
- Operator-owned modified/untracked paths in shared worktree: **not staged, not restored, not deleted**.
- Staged/committed paths: only workstream-authored checklist, closeout, and superseded-pointer update to HR rules.

---

## Required tags

```
manga-scene-checklist=artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md
manga-scene-checklist-mode=new
manga-scene-checklist-format-mode=both
manga-scene-checklist-prior-authority-status=superseded
manga-scene-checklist-positive-anchor=artifacts/qa/manga_true_layered_webtoon_proof_2026-07-10/true_L0_L2_L3_composite.png
manga-scene-checklist-positive-anchor-status=verified
manga-scene-checklist-negative-anchor=artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/panels/ep001_008.png;artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/panels/ep001_005.png
manga-scene-checklist-current-branch=agent/ws-manga-true-layered-webtoon-proof-20260710
manga-scene-checklist-workstream-branch=agent/ws-manga-canon-scene-assembly-checklist-20260711
manga-scene-checklist-environment-classification-preview=implementation_unbound (operator used ~400px delivery on proof 1024w / stillness 1080w)
manga-scene-checklist-lighting-gate=present
manga-scene-checklist-tone-gate=present
manga-scene-checklist-contact-shadow-gate=present
manga-scene-checklist-delivery-size-gate=present
manga-scene-checklist-camera-matrix=implementation_unbound
manga-scene-checklist-thresholds=mostly_implementation_unbound (eye-height/transform/tone/delivery-profile unbound; G8 azimuth partial)
manga-scene-checklist-next-action=scripts/manga/composition_grammar.py — enforce SCALE-001/CAMERA-001/THRESHOLD-001/CROP-001/GROUND-001/GROUND-002/EDGE-001; rerun true_L0_L2_L3 proof + stillness ep001_016/008/005
manga-scene-checklist-closeout=artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST_CLOSEOUT_2026-07-11.md
manga-scene-checklist-blocker=none
```

---

## STATUS

**LANDED** — canonical checklist authored; prior HR rules superseded in place with pointer; dirty-tree protocol held.
