# zh-TW Atom Translation — Gap Audit & Coverage Closure

**Date:** 2026-07-15
**Lane:** zh-TW production-scope coverage closure
**Owner:** Pearl_Localization (this lane) — coordinate with `ws_cjk_atom_translation_qwen25_20260420`
**`origin/main` at audit:** `8956e2222592fcc9105e4972479cd6c1f989c6bd`
**Model path:** Tier-1 Claude (`translate-zh-tw` subagents). **Qwen was NOT used** — see §3.

---

## 1. Headline

Production-scope zh-TW coverage moved **3,656/3,755 (97.36%) → 3,750/3,755 (99.87%)**, +94 files / 1,044 variants.

**100% is not reachable.** The final 5 files are blocked on a **defective English source**, not on
translation (§4). Closing them requires an English *authoring* lane, not a translator.

Scope is production-only (12 atom types) per operator ruling 2026-07-15. The 36 non-production
gap files (`COMPRESSION`/`SCENE`/`TEACHER_DOCTRINE`/`TRANSITION`/`QUOTE`/`ENGINE`) are deferred
to a later lane.

## 2. Measured gap (not quoted)

Scope replicates `scripts/ci/report_translation_coverage.py` exactly —
`BESTSELLER_SLOTS` (PIVOT, TAKEAWAY, THREAD, PERMISSION, STORY) +
`ENGINE_DIRS` (comparison, false_alarm, grief, overwhelm, shame, spiral, watcher), `len(rel.parts) >= 4`,
`locales/` excluded — computed against `git ls-tree origin/main` rather than the working tree.

| Scope | Total EN sources | zh-TW before | Missing before | After | Missing after |
|---|---:|---:|---:|---:|---:|
| Production (12 types) | 3,755 | 3,656 (97.36%) | 99 | **3,750 (99.87%)** | **5** |
| All atoms | 5,213 | 5,078 (97.41%) | 135 | 5,172 (99.21%) | 41 |

> Running the coverage script against a working tree reports **3,754/98.4%** — that reads local
> dirty state on a feature branch, not `origin/main`. Ground on `origin/main`; the 3,755 figure above
> is the script's own scope logic applied to the `origin/main` tree.

The gap was **92% two never-localized topics**: `mindfulness` (65 files) and `adhd_focus` (59).

## 3. Why Tier-1 Claude, not Qwen — both blockers reproduced live

`artifacts/qa/pearl_translator_14_locale_scope_20260715/SCOPE_LOCK.md` (PR #5679, merged
2026-07-15) blocked the **13-locale / 39,474-file** program. This lane is 99 files = **0.25%** of
that, so the volume arithmetic does not transfer. Both Qwen blockers were nonetheless re-probed
against `pearlstar.tail7fd910.ts.net:11434` (`qwen2.5:14b`) this session:

**Throughput — reproduced.** 8.5 tok/s fully warm (`load_duration` 0.07 s), vs the scope lock's
8.4 tok/s the day prior. A 14B model on a healthy GPU does 40–80 tok/s. Still CPU/VRAM-bound;
blocker now 5 days old.

**Quality — reproduced, and stronger than the scope lock's hedge.** SCOPE_LOCK §4 recorded the
contract-violating output as "weak evidence, flagged not concluded". Two of two zh-TW probes emitted
**Simplified Chinese into a zh-TW target** plus untranslated English:

> `burnout不是意志的失败。它是你所建立的系統無法承擔…` — `失败`/`压力`/`积累` are Simplified;
> `系統`/`失敗` Traditional in the same clause; `burnout` untranslated.

That is exactly the `SCRIPT_MISMATCH` defect class open PR #5682 is currently repairing. Routing
more Qwen at zh-TW would *add* to that backlog. Per `CLAUDE.md` LLM Tier Policy, operator-present
reviewed prose is **Tier 1**; precedent exists in `ws_translation_wave_ptbr_esus_20260712`
("direct Claude authoring (Tier 1, no LLM API). Landed 56 real files").

### Pre-existing contamination (reported, not fixed here)

A conservative Simplified-only-character scan over 600 landed zh-TW files found **23 (3.8%)**
already contaminated (extrapolating ~195 of 5,078). PR #5682 addresses 7. **Out of scope for this
lane** — reported to the #5682 owner to avoid collision. See the operator's
`artifacts/qa/zhtw_simplified_sweep_20260715/`.

## 4. The one real blocker — 5 files, defective English source

These 5 are **excluded**, not failed. Their English source cannot be translated:

| File | Defect |
|---|---|
| `nyc_executives/burnout/overwhelm` | 10/28 variants stubbed |
| `nyc_executives/imposter_syndrome/comparison` | 10/33 stubbed |
| `nyc_executives/imposter_syndrome/shame` | 10/33 stubbed |
| `nyc_executives/overthinking/spiral` | 10/18 stubbed |
| `nyc_executives/burnout/watcher` | 10/18 stubbed |

In each, the first 10 variants' **prose body is literally the next variant's header string**:

```
## RECOGNITION v01
---
path: watching yourself run the deal
BAND: 2
---
RECOGNITION v02      <-- prose body is a header, not prose
---
```

Consequences: headers skip (`v01 → v03 → v05`, evens absorbed as prose), and **header IDs duplicate**
(`EMBODIMENT v05` and `MECHANISM_PROOF v05` each appear twice) — violating
`.claude/skills/translation-qa/SKILL.md` rule 3 ("No duplicate localized header IDs"). No valid
target is derivable.

**This is an English authoring defect. Per lane rules, missing source content was not invented.**
Fix requires Pearl_Writer authoring the 50 missing English variants, then a 5-file translation
follow-up. **Correction to SCOPE_LOCK §5.3:** it attributes 93 of zh-TW's gaps to a
`validate_cjk_atom.py` role-schema gap. Re-tested this session, **131 of 135 English sources parse
cleanly** with real variants — the slot-role schema path is working. The residual blocker is stub
sources (5 files), not schema.

## 5. Method

Structure was never hand-authored. Each target is rebuilt through the repo's own
`parse_canonical()` / `format_canonical()` (`scripts/localization/run_translation_loop.py`), with
**only the prose swapped** — headers and metadata blocks pass through byte-exact.
Verified: **0 metadata drift across 1,044 variants**.

Staged smoke (3) → validate → pilot (12, engine-slot-weighted) → validate → scale (79, 8 shards).

## 6. Validation

```bash
# repo structural validator — 94/94 OK, exit 0
PYTHONPATH=. python3 scripts/localization/validate_cjk_atom.py --paths-file <targets94.txt>

# repo coverage (scope logic applied to origin/main; see §2 note on dirty trees)
PYTHONPATH=. python3 scripts/ci/report_translation_coverage.py --locales zh-TW
```

Lane gate (per file, all 94 PASS): repo validator · header parity vs source · zero Simplified ·
zero untranslated English · CJK density > 55%.

**Simplified detection.** Naive OpenCC `s2t` over-flags: it maps 台→臺, 吃→喫, 游→遊, 群→羣, 床→牀,
whose left-hand forms are correct, ubiquitous Taiwan usage (present in 4–25 of 400 landed files).
Big5 — Taiwan's charset — separates the cases: 台/吃/游/群/床 encode; 个/这/无/发/经/过 do not. The gate
flags only when **both** hold (`s2t` rewrites it AND Big5 cannot encode it). Tuned for precision;
rare Simplified forms sitting inside Big5 (极) are knowingly missed. Calibrated against known-good
and known-contaminated landed files before use.

## 7. Follow-ups

1. **Pearl_Writer:** author 50 missing English variants across the 5 stub files (§4), then translate.
2. **Pearl_Int:** Pearl Star GPU/VRAM saturation — 8.5 tok/s blocks all 13 locales, not just zh-TW.
3. **#5682 owner:** ~195 pre-existing Simplified-contaminated landed zh-TW files (§3).
4. **Deferred:** 36 non-production zh-TW gap files.
5. **Promote the gate:** per `CLAUDE.md` "memory is recall, not enforcement", the Simplified/English
   checks used here should become a CI gate so zh-TW script-mismatch cannot re-enter main.
