# zh-TW Simplified Contamination — Report + Enforcement — 2026-07-15

**Agent:** Pearl_QA · **Lane:** 04 (`20260715_finish_open_ops_bundle`)
**Measured at:** `9e9b9e606791590337cd7d0f2fb425def2e6f760` (== `origin/main` at audit time)
**Type:** REPORT + CI GATE. **`REPAIRS_PERFORMED=none`** — no contaminated file was
edited, translated, or repaired by this lane.
**Foundation:** lane 02 (`artifacts/qa/zh_tw_scope_audit_20260715/`, PR #5694, `364b8640`).

## 1. Lane 02's 869 is INDEPENDENTLY CONFIRMED

Lane 02 measured 869 at `b748f706`. This lane re-derived the number from scratch at
current `origin/main` and got the same answer.

| Tier | Lane 02 (`b748f706`) | **This lane (`9e9b9e60`)** | Verdict |
|---|---|---|---|
| Files scanned | 5,172 | **5,172** | match |
| `HIGH_CONFIDENCE_SIMPLIFIED` | 869 | **869** | **CONFIRMED** |
| `REVIEW_VARIANT_ONLY` | 1,651 | **1,651** | match |
| `CLEAN` | 2,652 | **2,652** | match |

`origin/main` moved `b748f706 → 364b8640 → 9e9b9e60` during the lane. **Zero zh-TW atoms
changed** across those moves (38 files changed, 0 matching `locales/zh-TW/CANONICAL.txt`),
so the corpus is byte-identical and the count carries forward exactly:

```bash
git diff --name-only 364b8640..9e9b9e60 | grep -c 'locales/zh-TW/CANONICAL.txt'   # -> 0
```

### One real correction: the severity tiers are keyed on DISTINCT chars

Lane 02's README reports `SPOT_LEAK (1–2 chars) 506 / PARTIAL (3–9) 321 / WHOLE_FILE (≥10) 42`
without saying *which* count "chars" means. It is **distinct** Simplified characters, not
total occurrences. The distinction is not cosmetic — it moves 40 files across the
WHOLE_FILE line:

| Severity | **By distinct chars (canonical — reproduces lane 02)** | By total occurrences |
|---|---|---|
| `WHOLE_FILE` (≥10) | **42** | 82 |
| `PARTIAL` (3–9) | **321** | 342 |
| `SPOT_LEAK` (1–2) | **506** | 445 |

Both columns are carried in the TSV so the ambiguity cannot recur. **Distinct is
canonical**, matching the merged lane-02 foundation and the gate's baseline.

## 2. Detector — reused rule, first landed implementation

The rule is lane 02's, unchanged:

> A char is Simplified-only **iff BOTH**: OpenCC `s2t` changes it **AND** Big5 cannot
> encode it.

The Big5 leg is load-bearing: naive `s2t` alone false-flags 台/吃/游/群/床 across **1,651**
legitimate Taiwan-usage files.

**Honest provenance note:** lane 02 cites reusing `zhtw_qa.py` from a prior lane. That file
**does not exist on `origin/main`** and is not on disk — it was a scratch script that was
never landed:

```bash
git ls-tree -r --name-only origin/main | grep -c zhtw_qa   # -> 0
```

So what was reused is the **calibrated rule**, not a landed module. This lane freezes that
rule into repo code (`scripts/ci/zh_tw_simplified_charset.py`) — the first landed
implementation. Independent re-derivation reproducing lane 02's 869/1651/2652 **and** its
506/321/42 tiers **and** its 7-fixed/6-remaining #5682 split is the evidence the two
implementations agree.

Calibration is asserted in CI by `tests/test_zh_tw_simplified_contamination.py`, not left
to prose:

| Case | Expectation |
|---|---|
| 台 吃 游 群 床 | never flagged (legit Taiwan usage; Big5-encodable) |
| 学 说 这 个 财 双 变 录 来 续 | always flagged |
| 极 | **known false negative** — rare Simplified form inside Big5 |

The rule is tuned for **precision**: a false positive would reject correct Traditional
prose and train people to bypass the gate. Under-reporting is the safe direction.

## 3. PR #5682 — DO NOT TOUCH (verified live, still OPEN)

`OPEN` / `MERGEABLE` / non-draft · head `5666b796938ba0f5d80e0287b01e7d9294244240`.
All 20 zh-TW paths it owns are marked `OWNED_BY_5682_DO_NOT_TOUCH` in the TSV.

Lane 02's ownership split was re-verified against the PR's own head — **exact match**:

| | Lane 02 | This lane | |
|---|---|---|---|
| zh-TW paths owned | 20 | **20** | match |
| script-fixed by #5682 | 7 | **7** | match |
| still Simplified after merge | 6 | **6** | match (same 6 paths, same chars) |
| **net after #5682 merges** | 862 | **862** | **869 − 7** |

### Named follow-up set — 6 files that stay contaminated after #5682

`followup_after_5682_merges.tsv`. **Flagged to the #5682 lane owner.** #5682 touches these
for PLACEHOLDER-class reasons; it does not fix their script. They remain
`OWNED_BY_5682_DO_NOT_TOUCH` while it is open — **re-audit them after it merges**.

| Severity | distinct | chars | file |
|---|---|---|---|
| PARTIAL | 4 | 记录双变 | `gen_z_professionals/burnout/INTEGRATION` |
| PARTIAL | 3 | 个这双 | `gen_z_professionals/financial_anxiety/INTEGRATION` |
| SPOT_LEAK | 2 | 续来 | `healthcare_rns/burnout/INTEGRATION` |
| SPOT_LEAK | 2 | 这个 | `healthcare_rns/financial_anxiety/INTEGRATION` |
| SPOT_LEAK | 2 | 个双 | `working_parents/burnout/INTEGRATION` |
| SPOT_LEAK | 1 | 财 | `gen_x_sandwich/financial_anxiety/INTEGRATION` |

## 4. Enforcement — the durable deliverable

> CLAUDE.md meta-rule: *memory is recall, not enforcement* — every hard-won lesson must be
> promoted to a CI hard gate, a can't-bypass default, or a CLAUDE.md rule.

Lane 02 named this gap explicitly: *"The Big5 detector is still **not a CI gate** … this
audit is recall — contamination can re-enter `main` until it is enforced."* This lane
closes it.

**`scripts/ci/check_zh_tw_simplified_contamination.py`** — wired into the **Drift
detectors** required check and readiness gate **34**.

### Why a DELTA (ratchet) gate

869 contaminated files are already on `main`. A gate that failed on contamination outright
would turn main permanently red and block every unrelated PR — and would be disabled within
a day, leaving the drift unenforced. So:

- `scripts/ci/zh_tw_simplified_baseline.tsv` records the 869 as **dated, sha-pinned
  known-debt**.
- PR mode inspects only zh-TW atoms **changed by that PR**. A PR touching none is a no-op.
- A changed file FAILS iff it carries **more** distinct Simplified chars than its baseline
  entry (`NEW_CONTAMINATION` if unlisted, `WORSENED` if listed).
- Improvements never fail; the gate prints the rows to delete.
- **The baseline may only SHRINK.** Adding a row to silence a red PR is the exact bypass
  this gate exists to prevent.

Renames inherit their baseline entry (`git diff -M`), so moving a contaminated file does not
false-fail as brand-new debt. Deletions are never violations.

### No runtime OpenCC dependency

The rule is a pure function of Unicode, so its output is a fixed set — frozen into
`zh_tw_simplified_charset.py` (2,477 Simplified-only + 129 Big5-encodable variant chars).
A blocking gate must not be able to redden on `pip install opencc` failing or on an OpenCC
upgrade silently reclassifying a char. Regenerate — never hand-edit — with:

```bash
python3 scripts/ci/zh_tw_simplified_charset.py --regenerate   # self-checks calibration
```

### Proof it behaves (every claim below was executed)

| Scenario | Result |
|---|---|
| **Whole landed corpus** (5,172 files) at `origin/main` | **PASS** in ~7s — main does not redden |
| PR touching no zh-TW atoms (`origin/main~1..origin/main`) | **PASS** (no-op) |
| **Real PR #5682** (touches 20 zh-TW files) | **PASS** — and independently named its 7 repairs |
| New Simplified in a changed zh-TW file | **FAIL** exit 1 (`NEW_CONTAMINATION`, 7 chars) |
| Baselined file made worse | **FAIL** exit 1 (`WORSENED`) |
| Traditional prose | **PASS** |
| `pytest tests/test_zh_tw_simplified_contamination.py` | **34 passed** |

## 5. Files

| File | Contents |
|---|---|
| `zh_tw_simplified_contamination.tsv` | 869 rows, **WHOLE_FILE tier first**, #5682 ownership marked |
| `followup_after_5682_merges.tsv` | the named 6-file follow-up set |
| `zh_tw_simplified_contamination_summary.json` | machine-readable counts + lane-02 reconciliation |
| `scripts/ci/zh_tw_simplified_baseline.tsv` | the gate's dated known-debt allowlist (869) |

`zh_tw_simplified_contamination.tsv` columns: `severity`, `distinct_simplified_chars`,
`total_simplified_occurrences`, `pr5682_ownership`, `simplified_chars_found`, `zh_tw_file`.

**Derivable columns deliberately omitted** (lane 02's gotcha, inherited): the `scan` CI
check hard-fails any blob > 1 MiB. `persona`/`topic`/`zh_tw_target` are mechanically
derivable from the path — do not "restore" them. Largest artifact here is 96 KB.
`simplified_chars_found` is capped at 24 chars; `distinct_simplified_chars` carries the
full count.

## 6. Reproduce

```bash
# the corpus ratchet (also the readiness-gate mode)
PYTHONPATH=scripts/ci:. python3 scripts/ci/check_zh_tw_simplified_contamination.py \
    --audit-corpus --head origin/main

# PR mode, as Drift detectors runs it
PYTHONPATH=scripts/ci:. python3 scripts/ci/check_zh_tw_simplified_contamination.py \
    --base origin/main --head HEAD
```

## 7. Standing rules reaffirmed

- **zh-TW is Tier-1 Claude only. Never route Qwen at zh-TW** — it emits Simplified. This
  gate is the mechanical backstop for that rule, which is why its failure message says so.
- Contamination is **not** repaired in a translation lane, and was not repaired here.
- The 869 is **debt, not a target**. The gate stops it growing; it does not shrink it.
  Shrinking it is a separate, sequenced repair lane — see the handoff.
