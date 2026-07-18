# Handoff: Pearl ebook path — Gen Z student × overthinking (registry build + macOS TTS)

**Audience:** Next operator or engineer picking up this thread.  
**Date context:** Session targeted **2026-04-18**; adjust paths if your tree differs.  
**Scope:** Governed **ebook / Pearl Prime freeze** flow (`pearl_prime.modular_format_freeze` is imported by `scripts/run_pipeline.py`), **not** the separate audiobook localization comparator (`scripts/audiobook_script/run_comparator_loop.py`).

---

## 1. What was attempted

| Item | Detail |
|------|--------|
| **Goal** | Assemble a book: **persona** `gen_z_student`, **topic** `overthinking`, **~2h** listen target (interpreted as shorter chapter count vs 12-ch `F006`). |
| **Governed entry** | `docs/EBOOK_PIPELINE_COMPLETE_GUIDE.md`: `create_job` → `acknowledge_guide` → `run_pipeline`. |
| **Arc** | Short files under `config/source_of_truth/master_arcs/` named `gen_z_student__overthinking__<engine>__F00x.yaml` are **legacy stubs** and **fail** `phoenix_v4.planning.arc_loader.load_arc()` (missing `arc_id`, `emotional_curve`, `emotional_role_sequence`, etc.). |
| **Arc workaround** | Generated a valid arc with `tools/arc_generator.py` into the job workspace (example below). |
| **Pipeline** | `scripts/run_pipeline.py` with `--workspace`, `--out`, `--render-book`, `--quality-profile draft`, no freebie index churn. |
| **TTS** | macOS **`say`** → intermediate **AIFF** → **`ffmpeg`** MP3; first attempt used invalid `say` output flags; plain `say -v Samantha -f book.txt -o out.aiff` is the working shape. |
| **Finder** | `open -R <path>/book.txt` to reveal the rendered book in Finder. |

---

## 2. Commands (copy-paste)

### 2.1 Job workspace (ebook pipeline)

Pick a workspace directory (must stay stable across runs for `job.json`).

```bash
cd /path/to/phoenix_omega
export WS="artifacts/pipeline_workspace/genz_student_overthinking_2hr_YYYYMMDD"
mkdir -p "$WS"

PYTHONPATH=. python3 scripts/pipeline/create_job.py \
  --pipeline ebook \
  --workspace "$WS" \
  --topic overthinking \
  --persona gen_z_student \
  --locale en-US \
  --arc config/source_of_truth/master_arcs/gen_z_student__overthinking__spiral__F003.yaml

PYTHONPATH=. python3 scripts/pipeline/acknowledge_guide.py --workspace "$WS"
```

**Note:** `--arc` on `create_job` only seeds `job.json` params; **`run_pipeline` still needs `--arc`** pointing at a **schema-valid** YAML (see §3).

### 2.2 Generate a valid arc (when master stub is invalid)

```bash
python3 tools/arc_generator.py \
  --template standard_escalation \
  --persona gen_z_student \
  --topic overthinking \
  --format F003 \
  --chapter-count 6 \
  --engine spiral \
  --out "$WS/generated_arc_F003_6ch.yaml"
```

- **F003 + 6 chapters** was used as a shorter book shape (vs `F006` / 12 chapters).  
- Template compatibility: `config/source_of_truth/master_arcs/templates/standard_escalation.yaml` lists allowed formats including `F003`.

### 2.3 Run assembly + render

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --arc "$WS/generated_arc_F003_6ch.yaml" \
  --topic overthinking \
  --persona gen_z_student \
  --workspace "$WS" \
  --out "$WS/compiled_plan.json" \
  --render-book \
  --quality-profile draft \
  --no-generate-freebies \
  --no-update-freebie-index
```

If the **word-count gate** blocks (registry builds can come in under `short_book_30` minimum), either fix content density upstream or, for **dev only**:

```bash
# Dev-only — do not use for production shipping decisions
PYTHONPATH=. python3 scripts/run_pipeline.py ... --skip-word-count-gate
```

### 2.4 Tuple viability debug (if `NO_STORY_POOL`)

```bash
PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py \
  --persona gen_z_student \
  --topic overthinking \
  --engine spiral \
  --format F003
```

Expect **`TUPLE_VIABLE`** only when `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` exists and parses with enough STORY depth (see §4).

### 2.5 macOS TTS → MP3

After `book.txt` exists:

```bash
BOOK="artifacts/rendered/registry-overthinking/book.txt"   # or your --render-dir
OUT_DIR="$(dirname "$BOOK")"
say -v Samantha -f "$BOOK" -o "$OUT_DIR/book_macos_tts.aiff"
ffmpeg -y -i "$OUT_DIR/book_macos_tts.aiff" -codec:a libmp3lame -qscale:a 3 "$OUT_DIR/book_macos_tts_samantha.mp3"
```

Avoid `say ... --data-format=...` unless you have confirmed the flag shape for your OS version; a bare `-o file.aiff` is the most portable.

### 2.6 Reveal book in Finder

```bash
open -R "/path/to/artifacts/rendered/registry-overthinking/book.txt"
```

---

## 3. Arc / schema blocker (important)

`phoenix_v4/planning/arc_loader.py` enforces **Arc-First Canonical Spec v1.1** (`REQUIRED_ARC_KEYS`, `emotional_role_sequence`, etc.). Many **one-line-style** `master_arcs/*.yaml` files will raise:

`ValueError: Arc schema invalid: Missing required keys: [...]`

**Primary fix (repo health):** regenerate or replace those stubs with full arcs (same as `tools/arc_generator.py` output), or wire `load_or_generate_arc()` where appropriate. Until then, **point `--arc` at a generated full YAML** (workspace or `master_arcs`).

---

## 4. Atoms layout vs tuple viability (`NO_STORY_POOL`)

`phoenix_v4/gates/check_tuple_viability.py` loads STORY from:

`atoms/<persona>/<topic>/<engine>/CANONICAL.txt`

For `gen_z_student` / `overthinking`, the repo had **slot-level** trees (e.g. `atoms/.../overthinking/STORY/CANONICAL.txt`) but **no** `.../overthinking/spiral/CANONICAL.txt`, so viability returned **`NO_STORY_POOL`** even though generic STORY content existed.

**Interim fix applied in session:** symlink under `atoms` (correct **relative** path — must stay inside `atoms/`):

```text
atoms/gen_z_student/overthinking/spiral  →  ../../gen_z_professionals/overthinking/spiral
```

**Wrong attempt (do not repeat):** `../../../gen_z_professionals/...` resolves **outside** `atoms/` to a non-existent repo-root path; Python reported `exists() == False`.

**Product / editorial caveat:** Pointing student at **professionals** spiral STORY may skew voice; long-term fix is a real `atoms/gen_z_student/overthinking/<engine>/CANONICAL.txt` (or compiler path alignment if student is intentionally flat-layout).

---

## 5. Runtime path that actually ran

Logs indicated **section registry mode** for overthinking:

- `Using section registry: .../registry/overthinking.yaml`
- Render output went to **`artifacts/rendered/registry-overthinking/book.txt`** (and `budget.json` alongside) when using default render dir behavior for that mode.

**Quality:** First successful render hit **~1,490 words** while runtime target **`short_book_30`** expected **4,500–7,500** words → **word count gate failed** (expected until registry density / slot policy is improved or gates skipped for dev).

---

## 6. Artifacts checklist (verify on disk)

| Artifact | Intended path / role |
|----------|----------------------|
| Job | `artifacts/pipeline_workspace/genz_student_overthinking_2hr_<date>/job.json` |
| Generated arc | `.../generated_arc_F003_6ch.yaml` |
| Compiled plan | `.../compiled_plan.json` |
| Rendered prose | `artifacts/rendered/registry-overthinking/book.txt` |
| Render budget | `artifacts/rendered/registry-overthinking/budget.json` |
| macOS TTS intermediate | `artifacts/rendered/registry-overthinking/test.aiff` or `book_macos_tts.aiff` (if completed) |
| MP3 | `.../book_macos_tts_samantha.mp3` (if `ffmpeg` was run after `say` finished) |

If any path is missing locally, re-run §2.3 (and §2.2 if the generated arc was deleted).

---

## 7. Related docs (read order)

1. `docs/EBOOK_PIPELINE_COMPLETE_GUIDE.md`  
2. `config/pipeline_registry.yaml` → `pipelines.ebook`  
3. `docs/audiobook_operator_runbook.md` — **different** pipeline (LM Studio + comparator); not used for this assembly.  
4. `docs/LONGFORM_STRATEGY.md` — word-count / dedup floor issues.  
5. `pearl_prime/README.md` — modular format freeze scope vs monolithic pipeline.

---

## 8. Prior thread: Month-1 execution sprint (PR #498)

A separate **Pearl_PM** sprint brief (Illustrious XL, portfolio surgery, vertical scroll, Skia, etc.) specified **Phase 0** blocking doc: `artifacts/coordination/month1_execution_decisions.md`. That workstream is **orthogonal** to the ebook assembly above; pick it up only if the operator is still driving that batch.

---

## 9. Suggested next actions

1. **Decide** whether the `gen_z_student/overthinking/spiral` symlink stays, is replaced with owned atoms, or is removed after copying a student-vetted subset.  
2. **Regenerate** master arc YAMLs for high-traffic tuples so `--arc` does not depend on workspace-only files.  
3. **Re-run** `run_pipeline` with `--quality-profile production` only after word-count and book-pass gates are green without `--skip-word-count-gate`.  
4. **Finish** MP3 if `say` left a large `.aiff` on disk: run `ffmpeg` once synthesis completes; validate duration with `ffprobe`.

---

## 10. Closeout receipt (session)

- **Ebook path:** Governed `ebook` pipeline via `scripts/run_pipeline.py` + `scripts/pipeline/create_job.py` + `acknowledge_guide.py`.  
- **Blockers hit:** Invalid legacy master arc schema; tuple viability `NO_STORY_POOL` until symlink; word-count gate under registry output.  
- **Operator UX:** Finder reveal via `open -R`; TTS pipeline documented for MP3 export.  
- **Handoff file:** This document: `artifacts/coordination/HANDOFF_pearl_ebook_gen_z_student_overthinking.md`.
