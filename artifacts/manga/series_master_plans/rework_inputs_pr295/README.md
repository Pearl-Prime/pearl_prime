# PR #295 arc plans — preserved REWORK INPUTS (Q-MPU-02 ruling)

**Source (credit):** branch `claude/manga-12ep-arc-authoring-egnwqf`, head
`4c6e2c3d59a9852a7196c44f2d22515c0ac1942b` (PR #295, draft — copied verbatim,
read-only absorb per the operator's Q-MPU-02 ruling of 2026-07-24: **REWORK
UNDER NEW CONTRACT, never merge #295**). Landed via manga process uplift Lane
06's PR so the content survives on main when the dispatcher closes #295 as
superseded (which only the dispatcher does, after Lanes 05+06 signals exist).

**What these are:** 20 structural planning files — `arc_plans/` (8 files:
en_US per-brand 4-arc / 48-episode block plans + index) and
`arc_plans_all_genres/` (12 files: full-taxonomy block plans + index + genre
assignment table). They are **PLANNING DELIVERABLES, not authored episodes**
(listing-as-story doctrine: none of this content enters a render queue).

**How they are consumed:** as migration inputs for Series Master Plan
upgrades per `docs/specs/MANGA_SERIES_MASTER_PLAN_CONTRACT.md` §Migration —
flagship-first (Q-MPU-01). First migration:
`../stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying.master_plan.yaml`
(from `arc_plans/en_US_iyashikei_batch_a.md` §stillness_press). Remaining
brands are migrated by the follow-on scale program (Lane 11 pilots the loop;
scale is out of Lane 06 scope).

**Do not** edit these files in place (they are a frozen source snapshot), do
not treat them as master plans (they predate the contract and use the 48-ep
4×12 frame — cadence in a master plan must be genre-derived from the pacing
yaml `arc_cadence` blocks, never a fixed 12), and do not delete them until
every brand they cover has a landed master plan.
