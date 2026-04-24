# AI Policy Blocker Audit — Manga Distribution

**Date:** 2026-04-25
**Branch:** `agent/ai-policy-blocker-audit-20260425`
**Driver:** PR #626 manga research §AI-policy blockers
**Scope:** Audit all code/config for upload paths targeting AI-banned manga platforms
**Outcome:** Clean — no live upload code targets blocked platforms. Forward guard installed.

---

## Audit findings

### What was searched
- `scripts/` — all Python files
- `phoenix_v4/` — all modules
- `config/` — all yaml/json configs
- `.github/workflows/` — CI definitions

### What was found

#### 1. Tapas references (1 file)
- `config/manga/manga_brand_series_plan.yaml` — comment in `platform_cadence` block:
  > `english_global: weekly    # Webtoon/Tapas US — weekly expected`

  **Action:** Comment only. No upload path. Left as-is — context for future planners.

#### 2. Shueisha / MangaPlus / JUMP TOON references (2 files)
- `config/source_of_truth/manga_profiles/series/cogclar_jp_04.yaml` — metadata field:
  > `platform_primary: "Jump SQ (Shueisha)"`

  **Action:** Series profile metadata. Aspirational platform target, no upload code. Left as-is — would need explicit reconciliation in a future series-plan rebuild PR.

- `config/comfyui_workflows/manga_covers/shonen_cover.json` — FLUX prompt text:
  > `"Shueisha Weekly Shonen Jump aesthetic"`

  **Action:** Style prompt only — references *aesthetic*, not submission target. Safe.

#### 3. Viz / Yen Press / Shogakukan references
- **None found.** No code, no config.

#### 4. Piccoma direct self-pub references
- **None found.** No code, no config attempting direct self-pub submission.

### Active uploaders / submitters in the repo
**Scanned for any `*upload*.py` / `*submit*.py` / `*publish*.py` script that targets a manga platform:**

- `scripts/music/upload_music_bank_r2.py` — Cloudflare R2, music. Out of scope.
- `scripts/video/run_upload.py` — video distribution. Not manga.
- `scripts/brand_admin/upload_teacher_example_reel_r2.py` — R2, teacher reels. Out of scope.
- `scripts/podcast/upload_podcast_to_r2.py` — R2, podcasts. Out of scope.
- `scripts/release/build_manga_webtoon.py` — **local file format builder only**, NOT an uploader. Builds vertical-scroll PNG + PDF on disk.

**No active manga uploader/submitter targets a blocked platform.**

---

## Risk profile

**Current state:** ZERO active risk. No code path automatically pushes AI-generated manga to Tapas, Shueisha, JUMP TOON, Viz, Yen Press, Shogakukan, Piccoma direct, or Kakao Page.

**Future state:** When manga upload connectors get built (per PR #626 immediate action #2 — KDP Comics + WEBTOON Canvas), there's a real risk an agent or human builds toward a blocked platform without checking the AI policy.

---

## Guardrails installed

### 1. Single source of truth for AI policy
**File:** `config/publishing/ai_policy_blockers.yaml`

Lists every manga platform with explicit status:
- `ALLOWED` — AI permitted (KDP, Comic C'moA, GlobalComix)
- `ALLOWED_GREY` — AI ambiguous; ship with disclosure (WEBTOON Canvas, Bookwalker, Pixiv Comic)
- `BLOCKED` — AI banned/disqualified; do not target (Tapas, Shueisha/MangaPlus/JUMP TOON, Jump Rookie, Viz, Yen Press, Shogakukan)
- `PARTNER_ONLY` — Self-pub closed; license/partnership only (Piccoma SMARTOON, LINE Manga Originals, Kakao Page, Bilibili Comics, Kuaikan Manhua)

Each platform entry includes: status, region, blocked_since, rationale, source citation, recommended fallback ("if_targeted" hint).

### 2. CI check script
**File:** `scripts/ci/check_blocked_platforms.py`

Scans uploader-pattern files (`scripts/publish/*_upload.py`, `scripts/manga/*_upload*.py`, etc.) for keyword references to BLOCKED / PARTNER_ONLY platforms. Fails CI when a new uploader targets a blocked platform without an explicit `# AI_POLICY_BLOCKER_OK: <platform>` waiver comment.

Validates clean against current repo (0 violations, 1 uploader-pattern file scanned — `build_manga_webtoon.py` which is a local builder, not a network uploader).

### 3. Waiver mechanism
For rare cases where a script *legitimately* references a blocked platform (e.g., a read-only catalog query, not an upload), authors add an inline comment:
```
# AI_POLICY_BLOCKER_OK: tapas (read-only metadata fetch, no submission)
```

CI parses these markers and exempts the file from the check for the named platform.

---

## What's NOT changed (deliberately)

- `manga_brand_series_plan.yaml` Tapas mention — remains as cadence-context comment
- `cogclar_jp_04.yaml` Jump SQ field — series profile aspiration, will reconcile during catalog rebuild
- `shonen_cover.json` Shueisha aesthetic prompt — referencing visual style, not submission target

These are platform-name *mentions* in configs, not upload paths. Removing them would lose useful planning context. The CI guard catches the actual risk: future code that *targets* these platforms.

---

## Files added by this PR

| File | Purpose |
|------|---------|
| `config/publishing/ai_policy_blockers.yaml` | Single source of truth, 16 platforms classified |
| `scripts/ci/check_blocked_platforms.py` | CI guard, exits 1 on violation |
| `artifacts/research/ai_policy_blocker_audit_2026-04-25.md` | This audit report |

---

## Next-step hooks

When PR #626 immediate action #2 (KDP Comics + WEBTOON Canvas connectors) ships:
- Both connectors will reference `config/publishing/ai_policy_blockers.yaml` to determine target platform AI policy
- CI check ensures no future uploader targets a BLOCKED platform without explicit waiver
- The connectors should match `platforms.amazon_kdp_comics` and `platforms.webtoon_canvas` entries

When a future PR adds a *new* connector (Comic C'moA, GlobalComix, LINE Manga Indies):
- Author adds platform entry to `ai_policy_blockers.yaml`
- CI check confirms no BLOCKED keyword references in the connector
- Disclosure logic reads `disclosure_required` field from the policy entry

---

## Status: GUARDRAIL INSTALLED. NO CODE REMOVED. ZERO RISK BEFORE — STILL ZERO RISK AFTER, NOW WITH ACTIVE PROTECTION.
