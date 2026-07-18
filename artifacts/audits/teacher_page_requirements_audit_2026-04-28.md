# Teacher Page Requirements Audit — 2026-04-28

**Issue:** [#778 — Complete teacher page requirements beyond routing and portraits](https://github.com/Ahjan108/phoenix_omega_v4.8/issues/778)
**Auditor:** Pearl_GitHub (this session)
**Subject:** `brand-wizard-app/public/teacher_showcase.html` (924 KB, on `origin/main` HEAD `1c7cd876ad`)
**Method:** Asset-disk inventory × per-teacher HTML section read × URL liveness probe
**Verdict:** **STOP — gap plan presented, no inline fixes applied** per Step 4 of operator brief.

---

## §1 — Methodology

For each of the 13 teachers + each of the 17 issue-#778 requirements, we recorded one of:

| Mark | Meaning |
|---|---|
| ✅ present | Requirement met; asset on disk + wired in HTML |
| ❌ missing | Asset not on disk, not wired, or text content absent |
| ⚠️ broken | Wired in HTML but URL fails to resolve, dead asset path, or HTML id collision |
| N/A | Asset legitimately doesn't apply to this teacher (e.g., reel not produced) |

Asset-disk facts cross-checked via `ls -la` on:
- `teacher_pics/` (13 portraits)
- `brand-wizard-app/public/assets/covers/kdp/` (52 covers — 4 per teacher)
- `brand-wizard-app/public/assets/audio/audiobook_chapters/` (12 of 13)
- `brand-wizard-app/public/assets/audio/podcast/` (13 of 13)
- `brand-wizard-app/public/assets/audio/showcase/` (13 hook clips)
- `brand-wizard-app/public/assets/manga_covers/` (97 files, ≥6 per teacher)
- `brand-wizard-app/public/assets/manga_panels/{teacher}/` (4 panels per teacher)
- `brand-wizard-app/public/assets/video/teacher_reels/` (4 of 13)
- `brand-wizard-app/public/assets/video/tiktok/` (13 of 13)

URL liveness check: `curl -I https://podcast.phoenix-omega.com/...` returns NXDOMAIN (host does not resolve from public DNS).

---

## §2 — Per-teacher × per-requirement audit table

Columns: 1=portrait · 2=bio · 3=teaching summary · 4=book sample · 5=book cover · 6=audiobook cover · 7=audiobook sample · 8=podcast audio · 9=podcast cover · 10=manga cover · 11=manga panels · 12=video reel · 13=CTA · 14=attribution · 15=broken-links-clean · 16=no-dup-page · 17=locale-notes

| Teacher | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ahjan | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ | ⚠️ | ⚠️ | ❌ |
| adi_da | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ | ⚠️ | ⚠️ | ❌ |
| joshin | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| junko | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| maat | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| master_feung | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| master_sha | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| master_wu | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| miki | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| omote | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| pamela_fellows | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ❌ | ✅ | ✅ | ✅ | ❌ |
| ra | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| sai_ma | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |

### Path / file references per requirement

| # | Requirement | Path pattern | Notes |
|---|---|---|---|
| 1 | Portrait | `teacher_pics/{teacher}.png` | All 13 EXIST on disk; HTML still uses first-initial gradient avatar (e.g., line 319: `<div class="teacher-avatar" ...>OM</div>`) — **not wired** |
| 2 | Bio / background | inline HTML "A Note on the Teachings of {Name}" inside Read Book section | All 13 present |
| 3 | Teaching summary | inline HTML — `teacher-tradition` + `teacher-focus` divs in section header | All 13 present |
| 4 | Book chapter sample | inline HTML — Read Book collapsible (≥10k words per teacher) | All 13 present |
| 5 | Book cover | `assets/covers/kdp/{teacher}_ebook.png` | All 13 present |
| 6 | Audiobook cover | `assets/covers/kdp/{teacher}_audiobook.png` | All 13 present, distinct from book |
| 7 | Audiobook sample | `assets/audio/audiobook_chapters/{teacher}_{topic}_ch1.mp3` | 12/13 — **maat missing** |
| 8 | Podcast audio | `assets/audio/podcast/{teacher}_podcast_3min.mp3` | All 13 present |
| 9 | Podcast cover | `assets/covers/kdp/{teacher}_podcast.png` | All 13 present, distinct |
| 10 | Manga cover | `assets/manga_covers/{teacher}_*.png` (multiple) | All 13 present (6–9 each) |
| 11 | Manga panels | `assets/manga_panels/{teacher}/page_001..004.png` | All 13 present (4 each) |
| 12 | Video reel | `assets/video/teacher_reels/{teacher}_reel.mp4` | 4/13 (adi_da, ahjan, ra, sai_ma); 9/13 N/A. ahjan + adi_da ALSO have R2 URL `https://podcast.phoenix-omega.com/...` which is **NXDOMAIN broken** |
| 13 | CTA | — | **0/13** — page has no Buy / Subscribe / Get / Listen Now / Read More buttons anywhere (global `grep` count = 0) |
| 14 | Attribution | inline header — name + brand + tradition + focus | All 13 present |
| 15 | Broken links | ahjan + adi_da reference `https://podcast.phoenix-omega.com/brand-admin/teachers/{t}/example_reel_v1.mp4` — host returns NXDOMAIN | 2/13 broken; 11/13 clean |
| 16 | No duplicate sections | ahjan + adi_da have HTML `id="*_video_example"` collisions (2 sections share the same id within the section) | 2/13 with collisions |
| 17 | Locale-readiness notes | Page is en_US-only with locale flag emojis (e.g., "🇺🇸 English" in stats line). **No per-locale switching, no zh_TW/ja_JP/ko_KR/etc. variants of the page exist** | All 13 marked ❌ — no localized variants exist |

---

## §3 — Tally

### Per-requirement totals

| # | Requirement | ✅ | ❌ | ⚠️ | N/A |
|---|---|---|---|---|---|
| 1 | Portrait wired | 0 | 13 | 0 | 0 |
| 2 | Bio | 13 | 0 | 0 | 0 |
| 3 | Teaching summary | 13 | 0 | 0 | 0 |
| 4 | Book sample | 13 | 0 | 0 | 0 |
| 5 | Book cover | 13 | 0 | 0 | 0 |
| 6 | Audiobook cover | 13 | 0 | 0 | 0 |
| 7 | Audiobook sample | 12 | 1 | 0 | 0 |
| 8 | Podcast audio | 13 | 0 | 0 | 0 |
| 9 | Podcast cover | 13 | 0 | 0 | 0 |
| 10 | Manga cover | 13 | 0 | 0 | 0 |
| 11 | Manga panels | 13 | 0 | 0 | 0 |
| 12 | Video reel | 4 | 0 | 2 | 9 (legitimate — asset not produced) |
| 13 | CTA | 0 | 13 | 0 | 0 |
| 14 | Attribution | 13 | 0 | 0 | 0 |
| 15 | No broken links | 11 | 0 | 2 | 0 |
| 16 | No duplicate sections | 11 | 0 | 2 | 0 |
| 17 | Locale-readiness | 0 | 13 | 0 | 0 |

### Headline numbers

- **Asset coverage is excellent**: requirements 2–11 + 14 are 100% present (≥12/13)
- **Three structural gaps fail across all (or most) teachers**:
  - **#1 Portrait**: 0/13 wired despite all 13 portraits existing on disk (PR #773 landed the files; HTML never updated to reference them)
  - **#13 CTA**: 0/13 — no purchase / subscribe / "next step" buttons anywhere on the page
  - **#17 Locale**: 0/13 — page is en_US-only, no language switcher, no per-locale variants
- **Per-teacher bugs**:
  - **maat**: missing audiobook chapter MP3 (#7)
  - **ahjan + adi_da**: each have a duplicate HTML `id="*_video_example"` collision (#16) AND reference an NXDOMAIN R2 host for one of their video URLs (#15)

---

## §4 — Gap classification

Per the operator's Step 4 brief:
> If gaps are small → fix in same PR. If gaps are large → stop and present gap plan.

### Small gaps (could land in this PR if authorized)

| ID | Gap | Fix scope | Risk |
|---|---|---|---|
| **G-1** | Portrait wiring (req #1) | Replace 13 `<div class="teacher-avatar" ...>{INITIALS}</div>` blocks with `<img src="teacher_pics/{teacher}.png" alt="{Name}" class="teacher-avatar-photo">` + minor CSS for circular crop | Low — assets exist; HTML edit is mechanical |
| **G-2** | Duplicate `_video_example` HTML ids (req #16) | Remove the second (R2-pointed) "Video — example reel" section in ahjan + adi_da (lines ~436–447 + equivalent in adi_da); keep the local-asset section | Low — surgical delete, no asset change |
| **G-3** | Broken R2 video URL (req #15) | The R2 URLs become moot once G-2 deletes those sections (they live in the duplicate sections being removed). Net: G-2 fixes G-3. | Low — collateral fix |

Total for G-1+G-2+G-3: ~50 lines changed, 1 file (`teacher_showcase.html`).

### Large gaps (require operator decision before any inline work)

| ID | Gap | Why it's large | What's needed |
|---|---|---|---|
| **G-4** | CTA (req #13) | 0/13 teachers have any CTA. Adding CTAs is a UX/copy/business design decision (Buy / Subscribe / Pre-order / Get Free Sample / Start Trial / etc.) and should not be invented unilaterally | Operator picks: (a) CTA copy, (b) destination URLs (per-teacher? generic?), (c) whether per-teacher or universal CTA |
| **G-5** | Locale-readiness (req #17) | 0/13 teachers have locale switching. Catalog now spans 8 markets per PR #738 but the showcase page stays en_US. Building per-locale variants or a runtime language switcher is a non-trivial architectural decision | Operator picks: (a) per-locale HTML files (`teacher_showcase_zh_TW.html` etc.) vs runtime switcher; (b) which locales get authoritative translations vs MT vs hide-until-ready |
| **G-6** | maat audiobook chapter (req #7 for 1 teacher) | Generating new audio is **explicitly out of scope** per #778 ("No new generated teacher content without approval; No LLM API calls") | Operator authorizes a separate Pearl_Star CosyVoice2 generation pass for `maat_{topic}_ch1.mp3` |

---

## §5 — Recommendation

**Do NOT inline-fix in this PR.** Reasons:
1. The collective gap is **large** (G-4 alone touches 13 teachers and needs UX/business design); per Step 4 this triggers "stop and present gap plan."
2. Fixing G-1 (portrait wiring) inline without authorization risks the same drift the operator caught earlier this session (PR #772/#773 were chained but each was authorized first).
3. Issue #778 explicitly says: "If gaps are small, fix them in the same PR. If gaps are large, do not guess or generate content. Instead: open the audit PR first, include a prioritized gap plan."

**Open this PR** (audit doc only, no code) and let the operator authorize each gap:

### Proposed PR sequence (operator authorization required for each)

| PR | Scope | Depends on |
|---|---|---|
| **PR-A (this one)** | `artifacts/audits/teacher_page_requirements_audit_2026-04-28.md` only | — |
| **PR-B** | G-1 + G-2 + G-3 — portrait wiring + dup-id removal + dead R2 URL removal | Operator: "yes, do PR-B" |
| **PR-C** | G-4 — CTA design + wiring | Operator: CTA copy + destinations |
| **PR-D** | G-6 — maat audiobook chapter | Operator: authorize Pearl Star generation |
| **PR-E** | G-5 — locale-readiness architecture | Operator: per-locale strategy decision |

PR-B is the **lowest-risk + highest-visible-value** next step. PR-C–E need operator design input.

---

## §6 — Out-of-scope items per #778 brief (NOT touched)

- ❌ No Cloudflare deploy (per "No Cloudflare deploy unless explicitly authorized after merge")
- ❌ No new generated teacher content (per "No new generated teacher content without approval")
- ❌ No LLM API calls (per "No LLM API calls")
- ❌ No broad redesign (per "No broad redesign unless required to expose existing assets")
- ❌ No `--admin` merge (per "No --admin")

---

## §7 — Appendix: HTML evidence for the 3 small bugs

### G-1 portrait wiring — current pattern (line 319)
```html
<div class="teacher-avatar" style="background:linear-gradient(135deg, #F5A623, #4A2C00)">OM</div>
```
**Should be:**
```html
<img src="teacher_pics/ahjan.png" alt="Ahjan" class="teacher-avatar-photo"
     style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #F5A623">
```

### G-2 duplicate HTML id (lines 398–410 vs 436–447)
Both blocks emit `id="ahjan_video_example"` and `id="arr_ahjan_video_example"`. Same pattern in adi_da section. Per HTML spec these IDs must be unique — duplicates break `getElementById`-based JS, accessibility tooling, and anchor jumps.

### G-3 dead R2 URL (line 406)
```html
<source src="https://podcast.phoenix-omega.com/brand-admin/teachers/ahjan/example_reel_v1.mp4" type="video/mp4">
```
`host podcast.phoenix-omega.com` → `NXDOMAIN`. The local equivalent `assets/video/teacher_reels/ahjan_reel.mp4` exists and is referenced in the duplicate (G-2) section.
