# EXECUTE — Lane 4 (Pearl_Int): Voice CJK6 + CosyVoice2-vs-Qwen3-TTS A/B

This is an execution prompt. End state: **each of the six CJK locales voiced from
its translated bank (Lane 3) using its gotcha ruleset (Lane 2), on the chosen
free self-hosted engine, with a small A/B first (CosyVoice2 vs open-weights
Qwen3-TTS) to pick the best CJK voice — plus per-locale sample clips for the
operator listen.** Do not stop at "A/B run"; produce the real per-locale banks.

## Depends on
- Lane 2 (`SOCIALTTS-L2-DONE`): six `social_media_tts_text_prep_{locale}.yaml`.
- Lane 3 (`SOCIALTTS-L3-DONE`): translated locale JSONL banks.
Confirm both landed on origin/main before starting.

## Contract (in-band)
- STARTUP_RECEIPT + branch from origin/main. RAP: read
  `docs/ROBUST_AGENT_PROTOCOL.md`; GPU work on Pearl Star; queue-first;
  `check_rap_compliance.py` must not regress; health-check the node first. Load
  env by exit code (never `--verbose`).
- **Single GPU — do not double-book.** If Lane 1's English scale run is still
  going, wait. Voice one locale at a time.
- Engine defaults per `config/tts/locale_voice_routing.yaml`
  `cosyvoice2_language`: ja=`ja`, ko=`ko`, zh-CN=`zh`, zh-TW=`zh`,
  **zh-HK=`yue` (Cantonese — hard rule; Mandarin = defect)**, zh-SG=`zh`.
- NO SSML / NO engine-param modulation (forbidden). Reuse
  `generate_voice_bank_onbox.py` (applies `apply_text_prep`) pointed at each
  locale's atoms + that locale's text-prep YAML — do NOT fork a parallel voicer.
  If the onbox script assumes English voice-matrix keys, extend it minimally to
  accept a `--locale`/`--lang` + locale text-prep path, English behavior identical.
- **Free engines only.** CosyVoice2 self-hosted = unlimited default. The A/B
  challenger is **open-weights Qwen3-TTS self-hosted on Pearl Star** (Apache-2.0,
  ~10 langs incl CJK) — NOT the DashScope cloud SKU (its 10k-110k-char free quota
  can't voice a bank; only use cloud for a tiny audition if at all, operator-present).
- Layer-honest: voiced MP3 = EXECUTED-REAL. Which engine "sounds better" and
  whether a locale is shippable = operator listen (PROVEN-AT-BAR), not yours.

## Steps
1. **A/B (per language, ~10 atoms each).** Voice the same 10 translated atoms on
   (a) CosyVoice2 and (b) self-hosted Qwen3-TTS. Byte-verify both; confirm
   correct language (esp. zh-HK = Cantonese, zh-TW ≠ Mainland accent). Produce a
   side-by-side sample set per language for the operator. Record which engine you
   recommend per language and why — but the operator picks.
2. **Operator listen gate.** Surface the A/B samples (`open` them) and HOLD.
   Scaling each locale waits on the operator naming the engine per language
   (they may pick CosyVoice2 for some, Qwen3-TTS for others). Do not scale on
   your own judgment.
3. **Scale per locale (after operator picks).** Voice the full translated bank
   for that locale on the chosen engine, resumable batches, real bytes, stub
   guard. Manifest per locale: `artifacts/social_media_voice_bank_cjk6_2026-07-24/
   {locale}/MANIFEST.tsv` + MP3s → R2 (dated prefix per locale). Verify:
   manifest count == atoms; 0 stubs; language correct; text-prep fired
   (speakable differs from raw where a rule applied).
4. **Reels caption wiring** per locale (same `caption_source: voice_bank_speakable`
   linkage as English); note any manifest-path config change needed.
5. **Land** code/config/manifest diffs (MP3s to R2, not git) → PR → merge.

## Closeout
```
CLOSEOUT_RECEIPT: SOCIALTTS-L4-DONE
ab_done: <6 languages, sample paths>   engine_recommended: <per-locale>
operator_picks: <per-locale engine, or PENDING-OPERATOR-LISTEN>
voiced: ja=<n> ko=<n> zh_CN=<n> zh_TW=<n> zh_HK(yue)=<n> zh_SG=<n>
zh_hk_cantonese_verified: <yes + how>   zh_tw_accent_verified: <not-Mainland, how>
manifests: <paths>   r2_prefixes: <per-locale>
pr(s): <# + SHA>   github: <MERGED / BLOCKED-403 offline @ sha>
acceptance_layer: EXECUTED-REAL per voiced locale — PROVEN-AT-BAR pending operator listen
NEXT_ACTION: operator listen per-locale samples → approve engine + scale sign-off
```
Append a dated note to this pack's INDEX.md. Held-for-operator-listen is the
correct terminal state for scaling — never scale a locale on agent taste alone.
