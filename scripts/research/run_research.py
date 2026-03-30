#!/usr/bin/env python3
"""
Two-pass generational research runner for Pearl News.
Pass 1: reasoning with /think; save to <timestamp>_reasoning.md.
Pass 2: YAML-only with /no_think; save to artifacts/research/<layer>/ with provenance.

Usage:
  python scripts/research/run_research.py --prompt-id psychology [--paste path/to/raw.txt]
  python scripts/research/run_research.py --prompt-id pain_points --paste artifacts/research/raw/feed_2026-03-04.txt
  python scripts/research/run_research.py --prompt-id event_impact --paste -   # read stdin
  python scripts/research/run_research.py --prompt-id narrative --dry-run
  python scripts/research/run_research.py --prompt-id platform --paste raw.txt
  python scripts/research/run_research.py --prompt-id linguistic --paste raw.txt
  python scripts/research/run_research.py --prompt-id semantic_trend --paste raw.txt

Requires: Ollama running with Qwen3-14B-GGUF (or set OLLAMA_MODEL).
  pip install requests pyyaml (optional, for YAML parse check)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Repo root (script lives in scripts/research/)
REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_ROOT = REPO_ROOT / "research" / "prompts"
ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "research"

# Per prompt-id: artifact subdirectory under artifacts/research/, then paths relative to PROMPTS_ROOT.
LAYER_CONFIG: dict[str, dict[str, Any]] = {
    "psychology": {
        "artifacts_subdir": "psychology",
        "system": "system/psych_pulse_researcher.txt",
        "tasks": ["tasks/psychology_task.txt"],
        "yaml_instruction": "tasks/psychology_yaml_instruction.txt",
    },
    "pain_points": {
        "artifacts_subdir": "pain_points",
        "system": "system/econ_script_analyst.txt",
        "tasks": ["tasks/pain_points_task.txt"],
        "yaml_instruction": "tasks/pain_points_yaml_instruction.txt",
    },
    "event_impact": {
        "artifacts_subdir": "world_events",
        "system": "system/identity_conflict_researcher.txt",
        "tasks": ["tasks/event_impact_task.txt"],
        "yaml_instruction": "tasks/event_impact_yaml_instruction.txt",
    },
    "narrative": {
        "artifacts_subdir": "narrative",
        "system": "system/dim4_narrative_system.txt",
        "tasks": [
            "tasks/dim4_prompt_4_1_task.txt",
            "tasks/dim4_prompt_4_2_task.txt",
            "tasks/dim4_prompt_4_3_task.txt",
        ],
        "yaml_instruction": "tasks/narrative_yaml_instruction.txt",
    },
    "platform": {
        "artifacts_subdir": "platform",
        "system": "system/dim5_platform_system.txt",
        "tasks": [
            "tasks/dim5_prompt_5_1_task.txt",
            "tasks/dim5_prompt_5_2_task.txt",
        ],
        "yaml_instruction": "tasks/platform_yaml_instruction.txt",
    },
    "linguistic": {
        "artifacts_subdir": "linguistic",
        "system": "system/dim6_story_system.txt",
        "tasks": [
            "tasks/dim6_prompt_6_1_task.txt",
            "tasks/dim6_prompt_6_2_task.txt",
            "tasks/dim6_prompt_6_3_task.txt",
        ],
        "yaml_instruction": "tasks/linguistic_yaml_instruction.txt",
    },
    "semantic_trend": {
        "artifacts_subdir": "linguistic",
        "system": "system/semantic_trend_spotter.txt",
        "tasks": ["tasks/semantic_trend_task.txt"],
        "yaml_instruction": "tasks/semantic_trend_yaml_instruction.txt",
    },
}

PROMPT_IDS = list(LAYER_CONFIG.keys())
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:14b")


def load_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().strip()


def _prompt_path(rel: str) -> Path:
    return PROMPTS_ROOT / rel


def collect_layer_paths(cfg: dict[str, Any]) -> list[Path]:
    paths: list[Path] = [_prompt_path(cfg["system"])]
    for rel in cfg["tasks"]:
        paths.append(_prompt_path(rel))
    paths.append(_prompt_path(cfg["yaml_instruction"]))
    return paths


def validate_layer_files(prompt_id: str, cfg: dict[str, Any]) -> list[Path]:
    paths = collect_layer_paths(cfg)
    missing = [p for p in paths if not p.exists()]
    if missing:
        details = "\n".join(str(p) for p in missing)
        raise FileNotFoundError(f"Missing prompt files for --prompt-id {prompt_id}:\n{details}")
    return paths


def load_layer_bundle(prompt_id: str, raw_data: str) -> tuple[str, str, str]:
    """Return (system_text, combined_task_text, yaml_instruction_text)."""
    cfg = LAYER_CONFIG[prompt_id]
    validate_layer_files(prompt_id, cfg)
    system = load_text(_prompt_path(cfg["system"]))
    filler = raw_data or "(no paste provided)"
    task_chunks: list[str] = []
    for rel in cfg["tasks"]:
        task_chunks.append(load_text(_prompt_path(rel)).replace("{{RAW_DATA}}", filler))
    combined_task = "\n\n---\n\n".join(task_chunks)
    yaml_instruction = load_text(_prompt_path(cfg["yaml_instruction"]))
    return system, combined_task, yaml_instruction


def call_ollama(prompt: str, model: str, use_think: bool, temperature: float = 0.6) -> str:
    """Call Ollama generate API. use_think=True appends /think to prompt."""
    try:
        import requests
    except ImportError:
        print("Install requests: pip install requests", file=sys.stderr)
        sys.exit(1)
    if use_think:
        prompt = prompt.rstrip() + "\n\n/think"
    url = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    return r.json().get("response", "")


def extract_analysis_summary(reasoning: str, max_chars: int = 12000) -> str:
    """Take first substantive part for YAML pass; strip <think> blocks if present."""
    text = reasoning
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL | re.IGNORECASE)
    if think_match:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    text = text.strip()
    if len(text) > max_chars:
        text = text[: max_chars - 80] + "\n\n[... truncated for YAML pass ...]"
    return text


def write_yaml_with_provenance(out_path: Path, yaml_body: str, prompt_id: str, model: str) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d")
    header = f"""# provenance
run_date: {now}
model: {model}
prompt_id: {prompt_id}
source: yaml_pass

"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(yaml_body)
        if not yaml_body.endswith("\n"):
            f.write("\n")


def run_dry_run(prompt_id: str, cfg: dict[str, Any], out_dir: Path) -> None:
    paths = validate_layer_files(prompt_id, cfg)
    print(f"prompt-id: {prompt_id}", file=sys.stderr)
    print(f"artifacts_subdir: {cfg['artifacts_subdir']}", file=sys.stderr)
    print(f"output_dir (resolved): {out_dir}", file=sys.stderr)
    print("prompt files:", file=sys.stderr)
    for p in paths:
        print(f"  ok {p.relative_to(REPO_ROOT)}", file=sys.stderr)


def main() -> None:
    prompt_help = (
        "Research layer: psychology, pain_points, event_impact (dims 1–3); "
        "narrative, platform, linguistic (dims 4–6); semantic_trend (linguistic plane)."
    )
    parser = argparse.ArgumentParser(description="Two-pass Qwen3 generational research")
    parser.add_argument("--prompt-id", required=True, choices=PROMPT_IDS, help=prompt_help)
    parser.add_argument("--paste", default=None, help="Path to raw data file, or '-' for stdin")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--skip-yaml-pass", action="store_true", help="Only run reasoning pass")
    parser.add_argument("--out-dir", default=None, help="Override artifacts/research subdir (full path)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify prompt paths exist and print config; do not call the LLM",
    )
    args = parser.parse_args()

    prompt_id = args.prompt_id
    cfg = LAYER_CONFIG[prompt_id]
    out_dir = Path(args.out_dir) if args.out_dir else ARTIFACTS_ROOT / cfg["artifacts_subdir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        run_dry_run(prompt_id, cfg, out_dir)
        return

    raw_data = ""
    if args.paste:
        if args.paste == "-":
            raw_data = sys.stdin.read()
        else:
            raw_data = load_text(Path(args.paste))

    system, task, yaml_instruction_template = load_layer_bundle(prompt_id, raw_data)
    prompt_pass1 = f"{system}\n\n---\n\n{task}"

    print("Pass 1 (reasoning with /think)...", file=sys.stderr)
    response1 = call_ollama(prompt_pass1, args.model, use_think=True, temperature=0.6)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    reasoning_path = out_dir / f"{ts}_reasoning.md"
    with open(reasoning_path, "w", encoding="utf-8") as f:
        f.write(response1)
    print(f"Wrote {reasoning_path}", file=sys.stderr)

    if args.skip_yaml_pass:
        return

    analysis_summary = extract_analysis_summary(response1)
    yaml_instruction = yaml_instruction_template.replace("{{ANALYSIS_SUMMARY}}", analysis_summary)
    prompt_pass2 = f"Output only valid YAML. No thinking, no markdown fences.\n\n{yaml_instruction}"

    print("Pass 2 (YAML only, /no_think)...", file=sys.stderr)
    response2 = call_ollama(prompt_pass2, args.model, use_think=False, temperature=0.4)
    yaml_path = out_dir / f"{ts}.yaml"
    write_yaml_with_provenance(yaml_path, response2.strip(), prompt_id, args.model)
    print(f"Wrote {yaml_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
