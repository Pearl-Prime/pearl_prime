# Pearl Prime Book Quality Gate — pilot notes

This pilot documents the deterministic **Pearl Prime Book Quality Gate** (`phoenix_v4/quality/book_quality_gate.py`) wired from `scripts/run_pipeline.py`. It writes `book_quality_report.json` next to `quality_summary.json` (spine and registry paths) or under the atom render directory; production (`--quality-profile=production`) exits non-zero when `release_band` is **Reject**.

## Policy string (canonical)

The gate emits the following policy text in the report (`policy` / `policy_statement` fields):

> Reject Pearl Prime manuscript output if it contains any internal artifact leakage, any obvious broken prose, any repeated 25+ word block, or any chapter with more than two unresolved mode jumps. Hold for revision if artifact-clean but scene-furniture repetition, weak chapter function, unstable voice, or cyclical progression. Pass only when the book reads as one authored therapeutic experience with low repetition, clean transitions, clear chapter purpose, and felt progression from recognition to possibility.

## What is checked

| Area | Deterministic? | Notes |
|------|----------------|-------|
| Artifact leakage | Yes | Builds on `delivery_contract_gate()` plus YAML regex bundle (slot lines, `##` assembly headers). |
| Verbatim duplicate paragraphs (25+ tokens) | Yes | Normalized paragraph rolling hash; `refrain_allowlist_normalized` in YAML. |
| Broken prose | Yes | Doubled words, orphan very short lines, clipped fragments, inline ` --- ` merge tails, register phrases. |
| Chapter function / mode jumps | Mixed | **Slot sequences:** if `chapter_slot_sequence` is passed (atom render), unresolved jumps use a fixed allowed-transition set. **Otherwise:** paragraph “modes” and bridge heuristics; rejects if **more than one chapter** exceeds **two** unresolved jumps, or a short chapter (&lt;800 words) shows **more than five** distinct structural modes. |
| Voice-register (somatic_first) | Yes | Early-chapter spiritual token ratio (frame lexicon), YAML doctrine markers, academic starters. |
| Scene-furniture repetition | Yes | Stem list per ~10k-word window; cross-chapter spread for **phrase-length** stems only. |
| Soft rubrics | Yes | 0–2 scores per dimension from word patterns and sentence stats — **no LLM**. |

## Known limitations

- Paragraph taxonomy and “unresolved jump” bridging are **heuristic** when slot sequences are absent (spine / registry path).
- `Chapter N` subtitles on the same line as the heading are stripped as one line; multi-line titles between `Chapter N` and body may be treated as a short first paragraph (can trigger orphan-line noise on edge layouts).
- Runtime policy: `micro_book_15` and `micro_book_20` default to **Reject** unless `--book-quality-override` is set (then other gates still apply).

## Sample output schema

See `book_quality_report.json` in this directory (generated from a small clean fixture). Top-level keys include: `policy`, `runtime_format`, `release_band`, `hard_gates`, `soft_rubrics`, `book_averages`, `chapters`, `repeated_blocks`, `scene_furniture`, `mode_jump_findings`, `fail_reasons`, `hold_reasons`, `pass_reasons`, `thresholds_used`, `config_version`, `frame`, `policy_override`, `runtime_policy_block`.

## Anxiety corpus (`artifacts/qa/pearl_prime_ahjan_genz_anxiety_all_runtimes.txt`)

Classification with the **implemented gate** (`frame=somatic_first`, `policy_override=true` so policy-only micro rejects are visible alongside content gates):

| Runtime id | Release band | Notes |
|------------|--------------|-------|
| `micro_book_15` | **Reject** | Doctrine/voice + broken prose + scene furniture + duplicates (see report fail list). |
| `micro_book_20` | **Reject** | Same pattern class; additional fail reasons on longer text. |
| `short_book_30` | **Reject** | At current YAML thresholds, soft rubric + scene-furniture signals contribute to Reject (not only Hold). |

Re-run locally with `pytest tests/test_book_quality_gate.py` (includes an optional full-corpus spot check when the QA file is present).
