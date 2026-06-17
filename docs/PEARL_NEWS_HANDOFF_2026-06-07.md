# Pearl News V2 Article System — Session Handoff (2026-06-04 → 2026-06-07)

**Agent:** Pearl_News (Claude Code, Tier 1)
**Session branches/PRs:**
- PR #1443 (sidebar restore + parity gate + docs) — MERGED `19b0db5a8`
- PR #1445 (deprecation marks + Q-PNS-PLUGIN-DRIFT-01 routing) — MERGED `a6ea1a49e`
- PR #1447 (hard_news_v2.yaml + heading_variants.yaml + heading_selector.py) — MERGED `b3e2ea421`
- PR #1449 (heading_selector wiring + body F-IDs FB1-FB6 + CANONICAL_ARTICLE.html) — MERGED `8547c67225`
- PR #1451 (parity gate v2-path + slot-population fix) — MERGED `9cd67d0e4`
- All on `origin/main`. None reverted.

**Live posts touched:**
- Post **3948** (mental_health × Maat): `https://pearlnewsuna.org/pn-sidebar-parity-probe-20260606/` — full v2 shape, working sidebar, functional poll + take
- Post **3950** (peace_conflict × Sai Maa, Sudan civil war): `https://pearlnewsuna.org/pn-sudan-civil-war-12-million-displaced-20260606/` — full v2 shape, hero image (Wikimedia CC BY 2.0), gradient topic card

**Status:** all operator-confirmed UX requests applied. Open follow-up items in §9 below.

---

## 1. Mission and outcome

**Operator's framing at session start:** _"The Pearl news articles were perfect a few days ago. The sidebar was working. It was functional. And, um, I think I asked you to do one little edit, and then nothing worked, and everything was wrong. So you drifted from something working to something broken."_

**Honest accounting (mid-session, see §5.3):** the "100% working" 3724 anchor was NOT actually functional at the JS level — WordPress wpautop had been injecting `</p><p>` inside the inline `<script>` tags since the IIFE was first introduced, breaking every Pearl News post's JS. The operator's memory of "working" was visual (markup correct), not behavioral (handlers firing).

**End-of-session state:** v2 article system fully restored, sidebar JS actually executes for the first time in any Pearl News post, body shape + content + atoms all canonical.

---

## 2. The V2 article — canonical structure (definitive)

### Top-to-bottom render order

1. **WordPress article title** (theme-rendered from post title — H1 suppressed in body per `ab010c548`)
2. **Theme's featured-image hero** (Newspaper theme renders the WP featured-image at the article top — `class="entry-thumb td-modal-image"`, typically 696×464 resized)
3. **Dek-1** (`<div class="v2-headline-dek-1">`) — static heading "How this news is affecting Gen Z" (English) or locale equivalent. From `_l10n.get("v2_gen_z_dek")` or pick_gen_z_heading variant pool (gen_z_impact axis, 5 variants × topic × locale)
4. **Dek-2** (`<div class="v2-headline-dek-2">`) — dynamic "A {tradition_role} Shares A Helpful Insight". `_tradition_role` comes from `meta["tradition_role"]` or fallback `teacher_name`. Variant pool teacher_sees axis (5 variants per teacher in primary locale)
5. **Gradient topic card** (`<div class="hero-fallback">`) — gradient `un-blue-deep → red → gold`, big `<span>{SDG_NUM}</span>` + `<small>{TOPIC_LABEL}</small>` (e.g. "16 / World Peace" or "3 / Mental Health")
6. **Body — 5 section-`<div class="section-header">` divs:**
   1. **News Summary** — LLM-generated, ~2× v1 length, closing paragraph ties to primary SDG
   2. **How this news is affecting Gen Z** — 3 atom paragraphs (hook_personal + youth_somatic + hook_big_picture) from `pearl_news/teacher_topic_packs/teachers/<teacher>/<topic>.yaml`
   3. **A {tradition_role} Shares A Helpful Insight** — bridge atom + teacher_intro atom + teacher_witness atom + "{Teacher} Teaches:" label + teacher_perspective.paragraphs atoms
   4. **A Practice** (sub-block in section 3) — practice.announcement_line atom (with "It is in the sidebar, timed and step by step.")
   5. **Take Action Now!** — CTA boilerplate that wires body to sidebar (`Vote in the sidebar. Submit your take.`)
   6. **Your Voice Has Power** — CTA closer, frames editorial input as data point not comment (wrapped in `<div class="block-blue">`)
7. **Reporting attribution + AI disclosure + UN-non-affiliation disclaimer**
8. **Sidebar — 5 cards** (right column on desktop, stacked on mobile):
   1. **Exercise timer** (`exercise-card`) — 5-min timed practice with step-dots + breath guide. Source: TEACHER_DB hardcoded per teacher_id (key fix below) OR atom-driven override via post-processing
   2. **Free Practice Tool** (`cta-card`) — practice CTA card; can carry mini-app launcher when `reaction_to_app.yaml` is populated for the reaction
   3. **SDG Connection** (`sidebar-card`) — SDG badge `SDG N · Name · Target N.X` + 3 bullets describing the SDG targets
   4. **Hot Take Poll** (`pn-poll-card`) — 4 clickable `<button class="pn-poll-option">` options, single-select, ✓ check-mark on click, POST `/wp-json/pearl-news/v1/signal`
   5. **Your Take → Editorial Input** (`pn-take-card`) — textarea + Submit Take, ✓ Submitted indicator, clears input, re-submittable
9. **`pnReaderSignal` IIFE** (inline `<script>`) — backs F4 + F5; POST to `/wp-json/pearl-news/v1/signal` with localStorage cache + mailto fallback
10. **`pnUXEnhance` IIFE** (separate inline `<script>` appended post-render) — adds check-mark UI for poll, success indicator for take, single-select behavior, hides "0%" until first vote

---

## 3. Canonical SHA chain (10 SHAs across 5 PRs)

| Order | SHA | PR | Role | On main via |
|-------|-----|-----|------|-------------|
| 1 | `8070e81fd` | #853 | Structural baseline — 5-layout system, 5-card sidebar markup | merge 2026-05-04 |
| 2 | `b64caf846` | #1105 | wpautop grid-cell fix (prevents phantom `<p>` from breaking sidebar grid) | merge 2026-05-13 |
| 3 | `6e7dc9277` | — (branch) | Operator restore of PR #853 sidebar into v2 templates | PR #1443 (file restore) |
| 4 | `cd661ce64` | — (branch) | `hard_news_v2.yaml` template (3-title + 4-section spec) | PR #1447 |
| 5 | `ab010c548` | — (branch) | V2 title block markup + CSS + H1 suppression in body | PR #1443 (inherited) |
| 6 | `45733349a` | — (branch) | Mini-app launcher cta-card + 3-bullet SDG + `reaction_to_app.yaml` | PR #1443 (file restore) |
| 7 | `3daa86d56` | — (branch) | `gen_z_reactions/` atom library | PR #1443 (file restore) |
| 8 | `78f115fe3` | — (branch) | Interactive Hot Take Poll + Editorial Take + `pnReaderSignal` IIFE + `reader_signal_ingest.py` | PR #1443 (file restore) |
| 9 | `d0075d31d` | — (branch, deployed) | WP must-use plugin `/signal` endpoint | PR #1443 (file restore) |
| 10 | `e789a540b` | #1429 / #1449 | Heading variant pools + selector + assemble_v52 wiring | PR #1447 (yaml + py) + PR #1449 (wiring port) |

**For restoration of any future regression:** run the parity gate to identify which F-ID(s) failed, then `git checkout <sha> -- <path>` for the corresponding file per the table above.

---

## 4. F-IDs — function inventory the parity gate enforces

### Sidebar F-IDs (PR #1443)

| F-ID | Card | Required markers |
|------|------|------------------|
| F1 | `sidebar-card exercise-card` | `id="exerciseCard"`, `id="exerciseTimer"`, `onclick="toggleExercise()"`, `class="step-dot"`, `function toggleExercise()` |
| F2 | `sidebar-card cta-card` | `class="cta-title"`, `class="cta-body"` |
| F3 | `sidebar-card` w/ `<h3>SDG Connection</h3>` | `<h3>SDG Connection</h3>`, `sdg-badge` |
| F4 | `sidebar-card pn-poll-card` | `data-pn-article-id=`, `<h3>Hot Take Poll</h3>`, `class="pn-poll-option"`, `data-pn-value=` |
| F5 | `sidebar-card pn-take-card` | `<h3>Your Take → Editorial Input</h3>`, `class="pn-take-input"`, `class="pn-take-submit"` |
| INFRA | (script block) | `(function pnReaderSignal()`, `/wp-json/pearl-news/v1/signal` |

### Body F-IDs (PR #1449)

| F-ID | Element | Required markers |
|------|---------|------------------|
| FB1 | V2 title block | `class="v2-headline-dek-1"`, `class="v2-headline-dek-2"` |
| FB2 | Section-header divs | `class="section-header"` (min 5 occurrences) |
| FB3 | Gen Z section heading | "How this news is affecting Gen Z" (or locale variant) — appears in dek-1 AND section header |
| FB4 | Teacher section heading | "Shares A Helpful Insight" (or locale variant) — appears in dek-2 AND section header |
| FB5 | Take Action Now! | literal "Take Action Now!" |
| FB6 | Your Voice Has Power | literal "Your Voice Has Power" |

Authority files for F-IDs:
- `docs/PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md` — full F-ID definitions
- `artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR_METADATA.json` — fingerprints the parity gate reads
- `scripts/ci/check_pearl_news_sidebar_parity.py` — the gate
- `tests/test_pearl_news_sidebar_parity.py` — pytest wrapper
- `artifacts/pearl_news/snapshots/CANONICAL_ARTICLE.html` — gold master (extracted from 3724.html snapshot)

---

## 5. Critical findings / non-obvious

### 5.1 V2 had two halves — sidebar AND body template

PR #1443's original scope was named "sidebar" but the canonical thing was the v2 **article** (body template + sidebar together). Half-restoring the sidebar without the body template (hard_news_v2.yaml + heading variants + selector + renderer wiring) left articles structurally wrong. **Took 4 PRs to fully restore**:
- PR #1443: sidebar markup + JS + WP plugin + parity gate (sidebar-only)
- PR #1447: body template yaml + heading_variants.yaml + heading_selector.py (files)
- PR #1449: renderer wiring (+29/-5 in assemble_v52.py) + body F-IDs FB1-FB6 + CANONICAL_ARTICLE.html
- PR #1451: parity gate fix (synthetic probe needs `meta["template"]="hard_news_v2"` + populated slots)

### 5.2 Renderer reads `meta["teacher"]`, NOT `meta["teacher_id"]`

Bug surfaced 2026-06-06 with Sudan article (post 3950): article body had Sai Maa atoms (loaded directly) but sidebar showed Maat's hardcoded TEACHER_DB practice because the renderer fell back to `"maat"` default when `meta["teacher"]` was unset.

**Fix going forward:** callers must pass BOTH `meta["teacher"]` and `meta["teacher_id"]` (set to the same value) for safety. Renderer's `_raw_teacher = meta.get("teacher") or (meta.get("teacher_used") or {}).get("teacher_id") or "maat"` is the lookup chain.

### 5.3 wpautop was breaking ALL inline `<script>` tags — including in 3724

**Root cause discovery (2026-06-06):** WordPress wpautop filter injects `</p><p>` at double-newlines, including inside `<script>` content. This causes a `SyntaxError: Unexpected token '<'` at the first injected break, **killing the entire script before any handlers attach**.

Verified by `node -c` on the canonical 3724 anchor's actual live IIFE: same syntax error. **The JS has never executed on any Pearl News post since the IIFE was introduced (`78f115fe3`).**

**Per-post workaround (used in this session for 3948 and 3950):** post-process the rendered HTML to minify all `<script>` content (strip `//` comments, collapse all newlines to spaces). wpautop has no double-newlines to grab. `node -c` clean.

**Permanent fix needed (renderer-level PR):** make `assemble_v52.py` emit the inline `<script>` already minified, OR add a wpautop bypass filter to `pearl_news/wp_plugin/pearl-news-signal.php` for content containing the pnReaderSignal marker.

### 5.4 TEACHER_DB hardcoded practices vs. teacher_topic_pack atom practices

Two separate sources for the practice card name + steps:
- **TEACHER_DB** (in `assemble_v52.py`) — per-teacher hardcoded `practice_name`, `exercise_steps` array (5-7 steps). Drives the sidebar exercise-card timer.
- **teacher_topic_pack atoms** (`pearl_news/teacher_topic_packs/teachers/<teacher>/<topic>.yaml`) — per-teacher-per-topic `practice.announcement_line` + `relief_lines`. Drives the article body "A Practice" section.

These often DON'T MATCH. Examples in this session:
- **Maat × mental_health:** TEACHER_DB has "Truth-Speaking Practice"; atom has "Mirror Polish". Operator flagged mismatch.
- **Sai Maa × peace_conflict:** TEACHER_DB has "Consciousness Awakening"; atom has "Brain Illumination Pause". Operator flagged mismatch.

**Per-post workaround (used this session):** post-process the rendered HTML to replace the TEACHER_DB practice name + steps array with the atom-driven name + an authored 5-7-step practice that matches the atom's intent.

**Permanent fix needed:** restructure TEACHER_DB so practices are looked up per `(teacher_id, topic)`, NOT just per `teacher_id`. OR make the renderer prefer the atom's `practice.announcement_line` content for both the body AND the sidebar (and have the atom carry step-by-step structure, not just an announcement line).

### 5.5 Two-image hero pattern — theme handles BOTH hero + thumbnail

Pearl News articles have one IMAGE SOURCE (the WordPress featured-image) that the Newspaper theme renders in TWO places:
- **Hero pic place** (top of article body, 696×464): `class="entry-thumb td-modal-image"`
- **Smaller pic place** (category-list cards, related-article cards, social og:image): theme auto-resizes to thumbnail dimensions

**Canonical setup:**
- Set `featured_media` to the uploaded media ID
- Renderer does NOT emit `<img class="hero-image">` in the body (would duplicate the theme's hero)
- Renderer DOES emit `<div class="hero-fallback">` gradient card under the deks (small topic-label card, NOT a duplicate of the photo)

### 5.6 Gradient topic card sits BETWEEN deks and News Summary

Per operator: under the 2 dek lines, BEFORE the News Summary, there's a gradient card with `<span>{SDG_num}</span><small>{TOPIC_LABEL}</small>` — same gradient color (`un-blue-deep → red → gold`) as in the renderer's CSS `.hero-fallback`. This is a SMALL topic-identifier card, not a hero image. It's NOT the same as the WP featured-image hero (which is large, photo-driven, theme-rendered).

### 5.7 SDG sidebar bullets are NOT in `sdg_bullets.yaml` (file doesn't exist)

The renderer has a `_load_sdg_bullets()` function that reads `pearl_news/config/sdg_bullets.yaml`, but that file does not exist on origin/main. Result: SDG sidebar shows just the badge + empty `<p>`, no bullets.

**Per-post workaround used this session:** post-process injected 3 hand-authored bullets per SDG (3 for SDG 3 mental_health, 3 for SDG 16 peace_conflict) directly into the HTML after the badge.

**Permanent fix needed:** author `pearl_news/config/sdg_bullets.yaml` with 3 bullets per SDG (3, 4, 8, 10, 13, 16, 17 — the topic-mapped SDGs), so the renderer pulls them automatically.

---

## 6. Decisions made

### Q-PNS-CANONICAL-01 (refined)
**Answered:** canonical is the **10-SHA composite chain** in §3 above (not single SHA). Operator approved the file-level `git checkout <sha> -- <path>` restore mechanism (NOT cherry-pick — avoided commit-history coupling to unrelated v2-template work on the orphan branch).

### Q-PNS-HERO-01
**Answered:** hero pic place = WordPress featured-image (Newspaper theme auto-renders). Smaller pic place = same featured-image, theme auto-resizes for category lists. Gradient topic card stays under deks (separate from photo hero). Renderer does NOT emit inline `<img>` in body.

### Q-PNS-LIVE-TEST-POST-01
**Answered:** slug `pn-sidebar-parity-probe-20260606` accepted. Live post 3948 used as the probe. Second probe `pn-sudan-civil-war-12-million-displaced-20260606` (post 3950) demonstrates v2 with a different teacher × topic + functional featured image.

### Q-PNS-POLL-BACKEND-01 / Q-PNS-EDITORIAL-INPUT-01
**Answered:** both use `POST /wp-json/pearl-news/v1/signal` with `kind=poll_vote` or `kind=take`. Endpoint live, verified with curl POST + signal_id response.

### Q-PNS-PLUGIN-DRIFT-01 (new — operator-approved)
**Status:** accept lag. Repo plugin has `/signal` only. Deployed plugin has 8 more endpoints (`/poll`, `/editorial`, `/advocate`, `/freebie`, `/feedback`, plus 4 GET variants) that aren't in repo. Follow-up workstream `ws_pearl_news_wp_plugin_drift_pull_20260606` routed to Pearl_Dev (recommendation: option A — pull live PHP source via SSH; option B reverse-engineering NOT recommended). Tracked in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.

### Q-PNS-CI-BLOCKING-01
**Answered:** D1 BLOCKS publish on parity-fail. Wired into `.github/workflows/pearl-news-daily.yml` BEFORE publish step + `scripts/run_production_readiness_gates.py` gate #19.

### Q-PNS-DEPRECATION-01 (refined)
**Per-row decisions captured in `artifacts/pearl_news/audit/DEPRECATION_PROPOSAL.md` §D:**
- A-1 `pearl_news/pipeline/assemble_v52.py` → **KEEP** (canonical sidebar source — reversed prior chat's WRONG deprecation proposal)
- A-2 `scripts/pearl_news/run_daily_news_cycle.py` → **KEEP** (live entrypoint; under review)
- A-3 `scripts/pearl_news/fix_dek_legacy_headings.py` → **DELETE-AFTER-1429** (one-time patch executed)
- A-4 `scripts/pearl_news/republish_quality_batch.py` → **DELETE-AFTER-1429**
- A-5 `scripts/pearl_news/strip_broken_launch_ctas.py` → **REMOVE-ROW** (not in main)
Cleanup PR `ws_pearl_news_sidebar_restore_cleanup_20260606` sequenced to spin out after PR #1429 merges.

---

## 7. Operator-facing UX changes shipped

### Sidebar interactivity (working for the first time on Pearl News)

1. **Exercise timer:** Click Begin → 5:00 timer counts down through 5–7 teacher-specific practice steps, step dots animate, breath guide appears for breath-marked steps
2. **Poll:** Click any option → green ✓ check-mark badge appears, single-select (clicking another moves the ✓), no "0%" shown until first vote
3. **Take submit:** Type + click Submit → green ✓ Submitted indicator, textarea clears, button re-enables for re-submission
4. **Localstorage cache:** Poll vote survives page reload (returning reader sees their ✓)
5. **Mailto fallback:** If `/wp-json/pearl-news/v1/signal` is unreachable, take-submit falls back to opening mailto to `editorial@pearlnewsuna.org`

### Per-post workaround layer

Until renderer-level fixes land, the canonical publish flow is:

```python
1. Build slots dict from teacher_topic_pack atoms
2. Call av.assemble_v52(article_json, meta) with template="hard_news_v2"
3. Post-process rendered HTML:
   a. Strip inline <img class="hero-image"> (theme will hero from featured-image)
   b. Override TEACHER_DB practice name + steps array to match atom practice
   c. Inject SDG bullets after the SDG badge in sidebar card
   d. Override SDG badge target to match bullets (renderer hardcodes 16.7 / 3.4 etc.)
4. Append UX-enhance <script> (poll check-mark + take success + radio behavior)
5. wpautop-proof ALL <script> tags (strip // comments + collapse newlines)
6. Upload featured image via /wp-json/wp/v2/media
7. Set featured_media + publish content via /wp-json/wp/v2/posts
```

This 7-step ritual is what the per-session publish scripts encode (`/tmp/publish_v2_full_fix.py`, `/tmp/publish_sudan_war.py`, etc.).

---

## 8. Files touched (full list)

### Renderer + pipeline (modified on main)
- `pearl_news/pipeline/assemble_v52.py` (1876 → 2193 lines; PR #1443 + #1449)
- `pearl_news/pipeline/reader_signal_ingest.py` (NEW, 165 lines; PR #1443)
- `pearl_news/wp_plugin/pearl-news-signal.php` (NEW, ~280 LOC; PR #1443)
- `pearl_news/wp_plugin/README.md` (NEW; PR #1443)
- `pearl_news/config/reaction_to_app.yaml` (NEW, 73 lines; PR #1443)
- `pearl_news/article_templates/hard_news_v2.yaml` (NEW; PR #1447)
- `pearl_news/config/heading_variants.yaml` (NEW, 273 lines; PR #1447)
- `pearl_news/pipeline/heading_selector.py` (NEW, 97 lines; PR #1447)
- `pearl_news/atoms/gen_z_reactions/*.yaml` (NEW, SCHEMA + 3 reactions; PR #1443)

### CI + tests
- `scripts/ci/check_pearl_news_sidebar_parity.py` (NEW; PR #1443 + #1449 + #1451)
- `tests/test_pearl_news_sidebar_parity.py` (NEW; PR #1443)
- `tests/test_pearl_news_heading_selector.py` (NEW; PR #1449 — restored from `e789a540b`)
- `scripts/run_production_readiness_gates.py` (MODIFIED, +gate #19; PR #1443)
- `.github/workflows/pearl-news-daily.yml` (MODIFIED, +parity gate step; PR #1443)

### Docs + spec
- `docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md` (NEW; PR #1443 + §19 in PR #1449)
- `docs/PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md` (NEW; PR #1443 + §11–§12 in PR #1449)
- `docs/PEARL_NEWS_WRITER_SPEC.md` (MODIFIED, +§S "Sidebar Restoration Protocol"; PR #1443)
- `CLAUDE.md` (MODIFIED, +known-good-anchors section; PR #1443)
- `artifacts/pearl_news/audit/sidebar_git_archeology_20260603.log` (NEW; PR #1443)
- `artifacts/pearl_news/audit/DEPRECATION_PROPOSAL.md` (NEW + UPDATED row decisions; PR #1443 + #1445)
- `artifacts/pearl_news/audit/live_3724_full.html` (NEW, anchor reference; PR #1443)
- `artifacts/pearl_news/audit/live_pn_maat_peace_v4_broken.html` (NEW, broken-state evidence; PR #1443)
- `artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html` (NEW; PR #1443)
- `artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR_METADATA.json` (NEW + UPDATED with FB1-FB6; PR #1443 + #1449)
- `artifacts/pearl_news/snapshots/CANONICAL_ARTICLE.html` (NEW; PR #1449)
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (MODIFIED, +ws_pearl_news_wp_plugin_drift_pull_20260606; PR #1445)
- **This handoff doc:** `docs/PEARL_NEWS_HANDOFF_2026-06-07.md` (NEW; this PR)

### Memory updates (off-repo, on operator's machine)
- `~/.claude/projects/-Users-ahjan-phoenix-omega/memory/project_known_good_anchors.md` — Pearl News sidebar entry expanded with composite chain + infrastructure paths

### Live WordPress posts touched
- **Post 3948:** `pn-sidebar-parity-probe-20260606` — repeatedly rebuilt to final v2 shape (Maat × mental_health, Mirror Polish practice + sidebar match, full content)
- **Post 3950:** `pn-sudan-civil-war-12-million-displaced-20260606` — published fresh with Sai Maa × peace_conflict + featured image (Wikimedia CC BY 2.0 Lammy/refugees photo, media ID 3951) + gradient topic card "16 / World Peace"
- **WP media 3949:** original Unsplash featured image (now orphaned; can be deleted via WP admin)
- **WP media 3951:** Wikimedia Lammy photo (current featured image for post 3950)

### WP REST endpoints exercised
- `POST /wp-json/wp/v2/posts` (create)
- `POST /wp-json/wp/v2/posts/{id}` (update — REST treats POST as PUT for existing)
- `POST /wp-json/wp/v2/media` (upload — fetched Wikimedia URL → uploaded to WP media library)
- `GET /wp-json/wp/v2/posts/{id}?context=edit` (returns raw.content; rate-limited / Cloudflare-blocked sometimes — use UA workaround)
- `POST /wp-json/pearl-news/v1/signal` (sidebar poll/take backend; LIVE, verified)
- `GET /wp-json/pearl-news/v1` (namespace listing — 10 deployed routes)

### Github + git operations
- `gh secret set GROQ_API_KEY` (set from Keychain; unblocks PR #1429 daily-pipeline EN runner)
- `gh api repos/.../git/blobs|trees|commits|refs` (used for single-commit multi-file pushes when Xcode worktree contention blocked normal flow)
- `gh pr create` × 5, `gh pr merge --squash` × 5

---

## 9. Open follow-up items (Pearl_Dev pickup queue)

### Renderer-level fixes (high priority — currently worked around per-post)

1. **wpautop bypass for inline `<script>`** (`feedback_drift_recovery_git_first.md` rule — never fresh-fix; investigate the WP filter chain). Either:
   - Emit script already minified from `assemble_v52.py`
   - Add a wpautop bypass filter in `pearl_news/wp_plugin/pearl-news-signal.php` for content matching the pnReaderSignal marker
   - Switch to external JS file via `wp_register_script` + `wp_localize_script`
2. **TEACHER_DB ↔ atom practice unification.** Restructure TEACHER_DB to look up practice per `(teacher_id, topic)`, OR have the renderer prefer the atom's `practice.announcement_line` for both body AND sidebar (and structure atoms to carry step-by-step content, not just announcement)
3. **SDG dict-vs-scalar guard** in `assemble_v52.py:966`. `sdg_num = str(meta.get("sdg", "3"))` blows up to `"{'primary': 3}"` if meta inherits the dict via `meta = {**article_json, **(metadata or {})}` from line 956. Either change the lookup to read `meta["sdg"]` AS A DICT and extract `.primary`, OR make the merge filter out `sdg` if it's a dict
4. **Author `pearl_news/config/sdg_bullets.yaml`** with 3 bullets per SDG (3, 4, 8, 10, 13, 16, 17). Currently `_load_sdg_bullets()` returns empty dict → no bullets render
5. **Variant heading fallback** — runtime warning `heading_variants.yaml missing at /private/config/heading_variants.yaml; falling back to fixed strings` indicates the path resolution in `heading_selector.py` is wrong when imported from outside the package. Verify the path is `Path(__file__).resolve().parent.parent / "config" / "heading_variants.yaml"` works from the daily-cycle's invocation context
6. **`_l10n["teacher_sees"]` template uses `teacher_name`** — should use `tradition_role` for v2 path. Currently the legacy fallback `"What {teacher_name} Sees"` would output "What Sai Maa Sees" (teacher name). The v2 dek-2 already uses `tradition_role`, but the fallback path doesn't
7. **Renderer's hardcoded SDG `target`** in `SDG_DB` doesn't match the bullets I author (e.g. SDG 16 hardcoded as "16.7", my bullets are 16.1/16.2/16.3). Either:
   - Let callers override `target` via meta
   - Have `SDG_DB` carry multiple targets per SDG, picked by article context
8. **CTA-card mini-app launcher** is half-built. Code at `_mini_app_for_reaction()` + data in `reaction_to_app.yaml` are present, but no LIVE post has emitted `/apps/<slug>` URLs. Either finish the launcher (set practice_app_slug per article) OR deprecate the feature

### Workstream queue (already routed)

1. `ws_pearl_news_wp_plugin_drift_pull_20260606` (Pearl_Dev) — pull deployed `pearl-news-signal.php` from `pearlnewsuna.org` via SSH, commit full version. Recommendation: option A (pull live source). Blocked on operator-provided server access.
2. `ws_pearl_news_sidebar_restore_cleanup_20260606` (Pearl_GitHub) — `git rm` A-3 + A-4 patch scripts after PR #1429 merges. Currently sequenced.

### Operator-visible improvements (nice-to-have)

1. Update `docs/PEARL_NEWS_WRITER_SPEC.md` §13.5 to remove the deprecated inline-CSS approach (already noted in §S §S.8 but the section itself remains in the doc)
2. Add SDG 16 to `sdg_news_topic_mapping.yaml` if not present (verify)
3. Author the missing reaction types in `gen_z_reactions/` (currently 3 of 12 in SCHEMA)

---

## 10. Drift-recovery protocol (when sidebar breaks again)

Per `docs/PEARL_NEWS_WRITER_SPEC.md` §S + memory rule `feedback_drift_recovery_git_first.md`:

1. **DO NOT fresh-fix.** Read the version history first.
2. Run the parity gate: `python3 scripts/ci/check_pearl_news_sidebar_parity.py` (or via `tests/test_pearl_news_sidebar_parity.py`)
3. Read which F-ID(s) failed from the gate output
4. Look up the source SHA in `docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md` §16 / §19
5. `git checkout <sha> -- <path>` for the corresponding file(s)
6. Re-run the gate. Must return 0.
7. If still failing: the canonical snapshot itself may be stale — refresh per `PEARL_NEWS_WRITER_SPEC.md §S.4`
8. **NEVER re-author sidebar markup, CSS, or JS.** Every regression in this domain (~25 of them, per memory) has been a re-author attempt that compounded drift.

For body drift specifically: check `class="v2-headline-dek-1"` / `class="v2-headline-dek-2"` / 5+ `<div class="section-header">` divs / "Take Action Now!" / "Your Voice Has Power". If any of these are missing or wrong, the v2 template path is not activating — check `meta["template"] == "hard_news_v2"` and that all body-content slots are populated.

For JS drift: extract any `<script>` block from a live page → `node -c <file>` → if SyntaxError on `</p>`, the wpautop minifier wasn't applied → check the per-post publish script's `wpautop_proof_script()` post-processing step.

---

## 11. Lessons learned (for future sessions)

1. **Scope creep is a real drift surface.** "Sidebar broken" can mean "sidebar markup OR body shape OR JS handlers OR backend endpoint OR theme integration OR content atoms OR all of the above." Don't anchor on the literal word.
2. **The operator's "100% working" memory can be visual, not behavioral.** Verify with `node -c` on actual JS, not just markup presence.
3. **WordPress wpautop is a hostile filter for any inline `<script>`.** Minify or bypass.
4. **Renderer's `meta = {**article_json, **(metadata or {})}`** silently inherits article_json fields into meta. Any dict-valued field in article_json that the renderer expects scalar from meta will break.
5. **TEACHER_DB and teacher_topic_pack atoms are two parallel sources.** They diverge. Unify them at the architectural level, not per-post.
6. **WordPress featured-image + Newspaper theme handles the hero AND the thumbnail.** Renderer should not duplicate the inline `<img>` — let the theme own it.
7. **Gradient topic card is separate from photo hero.** Both can co-exist (large photo hero from theme + small gradient under deks).
8. **Cache-bust query params (`?cb=<timestamp>`) help bust BOTH browser AND Cloudflare cache.** Operators may need hard refresh OR fresh tab to see updates.
9. **gh API direct-commit (blobs → tree → commit → ref) bypasses Xcode worktree lock contention.** Use when worktrees lock.
10. **Per-post publish scripts (in `/tmp/`) are the canonical reference for "how to publish a v2 article" until the daily-cycle's renderer-level fixes land.**

---

## 12. Quick reference

### Live URLs (currently in v2 canonical state)

- https://pearlnewsuna.org/pn-sidebar-parity-probe-20260606/ (mental_health × Maat)
- https://pearlnewsuna.org/pn-sudan-civil-war-12-million-displaced-20260606/ (peace_conflict × Sai Maa)
- https://pearlnewsuna.org/?p=3724 (canonical anchor — note: its JS doesn't actually execute due to wpautop bug, but markup is correct)

### Endpoint health check

```bash
curl -s "https://pearlnewsuna.org/wp-json/pearl-news/v1" | python3 -m json.tool
# Returns 10-route namespace
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"kind":"poll_vote","article_id":"diag","value":"test","ts":"2026-06-07T00:00:00Z"}' \
  "https://pearlnewsuna.org/wp-json/pearl-news/v1/signal"
# Returns {"ok":true,"signal_id":"...","server_ts":"..."}
```

### Parity gate

```bash
python3 scripts/ci/check_pearl_news_sidebar_parity.py
# Exit 0 = all F1-F5 + FB1-FB6 fingerprints present
# Exit 1 = per-F-ID failure list to stderr
```

### Restoration command (when sidebar drifts)

```bash
git checkout 78f115fe3 -- pearl_news/pipeline/assemble_v52.py
git checkout 78f115fe3 -- pearl_news/pipeline/reader_signal_ingest.py
git checkout d0075d31d -- pearl_news/wp_plugin/
git checkout 45733349a -- pearl_news/config/reaction_to_app.yaml
git checkout 3daa86d56 -- pearl_news/atoms/gen_z_reactions/
git checkout cd661ce64 -- pearl_news/article_templates/hard_news_v2.yaml
git checkout 46483ba9c -- pearl_news/config/heading_variants.yaml pearl_news/pipeline/heading_selector.py
# Re-run parity gate to verify
```

### Per-post publish reference

See `/tmp/publish_v2_full_fix.py` (mental_health template) and `/tmp/publish_sudan_war.py` (peace_conflict template) for the canonical per-post publish flow with all 7 post-processing steps.

---

**End of handoff. Pearl_News session 2026-06-04 → 2026-06-07 closed.**
