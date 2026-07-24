# Social Media Atom Bank — Layer-Honest 100% Production-Readiness Plan

Date: 2026-07-22 (authored 2026-07-23)
Agent: Pearl_PM (acceptance-layer taxonomy + cap-entry status co-signed against `docs/PEARL_ARCHITECT_STATE.md`
`SOCIAL-ATOM-BANK-VIBE-01`)
Project: `proj_social_atom_bank_vibe_20260721`
Subsystem: `social_media`

**This document does not claim the social media system is 100% production-ready. Its entire purpose is
the opposite: to name, layer, and sequence every real gap between "code/atoms exist" and "a real post
could ship, at catalog scale, in every promised platform×locale cell, with a verifiable human review
trail." Nothing below should be read or cited as a shippability claim.**

## Status of the two upstream lanes this plan depends on (re-verified live, 2026-07-23)

- **Lane A (git/PR landing):** PR **#75** (`fix(ci): land orphan config files breaking main Core tests +
  complete phoenix_v4.social`) is **MERGED**.
  It lands `phoenix_v4/social/__init__.py`, `phoenix_v4/social/media_selector.py`,
  `config/social/platform_specs.yaml`, `config/social/words_bank.yaml`, `config/social/visual_registry.yaml`,
  `config/manga/main_character_interaction_grammar.yaml`, a `SUBSYSTEM_AUTHORITY_MAP.tsv` row for
  `social_media`, and the `CANONICAL_ARTIFACTS_REGISTRY.tsv` fix for `evergreen_social_atom_bank`
  and the related registry/authority rows are now durable on `origin/main`. PR **#123** subsequently
  wired `check_social_post_variation.py` into production readiness; this correction assigns it the
  unique display number **45** because title/subtitle language conformance already occupies gate 44.
- **Lane B (research audit):** **COMPLETE.** `artifacts/qa/social_research_currency_audit_20260722/RESEARCH_CURRENCY_AUDIT.md`
  is on disk and its findings are folded into §3 (Research Cadence) and the gap list below.
- **Third, adjacent, out-of-scope gap** (named for CI-health awareness, not owned by this plan):
  `tests/manga/test_story_excellence_gate.py::test_gate_registry_includes_excellence_ids_without_dropping_wired_rows`
  fails on current `main` because `config/manga/gate_registry.yaml` is missing rows for 10
  `MANGA.STORY.*` excellence-gate IDs already implemented in `phoenix_v4/manga/story_quality/excellence_gate.py`.
  This is a manga-subsystem Core-test failure point, not a social-media gap; flagged here only because it
  affects the shared CI health this subsystem's own gates depend on.

---

## 1. Six-layer acceptance taxonomy (adapted from the manga/bestseller precedent)

`ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`

| Component | Layer today | Why not higher |
|---|---|---|
| **Evergreen atom bank** (`SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl`, 1,642 rows; `platform_surface_atoms.jsonl`, 250 rows) | **EXECUTED-REAL** | Real authored rows exist and the deterministic assembler runs against them today. Not **PROVEN-AT-BAR**: no blind-judged sample of assembled posts exists; 98.7% of rows carry identical undifferentiated `SRC_*` boilerplate citations (only 1.3% are falsifiable quote+path citations, per Lane B) — populated-but-non-specific provenance, not a quality proof. |
| **Brand/author vibe schema** (`SOCIAL-ATOM-BANK-VIBE-01`: `brand_id`/`author_id`/`vibe_ref` optional fields; `config/authoring/social_brand_author_voice_profiles.yaml`; `phoenix_v4/social/deterministic_social.py` wiring) | **CODE-WIRED** (durable on `origin/main`) | Decision ratified (`docs/PEARL_ARCHITECT_STATE.md` SOCIAL-ATOM-BANK-VIBE-01, 2026-07-21), voice catalog file written, kwargs wired through `generate_copy_package`/`select_visual`/`render_static_asset`/`build_carousel_package`/`select_beat_media`, tests passing per Lane 02 handoff (`test_no_brand_args_copy_package_is_byte_identical_to_baseline`, `test_brand_voice_changes_cta_and_sign_off`). Zero atom rows currently carry a non-null `brand_id`/`author_id`/`vibe_ref` (additive fields, unused so far), so this is not yet EXECUTED-REAL for a brand-specific run. |
| **Anti-spam / variation gate** (`scripts/ci/check_social_post_variation.py`, gate 45 in `run_production_readiness_gates.py`) | **CODE-WIRED** (durable on `origin/main` via PR #123; display-number correction in this change) | Real 3-gram Jaccard similarity gate with a documented PASS/FAIL mutation-test proof (2026-07-21, `--inject-duplicates 3` correctly fails 6 violations). PR #123 wired it as a required production-readiness check; gate 45 avoids the duplicate gate-44 label. |
| **APAC localization set** (`apac_localization_atoms.jsonl`, 60 rows: ja-JP/zh-TW/ko-KR/zh-CN/zh-HK/en-SG) | **EXECUTED-REAL** (thin evidence trail) | Real localized rows exist, promoted to `SOURCE_OF_TRUTH/` (Lane 05, 2026-07-18), all 60/60 carry `review_status=reviewed_candidate` (correctly not `draft`, but also not `production_ready`). Not **PROVEN-AT-BAR**: per Lane B, the entire "native/human review" evidence trail is one operator chat-level assertion (`OPD-OC7-02`: *"Operator chat 342 native reviewer evidence approved"*), not a named native-reviewer per-row sign-off artifact. The spec's own "human/native review before production use" gate is not verifiably satisfied yet. |
| **Visual b-roll bank** (Storyblocks: `artifacts/storyblocks_licensed/social_media_bank_storyblocks_20260720`) | **EXECUTED-REAL** (partial coverage only) | 16 real licensed assets exist across 8 topics (anxiety, burnout, boundaries, depression, grief, hope, loneliness, overthinking), wired as a consumer preference in `build_video_snippet_bank._licensed_storyblocks_stills`. The full 12-topic default list at max-per-topic-2 (~24 assets) is explicitly "not claimed" per the Lane 05 handoff — 4 topics have zero licensed assets today. |
| **Visual-license operator gate** (`artifacts/qa/deterministic_social_visual_gate_20260718/`) | **CODE-WIRED / EXECUTED-REAL, hard-blocked on an operator decision, not a code gap** | The gate itself is real and ran: 3 source visuals license-verified against the Pexels license, 405 render rows evaluated. But the gate's own verdict is `SIGNAL=det-social-visual-license-operator-look=BLOCKED_PENDING_OPERATOR_APPROVAL`, `LIVE_PUBLISHING_AUTHORIZED=no`, **0 of 405 render rows marked production-ready**. This cannot become PROVEN-AT-BAR by more code — it requires a human to read `artifacts/operator_read_packets/deterministic_social_visual_gate_20260718/operator_look_packet.md` and decide (see Q-SOCIAL-VISUAL-LICENSE-APPROVAL-01 below). |
| **Weekly research-refresh cadence** | **EXECUTED-REAL (single instance only — not a working recurring system)** | The mechanism ran once, manually, 2026-07-18 (digest + delta-atom promotion, both completed same-day). Per Lane B: zero cron/GitHub-Actions/scheduled-task artifact anywhere in the repo references it — "weekly" is not mechanically enforced. This regresses to **CONFIG-EXISTS** the moment a second week passes without a human re-dispatching it by hand — which, per the meta-rule in `CLAUDE.md` ("memory is recall, not enforcement — promote every hard-won lesson to a CI gate / can't-bypass default / CLAUDE.md rule"), is exactly the failure mode this taxonomy exists to catch before it becomes tribal memory. |
| **Governance/SSOT registration** (`SUBSYSTEM_AUTHORITY_MAP.tsv`, `docs/PROGRAM_STATE.md`) | **CODE-WIRED** | `social_media` is registered in `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`, and `docs/PROGRAM_STATE.md` contains the Social Media Atom Bank section. PR #75 and the subsequent documentation lane made both durable on `origin/main`. |

**Reading this taxonomy honestly:** nothing in the social-media subsystem has reached PROVEN-AT-BAR.
Several pieces have reached EXECUTED-REAL and the core code/config is durable on `origin/main`.
The single largest concrete blocker between "atoms exist" and "a real post could
ship with real visuals" is the visual-license operator gate (0/405 rows production-ready), which is an
operator decision, not a code gap.

---

## 2. Numbered, sequenced gap list

Each item: current layer → target layer, owner agent, rough sizing.

1. **COMPLETED — Land PR #75 (governance/SSOT + orphan-file landing).**
   Current: merged and durable on `origin/main`.
   Follow-on: PR #123 wired the anti-spam gate; this change corrects its duplicate display number.
   (workstream-overlap only, not a blocker). This is the fastest, lowest-risk unblock on this whole list and
   should be sequenced first — every other durability claim in this plan depends on it.

2. **Visual-license operator look-packet approval (or explicit rejection/fix request).**
   Current: EXECUTED-REAL gate output, BLOCKED_PENDING_OPERATOR_APPROVAL. Target: operator-ratified decision
   recorded (approve → PROVEN-AT-BAR path opens for the 3 verified visuals; reject/fix → named remediation).
   Owner: **operator** (see Q-SOCIAL-VISUAL-LICENSE-APPROVAL-01).
   Sizing: **operator decision** — read one packet (`operator_look_packet.md`, one contact sheet, one look
   matrix of 405 rows), decide. Not an agent-turn item.

3. **Storyblocks 12-topic b-roll fill completion.**
   Current: EXECUTED-REAL for 8/12 topics (16 assets). Target: EXECUTED-REAL for all 12 topics at the
   originally-scoped max-per-topic-2 (~24 assets), pending Q-SOCIAL-STORYBLOCKS-VOLUME-01.
   Owner: Pearl_Int (re-run `scripts/storyblocks/fill_social_bank.py` for the remaining 4 topics).
   Sizing: **one agent-turn** — same script, same pattern already proven for the first 8 topics; no new
   mechanism needed, just execution once the volume question is confirmed.

4. **Weekly-refresh cadence automation (cron/workflow/scheduled-task).**
   Current: EXECUTED-REAL (one manual run, 2026-07-18), zero recurrence mechanism. Target: CODE-WIRED
   recurring mechanism (a scheduled GitHub Actions workflow or `scripts/scheduled_tasks` entry that
   re-dispatches the weekly digest + delta-atom lane automatically) → EXECUTED-REAL once it fires
   unattended at least once.
   Owner: Pearl_Dev / Pearl_DevOps.
   Sizing: **one agent-turn** to wire the mechanism (the digest/delta lane logic itself already exists and
   worked correctly once — this is a scheduling/wiring gap, not a re-author of the research process), then
   passive verification the following week that it actually fired.

5. **APAC native-review evidence upgrade (chat-assertion → durable per-row artifact).**
   Current: EXECUTED-REAL rows at `review_status=reviewed_candidate`, backed only by `OPD-OC7-02`
   (one operator chat-level assertion). Target: a durable, row-level native-reviewer sign-off artifact
   (reviewer identity, date, per-row disposition) before any APAC row is promoted past `reviewed_candidate`
   toward `production_ready`.
   Owner: Pearl_Localization (native-fluent review) + Pearl_QA (artifact format/gate).
   Sizing: **multi-lane wave** — requires actual native-speaker review across 60 rows × 6 markets, not
   something a single agent-turn can fabricate; the artifact format itself (a TSV/JSON sign-off log) is a
   small agent-turn, but the review content depends on human/native-fluent judgment.

6. **Density/shape audit of the family × platform × locale matrix.**
   Current: ABSENT (no audit has quantified this yet — the ~1,642-row EN evergreen count and the spec's
   15 atom families × platform/surface/persona/topic/awareness-stage compatibility matrix have never been
   cross-tabulated for coverage density). Target: RESEARCHED → an audit doc quantifying, per
   `project_atom_deficit_is_shape_not_count` lens, how many (family, platform, locale, topic) cells the
   spec's compatibility rules imply are needed vs. how many currently have enough atoms to assemble a
   non-repetitive post (not just "an atom exists somewhere in this family").
   Owner: Pearl_QA / Pearl_Architect.
   Sizing: **one agent-turn** for a first-pass automated audit (parse the atom bank's metadata fields —
   `platform_fit`, `surface_fit`, `market_fit`, `topic`, `persona`, `awareness_stage` — and compute cell
   density), likely surfacing a **multi-lane wave** of gap-fill authoring as a follow-on once the shape of
   the deficit is known (this audit is a prerequisite for scoping that follow-on, not the follow-on itself).

7. **Citation-integrity repair (boilerplate → per-claim citation).**
   Current: EXECUTED-REAL with 98.7% undifferentiated boilerplate `SRC_*` tags (1.3% falsifiable). Target:
   a meaningfully higher fraction of rows carrying specific quote+path citations, especially for atoms
   making a claim (somatic/nervous-system claims, platform-rule claims) rather than pure craft/CTA rows
   that don't need one.
   Owner: Pearl_Social_Media_Writer.
   Sizing: **multi-lane wave** — 1,642 rows is not a single-turn fix; recommend prioritizing the subset of
   rows that make a falsifiable factual/platform claim first (a much smaller slice) rather than boiling
   the whole bank at once.

8. **Source Authority list reconciliation (governed docs untracked at `origin/main`).**
   Current: ABSENT (only the spec doc itself is tracked at `origin/main`; the other 6 governed Source
   Authority artifacts plus 2 ungoverned de facto sources — `docs/research_gemini_social_media_templates_english.txt`
   and `docs/research_social_media.txt` (directly quote-cited by 22 atom rows) — exist only as untracked
   local files). Target: either land the 7 governed docs to `origin/main` (SPECCED → CODE-WIRED) or
   explicitly document them as intentionally local-only working files, and decide whether the two
   ungoverned docs join §Source Authority or get retired.
   Owner: Pearl_Architect (spec authority) + Pearl_GitHub (landing).
   Sizing: **one agent-turn** to land the files (they already exist, just untracked) plus a small spec-doc
   edit; not multi-lane.

9. **Governance/SSOT registration — PROGRAM_STATE.md row.**
   Current: ABSENT. Target: CODE-WIRED (this plan lane adds it directly — see §4 and the file itself).
   Owner: Pearl_PM (this lane).
   Sizing: **done in this same turn** — see the PROGRAM_STATE.md edit accompanying this doc.

10. **Live-scheduling non-goal ratification.**
    Current: correctly `NOT_AUTHORIZED`, but never explicitly operator-ratified as a *permanent* design
    boundary (it has only ever been "not asked for"). Target: an explicit Q-gate answer on record so this
    stops being re-discovered as a "blocker" by future sessions.
    Owner: operator (see Q-SOCIAL-LIVE-SCHEDULING-NONGOAL-CONFIRM-01).
    Sizing: **operator decision**, near-zero effort (default answer is "yes, stays non-goal").

---

## 3. Q-SOCIAL-* open questions (operator-tier — not decided by this plan)

### Q-SOCIAL-VISUAL-LICENSE-APPROVAL-01
**Question:** Approve the visual-license operator look-packet
(`artifacts/operator_read_packets/deterministic_social_visual_gate_20260718/operator_look_packet.md`),
authorizing the 3 license-verified source visuals (and their 405 rendered rows) for production use?
**Recommended default:** Review the packet and the contact sheet
(`artifacts/qa/deterministic_social_visual_gate_20260718/contact_sheets/source_visual_gate_sheet.jpg`);
approve if the 3 verified source visuals meet the brand bar. **This plan does not decide this — it only
frames the choice.** Current state (`0/405 production-ready`, `LIVE_PUBLISHING_AUTHORIZED=no`) should be
re-confirmed as still current before acting, since it may have changed since this plan was authored.

### Q-SOCIAL-STORYBLOCKS-VOLUME-01
**Question:** Should the remaining Storyblocks 12-topic fill proceed at the originally-scoped
max-per-topic-2 (~8 more assets across the 4 missing topics), or a different volume (e.g. max-per-topic-3+
for higher rotation headroom, given the anti-spam gate's same-brand-near-dup threshold)?
**Recommended default:** proceed at max-per-topic-2 as originally scoped — matches the existing 8-topic
precedent and keeps licensing cost/scope proportional; revisit volume only if the anti-spam gate later
flags visual repetition specifically (today's gate covers caption-body similarity, not visual asset reuse).

### Q-SOCIAL-LIVE-SCHEDULING-NONGOAL-CONFIRM-01
**Question:** Confirm live scheduling (e.g. Metricool auto-publish) stays an explicit, ratified non-goal
for this phase of the social-media subsystem.
**Recommended default:** **yes, stays non-goal.** This is correctly stated in
`docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md` §Non-Goals ("No live publishing", "No Metricool
live scheduling") — it is a deliberate design boundary, not a defect or an accidentally-unbuilt feature.
Surfacing it here only so it is an explicit ratified decision on record rather than something a future
session silently re-discovers and treats as a bug. **What would need to change if live scheduling were
ever wanted:** an explicit operator ratification recorded in `artifacts/coordination/operator_decisions_log.tsv`
plus a spec amendment removing the non-goal line and adding a §Live Publishing Authorization section
(mirroring how `SOCIAL-ATOM-BANK-VIBE-01` was ratified as an architect decision before any code landed).

---

## 4. PROGRAM_STATE.md row

Added directly to `docs/PROGRAM_STATE.md` as `### Social Media Atom Bank`, following the existing
Status/Details format used by the other subsystem sections in that file (see e.g. `### Storefront`).
See that file for the live text; summarized here for convenience:

- **Status:** ACTIVE project since 2026-07-21; subsystem was previously **entirely absent** from this
  SSOT — that omission is itself one of the gaps this plan closes.
- **Details:** ~1,952 total atom rows across 3 files (1,642 EN evergreen + 250 platform/surface + 60 APAC
  localization); brand/author vibe schema (`SOCIAL-ATOM-BANK-VIBE-01`) and anti-spam variation gate
  code-wired and durable on `origin/main`; anti-spam gate wired by PR #123 and uniquely numbered 45;
  visual-license operator gate blocked 0/405 production-ready pending
  operator approval; Storyblocks b-roll bank 16 assets / 8 of 12 planned topics; weekly research-refresh
  cadence ran once (2026-07-18), no recurring mechanism; APAC review evidence is chat-level assertion only.
  No component has reached PROVEN-AT-BAR.

---

## Do-not-repeat notes for future sessions

- Do not report any part of this subsystem as "100% production-ready," "done," or "shippable" without
  naming its acceptance layer from §1.
- Do not re-discover live-scheduling `NOT_AUTHORIZED` as a bug — it is a ratified non-goal (Q-SOCIAL-
  LIVE-SCHEDULING-NONGOAL-CONFIRM-01, default already recommended "stays non-goal").
- Do not treat `review_status=reviewed_candidate` on the APAC bank as equivalent to a native-reviewer
  sign-off — it is not, per Lane B's audit (see gap #5 above).
- Do not treat a high row count (1,642 EN atoms) as proof of coverage density — apply the
  `project_atom_deficit_is_shape_not_count` lens (gap #6) before claiming any platform×locale×topic cell
  is well-covered.
