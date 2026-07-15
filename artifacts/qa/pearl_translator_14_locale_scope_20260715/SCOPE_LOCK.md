# Pearl Translator 14-Locale 100% — Scope Lock & Failure Audit

**Lane:** `01_Pearl_PM_failure_audit_scope_lock` (Wave 0)
**Agent:** Pearl_PM_ScopeLock
**Date:** 2026-07-15
**Pack:** `docs/agent_prompt_packs/20260715_pearl_translator_14_locale_100pct/`
**`origin/main` at audit:** `e754cce3d4e635d69657490b02ad1ac9afdb64c4`

---

## 0. Headline

**The 13 locale lanes in this pack cannot execute today, on either available model path.**
Wave 0 is MERGED. Waves 1–3 are BLOCKED **before translation**, per the pack's own rule
(`00_MASTER_DISPATCH_PROMPT.md`: *"If cloud agents cannot use Claude Sonnet, BLOCK before
translation rather than silently switching model family."*). Waves 4–5 do not run.

The blocker is not scoping, tooling, or worklist substrate. It is **volume vs. throughput**,
and it is arithmetic, not opinion. Both paths are quantified in §4.

---

## 1. Canonical locale scope

From `config/localization/locale_registry.yaml` and
`config/localization/native_check_contract.yaml` — these agree, no drift:

- **Baseline / reference:** `en-US`. No translation lane.
- **Translation targets (13):** `ja-JP`, `zh-CN`, `zh-TW`, `zh-HK`, `zh-SG`, `ko-KR`,
  `es-US`, `es-ES`, `fr-FR`, `de-DE`, `it-IT`, `hu-HU`, `pt-BR`.

14 canonical locales = 1 baseline + 13 targets. The pack's locale roster is **correct**.

## 2. Live coverage before execution (measured, not quoted)

```
PYTHONPATH=. python3 scripts/ci/report_translation_coverage.py \
  --locales ja-JP,ko-KR,zh-CN,zh-HK,zh-SG,zh-TW,es-US,es-ES,fr-FR,de-DE,it-IT,hu-HU,pt-BR
```

English source scope: **3,754 files** across 12 atom/engine types.

| Locale | Translated | Remaining | % |
|---|---:|---:|---:|
| zh-TW | 3,600 | 154 | 95.9% |
| ja-JP | 3,173 | 581 | 84.5% |
| zh-CN | 1,622 | 2,132 | 43.2% |
| zh-HK | 259 | 3,495 | 6.9% |
| zh-SG | 255 | 3,499 | 6.8% |
| ko-KR | 250 | 3,504 | 6.7% |
| es-US | 82 | 3,672 | 2.2% |
| pt-BR | 82 | 3,672 | 2.2% |
| es-ES | 1 | 3,753 | 0.0% |
| fr-FR | 1 | 3,753 | 0.0% |
| de-DE | 1 | 3,753 | 0.0% |
| it-IT | 1 | 3,753 | 0.0% |
| hu-HU | 1 | 3,753 | 0.0% |

**Total remaining file-translations: 39,474.**

The pack's embedded counts (`INDEX.md`) match live `origin/main` exactly. They are **not stale**.

### Native check

```
PYTHONPATH=. python3 scripts/ci/check_native_check.py --bootstrap-mode --json
```

`y=0  n=0  missing=43,092  total=43,092` → **production_y = 0.0%**.

The gate reports PASS **only because `--bootstrap-mode` is set**. Zero atoms in the entire
production scope carry `native_check: y`. Since the pack makes `native_check: y` a hard
completion condition (`FINAL COMPLETION BAR`), the native-check surface alone is a
43,092-row gap that no locale lane has ever started.

## 3. Corpus volume (measured)

```
find atoms -name CANONICAL.txt -not -path "*/locales/*" | wc -l          → 5,212 files
find atoms -name CANONICAL.txt -not -path "*/locales/*" -print0 \
  | xargs -0 cat | wc -wc                                                → 6,095,281 words / 40.4 MB
```

Corpus-wide average: **~1,170 words per atom**. These are full prose atoms
(sampled: 5,034 / 3,113 / 2,172 words), not strings or UI labels.

**Remaining translation volume: 39,474 atoms × ~1,170 words ≈ 46.2 million words of prose.**

For scale: ~46.2M words is roughly 460 full-length non-fiction books, translated, reviewed
for native fit, and landed through governance.

## 4. Why neither model path can execute this

### Path A — Claude Sonnet (what the pack mandates)

`00_MASTER_DISPATCH_PROMPT.md` → `MODEL_REQUIREMENT: Claude Sonnet for translation
drafting/revision lanes; Pearl_Writer as style/native-fit reviewer inside every locale lane`.

- ~46.2M words output ≈ **>100M output tokens** (CJK tokenizes ~1.5–2× worse per word than
  English), plus a comparable input volume, plus Pearl_Writer review passes on top.
- At the pack's own mandated batch size (25 slot files per PR), 39,474 files =
  **~1,579 pull requests**. Each must clear governance review, Drift detectors, and merge.
  At an optimistic 5 minutes of fully-automated PR wall-clock each, that is **~131 hours of
  serial PR/CI time alone**, ignoring translation itself.
- Governance caps do not rescue this by batching bigger: `pr_governance_review.py` blocks
  >500 files and `push_guard.py` caps at 1,000. Even at the maximum *legal* PR size, this is
  ~79 PRs of 500 files each — and the pack explicitly mandates 25.

This is not a session-scale task. It is not a week-scale task. **Committing Tier-1
subscription spend of this magnitude is an operator decision, not a dispatcher decision.**

### Path B — Tier-2 Qwen on Pearl Star (the substrate that is actually built)

This is what `CLAUDE.md`'s LLM Tier Policy prescribes for unattended bulk work, and what
`scripts/localization/{run_translation_loop,translate_atoms_to_locale,llm_client}.py`
already route to. **The pack forbids switching to it silently** — but it is blocked anyway:

**Live throughput probe, this session, against `http://100.92.68.74:11434` (`qwen2.5:14b`):**

| Probe | `load_duration` | `eval_count` | Generation rate |
|---|---:|---:|---:|
| Cold | (incl. load) | 62 tok | 6.6 tok/s |
| **Warm** | **0.08 s** | 80 tok | **8.4 tok/s** |

A 14B model on a healthy GPU generates **40–80 tok/s**. Measuring **8.4 tok/s fully warm**
means the model is running predominantly on CPU.

This **exactly reproduces the blocker diagnosed on 2026-07-11** and recorded in
`ACTIVE_WORKSTREAMS.tsv` under `ws_cjk_atom_translation_qwen25_20260420`:

> *"Found REAL throughput blocker: 170.9s/call measured vs 4-12s/call spec
> (docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md), root cause = GPU VRAM saturated
> (15.5/16.3GB, qwen2.5:14b running 67%/33% CPU/GPU split) by concurrent CosyVoice2 + an
> unidentified 9GB process."*

**The blocker is 4 days old and still unresolved.** (Direct `nvidia-smi` confirmation was not
possible from this session — `ssh 100.92.68.74` → `Permission denied (publickey)`. The
throughput measurement is the evidence; it is consistent with the recorded VRAM diagnosis.)

**Arithmetic at the measured rate:**

- ~1,170 words/atom → ~2,000 output tokens/atom (CJK).
- 2,000 tok ÷ 8.4 tok/s ≈ **238 s/atom** (~4 min).
- 39,474 atoms × 238 s ≈ 9.39M s ≈ **~109 days of continuous, uninterrupted single-stream
  GPU time** — and VRAM saturation is precisely what prevents parallelising it away.

### Path B quality signal (weak evidence, flagged not concluded)

The cold probe returned contract-violating output on a trivial 20-word sentence — an
untranslated English fragment plus an unsolicited translator's note:

> `あなたの身体はそれをYears Agoyears agoに学んだのです。` … `注：「Years AgOyears ago」という部分の意図が不明確なので…`

The warm probe on a longer passage returned clean, natural Japanese. **Two probes are not a
quality verdict** and this is recorded as a signal to test, not a finding. The throughput
number is the decisive blocker; quality needs its own bounded evaluation.

## 5. Lane collision — an active owner already holds this mission

`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` →
**`ws_cjk_atom_translation_qwen25_20260420`, status `active`, owner `Pearl_Localization`,
branch `agent/translation-cjk-qwen25-20260420`.**

This pack would have dispatched 13 fresh lanes across paths that workstream owns. Beyond the
collision, that lane has already **paid for and recorded findings this pack would have
re-derived from zero**:

1. The GPU/VRAM throughput blocker (§4), measured.
2. Queue-first dispatch via `pscli` is the clean Tier-2 path — Ollama-only, no cloud fallback.
3. **93 of zh-TW's 157 remaining gaps are blocked on a `validate_cjk_atom.py` role-schema
   gap — not on translation.** Dispatching a zh-TW translator lane would not have moved them.
4. `run_translation_loop.py` / `llm_client.py` carry a **cloud-first provider chain** with
   DeepSeek/Together/DashScope keys live in the operator env — a standing Tier-policy risk on
   the direct-HTTP path.
5. Deployed `/usr/local/bin/pscli` on Pearl Star is stale vs `origin/main`; no root to redeploy.

## 6. Old-prompt failure causes — verified

The dispatcher asked Wave 0 to verify the prior pack's failure claims
(`docs/agent_prompt_packs/20260714_books100_14_locale_completion/`). Verified:

| Claim | Verdict | Evidence |
|---|---|---|
| Depended on missing `scripts/localization/build_14_locale_worklist.py` | **TRUE** | `test -f` → exit 1 |
| Depended on missing `scripts/qa/run_final_books_100_matrix.py` | **TRUE** | `test -f` → exit 1 |
| Targeted a Books-100 matrix, not every translation surface | TRUE | pack read |
| Grouped locales in one lane, hiding per-language gaps | TRUE | pack read |
| Let lanes stop at smoke/pilot instead of looping to zero | TRUE | pack read |
| Did not require Sonnet + Pearl_Writer per locale | TRUE | pack read |
| Did not make `native_check: y` a hard completion condition | TRUE | pack read |

**But the diagnosis was incomplete, and that omission is why this pack inherits the same
fate.** The old pack did not stop *merely* because of missing scripts and loose lane
contracts. It stopped because **46.2M words of prose cannot be translated by a chat-session
agent fleet, and the Tier-2 GPU that could grind it is saturated.** This pack fixes the
process defects (per-locale lanes, loop-to-zero, hard native-check bar, substrate repair) —
every one of which is a genuine improvement — and then hits the same physical wall the old
pack hit. **Tighter lane contracts do not create throughput.**

## 7. Surfaces in scope (locked, for when execution is unblocked)

- `atoms/**/locales/<locale>/**` — 39,474 remaining file-translations. Primary surface.
- `native_check` sidecar metadata — 43,092 rows, currently 0% `y`. Hard bar for any 100% claim.
- `config/localization/quality_contracts/glossary.yaml` and
  `golden_translation_regression.yaml` — shared-file lock; one lane at a time.
- `SOURCE_OF_TRUTH/teacher_banks/*/approved_atoms_localized/<locale>/**` — teacher-bank parity.

## 8. Surfaces excluded

- **Pearl News locale surfaces** — no authority doc designates them a production *translation*
  surface. Excluded pending Pearl_Localization ruling.
- **Catalog/EPUB readiness** — explicitly not equivalent to atom coverage.
  `ws_cjk_atom_translation_qwen25_20260420` states it directly: *"Atom % ≠ catalog EPUB
  readiness."* Out of scope for this pack.
- **Renderer / composer work** — `OUT_OF_SCOPE` per the master dispatch prompt.

## 9. What would actually unblock this

Ranked. Each is an operator decision this dispatcher cannot make.

1. **Clear Pearl Star's GPU.** Identify and evict the CosyVoice2 + unidentified 9GB VRAM
   consumers. Restore `qwen2.5:14b` to full-GPU residency and re-probe. Target 40–80 tok/s.
   At 60 tok/s the ~109-day estimate collapses to ~15 days single-stream, and parallelism
   becomes possible once VRAM frees. **This is the single highest-leverage action and it
   blocks every other option.**
2. **Rule on the model tier for bulk translation.** The pack mandates Sonnet; `CLAUDE.md`
   Tier Policy prescribes Tier-2 Qwen for exactly this shape of unattended bulk work. These
   conflict. The conflict must be resolved by authority, not by a dispatcher picking one.
   If Tier-1 Sonnet is genuinely intended for 46.2M words, that needs explicit sign-off on
   the spend.
3. **Fix the `validate_cjk_atom.py` role-schema gap.** Unblocks 93 of zh-TW's 157 remaining
   gaps with zero translation. **zh-TW is 95.9% done — it is the only locale within reach of
   a real 100% claim**, and most of what remains is a schema bug, not prose.
4. **Close the Tier-policy hole** in `run_translation_loop.py` / `llm_client.py`'s cloud-first
   provider chain before any bulk run, or a large unattended job may silently bill paid APIs.
5. **Resolve the native_check strategy.** 43,092 rows at 0% `y`, with no lane that has ever
   produced one. Bulk-translating first and native-checking later would create 39,474 atoms
   that still cannot ship.
6. **Then** re-dispatch — routed through `ws_cjk_atom_translation_qwen25_20260420`'s owner,
   not as 13 fresh colliding lanes.

## 10. Required gates for a true 100% claim (unchanged, recorded)

Per `FINAL COMPLETION BAR`. All 13 targets at zero missing/partial; English header IDs
preserved exactly; no TODO/placeholder/English-fallback prose; locale script/region checks
pass; `native_check: y` complete on production-path atoms; glossary + golden regression
complete or excluded with proof; teacher-bank parity and Pearl News resolved per §7/§8;
all pack PRs merged or closed-as-superseded with value preserved.

**None of these are met today. `TRANSLATION_100PCT=no`, `NATIVE_CHECK_100PCT=no`.**
