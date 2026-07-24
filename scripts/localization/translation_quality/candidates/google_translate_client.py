#!/usr/bin/env python3
"""Google Cloud Translation API (v2, "Basic") candidate client.

**Confirmed distinction (per this lane's brief): this hits
`https://translation.googleapis.com/language/translate/v2` -- the
dedicated Google Cloud Translation product -- NOT the Gemini / "Google AI"
generative-language endpoint, and does NOT import the Google Generative AI
Python package (that import is the banned one, see
`config/governance/banned_llm_patterns.yaml` -> `google_genai`). This
module makes a plain REST call via `urllib` specifically to avoid pulling
in any Google GenAI SDK by accident. (The banned import path is
intentionally not spelled out literally in this docstring -- spelling it
out trips scripts/ci/audit_llm_callers.py on the docstring text itself,
not a real import; see banned_llm_patterns.yaml directly for the literal
pattern.)

Auth: `GOOGLE_TRANSLATE_API_KEY` (confirmed present in Keychain per this
lane's pre-requisite check, tracked in
scripts/ci/integration_env_registry.py). This is a simple API-key REST
call, no OAuth/service-account flow.

Usage:
    python3 scripts/localization/translation_quality/candidates/google_translate_client.py \\
        --source-locale en --target-locale zh-CN --text-file source.txt
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.translation_quality.candidates import CandidateResult  # noqa: E402

TRANSLATE_V2_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

# Google Cloud Translation locale codes differ slightly from Phoenix's
# BCP-47 codes for a couple of CJK targets -- map explicitly rather than
# guessing at request time.
_LOCALE_TO_GOOGLE_LANG = {
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
    "zh-HK": "zh-TW",  # Google Translate has no distinct zh-HK target; zh-TW is the closest supported code
    "zh-SG": "zh-CN",
    "ja-JP": "ja",
    "ko-KR": "ko",
    "es-US": "es",
    "es-ES": "es",
    "pt-BR": "pt",
    "fr-FR": "fr",
    "de-DE": "de",
    "it-IT": "it",
    "hu-HU": "hu",
    "en-US": "en",
}


class GoogleTranslateAuthError(RuntimeError):
    pass


def _google_lang(locale: str) -> str:
    return _LOCALE_TO_GOOGLE_LANG.get(locale, locale.split("-")[0])


def translate(
    text: str,
    *,
    source_locale: str = "en-US",
    target_locale: str = "zh-CN",
    api_key: str | None = None,
    timeout: float = 30.0,
) -> CandidateResult:
    key = api_key or os.environ.get("GOOGLE_TRANSLATE_API_KEY", "").strip()
    if not key:
        raise GoogleTranslateAuthError(
            "GOOGLE_TRANSLATE_API_KEY is not set. Load it via "
            "scripts/ci/load_integration_env_from_keychain.py before calling."
        )

    payload = {
        "q": text,
        "source": _google_lang(source_locale),
        "target": _google_lang(target_locale),
        "format": "text",
    }
    url = f"{TRANSLATE_V2_ENDPOINT}?key={urllib.parse.quote(key)}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google Translate API HTTP {exc.code}: {detail}") from exc

    translations = body.get("data", {}).get("translations", [])
    if not translations:
        raise RuntimeError(f"Google Translate API returned no translations: {body}")
    out_text = translations[0]["translatedText"]
    detected_source = translations[0].get("detectedSourceLanguage")

    return CandidateResult(
        candidate_id="google_translate_v2",
        text=out_text,
        meta={
            "endpoint": TRANSLATE_V2_ENDPOINT,
            "source_locale": source_locale,
            "target_locale": target_locale,
            "detected_source_language": detected_source,
        },
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-locale", default="en-US")
    ap.add_argument("--target-locale", required=True)
    ap.add_argument("--text-file", type=Path, required=True)
    args = ap.parse_args(argv)

    text = args.text_file.read_text(encoding="utf-8")
    try:
        result = translate(text, source_locale=args.source_locale, target_locale=args.target_locale)
    except GoogleTranslateAuthError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(result.text)
    print(f"\n--- meta: {result.meta}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
