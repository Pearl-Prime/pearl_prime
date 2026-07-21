# Waystream Cover Delta Queue — V1 Spec

**Status:** SPECCED (gt30d Wave-B C06 · 2026-07-22)  
**Keepers:** I041  
**Cite:** `docs/NAMING_COVER_SYSTEM_37x14.md`, COVER_FIVE_LAYER uniqueness.

## Purpose
Durable delta-queue for cover rerenders: only missing/invalid work queues by default; full rerender requires explicit `--force-rerender`.

## Cursor-may-implement
1. Queue manifest schema + dry-run CLI.
2. Never blind catalog-scale rerender in this lane.

## Signal
`gt30d-wb-c06-spec-terminal`
