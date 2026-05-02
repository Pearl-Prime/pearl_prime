# Portrait Cover Regeneration Plan — 13 EPUBs

**Status:** Operator-actionable. **No render budget required for the recommended path.**
**First written:** 2026-04-30 (Session 6 of the Phoenix Omega 100% production campaign)
**Owners:** Operator (run rebuild + validate) + Pearl_GitHub agent (refactor follow-ups if needed)

---

## 0. Goal

Move the 13 EPUBs in `artifacts/epub/` from invalid square covers
(1024×1024) to KDP-valid portrait covers (1600×2560). Validation closes via
the existing `scripts/publish/validate_epub.py --batch artifacts/epub/`
gate landed in Session 2 ([PR #812](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/812)).

## 1. Why this exists

Session 2's validator found that **all 13 shipped EPUBs fail KDP's
`cover_below_kdp_min` gate** — every cover is square 1024×1024, KDP requires
≥1000×1600 portrait. Without this fix, D-1.4 (first KDP submission test)
cannot succeed.

```
$ python3 scripts/publish/validate_epub.py --batch artifacts/epub/
[exit 1]
13/13 EPUBs flagged: cover_below_kdp_min
```

## 2. Inventory — the 13 books

| EPUB file | Title | Lang | Source cover (1024²) | Current EPUB cover | Words |
|-----------|-------|-----|----------------------|---------------------|------:|
| `adi_da_self_worth.epub`         | You Were Always Enough               | en | `artifacts/pipeline_examples/adi_da/cover_adi_da_self_worth.png`            | 1024×1024 | 5,379 |
| `ahjan_anxiety.epub`             | The Alarm Is Lying                   | en | `artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety.png`                 | 1024×1024 | 5,682 |
| `joshin_anxiety.epub`            | Quiet Enough                         | en | `artifacts/pipeline_examples/joshin/cover_joshin_anxiety.png`               | 1024×1024 | 5,358 |
| `junko_overthinking.epub`        | The Loop Breaker                     | en | `artifacts/pipeline_examples/junko/cover_junko_overthinking.png`            | 1024×1024 | 5,214 |
| `maat_boundaries.epub`           | The No That Saved Me                 | en | `artifacts/pipeline_examples/maat/cover_maat_boundaries.png`                | 1024×1024 | 6,397 |
| `master_feung_burnout.epub`      | After Burnout                        | en | `artifacts/pipeline_examples/master_feung/cover_master_feung_burnout.png`   | 1024×1024 |   254 ⚠️ |
| `master_sha_grief.epub`          | The Weight of Gone                   | en | `artifacts/pipeline_examples/master_sha/cover_master_sha_grief.png`         | 1024×1024 | 4,715 ⚠️ |
| `master_wu_courage.epub`         | The Way of Courage                   | en | `artifacts/pipeline_examples/master_wu/cover_master_wu_courage.png`         | 1024×1024 |   296 ⚠️ |
| `miki_imposter_syndrome.epub`    | Who Let Me In                        | en | `artifacts/pipeline_examples/miki/cover_miki_imposter_syndrome.png`         | 1024×1024 | 6,266 |
| `omote_sleep_anxiety.epub`       | Dark Room, Loud Brain                | en | `artifacts/pipeline_examples/omote/cover_omote_sleep_anxiety.png`           | 1024×1024 | 6,071 |
| `pamela_fellows_anxiety.epub`    | Wired for Worry                      | en | `artifacts/pipeline_examples/pamela_fellows/cover_pamela_fellows_anxiety.png` | 1024×1024 | 5,186 |
| `ra_imposter_syndrome.epub`      | The Proof Was Always You             | en | `artifacts/pipeline_examples/ra/cover_ra_imposter_syndrome.png`             | 1024×1024 | 6,032 |
| `sai_ma_grief.epub`              | Still Here Without You               | en | `artifacts/pipeline_examples/sai_ma/cover_sai_ma_grief.png`                 | 1024×1024 | 4,943 ⚠️ |

⚠️ = the book also fails the validator's `word_count_low` WARN gate
(under 5000 words). For Master Feung (254w) and Master Wu (296w) the EPUBs
are render fragments, not real books; cover regen does not unblock KDP for
those titles until the books themselves are re-rendered. They are listed
here for completeness only.

## 3. The four cover-source options

Per the operator's Session 6 brief:

| Option | Source | Cost | Output quality | Time |
|--------|--------|-----:|----------------|------|
| **A. Letterbox existing 1024² → 1600×2560** (existing builder, no `--raw-cover`) | Existing PNGs in `pipeline_examples/<teacher>/` | **$0** (local Pillow CPU) | Acceptable — original art centered, light-gray gutters top+bottom (~480 px each side) | minutes |
| **B. Local AI upscale + outpaint** (Real-ESRGAN + SD outpaint, or similar) | Existing PNGs + local model weights | $0 (local GPU/CPU) | Good — extended composition fills the gutters | ~hour |
| **C. Re-render via synced RunComfy** at 1600×2560 native | FLUX prompt per book (cover prompts are in `artifacts/pipeline_examples/<teacher>/cover_*.png` source workflows; can be reconstructed) | ~$0.04/image × 13 + ~30% retry rate ≈ **~$0.68** | Best — purpose-shaped portrait composition | hour after deployment sync (Session 5 §3A must land first) |
| **D. Manual operator / art pass** | Human or stock | hours-days human time | Best (curated) | 1–3 days |

### What's already available

`scripts/release/build_epub.py:prepare_embedded_ebook_cover()` already
contains **the option A path** (letterbox to `_EBOOK_COVER_W=1600` ×
`_EBOOK_COVER_H=2560` with light-gray fill `(245, 245, 245)`). It runs
automatically **unless** `--raw-cover` is passed.

The 13 EPUBs were apparently built with `--raw-cover`, OR before this
logic existed (the function is in the current builder). Either way: the
fix is to **rebuild without `--raw-cover`**. No new code needed.

### In-memory verification (run 2026-04-30, no files changed)

```
Target: 1600x2560

cover source                                       in         out         out_kb
------------------------------------------------------------------------------
adi_da/cover_adi_da_self_worth.png                 1024x1024  1600x2560     1134
ahjan/cover_ahjan_anxiety.png                      1024x1024  1600x2560     1451
joshin/cover_joshin_anxiety.png                    1024x1024  1600x2560     2533
junko/cover_junko_overthinking.png                 1024x1024  1600x2560     2448
maat/cover_maat_boundaries.png                     1024x1024  1600x2560     1411
master_feung/cover_master_feung_burnout.png        1024x1024  1600x2560     2944
master_sha/cover_master_sha_grief.png              1024x1024  1600x2560     1988
master_wu/cover_master_wu_courage.png              1024x1024  1600x2560     3362
miki/cover_miki_imposter_syndrome.png              1024x1024  1600x2560     1609
omote/cover_omote_sleep_anxiety.png                1024x1024  1600x2560     2596
pamela_fellows/cover_pamela_fellows_anxiety.png    1024x1024  1600x2560     1635
ra/cover_ra_imposter_syndrome.png                  1024x1024  1600x2560      914
sai_ma/cover_sai_ma_grief.png                      1024x1024  1600x2560     1663
```

13/13 sources letterbox cleanly. Largest output ~3.4 MB, well under KDP's
650 MB cap.

## 4. Recommendation — staged path A → C

**Stage 1 (NOW): Path A.** Run the builder without `--raw-cover` to
unblock the first KDP submission test. Cost $0, time minutes,
KDP-compliant immediately. Visual cost is the gray gutters; acceptable for
a first end-to-end ship to validate KDP pipeline.

**Stage 2 (after Session 5 §3A lands): Path C.** Re-render the 11
non-fragment covers natively at 1600×2560 via the synced RunComfy
deployment + the cookbook's per-genre prompts (PR #802). Costs ~$0.50,
delivers marketing-grade visuals.

**Skip B** unless A's gray gutters become a blocker — extra complexity
for marginal gain.

**Skip D** unless A and C both fail; manual art is the cost backstop, not
the default.

**Out of scope here:** the 3 books with `word_count_low` WARN
(Master Feung, Master Wu — fragments under 500 words; Master Sha — 4,715,
borderline). Those are content gaps, not cover gaps. Cover regen alone
won't make them KDP-shippable.

## 5. Stage 1 execution — Path A (recommended starting point)

### Prerequisite: confirm builder dependencies

```bash
python3 -c "from ebooklib import epub; from PIL import Image; print('ok')"
```

If either import fails, install: `pip install ebooklib Pillow`.

### Rebuild all 13 (single command)

The builder's `--batch` mode iterates the `TEACHER_BOOKS` manifest baked
into [`scripts/release/build_epub.py`](../../scripts/release/build_epub.py)
(13 entries, exactly matches the inventory above). Run **without
`--raw-cover`** so `prepare_embedded_ebook_cover()` letterboxes:

```bash
# Dry-run first (lists what would be built; touches nothing)
python3 scripts/publish/build_epub.py --batch --dry-run

# Real build (overwrites artifacts/epub/*.epub)
python3 scripts/publish/build_epub.py --batch
```

The wrapper `scripts/publish/build_epub.py` is the operator-stable entry
point landed in Session 3 ([PR #813](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/813));
it forwards verbatim to `scripts/release/build_epub.py`.

### Single-book rebuild (for spot fixes)

```bash
python3 scripts/publish/build_epub.py \
    --input artifacts/pipeline_examples/ahjan/book_ahjan_anxiety_15min.txt \
    --title "The Alarm Is Lying" \
    --subtitle "A Nervous System Guide to Anxiety Recovery" \
    --author "Ahjan" \
    --publisher "Inner Light Press" \
    --cover artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety.png \
    --output artifacts/epub/ahjan_anxiety.epub
```

Note: omit `--raw-cover`. That's the whole fix.

### Validation loop (per Session 6 brief)

```bash
python3 scripts/publish/validate_epub.py --batch artifacts/epub/
```

**Expected post-Stage-1 result:**
- Exit code 0 (or only WARN-level findings)
- All `cover_below_kdp_min` ERRORs cleared (13 → 0)
- Remaining findings expected:
  - 3× `word_count_low` WARN (Master Feung, Master Wu, Master Sha) — pre-existing content gap, not a cover issue
  - Possibly 13× `cover_below_kdp_ideal` WARN (1600×2560 letterboxed = exactly the KDP ideal target; the WARN fires only if dimensions are below ideal, which they won't be)

### If anything blocks

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Builder still produces 1024×1024 covers | Pillow not installed | `pip install Pillow` |
| `cover_below_kdp_min` still flagged | `--raw-cover` accidentally passed | Re-run without that flag |
| `epub_unreadable` after rebuild | Disk space / write permission | Check `ls -la artifacts/epub/` |
| Pillow MemoryError | Source image too large | Pre-resize source to ≤4096² before rebuild |

## 6. Stage 2 execution — Path C (after Session 5 §3A)

### Gating prerequisites

- Session 5 §3A complete (RunComfy deployment synced with `flux1-dev` config)
- Cookbook prompts merged ([PR #802](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/802) — already merged 2026-04-30)
- `smoke_test_flux_workflow_fix.py` refactored to use the production override shape (per Session 5 §5)

### Generation script (does not exist yet)

A new `scripts/publish/regen_covers.py` would iterate the 11
non-fragment books, fetch each book's cover prompt (reconstructable from
the existing `pipeline_examples/<teacher>/` workflows or the cookbook),
submit to RunComfy at `width=1600 height=2560` natively, and write
`artifacts/pipeline_examples/<teacher>/cover_<topic>_v2.png`. Then rebuild
EPUBs against the new sources. **This script is a future-PR deliverable.**

### Cost estimate

11 books × ~$0.04/image × 1.3 retry rate ≈ **$0.57 per full run**.

### Validation

Same `validate_epub.py --batch artifacts/epub/`. Expected: exit 0, all
ERRORs cleared, no WARN about `cover_below_kdp_ideal`.

## 7. Operator action items (ordered)

### Immediately (Stage 1, $0)

1. Run `python3 scripts/publish/build_epub.py --batch --dry-run` to confirm the 13-book manifest looks right.
2. Run `python3 scripts/publish/build_epub.py --batch` to rebuild all 13 EPUBs (overwrites `artifacts/epub/*.epub`).
3. Run `python3 scripts/publish/validate_epub.py --batch artifacts/epub/` to confirm all 13 pass the cover gate.
4. Commit the regenerated EPUBs as a small follow-up PR: `chore(epub): rebuild 13 EPUBs at 1600×2560 portrait (Stage 1 of Session 6 plan)`.
5. Decide which books are ready for KDP submission test (D-1.4) — the 10 with word_count ≥ 5,000 are the natural Stage-1 set.

### After Session 5 §3A (Stage 2, ~$0.50)

6. Open a follow-up PR: `feat(publish): regen_covers.py — native 1600×2560 cover regen via synced RunComfy`.
7. Run the regen against the 10 ready titles; validate; commit refreshed EPUBs.
8. Rerun `validate_epub.py --batch`; confirm no `cover_below_kdp_ideal` WARNs remain.

### Backlog (separate workstream)

9. Re-render the 3 fragment books (Master Feung, Master Wu, Master Sha) through the spine pipeline + Session 4 safety gate before any cover-side work.

## 8. Cost / risk envelope

| Action | Cost | Risk |
|--------|------|------|
| Read this plan | $0 | none |
| Stage 1 dry-run | $0 | none |
| Stage 1 rebuild (all 13) | $0 | low — backs out by `git checkout artifacts/epub/` |
| Stage 1 validate batch | $0 | none |
| Stage 1 KDP test ship (1 book) | $0 (KDP free to upload; revenue gates at sale) | low |
| Stage 2 RunComfy regen (11 books) | ~$0.57 | low — bounded |
| Stage 2 retry budget | ~$0.30 (worst case) | low |

## 9. Success criterion (per operator brief)

> "There is a clean, executable path from 'invalid square covers' to 'KDP-valid portrait covers.'"

**Achieved.** Stage 1 commands above are an executable path that produces
KDP-valid 1600×2560 portrait covers for 13/13 books at $0 cost. Stage 2 is
the quality upgrade once Session 5 unblocks it.

## 10. References

- [`docs/runbooks/RUNCOMFY_DEPLOYMENT_SYNC_RUNBOOK.md`](RUNCOMFY_DEPLOYMENT_SYNC_RUNBOOK.md) — Session 5
- [`scripts/publish/build_epub.py`](../../scripts/publish/build_epub.py) — Session 3 wrapper
- [`scripts/publish/validate_epub.py`](../../scripts/publish/validate_epub.py) — Session 2 validator
- [`scripts/release/build_epub.py:176`](../../scripts/release/build_epub.py) — `prepare_embedded_ebook_cover()` letterbox logic
- [`docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md`](../PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md) — D-1.2 / D-1.4 deliverables

---

## 11. What this PR (Session 6) ships

This document. **No code changes. No new EPUBs. No render budget spent.**
The plan is the deliverable; the actions inside it are operator + future-session work.

## 12. Cookbook v2 — corrected per-genre prompts (added 2026-05-02)

Stage 2 (Path C, native re-render via RunComfy) now sources its per-book
FLUX prompts from
[`config/manga/genre_prompt_cookbook_v2.yaml`](../../config/manga/genre_prompt_cookbook_v2.yaml).

The v2 cookbook supersedes the thin per-genre prompt fragments that lived
inside the prior `cover_regen_manifest.yaml`. The single most important
change is the **negation-rule fix from PR #802 §8**:

> Move all negations into a real negative-prompt slot. Stop appending
> `no text, no typography, no letters` to the positive. Either send them
> in the deployment's negative-prompt node, or drop them — appending them
> inline is actively harmful.

The prior fragments violated this; cookbook v2 does not. Every per-genre
`subject_prompt` and `style_modifiers` block in v2 is **pure positive
tokens**, and ALL negations are consolidated in the cookbook's
`universal_negative` field, which is piped to the deployment's negative
CLIPTextEncode slot by the (forthcoming) Stage-2 regen script.

### How Stage 2 will use the cookbook

The future `scripts/publish/regen_covers.py` (per §6 above) consumes
cookbook v2 via the helper script:

```bash
# Compose the FLUX positive prompt for a single book
python3 scripts/manga/cookbook_v2_compose_prompt.py --book ahjan_anxiety

# Also emit the negative for the negative-slot CLIPTextEncode override
python3 scripts/manga/cookbook_v2_compose_prompt.py \
    --book maat_boundaries --negative
```

Library API for the regen script: `compose_positive(book_id) -> str` and
`compose_negative() -> str` from
[`scripts/manga/cookbook_v2_compose_prompt.py`](../../scripts/manga/cookbook_v2_compose_prompt.py).

### Coverage and revisit gates

Cookbook v2 covers all 9 genres represented in the 13-book inventory:
`anxiety`, `sleep_anxiety`, `grief`, `boundaries`, `self_worth`,
`overthinking`, `imposter_syndrome`, `burnout`, `courage`. At first issue
every genre carries `revisit_after_r1: true` because R1's bestseller
archetype analysis
(`artifacts/research/kdp_bestseller_cover_analysis_2026-05-02.md`) had
not yet landed when the cookbook was authored. The cookbook is correct on
the negation rule and shippable as-is; the operator should refine each
genre's `archetype` / `palette` / `subject_prompt` against R1's findings
before mass regen.

### Loader and shape gates

Tests in [`tests/test_cookbook_v2_loader.py`](../../tests/test_cookbook_v2_loader.py)
pin the schema and enforce the no-negations-in-positive rule at CI time.

## 13. R5 — template-based two-stage flow (added 2026-04-30)

PR #837 (R4) landed
[`config/publishing/bestseller_templates.yaml`](../../config/publishing/bestseller_templates.yaml),
which declares per-genre **non-overlapping pixel zones** for imagery,
title, subtitle, and author. R5 (this PR) rewrote
[`scripts/publish/render_kdp_cover.py`](../../scripts/publish/render_kdp_cover.py)
to consume that contract and added a Stage-1 imagery script,
[`scripts/publish/render_imagery_for_template.py`](../../scripts/publish/render_imagery_for_template.py).
The result is a clean two-stage flow that replaces the R3
"render anything → bolt text on top → matte hack" architecture.

### The flow

```bash
# Stage 1 — FLUX renders imagery patches at each genre's
# imagery_zone aspect ratio (1.04:1 for sleep_anxiety,
# 2.40:1 for courage, etc.). Type-dominant genres
# (boundaries / self_worth / imposter_syndrome) are skipped:
# they have imagery_zone == null and never call FLUX.
python3 scripts/publish/render_imagery_for_template.py --batch \
    --config dev --i-have-confirmed-pearl-star

# Stage 2 — Composite the imagery patch into the canvas at the
# template's pixel coordinates, paint palette.primary.hex into
# the rest of the canvas, and composite type into title /
# subtitle / author zones (which never overlap imagery_zone
# by template construction). Also handles the type-dominant
# flat-canvas path.
PYTHONPATH=. python3 scripts/publish/render_kdp_cover.py --batch

# Gate — KDP validator must pass.
python3 scripts/publish/validate_epub.py --batch artifacts/epub/
```

### Why it works (where R3 failed)

* **No more text-on-imagery overlap.** R4's templates declare
  `overlap_rule: no_overlap` and the renderer enforces zone
  boundaries at render time. Title/subtitle/author each occupy
  their own non-overlapping pixel rectangles.
* **No more matte/backdrop band-aids.** Those R3 layers patched
  text-over-imagery contrast; with strict zones they are
  unnecessary and have been deleted.
* **Type-dominant genres bypass FLUX.** `boundaries`,
  `self_worth`, and `imposter_syndrome` are pure-typography
  bestsellers; the renderer paints `palette.primary.hex` over
  the canvas and composites type only.
* **Aspect-aware FLUX prompts.** Cookbook v2 (R5-rewritten per
  R4 §11) prompts FLUX at the imagery_zone aspect, not at the
  full 5:8 canvas. A 2.40:1 mountain prompt no longer comes back
  as a portrait crop with cliff-faces baked into the title region.

### Authority

* [`config/publishing/bestseller_templates.yaml`](../../config/publishing/bestseller_templates.yaml)
  — R4's contract; the source of truth for layout zones, palette,
  and type ratios.
* [`artifacts/research/bestseller_composition_templates_2026-05-03.md`](../../artifacts/research/bestseller_composition_templates_2026-05-03.md)
  §11 (per-genre FLUX prompts) and §10 (cross-genre rules).
* [`config/publishing/kdp_cover_typography.yaml`](../../config/publishing/kdp_cover_typography.yaml)
  — owns per-genre fonts (kept; R5 added Caveat for
  imposter_syndrome's script accent).
