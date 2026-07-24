# LFS → R2 Offload V1 Spec

**Status:** ACTIVE — pilot landed 2026-07-09 (#5306); Waves 3 & 4 landed on `main` 2026-07-23 (PR #151 `b702de43f9`, PR #161 `bccb188535`, owner-approved >50 deletions); Wave 2 = N/A (0 git-tracked files); only Phase B history rewrite (owner-gated) remains open  
**Owner:** Pearl_DevOps (infra) · Pearl_Int (R2 credentials lane)  
**Subsystem:** `pearl_devops` + `integrations`  
**Authority:** extends `scripts/artifacts/r2_sync.py`, `config/artifacts/r2_buckets.yaml`, `.gitattributes`  
**Supersedes:** closed PR #427 (parallel uploader — NOT canon; extend `r2_sync.py` only)

---

## 0. Problem

GitHub LFS is the **only metered $ risk** on this public repo. LFS smudge is the recurring **~3.2 GB/worktree** disk killer (`project_worktree_disk_constraint`). Cloudflare R2 is already live for EPUB/storefront delivery (`project_waystream_r2_delivery_chain`).

**Scope constraint:** FORWARD-ONLY. No `git lfs migrate`, BFG, or history rewrite. Existing LFS objects remain in history; `.gitattributes` is narrowed so moved families stop LFS-tracking on new commits.

---

## 1. Operator decisions (batch ratification)

| ID | Question | **Default (this spec)** | Escalate if |
|----|----------|---------------------------|-------------|
| **Q-LFS-01** | Which families move? | Manga render trees + frames + regenerable artifacts ≥1 MB under `artifacts/manga/**`, `assets/manga_catalog/**`. `SOURCE_OF_TRUTH/` and `atoms/` **NEVER** move. | Operator wants audio/SFX in wave 1 |
| **Q-LFS-02** | Manifest format? | Slug-keyed TSV per family under `artifacts/manifests/lfs_offload/<slug>.tsv` — columns: `repo_path`, `r2_key`, `bytes`, `sha256`. Companion YAML optional for `r2_sync.py verify`. | Operator prefers JSON |
| **Q-LFS-03** | Gate compat? | `check_render_progress_bytes.py` accepts offloaded rows via manifest `bytes`+`sha256` when image absent on disk. `scripts/ci/deep_verify_r2_offload.py` weekly fetch+sha256 from R2. Missing/undersized still **RED**. | Never weaken the 50 KB floor |
| **Q-LFS-04** | Local dev pull-on-demand? | **Yes** — `r2_sync.py pull-on-demand --slug <slug>` restores to `repo_path` locations. | — |
| **Q-LFS-05** | History? | Existing LFS blobs untouched. `.gitattributes` narrowed per family; offloaded binaries `git rm` from index after round-trip proof. | History rewrite = operator-ratification only |
| **Q-LFS-06** | CI smudge skip? | `GIT_LFS_SKIP_SMUDGE=1` default in workflows/worktree helpers once a family is manifest-only. | — |

**Ratification line (one line):** `Q-LFS-01..06: defaults accepted`

---

## 2. Architecture

```
┌─────────────────┐     push-offload      ┌──────────────────┐
│  Repo (manifest │ ────────────────────► │ Cloudflare R2    │
│  + TSV only)    │ ◄── pull-on-demand    │ phoenix-omega-   │
└─────────────────┘                       │ artifacts        │
        │                                 └──────────────────┘
        ▼
 check_render_progress_bytes.py
   ├─ disk/LFS pointer (existing)
   └─ manifest bytes+sha256 (new, offloaded)
        │
        ▼ (weekly)
 deep_verify_r2_offload.py → fetch R2 → sha256
```

**Principle 9:** extend `scripts/artifacts/r2_sync.py` + `scripts/artifacts/setup_r2.sh`. No parallel uploader.

**Presign rule:** manifests store **R2 keys only**. Presigned URLs expire ≤1 week (`reference_r2_presign_one_week_ceiling`).

---

## 3. Manifest contract

**Path:** `artifacts/manifests/lfs_offload/<slug>.tsv`

```tsv
# slug: stillness_press_alarm_composed_v4_ep_001
# namespace: manga_rendered_books
# bucket: phoenix-omega-artifacts
# produced_at: 2026-07-09T03:00:00Z
repo_path	r2_key	bytes	sha256
artifacts/manga/.../ep001_001.png	manga/rendered_books/.../ep001_001.png	1882246	abc...
```

**Slug naming:** `<series_short>_<subdir>` — stable, no dates in slug (dates go in `produced_at` meta).

**R2 key pattern:** per `config/artifacts/r2_buckets.yaml` namespace prefix + series_id + relative path.

---

## 4. Tooling

### 4.1 `r2_sync.py` (extended)

| Subcommand | Purpose |
|------------|---------|
| `push-offload` | Upload `--src` tree; write TSV manifest; optional YAML mirror |
| `pull-on-demand` | `--slug` or `--manifest` → restore files to `repo_path` columns |
| `push` / `pull` / `verify` / `ls` | Unchanged (Layer-2 YAML manifests) |

Shared helpers: `scripts/artifacts/lfs_offload_manifest.py`.

### 4.2 `check_render_progress_bytes.py` (extended)

When `--require-images`:
1. Image on disk ≥ 50 KB → **PASS** (unchanged)
2. LFS pointer with real size ≥ 50 KB → **PASS** (unchanged)
3. Image absent → lookup `repo_path` in `artifacts/manifests/lfs_offload/*.tsv`
4. Manifest entry `bytes` ≥ 50 KB and valid `sha256` → **PASS** (manifest-verify)
5. Else → **FAIL**

New flag: `--offload-manifest-dir` (default `artifacts/manifests/lfs_offload`).

### 4.3 `deep_verify_r2_offload.py` (new)

Weekly workflow (`.github/workflows/r2-offload-deep-verify.yml` — wave 2):
- For each TSV manifest entry: `head_object` size check + optional full download sha256
- Exit 1 on any mismatch

---

## 5. `.gitattributes` forward-only narrowing

Per-family exclusion **after** round-trip proof, placed **after** generic `*.png filter=lfs` rules (last match wins):

```gitattributes
# LFS→R2 offload V1 pilot — regenerable composed_v4_qwen render tree
artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/** -filter -diff -merge -text
```

Offloaded binaries are removed from git index; manifest + optional `.r2-offload-slug` sidecar remain.

---

## 6. Pilot V1 (this PR)

| Field | Value |
|-------|-------|
| Family | `composed_v4_qwen/` under alarm-is-lying series |
| Slug | `stillness_press_alarm_composed_v4_ep_001` |
| Files | 35 PNGs, ~68 MB |
| Namespace | `manga_rendered_books` |
| Proof | upload → manifest → delete local copy → pull-on-demand → sha256 match |
| Gate | `RENDER_PROGRESS.tsv` + `--require-images` green via manifest-verify |

---

## 7. Wave plan (post-pilot — CLOSEOUT, not this PR)

| Wave | Family | Est. GB | Priority | Status |
|------|--------|--------:|----------|--------|
| 2 | `assets/manga_catalog/**` | 6.0 | Highest smudge/$ leverage | **N/A** — target has 0 git-tracked files as of 2026-07-24 (`.gitignore:127`); handled by Lane 01 R2 backup, not git surgery |
| 3 | Remaining `artifacts/manga/**/assembled/`, `v4_render_cache/` | ~1.5 | Manga render trees | **DONE** — PR #151 `b702de43f9c93f36963794dd2513d45ae56b4c3d` (267 tracked files, owner-approved >50 deletions, 2026-07-23) |
| 4 | `brand-wizard-app/public/assets/covers/` (regenerable) | ~2.0 | After manga catalog | **DONE** — PR #161 `bccb1885352de1135c99e70cb1ac02075c302c91` (79 tracked files, owner-approved >50 deletions, 2026-07-23) |
| — | `SOURCE_OF_TRUTH/`, `atoms/`, `deliveries/**` | — | **NEVER** | — |

---

## 8. Acceptance

- [ ] Audit artifact with per-family table
- [ ] This spec + `CANONICAL_ARTIFACTS_REGISTRY.tsv` row
- [ ] Pilot round-trip sha256 proof logged in `artifacts/audit/LFS_OFFLOAD_PILOT_PROOF_2026-07-09.json`
- [ ] `check_render_progress_bytes.py --require-images` PASS on pilot TSV with images removed
- [ ] No gate weakening (50 KB floor intact)
