# EI as a Kernel — the Drift Sentinel

**Proposal (not ratified): instantiate the Enlightened Intelligence architecture a second time, pointed at the repo instead of the teachings, to prevent reinvention/contradiction drift — "wait, don't write that, it already exists."**

Author: Pearl_Research · Date: 2026-06-12 · Status: design proposal + working PoC (ratification is a gated follow-up; no cap entry this session)
Companion: [`sentinel_poc.py`](./sentinel_poc.py) + [`sentinel_report.md`](./sentinel_report.md) (the PoC run, on 406 real repo docs)

---

## 0. The one idea

**Enlightened Intelligence is not a content product — it is a *pattern*:**

> a **living graph of what's true/canonical** + a **reactive agent that reads new work against it** + a **hard floor it won't cross** + a **loop that learns from what it catches.**

Point that kernel at *teachings* → therapeutic books that never drift from the wisdom (the [EI frontier design](../ei_enlightened_intelligence_design_20260611/EI_FRONTIER_DESIGN.md)).
Point the **same kernel** at the *repo* → **the Drift Sentinel**: it watches what an agent is about to write and says *"that spec already exists — edit it"* / *"that deletes 20,000 files — stop."*

This doc specs the second instantiation, and ships a working proof that the core check runs **free, local, CPU-only, today**.

---

## 1. The category distinction (why this is a *sibling*, not the same EI)

The wisdom-EI must **not** police code — wrong corpus (doctrine graph doesn't know what `DURATION_SPEC.md` is), wrong judgment (spiritual fidelity ≠ architectural coherence). What generalizes is the **machine**, re-instantiated on a different corpus:

| | wisdom-EI | Drift Sentinel |
|---|---|---|
| **Corpus** | teacher doctrine + atoms | repo: specs, docs, registries, git history |
| **"Drift"** | spiritual/therapeutic | engineering/architectural (reinvention, contradiction, duplication) |
| **Floor** | fidelity to the teacher | governance (no mass-deletion, no reinventing a canonical, no contradicting a spec) |
| **Shared kernel** | **living graph + reactive gate + floor + learning loop** | **identical** |

They share architecture, never knowledge or judgment. Build the kernel once; instantiate per corpus.

---

## 2. Architecture

### 2.1 The Canonical Artifact Graph (the "what exists" knowledge)
A provenance-tracked graph whose nodes are the repo's canonical artifacts, mirroring the wisdom-EI's Living Wisdom Graph.

```
Node(artifact):
  id            docs/GITHUB_GOVERNANCE.md
  kind          spec | doc | runbook | config | registry | workflow
  title         "GitHub governance (source of truth)"
  embedding     BGE-m3 vector of (title + filename-identity + body)   # PoC: TF-IDF
  owner         subsystem owner (from SUBSYSTEM_AUTHORITY_MAP.tsv)
  authority     canonical | supporting | deprecated | superseded-by:<id>
  anchor_sha    last known-good SHA (from the anchors registry)
  status        active | stale (mtime / git age)

Edges:
  duplicates(weight)     a ──0.99── b      (cosine ≥ BLOCK)
  overlaps(weight)       a ──0.38── b      (WARN ≤ cosine < BLOCK)
  governed_by            doc ──→ authority_spec
  owns                   subsystem ──→ artifact
  supersedes             v2 ──→ v1
```
Seed sources (all already in-repo): `DOCS_INDEX.md`, `docs/specs/`, `SUBSYSTEM_AUTHORITY_MAP.tsv`, `ACTIVE_WORKSTREAMS.tsv`, the anchors registry, `git log`. Built CPU-only; enriched continuously (§2.4).

### 2.2 The reactive gate — three tiers (answering your "every agent vs always-on")
You can't run a deep semantic check on every keystroke, so the gate is tiered exactly like the wisdom-EI's 3-tier fitness (free heuristic → embedding surrogate → budgeted judge):

| Tier | When | Cost | Action | Mechanism |
|---|---|---|---|---|
| **0 — inline whisper** | every `Write`/`Edit` | ms, no LLM | *advisory*: "a file/spec named this already exists at Y; this path violates the authority map" | Claude Code **PreToolUse hook** → fast name/path/embedding lookup |
| **1 — discovery check** | agent's discovery pass / pre-commit | ~1 s, embeddings | *advisory*: "you're writing a duration spec; `DURATION_*` governs this — edit it" | Sentinel **skill** the agent calls (replaces voluntary self-check with a tool) |
| **2 — the veto** | PR open | seconds, CI | **blocks** mass-deletion, reinvention-of-canonical, spec-contradiction | extends `scripts/ci/pr_governance_review.py` (already a hard gate) |

**Rule: inline whispers, PR vetoes.** Tier 0/1 never block (that's how you avoid a nag everyone routes around); only the floor at Tier 2 blocks.

### 2.3 The governance floor (what blocks vs whispers)
BLOCK (non-negotiable, Tier 2): mass-deletion (>50 files, per CLAUDE.md rule 0) · creating a new artifact ≥ BLOCK-similar to a registered **canonical** · contradicting an authority doc · colliding with an active workstream.
WHISPER (Tier 0/1, advisory): overlaps in WARN band · new doc not in `DOCS_INDEX` · root-level file · sibling-session duplicate-in-flight.

### 2.4 The learning loop (what makes it "alive")
Every confirmed catch — an agent drifted, it got reverted, a PR got blocked — is a **labeled example**. The loop: (a) tunes the BLOCK/WARN thresholds per artifact-kind; (b) promotes recurring false-negatives into explicit rules; (c) keeps the graph fresh (re-embed on commit). Same Continual-Learning-Flywheel pattern, pointed at drift instead of reader response. Operator-gated before any threshold change ships.

---

## 3. What already exists vs. the gap (grounded)

**Already real (~40%):**
- `scripts/ci/pr_governance_review.py` — `check_mass_deletion`, `check_subsystem_scope`, `check_authority_docs`, `check_drift_patterns` (*"new spec when canonical exists"*, *"new docs that might duplicate"*), `check_workstream_conflict`, `check_pr_size`. **The Tier-2 veto exists** and blocks on BLOCKED status.
- The discovery protocol (check authority docs / anchors / existing files before acting) — but **voluntary**.

**The gap (this proposal):**
1. **No Canonical Artifact *Graph*** — "what exists" is scattered across `DOCS_INDEX` + TSVs; the drift check is **keyword/path-based** — it says *"you added a spec, go verify yourself,"* it doesn't **know** it's a duplicate. The PoC closes this: embed the corpus → *know*.
2. **No Tier-0 inline tier** — no hooks wired (`.claude/settings.json` has none); nothing catches drift *before* the PR.
3. **No learning loop** — every drift incident is forgotten instead of becoming a detector.

---

## 4. The PoC, and what it found (run it: `python3 sentinel_poc.py`)

A 130-line script builds the graph from **406 real repo docs** (128k TF-IDF features, ~1 s, CPU, no network — TF-IDF stands in for the production BGE-m3 embedder; the graph + gate logic is identical).

- **Demo 1 — real latent drift, zero synthesis.** The most-similar *existing* doc pairs are genuine duplicates/parallels that already drifted in: two near-identical PR1326 handoff docs (**0.465**), the `zh_HK`/`zh_TW`/`zh_SG` distribution guides reinventing each other (**~0.45**), a visual-identity **checklist vs runbook** (0.385), control-plane **go/no-go vs runbook** (0.36), onboarding-proof **backlog vs lane** (0.37). *These are the exact pairs a graph would have flagged the moment the second was written.*
- **Demo 2 — live intercept.** Feeding the **body** of a real doc under a new name (an agent re-authoring it): every case → **⛔ BLOCK**, *"~99% the same as `docs/X.md` (already canonical) — reuse it,"* and it surfaces the genuine siblings too (proposing a 5th locale guide flags `zh_HK` at 0.99 **and** `zh_TW`/`zh_SG` at 0.44/0.38).
- **Demo 3 — control.** A genuinely unrelated spec scores 0.045 → **✅ OK, no false alarm.**

**Honest limit:** TF-IDF under-scores paraphrase (different words → low cosine), so the PoC's BLOCK fires cleanly on near-copies and the *real-sibling* paraphrase cases sit in WARN (0.34–0.46). Production **BGE-m3 embeddings lift that paraphrase tail well above BLOCK** — the PoC under-states the production catch rate, it doesn't over-state it.

---

## 5. Build phases (each ships value standalone; gated on architecture cascade-settle)

| Phase | Build | Reuses | Flag |
|---|---|---|---|
| **P0** | **Canonical Artifact Graph** built from `DOCS_INDEX` + `docs/specs` + TSVs; swap TF-IDF→BGE-m3; **upgrade `pr_governance_review.check_drift_patterns` from keyword to semantic** (the Tier-2 veto gets eyes) | the PoC + the existing CI gate | 🟢 near-term, CPU |
| **P1** | **Tier-0 PreToolUse hook** (inline whisper on Write/Edit) + the **Sentinel skill** (Tier-1 discovery check) + owner/anchor/authority edges | Claude Code hooks; SUBSYSTEM_AUTHORITY_MAP; anchors registry | 🟡 |
| **P2** | **Learning loop** (catches → threshold tuning + new rules) + **multi-corpus** (instantiate the kernel on brand voice, on the 800-config catalog for no-duplicate-books) | the wisdom-EI Flywheel pattern | 🔴 |

---

## 6. Integrity / precision guardrails (the make-or-break)

- **Precision over recall.** It only speaks when confident; a nag gets routed around within a day. Inline = whisper, PR = veto.
- **Freshness or it lies.** A stale graph gives confidently-wrong *"this exists"* answers → re-embed on every commit; flag `stale` nodes; never block on a stale match.
- **Canonical-aware.** Blocking applies to reinventing a **registered canonical**, not to legitimately superseding one (that's a `supersedes` edge + owner sign-off).
- **Human disposes.** Tier-2 blocks are appealable to the operator/Architect; threshold changes are operator-gated (per the repo's serial-lane discipline on hot governance files).
- **Free/local.** BGE-m3 via sentence-transformers (CPU), the hook is local shell, the CI gate is existing. **No paid API** — `audit_llm_callers.py` stays green.

---

## 7. The payoff — "EI enhances everything," made precise

Not EI bolted onto every agent. **One kernel — graph + reactive gate + floor + learning loop — instantiated per corpus:**

- **teachings** → therapeutic books faithful to the wisdom (wisdom-EI)
- **the repo** → drift prevention (this Sentinel) — *catches PR #245's 20,006-file deletion in milliseconds instead of "hundreds of hours to recover"*
- **brand voice** → on-brand-or-blocked content
- **the 800-config catalog** → no two books that are secretly the same book

Same machine each time. That is the truest reading of your instinct: EI as a reusable kernel that makes everything it watches drift less and reuse more.
