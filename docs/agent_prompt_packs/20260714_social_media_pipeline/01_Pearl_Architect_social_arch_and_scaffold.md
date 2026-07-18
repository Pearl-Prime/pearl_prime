# L0 — Pearl_Architect — Social pipeline architecture + scaffold (Wave 0)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Architect for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Architect
- LANE=social-L0-arch
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud
- PERSISTENCE_SURFACES=branch/pr
- RESUME_SURFACE=docs/agent_prompt_packs/20260714_social_media_pipeline/INDEX.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md   (static authority — you unify around it)
- docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md                       (READ-ONLY — sibling branch owns it)
- docs/research_social_media.txt  (skim Parts 4, 7, 8, 10 — platform playbooks, SEO, tech specs, repurposing)
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv
- config/funnel/social_cta_config.yaml   (EXISTS — a downstream consumer; do NOT recreate)

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm no phoenix_v4/social/** or scripts/social/** already exists
  (`git ls-files 'phoenix_v4/social/*'`). If it does, STAND DOWN, report the delta, do not rebuild.
- check open PRs / ACTIVE_WORKSTREAMS for any existing "social pipeline" stream; if one exists, reconcile.

PRE-REQUISITE CHECKS:
- none (this is Wave 0). You gate everyone else.

DISCOVERY REPORT BEFORE ACTION (post before writing code):
- current origin/main SHA;
- confirm STATIC_SOCIAL spec is SPECCED-only (no implementing code);
- list the existing reuse targets: config/funnel/social_cta_config.yaml,
  config/funnel/freebie_to_book_map.yaml, phoenix_v4/marketing/, phoenix_v4/freebies/,
  artifacts/waystream/cover_pilot/compose_cover.py, phoenix_v4/manga/covers/,
  scripts/build_weekly_brand_package.py;
- proposed schema field lists for the four contracts below.

PROVENANCE:
- research: docs/research_social_media.txt; docs/book_deep_research.txt; operator expert brief (platform specs + PLATFORM_RULES)
- documents: docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md (+ you author the new master spec)
- builds_on: config/funnel/social_cta_config.yaml; phoenix_v4/marketing/; STATIC_SOCIAL Output Manifest
- inventory: EXTENDS (new subsystem `social_pipeline`); UNCHANGED for all existing subsystems; never REDUCED

MISSION (narrow):
Author the architecture + scaffold that lets Wave-1 lanes build in parallel against
fixed seams. You write DOCS, SCHEMAS, an empty package skeleton, config stubs, and
coordination rows — NO business logic (that is Wave 1).

DELIVERABLES:
1. docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md — unifies static (cross-ref the
   existing STATIC_SOCIAL spec, do not duplicate it) + image (Pearl Star/covers/PIL) +
   Canva template variant lane + video (Pearl Animator wiring) + captions/media-validation +
   Metricool scheduling + QA/ethics gates. Carries the wave graph, the data-contract seam,
   the auto-publish-OFF default, and the tier/RAP/collision guards. Add NEW-ARTIFACT-JUSTIFIED:
   new cross-cutting subsystem spanning marketing+video+integrations, no single owner today.
2. schemas/social/static_social_plan.schema.json — JSON Schema of the STATIC_SOCIAL spec's
   "Output Manifest" (book_id, brand_id, locale, source_book_path, assets[] with
   source_chapters/source_enhancements/hook/slides/caption/cta/visual_direction/safety_verdict).
3. schemas/social/social_media_asset.schema.json — one asset across ALL lanes: platform,
   format, source_trace (chapter/atom/campaign-row the claim points back to), hook,
   slides|caption, cta{url,text}, visual_direction, media_refs[], alt_text[], safety_verdict.
4. schemas/social/social_media_manifest.schema.json — per-book package (metadata + assets[] + provenance).
5. schemas/social/metricool_payload.schema.json — /v2/scheduler/posts payload
   (providers[], publicationDate, text, firstCommentText, media[], mediaAltText[],
   videoCoverMilliseconds, and per-platform *Data blocks per the expert brief).
6. phoenix_v4/social/__init__.py — empty package marker (so Wave-1 lanes never race on it).
7. config/social/README.md — states file ownership (L1 static_content_config.yaml;
   L2 platform_specs.yaml + platform_rules.yaml; L3 image_render_config.yaml; L4 canva_templates.yaml)
   so no two lanes write the same file. Include a stub config/social/.gitkeep if needed.
8. Coordination rows (you are the ONLY lane allowed to seed these):
   - SUBSYSTEM_AUTHORITY_MAP.tsv: add `social_pipeline` row (authority = the new master spec;
     config_path = config/social/; owner = Pearl_Marketing (content) + Pearl_Int (integrations) + Pearl_Video (video); status = active).
   - CANONICAL_ARTIFACTS_REGISTRY.tsv: add rows for the new spec + the four schemas + the phoenix_v4/social package (edit_not_recreate=YES singletons).
   - ACTIVE_WORKSTREAMS.tsv: add ONE parent row `ws_social_media_pipeline_20260714` (owner Pearl_PM) referencing this pack. Do NOT add per-lane rows — the dispatcher tracks lanes.

SMALLEST SAFE BATCH:
- smoke: write the four schema files; validate each parses as JSON Schema (`python -c "import json,glob; [json.load(open(f)) for f in glob.glob('schemas/social/*.json')]"`).
- pilot: hand-write ONE example social_media_manifest.json against the schema for the flagship
  book and validate it (jsonschema) — this becomes the shared fixture Wave-1 lanes build against.
  Put it at schemas/social/examples/flagship_manifest.example.json.
- scale: N/A (docs/scaffold lane).

HANG PREVENTION:
- poll interval: CI every 2-3 min after push.
- no-progress rule: inspect the CI log after two unchanged polls.
- hard stall rule: BLOCKED after three unchanged polls.
- max window: 90 min.

TESTS/PROOFS:
- `python -c "import jsonschema, json; jsonschema.validate(json.load(open('schemas/social/examples/flagship_manifest.example.json')), json.load(open('schemas/social/social_media_manifest.schema.json')))"`
- `python -c "import phoenix_v4.social"` imports clean.
- proof root: the merged PR + schemas/social/examples/.

DO NOT:
- do NOT write business logic (extractor/caption/render code) — that is Wave 1;
- do NOT edit docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md or docs/ghl/* (sibling branch);
- do NOT recreate config/funnel/social_cta_config.yaml;
- no gate weakening; no fake proof; no local-only finish; no giant batch first.

LANDING CONTRACT:
- MERGED: one PR (docs + schemas + package skeleton + config/social README + 3 coordination
  rows), required checks green, squash-merged, `social-arch-merged=<full-sha>` emitted in the
  PR thread and appended to docs/PROGRAM_STATE.md.
- BLOCKED: exact blocker + evidence + pushed branch + handoff.

CLEANUP LEDGER REQUIRED:
- worktree: (none expected — this is a small docs/schema PR; if you make one, remove it)
- local branch: delete after merge
- remote branch: delete after squash-merge
- scratch files: none outside the PR
- background jobs: none
- held artifacts: none

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L0-arch_2026-07-14.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Architect
- LANE: social-L0-arch
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: social-arch-merged=<full-sha>
- ACCEPTANCE_LAYER: CODE-WIRED (schemas + scaffold; not yet EXECUTED-REAL)
- PROOF_ROOT: schemas/social/examples/ + merged PR
- TESTS: <jsonschema validation output>
- CLEANUP: <ledger>
- HANDOFF: artifacts/coordination/handoffs/social-L0-arch_2026-07-14.md
- NEXT_ACTION: dispatcher launches Wave 1 (L1-L5) against these schemas
- TOKEN: CLOSEOUT_RECEIPT::social-L0-arch
~~~
