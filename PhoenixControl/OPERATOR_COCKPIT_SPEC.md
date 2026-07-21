# Pearl Prime (PhoenixControl) — Operator Cockpit Features Spec

**Status:** Phase 1 CODE-WIRED + BUILD-VERIFIED (2026-07-19); Phase 2+ still SPECCED · **Author:** Pearl_GitHub session 2026-07-19 · **For:** a fresh dev/Claude-Code session
**App:** the native macOS cockpit installed as `/Applications/Pearl Prime.app` (brand name); source is this `PhoenixControl/` dir, Xcode scheme **"Phoenix Control"**, one target.

---

## 0. FRESH-SESSION PROMPT (copy-paste this to start)

> Act as PhoenixControl dev. Implement **Phase 1** of `PhoenixControl/OPERATOR_COCKPIT_SPEC.md`
> (Preflight & Drift Runner). Read the spec top-to-bottom first — it is self-contained.
> Constraints: match existing view/service conventions (§3); do NOT introduce a paid LLM
> API or any network write; Phase 1 adds only read/analysis script execution (no git writes).
> Build + verify with the exact runbook in §2 before claiming done. Land your work OFFLINE
> per §7 (GitHub is 403 — `pearlstar_offline`, temp-index recipe, explicit paths, diff-stat
> gate) — nothing to origin/main. End with a CLOSEOUT naming the branch@sha and the verified
> build. Do Phase 2 only after Phase 1 builds, launches, and is landed.

Swap "Phase 1" → "Phase 2" for the Offline Landing Studio once Phase 1 is done.

---

## 1. WHY (the gap this closes)

Pearl Prime today is a **read-mostly monitor**: `ArtifactReader` loads ~15 JSON/JSONL
reports, `GitHubService` reads CI, `ScriptRunner` runs an **allowlist of 23 read/analysis
scripts**. It watches the *content pipeline* well but is **blind to the operator's daily
work**: the CLAUDE.md mandatory preflight + drift gates are CLI-only and skippable; all
offline landing is manual git plumbing; 56+ `offline/*` branches and 372 handoffs are
unsurfaced. This spec adds the operator surfaces, safely.

**Governing repo reality (do not violate):**
- **GitHub is 403 (account suspended).** All landing is offline on `pearlstar_offline`. See
  `docs/` + the handoffs under `artifacts/coordination/handoffs/`.
- **No paid LLM APIs** (CLAUDE.md, enforced by `.github/workflows/llm-policy-enforcement.yml`).
- **Never weaken a gate to pass.** These features *run* gates; they never edit gate logic.
- **Acceptance honesty:** gate-PASS ≠ shippable; file-existence ≠ authored. Surface the true layer.

---

## 2. BUILD & INSTALL RUNBOOK (verified 2026-07-19 — use exactly)

Full Xcode required (not just CLT). Build a clean Release:

```bash
cd /Users/ahjan/phoenix_omega
BUILD_DIR="$(mktemp -d)/pc_build"; mkdir -p "$BUILD_DIR"
xcodebuild \
  -project PhoenixControl/PhoenixControl.xcodeproj \
  -scheme "Phoenix Control" -configuration Release \
  -destination 'generic/platform=macOS' \
  CONFIGURATION_BUILD_DIR="$BUILD_DIR" \
  CODE_SIGN_IDENTITY="-" CODE_SIGNING_REQUIRED=NO CODE_SIGNING_ALLOWED=YES \
  build            # expect: ** BUILD SUCCEEDED ** (universal arm64 + x86_64)
```

Rebrand to "Pearl Prime" + ad-hoc sign LAST (after all Info.plist/binary edits), then install:

```bash
APP="$BUILD_DIR/Phoenix Control.app"; DEST="/Applications/Pearl Prime.app"
mv "$APP/Contents/MacOS/Phoenix Control" "$APP/Contents/MacOS/Pearl Prime"
PL="$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleExecutable 'Pearl Prime'" "$PL"
/usr/libexec/PlistBuddy -c "Set :CFBundleName 'Pearl Prime'" "$PL"
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName 'Pearl Prime'" "$PL"
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier 'com.phoenixomega.PearlPrime'" "$PL"
codesign --force --deep --sign - "$APP"        # ad-hoc; unquarantined local app runs fine
rm -rf "$DEST" && cp -R "$APP" "$DEST"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$DEST"
open "$DEST"    # verify it launches (first launch → "Open Settings" until repo path set)
```

**First-launch behavior (expected, not a bug):** shows *Open Settings* until you set the
repo path to `/Users/ahjan/phoenix_omega` (needs `scripts/` present + `python3` on PATH).
GitHub-backed tabs error while the account is 403-suspended.

---

## 3. ARCHITECTURE & CONVENTIONS (match these — do not reinvent)

```
PhoenixControl/
  PhoenixControlApp.swift          @main; builds AppState + services, injects into ContentView
  Models/                          AppState (@ObservableObject), *Report structs (Decodable)
  Services/
    ArtifactReader.swift           read-only: loads JSON/JSONL artifacts from repoPath
    GitHubService.swift            GitHub API read; token in Keychain (svc "com.phoenixomega.control")
    ScriptRunner.swift             ObservableObject; runs ALLOWLISTED scripts via Process; redactSecrets()
  Views/                           one SwiftUI View per tab (20 today)
  Views/Components/                StatusBadge, MetricCard, LiveLogView, EvidenceLogTable, ErrorStateView
  Theme/Colors.swift
```

**Adding a tab is a 3-touch pattern** (mirror `contentInventory`):
1. `Views/ContentView.swift` → add a `TabTag` enum case; add it to **all three** switches
   (`title`, `systemImage`, `guidance`) and to the right `sidebarSections` group. (Note: a
   missing `guidance` case is a compile error — "switch must be exhaustive".)
2. `Views/ContentView.swift` detail switch (~line 200+) → `case .yourTab: YourTabView(...)`.
3. Create `Views/YourTabView.swift` **and add it to the Xcode target** — i.e. add 4 lines to
   `PhoenixControl.xcodeproj/project.pbxproj` (PBXBuildFile + PBXFileReference + group child +
   Sources phase), mirroring an existing `E1…/E2…` pair. **A file on disk that is not in the
   pbxproj Sources phase silently fails to compile ("cannot find X in scope") — this exact bug
   shipped once.** Pick unused 24-hex IDs.

**ScriptRunner contract:** `allowedScripts: Set<String>` (top of the file) gates what may run.
`run(scriptRelPath:arguments:...)` spawns `python3 <script> <args>` (or pytest), streams output,
`redactSecrets()` scrubs it, `cancel()` kills. To run a new script you MUST add its repo-rel
path to `allowedScripts`. Runs `python3` from PATH; cwd = repoPath.

**Style:** SwiftUI, `@ObservedObject`/`@State`, async/await for network, `MetricCard`/`StatusBadge`
for tiles, `LiveLogView` for streamed output, `ErrorStateView` for the failure/empty state.

---

## 4. PHASE 1 — Preflight & Drift Runner  *(build first: ~1 day, no new trust boundary)*

A new tab **"Preflight & Gates"** that runs the mandatory checks with block-aware verdicts,
so they can't be skipped before a land. **Read/analysis only — no git writes.** All scripts
below already exist and are verified present.

### 4.1 Add these to `ScriptRunner.allowedScripts`
```
scripts/git/push_guard.py
scripts/ci/preflight_push.sh              # (shell — see 4.4)
scripts/git/health_check.sh               # (shell)
scripts/ci/check_rap_compliance.py
scripts/ci/pr_governance_review.py
scripts/git/disk_guard.py
scripts/run_production_readiness_gates.py
scripts/ci/check_render_progress_bytes.py
scripts/ci/check_manga_story_authored.py
scripts/ci/check_manga_wiring.py
scripts/ci/check_canonical_pipeline_path.py
scripts/ci/check_native_check.py
scripts/ci/check_acceptance_claim_language.py
```

### 4.2 UI — two sections
**A. Mandatory Preflight** (from CLAUDE.md "Mandatory Preflight") — a checklist that runs and
shows PASS / WARN / BLOCK per row:
- `push_guard.py` (env `PYTHONPATH=.`) · `preflight_push.sh` · `health_check.sh` ·
  `check_rap_compliance.py` · `pr_governance_review.py`
- Plus a git status strip: current branch, `git rev-list --left-right --count origin/main...HEAD`.

**B. Drift Detectors** (the "Drift detectors" required-check set — run locally pre-land):
- `check_render_progress_bytes.py` (stub-as-done) · `check_manga_story_authored.py`
  (listing-as-story) · `check_manga_wiring.py` (unwired-config) ·
  `check_canonical_pipeline_path.py` (bestseller four-piece-chord) ·
  `check_native_check.py --bootstrap-mode --json-out <tmp>` (translation native-check) ·
  `check_acceptance_claim_language.py` (claim-language G-CLAIM).

Each row: name, one-line what-it-catches, Run button, streamed output (`LiveLogView`),
verdict badge from **exit code** (0=PASS green; nonzero=BLOCK red; parse "WARN" in output →
amber). A top **"Run all"** button + an overall **"CLEAR TO LAND / BLOCKED"** banner.

### 4.3 Verdict rule
Exit 0 = PASS. Nonzero = BLOCK. If stdout contains `WARN`/`warning` but exit 0 = WARN (amber,
not blocking). **Never** infer PASS from output text alone — trust the exit code. Show the raw
tail so the operator sees *why*.

### 4.4 Shell scripts
`ScriptRunner` runs `python3` today. For the two `.sh` (`preflight_push.sh`, `health_check.sh`)
add a minimal branch: if path ends `.sh`, exec `/bin/bash <path>` instead of `python3 <path>`.
Keep the same allowlist gate + redaction + cwd=repoPath.

### 4.5 Acceptance criteria (Phase 1)
- New "Preflight & Gates" tab appears, all rows run, verdicts reflect real exit codes.
- BUILD SUCCEEDED via §2; app launches; tab is reachable with repo path set.
- No new network calls; no git-write; allowlist is the only execution surface.

---

## 5. PHASE 2 — Offline Landing Studio + armed `OperatorActions` service  *(the prize)*

Turns the manual offline-landing plumbing into a **guarded panel**. This is the app's first
**write** capability → introduce it behind an explicit **Arm** toggle and a dedicated service.

### 5.1 New service `Services/OperatorActions.swift` (write-capable, guardrailed)
Encapsulates git plumbing. Every action is **dry-run-preview first**, then execute only after
the operator confirms. Hard rules baked in (these mirror the CLI discipline — replicate exactly):
- **Base every commit on `origin/main^{tree}`**, never the dirty working tree. Recipe:
  `GIT_INDEX_FILE=<tmp> git read-tree origin/main^{tree}` → for each **explicit path**
  `git hash-object -w <path>` + `git update-index --add --cacheinfo 100644,<blob>,<path>` →
  `git write-tree` → `git commit-tree <tree> -p <base> -m <msg>` → `git update-ref refs/heads/<branch> <new>`.
- **Explicit paths only.** No `git add -A`. The UI is a file-picker of changed paths; nothing
  implicit is ever staged.
- **`GIT_LFS_SKIP_SMUDGE=1`** in the environment for all git ops (LFS repo).
- **Diff-stat gate before push:** compute `git diff --numstat origin/main <new>`. **BLOCK if**
  deletions > 50 files (mass-deletion rule), or total files > 500 (governance), or > 1000
  (push_guard MAX_FILES). Show the stat; require it match the picked paths exactly.
- **Brace all shell vars** in any composed command (`"${VAR}"`), zsh-safe.
- **Push target:** `pearlstar_offline` (remote `pearl_star:~/git/phoenix_omega_offline.git`),
  branch `offline/<slug>-<yyyymmdd>`. SSH `-o ConnectTimeout=8 -o BatchMode=yes`.
- **Verify synced** after push: local `rev-parse` == `pearlstar_offline/<branch>`; surface it.
- **Never** push to `origin` (it's 403 anyway); when GitHub restores this becomes "open PR" —
  leave a TODO seam, don't build PR-create now.

### 5.2 UI — "Offline Landing" tab
1. **Pick paths** (changed-files list from `git status --porcelain`, multi-select).
2. **Branch slug** + commit message fields.
3. **Preview**: shows the exact diff-stat vs origin/main + the governance verdict (green/BLOCK).
4. **Arm** toggle (off by default) — nothing writes until armed.
5. **Land** button (enabled only if armed + gate green): runs the recipe, streams output,
   shows `branch@sha` + synced verdict. Writes a handoff stub under
   `artifacts/coordination/handoffs/` (offline-landed too).
6. Runs **Phase 1 preflight automatically** before allowing Land (compose the two features).

### 5.3 Acceptance criteria (Phase 2)
- Dry-run preview matches a hand-run of the recipe (diff-stat identical).
- Governance caps actually BLOCK (test with a >50-deletion selection → blocked).
- A real small land produces a synced `offline/<slug>` branch; verified `local == remote`.
- Nothing writes while disarmed; `origin` is never a push target.

---

## 6. BACKLOG (spec later; not this pass)

- **Substrate & Replay Ledger** — live GitHub-403 / pearlstar / Qwen-tok-s probes; table of all
  `offline/*` branches with landed/synced/diverged/redundant status; replay queue for 403-clear.
- **Coordination Cockpit + Decisions Inbox** — parse `ACTIVE_WORKSTREAMS.tsv`, 372 handoffs,
  `operator_decisions_log.tsv`; sibling-session collision warnings; scrape `Q-*`/DEFAULT-pending
  into an inbox that appends `operator_decisions_log.tsv` (light write via OperatorActions).
- **Acceptance-Truth panel** — per book/locale true layer + native-check + claim-language + the
  file-existence-vs-authored gap.
- **Pearl Star/GPU monitor** · **Worktree & Disk Guard** (`disk_guard.py`).

---

## 7. LANDING YOUR WORK (offline — GitHub is 403)

Land via the same recipe Phase 2 automates (do it by hand for your own commits):
temp-index off `origin/main^{tree}`, explicit paths only (`PhoenixControl/**` + your handoff),
`GIT_LFS_SKIP_SMUDGE=1`, diff-stat gate, `commit-tree`, `update-ref`, push
`pearlstar_offline offline/pearlprime-<feature>-<yyyymmdd>`, verify `local == remote`. Write a
handoff at `artifacts/coordination/handoffs/pearlprime_<feature>_<date>.md`. Do NOT push origin.
Reference commit from this session: `offline/phoenixcontrol-buildable-fix-20260718@24ef876203`.

## 8. DO-NOT

- No paid LLM API, no telemetry, no network write.
- No `git add -A`; explicit paths only. No push to `origin`.
- Don't edit gate/drift script logic — the app *runs* them, never weakens them.
- Don't add a file to `Views/` without adding it to the pbxproj Sources phase (silent build fail).
- Don't claim done without a §2 BUILD SUCCEEDED + a launch check + an offline `branch@sha`.
```
