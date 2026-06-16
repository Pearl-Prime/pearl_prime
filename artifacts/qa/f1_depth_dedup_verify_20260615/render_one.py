#!/usr/bin/env python3
"""TRUE-pre-fix-vs-fixed F1 proof for the cross-chapter depth-dedup change.

ws_f1_depth_dedup_20260615 (task_48b619ed) — independent verification arm.

Renders ONE (arm, format) per invocation in an *isolated* process so the two
arms never share a module cache:

  * arm=prefix : loads origin/main's PRE-FIX ``enrichment_select`` via an
                 importlib shim (materialized with ``git show`` — no working-tree
                 mutation, fully reproducible). This is the honest "before".
  * arm=fixed  : uses the working-tree ``enrichment_select`` (the fix).

EVERYTHING ELSE is held identical across arms (composer, register_gate, atoms,
seed), so the F1 delta is attributable purely to the enrichment_select.py change.
Unlike the env-flag toggle in ``../f1_depth_dedup_20260615/gen_proof.py`` (whose
"baseline" is fix-with-fuzzy-off = book-wide registry + sibling rotation, NOT the
legacy per-chapter behaviour), this arm reproduces the genuine origin/main
per-chapter-exact-set baseline (⑤ leverB: standard 61 / extended 67 / deep 224).

Deterministic; NO paid LLM API (CLAUDE.md tier policy).
Run via run_all.sh.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
assert (ROOT / "phoenix_v4").is_dir(), f"repo root wrong: {ROOT}"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_MODNAME = "phoenix_v4.planning.enrichment_select"
TOPIC, PERSONA, TEACHER, SEED = "anxiety", "gen_z_professionals", "ahjan", "leverB_baseline"


def _install_prefix_shim() -> None:
    """Put origin/main's pre-fix enrichment_select in sys.modules BEFORE anything
    imports it, so the whole pipeline binds the legacy module for this process."""
    src = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"origin/main:phoenix_v4/planning/enrichment_select.py"]
    )
    tf = tempfile.NamedTemporaryFile("wb", suffix="_enrich_origin.py", delete=False)
    tf.write(src)
    tf.close()
    spec = importlib.util.spec_from_file_location(_MODNAME, tf.name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODNAME] = mod          # shim FIRST
    spec.loader.exec_module(mod)
    assert not hasattr(mod, "_SeenBodies"), "shim is NOT pre-fix (found _SeenBodies)"


def _probe_counts(prose: str) -> dict:
    probes = {
        "HOOK v02 'The task is open'": "The task is open",
        "EXERCISE 'Just thirty seconds'": "Just thirty seconds",
        "EXERCISE 'Now, I want you to notice'": "Now, I want you to notice",
        "doctrine 'This is The Unspoken'": "This is The Unspoken",
    }
    return {k: prose.count(v) for k, v in probes.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["prefix", "fixed"])
    ap.add_argument("--format", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.arm == "prefix":
        _install_prefix_shim()
    else:
        import phoenix_v4.planning.enrichment_select as _m
        assert hasattr(_m, "_SeenBodies"), "working tree is MISSING the fix (_SeenBodies)"

    # Imports AFTER the shim decision so the prefix arm binds the legacy module.
    import yaml
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
    from phoenix_v4.planning.beatmap_compile import (
        compile_beatmap, load_format_spec, load_topic_engines,
    )
    from phoenix_v4.planning.enrichment_select import (
        EnrichmentRequest, apply_depth_pass, select_enrichment,
    )
    from phoenix_v4.rendering.book_renderer import clean_for_delivery
    from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book
    from phoenix_v4.quality.register_gate import evaluate_register

    fmt = a.format
    spine = load_spine(TOPIC, ROOT, runtime_format=fmt)
    shaped = apply_knobs(spine, load_knob_profile(TOPIC, ROOT), runtime_format=fmt,
                         persona_id=PERSONA, repo_root=ROOT)
    beatmap = compile_beatmap(shaped, load_topic_engines(TOPIC, ROOT),
                              load_format_spec(fmt, ROOT), ROOT)
    req = EnrichmentRequest(beatmap=beatmap, teacher_id=TEACHER, persona_id=PERSONA,
                            topic_id=TOPIC, seed=SEED)
    enriched = select_enrichment(req, ROOT)
    depth_map = yaml.safe_load(
        (ROOT / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    enriched = apply_depth_pass(enriched, depth_map, repo_root=ROOT)
    prose = clean_for_delivery(compose_from_enriched_book(enriched, quality_profile="draft"))

    res = evaluate_register(prose, persona_id=PERSONA, topic_id=TOPIC, quality_profile="production")
    j = res.to_json()
    by_id: dict = {}
    f1_sizes: dict = {}
    f1_findings: list = []
    for f in j.get("findings", []):
        fid = f.get("failure_id", "?")
        by_id[fid] = by_id.get(fid, 0) + 1
        if fid == "F1":
            m = re.search(r"cluster size (\d+)", f.get("summary", ""))
            sz = int(m.group(1)) if m else 0
            f1_sizes[sz] = f1_sizes.get(sz, 0) + 1
            f1_findings.append({"size": sz, "summary": f.get("summary", ""),
                                "excerpt": f.get("evidence", {}).get("excerpt", "")})

    out = Path(a.out) / a.arm / fmt
    out.mkdir(parents=True, exist_ok=True)
    (out / "book.txt").write_text(prose, encoding="utf-8")
    score = {
        "arm": a.arm, "format": fmt,
        "chapters": len(re.findall(r"(?m)^Chapter \d+$", prose)),
        "words": len(prose.split()),
        "verdict": j["verdict"],
        "F1": by_id.get("F1", 0), "F2": by_id.get("F2", 0), "F7": by_id.get("F7", 0),
        "total_findings": len(j.get("findings", [])),
        "F1_sizes": dict(sorted(f1_sizes.items())),
        "cluster_phrase_counts": _probe_counts(prose),
        "largest_f1": sorted(f1_findings, key=lambda x: -x["size"])[:8],
    }
    (out / "score.json").write_text(json.dumps(score, indent=2), encoding="utf-8")
    print(json.dumps({k: score[k] for k in (
        "arm", "format", "chapters", "words", "verdict", "F1", "F2", "F7",
        "F1_sizes", "cluster_phrase_counts")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
