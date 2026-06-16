# Content-Length Targets — routed to the writing program (REAL length, never padding)

**Date:** 2026-06-13 · **From:** Pearl_Research (platform-duration strategy) · **To:** the writing program (Pearl_Writer / Pearl_Prime bestseller pipeline)
**Why:** `DURATION_GAP_VERIFICATION.md` proves we ship **no product that wins the flagship paid-book surfaces** — books render thin (~5k) to gold (~22k), and every paid-book platform's full-length norm needs more. That is a **content-length** problem (the writing program's job), not a config edit. These are the per-platform writing targets.

> **This is a ROUTE, not a config mutation.** The format registry already defines these word_targets (`deep_book_6h` word_range `[50000, 72000]`, `deep_book_4h` `[20000, 40000]` — owned by PR #1550, NOT edited here). The ask is **which format to author for which surface**, and **closing the thin-render shortfall so renders actually hit target.**

---

## The one priority: a real 52k-word "Complete" flagship

| Priority | Target word_target | Format (existing) | Tier | Wins (the $-maker surfaces) |
|---|--:|---|---|---|
| **#1 (do this first)** | **52,000** (band 45–63k) | `deep_book_6h` | **T7 Complete** | Audible 5–7 hr **+** KDP 150–230 pp **+** Spotify 4–6 hr **+** Apple/Google full AI audiobook — *simultaneously* |
| #2 (entry full-audiobook) | 30,000 | `deep_book_4h` | T6 Long-Form | Audible 3–5 hr tier; lower-mid KDP |
| (already shipping) | 22,000 | `standard_book` | T5 | a **podcast season** (8–10 ep) — NOT a standalone audiobook |
| (already shipping) | 3.5–9k | micro/short | T1–T4 | podcast episodes, KDP short-read funnels, lead-magnets |

**Until a real 52k-word T7 exists, we have nothing to list as a full Audible audiobook or a full KDP self-help book.** That is the single highest-leverage content move in the catalog.

---

## Persona modifier (CDIS §10.2 — apply on top of the flagship target)

| Persona band | Flagship word_target | Audiobook | Rationale |
|---|--:|--:|---|
| millennial_women / gen_x / corporate / tech_finance / entrepreneurs | **52–63k** | 5.8–7 hr | commute/session-aligned; bestseller median [A4] |
| working_parents | ~48k | 5.3 hr | chore-aligned, clean chapter breaks |
| gen_z_professionals / healthcare_rns / first_responders | **45k** | 5.0 hr | under-3–5 hr tolerance; still clears Audible floor |
| gen_alpha_students | (do not target flagship) | — | micro/podcast only; 9 min/day reading budget |

Chapter length 20–25 min (millennial/corporate) to 10–15 min (gen_z/shift workers) — the audiobook chapter is the session unit.

---

## CJK content-length (PROVISIONAL — gate on a measured render)

| Locale | Flagship word_target (EN-equiv) | Why it differs | Confidence |
|---|--:|---|---|
| **ja-JP** | ~52k (lands in band) | 52k×2.15 = 111.8k 文字 ÷ 300 文字/分 = 6.2 hr; in the 4–6 hr ja self-help band + 80–120k 文字 ebook band | ja expansion **measured**; rate **hard-sourced** [C8][C9] |
| **zh** (CN/TW/SG) | **higher: ~65–95k** | 52k→~83k 字 is BELOW the 100–150k 字 zh self-help ebook norm [C3]; zh wants MORE. (Audio = Ximalaya **episodic** 15–20 min, not one long file) | zh 1.6 expansion **UNVERIFIED — measure first** |
| **ko-KR** | T7 full **+** T1–T3 summary | ship BOTH a Welaaa full edition AND a Millie 15–30 min summary edition | ko 2.0 + 자/分 rate **UNVERIFIED — measure first** |

**Do not author CJK flagship word_targets as final until one zh + one ko render is measured on Pearl Star** (CosyVoice2 currently off). ja can proceed (anchored).

---

## The hard rule: REAL length, never padding

The reason to be long is **read-through revenue** (KU pages-read, Audible/Spotify completion-weighted payout, Kobo Plus). **Padding destroys the very thing it's trying to capture** — a 52k book padded to length completes at 40% and earns *less* than a tight 45k book at 90% [S6]. So:

- ✅ **Earn the length:** more distinct arcs, deeper scene/story/exercise development, integration/dwell beats (the operator's #1 craft concern — see memory `integration_pacing_priority`), genuinely additional teaching — content that sustains **≥70% completion** (the universal platform signal).
- ❌ **Never:** repeat phrasing, stretch sentences, inflate with filler, restate to hit a number. The duration audit already flagged thin renders HARD_FAIL the word_count_gate (#1550 honesty spine) — the fix is to fill with real content, not to relax the gate.

**Concrete blocker to close:** the §5B finding — catalog `標準書籍` books render ~5.2k words against a 22k target. Before chasing 52k, the writing program must close the **target-vs-render shortfall** on the tiers we already have, then extend the spine to the 52k flagship. Diagnosis of why renders fall short of target is a writing-program task (depth-fill / enrichment / multi-arc authoring), out of Pearl_Research's lane.

---

## Hand-off

- **Owner:** writing program (Pearl_Writer English prose via Claude subagents per memory `qwen_vs_pearl_writer`; Pearl_Prime bestseller pipeline).
- **Input:** the targets above (already expressible via the registry's `word_target`/`fill_regime`).
- **Gate:** operator approves the platform-strategy/tier→platform routing (this research) → writing program targets the flagship 52k → CJK after a measured render.
- **Not Pearl_Research's lane:** authoring books, editing the format registry, or diagnosing the render-shortfall mechanism.
