# Handoff — Pearl Prime Phase 1 Preflight & Drift Runner

**Agent:** PhoenixControl / Pearl_GitHub (offline landing) · **Date:** 2026-07-19
**Substrate:** `pearlstar_offline` (GitHub 403, account suspended) · **Terminal:** LANDED-OFFLINE
**Branch:** `offline/pearlprime-preflight-gates-20260719` (based on `origin/main^{tree}`)
**Acceptance layer:** `CODE-WIRED` + `EXECUTED-REAL` (Release build + launch verified). Not PROVEN-AT-BAR (no blind operator soak). Gate-PASS from the new tab ≠ shippable catalog work.

## What shipped (Phase 1 only)

New **Preflight & Gates** tab in PhoenixControl (Pearl Prime.app):

1. **ScriptRunner** — allowlisted the CLAUDE.md preflight + drift scripts; `.sh` paths exec `/bin/bash` (same allowlist/redaction/cwd).
2. **PreflightGatesView** — Mandatory Preflight (5) + Drift Detectors (6); per-row Run + LiveLogView; exit-code verdicts (0=PASS, nonzero=BLOCK, WARN in output + exit 0 = WARN); Run all; CLEAR TO LAND / BLOCKED banner; git branch + `rev-list --left-right --count origin/main...HEAD` strip.
3. **ContentView / pbxproj** — `TabTag.preflightGates` wired (title/systemImage/guidance + detail + Sources phase; IDs `G1…01`/`G2…01`).
4. **StatusBadge** — WARN / BLOCK / CLEAR TO LAND colors.

No network write. No git write from the app. No gate-script logic edits. Phase 2 (Offline Landing Studio) not started.

## Verified

- `xcodebuild -scheme "Phoenix Control" -configuration Release` → **BUILD SUCCEEDED** (universal arm64 + x86_64).
- Rebranded + ad-hoc signed → `/Applications/Pearl Prime.app` (`com.phoenixomega.PearlPrime`); process launched (pid observed).
- Binary contains `Preflight & Gates` / drift script path strings.

## Explicit paths landed (temp-index off `origin/main^{tree}`)

- `PhoenixControl/OPERATOR_COCKPIT_SPEC.md`
- `PhoenixControl/Services/ScriptRunner.swift`
- `PhoenixControl/Views/PreflightGatesView.swift`
- `PhoenixControl/Views/ContentView.swift`
- `PhoenixControl/Views/Components/StatusBadge.swift`
- `PhoenixControl/PhoenixControl.xcodeproj/project.pbxproj`
- `artifacts/coordination/handoffs/pearlprime_preflight_gates_20260719.md`

## Next

- Phase 2: Offline Landing Studio + armed `OperatorActions` (see `PhoenixControl/OPERATOR_COCKPIT_SPEC.md` §5).
- Replay as PR to `main` when GitHub 403 clears.
- Reference prior: `offline/phoenixcontrol-buildable-fix-20260718@24ef876203`.
