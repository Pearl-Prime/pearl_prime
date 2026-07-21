# L1 — Pearl_Marketing — Book→social extractor + static copy generator (Wave 1)

Paste this whole block into the lane agent chat.

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Marketing for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Marketing
- LANE=social-L1-extractor
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud
- PERSISTENCE_SURFACES=branch/pr/artifact
- RESUME_SURFACE=phoenix_v4/social/extractor.py

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_PIPELINE_MASTER_SPEC.md   (from L0)
- docs/specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md  (the content doctrine you implement)
- schemas/social/*.schema.json + schemas/social/examples/flagship_manifest.example.json (the seam)
- config/funnel/social_cta_config.yaml + config/funnel/freebie_to_book_map.yaml (REUSE — CTAs/hooks/hashtags)

LIVE STATE RECONCILIATION:
- verify social-arch-merged=<sha> exists on origin/main (schemas + package skeleton present).
- confirm phoenix_v4/social/__init__.py exists; if not, STOP BLOCKED (L0 not landed).
- re-read the schemas live; build against them, not against this prompt's paraphrase.

PRE-REQUISITE CHECKS:
- social-arch-merged=<sha>  → if missing, STOP BLOCKED "L0 not landed."

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- pick the proof book: the PROVEN-AT-BAR flagship (gen_z_professionals × anxiety) — locate its
  rendered book text (artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt is the golden) + its
  outline/enhancement artifacts + atom sources;
- list the book surfaces available (chapter clear points, MECHANISM, EXTERNAL_STORY,
  ANALOGY, TROUBLESHOOTING, CITED_EVIDENCE, CALLBACK_RETURN, memorable lines);
- proposed asset counts for the pilot book (target 30-50 across families per the spec).

PROVENANCE:
- research: docs/research_social_media.txt (Parts 2, 3, 6, 10 — content strategy, writing, carousels, repurposing)
- documents: STATIC_SOCIAL spec + SOCIAL_MEDIA_PIPELINE_MASTER_SPEC
- builds_on: config/funnel/social_cta_config.yaml; phoenix_v4/marketing/; the L0 schemas
- inventory: EXTENDS phoenix_v4/marketing (new social extractor/generator); UNCHANGED elsewhere

MISSION (narrow):
Build the book-to-social EXTRACTOR + STATIC copy GENERATOR. Given a rendered book +
its outline/enhancement artifacts, emit a schema-valid social_media_manifest.json whose
STATIC assets (IG carousels, LinkedIn PDFs, Pinterest Pins, FB/text posts, quote-with-
commentary, offer posts) carry authored copy AND a source_trace for every claim/story/
quote. Prose is Tier-1 Claude authoring (you), following the STATIC_SOCIAL Universal
Writing Arc and the default 20-post mix. Video/image RENDERING is other lanes — you emit
the PLAN + copy + visual_direction + media_refs placeholders they consume.

DELIVERABLES:
- phoenix_v4/social/extractor.py — reads book text + outline/enhancement artifacts, returns
  structured source surfaces with traces.
- phoenix_v4/social/static_generator.py — turns surfaces into schema-valid static assets
  (carousel slides, LinkedIn PDF thesis/sections, Pin copy, FB post, quote+commentary, offer)
  per the STATIC_SOCIAL post-family mix; pulls CTAs/hashtags/hooks from social_cta_config.yaml.
- config/social/static_content_config.yaml — the per-book mix knobs (family targets, quote-density
  ceiling <=15%, arc template). (This is L1's file; no other lane writes it — see config/social/README.md.)
- artifacts/social/pilot/<book_id>/static_social_plan.json + static_social_manifest.json (STATIC-scoped
  proof). NOTE: the UNIFIED artifacts/social/pilot/<book_id>/social_media_manifest.json (static+image+
  video merged) is owned/emitted by L6 (orchestrator), not this lane — do not write that filename here.
- tests/test_social_extractor.py + tests/test_social_static_generator.py.

SMALLEST SAFE BATCH:
- smoke: ONE chapter → ONE 9-slide carousel plan, schema-valid, every slide traced. Print it.
- pilot: ONE full flagship book → full 30-50 asset static plan (static_social_plan.json +
  static_social_manifest.json); assert quote-density <=15%, every asset has a source_trace,
  mix matches the spec's default distribution.
- scale: THREE books (add 2 more topics) only after pilot passes. Do NOT go past 3 in this lane.

HANG PREVENTION:
- poll interval: this is synchronous authoring/codegen — checkpoint after smoke and after pilot.
- no-progress rule: if the generator errors twice on the same book, reduce to the single-chapter smoke and inspect.
- hard stall rule: BLOCKED after three failed pilot attempts with the error captured.
- max window: 120 min.

TESTS/PROOFS:
- pytest tests/test_social_extractor.py tests/test_social_static_generator.py -x
- jsonschema-validate the emitted manifest against schemas/social/social_media_manifest.schema.json
- proof root: artifacts/social/pilot/<book_id>/

DO NOT:
- do NOT invent stories, citations, author disclosures, quotes, or therapeutic claims not present
  in the book/atoms/campaign plan (STATIC_SOCIAL Safety gate);
- do NOT exceed the 15% quote-card density ceiling;
- do NOT render images or video (other lanes) — emit visual_direction + media_ref placeholders;
- do NOT edit the 48_SOCIAL / ghl docs or any coordination TSV;
- no fake proof; no local-only finish; no giant batch first.

LANDING CONTRACT:
- MERGED: PR (code + config + tests + pilot artifacts), checks green, squash-merged,
  `social-extractor-merged=<full-sha>` emitted.
- BLOCKED: exact blocker + evidence + pushed branch + handoff.

CLEANUP LEDGER REQUIRED:
- worktree / local branch / remote branch / scratch files / background jobs / held artifacts
  (declare artifacts/social/pilot/<book_id>/ as intentionally kept — it is the proof root).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/social-L1-extractor_2026-07-14.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Marketing
- LANE: social-L1-extractor
- STATUS=MERGED|BLOCKED
- BRANCH / PR / MERGE_SHA:
- SIGNAL: social-extractor-merged=<full-sha>
- ACCEPTANCE_LAYER: EXECUTED-REAL if a real book emitted a valid traced manifest; else CODE-WIRED. NOT "done."
- PROOF_ROOT: artifacts/social/pilot/<book_id>/
- TESTS: <pytest + jsonschema output>
- CLEANUP / HANDOFF / NEXT_ACTION:
- TOKEN: CLOSEOUT_RECEIPT::social-L1-extractor
~~~
