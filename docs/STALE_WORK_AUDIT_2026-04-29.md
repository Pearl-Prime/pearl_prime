# Stale Work Audit — Phase 2 / B-series — 2026-04-29

**Purpose:** map what's now authoritatively on `origin/main` so any in-flight agent (worktree)
holding "Phase 2 / B1 / B2" work can decide what to discard, what to keep, and what (if anything)
deserves a separate small PR. **No commits are being made on behalf of those holdings — operator review required.**

**Scope:** this audit catalogs what landed on main between 2026-04-26 and 2026-04-29 across PRs
#771, #780, #790, #793, #795, #796, #792. Any uncommitted "Phase 2 / B1 / B2" work touching the
same files should be reviewed against this record before commit.

---

## 1. Authoritative state on main (`6375c8fcbf`, post-#792)

### 1.1 Catalogs (all 4 locales, listing-ready)

| File | Status | Authority |
|---|---|---|
| `artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv` | 1,478 rows, all listing-ready | PR #790 (B2) |
| `artifacts/catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv` | 1,478 rows, all listing-ready | PR #793 (B1) |
| `artifacts/catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv` | 2,818 rows, 2,658 listing-ready, 160 blocked_score | PR #793 (B1) |
| `artifacts/catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv` | 2,630 rows, all listing-ready | PR #793 (B1) |
| `artifacts/catalog/manga/{en_US,ja_JP,zh_TW,zh_CN}_manga_catalog.csv` | 727 ready + 153 image-QA-pending | PR #771 (catalogs) |
| `artifacts/catalog/launch_baseline/{top_50_combined,top_10_book_scripts_*,top_10_per_locale_combined}.csv` | Final launch baseline | PR #795 / #796 |

### 1.2 Generators

| File | Authoritative version | Notes |
|---|---|---|
| `scripts/catalog/generate_pearl_prime_book_script_catalog.py` | post-PR #793 — modifier model (`brand_voice_modifiers` + `persona_subtitle_modifiers` + locale-native blocks) | Do **not** reintroduce: `compute_flagship_set`, `_seeded_idx`, `title_dedup_phrases` loader, "flagship cap" logic from PR #788 |
| `scripts/catalog/generate_manga_catalog.py` | PR #771 | Pre-existing |
| `scripts/catalog/build_final_launch_report.py` | PR #795 / #796 | Top-50 + top-10 builder |
| `scripts/catalog/cluster_titles.py` | PR #792 | Acceptance gate; word-boundary keyword matching + density floor |
| `scripts/catalog/CLUSTER_TITLES_README.md` | PR #792 | Usage doc |

### 1.3 Configs

| File | Current shape | Notes |
|---|---|---|
| `config/catalog/catalog_generation_config.yaml` | Has `title_templates` (en_US, ~5/topic), `brand_voice_modifiers`, `persona_subtitle_modifiers` (en_US per #790), `title_templates_locale_native[locale]`, `brand_voice_modifiers_locale_native[locale]`, `persona_subtitle_modifiers_locale_native[locale]` (per #793 B1), `title_dedup_phrases` block at end (legacy from #788, **unused** after #790) | **Do not touch the legacy `title_dedup_phrases` block** without owner sign-off — leaving it as dormant authoring data per Option C decision (2026-04-29) |
| `config/catalog_planning/title_dedup_phrases.yaml` | Legacy file, no longer loaded by generator | Same — leave dormant |
| `config/manga/brand_genre_allocation.yaml` | PR #771 | Authoritative |
| `config/manga/canonical_genre_list.yaml` | PR #771 | Authoritative |

---

## 2. Original Phase 2 brief — what's now ✅ vs what's still ❌

The original **Phase 2 brief** (received earlier in this conversation) asserted several "✅ landed" items
that did **not** exist in the repo at the time. As of 2026-04-29, every catalog-side claim from that brief
has now been resolved by a downstream PR. Any agent acting on that brief without re-reading this audit
will reintroduce stale assumptions.

| Original Phase 2 brief claim | Then-state | Now (2026-04-29) | Resolved by |
|---|---|---|---|
| `title_templates.yaml` (en_US, 153 entries) at `config/catalog_planning/` | ❌ did not exist | ✅ inline in `catalog_generation_config.yaml::title_templates` (~5/topic) | PR #790 |
| `title_templates.{ja_JP,zh_TW,zh_CN}.yaml` (153 entries each) | ❌ did not exist | ✅ inline in `catalog_generation_config.yaml::title_templates_locale_native[locale]` | PR #793 |
| `description_templates.{locale}.yaml` × 3 | ❌ did not exist | Not added — current generator does not need locale-native description templates | n/a |
| `engine_title_angles.{locale}.yaml`, `series_templates.{locale}.yaml` | ❌ did not exist | Not added — out of scope for catalog launch | n/a |
| Generator `load_title_templates(locale)`, `load_engine_title_angles(locale)`, etc. | ❌ did not exist | Replaced by simpler modifier model in `pick_title_subtitle()` | PR #790 + #793 |
| `config/source_of_truth/manga_profiles/brands/stillness_press.yaml` (brand_portfolio_allocation profile) | ❌ did not exist | Not added — manga catalog uses `config/manga/brand_genre_allocation.yaml` matrix-row model from PR #771 | n/a |
| 21 new stillness_press genre series (`stillness_jp_20-29` + 11 `stillness_press_*_us`) | ❌ did not exist | Not added — out of scope; current catalog operates on the 12-brand × matrix-cell model | n/a |
| Pearl Prime catalog "stale; needs rebuild" | true at the time | ✅ rebuilt 3× (PR #780, #790, #793) | — |
| zh_TW + zh_CN manga catalogs | ❌ did not exist | ✅ in PR #771 | PR #771 |
| Brand × genre matrix migration for 11 remaining global-west brands | ❌ did not exist | Not done — out of scope per Option A scoping decisions; current matrix is in `config/manga/brand_genre_allocation.yaml` | n/a |

**Net:** every catalog/title item from the Phase 2 brief is either (a) shipped via downstream PRs
in a different shape, or (b) deliberately deferred / out of scope. **Do not commit code that
implements the original brief verbatim** — it would conflict with #790 / #793 architecture.

---

## 3. Specific patterns to AVOID reintroducing

If an in-flight agent is about to commit any of the following, treat as stale:

1. **`compute_flagship_set` helper** in `generate_pearl_prime_book_script_catalog.py` — PR #788 added it, PR #790 removed it. Reintroducing would conflict with the modifier model.
2. **`title_dedup_phrases.yaml` as a generator dependency** — PR #790 stopped loading the file. The file lives on disk but is dormant. Authoring more entries to it has no effect.
3. **`_seeded_idx` helper** — PR #788 / #791 era. Same removal status.
4. **`title_templates_by_brand` block in `catalog_generation_config.yaml`** — was the alternative B2 approach in closed PR #789. Not on main. Do not re-author it.
5. **`stillness_press.yaml` brand_portfolio_allocation profile** under `config/source_of_truth/manga_profiles/brands/` — was assumed by the Phase 2 brief but never built. Manga uses the matrix-row model in `config/manga/brand_genre_allocation.yaml`.
6. **`stillness_jp_20-29` series YAMLs** under `config/source_of_truth/manga_profiles/series/` — assumed by Phase 2 brief, not built.
7. **`load_title_templates(locale)` / `load_engine_title_angles(locale)` / `load_series_templates(locale)` loaders** — assumed by Phase 2 brief, not built. The generator uses `catalog_config.get("title_templates_locale_native", {}).get(locale, {})` directly.

---

## 4. What the audit CANNOT see

This audit cannot inspect uncommitted changes in other agent worktrees. The repo has 25+ active
worktrees (per `git worktree list`), each potentially holding in-flight work. If a specific worktree
is referenced by the operator as "the agent holding 35 files," the agent in that worktree should
run this checklist against their staged + unstaged diff before any commit:

```bash
# In the holding worktree, run from repo root:
git diff --name-only HEAD            # files changed in working tree
git diff --cached --name-only        # files staged for commit

# For each file in the output, cross-reference against §1 (authoritative) and §3 (avoid).
# If the change re-implements an item in §3 → DISCARD.
# If the change is in §1 (authoritative file) and matches main's shape → REDUNDANT (main already has it).
# If the change is genuinely new and not in §3 → propose as a small standalone PR with this audit linked.
```

---

## 5. Recommended next moves

**Operator action required for any in-flight Phase 2 worktree:**

1. Identify the holding worktree (path).
2. In that worktree, run the diff commands in §4 and produce a per-file disposition list:
   - `superseded_by_main` — the main copy already does this; discard the local copy
   - `still_useful` — net-additive content; propose as a small follow-up PR
   - `stale_assumption` — implements an item in §3; discard
3. Bring the disposition list back here (or to the agent in that worktree); do not auto-commit anything.

**Operator action for the Pearl Prime / B-series workstream itself:** the catalog system is sealed.
The next moves are launch QA — see [`docs/OPERATOR_QA_PACKET_2026-04-29.md`](OPERATOR_QA_PACKET_2026-04-29.md).

---

## 6. Recent merged PRs (audit trail)

| # | Title | SHA | Date |
|---|---|---|---|
| 771 | catalog(pearl-prime): book script catalogs (4 locales) + manga plan + genre reconciliation | 1c7cd876ad | 2026-04-28 |
| 780 | catalog(scoring): B3+B4 score backfill | 7ac4c9fbab | 2026-04-28 |
| 779 | audit(teachers): #778 — teacher page requirements audit | 7d243b8a34 | 2026-04-28 |
| 781 | fix(teacher-showcase): #778 PR-B — wire portraits + remove dup-id + dead R2 URL | 8526108ffb | 2026-04-28 |
| 784 | fix(teacher-showcase): #778 PR-D — generate maat boundaries ch1 audiobook | 516bcf4cde | 2026-04-29 |
| 785 | fix(teacher-showcase): #778 PR-C — per-teacher CTA blocks (placeholder anchors) | db8504affc | 2026-04-29 |
| 788 | catalog(b2): title dedup — flagship cap + brand+persona variant titles | 4e0c1d7ab8 | 2026-04-29 |
| 790 | feat(catalog): #786 B2 — title cannibalization fix (PASS all 4 gates) | 5ef8ceb4c3 | 2026-04-29 |
| 793 | catalog(b1): locale-native titles for ja_JP / zh_TW / zh_CN — layered on #790 | 296e0384d0 | 2026-04-29 |
| 795 | docs(catalog): final launch readiness report | 8b2fe200b9 | 2026-04-29 |
| 796 | docs(launch): final launch report — Issue #786 closeout | 632509bd5c | 2026-04-29 |
| 792 | catalog(b2): cluster_titles.py — B2 acceptance gate | 6375c8fcbf | 2026-04-29 |

Closed without merge (superseded):

| # | Title | Outcome | Reason |
|---|---|---|---|
| 789 | catalog(b2): brand-conditioned title templates | CLOSED | Superseded by #788 / #790 |
| 791 | catalog(b1): locale-native titles via title_dedup_phrases | CLOSED | Built on PR #788 stale state; superseded by #793 |
| 794 | catalog(b1): locale-native titles — Option C rebuild | CLOSED | Functionally identical to #793 which merged first |

---

## 7. Stop / hand back

This audit does not modify any worktree. It is read-only documentation.

Operator next step: confirm whether to take action on a specific holding worktree, or treat this
audit as the final word and let the holding worktree be discarded by its owner agent.
