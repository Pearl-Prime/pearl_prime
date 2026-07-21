# Handoff — PhoenixControl buildable-again fix (Pearl Prime cockpit)

**Agent:** Pearl_GitHub (offline landing) · **Date:** 2026-07-19
**Substrate:** `pearlstar_offline` (GitHub 403, account suspended) · **Terminal:** LANDED-OFFLINE
**Branch:** `offline/phoenixcontrol-buildable-fix-20260718` (based on `origin/main`)

## Problem

The native macOS cockpit `PhoenixControl/` (installed as **Pearl Prime.app**) had not
compiled since ~2026-07-13. Two defects, both present on `origin/main` (not branch-local):

1. **Orphaned source file** — `PhoenixControl/Views/PearlPrimeWebView.swift` is tracked in
   git and referenced by `ContentView`, but was never added to the Xcode target's Sources
   build phase in `project.pbxproj`. Compile error: *"cannot find 'PearlPrimeWebView' in
   scope."*
2. **Non-exhaustive switch** — `ContentView.swift` `TabTag.guidance` was missing the
   `.contentInventory` case (the `title` and `systemImage` switches had it). Compile error:
   *"switch must be exhaustive."*

The two `/Applications` bundles were 4-month-stale unsigned debug builds because of this.

## Fix (this branch — exactly 2 source files vs origin/main)

- `project.pbxproj`: add `PearlPrimeWebView.swift` to the target (PBXBuildFile +
  PBXFileReference + group child + Sources phase; IDs `E1…02`/`E2…02`, mirroring
  `ContentInventoryView.swift`).
- `ContentView.swift`: add the missing `.contentInventory` guidance case.

Verified: `xcodebuild -scheme "Phoenix Control" -configuration Release` → **BUILD
SUCCEEDED** (universal arm64+x86_64). The release build was rebranded to **Pearl Prime**
(`com.phoenixomega.PearlPrime`, ad-hoc signed), installed to `/Applications/Pearl Prime.app`,
and confirmed to launch without crashing. The two stale bundles were removed.

## Diff-stat gate

`origin/main..HEAD` = 3 files: the 2 source fixes + this handoff. No other paths. No
binary. Working tree not used as commit substrate (temp-index off `origin/main^{tree}`).

## Next

- Replay as a normal PR to `main` when GitHub 403 clears (it fixes the build for everyone,
  not just this machine).
- First launch of the app: point it at the repo path (`/Users/ahjan/phoenix_omega`);
  needs `scripts/` present + `python3` on PATH. GitHub-backed tabs error while 403.
