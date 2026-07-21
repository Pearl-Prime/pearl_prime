# Flagship Current-Main Preview — Chapters 1–3

**Pack date:** 2026-07-09  
**`origin/main` SHA:** `9f19951627bcca72db4fb60999cb559c0a88ddf1`  
**Source:** current-main rebuild (byte-identical to ratified golden)  
**Parity:** byte-identical (`sha256` `88fcff84f9d889226dc35e00acca5a215519395621200fc55abb580d5853959d`)

---

## 1. What this is

This directory is an operator-readable evidence pack showing **what the merged Pearl Prime book system produces today** for the flagship cell (`gen_z_professionals` × `anxiety`, arc F006, `extended_book_2h`).

- **Rebuild vs golden:** A fresh pipeline rebuild was run on `origin/main` at `9f19951627bcca72db4fb60999cb559c0a88ddf1`. The output is **byte-identical** to the ratified full-book golden (`artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt`). Chapters 1–3 in this pack are slices of that rebuild, not hand-authored prose.
- **Invocation:**

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic anxiety \
  --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --pipeline-mode spine \
  --runtime-format extended_book_2h \
  --quality-profile production \
  --exercise-journeys \
  --no-job-check \
  --render-book \
  --render-dir <render_dir> \
  --seed flagship_phase2_layer6
```

---

## 2. Why this is the right example

Per `docs/PROGRAM_STATE.md` on `origin/main`, the flagship book is **PROVEN-AT-BAR** (OPD-20260707-FLAGSHIP-L4, Layer-4 blind-read approved). It is the strongest real 12-chapter book artifact in the repo:

- Seed: `flagship_phase2_layer6`
- Format: `extended_book_2h` (twelve-shape doctrine)
- Both CH1 and full-book goldens are live and CI-enforced via `check_flagship_book_parity.py`
- July 9 merges on main were manga / ops / gate / PM-state work — **not** a new flagship prose rewrite

This pack answers: *"What does current main actually produce?"* — not an aspirational future book.

---

## 3. What you are seeing in Chapters 1–3

| Ch | Title | Words (approx) | Notes |
|---:|---|---:|---|
| 1 | Chapter 1 | 1245 | Hook: Slack-send confirmation loop. Priya scene (bedroom/doc). Protective-alarm angle definition. Sensation/story seam reflection. Noting exercise (`med_007`). Three story_plan beats (recognition → mechanism proof → turning point). Integration: 11pm Slack-off alarm practice. THREAD bridges to Ch2. |
| 2 | Chapter 2 | 1630 | Hook: Sunday-night calendar dread. Weather vs climate doctrine. Priya calendar-spiral scenes (Sunday couch → Monday kitchen). Cyclic sighing exercise. Empty-block practice integration. THREAD bridges to Ch3 shoulder tension. |
| 3 | Chapter 3 | 1547 | Hook: shoulders braced since Tuesday. Nervous-system pattern / somatic scoring. Priya body-held tension scenes. Exercise + integration carry naming-tension practice forward. THREAD sets up pre-meeting activation (Ch4). |

**Visible merged features in these chapters:**

- Spine pipeline with production quality profile + exercise journeys
- Twelve-shape story_plan arcs (recognition / mechanism_proof / turning_point per chapter)
- Persona atoms (HOOK, SCENE, PIVOT, TAKEAWAY, INTEGRATION, THREAD) with `persona_alarm_behavior` enrichment
- Composite doctrine + teacher_voice enrichment on REFLECTION/INTEGRATION slots
- Practice library exercises with `somatic_exercise` enrichment
- Chapter flow gate PASS on all three; register gate ADVISORY (F6=1 book-wide)

---

## 4. How it was assembled

Slot mapping is derived from **`selected_content_variants.json`** (primary trace surface). No hand reconstruction.

### Load-bearing sources


- **Ch1 HOOK/SCENE:** persona_atom `HOOK v89` + `SCENE v83` with `persona_alarm_behavior` — opens Priya Slack-send loop
- **Ch1 doctrine:** composite_doctrine `COMPOSITE_DOCTRINE v03` — sensation/story seam reflection
- **Ch1 exercise:** practice_library `med_007` (noting practice) via somatic_exercise enrichment
- **Ch1 stories:** story_plan twelve_shape ch1 recognition/mechanism_proof/turning_point arcs
- **Ch2 angle:** angle_atom `angle_def:PROTECTIVE_ALARM` continuation + calendar-spiral persona scenes
- **Ch2 exercise:** practice_library cyclic sighing pick with somatic_exercise enrichment
- **Ch3 somatic thread:** persona_atom SCENE/STORY slots carrying shoulder-bracing through-line

### Slot-by-slot table (Chapters 1–3)

| Chapter | Slot | Source | Source ID | Atom ID | Enrichment | Target | Actual |
|---|---|---|---|---|---|---:|---:|
| 1 | HOOK | persona_atom | `HOOK v89` | `HOOK v89` | persona_alarm_behavior | 476 | 50 |
| 1 | ANGLE_DEFINITION | angle_atom | `angle_def:PROTECTIVE_ALARM` | `angle_def:PROTECTIVE_ALARM` | — | 50 | 47 |
| 1 | SCENE | persona_atom | `SCENE v83` | `SCENE v83` | persona_alarm_behavior | 420 | 189 |
| 1 | STORY | story_plan | `story_plan:twelve_shape:ch1:story_1:recognition:overwhelm:v03` | `story_plan:twelve_shape:ch1:story_1:recognition:overwhelm:v03` | story_vividness | 50 | 92 |
| 1 | PIVOT | persona_atom | `PIVOT v50` | `PIVOT v50` | — | 50 | 78 |
| 1 | REFLECTION | composite_doctrine | `COMPOSITE_DOCTRINE v03` | `COMPOSITE_DOCTRINE v03` | teacher_voice | 284 | 259 |
| 1 | EXERCISE | practice_library | `med_007` | `med_007` | somatic_exercise | 80 | 64 |
| 1 | STORY | story_plan | `story_plan:twelve_shape:ch1:story_1:mechanism_proof:overwhelm:v05` | `story_plan:twelve_shape:ch1:story_1:mechanism_proof:overwhelm:v05` | story_vividness | 50 | 101 |
| 1 | STORY | story_plan | `story_plan:twelve_shape:ch1:story_1:turning_point:overwhelm:v08` | `story_plan:twelve_shape:ch1:story_1:turning_point:overwhelm:v08` | story_vividness | 50 | 130 |
| 1 | TAKEAWAY | persona_atom | `TAKEAWAY v19` | `TAKEAWAY v19` | — | 50 | 13 |
| 1 | INTEGRATION | persona_atom | `INTEGRATION v26` | `INTEGRATION v26` | teacher_voice | 240 | 189 |
| 1 | THREAD | persona_atom | `THREAD v13` | `THREAD v13` | — | 50 | 25 |
| 2 | HOOK | persona_atom | `HOOK v90` | `HOOK v90` | persona_alarm_behavior | 476 | 21 |
| 2 | ANGLE_CALLBACK | angle_atom | `angle_cb:PROTECTIVE_ALARM:L1` | `angle_cb:PROTECTIVE_ALARM:L1` | — | 476 | 216 |
| 2 | SCENE | persona_atom | `SCENE v84` | `SCENE v84` | persona_alarm_behavior | 420 | 166 |
| 2 | STORY | story_plan | `story_plan:twelve_shape:ch2:story_2:recognition:overwhelm:v18` | `story_plan:twelve_shape:ch2:story_2:recognition:overwhelm:v18` | story_vividness | 50 | 162 |
| 2 | PIVOT | persona_atom | `PIVOT v51` | `PIVOT v51` | — | 50 | 92 |
| 2 | REFLECTION | composite_doctrine | `COMPOSITE_DOCTRINE v01` | `COMPOSITE_DOCTRINE v01` | — | 284 | 316 |
| 2 | EXERCISE | practice_library | `cyclic_sighing` | `cyclic_sighing` | somatic_exercise | 80 | 153 |
| 2 | STORY | story_plan | `story_plan:twelve_shape:ch2:story_2:mechanism_proof:overwhelm:v22` | `story_plan:twelve_shape:ch2:story_2:mechanism_proof:overwhelm:v22` | story_vividness | 50 | 158 |
| 2 | STORY | story_plan | `story_plan:twelve_shape:ch2:story_2:turning_point:overwhelm:v18` | `story_plan:twelve_shape:ch2:story_2:turning_point:overwhelm:v18` | story_vividness | 50 | 162 |
| 2 | TAKEAWAY | persona_atom | `TAKEAWAY v21` | `TAKEAWAY v21` | — | 50 | 24 |
| 2 | INTEGRATION | persona_atom | `INTEGRATION v36` | `INTEGRATION v36` | — | 240 | 114 |
| 2 | THREAD | persona_atom | `THREAD v21` | `THREAD v21` | — | 50 | 39 |
| 3 | HOOK | persona_atom | `HOOK v91` | `HOOK v91` | — | 476 | 18 |
| 3 | ANGLE_CALLBACK | angle_atom | `angle_cb:PROTECTIVE_ALARM:L2` | `angle_cb:PROTECTIVE_ALARM:L2` | — | 476 | 222 |
| 3 | SCENE | persona_atom | `SCENE v85` | `SCENE v85` | — | 420 | 157 |
| 3 | STORY | story_plan | `story_plan:twelve_shape:ch3:story_3:recognition:overwhelm:v19` | `story_plan:twelve_shape:ch3:story_3:recognition:overwhelm:v19` | — | 50 | 145 |
| 3 | PIVOT | persona_atom | `PIVOT v52` | `PIVOT v52` | — | 50 | 83 |
| 3 | REFLECTION | composite_doctrine | `COMPOSITE_DOCTRINE v05` | `COMPOSITE_DOCTRINE v05` | — | 284 | 326 |
| 3 | EXERCISE | practice_library | `body_003` | `body_003` | somatic_exercise | 80 | 135 |
| 3 | STORY | story_plan | `story_plan:twelve_shape:ch3:story_3:mechanism_proof:overwhelm:v23` | `story_plan:twelve_shape:ch3:story_3:mechanism_proof:overwhelm:v23` | — | 50 | 153 |
| 3 | STORY | story_plan | `story_plan:twelve_shape:ch3:story_3:embodiment:overwhelm:v20` | `story_plan:twelve_shape:ch3:story_3:embodiment:overwhelm:v20` | — | 50 | 138 |
| 3 | TAKEAWAY | persona_atom | `TAKEAWAY v22` | `TAKEAWAY v22` | — | 50 | 20 |
| 3 | INTEGRATION | persona_atom | `INTEGRATION v37` | `INTEGRATION v37` | — | 240 | 101 |
| 3 | THREAD | persona_atom | `THREAD v22` | `THREAD v22` | — | 50 | 41 |

**Trace artifact:** `assembly_trace_ch1_ch3.json` (machine-readable, same data + chapter nesting)

**Supporting copies in this pack:** `selected_content_variants.json`, `quality_summary.json`, `chapter_flow_report.json`

**Not emitted in render dir:** `plan.json` — not present in this rebuild output; chapter/slot structure is fully represented in `selected_content_variants.json` and `chapter_flow_report.json`.

---

## 5. What this does NOT show yet

Honest gaps — not represented in this flagship cell or not on current main:

| Gap | Why absent |
|---|---|
| **Other personas / topics** | This pack is the single ratified flagship cell only (`gen_z_professionals` × `anxiety`). |
| **`deep_book_6h` format** | Retired for this cell per PROGRAM_STATE Option A; `extended_book_2h` is canonical here. |
| **Translation lanes** | English-only flagship; no localized variants in this trace. |
| **Manga / Pearl News / catalog listing surfaces** | Out of scope for book pipeline preview. |
| **Layer-4 blind-register prose edits** | ONTGP line-edit lane is separate from compose; this is compose output at register_gate ADVISORY. |
| **Exercise journey outcome scores at bar** | Pipeline logged journey outcome mismatches (awareness/integration thresholds) — visible in rebuild stderr, not blocking compose. |
| **Chapters 4–12** | Intentionally excluded; full book golden at `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt`. |
| **EPUB / audio delivery** | Compose text only; no downstream packaging in this pack. |

---

## Files

| File | Purpose |
|---|---|
| `README.md` | This memo |
| `chapter_01.txt` | Full Chapter 1 prose |
| `chapter_02.txt` | Full Chapter 2 prose |
| `chapter_03.txt` | Full Chapter 3 prose |
| `assembly_trace_ch1_ch3.json` | Slot-level assembly trace (Ch1–3) |
| `selected_content_variants.json` | Full-book variant trace (copied from rebuild) |
| `quality_summary.json` | Gate summary from rebuild |
| `chapter_flow_report.json` | Per-chapter flow metrics |

---

*Generated from current-main rebuild. Parity verified via `check_flagship_book_parity.py --snapshot full`.*
