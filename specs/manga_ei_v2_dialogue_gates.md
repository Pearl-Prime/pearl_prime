# Manga EI V2 Dialogue Gates Specification

**Authority:** `phoenix_v4/quality/ei_v2/dimension_gates.py`, `phoenix_v4/manga/qc/chapter_qc.py`, `phoenix_v4/manga/ite_pipeline.py`  
**Stage owner:** `CHAPTER_QC` (sub-check of `ITE_QC`)  
**Gate namespace:** `MDLG` (Manga Dialogue)  
**Version:** 1.0.0  
**Status:** DRAFT — implementation target

---

## 1. Overview: Why Dialogue Needs EI Gates

### The visual medium compression problem

Manga dialogue operates under constraints that prose does not face. A single speech bubble may contain 8–25 words that must simultaneously: identify who is speaking, advance the plot beat, carry the emotional register the panel art is building, and leave enough interpretive space for the reader to project their own feeling into the scene. Every word does more work. A gate system that evaluates prose (as the existing `gate_engagement`, `gate_somatic_precision`, and `gate_listen_experience` functions in `dimension_gates.py` do) will routinely pass dialogue that fails as manga dialogue, and vice versa — the signal sources and scoring heuristics need to be retuned for the visual medium.

The five dialogue-specific problems the MDLG gates address:

**Forward momentum.** Prose can afford a paragraph of reflection between action beats. In manga, each panel is a hard cut. Dialogue that doesn't pull the reader toward the next panel kills pacing immediately. The engagement gate (`MDLG-01`) operationalizes this as a panel-position-aware measure rather than the word-count proxy in the existing `gate_engagement()`.

**Somatic grounding without over-explaining.** The ITE system's `vt_somatic` dimension (weight 0.25 in `WEIGHTS` from `ite_scorer.py`) tracks whether the chapter uses body sensation as a carrier of therapeutic effect. Dialogue is the primary delivery channel for somatic language, yet manga dialogue that over-explains bodily experience reads as clinical. The somatic gate (`MDLG-02`) is activation-gated: it only fires when the panel's declared emotion belongs to a set where somatic language is expected, avoiding false positives on neutral exchanges.

**Genre contracts.** A shōnen reader has an implicit agreement with the genre: the protagonist earns their determination, emotional peaks are telegraphed and paid off, and the pacing is forward. Seinen readers expect psychological interiority and restrained expression. Violating these contracts — e.g., giving a seinen protagonist a shōnen declaration speech at a grief beat — creates cognitive dissonance that breaks immersion even if the individual dialogue lines are well-written. The genre-calibration section (§5) and the cohesion gate (`MDLG-05`) together enforce these contracts.

**The ITE engine alignment requirement.** The `run_ite_qc()` function in `ite_pipeline.py` runs T-04 stealth vocabulary on collected dialogue text (`_collect_dialogue()`). The existing check is binary: forbidden terms present/absent. EI V2 extends this to positive alignment. Each chapter has an `emotional_job` mapped to one of the seven ITE engine archetypes (shame, overwhelm, grief, false_alarm, spiral, watcher, comparison). Dialogue must actively reinforce that engine, not merely avoid contradicting it. Gate `MDLG-05` measures this positive alignment.

**Anti-manipulation boundary.** The ITE system's design philosophy (documented in `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md`) distinguishes genuine emotional resonance from manufactured emotional manipulation. In dialogue terms: a character expressing grief through halting sentence fragments and references to the past creates resonance. A character delivering three consecutive melodramatic declarations of loss is manufactured trauma — it performs emotion rather than transmitting it. The uniqueness gate (`MDLG-04`) and the cohesion gate's forbidden patterns table (§2, Gate MDLG-05) together enforce this boundary.

---

## 2. Gate Definitions for Manga Dialogue

Each gate inputs a `panel_dialogue_record` extracted from `chapter_script` + `lettering_spec_v2`. The record has the following shape:

```python
{
    "panel_id": str,
    "page_number": int,
    "panel_position_in_chapter_pct": float,   # 0.0–100.0
    "is_final_panel_of_chapter": bool,
    "is_chapter_climax": bool,                 # highest emotional_band panel
    "emotional_band": int,                     # 1–5, from panel spec
    "declared_emotion": str | None,            # e.g. "grief", "determination_peak"
    "genre": str,                              # e.g. "shonen", "seinen"
    "ei_engine": str,                          # chapter-level emotional_job
    "bubbles": [
        {
            "speaker": str,
            "text": str,
            "word_count": int,
            "bubble_area_pct": float           # % of panel area
        }
    ],
    "total_bubble_area_pct": float,
    "bubble_count": int,
}
```

---

### Gate MDLG-01: Engagement Hook

**What it measures:** Does dialogue create reader investment in the next panel or page? In the visual medium, each dialogue exchange either opens a gap (pulls forward) or closes one (resolves). The engagement gate measures the ratio of opening moves to closing moves across the panel's dialogue.

**Scoring rubric (0.0–1.0):**

| Score | Criterion |
|-------|-----------|
| 1.0 | Dialogue contains an explicit question, a cliffhanger fragment (sentence cut off with "..."), or an unresolved contradiction between what is said and what the reader knows |
| 0.8 | Dialogue references a named stake — a person's name + consequence, a goal + an obstacle, or a named threat |
| 0.6 | Dialogue is emotionally charged and consistent with the scene but does not point forward |
| 0.4 | Neutral information exchange: facts conveyed, no emotional valence, no hook |
| 0.2 | Dialogue that closes rather than opens: summarizes what just happened, explains the completed action, congratulates the resolution |
| 0.0 | Dialogue actively breaks immersion: exposition dump exceeding genre ceiling, unearned resolution (character declares victory before the reader has seen it), fourth-wall adjacent meta-commentary |

**Panel-position modifiers (applied after base score):**

| Position | Minimum required score | Effect if below minimum |
|----------|----------------------|------------------------|
| Final panel of chapter (`is_final_panel_of_chapter = True`) | 0.80 | Cap chapter engagement score at 0.50 regardless of other panels |
| Chapter climax panel (`is_chapter_climax = True`) | 0.60 | Reduce panel score to 0.45 |
| Opening panel (panel_position_in_chapter_pct ≤ 5.0) | 0.40 | No modifier; setup panels may orient the reader |
| All other panels | 0.40 | Acceptable floor |

**Thresholds:**
- PASS: ≥ 0.65
- WARN: 0.45–0.64
- BLOCK: < 0.45

**How to compute from `chapter_script` + `lettering_spec`:**

```python
def score_mdlg01_engagement(panel: dict) -> float:
    bubbles = panel.get("bubbles", [])
    if not bubbles:
        return 0.4  # silent panel; no dialogue to score

    all_text = " ".join(b["text"] for b in bubbles).strip()
    if not all_text:
        return 0.4

    score = 0.4  # baseline: neutral exchange

    # Check for explicit question
    if "?" in all_text:
        score = max(score, 0.8)

    # Check for trailing ellipsis (cliffhanger fragment)
    import re
    if re.search(r"\.{2,}\s*$", all_text) or re.search(r"—\s*$", all_text):
        score = max(score, 1.0)

    # Check for named stake: name + consequence pattern
    stake_pattern = re.compile(
        r"\b(if|when|unless|before|after)\b.{3,40}\b(die|fall|lose|fail|leave|"
        r"destroy|hurt|save|protect|end)\b",
        re.IGNORECASE,
    )
    if stake_pattern.search(all_text):
        score = max(score, 0.8)

    # Detect closing/resolving language (penalties)
    close_patterns = [
        r"\b(it'?s over|we (did|won|made it)|finally|at last|i can'?t believe we)\b",
        r"\b(as you (can see|know|saw)|which means|in other words)\b",
    ]
    closing_hits = sum(
        1 for p in close_patterns if re.search(p, all_text, re.IGNORECASE)
    )
    if closing_hits >= 2:
        score = min(score, 0.2)
    elif closing_hits == 1:
        score = min(score, 0.4)

    # Position modifiers
    if panel.get("is_final_panel_of_chapter") and score < 0.80:
        score = min(score, 0.50)  # trigger chapter-level cap
    elif panel.get("is_chapter_climax") and score < 0.60:
        score = 0.45

    return round(min(1.0, max(0.0, score)), 3)
```

**PASS case:** Protagonist stands at the door of the antagonist's fortress. Dialogue: `"You killed them all... and you still have the nerve to call yourself a protector?"` — explicit accusation with unresolved tension, trailing question. Score: 1.0.

**FAIL case:** After a battle ends, protagonist says: `"We did it. We finally beat them. The town is safe now."` — pure resolution, all three closing signals active. Score: 0.0 (BLOCK).

---

### Gate MDLG-02: Somatic Precision

**What it measures:** When a panel's emotional context calls for it, does dialogue ground the emotion in physical/body experience? The ITE system is built on the principle that emotion is carried in the body; `score_somatic()` in `ite_scorer.py` already tracks breath and color arc monotonicity as somatic proxies. Dialogue somatic precision makes this explicit in the text layer.

**Activation condition:** Gate MDLG-02 only activates (and only scores) when `declared_emotion` is one of:

```python
SOMATIC_ACTIVATION_EMOTIONS = frozenset({
    "fear", "grief", "determination_peak", "love_confession",
    "horror_encounter", "shame_exposure", "overwhelm_peak",
    "physical_exhaustion",
})
```

When not activated, MDLG-02 score is `None`, and its weight is redistributed to MDLG-01 (see §3 for weight redistribution).

**Genre-specific somatic vocabulary tables:**

| Genre | Expected somatic vocabulary | Context |
|-------|----------------------------|---------|
| Shōnen | fists clenching, blood roaring, legs giving out, adrenaline flooding, muscles screaming, lungs burning | battle, training, determination_peak |
| Shōjo | heart pounding, face flushing, stomach tightening, tears blurring, voice cracking, knees weak | emotional peaks, love_confession, grief |
| Seinen | numbness, hollow chest, weight that won't lift, sweat that won't dry, hands that shake, the room contracting | psychological stress, shame_exposure, spiral |
| Horror | cold creeping, nausea rising, skin crawling, ears ringing, held breath, throat closing | dread, horror_encounter |
| Sports | lungs burning, muscles screaming, tunnel vision, world going silent, legs moving before the mind | physical_exhaustion, determination_peak |
| Iyashikei | warmth spreading, breath slowing, shoulders dropping, the tightness releasing | resolution, healing beats |

**Scoring rubric (0.0–1.0):**

| Score | Criterion |
|-------|-----------|
| 1.0 | Dialogue explicitly names a body sensation that is genre-appropriate and contextually coherent |
| 0.8 | Dialogue implies somatic response through action description embedded in speech ("She stopped speaking, pressed both hands against her chest") |
| 0.6 | Emotional content present but expressed entirely in abstract/conceptual language ("I feel terrible", "This is agony") |
| 0.4 | Flat emotional expression with no somatic grounding ("I'm upset", "This is bad") |
| 0.2 | Body language in speech contradicts the stated emotion or the panel art (incoherence) |
| 0.0 | Dialogue claims a somatic experience that is physically implausible for the scene context |

**Thresholds (when active):**
- PASS: ≥ 0.70
- WARN: 0.50–0.69
- BLOCK: < 0.50

**How to compute:**

```python
# Genre somatic vocab sets (truncated; full sets in config/manga/somatic_vocab.yaml)
GENRE_SOMATIC_VOCAB: dict[str, frozenset[str]] = {
    "shonen": frozenset({"fist", "blood", "roar", "muscle", "lung", "adrenaline",
                         "clench", "surge", "burning", "scream"}),
    "shojo": frozenset({"heart", "flush", "stomach", "tear", "voice", "knee",
                        "pounding", "tighten", "crack", "blurring"}),
    "seinen": frozenset({"numb", "hollow", "chest", "sweat", "shake", "weight",
                         "lift", "contract", "cold", "hand"}),
    "horror": frozenset({"creep", "nausea", "crawl", "ringing", "throat", "breath",
                         "cold", "skin", "held", "close"}),
    "sports": frozenset({"lung", "muscle", "tunnel", "silent", "burning", "scream",
                         "vision", "leg", "mind", "body"}),
}

def score_mdlg02_somatic(panel: dict) -> float | None:
    if panel.get("declared_emotion") not in SOMATIC_ACTIVATION_EMOTIONS:
        return None  # gate inactive for this panel

    genre = panel.get("genre", "").lower().replace("-", "").replace("ō", "o")
    vocab = GENRE_SOMATIC_VOCAB.get(genre, frozenset())
    all_text = " ".join(b["text"] for b in panel.get("bubbles", [])).lower()
    tokens = set(re.findall(r"\w+", all_text))

    hits = len(tokens & vocab)
    if hits >= 2:
        return 1.0
    if hits == 1:
        # Check if it is clearly foregrounded (appears in first/last bubble)
        first_last = " ".join([
            panel["bubbles"][0]["text"] if panel["bubbles"] else "",
            panel["bubbles"][-1]["text"] if len(panel["bubbles"]) > 1 else "",
        ]).lower()
        first_last_hits = len(set(re.findall(r"\w+", first_last)) & vocab)
        return 0.8 if first_last_hits >= 1 else 0.6

    # No somatic vocab — check for abstract emotional language
    abstract_emotion = re.compile(
        r"\b(feel|feeling|terrible|awful|horrible|pain|hurt|agony|joy|happy)\b",
        re.IGNORECASE,
    )
    if abstract_emotion.search(all_text):
        return 0.4
    return 0.2  # no emotional language at all in an emotionally-activated panel
```

**PASS case (shōnen determination_peak):** `"My legs are giving out — but I won't stop. I can feel it, everything I have left, burning right here."` — two somatic hits (legs, burning). Score: 1.0.

**FAIL case (seinen grief, BLOCK):** `"I've made my peace with it. I'm fine. Everything is going to be okay."` — no somatic vocabulary, declared emotion is grief, statements directly contradict expected somatic register. Score: 0.0 (BLOCK).

---

### Gate MDLG-03: Listen Experience (Word Economy)

**What it measures:** Is dialogue economical enough for the visual medium? In manga, the reader's eye moves through panels at a pace controlled by layout, not by text. Excessive words per bubble interrupt this pacing, force the reader to switch cognitive mode from visual to textual, and break immersion. This gate is the MDLG equivalent of the existing `gate_listen_experience()` in `dimension_gates.py`, retooled for per-bubble word counts rather than TTS readability.

**Per-genre word-per-bubble ceilings:**

| Genre | Normal range | Max acceptable | BLOCK if exceeded |
|-------|-------------|---------------|------------------|
| Shōnen action | 8–15 | 20 | 25 |
| Shōnen emotional | 10–20 | 28 | 35 |
| Shōjo | 12–25 | 35 | 45 |
| Seinen internal monologue | 20–40 | 55 | 70 |
| Seinen dialogue | 10–20 | 28 | 35 |
| Kodomomuke | 5–12 | 18 | 22 |
| Horror | 5–10 | 15 | 20 |
| Sports | 6–14 | 20 | 26 |
| Slice of life | 8–20 | 30 | 38 |
| BL/GL | 10–22 | 32 | 42 |
| Mecha tactical | 10–20 | 28 | 35 |

**Additional structural constraints:**

| Constraint | WARN threshold | BLOCK threshold |
|-----------|---------------|----------------|
| Bubbles per panel | 3 | 5+ |
| Total dialogue area coverage | 25% of panel area | 30% of panel area |
| Consecutive long bubbles (same speaker) | 3 consecutive at "max acceptable" | 4+ consecutive |

**Scoring rubric (0.0–1.0):**

| Score | Criterion |
|-------|-----------|
| 1.0 | All bubbles within normal range; varied length creates visual rhythm |
| 0.8 | All bubbles within normal range; some bubbles at upper end of normal |
| 0.6 | Some bubbles at "max acceptable" threshold but none exceeding it |
| 0.4 | Multiple bubbles near the ceiling; pacing visibly suffers |
| 0.0 | Any single bubble exceeds BLOCK threshold (hard stop) |

**How to compute:**

```python
# Genre ceilings: (normal_max, warn_max, block_threshold)
GENRE_WORD_CEILINGS: dict[str, tuple[int, int, int]] = {
    "shonen_action":     (15, 20, 25),
    "shonen_emotional":  (20, 28, 35),
    "shojo":             (25, 35, 45),
    "seinen_mono":       (40, 55, 70),
    "seinen":            (20, 28, 35),
    "kodomomuke":        (12, 18, 22),
    "horror":            (10, 15, 20),
    "sports":            (14, 20, 26),
    "slice_of_life":     (20, 30, 38),
    "bl_gl":             (22, 32, 42),
    "mecha":             (20, 28, 35),
}

def score_mdlg03_word_economy(panel: dict) -> float:
    genre_key = _resolve_genre_key(panel.get("genre", ""))
    normal_max, warn_max, block_max = GENRE_WORD_CEILINGS.get(
        genre_key, (20, 30, 40)
    )
    bubbles = panel.get("bubbles", [])
    if not bubbles:
        return 1.0  # silent panel

    # Hard block: any single bubble over block ceiling
    for b in bubbles:
        if b["word_count"] > block_max:
            return 0.0  # BLOCK — do not average

    # Bubble count structural check
    if len(bubbles) >= 5:
        return 0.0  # BLOCK — too many bubbles

    # Total area coverage
    if panel.get("total_bubble_area_pct", 0) > 30:
        return 0.0  # BLOCK

    # Score per bubble, then average
    per_bubble_scores = []
    for b in bubbles:
        wc = b["word_count"]
        if wc <= normal_max:
            per_bubble_scores.append(1.0 if wc <= normal_max * 0.7 else 0.8)
        elif wc <= warn_max:
            # Linear interpolation: 0.6 at normal_max+1, 0.4 at warn_max
            frac = (wc - normal_max) / max(1, warn_max - normal_max)
            per_bubble_scores.append(round(0.6 - 0.2 * frac, 3))
        else:
            # Between warn_max and block_max: 0.2–0.0
            frac = (wc - warn_max) / max(1, block_max - warn_max)
            per_bubble_scores.append(round(0.2 - 0.2 * frac, 3))

    base_score = sum(per_bubble_scores) / len(per_bubble_scores)

    # Consecutive long-bubble penalty (same speaker)
    consecutive = _max_consecutive_long_bubbles(bubbles, warn_max)
    if consecutive >= 4:
        base_score = min(base_score, 0.2)
    elif consecutive >= 3:
        base_score = min(base_score, 0.5)

    # Structural warnings reduce ceiling but do not block
    if len(bubbles) == 4:
        base_score = min(base_score, 0.6)

    return round(max(0.0, min(1.0, base_score)), 3)
```

**PASS case (shōnen action):** Panel has 2 bubbles, 12 words and 8 words. Score: 1.0.

**WARN case (shōjo):** Love interest explains feelings in a single bubble of 38 words. Below the BLOCK ceiling (45) but above normal range. Score: 0.4 (WARN). **Revision direction:** Split into 3 bubbles (13/13/12 words), remove filler phrases that rephrase what the previous sentence established.

---

### Gate MDLG-04: Uniqueness

**What it measures:** Are dialogue lines sufficiently varied across the series? The existing `gate_uniqueness()` in `dimension_gates.py` uses word-overlap ratio between chapter texts. For manga dialogue this is insufficient because: (1) chapter dialogue is short, making overlap ratios unstable, and (2) the real uniqueness problem in manga is clichéd phrases — lines that feel like every other manga of the genre, not lines that echo other chapters of this specific series.

**Definition:** Two similarity scores are combined:

1. **Intra-series similarity:** cosine similarity of the current panel's dialogue against all dialogue lines previously stored in series memory (`artifacts/series_dialogue_corpus.jsonl`). Uses TF-IDF weighted unigram/bigram vectors.
2. **Archetype cliché detection:** exact or near-exact match against the banned phrase list.

**Scoring rubric (0.0–1.0):**

| Score | Criterion |
|-------|-----------|
| 1.0 | All dialogue lines have cosine similarity < 0.70 to any prior line; no cliché hits |
| 0.8 | Some similarity (0.70–0.80) but not repetition; organic variation present |
| 0.6 | Some near-duplicate lines (0.80–0.85); meaningfully different context |
| 0.4 | Multiple near-duplicate lines from within same chapter |
| 0.0 | Exact repetition of a prior series line, OR any banned phrase match |

**Banned phrase list (auto-BLOCK regardless of score):**

```python
BANNED_PHRASES: list[tuple[str, str]] = [
    # (pattern, reason)
    (r"\bthis is my (true |real |)power\b", "shonen_power_declaration_cliche"),
    (r"\bi won'?t give up\b", "shonen_resilience_cliche - once per arc only"),
    (r"\byou'?ll regret underestimating me\b", "shonen_threat_cliche"),
    (r"\bi'?ll protect them no matter what\b", "shonen_vow_cliche"),
    (r"\b(together|as one) we can (do anything|overcome anything)\b", "generic_teamwork_cliche"),
    (r"\bthe true strength (is|lies|was) (within|inside)\b", "mentor_cliche"),
    (r"\bbelieve in (your|the) (heart|power|self)\b", "mentor_cliche"),
]
```

Note on `"I won't give up"`: this phrase is permitted once per story arc as a callback echo (deliberate narrative repetition). The scorer must check `series_memory.arc_phrase_uses` to determine if the arc budget has been consumed.

**Anti-repetition reset:** After 6+ chapters have elapsed since a line was used, the cosine similarity threshold relaxes from 0.85 to 0.92, allowing deliberate callback echoes to pass.

```python
def score_mdlg04_uniqueness(
    panel: dict,
    series_corpus: list[dict],  # [{chapter_index, panel_id, text, arc_id}]
    chapter_index: int,
    arc_id: str,
) -> float:
    bubbles = panel.get("bubbles", [])
    all_text = " ".join(b["text"] for b in bubbles).lower()
    if not all_text.strip():
        return 1.0

    # Check banned phrases (auto-BLOCK)
    for pattern, reason in BANNED_PHRASES:
        # Special case: once-per-arc phrases
        if "once per arc" in reason:
            arc_uses = sum(
                1 for entry in series_corpus
                if entry.get("arc_id") == arc_id
                and re.search(pattern, entry.get("text", "").lower())
            )
            if arc_uses >= 1:
                return 0.0  # arc budget consumed
        elif re.search(pattern, all_text, re.IGNORECASE):
            return 0.0

    # Cosine similarity against corpus
    if not series_corpus:
        return 1.0  # no prior lines to compare against

    max_sim = 0.0
    near_dup_count = 0
    for entry in series_corpus:
        chapters_ago = chapter_index - entry.get("chapter_index", 0)
        threshold = 0.92 if chapters_ago > 6 else 0.85
        sim = _tfidf_cosine_similarity(all_text, entry.get("text", ""))
        if sim >= threshold:
            return 0.0  # exact match threshold
        if sim > 0.80:
            near_dup_count += 1
        max_sim = max(max_sim, sim)

    if near_dup_count >= 3:
        return 0.4
    if max_sim >= 0.80:
        return 0.6
    if max_sim >= 0.70:
        return 0.8
    return 1.0
```

**PASS case:** Protagonist says: `"Every time I reach this corridor, it feels narrower than the last time. As if the building itself is deciding."` — imagery specific to this story's setting, no prior instance. Score: 1.0.

**FAIL case:** Protagonist says: `"I won't give up! Not now, not ever!"` when the arc already contains this phrase. Banned phrase match. Score: 0.0 (BLOCK).

---

### Gate MDLG-05: Cohesion (EI Engine Alignment)

**What it measures:** Does dialogue reinforce the chapter's `emotional_job`? Each chapter is assigned an EI engine archetype (shame, overwhelm, grief, false_alarm, spiral, watcher, comparison). The existing `run_ite_qc()` T-04 gate checks that forbidden therapeutic terms are absent from dialogue. MDLG-05 goes further: it requires that the dominant emotional register of dialogue positively echoes the assigned engine.

This replaces the prose-oriented `gate_cohesion()` (which measures backward linkage to the prior chapter through transitional phrases) with a forward alignment measure against the chapter's declared emotional intention.

**EI engine dialogue alignment table:**

| EI Engine | Reinforcing dialogue patterns | Forbidden dialogue patterns |
|-----------|------------------------------|----------------------------|
| `shame` | Self-doubt phrasing, exposure fear ("they'll see what I really am"), hiding, deflection, minimizing ("it's nothing") | Triumphant declarations, casual unguarded confidence, public self-assertion |
| `overwhelm` | Fragmentation (dashes, ellipses), unfinished sentences, lists that trail off, "I can't keep up", simultaneous urgencies | Calm resolution, clear sequential plans, reassuring statements |
| `grief` | Slow past-tense framing ("she used to"), names without predicates, sentence fragments, prolonged silence (text-sparse panels) | Action urgency, present-tense planning, future promises |
| `false_alarm` | Misreading situations, relieved then uncertain ("I was so sure, but..."), anti-climactic deflation | Confirmed danger, actual loss, justified catastrophizing |
| `spiral` | Looping internal voice, self-referential ("I keep doing this"), escalating intensity across bubbles, the thought that cannot complete | External resolution, grounded action statements, conclusive decisions |
| `watcher` | Observation from outside, third-person-ish self-description ("she sees herself standing there"), emotional detachment markers | Direct I-statements of engagement, declarations of feeling, joining actions |
| `comparison` | Measuring against others ("she can do it, why can't I"), ranking language, "what's the point", self-erasure | Self-acceptance statements, unique value framings, "I don't need to be like them" |

**Scoring rubric (0.0–1.0):**

| Score | Criterion |
|-------|-----------|
| 1.0 | 3+ dialogue lines or bubbles directly echo the EI engine pattern per the table above |
| 0.8 | Majority of bubbles reinforce the engine; 1–2 are neutral |
| 0.6 | Even mix of reinforcing and neutral bubbles; engine present but not dominant |
| 0.4 | Mostly neutral; the engine is not expressed in dialogue |
| 0.2 | One or more bubbles contain language that is in the "forbidden" column for this engine |
| 0.0 | The dominant dialogue register is the forbidden register for the chapter's engine |

**How to compute:**

```python
# Engine alignment keyword sets (simplified; full sets in config/manga/ei_engine_vocab.yaml)
EI_ENGINE_REINFORCING: dict[str, list[str]] = {
    "shame": ["can't let them see", "i'm not", "pretend", "hide", "what they'd think",
              "i know i'm not", "never good enough", "if they knew"],
    "overwhelm": ["can't keep up", "too much", "all at once", "i don't know where",
                  "everything at the same", "—but", "—and then"],
    "grief": ["used to", "she was", "he was", "they were", "i remember",
              "not anymore", "since they", "back when"],
    "false_alarm": ["i thought", "i was sure", "it seemed like", "but it wasn't",
                    "turned out", "i was wrong", "relieved but"],
    "spiral": ["again", "every time", "i keep", "why do i always", "i know i should",
               "but i can't stop", "it's happening again"],
    "watcher": ["she sees herself", "he watches", "as if from outside", "the person i am",
                "they stand there", "watching herself", "from far away"],
    "comparison": ["she can", "he could", "better than me", "what's the point",
                   "why can't i", "they don't have to", "everyone else"],
}

EI_ENGINE_FORBIDDEN: dict[str, list[str]] = {
    "shame":    ["i'm proud", "watch this", "i'll show them all", "i did it"],
    "overwhelm": ["i have a plan", "here's what we'll do", "step by step", "calm down"],
    "grief":    ["we'll fight back", "we'll fix this", "next time", "from now on"],
    "false_alarm": ["we're all going to die", "this is really it", "no way out"],
    "spiral":   ["that's decided then", "never again", "from today forward"],
    "watcher":  ["i feel", "i love", "i hate", "i want", "i need"],
    "comparison": ["i'm fine as i am", "i don't need to be", "everyone's different"],
}

def score_mdlg05_cohesion(panel: dict) -> float:
    engine = panel.get("ei_engine", "")
    if not engine:
        return 0.6  # no engine assigned: neutral score

    bubbles = panel.get("bubbles", [])
    all_text = " ".join(b["text"] for b in bubbles).lower()

    reinforcing_vocab = EI_ENGINE_REINFORCING.get(engine, [])
    forbidden_vocab = EI_ENGINE_FORBIDDEN.get(engine, [])

    reinforcing_hits = sum(1 for phrase in reinforcing_vocab if phrase in all_text)
    forbidden_hits = sum(1 for phrase in forbidden_vocab if phrase in all_text)

    if forbidden_hits >= 2:
        return 0.0  # dominant contradiction
    if forbidden_hits == 1:
        base = 0.2
    elif reinforcing_hits >= 3:
        base = 1.0
    elif reinforcing_hits >= 2:
        base = 0.8
    elif reinforcing_hits == 1:
        base = 0.6
    else:
        base = 0.4  # neutral: engine absent from dialogue

    # Forbidden hit reduces score even if reinforcing present
    if forbidden_hits == 1:
        base = min(base, 0.2)

    return round(base, 3)
```

**PASS case (grief engine):** Character dialogue: `"She used to call every morning... I keep reaching for my phone."` — two reinforcing hits (past-tense framing, looping behavior). Score: 0.8.

**FAIL case (grief engine, BLOCK):** Chapter engine is grief. Protagonist says: `"We'll fix this. From now on, I'm going to be stronger. Next time will be different."` — three forbidden hits (future planning, resolution, promise). Score: 0.0 (BLOCK).

---

## 3. Gate Thresholds Table

| Gate | PASS | WARN | BLOCK |
|------|------|------|-------|
| MDLG-01 Engagement Hook | ≥ 0.65 | 0.45–0.64 | < 0.45 |
| MDLG-02 Somatic Precision | ≥ 0.70 (when active) | 0.50–0.69 | < 0.50 (when active) |
| MDLG-03 Word Economy | ≥ 0.70 | 0.50–0.69 | any bubble > block ceiling |
| MDLG-04 Uniqueness | ≥ 0.75 | 0.60–0.74 | < 0.60 or any banned phrase |
| MDLG-05 EI Cohesion | ≥ 0.70 | 0.50–0.69 | < 0.40 |

### Default gate weights (chapter-level aggregate score)

| Gate | Default weight | Notes |
|------|---------------|-------|
| MDLG-01 | 0.25 | |
| MDLG-02 | 0.15 | Redistributed equally to MDLG-01 and MDLG-03 when inactive |
| MDLG-03 | 0.30 | Highest — word economy is the bottleneck in the visual medium |
| MDLG-04 | 0.15 | |
| MDLG-05 | 0.15 | |

**Redistribution when MDLG-02 is inactive (no somatic-activation emotion in chapter):**

```
MDLG-01: 0.25 + 0.075 = 0.325
MDLG-03: 0.30 + 0.075 = 0.375
MDLG-04: 0.15
MDLG-05: 0.15
```

**Chapter dialogue gate passes when:**
1. All individual gates at PASS level (no BLOCKs), AND
2. Weighted average chapter score ≥ 0.70

A chapter with any BLOCK-level gate fails regardless of weighted average.

---

## 4. Integration with Existing QC Pipeline

### Where MDLG gates run

MDLG gates run as a sub-check of `ITE_QC`, triggered after `lettering_spec_v2` is available and chapter script is finalized. The pipeline ordering is:

```
CHAPTER_SCRIPT
  → LETTERING_SPEC_V2          # lettering agent assigns bubbles to panels
  → ITE_ANNOTATION             # annotate_panel_breath(), annotate_gutter_therapy()
  → ITE_COLOR_ARC              # build_color_arc()
  → FRACTAL_CHECK              # run_fractal_check()
  → ITE_QC (T-01 … T-20)      # run_ite_qc()
      └── MDLG_DIALOGUE_QC    # run_mdlg_qc() ← NEW, runs here
  → CHAPTER_QC (revision_queue)
```

MDLG gates require `lettering_spec_v2` rather than `lettering_spec` because MDLG-03 needs `bubble_area_pct` (panel area coverage), which is computed by the lettering agent in v2.

### Stage gate IDs in `gate_registry.yaml`

Add the following entries to `config/manga/gate_registry.yaml`:

```yaml
gates:
  # ... existing gates ...
  - gate_id: MDLG-01
    stage_owner: ite_qc
    description: "Manga dialogue engagement hook — panel forward momentum"
    severity: BLOCKER

  - gate_id: MDLG-02
    stage_owner: ite_qc
    description: "Manga dialogue somatic precision — body grounding at emotion peaks"
    severity: BLOCKER

  - gate_id: MDLG-03
    stage_owner: ite_qc
    description: "Manga dialogue word economy — per-bubble word count ceilings"
    severity: BLOCKER

  - gate_id: MDLG-04
    stage_owner: ite_qc
    description: "Manga dialogue uniqueness — series corpus anti-repetition"
    severity: BLOCKER

  - gate_id: MDLG-05
    stage_owner: ite_qc
    description: "Manga dialogue EI cohesion — engine alignment"
    severity: BLOCKER
```

### Series memory storage for MDLG-04

Each passing chapter's dialogue is written to the series corpus after chapter QC passes. The corpus is stored at `artifacts/series_memory/<series_id>/dialogue_corpus.jsonl`, one record per panel:

```json
{
  "chapter_index": 3,
  "panel_id": "ch03_p04_pan02",
  "arc_id": "arc_01",
  "text": "You've taken everything from me... but you couldn't take this.",
  "ei_engine": "grief",
  "genre": "shonen",
  "timestamp_iso": "2026-04-17T12:00:00Z"
}
```

The scorer reads this file at the start of each `run_mdlg_qc()` invocation. Writers do not update the file; it is written by the QC pipeline after a chapter fully passes.

### Revision request format

When any MDLG gate fails, the gate runner appends a structured `revision_request` to the chapter's `revision_queue`. This follows the same schema as the existing `revision_queue` artifact (see `build_revision_queue_for_chapter()` in `chapter_qc.py`):

```python
{
    "issue_code": "MDLG_03_WORD_ECONOMY_BLOCK",
    "gate_id": "MDLG-03",
    "severity": "BLOCKER",
    "stage_owner": "ite_qc",
    "description": "Panel ch03_p06_pan04: bubble 2 has 52 words (shonen_emotional ceiling: 35). "
                   "Split into 3 bubbles: target 18/17/17 words. Remove filler in sentences 2 and 4.",
    "panel_id": "ch03_p06_pan04",
    "bubble_index": 1,
    "observed_word_count": 52,
    "genre_block_ceiling": 35,
    "revision_direction": "split_bubble",
    "suggested_split_target_words_per_bubble": [18, 17, 17],
}
```

The `revision_direction` field is gate-specific:

| Gate | revision_direction values |
|------|--------------------------|
| MDLG-01 | `add_question`, `add_cliffhanger`, `remove_resolution_language` |
| MDLG-02 | `add_somatic_vocabulary`, `replace_abstract_emotion` |
| MDLG-03 | `split_bubble`, `reduce_word_count`, `remove_filler` |
| MDLG-04 | `replace_banned_phrase`, `rephrase_near_duplicate` |
| MDLG-05 | `align_to_ei_engine`, `remove_forbidden_register` |

---

## 5. Genre-Specific Gate Calibration

When `chapter.genre` is set, the following weight overrides replace the defaults from §3. All remaining weight budget (after the override) is distributed proportionally among the other active gates.

### Shōnen

Shōnen lives on forward momentum. The genre contract is explicit: every chapter ends with something unresolved, every battle has a turning point, and the reader's investment is sustained by perpetual hook. MDLG-01 gets the largest weight.

```python
GENRE_WEIGHT_OVERRIDES["shonen"] = {
    "MDLG-01": 0.35,  # up from 0.25
    "MDLG-02": 0.10,
    "MDLG-03": 0.25,
    "MDLG-04": 0.15,
    "MDLG-05": 0.15,
}
```

### Seinen

Psychological precision is the genre's core value. The somatic precision gate gets elevated weight because in seinen, the body's response often carries more narrative truth than what characters say explicitly.

```python
GENRE_WEIGHT_OVERRIDES["seinen"] = {
    "MDLG-01": 0.20,
    "MDLG-02": 0.25,  # up from 0.15
    "MDLG-03": 0.25,
    "MDLG-04": 0.15,
    "MDLG-05": 0.15,
}
```

Seinen also relaxes the MDLG-03 BLOCK threshold for internal monologue panels (identified by `bubble_type: "monologue"` in lettering_spec_v2). Monologue panels use the `seinen_mono` ceiling row rather than the `seinen` row.

### Horror

In horror, silence and brevity create dread. The fewer words on the page, the more the visual imagination fills in. MDLG-03 gets the highest weight of any genre.

```python
GENRE_WEIGHT_OVERRIDES["horror"] = {
    "MDLG-01": 0.20,
    "MDLG-02": 0.10,
    "MDLG-03": 0.40,  # up from 0.30
    "MDLG-04": 0.15,
    "MDLG-05": 0.15,
}
```

Horror also applies a stricter MDLG-03 PASS threshold: 0.80 (vs. the default 0.70).

### Shōjo

Emotional coherence is the shōjo genre contract. The reader invests in the emotional logic of the relationship, and dialogue that breaks emotional consistency — even slightly — can collapse the chapter's entire emotional payoff. MDLG-05 gets elevated weight.

```python
GENRE_WEIGHT_OVERRIDES["shojo"] = {
    "MDLG-01": 0.20,
    "MDLG-02": 0.15,
    "MDLG-03": 0.25,
    "MDLG-04": 0.15,
    "MDLG-05": 0.25,  # up from 0.15
}
```

---

## 6. Worked Examples

### Example 1 — Shōnen Climax (Expected: PASS)

**Context:** Chapter 12, shōnen action genre. EI engine: `spiral`. Protagonist faces the final villain. Panel is flagged `is_chapter_climax = True`. Declared emotion: `determination_peak`. Chapter position: 88%.

**Dialogue:**
> "You've taken everything from me... but you couldn't take this. My reason to fight."

**Gate-by-gate scoring (using shōnen weight overrides):**

| Gate | Raw computation | Score | Status |
|------|----------------|-------|--------|
| MDLG-01 | Trailing ellipsis detected (cliffhanger fragment) → base 1.0. Panel is climax, score ≥ 0.60 ✓. Chapter position 88% with no final panel flag → no cap. | **1.0** | PASS |
| MDLG-02 | `declared_emotion = determination_peak` → gate active (shōnen). No direct somatic vocab ("burn", "muscle") present. "Everything" is abstract. → 0.4 base. "My reason to fight" implies resolve but no body word. → score stays 0.4. | **0.4** | WARN |
| MDLG-03 | Two bubbles: 13 words + 5 words. Both within shōnen action normal range (≤15). Score: 1.0. Bubble count: 2 ✓ | **1.0** | PASS |
| MDLG-04 | No banned phrases. Cosine similarity against corpus: max_sim = 0.61 (related thematically but not near-duplicate). Score: 1.0. | **1.0** | PASS |
| MDLG-05 | Engine: `spiral`. Reinforcing vocab check: "everything" hit → 1 hit. "My reason" → not a spiral phrase. → reinforcing_hits = 1, forbidden_hits = 0. Score: 0.6. | **0.6** | WARN (but above 0.40 BLOCK) |

**Weighted aggregate (shōnen overrides):**

```
MDLG-01: 1.0 × 0.35 = 0.350
MDLG-02: 0.4 × 0.10 = 0.040  (active: determination_peak)
MDLG-03: 1.0 × 0.25 = 0.250
MDLG-04: 1.0 × 0.15 = 0.150
MDLG-05: 0.6 × 0.15 = 0.090
Total: 0.880
```

**Result: PASS** (0.880 ≥ 0.70; no individual BLOCKs; MDLG-02 WARN is acceptable). MDLG-02 revision note: add one somatic grounding word — e.g., change to `"...but you couldn't take this. This burning in my chest. My reason to fight."` to reach 1.0.

---

### Example 2 — Shōjo Mid-Chapter (Expected: WARN on MDLG-03)

**Context:** Chapter 7, shōjo genre. EI engine: `comparison`. Mid-chapter emotional beat at 55% position. Declared emotion: `love_confession`. Single panel, 1 bubble.

**Dialogue (original — 58 words):**
> "Every time I see you with her, I keep telling myself it doesn't mean anything, that we're just friends, that this thing I feel isn't real, but then you smile at her like that and I can't pretend anymore, I don't know what I'm supposed to do with all of this, I just... I don't know."

**Gate-by-gate scoring:**

| Gate | Raw computation | Score | Status |
|------|----------------|-------|--------|
| MDLG-01 | Trailing "I don't know" → not a cliffhanger fragment (it resolves into passivity). Named stake: "her" + implied consequence. → 0.8 base. No closing language. | **0.8** | PASS |
| MDLG-02 | Active (love_confession). "can't pretend" → near-somatic. "don't know what I'm supposed to do" → cognitive, not somatic. No shōjo vocab (heart, stomach, face flushing). → 0.4. | **0.4** | WARN |
| MDLG-03 | **Single bubble: 58 words.** Shōjo BLOCK ceiling: 45. 58 > 45. **Score: 0.0.** | **0.0** | BLOCK |
| MDLG-04 | "I don't know" appears once. No banned phrases. Cosine sim moderate. Score: 0.8. | **0.8** | PASS |
| MDLG-05 | Engine: `comparison`. Reinforcing hits: "every time I see you with her" (comparison), "I keep telling myself" (spiral marker, not comparison — neutral), "I don't know" (neutral). → 1 reinforcing hit. Score: 0.6. | **0.6** | WARN |

**Result: BLOCK** (MDLG-03 word ceiling exceeded).

**Revision request generated:**
```python
{
    "issue_code": "MDLG_03_WORD_ECONOMY_BLOCK",
    "gate_id": "MDLG-03",
    "severity": "BLOCKER",
    "panel_id": "ch07_p09_pan03",
    "bubble_index": 0,
    "observed_word_count": 58,
    "genre_block_ceiling": 45,
    "revision_direction": "split_bubble",
    "description": "58-word single bubble exceeds shōjo ceiling (45). Split into 3 bubbles, "
                   "target 19/19/20 words. Retain the 'every time I see you with her' opening "
                   "as standalone bubble. Move 'I can't pretend anymore' to second bubble. "
                   "Trim the trailing uncertainty to a single fragment.",
}
```

**Revised dialogue (3 bubbles, 19/13/8 words):**
- Bubble 1 (19w): `"Every time I see you with her, I tell myself it doesn't mean anything — that we're just friends."`
- Bubble 2 (13w): `"But then you smile like that. And I can't pretend anymore."`
- Bubble 3 (8w): `"I don't know what to do with this."`

Post-revision MDLG-03 score: 0.8 (PASS). MDLG-02 improvement: add one shōjo somatic word to bubble 2 (e.g., `"my stomach drops"`) to reach 0.8.

---

### Example 3 — Seinen Descent Arc (Expected: BLOCK on MDLG-05)

**Context:** Chapter 4, seinen genre. EI engine: `grief`. Protagonist has just lost their mentor. Panel at 70% chapter position, flagged mid-resolution. Declared emotion: `grief`.

**Dialogue:**
> "I've been thinking about this for a long time. From today on, I'm going to do things differently — be the kind of person he would've been proud of. I'll make everything he taught me count."

**Gate-by-gate scoring (using seinen weight overrides):**

| Gate | Raw computation | Score | Status |
|------|----------------|-------|--------|
| MDLG-01 | "From today on" + future plan → closing language. No question, no cliffhanger. Closing hits: 2 ("from today on", "I'll make everything count"). Score: 0.2. | **0.2** | BLOCK |
| MDLG-02 | Active (grief). No somatic vocab. "I've been thinking" is cognitive. No seinen grief vocabulary (hollow, weight, numbness). Score: 0.2. | **0.2** | BLOCK |
| MDLG-03 | 3 bubbles: 12/15/10 words. All within seinen_dialogue normal range (≤20). Score: 1.0. | **1.0** | PASS |
| MDLG-04 | "Make everything count" → no exact banned phrase. Cosine sim moderate. Score: 0.8. | **0.8** | PASS |
| MDLG-05 | Engine: `grief`. Forbidden hits: `"from now on"` (matches `"from today on"`) → 1. `"next time"` pattern → 0. `"we'll fix this"` pattern → 0. But "I'll make everything he taught me count" is future-planning (grief forbidden). Total forbidden_hits = 2. **Score: 0.0.** | **0.0** | BLOCK |

**Result: BLOCK** (MDLG-01 BLOCK + MDLG-02 BLOCK + MDLG-05 BLOCK; three simultaneous gate failures).

**Revision direction for MDLG-05:**
```python
{
    "issue_code": "MDLG_05_COHESION_BLOCK",
    "gate_id": "MDLG-05",
    "severity": "BLOCKER",
    "ei_engine": "grief",
    "forbidden_patterns_matched": ["future_planning", "resolution_promise"],
    "revision_direction": "align_to_ei_engine",
    "description": "Chapter EI engine is grief. Dialogue is in the planning/resolution register "
                   "(future tense, promises, forward momentum). Grief engine requires past-tense "
                   "framing, fragmentation, or silence. Replace with past-tense references to the "
                   "mentor and remove all forward-planning language.",
    "example_revision": "He used to say that. Every single morning. ...I hadn't realized "
                        "I was waiting to hear it again."
}
```

**Corrected dialogue (PASS target):**

> "He used to say that. Every single morning. I hadn't realized I was waiting to hear it again."

Post-revision scores: MDLG-01 (0.8 — trailing sentiment, named absent person), MDLG-02 (0.6 — no full somatic vocab but "waiting" implies somatic state), MDLG-05 (0.8 — past-tense framing, named person without predicate, reinforcing grief engine).

---

## 7. Implementation Checklist

For a developer implementing this spec from scratch:

- [ ] Add `run_mdlg_qc(chapter_script, lettering_spec_v2, series_corpus, chapter_index, arc_id)` function to `phoenix_v4/manga/qc/dialogue_gates.py`
- [ ] Implement `score_mdlg01_engagement()`, `score_mdlg02_somatic()`, `score_mdlg03_word_economy()`, `score_mdlg04_uniqueness()`, `score_mdlg05_cohesion()` as standalone functions
- [ ] Add `SOMATIC_ACTIVATION_EMOTIONS` constant; gate MDLG-02 must check activation before scoring
- [ ] Add `GENRE_WORD_CEILINGS` dict; pull genre key from `panel.genre` via `_resolve_genre_key()`
- [ ] Add `BANNED_PHRASES` list with per-arc once-only tracking via series memory
- [ ] Add `EI_ENGINE_REINFORCING` and `EI_ENGINE_FORBIDDEN` vocab dicts (seed from this spec; expand via `config/manga/ei_engine_vocab.yaml`)
- [ ] Implement weight redistribution when MDLG-02 is inactive
- [ ] Implement genre weight overrides for shōnen, seinen, horror, shōjo
- [ ] Wire `run_mdlg_qc()` into `run_ite_qc()` call in `ite_pipeline.py` (after T-20, before final `overall_pass` computation)
- [ ] Add gate IDs `MDLG-01` through `MDLG-05` to `config/manga/gate_registry.yaml`
- [ ] Add series corpus writer: append to `artifacts/series_memory/<series_id>/dialogue_corpus.jsonl` on chapter pass
- [ ] Add `revision_direction` field handling in `build_revision_queue_for_chapter()`
- [ ] Unit test: all three worked examples (§6) should produce the documented verdicts
- [ ] Unit test: banned phrase list exhaustively checked against canonical examples
- [ ] Unit test: MDLG-02 inactive path (no somatic-activation emotion) returns `None` and weight redistributes correctly
