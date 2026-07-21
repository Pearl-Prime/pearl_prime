# FREE_TO_PAID_LADDER_V1_SPEC

Status: REFRESHED SPEC
Classification: REFRESH
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/FREE_TO_PAID_LADDER_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `17a766508b852075741b00317829fe45e3dc910933e63bf17e22d16ae27cf971`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

The ladder remains high-value, but it must now align with the current marketing
and release reality: the GHL feed is live, the first paid EPUB exists, the
deterministic social system has only a bounded dry-run PASS, and production
visual/social/video use is gated by licensing and operator approval.

## Reconcile, Do Not Rebuild

Extend existing marketing/feed machinery:

- `scripts/marketing/build_marketing_feed.py`
- Marketing Volume SSOT and feed artifacts
- deterministic social media dry-run system
- non-manga image inventory/license gates
- Pearl Animator faceless shorts spec for video derivatives

Do not introduce a second marketing feed or live publishing path.

## Refreshed Ladder Contract

Every ladder asset must record:

- source book/atom/exercise/story/artifact;
- whether it is free, lead-magnet, nurture, paid, or post-purchase;
- reader-state promise and next action;
- allowed channels;
- visual/image/video dependency status;
- proof path and release authorization status;
- no-live-publish flag until operator approval.

## Production Boundaries

- Deterministic social dry-run PASS does not authorize Metricool or live social
  posting.
- Image-bank availability does not authorize commercial use without license and
  operator gates.
- Faceless video specs do not authorize publication without separate video
  review and channel release.

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: feed schema validates and dry-run rows are generated
  with provenance and no public side effects.
- `OPERATOR_READ_PASS`: operator approves ladder sequence and channel mapping.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted by this spec.
