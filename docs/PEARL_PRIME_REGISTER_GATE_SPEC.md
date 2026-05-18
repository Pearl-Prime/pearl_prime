# Pearl Prime Register Gate Spec

**Last updated:** 2026-05-18
**Owner:** Pearl_Architect (spec) → Pearl_Dev (implementation)
**Status:** DRAFT — calibrated against the 2026-05-18 ACCEPTANCE_VERDICT for the 2hr × ahjan × gen_z × anxiety book
**Authority:** `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` (4-layer acceptance stack — this gate operates between Layer 2 and Layer 3, catching the F1-F8 defects that machine gates currently miss)

---

## §1 Purpose

Close the loop between "all gates PASS" and "would not ship at trade-pub register." The 2026-05-18 calibration verdict (`artifacts/qa/ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md`) identified eight specific failure modes (F1-F8) that the existing gate stack misses. This spec defines a register gate that catches them automatically, so every render emits a verdict that reflects what a Pearl_Editor read would surface.

This gate does NOT replace Layer 3 (the human ONTGP read). It approximates 60-70% of what a Pearl_Editor would catch, so that Layer 3 reads happen only on books that pass machine register check — saving operator-time for the books that have a real chance at `system working`.

## §2 What this gate catches

The eight failure modes from the calibration verdict, mapped to detector dimensions:

| ID | Failure mode | Detector approach |
|---|---|---|
| **F1** | Templated mechanism-block repetition (3+ instances of the same structural-paragraph template, only mechanism-name and one anchor-detail varying) | Pairwise paragraph cosine-similarity within a book; clusters above threshold |
| **F2** | Broken slot-template fragments (sentences opening with lowercase noun phrase, dangling `:` with no content, paragraph ending in dangling preposition) | Sentence-start integrity check; punctuation-after-colon check; sub-3-word "sentence" check |
| **F3** | Off-doctrine teacher-bank content overrunning persona+topic substance | Per-teacher doctrinal-vocabulary allowlist + violation token-class set |
| **F4** | Verbatim closing-line repetition across chapters | Full-string match of last sentence per chapter |
| **F5** | Named-character continuity discontinuity | Cross-chapter named-entity recognition; rotation pattern check |
| **F6** | Pedagogical-cadence repetition (same sentence-length N-gram repeating across chapters at same structural position) | 4-gram of sentence-length sequences; cross-chapter match |
| **F7** | Over-prescribed practice density per chapter | Count distinct prescribed-action paragraphs |
| **F8** | Citation grafting (foreign credibility insertion) | Hard to fully automate; approximate via citation density vs trade-pub anchor density (requires anchor corpus, closed-loop step C) |

## §3 Detector specifications

### §3.1 F1 — Templated mechanism-block repetition

**Algorithm:**
1. Tokenize each paragraph (≥3 sentences) in the book.
2. For each paragraph, compute sentence-by-sentence cosine-similarity vector vs every other paragraph.
3. Pair-similarity = mean(sentence-level cosine similarities).
4. Pairs with similarity ≥ **0.75** form a cluster.
5. Cluster of size N:
   - N = 1: no concern
   - N = 2: **WARN** (one near-duplicate paragraph pair)
   - N ≥ 3: **FAIL** (repeated paragraph template)

**Calibration:** the Ch5/Ch11 mechanism-block triad in the calibration verdict reads at ~0.85 sentence-level similarity. Threshold 0.75 catches it without catching incidental similar-topic paragraphs.

**Output field in `register_gate_report.json`:**
```json
{
  "f1_templated_paragraph_clusters": [
    {
      "cluster_id": "f1_cluster_001",
      "paragraphs": [{"chapter": 5, "para_index": 8}, {"chapter": 5, "para_index": 14}, {"chapter": 11, "para_index": 10}],
      "shared_template": "The mechanism is X. This is what happens in the body of...",
      "similarity_mean": 0.87,
      "severity": "FAIL"
    }
  ]
}
```

### §3.2 F2 — Broken slot-template fragments

**Detection rules (any one → HARD FAIL the book; this is renderer-artifact protection):**

| Rule | Pattern | Example caught |
|---|---|---|
| `F2.A — colon-period-only` | `r":\s+\.($|\s)"` | `"Ahjan's reading of this is precise: ."` |
| `F2.B — sentence-end preposition` | `r"\b(with|of|by|to|for|on|in|from|the)\.$"` (case-insensitive) | `"In Ahjan's framework, the path begins with."` |
| `F2.C — sentence-start lowercase noun-phrase` | After `[\.\!\?]\s+` or `\n\n`, first word is lowercase AND is in the noun-list `{can, mechanism, attachment, suffering, the, this, that, a}` | `"mechanism running continuously is written..."` `"can explain the moment..."` |
| `F2.D — sub-4-word standalone paragraph` | Paragraph with `< 4 words` AND not a `## heading` | `"Ahjan's the practice"` (3 words) |
| `F2.E — colon followed by nothing or newline` | `r":\s*\n\n"` OR `r":\s*$"` (end of paragraph) | Slot-template dangling colons |

**Threshold:** any 1 instance = **HARD FAIL**. These are renderer artifacts, not author choices.

**Output field:**
```json
{
  "f2_broken_slot_fragments": [
    {"rule": "F2.A", "chapter": 5, "line": 369, "text": "Ahjan's reading of this is precise: ."},
    {"rule": "F2.B", "chapter": 1, "line": 7, "text": "In Ahjan's framework, the path begins with."}
  ],
  "f2_severity": "HARD_FAIL"
}
```

### §3.3 F3 — Off-doctrine teacher-bank overrun

**Per-teacher doctrinal vocabulary mapped from `SOURCE_OF_TRUTH/teacher_banks/<teacher>/doctrine/doctrine.yaml`:**

For each teacher, the doctrine.yaml `tradition` + `forbidden_claims` + `prohibited_outcomes` fields define the allowed-vs-forbidden vocabulary axes.

Example (ahjan — Tantric Buddhist):
- **Allowed tokens (no penalty):** `dharma`, `mindfulness`, `awakening`, `pratiyasamutpada`, `embodied`, `noticing`, `practice`, `mahayana`, `tantric`, `pali`, `ajahn` (honorific)
- **Forbidden tokens (each instance = WARN; >3 distinct tokens per chapter = FAIL):**
  - `Krishna`, `Bhakti`, `Vedanta`, `Sufi`, `Naqshbandi`, `Brahman` (other-tradition; tradition collision)
  - `Theravada`, `theravadan` (prohibited_outcomes per ahjan doctrine)
  - `transmission of light`, `enlightened ones`, generic-mystical phrases that don't match the doctrinal voice
  - `martial arts` (off-register for ahjan; flagged when teacher_wrapper inserts it generically)

**Algorithm:**
1. Load `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/doctrine.yaml`.
2. Extract `tradition`, `forbidden_claims`, `prohibited_outcomes` fields.
3. Build a forbidden-token regex from those.
4. Scan each chapter; count distinct forbidden tokens.
5. Per-chapter:
   - 0 tokens: no concern
   - 1-2 distinct tokens: **WARN**
   - 3+ distinct tokens: **FAIL** for that chapter
6. Book level: any chapter FAIL = book FAIL.

**Calibration:** Ch5 of the verdict book has `Krishna`, `Bhakti`, `Vedanta`-adjacent, `transmission of light` = 4+ distinct off-doctrine tokens → would FAIL. Ch11 has `path to liberation accessible to all`, `enlightened ones`, `martial arts`, `Love Beyond Self` = 4+ → would FAIL.

**Output:**
```json
{
  "f3_off_doctrine_violations": [
    {"chapter": 5, "tokens": ["Krishna", "Bhakti", "Vedanta", "transmission of light"], "severity": "FAIL"},
    {"chapter": 11, "tokens": ["enlightened ones", "martial arts", "path to liberation"], "severity": "FAIL"}
  ]
}
```

### §3.4 F4 — Verbatim closing-line repetition

**Algorithm:** extract the last non-empty sentence of each chapter; compute pairwise full-string match.

Threshold:
- 0 matches: no concern
- 1 match (2 chapters share closing): **WARN**
- 2+ matches: **FAIL**

**Output:**
```json
{
  "f4_closing_line_repeats": [
    {"chapters": [5, 11], "closing_line": "What remains is the moment after the alarm fires, when your body still wants to obey a prediction.", "severity": "WARN"}
  ]
}
```

### §3.5 F5 — Named-character continuity

**Algorithm:** named-entity recognition pass on each chapter's body prose (excluding dialogue speaker tags); extract distinct proper-name characters.

Pattern check:
- **PASS:** ≥ 60% of chapters share at least one named character (single-protagonist or stable ensemble) OR explicit cast-introduction in Ch1 names the full set used later.
- **WARN:** per-chapter rotation with no overlap (each chapter introduces fresh names without bridge).

**Output:**
```json
{
  "f5_named_character_map": {
    "chapter_1": ["Priya"],
    "chapter_5": ["Amara"],
    "chapter_11": ["Chris", "Jordan", "Nia"]
  },
  "f5_overlap_ratio": 0.0,
  "f5_severity": "WARN"
}
```

### §3.6 F6 — Pedagogical-cadence repetition

**Algorithm:** for each paragraph, extract a 4-gram of sentence lengths (e.g. `[7, 5, 12, 8]`). Look for 4-grams that appear in 3+ paragraphs across the book.

Threshold:
- 0 repeated 4-grams: PASS
- 1-2 repeated: WARN
- 3+ repeated: FAIL

**Calibration:** the "The variables are real. The stakes are genuine. The uncertainty is not manufactured by your anxiety. It is manufactured by the conditions." block appears in Ch1, Ch5, Ch11 with the same sentence-length 4-gram (~6, 6, 11, 8). 3 instances → would FAIL.

### §3.7 F7 — Over-prescribed practice density

**Algorithm:** count distinct prescribed-action paragraphs per chapter. Heuristic: a paragraph is "prescribed-action" if it contains ≥ 1 second-person imperative verb AND ≥ 1 timing cue or step number.

Threshold per chapter:
- 0-2 distinct practices: PASS
- 3 distinct: WARN
- 4+: FAIL

**Calibration:** Ch1 has 3 (cyclic sighing, 90-sec writing, Friday-4pm ledger) → would WARN.

### §3.8 F8 — Citation grafting (deferred; needs anchor corpus)

This is the dimension that requires `artifacts/reference/trade_pub_anchors/` (closed-loop step C). Without it, citation density comparison has no baseline.

Provisional threshold (until anchors land): any citation that names a specific external researcher/institution (Stanford, Harvard, Berkeley, etc.) AND appears WITHOUT an embedded narrative beat earning it → WARN.

Marked as "advisory only" until step (C) completes.

---

## §4 Aggregate verdict from register gate

Per the scorecard's status language, the register gate produces:

| Combined severity | Register verdict | Maps to scorecard status |
|---|---|---|
| 0 FAIL, 0 WARN | **REGISTER PASS** | combines with Layer 1+2 → `authored candidate` viable |
| 0 FAIL, ≤ 2 WARN | **REGISTER ADVISORY** | candidate but flagged for Layer 3 attention on specific dimensions |
| 0 FAIL, ≥ 3 WARN | **REGISTER WARN** | book is rough; Layer 3 verdict recommended before claiming `authored candidate` |
| ≥ 1 FAIL | **REGISTER FAIL** | book is not `authored candidate`; route to specific failure-mode lane per §5 |
| F2 HARD_FAIL | **REGISTER HARD_FAIL** | renderer-artifact leak; do NOT advance to Layer 3; route to renderer fix |

**Production rule:** under `--quality-profile production`, REGISTER FAIL or HARD_FAIL halts shipping. REGISTER WARN allows shipping with explicit operator override (logged to `operator_decisions_log.tsv`). REGISTER ADVISORY ships with a flag in the closeout.

---

## §5 Failure routing — which lane fixes which dimension

When register gate fires, the verdict MD MUST name the specific lane for each F-finding:

| F | Lane | Why |
|---|---|---|
| F1 (templated paragraph repetition) | Pearl_Editor + Pearl_Writer (atom diversification) OR Pearl_Dev (renderer dedupe extension) | Could be bank monotony (atom) or render-time stamping (renderer) |
| F2 (broken slot fragments) | Pearl_Dev (renderer slot-fill validation) | Renderer leaking unfilled slots; must validate every slot is filled before commit |
| F3 (off-doctrine overrun) | Pearl_Dev (TEACHER-MODE-WRAPPER-SEMANTICS-01 impl) + Pearl_Editor (teacher_bank atom doctrine compliance audit) | The cap-entry rule is real; impl ws must land |
| F4 (closing-line repetition) | Pearl_Dev (overlay or composer closing-line uniqueness check) | One-line fix at the composer |
| F5 (named-character discontinuity) | Pearl_Architect (decision on roster strategy) + Pearl_Editor (story_atom roster updates) | Design decision; once locked, content follows |
| F6 (cadence repetition) | Pearl_Editor + Pearl_Writer (atom variety in pedagogical-cadence atoms) | Bank variety problem |
| F7 (over-prescribed practices) | Pearl_Architect (per-chapter practice-density cap) + Pearl_Editor (atom routing) | Design decision on practice cardinality per chapter |
| F8 (citation grafting) | Pearl_Editor (atom audit) + Pearl_Architect (citation-pattern policy) | Needs anchor corpus before measurable |

---

## §6 Implementation skeleton

### §6.1 New file: `phoenix_v4/quality/register_gate.py`

```python
"""
Register gate — closes the loop between Layer 1+2 machine gates and Layer 3
human ONTGP read. Catches F1-F8 failure modes from the 2026-05-18 ACCEPTANCE
VERDICT calibration.

Reads: book.txt + quality_summary.json + chapter_flow_report.json + the
running teacher's doctrine.yaml.

Emits: register_gate_report.json with per-F detector findings and the
aggregate verdict (PASS / ADVISORY / WARN / FAIL / HARD_FAIL).
"""

from dataclasses import dataclass
from pathlib import Path
import re, yaml, json

@dataclass(frozen=True)
class RegisterGateResult:
    verdict: str  # PASS / ADVISORY / WARN / FAIL / HARD_FAIL
    findings: dict  # per-F detector outputs
    suggested_lanes: list[str]  # routing recommendations

def evaluate_register(
    book_path: Path,
    teacher_doctrine_yaml: Path,
    persona_id: str,
    topic_id: str,
    quality_profile: str = "production",
) -> RegisterGateResult:
    ...  # implementation per §3.1-§3.8
```

### §6.2 Integration with existing pipeline

In `scripts/run_pipeline.py`, after the existing gates emit, add:

```python
register_result = evaluate_register(
    book_path=Path(out_dir) / "book.txt",
    teacher_doctrine_yaml=Path(f"SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/doctrine/doctrine.yaml"),
    persona_id=persona_id,
    topic_id=topic_id,
    quality_profile=quality_profile,
)
# Write to register_gate_report.json
# Aggregate into quality_summary.json as gates.register_gate
# Under production profile, HARD_FAIL halts shipping; FAIL halts; WARN logs
```

### §6.3 Aggregator: `ship_readiness` verdict (closed-loop step E)

`ship_readiness = structural_gates_PASS AND register_gate ∈ {PASS, ADVISORY} AND scorecard_layer_1_2_PASS`

Where:
- `structural_gates_PASS` = Layer 1 from scorecard (chapter_flow + bestseller_craft + ei_v2 + scene_anchor_density + transformation_arc + book_pass + book_quality_gate all PASS)
- `register_gate` = this gate's verdict
- `scorecard_layer_1_2_PASS` = aggregate of structural + advisory checks

Books that pass `ship_readiness` are eligible for Layer 3 sample review. Books that don't are routed to the F-specific lanes per §5.

---

## §7 Test coverage requirements

The Pearl_Dev impl must include tests that:

1. **F1 regression:** synthesize a 3-paragraph block where only the noun varies; assert F1 cluster detected with severity FAIL.
2. **F2 regression:** insert each of F2.A-F2.E patterns into a test book; assert HARD_FAIL for each.
3. **F3 regression:** use the actual 2026-05-18 verdict book.txt as a positive test — assert Ch5 and Ch11 both flagged FAIL on F3.
4. **F4 regression:** craft a 2-chapter book where Ch1 and Ch2 share the closing line; assert WARN. Add Ch3 with same closing; assert FAIL.
5. **F5 regression:** synthesize a 3-chapter book with rotating named characters; assert WARN.
6. **F6 regression:** synthesize 3 paragraphs with the same sentence-length 4-gram; assert FAIL.
7. **F7 regression:** chapter with 4 distinct prescribed-action paragraphs; assert FAIL.

**Calibration assertion:** apply the gate to `artifacts/pearl_prime/extended_book_2h/ahjan_gen_z_professionals_anxiety_en_US_20260518T131809Z_round5/book.txt`. Expected verdict: **REGISTER FAIL** (per the 2026-05-18 calibration). If the gate passes that book, the thresholds are too lenient.

---

## §8 Cross-references

- Scorecard: `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`
- Calibration verdict: `artifacts/qa/ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md`
- Cap entries: TEACHER-MODE-WRAPPER-SEMANTICS-01 (F3 enforcement); BESTSELLER-INJECTIONS-MANDATORY-01 (named-character roster — F5)
- Anchor corpus (step C — needed for F8): `artifacts/reference/trade_pub_anchors/` (operator picks; not yet on disk)
- Implementation workstream: `ws_register_gate_implementation_20260518` (Pearl_Dev — to be opened by Pearl_PM after this spec lands)
- Aggregator workstream: `ws_ship_readiness_aggregator_20260518` (Pearl_Dev — closed-loop step E; depends on register gate impl landing first)

---

## §9 Out of scope (this spec)

- F8 (citation grafting) full automation — deferred until anchor corpus lands
- Layer 4 system-level benchmark — operator-time blind-10; not gate-able
- Voice / stylistic register matching against trade-pub anchors at sentence level — would require LLM-based comparison; out of scope under CLAUDE.md no-paid-API rule. (Possible future work via Pearl Star local-LLM for register classification, but the F1-F7 detectors are non-LLM and catch the bulk of defects.)
- Visual / image rendering quality (manga lane; separate gate set)
- TTS audio register for audiobooks (separate spec)

---

## §10 Change log

- 2026-05-18: initial draft authored as part of closed-loop step (D). Calibrated against the 2026-05-18 ACCEPTANCE VERDICT (step A). Implementation routed to Pearl_Dev via `ws_register_gate_implementation_20260518`. Aggregator routed to Pearl_Dev via `ws_ship_readiness_aggregator_20260518` (gated on impl landing). Once impl + aggregator land, every production render emits `register_gate_report.json` and the `ship_readiness` verdict feeds back into Layer 3 sampling decisions.
