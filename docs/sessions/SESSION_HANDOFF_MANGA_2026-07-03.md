# Session Handoff — Manga Vision-Conformance + M1 Enforcement Rails (2026-07-03)

**From:** Pearl_Architect (manga 100% certification lane)
**Cold-start authority (read in this order):**
1. `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md` — the honest R1–R8 baseline
2. `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` — the routed M1–M7 plan
3. This file — what shipped, what's open, exactly what to do next
4. `CLAUDE.md` → *Manga Vision-Conformance Doctrine* (six-layer taxonomy + the 3 enforced drift classes)

> **Golden rule for this lane:** label every status claim with its acceptance layer
> (`ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`).
> A config that exists ≠ working. A gate PASS ≠ the pro bar. Only a byte-verified artifact is
> EXECUTED-REAL; nothing is PROVEN-AT-BAR yet.

---

## 1. What shipped (merged to `main`)

| PR | SHA | What |
|---|---|---|
| [#4605](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/4605) | `2049a06ff0` | Vision-conformance certification (R1–R8, 41-agent fan-out + adversarial refutation) + 100% roadmap + PROGRAM_STATE Manga row + coordination rows + OPD-20260703-101 |
| [#4604](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/4604) | `00a9c24409` | Deterministic layer compositor (`scripts/manga/assemble_from_bank.py` + manifest schema + `make_object_sprite.py`) + the 6-panel layered demo strip |

**R1–R8 conformance (honest %):** R1 30 · R2 45 · R3 25 · R4 8 · R5 34 · R6 40 · R7 5 · R8 35.
**Render truth:** the *only* real render estate on `main` is the April "alarm is lying" tree
(386 files, 212.8 MB). sleep_vol1/somatic_vol1 TSVs reference box-side images absent from `main`.
image_bank is metadata-only. 0 trained LoRAs. Nothing PROVEN-AT-BAR.

## 2. What's open right now

**PR [#4607](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/4607) — M1 enforcement rails** (branch `agent/manga-m1-enforcement-rails-20260703`, head `48f3274e20`).
Three drift-class CI gates + CLAUDE.md doctrine + 20 tests.

- ⚠️ **ACTION: verify CI green before merge.** The first push failed *Drift detectors* because
  that job runs a dependency-light Python (no PyYAML/phoenix_v4) and the story gate imported both
  at module load. Fixed in `48f3274e20` (lazy yaml + inline substance mirrors + `pip install pyyaml`
  in that step). Confirm with:
  ```bash
  gh pr checks 4607 | awk -F'\t' '$2!="pass"{print}'
  ```
  If green: `gh pr merge 4607 --squash --delete-branch` (Rule-0 diff check first: `gh pr view 4607 --json deletions` — expect 0 file deletions).
- The three gates (all land green on `main`, fail on synthetic bad input):
  - `scripts/ci/check_render_progress_bytes.py` — **stub-as-done** kill (bytes < 50 KB on an `ok` row → FAIL). Wired into Drift detectors as **BLOCK** + readiness gate 21.
  - `scripts/ci/check_manga_story_authored.py` — **listing-as-story** kill. Exposes `assert_story_authored()` for render-dispatch import. Readiness gate 22 + Drift detectors.
  - `scripts/ci/check_manga_wiring.py` — **unwired-config-as-working** kill. Readiness gate 23 + Drift detectors.
  - Tests: `tests/ci/test_manga_m1_gates.py` (20, all pass under `PYTHONPATH=. pytest`).

**Other in-flight (not mine — do not touch):** the G1-RESIDUAL composer lane owns
`phoenix_v4` register/composer files. PR #3075 (queue dispatch-bug fix) + #4565 (queue reaper)
are queued read-only — reference, don't race. Snapshot branch
`snapshot/pearl-star-manga-saturation-wip-20260702` holds killed-agent refiller/monitor ops
(8 files, review-gated **REUSE** for M5 throughput — never auto-merge).

## 3. Operator decision slate (Q-MANGA-01..07)

Presented to the operator this session; recommendations below. **01/02/06 need explicit operator
ratification** (registry edit / product-shape / tentpole); the rest have safe defaults applied.

| # | Question | Recommendation | Status |
|---|---|---|---|
| 01 | Locale grid: registry-13 vs operator's 14 (pt_BR) | **Ratify pt_BR** as the 14th (research exists; Brazil is a real manga market) → M7 Wave A after fr_FR | operator ratifies (registry edit) |
| 02 | Western shape = illustrated self-help picture books (Gen Z/Alpha)? | **Confirm YES** — matches US search intent, cheaper to produce; encode in M2 allocation | operator confirms |
| 03 | GPU pilot envelope | **Grant ~2–4 GPU-h low-priority pilot**; CJK priority stays absolute | default applied |
| 04 | PuLID-first vs LoRA-first | **PuLID-first** (no training cost, workflows authored); LoRA for flagships only | default applied |
| 05 | ko_KR hold | **Keep hold** — plan-complete, ship-gated | default applied |
| 06 | Tentpole D1 (warrior_calm ja_JP) | **Option B** — re-point to the cultivation-burnout hybrid its authored script already proves (operator leaned B) | operator ratifies |
| 07 | Japan-only catalog legal entity | Proceed on technical default (identical 37 IDs); **legal entity is operator/legal-tier** | escalate legal item |

When the operator rules, log to `artifacts/coordination/operator_decisions_log.tsv` (next id: **OPD-20260703-102**) and, for pt_BR, amend `config/localization/locale_registry.yaml` under a cap amendment (do NOT silent-edit).

## 4. Next steps — dispatch order (all no-GPU until M5)

**Sequencing law:** stories first → per-series banks → layered assembly → locale rollout.

### M2 — R1 allocation chain (dispatchable NOW, no GPU, no operator-block)
Author `config/manga/locale_genre_allocations.yaml` (per-locale genre mix derived from the
`research/2026-03-30_*` triad; encode the CJK-genre-led vs Western-picture-book split per Q-02).
Each line cites its research doc+section. Then extend
`scripts/manga/generate_catalog_plan_from_strategic.py` (Phase 2X.4 vehicle) to consume it. Commission
missing research for it_IT + zh_SG (zero) and upgrade hu_HU. Fix registry flags C-1/C-2 (zh_TW, fr_FR
manga tracks missing from `market_catalog_registry.yaml`). **NEW-ARTIFACT-JUSTIFIED** + registry row.
Fire prompt: *"Pearl_Research + Pearl_Dev: execute Roadmap M2 (§2) — author locale_genre_allocations.yaml + wire the 2X.4 generator, branch agent/manga-m2-locale-allocations off origin/main."*

### M3 — R2/R6 stories first (the long pole, no GPU)
(a) Complete craft bibles for the 44 uncovered genres (Phase 2X.3). (b) Pearl_Writer batch-authors
37 en_US flagship chapter_scripts through the existing `run_manga_pipeline.run_one_book()` orchestration
— **each must pass `scripts/ci/check_manga_story_authored.py`** (the M1 entry gate) and carry the
craft-notes block the 16 existing scripts established. (c) Qwen adapts to CJK via
`translate_chapter_script.py`; ja_JP flagships get native-authored (genre-led) scripts.

### M4 — R3/R4 vessel wiring (no GPU)
Wire `config/manga/manga_mode_vessels.yaml` into `story_architect.py` + the chapter-writer prompt
assembly (the M1 wiring gate then reports it as *wired* — remove it from `KNOWN_UNWIRED` in
`check_manga_wiring.py`). Commission `docs/research/manga_craft/teacher_apparatus_per_genre.md`. Author
`docs/specs/MUSIC_MODE_MANGA_V1_SPEC.md` + one music-mode pilot script.

### M5 — R5 banks + assembly (GPU begins; **blocked on Pearl Star reachability**)
Per M3-storied flagship: author the bank contract (scene/object/character-pose inventories — the
`stillness_en_01` set is the template), render bank assets via `render_v5_episode.py` (merge PR #1276
V5.1 first), install PuLID nodes (V2-01 Phase B), then assemble via `assemble_from_bank.py`. Respect
OPD-135 (Milestone C continuity generator gates ep_002+). **When Pearl Star returns**, the Phase D
real-asset batch resume is ready:
`artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/demo_alarm_metaphor_6p/RESUME_COMMANDS.sh`
(~8 images, LOW priority per OPD-20260629-003 — do NOT preempt the CJK atom lane).

### M6 — R7 pro bar · M7 — R8 locale rollout
See roadmap §6–§7. M6 = the blind-10 judge protocol (needs operator-recruited JP pros). M7 = generator
waves per M2 allocation (fr_FR first), ≤180-file PRs/locale.

## 5. Environment gotchas that burned time this session

- **Pearl Star was unreachable all session** (SSH timeout to `100.92.68.74`, ComfyUI :8188 dead,
  `tailscale ping` no reply — local MagicSock health warning, possibly Mac-side). All box-side state is
  UNVERIFIED. Re-check reachability before any M5 GPU work.
- **Never trust the working tree for state** — it sits on the sibling G1 composer branch with churn.
  Resolve everything against `origin/main` via the git object DB.
- **After a session restart, Bash cwd resets to the shared repo root** — a bare `git checkout` there moves
  the *shared* tree (it briefly switched the sibling composer branch this session). Use `git -C <worktree>`
  or `cd <abs> &&` for every git state change from a worktree lane.
- **Sparse worktree recipe** (full checkout times out — repo is huge):
  `git worktree add --no-checkout … && git sparse-checkout init --cone && git sparse-checkout set <dirs> && GIT_LFS_SKIP_SMUDGE=1 git checkout <branch>`.
  If `git lfs checkout` silently no-ops but the object is local, materialize by hand: parse `oid` from the
  pointer, `cp .git/lfs/objects/<xx>/<yy>/<oid> <file>`.
- **Drift detectors CI job is dependency-light** (no PyYAML/phoenix_v4) — any gate you add there must be
  pure-Python or install its own deps (see the M1 story-gate fix). actionlint every workflow edit
  (PyYAML-valid ≠ GHA-valid).
- **The full bestseller gate is NOT a render-entry gate** — it demands ≥2 print pages + a non-empty close,
  which reject the real single-scroll webtoon ep_001. The M1 story-authored gate deliberately uses the
  ENTRY threshold. Don't "fix" the entry gate to match the bestseller gate.

## 6. NEXT_ACTION (single most important thing)

1. Verify #4607 CI is green (`gh pr checks 4607`), merge it (Rule-0 check first).
2. Get operator rulings on Q-MANGA-01/02/06; log OPD-20260703-102.
3. Dispatch **M2** (locale allocations) — no GPU, no blockers, entry gate = none.
