# Duration Correctness — Recommendations

**You decide; I recommend.** Each fix is tied to its marketing-expectation impact. Items needing a Pearl_Architect spec or config change are flagged.

---

## The one decision that resolves ~80% of this

**Re-derive every format's advertised duration from its real word target — don't shrink the books.**

The books are gold-quality and the right length for their value. The defect is that `duration_minutes` is a hand-set label disconnected from the word count and from the 150 WPM the product actually ships at. Replace the single hand-set number with a **derived pair**:

```
audiobook_minutes = round(word_target / 150)     # intended TTS pace (config + OVERLAY §413)
ebook_minutes     = round(word_target / 230)     # reading edition
```

where `word_target` is the format's real production target (cap for `standard_book`, floor-band for `deep_book_6h`, midpoint for the rest). Store **both** on each format; advertise the one matching the edition (audiobook listing vs ebook listing).

**Marketing impact:** the advertised number stops under-promising the audiobook by up to 2.6×. A buyer who sees "≈1 hour" and gets 2h23m is a refund/▼-review risk *even though longer is "more value"* — the expectation mismatch is the problem, not the length. Honest "≈2h20m, deep session" converts better to the audiobook buyer than a wrong "1 hour."

→ **Needs a Pearl_Architect spec:** a `duration_derivation` rule + `format_registry.yaml` schema change (replace `duration_minutes: N` with `audiobook_minutes` / `ebook_minutes`, or add a derivation function the registry loader applies). This is the primary deliverable.

---

## Per-format recommendation

Fix options: **(1)** adjust word cap · **(2)** fix wpm math (re-derive label) · **(3)** re-advertise honestly · **(4)** accept within tolerance.

| format | listening gap | my pick | new audiobook label | rationale |
|---|---|---|---|---|
| **standard_book** | **+161%** | **(2)+(3)+(1)** | **55 → ~143 min** | The big one. Re-derive label to ~2h20m. Also raise cap 20k→**22k** (1) so the systematic +7.6% render stops tripping the gate — or accept it; either way the label is what's broken. |
| compact_5ch_15min | +78% | (2)+(3) | 15 → ~27 min | Re-derive. Optionally rename ("~25-min reset"). |
| compact_5ch_20min | +72% | (2)+(3)+(1) | 20 → ~34 min | Re-derive; give cap +5% headroom (19% tip over). |
| micro_book_15 | +68% | (2)+(3) | 15 → ~25 min | Re-derive. |
| compact_8ch_30min | +58% | (2)+(3)+(1) | 30 → ~48 min | Re-derive; cap +5% headroom (21% tip over). |
| micro_book_20 | +49% | (2)+(3) | 20 → ~30 min | Re-derive. |
| short_book_30 | +43% | (2)+(3) | 30 → ~43 min | Re-derive. |
| extended_book_2h | +24% | (2)+(3) | 120 → ~150 min | Re-derive (NOTE band; modest but worth fixing in the same pass). |
| deep_book_4h | −11% | **(4)** accept | keep 240 | Within tolerance; runs slightly short. Honest enough. |
| deep_book_6h | +2% | **(4)** accept | keep 360 | Within tolerance. The model format. |

**Pattern:** option (2)/(3) — fix the label — applies to 8 of 10. Option (1) — cap change — is a secondary cleanup for `standard_book` (raise to 22k) and the two narrow-range compacts (+5% headroom). Option (4) — accept — for the two deep formats.

---

## Secondary items

### A. The 10 stub formats have no duration contract
`five_min_practice, pocket_guide, ten_things_to_do, symptom_to_action_atlas, daily_text_audio_companion, crisis_cards, weekly_challenge_pack, faq_audiobook, myth_vs_mechanism, protocol_library` carry **only `chapter_count_default`** — no `word_range`, no `duration_minutes`. They cannot advertise a duration honestly (or be QA'd for it) until both are added.
→ **Needs config:** add `word_range` + derived `audiobook_minutes`/`ebook_minutes` to each before they ship. **Recommend:** block these from any catalog listing that advertises a duration until populated.

### B. Stop the cap-creep masking pattern
`standard_book`'s cap was raised 13k→18k→20k to absorb gold renders while the 55-min label never moved. **Recommend a guardrail:** when a format's `word_range` changes, CI requires the derived duration label to be recomputed in the same PR (so words and minutes can never drift apart again).
→ **Needs config/CI:** extend `pr_governance_review.py` (or the duration scorecard gate) with a "word_range changed ⇒ duration must be re-derived" check.

### C. Wire the 150 WPM constant into ONE place
Today 150 lives in `duration_scorecard.yaml` (measurement only) and the label lives, unrelated, in `format_registry.yaml`. The derivation function should read the single `tts_wpm` constant so the label and the adherence scorecard can never disagree.
→ **Needs spec:** single-source the WPM constant; derivation + scorecard both consume it.

### D. CJK duration is unmeasured
Apply none of these English WPM numbers to `ja-JP/zh-TW/zh-CN/ko-KR`. Character-count duration math + locale narration rates needed.
→ **Recommend:** a follow-up CJK duration audit (separate, char-based) before CJK catalog scale-up.

### E. Confirm Mode 1 per format (optional rigor)
Render inflation (1.073) is measured on `standard_book` only. A one-book-per-format **dry-run-assembly pass** (depth-fill + render, deterministic, no LLM) would confirm the per-format overshoot for the other 9. Mode 2 needs no such pass.

---

## What needs a Pearl_Architect spec vs a config change

| item | type | owner |
|---|---|---|
| `duration_derivation` rule (words/150 listen, words/230 read) | **spec** | Pearl_Architect |
| `format_registry.yaml`: `duration_minutes` → `audiobook_minutes`/`ebook_minutes` | **config + schema** | Pearl_Architect → config |
| `standard_book` cap 20k→22k; compact +5% headroom | **config** | config |
| Stub formats: add `word_range` + derived durations | **config** | config |
| CI guardrail: word_range change ⇒ re-derive duration | **CI** (`pr_governance_review.py`) | Pearl_Architect |
| Single-source `tts_wpm` for label + scorecard | **spec** | Pearl_Architect |
| CJK char-based duration audit | **follow-up audit** | Pearl_Prime |

---

## Recommended sequence

1. **Decide the per-format labels** (table above) — operator sign-off on the new advertised minutes.
2. **Pearl_Architect specs** the `duration_derivation` rule + registry schema change.
3. **Config PR:** new derived durations for all 10 specced formats + cap tweaks; populate the 10 stubs.
4. **CI guardrail** so words/minutes can't drift again.
5. **CJK audit** before any CJK duration claims ship.

Net: one schema change + one derivation rule fixes the systematic Mode-2 gap across the catalog; two cap tweaks clean up Mode 1; a CI rule prevents recurrence.
