# Routing Note — the Drift Sentinel is the prototype of the *deferred* Phase-2b semantic arm

**Author:** Pearl_GitHub (with a Pearl_Architect routing hat) · **Date:** 2026-06-13
**Status:** design-only routing note. Installs nothing. No cap appended. Not merged-to-active.
**Companions in this PR:** [`EI_KERNEL_DRIFT_SENTINEL_SPEC.md`](./EI_KERNEL_DRIFT_SENTINEL_SPEC.md) · [`sentinel_poc.py`](./sentinel_poc.py) · [`sentinel_report.md`](./sentinel_report.md)

This note exists because the ground moved under the original design (2026-06-12) and the
Sentinel must be filed against where the codebase **actually is** today (2026-06-13), not
where it was when the spec was written. It does not edit the three artifacts; it routes them.

---

## What changed since the spec was written (2026-06-12 → 2026-06-13)

The **Canonical Artifacts Registry + reinvention guard SHIPPED** while this design sat pending.
That is precisely the "Already real (~40%)" + P0 layer the spec (§3, §5) anticipated — it is **no
longer a gap, and the Sentinel is no longer "the registry upgrade."** Concretely, on `origin/main`:

- `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` + `docs/specs/CANONICAL_ARTIFACTS_REGISTRY_SPEC.md` — the registry (cap **#1524**), full-seed to 67 rows (**#1549**).
- `scripts/ci/pr_governance_review.py` now carries **`check_reinvention()`** (origin/main L536) and **`check_drift_patterns()`** (origin/main L465) (**#1552**) — the Tier-2 veto the spec §2.2 calls for, in code, as a hard gate.

So the registry + the *name/path/keyword* reinvention veto are **done**. What is **not** done is the
semantic half — and the codebase says so out loud.

---

## The five points (what this note routes, and how)

### (a) This is the prototype of the EXPLICITLY-DEFERRED Phase-2b semantic arm — not a new subsystem, not the registry

`scripts/ci/pr_governance_review.py` (origin/main **L560–561**) states **verbatim**:

> *"The content-overlap (semantic) arm is **Phase-2b** and is NOT implemented here: it would
> require a local / Tier-2 embedding model (Gemma/Qwen via Ollama) per …"*

`sentinel_poc.py` **is** that arm: it embeds the doc corpus and scores a proposed artifact by
**content overlap** (cosine), which is exactly the check `check_reinvention()` defers. The current
guard catches reinvention by **filename/path/keyword**; the Sentinel adds the **"the words are
~99% the same even under a new name"** detection the deferral note names. It is therefore the
**semantic extension of an existing, landed gate** — *not* a parallel subsystem, and *not* the
Canonical Artifacts Registry (which already shipped via #1524 / #1549 / #1552).

### (b) The INSTALL extends `check_reinvention` / `check_drift_patterns` — gated under the existing cap on the serial lane, NOT built here

When adopted, Phase-2b does **not** add a new gate. It **extends** the two functions above so that a
proposed artifact scoring **≥ 0.80 content-overlap** against a **registered canonical** raises a
governance **WARN** (precision-first; BLOCK reserved for the floor cases the spec §2.3 enumerates —
mass-deletion, reinventing a canonical, contradicting an authority doc). That build is a **separate,
gated step** under cap **`CANONICAL-ARTIFACTS-REGISTRY-V1-01`** on the **serial
`PEARL_ARCHITECT_STATE.md` lane** — it is deliberately **not performed in this PR**. Filing the
prototype here ≠ installing it; the install rides the cap when the serial lane dispatches it.

### (c) Production swaps the PoC TF-IDF → BGE-m3, reusing the EI-P0 graph kernel + the now-up Ollama

The PoC uses CPU **TF-IDF** (scikit-learn) as a free/local stand-in. Production swaps the vectorizer
for **BGE-m3** (sentence-transformers, local) — the graph + gate logic is **identical** (PoC docstring;
spec §2.1, §4). Two reuse facts make this cheap:

1. **The embedding-graph kernel is built once.** The EI **P0** build constructs a corpus-agnostic
   embedding-graph KERNEL; Phase-2b here **re-instantiates that same kernel on the repo corpus**
   rather than greenfielding an embedder. *Build the machine once, point it at a second corpus* —
   the spec's "one kernel, instantiated per corpus" thesis (§0, §7), now literally a code-reuse path.
2. **The local model is up.** Pearl Star **Ollama (:11434)** is live as of **2026-06-13** — the exact
   "local / Tier-2 embedding model (Gemma/Qwen via Ollama)" the deferral note at L560 was waiting on.
   The blocker the codebase cited is **cleared**; what remains is the gated build, not a dependency gap.

**Free/local invariant holds:** TF-IDF today, BGE-m3 via local Ollama at install — **no paid LLM API**.
`scripts/ci/audit_llm_callers.py` stays green; the LLM Tier Policy (Tier-2 local, unattended) is honored.

### (d) The 3-tier deploy (the spec's §2.2 gate, mapped to today's surfaces)

| Tier | Surface | When | Action | Status |
|---|---|---|---|---|
| **0 — inline whisper** | Claude Code **PreToolUse hook** on Write/Edit | every edit | advisory: "a file/spec named/like this already exists at Y" | not wired (no `.claude` hook in this PR) |
| **1 — discovery check** | Sentinel **skill** the agent calls in its discovery pass | pre-commit | advisory: "you're writing a duration spec; `DURATION_*` governs this — edit it" | design-only |
| **2 — the (now-semantic) PR veto** | `pr_governance_review.py` `check_reinvention` / `check_drift_patterns` | PR open | **already blocks** name/path/keyword reinvention; Phase-2b **adds the semantic ≥0.80 WARN** | gate landed (#1552); semantic arm = the gated extension |

**Rule (spec §2.2): inline whispers, PR vetoes.** Tier 0/1 never block (a nag gets routed around);
only the Tier-2 floor blocks. Phase-2b lights up Tier-2's semantic eyes first; Tier-0/1 are later phases.

### (e) The honest PoC caveat (why it's filed as a prototype, not a finished detector)

**TF-IDF under-scores paraphrase** (different words → low cosine). The consequence, seen in the PoC
run (`sentinel_report.md`): the gate **fires cleanly on near-copies** (Demo 2: re-authored canon →
0.986–0.992 → ⛔ BLOCK) while genuine **paraphrase siblings sit in WARN** (Demo 1: 0.30–0.47 — e.g.
the `zh_HK`/`zh_TW`/`zh_SG` locale guides reinventing each other, the two PR1326 handoff dupes).
So the PoC **blocks clean near-copies and parks looser siblings in WARN** — it **under-states** the
production catch rate, it does not over-state it. **BGE-m3 lifts that paraphrase tail above BLOCK**,
raising the catch rate at install — which is exactly why Phase-2b is a *swap-the-embedder* upgrade of
a proven gate, not a fresh build.

---

## Anti-reinvention self-check (dogfooding the guard this routes into)

Per the repo's anti-reinvention architecture (router principle 9 + the Canonical Artifacts Registry +
the CI reinvention guard), the correct move is to **extend the landed guard, never greenfield a
parallel one** — building a second, separate drift checker would be the *exact* reinvention this tool
exists to prevent. This note therefore **routes the Sentinel into `check_reinvention` /
`check_drift_patterns`** rather than proposing a standalone Sentinel service. The Sentinel is the
semantic *arm* of the existing gate, filed against the existing cap.

---

## What this PR does and does NOT do

**Does:** preserves the 3 design artifacts + adds this one routing note (4 files, `artifacts/research/…`).
PoC re-verified on the live corpus (409 nodes / 130,131 features; Demo 1 surfaces real drift,
Demo 2 → 4× BLOCK, Demo 3 → OK; CPU, ~seconds, no network).

**Does NOT:** edit `scripts/ci/pr_governance_review.py` · add any `.claude` PreToolUse hook · wire any
CI · append a cap · touch any hot governance file (`PEARL_ARCHITECT_STATE.md` and siblings untouched)
· greenfield a parallel registry/guard · call a paid LLM API · merge.

---

## NEXT_ACTION (handoff to Pearl_Architect)

Adopt this as the **Phase-2b semantic content-overlap arm** of the reinvention guard, under cap
**`CANONICAL-ARTIFACTS-REGISTRY-V1-01`**, **when the serial `PEARL_ARCHITECT_STATE.md` lane
dispatches it**. At that point the install — semantic ≥0.80 content-overlap on `check_reinvention`
(+ the Tier-0 PreToolUse hook as a later phase) — is built, **reusing the EI-P0 graph kernel + the
now-up Pearl Star Ollama (BGE-m3)**. The TF-IDF → BGE-m3 swap is the only embedder change; the graph
and gate logic in `sentinel_poc.py` carry over unchanged.
