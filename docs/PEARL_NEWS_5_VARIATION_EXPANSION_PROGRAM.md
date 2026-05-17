# Pearl News — 5-Variation Atom Expansion Program

**Authority:** Operator directive 2026-05-17
**Reference cell (template):** `pearl_news/teacher_topic_packs/teachers/junko/mental_health.yaml` (merged in PR #1158)
**Helpers (already shipped):** `teacher_authority.py` + `atom_usage_tracker.py` (PR #1154)
**Status:** Multi-session program; 1 of 45 cells complete

## 1. Why this exists

Operator directive 2026-05-17:

> "There should not be separate authors for Pearl News. The authors should come from Pearl Prime."

> "Deterministic atoms for each teacher has five variations… vary the use of the five atoms… Keep track. Use them so that we have the fewest repeats."

Two governance changes are now live on `main`:

1. **`teacher_authority.py`** — silently overlays each pack's `identity:` block with the canonical values from `SOURCE_OF_TRUTH/teacher_banks/<id>/doctrine/doctrine.yaml`. No pack rewrites needed; 59 packs canonicalize at runtime.
2. **`atom_usage_tracker.py`** — LRU selector replacing `_stable_index`. With 5 atoms per slot, guarantees no repeat within a 4-pick window per `(teacher, topic, slot)` cell.

The LRU mechanism only delivers variety **if the packs actually have 5 options per slot**. Today most packs have 1-2. This program expands all roster cells to 5 options per slot.

## 2. Scope — exact cell inventory

Per `pearl_news/config/teacher_news_roster.yaml` (post-#1132 pamela_fellows + ra removal):

| Teacher | Canonical lang | Topics | Cells |
|---|---|---|---|
| ahjan | en | climate, mental_health, education, peace_conflict, partnerships, inequality | 6 |
| master_feung | zh-cn | climate, economy_work, partnerships, education, inequality | 5 |
| sai_ma | en | mental_health, climate, education, peace_conflict, partnerships | 5 |
| junko | ja | mental_health ✅, education, economy_work, climate | 3 remaining |
| miki | ja | climate, mental_health, education, partnerships | 4 |
| master_wu | zh-cn | mental_health, peace_conflict, education, economy_work, climate | 5 |
| joshin | ja | mental_health, education, climate, economy_work | 4 |
| maat | en | inequality, peace_conflict, climate, partnerships, economy_work | 5 |
| omote | ja | peace_conflict, mental_health, education | 3 |
| master_sha | en | climate, education, mental_health, peace_conflict | 4 |
| **Total** | | | **45 cells** |

- ✅ Complete: 1 (junko × mental_health)
- 🔲 Remaining: **44 cells**

## 3. Per-cell authoring contract

Each cell delivers:

### 3.1 EN base pack (`pearl_news/teacher_topic_packs/teachers/<id>/<topic>.yaml`)

11 slots, each with **exactly 5 options** carrying **5 distinct `semantic_family` values**:

| Slot | Min content | Notes |
|---|---|---|
| `hook_personal` | 5 × `line` | personal entry point |
| `hook_big_picture` | 5 × `line` | system frame |
| `teacher_intro` | 5 × `line` | how the teacher enters |
| `youth_somatic` | 5 × `line` | body-loop description |
| `teacher_witness` | 5 × `line` | "teacher has seen this" |
| `turnaround` | 5 × `stat_line_1` + `stat_line_2` | real-world action; **stats must be real and defensible** |
| `bridge` | 5 × `line` + `hidden_capacity` | data-to-teacher connector |
| `teacher_perspective` | 5 × `paragraphs` (3 each) | the teacher's teaching |
| `practice` | 5 × `display_name` + `announcement_line` + `relief_lines` | 5 NAMED practices in teacher's doctrine |
| `cta` | 5 × `org` + `line` | 5 DIFFERENT real resource organizations relevant to the topic |
| `title_system.headline_layer_2` | 5 × `line` | 5 distinct subhead framings |

**Semantic-family rule:** Each of the 5 options per slot MUST have a unique `metadata.semantic_family` value. The pack-level `variation_policy.avoid_same_semantic_family_within_article: true` will otherwise collapse the candidate pool.

### 3.2 Locale overlays

For every cell, the `ja` and `zh-cn` overlays mirror the 5 EN options by `id` (`pearl_news/teacher_topic_packs/locales/<lang>/teachers/<id>/<topic>.yaml`).

Overlays carry **only** the locale-specific text fields:
- `line`, `paragraphs`, `stat_line_1`, `stat_line_2`, `announcement_line`, `relief_lines`, `display_name`, `hidden_capacity`

Metadata (semantic_family, article_types, intensity, etc.) lives **only** in the EN base.

### 3.3 Doctrine compliance

Before authoring, read `SOURCE_OF_TRUTH/teacher_banks/<id>/doctrine/doctrine.yaml`. Honor:

- `tradition` — never write outside the teacher's own tradition
- `tone_profile` — speaker register
- `forbidden_claims` — explicit no-fly zones
- `tone_boundaries` — what the voice does and does not do
- `prohibited_outcomes` — entire angles that fail doctrine

**Sentence-level smell tests:**
- Junko = receiver, not creator. NOT a "teacher" in the conventional sense.
- Joshin = Shingon (Mikkyo). NOT generic Zen.
- Master Feung = Grand Painting / Chinese wisdom. NOT generic Asian wisdom.
- Maat = Naqshbandi Sufi. NOT generic mystical.
- Ahjan = Tantric Buddhist (Pali "Ajahn" honorific is OK). NOT Zen / NOT generic Buddhist.

## 4. Per-cell QA gate

Reuse the smoke tests from junko pilot (PR #1158). For each new cell:

```bash
# 1. YAML parse + 5-unique-family per slot + LRU rotation
PYTHONPATH=. python3 artifacts/pearl_news/_smoke_junko_lru_20260517.py
# (Adapt: change PACK_PATH to the new cell, change teacher_id/topic.)

# 2. Locale overlays land in target script for all 3 locales
PYTHONPATH=. python3 artifacts/pearl_news/_smoke_junko_locales_20260517.py
# (Same adaptation.)

# 3. Mandatory preflight
PYTHONPATH=. python3 scripts/git/push_guard.py
bash scripts/ci/preflight_push.sh
python3 scripts/ci/audit_llm_callers.py
```

All four must pass before opening the PR.

## 5. Session sizing + priority

### 5.1 Per-session yield

A single operator-present Claude Code session at the junko-pilot pace yields **1-2 cells** with full doctrine compliance + 3-locale coverage + smoke-test verification + PR shipped.

### 5.2 Priority order (recommended)

**Wave 1 — finish the active CJK teachers** (highest visible drift potential):

| # | Cell | Lang | Rationale |
|---|---|---|---|
| 1 | junko × education | ja | Adjacent to mental_health; same persona arc |
| 2 | junko × economy_work | ja | |
| 3 | junko × climate | ja | |
| 4 | master_feung × climate | zh-cn | Chinese teacher representation in pilot |
| 5 | master_feung × economy_work | zh-cn | |
| 6 | master_feung × education | zh-cn | |
| 7 | master_feung × inequality | zh-cn | |
| 8 | master_feung × partnerships | zh-cn | |
| 9 | master_wu × mental_health | zh-cn | |
| 10 | master_wu × peace_conflict | zh-cn | |
| 11 | master_wu × education | zh-cn | |
| 12 | master_wu × economy_work | zh-cn | |
| 13 | master_wu × climate | zh-cn | |

**Wave 2 — Japanese teachers complete** (8 cells: miki × 4, joshin × 4, omote × 3 = 11)

**Wave 3 — English teachers** (ahjan × 6, sai_ma × 5, maat × 5, master_sha × 4 = 20)

### 5.3 Estimated calendar

At 1 session/day × 1-2 cells/session: **~22-44 sessions** = 4-9 weeks of operator-attended authoring.

At 2 sessions/day on heavy days: **~11-22 sessions** = 2-4 weeks.

## 6. Per-session checklist

```
[ ] Pick cell from priority queue (Section 5.2)
[ ] git checkout -b agent/<teacher>-<topic>-5-variations-YYYYMMDD origin/main
[ ] Read SOURCE_OF_TRUTH/teacher_banks/<id>/doctrine/doctrine.yaml
[ ] Read SOURCE_OF_TRUTH/teacher_banks/<id>/signature_vibe/signature_vibe.yaml (if exists)
[ ] Read current pack (1-2 existing options as voice anchor)
[ ] Author EN base — 5 options × 11 slots, 5 unique semantic_families per slot
[ ] Author ja overlay (mirror EN by id)
[ ] Author zh-cn overlay (mirror EN by id)
[ ] Run adapted LRU smoke test → pass
[ ] Run adapted locale smoke test → pass
[ ] Preflight: push_guard, preflight_push, audit_llm_callers → all pass
[ ] git commit (use junko PR #1158 commit message as template)
[ ] git push -u origin <branch>
[ ] gh pr create (use junko PR #1158 body as template)
[ ] bash scripts/git/pre_merge_check.sh <PR_NUMBER> → pass
[ ] gh pr merge <PR_NUMBER> --admin --squash --delete-branch
[ ] git fetch origin && git checkout main && git pull
```

## 7. Risk register

| Risk | Mitigation |
|---|---|
| Doctrine drift in atoms | Per-cell smoke test + operator review at PR time |
| Stat fabrication in turnaround | Use only real, verifiable orgs/programs (see junko pack for 5 examples) |
| Locale text mismatch (English bleeding into ja/zh-cn) | Locale smoke test catches this — runs the Unicode script predicate |
| `semantic_family` collisions | LRU smoke test fails if `len(set(families)) != 5` |
| Pack-loader regression | `apply_authority_to_pack` overlay test (phase 4 of LRU smoke test) |

## 8. Out of scope

- New article templates (only `hard_news_spiritual_response` for now)
- New roster entries (use existing 10 teachers only)
- Pearl_Prime book chapter expansion (different system — `docs/PEARL_WRITER_EXPANSION_SPEC.md`)

## 9. Known-good anchor

The first proven cell is on `main` at SHA `833b8d89c` (PR #1158). Use this as the structural reference for every subsequent cell. If a future cell diverges from this structure, restore via:

```bash
git show 833b8d89c:pearl_news/teacher_topic_packs/teachers/junko/mental_health.yaml > /tmp/junko_reference.yaml
```
