# Manga Release Runbook

## Release invariant

A release is a repeatable production operation, not the existence of one successful
local proof. `overall-manga-green=NOT_PROVEN` remains until the final integrator
verifies all scoped lanes and human approval.

## Preconditions

- current `origin/main` recorded
- required PRs merged
- story doctrine report passes
- planned/output trace passes
- raw or recovered layer semantics recorded
- structural gates pass
- lettering and layout reports pass
- proof packet current
- blind-read approval present
- queue/storage/retry environment checked

## Production environment

Record:

- queue backend and queue name
- GPU/Pearl Star endpoint class, never secret URLs
- storage root and retention policy
- artifact root
- retry budget
- timeout values
- operator identity
- source commit
- config snapshot hash

## Standard run

1. Resolve story and panel contracts.
2. Submit/render panels.
3. Preserve raw layer telemetry.
4. Run selected-component structural recovery when raw roles are not certified.
5. Fail panel on missing purity, quality, or support gates.
6. Compose pages/webtoon.
7. Run lettering/layout QA.
8. Build proof packet.
9. Run blind-read bar.
10. Release only after operator approval.

## Failure policy

### Failed render

- record job ID, panel ID, attempt, backend, and error
- retry only within the configured budget
- never substitute another panel silently

### Failed layer QA

- preserve raw layers and telemetry
- attempt selected-component recovery
- record recovery note and selected source layer
- block if no clean candidate exists

### Failed story doctrine

- return to manga_writer or manga_story_doctor
- do not repair by adding explanatory dialogue downstream

### Failed lettering

- block locale release
- do not silently change writing mode or locale
- record font/glyph fallback status

### Failed blind read

- return to manga_editor with scorecard evidence
- technical green remains technical only

## Rollback

A rollback restores:

- previous source commit
- previous config snapshot
- previous proof packet
- previous release manifest

Never delete failed evidence needed for diagnosis.

## Release checklist

- [ ] Queue accepted jobs repeatedly
- [ ] Retry policy demonstrated
- [ ] Storage paths writable and retained
- [ ] Logs include trace IDs
- [ ] Artifacts contain no secret/local home paths
- [ ] CI-safe tests do not require live GPU
- [ ] Live-only proof is labeled
- [ ] Operator approval present
- [ ] Rollback target recorded
