# US Manga Lead-Picks · Status Report
**Date:** 2026-04-23 · **Operator:** Claude Code (Tier 1)
**Update:** Pearl Star is no longer a blocker. All 13 chapter 1 scripts written by Tier-1 prose. Only ComfyUI panel render remains.

## Deliverables in this artifact directory

| File | What it is | Status |
|---|---|---|
| `PITCHES.md` | 13 manga pitches (1 per US brand): logline, premise, character, 5-arc spine, teacher anchor, visual grammar, comp titles, target reader | ✅ Ready |
| `PITCH_REFINEMENT.md` | Re-read notes — 4 small revisions, 8 ready as-is, 1 false alarm | ✅ Ready |
| `CHAPTER_01_stillness_press.md` | Full 18-page chapter script for the Stillness Press lead — format reference | ✅ Ready |
| `CHAPTERS_02_TO_13.md` | Chapter 1 scripts for the other 12 brands — 9–10 pages each, ~6,800 words | ✅ Ready |
| `ROLLOUT_COMMANDS.sh` | Preflights ComfyUI + image-bank gates, runs panel render for all 13 (or one via `--brand`) | ✅ Ready (dry-run verified) |
| `runs/2026-04-23/runlog.txt` | Dry-run log | ✅ |

**Total written:** 13 pitches + 13 chapter 1 scripts (~7,500 words of original prose) + rollout tooling.

## Path A · Unblock + batch all 13

| Subtask | Status | Notes |
|---|---|---|
| Pearl Star Ollama | **No longer needed** | All 13 chapter scripts written by Tier 1. Pearl Star reserved for chapters 2+ scale-up. |
| ComfyUI for image banks | ❌ `COMFYUI_URL` set but server unreachable | Need RunComfy server warmed up. |
| Image bank generation × 13 | ⏸ Blocked on ComfyUI | Script ready: `scripts/image_generation/manga_teacher_batch.py --brand X --count 12`. ~10 min/brand once ComfyUI live. |
| Manga panel render × 13 | ⏸ Blocked on image banks | `ROLLOUT_COMMANDS.sh --execute` once banks populated. |

## Path B · One brand end-to-end (recommended next step)

Stillness Press is the cleanest first target:
- ✅ Chapter script complete (18 pages, format reference quality)
- ✅ Brand profile complete (`config/source_of_truth/manga_profiles/brands/stillness_press_iyashikei.yaml`)
- ✅ Teacher pack populated (Ahjan, Theravada, full TEACHER_DB entry incl. Saṃvega Reset)
- ⏸ Image bank: 0 PNGs at `image_bank/stillness_press/anxiety_overwhelm/` — need ~12 panels
- ⏸ Render: `./ROLLOUT_COMMANDS.sh --brand stillness_press --execute` once images exist

**Estimated wall time once ComfyUI is live:** 25 minutes (15 min image bank + 10 min pipeline render + R2 upload).

## Path C · Pitch refinement

Done — see `PITCH_REFINEMENT.md`. Summary:
- 8/13 ready as-is
- 4/13 want small fixes (re-anchor `bright_presence_tw` teacher to Ra, fix `cognitive_clarity` series_id, ground `sleep_restoration` patient encounter, swap qawwali troupe origin in `heart_balance`)
- 0/13 need full re-pitch (initial flag on `relational_calm` was a false alarm — left in the doc for honesty)
- 2 cross-cutting adds for the deck: explicit chapter count per arc, explicit practice-integration cadence per chapter

## What I did NOT do (and why)

- **Did not bypass the LLM tier policy.** No paid LLM API key was used. The chapter prose was written by Claude Code (the operator-present Tier-1 lane, sanctioned for refactors / features / analysis / **prose generation** per CLAUDE.md). This is the explicit allowance for "any task where a human will review the output before it ships."
- **Did not start ComfyUI for the user.** The server is theirs to spin up; the rollout script preflights and refuses if it's not answering.
- **Did not commit.** All 5 artifact files are uncommitted in `artifacts/manga_us_lead_picks/`. Standing by for direction on whether to commit on this branch (`claude/pensive-hodgkin-3511bd`) or land them somewhere else.

## Single-command reproduction

To verify the dry-run plan after this session:

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/pensive-hodgkin-3511bd
ls artifacts/manga_us_lead_picks/
./artifacts/manga_us_lead_picks/ROLLOUT_COMMANDS.sh         # dry-run
```

To execute path B (one brand end-to-end) once ComfyUI is up:

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
PYTHONPATH=. python3 scripts/image_generation/manga_teacher_batch.py \
  --brand stillness_press --topic anxiety_overwhelm --count 12
./artifacts/manga_us_lead_picks/ROLLOUT_COMMANDS.sh --brand stillness_press --execute
```

## Decision point

Two paths from here:

- **(1) Commit the artifact bundle now** so the work is preserved on the branch, then come back to render when ComfyUI is up.
- **(2) Start ComfyUI now and we run path B in this session** — generate Stillness Press image bank, render the chapter, ship one published manga as the format proof.
