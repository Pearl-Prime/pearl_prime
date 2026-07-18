#!/usr/bin/env python3
"""skill_eval_runner.py — P0-2 baseline-eval runner for Phoenix Omega skills.

Phase-2 implementation of `PRJ-AGENT-SYSTEM-IMPROVEMENT-V2` / workstream
`ws_agent_eval_harness_deepeval_agentevals_20260612`, item **P0-2** of
`docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md` (§2, §3.2, §5.4, §6).

What this does
--------------
Records a *baseline* eval for each named skill into that skill's own
directory (``skills/<name>/eval/baseline.json``), composed of two metric
families that mirror the `skill-creator` benchmark:

1. **trigger-accuracy** — does the skill's frontmatter ``description`` fire on
   positive prompts and stay quiet on negative (distractor) prompts? This is a
   deterministic string-overlap heuristic in dry-run; the judged mode asks the
   LOCAL Gemma/Qwen judge whether the description would route each prompt.
2. **task-score** — a handful of real-task benchmarks per skill, scored 0..1.
   In dry-run these are recorded as ``null`` (un-scored, pending a live judge);
   in judged mode each is graded by the local judge against a rubric.

Tier-2 compliance (CLAUDE.md LLM policy + .github/workflows/llm-policy-enforcement.yml)
--------------------------------------------------------------------------------------
This runner NEVER calls a paid LLM API. The judge is pointed at a **local
Ollama** endpoint (Gemma for English / Qwen for CJK6) read from the env vars
``GEMMA_BASE_URL`` / ``QWEN_BASE_URL`` (canonical, see
``artifacts/handoffs/HANDOFF_LLM_TWO_TIER_MIGRATION_20260420.md``) via the
config at ``scripts/eval/local_judge.config.yaml``. The default mode is
``--dry-run`` (no network, no judge), so the script is safe to run unattended
and in CI without credentials. Live judging is opt-in via ``--judge`` and only
ever talks to the local Ollama OpenAI-compatible endpoint.

Reuse-not-greenfield
--------------------
This is the runner half of the eval-tooling lane. It does NOT vendor DeepEval
or agentevals; it shells those libraries in (when present and ``--judge`` is
set) so the harness stays a thin orchestration layer over the ratified OSS
components, per spec §6 ("borrow patterns + OSS components, never a framework
runtime"). When DeepEval/agentevals are not installed, the runner degrades to
the deterministic dry-run heuristic so CI / a fresh checkout still works.

Usage
-----
    # Default: dry-run, no judge, no network. Writes baseline stubs.
    PYTHONPATH=. python3 scripts/eval/skill_eval_runner.py

    # Validate the case datasets + config only (no writes):
    PYTHONPATH=. python3 scripts/eval/skill_eval_runner.py --check

    # Live judged run against local Ollama (opt-in; needs GEMMA_BASE_URL):
    PYTHONPATH=. python3 scripts/eval/skill_eval_runner.py --judge

    # One skill only:
    PYTHONPATH=. python3 scripts/eval/skill_eval_runner.py --skill pearl-github

Exit codes
----------
    0  success (dry-run wrote baselines, or --check passed)
    1  a case dataset or config failed to load / validate
    2  --judge requested but the local judge is unreachable / misconfigured
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Repo geometry. This file lives at scripts/eval/skill_eval_runner.py, so the
# repo root is two parents up. Skill dirs live under <root>/skills/<name>/.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
EVAL_DIR = Path(__file__).resolve().parent
CASES_DIR = EVAL_DIR / "cases"
JUDGE_CONFIG_PATH = EVAL_DIR / "local_judge.config.yaml"

# The four skills P0-2 baselines (spec §2 P0-2). Order is stable for reporting.
TARGET_SKILLS: Tuple[str, ...] = (
    "pearl-github",
    "pearl-int",
    "deep-research",
    "phoenix-isolation-pr",
)

SCHEMA_VERSION = "skill-eval/baseline/v1"


# ---------------------------------------------------------------------------
# YAML loading. PyYAML is the single supported parser and is already pinned in
# the repo's requirements.txt / requirements-test.txt (pyyaml>=5.0) and in
# scripts/eval/requirements-eval.txt. We deliberately do NOT hand-roll a YAML
# subset parser (that would be reinvention, and a partial parser silently
# mis-reads edge cases). If PyYAML is somehow absent we fail loudly with a fix.
# ---------------------------------------------------------------------------
def _require_yaml():
    try:
        import yaml  # type: ignore

        return yaml
    except ImportError as exc:  # pragma: no cover - defensive, deps are pinned
        raise RuntimeError(
            "PyYAML is required: pip install -r scripts/eval/requirements-eval.txt "
            "(or the repo-root requirements.txt, which already pins pyyaml>=5.0)"
        ) from exc


def _load_yaml(path: Path) -> Any:
    """Load and parse a YAML file via PyYAML."""
    return _require_yaml().safe_load(path.read_text(encoding="utf-8"))


def _load_yaml_text(text: str) -> Any:
    """Parse a YAML *string* via PyYAML."""
    return _require_yaml().safe_load(text)


def _read_skill_description(skill_name: str) -> Optional[str]:
    """Pull the frontmatter ``description`` field from a skill's SKILL.md.

    Frontmatter is the leading ``---``-delimited YAML block. We extract just the
    description value (which may be a quoted string or a YAML block scalar).
    Returns None if the skill or its description is missing.
    """
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_md.exists():
        return None
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    front = text[3:end]
    data = _load_yaml_text(front)
    if isinstance(data, dict):
        desc = data.get("description")
        if isinstance(desc, str):
            return " ".join(desc.split())
    return None


# ---------------------------------------------------------------------------
# Trigger-accuracy: deterministic dry-run heuristic.
# ---------------------------------------------------------------------------
_STOP = {
    "the", "a", "an", "to", "of", "for", "and", "or", "in", "on", "is", "it",
    "this", "that", "with", "use", "any", "from", "i", "we", "you", "my", "our",
}


def _tokens(s: str) -> List[str]:
    out: List[str] = []
    cur: List[str] = []
    for ch in s.lower():
        if ch.isalnum() or ch in ("-", "_"):
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return [t for t in out if t and t not in _STOP]


def _overlap_score(prompt: str, description: str) -> float:
    """Fraction of meaningful prompt tokens that appear in the description.

    A cheap, fully-deterministic proxy for "would this skill's description make
    the router pick it for this prompt". It is NOT the production trigger logic
    (that is the model reading the description) — it exists only so the dry-run
    baseline has a reproducible number and the case datasets are exercised.
    """
    p = _tokens(prompt)
    if not p:
        return 0.0
    d = set(_tokens(description))
    hit = sum(1 for t in p if t in d)
    return round(hit / len(p), 4)


def _heuristic_trigger(
    description: str, positives: List[str], negatives: List[str], threshold: float
) -> Dict[str, Any]:
    """Score trigger-accuracy deterministically.

    A positive prompt is a true-positive if its overlap >= threshold; a negative
    prompt is a true-negative if its overlap < threshold. Accuracy is
    (TP + TN) / total. Per-prompt scores are recorded for inspection.
    """
    pos_scores = [(q, _overlap_score(q, description)) for q in positives]
    neg_scores = [(q, _overlap_score(q, description)) for q in negatives]
    tp = sum(1 for _, s in pos_scores if s >= threshold)
    tn = sum(1 for _, s in neg_scores if s < threshold)
    total = len(positives) + len(negatives)
    accuracy = round((tp + tn) / total, 4) if total else None
    return {
        "method": "dry-run-overlap-heuristic",
        "threshold": threshold,
        "true_positives": tp,
        "false_negatives": len(positives) - tp,
        "true_negatives": tn,
        "false_positives": len(negatives) - tn,
        "accuracy": accuracy,
        "positive_scores": [
            {"prompt": q, "overlap": s, "fired": s >= threshold} for q, s in pos_scores
        ],
        "negative_scores": [
            {"prompt": q, "overlap": s, "fired": s >= threshold} for q, s in neg_scores
        ],
    }


# ---------------------------------------------------------------------------
# Local judge client (opt-in, --judge only). Tier-2: local Ollama only.
# ---------------------------------------------------------------------------
class LocalJudgeError(RuntimeError):
    pass


def _load_judge_config() -> Dict[str, Any]:
    if not JUDGE_CONFIG_PATH.exists():
        raise LocalJudgeError(
            "local_judge.config.yaml not found next to skill_eval_runner.py"
        )
    cfg = _load_yaml(JUDGE_CONFIG_PATH)
    if not isinstance(cfg, dict):
        raise LocalJudgeError("local_judge.config.yaml did not parse to a mapping")
    return cfg


def _resolve_base_url(cfg: Dict[str, Any]) -> str:
    """Resolve the local Ollama base URL from env (canonical) then config.

    Canonical env vars per the two-tier migration handoff:
      GEMMA_BASE_URL (English judge) / QWEN_BASE_URL (CJK6 judge), both pointing
      at the Pearl Star Ollama OpenAI-compatible endpoint (.../v1, port 11434).
    The judge default uses the English (Gemma) endpoint; a CJK6 rubric may
    request the Qwen endpoint via the case dataset's ``judge_lang: cjk``.
    """
    judge = cfg.get("judge", {}) if isinstance(cfg.get("judge"), dict) else {}
    env_name = str(judge.get("base_url_env", "GEMMA_BASE_URL"))
    url = os.environ.get(env_name) or str(judge.get("base_url_fallback", "")).strip()
    if not url:
        raise LocalJudgeError(
            "no local Ollama base URL: set $%s (e.g. http://192.168.1.101:11434/v1) "
            "or base_url_fallback in local_judge.config.yaml" % env_name
        )
    # Hard guard: refuse anything that smells like a paid cloud endpoint.
    lowered = url.lower()
    banned = ("api.openai.com", "anthropic.com", "dashscope", "googleapis.com")
    if any(b in lowered for b in banned):
        raise LocalJudgeError(
            "refusing non-local judge endpoint %r (Tier-2 policy: Ollama only)" % url
        )
    return url


def _judge_available(base_url: str, timeout: float = 5.0) -> bool:
    """Best-effort reachability probe of the local Ollama /api/tags or /models.

    Uses only the stdlib (urllib) so no extra dep is needed just to probe.
    """
    import urllib.request

    # OpenAI-compatible servers expose /v1/models; Ollama exposes /api/tags.
    for suffix in ("/models", "/../api/tags"):
        try:
            req = urllib.request.Request(base_url.rstrip("/") + suffix, method="GET")
            with urllib.request.urlopen(req, timeout=timeout):  # nosec - local only
                return True
        except Exception:
            continue
    return False


def _make_local_client(base_url: str):
    """Construct an OpenAI-compatible client pointed at local Ollama.

    The OpenAI python package is the standard client for Ollama-compatible
    endpoints (see config/governance/banned_llm_patterns.yaml openai_api_cloud
    note). This line targets the local QWEN_BASE_URL / GEMMA_BASE_URL (ollama),
    never api.openai.com — the import is lazy so dry-run never needs it.
    """
    try:
        from openai import OpenAI  # ollama-compatible local client
    except Exception as exc:  # pragma: no cover - exercised only with --judge
        raise LocalJudgeError(
            "openai client not installed; pip install -r scripts/eval/requirements-eval.txt"
        ) from exc
    # base_url is a local ollama / GEMMA_BASE_URL endpoint (Tier-2), not cloud.
    return OpenAI(base_url=base_url, api_key=os.environ.get("OLLAMA_API_KEY", "ollama"))


# ---------------------------------------------------------------------------
# Case-dataset loading + validation.
# ---------------------------------------------------------------------------
REQUIRED_CASE_KEYS = ("skill", "trigger", "tasks")


def _case_path(skill_name: str) -> Path:
    return CASES_DIR / ("%s.cases.yaml" % skill_name)


def load_cases(skill_name: str) -> Dict[str, Any]:
    path = _case_path(skill_name)
    if not path.exists():
        raise FileNotFoundError("missing case dataset: %s" % path)
    data = _load_yaml(path)
    if not isinstance(data, dict):
        raise ValueError("case dataset %s did not parse to a mapping" % path)
    for key in REQUIRED_CASE_KEYS:
        if key not in data:
            raise ValueError("case dataset %s missing required key %r" % (path, key))
    trig = data.get("trigger") or {}
    if "positives" not in trig or "negatives" not in trig:
        raise ValueError(
            "case dataset %s trigger block needs 'positives' and 'negatives'" % path
        )
    return data


# ---------------------------------------------------------------------------
# Core run.
# ---------------------------------------------------------------------------
def evaluate_skill(
    skill_name: str,
    *,
    judge: bool,
    threshold: float,
    judge_client: Any = None,
    judge_model: Optional[str] = None,
) -> Dict[str, Any]:
    cases = load_cases(skill_name)
    description = _read_skill_description(skill_name)
    desc_present = description is not None
    description = description or ""

    trig = cases["trigger"]
    positives = [str(x) for x in (trig.get("positives") or [])]
    negatives = [str(x) for x in (trig.get("negatives") or [])]

    trigger_block = _heuristic_trigger(description, positives, negatives, threshold)
    trigger_block["judged"] = False

    tasks_in = cases.get("tasks") or []
    task_results: List[Dict[str, Any]] = []
    for t in tasks_in:
        if isinstance(t, dict):
            prompt = str(t.get("prompt", ""))
            rubric = str(t.get("rubric", ""))
            task_id = str(t.get("id", "task-%d" % (len(task_results) + 1)))
        else:
            prompt, rubric, task_id = str(t), "", "task-%d" % (len(task_results) + 1)
        task_results.append(
            {
                "id": task_id,
                "prompt": prompt,
                "rubric": rubric,
                # dry-run leaves the score un-graded (null) — it requires a judge
                "score": None,
                "judged": False,
            }
        )

    if judge and judge_client is not None:
        _judge_trigger(judge_client, judge_model, description, trigger_block)
        _judge_tasks(judge_client, judge_model, task_results)

    scored = [r["score"] for r in task_results if isinstance(r["score"], (int, float))]
    task_mean = round(sum(scored) / len(scored), 4) if scored else None

    return {
        "schema": SCHEMA_VERSION,
        "skill": skill_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "judged" if judge else "dry-run",
        "judge_model": judge_model if judge else None,
        "skill_description_present": desc_present,
        "metrics": {
            "trigger_accuracy": trigger_block,
            "task_score": {
                "mean": task_mean,
                "scored_count": len(scored),
                "total_count": len(task_results),
                "tasks": task_results,
            },
        },
        "notes": (
            "Dry-run baseline: trigger-accuracy via deterministic overlap "
            "heuristic; task scores un-graded (null) pending the local Gemma/Qwen "
            "judge (--judge). Regenerate with --judge once Pearl Star Ollama is "
            "reachable. See scripts/eval/README.md."
            if not judge
            else "Judged baseline graded by local Ollama (Tier-2)."
        ),
    }


def _judge_trigger(client, model, description, trigger_block) -> None:
    """Re-score trigger decisions with the local judge (overwrites heuristic)."""
    sys_prompt = (
        "You are a routing judge. Given a skill's description and a user prompt, "
        "answer strictly 'YES' if the skill should be selected for that prompt, "
        "or 'NO' otherwise. Answer with only YES or NO."
    )
    tp = fn = tn = fp = 0
    for entry in trigger_block.get("positive_scores", []):
        fired = _ask_yes_no(client, model, sys_prompt, description, entry["prompt"])
        entry["judge_fired"] = fired
        if fired:
            tp += 1
        else:
            fn += 1
    for entry in trigger_block.get("negative_scores", []):
        fired = _ask_yes_no(client, model, sys_prompt, description, entry["prompt"])
        entry["judge_fired"] = fired
        if fired:
            fp += 1
        else:
            tn += 1
    total = tp + fn + tn + fp
    trigger_block["judged"] = True
    trigger_block["method"] = "local-judge"
    trigger_block["true_positives"] = tp
    trigger_block["false_negatives"] = fn
    trigger_block["true_negatives"] = tn
    trigger_block["false_positives"] = fp
    trigger_block["accuracy"] = round((tp + tn) / total, 4) if total else None


def _ask_yes_no(client, model, sys_prompt, description, prompt) -> bool:
    content = "SKILL DESCRIPTION:\n%s\n\nUSER PROMPT:\n%s" % (description, prompt)
    resp = client.chat.completions.create(  # local ollama call (Tier-2)
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0,
    )
    text = (resp.choices[0].message.content or "").strip().upper()
    return text.startswith("Y")


def _judge_tasks(client, model, task_results) -> None:
    sys_prompt = (
        "You are a task-quality judge. Given a task prompt and a rubric, output a "
        "single float between 0.0 and 1.0 rating how well an agent equipped with "
        "the relevant skill could satisfy the rubric. Output ONLY the number."
    )
    for r in task_results:
        content = "TASK:\n%s\n\nRUBRIC:\n%s" % (r["prompt"], r["rubric"])
        resp = client.chat.completions.create(  # local ollama call (Tier-2)
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": content},
            ],
            temperature=0,
        )
        raw = (resp.choices[0].message.content or "").strip()
        r["score"] = _parse_score(raw)
        r["judged"] = True


def _parse_score(raw: str) -> Optional[float]:
    cur = ""
    for ch in raw:
        if ch.isdigit() or ch == ".":
            cur += ch
        elif cur:
            break
    try:
        val = float(cur)
    except ValueError:
        return None
    return max(0.0, min(1.0, round(val, 4)))


def write_baseline(skill_name: str, payload: Dict[str, Any]) -> Path:
    out_dir = SKILLS_DIR / skill_name / "eval"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "baseline.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------
def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--skill",
        action="append",
        choices=TARGET_SKILLS,
        help="Limit to one or more skills (repeatable). Default: all four.",
    )
    ap.add_argument(
        "--judge",
        action="store_true",
        help="Opt in to LIVE judging via local Ollama (Gemma/Qwen). Default off (dry-run).",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Validate case datasets + judge config and exit; write nothing.",
    )
    ap.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="Overlap threshold for the dry-run trigger heuristic (default 0.20).",
    )
    ap.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="Optional path to also write an aggregate run summary JSON.",
    )
    return ap.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    skills = tuple(args.skill) if args.skill else TARGET_SKILLS

    # --check: load + validate everything, write nothing.
    if args.check:
        ok = True
        for s in skills:
            try:
                load_cases(s)
                print("[ok] cases load: %s" % s)
            except Exception as exc:
                ok = False
                print("[FAIL] cases load: %s -> %s" % (s, exc), file=sys.stderr)
        try:
            _load_judge_config()
            print("[ok] judge config parses: %s" % JUDGE_CONFIG_PATH.name)
        except Exception as exc:
            ok = False
            print("[FAIL] judge config: %s" % exc, file=sys.stderr)
        return 0 if ok else 1

    judge_client = None
    judge_model = None
    if args.judge:
        try:
            cfg = _load_judge_config()
            base_url = _resolve_base_url(cfg)
            judge = cfg.get("judge", {}) if isinstance(cfg.get("judge"), dict) else {}
            judge_model = str(judge.get("model", "gemma3:27b"))
            if not _judge_available(base_url):
                print(
                    "[FAIL] local judge unreachable at %s — start Pearl Star Ollama "
                    "or run without --judge (dry-run)." % base_url,
                    file=sys.stderr,
                )
                return 2
            judge_client = _make_local_client(base_url)
            print("[ok] local judge reachable: %s (model=%s)" % (base_url, judge_model))
        except LocalJudgeError as exc:
            print("[FAIL] %s" % exc, file=sys.stderr)
            return 2

    summary: Dict[str, Any] = {
        "schema": "skill-eval/summary/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "judged" if args.judge else "dry-run",
        "skills": {},
    }
    rc = 0
    for s in skills:
        try:
            payload = evaluate_skill(
                s,
                judge=args.judge,
                threshold=args.threshold,
                judge_client=judge_client,
                judge_model=judge_model,
            )
            out = write_baseline(s, payload)
            ta = payload["metrics"]["trigger_accuracy"]["accuracy"]
            tm = payload["metrics"]["task_score"]["mean"]
            print(
                "[wrote] %s  trigger_accuracy=%s  task_mean=%s  -> %s"
                % (s, ta, tm, out.relative_to(REPO_ROOT))
            )
            summary["skills"][s] = {
                "trigger_accuracy": ta,
                "task_mean": tm,
                "baseline_path": str(out.relative_to(REPO_ROOT)),
            }
        except Exception as exc:
            rc = 1
            print("[FAIL] %s -> %s" % (s, exc), file=sys.stderr)
            summary["skills"][s] = {"error": str(exc)}

    if args.summary_out is not None:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print("[wrote] run summary -> %s" % args.summary_out)

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
