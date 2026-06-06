# Pearl News Sidebar — Function Inventory

**Last updated:** 2026-06-04
**Authored by:** Pearl_News (Phoenix Omega) — session `agent/pearl-news-sidebar-restore-20260603`
**Authority:** This document defines the stable function IDs (F1, F2, …) that the parity gate (`scripts/ci/check_pearl_news_sidebar_parity.py`) and the regression test (`tests/test_pearl_news_sidebar_parity.py`) enforce.
**Companion docs:** [`PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md`](./PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md) (chronology + canonical SHA chain), [`PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md`](./PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md) (PR #853 governing spec), [`PEARL_NEWS_WRITER_SPEC.md`](./PEARL_NEWS_WRITER_SPEC.md) §S (Sidebar Restoration Protocol).

---

## 0. How to use this document

- **F-IDs are STABLE.** Once an ID is assigned (F1, F2, …) the operator-anchored function it names does not change, even if the implementation moves or evolves.
- **Removing an F-ID** = a function is intentionally deprecated. Move the entry to §10 (Deprecated). Operator must approve via PR comment.
- **Adding an F-ID** = a NEW sidebar function ships. Author the entry in §1–§5 numbering range, update the parity-gate fingerprint in `CANONICAL_SIDEBAR_METADATA.json`, run D1 + D2.
- **Test fingerprints** are intentionally SHAPE-based, not content-based. Content (per-teacher exercise text, per-topic SDG bullets) is provided at runtime by data files; the parity gate verifies the renderer EMITS the slot, not what's in it.

---

## 1. F1 — Guided Practice Exercise Timer

**Card:** `sidebar-card exercise-card` (always rendered)
**Source SHA history:**
- `8070e81fd` (PR #853, 2026-05-04) — original 5-card scaffold, including exercise-card with `id="exerciseCard"`, `id="exerciseTimer"`, `class="step-dot"`, `onclick="toggleExercise()"`.
- `6e7dc9277` (branch-only, 2026-05-19) — re-restored when a v2 commit had collapsed it to a static practice-card. Restored full 8-step JS, step-dot progression, breath guide.
- **Latest restored content lives in:** `pearl_news/pipeline/assemble_v52.py` (lines ~1548 + JS at ~1391 in restored file)

**Backing code paths:**
- HTML emitter: `pearl_news/pipeline/assemble_v52.py` (function: `assemble_v52()` body, the `<!-- GUIDED EXERCISE -->` block)
- Per-teacher 8-step practice data: hardcoded `steps` array in the same file, branched by `teacher_id`
- JS: inline `<script>` block at end of sidebar (toggleExercise / advanceStep / pauseExercise / resumeExercise / showBreathGuide)

**Network endpoints:** none. Pure client-side timer.

**Dependencies:** teacher_id must be valid (junko / maat / ahjan / etc. — per `SOURCE_OF_TRUTH/teacher_banks/`).

**Test fingerprints (canonical anchors):**
- `<div class="sidebar-card exercise-card" id="exerciseCard">`
- `id="exerciseTimer"`
- `id="exerciseBtn"`
- `onclick="toggleExercise()"`
- `class="step-dot"`
- `function toggleExercise()`
- `function advanceStep()`

**Minimum constraints:** `min_step_dots: 5` (Junko has 8 steps; some teachers 5–8).

**Behavioral verification (acceptance #4):**
- Render sample article → click Begin button → timer counts down 5:00 → 4:59 → … → step-dots advance from filled to active to done → final "Done" state shows ✓.
- (Optional, browser-based) Use the `agent-browser` skill to open the rendered HTML in a headless browser, click `#exerciseBtn`, wait 3s, assert `#exerciseTimer` text changed.

**Current HEAD state (2026-06-04):** ✅ Restored from `78f115fe3` — `assemble_v52.py` line 1548 has the canonical `exerciseCard` div.

---

## 2. F2 — Free Practice Tool CTA (mini-app launcher)

**Card:** `sidebar-card cta-card`
**Source SHA history:**
- `8070e81fd` (PR #853, 2026-05-04) — original cta-card slot with `cta-title`, `cta-body`, `cta-primary` button.
- `45733349a` (branch-only, 2026-05-19) — refined: cta-card body now driven by `gen_z_reaction.reaction_id` lookup in `pearl_news/config/reaction_to_app.yaml`. Primary button launches `/apps/<app_filename>`. Secondary button anchor-jumps to the in-article practice.

**Backing code paths:**
- HTML emitter: `pearl_news/pipeline/assemble_v52.py` — `_mini_app_for_reaction()` helper + the `<!-- CTA -->` block
- App library: `somatic_exercise_freebee_apps/` (42 apps; 22 app*_ + 20 ex*_ series)
- Mapping: `pearl_news/config/reaction_to_app.yaml` (NEW — from 45733349a)
- Registry: `config/freebies/freebie_registry.yaml`

**Network endpoints:** Launch button → `https://phoenixprotocolbooks.com/apps/<app_filename>` (external mini-app library).

**Dependencies:**
- `gen_z_reactions` atom with valid `reaction_id` (per `pearl_news/atoms/gen_z_reactions/SCHEMA.md`)
- `practice_app_slug` set in article meta (else Launch button suppressed; secondary anchor remains)

**Test fingerprints:**
- `<div class="sidebar-card cta-card">`
- `class="cta-title"`
- `class="cta-body"`

**Note on H3 text:** The renderer emits `<h3>Free Tools</h3>`; live post 3724 has `<h3>Free Practice Tool</h3>` (a copy variant introduced at some point post-78f115fe3). The parity gate treats H3 text as a permitted delta — both variants are canonical.

**Gating behavior:** When `practice_app_slug` is empty (or `reaction_id` does not resolve in `reaction_to_app.yaml`), the Launch CTA button is suppressed. The sidebar still renders the cta-card div; only the link is absent. This is BY DESIGN — operator intent per `45733349a` commit body: _"the v2 sidebar card emits a 'Launch Practice ↗' button to /apps/<app_filename> plus a secondary 'Or read the practice ↓' link to the in-article anchor."_

**Current HEAD state:** ✅ Restored.

---

## 3. F3 — SDG Connection card

**Card:** `sidebar-card` with `<h3>SDG Connection</h3>`
**Source SHA history:**
- `8070e81fd` (PR #853, 2026-05-04) — original SDG card with `sdg-badge` span + single-bullet body.
- `45733349a` (branch-only, 2026-05-19) — expanded to 3-bullet detail per operator QA 2026-05-19: _"SDG bullets — 3 bullets, disclaimer relocated to article bottom."_

**Backing code paths:**
- HTML emitter: `pearl_news/pipeline/assemble_v52.py` — the `<!-- SDG DETAIL -->` block
- Data source: `pearl_news/config/sdg_news_topic_mapping.yaml` (topic → SDG number + target + 3 bullets)
- Fallback: article's `atom_file.sdg.primary` if topic mapping missing

**Network endpoints:** none. Pure data lookup.

**Dependencies:**
- `topic` set in article meta (mental_health / climate / peace_conflict / etc.)
- `sdg_news_topic_mapping.yaml` populated for that topic

**Test fingerprints:**
- `<h3>SDG Connection</h3>`
- `sdg-badge`

**Content constraint (not gate-enforced for synthetic probes):** `<li>` count ≥ 3 in production renders. The parity gate's synthetic probe does NOT populate SDG bullets (because the probe article doesn't carry real topic data); content-bullet verification is left to integration tests or live-page checks.

**Current HEAD state:** ✅ Restored.

---

## 4. F4 — Hot Take Poll

**Card:** `sidebar-card pn-poll-card`
**Source SHA history:**
- (Earlier static version) `8070e81fd` (PR #853, 2026-05-04) — static `<h3>Hot Take Poll</h3>` block; no interactive options yet.
- `78f115fe3` (branch-only, 2026-05-19) — **interactive layer authored from scratch**. Clickable `<button class="pn-poll-option">` with `data-pn-value`, animated `.pn-poll-bar`, `.pn-poll-count` percentages, `.pn-poll-status` text. Commit body explicitly notes: _"confirmed via git history that this never existed in this repo… Built it."_

**Backing code paths:**
- HTML emitter: `pearl_news/pipeline/assemble_v52.py` — the `<!-- POLL -->` block + the per-card button rendering loop
- JS handler: inline `pnReaderSignal` IIFE in same file (POSTs to `/wp-json/pearl-news/v1/signal`, localStorage tally)
- Aggregation: `pearl_news/pipeline/reader_signal_ingest.py` (NEW from 78f115fe3) — walks `artifacts/pearl_news/reader_signals/<YYYY-MM-DD>.jsonl` and emits `_engagement_scores.json` keyed by article_id with `poll_response_rate`, `poll_distribution`, etc.

**Network endpoints:**
- **POST `/wp-json/pearl-news/v1/signal`** — body: `{"kind":"poll_vote","article_id":"<string>","value":"<string>","ts":"<iso8601>"}`. Backed by `pearl_news/wp_plugin/pearl-news-signal.php` (d0075d31d).
- Response: `{"ok":true,"signal_id":"<uuid>","server_ts":"<iso8601>"}`.

**Dependencies:**
- 4 poll options hardcoded per article type ("My chest tightened" / "I scrolled past" / "I felt nothing" / "I texted someone") — these are SHAPE-stable; content varies by article emotional register
- `data-pn-article-id` attribute on the card div (matches `article_json["id"]` or `slug`)
- WP plugin deployed at `wp-content/mu-plugins/pearl-news-signal.php` on pearlnewsuna.org

**Test fingerprints:**
- `<div class="sidebar-card pn-poll-card"`
- `data-pn-article-id=`
- `<h3>Hot Take Poll</h3>`
- `class="pn-poll-options"`
- `class="pn-poll-option"`
- `data-pn-value=`
- `class="pn-poll-bar"`
- `class="pn-poll-count"`
- `class="pn-poll-status"`

**Behavioral verification (acceptance #4):**
- `curl -X POST -H 'Content-Type: application/json' -d '{"kind":"poll_vote","article_id":"sidebar-restore-probe","value":"diagnostic-test","ts":"2026-06-04T00:00:00Z"}' https://pearlnewsuna.org/wp-json/pearl-news/v1/signal` → expect `{"ok":true,"signal_id":"...","server_ts":"..."}`.
- ✅ Verified 2026-06-04 16:42 UTC: returned `{"ok":true,"signal_id":"7c791a49-0bb6-48e6-9034-8455bf2c8f98","server_ts":"2026-06-04T16:42:08+00:00"}`.

**Current HEAD state:** ✅ Restored.

---

## 5. F5 — Editorial Input ("Your Take" textarea + submit)

**Card:** `sidebar-card pn-take-card`
**Source SHA history:**
- (Earlier static version) `8070e81fd` (PR #853, 2026-05-04) — static `<h3>Your Take → Editorial Input</h3>` with textarea but no submit handler.
- `78f115fe3` (branch-only, 2026-05-19) — added `<button class="pn-take-submit">` + same `pnReaderSignal` IIFE handles `'take'` kind. Mailto fallback (`editorial@pearlnewsuna.org`) if endpoint unreachable.

**Backing code paths:**
- HTML emitter: `pearl_news/pipeline/assemble_v52.py` — the `<!-- CO-CREATION -->` block
- JS handler: same `pnReaderSignal` IIFE (handles both `.pn-poll-card` and `.pn-take-card`)
- Persistence: localStorage `pn_take_draft_<article_id>` (draft restore) + server JSONL via `/signal` endpoint
- Aggregation: `reader_signal_ingest.py` `take_submission_count` field

**Network endpoints:** same as F4 — POST `/wp-json/pearl-news/v1/signal` with body `{"kind":"take","article_id":"<string>","text":"<string>","ts":"<iso8601>"}`. Max 4000 chars per submission.

**Dependencies:** WP plugin honeypot fields (`website`, `url_field`, `homepage`) must NOT be in payload (anti-bot).

**Test fingerprints:**
- `<div class="sidebar-card pn-take-card"`
- `data-pn-article-id=`
- `<h3>Your Take → Editorial Input</h3>`
- `class="pn-take-input cocreation-input"`
- `class="pn-take-submit"`
- `class="pn-take-status"`

**Behavioral verification:**
- POST `{"kind":"take",…}` via same `/signal` endpoint → expect `{"ok":true,"signal_id":"...","server_ts":"..."}`.

**Current HEAD state:** ✅ Restored.

---

## 6. INFRA — `pnReaderSignal` IIFE (cross-cutting handler for F4 + F5)

**Not a card** — this is the cross-cutting JS handler that backs F4 and F5.

**Source SHA history:** `78f115fe3` only.

**Backing code paths:** Inline `<script>` block at end of sidebar (after toggleExercise). The IIFE iterates `document.querySelectorAll('.pn-poll-card')` and `.pn-take-card`, attaches click handlers, manages localStorage cache, posts to endpoint with mailto fallback.

**Test fingerprints:**
- `(function pnReaderSignal()`
- `const ENDPOINT = '/wp-json/pearl-news/v1/signal'`
- `const MAILTO_FALLBACK = 'editorial@pearlnewsuna.org'`
- `fetch(ENDPOINT`
- `localStorage`

**Current HEAD state:** ✅ Restored.

**Critical:** The OPERATOR-OBSERVED FAILURE MODE in the prior session was: **the markup for F4/F5 buttons was present, but this IIFE was MISSING from the rendered HTML.** Buttons rendered; clicks did nothing. The parity gate now treats this IIFE as REQUIRED (see `INFRA_reader_signal_iife` in `CANONICAL_SIDEBAR_METADATA.json`).

---

## 7. INFRA — WordPress must-use plugin (deployed backend)

**Not a card.** This is the WordPress server-side endpoint that F4 + F5 POST to.

**Source SHA history:** `d0075d31d` (branch-only, 2026-05-19).
**Deployment status:** Plugin file lives at `pearl_news/wp_plugin/pearl-news-signal.php` in repo. Deployed at `wp-content/mu-plugins/pearl-news-signal.php` on `pearlnewsuna.org` (auto-loads on WordPress boot; no admin activation step).

**Routes:**
- POST `/wp-json/pearl-news/v1/signal` — accept poll_vote + take signals, append to daily JSONL
- GET `/wp-json/pearl-news/v1/signal/aggregate/{article_id}` — return 30-day tally

**Rate limits:** 20/min, 500/day per hashed IP.

**Test fingerprints (PHP side):**
- `add_action('rest_api_init', function () { register_rest_route(PEARL_NEWS_SIGNAL_NAMESPACE, ...`
- `'methods' => 'POST'`
- `pearl_news_signal_handle_post`

**Behavioral verification:** Probe `GET /wp-json/pearl-news/v1` returns route listing including `/signal`.

**Current HEAD state:** ✅ Restored (repo). Plugin deployed live (verified 2026-06-04).

**Drift note:** Deployed plugin exposes 8 more endpoints (`/poll`, `/editorial`, `/advocate`, `/freebie`, `/feedback`, plus 4 GET variants) than the repo plugin implements. See `Q-PNS-PLUGIN-DRIFT-01` in version history §17. Operator accepted the lag for this PR; follow-up workstream needed.

---

## 8. Historical / removed functions

None as of 2026-06-04. (If a future operator decision deprecates a function, move its entry here with an explicit "Deprecated at SHA / date / by operator." line.)

---

## 9. How to add a NEW sidebar function

1. Pick the next F-ID (F6, F7, …).
2. Author the markup emitter in `pearl_news/pipeline/assemble_v52.py`.
3. Add an entry to this document with the full template (Card / Source / Backing code paths / Endpoints / Dependencies / Test fingerprints / Current HEAD state).
4. Add a `function_test_fingerprints.<F-ID>` block to `artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR_METADATA.json`.
5. Refresh the canonical snapshot (`artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html`) by extracting from a freshly-rendered live post.
6. Run `python3 scripts/ci/check_pearl_news_sidebar_parity.py` — must return 0.
7. Run `pytest tests/test_pearl_news_sidebar_parity.py` — all tests must pass.
8. PR body must include the operator-quote justifying the new function.

---

## 10. Quick-reference fingerprint summary (for the parity gate)

| F-ID | Card class | H3 text | Mandatory marker |
|------|-----------|---------|------------------|
| F1 | `sidebar-card exercise-card` | varies (`Practice · …`) | `id="exerciseCard"`, `toggleExercise()` |
| F2 | `sidebar-card cta-card` | "Free Tools" / "Free Practice Tool" | `cta-title`, `cta-body` |
| F3 | `sidebar-card` | "SDG Connection" | `sdg-badge` |
| F4 | `sidebar-card pn-poll-card` | "Hot Take Poll" | `pn-poll-option`, `data-pn-value`, `pn-poll-bar` |
| F5 | `sidebar-card pn-take-card` | "Your Take → Editorial Input" | `pn-take-input`, `pn-take-submit` |
| INFRA | (script block) | — | `pnReaderSignal`, `/wp-json/pearl-news/v1/signal`, `localStorage` |

---

**End of document.**
