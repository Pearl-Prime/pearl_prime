# Repo Size Audit — phoenix_omega_v4.8

**Date:** 2026-04-10
**Author:** Pearl_Dev + Pearl_GitHub
**PROJECT_ID:** proj_state_convergence_20260328

---

## Summary

| Metric | Size |
|--------|------|
| Total repo on disk | 93 GB |
| `.git/` (history + objects) | 59 GB |
| `.git/objects/pack/` (packed) | 56 GB |
| `.git/` loose objects | 2.99 GiB |
| `.claude/worktrees/` | 33 GB |
| Working tree (excl .git, .claude) | **1.4 GB** |
| Total files in working tree (excl node_modules) | 18,117 |
| Total files in working tree (incl node_modules) | 25,140 |

**Verdict:** Working tree is already under 5 GB (1.4 GB). The 93 GB total is driven by git history (59 GB) and Claude worktrees (33 GB). New clones download ~56 GB of pack data — far over the 2 GB target.

---

## Git Object Store Detail

```
count: 36,072 loose objects
size: 2.99 GiB loose
in-pack: 276,054 objects
packs: 9
size-pack: 55.58 GiB
prune-packable: 2,810
```

### Pack File Breakdown

| Pack File | Size | Likely Content |
|-----------|------|----------------|
| pack-d6be4ad3… | **47 GB** | Accumulated history (all branches/merges) |
| pack-8f659a77… | **6.1 GB** | pearl_star/ ISO + Linux packages |
| pack-596b9f00… | **1.6 GB** | Video renders, cover art across revisions |
| pack-0d03936d… | 530 MB | Mixed binary history |
| pack-952e0b0c… | 95 MB | Recent objects |
| pack-86a12897… | 93 MB | Recent objects |
| pack-6224658f… | 2.5 MB | Small pack |
| pack-c32373a3… | 2.0 MB | Small pack |
| pack-c7695ee7… | 76 KB | Tiny pack |

---

## Working Tree Breakdown

| Directory | Size | File Count | Dominant Type |
|-----------|------|------------|---------------|
| archive/ | 358 MB | 105 | .html (25) |
| brand-wizard-app/ | 337 MB | 7,825 | .js (3,908) — mostly node_modules |
| artifacts/ | 281 MB | 3,428 | .json (2,480) |
| assets/ | 180 MB | 125 | .wav (48) |
| atoms/ | 61 MB | 6,532 | .txt (6,524) |
| old_chat_specs/ | 31 MB | 86 | .rtf (36) |
| teachers/ | 30 MB | 592 | .txt (547) |
| pearl_news/ | 28 MB | 170 | .yaml (110) |
| old_chats/ | 24 MB | 12 | .html (11) |
| SOURCE_OF_TRUTH/ | 15 MB | 3,172 | .yaml (3,086) |
| config/ | 11 MB | 1,058 | .yaml (1,038) |
| anxiety_hack/ | 5.5 MB | 3 | .json (2) |
| docs/ | 3.7 MB | 235 | .md (216) |
| scripts/ | 3.6 MB | 370 | .py (311) |

---

## Top 50 Largest Files (Current Working Tree)

| Size | Path | Type | LFS Candidate? |
|------|------|------|---------------|
| 290 MB | archive/root_cleanup_2026_04_10/anxiety_hack.lpf | .lpf | YES — Logic Pro |
| 18 MB | artifacts/podcast_pilot/podcast/…_podcast_episode.mp3 | .mp3 | YES |
| 9.5 MB | brand-wizard-app/node_modules/esbuild/bin/esbuild | binary | NO — gitignored |
| 9.5 MB | brand-wizard-app/node_modules/@esbuild/darwin-arm64/bin/esbuild | binary | NO — gitignored |
| 7.5 MB | artifacts/catalog/full_catalog.csv | .csv | NO — text |
| 7.1 MB | teachers/ahjan/intake/EWorkbook_121408.pdf | .pdf | YES |
| 6.9 MB | artifacts/manga_book/ch03_webtoon.png | .png | YES |
| 6.9 MB | artifacts/manga_book/ch02_webtoon.png | .png | YES |
| 6.9 MB | artifacts/manga_book/ch01_webtoon.png | .png | YES |
| 5.9 MB | artifacts/audiobook_samples/ahjan_anxiety_ch1.mp3 | .mp3 | YES |
| 5.8 MB | artifacts/ei_v2/eval_rigorous_report.json | .json | NO — text |
| 5.8 MB | artifacts/manga_book/ch04_webtoon.png | .png | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/wind_gentle_01.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/wind_gentle_01.mp3 | .mp3 | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/stream_water_01.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/stream_water_01.mp3 | .mp3 | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/rain_gentle_02.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/rain_gentle_02.mp3 | .mp3 | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/rain_gentle_01.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/rain_gentle_01.mp3 | .mp3 | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/ocean_waves_02.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/ocean_waves_02.mp3 | .mp3 | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/ocean_waves_01.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/ocean_waves_01.mp3 | .mp3 | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/night_crickets_01.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/night_crickets_01.mp3 | .mp3 | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/forest_birds_01.wav | .wav | YES |
| 5.5 MB | assets/sfx_bank/nature_ambient/forest_birds_01.mp3 | .mp3 | YES |
| 5.5 MB | anxiety_hack/preview.mp3 | .mp3 | YES |
| 5.5 MB | artifacts/audiobook_samples/master_wu_courage_ch1.mp3 | .mp3 | YES |
| 5.5 MB | artifacts/audiobook_samples/joshin_anxiety_ch1.mp3 | .mp3 | YES |
| 5.2 MB | artifacts/audiobook_samples/ra_self_worth_ch1.mp3 | .mp3 | YES |
| 5.2 MB | artifacts/audiobook_samples/omote_sleep_anxiety_ch1.mp3 | .mp3 | YES |
| 5.2 MB | artifacts/audiobook_samples/junko_overthinking_ch1.mp3 | .mp3 | YES |
| 5.1 MB | artifacts/audiobook_samples/ajahn_x_boundaries_ch1.mp3 | .mp3 | YES |
| 5.1 MB | artifacts/audiobook_samples/master_feung_burnout_ch1.mp3 | .mp3 | YES |
| 5.0 MB | artifacts/audiobook_samples/pamela_fellows_burnout_ch1.mp3 | .mp3 | YES |
| 4.9 MB | artifacts/audiobook_samples/master_sha_grief_ch1.mp3 | .mp3 | YES |
| 4.8 MB | artifacts/audiobook_samples/miki_imposter_syndrome_ch1.mp3 | .mp3 | YES |
| 4.7 MB | artifacts/audiobook_samples/adi_da_self_worth_ch1.mp3 | .mp3 | YES |
| 4.6 MB | artifacts/audiobook_samples/sai_ma_grief_ch1.mp3 | .mp3 | YES |
| 4.6 MB | archive/root_cleanup_2026_04_10/e8a9896a-…html | .html | NO — text |
| 4.4 MB | artifacts/podcast_pilot/podcast/…_podcast_short.mp3 | .mp3 | YES |
| 4.3 MB | brand-wizard-app/node_modules/tailwindcss/… | .js | NO — gitignored |
| 4.2 MB | brand-wizard-app/node_modules/lucide-react/… | .map | NO — gitignored |
| 3.8 MB | pearl_news/del_intake_pics/cultural_insight.png | .png | YES |
| 3.7 MB | pearl_news/del_intake_pics/global_update.png | .png | YES |
| 3.7 MB | brand-wizard-app/node_modules/lucide-react/… | .map | NO — gitignored |
| 3.5 MB | old_chats/0c3299dd-…html | .html | NO — text |

---

## Top 50 Largest in Git History (Ever Committed)

| Size | Path | Still Exists? | LFS Candidate? |
|------|------|--------------|---------------|
| 6 GB | pearl_star/ubuntu-24.04.4-desktop-amd64.iso | NO — deleted | YES (should never have been committed) |
| 534 MB | pearl_star/linux-firmware_20240318…amd64.deb | NO — deleted | YES |
| 108 MB | pearl_star/linux-modules-extra-6.8.0-107…deb | NO — deleted | YES |
| 108 MB | pearl_star/linux-modules-extra-6.8.0-100…deb | NO — deleted | YES |
| 75 MB | artifacts/videos/youtube/master_feung_burnout_youtube.mp4 | NO — deleted | YES |
| 67 MB | artifacts/videos/youtube/master_sha_grief_youtube.mp4 | NO — deleted | YES |
| 67 MB | artifacts/videos/youtube/master_feung_burnout_youtube.mp4 | NO — rev 2 | YES |
| 57 MB | artifacts/videos/youtube/ahjan_anxiety_youtube.mp4 | NO — deleted | YES |
| 55 MB | artifacts/videos/youtube/miki_imposter_syndrome_youtube.mp4 | NO — deleted | YES |
| 52 MB | artifacts/videos/youtube/ahjan_anxiety_youtube.mp4 | NO — rev 2 | YES |
| 51 MB | artifacts/videos/youtube/adi_da_self_worth_youtube.mp4 | NO — deleted | YES |
| 51 MB | artifacts/videos/youtube/maat_boundaries_youtube.mp4 | NO — deleted | YES |
| 50 MB | artifacts/videos/youtube/ahjan_anxiety_youtube.mp4 | NO — rev 3 | YES |
| 50 MB | artifacts/videos/youtube/joshin_anxiety_youtube.mp4 | NO — deleted | YES |
| 44 MB | artifacts/videos/youtube/maat_boundaries_youtube.mp4 | NO — rev 2 | YES |
| 44 MB | artifacts/videos/youtube/adi_da_self_worth_youtube.mp4 | NO — rev 2 | YES |
| 44 MB | artifacts/videos/youtube/junko_overthinking_youtube.mp4 | NO — deleted | YES |
| 41 MB | artifacts/videos/youtube/master_wu_courage_youtube.mp4 | NO — deleted | YES |
| 40 MB | artifacts/videos/youtube/omote_sleep_anxiety_youtube.mp4 | NO — deleted | YES |
| 26 MB | artifacts/videos/youtube/.work_master_sha…/01_seg_hook.mp4 | NO — deleted | YES |
| 26 MB | artifacts/videos/youtube/joshin_anxiety_youtube.mp4 | NO — rev 2 | YES |
| 21 MB | brand-wizard-app/public/assets/video/youtube/ahjan_anxiety_youtube.mp4 | MAYBE | YES |
| 20 MB | artifacts/videos/youtube/junko_overthinking_youtube.mp4 | NO — rev 2 | YES |
| 19 MB | artifacts/videos/tiktok/master_feung_burnout_tiktok.mp4 | NO — deleted | YES |
| 17 MB | brand-wizard-app/public/assets/video/youtube/ahjan_anxiety_youtube.mp4 | MAYBE rev 2 | YES |
| 14 MB | artifacts/videos/youtube/.work_pamela…/03_seg_reflection.mp4 | NO — deleted | YES |
| 13 MB | artifacts/videos/youtube/.work_pamela…/02_seg_story.mp4 | NO — deleted | YES |
| 13 MB | artifacts/videos/youtube/.work_pamela…/01_seg_hook.mp4 | NO — deleted | YES |
| 13 MB | pearl_star/linux-headers-6.8.0-100…all.deb | NO — deleted | YES |
| 13 MB | artifacts/narration/master_wu_narration.wav | NO — deleted | YES |
| 12 MB | artifacts/videos/youtube/.work_ahjan…/02_seg_story.mp4 | NO — deleted | YES |
| 12 MB | artifacts/videos/tiktok/adi_da_self_worth_tiktok.mp4 | NO — deleted | YES |
| 12 MB | brand-wizard-app/public/assets/video/tiktok/ahjan_anxiety_tiktok_v2.mp4 | MAYBE | YES |
| 11 MB | brand-wizard-app/public/assets/covers/kdp/pamela_fellows_podcast.png | MAYBE | YES |
| 11 MB | brand-wizard-app/public/assets/covers/kdp/master_wu_podcast.png | MAYBE | YES |
| 11 MB | artifacts/videos/youtube/.work_ahjan…/03_seg_reflection.mp4 | NO — deleted | YES |
| 10 MB | brand-wizard-app/public/assets/covers/kdp/pamela_fellows_audiobook.png | MAYBE | YES |
| 10 MB | artifacts/videos/tiktok/maat_boundaries_tiktok.mp4 | NO — deleted | YES |
| 10 MB | brand-wizard-app/public/assets/video/tiktok/ahjan_anxiety_tiktok_v2.mp4 | MAYBE rev 2 | YES |
| 10 MB | artifacts/videos/tiktok/master_feung_burnout_tiktok.mp4 | NO — rev 2 | YES |
| 10 MB | artifacts/videos/youtube/.work_ahjan…/01_seg_hook.mp4 | NO — deleted | YES |
| 10 MB | brand-wizard-app/public/assets/covers/kdp/maat_audiobook.png | MAYBE | YES |
| 10 MB | brand-wizard-app/public/assets/covers/kdp/omote_podcast.png | MAYBE | YES |
| 9 MB | artifacts/videos/youtube/.work_ahjan…/01_seg_hook.mp4 | NO — rev 2 | YES |
| 9 MB | artifacts/simulation_10k.json | MAYBE | NO — text |
| 9 MB | artifacts/videos/youtube/.work_pamela…/04_seg_exercise.mp4 | NO — deleted | YES |
| 9 MB | artifacts/videos/tiktok/miki_imposter_syndrome_tiktok.mp4 | NO — deleted | YES |
| 9 MB | brand-wizard-app/node_modules/@esbuild/…/esbuild | NO — gitignored | NO |
| 9 MB | brand-wizard-app/public/assets/covers/kdp/omote_audiobook.png | MAYBE | YES |
| 8 MB | artifacts/videos/tiktok/ahjan_anxiety_tiktok.mp4 | NO — deleted | YES |

---

## Size by Extension (Working Tree, excl .git & .claude)

| Extension | Count | Total Size | LFS Candidate? |
|-----------|-------|------------|---------------|
| .mp3 | 611 | 320 MB | **YES** |
| .lpf | 1 | 290 MB | **YES** |
| .png | 406 | 179 MB | **YES** |
| .wav | 48 | 87 MB | **YES** |
| .mp4 | 47 | 21 MB | **YES** |
| .pdf | 3 | 9 MB | **YES** |
| .jpeg | 4 | 0.8 MB | YES |
| .docx | 28 | 0.8 MB | MAYBE (small) |
| .jpg | 38 | 0.5 MB | YES |
| .webp | 5 | 0.3 MB | MAYBE |
| .zip | 44 | 0.3 MB | YES |
| .xlsx | 1 | 0.03 MB | YES |

**Binary total in working tree:** ~908 MB (mp3 + lpf + png + wav + mp4 + pdf + jpeg + jpg + zip + xlsx + docx + webp)

---

## Claude Worktrees Breakdown

| Worktree | Size |
|----------|------|
| recursing-lalande/ | 8.3 GB |
| dazzling-germain/ | 7.9 GB |
| unruffled-sanderson/ | 7.8 GB |
| silly-bassi/ | 1.5 GB |
| stupefied-golick/ | 1.1 GB |
| great-curie/ | 1.0 GB |
| hardcore-yalow/ | 963 MB |
| serene-archimedes/ | 945 MB |
| modest-tereshkova/ | 945 MB |
| lucid-kapitsa/ | 945 MB |
| **Total** | **33 GB** |

Note: Three worktrees are 7-8 GB each — likely contain their own copies of large binary blobs. Cleaning stale worktrees would recover ~33 GB.

---

## Root Cause Analysis

The 93 GB repo breaks down as:

1. **`.git/objects/pack/` — 56 GB** — The history contains:
   - A 6 GB Ubuntu ISO (`pearl_star/`) committed then deleted
   - ~700 MB of Linux .deb packages committed then deleted
   - Hundreds of MB of MP4 video renders (YouTube/TikTok) committed, revised, deleted
   - Large PNG cover art committed across multiple revisions
   - Multiple revisions of the same binary files create separate blobs

2. **`.git/` loose objects — 3 GB** — Unpacked objects from recent work

3. **`.claude/worktrees/` — 33 GB** — Claude Code worktrees (not in git history, but consume disk)

4. **Working tree — 1.4 GB** — Actual content files (already reasonable)

---

## Recommendations

1. **Immediate (this PR):** Set up `.gitattributes` for LFS tracking — all future binary commits use LFS automatically
2. **Immediate:** Install `git lfs` via `brew install git-lfs`
3. **Short-term:** Clean stale `.claude/worktrees/` — recover ~33 GB
4. **Scheduled maintenance:** Run `git lfs migrate import --everything` to rewrite history — target: clone size under 2 GB
5. **Scheduled maintenance:** Add `pearl_star/` and `*.iso` and `*.deb` to `.gitignore`
