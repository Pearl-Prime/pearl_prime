# CI recovery Phase 2 — author cover art gate (FAIL → WARN on missing assets)

**Workstream:** `ws_ci_recovery_phase_2_impl_20260510`  
**Cap / PR context:** CI-BASELINE-RECOVERY Phase 2; PR #1006 ratifies **Q2 = relax-to-warn** for missing registry-referenced `cover_art_base` PNGs.

## Behavior

| Mode | Env / flag | Missing on-disk `cover_art_base` | Registry / style / palette issues |
|------|------------|-----------------------------------|-------------------------------------|
| **warn** (default) | `COVER_ART_GATE_MODE=warn` or unset | `::warning::` on stderr, **exit 0** | `FAIL:` on stderr, **exit 1** |
| **fail** (legacy) | `COVER_ART_GATE_MODE=fail` or `--gate-mode fail` | `FAIL:`, **exit 1** | `FAIL:`, **exit 1** |

CLI `--gate-mode` overrides `COVER_ART_GATE_MODE`.

## Smoke (repo checkout: `origin/main` @ implementation branch, same tree as Core tests gate)

**Before (strict / fail posture):**

```text
$ COVER_ART_GATE_MODE=fail python3 scripts/ci/check_author_cover_art.py
… FAIL: <author>: cover_art_base file does not exist: assets/authors/cover_art/…
Author cover art gate: every launchable author must have …
→ exit 1
```

**After (default warn posture, PR intent for Core tests):**

```text
$ COVER_ART_GATE_MODE=warn python3 scripts/ci/check_author_cover_art.py
::warning::author cover art (missing asset): daniel_voss: cover_art_base file does not exist: …
… (12 authors in this checkout)
::warning::Author cover art gate: missing cover_art_base file(s) for 12 launchable author(s); continuing under warn mode (Phase 2 Q2).
→ exit 0
```

## Automated tests

`PYTHONPATH=. python3 -m pytest tests/ci/test_check_author_cover_art_warn_mode.py -v` — **6** cases (missing PNG warn vs fail, present PNG, CLI override, default warn, hard error in warn mode).

## Files touched

- `scripts/ci/check_author_cover_art.py`
- `tests/ci/test_check_author_cover_art_warn_mode.py`
- `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` (Phase 2 implementation pointer)
