# Social Media TTS — CJK6 Text-Prep Gotcha Research (Lane 2, Pearl_Research)

**Date:** 2026-07-24 · **Owner:** Pearl_Research (Lane 2 of the
`docs/agent_prompt_packs/20260724_social_tts_en_plus_cjk6/` pack)
**Trigger:** Extend the English social-media TTS text-prep method
(`artifacts/research/social_media_tts_text_prep_2026-07-19/REPORT.md`) to the
6 CJK locales so Lane 4 can voice them on self-hosted CosyVoice2.
**Acceptance layer:** RESEARCHED + CONFIG-EXISTS. Every rule below is
authored, sourced, and unit-tested against the shared loader — **none of it
is EXECUTED-REAL**. Nothing here has been proven on actual synthesized
audio; that is explicitly Lane 4's job (`04_Pearl_Int_cjk6_voice_and_ab.md`).

---

## 0. Method (unchanged from the English precedent)

Per the 2026-07-19 report, this bank uses **stock CosyVoice2 voices, no
SSML, no engine-parameter modulation** — all quality work happens in
**text prep**: punctuation-as-pacing + phrase-level trap-word rewrites +
speakable expansions, gated by a `do_not_blind_replace` guard list. That
method transfers directly to CJK; only the *content* of the rules changes
per language. All six new rulesets:

- Mirror the schema (`schema_version: 2`) of `config/tts/social_media_tts_text_prep.yaml`.
- Load and apply through the **same** `scripts/social_media/tts_text_prep.py`
  consumer used for English (`load_prep(path)` / `apply_text_prep(text, prep)`).
- Never mutate SSOT atoms — synth-input only (`ssot_mutation: forbidden`).
- Carry `cosyvoice2_language` matching `config/tts/locale_voice_routing.yaml`.

### Loader extension (the one code change this lane needed)

The original `apply_text_prep` hardcoded English sentence-boundary
punctuation two places: (1) it only split sentences at `[.!?]` followed by
`\s+`, and (2) it force-appended `.` to any output that didn't already end
in `.!?`. Both are wrong for Chinese/Japanese, whose full-stop marks
(`。！？`) are not followed by a space and aren't ASCII. Blind reuse of the
old logic wouldn't crash — it would silently append a stray ASCII `.` after
a correctly-punctuated CJK sentence (e.g. `...呼吸。` → `...呼吸。.`).

Fix: `apply_text_prep` now reads three optional `policy` keys —
`sentence_end_chars`, `sentence_boundary_requires_space`,
`default_terminal_punct` — defaulting to exactly the old hardcoded English
values when absent, so **English output is byte-identical**
(`tests/test_social_media_tts_text_prep_cjk6.py::test_english_colon_and_pacing_unchanged`
and two sibling tests assert this). The five CJK-punctuation locales set:

```yaml
policy:
  sentence_end_chars: ["。", "！", "？"]
  sentence_boundary_requires_space: false
  default_terminal_punct: "。"
```

Korean keeps the English defaults (Korean punctuation is Latin-style: `. ! ?`
with a following space, unlike ja/zh*), so `ko_KR`'s policy block carries no
override — it inherits the same behavior as English by design, not by
oversight.

### Digit-guarded colon rule (new, applies to all 6)

English's colon rule (`':\s+'` → `'. '`) required a space after the colon,
which incidentally protected clock times (`3:00`, no space) from being
split. CJK colons (both ASCII `:` and fullwidth `：`) are usually **not**
followed by a space even in prose use (`标题：内容`), so reusing the
space-gated pattern would silently do nothing for CJK. Instead all six
CJK rulesets use a **digit-lookaround guard**:
`(?<!\d)[：:](?!\d)\s*` → locale full stop — this fires on setup/list
colons regardless of spacing while explicitly refusing to fire between two
digits, so `3:00` and `3：1` survive untouched
(`test_colon_becomes_fullwidth_period_but_not_between_digits`, parametrized
over 5 locales).

---

## 1. ja-JP (Japanese) — `config/tts/social_media_tts_text_prep_ja_JP.yaml`

**cosyvoice2_language: `ja`** · fallback `edge_tts ja-JP-NanamiNeural`

### Gotcha inventory
- **Kanji multi-reading ambiguity (音読み/訓読み).** A single kanji's
  correct reading depends on context and compound partner; this is the
  subject of active NLP research (arxiv:2201.09427, "Polyphone
  disambiguation and accent prediction using pre-trained language models in
  Japanese TTS front-ends") — not a problem a regex layer can solve
  generally. The report follows the same discipline the English precedent
  used for `use`/`does`/`reset`: **do not blind-replace**; instead force
  the unambiguous kana spelling only for specific, high-frequency phrases
  known to appear in this corpus.
- **一日 (ichinichi "one day"/duration vs tsuitachi "1st of the month").**
  Our wellness-pacing copy ("one day at a time") is always the duration
  sense — forced to いちにち for the two highest-frequency phrasings found
  in this content style.
- **分 (minute vs "understand"/"fraction") after small numbers before a
  rest/breathing noun** — forced to さんぷん for the specific "three-minute
  breathing exercise" phrasing common in this bank; left alone elsewhere
  (per the English report's own finding, "minute" is *usually* fine — same
  logic applies here, force only the confirmed-frequent shape).
- **一人 (hitori "alone" vs a literal person-count reading).** Forced to
  ひとり for the "you don't have to do this alone" framing that recurs in
  wellness copy.
- **Counter words (助数詞): 本/枚/人 have irregular readings tied to the
  preceding numeral** (本: いっぽん/ろっぽん/はっぽん/じゅっぽん irregular at
  1/6/8/10; 人: 一人=ひとり, 二人=ふたり irregular, 三人+ regular; 枚 has *no*
  irregular forms — Rosetta Stone / JP YoKoSo / Wasabi-JPN counter guides).
  These are dictionary-level and well-represented in any real JA TTS
  training corpus; documented as a watch-list rather than forced, consistent
  with the "don't fix what isn't actually broken" lesson from 覚/睡覚 in
  the Mandarin section below.
- **Pitch-accent minimal pairs** (箸/橋/端 all はし with three different
  pitch contours; 雨/飴; 神/紙/髪) — real and well-documented (JP YoKoSo,
  japaneseexplorer.com), but the actual risk trigger is *hiragana-only*
  spelling with no disambiguating kanji or context; since translated copy
  normally carries kanji, and CosyVoice2's JA G2P selects pitch from the
  kanji+dictionary, this is flagged as a watch-list item for Lane 4's
  listen rather than an automated rule — there is no reliable regex
  trigger for "this hiragana span was ambiguous."
- **Colon rushed by the engine** — same 2026-07-19 finding as English,
  ported to both ASCII `:` and fullwidth `：`.
- **ー (katakana long-vowel mark) looks like an em-dash but is NOT one** —
  explicit `do_not_blind_replace` guard so the em-dash rule never touches it.
- **Register: 敬語 (keigo) vs いやしい系 (iyashikei) softness** — a voice
  direction choice noted in `config/tts/locale_voice_routing.yaml`, not a
  text-prep rule; carried forward as guidance.

### Rule counts
Punctuation: 7 · Homograph/trap: 5 (1 disabled pending Lane 4 listen) ·
Speakable expansions: 7 · **Total: 19**

### Worked examples
```
IN : その一日を大切にしてください：三分だけ呼吸に集中しましょう
OUT: そのいちにちを大切にしてください。さんぷんだけ呼吸に集中しましょう。

IN : 一人で頑張らなくていいですよ（無理はしないで）
OUT: ひとりで頑張らなくていいですよ。
```
(colon→句点, ichinichi/sanpun forced readings, parenthetical aside stripped)

### Sources
- arxiv:2201.09427 — Polyphone disambiguation & accent prediction, JA TTS front-ends
- japanesewithanime.com — on'yomi/kun'yomi mechanics
- jpyokoso.com, wasabi-jpn.com, Rosetta Stone Japanese counters — 本/枚/人 irregular readings
- japaneseexplorer.com.sg, jpyokoso.com — pitch-accent minimal pairs (箸/橋/端, 雨/飴, 神/紙/髪)
- `config/tts/locale_voice_routing.yaml` — keigo/iyashikei register note

---

## 2. ko-KR (Korean) — `config/tts/social_media_tts_text_prep_ko_KR.yaml`

**cosyvoice2_language: `ko`** · fallback `edge_tts ko-KR-SunHiNeural`

### Gotcha inventory
- **Native-Korean vs Sino-Korean number system.** Korean has two number
  systems (migaku.com, 90daykorean.com): Sino-Korean for dates, money,
  minutes, phone numbers; native Korean for age, counting objects/people/
  animals, hours (native numbers cap at 99). A digit-first G2P front-end
  commonly defaults to the Sino-Korean reading for *any* bare digit —
  meaning "3시간" (three hours, should be 세 시간) risks being read as
  삼시간 (wrong). This is the headline, most actionable Korean gotcha and
  the one this ruleset spends its rule budget on: forced native-numeral
  spelling for digit+counter combinations across 개 (items), 시간 (hours),
  번 (times/repetitions), 명 (people) for the numbers 1/2/3/5 that this
  wellness/social corpus's small counting range (breaths, minutes,
  repetitions) actually uses.
  - **Regression caught and fixed during this research pass:** the first
    draft of these rules required a trailing `\b` after the counter
    (`\b3개\b`). That silently never fires when a grammatical particle
    attaches directly with no space — "3개**의**" (three items', genitive),
    "3개**를**" (three items, object marker) — because Python's `\b`
    treats Hangul as a word character, so no boundary exists between "개"
    and "의". Fixed by dropping the trailing `\b` (the *leading* `\b` is
    still required and correctly protects multi-digit numbers like "23개"
    from matching as if it were "3개"). Covered by
    `test_ko_counter_rule_fires_with_attached_particle_no_space` and
    `test_ko_counter_rule_does_not_fire_inside_multidigit_number`.
- **Sino-Korean counters must be left alone.** 분 (minutes), 초 (seconds),
  원 (currency), 년/월/일 (year/month/date) correctly read bare digits by
  default — explicitly excluded from the native-numeral rewrite table and
  called out in `do_not_blind_replace` + `homograph_guidance_notes`.
- **Hanja-derived homographs are a translation-meaning risk, not a TTS
  pronunciation risk.** Hangul is a phonetic script — a written Hangul word
  (e.g. 연패, which could be 連覇 "win streak" or 連敗 "lose streak"
  depending on hanja origin) has exactly one pronunciation regardless of
  intended meaning. TTS says the syllables right either way; getting the
  *word* right is Lane 3's job. Documented so this lane doesn't chase a
  non-existent TTS bug.
- **받침 (final-consonant) liaison/nasalization** (e.g. 국물→궁물, 책이→채기)
  is regular, productive Korean phonology any real KO acoustic model
  applies automatically — not fixable or necessary to fix at the text
  layer. Documented as guidance so nobody "fixes" it by hand later.
- **Loanword/brand-name pronunciation** for English terms that survive
  translation (TikTok, Instagram, YouTube, "Gen Z", "burnout", "RN") —
  Hangul phonetic spellings provided.
- **힐링 (healing/wellness) register** — voice-direction note, not a rule.

### Rule counts
Punctuation: 7 · Homograph/trap: 12 · Speakable expansions: 6 · **Total: 25**

### Worked examples
```
IN : 지금부터 3시간 동안 휴식을 취하세요: 3번 반복하면 됩니다
OUT: 지금부터 세 시간 동안 휴식을 취하세요. 세 번 반복하면 됩니다.

IN : 오늘 하루 3개의 작은 목표만 정해보세요
OUT: 오늘 하루 세 개의 작은 목표만 정해보세요.

IN : 3분만 기다리세요        (Sino-Korean minutes — correctly untouched)
OUT: 3분만 기다리세요.
```

### Sources
- migaku.com/blog/korean/korean-counting-system-native-sino-numbers
- 90daykorean.com native/Sino Korean number guides
- italki.com Korean number-system Q&A (100+ defaults to Sino-Korean in both systems)
- `config/tts/locale_voice_routing.yaml` — 힐링 register note

---

## 3. zh-CN (Mandarin, Mainland) — `config/tts/social_media_tts_text_prep_zh_CN.yaml`

**cosyvoice2_language: `zh`** · fallback `edge_tts zh-CN-XiaoxiaoNeural`

This is the **base Mandarin ruleset** — zh-TW and zh-SG extend it; zh-HK
(a different language, Cantonese) does not.

### Gotcha inventory
- **多音字 (polyphonic characters) — 长/行/重/得/了/着/还/看/种/为/上/过 and
  others.** Confirmed as an active NLP research area, not a solved regex
  problem: arxiv:2207.12089 (BERT for polyphone disambiguation),
  arxiv:2102.00621 (semi-supervised polyphone disambiguation),
  mandarinhq.com/2021/07/chinese-polyphones. Per those sources, "a
  polyphonic character has a commonly used pinyin and a few rare pinyin" —
  i.e. compound-level (dictionary) readings dominate and are usually
  correct; genuine ambiguity concentrates in rarer standalone usages. **This
  ruleset does not attempt blind single-character regex fixes** for the
  same reason the English precedent didn't blind-replace `use`/`does`/
  `reset` — false-positive risk. Two real, high-value fixes made the cut,
  both by **sidestepping** the polyphone with a synonym rather than trying
  to force a pronunciation through text:
  - `看护` (kān-hù, caregiving — relevant because this repo has a
    `healthcare_rns` persona) → `照护` (zhào-hù, same meaning, zero
    polyphone risk). 看 alone defaults to kàn ("look"), so 看护 read in a
    hurry risks the wrong initial reading.
  - `二个` → `两个` — a numeral-classifier correctness net (两 not 二
    precedes a measure word when counting quantity); should rarely fire if
    Lane 3's translation is clean, included as a safety net.
- **Documented non-fixes** (explicitly NOT rules, to stop this or a future
  lane from "fixing" a non-problem): 感觉/睡觉 (both senses of 觉 are
  dictionary-common and heavily represented in wellness copy — no
  intervention needed); 值得/觉得/记得 (dictionary-safe 得 readings); V不了
  pattern (忍不了, 撑不了 — 了 as liǎo is dictionary-common here); 行 in
  common compounds (可以/行, 银行, 行业).
- **Tone sandhi (一/不 sandhi, third-tone chain sandhi)** is a phonetic
  realization rule applied to the *written* characters 一/不 regardless of
  spelling — 100% the acoustic model's responsibility, no text-level fix
  exists. Documented, not "solved."
- **儿化 (erhua)** is a colloquial Beijing-area feature not expected in
  formal translated wellness/social copy — low relevance, documented as
  guidance rather than fabricating a rule with nothing to act on.
- **Colon rushed by the engine** — same finding, digit-guarded.
- **Untranslated brand/clinical terms** — "Gen Z"→Z世代, "burnout"→职业倦怠,
  "RN"→护士. TikTok/Instagram left **disabled by default**: TikTok ≠ 抖音
  (a different, China-only product) so auto-mapping would misrepresent the
  brand; Instagram transliteration choice deferred to brand/Lane 3
  guidance rather than assumed here.

### Rule counts
Punctuation: 7 · Homograph/trap: 2 · Speakable expansions: 5 (2 disabled
by design, brand-name judgment calls) · **Total: 14**

### Worked examples
```
IN : 请花三分钟专注呼吸：这是给看护人员的建议，二个简单步骤就够了
OUT: 请花三分钟专注呼吸。这是给照护人员的建议，两个简单步骤就够了。

IN : 你并不孤单（我们一直都在）
OUT: 你并不孤单。
```

### Sources
- arxiv:2207.12089, arxiv:2102.00621, arxiv:2501.01102 — Mandarin polyphone disambiguation (BERT/semi-supervised approaches)
- mandarinhq.com/2021/07/chinese-polyphones — common polyphone list (了上为着得过还看长种)
- Standard Mandarin numeral-classifier usage (二 vs 两) — general grammar reference, not disputed

---

## 4. zh-TW (Mandarin, Taiwan) — `config/tts/social_media_tts_text_prep_zh_TW.yaml`

**cosyvoice2_language: `zh`** (same generic code as zh-CN/zh-SG — see
structural-risk finding below) · fallback `edge_tts zh-TW-HsiaoChenNeural`
· **script: Traditional required** (reuse
`scripts/ci/check_zh_tw_simplified_contamination.py`, do not re-derive).

### Headline structural finding
`config/tts/locale_voice_routing.yaml` assigns zh-TW the **same**
`cosyvoice2_language: "zh"` code as zh-CN and zh-SG. CosyVoice2 very likely
runs one generic Mandarin phonetic model behind that code, with no
guarantee it applies Taiwan-specific lexicalized readings. This is a
materially different risk shape than the other locales: it's not a text-prep
problem so much as an **engine-selection** problem. **Recommendation for
Lane 4:** A/B CosyVoice2("zh") against `edge_tts zh-TW-HsiaoChenNeural`
(a genuinely separate Taiwan voice) specifically on the lexicalized-
difference words below, before shipping zh-TW as CosyVoice2-primary. This
mirrors why `locale_voice_routing.yaml` already hard-pins zh-HK to `yue`
with an Edge-TTS fallback for the same class of problem.

### Gotcha inventory
- **和 as the conjunction "and" — hàn in Taiwan vs hé on the Mainland.**
  Sourced and cross-checked (mandarinhq.com "Mainland Mandarin vs.
  Taiwanese Mandarin," Quora consensus). This is the one lexicalized
  pronunciation difference confirmed with reasonable confidence in this
  research pass. **Headline fix:** since the engine gives no guarantee of
  applying the Taiwan reading, rewrite the conjunction to `與` (yǔ) —
  formal, single-reading, idiomatic in written Traditional Chinese —
  sidestepping the hé/hàn ambiguity entirely instead of gambling on the
  model's lexicon. Guarded with lookahead/lookbehind against firing inside
  和-compounds where 和 is *not* the "and" conjunction: 溫和 (gentle), 和平
  (peace), 和諧 (harmony), 和解 (reconciliation), 和好 (make up), 隨和
  (easygoing), 附和 (echo/parrot) — all seven verified to survive untouched
  in testing (`test_zh_tw_he_conjunction_becomes_yu_but_compounds_survive`).
- **垃圾 (garbage) — reported lèsè (Taiwan, older/traditional reading) vs
  lājī (Mainland), with usage reportedly shifting among younger Taiwan
  speakers toward lājī too.** Lower confidence than the 和 finding — this
  research pass could not independently verify current prevalence with a
  primary source, only general comparison articles. Flagged as a
  **watch-list item, not enabled**, with no forced substitution (there is
  no clean synonym swap the way 看護→照護 works for the polyphone case) —
  Lane 4 should A/B this specific word on real audio.
  - Reused directly from zh-CN base: 看護→照護 (same rationale), 二個→兩個
    (same numeral-classifier net, Traditional-script forms).
  - 頸 (neck) — the operator's own prompt-pack hypothesis flagged a possible
    jǐng/gěng reading split. This research pass could not independently
    confirm a specific Taiwan-vs-Mainland split (unlike 和, which had a
    direct, checkable source) — left as an **unverified watch-list item**,
    explicitly labeled as such rather than asserted as fact. 脖子
    (colloquial "neck") sidesteps the question entirely if it fits the copy.
- **Neutral tone (輕聲)**, common on the Mainland, is comparatively rare in
  careful Taiwan Mandarin — an acoustic-model/voice-selection concern, not
  fixable in text; documented as guidance.

### Rule counts
Punctuation: 7 · Homograph/trap: 5 (2 disabled — 垃圾 and 頸 are watch-list
only, not confirmed enough to force) · Speakable expansions: 3 · **Total: 15**

### Worked examples
```
IN : 身體和情緒需要一起照顧：這是給看護人員的建議
OUT: 身體與情緒需要一起照顧。這是給照護人員的建議。

IN : 保持溫和的心態，追求內心的和平與和諧
OUT: 保持溫和的心態，追求內心的和平與和諧。   (compounds untouched — verified)
```

### Sources
- mandarinhq.com/2018/04, mandarinhq.com/2023/02 — Mainland vs. Taiwan Mandarin pronunciation differences
- Quora consensus thread on 和 as hé/hàn in Taiwan usage
- `scripts/ci/zh_tw_simplified_charset.py` / `check_zh_tw_simplified_contamination.py` — reused, not reinvented, for the Traditional-script precondition
- `config/tts/locale_voice_routing.yaml` — zh-TW/zh-HK routing notes, structural-risk analogy

---

## 5. zh-HK (Cantonese, Hong Kong) — `config/tts/social_media_tts_text_prep_zh_HK.yaml`

**cosyvoice2_language: `yue` — HARD RULE, never `zh`** · fallback
`edge_tts zh-HK-HiuGaaiNeural`

### Hard rule (carried at the top of the file and in a `hard_rules:` block)
`config/tts/locale_voice_routing.yaml` already states this
(`"zh-HK rule: cosyvoice2_language MUST be 'yue'. NEVER 'zh'."`). This
ruleset repeats it as a load-bearing, machine-readable field
(`cosyvoice2_language: yue`) and a `hard_rules` list, and the regression
test asserts it directly
(`test_zh_hk_hard_pins_yue_never_zh`). **A Mandarin render of Cantonese-
intended content is a defect, not a lesser-quality variant** — this is not
a text-prep-layer enforcement (Lane 4's driver has to actually pass `yue`
to the engine), only a documentation-and-test contract on this file.

### Gotcha inventory
- **Cantonese is a different phonological system from Mandarin, not an
  accent of it.** Six lexical tones (traditionally cited as nine, counting
  entering-tone duplicates) vs Mandarin's four; own romanization standard
  (Jyutping) with initials/finals that don't map 1:1 to Mandarin pinyin
  (jyutping.org). Mandarin fixes from zh_CN.yaml **do not transfer** —
  this ruleset does not inherit that file.
- **行 (hang4 "walk" vs hong4 "row/bank/profession", e.g. 銀行 ngan4hong4)**
  is the one polyphone confirmed present in *both* Mandarin and Cantonese
  with real sourcing in this pass — included as the cross-linguistic
  reference point; flagged in `do_not_blind_replace` since a Cantonese-
  specific fix would need Jyutping-level tooling this pass didn't build.
- **Formal Standard Written Chinese CAN be read aloud in Cantonese** using
  literary character readings — this is normal (HK news broadcasts do
  exactly this). So the real register question isn't "must use colloquial
  characters," it's **authenticity for casual social content**: if Lane 3's
  translation uses Cantonese-specific colloquial characters (嘅/咗/喺/唔/佢/
  啲/冇/嘢/咁), those are rarer/dialectal and a plausible weak spot for a
  Cantonese model with thinner training data than Mandarin/Japanese/Korean
  (migaku.com: "Cantonese pronunciation involves tone changes in connected
  speech, rhythm patterns, and subtle pitch adjustments that TTS systems
  don't capture well yet"). A **Jyutping cheat-sheet for the 9 most likely
  colloquial particles** is provided in the YAML
  (`cantonese_particle_reference`) as Lane 4's A/B ground truth — not
  auto-inserted anywhere, since choosing colloquial vs formal register is a
  Lane 3 translation decision.
- **Confidence note:** this file's homograph/trap section is intentionally
  the thinnest of the six (1 rule, disabled by default) because
  authoritative, checkable Cantonese-TTS-specific sourcing was scarcer in
  this research pass than for Mandarin/Japanese/Korean. This is stated
  explicitly rather than padded with unverified rules — Lane 4 should
  budget extra A/B listening time for this locale specifically.

### Rule counts
Punctuation: 7 · Homograph/trap: 1 (disabled — low confidence, pending Lane
3 sample review) · Speakable expansions: 3 · **Total: 11**

### Worked examples
```
IN : 記住：你唔係一個人面對呢件事
OUT: 記住。你唔係一個人面對呢件事。

IN : 每日抽三分鐘專注呼吸就夠喇
OUT: 每日抽三分鐘專注呼吸就夠喇。
```
(Colon and terminal-punctuation rules apply cleanly to colloquial written
Cantonese exactly as they do to formal Chinese — the punctuation layer is
script-level, not register-level.)

### Sources
- jyutping.org — Jyutping romanization system overview
- migaku.com/blog/language-fun/cantonese-pronunciation — Cantonese tone system, TTS maturity caveat
- Wikipedia, "Literary and colloquial readings" — written-Cantonese colloquial character background
- `config/tts/locale_voice_routing.yaml` — the yue hard rule and HiuGaaiNeural fallback (source of truth this file mirrors, does not invent)

---

## 6. zh-SG (Mandarin, Singapore) — `config/tts/social_media_tts_text_prep_zh_SG.yaml`

**cosyvoice2_language: `zh`** · fallback `edge_tts zh-CN-XiaoxiaoNeural`
(no distinct zh-SG Edge-TTS voice exists — Singapore routes through the
Mainland fallback voice too)

### Gotcha inventory — genuinely the smallest of the six
Per the Lane 2 pack brief, Singapore Mandarin "shares Mainland Mandarin's
多音字 handling." Unlike zh-TW (script + accent mismatch against the
generic `zh` model) or zh-HK (a different language), zh-SG's phonetic risk
surface sits close to zh-CN's out of the box — **what differs is register,
not pronunciation** (`config/tts/locale_voice_routing.yaml`: "Neutral
accent, pragmatic register"). This ruleset directly reuses zh-CN's two
polyphone fixes (看护→照护, 二个→两个) rather than re-deriving them, and
keeps the rest of the file intentionally thin — padding it with invented
Singapore-specific pronunciation rules with no sourcing would be worse than
stating plainly that the delta is small.
- **Singlish-influenced particles** (啊/嘛/啦/咯 etc.) are not expected in
  this formal wellness/social copy; if they do surface, they use the same
  characters and readings as standard Mandarin — documented as
  no-action-needed rather than silently ignored.
- Simplified script (same as zh-CN) — no Traditional-script precondition
  needed, unlike zh-TW.

### Rule counts
Punctuation: 7 · Homograph/trap: 2 (reused from zh-CN) · Speakable
expansions: 3 · **Total: 12**

### Worked examples
```
IN : 请花三分钟专注呼吸：这是给看护人员的建议
OUT: 请花三分钟专注呼吸。这是给照护人员的建议。

IN : 你并不孤单，我们一直都在
OUT: 你并不孤单，我们一直都在。
```

### Sources
- `docs/agent_prompt_packs/20260724_social_tts_en_plus_cjk6/02_Pearl_Research_cjk6_tts_gotchas.md` — pack brief's own characterization (zh-SG shares Mainland 多音字 handling)
- `config/tts/locale_voice_routing.yaml` — zh-SG register note

---

## 7. Summary table

| Locale | cosyvoice2_language | Script | Punct rules | Homograph/trap | Speakable | Total | Confidence |
|---|---|---|---|---|---|---|---|
| ja-JP | ja | — | 7 | 5 (1 disabled) | 7 | 19 | High |
| ko-KR | ko | — | 7 | 12 | 6 | 25 | High |
| zh-CN | zh | Simplified | 7 | 2 | 5 (2 disabled) | 14 | High |
| zh-TW | zh | Traditional | 7 | 5 (2 disabled) | 3 | 15 | Medium (engine-selection risk flagged) |
| zh-HK | **yue** | Traditional | 7 | 1 (disabled) | 3 | 11 | Lower (thinnest sourcing; extra A/B budget recommended) |
| zh-SG | zh | Simplified | 7 | 2 (reused) | 3 | 12 | High (small, honest delta) |
| **Total** | | | **42** | **27** | **27** | **96** | |

---

## 8. What Lane 4 must still prove (not claimed here)

Per the pack's layer-honesty requirement, none of the above is more than
RESEARCHED + CONFIG-EXISTS until Lane 4:
1. Runs these six rulesets through `apply_text_prep` against real
   translated atoms (Lane 3 output) and synthesizes on CosyVoice2.
2. Confirms zh-HK output is audibly Cantonese, not Mandarin-with-
   Traditional-characters (the one non-negotiable pass/fail check).
3. A/B tests zh-TW CosyVoice2("zh") against Edge-TTS zh-TW-HsiaoChenNeural
   on the 和/垃圾/頸 watch-list before deciding zh-TW's primary engine.
4. Listens for the disabled-by-default rules in each file (ja 介護ケア,
   zh-CN TikTok/Instagram, zh-TW 垃圾/頸, zh-HK 睇護→照顧) and either
   enables them with evidence or leaves them off with a documented reason.

---

## Provenance

```
research: WebSearch (2026-07-24) — Chinese polyphone disambiguation (arxiv),
          Taiwan vs Mainland Mandarin pronunciation, Japanese kanji readings
          + counters, Korean native/Sino-Korean numbers, Cantonese Jyutping;
          artifacts/research/social_media_tts_text_prep_2026-07-19/REPORT.md
          (method precedent); docs/agent_prompt_packs/20260724_social_tts_en_
          plus_cjk6/02_Pearl_Research_cjk6_tts_gotchas.md (task brief);
          config/tts/locale_voice_routing.yaml (engine routing source of truth)
documents: config/tts/social_media_tts_text_prep_{ja_JP,ko_KR,zh_CN,zh_TW,
           zh_HK,zh_SG}.yaml (NEW); scripts/social_media/tts_text_prep.py
           (EXTENDED, English-behavior-preserving); tests/
           test_social_media_tts_text_prep_cjk6.py (NEW, 35 tests)
inventory: EXTENDS the English text-prep method to 6 CJK locales; REDUCES
           risk of blind polyphone/homograph regex by documenting why most
           single-character "fixes" would be unsafe and choosing synonym-
           swap or watch-list strategies instead
acceptance_layer: RESEARCHED + CONFIG-EXISTS — NOT proven until Lane 4
           voices real audio (EXECUTED-REAL is Lane 4's deliverable, not this one's)
```
