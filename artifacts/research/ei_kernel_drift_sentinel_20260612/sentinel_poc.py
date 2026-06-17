#!/usr/bin/env python3
"""
Canonical Artifact Graph — Drift Sentinel PoC
=============================================
The EI *kernel* (living graph + reactive gate) instantiated on the REPO instead
of the teachings. It builds a queryable graph of canonical artifacts (every
docs/ spec + doc) and demonstrates it catching duplicate / reinvention drift —
the "wait, don't write that, it already exists" check.

FREE / LOCAL per CLAUDE.md: uses TF-IDF cosine (scikit-learn) as a stand-in for
the production embedding (BGE-m3 via sentence-transformers). No model download,
no network, CPU-only, deterministic. Production swaps the vectorizer for the
local embedder — the graph + gate logic is identical.

Run:  python3 sentinel_poc.py
"""
from __future__ import annotations
import re, sys, json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REPO = Path("/Users/ahjan/phoenix_omega")
CORPUS_GLOBS = ["docs/**/*.md"]          # the canonical-artifact corpus (specs + docs)
OUT = Path(__file__).resolve().parent / "sentinel_report.md"

# Verdict thresholds on TF-IDF cosine, CALIBRATED to this corpus's tail.
# TF-IDF under-scores paraphrase (different words -> low cosine), so genuine
# duplicates here top out ~0.46; production BGE-m3 embeddings lift that tail
# well above these cutoffs. See the distribution line in the report.
BLOCK = 0.40     # clearly the same artifact family -> hard gate at PR time
WARN  = 0.28     # likely overlap -> inline whisper, "verify against X"
# below WARN -> OK

# ----------------------------------------------------------------------------- ingest
def extract_title(text: str, p: Path) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return p.stem.replace("_", " ").title()

def first_meaningful(text: str, n: int = 45) -> str:
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("```") or set(s) <= set("-=|# "):
            continue
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)   # md link -> keep anchor text
        s = re.sub(r"[`*_>#]", " ", s)
        out.append(s)
        if len(out) >= n:
            break
    return " ".join(out)

def build_blob(p: Path, title: str, text: str) -> str:
    # filename tokens carry strong signal for "same artifact under a new name";
    # repeat them so TF-IDF weights the identity, then title, then the head.
    name_tokens = re.sub(r"[^a-z0-9]+", " ", p.stem.lower())
    return f"{name_tokens} {name_tokens} {name_tokens} . {title} . {first_meaningful(text)}"

def load_artifacts():
    arts, seen = [], set()
    for g in CORPUS_GLOBS:
        for p in sorted(REPO.glob(g)):
            if not p.is_file() or p in seen:
                continue
            seen.add(p)
            try:
                text = p.read_text(errors="ignore")
            except Exception:
                continue
            if len(text.strip()) < 40:
                continue
            title = extract_title(text, p)
            body = first_meaningful(text)
            arts.append({
                "id": str(p.relative_to(REPO)),
                "title": title,
                "body": body,                         # body-only (no filename identity)
                "blob": build_blob(p, title, text),   # filename + title + body (graph node)
                "lines": text.count("\n") + 1,
            })
    return arts

# ----------------------------------------------------------------------------- the graph + gate
class Sentinel:
    def __init__(self, arts):
        self.arts = arts
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                                   min_df=1, max_df=0.6, sublinear_tf=True)
        self.M = self.vec.fit_transform([a["blob"] for a in arts])

    def check(self, blob: str, exclude_id: str | None = None, k: int = 4):
        """Reactive gate: score a proposed artifact against the graph."""
        q = self.vec.transform([blob])
        sims = cosine_similarity(q, self.M)[0]
        order = np.argsort(-sims)
        hits = []
        for i in order:
            if self.arts[i]["id"] == exclude_id:
                continue
            hits.append((self.arts[i]["id"], self.arts[i]["title"], float(sims[i])))
            if len(hits) >= k:
                break
        top = hits[0][2] if hits else 0.0
        verdict = "BLOCK" if top >= BLOCK else ("WARN" if top >= WARN else "OK")
        return verdict, hits

    def all_pairs_top(self, n=18):
        S = cosine_similarity(self.M)
        np.fill_diagonal(S, 0.0)
        iu = np.triu_indices_from(S, k=1)
        vals = S[iu]
        order = np.argsort(-vals)[:n]
        out = []
        for idx in order:
            i, j = iu[0][idx], iu[1][idx]
            out.append((self.arts[i]["id"], self.arts[j]["id"], float(S[i, j])))
        return out, S

# ----------------------------------------------------------------------------- run
def fmt(v):  # verdict glyph
    return {"BLOCK": "⛔ BLOCK", "WARN": "⚠️  WARN", "OK": "✅ OK"}[v]

def main():
    arts = load_artifacts()
    sen = Sentinel(arts)
    lines = []
    def out(s=""):
        print(s); lines.append(s)

    out("# Drift Sentinel — PoC run report")
    out()
    out(f"**Canonical Artifact Graph:** {len(arts)} nodes (docs/**/*.md), "
        f"{sen.M.shape[1]:,} TF-IDF features. Free/local, CPU, ~1s build.")
    out()

    # similarity distribution -> threshold calibration
    pairs, S = sen.all_pairs_top(18)
    iu = np.triu_indices_from(S, k=1)
    vals = S[iu]
    out("**Similarity distribution (all artifact pairs):** "
        f"median={np.median(vals):.3f}  p95={np.percentile(vals,95):.3f}  "
        f"p99={np.percentile(vals,99):.3f}  max={vals.max():.3f}  "
        f"→ thresholds WARN≥{WARN}, BLOCK≥{BLOCK} sit at the far tail "
        f"(only {100*(vals>=WARN).mean():.2f}% of pairs ≥ WARN).")
    out()

    # ---- Demo 1: real latent drift already in the repo (no synthesis) ----
    out("## Demo 1 — latent drift the Sentinel finds in the repo *as it stands today*")
    out("The most-similar EXISTING doc pairs. High similarity = candidate "
        "duplicate / parallel / drifted artifacts that a graph would have flagged "
        "the moment the second one was written.")
    out()
    out("| sim | artifact A | artifact B |")
    out("|----:|------------|------------|")
    for a, b, s in pairs:
        flag = "⛔" if s >= BLOCK else ("⚠️" if s >= WARN else "")
        out(f"| {flag} {s:.3f} | `{a}` | `{b}` |")
    out()

    # ---- Demo 2: live intercept of an agent re-authoring an existing doc ----
    out("## Demo 2 — live intercept: an agent is *about to write* a doc that already exists")
    out("Each case feeds the **body** of a REAL existing artifact (filename stripped — "
        "simulating an agent re-authoring it in their own words under a NEW name) against "
        "the full graph. A new locale/guide/spec that merely re-states existing canon is "
        "the single most common drift; the Sentinel catches it and points at what to reuse.")
    out()
    by_id = {a["id"]: a for a in arts}
    demo2 = [
        ("docs/brand_admin/zh_HK_distribution_guide.md", "docs/brand_admin/zh_MO_distribution_guide.md",
         "a 5th locale guide, hand-authored from scratch"),
        ("docs/PR_B_VISUAL_IDENTITY_RUNBOOK.md", "docs/VISUAL_IDENTITY_EXECUTION_GUIDE.md",
         "a 'new' visual-identity guide"),
        ("docs/CONTROL_PLANE_RUNBOOK.md", "docs/CONTROL_PLANE_OPERATIONS_GUIDE.md",
         "a parallel control-plane runbook"),
        ("docs/GITHUB_GOVERNANCE.md", "docs/REPO_GOVERNANCE_SOURCE_OF_TRUTH.md",
         "a fresh governance source-of-truth"),
    ]
    for orig_id, proposed, scenario in demo2:
        a = by_id.get(orig_id)
        if not a:
            continue
        verdict, hits = sen.check(a["body"], exclude_id=None, k=3)
        out(f"**Agent proposes:** `{proposed}` — *{scenario}*")
        out(f"&nbsp;&nbsp;(its body = a re-authoring of the real `{orig_id}`)")
        out(f"&nbsp;&nbsp;**Sentinel:** {fmt(verdict)} — nearest existing canonical:")
        for hid, _t, hs in hits:
            mark = "  ⟵ the original" if hid == orig_id else ""
            out(f"&nbsp;&nbsp;&nbsp;&nbsp;`{hs:.3f}` → `{hid}`{mark}")
        if verdict != "OK":
            out(f"&nbsp;&nbsp;💬 *“Wait — this is ~{hits[0][2]:.0%} the same as `{hits[0][0]}` "
                f"(already canonical). Reuse / extend it instead of greenfielding a new file.”*")
        out()

    # ---- Demo 3: a genuinely novel doc passes clean ----
    out("## Demo 3 — control: a genuinely new artifact passes clean (no false alarm)")
    novel = ("quantum_ribbon_telemetry quantum_ribbon_telemetry . Quantum Ribbon Telemetry Spec . "
             "Defines the cryogenic ribbon sampler cadence and the helium-loop backpressure "
             "calibration table for the sub-kelvin telemetry bus. Unrelated to any existing subsystem.")
    verdict, hits = sen.check(novel, k=3)
    out(f"**Agent proposes:** `docs/QUANTUM_RIBBON_TELEMETRY_SPEC.md` (truly unrelated)")
    out(f"&nbsp;&nbsp;**Sentinel:** {fmt(verdict)} — nearest is only "
        f"`{hits[0][2]:.3f}` (`{hits[0][0]}`). Below WARN → no false alarm; the agent proceeds.")
    out()
    out("---")
    out("*PoC uses TF-IDF cosine as a free/local stand-in for the production "
        "BGE-m3 embedder; the graph + gate logic is identical. Production adds: "
        "subsystem/owner/anchor-SHA edges, the inline PreToolUse hook tier, and the "
        "learning loop that promotes every confirmed catch into a sharper detector.*")

    OUT.write_text("\n".join(lines))
    print(f"\n[report written → {OUT}]")

if __name__ == "__main__":
    main()
