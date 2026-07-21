# Market Voice Brief — 14-Locale Translation Contract

**Owner:** Pearl_Localization (`translation` subsystem, `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`)
**Authored by:** Pearl_Writer, 2026-07-09
**Status:** NEW reference artifact. Supplements — does not replace — the canonical sources below.

## What this is

A single per-locale market-language contract for **titles, subtitles, descriptions, CTA
language, and taboo framing** across the canonical 14 locales. It exists because no such
brief existed before this document: `config/localization/quality_contracts/README.md` +
`glossary.yaml` cover *term-level* translation (10 brand terms, CJK-only), and
`config/localization/locale_registry.yaml` covers *distribution/TTS/script* facts, but
neither answers "what register, framing, and taboo language should this locale's
title/subtitle/description/CTA copy use, and what does a good vs. bad line actually look
like." This file closes that gap for downstream localization, marketing-copy, and
catalog-authoring agents.

**Does NOT change:** locale membership (still the 14 in `locale_registry.yaml`), glossary
term translations, release thresholds, golden regression segments, or subsystem ownership.
Those remain owned by `config/localization/quality_contracts/README.md` + `glossary.yaml`
+ `release_thresholds.yaml` + `golden_translation_regression.yaml` (Pearl_Localization).
This brief is a **reference layer on top of** those files, not a fork of them.

**Does NOT translate catalog content.** No book, title, subtitle, or description in this
document is a shippable localized asset — every example pair below is illustrative only,
to calibrate register and framing for the agent doing the real translation work.

## How to use this doc

1. Before writing or reviewing a title/subtitle/description/CTA in a target locale, read
   that locale's section below in full.
2. Cross-check any of the 10 core brand terms (`nervous system`, `the alarm`, `the mask`,
   `the pattern`, `the strategy`, `the cost`, `somatic`, `watcher`, `false alarm`,
   `the thread`) against `glossary.yaml` first — this brief does not re-derive glossary
   translations, it tells you the framing rules those terms must sit inside.
3. Title/subtitle structure (Formula-4: topic/hook keyword placed after a colon, a
   persona token present in the subtitle, a combined title+subtitle length ceiling) is
   the shared architecture default across all locales — see
   `docs/NAMING_COVER_SYSTEM_37x14.md`. It is currently **byte-verified only for the
   Waystream `en_US` catalog** (94.1% pass rate); no other locale has localized
   title/subtitle text on `main` yet. When you are the first to translate a title into a
   target locale, preserve the *semantic slots* (hook/keyword + persona reference) rather
   than word-for-word translating the English Formula-4 output — literal translation
   routinely breaks natural word order, especially in CJK and German compound-noun
   contexts (see per-locale notes below).
4. If a locale's mental-health wording caution conflicts with a literal English source
   sentence, the caution in this brief wins — flag the conflict rather than translating
   through it.

## Canonical facts this brief inherits (do not re-litigate here)

- 14 locales, membership frozen: `en-US, zh-CN, zh-TW, zh-HK, zh-SG, ja-JP, ko-KR, es-US,
  es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR` (`locale_registry.yaml`).
- Script split: zh-CN/zh-SG = Simplified; zh-TW/zh-HK = Traditional. Never mix.
- Distribution hard rules (`locale_registry.yaml` → `distribution_rules`):
  `zh-CN` not via Findaway; `zh-TW` and `zh-HK` not in US storefront; `en-US` not in TW
  storefront; `hu-HU` must use ElevenLabs (Google Neural2 has no hu-HU voice); a
  locale/storefront mismatch is a **CI failure**, not a warning.
- Glossary coverage today is **CJK-only** (6 locales × 10 terms in `glossary.yaml`); the
  8 non-CJK locales (en-US, es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR) have **zero**
  glossary entries for the 10 core brand terms as of this writing. Treat any ad hoc
  translation of those terms in a non-CJK locale as provisional until Pearl_Localization
  populates the glossary — flag the choice in the PR rather than silently deciding it.

---

## en-US — English (United States) — baseline reference locale

- **Register:** Direct, second-person, plain-English self-help register. This is the
  reference register every other locale's brief entry below is adapted *from*, not a
  locale requiring its own translation pass.
- **Preferred framing:** Nervous-system / somatic framing ("your body did this to protect
  you"), practical and evidence-adjacent without being clinical.
- **Disallowed framing:** Diagnostic language presented as fact ("you have generalized
  anxiety disorder"); this is self-help content, not a clinical claim.
- **Title/subtitle constraints:** Formula-4 is enforced here and only here today (topic
  keyword after the colon, persona token in the subtitle, combined length ceiling) — see
  `waystream_subtitle_regen.py`. This is the pattern every other locale should structurally
  mirror, not literally translate.
- **Translation dangers / calques to avoid:** N/A (source locale) — but note idioms coined
  here (`the alarm is lying`, `the mask`, `the cost`) are figurative and must be treated as
  concepts to re-express, not strings to transliterate, when localized.
- **Mental-health wording caution:** Keep "nervous system," "somatic," "pattern" — avoid
  drifting into diagnostic/clinical vocabulary (DSM-style labels) in consumer-facing copy.
- **Storefront/territory gotchas:** `en-US` must not appear in the TW storefront
  (`distribution_rules.en-US_not_in_TW_storefront`).
- **Good vs bad example:**
  - GOOD: *"The Alarm Is Lying: A Guide for the Overwhelmed Professional"*
  - BAD: *"Generalized Anxiety Disorder Management for Executives"* (clinical framing,
    no persona hook, violates Formula-4 keyword placement).

## zh-CN — Chinese (Simplified) — Mainland China

- **Register:** Formal-practical Putonghua; avoid overly casual internet slang, avoid
  overly literary/classical register — target a calm, competent-authority voice.
- **Preferred framing:** Practical stress-management and nervous-system framing;
  self-improvement / self-cultivation angle reads well.
- **Disallowed framing:** Anything that reads as a clinical mental-illness diagnosis, or
  language that could be construed as medical advice — mainland regulatory sensitivity
  around health claims is high. Avoid politically adjacent metaphors entirely (e.g. any
  language evoking surveillance/"watching" in an authority-figure sense — note the
  glossary's own `watcher` = 观察者 is scoped to mindfulness-observer, keep it there).
- **Title/subtitle constraints:** Simplified-script compact titles read better shorter
  than the English original; do not pad a translated title to match the English
  character count — CJK conveys more meaning per character.
- **Translation dangers / calques to avoid:** Do not calque English idiom structure
  ("the alarm is lying" → a literal 警报在说谎 reads as a personified-object error in
  Chinese). Re-express as the *concept* (a false threat signal, 误报 per glossary), not a
  literal talking-alarm image.
- **Mental-health wording caution:** Per `manga_catalog_reconciliation` gray-zone
  distribution finding, zh-CN content carries a **HIGH** distribution-risk rating —
  full AI-disclosure and conservative claim language are load-bearing, not optional.
- **Storefront/territory gotchas:** Google Play is **not available** in mainland China;
  Findaway does **not** distribute here (`distribution_rules.zh-CN_not_via_findaway`);
  route through local platforms (`ximalaya`, `netease_cloud_music`, `wechat_read`,
  `dedao`) per `locale_registry.yaml`.
- **Good vs bad example:**
  - GOOD: *"别再自我怀疑：为过度思考者而写的减压指南"* (practical, persona-anchored,
    non-clinical)
  - BAD: *"广泛性焦虑障碍自助手册"* ("Generalized Anxiety Disorder self-help manual" —
    reads as a medical claim, high regulatory risk).

## zh-TW — Chinese (Traditional) — Taiwan

- **Register:** Traditional-script Mandarin with a Taiwanese cultural flavor; warmer and
  slightly more informal than zh-CN's register — direct address reads naturally here.
- **Preferred framing:** Same nervous-system/somatic core framing as en-US, expressed with
  Taiwan-market self-help conventions (encouraging, personal-growth oriented).
- **Disallowed framing:** Do not reuse zh-CN copy verbatim — positioning differs
  significantly between zh-CN and zh-TW per `locale_registry.yaml`; a mainland-flavored
  phrase can read as foreign/off-register here.
- **Title/subtitle constraints:** Same CJK compact-title rule as zh-CN — do not pad to
  English length; keep the persona-hook structure but let it breathe in Traditional
  characters rather than forcing an English-length subtitle.
- **Translation dangers / calques to avoid:** Same anti-literal-idiom rule as zh-CN
  (do not personify "the alarm" as a talking object) — but do not simply reuse the zh-CN
  translation string; author or adapt separately for Taiwan register.
- **Mental-health wording caution:** Mental-health stigma is present but framing has more
  latitude than mainland China; wellness/self-development framing still outperforms overt
  clinical language.
- **Storefront/territory gotchas:** zh-TW must **not** appear in the US storefront
  (`distribution_rules.zh-TW_not_in_US_storefront`) — keep TW-market copy in TW-market
  storefront listings only.
- **Good vs bad example:**
  - GOOD: *"別讓假警報綁架你的一天：給過度努力者的神經系統指南"*
  - BAD: reusing the zh-CN title string unchanged — same words, wrong register, reads as
    translated-from-mainland rather than authored-for-Taiwan.

## zh-HK — Chinese (Traditional / Cantonese) — Hong Kong

- **Register:** Formal written Chinese or written Cantonese, per `locale_registry.yaml`
  notes; narration voice must be Cantonese-capable (`yue-HK`), not Mandarin — the same
  discipline applies to written copy register (do not default to Mandarin-flavored
  phrasing).
- **Preferred framing:** Practical, competence-oriented; Hong Kong's fast urban-professional
  market responds to efficiency/burnout-relief framing.
- **Disallowed framing:** Do not reuse zh-TW copy unchanged — "positioning and invisible
  scripts differ from zh-TW (different cultural context)" per the locale registry;
  treat as a genuinely separate authoring pass.
- **Title/subtitle constraints:** Same CJK compact-title principle; where Cantonese-specific
  vocabulary diverges from standard written Chinese, prefer the version a Hong Kong reader
  would recognize as native, not textbook Mandarin-Chinese phrasing translated flat.
- **Translation dangers / calques to avoid:** Avoid Mandarin-only idiom or vocabulary
  choices that read as "translated from the mainland/Taiwan version" rather than
  HK-native. Same anti-personification rule for "the alarm."
- **Mental-health wording caution:** Same wellness-over-clinical preference as the rest of
  the Chinese-language markets; HK's dense urban-professional readership responds to
  burnout/overwhelm framing specifically.
- **Storefront/territory gotchas:** zh-HK must **not** appear in the US storefront
  (`distribution_rules.zh-HK_not_in_US_storefront`).
- **Good vs bad example:**
  - GOOD: a Cantonese-register line built for HK commuting-professional burnout, reviewed
    by an HK-fluent pass, not machine-translated from zh-TW.
  - BAD: shipping the zh-TW string as-is under a `zh-HK` label — this is the single most
    likely accidental drift in this locale (Traditional script matches, register does not).

## zh-SG — Chinese (Simplified / Singaporean) — Singapore

- **Register:** Simplified-script, Singaporean-inflected Mandarin; note the registry's own
  caution — English dominates commerce in Singapore, so this locale may be lower-priority
  than an eventual `en-SG` variant; do not over-invest translation effort here relative to
  higher-opportunity CJK locales without an explicit go-ahead.
- **Preferred framing:** Similar practical/self-improvement framing to zh-CN, adapted for
  a Singaporean multicultural professional readership.
- **Disallowed framing:** Do not reuse zh-CN copy unchanged — "positioning differs from
  zh-CN (Singaporean cultural context)" per the registry; also avoid the political-metaphor
  caution that applies to zh-CN (same script family, similar sensitivity).
- **Title/subtitle constraints:** Same CJK compact-title principle as zh-CN/zh-TW/zh-HK.
- **Translation dangers / calques to avoid:** Same anti-literal-idiom rule as the other
  Chinese-script locales.
- **Mental-health wording caution:** Practical/wellness framing preferred; no elevated
  regulatory-risk flag documented for zh-SG the way there is for zh-CN, but treat with the
  same conservative default until a locale-specific ruling exists.
- **Storefront/territory gotchas:** No Findaway/Google-Play exclusion documented for
  zh-SG specifically (distribution IDs present for all major storefronts per
  `locale_registry.yaml`) — but confirm whether `zh-SG` or `en-SG` is the intended catalog
  locale before large-scale authoring; this is an open question in the registry notes, not
  yet resolved.
- **Good vs bad example:**
  - GOOD: a Singapore-context line referencing local professional life (multicultural
    workplace, dense urban pace) rather than a mainland-China-specific cultural reference.
  - BAD: verbatim zh-CN copy with no adaptation for Singaporean context.

## ja-JP — Japanese — Japan

- **Register:** Politeness register (丁寧語, teineigo) is **required** for narration and
  should carry through to written copy register as well — casual/plain-form (だ/である)
  copy reads as inappropriate for this content category.
- **Preferred framing:** Secular, practical, nervous-system-framed. This is explicit and
  load-bearing per `locale_registry.yaml`: **"positioning must be secular, practical,
  nervous-system-framed — not 'therapy' or 'mental health.'"**
- **Disallowed framing:** Do NOT use "therapy" (セラピー) or "mental health" (メンタルヘルス)
  as the primary framing — mental-health stigma in Japan means clinical-sounding terms
  suppress interest rather than build trust. Reframe as nervous-system regulation,
  somatic practice, or stress-relief, never as a therapy substitute.
- **Title/subtitle constraints:** Japanese titles benefit from concrete sensory/place
  detail already present in the atom library (Mount Kurama, Kyoto, urban Tokyo) —
  immersion detail is a documented strength here; do not strip it out for a generic
  translation. Keep titles compact; avoid literal English-length subtitles.
- **Translation dangers / calques to avoid:** Avoid direct katakana loanword overuse for
  concepts that have a more natural native-Japanese phrasing (e.g. default to 神経系
  for "nervous system" per glossary, not a katakana transliteration). Do not literally
  translate "the alarm is lying" — 誤報 (false alarm, per glossary) is the grounded
  concept; the personified "lying" verb does not carry over naturally.
- **Mental-health wording caution:** This is the single most explicit taboo in the whole
  locale registry — treat "therapy"/"mental health" as blocked vocabulary for this
  locale's consumer-facing copy, full stop.
- **Storefront/territory gotchas:** Audible Japan (`audible_jp`) is a **separate**
  storefront ID from Audible US — do not conflate; Kobo is a notably strong channel here
  (call out in distribution copy where relevant).
- **Good vs bad example:**
  - GOOD: *「アラームは誤作動している：頑張りすぎるあなたへ、神経系を整えるガイド」*
    (secular, nervous-system framing, polite register)
  - BAD: *「不安障害のためのメンタルヘルス・セラピーガイド」* ("mental health therapy
    guide for anxiety disorder" — exactly the blocked clinical/therapy framing).

## ko-KR — Korean — South Korea

- **Register:** High-energy, direct address fits this market; per the registry, Korea's
  "빨리빨리" (fast-paced) culture means **micro-sessions may outperform deep dives** —
  copy should not oversell long-form depth as the primary selling point here.
- **Preferred framing:** Achievement-culture-aware framing (학벌/academic-achievement
  pressure) — burnout, perfectionism, and social-anxiety angles are particularly
  resonant per the registry notes.
- **Disallowed framing:** Avoid framing that ignores the achievement-pressure context —
  generic "just relax" copy underperforms; anchor to the specific pressures (performance,
  comparison, burnout) this market's readers recognize.
- **Title/subtitle constraints:** Titles that signal quick, actionable relief (short
  sessions, immediate technique) are expected to perform better than titles promising a
  long deep-dive journey — reflect this in subtitle framing, not just title choice.
- **Translation dangers / calques to avoid:** Do not calque English idiom order; Korean
  sentence structure (SOV) means a literal word-order translation of an English title
  reads awkwardly — restructure, don't transliterate.
- **Mental-health wording caution:** Registry notes mental-health awareness is "growing
  rapidly post-pandemic" — clinical language is less taboo here than in Japan, but
  achievement/burnout framing still outperforms generic wellness copy.
- **Storefront/territory gotchas:** Local platforms `naver_audiobook` and `kakao_page`
  are documented alongside standard storefronts — call these out in any Korea-specific
  distribution copy.
- **Good vs bad example:**
  - GOOD: *"3분이면 충분합니다: 완벽주의에 지친 당신을 위한 신경계 리셋"* (3 minutes is
    enough — micro-session framing, achievement-culture-aware persona)
  - BAD: a title promising a "12-week deep transformation journey" — mismatched to the
    fast-paced-content-expected market signal in the registry.

## es-US — Spanish (US Hispanic market)

- **Register:** Neutral Latin American Spanish — explicitly **not** Castilian per the
  registry ("Neutral Latin American Spanish preferred (not Castilian)").
- **Preferred framing:** Same nervous-system/somatic framing as en-US, translated into
  neutral LatAm register; this is the largest non-English US audiobook opportunity per
  the registry, so treat it as a first-class market, not an afterthought translation.
- **Disallowed framing:** Do not use Castilian-specific vocabulary or the `vosotros` verb
  form — that belongs to es-ES only, and using it here reads as foreign to the US
  Hispanic audience.
- **Title/subtitle constraints:** Same Formula-4 semantic-slot structure as en-US
  (keyword hook + persona reference); Spanish titles run longer than English for the same
  meaning — do not force an English-length ceiling onto the translated title.
- **Translation dangers / calques to avoid:** Avoid Spain-specific idiom or slang; also
  avoid over-literal translation of English figurative phrases ("the alarm is lying")
  — prefer a natural LatAm-Spanish rendering of the false-alarm concept over a strict
  transliteration.
- **Mental-health wording caution:** No elevated stigma flag documented for this locale;
  standard nervous-system/somatic framing applies as in en-US.
- **Storefront/territory gotchas:** Distributes to **US storefronts only** — same
  territory as en-US but a distinct locale; do not conflate with es-ES's separate
  storefront IDs.
- **Good vs bad example:**
  - GOOD: *"La alarma está mintiendo: una guía para quienes nunca logran descansar"*
  - BAD: *"La alarma está mintiendo: una guía para vosotros que nunca descansáis"*
    (Castilian `vosotros` form in a US Hispanic-market title).

## es-ES — Spanish (Castilian) — Spain

- **Register:** Castilian Spanish register — `vosotros` verb forms and the c/z
  pronunciation-driven spelling distinctions are expected here (per the registry).
- **Preferred framing:** Same core nervous-system/somatic framing, expressed in
  Peninsular-Spanish idiom and register.
- **Disallowed framing:** Do not reuse es-US copy unchanged — the registry explicitly
  calls out that this is a **separate storefront** from es-US; treat the translation as
  its own authoring pass, not a `vosotros`-swap of the LatAm string.
- **Title/subtitle constraints:** Same Formula-4 semantic-slot structure; expect similar
  length expansion versus English as in es-US.
- **Translation dangers / calques to avoid:** Avoid LatAm-specific vocabulary/slang
  (the inverse of the es-US caution); avoid literal transliteration of English figurative
  phrases.
- **Mental-health wording caution:** No elevated stigma flag documented; standard framing
  applies.
- **Storefront/territory gotchas:** "Separate storefront from es-US — do not mix in same
  catalog upload" is explicit in the registry; this is a hard packaging rule, not just a
  style preference.
- **Good vs bad example:**
  - GOOD: *"La alarma está mintiendo: una guía para quienes nunca lográis descansar"*
    (vosotros form, Castilian register)
  - BAD: shipping the es-US catalog entry unchanged under the es-ES storefront listing.

## fr-FR — French — France (and French-speaking Europe)

- **Register:** More philosophical framing is culturally accepted here than in most other
  markets — the registry explicitly notes mental-health discourse "differs — more
  philosophical framing accepted."
- **Preferred framing:** Stoic/existentialist framing can sit **alongside** the somatic
  approach per the registry — this is a documented opportunity, not just a tolerance; a
  purely somatic/body-based pitch may underperform a version that also nods to the
  philosophical tradition (facing the self honestly, etc.).
- **Disallowed framing:** Avoid an overly clinical-American self-help tone applied
  unchanged — French readers of this content category expect more intellectual
  framing than a purely prescriptive "5 steps" American self-help voice.
- **Title/subtitle constraints:** French titles typically run longer than English for
  equivalent meaning (grammatical gender + article usage); do not force the English
  character-length ceiling.
- **Translation dangers / calques to avoid:** Avoid anglicisme-heavy translations of
  therapeutic vocabulary where a native French term exists and is culturally weightier
  (e.g. prefer a philosophically-toned French phrase over a flat calque of "the alarm is
  lying").
- **Mental-health wording caution:** Less taboo around psychological/therapeutic
  vocabulary than Japan or Hungary; the philosophical-framing opportunity above is the
  more important craft lever here, not a taboo to avoid.
- **Storefront/territory gotchas:** Standard EU storefront IDs (`google_play`, `findaway`,
  `apple_books`, `kobo`, `spotify` all `FR`) — no exclusion rules documented beyond the
  general EU set.
- **Good vs bad example:**
  - GOOD: *"L'alarme ment : petit traité pour ceux qui n'arrivent jamais à se reposer"*
    (philosophical/literary-toned framing, "petit traité" nods to the French
    essay/treatise tradition)
  - BAD: a flat, clinical, American-styled "5 Steps to Calm Your Nervous System" tone with
    no adaptation to the accepted philosophical register.

## de-DE — German — Germany / Austria / Switzerland (DACH)

- **Register:** Evidence-based, science-grounded tone. The registry is explicit:
  "evidence-based, science-grounded framing strongly preferred."
- **Preferred framing:** Secular nervous-system/neuroscience angle. Registry: **"Avoid
  overtly spiritual framing — secular nervous system/neuroscience angle works best."**
  High-search terms to anchor to: **"Stressbewältigung"** (stress management) and
  **"Burnout."**
- **Disallowed framing:** No spiritual, mystical, or vaguely "energy"-based framing —
  this is the strongest secular-framing requirement of any locale in this brief alongside
  ja-JP's therapy/mental-health taboo. If a source atom leans spiritual/metaphysical, it
  needs a secular-neuroscience reframe for this locale, not a literal translation.
- **Title/subtitle constraints:** German compound nouns can make literal translations of
  English titles run significantly longer — do not force the English length ceiling;
  prefer a well-formed shorter German compound over a padded phrase-by-phrase translation.
- **Translation dangers / calques to avoid:** Avoid English loanword overuse where a
  precise German compound exists (Germans expect precision here — "Stressbewältigung" over
  an anglicized alternative). Avoid literal translation of American self-help idiom
  ("the alarm is lying") without a science-grounded reframe.
- **Mental-health wording caution:** Clinical/scientific vocabulary is **preferred**, not
  avoided (opposite of ja-JP) — but keep it secular-neuroscience, not spiritual.
- **Storefront/territory gotchas:** `audible_de` is Germany's own significant Audible
  storefront, called out separately from the general set — largest European audiobook
  market per the registry, so DE-specific distribution copy should not be an afterthought.
- **Good vs bad example:**
  - GOOD: *"Fehlalarm im Nervensystem: Ein wissenschaftlich fundierter Leitfaden gegen
    Stressbewältigung und Burnout"* (neuroscience-grounded, secular, uses the documented
    high-search terms)
  - BAD: *"Die Energie deines inneren Selbst heilen"* ("healing your inner self's energy"
    — exactly the overtly spiritual framing the registry says to avoid).

## it-IT — Italian — Italy

- **Register:** Wellness and self-development register; the registry explicitly says to
  **avoid clinical language in titles** specifically (description copy has slightly more
  latitude than title copy).
- **Preferred framing:** Wellness/self-development framing, warm and encouraging register.
- **Disallowed framing:** Clinical vocabulary in the **title** specifically — reserve any
  more clinical-adjacent language, if used at all, for body/description copy, never the
  title.
- **Title/subtitle constraints:** Titles should read as wellness/lifestyle products, not
  medical or therapeutic products — this is a title-specific constraint per the registry,
  distinct from a locale-wide taboo.
- **Translation dangers / calques to avoid:** Avoid literal transliteration of English
  clinical-adjacent terms into an Italian title even when a direct cognate exists (e.g.
  a cognate that sounds clinical in Italian should be avoided in the title even if
  acceptable in English).
- **Mental-health wording caution:** Same title-only clinical-avoidance rule above;
  no stronger locale-wide stigma flag documented beyond that.
- **Storefront/territory gotchas:** Standard EU storefront set (`google_play`,
  `findaway`, `apple_books`, `kobo`, `spotify` all `IT`); no exclusion rules documented.
- **Good vs bad example:**
  - GOOD: *"Il falso allarme: una guida al benessere per chi non riesce mai a fermarsi"*
    (wellness framing, no clinical vocabulary in the title)
  - BAD: *"Gestione del disturbo d'ansia generalizzato"* ("generalized anxiety disorder
    management" — clinical vocabulary in the title, exactly what the registry flags).

## hu-HU — Hungarian — Hungary

- **Register:** Wellness/self-development framing preferred over clinical language — the
  registry notes stigma "remains higher than Western Europe."
- **Preferred framing:** Same wellness/self-development framing as it-IT, but with the
  stigma caution taken more seriously (Hungary is flagged as higher-stigma than the rest
  of Western Europe, not on par with it).
- **Disallowed framing:** Clinical/diagnostic language across the whole piece (title AND
  description), not just the title — this is a broader caution than it-IT's title-only
  rule, given the higher documented stigma.
- **Title/subtitle constraints:** Same general principle as other European locales
  (semantic-slot structure over literal length-matching); no locale-specific length note
  beyond the general guidance.
- **Translation dangers / calques to avoid:** Standard anti-literal-translation guidance;
  no additional Hungarian-specific idiom note documented beyond the framing caution above
  — flag any idiom uncertainty for native review given the smaller translator pool for
  this locale.
- **Mental-health wording caution:** This is the strongest wellness-over-clinical caution
  documented for a European locale in the registry — treat it with the same seriousness
  as the ja-JP therapy/mental-health taboo, scaled to Hungary's context.
- **Storefront/territory gotchas:** **`hu-HU` must use ElevenLabs, not Google** —
  Google Neural2 has no Hungarian voice (`distribution_rules.hu-HU_use_elevenlabs_not_google`).
  This is a TTS/production rule, but it signals this locale gets comparatively less
  tooling investment elsewhere too — do not assume parity of translation-support tooling
  with larger EU locales.
- **Good vs bad example:**
  - GOOD: *"A téves riasztás: jóléti útmutató azoknak, akik sosem tudnak megpihenni"*
    (wellness framing throughout, no clinical vocabulary)
  - BAD: any title or description using a diagnostic label (anxiety disorder, clinical
    depression, etc.) — avoid across the whole piece, not just the headline.

## pt-BR — Portuguese (Brazil) — 14th locale (Q-MANGA-01)

- **Register:** Neutral Brazilian Portuguese — explicitly **not** European Portuguese
  per the registry ("Neutral Brazilian Portuguese (not European)").
- **Preferred framing:** Self-help + comics-culture-aware framing; Brazil has a real
  manga/webtoon market (Conrad Editora, Social Comics, WEBTOON PT per the registry) and
  the registry notes **WHO anxiety prevalence is world-highest** here — anxiety-topic
  framing is a strong opportunity, not a niche.
- **Disallowed framing:** Avoid European Portuguese vocabulary, spelling, or grammar
  (e.g. European-only constructions) — this locale is Brazilian-market first per the cap
  ratification (Q-MANGA-01).
- **Title/subtitle constraints:** Same general semantic-slot structure as other Latin
  locales; Portuguese, like Spanish, tends to run longer than English for equivalent
  meaning — do not force the English length ceiling.
- **Translation dangers / calques to avoid:** Avoid European-Portuguese calques
  (vocabulary/spelling differences between pt-PT and pt-BR are non-trivial — this is not
  a simple dialect toggle). Avoid literal English-idiom transliteration as in other
  locales.
- **Mental-health wording caution:** No elevated clinical-language taboo documented
  beyond the general secular/practical framing baseline; the anxiety-prevalence data point
  above suggests directness about the anxiety topic itself is workable, but keep the
  same non-diagnostic-label discipline as en-US.
- **Storefront/territory gotchas:** This locale was added via a **cap amendment** (14th
  locale, Q-MANGA-01, ratified 2026-07-04) — it is real and frozen, but has the least
  production history of the 14; expect fewer existing translated assets to draw
  precedent from than any other locale in this brief.
- **Good vs bad example:**
  - GOOD: *"O alarme está mentindo: um guia para quem nunca consegue descansar"* (neutral
    Brazilian Portuguese, direct framing)
  - BAD: a title using European-Portuguese-only vocabulary or verb conjugation patterns
    lifted from a pt-PT source instead of authored for pt-BR.

---

## Provenance

- **research:** `docs/PROGRAM_STATE.md`, `docs/SESSION_UNITY_PROTOCOL.md`,
  `artifacts/coordination/{ACTIVE_PROJECTS,ACTIVE_WORKSTREAMS,SUBSYSTEM_AUTHORITY_MAP}.tsv`,
  `docs/NAMING_COVER_SYSTEM_37x14.md` (Formula-4 / title-subtitle localization gap
  finding), `proj_manga_catalog_reconciliation_20260426` (zh-CN gray-zone distribution
  risk rating).
- **documents:** `config/localization/locale_registry.yaml` (facts of record for every
  claim above), `config/localization/quality_contracts/README.md` + `glossary.yaml`
  (term-level translation contract this brief sits on top of).
- **builds_on:** `config/localization/locale_registry.yaml` (`concept_key`: locale
  definitions) — this brief extends it with voice/framing guidance, does not fork or
  replace it.
- **inventory:** NEW artifact. No existing function reduced or replaced;
  `config/localization/quality_contracts/README.md`, `glossary.yaml`,
  `release_thresholds.yaml`, and `golden_translation_regression.yaml` are unchanged.
