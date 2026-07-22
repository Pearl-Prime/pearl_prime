# zh-CN Wave 1 — Shard 06 Skip Report

20 atoms attempted, 10 accepted, 10 skipped. All 20 source atoms are
`compassion_fatigue` topic across `nyc_executives`, `healthcare_rns`,
`tech_finance_burnout`, and `entrepreneurs` persona pools.

## Accepted (10) — committed to `locales/zh-CN/CANONICAL.txt`

- `atoms/nyc_executives/compassion_fatigue/PIVOT/CANONICAL.txt`
- `atoms/nyc_executives/compassion_fatigue/INTEGRATION/CANONICAL.txt`
- `atoms/nyc_executives/compassion_fatigue/EXERCISE/CANONICAL.txt`
- `atoms/tech_finance_burnout/compassion_fatigue/false_alarm/CANONICAL.txt`
- `atoms/tech_finance_burnout/compassion_fatigue/shame/CANONICAL.txt`
- `atoms/tech_finance_burnout/compassion_fatigue/spiral/CANONICAL.txt`
- `atoms/tech_finance_burnout/compassion_fatigue/comparison/CANONICAL.txt`
- `atoms/tech_finance_burnout/compassion_fatigue/REFLECTION/CANONICAL.txt`
- `atoms/entrepreneurs/compassion_fatigue/watcher/CANONICAL.txt`
- `atoms/entrepreneurs/compassion_fatigue/spiral/CANONICAL.txt`

All 10 pass `structural_validator.py` (`ok: true`, zero reasons) and
`script_contamination.py` (`OK`, zero findings) after one hand-repair pass
each (see "Repairs applied" below). All 10 were additionally hand-checked
per the cross-shard coordinator note (shard 04, PR #101) for drift off the
`glossary_project.yaml`-locked term for "compassion fatigue" (共情耗竭) —
DashScope's raw output drifted to 同情疲劳 (atoms 02/16/19) and 共情疲劳
(atoms 08/09/14) in dozens of instances; all instances were corrected to
the locked 共情耗竭 before commit. This drift was NOT caught by
`structural_validator.py`'s glossary avoid-list check, because
`glossary_project.yaml`'s avoid list for this term only lists the
Traditional-script forms (同情心疲勞/慈悲疲勞), not the Simplified
colloquial drift forms — this is a real gap in the avoid-list coverage,
not just a DashScope quality issue (see "Tooling gaps found" below).

### Repairs applied (hand-fix, no extra DashScope call)

- Glossary avoid-list violations: `身份` used for the English "identity"
  (self-concept) sense — reworded to the locked `自我认同` per
  `glossary_core.yaml`. Affected: PIVOT (via EMBODIMENT block, not
  ultimately committed — see below), false_alarm, shame, spiral,
  comparison, REFLECTION, watcher, spiral(entrepreneurs).
- One missing trailing `---` delimiter (DashScope dropped it):
  `false_alarm/CANONICAL.txt` MECHANISM_PROOF v07.
- Leftover untranslated English fragments DashScope left mid-sentence
  ("spiraling", "elaboration", "exhausting", "reclaim") in
  `entrepreneurs/compassion_fatigue/spiral/CANONICAL.txt` — reworded to
  natural zh-CN. These were NOT caught by the `untranslated_english`
  structural check because the check only fires when an entire block's
  stripped body is ascii-only; a block that is mostly CJK with a few
  stray English words embedded passes that check silently. Flagging this
  as a validator gap as well.
- Locked-term drift (`同情疲劳` / `共情疲劳` → `共情耗竭`), see above.

## Skipped (10) — NOT committed, no zh-CN file written

### A. Validator limitation: `duplicate_header_ids` false-positive (3 atoms)

- `atoms/nyc_executives/compassion_fatigue/watcher/CANONICAL.txt`
- `atoms/nyc_executives/compassion_fatigue/overwhelm/CANONICAL.txt`
- `atoms/nyc_executives/compassion_fatigue/grief/CANONICAL.txt`

These are large STORY-shape atoms where the same `## RECOGNITION vNN`
header (v01..v05) is deliberately reused across 5 different story
instances, each distinguished only by a `path:` frontmatter value (e.g.
5 different `RECOGNITION v01` blocks with different `path:` and
`COST_INTENSITY:` values). This shape is present **identically in the
English source** — confirmed by running `parse_blocks()` directly against
the English source: it reports the exact same 5x duplicate header IDs the
candidate does. `structural_validator.py`'s `duplicate_header_ids` check
does not compare source-vs-candidate duplication count, it just flags any
duplicate in the candidate outright — so this atom shape can never pass
regardless of translation quality. Translation was completed and
faithfully preserves header identity/order 1:1 with source (verified);
only the ok:true gate fails. Recommend: `structural_validator.py`'s
duplicate check should be reason-relaxed when the source has the exact
same duplicate multiset (i.e. only flag duplicates *introduced* by the
candidate, not duplicates inherited from source). Draft translations for
these 3 exist at the shard's working files if a maintainer wants to
recover them once the validator is patched; not committing them
per-instructions ("no hand-patch to force pass").

### B. Source content is a stub / has no prose (3 atoms)

- `atoms/nyc_executives/compassion_fatigue/COMPRESSION/CANONICAL.txt`
- `atoms/healthcare_rns/compassion_fatigue/COMPRESSION/CANONICAL.txt`
- `atoms/tech_finance_burnout/compassion_fatigue/COMPRESSION/CANONICAL.txt`

All three `COMPRESSION` shape atoms contain only
`## COMPRESSION vNN` / `---` / `compression_family: CN` / `---` blocks —
zero prose body across all ~30 variants in each file. There is nothing to
translate; the `compression_family: CN` value is an enum-like identifier,
not translatable content. This matches the known "EN-source-corrupted
atoms" backlog (see `docs(qa)` commit `386bf02bef`, "atom authoring
backlog for EN-source-corrupted atoms (650 rows)"). Reporting as a source
blocker per instructions ("if the English source is malformed, report the
blocker rather than inventing missing meaning") rather than inventing
placeholder prose.

### C. Source is genuinely malformed / corrupted (4 atoms)

- `atoms/tech_finance_burnout/compassion_fatigue/overwhelm/CANONICAL.txt`
- `atoms/tech_finance_burnout/compassion_fatigue/grief/CANONICAL.txt`
- `atoms/entrepreneurs/compassion_fatigue/overwhelm/CANONICAL.txt`
- `atoms/entrepreneurs/compassion_fatigue/INTEGRATION/CANONICAL.txt`

The first three share an identical corruption pattern: `path:` frontmatter
values are human-readable titles instead of real paths (e.g.
`path: The portfolio that's too big`), and the block "body" is literally
just the next header's label text (e.g. a `RECOGNITION v01` block's body
is the literal string `RECOGNITION v02`) rather than real prose — there is
no actual sentence content to translate in these blocks at all.

`INTEGRATION/CANONICAL.txt` (entrepreneurs) has a different but equally
real corruption: `## INTEGRATION v02` and `v04` headers have empty bodies
between their opening and closing `---`; `## INTEGRATION v07`'s opening
`---` delimiter is missing entirely (header line runs straight into
`integration_mode: BODY-LANDED` with no delimiter); and `v05`/`v06`/`v07`
each appear **twice** in the same file with genuinely different content
and even a different frontmatter key convention the second time
(`integration_mode` → `mode`, `BODY-LANDED` → `BODY_LANDED`), separated by
a stray, contentless `---\n\n---\n\n---` block — evidence of two different
generation runs concatenated into one file.

None of these four are translatable as-is without inventing missing
meaning. Reporting as source blockers per instructions.

## Tooling gaps found (for coordinator / Lane 00 owner)

1. `structural_validator.py`'s `duplicate_header_ids` check has no
   source-comparison escape hatch for atoms whose *English source* itself
   legitimately reuses a header ID across multiple story instances
   (distinguished by `path:`/frontmatter, not by header). Affects at least
   3 atoms in this shard alone; likely affects every persona's
   `watcher`/`overwhelm`/`grief` STORY-shape atom pool sharing this
   generation template.
2. `structural_validator.py`'s `untranslated_english` check is
   block-granular and only fires when an *entire* block is ascii-only —
   it misses a handful of English words left stranded inside an otherwise
   fully-translated CJK paragraph (confirmed real case in this shard).
3. `glossary_project.yaml`'s avoid-list for "compassion fatigue" only
   lists Traditional-script variants (同情心疲勞/慈悲疲勞), so the
   Simplified colloquial drift forms DashScope actually produces
   (同情疲劳, 共情疲劳) are not caught by
   `structural_validator.py`'s glossary check at all — this exactly
   matches the shard-04 cross-shard finding surfaced mid-task and is
   confirmed independently here (found in 6 of this shard's 10 accepted
   atoms, dozens of instances, before manual correction).
