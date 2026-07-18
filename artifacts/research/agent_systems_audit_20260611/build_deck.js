// Builds AGENT_SYSTEM_IMPROVEMENT_DECK.pptx — Pearl Prime tokens.
// Palette: ink #0e0a06 (near-black), cream #faf6f0, amber #d97706.
const pptxgen = require("pptxgenjs");

const INK = "0E0A06";      // near-black background
const INK2 = "1C160F";     // slightly lifted ink for cards on dark
const CREAM = "FAF6F0";    // light background / light text
const CREAM2 = "EFE7DB";   // muted cream
const AMBER = "D97706";    // accent
const AMBER_LT = "F0B370"; // lighter amber for secondary accents
const MUTE = "8A7E70";     // muted brown-grey text
const GREEN = "4F7A52";    // "doing" green (subtle, on-brand muted)
const RED = "B05438";      // gap terracotta (on-brand, not pure red)

const HF = "Georgia";      // header font (personality)
const BF = "Calibri";      // body font

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Pearl_Research";
pres.title = "Agent System Improvement — SOTA Audit";
const W = 13.3, H = 7.5;

const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.22 });

// ---- helpers ----
function accentBar(slide, color = AMBER) {
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.18, h: H, fill: { color } });
}
function footer(slide, n) {
  slide.addText("Phoenix Omega · Agent + Skills + Systems-Tooling SOTA Audit · 2026-06-11",
    { x: 0.6, y: H - 0.42, w: 10.5, h: 0.3, fontSize: 9, color: MUTE, fontFace: BF, align: "left" });
  slide.addText(String(n), { x: W - 0.9, y: H - 0.42, w: 0.5, h: 0.3, fontSize: 9, color: MUTE, fontFace: BF, align: "right" });
}
function numCircle(slide, x, y, label, d = 0.42, fill = AMBER, txt = INK) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill } });
  slide.addText(label, { x, y: y - 0.01, w: d, h: d, fontSize: 15, bold: true, color: txt, align: "center", valign: "middle", fontFace: BF, margin: 0 });
}
function card(slide, x, y, w, h, fill = INK2) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: AMBER, width: 0.5 }, shadow: shadow() });
}

// ===================== SLIDE 1 — TITLE (dark) =====================
{
  const s = pres.addSlide();
  s.background = { color: INK };
  // amber motif: thin top rule + big offset block
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.12, fill: { color: AMBER } });
  s.addShape(pres.shapes.RECTANGLE, { x: 8.7, y: 1.0, w: 4.6, h: 5.5, fill: { color: INK2 } });
  s.addText("PEARL RESEARCH", { x: 0.8, y: 1.3, w: 7, h: 0.4, fontSize: 14, color: AMBER, bold: true, charSpacing: 4, fontFace: BF });
  s.addText([
    { text: "Are our agents,", options: { breakLine: true } },
    { text: "skills & systems", options: { breakLine: true } },
    { text: "using the best", options: { breakLine: true } },
    { text: "of what exists?" },
  ], { x: 0.8, y: 1.85, w: 7.6, h: 3.6, fontSize: 40, bold: true, color: CREAM, fontFace: HF, lineSpacingMultiple: 1.0, valign: "top" });
  s.addText("2025–2026 SOTA audit · roadmap · operator deck",
    { x: 0.8, y: 5.6, w: 7.6, h: 0.5, fontSize: 16, color: CREAM2, italic: true, fontFace: BF });
  // right-block stat stack
  const stats = [["9", "patterns already DOING"], ["6", "agent + 5 skill GAPS"], ["30+", "cited sources"], ["6", "P0 quick wins"]];
  let yy = 1.35;
  stats.forEach(([n, l]) => {
    s.addText(n, { x: 9.0, y: yy, w: 1.7, h: 0.8, fontSize: 40, bold: true, color: AMBER, fontFace: HF, align: "left", valign: "middle", margin: 0 });
    s.addText(l, { x: 10.5, y: yy + 0.08, w: 2.6, h: 0.7, fontSize: 12, color: CREAM2, fontFace: BF, align: "left", valign: "middle", margin: 0 });
    yy += 1.22;
  });
  s.addText("Extends docs/AGENT_SYSTEM_AUDIT_2026_04.md — does not re-litigate it.",
    { x: 0.8, y: 6.55, w: 8, h: 0.3, fontSize: 11, color: MUTE, fontFace: BF });
}

// ===================== SLIDE 2 — Verdict at a glance (light) =====================
{
  const s = pres.addSlide();
  s.background = { color: CREAM };
  accentBar(s);
  s.addText("The verdict in one slide", { x: 0.6, y: 0.45, w: 11, h: 0.7, fontSize: 32, bold: true, color: INK, fontFace: HF });
  s.addText("Architecture: strong. Instrumentation & self-improvement loops: the gap.",
    { x: 0.62, y: 1.15, w: 11.5, h: 0.4, fontSize: 15, color: MUTE, italic: true, fontFace: BF });

  const cols = [
    ["9", "ALREADY DOING", GREEN, "Orchestrator-worker, isolated workers, separate verify pass, externalized state, cost-control on fan-out, reuse-first."],
    ["7", "PARTIAL", AMBER, "JIT retrieval, compaction, evaluator-optimizer, reflection, handoff contract, code-as-action."],
    ["6", "AGENT GAPS", RED, "Trajectory eval, observability/tracing, skill-eval harness, registry validation, auto-dispatch, eval-driven skill loop."],
    ["5", "SKILL GAPS", RED, "No skill evals, no versioning, under-used scripts, 10/14 agents skill-less, no two-Claude loop."],
  ];
  const cw = 2.95, gap = 0.18, x0 = 0.6, y0 = 1.75, ch = 3.7;
  cols.forEach(([n, t, c, body], i) => {
    const x = x0 + i * (cw + gap);
    card(s, x, y0, cw, ch, "FFFFFF");
    s.addShape(pres.shapes.RECTANGLE, { x, y: y0, w: cw, h: 0.12, fill: { color: c } });
    s.addText(n, { x, y: y0 + 0.35, w: cw, h: 1.0, fontSize: 52, bold: true, color: c, align: "center", fontFace: HF, margin: 0 });
    s.addText(t, { x, y: y0 + 1.45, w: cw, h: 0.4, fontSize: 14, bold: true, color: INK, align: "center", charSpacing: 1, fontFace: BF });
    s.addText(body, { x: x + 0.2, y: y0 + 1.95, w: cw - 0.4, h: 1.6, fontSize: 11.5, color: "44403A", align: "left", valign: "top", fontFace: BF });
  });
  s.addText("Tally across 23 scored SOTA patterns:  ✅ 9  ·  🟡 7  ·  ❌ 6  ·  ⚪ 2 (N/A — paid-API & heavyweight frameworks, excluded by Tier policy / reuse-first).",
    { x: 0.6, y: 5.7, w: 12, h: 0.5, fontSize: 12, color: INK, fontFace: BF });
  footer(s, 2);
}

// ===================== SLIDE 3 — Where we're already strong (dark) =====================
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.12, fill: { color: AMBER } });
  s.addText("Where we're already ahead of the curve", { x: 0.6, y: 0.5, w: 12, h: 0.7, fontSize: 30, bold: true, color: CREAM, fontFace: HF });
  s.addText("These aren't accidents — protect them in any refactor.", { x: 0.62, y: 1.18, w: 11, h: 0.4, fontSize: 14, color: AMBER_LT, italic: true, fontFace: BF });

  const items = [
    ["Learned the 15× lesson, then codified it", "Anthropic warns: don't fan out 50 subagents / don't fan out on shared state. Our serial-lane + disk-constraint + validation-before-scaling rules ARE that lesson, learned operationally."],
    ["CLOSEOUT_RECEIPT = disciplined condensed return", "The exact 'workers return short summaries' contract from the multi-agent post. Most framework users dump full context back; we don't."],
    ["Git-as-durable-memory + persist-or-dump", "Stronger durability than in-memory agent frameworks. LangGraph checkpointing is the closest commercial analog."],
    ["Reuse-first as a stated principle", "Pre-empts the #1 agent-system failure: greenfielding parallel implementations. Anti-reinvention is policy."],
  ];
  const y0 = 1.85, rh = 1.18;
  items.forEach(([t, b], i) => {
    const y = y0 + i * rh;
    numCircle(s, 0.7, y + 0.12, String(i + 1));
    s.addText(t, { x: 1.35, y: y, w: 11.2, h: 0.4, fontSize: 17, bold: true, color: CREAM, fontFace: BF, margin: 0 });
    s.addText(b, { x: 1.35, y: y + 0.42, w: 11.4, h: 0.7, fontSize: 12.5, color: CREAM2, fontFace: BF, margin: 0 });
  });
  footer(s, 3);
}

// ===================== SLIDE 4 — Top gaps (light) =====================
{
  const s = pres.addSlide();
  s.background = { color: CREAM };
  accentBar(s, RED);
  s.addText("The honest gaps", { x: 0.6, y: 0.45, w: 11, h: 0.7, fontSize: 32, bold: true, color: INK, fontFace: HF });
  s.addText("We judge outputs (PR diffs, artifacts) — never trajectories. Everything below is downstream of that.",
    { x: 0.62, y: 1.15, w: 12, h: 0.4, fontSize: 14, color: MUTE, italic: true, fontFace: BF });

  const gaps = [
    ["1", "No trajectory eval / no observability", "Flying blind on HOW agents reach outcomes. Can't measure any other improvement without traces. Highest leverage."],
    ["2", "No eval harness for skills/agents", "Can't catch a prompt regression or a skill that stopped triggering. skill-creator already gives us the tooling — we just don't run it."],
    ["3", "Unfinished handoff + registry plumbing", "AGENT_HANDOFF_SPEC.md, check_agent_registry.py, auto-dispatch — all DESIGNED in the 2026-04 spec, never built. Cheap to finish."],
    ["4", "No evaluator-optimizer content loop", "Quality gates exist but aren't wired as auto-regenerate. Relevant to book / manga / EI quality."],
    ["5", "Reflective-memory ossification risk", "MEMORY.md could lock in a wrong lesson (documented Reflexion failure mode). The git-first rule helps; a periodic challenge-pass helps more."],
  ];
  const y0 = 1.75, rh = 0.92;
  gaps.forEach(([n, t, b], i) => {
    const y = y0 + i * rh;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 12.1, h: 0.82, fill: { color: "FFFFFF" }, line: { color: CREAM2, width: 0.5 } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 0.1, h: 0.82, fill: { color: RED } });
    numCircle(s, 0.85, y + 0.2, n, 0.42, RED, "FFFFFF");
    s.addText(t, { x: 1.5, y: y + 0.08, w: 11, h: 0.35, fontSize: 16, bold: true, color: INK, fontFace: BF, margin: 0 });
    s.addText(b, { x: 1.5, y: y + 0.43, w: 11, h: 0.35, fontSize: 11.5, color: "44403A", fontFace: BF, margin: 0 });
  });
  footer(s, 4);
}

// ===================== SLIDE 5 — Top-5 OSS tooling picks (dark) =====================
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.12, fill: { color: AMBER } });
  s.addText("Top-5 free / open-source tooling picks", { x: 0.6, y: 0.5, w: 12, h: 0.7, fontSize: 29, bold: true, color: CREAM, fontFace: HF });
  s.addText("All self-hostable · all Tier-2-compatible (local judge = Gemma/Qwen) · zero paid-API in repo code.",
    { x: 0.62, y: 1.18, w: 12, h: 0.4, fontSize: 13, color: AMBER_LT, italic: true, fontFace: BF });

  const rows = [
    ["1", "Langfuse / Arize Phoenix", "Self-hosted OTel tracing + eval for every agent run & LLM call — closes gap #1 repo-wide", "Apache-2.0"],
    ["2", "DeepEval + agentevals", "50+ metrics incl. hallucination/faithfulness; trajectory scoring. Quality → gated metrics", "Apache-2.0 / MIT"],
    ["3", "Kokoro-82M + F5-TTS", "Sub-0.3s draft narration + OSS voice-clone fallback alongside ElevenLabs", "Apache-2.0 / MIT"],
    ["4", "RAGAS / CometKiwi", "Reference-free citation faithfulness + reference-free MT quality gate for localization", "Apache-2.0 / MIT"],
    ["5", "PuLID-Flux II + InstantID", "Confirms our manga face-lock choice is current SOTA; InstantID = angle-robust alternate", "Apache-2.0"],
  ];
  const y0 = 1.8, rh = 0.95;
  rows.forEach(([n, tool, what, lic], i) => {
    const y = y0 + i * rh;
    card(s, 0.6, y, 12.1, 0.84, INK2);
    numCircle(s, 0.82, y + 0.21, n);
    s.addText(tool, { x: 1.45, y: y + 0.08, w: 3.55, h: 0.7, fontSize: 15, bold: true, color: AMBER_LT, valign: "middle", fontFace: BF, margin: 0 });
    s.addText(what, { x: 5.1, y: y + 0.08, w: 6.1, h: 0.7, fontSize: 11.5, color: CREAM2, valign: "middle", fontFace: BF, margin: 0 });
    s.addText(lic, { x: 11.25, y: y + 0.08, w: 1.4, h: 0.7, fontSize: 10.5, color: GREEN, bold: true, valign: "middle", align: "right", fontFace: BF, margin: 0 });
  });
  footer(s, 5);
}

// ===================== SLIDE 6 — Roadmap (light) =====================
{
  const s = pres.addSlide();
  s.background = { color: CREAM };
  accentBar(s);
  s.addText("The roadmap", { x: 0.6, y: 0.45, w: 8, h: 0.7, fontSize: 32, bold: true, color: INK, fontFace: HF });
  s.addText("Build on what exists. Many items just finish the 2026-04 spec's unshipped work.",
    { x: 0.62, y: 1.15, w: 12, h: 0.4, fontSize: 14, color: MUTE, italic: true, fontFace: BF });

  const lanes = [
    ["P0", "QUICK WINS · 6", AMBER, [
      "check_agent_registry.py (finish §5 validator)",
      "Run skill-creator evals on the 4 skills",
      "Trim pearl-github SKILL.md (479/500 lines)",
      "Pilot Langfuse — trace ONE pipeline  🏛",
      "Write AGENT_HANDOFF_SPEC.md  🏛",
      "consolidate-memory cadence for MEMORY.md",
    ]],
    ["P1", "HIGH VALUE · 7", "9A5A2B", [
      "Author pearl-prime + pearl-dev SKILLs  🏛",
      "DeepEval + RAGAS CI quality gates  🏛",
      "Evaluator-optimizer content loop  🏛",
      "CometKiwi reference-free MT gate",
      "Kokoro/F5 TTS draft + fallback tier",
      "agentevals trajectory scoring  🏛",
      "scripts/ helper for isolation-pr skill",
    ]],
    ["P2", "STRATEGIC · 6", MUTE, [
      "Auto-dispatch suggester (code_globs)  🏛",
      "Per-skill CHANGELOG + version",
      "Repo-wide observability rollout  🏛",
      "Music-mode → ACE-Step/YuE (Apache-2.0)",
      "Two-Claude skill-refinement loop",
      "InstantID angle-robust manga alternate",
    ]],
  ];
  const cw = 4.0, gap = 0.18, x0 = 0.6, y0 = 1.7, ch = 4.55;
  lanes.forEach(([tag, hdr, c, items], i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: y0, w: cw, h: ch, fill: { color: "FFFFFF" }, line: { color: CREAM2, width: 0.5 }, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: y0, w: cw, h: 0.62, fill: { color: c } });
    s.addText(tag, { x: x + 0.15, y: y0 + 0.05, w: 1.0, h: 0.52, fontSize: 22, bold: true, color: "FFFFFF", valign: "middle", fontFace: HF, margin: 0 });
    s.addText(hdr, { x: x + 1.15, y: y0 + 0.05, w: cw - 1.3, h: 0.52, fontSize: 12, bold: true, color: "FFFFFF", valign: "middle", align: "right", charSpacing: 1, fontFace: BF, margin: 0 });
    s.addText(items.map((t, k) => ({ text: t, options: { bullet: { code: "2022" }, color: "33302B", breakLine: true, paraSpaceAfter: 6 } })),
      { x: x + 0.22, y: y0 + 0.78, w: cw - 0.4, h: ch - 0.95, fontSize: 11.5, color: "33302B", fontFace: BF, valign: "top" });
  });
  s.addText("🏛 = needs a Pearl_Architect spec (cascade-settle gate) before dispatch.",
    { x: 0.6, y: 6.35, w: 12, h: 0.3, fontSize: 11, color: MUTE, italic: true, fontFace: BF });
  footer(s, 6);
}

// ===================== SLIDE 7 — Recommended first move + NEXT (dark) =====================
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.12, fill: { color: AMBER } });
  s.addText("Recommended first move", { x: 0.6, y: 0.55, w: 12, h: 0.7, fontSize: 30, bold: true, color: CREAM, fontFace: HF });

  // big callout
  card(s, 0.6, 1.5, 12.1, 1.55, INK2);
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.5, w: 0.14, h: 1.55, fill: { color: AMBER } });
  s.addText("Approve the 4 un-gated P0 items now.",
    { x: 1.0, y: 1.62, w: 11.5, h: 0.55, fontSize: 21, bold: true, color: AMBER_LT, fontFace: HF, margin: 0 });
  s.addText("check_agent_registry.py · skill evals · trim pearl-github SKILL · consolidate-memory cadence — all self-contained, near-zero risk, finish-what-exists. Then spec the observability pilot (P0-4) so all eval work has somewhere to land.",
    { x: 1.0, y: 2.18, w: 11.5, h: 0.8, fontSize: 13, color: CREAM2, fontFace: BF, margin: 0 });

  s.addText("Why this order", { x: 0.6, y: 3.35, w: 6, h: 0.4, fontSize: 16, bold: true, color: AMBER, fontFace: BF });
  s.addText([
    { text: "Observability (P0-4) is the keystone — every eval tool emits into it.", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 5 } },
    { text: "P1 is gated on P0: new skills want the eval harness; quality gates want traces.", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 5 } },
    { text: "Nothing adopts a heavyweight framework — borrow patterns + OSS, not runtimes (reuse-first).", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 5 } },
    { text: "All eval judges = Gemma/Qwen local. Zero paid-API in repo code (CLAUDE.md).", options: { bullet: { code: "2022" } } },
  ], { x: 0.7, y: 3.8, w: 12, h: 1.7, fontSize: 13, color: CREAM2, fontFace: BF, valign: "top" });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 5.75, w: 12.1, h: 0.95, fill: { color: AMBER } });
  s.addText("NEXT_ACTION", { x: 0.85, y: 5.85, w: 3, h: 0.4, fontSize: 13, bold: true, color: INK, charSpacing: 2, fontFace: BF, margin: 0 });
  s.addText("Operator reviews deck → approves P0 items → Pearl_Architect specs the chosen improvements (🏛 items gated on cascade-settle).",
    { x: 0.85, y: 6.18, w: 11.9, h: 0.45, fontSize: 13.5, bold: true, color: INK, fontFace: BF, margin: 0 });
  footer(s, 7);
}

pres.writeFile({ fileName: "AGENT_SYSTEM_IMPROVEMENT_DECK.pptx" }).then((f) => console.log("WROTE", f));
