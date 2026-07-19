# Social Media TTS — Text Prep & Gender-Only Voice Plan (Pearl_Research)

**Date:** 2026-07-19 · **Owner:** Pearl_Research  
**Trigger:** Operator listen — CosyVoice **param / persona modulation sounded weird**; stock voice was better.  
**Acceptance:** research + config proposed; **not** a full re-synth until operator ratifies gender map + text-prep rules.

---

## 1. Verdict (plan change)

| Old plan (failed listen) | New plan |
|--------------------------|----------|
| One voice identity per persona **plus** pace/pause/warmth/pitch/stability modulation per topic | **Stock CosyVoice only:** `english_female` or `english_male` — **no engine params** |
| SSML / prosody tags (onboarding path) | **No SSML** for this bank — plain text only |
| Quality via voice knobs | Quality via **text prep**: homograph rewrites + **punctuation pacing** |

CosyVoice EN built-ins are trained as whole speakers. Nudging “warmth/BPM” (or equivalent) for persona/topic does not give a clean second register — it degrades the stock voice. Operator confirmed: Gen Z anxiety “modified” < regular voice.

**152 R2/local clips from the modulated scale run are VOID** (wrong contract). Do not ship them.

---

## 2. What existing Phoenix docs already say (reuse)

| Doc | Useful for social bank? | Takeaway |
|-----|-------------------------|----------|
| `docs/VOICE_PERSONA_TOPIC_RESEARCH.md` §§1–6 | Long-form audiobook / therapeutic | Keep for books; **do not drive CosyVoice API knobs** for reels |
| §7 Short-Form Social (Wave 1) | Partial | Keep register notes (hook, loudness); **strike** param-modulation as production lever |
| `specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md` | Opposite lane | ElevenLabs + **cumulative SSML** for wizard briefing — **explicitly not** the social/CosyVoice path |
| `docs/VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md` | Routing | CosyVoice for CJK narrators; EN Piper historically — social bank stays CosyVoice EN stock |
| `config/video/pacing_by_content_type.yaml` | Video edit pacing | Orthogonal (cut length); voice pacing = **text punctuation** |

**Policy for this bank:** diverge from onboarding SSML. Operator rule: SSML usually adds defects; give the engine clean speakable text.

---

## 3. Gender-only voice map (recommended default)

Stock CosyVoice2 voices only. No `clone_ref`, no param overlays, no persona “bright/warm” engine tweaks.

| Persona | Gender | `voice_id` | Why |
|---------|--------|------------|-----|
| `corporate_managers` | male | `english_male` | Anxiety male was BEST; keeps one male identity in the set |
| `gen_z_professionals` | female | `english_female` | Anxiety female was GOOD on stock-ish delivery |
| `healthcare_rns` | female | `english_female` | Compassion-fatigue female was GOOD |

**Alternate (operator may flip):** corporate → `english_female` (also BEST on listen). Do not assign three different “timbres” via params — only this binary.

Machine contract: `config/tts/social_media_voice_matrix.yaml` (rewritten to gender-only).  
Text contract: `config/tts/social_media_tts_text_prep.yaml`.

---

## 4. Pacing without SSML — punctuation buys time

External + operator doctrine (aligned):

- **Period** = full stop + breath (use more often than essay prose).
- **Comma** = micro-pause inside a thought (add at clause boundaries you’d breathe).
- **Question mark** = rising tone (real questions only).
- **Ellipsis `...`** = longer beat (use sparingly; engines vary).
- **Avoid:** parentheses, markdown/bullets, ALL CAPS emphasis, stacked `!!`, em-dash spam (rewrite as period or comma).
- **Short sentences** for reels: one idea per sentence; 15–60s scripts should sound spoken, not written.

**Practical rewrite rule for atom → speakable text:**

1. Split any sentence > ~22 words at a natural clause.
2. After a hook clause, prefer `.` before the next beat.
3. Before the payoff/CTA, insert `.` or `,` so the voice doesn’t rush the landing.
4. Read aloud once; wherever you gasp, insert punctuation.

Example (same meaning, better TTS):

- Before: `You can feel it after the third urgent chat ping: tight chest, fast checking, and the urge to fix every silence immediately.`
- After: `You can feel it after the third urgent chat ping. Tight chest. Fast checking. And the urge to fix every silence, immediately.`

(Operator taste may prefer slightly less choppy — start with **clause periods**, not telegraphic fragments, then tune.)

---

## 5. Homographs & TTS trap words — evergreen bank scan

Scan of 1,620 evergreen atoms (broad candidate list): **813** token hits; many are low-risk in context (`use`, `does`, `reset`). **High-risk for wrong pronunciation** in this bank:

| Word | Hits (approx) | Failure mode | Prefer rewrite |
|------|---------------|--------------|----------------|
| **live** | 21 | `/laɪv/` vs `/lɪv/` | “live in your body” → keep *liv*; “a live session” → “a real-time session” / “happening now” |
| **read** | 9 | present `/riːd/` vs past `/rɛd/` | “read it out loud” (present) → “say it out loud” / “speak it aloud”; past → “you already looked at” |
| **close** | 9 | verb `/kloʊz/` vs adj `/kloʊs/` | “close the loop” (verb) usually OK; “a close friend” → “a trusted friend” if misread |
| **project** | 18 | noun vs verb | “not a project that…” (noun) usually OK; verb “project confidence” → “show confidence” |
| **separate** | 9 | verb vs adj | “separate it from” (verb) → “set it apart from” if mis-stressed |
| **minute** | 30 | usually fine in “two-minute” | If misread as /maɪˈnjuːt/: “two minutes of” |
| **perfect** | 18 | usually adj OK | rare verb “perfect the habit” → “refine the habit” |
| **lead / wind / tear / wound / bass / bow** | low/absent in bank | classic traps | keep on watchlist for weekly delta atoms |

**Do not** naively string-replace `use`/`does`/`reset` — high false-positive rate.

Overlay implementation: phrase-level / regex rules in `config/tts/social_media_tts_text_prep.yaml` (apply before synth; SSOT atoms stay unchanged unless a separate copy-edit wave is approved).

---

## 6. Other plain-text TTS best practices (for this bank)

1. **Expand speakables:** `RN` → `R N` or `nurse`; `Gen Z` → `Gen Zee` if misread; avoid raw URLs.
2. **Numbers:** prefer words for small counts in hooks (“three breaths”); keep digits only when clearly ordinal/list.
3. **Colons:** CosyVoice often rushes past `:`. Prefer `.` after the setup clause.
4. **Quotes:** strip decorative quotes around phrases; TTS may say “quote”.
5. **One voice, many scripts:** gender map is stable; all quality work is on the text prep pass.
6. **Listen bar:** stock male/female smoke on **prepped** text beats unprepped + param-mod every time (operator evidence).

---

## 7. Pipeline implications (Lane 2 restart)

```
atom.text (SSOT)
    → text_prep.apply(rules)     # NEW — punctuation + homograph rewrites
    → CosyVoice /api/v1/tts      # speaker = english_male|english_female only
    → ffmpeg wav→mp3
    → R2 + MANIFEST.tsv
```

- **Discard** modulated bank (`social_media/voice_bank/20260719/` rows from param era, or re-key run id `20260719b`).
- **Do not** pass pace/warmth/pitch into CosyVoice for this product.
- Register text-prep as canonical config; driver must call it.

---

## 8. Open operator questions

1. **Q-SMV-G01:** Confirm gender map (corp=male, gen_z=female, RN=female) or flip corporate to female?
2. **Q-SMV-G02:** How aggressive on punctuation — mild (extra commas) vs strong (short punchy sentences)?
3. **Q-SMV-G03:** Text prep writes a **sidecar speakable field** vs mutates synth input only (recommended: synth-input only; SSOT untouched)?

**Recommended defaults:** G01 as table above · G02 mild-to-medium · G03 synth-input only.

---

## Provenance

```
research: operator listen 2026-07-19; docs/VOICE_PERSONA_TOPIC_RESEARCH.md;
          specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md (SSML lane — diverge);
          FreeTTS / vibecasting / Smallest AI / Inworld TTS plain-text practices
documents: config/tts/social_media_voice_matrix.yaml (gender-only rewrite);
           config/tts/social_media_tts_text_prep.yaml (NEW)
inventory: EXTENDS research; REDUCES failed param-modulation contract
```
