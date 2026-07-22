# Manga Drawing-Tradition Wave-2 — Re-implementation Spec

**Status:** SPECCED (nothing below is CODE-WIRED yet — see per-item baseline)
**Written:** 2026-07-21
**Why this doc exists:** A prior Cursor session reported all 4 items below as
"complete, local/uncommitted" on 2026-07-08. That session hit repeated
`ERROR_EXTENSION_HOST_TIMEOUT` crashes. On 2026-07-21 we verified, from the
exact same working directory (`/Users/ahjan/phoenix_omega`,
`agent/bestseller-atom-flow-lanes-20260721`) that session was using, that
**none of the 4 claimed artifacts exist on disk** — no `style_resolution.py`,
no wave-2 genre entries in the tradition config, no closeout `.md` files, and
no matching `git stash` entry across 165+ stashes. The working theory is the
report was emitted without the underlying file writes ever completing (a
stalled extension host can drop a tool call silently while the model still
narrates success) — not that finished work was later deleted. Do not trust
prior "done" claims for this work; verify everything against the live repo
before building on it.

**Instructions for whoever picks this up:** treat every "current baseline"
line below as re-verified as of 2026-07-21. Re-verify again before you start
if time has passed — branch/file state in this repo moves fast and multiple
sibling sessions share working trees here.

---

## Item 1 — Drawing-tradition backfill, wave 2

**Goal:** upgrade 6 genres from `deferred_phase2` to a deep drawing-tradition
block: `mystery`, `supernatural_everyday`, `workplace`, `battle`,
`sci_fi_cyberpunk`, `sports`.

**Current baseline (verified 2026-07-21):** `config/manga/drawing_tradition_per_genre.yaml`
has 8 genres at `status: top_8_deep` (`healing`, `dark_fantasy`,
`psychological_horror`, `mecha`, `romance`, `slice_of_life`,
`fantasy_adventure`, `comedy`) and 17 at `status: deferred_phase2`, including
all 6 target genres for this wave plus `horror`, `essay`, `food`, `family`,
`procedural`, `historical`, `cultivation`, `school`, `memoir`,
`social_issue`, `graphic_medicine`, `battle_internal` (those 12 stay
deferred — out of scope for this wave).

**What actually needs to change:**
1. **Data, not code, is the primary lift:** `phoenix_v4/manga/genre_tradition.py::resolve_tradition_genre()`
   already generically resolves any genre block whose `status != deferred_phase2`
   — it does NOT need new logic to "add" genres, only the YAML config needs
   new blocks. Confirm this reading is still accurate before assuming code
   changes are needed at all.
2. For each of the 6 target genres, author a full drawing-tradition block in
   `config/manga/drawing_tradition_per_genre.yaml` matching the schema used
   by the 8 existing `top_8_deep` genres: `A_line_tradition`, `B_ink`,
   `C_expression`, `D_framing`, `E_palette`, `F_forbidden_drift_patterns`,
   `G_mangaka_exemplars`, `H_token_mapping` (per base_model: `flux_schnell`,
   `qwen_image`, `animagine_xl_4_0`/`animagine`). Use the 8 existing deep
   blocks as the template/reference for depth and structure.
3. Change `status:` from `deferred_phase2` to whatever value the new blocks
   should carry — the report called this `wave_2_deep`; confirm/decide
   whether `resolve_tradition_genre()`'s check (`status != "deferred_phase2"`)
   already treats any non-deferred status as active (it does, per current
   code), so `wave_2_deep` works as a label without further code changes —
   but double check nothing else in the codebase branches specifically on
   `status == "top_8_deep"` in a way that would exclude a `wave_2_deep` value.
4. **`psychological_horror` constraint (must preserve):** it must stay on its
   own deep block and must NOT collapse into the deferred `horror` genre —
   these are two distinct genre ids in the config. Verify `psychological_horror`
   is still `top_8_deep` after your changes (it should be untouched) and that
   `horror` remains `deferred_phase2` (also untouched — not in this wave's scope).
5. Wire-through check: confirm `scripts/manga/visual_from_script.py` and
   `scripts/manga/prompt_authority.py` (note: `prompt_authority.py` lives
   under `scripts/manga/`, not `phoenix_v4/manga/` — verify exact path
   before editing) already call `resolve_tradition_genre()` / consume its
   output for all genres generically (they likely do, since the function is
   generic) rather than needing per-genre-list changes. If they hardcode a
   genre allowlist anywhere, that's the one real code change this item needs.

**Acceptance:** a chapter script with `genre: mystery` (or any of the 6)
resolves non-empty positive/negative tradition tokens from
`resolve_tradition_genre()` + `cookbook_entry()`, folds into panel prompts via
the production compiler, and a `psychological_horror` chapter still resolves
its own tokens (not `horror`'s, which should still fail open to empty).

---

## Item 2 — Qwen Pearl Star worker

**Goal:** replace a stub worker with a real one mirroring
`scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json`
— split loaders, 28 steps, cfg 4.0, stall timeouts 600s/900s, blob gate.

**Current baseline (verified 2026-07-21):** Two worker files exist, and
**neither is obviously the "stub" the report describes** — this needs
re-investigation, not blind replacement:
- `scripts/pearl_star/worker/qwen_manga_worker.py` (207 lines) — has
  `steps: 24, cfg: 4.0` (report claims 28 steps, not 24 — discrepancy to
  resolve) and references `stall_warn_at_s=STALL_WARN_S`,
  `stall_kill_at_s=STALL_KILL_S` (stall-gate machinery already present in
  some form).
- `scripts/pearl_star/worker/qwen_layered_manga_worker.py` (245 lines) —
  not yet inspected for this spec; check whether this is actually the
  "real" worker already, or a different lane entirely.

**What to do:**
1. Read both files fully, and read `qwen_image_no_pulid_manga.json` fully
   (split loaders, node graph, step/cfg values, whatever else it specifies)
   before writing anything.
2. Determine which file (if either) is the target for this rewrite, or
   whether a new file is warranted. Do not assume the report's "replaced a
   stub" framing is accurate — verify from the current code, since the
   report's other claims didn't hold up.
3. Match the reference workflow's actual step count (verify 28 vs the 24
   currently in `qwen_manga_worker.py`) and cfg — don't trust the report's
   number over the actual JSON's numbers if they conflict.
4. Preserve/extend the blob-gate and stall-timeout pattern already used
   elsewhere in `scripts/pearl_star/worker/` for consistency.
5. Per [[reference_r2_presign_one_week_ceiling]] / RAP doctrine
   (`docs/ROBUST_AGENT_PROTOCOL.md`) — queue-first dispatch via `pscli` is
   mandatory for Pearl Star GPU/LLM work; don't bypass the queue.

**Acceptance:** unit graph tests pass (build the ComfyUI graph and assert
node/param shape without needing a live GPU). Live PNG smoke test is
expected to stay blocked unless ComfyUI + the Qwen model trio are actually
on-box on `pearl_star` — confirm current model/ComfyUI availability there
before promising a live smoke test; don't claim "smoke passed" without an
actual rendered PNG to point to (EXECUTED-REAL bar per the manga vision-
conformance doctrine in `CLAUDE.md`).

---

## Item 3 — `assemble_from_bank.py` modernization — DONE (2026-07-21, verified)

**Resolved 2026-07-21:** found this item's actual work sitting as an
uncommitted diff in the working tree (survived because it modified a
tracked file rather than creating new untracked files, unlike items 1/2/4).
Verified the diff was self-contained (no lock contention, no other pending
changes on the file), ran `scripts/manga/tests/test_assemble_from_bank.py`
pre-commit (33 passed, 2 skipped), committed narrowly-scoped as
`aad5cf2152`, then re-ran the tests against the committed state to confirm
(same result: 33 passed, 2 skipped). This item is CODE-WIRED and
test-verified. No further action needed unless new gaps are found.

**Goal (original, for reference):** keep it as the canonical bank
compositor; `--bubbles` should use `bubble_render_v2` with genre-aware
config sourced from the manifest.

**Current baseline (verified 2026-07-21): this one is already mostly true.**
`scripts/manga/assemble_from_bank.py` already references
`phoenix_v4.manga.chapter.bubble_render_v2.render_bubbles_onto_panel_v2` and
has a `--bubbles`-related genre-aware wiring block (see line ~1099 comment
"Genre for bubble_render_v2: CLI wins, else manifest/series metadata" and the
import + `--help` string near line ~1133-1197 as of this writing — line
numbers will drift, re-grep).

**What to do:**
1. First determine whether this is pre-existing baseline code (predates the
   2026-07-08 session and isn't actually "wave 2" work) or was genuinely
   landed by that session through some path that did survive (e.g. committed
   directly rather than left uncommitted — check `git log -p` on this file
   around 2026-07-08 for a real commit, since this is the one item where
   something matching the report's description is actually present).
2. If it's pre-existing/already correct, this item may need **no further
   work** — just confirm against the report's specific claims:
   - callsites: `generate_assembly_manifest.py`, `run_composition_grammar_pilot.py`,
     `m5_prep_bank_contracts.py`, `test_assemble_from_bank.py` — grep for
     `assemble_from_bank` imports/calls in each and confirm they're current.
   - closeout claims a "replacement" relationship with
     `phoenix_v4/manga/chapter/bubble_render_v2.py` — confirm that file
     exists and is the one actually imported (it should, per the grep above).
3. If gaps are found, close them; if not, write a short verification note
   (not a fabricated closeout) documenting what was checked.

**Acceptance:** `test_assemble_from_bank.py` passes; a manifest-driven
`--bubbles` run picks up genre from the manifest/series metadata without a
CLI override, and CLI override still wins when given.

---

## Item 4 — Style default removal

**Goal:** stop defaulting every chapter render to `style_id=dark_psychological`
regardless of genre; resolve style through an explicit authority chain with a
narrow, documented fallback.

**Current baseline (verified 2026-07-21):** `phoenix_v4/manga/style_resolution.py`
**does not exist**. Three CLI entry points still hardcode the old default:
- `scripts/manga/run_chapter_production.py:42` — `ap.add_argument("--style-id", default="dark_psychological")`
- `scripts/manga/run_chapter_visual.py:44` — same
- `scripts/manga/run_manga_chapter.py:93` — same

This item has **not been started** — the report's claim that this was done
was false on this checkout.

**What to build:**
1. New module `phoenix_v4/manga/style_resolution.py` implementing an
   explicit authority chain, highest to lowest priority (per the report,
   verify this ordering makes sense against how the 3 CLI scripts actually
   consume style today): explicit override → script style → request style →
   teacher archetype → profile grammar → genre-family signal → fallback.
2. Fallback rule: `grounded_realism` when nothing else resolves — confirm
   this genre id exists somewhere sensible (check `config/manga/canonical_genre_list.yaml`
   or the style/archetype config it should live in) before hardcoding it.
3. Change the 3 CLI scripts' `--style-id` default from `"dark_psychological"`
   to `None` (or omit default entirely), and have them call the new
   resolver when no explicit `--style-id` is passed.
4. Report's claimed test cases (re-verify each, don't assume): `healing` →
   `cozy_iyashikei`; `psychological_horror` → `dark_psychological`; `mecha`
   → `power_progression`; explicit override wins over everything; no-signal
   → `grounded_realism` (source=`narrow_fallback`).

**Acceptance:** a healing-genre chapter run with no `--style-id` resolves to
an iyashikei-family style, not `dark_psychological`; an explicit
`--style-id` flag still overrides everything; a genre-less/signal-less
request falls back to `grounded_realism` and logs why (source tag).

---

## Cross-cutting

- **Tests:** the report claimed "28 tests pass across style resolution,
  wave-2 tradition, genre wiring, qwen graph, and scene-aware compiler" —
  none of these test files/additions exist on this checkout either (they'd
  live near the modules above, likely `tests/manga/` or co-located). Write
  real tests as part of implementing each item, don't assume the count.
- **Closeouts:** write real closeout artifacts at
  `artifacts/qa/manga_<item>_closeout_<date>.md` only after the work is
  actually verified working — match the honest-acceptance-taxonomy rule in
  `CLAUDE.md` (SPECCED vs CODE-WIRED vs EXECUTED-REAL vs PROVEN-AT-BAR).
- **Commit discipline:** this working tree has multiple concurrent sibling
  sessions active (observed directly during the 2026-07-21 R2/cleanup work
  in this same repo). Commit each item's work promptly and narrowly-scoped
  (`git commit -- <specific paths>`, never a bare `git commit -a` or
  pathspec-less commit) to avoid sweeping in a sibling session's unrelated
  staged changes — this happened once already today (see commit `eca2842a18`
  fixing a contamination from commit `969cbecf36`).
- **Do not repeat the original failure:** after any file write, verify it
  landed on disk (`ls`/`cat`/`git status`) before reporting the item done.
  Don't narrate completion from intent.
