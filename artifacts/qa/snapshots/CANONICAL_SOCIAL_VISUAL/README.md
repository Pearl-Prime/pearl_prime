# CANONICAL_SOCIAL_VISUAL — dormant golden snapshot (staged 2026-07-19)

**This directory is intentionally empty.** It is the target location for the
byte-frozen "golden" social-visual set (shortform MP4s + static/carousel
winners) once the operator approves the look packet at
`artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md`.

This mirrors the Pearl News sidebar capture-once-defend-forever pattern
(`artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html` +
`CANONICAL_SIDEBAR_METADATA.json`, defended by
`scripts/ci/check_pearl_news_sidebar_parity.py`).

## Do NOT populate this directory before operator approval

No agent should write `CANONICAL_SOCIAL_VISUAL_METADATA.json` or any golden
byte copies into this directory without an explicit operator go-ahead on the
LOOK_APPROVAL.md packet above. Populating early would freeze an unapproved
look as the permanent regression baseline — the operator would then be the
regression test twice (once at approval, again every time the machine wrongly
defends a look nobody signed off on).

## How the freeze happens (after approval, one-line step)

```bash
python3 scripts/social/freeze_social_visual_golden.py \
  --approved-set pilot \
  --confirm-operator-approved
```

This is a **populate-only** tool: it copies the approved MP4s + static/carousel
winners into this directory, records sha256 + dims/duration/bytes in
`CANONICAL_SOCIAL_VISUAL_METADATA.json`, and from that point on
`scripts/ci/check_social_visual_parity.py` stops skipping and starts defending
the frozen bytes on every run.

## Current state

- `CANONICAL_SOCIAL_VISUAL_METADATA.json`: **absent** (by design)
- Parity gate (`scripts/ci/check_social_visual_parity.py`): **exit 0 / SKIP**
  (dormant — no golden to defend yet)
- Freeze tool (`scripts/social/freeze_social_visual_golden.py`): **staged**,
  requires `--confirm-operator-approved` to run
