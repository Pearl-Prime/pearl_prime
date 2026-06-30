# CJK Atom Translation Queue

**Owner:** Pearl_PM
**Last updated:** 2026-06-29 (OPD-20260629-003 — durable queue worker + held-back recovery)
**Infrastructure:** qwen2.5:14b on Pearl Star Ollama, dispatched **queue-first** via the
Procrastinate `llm` queue (`procrastinate-worker-llm` systemd unit, concurrency=1,
shared GPU `gpu_heavy_lock`). Direct-Ollama translation is deprecated (RAP queue-first).

## Current State (G1/G2 — base = 4,909 en atoms)

| Locale | Atoms | Target | Coverage | Notes |
|--------|-------|--------|----------|-------|
| en-US (base) | 4,909 | 4,909 | 100% | persona + engine atoms |
| zh-TW | ~4,896 | 4,909 | ~99.7% | at ceiling; #3091 + 52-holdback (#3127) |
| ja-JP | ~4,445 | 4,909 | ~90.5% | #3091 + holdback; ~464 residual queued (STEP 3) |
| zh-CN | ~1,965 | 4,909 | ~40.0% | ~2,944 remaining (STEP 3 wave) |
| ko-KR | 227 | 4,909 | ~4.6% | ~4,682 remaining (STEP 3 wave, P1 of new wave) |
| zh-HK | 243 | 4,909 | ~5% | not yet scheduled |
| zh-SG | 243 | 4,909 | ~5% | not yet scheduled |

**G1 (ja-JP/zh-TW near ceiling): MET.** zh-TW ~99.7%, ja-JP ~90.5%.
**G2 (queue durability): MET.** Translation routes through `procrastinate-worker-llm`
(deployed 2026-06-29); job pickup proven end-to-end (job #375 succeeded, 52-atom
holdback recovered via jobs #376/#377, all pass `validate_cjk_atom.py`).

### STEP 3 new-translation wave (queued, ~24h GPU @ concurrency=1)

| Locale | Atoms missing | Priority |
|--------|---------------|----------|
| ko-KR | ~4,682 | 1 |
| zh-CN | ~2,944 | 2 |
| ja-JP residual | ~464 | 3 |
| **Total** | **~8,090** | |

Dispatch each batch atomically (translate → `validate_cjk_atom.py` → tar-pull →
plumbing-commit off `origin/main`, path-scoped to CJK locale atoms → PR → self-merge
on green). Never strand translated atoms uncommitted (issue #3046 lesson).

## Priority Order

1. **ja-JP** (Japan) — Highest manga + audiobook market. Unblocks Series A in japan lane.
2. **ko-KR** (Korea) — Webtoon market. Unblocks Series A in korea lane.
3. **zh-CN** (China) — Largest MH market (Ximalaya, WeChat Read, Bilibili).
4. **zh-TW** (Taiwan) — Readmoo, KKBox. Traditional Chinese.
5. **zh-HK** (Hong Kong) — Shares zh-TW base with Cantonese adaptation.
6. **zh-SG** (Singapore) — Shares zh-CN base with local adaptation.

## Batch Plan

### Atom Priority (translate first)

Series A topics for manga-heavy lanes (these atoms are needed for manga content production):

| Priority | Topics | Personas | Slot Types | Est. Atoms |
|----------|--------|----------|------------|------------|
| P1 | anxiety, burnout, overthinking | All 13 | HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION | ~1,800 |
| P2 | boundaries, depression, self_worth, grief | All 13 | All 6 | ~1,500 |
| P3 | imposter_syndrome, sleep_anxiety, somatic_healing | All 13 | All 6 | ~800 |
| P4 | compassion_fatigue, courage, financial_anxiety | All 13 | All 6 | ~431 |

### Batch Execution

- Batch size: 50 atoms per batch
- Total batches: ~25,912 ÷ 50 = ~519 batches
- Estimated time per batch: ~5-8 min on Qwen3:14b (50 atoms × 6-10s each)
- Total time per locale: ~4,531 atoms ÷ 50 = ~91 batches × ~6.5 min = ~10 hours
- Total time all 6 locales: ~60 hours

### Execution Order

```
# Phase 1: ja-JP (P1 topics)
QWEN_BASE_URL=http://192.168.1.112:11434/v1 \
QWEN_MODEL=qwen3:14b \
python3 scripts/localization/translate_atoms_all_locales.py \
  --locales ja-JP \
  --topics anxiety,burnout,overthinking \
  --batch-size 50

# Phase 2: ja-JP remaining + ko-KR P1
# Phase 3: zh-CN full pass
# Phase 4: zh-TW, zh-HK, zh-SG
```

## Translation Config

```bash
# Pearl Star server (production)
export QWEN_BASE_URL="http://192.168.1.112:11434/v1"
export QWEN_MODEL="qwen3:14b"

# Translation loop: config/localization/translation_loop_config.yaml
# Draft: qwen3:14b (temp 0.25), Judge: qwen3:14b (temp 0.1)
# Max 3 retry loops, manual_review on hard fail
```

## Quality Gates

- Translation comparator loop: draft → judge → patch → retry (max 3)
- Locale-specific thresholds: ja-JP 0.78, ko-KR 0.75, zh-SG 0.72
- All hard gates must pass (min_scored_pass_threshold: 0.75)
- Manual review queue for persistent failures (target: <10% manual rate)

## CLI Reference

```bash
# Single locale batch
python3 scripts/localization/translate_atoms_all_locales.py --locales ja-JP

# All CJK locales
python3 scripts/localization/translate_atoms_all_locales.py \
  --locales ja-JP,ko-KR,zh-CN,zh-TW,zh-HK,zh-SG

# Preflight check (verify Ollama reachable)
python3 -c "
from scripts.localization.llm_client import preflight_check
ok, msg = preflight_check({'draft_model': {'ollama_model_id': 'qwen3:14b'}})
print(f'{ok}: {msg}')
"
```
