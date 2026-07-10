# ja-JP Translation Closure — 2026-07-10

**Agent:** Pearl_Localization
**Workstream:** `ws_cjk_atom_translation_qwen25_20260420` (owner: Pearl_Localization, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`)
**Branch:** `agent/ja-jp-translation-closure-20260710` (from `origin/main` @ `12799deabe294baf1d9da00305c2a3d43620d946`)

## Honest status: PARTIAL, real, verified — not full closure

This session advanced ja-JP bestseller-atom translation coverage with 5 genuinely
translated, byte-verified atoms and fixed one real tool bug that was blocking the
free/Tier-2 (Ollama/Pearl Star) execution path entirely. Full closure of the
remaining backlog is blocked by Pearl Star hardware throughput, not by policy or
tooling — see "Blocker" below. The background translation process was stopped
cleanly at a consistent checkpoint rather than left writing files after this
session's final commit.

## Discovery — re-derived backlog (per task instructions: do not trust stale counts)

The workstream row's last note (2026-04-24) claimed "ja-JP at 89.3% with ~366
atoms remaining." That number is stale. Also, the standing coverage tool
(`scripts/ci/report_translation_coverage.py`) has a **path-parsing bug**: for
atom source files nested more than 4 path segments deep (e.g.
`atoms/{persona}/anchored/{topic}/{engine}/CANONICAL.txt` or
`atoms/{persona}/{topic}/{engine}/{SLOT}/CANONICAL.txt`), it mis-derives
`topic`/`slot` from fixed positional indices and checks the wrong `locales/`
path, producing false "missing" and false "present" results for those entries.
**Not fixed in this session** — it is out of this lane's `translation execution
scripts` write scope and doesn't block ja-JP closure (see "Verified tool bug"
below for the one bug that did meet that bar). Flagged as a follow-up (see
Follow-ups).

**Authoritative backlog** = the manifest actually produced by
`scripts/translate_atoms_all_locales_cloud.py`'s `discover_atoms()` +
`output_path_for()` (the real execution surface for this workstream, exactly
4-level `atoms/{persona}/{topic}/{slot_or_engine}/CANONICAL.txt` paths only).
Re-derived by importing and calling that exact function — not a reimplementation:

```
python3 - <<'EOF'
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("t", "scripts/translate_atoms_all_locales_cloud.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
atoms_root = Path("atoms").resolve()
manifest = mod.discover_atoms(atoms_root)
missing = [i for i in manifest if not mod.output_path_for(atoms_root, i[0], i[1], i[2], "ja-JP").is_file()]
print(len(manifest), len(missing))
EOF
```

| | Before (this session) | After (this session) |
|---|---|---|
| Total in-scope atoms | 2,396 | 2,396 |
| ja-JP translated | 2,165 | **2,170** |
| ja-JP missing | **231** | **226** |

Cross-checked against the (buggy-but-monotonic-for-4-level-paths) standing
report: `scripts/ci/report_translation_coverage.py --locales ja-JP` moved from
3297/3752 (87.9%) to 3302/3752 (88.0%) — a +5 delta, consistent with the 5 files
actually written.

**Top personas in the real (231-atom) backlog:** nyc_executives (65),
midlife_women (34), working_parents (16), corporate_managers (13), educators (13),
entrepreneurs/first_responders/gen_alpha_students/gen_x_sandwich/
gen_z_professionals/gen_z_student/healthcare_rns/millennial_women_professionals/
tech_finance_burnout (10 each).
**Top topics:** mindfulness (79), adhd_focus (76), long tail of ~15 other topics
(burnout, imposter_syndrome, boundaries, overthinking, depression, sleep_anxiety,
compassion_fatigue, courage, financial_stress, grief, social_anxiety,
financial_anxiety, somatic_healing, anxiety, self_worth).
**Slot/engine breakdown:** PERMISSION 56, TAKEAWAY 46, THREAD 44, PIVOT 34,
STORY 28 (slot types = 208/231, ~90%); engine types (comparison, shame,
overwhelm, watcher, spiral) = 23/231, ~10%.

## Open-PR overlap check (pre-req #2)

`gh pr list --state open --search "ja_JP OR localization OR translation"` returned
30 open PRs, all `feat(catalog): ja_JP skeletons {brand} batch {N}` touching
`config/source_of_truth/book_plans_ja_jp/*.yaml` — a different subsystem
(catalog skeleton plans, not atom-level locale translation). No open PR touches
`atoms/**/locales/ja-JP/*.txt` or `SOURCE_OF_TRUTH/teacher_banks/**/locales/ja-JP/*.yaml`.
No overlap; safe to proceed.

## What shipped in this session

**5 new ja-JP bestseller-atom translations** (real, human-legible, quality-checked
Japanese — spot-checked in full, not just line-counted):
- `atoms/corporate_managers/adhd_focus/PIVOT/locales/ja-JP/CANONICAL.txt`
- `atoms/corporate_managers/adhd_focus/PERMISSION/locales/ja-JP/CANONICAL.txt`
- `atoms/corporate_managers/adhd_focus/TAKEAWAY/locales/ja-JP/CANONICAL.txt`
- `atoms/nyc_executives/adhd_focus/PIVOT/locales/ja-JP/CANONICAL.txt`
- `atoms/nyc_executives/adhd_focus/PERMISSION/locales/ja-JP/CANONICAL.txt`

**1 verified tool-bug fix** in `scripts/translate_atoms_all_locales_cloud.py`
(in-scope per mission's exception clause: "do not change translation execution
scripts unless a verified tool bug blocks ja-JP closure"):

The script's own preflight (`main()`) hard-blocked execution unless one of the
**banned-by-CLAUDE.md paid cloud keys** (`DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`,
`TOGETHER_API_KEY`, `GOOGLE_AI_API_KEY`, `CLOUDFLARE_AI_API_TOKEN`) was set —
even though the underlying `scripts/localization/llm_client.py` already fully
implements a free/local **Ollama mode** (`_is_ollama_endpoint()`) for exactly
this Tier-2 use case ("Qwen (CJK6) on Pearl Star via Ollama — free, unattended").
This forced any caller who wanted CLAUDE.md-compliant translation toward a
banned paid provider or a hard stop. Fixed by importing `_is_ollama_endpoint`
and adding it to the `_has_llm_key` check (2-line diff, no behavior change for
any existing cloud-key caller). Verified: Pearl Star reachable at
`pearlstar.tail7fd910.ts.net:11434`, model `qwen2.5:14b` present
(`ollama-detected` via `/v1/models`), preflight now passes with only
`OLLAMA_HOST`/`OLLAMA_MODEL` set and all cloud keys unset.

## Blocker — Pearl Star hardware throughput (not policy, not tooling)

`qwen2.5:14b` on Pearl Star (`/api/ps`) reports `size_vram: 3.37GB` of a
`10.3GB` model — **only ~33% GPU-offloaded**, the rest running on CPU. Measured
latency: ~25–40s/atom at concurrency 1 (clean, uncontended); 116s–549s/atom at
concurrency 4 (self-contention on the partially-CPU-bound model). At the
observed sustained rate, closing the full 226-atom residual would take roughly
2–5+ hours of continuous unattended runtime — squarely within the Tier-2
"free, unattended" design intent (this is not meant to be babysat
synchronously), but beyond a single interactive session.

**Secondary, smaller finding:** 2 of 5 dispatched engine-type atoms (28-variant
`comparison`/`overwhelm` files) failed `validate_translation` with
`variant count mismatch: expected 28, got 0` — the model's output didn't parse
into 28 variants, plausibly related to the model's small `context_length: 4096`
(from `/api/ps`) against a large 28-variant source prompt. This affects only the
~23/231 engine-type multi-variant atoms (~10% of the backlog); the ~208
slot-type atoms (PERMISSION/TAKEAWAY/THREAD/PIVOT/STORY, typically 4–12
variants) are not expected to hit this ceiling. Not fixed in this session
(would require Pearl Star-side Ollama config, e.g. `num_ctx`, out of this
lane's write scope) — flagged as a follow-up.

## Resume command (exact — verified working)

```bash
unset DASHSCOPE_API_KEY DEEPSEEK_API_KEY TOGETHER_API_KEY GOOGLE_AI_API_KEY CLOUDFLARE_AI_API_TOKEN
export OLLAMA_HOST="http://pearlstar.tail7fd910.ts.net:11434"
export OLLAMA_MODEL="qwen2.5:14b"
python3 scripts/translate_atoms_all_locales_cloud.py \
  --locale ja-JP --resume --batch-size 2 --rate-limit 0.2 \
  --checkpoint-path artifacts/localization/ja_jp_closure_20260710/checkpoint.jsonl \
  --output-log artifacts/localization/ja_jp_closure_20260710/output_log.jsonl
```

`--batch-size 2` (down from the 4 used in this session) is recommended given the
partial-VRAM-offload contention observed. `--resume` makes this safe to run
repeatedly/unattended (skips anything already valid, matching the checkpoint
already committed in this branch).

## Quality-contract verification

- `python3 scripts/check_golden_translation.py --locales ja-JP zh-CN zh-TW ko-KR zh-HK zh-SG`
  → **OK (8 segments × 6 locale(s))**, before and after this session's changes.
- `python3 scripts/ci/report_translation_coverage.py --locales ja-JP,zh-CN,zh-TW,ko-KR,zh-HK,zh-SG --output artifacts/localization/coverage_after_20260710.json`
  → ja-JP 88.0% (3302/3752, legacy/buggy-but-monotonic metric); zh-TW/zh-CN/ko-KR/zh-HK/zh-SG
  untouched by this lane (out of scope — `zh-TW`/`zh-CN` explicitly OUT_OF_SCOPE
  per mission brief; ko-KR/zh-HK/zh-SG not part of this session's mandate).
- No zh-TW or zh-CN files touched (confirmed via `git status --short` — only
  `atoms/{corporate_managers,nyc_executives}/adhd_focus/{PIVOT,PERMISSION,TAKEAWAY}/locales/ja-JP/`
  and `scripts/translate_atoms_all_locales_cloud.py` changed).
- `python3 scripts/ci/audit_llm_callers.py` — run before push (see CLOSEOUT_RECEIPT for result).

## Follow-ups flagged (out of this lane's scope, not attempted here)

1. **Teacher-bank ja-JP gap is enormous and separate from the ~231-atom bestseller
   backlog.** `python3 scripts/localization/teacher_bank_locale_parity.py --locales ja-JP --verbose`
   shows 14 of 15 teacher banks at **0% ja-JP** (only `adi_da` at 36%, missing
   `COMPRESSION`). That's ~1,900+ atoms (14 teachers × ~135 avg en-US atoms ×
   up to 11 slot types) at zero — a separate, much larger workstream than the
   "~366 atoms remaining" figure the `ws_cjk_atom_translation_qwen25_20260420`
   row referenced (which was about the persona/topic bestseller tree, not
   teacher banks). `release_thresholds.yaml` currently sets
   `min_teacher_bank_parity_cjk: 0.0` (advisory-only), so this isn't a hard gate
   today, but it's a real, large, undocumented-in-scope gap worth its own lane.
2. **`scripts/ci/report_translation_coverage.py` path-parsing bug** (see
   Discovery section) — produces incorrect missing/present counts for atoms
   nested more than 4 path segments deep. Should be fixed to use
   `source.parent / "locales" / locale / "CANONICAL.txt"` (depth-independent)
   instead of positional `rel.parts[0..2]` indexing.
3. **`.github/workflows/translate-bestseller-atoms.yml`** prefers
   `TOGETHER_API_KEY` and falls back to `DASHSCOPE_API_KEY` — both are on
   CLAUDE.md's BANNED paid-LLM-API list. This CI workflow predates this session
   and was not touched (workflow/CI changes are outside this lane's
   `WRITE_SCOPE`), but it's a standing LLM Tier Policy violation an owner should
   address (e.g., point it at Pearl Star Ollama, gated behind self-hosted-runner
   reachability, or retire it in favor of the interactive/queued path used here).
