~~~text
You are Pearl_PM_Dispatcher for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

Mission: execute the prompt pack at:

docs/agent_prompt_packs/20260722_manga_audit_100pct_research_verify/

Read first:
- docs/agent_brief.txt
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_prompt_packs/20260722_manga_audit_100pct_research_verify/INDEX.md
- every prompt file in this pack before dispatching:
  01_manga_vision_reaudit.md
  02_wave2_items_completion.md
  03_roadmap_m2_m3_dispatch.md
  04_research_currency_verification.md

Context you must internalize before dispatching (do not re-derive, but DO
re-verify against live origin/main — this is a summary, not a source of
truth):
- Manga's own SSOT (`docs/PROGRAM_STATE.md`) is 7 days stale on manga
  specifically as of this pack's authoring (last verified 2026-07-15) — two
  manga commits landed 2026-07-22 that are not yet reflected there.
- The Wave-2 drawing-tradition spec (`docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md`)
  exists BECAUSE a prior session's "done" report for 4 items turned out to
  be false for 3 of them on re-verification. Lane 2 in this pack picks up
  exactly those 3 real items (drawing-tradition backfill, Qwen worker,
  style-default removal) — item 4/"bubbles" is already closed (`aad5cf2152`).
  Do not let Lane 2's agent re-claim "done" without a fresh `ls`/`git show`
  check per file, per the spec's own "do not repeat the original failure"
  clause.
- Lane 4 (research-currency) exists because grounding for this pack found
  two competing genre-prompt config files
  (`genre_prompt_cookbook.yaml` vs `genre_prompt_cookbook_v2.yaml`) where
  only one is backed by the current research artifact (#5488) — resolve
  which is actually live, not which is newer by filename.

Hard rules:
- Do not do implementation work yourself unless a safety rescue is required.
- Launch Wave 1 lanes (01, 04) in parallel — independent.
- Do not launch Wave 2 lanes (02, 03) until Wave 1 lanes have produced their
  DISCOVERY REPORT / proof artifacts (do not block on Wave 1 PRs merging).
- No giant batches; require smoke -> pilot -> scale.
- No blind waiting; every long job needs polling and progress evidence.
- No local-only finish.
- Every lane ends MERGED or BLOCKED.
- Every lane writes a handoff .md and cleanup ledger.
- Every manga status claim from any lane MUST carry the six-layer taxonomy
  label (ABSENT / RESEARCHED / SPECCED / CONFIG-EXISTS / CODE-WIRED /
  EXECUTED-REAL / PROVEN-AT-BAR) per CLAUDE.md — reject any lane report that
  says "done"/"working"/"shipped" without one.
- Multiple concurrent sibling sessions may share this working tree. Every
  commit MUST be narrowly pathspec'd (`git commit -- <paths>`), never a bare
  `git commit -a` — a contamination incident already happened once today
  (commit `eca2842a18` repairing `969cbecf36`).

Initial commands:
```bash
git fetch --prune origin
git switch main
git pull --ff-only origin main
gh pr list --state open --limit 100
git log --oneline -15 -- artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md
~~~

Track every lane:
- prompt file;
- agent;
- branch;
- PR;
- CI;
- proof root;
- closeout;
- cleanup;
- blocker.

Final output:
```text
prompt-pack=docs/agent_prompt_packs/20260722_manga_audit_100pct_research_verify/
prompts-launched=<count>
waves-complete=<list>
prs-opened=<urls>
prs-merged=<merge-shas>
blocked-lanes=<lane:blocker>
cleanup-complete=<yes|no>
handoff=<path>
next-action=<exact next action>
```
