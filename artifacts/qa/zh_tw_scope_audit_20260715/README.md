# zh-TW Scope Audit — 2026-07-15

**Agent:** Pearl_Localization · **Lane:** 02 (`20260715_finish_open_ops_bundle`)
**Measured at:** `b748f706327f500d414f60a1b967c70783b94538` (== `origin/main` at audit time)
**Type:** REPORT-ONLY. No file was translated, edited, or repaired by this audit.

## Headline: the pack's "99" is stale; the "36" is exact

| Question | Pack claim | **Measured** | Verdict |
|---|---|---|---|
| Production zh-TW files needing Tier-1 Claude | 99 | **5** | **STALE** — see delta |
| Non-production deferred | 36 | **36** | **VERIFIED EXACT** |
| Landed zh-TW files containing Simplified | — | **869** (862 after #5682) | New finding |

### Why 99 → 5 (do not reconcile back to 99)

PR **#5693** ("translate(zh-TW): close remaining atom coverage gaps (production scope)")
**merged 2026-07-15T11:04:54Z**, and its merge commit `b748f706` **is** the current
`origin/main`. It translated **94** of the 99 via Tier-1 Claude. `99` was the *pre-#5693*
baseline (`3755 − 3656 = 99`). The prompt pack snapshot (`origin/main` = `8956e222`)
predates that merge.

**5 remain — and none are translatable.** All 5 are blocked on a **defective English
source**, not on translation capacity:

```
atoms/nyc_executives/burnout/overwhelm/CANONICAL.txt
atoms/nyc_executives/burnout/watcher/CANONICAL.txt
atoms/nyc_executives/imposter_syndrome/comparison/CANONICAL.txt
atoms/nyc_executives/imposter_syndrome/shame/CANONICAL.txt
atoms/nyc_executives/overthinking/spiral/CANONICAL.txt
```

Verified defect: the prose body of each early variant is literally the *next header
string* (e.g. body of `RECOGNITION v01` == `"RECOGNITION v02"`); headers skip v01→v03→v05
and duplicate IDs. **Do NOT dispatch a translator at these** — they need Pearl_Writer to
author ~50 English variants first, then a 5-file translation follow-up.

> **Lane 03 consequence:** the zh-TW production translation lane has **no translatable
> work left**. It is Pearl_Writer-blocked, not Pearl_Localization-blocked.

## Production-scope rule (repo-grounded, not invented)

**Authority:** `scripts/ci/report_translation_coverage.py` lines 34–36 (docstring cites
`PEARL_PRIME_100_PERCENT_DEV_PLAN §5`).

A file is **PRODUCTION** iff it is `atoms/{persona}/{topic}/{TYPE}/CANONICAL.txt` with no
`locales/` component and `TYPE` in:

- `BESTSELLER_SLOTS` = PIVOT, TAKEAWAY, THREAD, PERMISSION, STORY
- `ENGINE_DIRS` = comparison, false_alarm, grief, overwhelm, shame, spiral, watcher

Everything else (COMPRESSION, SCENE, TEACHER_DOCTRINE, TRANSITION, QUOTE, ENGINE, …) is
**NON_PRODUCTION**. Totals: 5,213 English sources = 3,755 production + 1,458 non-production.
This rule reproduces the repo tool's own `3750/3755 (99.9%) remaining=5` exactly.

The 36 deferred break down as: COMPRESSION 28, SCENE 2, TEACHER_DOCTRINE 2, QUOTE 1,
TRANSITION 1, ENGINE 1, `ahjan` 1 — consistent with the operator scope ruling.

## Simplified contamination: 869 landed files

Detector **reused** (not greenfielded) from the prior zh-TW lane's `zhtw_qa.py`. A char is
Simplified-only **iff BOTH**: OpenCC `s2t` changes it **AND** Big5 cannot encode it.

> Naive s2t alone is **wrong** — it false-flags 台/吃/游/群/床, which are correct, ubiquitous
> Taiwan usage. Big5 (Taiwan's charset) separates the cases cleanly.

**Calibrated before trusting** (per the standing instruction), on real landed files:

| Case | File | Result |
|---|---|---|
| Single-char leak | `educators/depression/STORY` | `眼前的学生` — Traditional prose, one Simplified `学` → **true positive** |
| Whole-passage | `educators/anxiety/spiral` | `说她拥有实质性的信誉…这个` → **true positive** |
| Clean control | `educators/burnout/STORY` | `學生 / 從外表 / 寫下` → **true negative** |

### Confidence tiers (5,172 landed zh-TW files)

| Tier | Count | Meaning |
|---|---|---|
| `HIGH_CONFIDENCE_SIMPLIFIED` | **869** | s2t-changed AND non-Big5 → act on these |
| `REVIEW_VARIANT_ONLY` | 1,651 | s2t-changed but Big5-OK → **legitimate Taiwan usage, do NOT "fix"** |
| `CLEAN` | 2,652 | no signal |

### Severity of the 869

| Severity | Count | Shape |
|---|---|---|
| `SPOT_LEAK` (1–2 chars) | 506 | Traditional prose, isolated Simplified char |
| `PARTIAL` (3–9) | 321 | mixed |
| `WHOLE_FILE` (≥10) | 42 | translated in Simplified outright |

Known false negative: rare Simplified forms sitting inside Big5 (e.g. 极). Tuned for
precision — a false positive would reject correct prose.

## PR #5682 ownership — DO NOT TOUCH

`OPEN` / `CLEAN` / non-draft · 52 files (+239 −1570) · head `agent/atom-health-small-fixes-20260714`.
Full list: `pr5682_owned_files.txt` / `pr5682_owned_files.json`.

- 52 files total; **20** are zh-TW paths (the title's "7" is the SCRIPT_MISMATCH *class*, not the path count).
- **7** zh-TW files are genuinely script-fixed by the PR — measured against its head, this
  matches the title's "7 zh-TW files" exactly.
- **6** zh-TW files it touches **remain Simplified after merge** (placeholder-class fixes,
  not script fixes): `gen_x_sandwich/financial_anxiety/INTEGRATION` (财),
  `gen_z_professionals/burnout/INTEGRATION` (双变录记),
  `gen_z_professionals/financial_anxiety/INTEGRATION` (个双这),
  `healthcare_rns/burnout/INTEGRATION` (来续), `healthcare_rns/financial_anxiety/INTEGRATION` (个这),
  `working_parents/burnout/INTEGRATION` (个双).
- Net contamination after #5682 merges: **869 − 7 = 862**.

**Collision rule for downstream lanes:** every path in `pr5682_owned_files.txt` is
`OWNED_BY_5682_DO_NOT_TOUCH` while #5682 is open — including those 6 still-contaminated
files. Re-audit them *after* #5682 merges.

## Files

| File | Contents |
|---|---|
| `zh_tw_scope_matrix.tsv` | 5,213 rows — every English source × scope × status × contamination × ownership |
| `zh_tw_scope_summary.json` | machine-readable counts + pack reconciliation |
| `pr5682_owned_files.txt` / `.json` | do-not-touch list |

`status` values: `NEEDS_TIER1_CLAUDE_TRANSLATION` (5) · `DEFERRED_NON_PRODUCTION` (36) ·
`LANDED_SIMPLIFIED_CONTAMINATED` (869) · `LANDED_CLEAN` (4,303).

### Derived columns (kept out of the TSV on purpose)

The repo's `scan` gate caps in-repo blobs at 1 MiB (Layer 2 policy: bulk artifacts belong in
R2). Three columns were dropped because they are **mechanically derivable** from
`english_source`, which brought the file to 586 KB with **no rows and no signal lost**:

```python
zh_tw_target = english_source.replace("/CANONICAL.txt", "/locales/zh-TW/CANONICAL.txt")
persona      = english_source.split("/")[1]
topic        = english_source.split("/")[2]
```

Do not "restore" them — that reintroduces the gate failure for zero information.

## Reproduce

```bash
GIT_LFS_SKIP_SMUDGE=1 git worktree add /tmp/wt-zhtw-scope -b <br> origin/main
cd /tmp/wt-zhtw-scope
PYTHONPATH=. python3 scripts/ci/report_translation_coverage.py --locales zh-TW
gh api repos/Ahjan108/phoenix_omega_v4.8/pulls/5682/files --paginate --jq '.[].filename'
```

**Gotcha:** `report_translation_coverage.py` reads the **working tree**. Run it on a dirty
branch and it prints a false baseline. This audit ran from a clean worktree at `origin/main`.

## Standing rules reaffirmed

- **zh-TW is Tier-1 Claude only.** Never route Qwen at zh-TW — it emits Simplified.
- Do not repair contamination inside a translation lane; that is lane 04, report-only.
- The Big5 detector is still **not a CI gate**. Per the "memory is recall, not enforcement"
  doctrine, this audit is recall — contamination can re-enter `main` until it is enforced.
  See NEXT_ACTION in the handoff.
