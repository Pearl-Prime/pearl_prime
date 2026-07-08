# Canonical Artifacts Registry + Reinvention Guard — V1 Spec

**Status:** PROPOSED (ratified by cap `CANONICAL-ARTIFACTS-REGISTRY-V1-01`, **ACTIVE**, 2026-06-12)
**Owner:** Pearl_Architect (spec) · Pearl_GitHub (registry data) · Pearl_Dev (guard build, Phase 2)
**Subsystem:** `pearl_devops` (the guard) + `integrations` (the registry sweep)
**Authority docs it extends:** `docs/GITHUB_GOVERNANCE.md`, `docs/PEARL_ARCHITECT_STATE.md` (known-good anchors registry), `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`, `docs/DOCS_INDEX.md`
**Phase:** This is a **Phase-1 governance + spec document only.** It DESCRIBES the registry schema, the override protocol, and the guard algorithm. It does **not** ship any `.py` engine, generator, or resolver. The guard's `check_reinvention()` function is BUILT in a Phase-2 workstream (`ws_pearl_dev_reinvention_guard_extension_20260612`).

---

## 0. Purpose — the anti-reinvention problem

Phoenix Omega has a recurring, expensive failure mode: an agent that needs capability X **greenfields a brand-new X** instead of editing the X that already exists. The repo then carries two parallel implementations that drift apart. Historical examples this registry is designed to prevent:

- A second Pearl News assembler appearing alongside `pearl_news/pipeline/assemble_v52.py`.
- A new bestseller CLI alongside `scripts/run_pipeline.py`.
- A fresh manga brand list alongside `config/manga/canonical_brand_list.yaml`.
- The teacher-photo overwrite drift documented in the known-good anchors registry (PR #773 clobbered `teacher_pics/` at 800×1000; restore SHA `c513ac18d`).

The fix is a **three-layer anti-reinvention system** that makes "edit the canonical artifact" the path of least resistance and makes "author a new one" a deliberate, justified, reviewed act.

This spec is **reuse-not-greenfield by construction**: it does not replace the known-good anchors registry in `PEARL_ARCHITECT_STATE.md` or `SUBSYSTEM_AUTHORITY_MAP.tsv`. It **promotes** the highest-confidence facts from those into a single machine-readable lookup, and cross-links back to the prose sources for context.

---

## 1. The three-layer model

| Layer | Mechanism | Surface | This spec's deliverable |
|---|---|---|---|
| **Layer 1 — Reflex** | Router principle 9 "Reuse before authoring" in `docs/agent_brief.txt` | Every prompt the router emits inherits the reflex | New §9 inserted between §8 and `## Revert` |
| **Layer 2 — Registry** | `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` (9-col TSV) | A lookup an agent (or the guard) consults before creating a file | The registry file + seed rows |
| **Layer 3 — Guard** | `check_reinvention()` extending `scripts/ci/pr_governance_review.py` | A PR check that flags likely reinventions | This spec DESCRIBES it; Phase-2 ws BUILDS it |

The three layers are defence-in-depth: Layer 1 catches the reflex at authoring time, Layer 2 gives the agent (and the guard) ground truth, Layer 3 catches anything the first two missed at PR time.

### 1.1 Why Layer 1 cites the registry "when present"

Principle 9 is authored in the SAME PR as the registry (the prompt explicitly couples them). It cites the registry **"when present"** so the brief stays valid even on branches/checkouts where the registry file has not yet landed — the reflex ("check whether a canonical artifact already exists before authoring a new one") is always correct; the specific lookup file is a convenience that may or may not be on a given ref.

---

## 2. The registry schema (11 columns, TAB-separated, LF line endings)

File: `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`

| # | Column | Meaning | Example |
|---|---|---|---|
| 1 | `concept_key` | Stable snake_case identity of the *capability*, not the file. The thing an agent is tempted to reinvent. | `pearl_news_sidebar` |
| 2 | `canonical_path` | The ONE path that owns this capability. Full repo-relative path (file or dir with trailing `/`). | `pearl_news/pipeline/assemble_v52.py` |
| 3 | `sha_or_pr` | Provenance anchor: short SHA and/or `PR#NNN`. Where the canonical version landed / was last known good. | `PR#853 8070e81fd` |
| 4 | `owner_agent` | The Pearl_* agent that owns edits to this artifact. | `Pearl_News` |
| 5 | `subsystem` | Subsystem id from `SUBSYSTEM_AUTHORITY_MAP.tsv` (cross-link key). | `pearl_news` |
| 6 | `edit_not_recreate` | `YES` = always edit in place. `NO-without-ratification` = a new variant needs a cap-entry / operator ratification first. | `YES` |
| 7 | `last_verified` | ISO date the canonical_path + sha_or_pr were last confirmed correct. | `2026-06-12` |
| 8 | `supersedes` | Older path(s) this canonical replaced, `;`-joined, or `-` if none. Helps catch "you edited the dead one." | `-` |
| 9 | `notes` | Free text: drift history, mirror paths, gotchas. | `drift = PR#773 manga overwrite 800x1000; restore both mirrors` |
| 10 | `research_refs` | **§18 provenance.** Research artifact(s)/claim-id(s) the capability rests on (`;`-joined paths under `pearl_research/`, `artifacts/research/`, `docs/research/`), or `UNKNOWN-BACKFILL` where genuinely untraceable (honest, never invented). | `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md` |
| 11 | `doc_refs` | **§18 provenance.** The governing spec / authority doc(s) that define the capability (`;`-joined), or `UNKNOWN-BACKFILL`. Backfilled best-effort from `SUBSYSTEM_AUTHORITY_MAP.tsv` + self-referencing spec rows. | `docs/PEARL_NEWS_WRITER_SPEC.md` |

Columns 10–11 encode the **research → documents → code** provenance chain of `docs/agent_brief.txt` §18. They were added by the provenance-tracer PR (2026-07-09) and backfilled deterministically: `doc_refs` from the row's subsystem authority docs (or the row's own path when it *is* a spec/authority doc); `research_refs` from any research-dir path in those docs / the canonical path itself, else `UNKNOWN-BACKFILL`. The `load_canonical_registry()` loader reads them via `DictReader`, so a ref predating this PR (10-or-fewer columns) yields `""` and never crashes (fail-open).

**Header row (verbatim, single TAB between columns):**

```
concept_key	canonical_path	sha_or_pr	owner_agent	subsystem	edit_not_recreate	last_verified	supersedes	notes	research_refs	doc_refs
```

### 2.1 `edit_not_recreate` semantics

- `YES` — the artifact is a singleton; agents EDIT it, never fork it. The guard treats a *new* file whose normalized path collides with (or is a sibling basename of) a `YES` row's `canonical_path` as a high-signal WARN.
- `NO-without-ratification` — a new variant is permitted **only** after a `PEARL_ARCHITECT_STATE.md` cap entry or operator ratification authorises it (e.g. `config/manga/canonical_brand_list.yaml` may not be re-authored without a ratification, because brand-canon changes ripple through the whole manga catalog).

---

## 3. Seed rows (high-confidence; full sweep deferred)

The registry ships seeded with ~6-10 rows the orchestrator already trusts (promoted from the known-good anchors registry + `SUBSYSTEM_AUTHORITY_MAP.tsv`). A **full sweep** of all canonical artifacts is explicitly **deferred to a child workstream** (`ws_pearl_github_canonical_registry_full_seed_sweep_20260612`) per the SCOPE default — we do not block this spec on enumerating every artifact in the repo. Each seeded row was verified to exist on `origin/main` at authoring time (2026-06-12).

The seed set (see the `.tsv` deliverable for exact rows):

1. `pearl_news_sidebar` → `pearl_news/pipeline/assemble_v52.py` (PR#853 8070e81fd, Pearl_News, `pearl_news`, `YES`)
2. `pearl_prime_bestseller_cli` → `scripts/run_pipeline.py` (PR#669 cbfbe14c3 / #939, Pearl_Prime, `pearl_prime`, `YES`)
3. `manga_brand_canon` → `config/manga/canonical_brand_list.yaml` (PR#722 9205b2307, Pearl_Dev, `manga_pipeline`, `NO-without-ratification`)
4. `teacher_real_photos` → `teacher_pics/` + `brand-wizard-app/public/teacher_pics/` (c513ac18d, Pearl_Brand, `dashboard`, `YES`) — two mirrors, both restored together
5. `manga_v2_model_arch` → `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (PR#924 ec46a7223, Pearl_Dev, `manga_pipeline`, `NO-without-ratification`)
6. `subsystem_authority_map` → `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` (Pearl_PM, governance, `YES`) — the map itself is a canonical artifact
7. `llm_policy_enforcement` → `.github/workflows/llm-policy-enforcement.yml` (Pearl_DevOps, `pearl_devops`, `YES`)
8. `docs_index` → `docs/DOCS_INDEX.md` (Pearl_PM, governance, `YES`)

(Authority-doc rows 6-8 are drawn from `SUBSYSTEM_AUTHORITY_MAP.tsv` / repo governance and self-evidently exist.)

---

## 4. The reinvention guard (Layer 3) — algorithm DESCRIPTION (Phase-2 build)

The guard is a new check function `check_reinvention(files, registry)` added to `scripts/ci/pr_governance_review.py`, registered in `main()`'s `results = [...]` list alongside the existing six checks (`check_mass_deletion`, `check_pr_size`, `check_subsystem_scope`, `check_authority_docs`, `check_drift_patterns`, `check_workstream_conflict`). It reuses the existing loader pattern: a new `load_canonical_registry()` mirroring `load_subsystem_map()` / `load_active_workstreams()` (TSV `DictReader`, returns `[]` if the file is absent — fail-open, never crash a PR because the registry is missing on that ref).

The guard has **two arms**:

### 4.1 Path-match arm (deterministic — SHIPS FIRST, Phase-2)

For each **added** file (`status == "A"`) in the PR diff:

1. Normalize its path (strip leading `./`, collapse `//`, lowercase-fold for comparison only — store original for the message).
2. Compare against every registry row's normalized `canonical_path` using **full normalized canonical_path matching** (NOT bare basename). Rationale (MATCH-ALGO default): bare-basename matching produces false positives on ubiquitous filenames like `CANONICAL.txt`, `README.md`, `config.yaml`; full-path normalization avoids them.
3. A match fires when the added file is:
   - byte-identical normalized path to a `canonical_path` that is being **added** rather than modified (i.e. the canonical was deleted+re-added, or a duplicate landed at the same path on a parallel branch), **or**
   - a same-directory sibling whose basename equals the canonical's basename under a different parent (e.g. `pearl_news/v2/assemble_v52.py` vs canonical `pearl_news/pipeline/assemble_v52.py`) — a likely fork.
4. On a `YES` row → **WARN** with: the added path, the canonical path it likely duplicates, the owner agent, and the remediation ("edit the canonical artifact, or add the `NEW-ARTIFACT-JUSTIFIED:` override + a registry row in this same PR").
5. On a `NO-without-ratification` row → **WARN** additionally noting that a cap-entry / operator ratification is required before a new variant is permitted.

This arm is **fully deterministic** (string matching only — no model, no network), which is why it ships first.

### 4.2 Content-overlap arm (semantic — FLAGGED FOR PHASE 2, Tier-2-local ONLY)

A stronger arm compares the *content* of an added file against registry canonical files to catch reinventions that landed at a **different** path with a **different** filename but the **same capability**.

**Hard constraint (LLM Tier policy + `.github/workflows/llm-policy-enforcement.yml`):** this arm MUST use a **local / Tier-2 embedding model** (Gemma/Qwen via Ollama on Pearl Star `:11434`, per `config/governance/allowed_llm_patterns.yaml`). It **MUST NOT** call any paid LLM API (`ANTHROPIC_API_KEY`, OpenAI cloud, Google AI, DashScope cloud, etc.). A guard that phones a paid API would itself be blocked by the LLM-policy enforcement workflow — and would be the exact kind of governance hypocrisy this repo forbids.

Algorithm sketch (to be built in Phase 2, NOT in this spec):
1. Embed the added file's content and each candidate canonical file's content with a local embedding model served by Ollama.
2. Cosine-similarity ≥ **0.80** (OVERLAP-THRESHOLD default) → **WARN** "added file <X> is N% similar to canonical <Y>; likely a reinvention."
3. Scope candidates by subsystem (only compare against canonicals in the same/adjacent subsystem) to keep it cheap and offline-fast.

This arm is **descriptive only** in Phase 1. The Phase-2 ws decides the exact local model, batching, and caching. **No embedding code is authored here.**

### 4.3 Severity — WARN-only in Phase 1

Per the SEVERITY default, `check_reinvention()` emits **WARN, never BLOCKED**, in its first iteration. It surfaces likely reinventions for human judgment without blocking merges (a false-positive block on a legitimately-new artifact would be worse than a missed reinvention). Promotion to BLOCKED for `NO-without-ratification` rows is a deferred follow-up, gated on false-positive-rate data from real PRs.

---

## 5. Override protocol — `NEW-ARTIFACT-JUSTIFIED`

Sometimes a genuinely-new artifact is correct (a real new capability, not a fork). To author one without the guard nagging:

1. Add the tag **`NEW-ARTIFACT-JUSTIFIED: <reason>`** to the PR description (or the commit body).
2. In the **same PR**, add a row to `CANONICAL_ARTIFACTS_REGISTRY.tsv` for the new canonical artifact (so the next agent finds it and does not re-reinvent *it*).
3. For a path that collides with a `NO-without-ratification` row, the override additionally requires a `PEARL_ARCHITECT_STATE.md` cap-entry or operator ratification (the override tag alone is insufficient).

The guard, when it sees the `NEW-ARTIFACT-JUSTIFIED:` tag, downgrades its WARN to an INFO acknowledging the justification (Phase-2 behavior; described here for completeness).

An **allowlist** file — `config/governance/reinvention_allowlist.yaml` — provides a standing, reviewed exception channel for paths that legitimately mirror a canonical (e.g. the `brand-wizard-app/public/teacher_pics/` mirror of `teacher_pics/`). It ships **empty** (schema-only) in Phase 1; entries are added under review.

---

## 6. Ratified Q-CAR defaults (this cap's decisions)

| Q-ID | Axis | Ratified default |
|---|---|---|
| Q-CAR-SEVERITY | Guard severity Phase 1 | **WARN-only** — no BLOCKED until false-positive data exists |
| Q-CAR-SCOPE | Initial registry coverage | **Seed ~6-10 high-confidence rows now**; full sweep deferred to `ws_pearl_github_canonical_registry_full_seed_sweep_20260612` |
| Q-CAR-OVERLAP-THRESHOLD | Content-overlap similarity cut | **0.80**, computed with a **local / Tier-2** embedding model (Ollama); **path-match arm ships first** |
| Q-CAR-OVERRIDE-TAG | Escape hatch | **`NEW-ARTIFACT-JUSTIFIED: <reason>`** in PR body **+ a registry row in the same PR** |
| Q-CAR-VERIFY-CADENCE | `last_verified` refresh | **Opportunistic** (whenever an agent touches a canonical) **+ quarterly** sweep |
| Q-CAR-MATCH-ALGO | Path comparison | **Full normalized `canonical_path`** (NOT bare basename — avoids `CANONICAL.txt` / `README.md` false positives) |
| Q-CAR-LAYER1-COUPLING | Principle 9 timing | **Author §9 in THIS spec's PR** (Layer 1 cites the registry "when present") |

All seven are **in-envelope** governance-mechanism decisions (no legal/financial/brand-identity call) and are logged to `operator_decisions_log.tsv` under one OPD row.

---

## 7. Relationship to existing governance (no duplication)

- **Known-good anchors registry** (`PEARL_ARCHITECT_STATE.md`): remains the **prose source of truth** for drift history and per-subsystem anchors. The registry TSV **promotes** its highest-confidence facts into a machine-readable lookup; it does not replace the prose. When the two disagree, the prose anchors registry wins and the TSV row's `last_verified` is refreshed.
- **`SUBSYSTEM_AUTHORITY_MAP.tsv`**: owns the *subsystem → authority-doc → owner* mapping at the **directory** level. The Canonical Artifacts Registry operates at the **specific-file** level (the ONE file that owns a capability). The `subsystem` column is the cross-link key. No overlap in granularity.
- **`DOCS_INDEX.md`**: the human index of docs. Authority-doc rows in the registry (`docs_index`, `subsystem_authority_map`) point back to it. The registry does not duplicate the doc index; it records which doc files are canonical singletons.
- **`pr_governance_review.py`**: the registry adds ONE check (`check_reinvention`) to the existing six. It does not fork or rewrite the script — it extends it, reusing the established loader + `results=[...]` pattern. (Reuse-not-greenfield applies to the guard itself.)

---

## 8. Out of scope for Phase 1 (Phase-2 / follow-up)

- The `check_reinvention()` `.py` implementation (built by `ws_pearl_dev_reinvention_guard_extension_20260612`).
- The content-overlap embedding pipeline (Tier-2-local).
- Promotion of any WARN to BLOCKED.
- The full-repo canonical-artifact sweep (built by `ws_pearl_github_canonical_registry_full_seed_sweep_20260612`).
- Auto-population of `last_verified` from git history.

---

## 9. Anti-drift self-check

- No implementation code in this spec — it DESCRIBES the guard; a Phase-2 ws BUILDS it.
- No paid LLM API anywhere — content-overlap arm is Tier-2-local (Ollama Gemma/Qwen) by hard constraint.
- Reuse-not-greenfield — extends `pr_governance_review.py`, promotes (does not replace) the known-good anchors registry + `SUBSYSTEM_AUTHORITY_MAP.tsv`.
- Every seed row's `canonical_path` was verified to exist on `origin/main` at authoring (2026-06-12).

---

## 10. The §18 provenance tracer (research → documents → code + no-lost-functions)

Added by the provenance-tracer PR (2026-07-09), enforcing `docs/agent_brief.txt` §18. This
is the machine form of "everything descends from research, through documents, into code —
and old functions survive new features." It EXTENDS the machinery this spec already owns; it
does not add a parallel system.

**(a) Provenance columns** — registry columns 10–11 (`research_refs`, `doc_refs`; §2). Every
canonical artifact now records the research it rests on and the doc that governs it.

**(b) `check_provenance()`** — a new check in `scripts/ci/pr_governance_review.py` (the 12th,
alongside `check_reinvention`). A **capability-class** PR (adds ≥1 new code/config/spec file in
a governed subsystem, and its conventional-commit type is not a bugfix type) must carry a
`PROVENANCE:` block (`research` / `documents` / `builds_on` / `inventory`) in its body or a
commit body. Ladder: a **missing** block is `WARN` in the report phase and flips to `BLOCK` in
the strict phase (one constant, `PROVENANCE_MISSING_SEVERITY`). A block that declares
`research: NONE` is a hard `BLOCK` in any phase — "route a Pearl_Research lane first."
Bugfix-class PRs (conservative: explicit `fix|chore|docs|test|refactor|revert|style|ci|build|perf`
prefix, or modify-only) are exempt entirely. Shares the existing override-token plumbing.

**(c) `check_capability_regression.py`** — the no-lost-functions gate (registry row
`capability_regression_gate`). A **sibling** of `check_data_dictionary.py` (NEW-ARTIFACT-JUSTIFIED:
`check_data_dictionary` is an internal-consistency gate over the current tree; this is a
baseline-vs-HEAD **diff** that must read another git ref and reason about status *transitions* —
a distinct concern; the two share the builder, not the logic). It regenerates the data dictionary
at HEAD, diffs against the committed dictionary at the baseline ref (default `origin/main`), and
`BLOCK`s any path that was `WIRED` at baseline and is now removed or orphaned
(`UNWIRED`/`KNOWN_UNWIRED`) — unless the PR carries `CAPABILITY-RETIREMENT-RATIFIED: <OPD ref>`.
Fail-open when the baseline dictionary is unreadable. Wired into `.github/workflows/drift-detectors.yml`
and `scripts/run_production_readiness_gates.py` (gate 32), the same surfaces as its sibling, so it is
a required check.

**PM + Architect in the loop** (`docs/SESSION_UNITY_PROTOCOL.md`, `docs/PEARL_PM_STATE.md`,
`docs/PEARL_ARCHITECT_STATE.md`): the STARTUP_RECEIPT carries a `PROVENANCE:` field; CLOSEOUT
updates the lane's `ACTIVE_WORKSTREAMS.tsv` row and, on milestone merges, `PROGRAM_STATE.md`.
Architect adjudicates caps + `builds_on`; PM owns the workstream registry + `PROGRAM_STATE`
currency. One serial actor on those hot files.
- Principle 9 is additive and revertable (sits between §8 and `## Revert`; the `## Revert` instruction covers it).
