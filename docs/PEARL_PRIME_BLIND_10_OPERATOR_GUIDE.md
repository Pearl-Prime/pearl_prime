# Blind-10 Operator Guide — Pearl Prime System-Level Benchmark

**What this is:** the operator-attended step (F) of the closed loop. The acceptance scorecard's Layer 4. The thing that prevents the gates from gradient-descending into "passes all checks but feels generated."

**Why operator-only:** Layer 1-3 are machine + agent + Pearl_Editor sample. Layer 4 is YOUR taste, blind. Cannot delegate. Cannot automate. This is the only step in the closed loop where the human oracle is structurally irreplaceable.

**How often:** every 10 books rendered, OR quarterly minimum, whichever first.

**How long:** ~3-5 hours of operator-attended reading per blind-10 cycle.

---

## Step 1 — Identify the 10 books to blind-read

Take the 10 most recently rendered production-profile books from `artifacts/pearl_prime/`. Don't cherry-pick; the point is to sample the actual output stream the system is producing.

```bash
ls -t artifacts/pearl_prime/*/*round*/book.txt 2>/dev/null | head -10 > /tmp/blind_10_queue.txt
cat /tmp/blind_10_queue.txt
```

That's your queue. Don't sort, don't curate, just read in order.

## Step 2 — Read each book blind

**"Blind" means:**
- Don't read the verdict MDs or gate reports BEFORE the read
- Don't check which persona × topic × teacher it is
- Don't check the production date
- Just read

**You can read at any speed:** skim or deep. The point is to form an impression of each book on its own terms.

**Minimum:** read Chapter 1 + Chapter 5 or 6 + Chapter 11 or last. ~15-20 minutes per book. The same sampling protocol Pearl_Editor uses at Layer 3.

**Maximum:** end-to-end deep read. ~1-2 hours per book if you have time.

The Blind-10 verdict doesn't require the full read of each book — but you must read AT LEAST the 3-chapter sample. If you only have time to skim 1-2 books deeply, do those AND skim-sample the other 8.

## Step 3 — Score each book on the two-question rubric

After each book, fill in the row in the scorecard. Two yes/no questions per book + 2 free-text:

```
| # | Book ID                                      | Felt assembled? | Sit next to trade-pub? | Strongest dimension                  | Weakest dimension                     |
|---|----------------------------------------------|-----------------|------------------------|--------------------------------------|---------------------------------------|
| 1 | ahjan_gen_z_professionals_anxiety_..._round5 | yes / no        | yes / no               | "Priya scene specificity"           | "templated mechanism repetition"      |
| 2 | ...                                          | yes / no        | yes / no               | ...                                  | ...                                   |
```

**"Felt assembled"** = could the reader sense the seams; did this read like it was generated paragraph-by-paragraph from templates rather than authored as a whole.

**"Sit next to trade-pub"** = would you place this book on the same physical shelf as Body Keeps Score / Waking the Tiger / Myth of Normal / What My Bones Know. Be honest. Most current Pearl Prime renders will get a NO on this.

**Free-text dimensions:** brief — 5-15 words each. The patterns across the 10 are the data; one book's note is just one signal.

## Step 4 — Compute the system-level verdict

After all 10 are scored:

| Metric | Calculation | Threshold |
|---|---|---|
| `felt_assembled_pass_rate` | (count of "yes" on Q1) / 10 | ≥ 7/10 = **PASS** at this layer |
| `shelf_next_to_trade_pub_pass_rate` | (count of "yes" on Q2) / 10 | ≥ 6/10 = **PASS** at this layer |

**Combined verdict:**
- BOTH thresholds met → **SYSTEM PASS** at bestseller-register layer
- ONE threshold met → **SYSTEM WARN** — direction is right but at-scale shipping isn't safe yet
- NEITHER threshold met → **SYSTEM FAIL** — the factory is producing delivery-grade not bestseller-register; tuning required

## Step 5 — Route the findings

Cluster the WEAKEST DIMENSION notes from the 10 rows. If the same weakness shows up 4+ times across the blind-10, that's a system-level pattern → routes to:

| Weakness pattern | Lane |
|---|---|
| "templated repetition" / "I've read this paragraph" | Register gate F1 + Pearl_Editor bank diversification |
| "slot fragments" / "broken sentences" | Register gate F2 + renderer fix |
| "off-doctrine content" / "wrong tradition for this teacher" | Register gate F3 + Pearl_Editor teacher_bank audit |
| "same closing across books" / "everything reads the same" | Register gate F4 + composer fix |
| "no consistent characters" | Register gate F5 + Pearl_Architect roster decision |
| "feels lecture-y" / "too many instructions" | Register gate F7 + Pearl_Architect practice-density cap |
| "doesn't sound like a real person wrote this" | Anchor corpus update + register gate threshold recalibration |

The STRONGEST DIMENSION notes are equally important: anything appearing as a strength 4+ times tells you which atom-bank / pipeline-stage is producing your best output. Protect it.

## Step 6 — Commit the verdict

Write the verdict as `artifacts/qa/BLIND_10_VERDICT_<YYYY-MM-DD>.md`. Template:

```markdown
# Blind-10 Verdict — <date>

## Books sampled
1-10. (paste the queue from Step 1)

## Per-book rubric
(paste the rubric table from Step 3, filled in)

## System-level verdict
- felt_assembled_pass_rate: X/10
- shelf_next_to_trade_pub_pass_rate: Y/10
- Combined: PASS / WARN / FAIL

## Top patterns
- Weakest dimension top-3 (with counts):
  - "..." (N/10)
  - "..." (N/10)
- Strongest dimension top-3 (with counts):
  - "..." (N/10)

## Routing
- Pattern → lane (per Step 5)

## Anchor corpus refresh decision
- Did anchors hold their place as the register comparator? yes/no
- Add new anchors? Drop existing? Note here.

## Next-cadence note
- When the next blind-10 should run (every 10 books OR end of <month>)
```

Commit + push as a single small PR. The verdict MD becomes input to the next register-gate calibration cycle.

---

## Time budget realism

| Mode | Per-book time | Total for 10 |
|---|---|---|
| Skim (3-chapter sample only) | 15 min | ~2.5 hours |
| Read (3-chapter sample + careful) | 25 min | ~4 hours |
| Deep (whole book) | 60-90 min | 10-15 hours |

Default to skim/read. Deep is for the rare case where a book might be your first SYSTEM PASS — then read it through to confirm.

---

## What you DON'T do during blind-10

- Don't fix anything mid-cycle. The whole point is to capture the system's current output without intervening.
- Don't reread a book after seeing its gate report. Once you've seen the report, you're not blind anymore.
- Don't skip books because "I already know that one is rough." Read it anyway; data point matters.

---

## Cross-references

- Scorecard: `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` Layer 4
- Register gate: `phoenix_v4/quality/register_gate.py` + `docs/PEARL_PRIME_REGISTER_GATE_SPEC.md`
- Anchor corpus: `artifacts/reference/trade_pub_anchors/`
- Closed-loop plan: `docs/PEARL_PRIME_BOOKS_VISION_AND_DELIVERY_AUDIT.md`
- Latest single-book verdict: `artifacts/qa/ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md`

---

## When to run the FIRST blind-10

**Right now is fine** — there are enough books in `artifacts/pearl_prime/` to sample. The 2hr ahjan book is one of them; the other 9 are whatever else is on disk. The first blind-10 will set the baseline; future ones measure drift.

Alternatively: defer until 10 NEW books have been rendered post-register-gate-impl. That gives you a baseline against books that the register gate could have caught issues on. Either choice is valid; pick based on appetite.

---

## Operator: when you're ready, this can fit in one afternoon. The Blind-10 is the closed-loop's only operator-time-mandatory step — everything else can be automated or delegated. This one cannot. It's worth the 3-4 hours.
