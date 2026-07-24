# EXECUTE — Lane 2 (Pearl_Research): CJK6 TTS "gotcha" text-prep research

This is an execution prompt. End state: **six per-language TTS text-prep
rulesets — one each for ja-JP, ko-KR, zh-CN, zh-TW, zh-HK (Cantonese), zh-SG —
committed as config + a research report, in the SAME shape as the existing
English ruleset, so Lane 4 can voice each locale correctly.** Do not stop at an
outline; produce the actual rule files.

## The English precedent to mirror (read first, fully)
- `artifacts/research/social_media_tts_text_prep_2026-07-19/REPORT.md` — the
  English method: NO SSML; punctuation as pacing (period=stop, comma=micro-pause,
  colon→period because CosyVoice rushes colons); homograph/heteronym rewrites
  (live/live, read, close, project, minute…); speakable expansions (RN→nurse,
  Gen Z→Gen Zee); number/abbreviation normalization; a `do_not_blind_replace`
  guard list to avoid false positives.
- `config/tts/social_media_tts_text_prep.yaml` (schema v2) — the machine-readable
  ruleset the code consumes. Your six outputs mirror this structure.
- `scripts/social_media/tts_text_prep.py` — `apply_text_prep(text, prep)` /
  `load_prep(path)`: the consumer. Your YAMLs must load and apply through it
  (or an extended version if a language needs a rule class English lacks — if so,
  extend the loader minimally and keep English behavior identical).

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD, `git status --short | head`, `gh auth status`,
  `git fetch origin`. Branch from origin/main.
- PROVENANCE: research → config → (Lane 4 consumes). This is genuine
  per-language linguistics research; cite sources. Engine target = CosyVoice2
  (self-hosted) with `cosyvoice2_language` per `locale_voice_routing.yaml`
  (`ja`, `ko`, `zh`, `zh`, **`yue`**, `zh`).
- LLM tier: this is operator-present research/authoring = Tier-1 Claude. Do not
  wire any paid API. Do not run live TTS (that's Lane 4).
- Layer-honest: a ruleset is RESEARCHED/CONFIG-EXISTS until Lane 4 proves it on
  real audio (EXECUTED-REAL) — do not claim a language "works" from a YAML alone.

## Per-language research — the real gotchas to cover
For EACH of the six, produce the language-specific equivalent of the English
rules. Non-exhaustive prompts (research the actual set):
- **ja-JP** (`ja`): pitch-accent minimal pairs that flip meaning; kanji with
  multiple readings (音読み/訓読み) the engine may misread; counter words
  (本/枚/人…) and how numbers read before them; long-vowel/geminate handling;
  keigo register vs iyashikei softness (matrix note). Punctuation: 。read as full
  stop, 、as pause; avoid Latin colon.
- **ko-KR** (`ko`): hanja-derived homographs; number systems (native Korean vs
  Sino-Korean) and when each is read; final-consonant liaison (받침) mis-reads;
  loanword/English-term pronunciation; 힐링 register.
- **zh-CN** (`zh`, Mandarin): tone-sandhi (esp. 一/不 and 3rd-tone chains);
  polyphonic characters (多音字: 长/行/重/得/了…) whose reading depends on sense;
  number/measure-word reading; 儿化 where relevant. Punctuation: 。！？，、.
- **zh-TW** (`zh`, Taiwanese Mandarin): same 多音字 issues PLUS Taiwan-specific
  readings that differ from Mainland (e.g. 和 as "hàn", 垃圾, 企業, 頸…); ensure
  Traditional-char input; flag any char the engine reads with a Mainland
  pronunciation. (Translation itself is Lane 3's job and is Claude-only for
  zh-TW; you only spec the pronunciation rules.)
- **zh-HK** (`yue`, CANTONESE — hard rule): this is NOT Mandarin. Cantonese
  tone/jyutping considerations; colloquial vs written-Cantonese char readings;
  ensure the ruleset + Lane 4 both target `yue`. A Mandarin render here is a
  defect. Note the fallback voice `zh-HK-HiuGaaiNeural` (Edge-TTS) if CosyVoice2
  `yue` proves weak.
- **zh-SG** (`zh`, Singapore Mandarin): neutral/pragmatic register; Singapore
  lexical items; otherwise shares Mainland Mandarin 多音字 handling.

For each: also carry over the universal ones — colon→period, no SSML, short
sentences, speakable expansions of English brand/clinical terms that survive
translation, and a `do_not_blind_replace` guard so a rewrite rule doesn't
corrupt an innocent occurrence.

## Deliverables
- `config/tts/social_media_tts_text_prep_{ja_JP,ko_KR,zh_CN,zh_TW,zh_HK,zh_SG}.yaml`
  — six rulesets, same schema as the English file, loadable by `tts_text_prep.py`.
- `artifacts/research/social_media_tts_text_prep_cjk6_2026-07-24/REPORT.md` — one
  section per language: the gotcha inventory, the rules chosen, sources cited,
  and 2-3 worked before→after examples per language.
- If `tts_text_prep.py` needed extension for a language, a minimal, tested diff
  (English behavior byte-identical; add a regression test).
- Land on a branch → PR → merge per rules.

## Closeout
```
CLOSEOUT_RECEIPT: SOCIALTTS-L2-DONE
rulesets: <6 paths>   report: <path>
per_language_rule_counts: ja=<n> ko=<n> zh_CN=<n> zh_TW=<n> zh_HK(yue)=<n> zh_SG=<n>
loader_change: <none / minimal diff + test>
pr: <# + SHA>   github: <MERGED / BLOCKED-403 offline @ sha>
acceptance_layer: RESEARCHED + CONFIG-EXISTS — NOT proven until Lane 4 voices real audio
NEXT_ACTION: Lane 4 applies these against translated atoms
```
Append a dated note to this pack's INDEX.md.
