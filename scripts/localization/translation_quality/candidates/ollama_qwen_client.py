#!/usr/bin/env python3
"""Ollama/Qwen candidate client -- the default, always-available candidate.

Thin wrapper over the existing scripts/localization/llm_client.py Ollama
path (Tier-2, local, free, unattended-safe per CLAUDE.md's LLM Tier
Policy). Does not duplicate llm_client.py's provider-selection logic --
delegates to it entirely.

Usage:
    python3 scripts/localization/translation_quality/candidates/ollama_qwen_client.py \\
        --source-locale en-US --target-locale zh-CN --text-file source.txt

    from scripts.localization.translation_quality.candidates.ollama_qwen_client import (
        translate,
    )
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.llm_client import call_llm_with_meta  # noqa: E402
from scripts.localization.translation_quality.candidates import CandidateResult  # noqa: E402

DEFAULT_SYSTEM_PROMPT = (
    "You are a professional literary translator. Translate the user's text "
    "from {source_locale} to {target_locale}. Preserve every placeholder "
    "token in {{curly_braces}}, every Markdown link, every HTML tag, and "
    "every URL exactly as given. Output ONLY the translation, no commentary."
)


def translate(
    text: str,
    *,
    source_locale: str = "en-US",
    target_locale: str = "zh-CN",
    model_cfg: dict | None = None,
) -> CandidateResult:
    cfg = model_cfg or {"draft_model": {}}
    system_prompt = DEFAULT_SYSTEM_PROMPT.format(
        source_locale=source_locale, target_locale=target_locale
    )
    out_text, meta = call_llm_with_meta(system_prompt, text, cfg, role="draft")
    meta["source_locale"] = source_locale
    meta["target_locale"] = target_locale
    model_id = meta.get("model_requested", "qwen2.5:14b")
    return CandidateResult(candidate_id=f"ollama_{model_id}", text=out_text, meta=meta)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-locale", default="en-US")
    ap.add_argument("--target-locale", required=True)
    ap.add_argument("--text-file", type=Path, required=True)
    args = ap.parse_args(argv)

    text = args.text_file.read_text(encoding="utf-8")
    result = translate(text, source_locale=args.source_locale, target_locale=args.target_locale)
    print(result.text)
    print(f"\n--- meta: {result.meta}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
