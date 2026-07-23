# Session Handoff — Manga Image-Bank Infra, Roadmap Doc-Drift, zh_TW Smoke Cell

**Date:** 2026-07-23 · **Agent:** Claude Code (this session, Pearl_GitHub-scoped) · **Tier:** 1 (operator present, remote/cloud container — no Tailscale/Pearl Star GPU access)
**Repo:** Pearl-Prime/pearl_prime · **Session branch:** `claude/manga-infra-verify-prompts-1dokma`
**Result:** 2 PRs merged (**#206**, **#234**), 3 PRs open and CI-green-pending (**#243**, **#245**, **#246**) — none merged yet, all awaiting operator review per their own "do not merge" instructions or final `Core tests` confirmation.

---

## 1. What was asked, in order

1. Ground a manga image-bank/free-infra prompt pack in real repo state and hand off paste-ready prompts.
2. `merge` — merge the resulting PR.
3. `fix manga 100% production pipeline` (deliberately broad).
4. `status` — status check.
5. `fix: Still outstanding on all three: Core tests and parse-sweep fail...` — actually resolve the pre-existing CI noise, not just note it.
6. `document whole session and give me a .md handoff for next session` — this document.

## 2. Timeline / what actually happened

### Phase A — Manga image-bank free-infra prompt pack (PR #206, MERGED)
Researched live repo state (RunComfy decommissioned 2026-06-13, Pearl Star/ComfyUI is the sole free image-gen path, `flux1-schnell-fp8` is the only license-clean checkpoint, zero trained LoRAs anywhere, panel art is locale-agnostic — only bubble/lettering is per-locale). Authored a 2-lane, docs-only prompt pack at `docs/agent_prompt_packs/20260723_manga_image_bank_free_infra/`. Landed as **PR #206**, merged `8641213c1a` (squash). Three pre-existing CI failures on that PR (`Core tests`, `Release gates`, `parse-sweep`) were verified as pre-existing on `origin/main` (unrelated to the docs-only diff) before merging.

### Phase B — Lane 1 GPU verification attempt: BLOCKED, correctly
Tried to execute the prompt pack's Lane 1 (live Pearl Star smoke test) directly in this session. **Blocked**: this cloud container has no Tailscale, no `PS_QUEUE_DSN`, and `pearlstar.tail7fd910.ts.net` doesn't resolve (`curl: (6) Could not resolve host`). Correctly stopped and reported BLOCKED rather than fabricating a result — this is exactly why the prompt pack was designed to be pasted into a Tailscale-joined session, not run here. **Not resolved this session** — still needs a session with real Pearl Star network access.

### Phase C — "fix manga 100% production pipeline": investigation, not blind action
Given the enormous scope (7-milestone roadmap, M1–M7), investigated before acting:
- Ran `check_manga_wiring.py`, `check_render_progress_bytes.py`, `check_manga_story_authored.py` live — **all PASS**.
- Ran `pytest tests/manga/` (562 tests) — **all pass** once local deps (PIL, numpy, jsonschema — missing only in this container's pip env, not a repo bug) were installed.
- **Finding: the 2026-07-03 roadmap doc and `PROGRAM_STATE.md` were badly stale.** M1 (CI gates), M2 (`config/manga/locale_genre_allocations.yaml` + registry C-1/C-2), and M4 (`manga_mode_vessels.yaml` wired into `story_architect.py::apply_mode_vessel`, plus `MANGA_MODE_WRAPPER_DESIGN.md`/`MUSIC_MODE_MANGA_V1_SPEC.md`/`teacher_apparatus_per_genre.md`) are all already CODE-WIRED/EXECUTED-REAL and gate-green — none of this was reflected in the tracking docs.
- **Real remaining gap: M3 (stories authored at scale).** Discovered an active, already-scoped same-day program: `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/` (PR #103, merged) with a full `ASSIGNMENT_MATRIX.tsv` (109 cells: en_US/ja_JP/zh_TW × 37 brands). Live count: **en_US 37/37 cells** have a gate-passing `ep_001`, **ja_JP 17/37**, **zh_TW 0/37** — despite zh_TW's research blocker (lane 01, modern-reader-context doctrine) already being resolved. Nobody had dispatched the zh_TW writer lane.
- M5 (GPU banks)/M6 (blind-judge)/M7 (locale rollout) remain genuinely blocked on Pearl Star access and operator decisions (judge recruiting, legal entity) — **not actionable from this container, not attempted**.

### Phase D — PR #243: doc-drift correction (OPEN, CI green pending Core tests)
Updated `docs/PROGRAM_STATE.md`'s manga section and added a missing `ws_manga_48ep_3catalog_writing_20260723` row to `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, recording the true M1/M2/M4/M3 state above. **Drive-by fix:** found and stripped literal unresolved git-conflict markers (`<<<<<<< origin/main` / `=======` / `>>>>>>> <sha>`, empty payload) already committed into `ACTIVE_WORKSTREAMS.tsv` on `origin/main` — pre-existing corruption from an earlier bad merge, unrelated to this session's work, found while editing the same file.
- Branch: `claude/manga-infra-verify-prompts-1dokma` (this session's designated branch — had to restart it from fresh `origin/main` since its prior PR #206 had already merged; never stack on merged history).
- PR: **#243**, draft, base `main`.

### Phase E — PR #245: zh_TW smoke-cell authoring (OPEN, CI green pending Core tests)
Dispatched the concrete next step of the M3 gap: author the zh_TW pilot cell (`cognitive_clarity`, flagship, psychological_thriller) per `04_WRITER_LANE_ZH_TW_PROMPT.md`'s own "smoke cell" instructions.
- **First dispatch attempt** (to the `translate-zh-tw` specialist agent) was **correctly declined** — that agent is narrowly scoped to `atoms/**/locales/zh-TW/CANONICAL.txt` locale-QA translation, not general authoring+git+PR work, and it refused to silently pivot scope. This was the right call from it, not a failure.
- **Re-dispatched to a `general-purpose` agent** with the same brief plus explicit instruction to write genuine literary-register Traditional Chinese (not machine-translated-sounding). Succeeded: authored `artifacts/manga/arc_storyboards/cognitive_clarity__han_yushen__zh_TW__overthinking__the_missing_hour/ep_001.arc_storyboard.yaml`, `artifacts/manga/chapter_scripts/cognitive_clarity__han_yushen__zh_TW__overthinking__the_missing_hour/ep_001.yaml`, and a new author-pool profile `config/authoring/manga_authors/han_yushen_zh_tw_003.yaml` (filling a seinen/psychological_thriller register gap in the zh_TW pen-name pool).
- **Honestly logged blocker (not worked around):** `scripts/ci/check_manga_arc_storyboard.py` — cited as mandatory by the dispatch pack — **does not exist in this repo** (also absent: its schema, its planner doc, `plan_genre_scene_coverage.py`, `genre_scene_templates/`). The storyboard file mirrors the shape of the merged ja_JP precedent instead. Flagged for the operator/a follow-on lane, not silently invented.
- **Self-check via `validate_story_excellence.py`:** 8/9 gates PASS at score 100. The 9th was blocked purely by a config gap — see Phase F.
- PR: **#245**, draft, base `main`.

### Phase F — PR #246: `reader_markets` allowlist fix (OPEN, CI green pending Core tests)
PR #245's self-check surfaced a real, separate, high-leverage bug: `config/manga/story_excellence_gates.yaml`'s `reader_markets: [en_US, ja_JP, zh_CN, fr_FR]` never had `zh_TW` added, even though `modern_reader_story_doctrine.yaml` already carries a real zh_TW profile. This structurally blocked `MANGA.STORY.RESEARCH_DOCTRINE_COVERAGE` for **every** zh_TW submission regardless of content quality — not just PR #245's cell, the entire 36-cell zh_TW wave.
- One-line fix: added `zh_TW` to the allowlist. Verified no other code hardcodes this exact 4-market list. 562/562 `tests/manga/` pass; both manga CI gates green.
- PR: **#246**, draft, base `main`.

### Phase G — G-CLAIM gate false-positive on PR bodies (fixed) + a CI gotcha (documented)
`#243` and `#245` both failed the `Drift detectors` job on `check_acceptance_claim_language.py` (G-CLAIM/Q-ENFORCE-02): their PR bodies contained "bestseller"/"shippable" in **negations** ("not bestseller", "nothing here is bestseller") — the gate only pattern-matches the trigger word (`CLAIM_RE`), not the negation; it separately requires one of its recognized acceptance-layer phrases (`Layer 1-4`, `bestseller register`, `system working`, etc. — see `ACCEPTANCE_LAYER_RE` in the script) to appear **anywhere** in the same text. Reworded both PR bodies to keep the same meaning while using the gate's recognized vocabulary; verified locally against the actual regex before pushing.
- **Gotcha for next session:** `mcp__github__actions_run_trigger` with `rerun_failed_jobs` **replays the original triggering event's payload** (including the PR body snapshot at PR-creation/last-sync time) — it does **not** refetch the live PR body. Editing a PR body via `update_pull_request` and then just re-running the failed job will reproduce the exact same failure. The only way to get a fresh `pull_request: synchronize` event (which does capture the live body) is an actual push — used a trivial `git commit --allow-empty` to each branch to force it.

### Phase H — Root cause of `Core tests`/`parse-sweep` failures: found existing fix, merged it (PR #234, MERGED)
All of #206/#243/#245/#246 hit the same `Core tests`/`parse-sweep` failure: `test_canonical_atom_parse_sweep_guard.py::test_parse_sweep_is_green_tree_wide` / `check_canonical_atom_parse_sweep.py` flagging **NEW STUB CONTENT** in 4 pre-existing files:
- `atoms/corporate_managers/compassion_fatigue/{grief,overwhelm,watcher}/locales/zh-CN/CANONICAL.txt`
- `atoms/entrepreneurs/compassion_fatigue/watcher/locales/zh-CN/CANONICAL.txt`

Root cause: these zh-CN files (added by PR #111, wave1 shard 08) faithfully mirrored a pre-existing bare-stub-prose defect already present in their **English source** files (a `## LABEL vNN` header whose prose body is literally the bare, unauthored next-header label, e.g. body text `RECOGNITION v02` under header `## RECOGNITION v01` — the PR #1590 failure class). The EN sources were already in the stub baseline; the new zh-CN mirrors were not, so every PR against `main` tripped this as a "new" regression.

**Before authoring a fix, checked for existing work first** and found **PR #234** (`claude/elegant-hopper-apv11k`, authored by another session at 08:15 UTC that same morning) already contained the correct fix: real authored prose (English + genuine Traditional-register Chinese, not machine-translated) for all 10 stub variants across the 4 files, verified clean by the check script itself, governance-approved, zero baseline-gaming (per the check's own explicit instruction not to silence it via the baseline file). It had been sitting open and unmerged. Verified the diff (8 files, +80/-80, 0 net file-count change — well within the 50-file-deletion safety threshold) and **merged it**: `a3bcd69e3d15410093c4ccb4823f7f39e7a4697d`.

**Note:** PR #234 itself also has a *separate*, still-unresolved `Core tests` failure at a later step: `scripts/ci/smoke_manga_chapter_runner.py` fails with `DAG failed: Chapter writer mode is 'claude' ... no authored chapter script pair was found` — it needs `MANGA_WRITER_MODE=stub` (or an authored pair) for unattended CI smoke runs. This is a **different, later pytest-suite step** than the one blocking #243/#245/#246 (which fail earlier, at the parse-sweep assertion, before ever reaching this step) — **not yet diagnosed or fixed this session.** Worth checking whether it's still present on current `main` and, if so, whether it's blocking anything real.

### Phase I — Propagated the fix to all three open PRs
Merged `origin/main` (now containing PR #234's fix) into all three branches (`claude/manga-infra-verify-prompts-1dokma`, `agent/manga48-zhtw-smoke-cognitive-clarity`, `agent/manga-zhtw-reader-market-allowlist-20260723`) — all merged cleanly, no conflicts — and pushed. As of this document, fresh CI is running on all three: **`parse-sweep` and `Drift detectors` now PASS on all three** (confirms the G-CLAIM fix and the stub-content fix both hold); **`Core tests` was still `in_progress`** at write time (it's a ~12-minute full pytest run) — **next session should check its final result.**

## 3. Current state — all touched PRs

| PR | Title | State | Base commit note |
|---|---|---|---|
| [#206](https://github.com/Pearl-Prime/pearl_prime/pull/206) | Manga image-bank free-infra prompt pack | **MERGED** `8641213c1a` | docs-only |
| [#234](https://github.com/Pearl-Prime/pearl_prime/pull/234) | compassion_fatigue stub-prose fix (EN+zh-CN) | **MERGED** `a3bcd69e3d` | authored by a different session; this session found + verified + merged it |
| [#243](https://github.com/Pearl-Prime/pearl_prime/pull/243) | Manga roadmap doc-drift correction + workstream registration | OPEN, draft, not merged | branch `claude/manga-infra-verify-prompts-1dokma`, head `0a3628d1f0` (post-merge-of-main) |
| [#245](https://github.com/Pearl-Prime/pearl_prime/pull/245) | zh_TW smoke cell — `cognitive_clarity` ep_001 | OPEN, draft, not merged | branch `agent/manga48-zhtw-smoke-cognitive-clarity`, head `c18a760df3`; **do not merge without operator voice/quality read** per the writing pack's own ramp discipline |
| [#246](https://github.com/Pearl-Prime/pearl_prime/pull/246) | `reader_markets` allowlist: add zh_TW | OPEN, draft, not merged | branch `agent/manga-zhtw-reader-market-allowlist-20260723`, head `dc20e940d4` |

All three open PRs are subscribed for webhook activity (CI/review events) in this session's transcript. A `send_later` check-in trigger (~hourly cadence pattern used throughout) was active during the session; verify whether it's still armed or already fired/expired.

## 4. What still needs doing (prioritized)

1. **Check final `Core tests` result on #243/#245/#246** (was `in_progress` at write time) and merge each once green + reviewed, or address any new failure.
2. **#245 explicitly should NOT be merged solo** — per the writing pack's own ramp discipline ("do NOT scale past this [pilot] without an operator read on voice/quality"), the zh_TW pilot cell needs an operator read before the zh_TW wave continues past it, even though it's technically gate-passing.
3. **`check_manga_arc_storyboard.py` genuinely does not exist** despite being cited as mandatory by `docs/agent_prompt_packs/manga_arc_storyboard_planner.md` and the 48ep writing pack. Either author it (per its cited spec) or correct the pack's citation — currently every wave authoring a storyboard is flying blind on this gate.
4. **PR #234's `smoke_manga_chapter_runner.py` / `MANGA_WRITER_MODE=stub` Core-tests failure** — separate from the stub-content issue, not diagnosed. Check if it's still present on current `main`.
5. **Lane 1 (live Pearl Star GPU smoke test)** from the original image-bank prompt pack is still unexecuted — needs a session with real Tailscale/Pearl Star network access (a Mac with Keychain creds, or a properly configured Codespace), not this cloud container.
6. **M3 scale continuation:** ja_JP still 20/37 `NEW_SERIES` cells unauthored; zh_TW has 35 more `NEW_SERIES` cells after the smoke cell (per `ASSIGNMENT_MATRIX.tsv`); zh_TW author pool is thin (now 3 pen-name profiles vs. 255 for ja_JP — flagged as `Q-MANGA48-ZHTW-AUTHORS-01`, default is to keep adding a few per wave, not escalate).
7. **`docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` itself** is still stale (M1/M2/M4 shown as open when they're done) — only `PROGRAM_STATE.md` was corrected this session (via #243); consider updating the roadmap doc's own milestone table too.

## 5. Reusable lessons for next session

- **Rerunning a failed CI job via the Actions API does not pick up PR-body edits** — it replays the original event's stored payload. Force a fresh `synchronize` event (an actual push, even a trivial one) if a body-content-dependent gate needs to re-evaluate.
- **`check_acceptance_claim_language.py` (G-CLAIM)** requires one of `structurally clear | authored candidate | system working | bestseller register | path works | Layer [1-4] | acceptance_layer:` to appear **anywhere** in a PR body/CLOSEOUT that also contains `bestseller|shippable|production-ready|register-PASS` — negating the claim in prose is not enough; use the recognized vocabulary.
- **Specialist locale-QA subagents (e.g. `translate-zh-tw`) correctly refuse out-of-scope authoring+git+PR tasks** — that's a feature, not a bug. Re-dispatch such work to `general-purpose` with an explicit instruction to preserve native-register quality.
- **Before authoring any fix, check for an already-open PR first** (`list_pull_requests` with `head:`, or `git log --all -- <path>` to find commits living on unmerged branches) — this session found two cases (PR #234, and the pre-existing #103 writing-pack program) where real, correct, unmerged work already existed and duplicating it would have wasted effort and diverged from the established character voice/continuity.
- **This container has no Pearl Star / Tailscale network access** — any task requiring live GPU dispatch, ComfyUI, or Ollama on Pearl Star must be handed to a session running somewhere with that connectivity; don't attempt it here, and say so plainly rather than guessing.
- **Session branch reuse after a merge:** if the designated session branch's PR already merged, restart the branch from fresh `origin/main` (`git fetch && git checkout -B <branch> origin/main`) rather than stacking new commits on already-merged history.

---
*Generated by Claude Code, end of session 2026-07-23.*
