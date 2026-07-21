# Recommended Taxonomy — Caption/Atom → Storyblocks Query Compiler

**Lane:** 01 → input for Lane 02  
**Date:** 2026-07-20  
**Method name:** Controlled Taxonomy Query Compiler (CTQC)  
**Authority research:** `RESEARCH_REPORT.md`  
**Atom schema fields:** `topic`, `persona`, `hook_family`, `tone`, `text`  
(`docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md`)

---

## 0. Design principles

1. **Fields first, caption second.** Never send full caption prose as `keywords`.
2. **AND hard anchors** via `required_keywords`; **exclude traps** via `filtered_keywords`.
3. **Beat role** sets duration window; **mood_register** (from topic) sets audio recipe.
4. **Persona** only modulates workplace/home/clinical visual flavor — does not invent new topics.
5. **Runnable offline:** examples below need no Storyblocks keys.

---

## 1. Machine-readable mapping tables (Lane 02 YAML shape)

### 1.1 `topic` → `mood_register` + base visual keywords

Mirrors `config/social/media_bank_sizing_20260719.yaml` mood clusters; extends with stockable visuals.

```yaml
# proposed: config/social/storyblocks_query_taxonomy.yaml  (Lane 02 implements)
topic_to_mood_register:
  anxiety: tense_anxious
  financial_anxiety: tense_anxious
  financial_stress: tense_anxious
  social_anxiety: tense_anxious
  sleep_anxiety: tense_anxious
  overthinking: tense_anxious
  depression: heavy_low
  grief: heavy_low
  burnout: heavy_low
  compassion_fatigue: heavy_low
  somatic_healing: grounding_somatic
  boundaries: grounding_somatic
  courage: empowering_courage
  self_worth: empowering_courage
  imposter_syndrome: empowering_courage

topic_visual_keywords:
  anxiety:
    primary: [anxious, nervous, tense, worried]
    secondary: [breathing, pacing, overthinking, racing thoughts]
    objects: [phone, laptop, clock, heartbeat]
    filtered: [party, festival, concert, parade, celebration, comedy]
  burnout:
    primary: [exhausted, tired, burnout, drained]
    secondary: [late night, overworked, fatigue]
    objects: [laptop, desk, coffee, office]
    filtered: [gym motivation, party, vacation montage]
  boundaries:
    primary: [boundary, conversation, assertive, pause]
    secondary: [serious discussion, colleagues, listening]
    objects: [meeting room, doorway, calendar]
    filtered: [hug montage, wedding, party]
  social_anxiety:
    primary: [nervous, crowd, shy, awkward]
    secondary: [public space, subway, waiting room]
    objects: [crowd, elevator, hallway]
    filtered: [concert, festival, cheering, parade]
  depression:
    primary: [lonely, somber, quiet, withdrawn]
    secondary: [rain window, empty room, slow morning]
    objects: [window, bed, rain]
    filtered: [party, festival, extreme sports]
  grief:
    primary: [grief, mourning, remembrance, quiet sadness]
    secondary: [memorial, alone, reflection]
    objects: [photo frame, candle, empty chair]
    filtered: [party, comedy, nightclub]
  overthinking:
    primary: [thinking, worried, restless, insomnia]
    secondary: [night thoughts, decision paralysis]
    objects: [notebook, clock, phone screen]
    filtered: [party, festival]
  courage:
    primary: [confident, determined, brave, resolve]
    secondary: [standing tall, first step]
    objects: [sunrise, mountain path, open door]
    filtered: [aggression, fight, war]
  self_worth:
    primary: [self care, calm confidence, mirror]
    secondary: [gentle strength, grounded]
    objects: [mirror, journal, plant]
    filtered: [luxury flex, party]
  imposter_syndrome:
    primary: [workplace, doubt, presentation nerves]
    secondary: [meeting, laptop, office]
    objects: [conference room, badge, desk]
    filtered: [party, festival]
  sleep_anxiety:
    primary: [insomnia, sleepless, night anxiety]
    secondary: [dark bedroom, clock 3am]
    objects: [bed, alarm clock, moonlight]
    filtered: [party, nightclub dancing]
  somatic_healing:
    primary: [breathing, body awareness, grounding]
    secondary: [stretch, calm hands, nature walk]
    objects: [hands, leaves, water]
    filtered: [hospital gore, surgery closeup]
  compassion_fatigue:
    primary: [caregiver tired, emotional exhaustion]
    secondary: [healthcare worker pause, quiet break]
    objects: [scrubs, break room, coffee]
    filtered: [party, festival]
  financial_anxiety:
    primary: [bills, budget stress, money worry]
    secondary: [calculator, receipts, tense at desk]
    objects: [calculator, laptop, paperwork]
    filtered: [luxury cars, casino]
  financial_stress:
    primary: [money stress, unpaid bills, scarcity]
    secondary: [budgeting, worried adult]
    objects: [wallet, statements, phone banking]
    filtered: [yacht, luxury flex]
```

### 1.2 `hook_family` → visual emphasis weights

```yaml
hook_family_weights:
  practical_tool:
    prefer_objects: 1.4
    prefer_faces: 0.8
    keyword_boost: [hands, checklist, tool, notebook, timer]
  contrarian_reframe:
    prefer_faces: 1.2
    prefer_objects: 1.0
    keyword_boost: [pause, rethink, crossroads, unexpected]
  felt_recognition:
    prefer_faces: 1.5
    prefer_objects: 0.7
    keyword_boost: [close up, emotion, expression, alone]
  story_case:
    prefer_faces: 1.1
    prefer_objects: 1.1
    keyword_boost: [workplace, daily life, commute]
  myth_bust:
    prefer_faces: 1.0
    prefer_objects: 1.2
    keyword_boost: [contrast, before after, myth]
  # default for unknown hook_family:
  _default:
    prefer_faces: 1.0
    prefer_objects: 1.0
    keyword_boost: []
```

### 1.3 `tone` → style filters

```yaml
tone_filters:
  calm professional:
    required_any: [office, workplace, adult]
    filtered_extra: [teen party, nightclub, extreme sport]
    quality: HD
    safe_search: true
  warm companion:
    keyword_boost: [soft light, gentle, home]
    filtered_extra: [harsh neon, horror]
  direct coach:
    keyword_boost: [focused, determined, clear]
    filtered_extra: [chaos party]
  soft clinical:
    keyword_boost: [calm, therapy adjacent, quiet room]
    filtered_extra: [hospital emergency, blood]
  _default:
    filtered_extra: [gore, explicit, weapon]
```

### 1.4 `persona` → scene flavor (optional secondary)

```yaml
persona_scene_flavor:
  corporate_managers: [office, meeting, laptop, desk, commute]
  healthcare_rns: [hospital corridor, scrubs, break room, night shift]
  working_parents: [home kitchen, morning rush, school run]
  gen_z_professionals: [open office, phone, coworking]
  educators: [classroom, desk grading, hallway]
  nyc_executives: [city commute, skyline window, elevator]
  _default: [everyday adult, indoor]
```

### 1.5 Beat role → duration + clip policy

```yaml
beat_role_query:
  hook:
    target_s: 3.0
    max_duration: 8
    min_duration: 2
    prefer: short_tagged_snippet
  beat:
    target_s: 5.0
    max_duration: 12
    min_duration: 3
    prefer: short_tagged_snippet
  value:
    target_s: 8.0
    max_duration: 20
    min_duration: 6
    prefer: longer_single_clip
  endcard:
    target_s: 2.0
    max_duration: 6
    min_duration: 1
    prefer: short_tagged_or_brand_plate
```

### 1.6 Audio: `mood_register` → Storyblocks audio params

```yaml
mood_register_audio:
  tense_anxious:
    keywords: [tense, anxious, suspense, pulse, underscore]
    content_type: music
    min_bpm: 90
    max_bpm: 130
    has_vocals: false
    filtered_keywords: [comedy, christmas, kids]
  heavy_low:
    keywords: [melancholy, somber, ambient, slow, reflective]
    content_type: music
    max_bpm: 90
    has_vocals: false
    filtered_keywords: [upbeat, party, edm drop]
  grounding_somatic:
    keywords: [calm, ambient, peaceful, breath, soft piano]
    content_type: music
    max_bpm: 100
    has_vocals: false
    filtered_keywords: [aggressive, horror, trap]
  empowering_courage:
    keywords: [uplifting, inspiring, hopeful, resolve, warm]
    content_type: music
    min_bpm: 100
    max_bpm: 140
    has_vocals: false
    filtered_keywords: [aggressive, war drums, horror]
```

### 1.7 Query compile algorithm (pseudocode for Lane 02)

```python
def compile_storyblocks_video_query(atom: dict, beat_role: str) -> dict:
    topic = atom["topic"]
    persona = atom.get("persona") or "_default"
    hook = atom.get("hook_family") or "_default"
    tone = atom.get("tone") or "_default"
    tv = topic_visual_keywords[topic]
    hw = hook_family_weights.get(hook, hook_family_weights["_default"])
    tf = tone_filters.get(tone, tone_filters["_default"])
    br = beat_role_query[beat_role]
    flavor = persona_scene_flavor.get(persona, persona_scene_flavor["_default"])

    keywords = unique(
        tv["primary"][:3]
        + hw["keyword_boost"][:2]
        + flavor[:2]
        + tv["objects"][:2]
        + extract_concrete_nouns(atom.get("text", ""), max_n=2)  # allowlist nouns only
    )
    required = [tv["primary"][0]] + ([flavor[0]] if "office" in flavor or "workplace" in flavor else [])
    filtered = tv["filtered"] + tf.get("filtered_extra", [])

    return {
        "keywords": ",".join(keywords),
        "required_keywords": ",".join(required[:2]),
        "filtered_keywords": ",".join(filtered),
        "content_type": "footage,motionbackgrounds",
        "max_duration": br["max_duration"],
        "min_duration": br["min_duration"],
        "orientation": "vertical",  # shorts-native; override per surface
        "safe_search": "true",
        "has_talent_released": "true",  # prefer for people topics
        "sort_by": "most_relevant",
        "extended": "keywords,hasTalentReleased,hasPropertyReleased,durationMs,hasAudio,description",
        "results_per_page": 20,
    }
```

### 1.8 Deterministic rank score

```text
score =
  3.0 * |token_overlap(title+keywords, compiled.primary)|
+ 1.5 * |token_overlap(title+keywords, compiled.objects ∪ hook_boost)|
+ 1.0 * duration_proximity(duration, target_s)   # 1.0 if within 2s else decay
+ 1.0 * (has_talent_released if people_primary else 0.5)
+ 0.5 * orientation_match(vertical)
- 5.0 * any(filtered_token in title+keywords)
+ 0.0..2.0 * optional_local_clip_cosine(thumbnail, " ".join(primary+objects))
```

Pick argmax; on tie prefer shorter clip for hook/beat/endcard, longer for value.

---

## 2. Worked examples (pilot — 3 real atoms)

Pulled from `SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl` on 2026-07-20.

### Example A — anxiety × practical_tool × hook

| Field | Value |
|-------|-------|
| `atom_id` | `EVG-ENUS-ANXI-CORP-B-01` |
| `topic` | `anxiety` |
| `persona` | `corporate_managers` |
| `hook_family` | `practical_tool` |
| `tone` | `calm professional` |
| `text` | That is the hinge: once the signal is named, the next atom should offer one action instead of another explanation. |

**Derived:** `mood_register=tense_anxious`; caption nouns kept: `signal`, `action` (low visual value → mostly dropped).

**Compiled video query (`beat_role=hook`):**

```text
GET /api/v2/videos/search
  keywords=anxious,nervous,tense,hands,checklist,office,meeting,phone,laptop
  required_keywords=anxious,office
  filtered_keywords=party,festival,concert,parade,celebration,comedy,teen party,nightclub,extreme sport
  content_type=footage,motionbackgrounds
  max_duration=8
  min_duration=2
  orientation=vertical
  safe_search=true
  has_talent_released=true
  sort_by=most_relevant
  extended=keywords,hasTalentReleased,hasPropertyReleased,durationMs,hasAudio,description
  results_per_page=20
```

**Audio bed (`mood_register=tense_anxious`):**

```text
GET /api/v2/audio/search
  keywords=tense,anxious,suspense,pulse,underscore
  content_type=music
  min_bpm=90
  max_bpm=130
  has_vocals=false
  filtered_keywords=comedy,christmas,kids
  extended=moods,genres,bpm,keywords,pro
```

**Human review expectation:** Prefer office/phone anxiety over concert crowds (filtered). Rank titles containing nervous/anxious/office higher.

---

### Example B — burnout × practical_tool × value

| Field | Value |
|-------|-------|
| `atom_id` | `EVG-ENUS-BURN-CORP-B-01` |
| `topic` | `burnout` |
| `persona` | `corporate_managers` |
| `hook_family` | `practical_tool` |
| `tone` | `calm professional` |
| `text` | That is the hinge: once the signal is named, the next atom should offer one action instead of another explanation. |

**Derived:** `mood_register=heavy_low`; `beat_role=value` → longer single clip.

**Compiled video query (`beat_role=value`):**

```text
GET /api/v2/videos/search
  keywords=exhausted,tired,burnout,hands,checklist,office,meeting,laptop,desk
  required_keywords=exhausted,office
  filtered_keywords=gym motivation,party,vacation montage,teen party,nightclub,extreme sport
  content_type=footage,motionbackgrounds
  max_duration=20
  min_duration=6
  orientation=vertical
  safe_search=true
  has_talent_released=true
  sort_by=most_relevant
  extended=keywords,hasTalentReleased,hasPropertyReleased,durationMs,hasAudio,description
```

**Audio bed (`heavy_low`):**

```text
keywords=melancholy,somber,ambient,slow,reflective
content_type=music
max_bpm=90
has_vocals=false
```

**Human review expectation:** Continuous desk/fatigue shot 6–15s; avoid jump-cut montage inside the value beat.

---

### Example C — boundaries × contrarian_reframe × beat

| Field | Value |
|-------|-------|
| `atom_id` | `EVG-ENUS-BOUN-CORP-HC-01` |
| `topic` | `boundaries` |
| `persona` | `corporate_managers` |
| `hook_family` | `contrarian_reframe` |
| `tone` | `calm professional` |
| `text` | corporate managers: assuming a clear no will cost you the relationship is not the whole story. |

**Derived:** `mood_register=grounding_somatic`; caption nouns: `managers`, `relationship` → weak stock terms; use taxonomy conversation/meeting instead.

**Compiled video query (`beat_role=beat`):**

```text
GET /api/v2/videos/search
  keywords=boundary,conversation,assertive,pause,rethink,crossroads,office,meeting,meeting room,doorway
  required_keywords=conversation,office
  filtered_keywords=hug montage,wedding,party,teen party,nightclub,extreme sport
  content_type=footage,motionbackgrounds
  max_duration=12
  min_duration=3
  orientation=vertical
  safe_search=true
  has_talent_released=true
  sort_by=most_relevant
  extended=keywords,hasTalentReleased,hasPropertyReleased,durationMs,hasAudio,description
```

**Audio bed (`grounding_somatic`):**

```text
keywords=calm,ambient,peaceful,breath,soft piano
content_type=music
max_bpm=100
has_vocals=false
```

**Human review expectation:** Two adults in a serious workplace conversation; exclude celebration/hug stock.

---

## 3. Fallback: existing Pexels bank

If Storyblocks search returns `< 3` candidates after filtering, or MAU headroom is tight:

1. Query local/topic plates under `artifacts/stock_image_bank/` / curated winners for stills.
2. For video, keep Pexels path in `build_video_snippet_bank.py` as provider=`pexels` until Storyblocks confirm path is EXECUTED-REAL.
3. Same CTQC keyword set can feed Pexels `query` string (space-separated primary+objects).

---

## 4. Lane 02 implementation checklist

- [ ] Add `config/social/storyblocks_query_taxonomy.yaml` from §1 tables
- [ ] Implement `compile_storyblocks_video_query` + ranker (no paid vision API)
- [ ] Extend `StoryblocksAPIClient.search_videos` kwargs; add `search_audio`
- [ ] Wire only through `confirm_download` for HD; search/preview for ranking
- [ ] Unit tests: 3 examples above → exact expected keyword sets (golden strings)
- [ ] Document CLIP optional path with `embedding_purpose=selection_assist` wall-off

---

## 5. Taxonomy recommendation summary (for handoff greppers)

**RECOMMENDED_TAXONOMY:** CTQC — map `{topic, persona, hook_family, tone, beat_role}` → weighted Storyblocks `keywords` + `required_keywords` + `filtered_keywords` + duration window; rank by token overlap + duration + release flags (+ optional local CLIP on thumbnails). Do not use raw caption as search string.
