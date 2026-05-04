# TEACHER_DOCTRINE Atom Convention (2026-05-04)

**Status:** `proposal` / `pending wiring` — atoms authored under this convention are not yet loadable by `phoenix_v4/planning/enrichment_select.py`. A follow-up engineering PR is required to wire the persona-source lookup. See **Wiring requirements** below.

## What this establishes

A new on-disk convention for persona-source `TEACHER_DOCTRINE` atoms:

```
atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt
```

Each `CANONICAL.txt` contains 5 variant blocks (`v01`–`v05`), each teaching one named nervous-system mechanism in the persona's voice register. Variants are addressed by their incrementing header (`## TEACHER_DOCTRINE v01`, `v02`, ...) and selected by the renderer downstream of the enrichment-select layer.

This is the first `TEACHER_DOCTRINE/CANONICAL.txt` convention in the repo. No prior persona-source path existed for this slot type.

## Why

`phoenix_v4/planning/enrichment_select.py` (around line 1061) raises:

```
EnrichmentGapError: No enrichable content for slot TEACHER_DOCTRINE
(topic=anxiety chapter=2 slot_index=5).
Sources tried: persona=False, registry=False, teacher=False.
```

This error blocks rendering for `standard_book`, `extended_book_2h`, `deep_book_4h`, and `deep_book_6h` runtime formats. `TEACHER_DOCTRINE` is `section_06` in `phoenix_v4/planning/beatmap_compile.py` with a 460-word target in standard format. The registry-resolver fallback chain (`registry_resolver.py:59`) is `["COMPRESSION", "REFLECTION"]`, but the error indicates the registry source itself is also empty, so the persona source is the load-bearing path.

This convention closes the persona-source gap for the `gen_z_professionals` persona across the 5 highest-priority topics: `anxiety`, `burnout`, `imposter_syndrome`, `sleep_anxiety`, `financial_anxiety`.

## Schema

Each variant block:

```
## TEACHER_DOCTRINE v<NN>
---
mode: <SECULAR_BRIDGE | DOCTRINE_SECULAR_BRIDGE | MECHANISM_BRIDGE>
doctrine_source: <somatic | reserved>
mechanism: <false_alarm | spiral | comparison | overwhelm | shame>
weight: <standard | heavy>
carry_line: "<one-sentence takeaway, ≤140 chars, no em-dashes inside quoted string>"
---
<150–250 word body>
---
```

### Field allowed values

- **`mode`**:
  - `SECULAR_BRIDGE` — default for persona-source atoms; secular bridge between mechanism and lived experience.
  - `DOCTRINE_SECULAR_BRIDGE` — registry-source mode tag (per `enrichment_select.py:95`); reserved for atoms that bridge a doctrinal frame to secular language.
  - `MECHANISM_BRIDGE` — registry-source mode tag (per `enrichment_select.py:95`); reserved for atoms that bridge two named mechanisms.
- **`doctrine_source`**: `somatic` is the default for nervous-system / body-up framing. Other values reserved (e.g. `cognitive`, `relational`) for future expansion.
- **`mechanism`**: exactly one of the 5 mechanisms in the taxonomy below. Required.
- **`weight`**: `standard` (default, ~460 words at full body weight in standard format) or `heavy` (extended doctrinal weight; reserved for `deep_book_6h`).
- **`carry_line`**: ≤140 characters, no em-dashes inside the quoted string. The carry line is the one-sentence takeaway used by downstream compact-format renderers and TAKEAWAY/COMPRESSION fallbacks.

### Body rules

- 150–250 words strict.
- Names the mechanism explicitly (e.g. "the alarm system," "the prediction loop," "the comparison engine," "the working-memory budget," "the shame loop").
- Connects to a specific gen_z_professional context: Slack ping at 9:47 pm, LinkedIn promo announcement, Notion task list, 1:1 with manager, OKR check-in, Discord salary leak, comp band reveal, college roommate, cohort peer.
- Plain language. No clinical jargon. Translate any clinical term into ordinary speech ("your body's alarm system" rather than "autonomic dysregulation").
- Closes with what changes when the mechanism is seen / named. Does not promise resolution.
- 2nd-person address.

## Mechanism taxonomy

| mechanism | brief description |
| --- | --- |
| `false_alarm` | Body's alarm system firing in the absence of a real, present threat. The system reads pattern, not content. |
| `spiral` | Prediction loop / catastrophizing chain. Each link is treated as evidence for the next, even though every link past the first is invented. |
| `comparison` | Social-comparison engine measuring interior against peers' edited surface. Asymmetric input. |
| `overwhelm` | Working-memory / context-switch / open-loop overload. Capacity question, not a discipline failure. |
| `shame` | Secret conviction that you specifically are behind, faking it, or doing it wrong. Survives by being hidden. |

The 5 variants in each topic file map v01→v05 to these 5 mechanisms in the order shown above. Topics apply the mapped mechanism to that topic's specific anxiety surface.

## Voice anchor

`gen_z_professionals` register sources:

- `atoms/gen_z_professionals/<topic>/REFLECTION/CANONICAL.txt` — primary register anchor.
- `atoms/gen_z_professionals/<topic>/<mechanism>/CANONICAL.txt` — mechanism vocabulary anchor (e.g. `false_alarm/CANONICAL.txt`, `spiral/CANONICAL.txt`).

Permitted vocabulary anchors: Slack, LinkedIn, Notion, Discord, 1:1, OKR, standup, promo, comp band, cohort, peer, college roommate, deliverable, manager, bank app, 401k, equity.

Banned: boomer registers ("in my day"), millennial-cringe registers ("adulting"), clinical jargon ("autonomic dysregulation," "executive dysfunction," "HPA axis"), em-dashes inside `carry_line` quoted strings.

## Wiring requirements (follow-up engineering PR)

To make these atoms loadable, a follow-up PR must:

1. Extend `phoenix_v4/planning/enrichment_select.py` persona-source lookup to read from:

   ```
   atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt
   ```

   when `slot_type == "TEACHER_DOCTRINE"` and the persona-source flag is set.

2. Parse the file as 5 variant blocks delimited by `## TEACHER_DOCTRINE v<NN>` headers, with YAML-ish front-matter between `---` fences and free body text after the second `---`.

3. Map the variant `mode` field to the existing registry-source tuple lookup in `enrichment_select.py:95`:

   ```python
   "TEACHER_DOCTRINE": ("DOCTRINE_SECULAR_BRIDGE", "MECHANISM_BRIDGE")
   ```

   `SECULAR_BRIDGE` (default) should be treated as a persona-source override of either tuple member.

4. After wiring, the `EnrichmentGapError` raise site (around `enrichment_select.py:1061`) should report `persona=True` for any of the 5 backfilled topics under `gen_z_professionals`.

## Validation

After the wiring PR lands:

```bash
python3 scripts/registry/validate_variant_coverage.py --strict --persona gen_z_professionals
```

should now show `TEACHER_DOCTRINE` coverage for all 5 backfilled topics:

- `gen_z_professionals/anxiety`
- `gen_z_professionals/burnout`
- `gen_z_professionals/imposter_syndrome`
- `gen_z_professionals/sleep_anxiety`
- `gen_z_professionals/financial_anxiety`

End-to-end check: rendering `topic=anxiety chapter=2 slot_index=5` in `standard_book` format should no longer raise `EnrichmentGapError`. The renderer should select one of the 5 variants (selection rule lives in the wiring PR).

## Files added under this convention

- `atoms/gen_z_professionals/anxiety/TEACHER_DOCTRINE/CANONICAL.txt`
- `atoms/gen_z_professionals/burnout/TEACHER_DOCTRINE/CANONICAL.txt`
- `atoms/gen_z_professionals/imposter_syndrome/TEACHER_DOCTRINE/CANONICAL.txt`
- `atoms/gen_z_professionals/sleep_anxiety/TEACHER_DOCTRINE/CANONICAL.txt`
- `atoms/gen_z_professionals/financial_anxiety/TEACHER_DOCTRINE/CANONICAL.txt`

5 topics × 5 variants = 25 atom blocks total.
