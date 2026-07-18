#!/usr/bin/env python3
"""
Two-pass generational research runner for Pearl News.
Pass 1: reasoning (Qwen enable_thinking=True or Ollama /think).
Pass 2: structured YAML (enable_thinking=False or Ollama /no_think).

Usage:
  python scripts/research/run_research.py --prompt-id psychology --prepare-deep-research-prompt --paste path/to/session.txt
  python scripts/research/run_research.py --prompt-id psychology --paste path/to/raw_feed.txt --allow-legacy-direct-run

Config (OpenAI-compatible Qwen / DashScope — repo standard):
  QWEN_BASE_URL → else docs/qwen_api_base_url.txt
  QWEN_API_KEY  → else docs/qwen_api_key.txt
  QWEN_MODEL    → else docs/qwen_model.txt

Backward compat: if QWEN_BASE_URL contains "11434", uses Ollama /api/generate (OLLAMA_MODEL, OLLAMA_HOST).

Requires: pip install openai requests pyyaml
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

from research_prompt_builder import (
    ResearchPromptInputs,
    build_prompt_package,
    write_prompt_package,
)

# Repo root (script lives in scripts/research/)
REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_ROOT = REPO_ROOT / "research" / "prompts"
ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "research"

DOCS_QWEN_BASE = REPO_ROOT / "docs" / "qwen_api_base_url.txt"
DOCS_QWEN_KEY = REPO_ROOT / "docs" / "qwen_api_key.txt"
DOCS_QWEN_MODEL = REPO_ROOT / "docs" / "qwen_model.txt"

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
        "artifacts_subdir": "semantic_trend",
        "system": "system/semantic_trend_spotter.txt",
        "tasks": ["tasks/semantic_trend_task.txt"],
        "yaml_instruction": "tasks/semantic_trend_yaml_instruction.txt",
    },
}

PROMPT_IDS = list(LAYER_CONFIG.keys())
OLLAMA_DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:14b")
LEGACY_DIRECT_RUN_ENV = "PEARL_RESEARCH_ALLOW_LEGACY_DIRECT_RUN"


def _read_repo_text(relative: str) -> str:
    path = REPO_ROOT / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def _load_qwen_api_key_from_file() -> str:
    """Match pearl_news.pipeline.slot_provider_qwen key file parsing."""
    raw = _read_repo_text("docs/qwen_api_key.txt")
    if not raw:
        return ""
    patterns = [
        r'Api\s*key\s*=\s*"([^"]+)"',
        r"Api\s*key\s*=\s*'([^']+)'",
        r"Api\s*key\s*=\s*([^\s]+)",
        r"\b(sk-[A-Za-z0-9._-]+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return re.sub(r"^-+(?=sk-)", "", value)
    value = raw.strip().strip('"').strip("'")
    return re.sub(r"^-+(?=sk-)", "", value)


def _load_qwen_base_url_from_file() -> str:
    raw = _read_repo_text("docs/qwen_api_base_url.txt")
    if not raw:
        return ""
    match = re.search(r"(https?://[^\s\"']+)", raw)
    if match:
        return match.group(1).strip()
    return raw.strip().strip('"').strip("'")


def _load_qwen_model_from_file() -> str:
    raw = _read_repo_text("docs/qwen_model.txt")
    if not raw:
        return ""
    if "=" in raw:
        raw = raw.split("=", 1)[1].strip()
    return raw.strip().strip('"').strip("'")


def resolve_qwen_config() -> tuple[str, str, str]:
    """Return (base_url, api_key, model_hint) after env + file + slot-style defaults."""
    base_url = os.environ.get("QWEN_BASE_URL", "").strip() or _load_qwen_base_url_from_file()
    if os.environ.get("QWEN_API_KEY") is not None:
        api_key = (os.environ.get("QWEN_API_KEY") or "").strip()
    else:
        api_key = _load_qwen_api_key_from_file()
    model = os.environ.get("QWEN_MODEL", "").strip() or _load_qwen_model_from_file()
    if api_key and (not base_url or "localhost" in base_url or "127.0.0.1" in base_url):
        if "11434" not in base_url:
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if api_key and not model:
        model = "qwen-plus"
    return base_url, api_key, model


def is_ollama_endpoint(base_url: str) -> bool:
    return "11434" in base_url


def ollama_host_from_base_url(base_url: str) -> str:
    if not base_url.strip():
        return os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    u = base_url.strip()
    if not u.startswith("http"):
        u = "http://" + u
    parsed = urllib.parse.urlparse(u)
    if parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def load_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().strip()


def load_path_or_literal(value: str) -> str:
    path = Path(value)
    try:
        if path.exists() and path.is_file():
            return load_text(path)
    except OSError:
        return value
    return value


def legacy_direct_run_allowed(flag_value: bool) -> bool:
    env_value = os.environ.get(LEGACY_DIRECT_RUN_ENV, "").strip().lower()
    return flag_value or env_value in {"1", "true", "yes", "on"}


def require_prompt_package_or_legacy_ack(
    *,
    prepare_deep_research_prompt: bool,
    allow_legacy_direct_run: bool,
) -> None:
    """Guard Pearl_Research from raw-context-to-generic-prompt execution."""
    if prepare_deep_research_prompt or legacy_direct_run_allowed(allow_legacy_direct_run):
        return
    raise RuntimeError(
        "direct Pearl_Research execution is blocked by default. Generate a prompt package first "
        "with --prepare-deep-research-prompt for messy, implementation-adjacent, regional, or "
        "decision-oriented research. For the legacy Pearl News feed-extraction lane only, rerun "
        "with --allow-legacy-direct-run or set PEARL_RESEARCH_ALLOW_LEGACY_DIRECT_RUN=1."
    )


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


def call_ollama_generate(
    prompt: str,
    model: str,
    *,
    use_think_suffix: bool,
    temperature: float,
    ollama_host: str,
) -> str:
    try:
        import requests
    except ImportError:
        print("Install requests: pip install requests", file=sys.stderr)
        sys.exit(1)
    if use_think_suffix:
        prompt = prompt.rstrip() + "\n\n/think"
    url = ollama_host.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    r = requests.post(url, json=payload, timeout=600)
    r.raise_for_status()
    return r.json().get("response", "")


def _extract_message_text(resp: Any) -> str:
    choice = resp.choices[0] if getattr(resp, "choices", None) else None
    if not choice or not getattr(choice, "message", None):
        return ""
    msg = choice.message
    parts: list[str] = []
    reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)
    if reasoning:
        parts.append(str(reasoning).strip())
    content = (msg.content or "").strip()
    if content:
        parts.append(content)
    return "\n\n".join(parts).strip() if parts else ""


def call_openai_chat(
    client: Any,
    model: str,
    messages: list[dict[str, str]],
    *,
    enable_thinking: bool,
    temperature: float,
    max_tokens: int,
) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body={"enable_thinking": enable_thinking},
    )
    return _extract_message_text(resp)


def create_openai_client(base_url: str, api_key: str) -> Any:
    from openai import OpenAI

    return OpenAI(base_url=base_url.rstrip("/"), api_key=api_key or "lm-studio", timeout=600.0)


def _strip_yaml_fences(raw: str) -> str:
    s = raw.strip()
    if not s.startswith("```"):
        return s
    lines = s.splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    while lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _validate_yaml_body(yaml_body: str) -> None:
    try:
        import yaml as pyyaml  # type: ignore
    except ImportError:
        return
    try:
        pyyaml.safe_load(yaml_body)
    except Exception as e:
        raise ValueError(f"YAML parse failed: {e}") from e


def _validate_written_artifact(path: Path) -> None:
    try:
        import yaml as pyyaml  # type: ignore
    except ImportError:
        return
    text = path.read_text(encoding="utf-8")
    try:
        pyyaml.safe_load(text)
    except Exception as e:
        raise ValueError(f"Written artifact failed YAML parse ({path}): {e}") from e


def format_reasoning_artifact(
    body: str,
    *,
    layer: str,
    model: str,
    date_str: str,
    mode_line: str,
) -> str:
    """Markdown with YAML frontmatter (Pearl News two-pass convention)."""
    header = (
        "---\n"
        f"layer: {layer}\n"
        f"model: {model}\n"
        f"mode: {mode_line}\n"
        f"date: {date_str}\n"
        "pass: 1\n"
        "---\n\n"
    )
    return header + body.lstrip("\n")


def extract_analysis_summary(reasoning: str, max_chars: int = 12000) -> str:
    text = reasoning
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL | re.IGNORECASE)
    if think_match:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    if text.startswith("---"):
        end = text.find("\n---\n", 3)
        if end != -1:
            text = text[end + 5 :].lstrip()
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
    base_url, api_key, model_hint = resolve_qwen_config()
    transport = "ollama" if base_url and is_ollama_endpoint(base_url) else "openai"
    if not base_url and not api_key:
        transport = "ollama"
    print(f"prompt-id: {prompt_id}", file=sys.stderr)
    print(f"artifacts_subdir: {cfg['artifacts_subdir']}", file=sys.stderr)
    print(f"output_dir (resolved): {out_dir}", file=sys.stderr)
    print(f"transport (resolved): {transport}", file=sys.stderr)
    if transport == "openai":
        print(f"QWEN_BASE_URL: {base_url or '(empty)'}", file=sys.stderr)
        print(f"QWEN_API_KEY: {'set' if api_key else 'missing'}", file=sys.stderr)
        print(f"QWEN_MODEL (hint): {model_hint or '(default after --model)'}", file=sys.stderr)
    print("prompt files:", file=sys.stderr)
    for p in paths:
        print(f"  ok {p.relative_to(REPO_ROOT)}", file=sys.stderr)


def run_layer_openai(
    *,
    client: Any,
    model: str,
    system: str,
    task: str,
    yaml_instruction_template: str,
    prompt_id: str,
    reasoning_path: Path,
    yaml_path: Path,
    layer_label: str,
    date_for_frontmatter: str,
    mode_line_p1: str,
) -> None:
    messages_p1: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": task},
    ]
    print("Pass 1 (reasoning, enable_thinking=True)...", file=sys.stderr)
    response1_raw = call_openai_chat(
        client,
        model,
        messages_p1,
        enable_thinking=True,
        temperature=0.6,
        max_tokens=16384,
    )
    reasoning_doc = format_reasoning_artifact(
        response1_raw,
        layer=layer_label,
        model=model,
        date_str=date_for_frontmatter,
        mode_line=mode_line_p1,
    )
    reasoning_path.write_text(reasoning_doc, encoding="utf-8")
    print(f"Wrote {reasoning_path}", file=sys.stderr)

    analysis_summary = extract_analysis_summary(reasoning_doc)
    yaml_instruction = yaml_instruction_template.replace("{{ANALYSIS_SUMMARY}}", analysis_summary)
    user_p2 = (
        "Now output structured YAML for this analysis.\n\n"
        "Output only valid YAML. No thinking, no markdown fences.\n\n"
        f"{yaml_instruction}"
    )
    messages_p2: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": task},
        {"role": "assistant", "content": response1_raw},
        {"role": "user", "content": user_p2},
    ]
    print("Pass 2 (YAML, enable_thinking=False)...", file=sys.stderr)
    response2_raw = call_openai_chat(
        client,
        model,
        messages_p2,
        enable_thinking=False,
        temperature=0.4,
        max_tokens=8192,
    )
    yaml_body = _strip_yaml_fences(response2_raw)
    _validate_yaml_body(yaml_body)
    write_yaml_with_provenance(yaml_path, yaml_body, prompt_id, model)
    _validate_written_artifact(yaml_path)
    print(f"Wrote {yaml_path}", file=sys.stderr)


def run_layer_ollama(
    *,
    model: str,
    ollama_host: str,
    system: str,
    task: str,
    yaml_instruction_template: str,
    prompt_id: str,
    reasoning_path: Path,
    yaml_path: Path,
    layer_label: str,
    date_for_frontmatter: str,
) -> None:
    prompt_pass1 = f"{system}\n\n---\n\n{task}"
    print("Pass 1 (Ollama /think)...", file=sys.stderr)
    response1_raw = call_ollama_generate(
        prompt_pass1,
        model,
        use_think_suffix=True,
        temperature=0.6,
        ollama_host=ollama_host,
    )
    reasoning_doc = format_reasoning_artifact(
        response1_raw,
        layer=layer_label,
        model=model,
        date_str=date_for_frontmatter,
        mode_line="reasoning (/think)",
    )
    reasoning_path.write_text(reasoning_doc, encoding="utf-8")
    print(f"Wrote {reasoning_path}", file=sys.stderr)

    analysis_summary = extract_analysis_summary(reasoning_doc)
    yaml_instruction = yaml_instruction_template.replace("{{ANALYSIS_SUMMARY}}", analysis_summary)
    prompt_pass2 = (
        "/no_think\n\n"
        "Now output structured YAML for this analysis.\n\n"
        "Output only valid YAML. No thinking, no markdown fences.\n\n"
        f"{yaml_instruction}"
    )
    print("Pass 2 (Ollama /no_think)...", file=sys.stderr)
    response2_raw = call_ollama_generate(
        prompt_pass2,
        model,
        use_think_suffix=False,
        temperature=0.4,
        ollama_host=ollama_host,
    )
    yaml_body = _strip_yaml_fences(response2_raw)
    _validate_yaml_body(yaml_body)
    write_yaml_with_provenance(yaml_path, yaml_body, prompt_id, model)
    _validate_written_artifact(yaml_path)
    print(f"Wrote {yaml_path}", file=sys.stderr)


def main() -> None:
    prompt_help = (
        "Research layer: psychology, pain_points, event_impact (dims 1–3); "
        "narrative, platform, linguistic (dims 4–6); semantic_trend (artifacts/research/semantic_trend/)."
    )
    parser = argparse.ArgumentParser(description="Two-pass Qwen3 generational research")
    parser.add_argument("--prompt-id", required=True, choices=PROMPT_IDS, help=prompt_help)
    parser.add_argument("--paste", default=None, help="Path to raw data file, or '-' for stdin")
    parser.add_argument(
        "--model",
        default=None,
        help="Override model id (else QWEN_MODEL / docs file, or Ollama OLLAMA_MODEL)",
    )
    parser.add_argument("--skip-yaml-pass", action="store_true", help="Only run reasoning pass")
    parser.add_argument("--out-dir", default=None, help="Override artifacts/research subdir (full path)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify prompt paths exist and print config; do not call the LLM",
    )
    parser.add_argument(
        "--output-stem",
        default=None,
        metavar="STEM",
        help="Fixed filenames: <STEM>_reasoning.md and <STEM>.yaml (e.g. 2026-03-31). "
        "Default: UTC timestamp.",
    )
    parser.add_argument(
        "--prepare-deep-research-prompt",
        action="store_true",
        help="Build the pre-research brief and provider-specific deep research prompts, then exit without research execution.",
    )
    parser.add_argument(
        "--allow-legacy-direct-run",
        action="store_true",
        help="Explicitly allow the legacy direct Qwen/Ollama feed-extraction lane without prompt package generation.",
    )
    parser.add_argument("--brief-issue", default="", help="Issue/decision description for the research brief.")
    parser.add_argument(
        "--brief-failing-output",
        action="append",
        default=[],
        help="Failing output text or path. Repeatable.",
    )
    parser.add_argument(
        "--brief-relevant-file",
        action="append",
        default=[],
        help="Relevant repo file to excerpt into the research brief. Repeatable.",
    )
    parser.add_argument("--brief-context", default="", help="Additional repo or operator context for the brief.")
    parser.add_argument("--brief-title", default="", help="Override prompt package title.")
    parser.add_argument("--brief-market", action="append", default=[], help="Market hint, e.g. China or Japan.")
    parser.add_argument("--brief-locale", action="append", default=[], help="Locale hint, e.g. zh-CN or ja-JP.")
    parser.add_argument("--brief-platform", action="append", default=[], help="Platform hint. Repeatable.")
    parser.add_argument(
        "--brief-source-preference",
        action="append",
        default=[],
        help="Preferred source class, report, or domain. Repeatable.",
    )
    parser.add_argument(
        "--brief-exclude",
        action="append",
        default=[],
        help="Advice, source type, or scope to exclude. Repeatable.",
    )
    parser.add_argument(
        "--brief-out-dir",
        default=None,
        help="Output directory for prompt package. Default: artifacts/research/prompt_packages/.",
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

    if args.prepare_deep_research_prompt:
        relevant_files: dict[str, str] = {}
        for file_value in args.brief_relevant_file:
            path = Path(file_value)
            if not path.exists():
                raise FileNotFoundError(f"--brief-relevant-file does not exist: {file_value}")
            relevant_files[str(path)] = load_text(path)
        prompt_package = build_prompt_package(
            ResearchPromptInputs(
                transcript=raw_data,
                issue_description=args.brief_issue,
                failing_outputs=[load_path_or_literal(item) for item in args.brief_failing_output],
                relevant_files=relevant_files,
                repo_context=args.brief_context,
                prompt_id=prompt_id,
                title=args.brief_title,
                markets=args.brief_market,
                locales=args.brief_locale,
                platforms=args.brief_platform,
                source_preferences=args.brief_source_preference,
                exclusions=args.brief_exclude,
            )
        )
        package_dir = (
            Path(args.brief_out_dir)
            if args.brief_out_dir
            else ARTIFACTS_ROOT / "prompt_packages"
        )
        paths = write_prompt_package(prompt_package, package_dir, args.output_stem)
        print("Prepared Pearl_Research prompt package.", file=sys.stderr)
        print(f"Recommended provider: {prompt_package['routing']['provider_display_name']}", file=sys.stderr)
        print(f"Recommended prompt key: {prompt_package['recommended_prompt_key']}", file=sys.stderr)
        for label, path in paths.items():
            print(f"{label}: {path}", file=sys.stderr)
        return

    try:
        require_prompt_package_or_legacy_ack(
            prepare_deep_research_prompt=args.prepare_deep_research_prompt,
            allow_legacy_direct_run=args.allow_legacy_direct_run,
        )
    except RuntimeError as exc:
        parser.error(str(exc))

    base_url, api_key, model_hint = resolve_qwen_config()
    use_ollama = bool(base_url and is_ollama_endpoint(base_url))
    if not base_url and not api_key:
        use_ollama = True
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        resolved_model = args.model or OLLAMA_DEFAULT_MODEL
    elif use_ollama:
        ollama_host = ollama_host_from_base_url(base_url)
        resolved_model = args.model or OLLAMA_DEFAULT_MODEL
    else:
        ollama_host = ""
        if not base_url:
            print(
                "error: QWEN_BASE_URL missing (set env or docs/qwen_api_base_url.txt)",
                file=sys.stderr,
            )
            sys.exit(1)
        if not api_key:
            print(
                "error: QWEN_API_KEY missing (set env or docs/qwen_api_key.txt)",
                file=sys.stderr,
            )
            sys.exit(1)
        resolved_model = args.model or model_hint or "qwen-plus"

    system, task, yaml_instruction_template = load_layer_bundle(prompt_id, raw_data)

    if args.output_stem:
        stem = args.output_stem.strip()
        reasoning_path = out_dir / f"{stem}_reasoning.md"
        yaml_path = out_dir / f"{stem}.yaml"
        date_for_frontmatter = (
            stem if re.match(r"^\d{4}-\d{2}-\d{2}$", stem) else datetime.utcnow().strftime("%Y-%m-%d")
        )
    else:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        reasoning_path = out_dir / f"{ts}_reasoning.md"
        yaml_path = out_dir / f"{ts}.yaml"
        date_for_frontmatter = datetime.utcnow().strftime("%Y-%m-%d")

    layer_label = cfg["artifacts_subdir"]

    if use_ollama:
        if args.skip_yaml_pass:
            prompt_pass1 = f"{system}\n\n---\n\n{task}"
            response1_raw = call_ollama_generate(
                prompt_pass1,
                resolved_model,
                use_think_suffix=True,
                temperature=0.6,
                ollama_host=ollama_host,
            )
            reasoning_doc = format_reasoning_artifact(
                response1_raw,
                layer=layer_label,
                model=resolved_model,
                date_str=date_for_frontmatter,
                mode_line="reasoning (/think)",
            )
            reasoning_path.write_text(reasoning_doc, encoding="utf-8")
            print(f"Wrote {reasoning_path}", file=sys.stderr)
            return
        run_layer_ollama(
            model=resolved_model,
            ollama_host=ollama_host,
            system=system,
            task=task,
            yaml_instruction_template=yaml_instruction_template,
            prompt_id=prompt_id,
            reasoning_path=reasoning_path,
            yaml_path=yaml_path,
            layer_label=layer_label,
            date_for_frontmatter=date_for_frontmatter,
        )
        return

    client = create_openai_client(base_url, api_key)
    if args.skip_yaml_pass:
        messages_p1 = [
            {"role": "system", "content": system},
            {"role": "user", "content": task},
        ]
        response1_raw = call_openai_chat(
            client,
            resolved_model,
            messages_p1,
            enable_thinking=True,
            temperature=0.6,
            max_tokens=16384,
        )
        reasoning_doc = format_reasoning_artifact(
            response1_raw,
            layer=layer_label,
            model=resolved_model,
            date_str=date_for_frontmatter,
            mode_line="reasoning (enable_thinking=True)",
        )
        reasoning_path.write_text(reasoning_doc, encoding="utf-8")
        print(f"Wrote {reasoning_path}", file=sys.stderr)
        return

    run_layer_openai(
        client=client,
        model=resolved_model,
        system=system,
        task=task,
        yaml_instruction_template=yaml_instruction_template,
        prompt_id=prompt_id,
        reasoning_path=reasoning_path,
        yaml_path=yaml_path,
        layer_label=layer_label,
        date_for_frontmatter=date_for_frontmatter,
        mode_line_p1="reasoning (enable_thinking=True)",
    )


if __name__ == "__main__":
    main()
