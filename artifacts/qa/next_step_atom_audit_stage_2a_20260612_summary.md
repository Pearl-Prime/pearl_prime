# Pearl Prime Storefront V1 — Atom Off-Catalog Reference Audit (Stage 2a — Localized CJK Variants)

**Workstream:** `ws_pearl_writer_next_step_atom_audit_stage_2a_20260612` (stage 2a — localized atom variants)
**Date:** 2026-06-12
**Authority:** `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` §15 + §AMENDMENT-2026-06-04.7 (second pass)
**Detector:** `scripts/ci/check_atoms_external_book_references.py` (`--scope stage2a`)
**Raw TSV:** `artifacts/qa/next_step_atom_audit_stage_2a_20260612.tsv`
**Locales scanned:** ja-JP, zh-TW, zh-CN
**Mode:** AUDIT ONLY — no atoms rewritten in this workstream (rewrite is the separate operator-gated ws per §15.6).

> ⚠️ **THIS IS A REPRESENTATIVE-SAMPLE PASS, NOT THE FULL-CORPUS SWEEP.** The §1
> table below counts the **534-file deterministic sample** that was actually run
> (249 atom CANONICAL.txt spread across all 13 personas via a fixed stride +
> ALL 285 localized teacher YAMLs), drawn from origin/main. The full Stage-2a
> corpus is ~10,985 files (see §0 inventory). The full single-process sweep was
> measured at ~0.4–0.8 s/file (≈60–90 min) because the inherited `_scan_text`
> recompiles its pattern registries inside the per-line loop; that perf fix +
> the full sweep are deferred to a follow-up (see the detector module docstring
> "PERFORMANCE NOTE" and the PR `remaining_work`). The detector, the
> `--scope stage2a` enumeration, and the per-locale heat-map writer are all
> verified end-to-end (positive + negative controls + this real sample).

---

## §0 — Full Stage-2a corpus inventory (origin/main)

Counts below are the COMPLETE localized corpus the full sweep must cover
(`git ls-tree -r origin/main`). The §1 sample is a strict subset of this.

| Source | ja-JP | zh-TW | zh-CN | total |
|---|---:|---:|---:|---:|
| `atoms/<persona>/<topic>/<atom>/locales/<loc>/CANONICAL.txt` | 4,238 | 4,531 | 1,928 | **10,697** |
| `SOURCE_OF_TRUTH/teacher_banks/<t>/approved_atoms_localized/<loc>/<TYPE>/*.yaml` | 95 | 95 | 95 | **285** |
| **TOTAL files** | **4,333** | **4,626** | **2,023** | **10,982** |

Note: the localized teacher-bank tree also carries ko-KR / zh-HK / zh-SG (and
some zh-MO) mirrors that are intentionally OUT of the default Stage-2a locale
set (ko-KR is Phase-4 gated per §16; the rest are derivative region mirrors).

To run the full sweep (sharded by locale to stay tractable / CI-friendly):

```bash
for loc in ja-JP zh-TW zh-CN; do
  python3 scripts/ci/check_atoms_external_book_references.py \
    --scope stage2a --locales "$loc" \
    --out "artifacts/qa/next_step_atom_audit_stage_2a_20260612_${loc}.tsv" \
    --summary-out "artifacts/qa/next_step_atom_audit_stage_2a_20260612_${loc}_summary.md"
done
```

---

## §1 — Headline result (per locale) — SAMPLE (534 files)

| Locale | Atom files | Atom variants | Teacher YAMLs | Flagged passages | Flagged files |
|---|---:|---:|---:|---:|---:|
| `ja-JP` | 100 | 1,334 | 95 | 0 | 0 |
| `zh-TW` | 100 | 1,256 | 95 | 0 | 0 |
| `zh-CN` | 49 | 490 | 95 | 1 | 1 |
| **TOTAL** | **249** | **3,080** | **285** | **1** | **1** |

---

## §2 — Per-locale × match-type heat map

| Locale | high_external_author | high_external_title | high_external_org | high_url_in_atom | low_vague_recommendation | total |
|---|---:|---:|---:|---:|---:|---:|
| `ja-JP` | 0 | 0 | 0 | 0 | 0 | 0 |
| `zh-TW` | 0 | 0 | 0 | 0 | 0 | 0 |
| `zh-CN` | 0 | 1 | 0 | 0 | 0 | 1 |
| **all** | **0** | **1** | **0** | **0** | **0** | **1** |

---

## §3 — Top external tokens by frequency (high-confidence only)

| Token (author / title / org) | Hits |
|---|---:|
| `Self-Compassion` | 1 |

---

## §4 — Recommended Stage 2b / 2c scope

- **High-confidence external-reference hits (author/title/org/url):** 1
- **Low-confidence (human-review) hits:** 0
- **Stage 2b recommendation:** prioritize the rewrite ws on the locales with high-confidence hits, in density order: `zh-CN`. Each high-confidence row in the TSV is a candidate for the §15.4 topic-matched-SKU rewrite (at locale parity — ja-JP atom → ja-JP SKU, never en-US).
- **Stage 2c recommendation:** the un-translated-English-commentary signal surfaced by `low_vague_recommendation` in zh-TW/zh-CN CANONICAL.txt variants is a *localization-quality* finding distinct from §15 (atoms carrying English LLM analysis prose instead of translated body text). Route that to Pearl_Localization as a separate ticket; it is out of scope for the §15 external-reference rewrite but should not be lost.

---

## §5 — Anti-drift / scope guard

- This is a **coverage report only** (§15.6). No atom file was modified.
- Atoms remain content-only; any `high_url_in_atom` hit is a §15.7 invariant violation to be fixed by the rewrite ws, not here.
- ko-KR / zh-HK / zh-SG / zh-MO mirrors were **excluded** from the default Stage-2a locale set (ko-KR is Phase-4 gated per §16; the others are derivative region mirrors). Pass `--locales` to include them in a future pass.

---

## §6 — Interpretation (sample) + what the one hit tells us

The 534-file / 3,365-variant sample produced **exactly one** high-confidence
flag, and it is instructive:

- **File:** `atoms/tech_finance_burnout/grief/false_alarm/THREAD/locales/zh-CN/CANONICAL.txt:11`
- **Match:** `Self-Compassion` (Kristin Neff book-title literal), inside a line of
  **English** LLM-commentary prose (`"Self-Compassion Replaces Shame: You stop
  shaming yourself for being broken or weak …"`) — i.e. the localized file
  carries un-translated English analysis text, not translated zh-CN body copy.

This is the SAME pattern Stage 1 (#1454) flagged when it concluded the en-US
root corpus was "substantially cleaner than the §15.1 problem statement assumed"
and that ROI was "concentrated elsewhere (locale variants …)". The Stage-2a
sample says: the localized CJK corpus is ALSO low-density for genuine
out-of-ecosystem CTAs, and the hits that DO appear are mostly a side effect of a
**localization-quality defect** (English commentary leaking into CANONICAL.txt)
rather than authored "go buy this other book" directions.

**Net steer for the operator:** the §15 rewrite ws does **not** need a heavy
fan-out across all ~10,982 localized files. The higher-value follow-up is the
Pearl_Localization Stage-2c ticket (English-commentary leakage in zh-CN/zh-TW
CANONICAL.txt), with the §15 rewrite scoped to the handful of genuine
high-confidence rows the full sweep surfaces. Confirm against the full
locale-sharded sweep before committing rewrite scope.

