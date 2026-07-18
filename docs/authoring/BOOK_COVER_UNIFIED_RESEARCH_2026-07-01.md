# Book Cover — Unified Research & Proposed Spec (2026-07-01)

**Author:** Pearl_Research (Tier-1 Claude, operator-reviewed)
**Status:** RESEARCH SYNTHESIS + PROPOSED SPEC — read-only on code; a follow-up build agent implements.
**Scope:** Consolidates the scattered (and partly aspirational) cover research into one authority answering
four operator questions: (a) free-template sourcing for error reduction, (b) the 4-level per-author
uniqueness model for **books**, (c) the per-platform requirements matrix + gap analysis (KDP-only →
multi-platform), (d) the teacher-vs-author byline correction.
**Grounding:** All counts/state resolved against `origin/main` (HEAD `6d1248bd43`), never the working tree.
**Deconfliction:** PR #4269 (`agent/cover-fingerprint-framing-20260701`) is the LIVE cover-render actor. This
doc does NOT edit `scripts/publish/abstract_cover_art.py`, `scripts/publish/render_kdp_cover.py`, or
`config/publishing/kdp_cover_typography.yaml`. Cite, do not fork (CANONICAL_ARTIFACTS_REGISTRY).

---

## 0. NEW-ARTIFACT JUSTIFICATION

This doc spans platform + template + uniqueness + identity — broader than any single existing doc. The
existing docs each cover one slice; none reconciles them or carries the operator's 4-level ask across the
**book** (not manga) path. This is a synthesis + proposed spec, not a re-implementation.

---

## 1. EXISTING-RESEARCH INVENTORY (cite, do not duplicate)

| Doc / config | What it covers | Landed on `origin/main`? | Stale? |
|---|---|---|---|
| `docs/authoring/AUTHOR_COVER_ART_SPEC.md` | **Audiobook** 4-slot deterministic blueprint: slots symbolic/environmental/abstract/human; `slot = SHA256(author_id + ":" + book_id) % 4`; **2400×2400 square**; WCAG-AA 4.5:1 contrast gate; pHash collision guard ≥12 same-brand / ≥8 same-author; PNG + JPEG (≤2 MB) export; slot-aware text zones. | **YES** | Current (v1.0.0). |
| `docs/authoring/AUTHOR_COVER_ART_SYSTEM.md` + `config/authoring/author_cover_art_registry.yaml` | Per-author **signature base gradient/palette** tokens (the anti-spam fingerprint); asset path `assets/authors/cover_art/{author_id}_base.png`. | **YES** | Current. |
| `specs/manga_cover_uniqueness_engine.md` (67 KB) | The existing **4-LAYER** scheme: **L1 Brand** (immutable) / **L2 Series** (immutable) / **L3 Volume** (hash-seed variation + anti-repetition guardrails) / **L4 Market** (typography swap, title reflow, rating badge, trim adjust, spine, regulatory). Deterministic seed cascade; variation bank min-sizes. | **YES** | **ASPIRATIONAL** — `docs/DOCS_INDEX.md:68` flags the manga cover specs as *design targets, not production gates*; minimal runtime wiring. Treat the **scheme** as canonical, the **wiring** as not-yet-built. |
| `artifacts/release/COVER_PACKAGING_PLATFORM_AUDIT_2026_04_10.md` | **Per-platform requirements matrix** (KDP, KDP Select, Google Play ebook + audiobook, Apple Books, Kobo, B&N/NOOK, ACX/Audible, Voices/Findaway) with official-source links + repo-compliance verdicts + the Kobo 3:4 gap + the ACX JPG-2400 gap. | **YES** | Numbers **re-validated 2026-07-01** (§4). Two minor upward drifts (Kobo min, ACX recommended); core ratios unchanged. |
| `docs/PEN_NAME_AUTHOR_SYSTEM.md` + `config/author_registry.yaml` | Pen-name (byline) SSOT: `author_id → pen_name, brand_id, persona_ids, topic_ids, positioning_profile`. Resolver looks up here for author-bound books, **distinct from teacher_id**. `config/author_registry.yaml` comment: `stillness_press (teacher: ahjan) — 12 pen-name authors`. | **YES** | Current. |
| `config/teachers/teacher_registry.yaml` | Teacher-mode SSOT (`ahjan` at L34). Teacher ≠ byline. | **YES** | Current. |
| Project memory | [Cover system + author fingerprint], [Cover text-overlay two-stage], [Cover thumbnail readability], [Waystream cover system], [Sai Maa never author]. | — | Current. |

**Net finding:** the research is **landed, not lost** — the failure is *fragmentation + non-wiring*, not absence.
Two cover systems coexist on main but are not unified:
1. **AUTHOR_COVER_ART_SPEC** — model-first, **2400×2400 square**, audiobook-oriented, multi-format export. Designed but **not wired to the live book path**.
2. **Active KDP renderer** — `abstract_cover_art.py` (`CANVAS_W, CANVAS_H = 1600, 2560`, line 33) + `render_kdp_cover.py` (`CANVAS_W=1600 / CANVAS_H=2560`, lines 85-86). This is the path that actually ships, and it is **portrait-only (5:8), KDP-only**.

---

## 2. THE 4-LEVEL UNIQUENESS MODEL FOR BOOKS

### 2.1 The reconciliation problem
Three vocabularies exist:
- **Operator's ask:** "brand / author / catalog / topic" (flat, four levels).
- **Manga engine:** L1 Brand / L2 Series / L3 Volume / L4 Market (immutable→variable, + a market layer).
- **Book 4-slot blueprint:** one author → 4 base images; per book pick `slot = SHA256(author_id+":"+book_id) % 4`.

These are not in conflict — they describe **different axes**. The operator's levels are the *identity hierarchy*;
the book blueprint is the *per-book selector*; the manga L4 is a *presentation adaptation*. The unified model
keeps all three by separating **identity levels** (what makes a cover belong to a brand/author/book) from the
**adaptation layer** (how that cover is re-presented per platform).

### 2.2 Proposed canonical model (RECOMMENDED — Q-LEVELS-01 default)

| Level | Name | Immutability | Mechanism (carries existing determinism + anti-dup) |
|---|---|---|---|
| **L1** | **Brand** | Immutable per brand | Brand signature `style_pool` / base palette; CI-enforced unique across brands (AUTHOR_COVER_ART_SPEC §11; author_cover_art_registry). pHash **≥12 within brand** is the brand-level anti-dup floor. |
| **L2** | **Author (pen-name)** | Immutable per author | Per-author signature gradient/palette + **4 unique base images** + unique `prompt_fills`. Byline resolves from `config/author_registry.yaml` (NOT teacher). pHash **≥8 within author** warns. |
| **L3** | **Series / Catalog** | Stable per series | Series-scoped composition/motif constraints (manga L2 analog). For non-series books, the catalog row is the L3 carrier. |
| **L4** | **Book (topic)** | Unique per book | `slot = SHA256(author_id + ":" + book_id) % 4` (existing). Topic-driven palette/symbol selection. Anti-repetition: if a slot collides on pHash, bump `(slot+1)%4`; if all 4 collide → "author needs new base images" (existing behavior). |
| **L5** | **Platform / Market** *(adaptation, non-destructive)* | Per-target | Mirrors manga **L4 Market**: re-render the SAME design at the target aspect/size/format. Trim/typography reflow + safe-area re-validation only; **never** changes the L1–L4 core design. This is where 1600×2560 / 1920×2560 / 2400² diverge. |

**Why a 5th layer instead of the flat 4:** the operator's "topic" and the platform export are different concerns —
one design must ship to several aspect ratios. Folding platform into "topic" would force a separate design per
platform (drift + cost). The manga engine already proved the immutable-design / adaptive-presentation split
(manga §2.4, §3.4: "the same character focal/pose/setting appears in JP and US editions… what differs is the
presentation layer"). We adopt it verbatim for books.

**Alternative (Q-LEVELS-01 alt):** the operator's literal flat **Brand / Author / Catalog / Topic** with platform
folded into Topic. Simpler vocabulary; cost = a design fork per platform and loss of the manga-proven
design/presentation separation. **Not recommended.**

### 2.3 Determinism + anti-dup carry-across (invariant across all levels)
- **Determinism:** the seed is `SHA256(author_id + ":" + book_id)` at L4; L5 is a pure function of the L4 output + target profile (no new randomness). Same `(author, book, platform)` → byte-identical cover. This matches both the book blueprint (§5) and manga's seed cascade (§3).
- **pHash anti-dup:** ≥12 Hamming within brand (FAIL), ≥8 within author (WARN) — applied at the **L4 design**, before L5 resize, so platform variants of the same book are intentionally near-identical and do not trip the guard against each other (guard scopes by `book_id`).
- **WCAG-AA 4.5:1:** contrast re-checked **per L5 target**, because text-zone luminance changes when the design is re-composited at a new aspect ratio. Two-stage doctrine holds: FLUX renders imagery only; PIL composites all text and runs the contrast check (never put title/author/subtitle in a FLUX prompt).

---

## 3. PER-PLATFORM REQUIREMENTS MATRIX + GAP LIST

Lead source: `artifacts/release/COVER_PACKAGING_PLATFORM_AUDIT_2026_04_10.md` (the internal audit). Launch-critical
numbers (Google Play, Kobo, ACX) **re-validated against official platform docs 2026-07-01** — see §4 for the two drifts.

| Platform | Surface | Aspect | Recommended px | Min px | Format | Notes |
|---|---|---|---|---|---|---|
| **Amazon KDP** | ebook storefront | **1.6:1 (5:8)** | **1600 w × 2560 h** | 625×1000 | JPEG/TIFF (upload), PNG embed | RGB 72 dpi (300 ppi rec.), <50 MB, ratio ≥1.6:1. **Current output matches.** |
| **Google Play Books** | ebook cover | portrait (front-cover in EPUB) | ≥1600 portrait | **640** (min dimension) | jpeg/png/tiff/pdf | Max 7200; file <2 GB. EPUB must contain front cover. **Satisfied by portrait master.** |
| **Google Play Books** | audiobook | **1:1** | **2400×2400** | 1024 | jpeg/png | Max 7200, 72 dpi min, no 3D mockup/letterbox. **GAP — square not generated for book path.** |
| **Apple Books** | marketing cover | portrait | ≥1600 portrait | **1400** (short side) | JPEG/PNG, RGB | Do not upscale small sources; interior image cap 5.6 M px. **Satisfied.** |
| **Kobo Writing Life** | ebook | **3:4 (0.75)** | **2500×3500** (high-DPI) | **1400×1873** (reject below) | JPG/PNG, RGB | ≤5 MB, portrait, no CMYK/TIFF. **GAP — KDP 5:8 (0.625) ≠ Kobo 3:4. Need ≥1920×2560 (or 2500×3500) export.** |
| **B&N / NOOK Press** | ebook | portrait | ≥1400×1400 | 750×750 | JPG/PNG | 5 KB–2 MB. **Satisfied by portrait master.** |
| **ACX / Audible** | audiobook | **1:1** | **3000×3000** (future-proof) | **2400×2400** | **JPG**/PNG/TIF, RGB 24-bit | True square, **no borders/letterboxing**, <5 MB. Title+author required; **no marketing copy**. **GAP — square not generated; export JPG.** |
| **Google Play / Voices by INaudio (Findaway)** | audiobook | **1:1** | **2400×2400** | 2400×2400 | JPEG pref (≤2 MB) | No borders/letterboxing; rejects "auto-generated/template-stamped" look; strip any "AUDIOBOOK" badge for distributor submission. **GAP — square + unbadged variant.** |

### 3.1 GAP LIST vs current `1600×2560`-only output
1. **Kobo 3:4 portrait** — current 5:8 is the wrong aspect. **Add a 3:4 export profile** (≥1920×2560; 2500×3500 for high-DPI). *Highest-value ebook gap.*
2. **Audiobook 1:1 square** — Google Play audiobook + ACX + Findaway all need **2400×2400** (ACX recommends 3000×3000; export **JPG** for ACX). AUTHOR_COVER_ART_SPEC already specs 2400² + PNG/JPEG — **wire it to the book path** rather than re-author.
3. **Format export** — KDP wants **JPEG/TIFF** on upload but the embed default is PNG; ACX/Findaway want **JPG ≤5/≤2 MB**. Add a per-platform format+size export step (the JPEG quality-stepping logic already exists in AUTHOR_COVER_ART_SPEC §6).
4. **Badge hygiene** — strip "AUDIOBOOK"/format callouts for Findaway/ACX strict art checks; keep badged variants for marketing only.

---

## 4. WEB RE-VALIDATION OF LAUNCH-CRITICAL NUMBERS (2026-07-01)

The audit is dated 2026-04-10. Re-checked the three launch-critical platforms against current official docs:

| Platform | Audit (2026-04-10) | Official (2026-07-01) | Verdict |
|---|---|---|---|
| **Google Play** (ebook + audiobook) | ebook min 640; audiobook 2400² rec / 1024 min, jpeg/png | **Unchanged** | ✅ No change. |
| **Kobo** | 3:4; "e.g. 1920×2560"; ≤5 MB; JPG/PNG | 3:4 **confirmed**; **min now 1400×1873 (reject below)**; **rec 2500×3500** high-DPI; RGB only (no CMYK/TIFF) | ⚠️ **Drift up:** explicit reject-below min + higher recommended master. 1920×2560 still valid 3:4 and above min; prefer 2500×3500 for Kobo-first. |
| **ACX/Audible** | 2400×2400; JPG; RGB; square | 2400×2400 **min confirmed**; **rec 3000×3000 (future-proof)**; JPG/PNG/TIF; 24-bit RGB; true square no borders; <5 MB; title+author, no marketing copy | ⚠️ **Drift up:** added 3000×3000 recommendation. 2400² floor unchanged. |

**Action:** carry **2400×2400 as the audiobook floor** and **3000×3000 as the recommended master**; **2500×3500** as the
Kobo high-DPI master. No launch-critical number *decreased*; the only changes are higher recommended sizes.

Sources: [KDP cover criteria](https://kdp.amazon.com/en_US/help/topic/G200645690),
[Google Play book file guidelines](https://support.google.com/books/partner/answer/3424254),
[Google Play cover upload](https://support.google.com/books/partner/answer/14187606),
[Kobo Cover Image Tips](https://kobowritinglife.zendesk.com/hc/en-us/articles/360059385711-Cover-Image-Tips),
[ACX cover art requirements](https://help.acx.com/s/article/cover-art-requirements),
[Apple Book Cover Art](https://help.apple.com/itc/booksassetguide/en.lproj/itc1bda991ba.html).

---

## 5. FREE-TEMPLATE SOURCING + ERROR-REDUCTION PLAYBOOK

**Principle:** the existing system is already **template-driven** (slot-aware text zones, deterministic slots,
two-stage FLUX-imagery / PIL-text). The free-template lane is about **reducing error classes**, not freehand
design. Map each vetted free source to the specific error it prevents.

### 5.1 Vetted free sources (license-clean)
| Need | Free source | License | Maps to error class |
|---|---|---|---|
| Display/body fonts | **OFL fonts already bundled** in repo (`_load_font` in render_kdp_cover.py reads bundled families) | SIL OFL — embeddable, commercial-OK | Avoids font-licensing risk; keep using bundled OFL — do not pull random web fonts. |
| Background imagery (when not FLUX-rendered) | **CC0 / public-domain**: Unsplash (CC0-like license), Pexels, Wikimedia Commons PD, Openverse (filter CC0/PD) | CC0 / PD | License-clean fallbacks; **but** two-stage doctrine prefers FLUX-rendered imagery — use CC0 only as backstop. |
| Layout/zone references | **KDP Cover Creator**, **Reedsy free templates**, **Canva free book-cover templates** | Free-to-use templates | Reference **zone geometry** (safe area, title band) to validate the repo's text-zone config — not to import bitmaps. |
| Aspect/trim references | KDP/Kobo/ACX official spec pages (§4) | — | Source of truth for the L5 platform profiles. |

### 5.2 Error-class → mitigation map (tie to the existing zone/template engine)
| Error class (system hits) | Root cause | Template-driven mitigation |
|---|---|---|
| **TitleTooLongForTemplate / zone overflow** | Long titles/subtitles overflow the fixed text zone (memory: ~528/800 subtitles too long) | Use slot text-zone bounds (AUTHOR_COVER_ART_SPEC §3) + the existing `_wrap_to_width` / font-shrink loop (render_kdp_cover.py ~L451-472, **owned by PR #4269 — do not edit**); feed a **short cover-hook** field, not the full subtitle. |
| **Bleed / safe-area mistakes** | No per-platform bleed/safe-area enforcement | Add safe-area validation **per L5 profile**; ACX/Findaway = no borders/letterboxing; KDP print needs bleed (not ebook). |
| **Platform-size mismatch** | One 1600×2560 asset shipped to a 3:4 or 1:1 surface | L5 platform profiles (§6) make the export aspect explicit; never reuse portrait for square. |
| **KDP near-duplicate rejection** | Covers too similar across a brand/author | Existing pHash guard (≥12 brand / ≥8 author) + per-author 4 unique base images + signature palette. Keep the guard at L4 design. |
| **Contrast failures (illegible thumbnail)** | Text luminance vs background fails small-size | WCAG-AA 4.5:1 check **per L5 target** (luminance shifts with aspect); thumbnail-readability cap per memory [Cover thumbnail readability]. |

---

## 6. IDENTITY-BUG FINDING + FIX RECOMMENDATION (do NOT fix here)

### 6.1 The bug
Teacher-mode identity leaks into the **author byline**. `scripts/release/build_epub.py` defines `TEACHER_BOOKS`
(lines **87–124**) with each row hardcoding the **teacher's name as `author`**:
```
{"id": "ahjan", "author": "Ahjan", "publisher": "Inner Light Press", ...}
{"id": "sai_ma", "author": "Sai Maa", "publisher": "Healing Ground Press", ...}
```
This flows: `TEACHER_BOOKS[].author` → `build_book(author=book["author"])` → `book.add_author(author)` (line **305**)
and the printed byline `By {author}` (line **344**). The `--batch` path ("all 13 teacher books") therefore bylines
every book with a **teacher**, not a pen-name author. `scripts/publish/build_epub.py:31` is only the docstring echo
of the same example (`--author "Ahjan"`) — the **real** site is the backend `scripts/release/build_epub.py`.

This is the **same class as the Sai-Maa rule** (memory [Sai Maa never author]): teachers are teacher-mode-only,
never author bylines. `ahjan` is legitimately a teacher (teacher_registry.yaml L34) **and** a Stillness-Press
character — the bug is *specifically its use as an `--author` byline*, not its existence.

### 6.2 The fix (recommended; build agent implements)
- **Byline source:** resolve from the pen-name SSOT `config/author_registry.yaml` (and `docs/PEN_NAME_AUTHOR_SYSTEM.md`).
  For a teacher-mode book, map **brand → pen-name author** (e.g. `stillness_press` → one of its **12 pen-name authors**,
  selected by the existing author resolver), and use that pen-name as `--author`.
- **Teacher credit:** carry the teacher in a **distinct field** — e.g. `teaching_by` / "teaching by <teacher>" in the
  EPUB metadata/front-matter — **never** in `--author` / `book.add_author()`.
- **Exact sites to change:**
  1. `scripts/release/build_epub.py` — `TEACHER_BOOKS` schema (lines 87–124): split `author` into `pen_name_author`
     (byline) + `teacher` (credit); `build_book(...)` signature + `add_author()` (L305) + `By {author}` (L344) read the
     pen-name; add a separate "teaching by" line.
  2. The batch byline path: `build_all_teacher_books()` (~L400-428) which passes `author=book["author"]`.
  3. `scripts/publish/build_epub.py:31` — update the docstring example to a pen-name author (cosmetic, prevents copy-paste of the wrong pattern).
- **Guardrail:** add a check that `--author` is never a value present in `config/teachers/teacher_registry.yaml`
  (extends the Sai-Maa-class rule to a CI/test assertion).

---

## 7. PRIORITIZED IMPLEMENTATION LANE (for the follow-up BUILD prompt; ≤180-file PRs)

> **Coordinate with PR #4269** — it owns the live render code. These lanes either land **after** #4269 merges or
> touch **new** profile/exporter files, not #4269's files.

| # | Lane | Scope | Touches | Depends on |
|---|---|---|---|---|
| **1** | **Platform-size profiles** | New `config/publishing/platform_cover_profiles.yaml`: per-target aspect/size/format/safe-area/bleed (KDP 1600×2560, Kobo 2500×3500 @3:4, audiobook 2400²→3000² @1:1, format+max-MB per platform). Pure config, no render edits. | 1–2 new files | none |
| **2** | **Byline-source fix (identity bug)** | Implement §6.2: pen-name byline from `author_registry.yaml`, `teaching_by` field, CI guard. | `scripts/release/build_epub.py` + 1 test + docstring | none (independent) |
| **3** | **Kobo 3:4 exporter** | L5 export profile producing 3:4 portrait (≥1920×2560 / 2500×3500) from the L4 design. Reads lane-1 profiles. | new exporter module + test | lane 1; **after #4269** |
| **4** | **Audiobook square exporter** | Wire AUTHOR_COVER_ART_SPEC's 2400² (→3000²) square + JPG export to the book path (Google Play audiobook + ACX + Findaway); unbadged variant. | new exporter + test | lane 1; **after #4269** |
| **5** | **4-level wiring** | Encode L1–L5 model (§2.2) as the canonical selector contract; pHash/WCAG carried per §2.3; reconcile with manga engine naming. | spec + selector glue + test | lanes 1,3,4 |

Each lane is independently shippable and well under the 180-file cap. Lane 2 has **no dependency** and can ship first.

---

## 8. OPEN OPERATOR QUESTIONS (recommended defaults)

| ID | Question | Recommended default | Alternative |
|---|---|---|---|
| **Q-LEVELS-01** | Canonical levels for books | **Brand → Author(pen-name) → Series/Catalog → Book(topic)**, with **Platform/Market as a non-destructive L5** (mirrors manga L4). | Operator's literal flat Brand/Author/Catalog/Topic (platform folded into Topic). Cost: a design fork per platform. |
| **Q-PLATFORM-PRIORITY-01** | First platforms beyond KDP | **Google Play ebook + Kobo** (the 3:4 gap) first, then **audiobook square (2400²/3000²)**. | All-at-once (higher blast radius). |
| **Q-TEACHERMODE-BYLINE-01** | Teacher-mode byline | **Pen-name author byline + teacher in a separate "teaching by" field**; teacher NEVER in `--author`. | (none recommended — Sai-Maa-class rule). |

---

## 9. RELATED CANONICAL ARTIFACTS (edit-in-place, do not fork)
- `docs/authoring/AUTHOR_COVER_ART_SPEC.md`, `docs/authoring/AUTHOR_COVER_ART_SYSTEM.md`
- `config/authoring/author_cover_art_registry.yaml`
- `specs/manga_cover_uniqueness_engine.md` (aspirational — design target)
- `artifacts/release/COVER_PACKAGING_PLATFORM_AUDIT_2026_04_10.md`
- `docs/PEN_NAME_AUTHOR_SYSTEM.md`, `config/author_registry.yaml`, `config/teachers/teacher_registry.yaml`
- **Render code (PR #4269 — do not edit from research):** `scripts/publish/abstract_cover_art.py`,
  `scripts/publish/render_kdp_cover.py`, `config/publishing/kdp_cover_typography.yaml`
- `scripts/release/build_epub.py` (identity-bug fix site — for the build agent, not this doc)

---

*End — Pearl_Research synthesis 2026-07-01. Read-only on code. Follow-up build agent implements §7.*
