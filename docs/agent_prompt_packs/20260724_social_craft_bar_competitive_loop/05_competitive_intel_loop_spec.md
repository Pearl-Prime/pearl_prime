# Lane 05 — Competitive-Intelligence Loop SPEC (spec-only; operator-gated)

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Research (+ Pearl_Architect as builds_on adjudicator) for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-competitive-intel-spec-20260724). Explicit-path staging; poison protocol.

STARTUP_RECEIPT:
- AGENT=Pearl_Research
- LANE=social_competitive_intel_spec_20260724
- EXECUTION_MODE=local_fallback ; BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=branch/PR/spec
- RESUME_SURFACE=artifacts/coordination/handoffs/social_competitive_intel_spec_2026-07-24.md

READ FIRST:
- docs/social_media_YT1.txt … YT6.txt (tracked post-Lane-01) — the research base. The flywheel 4 of
  6 videos teach: scout creators → detect outlier videos (views vs channel average, 48h–5d window,
  prioritize smaller creators) → transcribe winners → remix structure-not-content in own voice from
  own knowledge base.
- docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md — §Non-Goals (no private-account scraping)
  and §Weekly Research Refresh ("competitor and best-in-category post teardown" is already a named
  input — your spec EXTENDS this hook, it does not contradict it)
- scripts/feeds/check_trends.py + score_trends.py (keyword-heat trend lane — the adjacent existing
  system your spec must build_on or explicitly distinguish, never duplicate)
- artifacts/qa/social_research_currency_audit_20260722/RESEARCH_CURRENCY_AUDIT.md

PRE-REQUISITE CHECKS:
- social-research-landed=<sha> exists (Lane 01). Missing → STOP (your provenance cites those files).
- Q-SOCIAL-COMPETITIVE-INTEL-01 ratified (dispatcher batch). If not yet ratified → author the spec
  as DRAFT status with the Q-gate stamped OPEN in the header, land it, and mark the closeout
  BLOCKED-ON-RATIFICATION (the spec may exist unratified; no code may).

LIVE STATE RECONCILIATION: fetch; re-verify ABSENT claims (no creator DB, no outlier detection, no
transcript-ingest, no remix code — grep scripts/social/ phoenix_v4/social/ config/social/).

DISCOVERY REPORT before action: current SHA; adjacent-system inventory (trend feeds, weekly refresh,
Whisper own-audio usage); any sibling PR/spec (gh pr list --search "competitive" --search "outlier").

PROVENANCE:
- research: docs/social_media_YT1–6.txt (primary); RESEARCH_CURRENCY_AUDIT.md (cadence findings)
- documents: PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC (extended, not contradicted)
- builds_on: weekly-research-refresh lane (writer spec §refresh); trend-feed scoring pattern;
  evergreen_social_atom_bank (remix output lands as WEEKLY_TREND_DELTA-style atoms)
- inventory: EXTENDS (spec only; zero code)

MISSION (narrow, SPEC-ONLY): author docs/specs/SOCIAL_COMPETITIVE_INTEL_LOOP_V1_SPEC_2026-07-24.md:
1. **Compliance envelope FIRST (the operator gate's substance):** public metadata + official
   APIs/oEmbed/public RSS only; no login-required automation; no private-account scraping; no
   CAPTCHA bypass; per-platform ToS notes; data retention limits; the envelope is a hard gate every
   downstream implementation PR must cite.
2. **Creator/competitor registry:** schema (YAML/TSV under config/social/), per-brand niche
   definitions, vetting criteria (from YT1: topical fit, not just follower count), dedupe rules.
3. **Outlier detection:** metric = video views vs creator's rolling channel average (YT5's
   outlier-score formula: views_in_window / channel_avg × 100; thresholds ≥200 strong / ≥500 viral),
   window 48h–5d configurable, smaller-creator priority (<50k) per YT5; source = public metadata
   only; scoring script contract (inputs/outputs, no implementation).
4. **Winner ingestion:** transcript/caption acquisition WITHIN the envelope (official APIs, oEmbed,
   auto-captions where licensed); storage as research rows with full provenance (URL, metric
   snapshot, date).
5. **Remix contract:** structure-not-content transfer — extract hook grammar, beat order, format
   (hook-and-demo, text-on-screen, carousel skeleton); FORBID verbatim reuse; output = new atom rows
   + template-variant proposals in OUR voice (voice profiles), gated by Lane 02's craft gate + the
   anti-spam gate; every remix row cites its source row (fixes the 98.7%-boilerplate citation
   failure class for this new row family from day one).
6. **Cadence integration:** runs as an input to the EXISTING weekly refresh (Lane 06's mechanism),
   not a new parallel pipeline; Tier-2/unattended-safe steps identified explicitly (LLM policy).
7. **Acceptance layering + rollout:** SPECCED → CONFIG-EXISTS (registry seeded) → CODE-WIRED
   (scorer) → EXECUTED-REAL (first weekly run with real outlier table) → PROVEN-AT-BAR (remixed
   posts beat non-remixed in the blind-read protocol); Q-gates for each code phase.
8. **Registry row:** add the spec's concept_key to CANONICAL_ARTIFACTS_REGISTRY.tsv with
   NEW-ARTIFACT-JUSTIFIED rationale (nothing existing covers competitive intel — cite the grep-empty
   evidence).

DELIVERABLES: the spec; registry row; handoff; PR.

SMALLEST SAFE BATCH: smoke = spec outline reviewed against writer spec for contradiction; pilot =
full spec; scale = n/a (spec-only lane).

HANG PREVENTION: standard 2/3 polling; max window 4 h.

TESTS/PROOFS: docs-only CI green; contradiction check vs writer spec §Non-Goals quoted in the
handoff; registry row passes pr_governance_review reinvention guard.

DO NOT: write any scraping/collection code; name any paid API as a dependency; contradict the
live-scheduling non-goal; duplicate the trend-feed lane (distinguish: keyword-heat ≠ per-video
outlier); touch coordination hot files.

LANDING CONTRACT: MERGED (spec PR squash-merged + signal) or BLOCKED (only a true blocker — the
unratified-Q case still lands the DRAFT spec and reports BLOCKED-ON-RATIFICATION with the landed
SHA).

CLEANUP LEDGER + HANDOFF: artifacts/coordination/handoffs/social_competitive_intel_spec_2026-07-24.md

CLOSEOUT_RECEIPT: standard fields + full MERGE_SHA.
SIGNAL: social-competitive-loop-spec-landed=<full merge SHA>
ACCEPTANCE LAYER: SPECCED (at most). Code is a future, separately-ratified pack.
~~~
