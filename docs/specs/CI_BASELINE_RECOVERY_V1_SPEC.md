# CI Baseline Recovery V1 — operator-readable spec

**Project:** `PRJ-CI-BASELINE-RECOVERY-V1`  
**Cap ID:** `CI-BASELINE-RECOVERY-V1-01`  
**Subsystem (primary):** `pearl_devops`  
**Authority:** `docs/GITHUB_OPERATIONS_FRAMEWORK.md`; `docs/GITHUB_GOVERNANCE.md`; `docs/BRANCH_PROTECTION_REQUIREMENTS.md`; `config/governance/required_checks.yaml`; `CLAUDE.md` (mass-deletion rule 0).  
**Baseline commit (discovery):** `465b772186f049fa3ce63453ccdc616bc5d98e23` (`main` at time of Pearl_DevOps discovery, 2026-05-09).  
**Status:** proposed — pending operator answers on §16 (Q1–Q3) and priority pick before workstreams flip to active.

This document is **CAP + scoping only**. No remediation steps are authorized here; implementation lands in follow-up Pearl_DevOps / Pearl_Dev sessions after the cap activates.

---

## 1. Scope

- **In scope:** Per-required-check root cause analysis for **Core tests**, **Release gates**, and **Verify governance** (the three contexts blocking normal merge on `main` without `--admin` bypass). Phased recovery plan with **named workstreams**, acceptance criteria, anti-drift rules, budget, and operator decision card.
- **Out of scope (explicit):** Changing `config/governance/required_checks.yaml` or GitHub rulesets **until** fixes are merged and green on `main`; merging this spec PR with `--admin` except under existing emergency policy; asset generation beyond scoping notes (Pearl_Editor owns cover art policy per workstream); any change to **Workers Builds: pearl-prime** requirement status (remains non-blocking per `required_checks.yaml` unless a separate governance amendment ratifies otherwise).

**Acceptance criteria (program-level):** All contexts listed in `config/governance/required_checks.yaml` as **required** (`Core tests`, `Release gates`, `EI V2 gates`, `Verify governance`) are **green on `main` HEAD** after remediation PRs land; routine PR merges proceed **without** `--admin` solely to bypass failing required checks; branch protection operates as designed (`docs/GITHUB_OPERATIONS_FRAMEWORK.md`).

---

## 2. Per-check root cause analysis

### 2.1 Core tests (required)

| Field | Record |
|--------|--------|
| **Failure run URL (`main` @ `465b772186…`)** | https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/25583091777 |
| **(a) Symptom** | Workflow **Core tests** fails after pytest/smoke steps; **V4.5 Production Readiness** reports **condition 18** failure. |
| **(b) Root cause** | Launchable pen-name authors in registry reference **`cover_art_base`** PNG paths under `assets/authors/cover_art/<author_id>_base.png` that **do not exist** in the repo checkout on CI. Same class of failure as Pearl_GitHub session on PR #974 (log excerpt: `daniel_voss`, `iris_tam`, `kai_okafor`, … `tara_woodfield`). Gate implementation: `scripts/ci/check_author_cover_art.py` (author cover art validation); invoked from production readiness / Core tests pipeline. |
| **(c) Minimal fix scope (scoping only)** | Either: **(c1)** add/regenerate missing PNGs + registry alignment (`config/authoring/author_cover_art_registry.yaml`, `assets/authors/cover_art/*.png`), **or** **(c2)** change gate severity / readiness classification so missing assets **warn** instead of **fail** (requires Pearl_Architect + Pearl_Editor policy alignment — see §16 Q2). Validation: `PYTHONPATH=. python scripts/run_production_readiness_gates.py` locally + Core tests green on `main`. |
| **(d) Effort** | **(c1) L** (bulk assets + LFS/git hygiene). **(c2) S–M** (code + tests + governance note; faster wall-clock, weaker strictness). |
| **(e) Dependencies** | **Verify governance** should be green first so merges are not blocked on a false-positive governance scan while cover-art work proceeds (ordering preference, not hard technical dependency). |

### 2.2 Release gates (required)

| Field | Record |
|--------|--------|
| **Failure run URL on exact `465b772186…`** | **No `Release gates` workflow run** returned from GitHub Actions API for `head_sha=465b772186f049fa3ce63453ccdc616bc5d98e23` (push to `main` did not match `paths:` filters in `.github/workflows/release-gates.yml` — docs-only / out-of-filter paths). |
| **Representative failure URL (same root cause class)** | https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/25582988171 (`main`, `head_sha=10ed203bd667e3890633842f82a2c56972dfa8d5` — prior push touching `config/**`). |
| **(a) Symptom** | Job **Production readiness gates** fails; same **condition 18 — Author cover art** as Core tests. |
| **(b) Root cause** | **Shared with Core tests:** `scripts/run_production_readiness_gates.py` → author cover art gate / `scripts/ci/check_author_cover_art.py` vs missing files under `assets/authors/cover_art/`. |
| **(c) Minimal fix scope** | Same as §2.1(c). After Core tests gate is satisfied, Release gates should re-run on a commit touching `phoenix_v4/**`, `scripts/**`, `config/**`, `atoms/**`, or `.github/workflows/release-gates.yml` per workflow `on.push.paths`. |
| **(d) Effort** | **M** (same remediation as §2.1; additional wall-clock for sim/canary/smoke steps once the shared gate passes). |
| **(e) Dependencies** | Depends on §2.1 resolution; **downstream** steps in `release-gates.yml` (sim analyzer, rigorous system test, canary, smoke) may expose **additional** failures — out of scope for this cap unless they appear after cover-art + governance fixes (then fold under `ws_ci_recovery_release_gates` extension or new amendment). |

### 2.3 Verify governance (required) — GitHub Actions job name **Verify governance**

| Field | Record |
|--------|--------|
| **Failure run URL (`main` @ `465b772186…`)** | https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/25583091776 (workflow file: `.github/workflows/github-governance-check.yml`, job name `Verify governance`). |
| **(a) Symptom** | `PYTHONPATH=. python scripts/ci/verify_github_governance.py --mode local` exits **1**; log line: `FAIL: Bypass logic in check_branch_protection_ruleset.py`. |
| **(b) Root cause** | **False positive from static pattern scan:** `verify_github_governance.py` defines `FORBIDDEN_PATTERNS` including `re.compile(r"bypass_actors", re.I)` (line **29**). `scripts/ci/check_branch_protection_ruleset.py` **legitimately** references the GitHub API field `bypass_actors` when auditing ruleset `13451138` (expected hardened `bypass_mode == "pull_request"`). The scanner flags that substring as “Bypass logic” without exempting the audited ruleset-check script. |
| **(c) Minimal fix scope** | **Single-file or two-file small change (next session):** allowlist `check_branch_protection_ruleset.py` before forbidden-pattern scan, **or** narrow `FORBIDDEN_PATTERNS` to contexts that indicate disabled enforcement (e.g. YAML `enforcement: disabled`) without banning API field names in audited scripts. Add/adjust a unit or self-check so governance does not regress. Files: `scripts/ci/verify_github_governance.py` (primary); optionally `scripts/ci/check_branch_protection_ruleset.py` only if rename/doc clarity is chosen. |
| **(d) Effort** | **S** (low line count; high leverage — unblocks Verify governance on all PRs). |
| **(e) Dependencies** | **None** upstream. Should be **Phase 1** so operators stop needing `--admin` for governance false positives while cover-art recovery proceeds. |

---

## 3. Phased fix plan (named workstreams)

| Phase | Goal | Primary workstream | Owner agents |
|-------|------|---------------------|--------------|
| **Phase 1** | Restore **Verify governance** to green on `main` by eliminating the false positive on `check_branch_protection_ruleset.py`. | `ws_ci_recovery_verify_governance_bypass` | Pearl_DevOps |
| **Phase 2** | Restore **Core tests** production-readiness **condition 18** (author cover art) via assets **or** gate-severity policy per operator Q2. | `ws_ci_recovery_core_tests_cover_art` | Pearl_DevOps + Pearl_Editor |
| **Phase 3** | Confirm **Release gates** full job (readiness + sim + rigorous + canary + smoke) green on `main` after Phase 2; address any newly surfaced failures inside the same project or amendment. | `ws_ci_recovery_release_gates` | Pearl_DevOps |
| **Phase 4 (acceptance)** | Record green required-check snapshot on `main`, archive evidence in audit markdown, confirm routine PR merge **without** `--admin` for required-check bypass; update coordination TSV statuses. | `ws_ci_recovery_acceptance` | Pearl_DevOps |

**Default sequencing:** Phase **1 → 2 → 3 → 4**. Operator may reorder **2 vs 1** only if policy explicitly accepts temporary governance `--admin` during cover-art firefight (not recommended).

---

## 4. Anti-drift

1. **`--admin` merge trail:** Every historical `--admin` merge remains in GitHub + coordination audit trail; **no history rewrite**, no silent deletion of merge receipts.
2. **Post-recovery posture:** After baseline green, **`--admin`** merges are reserved for **true emergencies** only — each use requires **operator-level explicit justification** recorded (PR comment or incident doc).
3. **New required checks:** Any new name appended to `config/governance/required_checks.yaml` MUST be **green on `main` as an opt-in / non-required check first** where feasible, then promoted to required after stability window (prefer PR-check soak → ruleset update).
4. **Cover art / asset gates:** Long-term posture (Pearl_Editor follow-up): gates **must not block CI on missing author PNGs** indefinitely — prefer **WARN** + dashboard over **FAIL**, once catalog readiness model is ratified (ties to §16 Q2).

---

## 5. Action items (workstreams)

| workstream_id | Status (now) | Task summary |
|----------------|--------------|--------------|
| `ws_ci_recovery_verify_governance_bypass` | proposed | Patch `verify_github_governance.py` allowlist / pattern scope; verify `Verify governance` green on `main`. |
| `ws_ci_recovery_core_tests_cover_art` | proposed | Resolve condition 18: missing `assets/authors/cover_art/*_base.png` vs registry; or gate warn-not-fail per policy. |
| `ws_ci_recovery_release_gates` | proposed | Re-run full Release gates path-filtered workflow; fix any failures after shared readiness gate is green. |
| `ws_ci_recovery_acceptance` | proposed | Phase 4: capture `gh` check snapshot + URLs; write `artifacts/audit/ci_baseline_recovery_acceptance_YYYY-MM-DD.md`; confirm no routine `--admin` for required checks. |

---

## 6. Budget

- **Tier 1 (operator-present):** Cap ratification, sequencing decisions (§16), and sign-off on Phase 4 evidence.
- **Tier 2 (unattended):** Allowed for scripted asset batch generation / long CI reruns **after** policy locked in §16 Q2.

---

## 7. Status + operator decision card

**Cap status:** `CI-BASELINE-RECOVERY-V1-01` = **proposed** — pending operator priority pick and §16 answers.

### Operator decision card (verbatim — record answers in PR comment or amend this §16)

**Q1:** Approve the phased plan **as proposed** (Phase 1 → 2 → 3 → acceptance), **or** specify a reorder (e.g. cover-art before governance patch) with rationale.

**Q2:** For the author cover art gate — **(A)** add missing PNGs / strict registry compliance (preserves fail-hard), **or** **(B)** relax gate to **warn-not-fail** for missing assets (faster; accepts gaps as warnings until Pearl_Editor fills assets).

**Q3:** Acceptance threshold — **(A)** all **required** checks green on `main` = pass, **or** **(B)** additionally require **Workers Builds: pearl-prime** green even though it is currently **non-blocking** in `required_checks.yaml`.

---

## Cross-reference

- Coordination: `artifacts/coordination/ACTIVE_PROJECTS.tsv` (`PRJ-CI-BASELINE-RECOVERY-V1`), `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (four `ws_ci_recovery_*` rows).
- Architect cap entry: `docs/PEARL_ARCHITECT_STATE.md` (`CI-BASELINE-RECOVERY-V1-01`).

---

## Phase 2 — cover_art gate relaxation (detail; ratified 2026-05-10)

**Problem anchor:** §2.1 / §2.2 — **condition 18** fails **Core tests** (and **Release gates** when path filters match) when launchable authors reference **`cover_art_base`** paths under `assets/authors/cover_art/<author_id>_base.png` that are absent on the CI checkout.

**Q2 decision (ratified):** Operator selects **§16 Q2 option (B)** — **relax-to-warn**: missing files remain visible (non-silent) but **do not fail** the author cover art gate / readiness classification that currently hard-fails Core tests. Strict asset compliance **(§16 Q2 option A)** is **not** the chosen path for Phase 2 recovery.

**Documentation vs implementation:** This section ratifies **policy and sequencing** only. The follow-up implementation PR adjusts `scripts/ci/check_author_cover_art.py` and any production-readiness mapping in `scripts/run_production_readiness_gates.py` (and tests) so missing PNGs emit **WARN** and Core tests can pass. That code change is **out of scope** for the cap-amendment documentation PR and is owned under workstream **`ws_ci_recovery_phase_2_impl_20260510`**.

**Pearl_Editor coupling:** WARN posture does not remove the obligation to backfill or regenerate assets per editorial/catalog plans; it only removes **CI hard-block** for the missing-file class while recovery proceeds.

**Acceptance hint for implementation PR:** `PYTHONPATH=. python scripts/run_production_readiness_gates.py` (and Core tests workflow) **green on `main`** with intentional missing asset fixtures producing **warnings**, not condition-18 **fail**, unless a separate strict mode is later ratified.

**Workstream split:** **`ws_ci_recovery_core_tests_cover_art`** — umbrella Phase 2 lane (verification + handoff toward Release gates). **`ws_ci_recovery_phase_2_impl_20260510`** — concrete gate-relaxation implementation PR.

**Implementation (code):** `scripts/ci/check_author_cover_art.py` — default **warn** (PR #1006 / §16 Q2); missing on-disk `cover_art_base` emits **`::warning::`** on stderr and exits **0**; **`COVER_ART_GATE_MODE=fail`** or **`--gate-mode fail`** restores strict fail-hard. Tests: `tests/ci/test_check_author_cover_art_warn_mode.py`. Operator smoke log: `artifacts/qa/ci_recovery_phase_2_cover_art_warn_impl_2026-05-10.md`.

---

## Phase 2.5 — Core tests pytest dependency gap (post-#1011 still-red; diagnosed 2026-05-10)

**Evidence:** GitHub Actions run **25614516443** on `main` @ **`805f62947d01c29820860785b8abce9d6a5f2c61`** — workflow **Core tests**, step **Run fast/core pytest**, fails during collection with **`ModuleNotFoundError: No module named 'fastapi'`** importing `brand-wizard-app/server/music_survey_routes.py` from `tests/brand_wizard/test_music_survey_save_handler.py`.

**Why Phase 2 did not green Core tests:** Phase 2 relaxed **Gate 18 (author cover art)** only. Core tests runs **pytest before** `scripts/run_production_readiness_gates.py`; the failure occurs **before** any cover_art gate executes.

**Recommended remediation (implementation PR, not this spec):** Extend **`requirements-test.txt`** with **`fastapi`** (minimal alignment; see proposed diff in `artifacts/qa/ci_recovery_phase_2_core_tests_diagnostic_2026-05-10.md`). **Workstream:** `ws_ci_recovery_phase_2_5_core_tests_brand_wizard_deps`. **Effort:** **S**.

**Workflow env note:** `COVER_ART_GATE_MODE` is **not** set in `.github/workflows/*.yml`; default **warn** in `check_author_cover_art.py` remains sufficient **once pytest passes**. No workflow-only fix is indicated for cover_art for this failure mode.

---

## Phase 2.6 — TestClient dependency closure (deps; diagnostic 2026-05-10)

**Problem anchor:** After Phase 2.5 added **`fastapi`** to **`requirements-test.txt`**, **Core tests** (`.github/workflows/core-tests.yml`) still failed on **`tests/test_server_health.py`** collection: **`starlette.testclient`** requires **`httpx`**, which was **not** installed by that workflow.

**Why Phase 2.5 was incomplete:** **`fastapi`** alone does not install **`httpx`** in the minimal CI pin path; **`TestClient`** is the next import and fails without **`httpx`**.

**Policy / sequencing (this spec):** Treat **Phase 2.6** as a small **test dependency closure** under the same recovery program — align **`requirements-test.txt`** (preferred) or **`core-tests.yml`** with the stack already implied by **`server-ci.yml`** (`pip install httpx`).

**Documentation vs implementation:** Evidence and recommendation: **`artifacts/qa/ci_recovery_phase_2_6_diagnostic_2026-05-10.md`**. Implementation (add **`httpx`** to test requirements or workflow) is a **separate** code PR — not merged via this diagnostic-only lane.
