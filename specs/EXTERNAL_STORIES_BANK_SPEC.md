# External Stories Bank — Spec (Pearl_Research)

**Authority:** Pearl_Research  
**Status:** Wave 1 seeded — `unwired` / `KNOWN_UNWIRED`  
**Extends:** Accent family (quotes · evidence · wisdom essence · author commentary · **external stories**)  
**Created:** 2026-07-07  
**Bank path:** `SOURCE_OF_TRUTH/accent_banks/external_stories/`

---

## Rule 0 — Integrity Boundary (non-negotiable)

Our authors are **pen-name / EI personas** (`config/author_registry.yaml`, `docs/PEN_NAME_AUTHOR_SYSTEM.md`). They have **no real biography, no clients, no case history**. Invented role anchors in `assets/authors/*/bio.yaml` are crafted fiction for marketplace identity — not verifiable life stories.

Therefore this bank:

1. **Zero fabricated "true" stories** — no invented historical events, no fake NPR anecdotes, no apocryphal quotes dressed as fact.
2. **Zero claimed client cases** — the "my client Sarah…" authority slot is **permanently replaced** by cited external true stories.
3. **Zero invented author history** — author personal narrative is allowed only in the **author-commentary lane** as observed witness-register commentary, never as claimed biography.
4. Every entry is exactly one of:
   - **(a)** A verifiable real event or person with citation.
   - **(b)** A cultural work referenced *as a work* ("In the film…", "In the myth of…").
   - **(c)** A broadcast / interview story with source + attribution (Moth, Fresh Air, StoryCorps, TED, This American Life).

**Relationship to existing story systems (do not conflate):**

| Layer | System | Role |
|-------|--------|------|
| Reader-mirror fiction | `story_atoms/`, `atoms/`, character rosters (Priya, Marcus, Maya) | Spine — **untouched** |
| Author voice | Author-commentary accent lane | Witness-register only |
| Client authority | **This bank** | Cited true external stories |
| Science authority | Evidence bank | Findings + documented cases |
| Tradition texture | Wisdom essence bank | Secular distillation |

---

## 1. Entry Schema

```yaml
story_id: ext_{topic}_{slug}_v01
type: historical | mythic | film | book | sports | business | pop_culture | true_life_broadcast
emotional_shape: cautionary | breakthrough | contrast | humor | tearjerker | underdog | quiet-recognition
story: |                                   # 100–250 words, golden-ch1 register
source: "Primary source label"
citation: "Full citation string"
rights_class: public_domain_retelling | verified_facts_only | nominative_reference | paraphrase_attributed
topic_keys: [anxiety, ...]
doctrine_keys: ["COMPOSITE_DOCTRINE v01", ...]
locale_fit: [universal] | [en_US] | [zh_CN] | ...
secular_safe: true | false
persona_fit: [...]                         # optional planner hint
position_fit: supports REFLECTION | supports PIVOT | supports TAKEAWAY | supports HOOK
sensitivity_notes: ""
```

### Craft rule (human center)

Every story must reveal the wound, expose the pattern, or demonstrate the transformation. Decoration without a human center is rejected.

---

## 2. Rights Policy (per class)

| Class | Policy |
|-------|--------|
| `historical` / `mythic` / public-domain figures | Free retelling; cite primary source |
| Living people / active business | Verified public facts only; **no invented interiority** |
| `film` / `book` | Short nominative reference + insight; **never plot-length retellings** |
| `true_life_broadcast` | Paraphrase-with-attribution default; short quotes only when cited |
| Aggregator-sourced anecdotes | **Banned** |
| Misattribution | Same verification discipline as quote bank |

### Operator defaults (Q-EXT)

| ID | Question | Default |
|----|----------|---------|
| Q-EXT-01 | Default story-mix for flagship (`stillness_press`) | `practical_credible` with wisdom flair |
| Q-EXT-02 | Living-celebrity stories? | Sparingly; verified-facts-only; prefer completed careers |
| Q-EXT-03 | Broadcast sources beyond Moth / Fresh Air | StoryCorps, This American Life, TED |

---

## 3. Locale-Fit Clusters (11 — quote-bank pattern)

Wave 1: `universal`, `en_US`, `zh_CN`, `zh_TW`, `ja_JP`.  
zh_CN exclusions mirror quote bank (Western political icons, Dalai Lama, devotional religious one-liners in secular brands).

---

## 4. Story-Mix Profiles (planner knob)

See `config/authoring/story_mix_profiles.yaml`. Profiles: `practical_credible` (Atomic-Habits-like), `intimate_voice` (Badass-like), `timeless_wisdom` (Power-of-Now-like).

Dosage: 2–4 typical per book, max 6, reuse cap ≤3 per brand per quarter, shingle-gate scope.

---

## 5. Emotional-Range Placement

| `emotional_shape` | Recommended beat |
|-------------------|------------------|
| `cautionary` | near PIVOT / cost |
| `humor` | after heavy doctrine |
| `tearjerker` | mechanism-cost or turning |
| `breakthrough` | near TAKEAWAY |
| `contrast` | REFLECTION or early PIVOT |
| `underdog` | HOOK or REFLECTION |
| `quiet-recognition` | REFLECTION |

---

## 6. Wiring Status

**`status: unwired`** — `KNOWN_UNWIRED: accent_banks/external_stories/`. Zero pipeline wiring in Wave 1.

---

## 7. Wave Plan

| Wave | Topics | Clusters | Target |
|------|--------|----------|--------|
| 1 | anxiety, burnout, overthinking, imposter_syndrome, financial_anxiety | universal, en_US, zh_CN, zh_TW, ja_JP | 15–20/topic |
| 2 | boundaries, social_anxiety, self_worth, sleep_anxiety, grief, depression | + EU | 12–15/topic |
| 3 | remaining canonical 15 | all 11 | fill |
