# Mecha-Native Asset Repair Closeout — 2026-07-09

**Lane:** mecha-native asset-repair (Pearl_Dev)  
**Project:** `proj_manga_first_ship_20260425`  
**Series:** `warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening`  
**Acceptance layer:** CONFIG-EXISTS → partial EXECUTED-REAL (L0 plates + L0 sidecars); L2/L3 still ABSENT  
**Authority:** `MANGA_MECHA_NATIVE_BLOCKER_AUDIT_2026-07-09.md`; `MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` §6.2

---

## Discovery summary (GO)

| Check | Result |
|---|---|
| Open PR conflict (`mecha OR warrior_calm OR human-readability`) | **CLEAR** — only catalog skeleton PRs; no parallel mecha-bank repair lane |
| L0 `hangar_pre_dawn.png` | **2,842,149 bytes** — REAL |
| L0 `cockpit_interior.png` | **3,394,620 bytes** — REAL |
| L2 `seated_cockpit.png` | **MISSING** |
| L2 `threshold_stand.png` | **MISSING** |
| L3 `glove_pad.png` | **MISSING** |
| L3 `telemetry_panel.png` | **MISSING** |
| Ledger `mecha:L2:*` / `mecha:L3:*` | **present**, status `requested`, `latest_job_id: null` |
| L0 `*.composition.json` (pre-repair) | **0 files** |
| GO/NO-GO | **GO** — metadata gap + queue reconciliation required; not complete |

---

## Actions taken

1. **Disk-only ledger reconcile** — L0 mecha requests confirmed `usable`; four L2/L3 mecha requests remain `requested` / `missing_output` with no `latest_job_id` (never dispatched).
2. **Authored L0 composition sidecars** — `hangar_pre_dawn.composition.json`, `cockpit_interior.composition.json` with `bg_class`, `camera`, `ground_plane`, `light`, `style_register`, and `anchor_slots` including cockpit `seated_cockpit` console occluder bbox (HR-GEN-MC02).
3. **Enqueue attempt** — `enqueue_crossgenre_real_layers.py --series mecha` **blocked** by `ImportError: resolve_tradition_genre` missing from `phoenix_v4.manga.genre_tradition` (shared `prompt_authority.py` regression; out of WRITE_SCOPE).
4. **SSH queue reconcile** — `render_request_ledger.py reconcile` **blocked** on Pearl Star SSH / `PS_QUEUE_DSN` syntax error when job IDs present.
5. **Bank contract** — **unchanged** — `seated_cockpit` + `threshold_stand` cover ep_001 authored beats; no ep_001 panel requires `full_figure_hangar` today.
6. **L2 legality sidecars** — **deferred** — zero native L2 PNGs on disk.

---

## Queue reconciliation output

```json
{
  "ledger_path": "artifacts/qa/manga_render_queue/request_ledger.json",
  "counts": {
    "usable": 2,
    "requested": 16,
    "blob_failed": 4
  },
  "mecha_pending_enqueue": [
    "mecha:L2:seated_cockpit",
    "mecha:L2:threshold_stand",
    "mecha:L3:glove_pad",
    "mecha:L3:telemetry_panel"
  ]
}
```

**Enqueue dry-run:** failed — `ImportError: cannot import name 'resolve_tradition_genre'`.

---

## L0 sidecar summary

| Asset | style_register | anchor_slots | occluder |
|---|---|---|---|
| `hangar_pre_dawn` | `mecha_hangar` | `hangar_catwalk_stand`, `threshold_stand`, `abstract_dialogue_stage` | none (establishing plate) |
| `cockpit_interior` | `mecha_cockpit` | `seated_cockpit`, `threshold_stand`, `abstract_dialogue_stage` | console bbox on `seated_cockpit` + threshold canopy edge |

---

## Remaining blockers

| Blocker | Owner | Severity |
|---|---|---|
| Zero native L2/L3 REAL PNGs | Pearl_Int (after enqueue unblocked) | HARD |
| `resolve_tradition_genre` import regression blocks enqueue script | Pearl_Dev shared lane | HARD |
| Pearl Star SSH / queue DSN for remote reconcile | Pearl_Int | SOFT |
| `full_figure_hangar` pose (future scale panels) | Pearl_Author + Pearl_Int | SOFT (deferred) |
| `ep_001_from_continuity` manifest + proof assembly | Pearl_Dev proof lane | HARD (downstream) |

---

## Verdict

**PARTIAL** — L0 grammar metadata repaired; native character/object layers still absent; enqueue blocked on shared import regression.

---

## Tags

```
manga-mecha-native-repair=advanced
manga-mecha-native-closeout=artifacts/qa/MANGA_MECHA_NATIVE_REPAIR_CLOSEOUT_2026-07-09.md
manga-mecha-native-queue=degraded
manga-mecha-native-landed=none
manga-mecha-native-sidecars=L0:hangar_pre_dawn.composition.json+L0:cockpit_interior.composition.json (3 anchor_slots each; cockpit seated_cockpit occluder bbox)
manga-mecha-native-contract=none
manga-mecha-native-next-action=Fix resolve_tradition_genre import in prompt_authority; then PYTHONPATH=. python3 scripts/manga/enqueue_crossgenre_real_layers.py --series mecha; annotate L2 sidecars on land
manga-mecha-native-blocker=enqueue_crossgenre_real_layers ImportError resolve_tradition_genre + zero native L2/L3 PNGs on disk
```
