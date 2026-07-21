# Flagship parity check — lane 03

**Command:** `PYTHONPATH=. python3 scripts/ci/check_flagship_book_parity.py --snapshot ch1`
**Log:** `flagship_parity_ch1.log`
**Result:** ❌ FAILED in the current working tree (expected sha256 `d9d16ec8...`,
6,946 bytes; rebuilt sha256 `d9d16a8b...`, 7,993 bytes).

## Root cause: pre-existing dirty-shared-tree drift, NOT this lane's edits

Identical finding to Lane 02's `lane02/FLAGSHIP_PARITY_NOTE.md`, re-verified fresh by
this lane. The frozen flagship golden is `gen_z_professionals × anxiety` (topic
**anxiety**). This lane's edits are scoped exclusively to **topic `burnout`**, in the
3 designated cells' own `STORY` atom banks:

- `atoms/corporate_managers/burnout/STORY/CANONICAL.txt`
- `atoms/tech_finance_burnout/burnout/STORY/CANONICAL.txt`
- `atoms/healthcare_rns/burnout/STORY/CANONICAL.txt`

None of these are read by a `gen_z_professionals × anxiety` render. `git status
--short SOURCE_OF_TRUTH/accent_banks/` at the time of this check shows the same
already-documented, still-uncommitted anxiety-topic drift from other concurrent lanes
that Lane 02 flagged yesterday:

```
 M SOURCE_OF_TRUTH/accent_banks/author_commentary/anxiety/ravi_chandra/en_US.yaml
 M SOURCE_OF_TRUTH/accent_banks/external_stories/anxiety_entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/reflection_questions/anxiety/entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/troubleshooting/anxiety/entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/wisdom_essence/anxiety/entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/wisdom_essence/boundaries/entries.yaml
```

These are exactly the accent-bank files a `gen_z_professionals × anxiety` Ch1 render
consumes. This lane did not author, touch, or stage any of them — `git status --short
atoms/corporate_managers/burnout/STORY/ atoms/tech_finance_burnout/burnout/STORY/
atoms/healthcare_rns/burnout/STORY/` confirms this lane's diff is exactly the 3
`CANONICAL.txt` files above, all `burnout`-topic.

**Conclusion: no golden drift attributable to this lane.** Same conclusion, same
provable-disjoint-diff method as Lane 02. This lane's offline landing (temp-index
plumbing, explicit-path `git add -f`) stages only the 3 burnout-scoped `STORY`
files plus this lane's own proof/handoff paths — none of the anxiety-topic drift
above is included in this lane's offline commit.

## Additional check: could the STORY atom fix touch a golden-fed atom?

`grep` confirmed the 3 edited files are outside `atoms/gen_z_professionals/anxiety/**`
entirely (different persona directory, different topic directory) — structurally
impossible for this edit to feed the `gen_z_professionals × anxiety` golden render
path. No further parity risk.
