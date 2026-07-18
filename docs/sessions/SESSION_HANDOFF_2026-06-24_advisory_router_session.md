# Session Handoff — Advisory/Router Session (2026-06-22 → 2026-06-24)

**Repo:** `Ahjan108/phoenix_omega_v4.8` · **`origin/main` at handoff = `a5b7c06a0d`**
**SSOT:** `docs/PROGRAM_STATE.md` (refreshed in the same commit as this doc — read it first)
**Session type:** router/advisor — produced paste-ready prompts, reviewed plans, made corrections.
Most execution happened in *other* sessions; this doc records the decisions, the prompts dispatched, the
corrections, and the standing lessons.

---

## 0. The single most important clarification this session

**"Listings" ≠ "EPUBs."** The catalog shows **~1,519 tier-3 LISTINGS** (title/subtitle/description/cover/dashboard
= storefront metadata) on main. That is **not** the same as readable, sellable **EPUB files** — of which the current
catalog has **~0 assembled**. This conflation (the word "books") repeatedly misled status reports ("800 EPUBs
assembled" — false; "0% executed" — also false). The SSOT now separates the two tracks; keep them separate.

---

## 1. What landed on main this window (incl. parallel sessions)

- **SSOT established** — `docs/PROGRAM_STATE.md` is the canonical first-read (PR #1841), wired into CLAUDE.md
  Read-First + DOCS_INDEX; stale May planning docs SUPERSEDED-stamped; `worldwide_catalog_plan_*.tsv` archived.
- **GHL marketing feed — LIVE** (#1866/#1867/#1875/#1882): `marketing_feed.json` published on brand-admin Pages
  (public HTTPS), R2 provision workflow, 15-topic integration + E5 coverage, all 15 funnel landings → GHL capture.
- **Waystream publish handoff** (#1877, #5518641b68): publish pipeline + delivery feed + storefront SKUs; EPUB
  render-optimization plan spec (c85008a721).
- **CI green** lane (#1868/#1869/#1870) + devotion_path dashboard covers on CF Pages (#1881).
- **Router Operating Principles v2** updated: PROGRAM_STATE.md first read; PEARL_ARCHITECT_STATE annotated
  cap-registry-only; new **Principle 10** (ground on SSOT + origin/main, never the working tree; listings≠EPUB;
  follow SUPERSEDED headers).

## 2. Decisions / prompts dispatched this session

- **Waystream covers** → finish FLUX pools, `--no-fallback`, dashboard (two-stage covers = PIL text over FLUX
  imagery → re-titling is **zero-GPU**, not a re-render).
- **Title duplication (live, unfixed on main):** Waystream titles are **186 distinct / 800**, subtitles **398/800**.
  A prior title-dedup **stranded on an unmerged branch** — main was never fixed.
- **SEO title fix plan (amended, ready):** hard-gate **distinct titles + distinct (title,subtitle) pairs** (800-unique
  *subtitles* is likely unachievable — gate pairs, not subtitles); scorer biases the persona-scenario form over the
  colliding `Topic: {angle}`; **cover re-composite bundled** (every title change restales the baked cover); keyed by
  **plan book_id** (the cover CSV uses a different id scheme — 0 overlap); land on main.
- **First Waystream EPUB pilot:** `corporate_managers × burnout × overwhelm` → DRAFT (BUILD_EXIT=1) → F1/F4 fix →
  **register PASS / BUILD_EXIT=0 locally**. EPUB: *After the Flame: When Everything Is Too Much* (Theo Castellan).
  ⚠ The F1/F4 fix commit **`4474753be9` is STRANDED — local-only, NOT on origin.** `cc4056b259` (F6/F7/F13) is on
  origin. **Push 4474753be9 before relying on it**, ideally as an engine PR off `origin/main` (these fixes are
  generic — they unblock all brands, not just Waystream).
- **Production-gate residuals** (next cells): F2 (phrasal-verb precision — add motion-arrival verbs, keep dropped-slot
  HARD_FAIL test green), F7 (composer-output cap; verify it preserves exactly 1 genuine atom exercise/chapter).
- **GHL feed plan (amended → landed):** paid items gate on **real attached asset** (not URL-resolves) → `pending_asset`;
  free items gate on **asset-exists** too; **free-content-first launch**, paid auto-promotes on attach. (Now live.)

## 3. Determinism + the "what's needed for 800" question (open audit)

- **Book assembly is deterministic atom-composition** (spine/production composes pre-authored atoms by seed+arc; no
  LLM at build). The LLM was upstream (authoring atoms/plans), once. **One thing to verify:**
  `phoenix_v4/rendering/pearl_writer_expand.py` is in the render path and *can* call an LLM — confirm it is **not**
  invoked in spine/production (thin pool must **raise `InsufficientVariantsError`** → fix by adding atoms, NOT
  LLM-expand at build).
- **The "blocker" is three different axes, not one** (an agent conflated them): (1) **missing cells** = no master_arc
  (`buildable_matrix.tsv`); (2) **exercise inventory** = the 300+ in `SOURCE_OF_TRUTH/exercises_v4/` — **global/shared,
  not per-cell** (`audit_exercise_coverage.py`); (3) **per-cell pool depth** = per-(persona,topic,slot) variants below
  the 12-chapter floor (`atom_coverage_audit.py` — NOT the false-zero gap-matrix TSV).
- **Verify wiring (was working before — don't drift):** the **3-layer story** (`SOURCE_OF_TRUTH/story_atoms/`:
  character_roster + scene_injection_map + story_atom_tier_templates; `story_planner.build_story_schedule`; STORY at
  sec 2/5/9 per PR #669) and the **300+ exercises** are used, not a hardcoded fallback. Known regression to check
  against: `docs/diagnostics/OPD-142_STORY_SCHEDULE_REGRESSION_FORENSIC_2026-05-21.md`.

## 4. Standing lessons reinforced (the expensive ones)

- **STRANDED-COMMIT PATTERN:** work committed locally but **not pushed to origin** vanishes / can't be cherry-picked.
  Hit ≥4× this window — the SSOT v1, the title-dedup, the F1/F4 EPUB fix, and the earlier `en_US_listings` handoff
  (confirmed NOT on main). **Always push to origin; verify with `git branch -r --contains <sha>`.**
- **SHARED-TREE CHURN:** the working tree shows whatever branch it's on, not main (it showed 800-distinct titles
  locally while main had 186). Ground state on `origin/main`, never the working tree or git-date.
- **ASSEMBLY MUST STAY DETERMINISTIC:** thin pools → more atoms, never LLM-at-build.
- **VERIFY-DON'T-ASSERT** caught, this window: the 800-vs-186 titles, the "0% executed" stale May report, the SSOT
  landing on the wrong branch, the catastrophic `*.txt` delete glob (would have nuked the 17,712-file atom corpus +
  `ps.txt`), and the stranded F1/F4 commit.
- **BUDGET ROUTING:** engine/dedup + short atom-variant work → **Sonnet** (and bulk atom-gen → local Gemma on Pearl
  Star) — keep Opus in reserve. Note: Sonnet still counts toward the weekly **all-models** cap (it does not avoid the
  cap; it's just weighted cheaper). Truly $0-Claude = local Gemma/Qwen only.

## 5. Open lanes / NEXT_ACTION (priority order)

1. **First durable Waystream EPUB:** push `4474753be9` to origin (engine PR off main, F1/F4 + F6/F7/F13), verify the
   pilot passes from origin, then F2/F7 precision for the next cells. This is the gate to *any* real sellable book.
2. **Waystream SEO/title fix** (amended plan; **Sonnet**): distinct titles + unique pairs + cover re-composite +
   land on main — fixes the 186-distinct duplication that's live on main.
3. **Determinism + 3-axis "what's needed for 800" audit** (read-only, **Sonnet**): confirm no LLM-at-build, the
   exercises + 3-layer story are wired, and produce the per-brand (missing-arc / per-slot-depth) gap matrix split into
   content-gap (atoms/arcs) vs production-gate-gap.
4. **Localization** — after titles are distinct (so 13 locales inherit clean titles, not multiplied duplication).
5. **Scale:** the ~450 Waystream cells + all-brands EPUBs flow once the gate holds + atoms/arcs fill + the R2/store
   fulfillment is wired (GHL feed already auto-promotes paid items on attach).

**Reality line:** listings + the GHL free funnel + the live store are real on main. **Real sellable EPUBs are still
~0** — the production gate (F-class composer work) + securing the stranded fix + per-cell atom depth are what stand
between the catalog and the first durable, gate-passing, on-the-shelf Waystream book.
