#!/usr/bin/env python3
"""Add phoenix_lead bypass to public/breathwork/lp-*.html landing pages."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LP_DIR = REPO / "public" / "breathwork"

LEAD_SCRIPT = '<script src="/free/js/phoenix_lead.js"></script>\n'
INIT_SNIPPET = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  if (!window.PhoenixLead) return;
  var toolUrl = typeof TOOL_URL !== 'undefined' ? TOOL_URL : (document.getElementById('toolLink') && document.getElementById('toolLink').getAttribute('href'));
  if (toolUrl && toolUrl.indexOf('somatic_exercise') < 0 && toolUrl.indexOf('tools/') === 0) {
    toolUrl = '/somatic_exercise_freebee_apps/' + toolUrl.replace(/^tools\\//, '').replace(/\\.html$/, '') + '.html';
    var map = {
      'cyclic-sighing': 'app26_cyclic_sighing.html',
      'box-breathing': 'ex02_box_breathing.html',
      '478-breathing': 'ex01_478_breathing.html',
      'body-scan': 'ex13_body_scan.html'
    };
    var key = toolUrl.split('/').pop().replace('.html','');
    for (var k in map) {
      if (toolUrl.indexOf(k) >= 0) { toolUrl = '/somatic_exercise_freebee_apps/' + map[k]; break; }
    }
  }
  PhoenixLead.initBreathworkLanding({ toolUrl: toolUrl || '#' });
});
</script>
"""


def main() -> int:
    patched = 0
    for path in sorted(LP_DIR.glob("lp-*.html")):
        text = path.read_text(encoding="utf-8")
        if "phoenix_lead.js" in text:
            continue
        if "</body>" not in text:
            continue
        if "/free/js/phoenix_lead.js" not in text:
            text = text.replace("</body>", LEAD_SCRIPT + INIT_SNIPPET + "\n</body>", 1)
        path.write_text(text, encoding="utf-8")
        patched += 1
    print(f"Patched {patched} breathwork LPs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
