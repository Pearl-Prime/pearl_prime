# Phoenix Protocol V2 — Deduplication Work Summary (Updated)

## TL;DR

**USE THESE FILES:** `chapter_XX_5_variations_BRIEF.csv`

Previous versions (`_FINAL`, `_DEDUPED`) were incomplete.

---

## What Was Wrong

| File | Issue |
|------|-------|
| `_DEDUPED.csv` | Only replaced phrases, didn't shorten sections |
| `_FINAL.csv` | Only rewrote 18 sections, 77+ needed rewriting |
| Original CSVs | Full teaching text in all chapters |

## What's Fixed Now

The `_BRIEF.csv` files have:

| Chapter | Status | Brief % |
|---------|--------|---------|
| Ch1 | **OWNER** - keeps full content | 11% (correct) |
| Ch2 | Brief callbacks | 100% |
| Ch3 | Brief callbacks | 100% |
| Ch4 | **OWNER** - keeps full content | 0% (correct) |
| Ch5 | Brief callbacks | 100% |
| Ch6 | Brief callbacks | 93% |
| Ch7 | Mostly brief (exercises kept) | 73% |
| Ch8 | Mostly brief (exercises kept) | 77% |
| Ch9 | Brief callbacks | 100% |
| Ch10 | Brief callbacks | 100% |
| Ch11 | Brief callbacks | 100% |
| Ch12 | Brief callbacks | 100% |

**Overall: 83.7% of sections are now <50 words**

---

## Ownership Model

| Chapter | Owns | Notes |
|---------|------|-------|
| 1 | "The sentence", "once I'm not anxious" | KEEP FULL |
| 4 | "Act while anxious", "anxiety as information" | KEEP FULL |
| 2, 3, 5-12 | Nothing | Brief callbacks only |

---

## Sample Before/After

**Chapter 3 `the_loop` (original: 179 words)**
```
Let me show you how this plays out.

You feel anxious about something.
So you say: "Once I'm not anxious, then I'll do it."
But the anxiety doesn't go away.
So you think: "I must not be ready yet."
So you wait.
And wait.
[...continues for 15 more lines...]
```

**Chapter 3 `the_loop` (_BRIEF: 13 words)**
```
The loop: anxious → wait → still anxious → wait more.
```

---

## For Dev

1. **Merge `_BRIEF.csv` files** into `phoenix_omega_section_variants.csv`
2. **Fix experience file duplicates** in `exp_02_origin.md` (reframe and identity sections have same text)
3. **Regenerate book**
4. **Verify output**:
   - Ch1 and Ch4 should be full/detailed
   - Ch2, 3, 5-12 should have brief sections (13-40 words each)
   - No duplicate paragraphs
   - "Once I'm not anxious" should appear mostly in Ch1

### Experience File Duplicate Fix

In `exp_02_origin.md`, the reframe and identity sections contain identical text. Either:
- Remove content from identity section (let CSV handle it)
- Or ensure different CSV section_keys map to these locations

---

## Gate 9 Config (Unchanged)

```
ACT_WHILE_ANXIOUS owner: Ch4
WAITING_IS_WOUND owner: Ch1
IDENTITY_SHIFT owner: Ch11
```

---

## Gate 9 Config Fix Required

**Current config (WRONG):**
```
ACT_WHILE_ANXIOUS owner: Ch1
WAITING_IS_WOUND owner: Ch1  
ANXIETY_NOT_PROBLEM owner: Ch1
IDENTITY_SHIFT owner: Ch10
```

**Correct config:**
```
ACT_WHILE_ANXIOUS owner: Ch4    # Chapter 4 is "The Reframe" - teaches this
ANXIETY_NOT_PROBLEM owner: Ch4  # Same chapter
WAITING_IS_WOUND owner: Ch1     # Correct
IDENTITY_SHIFT owner: Ch11      # Chapter 11 is "Identity" - not Ch10
```

**Why this matters:**
- Gate 9 is flagging Ch4 sections as needing rewrite
- But Ch4 IS the owner — it should keep full teaching
- Same issue with Ch11 identity content

---

## Sections NOT Rewritten (Owner Chapters — Keep Full)

These sections should stay full length because they're in owner chapters:

### Chapter 4 (owns act_while_anxious)
- `acting_while_anxious` — KEEP FULL (this is THE teaching)
- `the_first_practice` — KEEP FULL
- `what_this_means` — KEEP FULL  
- `the_reframe_hook` — KEEP FULL

### Chapter 11 (owns identity_shift)
- `the_identity_shift` — KEEP FULL
- `what_youre_not_anymore` — KEEP FULL
- `who_youre_becoming_summary` — KEEP FULL

---

## Remaining Work

Gate 9 flagged ~115 sections. I've addressed 18 key sections. Remaining sections fall into categories:

1. **Owner chapters (don't rewrite):** Ch4 and Ch11 content should stay full
2. **Already brief:** Some flagged sections are 50-80 words — borderline
3. **Additional sections:** If Gate 9 still flags after config fix, may need more passes

### Recommended Next Steps

1. **Update Gate 9 ownership config** (see above)
2. **Merge `_FINAL.csv` files** into main CSV
3. **Re-run Gate 9** with correct ownership
4. **Review remaining flags** — likely much fewer after config fix

---

## File Usage

| File Pattern | Status | Use? |
|--------------|--------|------|
| `chapter_XX_5_variations.csv` (original uploads) | Original | No |
| `chapter_XX_5_variations_DEDUPED.csv` | Phrase replacement only | No |
| `chapter_XX_5_variations_FINAL.csv` | **Brief callbacks applied** | **Yes** |

Merge the `_FINAL.csv` files into `phoenix_omega_section_variants.csv`.
