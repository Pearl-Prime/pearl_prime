# Teacher Showcase Media Wiring Status — 2026-04-10

**PROJECT_ID:** proj_state_convergence_20260328  
**SUBSYSTEM:** brand_admin  
**Page:** `brand-wizard-app/public/teacher_showcase.html`  
**Showcase teachers (13):** ahjan, adi_da, joshin, junko, maat, master_feung, master_sha, master_wu, miki, omote, pamela_fellows, ra, sai_ma  

**Note:** `ahjan` has pipeline assets under `assets/` (panels, audiobook ch1, audiobook cover) but **no** teacher section on this page — treated as **orphaned / out of scope** for the 13× matrix below.

---

## Phase 1 — Disk inventory (summary)

| Bucket | Count / notes |
|--------|----------------|
| Legacy ebook PNGs (`covers/*.png`) | 12 files (no `ahjan` in root list) |
| KDP covers (`covers/kdp/*.png`) | 13 teachers × 4 roles = 52 files |
| Audiobook jackets (`covers/audiobook/`) | 13 files |
| Manga character + topic PNGs | See tree; **maat** has no `maat_cover_*.png` |
| Manga panels | 12 teacher dirs with 4 pages; **maat** pages were at `manga_panels/p01_01.png` … `p04_01.png` (misplaced) — **remedied in commit** by moving to `manga_panels/maat/page_001.png` … |
| Audiobook ch1 MP3s | 13 |
| Hook MP3s (`audio/showcase/`) | 13 |
| Podcast MP3s (`audio/podcast/*_3min.mp3`) | 13 |
| TikTok/Reels MP4s | 14 files (ahjan: **two** clips) |
| YouTube MP4s (`video/youtube/`) | **0** |
| Investor demo MP3s (`audio/investor_demo/`) | **0** (path absent) |

---

## Phase 2 — HTML pattern counts (after remediation)

| Pattern | Count |
|---------|------|
| KDP `*_ebook.png` | 13 |
| KDP `*_audiobook.png` | 13 |
| KDP `*_podcast.png` | 13 |
| KDP `*_social.png` | 13 |
| Legacy `covers/cover_*.png` (mostly video posters + prose) | 13 |
| `manga_panels/` | 52 gallery refs + reader paths |
| `audiobook_chapters/*.mp3` | 13 |
| `audio/showcase/*.mp3` | 13 |
| `podcast/*_3min.mp3` | 13 |
| `togglePodcast` | 1 definition, 13 bindings |
| `video/tiktok/*.mp4` | **14** (ahjan: TikTok + Instagram/Reels) |
| `video/youtube/*.mp4` | 0 |
| YouTube placeholder copy | 13 |

---

## Summary table

| Media Type | On disk (for 13) | Wired in HTML | Gap (pre-fix) |
|------------|------------------|---------------|----------------|
| KDP ebook | 13/13 | 13/13 | None |
| KDP audiobook | 13/13 | 13/13 | None |
| KDP podcast | 13/13 | 13/13 | None |
| KDP social | 13/13 | **was 0/13** | **TYPE A — fixed** |
| Manga characters (3 views) | 13/13 | 13/13 | None |
| Manga triptych | 13/13 | 13/13 | None |
| Manga topic cover (`*_cover_*`) | 12/13 (**maat** none) | Formats card uses **maat_front** | TYPE C for maat dedicated topic cover asset |
| Extra topic covers on disk | joshin ×2 extra; junko ×2 extra; master_wu ×2 extra | **was unwired** | **TYPE A — fixed** (extra row) |
| Manga chapter panels | **was 12/13 dirs** | **maat** pointed at missing dir | **TYPE B path/layout — fixed** (move PNGs) |
| Audiobook ch1 | 13/13 | 13/13 | None |
| Hooks | 13/13 | 13/13 | None |
| Podcast | 13/13 | 13/13 | None |
| TikTok/Reels | 13 TikTok + 1 extra Reels | **ahjan Reels unwired** | **TYPE A — fixed** |
| YouTube | 0 | Placeholder only | TYPE C (generation) |
| Book prose | 13 | 13 sections | None |

---

## Per-teacher matrix (Y = yes, N = no; “topic cover” = `manga_covers/{id}_cover_*.png`)

Legend: **Disk** / **HTML** / **Visible** (collapsible OK).

| Teacher | KDP e/a/p/so | Manga F/3Q/Pr | Trip P/S/Sy | Topic cover | Panels×4 | Ch1 | Hook | Pod | Tik/IG | YT placeholder | Book |
|---------|--------------|---------------|-------------|-------------|---------|-----|------|-----|--------|----------------|------|
| ahjan | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y/Y | Y | Y |
| adi_da | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |
| joshin | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y (+extras wired) | Y | Y | Y | Y | Y | Y | Y |
| junko | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y (mindfulness file); extras wired | Y | Y | Y | Y | Y | Y | Y |
| maat | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | **N** (front in formats) | **Y** (after file move) | Y | Y | Y | Y | Y | Y |
| master_feung | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |
| master_sha | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |
| master_wu | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y (+extras wired) | Y | Y | Y | Y | Y | Y | Y |
| miki | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |
| omote | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |
| pamela_fellows | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |
| ra | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |
| sai_ma | Y/Y/Y/Y | Y/Y/Y | Y/Y/Y | Y | Y | Y | Y | Y | Y | Y | Y |

---

## Gap taxonomy (session)

| Type | Item | Action |
|------|------|--------|
| A | KDP social covers on disk, not in HTML | Added fifth format card per teacher |
| A | `ahjan_self_worth_instagram_90s.mp4` on disk, not wired | Second `<video>` in Watch |
| A | Extra topic covers (joshin, junko, master_wu) | Added `manga-topic-extra` row per teacher |
| B | `junko_cover_overthinking.png` referenced but **missing** on disk | Point formats manga card at `junko_cover_mindfulness.png` |
| B | `maat_cover_boundaries.png` referenced but **missing** on disk | Use `maat_front.png` for formats manga slot |
| B | `pamela_fellows` video poster pointed at non-existent legacy burnout PNG | Poster → `kdp/pamela_fellows_audiobook.png` |
| B | `ra` video poster `cover_ra_self_worth.png` **missing** | Poster → `kdp/ra_audiobook.png` |
| B | Maat panels at wrong paths | Move into `manga_panels/maat/page_00N.png` |
| C | YouTube landscape MP4s | None on disk; placeholder copy updated to “coming soon” |
| C | Investor demo audio | No directory / files |
| — | `ahjan` assets | Orphaned relative to this HTML (no section) |

---

## Gaps fixed this session

1. Wired **KDP social** (`*_social.png`) for all 13 teachers; expanded formats grid to five columns.
2. Wired **Ahjan Instagram/Reels** clip; normalized TikTok/Reels posters to KDP audiobook for Ahjan.
3. **Relocated maat chapter panels** from `p01_01.png`–`p04_01.png` into `manga_panels/maat/page_001.png`–`page_004.png`.
4. Corrected **junko** formats manga asset to existing **`junko_cover_mindfulness.png`**.
5. Corrected **maat** formats manga asset to **`maat_front.png`** (no dedicated topic cover file).
6. Fixed **pamela_fellows** and **ra** video **poster** paths to existing KDP/legacy assets.
7. Added **extra topic-cover** thumbnails for **joshin**, **junko**, **master_wu**.
8. Replaced YouTube stub text with **“YouTube video — coming soon (5 min landscape)”** everywhere.
9. Added **`onerror="this.style.display='none'"`** to manga gallery, character views, and triptych images where missing.

---

## Remaining gaps (generation / backlog)

1. **YouTube** 5‑minute landscape MP4s for each teacher — not present under `assets/video/youtube/`.
2. **Maat** dedicated `maat_cover_*.png` topic cover — optional; formats currently use character front.
3. **ahjan** — decide whether to add a 14th section or retire loose assets.
4. **Investor demo** clips — separate surface; not part of teacher showcase.

---

## Evidence

- Branch: `agent/showcase-media-audit` from `origin/main`
- Files touched: `brand-wizard-app/public/teacher_showcase.html`, `brand-wizard-app/public/assets/manga_panels/maat/*`, this report, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
