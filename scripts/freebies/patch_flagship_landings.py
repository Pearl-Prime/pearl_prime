#!/usr/bin/env python3
"""Inject phoenix_lead + single-capture wiring into top-5 flagship funnel landings."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FREE = REPO / "brand-wizard-app" / "public" / "free"

FLAGSHIPS = {
    "anxiety-nervous-system-reset": {
        "topic": "anxiety",
        "funnel_slug": "anxiety-nervous-system-reset",
        "quiz_id": "breath_timer",
        "form_id": "capture-section",
        "tool_id": "tool-section",
        "somatic": "ex01_478_breathing.html",
        "somatic_label": "Try the 4-7-8 practice I use when the alarm won't shut off",
        "somatic_container": None,
        "hook": "90-second reset that shuts off my alarm system — works for me every time",
        "subhead_class": "subtitle",
        "capture_handler": "capture-form",
    },
    "overthinking-thought-sorter": {
        "topic": "overthinking",
        "funnel_slug": "overthinking-thought-sorter",
        "quiz_id": "thought_sorter_assessment",
        "form_id": "capture-section",
        "tool_id": "tool-section",
        "somatic": "ex02_box_breathing.html",
        "somatic_label": "Try the box-breath reset I use when loops won't stop",
        "somatic_container": "somatic-result-link",
        "hook": "I sorted my brain loops in 2 minutes — this is the exact sorter I use",
        "subhead_class": "subtitle",
        "capture_handler": "capture-form",
        "email_before_result": True,
    },
    "financial-anxiety-check-in": {
        "topic": "financial_anxiety",
        "funnel_slug": "financial-anxiety-check-in",
        "quiz_id": "financial_checkin",
        "form_id": "form-section",
        "tool_id": "tool-section",
        "somatic": "ex04_extended_exhale.html",
        "somatic_label": "Try the extended-exhale reset I use when money panic hits",
        "somatic_container": "somatic-result-link",
        "hook": "Your bank balance isn't the whole story — this 10-question check is what I use",
        "subhead_class": "subhead",
        "capture_handler": "submitForm",
        "email_before_result": True,
    },
    "courage-decision-map": {
        "topic": "courage",
        "funnel_slug": "courage-decision-map",
        "quiz_id": "decision_resistance_map",
        "form_id": "capture-section",
        "tool_id": "tool-section",
        "somatic": "ex15_intention_quadrant.html",
        "somatic_label": "Try the intention quadrant I use before hard decisions",
        "somatic_container": "somatic-result-link",
        "hook": "The thing I've been avoiding — mapped in 6 steps. This is my protocol",
        "subhead_class": "subtitle",
        "capture_handler": "capture-form",
        "email_before_result": True,
    },
}

ASSETS = """
<link rel="stylesheet" href="/free/js/phoenix_tool.css">
<script src="/free/js/phoenix_lead.js"></script>
<script src="/free/js/phoenix_funnel.js"></script>
"""

EMAIL_GATE_BLOCK = """
    <div id="email-gate-section" class="card phoenix-email-gate" style="display:none;">
      <h2 style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;margin-bottom:8px;">Get your result + next practice</h2>
      <p style="color:#8B8A82;font-size:14px;margin-bottom:20px;">One email. No spam. Then your personalized result unlocks.</p>
      <div class="form-group">
        <label for="gate-name">First name</label>
        <input type="text" id="gate-name" placeholder="Your name">
      </div>
      <div class="form-group">
        <label for="gate-email">Email</label>
        <input type="email" id="gate-email" placeholder="your@email.com">
      </div>
      <p id="gate-error" class="error-msg" style="display:none;">Please enter a valid email.</p>
      <button class="btn" type="button" onclick="submitEmailGate()">Show My Result</button>
    </div>
"""

def _inject_assets(text: str) -> str:
    if "phoenix_funnel.js" in text:
        return text
    return text.replace("</body>", ASSETS + "\n</body>", 1)


def _inject_hook(text: str, meta: dict) -> str:
    hook = meta.get("hook") or ""
    cls = meta.get("subhead_class") or "subhead"
    marker = f'<p class="{cls}">'
    if hook and marker in text and hook[:24] not in text:
        text = text.replace(marker, f"{marker}{hook}. ", 1)
    return text


def _hide_top_capture(text: str, form_id: str) -> str:
    needle = f'id="{form_id}"'
    if needle not in text:
        return text
    return text.replace(f'<div class="capture-card" id="{form_id}">', f'<div class="capture-card" id="{form_id}" style="display:none;">', 1).replace(
        f'<div id="{form_id}" class="card">', f'<div id="{form_id}" class="card" style="display:none;">', 1
    )


def _show_tool_on_load(text: str, tool_id: str) -> str:
    if f"id=\"{tool_id}\"" not in text:
        return text
    if "tool-section visible" in text or f'id="{tool_id}" class="visible"' in text:
        return text
    text = text.replace(f'<div id="{tool_id}">', f'<div id="{tool_id}" class="visible" style="display:block;">', 1)
    return text


def _inject_email_gate(text: str, tool_id: str) -> str:
    if "email-gate-section" in text:
        return text
    anchor = f'<div id="{tool_id}"'
    idx = text.find(anchor)
    if idx < 0:
        return text
    close = text.find(">", idx) + 1
    return text[:close] + EMAIL_GATE_BLOCK + text[close:]


def _inject_somatic_container(text: str, container_id: str) -> str:
    if not container_id or f'id="{container_id}"' in text:
        return text
    return text.replace(
        "</div>\n\n  <div class=\"cta-banner\">",
        f'</div>\n      <div id="{container_id}"></div>\n\n  <div class="cta-banner">',
        1,
    ).replace(
        "</div>\n\n      <div class=\"cta-banner\">",
        f'</div>\n        <div id="{container_id}"></div>\n\n      <div class="cta-banner">',
        1,
    )


def _inject_bootstrap(text: str, meta: dict) -> str:
    marker = "PHOENIX_FLAGSHIP_BOOTSTRAP"
    if marker in text:
        return text
    on_unlock_lines = []
    if meta.get("email_before_result"):
        on_unlock_lines.append("if (typeof buildQuestions === 'function') buildQuestions();")
        on_unlock_lines.append("if (typeof renderQuestions === 'function') renderQuestions();")
    else:
        on_unlock_lines.append("if (typeof buildQuestions === 'function') buildQuestions();")
    on_unlock = "\n    ".join(on_unlock_lines)
    somatic = ""
    if meta.get("somatic_container") and meta.get("somatic"):
        somatic = (
            "if (typeof revealPendingResult === 'function') {"
            " var _orig = revealPendingResult; revealPendingResult = function() { _orig(); "
            f"PhoenixFunnel.injectSomaticResultLink('{meta['somatic_container']}', '{meta['somatic']}', '{meta['somatic_label']}'); }};"
        )
    block = (
        "<script>\n"
        "document.addEventListener('DOMContentLoaded', function() {\n"
        "  if (!window.PhoenixFunnel) return;\n"
        f"  PhoenixFunnel.initSkipFormIfCaptured('{meta['form_id']}', '{meta['tool_id']}', function() {{\n"
        f"    {on_unlock}\n"
        "  });\n"
        "  PhoenixFunnel.bindEmailBeforeResult({\n"
        f"    topic: '{meta['topic']}',\n"
        f"    funnelSlug: '{meta['funnel_slug']}',\n"
        f"    quizId: '{meta['quiz_id']}',\n"
        "    pendingScore: window.pendingScore,\n"
        "    pendingScoreBand: window.pendingScoreBand,\n"
        "    onSuccess: function() { if (typeof revealPendingResult === 'function') revealPendingResult(); }\n"
        "  });\n"
        f"  {somatic}\n"
        "});\n"
        "</script>"
    )
    return text.replace("</body>", f"<!-- {marker} -->\n{block}\n</body>", 1)


def _patch_overthinking_js(text: str, meta: dict) -> str:
    if "revealPendingResult" in text:
        return text
    gate_fn = """
  function revealPendingResult() {
    showResult();
    if (window.PhoenixFunnel) {
      PhoenixFunnel.injectSomaticResultLink('somatic-result-link', '%s', '%s');
    }
  }

  function requestResults() {
    if (window.PhoenixLead && PhoenixLead.shouldShowEmailGate()) {
      document.getElementById('email-gate-section').style.display = 'block';
      return;
    }
    revealPendingResult();
  }
""" % (meta["somatic"], meta["somatic_label"])
    text = text.replace("function showResult() {", gate_fn + "\n  function showResult() {", 1)
    text = text.replace(
        "document.getElementById('qnext-' + i).onclick = nextQ(${i})",
        "",
    )
    text = text.replace(
        "${isLast ? 'See My Result' : 'Next &rarr;'}",
        "${isLast ? 'See My Result' : 'Next &rarr;'}",
    )
    text = text.replace(
        'onclick="nextQ(${i})" disabled>${isLast ? \'See My Result\' : \'Next &rarr;\'}</button>',
        'onclick="' + ("requestResults()" if False else "") + '" disabled>${isLast ? \'See My Result\' : \'Next &rarr;\'}</button>',
    )
    # Patch last-question button to call requestResults instead of showResult path
    text = text.replace(
        '<button class="btn-qnext" id="qnext-${i}" onclick="nextQ(${i})" disabled>${isLast ? \'See My Result\' : \'Next &rarr;\'}</button>',
        '<button class="btn-qnext" id="qnext-${i}" onclick="${isLast ? \'requestResults()\' : \'nextQ(\' + i + \')\'}\" disabled>${isLast ? \'See My Result\' : \'Next &rarr;\'}</button>',
    )
    # Fix nextQ to gate on last question
    old = """    if (next >= questions.length) {
      showResult();
      return;
    }"""
    new = """    if (next >= questions.length) {
      requestResults();
      return;
    }"""
    return text.replace(old, new, 1)


def _patch_financial_js(text: str, meta: dict) -> str:
    if "revealPendingResult" in text:
        return text
    extra = """
    let pendingScore = null;
    function revealPendingResult() {
      const total = pendingScore;
      document.getElementById('questions-block').style.display = 'none';
      document.getElementById('submit-block').style.display = 'none';
      document.getElementById('email-gate-section').style.display = 'none';
      document.getElementById('results-block').style.display = 'block';
      document.getElementById('result-score').textContent = total;
      const msgs = [
        "Your money relationship is relatively stable. The check-in is good practice.",
        "You're carrying a real money anxiety load. It's running in the background more than you realize.",
        "Money anxiety is a significant strain on your daily experience. The pattern is learnable and changeable."
      ];
      document.getElementById('result-message').textContent = total <= 10 ? msgs[0] : total <= 20 ? msgs[1] : msgs[2];
      if (window.PhoenixFunnel) {
        PhoenixFunnel.injectSomaticResultLink('somatic-result-link', '%s', '%s');
      }
    }
    function scoreAudit() {
      let total = 0;
      for (let i = 0; i < questions.length; i++) {
        const checked = document.querySelector(`input[name="q${i}"]:checked`);
        if (!checked) {
          document.getElementById('audit-error').style.display = 'block';
          return;
        }
        total += parseInt(checked.value);
      }
      pendingScore = total;
      if (window.PhoenixLead && PhoenixLead.shouldShowEmailGate()) {
        document.getElementById('email-gate-section').style.display = 'block';
        return;
      }
      revealPendingResult();
    }
""" % (meta["somatic"], meta["somatic_label"])
    # Replace old scoreAudit function
    start = text.find("    function scoreAudit() {")
    end = text.find("    }\n  </script>", start)
    if start >= 0 and end >= 0:
        text = text[:start] + extra.strip() + "\n" + text[end + 6 :]
    # Remove top form submit path — tool visible on load handled by bootstrap
    text = text.replace("document.getElementById('tool-section').style.display = 'block';\n      buildQuestions();", "buildQuestions();")
    return text


def _patch_courage_js(text: str, meta: dict) -> str:
    if "revealPendingResult" in text:
        return text
    extra = """
  function revealPendingResult() {
    document.getElementById('completion-card').classList.add('visible');
    if (window.PhoenixFunnel) {
      PhoenixFunnel.injectSomaticResultLink('somatic-result-link', '%s', '%s');
    }
  }
  function completeMap() {
    if (window.PhoenixLead && PhoenixLead.shouldShowEmailGate()) {
      document.getElementById('email-gate-section').style.display = 'block';
      return;
    }
    revealPendingResult();
  }
""" % (meta["somatic"], meta["somatic_label"])
    text = text.replace("  function advance(fromStep) {", extra + "\n  function advance(fromStep) {", 1)
    old = """    if (fromStep >= totalSteps) {
      document.getElementById('completion-card').classList.add('visible');
      return;
    }"""
    new = """    if (fromStep >= totalSteps) {
      completeMap();
      return;
    }"""
    return text.replace(old, new, 1)


def _patch_anxiety_capture(text: str, meta: dict) -> str:
    if "PhoenixLead.captureLead" in text:
        return text
    old = """  document.getElementById('capture-form').addEventListener('submit', function(e) {
    e.preventDefault();
    // GA4 lead_submit
    if (typeof gtag === 'function') {
      gtag('event', 'lead_submit', {
        event_category: 'funnel',
        event_label: 'anxiety-nervous-system-reset',
        topic: 'anxiety',
        value: 0
      });
    }

    document.getElementById('capture-section').style.display = 'none';
    document.getElementById('tool-section').classList.add('visible');
  });"""
    new = """  document.getElementById('capture-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var nameEl = document.querySelector('#capture-form input[type="text"]');
    var emailEl = document.querySelector('#capture-form input[type="email"]');
    var name = nameEl ? nameEl.value.trim() : '';
    var email = emailEl ? emailEl.value.trim() : '';
    if (!window.PhoenixLead) {
      document.getElementById('capture-section').style.display = 'none';
      document.getElementById('tool-section').classList.add('visible');
      return;
    }
    PhoenixLead.captureLead({
      email: email,
      first_name: name,
      topic: 'anxiety',
      funnel_slug: 'anxiety-nervous-system-reset',
      quiz_id: 'breath_timer',
      tags: ['quiz_anxiety']
    }).then(function() {
      document.getElementById('capture-section').style.display = 'none';
      document.getElementById('tool-section').classList.add('visible');
    }).catch(function() {
      document.getElementById('capture-section').style.display = 'none';
      document.getElementById('tool-section').classList.add('visible');
    });
  });"""
    return text.replace(old, new, 1)


def main() -> int:
    for slug, meta in FLAGSHIPS.items():
        path = FREE / slug / "index.html"
        if not path.exists():
            print(f"missing: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        text = _inject_hook(text, meta)
        if meta.get("email_before_result"):
            text = _hide_top_capture(text, meta["form_id"])
            text = _show_tool_on_load(text, meta["tool_id"])
            text = _inject_email_gate(text, meta["tool_id"])
            text = _inject_somatic_container(text, meta.get("somatic_container"))
        text = _inject_assets(text)
        text = _inject_bootstrap(text, meta)
        if slug == "overthinking-thought-sorter":
            text = _patch_overthinking_js(text, meta)
        elif slug == "financial-anxiety-check-in":
            text = _patch_financial_js(text, meta)
        elif slug == "courage-decision-map":
            text = _patch_courage_js(text, meta)
        elif slug == "anxiety-nervous-system-reset":
            text = _patch_anxiety_capture(text, meta)
        path.write_text(text, encoding="utf-8")
        print(f"patched {slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
