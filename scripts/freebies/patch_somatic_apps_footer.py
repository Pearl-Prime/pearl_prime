#!/usr/bin/env python3
"""Inject phoenix_lead.js footer into somatic_exercise_freebee_apps/*.html."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APPS_DIR = REPO / "somatic_exercise_freebee_apps"

MARKER = "<!-- phoenix-lead-footer -->"
INJECT = """
<!-- phoenix-lead-footer -->
<link rel="stylesheet" href="/free/js/phoenix_tool.css">
<script src="/free/js/phoenix_lead.js"></script>
<script>
  if (window.PhoenixLead) {
    PhoenixLead.initToolPage({
      footerCta: "This reset works for me every time. The full system is in the book — try it and see."
    });
  }
</script>
"""


def main() -> int:
    patched = 0
    for path in sorted(APPS_DIR.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        if "</body>" not in text:
            print(f"skip (no body): {path.name}")
            continue
        text = text.replace("</body>", INJECT + "\n</body>", 1)
        path.write_text(text, encoding="utf-8")
        patched += 1
    print(f"Patched {patched} somatic apps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
