# Operator Score Capture — Wave-2 Blind-10 (EMPTY)

**Status:** blank — operator fills after reading. Agents must not invent scores.
**Approved:** OPD-W2-BLIND10-01 (operator: blind-10 read approved).
**Do not open** `MANIFEST.tsv` or `KEY_SEALED.md` until all 10 rows below are filled.

Reading copies (anonymized): `/tmp/blind10_reading_copies_20260718/Book_01.epub` … `Book_10.epub`
Canonical blank sheet (same rubric): `SCORING_SHEET.md`

## Rubric (fill per book)

| Field | Meaning |
|-------|---------|
| Felt assembled? | `yes` = seams/templates visible (bad). `no` = reads as authored whole (good). |
| Sit next to trade-pub? | `yes` / `no` — same shelf as Body Keeps Score / Waking the Tiger / Myth of Normal / What My Bones Know. |
| Strongest / Weakest | Free-text, 5–15 words each. |

Minimum sample per book: **Ch1 + Ch6 + Ch12** (~15–20 min). Read order: Book_01 → Book_10.

### Polarity for system math (use this sheet, not a mental shortcut)

- `felt_assembled_pass_rate` = count of **"no"** on Q1 / 10 — PASS when ≥ 7/10
- `shelf_next_to_trade_pub_pass_rate` = count of **"yes"** on Q2 / 10 — PASS when ≥ 6/10
- BOTH → SYSTEM PASS · ONE → SYSTEM WARN · NEITHER → SYSTEM FAIL

Even a SYSTEM PASS on this packet is Layer-4 evidence about the **Layer-1 structurally clear** shipping stream — not proof of Layer-3 `system working` (still 0) and not a claim that agents may invent.

---

## Per-book scores (operator only)

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

## System-level verdict (after all 10)

felt_assembled_pass_rate: ___/10   (count of **no** on Q1)

shelf_next_to_trade_pub_pass_rate: ___/10   (count of **yes** on Q2)

Combined verdict: ___________________   (PASS / WARN / FAIL)

## Optional 5-axis (1–5) — not required for Layer-4 math

| # | Book ID | Emotional Pull | Clarity | Memorability | Practicality | Identity Shift |
|---|---------|----------------|---------|--------------|--------------|----------------|
| 1 | Book_01 |                |         |              |              |                |
| 2 | Book_02 |                |         |              |              |                |
| 3 | Book_03 |                |         |              |              |                |
| 4 | Book_04 |                |         |              |              |                |
| 5 | Book_05 |                |         |              |              |                |
| 6 | Book_06 |                |         |              |              |                |
| 7 | Book_07 |                |         |              |              |                |
| 8 | Book_08 |                |         |              |              |                |
| 9 | Book_09 |                |         |              |              |                |
| 10 | Book_10 |               |         |              |              |                |

## After scoring (Step 4+)

1. Open `KEY_SEALED.md` only now.
2. Write `artifacts/qa/BLIND_10_VERDICT_<YYYY-MM-DD>.md` per `docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md` Step 6.
3. Label honestly: input pool = Layer 1 `structurally clear`; SYSTEM_WORKING_CELLS=0.
