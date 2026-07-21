# Seam notes — tech_finance_burnout × burnout × overwhelm

## Fixed (in scope): leaked batch-generation metadata in STORY atoms (10 entries, v21–v30)

File: `atoms/tech_finance_burnout/burnout/STORY/CANONICAL.txt`. Identical defect
signature and fix method as the corporate_managers cell (see that cell's `NOTES.md`
for the full before/after example) — bolted-on `Wave2-NNN ... as an lived scene ...
cell-specific` tail removed, bodies rewritten as clean, grammatical, tech/finance-
grounded character studies (sprint board freeze, earnings model tab, on-call phone,
late subway platform, desk after market close, compliance checklist, code-review
queue, trading-floor exit, weekend Slack mute, Bloomberg terminal glow).

## Documented, NOT fixed: shared renderer ambient-detail template bug (catalog-wide, out of scope)

The Ch1/5/12 read surfaced a severe, repeated seam: the literal string **"soft
daylight along the sill"** (and structurally identical siblings — see the
healthcare_rns cell's read of the same bug family, e.g. *"The window holds cool
light over the window."*, *"A passing shadow at the sill holds steady moves through
the room."*) is used as ambient scene-detail filler and is frequently ungrammatical
or factually incoherent in context (daylight at 11 PM; "on soft daylight along the
sill"; ambient light through the sill inside a parking garage).

Traced to source: `config/rendering/environment_fallback_families.yaml` —
`window_reference` / light-detail families contain entries whose `text` field is
itself malformed, e.g. (verified in-file, line ~1419):

```yaml
- text: "The glass holds a softened outline at the frame holds steady."
  shape: object_led
  roots: ["window", "glass"]
```

The doubled predicate ("holds ... holds steady") and cross-scene reuse without regard
to time-of-day/interior-exterior logic is baked into the template data itself, not a
one-off render bug.

**Why not fixed here, even though it is squarely a "seam paragraph" style defect:**

1. **Not scoped to the 3 designated cells.** This file is shared, catalog-wide
   rendering infrastructure (`config/rendering/`), not `atoms/<persona>/<topic>/**`.
   The mission's WRITE_SCOPE restricts atom/seam edits to the 3 designated cells;
   this config is consumed by every persona/topic in the catalog, including personas
   and topics well outside this lane's remit.
2. **Golden-drift risk.** The frozen flagship golden (`gen_z_professionals × anxiety`)
   is explicitly protected ("do not touch... or atoms feeding them"). Confirmed via
   `grep` that the *exact* broken strings found in this render do **not** appear in
   `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt` today, but the underlying
   family (`window_reference` / light-detail) is generic enough that a persona-neutral
   edit could still change a *future* golden re-render's exact bytes and trip
   `check_flagship_book_parity.py` on an unrelated PR. Editing shared infra without a
   dedicated parity-gated lane is exactly the risk Lane 02 flagged for the C4 registry
   fix, and the same discipline applies here.

**Recommended fix (for a future dedicated lane, not claimed done here):** repair the
malformed `text:` entries in `config/rendering/environment_fallback_families.yaml`
(remove doubled predicates, gate light-based fillers by a scene's own established
time-of-day/interior flag instead of applying them unconditionally), then re-run
`check_flagship_book_parity.py --snapshot ch1` and `--snapshot book` to prove the
frozen golden is unaffected before landing. Likely Pearl_Dev-owned (rendering config,
not a content bank).
