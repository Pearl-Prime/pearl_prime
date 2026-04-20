# Teacher showcase — handoff

Single reference for **`brand-wizard-app/public/teacher_showcase.html`**, related public assets, automation touched in this workstream, and follow-ups.

---

## Primary artifact

| Item | Path |
|------|------|
| Showcase page (Cloudflare Pages / static) | `brand-wizard-app/public/teacher_showcase.html` |
| Public assets root | `brand-wizard-app/public/` |

Teachers are **13** sections (`<section id="…" class="teacher-section">`):  
`ahjan`, `adi_da`, `master_feung`, `sai_ma`, `ra`, `junko`, `miki`, `master_wu`, `pamela_fellows`, `joshin`, `maat`, `omote`, `master_sha`.

---

## Formats row (current behavior)

Each teacher has a **Formats** collapsible with a **4-column** grid:

1. **Ebook** — cover + label + imprint (`format-brand`) where present  
2. **Audiobook** — audiobook cover, **Audiobook** label, **Chapter 1 — {topic}** line, **custom play/pause** (no CosyVoice / LUFS meta under the card)  
3. **Manga** — cover + `format-meta` (e.g. genre)  
4. **Podcast** — square podcast cover, **Podcast** label, **custom play/pause** (no “3 min · click to play”)

**Removed from Formats**

- **Social** card (“Shorts / feeds”) — entire card removed for all teachers.  
- **Listen — Chapter 1** section — entire toggle + block removed globally (including **30s Hook Preview** that lived under Listen).

**CSS** (in-page `<style>`)

- `.formats-grid` uses `repeat(4, 1fr)` (was 5 when Social existed).  
- `.format-audio-wrap`, `.format-audio-btn`, `.format-audio-icon` — circular control, hidden `<audio>`.

**JS** (before `</body>`)

- `toggleFormatAudio(btn)` — toggles play/pause for the `<audio>` inside `.format-audio-wrap`; **pauses and resets** any other format-row audio so only one sample plays at a time.  
- `filterFormat(format)` — the filter bar’s **Audio** button still calls `filterFormat('listen')`. There is no `_listen` UI anymore, so **`listen` is mapped to the same suffix as `formats`** (`matchSuffix = format === 'listen' ? 'formats' : format`) so “Audio” and “Covers” both surface the Formats row and the page does not go empty.

---

## Video — example reel

- Sections like **Video — example reel** point at:  
  `assets/video/teacher_reels/{logical}_reel.mp4`  
  (e.g. `ahjan_reel.mp4`, `ra_reel.mp4`, `sai_ma_reel.mp4`).  
- Public directory: **`brand-wizard-app/public/assets/video/teacher_reels/`**  
- **Watch** rows may still reference TikTok paths under `assets/video/tiktok/` where applicable.

### Package → public reel filenames

Source-of-truth for naming is whatever the HTML expects (`*_reel.mp4`). A helper script (when present in repo) may map package drops to those names, for example:

- `ra.mp4` → `ra_reel.mp4`  
- `sai_maa_vid.mp4` / `sai_ma_vid.mp4` / `sai_maa.mp4` / `sai_ma.mp4` → `sai_ma_reel.mp4`  
- Other `*.mp4` → `{stem}_reel.mp4`  
- `ahjan.mp4` may be skipped if `ahjan_reel.mp4` already exists (avoid clobber)

Search the repo for **`sync_teacher_package_reels`** or **`teacher_vid_package`** if paths moved.

**Staging folder (convention):** `teacher_vid_package/` at repo root — drop `*.mp4` here, then run the sync script from repo root if your tree includes it.

---

## Chapter 1 audiobook MP3s

Served from:

`brand-wizard-app/public/assets/audio/audiobook_chapters/*_ch1.mp3`

These are the URLs wired into the **Audiobook** format card’s hidden `<audio>` (one file per teacher; stem varies by teacher).

---

## Podcast MP3s

Served from:

`brand-wizard-app/public/assets/audio/podcast/*_podcast_3min.mp3`

Wired into the **Podcast** format card’s hidden `<audio>`.

---

## Repo inventory (media / HTML)

Generated lists (paths may be refreshed by re-running a workspace walk):

| File | Purpose |
|------|---------|
| `artifacts/media_html_paths_inventory.txt` | One path per line: `.html`, common image/video extensions |
| `artifacts/media_html_paths_inventory_SUMMARY.txt` | Counts by extension and top-level prefix |

The generator skipped `.git/`, `node_modules/`, `.cursor/`, `.claude/worktrees/`, and common junk dirs. **Large duplicate trees** such as `_wt_beatmap/` and `_wt_inj/` dominated counts when last run — good candidates for archival or deletion if not needed.

---

## Operational checklist for deploy

1. **Commit** `teacher_showcase.html` and any new binaries under `public/`.  
2. **Large MP4/MP3:** prefer **Git LFS** (or your org’s asset pipeline) so Pages/deploy does not miss blobs.  
3. After adding reels: confirm URLs in browser Network tab (no 404 on `teacher_reels/*.mp4`).  
4. Smoke-test **Formats** → audiobook + podcast buttons on mobile (touch targets are 48px).

---

## Quick grep / slice commands

```bash
# All teacher reel references in the showcase
grep -n 'teacher_reels/' brand-wizard-app/public/teacher_showcase.html

# Inventory slice: only public app
grep '^brand-wizard-app/public/' artifacts/media_html_paths_inventory.txt
```

---

## Follow-ups (optional)

- **Filter UX:** “Audio” and “Covers” both show Formats — consider renaming buttons or merging.  
- **Podcast vs audiobook cover:** if covers are too similar, consider swapping podcast tile image (noted in product discussion).  
- **Regenerate** `public/data/teacher_videos_inventory.json` (or equivalent) if your pipeline still emits it — search repo for `teacher_videos_inventory` / `build_teacher`.

---

## File touched in this handoff doc’s scope

- `brand-wizard-app/public/teacher_showcase.html` — formats UI, listen removal, custom audio controls, filter mapping, reel sections.  
- `brand-wizard-app/public/assets/video/teacher_reels/` — reel MP4s (ensure tracked in git as needed).  
- `artifacts/media_html_paths_inventory*.txt` — path inventories (regenerable).  
- `docs/TEACHER_SHOWCASE_HANDOFF.md` — this document.

---

*Last updated for handoff: 2026-04-18.*
