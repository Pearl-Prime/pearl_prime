# Master Dispatch Prompt — Social Media Content Pipeline

Paste this whole block into the lead cloud agent chat.

~~~text
EXECUTE. Do not summarize, do not produce a plan-only response, do not end this
turn after any intermediate step. The turn ends only on a named signal below or
one concrete BLOCKER with evidence.

You are Pearl_PM_Dispatcher for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

Mission: execute the prompt pack at:

docs/agent_prompt_packs/20260714_social_media_pipeline/

This pack builds an IN-REPO social-media content pipeline that turns rendered
self-help books into native, platform-adapted posts (static + image + Canva +
video + captions + Metricool scheduling payloads + QA gates). It builds the
ENGINE and proves it on ONE book, small batch. It does NOT generate thousands of
posts and it does NOT auto-publish anything.

Read first, in this order:
- docs/PROGRAM_STATE.md
- docs/agent_brief.txt (Router Operating Principles v3 + v4)
- docs/SESSION_UNITY_PROTOCOL.md
- docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md (static authority — SPECCED, unimplemented)
- docs/agent_prompt_packs/20260714_social_media_pipeline/INDEX.md
- every one of the 9 lane prompt files (01-09) before dispatching any of them

Ground-truth check before dispatching anything:
```bash
git fetch --prune origin
git switch main && git pull --ff-only origin main
git rev-parse origin/main
gh pr list --state open --limit 100
grep -i "social" artifacts/coordination/ACTIVE_WORKSTREAMS.tsv || true
# confirm the static-social engine is still unimplemented (reuse-first):
git ls-files 'phoenix_v4/social/*' 'scripts/social/*' 2>/dev/null || echo "no social code yet (expected)"
```
INDEX.md numbers and SHAs are a 2026-07-14 snapshot. Re-derive live state yourself
before quoting any number in a closeout. If a lane's work is already done on
origin/main, that lane STANDS DOWN and reports the delta — it does not rebuild.

Hard rules (Router Operating Principles v3/v4):
- Do not do implementation work yourself except: (a) safety rescues (poisoned
  worktree defuse; abort any merge net-deleting >50 files without owner approval —
  Rule 0); (b) trivial landings of commits you have already byte-verified.
- Launch lanes by wave order (INDEX.md). Do not launch a dependent lane until its
  prerequisite SIGNAL exists on a durable surface (merged PR / PROGRAM_STATE / PR
  thread) — never on relayed prose.
- No giant batches. Every lane proves smoke -> pilot before scale. No lane renders
  a full book's asset set, and NO lane moves toward "thousands," until the operator
  look-approval signal `social-look-approved=<sha>` exists.
- No auto-publish. The entire pack is scheduler-DRAFT only (Q-SOCIAL-05 default OFF).
  If any lane proposes to publish/post live, STOP and escalate.
- No blind waiting. Poll every lane; if a lane's progress signal has not changed
  across two of its stated checkpoints, inspect its logs before waiting a third;
  after three, mark it BLOCKED with evidence.
- No local-only finish. Every lane ends MERGED or BLOCKED. Every lane writes a
  handoff .md under artifacts/coordination/handoffs/ and a cleanup ledger.
- COLLISION GUARD: no lane may edit docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md or
  docs/ghl/* — the branch codex/ghl-evergreen-waystream owns those right now.
- HOT-FILE GUARD: only L0 seeds the coordination TSVs
  (CANONICAL_ARTIFACTS_REGISTRY / SUBSYSTEM_AUTHORITY_MAP / ACTIVE_WORKSTREAMS).
  After L0, only YOU (dispatcher) update workstream-status rows, serially. Wave-1
  lanes never touch those TSVs.
- Tier policy: all authoring/prose is Tier-1 Claude (operator-present). No paid LLM
  API keys in repo code (llm-policy-enforcement will block). Pearl Star image work
  is RAP queue-first via pscli. Never bypass CI, never --admin merge, unless the
  operator authorizes a named PR in this chat.

Dispatch order:
1. WAVE 0 — launch L0 (01_Pearl_Architect_social_arch_and_scaffold.md) ALONE.
   Wait for: `social-arch-merged=<sha>` (new master spec + schemas + package
   skeleton + config/social README + registry/authority/workstream rows, MERGED).
2. WAVE 1 — on that signal, launch IN PARALLEL:
     - L1 02_Pearl_Marketing_book_to_social_extractor.md
     - L2 03_Pearl_Int_captions_validation_metricool.md
     - L3 04_Pearl_Int_image_lane_pearlstar_covers.md
     - L4 05_Pearl_Int_canva_template_lane.md
     - L5 06_Pearl_Video_video_lane_animator.md
   These share no hot files (disjoint filenames under config/social/ and
   phoenix_v4/social/; all build against L0 schemas + fixtures, not each other).
   Track each to MERGED or BLOCKED. L4 may legitimately end
   `social-canva-lane-blocked=<missing-credential>` if the Canva Connect credential
   is absent in the run environment — that is a VALID terminal state, not a failure
   to chase; the lane must still land its code + mock tests.
3. WAVE 1.5 — OPERATOR LOOK GATE. When L3 and L4 have rendered their pilot assets
   (and L5 has produced its pilot-video instructions), STOP and present the pilot
   renders to the operator for a look-approval. Do NOT let L3/L4 scale render volume
   before the operator emits `social-look-approved=<sha/thread-ref>`. This is a
   human-taste gate (memory: Waystream cover system is gated on look-approval;
   validation-before-scaling). Surface it as Q-SOCIAL-LOOK with the pilot paths.
4. WAVE 2 — once `social-extractor-merged` AND `social-captions-metricool-merged`
   exist, launch L6 (07_Pearl_Dev_pipeline_orchestrator.md). L6 runs the ONE-book
   end-to-end DRY-RUN (plans + captions + payloads + 1 image; no live schedule).
5. WAVE 3 — once `social-orchestrator-merged` exists, launch L7
   (08_Pearl_Research_qa_gates.md): implement + mutation-test the QA/ethics gates,
   wire into Drift detectors / readiness gates.
6. WAVE 4 — once all lane signals exist, launch L8
   (09_Pearl_PM_final_auditor.md): production audit on the one-book proof, honest
   acceptance-layer labelling, PROGRAM_STATE update, operator packet + `open`.

Batch these operator questions once (recommended defaults in INDEX.md §"Open
operator questions"); ask the operator to ratify in one line, do not decide
unilaterally: Q-SOCIAL-01 scheduler, Q-SOCIAL-02 image renderer of record,
Q-SOCIAL-03 first-proof scale, Q-SOCIAL-04 first-proof platforms, Q-SOCIAL-05
auto-publish OFF. Also carry Q-SOCIAL-LOOK (the Wave 1.5 look gate).

Escalate (Q-<TAG>-NN, default stated) rather than deciding: any request to
auto-publish; any lane that wants to scale past the pilot before look-approval;
any Canva/Metricool live call that would need a credential not in the environment;
any change that would edit the sibling-owned 48_SOCIAL / ghl docs.

Track every lane: prompt file; agent; branch; PR; CI; proof root; signal; closeout;
cleanup; blocker.

Final output — do not end the turn without emitting this exact block:
```text
prompt-pack=docs/agent_prompt_packs/20260714_social_media_pipeline/
prompts-launched=<count>
waves-complete=<list>
prs-opened=<urls>
prs-merged=<lane:merge-sha ...>
blocked-lanes=<lane:blocker>
look-approval=<social-look-approved=... | PENDING>
acceptance-layer=<per-lane SPECCED|CODE-WIRED|EXECUTED-REAL|PROVEN-AT-BAR>
cleanup-complete=<yes|no>
handoff=artifacts/coordination/handoffs/social-pipeline-final_2026-07-14.md
next-action=<exact next action>
```
~~~
