# LFS Offload Audit — 2026-07-09

**Author:** Pearl_DevOps + Pearl_Int  
**PROJECT_ID:** lfs-r2-offload-pilot  
**Evidence method:** Filesystem scan of binary extensions in key dirs + `git check-attr filter` spot checks. Full `git lfs ls-files -s` timed out at 600s on this repo (57k+ tracked files); inventory is conservative lower-bound from working-tree scan.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Binary files scanned (key dirs) | 10,395 |
| Total binary bytes (disk + LFS pointers) | **10.95 GB** |
| LFS smudge budget per worktree (operator memory) | ~3.2 GB |
| Metered $ risk | GitHub LFS storage + bandwidth (only metered cost on public repo) |
| R2 lane | Live (`scripts/artifacts/r2_sync.py`, `phoenix-omega-artifacts` bucket) |

**Billing reconciliation:** Operator-reported accruing LFS line item is consistent with `assets/manga_catalog` (6.2 GB) + `brand-wizard-app/public` (4.1 GB) + manga render trees (~0.5 GB alarm_is_lying alone). These families dominate smudge on clone/checkout. Forward-only offload targets regenerable manga render trees first; SOURCE_OF_TRUTH/ and atoms/ stay in-repo.

---

## Per-Family Classification

| Family | Files | MB | GB | Class | CI/worktree smudge? |
|--------|------:|---:|---:|-------|---------------------|
| `assets/manga_catalog` | 6,078 | 6,181.6 | 6.05 | BUILD-ARTIFACT (regenerable frames) | **YES** — largest smudge offender |
| `brand-wizard-app/public` | 3,386 | 4,121.4 | 4.03 | MIXED — deliveries un-LFS'd (#1729); covers/audio/video still heavy | **PARTIAL** — deliveries excluded; covers still smudge |
| `manga/alarm_is_lying` | 550 | 453.3 | 0.44 | BUILD-ARTIFACT (render trees) | **YES** — pilot family |
| `assets/sfx_bank` | 96 | 174.6 | 0.17 | SOURCE-adjacent (reusable SFX) | YES if smudged |
| `artifacts/manga/image_bank` | 66 | 101.1 | 0.10 | BUILD-ARTIFACT | YES |
| `artifacts/qa` | 26 | 18.2 | 0.02 | BUILD-ARTIFACT | occasional |
| `artifacts/catalog` | 14 | 7.4 | 0.01 | DELIVERY (brand1_deep un-LFS'd) | low |
| `SOURCE_OF_TRUTH/` | — | ~15 | 0.01 | **SOURCE-OF-TRUTH** — NEVER move | text-primary |
| `atoms/` | — | ~61 | 0.06 | **SOURCE-OF-TRUTH** — NEVER move | text-primary |
| `deliveries/**` | — | — | — | **DELIVERY** — already R2-native / un-LFS'd (#1729) | NO |

---

## Top-20 Offenders (working tree, by file size)

| MB | Path | Notes |
|---:|------|-------|
| 11.76 | `brand-wizard-app/public/assets/covers/kdp/pamela_fellows_podcast.png` | KDP cover |
| 11.34 | `brand-wizard-app/public/assets/covers/kdp/master_wu_podcast.png` | KDP cover |
| 10.82 | `brand-wizard-app/public/assets/covers/kdp/pamela_fellows_audiobook.png` | KDP cover |
| 6.92 | `artifacts/manga_book/ch01_webtoon.png` | Regenerable |
| 6.92 | `artifacts/manga_book/ch02_webtoon.png` | Regenerable |
| 6.92 | `artifacts/manga_book/ch03_webtoon.png` | Regenerable |
| 5.92 | `artifacts/audiobook_samples/ahjan_anxiety_ch1.mp3` | Audio sample |
| 2.13 | `artifacts/manga/.../composed_v4_qwen/ep_001/ep001_005.png` | Pilot candidate panel |

Full machine-readable inventory: `artifacts/audit/LFS_INVENTORY_2026-07-09.tsv` (per-family summary; regenerable via audit script in spec).

---

## Pilot Candidate Detail

**Path:** `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/`

| Metric | Value |
|--------|-------|
| PNG count | 35 |
| On-disk size | 68 MB |
| LFS filter | `filter: lfs` (confirmed via `git check-attr`) |
| Regenerable | YES — Qwen compose pass, reproducible from continuity/script |
| RENDER_PROGRESS | Created in pilot PR for gate-compat proof |

---

## Smudge Impact (operator memory cross-check)

- `project_worktree_disk_constraint`: each worktree smudge ≈ 3.2 GB → dispatch kills at 99% disk.
- Offloading `composed_v4_qwen` pilot alone saves **68 MB** smudge per worktree for that subtree; wave-1 target (`assets/manga_catalog` + manga render trees) projects **>6.5 GB** LFS bandwidth reduction per full smudge.
