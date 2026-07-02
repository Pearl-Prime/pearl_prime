# Pearl Prime — Beat-Line Ceiling Calibration + Render-Hardening (G1/G2/G3)

**Date:** 2026-07-02
**Lane:** Pearl_Prime render-hardening, fast-follow to PR #4566
**Concept:** `pearl_prime_render_hardening_g1g2g3`
**Base:** `origin/main` (post `2cc6b7a24f`)

## Why this exists

PR #4566 disabled the `365fd19cc3` dwell-beat injector and added a bare-slot HARD gate.
This lane closes the three residual holes that let an **automated-quality-PASS book still
read as stitched one-liners** instead of cohesive bestseller prose:

- **G1** — the word-count *floor padder* re-added standalone one-line filler on the spine
  path (the exact choppy shape the injector produced) to hit a word floor.
- **G2** — the register gate had **no dedicated ceiling** on beat-line density: `F1` only
  inspects paragraphs of ≥3 sentences (one-line beats slip under it) and `F13` is
  advisory (never gates). A ~35%-beat-line render could PASS.
- **G3** — bestseller/catalog builds only reach bestseller register on the full
  **four-piece chord** (`--pipeline-mode spine --quality-profile production
  --exercise-journeys`); a build that omits a flag silently falls back to the fast
  registry path / a non-production profile and ships choppy or gate-skipped output.

Doctrine tie-in: an under-length or thin book is an **atom-shape / thin-pool signal to
surface**, never something to paper over with filler (see memory
`feedback_atom_deficit_is_shape_not_count`). The composer is deterministic — a thin book
raises `InsufficientVariantsError`; it is never LLM-padded.

---

## G1 — Spine word-floor padder disabled

**File:** `scripts/run_pipeline.py` (`_run_spine_pipeline_mode`, both floor call sites).

- `ensure_word_count_floor` is **not called on the spine path**. #4566 no-op'd the
  function body; G1 closes the two **call sites** too, so a future re-enable of the
  function body cannot silently re-introduce choppy filler on the release path.
- An under-length spine render is recorded in the governance report under
  `spine_word_floor_signals` (stage, word_count, floor, `action: not_padded`, reason) —
  surfaced, not padded.
- **Kill-switch:** `PHOENIX_SPINE_WORD_FLOOR_PAD=1` re-enables padding on spine
  (NOT for the release path).

**Q-FASTFOLLOW-01 = (a)** — no-op / surface-as-signal on spine (default). Rejected
alternative (b) "pad only with multi-sentence cohesive atom content": still masks the
thin-pool signal and reaches for content the deterministic composer does not have.

---

## G2 — `F14` beat-line-share ceiling (HARD_FAIL)

**File:** `phoenix_v4/quality/register_gate.py` (`_detect_f14_beat_line_share`, wired into
`evaluate_register` and gated by `_aggregate_verdict`'s generic
`any(f.severity == "HARD_FAIL")`).

**Metric — BEAT-LINE SHARE:**

```
beat_line_share = (# body paragraphs that are a single short standalone beat line)
                  / (# body paragraphs)
```

A paragraph counts as a **beat line** iff it is:
- a single sentence, and
- ≤ `F14_BEAT_MAX_WORDS` (**11**) words, and
- not dialogue, a heading, a chapter marker, a markdown rule, or a list item.

Structural / front-matter lines are excluded from **both** numerator and denominator so
they neither inflate nor mask the ratio. The ratio is only scored once a real book's worth
of paragraphs exists (`F14_MIN_BODY_PARAS = 12`) so short slices stay unflagged.

**Constants:** `F14_BEAT_LINE_SHARE_MAX = 0.25`, `F14_BEAT_MAX_WORDS = 11`,
`F14_MIN_BODY_PARAS = 12`.

**Kill-switch:** `REGISTER_GATE_F14_BEATLINE=0` (or `quality_profile="draft"`) disables it.

### Calibration table

Measured on the two committed fixtures under `tests/fixtures/register_gate_f14/`
(`way_stream_sanctuary · corporate_managers · burnout · grief`):

| Fixture | Beat lines / body paras | Share | Verdict @ cutoff 0.25 |
|---|---|---|---|
| `choppy_stitched_book.txt` (stitched EPUB render, `365fd19cc3`-class) | 198 / 565 | **35.0%** | **HARD_FAIL** |
| `clean_seamwritten_book.txt` (hand-seam-written FINAL, good baseline) | 5 / 181 | **2.8%** | **PASS** (no F14) |

**Cutoff 0.25** sits ~10 pts below the FAIL sample and ~22 pts above the PASS sample —
a wide, stable margin. **Q-FASTFOLLOW-02:** cutoff = 0.25 (25%), the midpoint band that
cleanly separates the two fixtures.

Regression tests (`tests/test_register_gate.py`): `test_f14_hard_fails_choppy_render`,
`test_f14_passes_cohesive_render`, `test_f14_kill_switch_env_disables`.

> **Gotcha honored:** `F1_MIN_PARA_SENTENCES` was **not** lowered to catch beats (that
> false-positives on legitimately short paragraphs). F14 is a dedicated, independent check.

---

## G3 — Four-piece chord CI-assert (no global-default flip)

**File:** `scripts/ci/check_canonical_pipeline_path.py`.

The drift detector was extended from "must use `--pipeline-mode spine`" to the full
canonical chord. Each missing flag is reported as a separate violation reason:

- `--pipeline-mode spine` (canonical bestseller path)
- `--quality-profile production` (all gates at production severity; a variable that
  resolves to it — `$VAR` / `${{ ... }}` — is accepted; a literal `draft`/`debug` is not)
- `--exercise-journeys` (canonical production invocation)

`--render-book` is the **invocation trigger** (production marker), not scored as a chord
flag. Python-list wrappers (`"--flag", "value"`) and shell backslash-continued
invocations are both parsed.

**Kill-switch:** `CANONICAL_PIPELINE_CHORD_FULL=0` reverts to pre-G3 spine-flag-only
checking. **Allowlist:** `# CI-ALLOWLIST: legacy-registry-ok — <reason>` skips a block.

**Q-FASTFOLLOW-03 = (a)** — CI-assert the chord; **do NOT flip the global
`--pipeline-mode` default.** The detector runs in the existing `drift-detectors.yml` gate
at **`--gate-mode warn`** (non-blocking, "warn until PR #1379 lands") over **PR-changed
files only**. Flipping the CLI default from `registry`→`spine` was rejected here: it is a
CLI-default flip with broad structural-test blast radius (every entrypoint invocation
without the flag regresses — memory `feedback_default_flip_test_undercount`) and touches a
ratified cap (`COHESIVE-FLOW-PATH-DEFAULT-SPINE-01`). That flip remains an **operator-tier
escalation**, not landed in this lane.

Repo-wide scan with the full chord ON currently surfaces ~188 warnings (mostly docs shell
examples + a few production workflows missing `--exercise-journeys`). These are
**warnings, not blockers** (warn mode + changed-files scope); folding them in is
follow-up hygiene, tracked as the escalation above.

Regression tests: `tests/ci/test_drift_detectors.py`.

---

## Kill-switch summary

| Gate | Flag | Effect |
|---|---|---|
| G1 | `PHOENIX_SPINE_WORD_FLOOR_PAD=1` | re-enable spine floor padding (non-release only) |
| G2 | `REGISTER_GATE_F14_BEATLINE=0` | disable F14 (also off under `quality_profile=draft`) |
| G3 | `CANONICAL_PIPELINE_CHORD_FULL=0` | revert to spine-flag-only chord check |

## Canonical bestseller invocation (the chord)

```bash
# CI-ALLOWLIST: legacy-registry-ok — documentation reference, not an executed build
PYTHONPATH=. python3 scripts/run_pipeline.py --render-book \
  --pipeline-mode spine --quality-profile production --exercise-journeys
```

## NEXT_ACTION (gate to the 800-book EPUB campaign)

Real-render proof of `corporate_managers × burnout` on a render-capable box: measure
beat-line share **before/after** on a live spine render and confirm G2 (F14) PASSES the
real cohesive render. Local render is blocked here by `NO_STORY_POOL` (no atoms in this
tree), so G2 is calibrated on the committed fixtures; the live-render proof is the gate
that unblocks the 800-book EPUB-assembly campaign.
