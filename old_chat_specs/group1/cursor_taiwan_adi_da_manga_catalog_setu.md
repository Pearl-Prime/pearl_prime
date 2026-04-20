# Taiwan Adi Da manga catalog setup
_Exported on 4/16/2026 at 19:23:39 GMT+8 from Cursor (3.1.15)_

---

**User**

Here’s a single paste-ready prompt that covers Taiwan-only Adi Da manga, Sai Maa id cleanup, optional 6–18 title encoding, and parity checks. It matches your lane file pattern (taiwan: / _tw suffixes).


You are Pearl_Dev + Pearl_Architect + Pearl_PM. Obey docs/SESSION_UNITY_PROTOCOL.md (STARTUP_RECEIPT / CLOSEOUT_RECEIPT).
OWNER DECISION (verbatim)
adi da is ok for manga taiwan catalog only.
TASK — Manga / catalog parity for Pearl Prime teacher mode (full package)
A) Taiwan-only Adi Da manga brand
- `adi_da` is in `config/teachers/teacher_registry.yaml` but absent from the 12 global teacher brands in `config/manga/manga_brand_series_plan.yaml` and from the per-lane teacher lists in `config/catalog_planning/teacher_brand_lane_assignments.yaml`.
- Add **one** new teacher-mode brand **only under lane `taiwan:`** (zh-TW), with a unique base name + `_tw` suffix consistent with existing patterns (e.g. `bright_presence_tw` or owner-chosen slug — must not collide with existing `stillness_press_tw` … `devotion_path_tw`).
- Map `{ teacher: adi_da, content: [audiobooks, manga, video, exercises, freebies] }` (or subset owner approves) for **that brand only** on **taiwan**.
- Do **not** add `adi_da` to other lanes (english_global, japan, korea, china, etc.) unless owner explicitly expands scope later.
- Add a **`manga_brand_series_plan.yaml` brand block** for this Taiwan Adi Da line: `primary_lane: taiwan` (or document equivalent), `teacher: adi_da`, **unique `genre`** and `topic_allocation` vs the other 12 brands (reuse `teacher_character_prompts.yaml` for `adi_da` as visual baseline; align prose notes with `dark_psychological` / doctrine).
- Update `teacher_brand_lane_assignments.yaml` **summary** section to state the exception: **Taiwan lane = 13 teacher-mode brands**; all other lanes remain **12**. Fix any arithmetic (`total_brand_instances`, teacher_reach strings) that becomes wrong if summary claims 12×12 everywhere.
B) Canonical teacher id — Sai Maa
- Registry and `manga_brand_series_plan` use `sai_ma`; `config/manga/teacher_character_prompts.yaml` and `config/tts/manga_character_voice_bank.yaml` use `sai_maa`.
- Pick **one** canonical id (`sai_ma` recommended). Migrate YAML keys and any Python that references `sai_maa`; add a **temporary alias** in one loader if needed for backward compatibility, then remove alias once tests pass.
C) Optional — encode “6–18 titles” per brand (if product still wants it)
- `manga_brand_series_plan.yaml` today uses `active_series_target` / `new_series_per_year`, not literal 6–18.
- Either add explicit `target_series_catalog_min` / `target_series_catalog_max` (6–18 or per-brand ranges) **or** document the derived formula in `docs/MANGA_IMPLEMENTATION_OUTLINE.md` and add a small validation script under `scripts/` that asserts each brand’s planned throughput falls in owner-approved bounds.
D) Invariants & tests
- **1 teacher per brand** everywhere (existing rule).
- **No teacher appears twice** on the same lane under teacher-mode brands.
- **Taiwan:** exactly **one** brand row for `adi_da` after change.
- Add or extend tests (e.g. under `tests/`) that load YAML and assert:
  - union of `teacher:` keys in `manga_brand_series_plan.brands` matches intended set (12 global + 1 Taiwan-only OR 13 entries with clear schema);
  - every `teacher_registry` teacher either has a global manga brand **or** is explicitly allowed as Taiwan-only (`adi_da`) per a small allowlist in test;
  - `teacher_character_prompts.yaml` keys match registry ids after `sai_ma` fix.
E) Authority reads
specs/AI_MANGA_PIPELINE_SUMMARY.md; docs/MANGA_IMPLEMENTATION_OUTLINE.md; docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md (portfolio context); config/manga/gate_registry.yaml if present; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (conflict scan — avoid ws_teacher_manga_triptych collision on unrelated paths).
WRITE_SCOPE
config/manga/manga_brand_series_plan.yaml; config/manga/teacher_character_prompts.yaml (key rename + any prompt tweaks); config/catalog_planning/teacher_brand_lane_assignments.yaml; config/tts/manga_character_voice_bank.yaml; phoenix_v4/** or scripts/** only if loaders need alias; tests/**; optional docs/MANGA_IMPLEMENTATION_OUTLINE.md for the 6–18 encoding.
OUT_OF_SCOPE
Adding Adi Da to non-Taiwan lanes; Pearl News; video flux washout; narrator_voice_assignments wholesale edits.
CLOSEOUT
- Table: teacher_id → brand_slug(s) → lane(s) → manga genre → prompt style_archetype.
- Note: “Adi Da manga = Taiwan catalog only.”
- PR link; merge SHA; pytest subset results.
STARTUP_RECEIPT
STARTUP_RECEIPT
AGENT:
TASK:
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: manga_pipeline; core_pipeline (catalog)
AUTHORITY_DOCS:
READ_PATH_COMPLETE:
WRITE_SCOPE:
OUT_OF_SCOPE:
BLOCKERS:
READY_STATUS:


---

**Cursor**

Implementing manga/catalog parity: reading SESSION_UNITY_PROTOCOL and relevant configs, then applying changes and tests.



Checking loaders for `teacher_character_prompts` / `sai_maa` and skimming authority docs.



Implementing changes: updating the manga plan header comment, adding the `bright_presence_tw` brand block, updating lane assignments and summary, renaming `sai_maa` → `sai_ma`, updating `visual_prompt_compiler` and triptych script, adding tests and validation script, and documenting in `MANGA_IMPLEMENTATION_OUTLINE.md`.



Applying file edits.



Here is the session paperwork and what was implemented.

---

**STARTUP_RECEIPT**  
AGENT: Pearl_Dev + Pearl_Architect + Pearl_PM (Cursor)  
TASK: Manga / catalog parity — Taiwan-only Adi Da brand, `sai_ma` id cleanup, 6–18 catalog bounds, parity tests  
PROJECT_ID: proj_state_convergence_20260328  
SUBSYSTEM: manga_pipeline; core_pipeline (catalog)  
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md (resume manga row); artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (conflict scan: `ws_teacher_manga_triptych` touches overlapping config only — no unrelated path conflict); specs/AI_MANGA_PIPELINE_SUMMARY.md (skim); docs/MANGA_IMPLEMENTATION_OUTLINE.md; docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md (not re-read in full this session); config/manga/gate_registry.yaml (present, unchanged)  
READ_PATH_COMPLETE: yes (minimum + manga authority set above)  
WRITE_SCOPE: config/manga/*; config/catalog_planning/teacher_brand_lane_assignments.yaml; config/tts/manga_character_voice_bank.yaml; phoenix_v4/manga/visual_prompt_compiler.py; scripts/catalog/build_catalog_analysis_bundle.py; scripts/image_generation/generate_teacher_showcase_triptych.py; scripts/manga/validate_manga_series_catalog_bounds.py; tests/test_manga_catalog_parity.py; docs/MANGA_IMPLEMENTATION_OUTLINE.md  
OUT_OF_SCOPE: Non-Taiwan Adi Da lanes; Pearl News; video flux; narrator_voice_assignments wholesale edits  
BLOCKERS: none  
READY_STATUS: ready  

---

### What changed

**A — Taiwan-only Adi Da**  
- `config/manga/manga_brand_series_plan.yaml`: new brand `bright_presence_tw` with `teacher: adi_da`, `primary_lane: taiwan`, genre `philosophical_dark`, `topic_allocation` (depression / grief / courage), pacing aligned to other brands.  
- `config/catalog_planning/teacher_brand_lane_assignments.yaml`: under nested `taiwan` (same YAML shape as today: regional lanes live under `english_global` in the file), added `bright_presence_tw` with full content list. Summary arithmetic updated: **433** total brand instances, **145** teacher-mode rows, Taiwan **37** brands per lane (13 teacher + 24 standard).

**B — Canonical `sai_ma`**  
- Renamed YAML keys `sai_maa` → `sai_ma` in `teacher_character_prompts.yaml` and `manga_character_voice_bank.yaml`.  
- `phoenix_v4/manga/visual_prompt_compiler.py` default block key updated.  
- Triptych script: dropped the old `sai_maa` → `sai_ma` filename alias (no loader alias added; registry already used `sai_ma`).

**C — 6–18 encoding**  
- `global_defaults.target_series_catalog_min: 6` and `target_series_catalog_max: 18` in `manga_brand_series_plan.yaml`.  
- `scripts/manga/validate_manga_series_catalog_bounds.py` enforces consistency (e.g. `max_active_series` and `new_series_per_year` vs ceiling).  
- Short section in `docs/MANGA_IMPLEMENTATION_OUTLINE.md`.

**D — Tests**  
- `tests/test_manga_catalog_parity.py`: registry ↔ prompts keys; manga plan covers all teachers with Taiwan-only rule; no duplicate teachers per lane via `iter_teacher_planning_rows`; Taiwan exactly one `adi_da` row; summary totals match computed rows; validation script exits 0.

**E — Bundle script**  
- `scripts/catalog/build_catalog_analysis_bundle.py` reads `brands_per_lane_default` (fallback to legacy `brands_per_lane`).

---

### Teacher → brand → lane → manga genre → prompt `style_archetype`

| teacher_id | Primary manga plan slug | Lanes (teacher-mode) | manga `genre` | `style_archetype` (prompts) |
|------------|-------------------------|----------------------|---------------|-----------------------------|
| ahjan | stillness_press | all 12 | iyashikei | cozy_iyashikei |
| joshin | cognitive_clarity | all 12 | seinen | dark_psychological |
| pamela_fellows | somatic_wisdom | all 12 | shojo | webtoon_vertical_romance |
| master_feung | qi_foundation | all 12 | cultivation | interactive_branching |
| miki | digital_ground | all 12 | manhwa | cozy_iyashikei |
| maat | heart_balance | all 12 | shojo | power_progression |
| junko | relational_calm | all 12 | iyashikei | dark_psychological |
| master_wu | warrior_calm | all 12 | cultivation | interactive_branching |
| master_sha | sleep_restoration | all 12 | iyashikei | cozy_iyashikei |
| omote | body_memory | all 12 | shojo | hyper_clean_cinematic |
| ra | solar_return | all 12 | isekai | dark_psychological |
| sai_ma | devotion_path | all 12 | shonen | webtoon_vertical_romance |
| adi_da | bright_presence_tw | **taiwan only** | philosophical_dark | dark_psychological |

**Note:** Adi Da manga is **Taiwan catalog only** (`bright_presence_tw`); he is not on other lanes.

---

### CLOSEOUT_RECEIPT

AGENT: Pearl_Dev + Pearl_Architect + Pearl_PM (Cursor)  
TASK: (same as STARTUP)  
COMMIT_SHA: `75d385971f094c27955b697d1cd6d1f867b52e02`  
FILES_WRITTEN: `config/manga/manga_brand_series_plan.yaml`; `config/manga/teacher_character_prompts.yaml`; `config/catalog_planning/teacher_brand_lane_assignments.yaml`; `config/tts/manga_character_voice_bank.yaml`; `phoenix_v4/manga/visual_prompt_compiler.py`; `scripts/image_generation/generate_teacher_showcase_triptych.py`; `scripts/catalog/build_catalog_analysis_bundle.py`; `scripts/manga/validate_manga_series_catalog_bounds.py` (new); `tests/test_manga_catalog_parity.py` (new); `docs/MANGA_IMPLEMENTATION_OUTLINE.md`  
FILES_READ: authority set listed in STARTUP_RECEIPT  
STATUS: completed  
HANDOFF_TO: Pearl_GitHub (if you want this on GitHub: branch from `origin/main`, push, open PR)  
NEXT_ACTION: Optional: run full `pytest` locally; open PR with governance preflight per `CLAUDE.md`  

**PR link:** not created in this session (local commit only on current branch).  
**Pytest subset:** `tests/test_manga_catalog_parity.py`, `tests/test_manga_visual_prompt_compiler.py`, `tests/test_build_catalog_analysis_bundle_smoke.py` — **12 passed**.

---

**User**

do you have sai_maa_vid.mp4 or ra.mp4 ?
were you helping me move vids? 

---

**Cursor**

Searching the workspace for those files. I wasn’t part of a separate “move videos” thread in our chat here — the last work we did together was manga/catalog config and tests.



Here’s what the repo and a quick scan show:

### `sai_maa_vid.mp4`
**Not in this workspace** under that name. The tracked clip for Sai Maa uses the canonical slug **`sai_ma`**:

- `brand-wizard-app/public/assets/video/tiktok/sai_ma_depression_tiktok.mp4`

That’s also what `artifacts/video/TEACHER_R2_URL_INVENTORY.md` records (2026-04-15): no `sai_maa_vid.mp4` in git; if something was named that elsewhere, it’s likely a typo or a one-off export — check R2 / your uploader.

### `ra.mp4`
**No file literally named `ra.mp4`** under `brand-wizard-app/public` (or in the tiktok list). Ra’s clip there is:

- `brand-wizard-app/public/assets/video/tiktok/ra_courage_tiktok.mp4`

### Was I helping you move videos?
**In our chat here, no** — the only thread I have with you in this session was the manga/catalog parity work. A **separate** pass documented **`artifacts/video/TEACHER_R2_URL_INVENTORY.md`** (teacher/R2 URL inventory); that may be what you’re remembering, but it wasn’t this same back-and-forth.

If you want, we can next search your machine for `sai_maa_vid.mp4` / `ra.mp4` outside the repo or wire HTML to match whatever filenames you actually uploaded to R2.

