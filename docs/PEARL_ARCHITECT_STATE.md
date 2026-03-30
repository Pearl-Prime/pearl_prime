# Pearl_Architect State

Last verified: 2026-03-28  
Owner: Pearl_Architect

## Purpose

This file is the fast resume point for architecture routing and drift prevention in Phoenix Omega.

It answers:

- what the canonical architecture anchors are
- how Pearl_Architect differs from Pearl_PM
- what common routing failures look like
- what sources should be consulted first when a task is ambiguous

## Core Distinction

- **Pearl_PM = where work should continue**
- **Pearl_Architect = where work belongs**

Pearl_PM resolves overlap, active workstreams, project fit, and handoffs.  
Pearl_Architect resolves subsystem ownership, governing docs, required repo sources, and architecture drift risk.

## Canonical Architecture Anchors

When routing a task, start here:

1. [docs/SYSTEMS_V4.md](./SYSTEMS_V4.md) — systems-level overview
2. [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md) — sole system architecture authority
3. [docs/DOCS_INDEX.md](./DOCS_INDEX.md) — authoritative navigation map
4. [docs/OWNERSHIP_MATRIX.md](./OWNERSHIP_MATRIX.md) — repo and path-family ownership boundaries
5. [artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv](../artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv) — subsystem shortcut map

## Common Drift Patterns

Reject or reroute proposals when they:

- invent a parallel UI or onboarding surface instead of updating the governed bundle
- invent generic SaaS flows where governed brand, funnel, or registry structures already exist
- introduce a new workbook, doc, or spec when a canonical file already exists
- treat historical salvage or old chat notes as current truth
- mix GitHub/repo-health work into non-GitHub lanes
- present planned or inferred business claims as if they were verified repo truth

## Current Routing Truth

- **Arc-First remains sole architecture authority.** If a proposal conflicts with Arc-First, Arc-First wins.
- **DOCS_INDEX is the canonical navigation layer.** If a task cannot be routed from there, Pearl_Architect must surface the gap.
- **SUBSYSTEM_AUTHORITY_MAP is a shortcut, not a replacement for DOCS_INDEX.**
- **Qwen-Agent / LM Studio retired operator patterns are historical only unless a new governing doc explicitly revives them.**
- **Existing workstream wins for execution; authority-doc fit wins for subsystem routing.**

## High-Value First Reads By Task Shape

| Task shape | Start here |
|-----------|------------|
| System architecture / pipeline | `docs/SYSTEMS_V4.md`, `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` |
| GitHub / repo health | `docs/GITHUB_OPERATIONS_FRAMEWORK.md`, `docs/OWNERSHIP_MATRIX.md` |
| Presentation / onboarding / UI translation | `docs/DOCS_INDEX.md`, subsystem authority, existing HTML/UI files |
| Content / prompts / messaging | subsystem authority, writer specs, current live docs/assets |
| Recovery / overlap / salvage | `docs/PEARL_PM_STATE.md`, `ACTIVE_PROJECTS.tsv`, `ACTIVE_WORKSTREAMS.tsv` |

## Next Actions

1. Keep `SUBSYSTEM_AUTHORITY_MAP.tsv` aligned with live authority docs.
2. Surface gaps when a recurring task cannot be routed cleanly from the current architecture docs.
3. Block generic or duplicate architecture before implementation starts.
4. Keep Pearl_Architect docs aligned with `SESSION_UNITY_PROTOCOL.md`.

## Architect routing decisions

### BG-PR-08 — Bestseller-grade book arc validation (closed-not-needed)

**Status:** **closed-not-needed** (Option B, 2026-03-31).  
**Rationale:** No single in-repo spec named `validate_book_emotion_arc` / `BookArcResult`; arc validation is **distributed** across existing loaders and validators (e.g. `arc_loader`, `validate_arc_alignment`, `validate_compiled_plan`, `emotion_arc_validator.validate_emotion_arc`). Further consolidation is optional engineering polish, not a blocking architecture gap.
