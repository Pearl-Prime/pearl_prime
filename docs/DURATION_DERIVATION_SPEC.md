# Duration Derivation Spec — Pearl Prime runtime formats

**Status:** ACTIVE (ratified 2026-06-12; Phase-2 config + CI guard landed; Group A stub backfill 2026-07-07).
**Owner:** Pearl_Architect (spec) → Pearl_Dev (config + CI build).
**Cap entry:** `DURATION-DERIVATION-01` (`docs/PEARL_ARCHITECT_STATE.md`).
**Mirrors:** `AUTO-PLAN-SSOT-01` — single registry is the canonical source; downstream readers derive, never hand-set.
**Date:** 2026-06-12 · **Scope:** en-US only (CJK deferred — see §7).

---

## 0. TL;DR

A runtime format's advertised duration is today a **hand-set label** (`duration_minutes` in
`config/format_selection/format_registry.yaml`) that is disconnected from the format's real word
target and from the 150 WPM the product actually ships at. The landed audit
(`artifacts/qa/duration_correctness_audit_20260611/`, PR #1510 `f27dafdb2`) proved the gap:
`standard_book` is advertised at **55 min** but is really **~143 min (2h23m)** as an audiobook at
150 WPM — **+161%**. The books are gold-quality and the right length; **the labels are wrong.**

This spec makes the advertised duration a **derived value**, single-sourced from `tts_wpm` and the
format's word target:

```
audiobook_minutes = round(word_target / 150)     # intended TTS pace (config + OVERLAY §413)
ebook_minutes     = round(word_target / 230)     # reading edition
```

It defines the `word_target` derivation (a new per-format `fill_regime` field), single-sources the
WPM constant, reconciles `standard_book`'s word-range cap (18k→22k), specifies a CI co-change guard
so words and minutes can never drift apart again, scopes to en-US, and lays out the
`duration_minutes` deprecation/migration path.

**Phase boundary:** this document DESCRIBES the rules. Phase-2 config + CI guard **landed**
(2026-06-12+); Group A atom-native stub backfill landed 2026-07-07. Reader migration of
`duration_minutes` and CJK char-based audit remain open follow-ups.

---

## 1. Problem statement (grounded in the landed audit)

Read the audit first: `artifacts/qa/duration_correctness_audit_20260611/DURATION_CORRECTNESS_REPORT.md`
(+ `RECOMMENDATIONS.md`, `projection_results.json`).

### 1.1 There is no word→minute formula in the advertising path

Each runtime format carries a hand-set fixed `duration_minutes` in `format_registry.yaml`. It is
never derived from word count. The **only** word→minute conversion anywhere in the codebase is:

```yaml
# config/duration_scorecard.yaml
duration_adherence_scorecard:
  tts_wpm: 150            # "TTS WPM estimate (standard audiobook pace)"
  duration_tolerance_pct: 10
```

…and it is consumed **only** by the read-only measurement tool
`phoenix_v4/ops/duration_adherence_scorecard.py` (`estimated_min = actual_words / wpm`, lines ~293
and ~455–456). It is never the source of the advertised number. So the label and the measurement
tool can silently disagree, and they do.

### 1.2 Intended consumption pace = 150 WPM (audiobook), confirmed twice

- `config/duration_scorecard.yaml` → `tts_wpm: 150`
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` §413 (verbatim): *"read the atom sequence
  aloud at TTS pace (flat, 150 WPM)."*

The ebook reading edition (Pearl Prime ships both) is conventionally ~230 WPM.

### 1.3 The marketing gap is systematic (Mode 2)

At 150 WPM, **7 of 10 fully-specced formats run long past tolerance**; only `deep_book_4h` (−11%)
and `deep_book_6h` (+2%) are honest. Headline: `standard_book` advertised ≈ "1 hour", real
audiobook ≈ **2h23m** (+161%). Implied WPM across formats spans **125 → 364** with no consistent
formula (`DURATION_CORRECTNESS_REPORT.md` §2–§3).

### 1.4 Three fill regimes already exist implicitly (root of word_target)

The pipeline already fills word budgets three different ways. This spec **names** them; it does not
invent them.

| regime | rule (today, implicit) | anchor on `origin/main` |
|---|---|---|
| **midpoint** | plan total validated to word_range midpoint ±10% | `phoenix_v4/planning/beatmap_compile.py:651` (`raise ValueError ... outside ±10% of runtime midpoint`) |
| **cap** | gold/depth-fill pins to the ceiling | QA gold `standard_book`: pre_depth 19,026 → depth-fill 20,000 (=cap target) → render ~21,454 |
| **floor** | fills to just above the floor | `deep_book_6h` registry comment: "compose retains ~72% → ~52K final (clear 50K floor)" |

### 1.5 Mode 1 (cap overshoot) is real but contained

`standard_book` exceeds its own word cap in **94%** of gold books (median ~21,514, +7.6% over the
20k depth-fill target). Historically "fixed" by **raising the cap** (13k→18k→20k) while the 55-min
label never moved — i.e. the cap was moved to match the overshoot, masking the problem. This spec's
guard (§6) plus the `standard_book` cap reconciliation (§5) close this without shrinking books.

---

## 2. Design principle — registry-as-SSOT (mirrors AUTO-PLAN-SSOT-01)

`AUTO-PLAN-SSOT-01` established: `format_registry.yaml` is the canonical home for a per-format value
(`chapter_count_default`), and the duplicate hand-maintained copy
(`book_structure_plan.FORMAT_CHAPTER_COUNTS`) must read from it rather than diverge.

This spec applies the same principle to duration:

1. **The word target is derived from registry fields** (`word_range` + a new `fill_regime`), not
   hand-set.
2. **The advertised minutes are derived from the word target and a single `tts_wpm` constant**, not
   hand-set.
3. **The same `tts_wpm` constant** feeds both the advertised-duration derivation and the read-only
   adherence scorecard, so label and measurement can never disagree (§4.3).

Net: one value (`tts_wpm`) and two registry fields per format (`word_range`, `fill_regime`)
determine the advertised duration. No second source of truth.

---

## 3. The `fill_regime` field (NEW, per format)

A new required field on each fully-specced runtime format in `format_registry.yaml`:

```yaml
runtime_formats:
  standard_book:
    fill_regime: cap        # NEW. one of: cap | floor | midpoint
    # ... existing fields (word_range, chapter_count_default, etc.)
```

| value | meaning | word_target derivation (§4.1) |
|---|---|---|
| `cap` | gold/depth-fill pins to the ceiling (the $-makers path) | `word_range[max]`, or a declared `cap_word_target` override if present |
| `floor` | fills to just above the floor | `round(word_range[min] × 1.04)` |
| `midpoint` | plan validated to word_range midpoint ±10% | `round((word_range[min] + word_range[max]) / 2)` |

### 3.1 Initial assignment (from the audit's measured regimes)

| format | fill_regime | source |
|---|---|---|
| standard_book | `cap` | gold depth-fill pins to ceiling; 94% over cap |
| deep_book_6h | `floor` | registry comment "~52K final (clear 50K floor)" |
| micro_book_15 | `midpoint` | audit regime=midpoint |
| micro_book_20 | `midpoint` | audit regime=midpoint |
| short_book_30 | `midpoint` | audit regime=midpoint |
| extended_book_2h | `midpoint` | audit regime=midpoint |
| deep_book_4h | `midpoint` | audit regime=midpoint |
| compact_book_5ch_15min | `midpoint` | audit regime=midpoint |
| compact_book_5ch_20min | `midpoint` | audit regime=midpoint |
| compact_book_8ch_30min | `midpoint` | audit regime=midpoint |
| one_hour_book | `midpoint` | NEW first-class 1-hour tier (operator OPD-20260613-001); midpoint(8000,10000)=9000 |

These assignments mirror the `regime` field already recorded per-format in
`projection_results.json` — they are not new editorial choices.

### 3.2 The 1.04 floor multiplier

The `floor` regime uses `× 1.04` (not the raw floor) because compose/dedup overshoots the floor
slightly to clear it deterministically (`deep_book_6h` median 55,229 vs floor 50,000 ≈ +10%, but
the spec uses a conservative +4% so the *label* under-promises rather than over-promises). The
derived `deep_book_6h` audiobook label lands at `round(50000 × 1.04 / 150) = 347 min`, within the
±15% guard band of the accepted real ~368 min (and of the current 360-min label). Rationale: the
label is a deterministic, defensible floor-band estimate, not a render measurement. See §4.5 on why
render_inflation is deliberately excluded.

---

## 4. Derivation rules

### 4.1 `word_target` (per format)

```
word_target(fmt) =
    if fill_regime == "cap":      cap_word_target if declared else word_range[max]
    if fill_regime == "floor":    round(word_range[min] * 1.04)
    if fill_regime == "midpoint": round((word_range[min] + word_range[max]) / 2)
```

`cap_word_target` is an OPTIONAL per-format override (used by `standard_book` — see §5) for cases
where the real production cap differs from `word_range[max]`.

### 4.2 Advertised minutes (the derived pair)

```
audiobook_minutes(fmt) = round(word_target(fmt) / tts_wpm)        # tts_wpm = 150
ebook_minutes(fmt)     = round(word_target(fmt) / ebook_wpm)      # ebook_wpm = 230
```

Both are stored on each format (new fields `audiobook_minutes`, `ebook_minutes`). Listings advertise
the field matching the edition: audiobook listing → `audiobook_minutes`; ebook listing →
`ebook_minutes`.

`tts_wpm` is **read from the single constant** (§4.3); it is NOT re-declared in the registry.
`ebook_wpm` (230) is declared once alongside it (the scorecard config is the natural home — see
§4.3).

### 4.3 Single-sourced WPM (mirrors AUTO-PLAN-SSOT-01's "one canonical home")

The derivation function MUST read `tts_wpm` from `config/duration_scorecard.yaml`
(`duration_adherence_scorecard.tts_wpm`), the same constant the read-only adherence scorecard
already uses. It MUST NOT hard-code 150 and MUST NOT re-declare it in `format_registry.yaml`.

`ebook_wpm: 230` is added once to the same scorecard config block (it does not exist on main today;
the audit used 230 as the conventional reading rate). The derivation and any future ebook-adherence
measurement both read it from there.

Result: the advertised label and the adherence measurement consume the *same* WPM constants, so they
can never disagree (closes `RECOMMENDATIONS.md` item C).

### 4.4 Worked examples (against current registry word_ranges on main)

| format | fill_regime | word_target | audiobook_minutes | ebook_minutes | current label | Δ vs old |
|---|---|---|---|---|---|---|
| standard_book | cap | 22,000 (reconciled, §5) | 147 | 96 | 55 | label was −63% |
| micro_book_15 | midpoint | 3,500 | 23 | 15 | 15 | label was −35% |
| micro_book_20 | midpoint | 4,250 | 28 | 18 | 20 | label was −29% |
| short_book_30 | midpoint | 6,000 | 40 | 26 | 30 | label was −25% |
| extended_book_2h | midpoint | 21,000 | 140 | 91 | 120 | label was −14% |
| deep_book_4h | midpoint | 30,000 | 200 | 130 | 240 | label was +20% |
| deep_book_6h | floor | 52,000 | 347 | 226 | 360 | label was +4% |
| compact_book_5ch_15min | midpoint | 3,750 | 25 | 16 | 15 | label was −40% |
| compact_book_5ch_20min | midpoint | 4,750 | 32 | 21 | 20 | label was −38% |
| compact_book_8ch_30min | midpoint | 6,500 | 43 | 28 | 30 | label was −30% |
| one_hour_book | midpoint | 9,000 | 60 | 39 | (new tier) | NEW (OPD-20260613-001) |

(`word_target` uses the registry word_range on `origin/main`; e.g. extended_book_2h `[17000,25000]`
→ midpoint 21,000. `standard_book` uses the reconciled `cap_word_target` of 22,000 from §5.)

### 4.5 `realistic_words` excludes render_inflation (the label stays deterministic)

The audit measured `render_inflation = 1.073` from a **single** gold render
(`21,454 / 20,000`) and flagged it as a single anchor extrapolated across all formats. This spec
defines the advertised label on `word_target` **without** render_inflation — i.e.
`realistic_words = word_target`. Rationale:

- The label must be deterministic and reproducible from config alone (no dependency on a render).
- render_inflation is a single-format anchor; applying it to all 10 formats is unproven (the audit's
  own caveat E recommends a per-format dry-run pass to confirm).
- For the `cap` regime, render overshoot is absorbed as **cap headroom** (the §5 cap raise), not
  folded into the advertised minutes.

If a future per-format render audit (audit caveat E) confirms inflation, a follow-up may adjust the
`cap` regime's `cap_word_target` upward — but the formula stays `word_target / wpm`.

---

## 5. `standard_book` cap reconciliation (the one operator-facing number)

This is the single most consequential change and the only operator-reversible decision. It is logged
as an OPD (`artifacts/coordination/operator_decisions_log.tsv`) and called out in the cap entry.

**Facts on `origin/main`:**
- Registry `standard_book.word_range` = `[9000, 18000]` (ceiling raised 13000→18000 per
  `bestseller-chord-audit-2026-05-17 Axis 4`, so 12-chapter arcs don't truncate).
- Gold depth-fill targets **20,000** (QA budget.json), render hits **~21,454** (~21.5k).
- 94% of gold books exceed the registry word-range max → trip the word-range gate.

**Two coupled moves:**

1. **Derive the advertised label from the REAL gold render**, not the old 55-min guess. The real
   audiobook is ~143 min at the ~21.5k render. Using the reconciled `cap_word_target` of 22,000
   (next clean step above the ~21.5k render, giving small headroom), the derived
   `audiobook_minutes = round(22000 / 150) = 147 min`, `ebook_minutes = round(22000 / 230) = 96 min`.
   (The audit's headline ~143 min ≈ the 21.5k render at 150 WPM; 147 min is the same number rounded
   off the 22k reconciled cap. Either is honest; the spec advertises the cap-derived 147 so the
   label and the gate ceiling agree.)

2. **Raise the registry word-range ceiling 18,000 → 22,000** so the systematic ~21.5k render stops
   tripping the word-range gate. Set `cap_word_target: 22000` (so `word_target` = 22,000 explicitly,
   independent of any future word_range edits). This replaces the historical "raise the cap to mask
   the overshoot, label never moves" anti-pattern with "raise the cap AND re-derive the label in the
   same change" — exactly what the §6 guard enforces going forward.

**Default chosen** per `RECOMMENDATIONS.md:32` ("raise cap 20k→**22k** … the label is what's
broken"). The 20k→22k in the recommendation is relative to the depth-fill target; against the
**registry ceiling on main** the move is **18k→22k**. Recorded explicitly as an OPD,
`in_envelope=yes`, reversible, **flagged for operator** because it changes a customer-facing
advertised number (55 min → ~147 min).

---

## 6. CI guard contract — word_range / duration co-change (v1 = path-level BLOCK)

Adds one check, `check_duration_derivation(files)`, registered in the `pr_governance_review.py`
`main()` results list (alongside `check_mass_deletion`, `check_pr_size`, …; the list at ~lines
404–411 on `origin/main`).

### 6.1 Why path-level (not value-level) in v1

`pr_governance_review.py` `get_changed_files()` returns `[{status, path}]` — **changed file PATHS
only, no diff content / no field values** (confirmed: `_parse_gh_name_status`,
`git diff --name-status`). The guard therefore cannot read whether `word_range` numerically changed.
v1 is a **path-level co-change** rule: if the registry file is touched, the derivation config and
the spec must be touched in the same PR. A value-level guard (parse the YAML diff, recompute
minutes) is a **v2** enhancement noted in §6.4, requiring the script to read file contents at two
refs.

### 6.2 The v1 rule

```
TRIGGER: config/format_selection/format_registry.yaml is in the changed-paths set (status A or M).

REQUIRE (all must also be in the changed-paths set), else BLOCK:
  - the duration-derivation artifact that carries fill_regime + audiobook_minutes/ebook_minutes
    (i.e. the registry edit must travel with the derived-fields update — in v1 these live in the
    same format_registry.yaml file, so this clause is satisfied intra-file; the guard's job is the
    NEXT clause), AND
  - docs/DURATION_DERIVATION_SPEC.md  (this spec — forces the author to re-read the derivation
    contract when changing word_range), OR an explicit override token.

OVERRIDE: a PR body / commit-trailer token `DURATION-DERIVATION-OK: <reason>` downgrades BLOCK→WARN
  (for registry edits that provably don't touch word_range/fill_regime/duration — e.g. adding a
  compatible_structural_formats entry). The token requires a human-written reason.

RESULT shape (matches existing checks):
  { "check": "duration_derivation",
    "status": "BLOCKED" | "WARN" | "PASS",
    "message": "...",
    "details": {...} }
```

### 6.3 The ±15% tolerance band (guard's acceptance band — NOT the scorecard's 10%)

When the guard graduates to value-level (v2) it accepts a derived label within **±15%** of the real
target. v1 records this band in the spec and in the guard's docstring as the contract; it does not
yet compute it. **±15% is deliberately wider than `duration_scorecard.yaml`'s
`duration_tolerance_pct: 10`** — the scorecard's 10% stays for *measurement* of renders; the
derivation guard's 15% is for *label acceptance*. The 15% band keeps the two already-accepted deep
formats green:

- `deep_book_4h` real −11% (within ±15% → accepted, no relabel needed)
- `deep_book_6h` real +2% (within ±15% → accepted)

Using the scorecard's 10% would incorrectly flag `deep_book_4h` (−11%). Hence two distinct bands,
each single-purpose. (Per audit §6 the band used to triage was ≤±15% fine / 15–25% note / >25% act;
the guard adopts the ≤±15% "fine" boundary as its pass band.)

### 6.4 v2 (noted, not built here)

Value-level: read `format_registry.yaml` at `origin/main` and at `HEAD`, diff `word_range` /
`fill_regime` / `cap_word_target` per format, recompute `audiobook_minutes`/`ebook_minutes`, and
BLOCK if the stored label is outside ±15% of the recomputed value. Requires the guard to read file
*contents* at two refs (the script already shells `git`; this is additive). Tracked as a follow-up
under the CI-guard workstream, not in v1 scope.

---

## 7. Scope: en-US only; CJK deferred

The derivation is **English word-count math** and MUST early-skip non-en-US:

```
if locale not in {"en-US", "en"}:  # derivation does not apply
    return  # CJK/other handled by a separate char-based audit (deferred)
```

CJK locales (`ja-JP`, `zh-TW`, `zh-CN`, `ko-KR`) use **character counts** and different narration
rates (Mandarin ~250–300 chars/min; Japanese differs). Applying 150 WPM to CJK is wrong. A separate
char-based duration audit + a CJK derivation addendum is required before any CJK duration claim
ships (`DURATION_CORRECTNESS_REPORT.md` caveat "CJK not covered"; `RECOMMENDATIONS.md` item D). That
audit is **out of scope for this spec** and is flagged as a deferred follow-up (not a child ws of
this spec).

---

## 8. Atom-native modular formats (Group A — duration contracts)

Ten atom-native runtime formats were backfilled under `AUTO-PLAN-SSOT-01-AMENDMENT` Group A
(`chapter_count_default` only, 2026-05-06). **Duration contracts landed 2026-07-07**
(`ws_stub_format_duration_backfill`): each carries `word_range`, `fill_regime: midpoint`,
and derived `audiobook_minutes` / `ebook_minutes` from aggregate word bands in
`docs/ATOM_NATIVE_MODULAR_FORMATS.md`:

`five_min_practice, pocket_guide, ten_things_to_do, symptom_to_action_atlas,
daily_text_audio_companion, crisis_cards, weekly_challenge_pack, faq_audiobook,
myth_vs_mechanism, protocol_library`.

Rules:

1. **The derivation SKIPs any format without a `word_range`** (no `word_range` ⇒ no `word_target`
   ⇒ no derived minutes). No crash, no zero-minute label.
2. **The §6 guard SKIPs formats with no word_range changes** (nothing to co-derive).
3. **Listing / advertising gate (enforced):** `scripts/ci/check_format_duration_contracts.py`
   BLOCKs when a runtime format carries `audiobook_minutes`, `ebook_minutes`, or `duration_minutes`
   without a `word_range` + `fill_regime` that matches the derived values. Use
   `phoenix_v4.ops.duration_derivation.can_advertise_duration()` in listing builders.
   A format without an honest contract **must not** advertise a duration on any storefront surface.

---

## 9. Migration: deprecate `duration_minutes` transitionally

`duration_minutes` is NOT deleted in the first Phase-2 PR (back-compat for current readers).

**Transitional state (Phase-2 config PR):**
- Add `fill_regime`, `audiobook_minutes`, `ebook_minutes` (and `cap_word_target` where used) to each
  fully-specced format.
- Keep `duration_minutes` with a deprecation comment:
  `# DEPRECATED — superseded by audiobook_minutes/ebook_minutes (DURATION-DERIVATION-01). Do not
  hand-edit; readers migrate per follow-up.`
- The derived `audiobook_minutes` SHOULD equal the value a corrected `duration_minutes` would carry,
  so existing readers that still read `duration_minutes` get the *old* (wrong) number until they
  migrate — therefore the same Phase-2 PR SHOULD overwrite `duration_minutes` with the derived
  `audiobook_minutes` value (so even un-migrated readers advertise the honest number), while marking
  it deprecated.

**Reader migration (follow-up, separate ws — NOT a child of this spec):**
- `phoenix_v4/ops/duration_adherence_scorecard.py` and any catalog/listing builder that reads
  `duration_minutes` migrate to read `audiobook_minutes` (audiobook listings) or `ebook_minutes`
  (ebook listings).
- Once all readers migrate, a final PR removes `duration_minutes`. That removal PR is itself subject
  to the §6 guard.

---

## 10. Phase-2 child workstreams (landed 2026-06-12+)

Both original Phase-2 builds are **complete on main**:

1. **Duration-derivation config build** (`ws_duration_derivation_config_build_20260612`) —
   `fill_regime`, `audiobook_minutes`/`ebook_minutes`, `cap_word_target` on ladder formats;
   `phoenix_v4/ops/duration_derivation.py`; `tests/test_duration_derivation.py`.

2. **CI-guard build** (`ws_duration_derivation_ci_guard_20260612`) —
   `check_duration_derivation()` in `scripts/ci/pr_governance_review.py`.

**Follow-up landed 2026-07-07:** `ws_stub_format_duration_backfill` — Group A atom-native
formats backfilled; `scripts/ci/check_format_duration_contracts.py` enforces §8 advertising gate.

**Still open (not child ws of original spec):** reader migration off `duration_minutes`; CJK
char-based audit per `docs/DURATION_DERIVATION_SPEC_CJK_ADDENDUM.md`; v2 value-level CI guard.

---

## 11. Anchor index (every claim above is sourced on `origin/main`)

- `config/format_selection/format_registry.yaml` — `runtime_formats` (hand-set `duration_minutes`;
  `standard_book.word_range [9000,18000]`; `deep_book_6h` "~52K final" comment; 10 stub formats with
  only `chapter_count_default`).
- `config/duration_scorecard.yaml` — `tts_wpm: 150`, `duration_tolerance_pct: 10` (measurement-only;
  no `ebook_wpm` today).
- `phoenix_v4/ops/duration_adherence_scorecard.py` — `estimated_min = actual_words / wpm` (~L293,
  L455–456); read-only.
- `phoenix_v4/planning/beatmap_compile.py:651` — midpoint ±10% validator.
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` §413 — "TTS pace (flat, 150 WPM)".
- `scripts/ci/pr_governance_review.py` — `get_changed_files()` returns `[{status, path}]`;
  `main()` results list at ~L404–411; check return shape `{check, status, message, details}`.
- `artifacts/qa/duration_correctness_audit_20260611/` — `DURATION_CORRECTNESS_REPORT.md`,
  `RECOMMENDATIONS.md` (cap 20k→22k default at :32), `projection_results.json` (per-format `regime`,
  `word_range`, gaps; standard_book listen 143.4 / +160.8%, deep_book_6h +2.2%, deep_book_4h −10.8%).
- `docs/PEARL_ARCHITECT_STATE.md` — `AUTO-PLAN-SSOT-01` (registry-as-SSOT pattern, L438),
  `AUTO-PLAN-SSOT-01-AMENDMENT` Group A (10 stub formats, L523).
