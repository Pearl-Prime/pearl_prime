# Blind-10 Scoring Sheet — BLANK, ready for operator

**Do not fill this in before reading `HOW_TO_RUN.md` and `READ_ORDER.md`, and
do not open `KEY_SEALED.md` or `MANIFEST.tsv` until every row below is filled.**

Per `docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md` Step 3. Two yes/no questions
+ 2 free-text per book.

- **Felt assembled?** = could you sense the seams; did this read like it was
  generated paragraph-by-paragraph from templates rather than authored as a
  whole. (`yes` = it felt assembled — that is a bad sign; `no` = it read as
  authored — that is a good sign. Mirrors the guide's convention.)
- **Sit next to trade-pub?** = would you place this book on the same physical
  shelf as *Body Keeps Score* / *Waking the Tiger* / *Myth of Normal* / *What
  My Bones Know*. Be honest.

| # | Book ID | Felt assembled? (yes/no) | Sit next to trade-pub? (yes/no) | Strongest dimension (5–15 words) | Weakest dimension (5–15 words) |
|---|---------|---------------------------|----------------------------------|-----------------------------------|----------------------------------|
| 1 | Book_01 |                           |                                  |                                    |                                  |
| 2 | Book_02 |                           |                                  |                                    |                                  |
| 3 | Book_03 |                           |                                  |                                    |                                  |
| 4 | Book_04 |                           |                                  |                                    |                                  |
| 5 | Book_05 |                           |                                  |                                    |                                  |
| 6 | Book_06 |                           |                                  |                                    |                                  |
| 7 | Book_07 |                           |                                  |                                    |                                  |
| 8 | Book_08 |                           |                                  |                                    |                                  |
| 9 | Book_09 |                           |                                  |                                    |                                  |
| 10 | Book_10 |                          |                                  |                                    |                                  |

## System-level verdict (compute after all 10 rows are filled)

- `felt_assembled_pass_rate` = (count of **"no"** on Q1, i.e. did NOT feel
  assembled) / 10 — PASS at this layer when ≥ 7/10
- `shelf_next_to_trade_pub_pass_rate` = (count of **"yes"** on Q2) / 10 —
  PASS at this layer when ≥ 6/10
- Combined verdict: BOTH thresholds met → **SYSTEM PASS** · ONE met →
  **SYSTEM WARN** · NEITHER met → **SYSTEM FAIL**

_____________________________  ______________
felt_assembled_pass_rate: ___/10   shelf_next_to_trade_pub_pass_rate: ___/10

Combined verdict: ___________________

---

## Optional supplementary axes (5-axis, 1–5 scale)

Per `docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md` Step 3. Not required for the
Layer-4 verdict math above; useful extra signal if you have time.

| # | Book ID | Emotional Pull (1-5) | Clarity (1-5) | Memorability (1-5) | Practicality (1-5) | Identity Shift (1-5) |
|---|---------|----|----|----|----|----|
| 1 | Book_01 |    |    |    |    |    |
| 2 | Book_02 |    |    |    |    |    |
| 3 | Book_03 |    |    |    |    |    |
| 4 | Book_04 |    |    |    |    |    |
| 5 | Book_05 |    |    |    |    |    |
| 6 | Book_06 |    |    |    |    |    |
| 7 | Book_07 |    |    |    |    |    |
| 8 | Book_08 |    |    |    |    |    |
| 9 | Book_09 |    |    |    |    |    |
| 10 | Book_10 |   |    |    |    |    |

## Routing notes (fill after unsealing `KEY_SEALED.md`)

Cluster weakest-dimension notes; if the same weakness shows up 4+ times,
route per the operator guide's Step 5 table (F1/F2/F3/F4/F5/F7 / anchor
corpus). Protect strongest-dimension patterns appearing 4+ times.

