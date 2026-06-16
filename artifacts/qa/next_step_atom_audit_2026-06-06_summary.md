# Pearl Prime Storefront V1 — Atom Off-Catalog Reference Audit

**Workstream:** `ws_pearl_writer_next_step_atom_audit_20260603` (stage 1)
**Date:** 2026-06-06
**Authority:** `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` §15.3 + §AMENDMENT-2026-06-04.7
**Parent PRs (merged on origin/main):** PR #1433 (V1 spec) SHA `69e9855f72471603f320f1b96ae72e899a3e8778`; PR #1446 (AMENDMENT-2026-06-04) SHA `eb9c4ab841e49f0fa5e72b4497505f1325837c7d`
**Detector:** `scripts/ci/check_atoms_external_book_references.py`
**Raw TSV:** `artifacts/qa/next_step_atom_audit_2026-06-06.tsv`
**Mode:** AUDIT ONLY — no atoms rewritten in this workstream.

---

## §1 — Headline result

The stage-1 audit (en-US `anxiety` + `overthinking` × all personas + teacher-bank `body:` content) ran cleanly:

| Metric | Value |
|---|---|
| Atom CANONICAL.txt files scanned (en-US) | **112** |
| Atom variants scanned (within CANONICAL.txt) | **2,387** |
| Teacher-bank approved-atom YAMLs scanned | **2,418** |
| Total atom payloads scanned | **4,805** |
| Total flagged | **2** |
| `high_external_author` | 0 |
| `high_external_title` | 1 |
| `high_external_org` | 0 |
| `high_url_in_atom` | 0 |
| `low_vague_recommendation` | 1 |

**Interpretation.** The en-US `anxiety` + `overthinking` atom corpus is **substantially cleaner** than the §15.1 problem statement assumed. The 2,387 atom-variants and 2,418 teacher-bank atoms yielded only two flagged passages — and both are arguably edge-case borderline matches, not the "go read Bessel van der Kolk's *The Body Keeps the Score*" archetype that motivated the audit. The high-confidence detector is **NOT** finding flagrant external-book CTAs in this slice. This is a strong signal that the §15 cleanup ROI is concentrated elsewhere (locale variants under `atoms/<persona>/<topic>/<atom>/locales/<locale>/`, teacher-mode candidate atoms, or other topics) rather than in the en-US root canonical atoms.

---

## §2 — Per-match detail

Both flagged passages with full context.

### 2.1 `low_vague_recommendation` — gen_z_professionals / anxiety / REFLECTION

**File:** `atoms/gen_z_professionals/anxiety/REFLECTION/CANONICAL.txt`
**Line:** 353
**Match:** `Maté` (Gabor Maté, author surname, no book-noun in ±10 word window)
**Passage:**

> The body answers all three audiences at once. The cost is paid in micro-muscle tension across the face that lasts thirty minutes after the call ends, in a particular kind of fatigue that did not exist as a category in 2019. The conditions are new. The biology is the same. **Maté would name it cleanly: a sane response to a setup that nobody designed on purpose and everybody now lives inside.**

**Assessment.** This is **borderline**. The atom does not direct the reader to read Maté's books — it invokes his framing as rhetorical authority. Whether this constitutes a "go out of ecosystem" CTA per §15.1 is a Pearl_Editor + operator judgement. The conservative rewrite would substitute the framing with content from a Pearl Prime stillness_press SKU on systemic anxiety.

**Suggested action (audit-only — not applied):** `human_review`.

### 2.2 `high_external_title` — teacher_banks / ahjan / EXERCISE_043_mined

**File:** `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/EXERCISE/ahjan_EXERCISE_043_mined.yaml`
**Line:** 6
**Match:** `Letting Go` (matched the David R. Hawkins title literal)
**Passage:**

> Letting Go of Societal Conditioning — There is great importance in examining societal conditioning, which often leads to stress and inner conflict.

**Assessment.** **False positive on the title-literal match.** "Letting Go of Societal Conditioning" is a section heading in the mined source, not a reference to the Hawkins book. However, the YAML `source_refs` field reveals the body was scraped from `BD Blog - Title: The Transformative Power of Gratitude` — this content originated outside the Pearl Prime authoring system and was promoted into runtime-visible atoms via `synthesis_method: kb_mine_v1`. The teacher_banks/ahjan corpus may warrant a follow-up "mined atoms in approved" audit even though this specific match is a false positive on the book-title pattern.

**Suggested action (audit-only — not applied):** `human_review`; consider broader audit of `synthesis_method: kb_mine_v1` atoms in approved_atoms/.

---

## §3 — Persona × topic heat map (variants scanned vs hits)

| Persona | anxiety variants | overthinking variants | flagged |
|---|---:|---:|---:|
| corporate_managers | 132 | 90 | 0 |
| educators | 110 | 12 | 0 |
| entrepreneurs | 95 | 88 | 0 |
| first_responders | 98 | 98 | 0 |
| gen_alpha_students | 110 | 88 | 0 |
| gen_x_sandwich | 115 | 88 | 0 |
| gen_z_professionals | 182 | 90 | **1** |
| gen_z_student | 23 | 23 | 0 |
| healthcare_rns | 112 | 88 | 0 |
| midlife_women | 12 | 12 | 0 |
| millennial_women_professionals | 115 | 88 | 0 |
| nyc_executives | 125 | 12 | 0 |
| tech_finance_burnout | 115 | 90 | 0 |
| working_parents | 88 | 88 | 0 |
| **Totals** | **1,432** | **955** | **1 (atoms)** |

Teacher-bank totals: **2,418 YAMLs / 1 hit (false positive)**.

**Coverage gaps noted (not in scope for stage 1).** Several personas have low variant counts for `overthinking` (educators=12, midlife_women=12, nyc_executives=12). These look like partial topic coverage rather than under-detection — a separate Pearl_Editor concern, not Pearl_Writer's.

---

## §4 — Top external authors / titles / orgs by frequency

| Rank | Reference | Type | Frequency | Confidence |
|---|---|---|---:|---|
| 1 | `Maté` (Gabor Maté) | author surname | 1 | low_vague (no book-noun proximity) |
| 2 | `Letting Go` (David R. Hawkins) | title literal | 1 | high (false positive on context) |
| 3-20 | — | — | — | — |

Top 5 truncated to actual hit count: only 2 distinct references found. The lower-bound registry of 30+ external authors (van der Kolk, Brach, Tolle, Tara Brach, Plum Village, Insight Timer, Calm, Headspace, MBSR, etc.) produced **zero** high-confidence en-US matches in the staged scope.

---

## §5 — Sample passages per match_type (3 each — fewer where corpus dry)

### 5.1 `high_external_author` (0 samples — none found)

Empty. The corpus does not contain explicit external-author book recommendations in the staged scope. The pattern registry remains armed for stage 2.

### 5.2 `high_external_title` (1 sample only)

1. **`Letting Go`** — `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/EXERCISE/ahjan_EXERCISE_043_mined.yaml:6` — false-positive context; see §2.2.

### 5.3 `high_external_org` (0 samples)

The detector with the AMBIGUOUS_ORGS proximity-gating revision flagged zero ambiguous-noun hits (Calm, Headspace) once brand-context proximity (`app|subscribe|download|founder`) was required. The pre-tightening v1 detector had 3 hits but all 3 were false positives (e.g., "Steady. There is a difference. Calm implies the absence of anxiety. Calm comes from a nervous system...").

### 5.4 `high_url_in_atom` (0 samples)

The corpus is genuinely URL-free — atoms remain content-only per §15.7 invariant.

### 5.5 `low_vague_recommendation` (1 sample)

1. **`Maté`** — `atoms/gen_z_professionals/anxiety/REFLECTION/CANONICAL.txt:353` — see §2.1.

---

## §6 — Detector design notes (what passed, what's tuned)

### 6.1 Patterns implemented per §15.3

- ✅ External author surname registry: 30+ authors including all spec-required surnames (van der Kolk, Brach, Tolle, Hanh, Goleman, Kabat-Zinn, Brown, Maté, Pinker, Levine, Porges, Doidge, Frankl, Williamson, Chödrön, Dalai, Thich) — tiered into multi-word (always high), distinctive-single-token (high if book-noun proximity; low if absent), common-English-token (high only with book-noun proximity, else skipped).
- ✅ Italic-quoted title pattern (`*Title Words* by Author`).
- ✅ Double-quoted title pattern.
- ✅ Unambiguous title literals (26 well-known book titles, all distinctive multi-word).
- ✅ Ambiguous title literals (Quiet, Mindset, Calm, Headspace, Awakening) — flagged only with italic delimiters OR " by <CapitalizedName>" OR ±10-word book-noun proximity.
- ✅ Unambiguous org registry (Insight Timer, Plum Village, Spirit Rock, MBSR, MBCT, UCLA Mindful, Waking Up app, Sam Harris, Shambhala, Goenka, Vipassana, Dharma Seed, Insight Meditation Society, Tricycle, Lion's Roar, Sounds True, TED Talk, YouTube channel, 10% Happier, Ten Percent Happier).
- ✅ Ambiguous org registry (Calm, Headspace, Awakening) — flagged only with brand-context proximity (app/subscribe/download/founder/CEO/company/brand).
- ✅ External podcast pointer ("Podcast by/called/titled <CapName>").
- ✅ URL pattern (`https?://...`).
- ✅ Vague-recommendation registry (great book, wonderful teacher, my teacher said, subscribe to, check out, I recommend, highly recommend, you should read, go read, great resource).

### 6.2 Per-atom variant handling

Atom CANONICAL.txt files contain numbered variants (`## INTEGRATION v01` ... `v25`). The detector iterates the entire file once and reports file-relative line numbers, which give human reviewers unambiguous anchors. Variant counts are extracted via `^##\s+\w+\s+v\d+\s*$` for the totals row.

### 6.3 Teacher YAML body extraction

Teacher-bank approved atoms are YAML, not text. The v1 detector naively scanned the whole YAML — including metadata fields like `teacher_id` — which produced false-positive book-noun proximity hits. The shipped detector extracts only the `body:` field content and reports line numbers offset from the file start.

### 6.4 False positive triage during tuning

The pre-tightened detector v1 produced 69 hits, of which ~95% were false positives on common-English-as-book-title (Quiet, Mindset, Calm). Tuning steps:

1. Split `EXTERNAL_TITLES` into `UNAMBIGUOUS_TITLES` (always flagged) and `AMBIGUOUS_TITLES` (flagged with proximity context).
2. Made `Quiet`/`Mindset`/`Calm`/`Headspace`/`Awakening` require italic delimiters, "by" clause, OR book-noun proximity.
3. Added brand-context gating to `Calm`/`Headspace`/`Awakening` org matches (requires `app|subscribe|download|founder` co-occurrence).
4. Tiered author surnames: multi-word always-high, distinctive-single low-vague if no book-noun, common-English-token skip without context.
5. Restricted teacher-YAML scanning to the `body:` field only.

Post-tuning: 2 hits, both arguably borderline. Precision ≈ 50% (1 real low-vague Maté reference; 1 contextual FP on "Letting Go").

---

## §7 — Recommended next-pass scope

Per spec §AMENDMENT-2026-06-04.7, the audit cascade is:

1. **Pass 1 — DONE THIS WS:** en-US `anxiety` + `overthinking` × all personas + teacher banks. **Result: 2 hits, 1 likely false positive.**
2. **Pass 2 — operator-review-gated:** en-US remaining topics × all personas + ja-JP `anxiety` + `overthinking` × all personas.
3. **Phase A gate:** en-US + ja-JP audit + rewrite complete before launch.

### 7.1 Operator decision required before stage 2

Given the **very low hit rate in stage 1**, the operator may want to consider whether the audit should:

**(a) Expand by locale first** — Spot checks during this audit revealed multiple high-confidence hits in `atoms/<persona>/<topic>/<atom>/locales/zh-TW/CANONICAL.txt`, `zh-CN/`, `ja-JP/` (e.g., "The Body Keeps the Score" literally appears in 4 separate zh-TW / zh-CN atom files). **Recommendation: stage 2 should prioritize the localized atoms (locales/{ja-JP,zh-TW,zh-CN,zh-HK,zh-SG,ko-KR}) BEFORE expanding to remaining en-US topics**, because that's where the §15.1 archetype actually lives.

**(b) Expand the topic axis first** — en-US `grief`, `burnout`, `shame`, `relationships`, `purpose`, etc. The teacher-bank `kb_mine_v1` mined atoms may have higher external-reference density across topics; the `ahjan_EXERCISE_043_mined` example is a hint.

**(c) Combine the AMENDMENT pass-2 plan as written** — en-US remaining topics + ja-JP anxiety + overthinking. Defaults from the AMENDMENT.

### 7.2 Pearl_Writer recommendation

**Prioritize (a) and (b) over (c).** Specifically:

- **Stage 2a (suggested):** `atoms/<persona>/<topic>/<atom>/locales/{ja-JP,zh-TW,zh-CN,zh-HK,zh-SG,ko-KR}/CANONICAL.txt` for `anxiety` + `overthinking` — to find the actual high-density external-reference content the audit was designed to surface.
- **Stage 2b (suggested):** `SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/` filtered by `synthesis_method: kb_mine_v1` — the mined-from-blog atoms are a higher-risk surface than the doctrine-grounded synthesized atoms.
- **Stage 2c (per AMENDMENT default):** en-US remaining topics × all personas.

These three sub-stages can run in parallel as separate ws if operator approves.

### 7.3 Rewrite ws gating

Per §15.6, the rewrite workstream (`ws_pearl_writer_next_step_atom_rewrite_<future-date>`) is gated on operator review of this report. **Given stage 1's tiny hit count, the rewrite ws may not be cost-justified for the stage-1 scope alone** — the 2 hits could be handled inline by Pearl_Editor as a sub-50-line PR rather than a dedicated workstream. The rewrite ws becomes more justified once stage 2a (localized variants) lands additional hits.

---

## §8 — CI integration

`scripts/ci/check_atoms_external_book_references.py` ships with a non-blocking warning workflow at `.github/workflows/atoms-external-ref-audit.yml`. The workflow:

- Triggers on PRs touching `atoms/**/*.txt` or `SOURCE_OF_TRUTH/teacher_banks/**/*.yaml`.
- Runs `--scope stage1` (or filters to changed files via `--paths`) and surfaces any net-new matches.
- Posts a comment on the PR with the delta vs main.
- **Does NOT block the PR.** Per §15.6, the audit workstream is informational only; the rewrite workstream will graduate this to a blocking check.

Rationale for new workflow file (vs adding step to `docs-ci.yml`): `docs-ci.yml` is scoped to `docs/**`, `specs/**`, onboarding registry, and a handful of governance scripts. Atoms aren't docs and shouldn't add a path-filter to the docs workflow. A dedicated atoms-audit workflow is also easier to graduate to blocking later without disturbing docs CI.

---

## §9 — Closeout

### What this ws produced
- `scripts/ci/check_atoms_external_book_references.py` — production detector (regex-based, no LLM, Tier policy compliant).
- `artifacts/qa/next_step_atom_audit_2026-06-06.tsv` — per-match TSV (header + 2 rows).
- `artifacts/qa/next_step_atom_audit_2026-06-06_summary.md` — this report.
- `.github/workflows/atoms-external-ref-audit.yml` — non-blocking CI warning workflow.

### What this ws did NOT do
- No atom files were modified. The rewrite is a separate, operator-gated workstream.
- No spec doc edits. Pearl_Architect owns those.
- No `artifacts/coordination/*.tsv` edits. Pearl_PM owns those.

### NEXT_ACTION
**Operator** reviews this summary → approves stage 2 expansion (recommendation: stage 2a localized + stage 2b mined-atoms-filtered + stage 2c per AMENDMENT default) → Pearl_PM authors the next workstream rows in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` → Pearl_Writer executes stage 2 with the same detector (now armed for non-en-US locales) → Pearl_Writer authors the rewrite ws gated on stage 2 results.

Per §AMENDMENT-2026-06-04.7 the en-US + ja-JP audit + rewrite cycle must both complete before Phase A launch. HARD CTA cutover semantics apply to atoms recommending external books.
