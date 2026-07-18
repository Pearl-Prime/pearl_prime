# Flagship parity check — lane 02

**Command:** `PHOENIX_OMEGA_REMOTE=local-override PYTHONPATH=. python3 scripts/ci/check_flagship_book_parity.py --snapshot ch1`
**Log:** `flagship_parity_ch1.log`
**Result:** ❌ FAILED in the current working tree (expected sha256 `d9d16ec8...`, 6,946
bytes; rebuilt sha256 `1e74b83b...`, 8,755 bytes).

## Root cause: pre-existing dirty-shared-tree drift, NOT this lane's edits

The frozen flagship golden is `gen_z_professionals × anxiety` (topic **anxiety**).
This lane's edits are scoped exclusively to **topic `burnout`** paths:

- `SOURCE_OF_TRUTH/accent_banks/wisdom_essence/burnout/entries.yaml` (new)
- `SOURCE_OF_TRUTH/accent_banks/author_commentary/burnout/lena_thorne/en_US.yaml` (new)
- `SOURCE_OF_TRUTH/accent_banks/author_commentary/burnout/ravi_chandra/en_US.yaml` (new)

None of these are read by an `anxiety`-topic render. `git status --short
SOURCE_OF_TRUTH/accent_banks/` at the time of this check shows the actual likely
cause — **other concurrent lanes' uncommitted edits already in this shared tree**,
predating this lane's work (per the conversation's initial git-status snapshot):

```
 M SOURCE_OF_TRUTH/accent_banks/author_commentary/anxiety/ravi_chandra/en_US.yaml
 M SOURCE_OF_TRUTH/accent_banks/external_stories/anxiety_entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/reflection_questions/anxiety/entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/troubleshooting/anxiety/entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/wisdom_essence/anxiety/entries.yaml
 M SOURCE_OF_TRUTH/accent_banks/wisdom_essence/boundaries/entries.yaml
```

These are exactly the accent-bank files a `gen_z_professionals × anxiety` ch1 render
consumes. This lane did not author or touch any of them. This is the documented risk
in `CLAUDE.md` / `INDEX.md`: "Local checkout is the dirty shared tree — READ surface
only, never a commit substrate." The offline-landing recipe (temp-index plumbing,
explicit-path `git add -f`) used by this lane stages **only** the 3 new burnout-scoped
files plus this lane's own proof/handoff paths — none of the anxiety-topic drift above
is included in this lane's offline commit, so the golden is not at risk from this
lane's land.

**Conclusion: no golden drift attributable to this lane. FLAGSHIP_PARITY=byte-identical
not verified as PASS in the ambient dirty tree (pre-existing unrelated drift present),
but the parity break is provably disjoint from this lane's diff.** Flagging this
drift to Pearl_GitHub / dispatcher for hygiene follow-up is appropriate; re-fixing it
is out of this lane's scope (owned by whichever lane modified the `anxiety` files).
