# CI Baseline Recovery V1 — Phase 4 acceptance audit

**Project:** `PRJ-CI-BASELINE-RECOVERY-V1`  
**Cap:** `CI-BASELINE-RECOVERY-V1-01`  
**Workstream:** `ws_ci_recovery_acceptance`  
**Agent:** Pearl_DevOps  
**Audit date:** 2026-05-27  
**`main` HEAD verified:** `15b46e37a29d5a6349e0d0cfa1a189f6ba1abc18` (PR #1325)  
**Verdict:** **PARTIAL**

---

## Executive summary

| Dimension | Result |
|-----------|--------|
| **Ruleset-required merge gate** (`Verify governance`, ruleset `13451138`) | **PASS** — green on `main` HEAD and on the last 3 merged PRs; no merge-commit evidence of `--admin` to bypass a failing `Verify governance` |
| **Core tests** (contract in `required_checks.yaml`) | **PASS on `main` HEAD** — success at `15b46e37a` |
| **Release gates** (contract) | **FAIL on `main` HEAD** — [run 26464229825](https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/26464229825); Phase 3 remains (`ws_ci_recovery_release_gates`) |
| **Workers Builds: pearl-prime** (non-blocking per OPD-153) | **FAIL** (expected accepted noise) |
| **Routine `--admin` for required-check bypass** | **Not observed** on last 15 merges (all merged with `Verify governance` = success on merge commit) |

**PARTIAL rationale:** Acceptance criteria for **ruleset merge hygiene** and **Phase 1–2 recovery PRs** are met; **Release gates** on `main` are still red; **Workers Builds** remains non-required flapping per OPD-153.

---

## A. Last 15 merged PRs on `main`

Source: `gh pr list --state merged --base main --limit 15` + per-merge-commit check-runs API (`2026-05-27`).

| PR | Title (short) | Merge SHA | Merged (UTC) | Verify governance | Core tests | Release gates | Workers Builds | `--admin` for required? |
|----|---------------|-----------|--------------|-------------------|------------|---------------|----------------|-------------------------|
| [#1325](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1325) | preflight OPD-max hint (#1325) | `15b46e37` | 2026-05-26T17:27:47Z | success | success | failure | failure | no |
| [#1324](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1324) | ep_002 scene_inventory | `be988aa8` | 2026-05-26T17:16:18Z | success | success | failure | failure | no |
| [#1323](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1323) | OPD-145 split-at-build | `29c1f261` | 2026-05-26T15:54:25Z | success | success | — (not run) | failure | no |
| [#1322](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1322) | OPDs 145-150 + PR template checkbox | `c2e83b37` | 2026-05-26T16:51:14Z | success | success | failure | failure | no |
| [#1320](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1320) | BR-CANON-02 cap entry | `a3d0f436` | 2026-05-26T15:46:11Z | success | success | — | failure | no |
| [#1318](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1318) | CI cascade + ep_002 brief + Milestone H | `aca845e3` | 2026-05-26T14:57:27Z | success | success | — | failure | no |
| [#1316](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1316) | ep_002 beatsheet draft | `cd65f7c2` | 2026-05-26T16:34:14Z | success | success | — | failure | no |
| [#1315](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1315) | brand_admin_v2 hub link | `fc795cae` | 2026-05-26T15:52:46Z | success | success | — | failure | no |
| [#1312](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1312) | weekly_packages seed W22 | `03914d36` | 2026-05-26T14:06:05Z | success | **failure** | failure | failure | no |
| [#1310](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1310) | continuity_state generator | `f992eef0` | 2026-05-26T16:13:26Z | success | success | failure | failure | no |
| [#1309](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1309) | open 4 follow-up ws (#1305) | `c1fa2c8a` | 2026-05-26T14:02:07Z | success | **failure** | — | failure | no |
| [#1307](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1307) | ep_001 beatsheet Step 0 | `8794601a` | 2026-05-26T16:04:07Z | success | success | — | failure | no |
| [#1305](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1305) | brand-admin v2 weekly-work | `182c9658` | 2026-05-26T14:05:53Z | success | **failure** | — | failure | no |
| [#1296](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1296) | live 3-axis brand index | `dbeb40e0` | 2026-05-26T14:02:15Z | success | **failure** | — | failure | no |
| [#1290](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1290) | V5.1 catalog rollout plan | `22326ace` | 2026-05-26T16:03:55Z | success | success | failure | failure | no |

**`--admin` bypass column:** Ruleset `13451138` requires only **`Verify governance`**. A PR merged with `Verify governance` = **failure** on its merge commit would imply `--admin` (or ruleset bypass). **None** of the 15 rows show that pattern. Several PRs merged with **Core tests** = failure (#1296, #1305, #1309, #1312), confirming **Core tests is not ruleset-enforced** (contract vs live ruleset drift documented in `config/governance/required_checks.yaml` vs ruleset).

**Last 3 PRs (#1325, #1324, #1323):** `Verify governance` = success on all three → **PASS** per acceptance card for ruleset merge path without `--admin`.

---

## B. Branch protection / ruleset state

Legacy endpoint `GET .../branches/main/protection/required_status_checks` → **404 Branch not protected** (expected; protection is ruleset-based).

**Ruleset `13451138` — "Protect main"** (`GET .../rulesets/13451138`):

| Field | Value |
|-------|-------|
| `enforcement` | `active` |
| `required_status_checks` | **`["Verify governance"]` only** |
| `strict_required_status_checks_policy` | `false` |
| `bypass_actors` | Repository role, `bypass_mode: pull_request` |

**Confirmation:** Live GitHub enforcement matches operator intent documented post-recovery — only **Verify governance** blocks merge; **Core tests**, **Release gates**, **EI V2 gates** remain contract-listed in `config/governance/required_checks.yaml` but are **not** currently in the active ruleset required list.

---

## C. `main` HEAD gate snapshot (`15b46e37a`)

| Check | Conclusion | Notes |
|-------|------------|-------|
| Verify governance | **success** | [run 26464229717](https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/26464229717) |
| Core tests | **success** | [run 26464229718](https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/26464229718) |
| Release gates | **failure** | [run 26464229825](https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/26464229825) |
| EI V2 gates | — | No check-run on this commit (path-filter / not triggered) |
| Workers Builds: pearl-prime | **failure** | Non-blocking per `required_checks.yaml` + OPD-153 |

---

## D. Phase recovery PR evidence

| Phase | PR | Merge SHA | Verify governance | Core tests | Notes |
|-------|-----|-----------|-------------------|------------|-------|
| **1 — governance false positive** | [#997](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/997) | `b4c16dcb` | success | failure at merge | Phase 1 landed; merge-time Core red pre–Phase 2 |
| **2 — cover_art policy (Q2 warn)** | [#1006](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1006) | `7c34e3c5` | success | failure at merge | Policy ratification doc-only lane |
| **2 — cover_art WARN impl** | [#1011](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1011) | `805f6294` | success | failure at merge | `check_author_cover_art.py` default warn; Core later green on main after Phase 2.5/2.6 deps |

---

## E. Operator decisions & follow-ups

### OPD-152 — cascade-prevention (PR template)

- **Row:** `OPD-152` in `artifacts/coordination/operator_decisions_log.tsv`
- **Evidence:** `.github/pull_request_template.md` checkbox — planner/composer signal changes must update test assertions in the same commit (landed PR #1322 / #1318 chain).

### OPD-153 — Workers Builds reclassification

- **Row:** `OPD-153` (2026-05-27)
- **Evidence:** `artifacts/audits/workers_builds_pearl_prime_audit_2026-04-27.md`; `non_blocking_checks` in `config/governance/required_checks.yaml`; all 15 recent merges show **Workers Builds: pearl-prime** = failure without blocking merge.

### PR #1325 — preflight OPD-max hint

- **Change:** `scripts/ci/preflight_push.sh` lines 7–13 — informational max OPD from `origin/main:artifacts/coordination/operator_decisions_log.tsv`
- **Motivation:** OPD numbering collision cascade (OPD-152 follow-up); merged as #1325 at `15b46e37a`

---

## F. Verdict matrix (acceptance card)

| Criterion | Result |
|-----------|--------|
| Last 3 PRs green on **Verify governance** without `--admin` | **PASS** |
| **Workers Builds** non-required flapping (OPD-153) | **PARTIAL** (expected) |
| **Core tests** green on `main` HEAD | **PASS** |
| **Release gates** green on `main` HEAD | **FAIL** → Phase 3 (`ws_ci_recovery_release_gates`) |
| Required check failed on last 3 PRs (**ruleset** = Verify governance only) | **PASS** (none failed) |

**Overall: PARTIAL** — close **Phase 4 acceptance** and **project** for ruleset/`--admin` recovery; keep **`ws_ci_recovery_release_gates`** runnable for Release gates green on `main`.

---

## G. Phase 3 scope (if pursuing full yaml-contract green)

1. Triage [Release gates run 26464229825](https://github.com/Ahjan108/phoenix_omega_v4.8/actions/runs/26464229825) on `15b46e37a` — failure beyond condition 18 (cover_art WARN per #1011).
2. Execute `ws_ci_recovery_release_gates` — sim / rigorous / canary / smoke per `docs/specs/CI_BASELINE_RECOVERY_V1_SPEC.md` §2.2.
3. Optional operator action: Cloudflare dashboard disconnect pearl-prime GitHub watcher (OPD-153 Path A1) to remove UI noise.

---

*Generated by Pearl_DevOps `ws_ci_recovery_acceptance` close-out.*
