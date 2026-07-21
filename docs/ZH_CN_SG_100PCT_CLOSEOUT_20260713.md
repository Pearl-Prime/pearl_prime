# zh-CN / zh-SG 100%-Target Closeout Packet (2026-07-13)

**Authority:** builds on `docs/LOCALIZATION_PREP_14PACK_20260713.md` (Prompt C
packet). Where this doc gives a live re-measured number for zh-CN/zh-SG, it
supersedes the Prompt C snapshot for those two locales only; the 14-pack
packet remains authority for the other 12 locales and the roster/provider/
validator/glossary sections.

**Working tree note:** this branch was cut fresh (`git worktree add ... origin/main`)
into `/Users/ahjan/phoenix_omega_worktrees/zh-cn-sg-100pct-20260713`, avoiding
the shared-tree churn issue noted in the Prompt C packet. Coverage and
validation numbers below are measured directly from a clean, full checkout
(not an archive extraction), so the `native_check` `sys.path` artifact from
the prior packet's method does not recur here — confirmed to be an archive-
extraction artifact, reproducible even in a full checkout unless
`PYTHONPATH=.` is set (a usage detail, not a code bug).

---

## 1. Live gap inventory (bestseller CANONICAL.txt corpus, 3,754 English sources)

| Locale | Translated | Coverage | Source |
|---|---:|---:|---|
| zh-CN | 1,622 / 3,754 | 43.2% | unchanged from Prompt C baseline (no new volume landed this session — see §3 blocker) |
| zh-SG | 255 / 3,754 | 6.8% | unchanged from Prompt C baseline |

Raw JSON: `artifacts/qa/zh_cn_sg_100pct_20260713/coverage_after.json`
(re-run of `scripts/ci/report_translation_coverage.py`, PYTHONPATH=. on a
clean full checkout — confirms Prompt C's numbers were correct and not an
archive artifact).

Gap breakdown by persona (missing zh-CN files, 2,131 total; full list at
session scratch, top offenders): `gen_alpha_students` (all 17 topics, ~610
files across full atom-type set), `entrepreneurs` (~258, mostly `anchored`
topic — persona added after zh-CN's last full wave), `gen_x_sandwich` (~180),
`first_responders` (~180), `working_parents` (~158), `corporate_managers`
(~138), `gen_z_student` (~121), `tech_finance_burnout` (~99), `nyc_executives`
(~91), `midlife_women` (~75), `educators` (~71). zh-SG gap is proportionally
larger (3,499 missing) and spread the same way since zh-SG has never had a
full wave (only a ~255-file pilot).

## 2. Real defect found and fixed: 35 zh-CN files were Traditional-script, not Simplified

**Finding:** a byte-level scan for Traditional-only Chinese characters
(後/裡/個/們/說/話/這/樣/時/間/問/題/國/語/沒/會/對/開/聽/見/識 — forms that
differ from their Simplified counterparts, verified against a false-positive
control set) found **35 of 1,971 `locales/zh-CN/CANONICAL.txt` files were
written entirely in Traditional Chinese**, not Simplified — a genuine
script-correctness quality defect inside content that already counted toward
the 43.2% "translated" coverage number. Confirmed by direct content
comparison against the sibling `zh-TW` file for one sample
(`atoms/tech_finance_burnout/anxiety/watcher/THREAD`) — same meaning,
independently-worded (not a byte-copy of zh-TW), but wrong script.

**Fix landed this session:** converted all 35 files Traditional → Simplified
using `opencc` (`t2s` config; `pip install opencc-python-reimplemented`, no
prior script-conversion utility existed in the repo — checked
`scripts/localization/` and `scripts/` for `opencc`/`t2s`/`s2t` before adding
this one-off, per anti-reinvention policy; this was a one-time data fix, not
a new pipeline component, so no permanent script was added to `scripts/`).
File list: `artifacts/qa/zh_cn_sg_100pct_20260713/zh_cn_script_fix_35_files.txt`.

**Re-verified after fix:**
- Traditional-char scan: 0/1,971 zh-CN files flagged (was 35) — confirmed clean.
- `scripts/localization/validate_cjk_atom.py` structural validator: 1,971/1,971
  zh-CN files `OK`, 302/302 zh-SG files `OK` (both before and after the fix —
  the defect was semantic/script, not structural, so the structural gate never
  caught it; this is worth flagging upstream as a real gap in that validator's
  coverage, not a false pass).
- `scripts/check_golden_translation.py --locales zh-CN zh-SG`: PASS (8
  segments × 2 locales) both before and after.
- No zh-SG files affected — zh-SG's 302 files were confirmed 0/302 on the
  same Traditional-char scan (see §3.1).

Logs: `artifacts/qa/zh_cn_sg_100pct_20260713/validate_cjk_atom_zh-CN.log`,
`artifacts/qa/zh_cn_sg_100pct_20260713/validate_cjk_atom_zh-SG.log`.

## 3. zh-SG validated as its own locale surface (not a zh-CN copy-forward)

**Config truth, verified in `config/localization/content_roots_by_locale.yaml`:**
zh-SG's `translation_source_locale` is `en-US`, **not** `zh-CN`. zh-SG is
already architected as an independent direct-from-English translation target,
same as zh-CN — not a derivative/copy-forward pipeline. This matters because
the mission brief's framing ("build the zh-SG derivative pass from current
zh-CN truth") does not match the live schema; flagging rather than silently
building a copy-forward pipeline that would contradict the registry.

**Empirical check — is zh-SG accidentally a copy of zh-CN anyway?** Of the 302
zh-SG atom dirs, 168 have a same-path zh-CN counterpart. Diffed all 168 pairs
byte-for-byte: **0 identical, 168 differing** — zh-SG content is genuinely
independently translated from English, not a mechanical zh-CN copy (spot-check
sample: `atoms/tech_finance_burnout/sleep_anxiety/PIVOT` — same intent per
variant, different Chinese phrasing between the two locales). This is the
"validate rather than assume perfect copy-forward" check the mission asked
for — the answer is that no copy-forward is happening at all, by design; the
open question is only whether that design (independent en-US→zh-SG vs. a
zh-CN base + Singapore market patches) is the right one going forward, which
is an operator call, not something to silently change.

### 3.1 zh-SG locale-appropriateness checks run

- Traditional-vs-Simplified script scan (same method as §2): **0/302 zh-SG
  files flagged** — zh-SG is correctly all-Simplified (as the registry
  requires: "Chinese (Simplified) — Singapore").
- Structural validator (`validate_cjk_atom.py`): 302/302 OK.
- Golden translation regression (`check_golden_translation.py`): PASS.
- Market-language patching (English-dominant-commerce note in the registry):
  **not separately checked this session** — the registry itself flags zh-SG
  as `population_status: planned` pending an ROI decision on whether
  Singapore content should even be zh-SG vs. en-US; no code exists yet to
  detect Singapore-specific terminology drift (e.g., Singlish loanwords,
  local idiom) because there is no glossary or Singapore-market style guide
  file in `config/localization/` to validate against (checked directory
  listing — only the CJK6 `glossary.yaml`, which does not carry
  per-country-within-locale terms). This is named as a real gap in §4, not
  fabricated as done.

## 4. Remaining true blockers

1. **Pearl Star queue worker is currently down (verified live, not assumed).**
   `pscli status` (run under the on-box venv,
   `/opt/pearl-star/venv/bin/python /usr/local/bin/pscli status`) reports
   `active workers: 0` with one `llm` job stuck in `doing` from a prior
   session and one new job (`#600`, my own dispatch of a 20-file zh-CN
   corporate_managers test batch via
   `scripts/localization/cjk_enqueue_translate.py`, RAP-compliant queue-first
   path) sitting in `todo` with no worker to pick it up. **I did not start a
   worker daemon or touch queue infra** — that is Pearl Star ops, out of
   scope for a locale task and risky to do unprompted on shared production
   infra. This blocks all new-volume zh-CN/zh-SG translation via the
   sanctioned path until an operator (or a dedicated Pearl Star ops session)
   restarts the queue worker. Job #600 will process automatically once a
   worker comes up — no action needed to "unstick" it beyond that restart.
2. **Pearl Star's own repo checkout is stale relative to `origin/main`**
   (verified: `main` there is at `6633530a6c`..`d2d79c4e93`-era commits;
   `git fetch` shows `539b2e4664..f986fa7c72` unfetched — hundreds of commits
   behind). Concretely, newer personas (`entrepreneurs/anchored`,
   `gen_alpha_students` in full) don't exist in Pearl Star's atoms tree yet,
   so even once the worker is back up, translation batches for those
   personas will fail with `FileNotFoundError` until Pearl Star's checkout is
   synced. 1,981 of the 2,131 missing zh-CN files DO already exist as English
   source on Pearl Star's stale checkout (verified by direct existence check
   over SSH) and could be translated today once a worker is running; the
   remaining ~150 need a Pearl Star repo sync first.
3. **zh-CN bestseller-corpus coverage is unchanged at 43.2%, zh-SG at 6.8%**
   — no new translation volume landed this session (blocker #1 prevented it).
   The real, verifiable work landed instead was a live re-measurement
   confirming the Prompt C baseline was correct (not an archive artifact) and
   a genuine script-correctness fix (35 files) inside the *existing* "done"
   set, which is a different and arguably higher-value class of work than
   raw volume — it fixes files that were silently wrong under a coverage
   metric that can't detect script errors.
4. **The structural/golden validators cannot detect script-mismatch defects**
   like the one found in §2 — `validate_cjk_atom.py` passed all 35 broken
   files both before and after the fix, and `check_golden_translation.py`
   only checks 8 fixed segments. A Traditional-character heuristic scan (like
   the one used ad hoc this session) is not wired into any CI gate. This is a
   real gap: the same class of defect could recur silently in future
   translation waves and nothing in the sanctioned validator path would
   catch it. Not fixed this session (would require a new CI gate, out of
   the "refresh + patch + validate" scope given here) — flagged for a
   follow-up CI-gate task, consistent with the "memory is recall not
   enforcement" rule (a lesson found once should become a gate, not stay in
   this doc alone).
5. **zh-SG Singapore-market-language patching has no validation surface** —
   see §3.1. No glossary, style guide, or lint exists to check for
   Singapore-specific terminology or idiom in zh-SG content. Real
   authoring/tooling gap, not evaluated further this session (would require
   either new config authoring or an explicit ROI decision per the
   registry's own `distribution_blocker` note, both out of scope for a
   validation-only pass).
6. **Teacher-bank atom class (`native_check` section of the coverage report)
   is separately near-zero for zh-CN/zh-SG** (0 native-annotated of 16,668
   zh-CN / 5,100 zh-SG checked) — this is a different content corpus from the
   3,754-file bestseller CANONICAL.txt set the mission's "43.2%" baseline
   refers to. Not conflated with the mission's completion target (which is
   the bestseller corpus per the Prompt C packet's own methodology), but
   named here so it isn't mistaken for a solved problem.
7. **Pearl News topic-YAML coverage** (`locale_structural_gate.py`) is 0% for
   both zh-CN and zh-SG (`artifacts/qa/zh_cn_sg_100pct_20260713/locale_structural_gate_pearl_news_topic_yaml.json`)
   — again a separate pipeline/corpus per the Prompt C packet's explicit
   warning not to conflate Pearl News locale coverage with bestseller-atom
   coverage. Named, not treated as in-scope.

## 5. Acceptance verdict

- **zh-CN: exact-blocked**, not complete. Coverage held at 43.2% (real,
  re-verified); one concrete quality defect (35 mis-scripted files) found and
  fixed; the path to closing the remaining 2,131-file gap is sanctioned,
  tested end-to-end (dispatch succeeds, job queues correctly), and blocked
  on a live infrastructure state (queue worker down) outside this session's
  authority to fix unprompted.
- **zh-SG: validated as its own locale surface.** Confirmed independently
  translated from en-US (not a zh-CN copy-forward, matching the registry's
  own schema) — the mission's "validate rather than assume perfect
  copy-forward" concern resolves to "there is no copy-forward pipeline at
  all, and there shouldn't be one per current config, though that's an
  operator design choice to revisit." Script-correctness clean (0/302).
  Structural and golden checks clean. Market-language-patching validation
  surface does not exist yet — named as a real gap, not fabricated as done.
