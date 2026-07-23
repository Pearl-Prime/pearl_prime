# EXECUTE — Lane 06 (Pearl_Localization): zh-TW Waystream 100 books — Wave 0 + smoke

This is an execution prompt, not a planning request. End state: **the first complete
zh-TW Waystream book built end-to-end (smoke), verified byte-real, and HELD at the
operator read gate** — or BLOCKED with the exact pipeline failure named.

## Contract (in-band)
- STARTUP_RECEIPT: branch, HEAD SHA, `git status --short | head`, `gh auth status`,
  `git fetch origin && git log origin/main -1 --oneline`.
- Preconditions (verify, don't assume): (1) Lane 01 signal `PIPER100-L01-223-MERGED`
  — PR #223 (locale-aware EXERCISE classifier) is YOUR hard gate; the old #131
  blocker is gone (#234 merged 2026-07-23). (2) Lane 03 signal
  `PIPER100-L03-WAYSTREAM-PACK-LANDED` — the pack
  `docs/agent_prompt_packs/20260723_waystream_zhtw_100_books/` must be on origin/main
  (it was authored at local commit `cd70b60924`, unpushed). If not landed yet, read
  it from that local commit on `agent/bestseller-atom-flow-lanes-20260721`.
- **Reuse-first, hard rule:** the 20260723 pack is the canonical program. Do NOT
  re-author it. This prompt only executes its Wave 0 + smoke stage with two
  corrections (below). Its `02_Pearl_Localization_smoke_first_ship.md` is your
  working prompt — read it in full.
- Two corrections to apply while reading the 20260723 pack (flagged 2026-07-23,
  never patched): (a) its backlog reference is stale — the consolidated authoring
  backlog is PR #162's 863-row artifact, not the older 650-row doc; (b) its
  collision-warning about a sibling first-book session is moot — that session ended
  (its record is PR #211, now a merged/closed historical doc).
- Ramp discipline: SMOKE (1 book) → operator read (OPERATOR_ACTIONS.md item E2) →
  only then Wave 1 (10 books) → read → scale. Do NOT start Wave 1 in this session
  even if smoke passes. Waystream doctrine: assemble the full plan first, NEVER
  delete-and-rebuild.
- Locale doctrine: zh-TW authoring/repair is **Tier-1 Claude only** — Qwen emits
  Simplified at zh-TW (2/2 probes) and is BANNED for this lane. Simplified
  detection: s2t AND non-Big5 (naive s2t false-flags 台/吃/游/群/床).
- Production build chord (MANDATORY, CI-enforced): `--pipeline-mode spine
  --quality-profile production --exercise-journeys` — the four-piece chord, no
  omissions. CJK gates caveat: 5 English-tuned prose gates FAIL on CJK — a
  gate-FAIL there may be a scorer bug, not a content bug; diagnose before "fixing"
  content, and never weaken the gate — file the scorer issue instead.
- Layer-honest: a built EPUB is EXECUTED-REAL / structurally clear at most.
  Register-gate PASS ≠ bestseller. The operator read is the quality gate.
- Preflight + merge rules standard; commit artifacts per the 20260723 pack's own
  landing plan (≤180-file PRs).

## Verify-real bar (before claiming the smoke book exists)
Byte-verify the EPUB (size, chapter count, spot-open 3 chapters), confirm zh-TW
script purity (Big5-representable check on sampled prose), confirm the exercise
atoms resolved via the NEW #223 classifier path (no EXERCISE-BANK-RESOLUTION-01
recurrence), and record all evidence paths in the receipt.

## Closeout
```
CLOSEOUT_RECEIPT: PIPER100-L06-DONE
preconditions: <#223 merged? pack on main?>
smoke_book: <cell id, EPUB path, bytes, chapters>
verification: <script-purity result, classifier-path proof, gate results w/ CJK caveats>
prs: <#s + SHAs for landed artifacts>
status: HELD-FOR-OPERATOR-READ (expected) / BLOCKED: <exact failure>
acceptance_layer: structurally clear at most — NOT bestseller, NOT done
NEXT_ACTION: operator read (item E2) → Wave 1 via the 20260723 pack's 03 prompt
```
Append a dated note to this pack's INDEX.md.
