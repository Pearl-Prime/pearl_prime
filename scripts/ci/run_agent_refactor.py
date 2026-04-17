#!/usr/bin/env python3
"""
run_agent_refactor.py — Generic Claude API agent that reads a spec, analyses the
target scope, produces code changes, and commits them to the current branch.

Used by P0.6, P0.9, ACT-012 through ACT-015, and future agent workflows.

Usage:
    python3 scripts/ci/run_agent_refactor.py \
        --task p0-6-content-bank-refactor \
        --branch agent/p0-6-content-bank-refactor-20260417 \
        --specs artifacts/analysis/bestseller_action_plan.md \
        --scope "phoenix_v4/rendering/book_renderer.py phoenix_v4/planning/enrichment_select.py" \
        --requirements "Remove _LOC_VAR_FALLBACKS ..." \
        [--context-file path/to/extra_context.txt] \
        [--dry-run true]

Environment:
    ANTHROPIC_API_KEY — required

Exit codes:
    0 — success (changes made or dry-run complete)
    1 — agent produced no actionable output
    2 — API error / missing credentials
"""
import argparse
import os
import subprocess
import sys
import textwrap
from pathlib import Path


MAX_FILE_CHARS = 60_000   # truncate large files before sending to Claude
MAX_SCOPE_FILES = 10


def parse_args():
    p = argparse.ArgumentParser(description="Claude API refactor agent")
    p.add_argument("--task", required=True, help="Task identifier (for logging)")
    p.add_argument("--branch", required=True, help="Current git branch name")
    p.add_argument("--requirements", required=True, help="Natural-language requirements for the agent")
    p.add_argument("--specs", help="Path to spec/action-plan markdown file")
    p.add_argument("--scope", help="Space-separated file paths to read as context")
    p.add_argument("--context-file", help="Extra context file (e.g. grep output)")
    p.add_argument("--dry-run", default="false", help="If 'true', produce plan only — no file writes")
    return p.parse_args()


def read_file_safe(path: str, max_chars: int = MAX_FILE_CHARS) -> str:
    try:
        content = Path(path).read_text()
        if len(content) > max_chars:
            return content[:max_chars] + f"\n\n[... truncated at {max_chars} chars ...]"
        return content
    except Exception as e:
        return f"[Could not read {path}: {e}]"


def get_current_files_content(scope_str: str) -> str:
    if not scope_str:
        return ""
    parts = []
    for path in scope_str.split()[:MAX_SCOPE_FILES]:
        content = read_file_safe(path)
        parts.append(f"### File: {path}\n```python\n{content}\n```")
    return "\n\n".join(parts)


def build_prompt(args) -> str:
    dry_run = args.dry_run.lower() == "true"

    sections = [
        f"# Agent Task: {args.task}",
        f"Branch: `{args.branch}`",
        "",
        "## Requirements",
        args.requirements,
        "",
    ]

    if args.specs and Path(args.specs).exists():
        spec_content = read_file_safe(args.specs, max_chars=20_000)
        sections += [
            "## Governing Spec (excerpted)",
            f"```markdown\n{spec_content}\n```",
            "",
        ]

    if args.context_file and Path(args.context_file).exists():
        ctx = read_file_safe(args.context_file, max_chars=10_000)
        sections += [
            "## Additional Context",
            f"```\n{ctx}\n```",
            "",
        ]

    if args.scope:
        file_contents = get_current_files_content(args.scope)
        if file_contents:
            sections += [
                "## Current File Contents (scope)",
                file_contents,
                "",
            ]

    if dry_run:
        sections += [
            "## Mode: DRY RUN",
            "Produce a **plan only**. List every file you would change, what you would change,",
            "and why. Do NOT produce actual code diffs. End with `PLAN_COMPLETE`.",
        ]
    else:
        sections += [
            "## Mode: IMPLEMENT",
            "Produce complete file contents for every file that needs to change.",
            "Format each file as:",
            "```",
            "### WRITE_FILE: path/to/file.py",
            "<complete file content>",
            "### END_FILE",
            "```",
            "",
            "Rules:",
            "- Only output files that actually need to change.",
            "- Do not truncate — output complete file content.",
            "- Include all existing code plus your additions/changes.",
            "- Add docstrings to new functions.",
            "- Follow existing code style.",
            "- If you cannot safely make a change, explain why and output `SKIP_FILE: path reason`.",
            "- End with `IMPLEMENTATION_COMPLETE`.",
        ]

    return "\n".join(sections)


def call_claude_api(prompt: str) -> str:
    """Call Claude API via the anthropic SDK."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic SDK not installed. Run: pip install anthropic", file=sys.stderr)
        sys.exit(2)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(2)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Calling Claude API (prompt length: {len(prompt)} chars)...", file=sys.stderr)
    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}", file=sys.stderr)
        sys.exit(2)


def apply_file_writes(response: str, dry_run: bool) -> int:
    """Parse WRITE_FILE blocks from the response and apply them."""
    import re

    file_blocks = re.findall(
        r"### WRITE_FILE: (.+?)\n(.*?)### END_FILE",
        response,
        re.DOTALL,
    )

    if not file_blocks:
        print("No WRITE_FILE blocks found in agent response.", file=sys.stderr)
        return 0

    written = 0
    for path_str, content in file_blocks:
        path_str = path_str.strip()
        content = content.strip()

        if dry_run:
            print(f"[DRY RUN] Would write: {path_str} ({len(content)} chars)", file=sys.stderr)
            written += 1
            continue

        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        print(f"Written: {path_str} ({len(content)} chars)", file=sys.stderr)
        written += 1

    # Check for SKIP_FILE entries and log them
    skip_blocks = re.findall(r"SKIP_FILE: (.+?)$", response, re.MULTILINE)
    for skip in skip_blocks:
        print(f"Agent skipped: {skip}", file=sys.stderr)

    return written


def main():
    args = parse_args()
    dry_run = args.dry_run.lower() == "true"

    if dry_run:
        print(f"[{args.task}] DRY RUN mode — no files will be written.", file=sys.stderr)

    prompt = build_prompt(args)
    print(f"[{args.task}] Prompt built ({len(prompt)} chars). Calling API...", file=sys.stderr)

    response = call_claude_api(prompt)

    # Save raw response for debugging
    Path("artifacts").mkdir(exist_ok=True)
    raw_out = Path(f"artifacts/{args.task}-raw-response.txt")
    raw_out.write_text(response)
    print(f"Raw response saved to {raw_out}", file=sys.stderr)

    if dry_run:
        print("=== DRY RUN PLAN ===")
        print(response)
        sys.exit(0)

    # Apply file writes
    n_written = apply_file_writes(response, dry_run=False)
    print(f"[{args.task}] Files written: {n_written}", file=sys.stderr)

    if n_written == 0:
        print("WARNING: Agent produced no file writes.", file=sys.stderr)
        print(response[:2000])
        sys.exit(1)

    print(f"[{args.task}] Implementation complete. {n_written} files written.", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
