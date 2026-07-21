# Seam notes — healthcare_rns × burnout × overwhelm

## Fixed (in scope): leaked batch-generation metadata in STORY atoms (7 entries, v24–v30)

File: `atoms/healthcare_rns/burnout/STORY/CANONICAL.txt`. Identical defect signature
and fix method as the other 2 cells (see corporate_managers cell's `NOTES.md` for the
full before/after pattern) — rewritten as clean, grammatical, healthcare-grounded
character studies (nurses' station desk, break-room microwave, EHR login screen,
handoff whiteboard, supply closet light, overnight hallway, charge-nurse phone).

## Documented, NOT fixed: two renderer-level defects (catalog-wide / cross-cutting, out of scope)

### 1. Ch5 mid-sentence truncation

`book.txt` line 426 (in the sampled prior manuscript) ends: *"The signal makes more
sense once the context is"* — no period, no continuation, mid-clause. This reads as a
section-join or depth-enrichment boundary bug in the renderer (a section was cut
before its intended closing clause was appended), not a content-atom problem — there
is no single atom file to "fix" here; the defect is in how sections are stitched.
Composer/wiring-adjacent; out of this lane's banned-lever scope. Flagged for Pearl_Dev.

### 2. Broken `window_reference` / light-detail ambient template family

Same root cause as documented in the tech_finance_burnout cell's `NOTES.md`
(`config/rendering/environment_fallback_families.yaml`) — confirmed present in this
manuscript too:

- L1009: *"The glass holds a softened outline at the frame holds steady. is a clock
  concept — you know it changed because the windows got dark."* (missing subject,
  doubled predicate)
- L1013: *"A passing shadow at the sill holds steady moves through the room. through
  the room window."* (duplicate broken phrase, also seen in Ch5 lines 375/379 of this
  same manuscript, and in the tech_finance_burnout cell's manuscript — confirmed
  shared, catalog-wide renderer config, not persona-specific content)

Not fixed here for the same reason given in the tech_finance_burnout cell's notes:
shared infra outside `atoms/**`, golden-drift risk, needs its own parity-gated lane.

## Cross-cell corroboration

These are the *second and third* independent sightings (across 2 of the 3 designated
cells, different personas) of the exact same broken `environment_fallback_families.yaml`
template family — this is strong evidence the defect is genuinely systemic rendering
infrastructure, not noise. Recommend the future fix lane treat this as a confirmed
priority alongside Lane 02's C4 registry finding.
