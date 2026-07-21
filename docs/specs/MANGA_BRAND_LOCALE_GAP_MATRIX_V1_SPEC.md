# Manga Brand × Locale Gap Matrix — V1 Spec

**Status:** SPECCED (gt30d Wave-B C05 · 2026-07-22)  
**Keepers:** I033  
**MERGE:** `ARTIFACTS_RETENTION_POLICY_V1_SPEC` / LFS-to-R2 — do not fork retention.

## Purpose
Matrix of manga brands × locales classifying assets as: PRESENT | LFS_POINTER_ONLY | ABSENT.

## Cursor-may-implement
1. Script under `scripts/manga/` or `scripts/audit/` emitting TSV matrix (smoke: 2 brands × 2 locales).
2. No destructive prune; dry-run only unless operator authorizes.

## Signal
`gt30d-wb-c05-spec-terminal`
