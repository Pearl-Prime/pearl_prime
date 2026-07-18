# Atom Stub Debt — tracking artifact (2026-07-01)

THE GATE: make it impossible to ship an EPUB containing an unfilled atom stub,
catalog-wide. This artifact tracks the **remaining** unfilled atom-stub variants
after the loader-hardening fix and the priority HOOK fill landed.

## What changed (the fix this artifact accompanies)

1. **Loader hardening** — `phoenix_v4/rendering/prose_resolver.py`
   `_parse_block_file_with_prose` / `_parse_canonical_with_prose` now EXCLUDE any
   `## <SLOT> vNN` body that matches the stub pattern (reusing the registry's
   `enrichment_select._REGISTRY_PLACEHOLDER_RE` + mirrored bracket / pipeline /
   bare-ellipsis / unresolved-variable detectors) from the selectable variant
   pool — for ALL slot types. A required slot whose blocks are ALL stubs raises
   `InsufficientVariantsError` (author atoms upstream — never ship the stub).

2. **Assembly-path gate** — `scripts/release/build_epub.py` now invokes the
   #3787 stub-catch (`book_renderer.delivery_contract_gate`) before EPUB
   emission. A stub BLOCKS the build (raise / non-zero exit), not warns.

3. **Priority fill** — the 12 base HOOK cells that were the actual leak vector
   (1 real + ~29 `[Persona-specific hook for …]` stubs each) were filled with
   real Tier-1 prose so every base HOOK cell now clears the 3-variant runtime
   floor (`base_cells_raising_under_runtime_gate = 0`).

## Why the remaining tail is SAFE (fanout can proceed)

The loader now DROPS every stub variant listed below from the selectable pool,
so none of them can leak into reader-facing prose. Every base cell has >= 3 real
variants, so none raise. The tail is therefore a **quality backlog** (more
authored variety per cell), not a **ship blocker**.

## Remaining stub debt (see `stub_debt_census.json` for the full per-cell list)

| scope  | files with stub variants | stub variants total | cells raising under runtime gate |
|--------|--------------------------|---------------------|----------------------------------|
| base (en) | 12 | 300 | **0** |
| locale (CJK + others) | 22 | 660 | n/a (locale falls back to en) |

- **Base tail (300 variants across 12 HOOK cells):** these are the `v06+` stubs
  of the already-priority-filled HOOK cells. Each cell has 5–8 real variants;
  filling more adds HOOK variety but is not required for a clean ship.
- **Locale tail (660 variants across 22 files):** locale CANONICAL.txt copies of
  the same HOOK cells. The resolver falls back to the (now-clean) English base
  variant when a locale variant is a stub, so these do not leak either.

## Next actions (backlog, operator-prioritized)

1. Author additional real HOOK variants for the 12 base cells (drain the 300
   `v06+` stubs) for richer per-book HOOK rotation — Tier-1 (Pearl_Writer).
2. Translate the filled base HOOK prose into the CJK locales to drain the 660
   locale stubs (Qwen, Tier-2, scheduled lane — CJK only).
3. Re-run `stub_debt_census.json` generation to confirm the tail shrinks.

No GPU / paid LLM was used to produce this artifact or the prose fills.
