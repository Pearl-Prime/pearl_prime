# 05 — Final audit lane (Wave 4, run after each wave's writer PRs merge)

Paste into a fresh session after every scale wave (not just once at the very
end — this is a per-wave QA checkpoint per
`docs/PROMPT_ROUTER_OPERATING_MANUAL.md` SS8's wave model, plus one final
program-level pass after the last wave). Part of the pack at
`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/`.

## EXECUTE

Do not stop at "spot-checked, looks fine." Produce a written audit artifact
and an operator look-packet; that is the deliverable.

## STARTUP_RECEIPT

```
AGENT:              Pearl_PM (QA/audit posture)
TASK:               re-verify a merged manga-48ep writer wave; produce operator look-packet
PROJECT_ID:         proj_manga_catalog_reconciliation_20260426
SUBSYSTEM:          manga_pipeline (read + QA artifacts only)
AUTHORITY_DOCS:     00_MASTER_DISPATCH_PROMPT.md; MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md;
                    CLAUDE.md Manga Vision-Conformance Doctrine (six-layer taxonomy)
READ_PATH_COMPLETE: <confirm yes>
WRITE_SCOPE:        artifacts/qa/manga_48ep_3catalog_look_packet_<catalog>_<wave>.md;
                    artifacts/coordination/handoffs/
OUT_OF_SCOPE:       editing any chapter_script/arc_storyboard file (findings
                    only; rework happens in the writer lane, not here)
PROVENANCE:         none (bugfix/audit-class -- verification, not new capability)
BLOCKERS:           requires the wave being audited to have a merged PR
READY_STATUS:       ready once a wave has merged
```

## Mission

1. For every cell merged in the wave being audited, re-run (do not trust the
   writer lane's self-report):
   - `PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py --chapter-script <path>` per episode
   - `PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py --arc-plan <path>` per episode
   - `PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py --story-handoff <path> --chapter-script <path> --production` per episode
2. Sample at least 3 episodes per catalog (more for larger waves) and manually
   read them against the `tests/fixtures/manga/story_excellence/block/*`
   failure-mode list (mention-only props, no-cost portals, generic healing,
   stats-only sports, poster-not-relationship social issues, tourist-Japan
   default, flattened-to-US-or-PRC register). Write up any near-misses even if
   the automated gate passed — the gate catches the worst failures, not every
   craft problem.
3. Produce an operator look-packet (per Router SS16 — a read-approval captured
   once per catalog, then frozen as the quality bar) at
   `artifacts/qa/manga_48ep_3catalog_look_packet_<catalog>_<wave>.md`: 2-3
   full episodes rendered as plain readable text (not raw YAML) for the
   operator to read start-to-finish, plus your audit findings.
4. Label every finding on the six-layer manga taxonomy (CLAUDE.md Manga
   Vision-Conformance Doctrine) — gate-PASS is `authored_candidate` at best,
   never `bestseller` or `PROVEN-AT-BAR` without an operator blind-read.

## Landing + signal

This is a read-mostly lane but still needs a handoff and a durable artifact —
commit the look-packet + audit findings as their own small PR (docs/artifacts
only, no code changes) or attach to the writer wave's PR if still open.
Signal: `manga48-qa-wave-<n>-<catalog>=<full-SHA>`.

## CLOSEOUT_RECEIPT

Name every episode audited, every gate re-run, every finding (even "no
issues found" is a finding, stated explicitly, not implied by silence).
NEXT_ACTION: point back to the master prompt's next wave, or flag specific
cells for rework before the next wave proceeds.
