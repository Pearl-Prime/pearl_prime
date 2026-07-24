# Manga Video Pose-Bank (V-Bank V1) — Prompt Pack (2026-07-24)

**Program goal:** stand up a video-capture supply lane for the manga image bank — free Alibaba
(Wan) video clips of a continuity-locked character, harvested into validated, metadata-rich,
outfit-keyed pose layers that the existing deterministic assembler consumes — with the
100-episode story analysis (uplift Lanes 06/09) defining what the bank needs, and the bank
requirements compiling into the video capture prompts. If the pilot proves the method, the
never-executed LoRA training lane is formally retired to last-resort status.

**Live truth anchor (router, 2026-07-24):** `origin/main` = `760ec2a5611951cdcd587ab9f8380aa1ed92a6fb`.
Open PRs at authoring time: **#310** (DashScope free-quota exception — OPEN/MERGEABLE, the whole
free-media lane exists ONLY on that branch + untracked local copies), **#331** (uplift Lane 06
master-plan contract — OPEN), **#295** (draft — rework-never-merge per Q-MPU-02). Uplift Lanes
01–05 + 10 are MERGED with signals; Lanes 07/08/09/11/12 not started. Every lane re-verifies
these claims live before acting.

**Source request:** operator 2026-07-24 — "prompts for robust pipeline to get free alibaba video
clips to do manga with better consistency. 100 story analysis defines image bank reqs that define
video prompts. clean up old lora stuff if this is a better way." Method research attached from
`old_chat_specs/Untitled 411.txt` (video-to-sprite-bank architecture: capture manifest → short
identity-anchored clips → frame extraction → validation → immutable bank → deterministic assembly).

## Grounding corrections (discovery pass, 2026-07-24 — these are pack premises, re-verify live)

| Operator premise | Verified truth | Disposition |
|---|---|---|
| "Free alibaba video clips" as a standing pipeline | Free quota is **one-time, per-model**: ~45s wan2.7-t2v + 50s wan2.7-i2v remain (≈19 five-second clips), 100-image qwen still bucket, sunset **2026-10-18**. The exception in CLAUDE.md is explicitly "not a standing pipeline" | Cloud free quota = **one-character method pilot only** (Lane 05). Standing scale = **self-hosted open-weights Wan/VACE on Pearl Star** (still Alibaba, still $0/clip) — feasibility researched in Lane 02 |
| Reference-to-video (R2V) per the attached research | The landed client (`scripts/social/dashscope_free_media.py`, PR #310) supports **t2i/t2v/i2v only** — zero r2v/keyframe/continuation code. `wan2.7-r2v` appears in the 07-19 recon with its own free bucket (unconfirmed) | Available consistency mechanism NOW = **i2v anchored to a canonical still** (same anchor image across all clips). Lane 02 confirms r2v free quota + API; if real, Lane 04 extends the exempt client **in place** |
| "Clean up old lora stuff" | LoRA lane is **plan-only end to end**: zero `.safetensors` anywhere, zero LoraLoader nodes, no training code, reference PNGs absent. Already demoted to fallback (Q-MANGA-04 PuLID-first; roadmap M5) | Retirement = spec/config/status surgery (Lane 06), **gated on the pilot verdict** (Lane 05 signal). No render-path code changes, no deletion of research artifacts |
| Video frames go straight into panels | Doctrine: DashScope free-lane output is **INTERIM provenance, never final art** (CLAUDE.md). Bank canon polices cutouts hard (class-A alpha gates, single-connected-component L2, 50KB byte floor, §6.8 pose-cardinality budget) | DashScope-derived poses = INTERIM forever; **self-hosted Wan output (Apache-2.0) = REAL-eligible** after the same gates. Frames enter as standard manifest layers — **no assembler edits** |
| 100-story analysis → bank reqs | Uplift Lane 09 (`series_demand_rollup.yaml`, extends `generate_bank_contracts_from_script.py`) IS that analysis — **not started yet**; Lane 06 contract on open PR #331 | Lane 04's demand→capture compiler consumes the rollup **when its signal exists**; pilot falls back to the stillness golden master plan + per-episode bank contracts (Lane 11's check-don't-require pattern) |

## Prompt count and wave order

7 lane prompts + this INDEX + `00_MASTER_DISPATCH_PROMPT.md` (Pearl_PM dispatcher — REQUIRED entry point).

| Wave | Lane | Owner | Mission (one line) | Gates on |
|---|---|---|---|---|
| 0 | 01_land_dashscope_lane | Pearl_GitHub | Merge PR #310 on green; scope-note the exception for the manga pilot (OPD row); close the api-key silent-fallback drift risk | — |
| 1 | 02_video_capability_research | Pearl_Research | Web + on-box research: r2v free-tier truth; self-hosted Wan/VACE/LTX on 16GB 5070 Ti (2026 quant era); consistency-method evidence; capture-program design | — |
| 2 | 03_vbank_contract_spec | Pearl_Architect + Pearl_Dev | Video-Capture→Bank contract: capture-manifest schema, demand→capture compiler contract, frame gate chain, provenance rules, identity-ladder draft | 01, 02 |
| 2.5 | 04_capture_tooling | Pearl_Dev | Implement `scripts/manga/video_bank/`: compiler, capture runner (imports the exempt client — NO new call sites), frame extractor, pose-from-frame maker, validators + tests | 03 |
| 3 | 05_pilot_capture_burn | Pearl_Dev | ONE character × one outfit through the whole loop on the real free quota (operator-gated burn): anchors → clips → frames → validated INTERIM pose slice → assembled panels → consistency scorecard + verdict | 04 (+ Q-VBANK-01 GO) |
| 4 | 06_lora_disposition | Pearl_Architect | Encode the verdict: amend MANGA-LAYERED-PIPELINE-V2-01 C6/C7/B8, roadmap M5, §15.A.2 identity gate, brand_lora_plans banner; OPD rows | 05 |
| 5 | 07_final_audit_ssot | Pearl_PM | Verify every signal, update PROGRAM_STATE manga row + workstreams + registry, name honest acceptance layers | all |

**Dependencies are signal-gated, never narrative.** Signal tokens (each `=<full merge SHA>`, durable
on the merged PR / lane handoff):
`dashscope-free-media-landed`, `manga-video-capability-research-merged`,
`manga-video-pose-bank-spec-merged`, `manga-video-bank-tooling-merged`,
`manga-video-pose-bank-pilot-executed-real` (verdict field: `method_better|method_worse|inconclusive`),
`manga-lora-lane-disposition-merged`, `manga-video-pose-bank-audited`.

Cross-pack signals this pack READS (uplift pack, 2026-07-24): `manga-series-master-plan-contract-merged`
(Lane 06/#331), `manga-bank-demand-rollup-merged` (Lane 09 — not started), `manga-process-pilot-*`
(Lane 11 — not started). Consume content only behind the signal; otherwise use the documented fallback.

## Owners / subsystem authority

Subsystem `manga_pipeline` (owner **Pearl_Dev**; authority `specs/AI_MANGA_PIPELINE_SUMMARY.md`,
`docs/MANGA_IMPLEMENTATION_OUTLINE.md`). Render authority: `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md`
(registry `NO-without-ratification` — this pack frames video capture as a **bank supply lane**, not an
architecture variant; the V5 doc is NOT edited). Layer/bank contract: `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md`
(Lane 03 edits in place). Identity: `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` (read-only;
ladder amendment lands in the cap entry, Lane 06). Governance: `config/governance/banned_llm_patterns.yaml`
+ CLAUDE.md exception text (Lane 01 only). GPU: RAP queue-first via `pscli` (`docs/ROBUST_AGENT_PROTOCOL.md`).

## Substrate (every lane)

Shared checkout is DIRTY and sibling sessions are live. No full worktrees (262k files, ~3.2 GB LFS
smudge). Docs/config lanes use the plumbing pattern (temp index off `origin/main^{tree}`,
`GIT_LFS_SKIP_SMUDGE=1`, explicit paths, staged-diff gate `git diff --cached --stat origin/main` =
exact intended list). Code lanes may use a sparse-cone worktree ≥20 GB free — poison protocol
mandatory (`git reset origin/main` first; never `git add -A`). Cloud burns: operator-present shell
only (`PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1` + `DASHSCOPE_FREE_QUOTA_API_KEY`), never cron/workflow.

## Hot-file collision map (serialize; ONE writer at a time)

- **PR #310 / branch `agent/dashscope-free-quota-exception-20260724` / CLAUDE.md / `banned_llm_patterns.yaml`** — Lane 01 only. The scope-note lands as a follow-up commit ON that PR before merge (one PR, one merge), or as an immediate tiny successor PR if #310 merges first.
- **`docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md`** — Lane 03 only (no uplift lane touches it).
- **`config/manga/gate_registry.yaml` + `scripts/run_production_readiness_gates.py`** — uplift Lane 07 owns story-gate edits and Lane 06/#331 adds gate 48. This pack adds **no numbered gate**; Lane 04's validators run as scripts + tests; gate promotion is a declared follow-on after the uplift waves settle.
- **`config/source_of_truth/manga_profiles/series/stillness_en_01.character_pose_inventory.yaml` + `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/`** — shared with uplift Lane 11 (not started at authoring). Lane 05 works proof-root-first (`artifacts/qa/manga_video_pose_bank_pilot_2026-07-24/`); the series-bank ingest + pose-inventory registration is its own small serialized PR, deferred if Lane 11 is live at that moment (dispatcher arbitrates; one actor per resource).
- **`docs/PEARL_ARCHITECT_STATE.md`** — Lane 06 only (serial with any live uplift/architect session; claim via dispatcher).
- **`docs/PROGRAM_STATE.md` / `ACTIVE_WORKSTREAMS.tsv` / `CANONICAL_ARTIFACTS_REGISTRY.tsv` / `DOCS_INDEX.md`** — dispatcher + Lane 07 serial owners; other lanes REQUEST rows via closeouts. Uplift Lane 12 also writes PROGRAM_STATE when it fires — dispatcher coordinates (whoever lands second re-roots).
- **`scripts/social/dashscope_free_media.py`** — Lane 01 (key-fallback fix) then Lane 04 (r2v extension, only if Lane 02 proves quota) — strictly in that order, and ONLY this file may contain DashScope endpoint patterns (exempt path). Any other file touching `X-DashScope-Async` or `/services/aigc/` **cannot merge** (banned-patterns gate).

## Operator questions (recommend defaults; dispatcher logs OPD rows on ratification)

- **Q-VBANK-01 — spend the free video quota on the pilot?** The remaining ~45s t2v + 50s i2v (+ r2v bucket if Lane 02 confirms) is one-time and expires 2026-10-18. The pilot consumes most of it on ONE character's capture program. **Default: GO** — this is the operator's stated purpose; batch every capture prompt before burning; keep ≥10s reserve for retakes.
- **Q-VBANK-02 — pilot character?** **Default: `mira_aoki` (stillness_press flagship)** — richest existing anchors (PuLID reference L2 assets, `character_pose_inventory`, model sheets, read-approved episodes), and it makes the scorecard comparable against the existing PuLID-stills baseline. Alternative: `warrior_calm` MC if the operator wants zero contact with the uplift pilot series (costs comparability).
- **Q-VBANK-03 — provenance posture?** **Default:** DashScope-derived poses stay **INTERIM permanently** (doctrine unchanged); self-hosted Wan/VACE output is **REAL-eligible** after class-A + face-distance gates. No V5 ratification needed under the supply-lane framing.
- **Q-VBANK-04 — LoRA retirement depth?** **Default: retire-and-banner** — C6/C7/B8 → "not planned; last-resort behind PuLID + capture bank", `brand_lora_plans.yaml` header banner, ws row closed. **No deletion**, no catalog-column migration in this pack (declared follow-on if the verdict is strong).

## Terminal state required

Every writing lane ends MERGED or BLOCKED (work pushed + NEXT_ACTION) — no third state. Cleanup
ledger + handoff `.md` per lane (`artifacts/coordination/handoffs/manga_video_pose_bank_lane0N_2026-07-24.md`).
Lane 07 updates PROGRAM_STATE and names the honest acceptance layer for every deliverable:
research=RESEARCHED, spec=SPECCED, tooling=CODE-WIRED, pilot=at most **EXECUTED-REAL** (byte-verified
clips/frames/panels). Nothing in this pack claims PROVEN-AT-BAR — that stays gated on blind-10
judged scorecards (roadmap M6), which this pack feeds but does not satisfy.
