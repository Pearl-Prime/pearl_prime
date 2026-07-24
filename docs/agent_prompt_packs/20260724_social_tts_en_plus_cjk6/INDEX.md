# Prompt Pack — Social-Media TTS: English + CJK6 (2026-07-24)

**Authored by:** Piper · **Operator directive:** finish the English social voice
bank on self-hosted CosyVoice2, then extend TTS to the 6 CJK locales (ja-JP,
ko-KR, zh-CN, zh-TW, zh-HK-Cantonese, zh-SG) — per-language gotcha research,
translation, voicing, and a CosyVoice2-vs-Qwen3-TTS A/B.

## Paste-ready next action
Paste `00_MASTER_DISPATCH_PROMPT.md` into a fresh Pearl_PM lead agent.
For the fastest real result, dispatch **Lane 1 alone first** (finish English —
it's unblocked and proves the corrected pipeline).

## Contents
| File | What |
|---|---|
| `TTS_STATE_2026-07-24.txt` | Plain-English state (operator-facing) |
| `00_MASTER_DISPATCH_PROMPT.md` | Pearl_PM dispatcher, order, hard rules, closeout |
| `01_Pearl_Int_finish_english_voice_bank.md` | Voice all 1,642 EN atoms on CosyVoice2 (correct text-prep script) |
| `02_Pearl_Research_cjk6_tts_gotchas.md` | 6 per-language TTS text-prep rulesets |
| `03_Pearl_Localization_cjk6_translate.md` | Translate the bank into CJK6 (zh-TW=Claude, zh-HK=Cantonese) |
| `04_Pearl_Int_cjk6_voice_and_ab.md` | Voice CJK6 + CosyVoice2-vs-Qwen3-TTS A/B + operator listen |

## Dependency graph
Lane 1 (now) ∥ [Lane 2 ∥ Lane 3] → Lane 4 (needs 2+3). Single Pearl Star GPU —
Lane 1's scale run finishes before Lane 4's; voice one locale at a time.

## Load-bearing facts this pack encodes
1. English is NOT voiced yet (only 8 audition clips) — Lane 1 is the first real run.
2. `generate_voice_bank.py` skips text-prep (bug); use `generate_voice_bank_onbox.py`.
3. Qwen-TTS *cloud* free quota can't cover a bank; CosyVoice2 self-hosted (unlimited)
   is the CJK default; open-weights Qwen3-TTS self-hosted is the A/B challenger.
4. zh-HK = Cantonese (`yue`), never Mandarin. zh-TW translation = Claude only
   (Qwen emits Simplified). NO SSML (operator-killed).
5. Free-TTS capability (context): 7 premium-free, 6 good-free (Edge-TTS, EU — later
   pack), 1 paid-recommended (hu-HU). This pack covers the 7 free CJK+EN.

## Completion log (lanes append here)
- (empty)
