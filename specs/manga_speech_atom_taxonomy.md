# Manga Speech Atom Taxonomy
**Version:** 1.0.0  
**Spec owner:** Pearl_Architect  
**Schema source:** `config/source_of_truth/manga_speech_atoms/schema.yaml`  
**Last updated:** 2026-04-17

---

## 1. Taxonomy Overview

A speech atom is the minimal self-describing unit of manga dialogue. Where the existing pipeline stores `panel.dialogue` as a plain string list with no rendering intent, speech atoms encode the full rendering contract: visual treatment, emotional weight, anti-repetition constraints, and EI system linkage.

### 1.1 Dimension Definitions

Each atom sits at the intersection of five primary dimensions:

| Dimension | Values |
|---|---|
| `genre` | shonen, shojo, seinen, josei, kodomomuke, isekai, horror, sports, slice_of_life, bl_gl, mecha |
| `archetype` | protagonist, antagonist, mentor, rival, love_interest, comic_relief, narrator, mysterious_stranger, ally, villain, kuudere, tsundere |
| `emotion` | determination, fear, love, anger, surprise, grief, joy, confusion, awe, despair, resolve, embarrassment, longing, contempt, hope |
| `intensity` | whisper, calm, normal, excited, shouting, screaming, internal |
| `bubble_style` | round_normal, spiky_emphasis, cloud_thought, square_narration, whisper_dashed, scream_ultra, electronic_sharp, drip_horror, shojo_soft |

These dimensions are **not all independently combinable.** Section 7 contains the full valid matrix. The most important structural constraint is this: **`bubble_style` is partially redundant with `intensity` and `genre`** — selecting an atom already encodes most visual choices. Downstream renderers use `bubble_style`, `font_override`, and `tail_style` directly; they do not recompute these from genre + intensity.

### 1.2 What Makes an Atom Different from a Template String

A plain template string answers: "what does the character say?"  
A speech atom answers all of:

- What does the character say? (`text_template`, `variants`)
- How does the word balloon look? (`bubble_style`, `tail_style`, `position_hint`)
- How does the font treat the words? (`font_override`, `word_count_target`)
- Is there a sound effect beside it? (`sfx_companion`)
- What cannot come right after it without tonal collapse? (`forbidden_after`)
- How long before this beat can appear again? (`cooldown_chapters`)
- Which therapeutic emotional layer does this serve? (`ei_emotion_mapping`)

### 1.3 Invalid Combinations

Not every combination of the five dimensions produces a coherent atom. Invalid combinations fall into three categories:

**Category A — Structural impossibility:**  
`bubble_style: cloud_thought` requires `intensity: internal` or `intensity: whisper`. A shouting thought bubble is a contradiction in manga grammar.  
`bubble_style: electronic_sharp` is reserved for mechanical/digital speech (mecha, AI characters). Using it for organic characters breaks reading contracts.  
`bubble_style: drip_horror` is restricted to the `horror` genre and characters in extreme distress. It must not appear in shojo or kodomomuke.

**Category B — Archetype/intensity mismatch:**  
`archetype: narrator` cannot use `intensity: shouting` or `intensity: screaming`. Narrators are always external, never vocally intense.  
`archetype: mentor` with `intensity: screaming` is almost always wrong — the exception is grief that breaks composure, which should be treated as a one-time `cooldown_chapters: 5` atom.  
`archetype: kuudere` with `intensity: excited` or `shouting` collapses the archetype's defining trait (emotional flatness reads as suppressed intensity, not absence of it).

**Category C — Genre/emotion mismatch:**  
`genre: kodomomuke` prohibits `emotion: despair`, `contempt`, or `grief` above `intensity: normal`. The genre's audience contract requires resolution or reframing within the same panel sequence.  
`genre: horror` very rarely has `emotion: joy` unless it is ironic or wrongly-directed — when used, it requires `bubble_style: drip_horror` or `round_normal` with explicit `sfx_companion: null` to signal unease.  
`genre: sports` rarely has `archetype: narrator` with `emotion: grief` that is not sports-outcome-adjacent. If the grief is personal (non-sport), use `genre: slice_of_life` atoms in the same panel sequence.

---

## 2. Anti-Repetition System

Manga dialogue fatigue is real and measurable: when the same tonal beat — not the same words, but the same *feeling* — appears too close together, readers disengage. The atom system has two interlocking mechanisms.

### 2.1 `forbidden_after`

`forbidden_after` is a list of `atom_id` values that **must not immediately follow this atom** within the same chapter. This is a directional constraint: atom A forbids atom B after it, but atom B may not symmetrically forbid atom A.

The check operates at **panel sequence level**, not page level. Two atoms in consecutive panels within the same chapter trigger the constraint. Two atoms in consecutive chapters do not (that is governed by `cooldown_chapters`).

**Common patterns to prevent:**

| Pattern | Problem |
|---|---|
| Two shouting determination atoms back-to-back | Emotional saturation; the second lands flat |
| Two villain contempt monologue atoms in same chapter | Reader begins summarizing instead of reading |
| Tsundere embarrassment immediately after tsundere love | Collapses the push-pull arc within a single chapter |
| Cold narrator followed immediately by warm narrator | Tonal whiplash without visual transition break |

### 2.2 `cooldown_chapters`

`cooldown_chapters: N` means the same `atom_id` (or any atom sharing the same `genre + archetype + emotion + intensity` signature, i.e., atoms that are functional siblings) must not appear in chapter `n` through chapter `n + N`.

A `cooldown_chapters: 0` value means the atom is considered tonally neutral and repeatable (the silence atom, ellipsis beats, minor acknowledgments).

The algorithm for enforcement is described fully in Section 5.

### 2.3 Combined Effect

The two mechanisms operate at different scopes:

- `forbidden_after` = **local** (within chapter, panel adjacency)
- `cooldown_chapters` = **global** (across chapter sequence)

An atom can pass the `cooldown_chapters` check but fail `forbidden_after` (it has been long enough since the last use, but the *immediately preceding panel* used a forbidden sibling). Both checks must pass for an atom to be selectable.

---

## 3. Dialogue Sequence Composition

Speech atoms are building blocks, not complete scenes. The pipeline must compose them into valid sequences: call-response pairs, monologue chains, and group conversations.

### 3.1 Call-Response Pairs

The canonical pattern is:

```
atom_A  →  atom_B
speaker_1 (initiating)   speaker_2 (responding)
```

Valid call-response rules:

1. **Intensity should not jump more than two steps.** If atom_A is `whisper`, atom_B should be `calm`, `normal`, or at most `excited` — not `screaming`. A two-step jump requires a visual transition panel between them (no dialogue, silence beat).
2. **`emotion` in atom_B should be reactive to atom_A's emotion.** The valid reaction matrix:

| atom_A emotion | Valid atom_B emotions |
|---|---|
| determination | contempt, respect/resolve, fear, anger |
| love | love (reciprocation), embarrassment, confusion, longing |
| contempt | anger, despair, determination, contempt (escalation) |
| grief | awe (witnessing), resolve (companion), grief (shared) |
| anger | fear, anger (counter), resolve, contempt |
| hope | hope (shared), fear (cautious), love |
| despair | resolve (companion), grief (shared), awe (witness) |

3. **`archetype` roles must be socially coherent.** A `narrator` never responds in a call-response pair. `mysterious_stranger` never initiates — they always respond or interject.

### 3.2 Monologue Chains

A monologue chain is three or more consecutive atoms from the same archetype (villain monologue, mentor wisdom cascade, protagonist inner spiral). Rules:

1. Maximum chain length is **4 atoms per character per chapter**. Beyond this, the sequence should be broken by a visual beat (action panel, reaction shot, silence).
2. Intensity arc within a chain must follow one of two patterns:
   - **Escalation:** `calm → normal → excited → shouting` (or subset)
   - **Fade-in:** `internal → whisper → calm → normal` (revelation pattern common in seinen)
   - **Flat intensity** (same intensity throughout) is valid only for `narrator` archetype.
3. Within a chain, all atoms must share the same `archetype`. Switching archetypes mid-chain breaks the monologue and starts a new sequence type.

### 3.3 Group Conversations

Three or more archetypes speaking within a chapter segment. Rules:

1. No single archetype should hold more than 40% of the atom slots in a group conversation.
2. The conversation must have an **anchor archetype** — one character whose atoms have the highest `word_count_target` average. This is the character driving the scene.
3. `comic_relief` archetype atoms may be inserted between high-intensity atoms to relieve pressure, but no two `comic_relief` atoms may appear within the same 5-panel window.

---

## 4. Integration with `ChapterContract.emotional_job`

Every chapter in the Phoenix Omega pipeline has a `ChapterContract` with an `emotional_job` field. This field is a string drawn from the EI V2 taxonomy: `shame`, `overwhelm`, `grief`, `false_alarm`, `spiral`, `watcher`, `comparison`.

### 4.1 Mapping Protocol

Each atom carries:

```yaml
ei_emotion_mapping:
  primary: <ei_emotion>
  intensity_modifier: low | medium | high
```

When the pipeline selects atoms for a chapter with `emotional_job: grief`, it should **prefer** atoms where `ei_emotion_mapping.primary == grief`. However, the mix should not be monolithic. The recommended distribution is:

| `ei_emotion_mapping.primary` | Target proportion |
|---|---|
| Matches `emotional_job` | 50–65% |
| Contextually adjacent (see table below) | 20–35% |
| Contrast / counterpoint | 5–15% |

**Contextually adjacent EI emotions:**

| `emotional_job` | Adjacent EI emotions |
|---|---|
| shame | comparison, overwhelm |
| overwhelm | spiral, false_alarm |
| grief | watcher, shame |
| false_alarm | overwhelm, comparison |
| spiral | grief, overwhelm |
| watcher | grief, shame |
| comparison | shame, false_alarm |

### 4.2 `intensity_modifier` and Chapter Pacing

The `intensity_modifier` (low/medium/high) maps to chapter pacing position:

- **low** — setup panels, establishing dialogue, chapter opening
- **medium** — rising action, character interactions, mid-chapter
- **high** — climax panels, confrontation, chapter closing beat

The pipeline should ensure at least one `high` intensity_modifier atom appears in the final third of a chapter's atom sequence, and the chapter should not open with a `high` intensity_modifier atom unless a visual cold-open justifies it.

---

## 5. Deterministic Selection Algorithm

The pipeline uses a `hashlib.sha256`-based deterministic integer as its selection primitive, following the existing pattern in `phoenix_v4/manga/series/story_architect.py`:

```python
import hashlib

def _deterministic_int(seed: str, max_val: int) -> int:
    """Stable integer from a seed string. Same input always produces same output."""
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % max_val
```

### 5.1 Atom Selection

To select which atom to use for a given panel:

```python
def select_atom(
    candidate_atoms: list[dict],
    series_id: str,
    chapter_id: str,
    panel_id: str,
    *,
    cooldown_history: dict[str, int],   # atom_id -> last chapter index it was used
    last_atom_id: str | None,           # atom used in immediately preceding panel
    current_chapter_index: int,
) -> dict:
    """
    Deterministically select an atom from candidates, respecting anti-repetition rules.
    Returns the selected atom dict.
    """
    seed = f"{series_id}:{chapter_id}:{panel_id}"

    eligible = [
        a for a in candidate_atoms
        if _passes_cooldown(a, cooldown_history, current_chapter_index)
        and _passes_forbidden_after(a, last_atom_id)
    ]

    if not eligible:
        # Fallback: relax forbidden_after, keep cooldown
        eligible = [
            a for a in candidate_atoms
            if _passes_cooldown(a, cooldown_history, current_chapter_index)
        ]

    if not eligible:
        # Final fallback: use full candidate list
        eligible = candidate_atoms

    idx = _deterministic_int(seed, len(eligible))
    return eligible[idx]


def _passes_cooldown(atom: dict, history: dict[str, int], current_idx: int) -> bool:
    cooldown = atom.get("cooldown_chapters", 0)
    if cooldown == 0:
        return True
    last_used = history.get(atom["atom_id"])
    if last_used is None:
        return True
    return (current_idx - last_used) >= cooldown


def _passes_forbidden_after(atom: dict, last_atom_id: str | None) -> bool:
    if last_atom_id is None:
        return True
    return last_atom_id not in atom.get("forbidden_after", [])
```

### 5.2 Variant Selection

Once an atom is selected, the specific text to render is chosen from `variants` (or `text_template` if variants list is shorter than expected) using the same deterministic pattern with a panel-specific sub-seed:

```python
def select_variant(atom: dict, series_id: str, chapter_id: str, panel_id: str) -> str:
    all_texts = [atom["text_template"]] + atom.get("variants", [])
    seed = f"{series_id}:{chapter_id}:{panel_id}:variant"
    idx = _deterministic_int(seed, len(all_texts))
    return all_texts[idx]
```

This guarantees that:
- The same `(series_id, chapter_id, panel_id)` triple always selects the same atom AND the same variant.
- Different series with identical chapter/panel IDs diverge because `series_id` is part of the seed.
- Re-runs without state change are fully reproducible.

### 5.3 Slot Filling

Text templates may contain slots: `{stake}`, `{name}`, `{place}`, `{opponent}`. These are filled from the chapter's context variables (from `ChapterContract` or the chapter script metadata). If a slot variable is not defined, the slot should be replaced with the archetype's default value from the series bible, not left as a raw `{variable}` string.

---

## 6. Genre Authenticity Rules

Genre is not just a tag — it encodes a **reader contract**. Violating the contract breaks immersion more than any individual dialogue choice.

### 6.1 Shōnen vs. Seinen

These two genres are the most commonly confused because both can feature male protagonists in high-stakes conflicts. The difference is philosophical:

**Shōnen** operates on the belief that will can overcome circumstance. The protagonist's emotional journey curves upward even through setbacks. Failure is framed as preparation, not evidence of fundamental inadequacy. The shouting determination atoms in shōnen carry genuine conviction — the text means what it says.

**Seinen** operates on the belief that circumstance is more durable than will. The protagonist's resolve may be genuine but the narrative does not reward it automatically. The "resolve" atoms in seinen tend to be quieter, more private, and often framed by the narrator as insufficient or costly. The character believes; the story does not always confirm the belief.

Operationally:
- Shōnen `determination` atoms use `spiky_emphasis` bubbles and `bold_action` fonts.
- Seinen `resolve` atoms use `square_narration` or `round_normal` bubbles and no font override.
- Shōnen villains state their philosophy to be defeated. Seinen antagonists state their philosophy to be *understood* — and are sometimes right.

### 6.2 Shōjo vs. Josei

**Shōjo** centers on emotional texture and the navigation of social relationships, usually in the register of possibility — love might happen, understanding might arrive, connection is within reach. The bubble styles (`shojo_soft`, `cloud_thought`) are gentler. Dialogue is more interior, more circling.

**Josei** ages this up: the same emotional texture but now weighted by time and consequence. A josei protagonist does not wonder if love is possible — she wonders whether love is worth the specific cost this particular time. The `square_narration` and `italic_internal` voice is more common. Embarrassment atoms appear less; longing and resolve atoms appear more.

### 6.3 Horror

Horror atoms are structurally different from all other genres: they work by **withholding information**. Whisper intensity and dotless tails are default. The `drip_horror` bubble style should be used sparingly — its power depends on scarcity. A chapter that uses `drip_horror` on every horror atom has no `drip_horror`.

The narrator in horror is unusual: it is often more frightened than the characters, or knows more than them. The `square_narration` bubble in horror should feel cold, not authoritative.

### 6.4 Isekai

Isekai protagonists are, canonically, self-inserts observing a strange world. Their authentic register is **meta-awareness** — they notice genre conventions, they comment on logic, they are confused by things that would be obvious to in-world characters. The `confusion` and `awe` atoms for isekai should carry this observational quality. A protagonist who reacts exactly like a native character is not functioning as an isekai protagonist.

### 6.5 Sports

Sports atoms must be physically grounded. The body is always present: muscles, breath, sweat, fatigue, injury. An emotion without physical grounding reads as generic, not sports-genre authentic. `determination_shouting` in sports always has a physical referent in the text or sfx.

---

## 7. Valid Matrix Summary

### 7.1 Genre × Archetype Validity

`Y` = valid, `M` = marginal (requires special justification), `N` = invalid

| | protagonist | antagonist | mentor | rival | love_interest | comic_relief | narrator | mysterious_stranger | ally | villain | kuudere | tsundere |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **shonen** | Y | M | Y | Y | M | Y | Y | M | Y | Y | M | M |
| **shojo** | Y | N | Y | Y | Y | Y | M | M | Y | N | M | Y |
| **seinen** | Y | Y | Y | M | M | N | Y | Y | Y | Y | Y | N |
| **josei** | Y | M | Y | N | Y | N | Y | M | Y | M | Y | M |
| **kodomomuke** | Y | N | Y | Y | Y | Y | Y | N | Y | N | N | N |
| **isekai** | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | M | Y |
| **horror** | Y | Y | M | N | N | N | Y | Y | Y | Y | M | N |
| **sports** | Y | N | Y | Y | M | Y | Y | N | Y | N | N | N |
| **slice_of_life** | Y | N | Y | N | Y | Y | Y | M | Y | N | Y | Y |
| **bl_gl** | Y | N | Y | N | Y | N | Y | M | Y | N | Y | Y |
| **mecha** | Y | Y | Y | Y | N | M | Y | Y | Y | Y | Y | N |

**Notes on marginal (`M`) cases:**
- `shonen + love_interest`: valid but must not dominate shonen tone; bubble style should stay `round_normal` not `shojo_soft`
- `seinen + rival`: valid but the rivalry is usually philosophical or professional, not competitive in shonen sense
- `horror + mentor`: valid only if the mentor is unreliable or already compromised
- `josei + antagonist`: valid when the antagonist is an institution, relationship dynamic, or past self rather than a person

### 7.2 Intensity × Bubble Style Validity

| intensity | Valid bubble styles |
|---|---|
| whisper | whisper_dashed, shojo_soft |
| calm | round_normal, square_narration, shojo_soft |
| normal | round_normal, square_narration, shojo_soft, electronic_sharp |
| excited | round_normal, spiky_emphasis, shojo_soft |
| shouting | spiky_emphasis, scream_ultra, electronic_sharp |
| screaming | scream_ultra, spiky_emphasis |
| internal | cloud_thought, square_narration, whisper_dashed |

`drip_horror` is cross-intensity and can be paired with any intensity in `horror` genre only.

### 7.3 Archetype × Intensity Hard Restrictions

| archetype | Forbidden intensities |
|---|---|
| narrator | shouting, screaming, excited |
| kuudere | screaming, excited (unless climax arc-break moment; cooldown_chapters: 5+) |
| mysterious_stranger | screaming |
| mentor | screaming (see Section 1.3 exception) |

---

## 8. Expansion Guidelines

When adding new atoms to `schema.yaml`, all of the following must hold:

### 8.1 Uniqueness Check

Before adding an atom, query the existing atoms for the signature `genre + archetype + emotion + intensity`. If five or more atoms already exist with the same signature, a new atom requires explicit justification in a comment. Five atoms per signature is the soft ceiling; ten is the hard ceiling.

### 8.2 Variant Quality

Each variant must:
- Carry the same semantic load as `text_template` (it fills the same story slot)
- Differ in register or emphasis, not just word-swap synonyms
- Be authentically genre-appropriate on its own, without context from the parent atom

Variants that are too similar (differ by only one or two words) should be merged into one variant with a slot variable instead.

### 8.3 `forbidden_after` Hygiene

When adding atom B, check all existing atoms for functional siblings (same signature). If atom B would be tonally repetitive when used after a sibling, add the sibling to atom B's `forbidden_after` list. Do not only add the new atom to the old atom's `forbidden_after` — the constraint must be declared by the atom that should not appear, not the atom that should not be followed.

### 8.4 `ei_emotion_mapping` Assignment

Every atom must have a `primary` value from the canonical EI V2 list: `shame | overwhelm | grief | false_alarm | spiral | watcher | comparison`. When in doubt, use the following heuristic:

| atom `emotion` | Default EI `primary` |
|---|---|
| determination, resolve, hope | shame (earned identity) |
| anger, contempt | overwhelm |
| grief, longing | grief |
| surprise, awe, confusion | false_alarm |
| despair | spiral |
| observational (narrator) | watcher |
| embarrassment, envy | comparison |

This heuristic should be overridden when the narrative context clearly points to a different EI primary. A character's anger at being abandoned maps to `grief`, not `overwhelm`.

### 8.5 Naming Convention Enforcement

`atom_id` must strictly follow the pattern: `atom_{genre}_{archetype}_{emotion}_{intensity}_{nn}` where `nn` is a zero-padded two-digit integer starting at `01`. If an existing atom already occupies `01`, use `02`, and so on. Do not use descriptive suffixes or underscores beyond the pattern.

### 8.6 Cross-Genre Atoms

Atoms in the `slice_of_life` genre with `archetype: protagonist` or `archetype: narrator` function as cross-genre universals and should be used when no genre-specific atom fits. This is by design. Do not create a copy of a universal atom in every genre — keep the universal in `slice_of_life` and reference it cross-genre in the selection logic.

### 8.7 Testing New Atoms

Before committing new atoms, run the atom through a simulated three-chapter sequence at the target `emotional_job` to verify:
1. The `cooldown_chapters` value allows the atom to appear at most once per intended frequency
2. The `forbidden_after` list is sufficient to prevent the most obvious tonal collision in context
3. The `variants` count is 3 or more (atoms with fewer than 3 variants have insufficient selection surface)
4. The `word_count_target` matches the actual word count of `text_template` (±2 words is acceptable)

---

*This document is the authoritative taxonomy reference. Changes to `schema.yaml` that introduce new valid values for any enum field must be reflected here in the corresponding matrix or definition table.*
