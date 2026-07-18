// Duration Correctness Audit — operator deck. Pearl Prime tokens.
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Pearl_Prime";
pres.title = "Duration Correctness Audit";

// ── palette ──
const INK = "0E0A06", CREAM = "FAF6F0", AMBER = "D97706", AMBER_DK = "B45309";
const CARD = "FFFFFF", CARD_WARM = "F4EDE2", BODY = "2A2118", TAUPE = "8A7B68";
const RED = "B23A2E", GREEN = "4F7A3A", DIV = "E7D9C4";
const W = 13.33, H = 7.5, MX = 0.7;
const HF = "Georgia", BF = "Calibri";
const shadow = () => ({ type: "outer", color: "000000", blur: 9, offset: 3, angle: 135, opacity: 0.12 });

function footer(slide, n, dark) {
  const c = dark ? "9C8E78" : TAUPE;
  slide.addText("Pearl Prime · Duration Correctness Audit · 2026-06-11 · plan-only (no assembly)",
    { x: MX, y: H - 0.42, w: 9.5, h: 0.3, fontSize: 9, color: c, fontFace: BF, align: "left", margin: 0 });
  slide.addText(String(n), { x: W - 1.0, y: H - 0.42, w: 0.5, h: 0.3, fontSize: 9, color: c, fontFace: BF, align: "right", margin: 0 });
}
function kicker(slide, text, dark) {
  slide.addText(text.toUpperCase(), { x: MX, y: 0.5, w: 11, h: 0.3, fontSize: 12, bold: true,
    color: AMBER, fontFace: BF, charSpacing: 3, margin: 0 });
}

// ════════ SLIDE 1 — TITLE (dark) ════════
let s = pres.addSlide(); s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: H, fill: { color: AMBER } });
s.addText("PEARL PRIME · QA AUDIT", { x: MX, y: 1.5, w: 11, h: 0.4, fontSize: 14, bold: true,
  color: AMBER, fontFace: BF, charSpacing: 4, margin: 0 });
s.addText("Duration Correctness", { x: MX, y: 2.05, w: 12, h: 1.3, fontSize: 60, bold: true,
  color: CREAM, fontFace: HF, margin: 0 });
s.addText("Is the hour book really an hour?", { x: MX, y: 3.45, w: 12, h: 0.7, fontSize: 26,
  italic: true, color: "D9CBB6", fontFace: HF, margin: 0 });
s.addText([
  { text: "1,000 books planned · no prose, no LLM   ", options: { color: "C9BBA4" } },
  { text: "│   10 runtime formats   │   listening (150 WPM) + reading (230 WPM)", options: { color: "9C8E78" } },
], { x: MX, y: 4.5, w: 12, h: 0.4, fontSize: 14, fontFace: BF, margin: 0 });
s.addText("THE BOOKS ARE FINE.  THE LABELS ARE WRONG.", { x: MX, y: 5.5, w: 12, h: 0.5, fontSize: 18,
  bold: true, color: AMBER, fontFace: BF, charSpacing: 1, margin: 0 });
footer(s, 1, true);

// ════════ SLIDE 2 — TL;DR three answers (cream) ════════
s = pres.addSlide(); s.background = { color: CREAM };
kicker(s, "The three answers you asked for");
s.addText("Headline", { x: MX, y: 0.85, w: 11, h: 0.8, fontSize: 38, bold: true, color: INK, fontFace: HF, margin: 0 });
const cards = [
  { big: "55 min → 2h23m", pct: "+161%", lab: "The standard book's real audiobook length. Not a rounding gap — the label is off by ~2.6×.", col: RED },
  { big: "94%", pct: "over cap", lab: "of gold standard_books exceed their own 20,000-word ceiling (and that cap was already raised 13k→18k→20k).", col: AMBER_DK },
  { big: "7 of 10", pct: "run long", lab: "formats exceed the act threshold at the intended 150-WPM listening pace. Only the two deep formats are honest.", col: INK },
];
const cw = 3.86, gap = 0.36, x0 = MX;
cards.forEach((c, i) => {
  const x = x0 + i * (cw + gap);
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: cw, h: 3.7, fill: { color: CARD }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: cw, h: 0.14, fill: { color: c.col } });
  s.addText(c.big, { x: x + 0.3, y: 2.35, w: cw - 0.6, h: 1.0, fontSize: c.big.length > 8 ? 34 : 46, bold: true, color: INK, fontFace: HF, margin: 0, valign: "middle" });
  s.addText(c.pct.toUpperCase(), { x: x + 0.3, y: 3.35, w: cw - 0.6, h: 0.4, fontSize: 15, bold: true, color: c.col, fontFace: BF, charSpacing: 2, margin: 0 });
  s.addShape(pres.shapes.LINE, { x: x + 0.3, y: 3.85, w: cw - 0.6, h: 0, line: { color: DIV, width: 1 } });
  s.addText(c.lab, { x: x + 0.3, y: 4.0, w: cw - 0.6, h: 1.45, fontSize: 13.5, color: BODY, fontFace: BF, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
});
s.addText([
  { text: "Why:  ", options: { bold: true, color: INK } },
  { text: "duration is a hand-set label, never computed from word count. The product ships as audiobook at 150 WPM, but the labels imply 125–364 WPM with no formula.", options: { color: BODY } },
], { x: MX, y: 5.95, w: 11.9, h: 0.8, fontSize: 14, fontFace: BF, margin: 0, lineSpacingMultiple: 1.05 });
footer(s, 2, false);

// ════════ SLIDE 3 — how duration is set (cream, two-col) ════════
s = pres.addSlide(); s.background = { color: CREAM };
kicker(s, "How duration is determined");
s.addText("There is no word→minute formula", { x: MX, y: 0.85, w: 12, h: 0.8, fontSize: 34, bold: true, color: INK, fontFace: HF, margin: 0 });
// left text
const L = [
  ["Hand-set label", "Each format's duration_minutes is typed into format_registry.yaml. It is never derived from the word count."],
  ["One WPM constant exists — and it's only for measuring", "tts_wpm: 150 lives in duration_scorecard.yaml, used solely by the read-only adherence scorecard — never to set the advertised number."],
  ["Intended pace = 150 WPM (audiobook)", "Confirmed twice: the config, and OVERLAY_SPEC §413 — “read the atom sequence aloud at TTS pace (flat, 150 WPM).”"],
  ["So the honest label is", "audiobook = words ÷ 150   ·   ebook = words ÷ 230"],
];
let yy = 2.0;
L.forEach((it) => {
  s.addShape(pres.shapes.OVAL, { x: MX, y: yy + 0.05, w: 0.16, h: 0.16, fill: { color: AMBER } });
  s.addText(it[0], { x: MX + 0.32, y: yy - 0.04, w: 6.4, h: 0.35, fontSize: 16, bold: true, color: INK, fontFace: BF, margin: 0 });
  s.addText(it[1], { x: MX + 0.32, y: yy + 0.32, w: 6.5, h: 0.7, fontSize: 13, color: BODY, fontFace: BF, margin: 0, lineSpacingMultiple: 1.03 });
  yy += 1.12;
});
// right: implied wpm callout card
const rx = 8.0, rw = 4.6;
s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 2.0, w: rw, h: 4.3, fill: { color: INK }, shadow: shadow() });
s.addText("IMPLIED WPM, BY FORMAT", { x: rx + 0.35, y: 2.3, w: rw - 0.7, h: 0.35, fontSize: 13, bold: true, color: AMBER, fontFace: BF, charSpacing: 2, margin: 0 });
s.addText("what each hand-set label assumes you read at", { x: rx + 0.35, y: 2.66, w: rw - 0.7, h: 0.3, fontSize: 11, italic: true, color: "9C8E78", fontFace: BF, margin: 0 });
s.addText("125", { x: rx + 0.35, y: 3.1, w: 1.7, h: 1.0, fontSize: 50, bold: true, color: GREEN, fontFace: HF, margin: 0 });
s.addText("deep_book_4h\n(the only honest one)", { x: rx + 0.35, y: 4.05, w: 1.9, h: 0.6, fontSize: 11, color: "C9BBA4", fontFace: BF, margin: 0 });
s.addText("364", { x: rx + 2.5, y: 3.1, w: 1.8, h: 1.0, fontSize: 50, bold: true, color: RED, fontFace: HF, margin: 0 });
s.addText("standard_book\n(at its 20k cap)", { x: rx + 2.5, y: 4.05, w: 1.9, h: 0.6, fontSize: 11, color: "C9BBA4", fontFace: BF, margin: 0 });
s.addShape(pres.shapes.LINE, { x: rx + 0.35, y: 4.95, w: rw - 0.7, h: 0, line: { color: "3A332B", width: 1 } });
s.addText([
  { text: "Honest audiobook pace = 150 WPM.", options: { bold: true, color: CREAM, breakLine: true } },
  { text: "A 2.9× spread with no formula behind it.", options: { color: "9C8E78" } },
], { x: rx + 0.35, y: 5.1, w: rw - 0.7, h: 0.9, fontSize: 13, fontFace: BF, margin: 0, lineSpacingMultiple: 1.05 });
footer(s, 3, false);

// ════════ SLIDE 4 — the marketing gap (cream, chart) ════════
s = pres.addSlide(); s.background = { color: CREAM };
kicker(s, "Mode 2 — the marketing gap");
s.addText("At 150 WPM, almost everything runs long", { x: MX, y: 0.85, w: 12, h: 0.8, fontSize: 32, bold: true, color: INK, fontFace: HF, margin: 0 });
// horizontal bar: listening gap % per format, sorted desc
const gapRows = [
  ["standard_book", 161, RED], ["compact_5ch_15min", 78, RED], ["compact_5ch_20min", 72, RED],
  ["micro_book_15", 68, RED], ["compact_8ch_30min", 58, RED], ["micro_book_20", 49, RED],
  ["short_book_30", 43, RED], ["extended_book_2h", 24, AMBER], ["deep_book_6h", 2, GREEN], ["deep_book_4h", -11, GREEN],
];
s.addChart(pres.charts.BAR, [{
  name: "Listening duration gap %",
  labels: gapRows.map(r => r[0]),
  values: gapRows.map(r => r[1]),
}], {
  x: MX, y: 1.75, w: 8.3, h: 5.15, barDir: "bar",
  chartColors: gapRows.map(r => r[2]),
  chartArea: { fill: { color: CREAM } }, plotArea: { fill: { color: CREAM } },
  catAxisLabelColor: BODY, catAxisLabelFontSize: 11, catAxisLabelFontFace: BF,
  catAxisLabelPos: "low", // pin format names to far-left edge so the negative deep_book_4h bar's label can't overprint them
  valAxisLabelColor: TAUPE, valAxisLabelFontSize: 10,
  valGridLine: { color: DIV, size: 0.5 }, catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontSize: 11, dataLabelFontBold: true,
  dataLabelFormatCode: '+0;\\-0',
  showLegend: false, showTitle: false, valAxisMinVal: -30, valAxisMaxVal: 180,
});
// right rail callouts
const RR = 9.4, rrw = 3.25;
s.addShape(pres.shapes.RECTANGLE, { x: RR, y: 1.85, w: rrw, h: 1.5, fill: { color: CARD }, shadow: shadow() });
s.addText("READ IT AS", { x: RR + 0.25, y: 2.05, w: rrw - 0.5, h: 0.3, fontSize: 11, bold: true, color: AMBER_DK, fontFace: BF, charSpacing: 2, margin: 0 });
s.addText("A “15-min micro” is ~25 min. A “1-hour standard” is 2h23m.", { x: RR + 0.25, y: 2.4, w: rrw - 0.5, h: 0.9, fontSize: 13.5, color: BODY, fontFace: BF, margin: 0, lineSpacingMultiple: 1.05 });
s.addShape(pres.shapes.RECTANGLE, { x: RR, y: 3.55, w: rrw, h: 1.55, fill: { color: CARD }, shadow: shadow() });
s.addText("READING EDITION", { x: RR + 0.25, y: 3.75, w: rrw - 0.5, h: 0.3, fontSize: 11, bold: true, color: AMBER_DK, fontFace: BF, charSpacing: 2, margin: 0 });
s.addText("At 230 WPM the small formats are ~honest, but the big ones run short (deep_4h −42%).", { x: RR + 0.25, y: 4.1, w: rrw - 0.5, h: 0.95, fontSize: 13, color: BODY, fontFace: BF, margin: 0, lineSpacingMultiple: 1.05 });
s.addShape(pres.shapes.RECTANGLE, { x: RR, y: 5.3, w: rrw, h: 1.4, fill: { color: INK }, shadow: shadow() });
s.addText([
  { text: "Only honest pair:\n", options: { color: "9C8E78", breakLine: true } },
  { text: "deep_book_4h  ·  deep_book_6h", options: { bold: true, color: GREEN } },
], { x: RR + 0.25, y: 5.55, w: rrw - 0.5, h: 0.95, fontSize: 14, fontFace: BF, margin: 0, lineSpacingMultiple: 1.1 });
footer(s, 4, false);

// ════════ SLIDE 5 — Mode 1 vs Mode 2 (cream, two cards) ════════
s = pres.addSlide(); s.background = { color: CREAM };
kicker(s, "Two separate failure modes");
s.addText("Which is which", { x: MX, y: 0.85, w: 12, h: 0.8, fontSize: 34, bold: true, color: INK, fontFace: HF, margin: 0 });
const modes = [
  { t: "MODE 1", sub: "Assembly overshoots its own word cap", col: AMBER_DK,
    rows: [["What", "render exceeds word_range[max]"], ["Cause", "gold depth-fill pins to the cap, render adds ~+7%"], ["Who", "standard_book (94%); minor compact tails"], ["Severity", "contained — and partly self-masked by raising the cap"]] },
  { t: "MODE 2", sub: "The advertised duration is just wrong", col: RED,
    rows: [["What", "duration_minutes ≠ words ÷ 150"], ["Cause", "hand-set label, no formula, implied 125–364 WPM"], ["Who", "almost every format — 7 act, 1 note, 2 fine"], ["Severity", "systematic & large — up to +161%"]] },
];
modes.forEach((m, i) => {
  const x = MX + i * (5.95 + 0.4);
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: 5.95, h: 4.5, fill: { color: CARD }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: 5.95, h: 0.85, fill: { color: m.col } });
  s.addText(m.t, { x: x + 0.35, y: 2.05, w: 5, h: 0.4, fontSize: 20, bold: true, color: "FFFFFF", fontFace: HF, margin: 0 });
  s.addText(m.sub, { x: x + 0.35, y: 2.42, w: 5.3, h: 0.35, fontSize: 13, italic: true, color: "FBEFE0", fontFace: BF, margin: 0 });
  let ry = 3.05;
  m.rows.forEach((r) => {
    s.addText(r[0].toUpperCase(), { x: x + 0.35, y: ry, w: 1.5, h: 0.6, fontSize: 11, bold: true, color: TAUPE, fontFace: BF, margin: 0, valign: "top", charSpacing: 1 });
    s.addText(r[1], { x: x + 1.85, y: ry, w: 3.85, h: 0.72, fontSize: 13.5, color: BODY, fontFace: BF, margin: 0, valign: "top", lineSpacingMultiple: 1.0 });
    ry += 0.82;
  });
});
s.addText([
  { text: "The dominant problem is Mode 2. ", options: { bold: true, color: INK } },
  { text: "One duration-derivation fix resolves most of it; Mode 1 is a small, concentrated cleanup.", options: { color: BODY } },
], { x: MX, y: 6.65, w: 12.3, h: 0.5, fontSize: 14, fontFace: BF, margin: 0 });
footer(s, 5, false);

// ════════ SLIDE 6 — standard_book deep dive (cream) ════════
s = pres.addSlide(); s.background = { color: CREAM };
kicker(s, "The worst offender");
s.addText("standard_book: the cap moved, the label never did", { x: MX, y: 0.85, w: 12.2, h: 0.8, fontSize: 30, bold: true, color: INK, fontFace: HF, margin: 0 });
// timeline of cap creep
const steps = [["13k", "original"], ["18k", "raised"], ["20k", "raised again"], ["21.5k", "gold render"]];
const tx0 = MX + 0.2, tw = 2.55, ty = 2.3;
steps.forEach((st2, i) => {
  const x = tx0 + i * tw;
  const isLast = i === steps.length - 1;
  s.addShape(pres.shapes.RECTANGLE, { x, y: ty, w: 1.9, h: 1.25, fill: { color: isLast ? RED : CARD }, shadow: shadow() });
  s.addText(st2[0], { x, y: ty + 0.18, w: 1.9, h: 0.6, fontSize: 30, bold: true, color: isLast ? "FFFFFF" : INK, fontFace: HF, align: "center", margin: 0 });
  s.addText(st2[1], { x, y: ty + 0.82, w: 1.9, h: 0.35, fontSize: 11, color: isLast ? "FBEFE0" : TAUPE, fontFace: BF, align: "center", margin: 0 });
  if (i < steps.length - 1) s.addText("→", { x: x + 1.9, y: ty + 0.3, w: 0.65, h: 0.6, fontSize: 26, bold: true, color: AMBER, fontFace: BF, align: "center", margin: 0 });
});
s.addText("word cap, raised three times to absorb the overshoot — masking it rather than fixing it", { x: MX + 0.2, y: ty + 1.35, w: 10.2, h: 0.35, fontSize: 12.5, italic: true, color: TAUPE, fontFace: BF, margin: 0 });
// the frozen label vs reality
s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 4.35, w: 5.95, h: 2.15, fill: { color: CARD }, shadow: shadow() });
s.addText("ADVERTISED", { x: MX + 0.35, y: 4.6, w: 5, h: 0.3, fontSize: 12, bold: true, color: TAUPE, fontFace: BF, charSpacing: 2, margin: 0 });
s.addText("55 min", { x: MX + 0.35, y: 4.95, w: 5, h: 1.0, fontSize: 56, bold: true, color: INK, fontFace: HF, margin: 0 });
s.addText("frozen since the 13k design", { x: MX + 0.35, y: 5.95, w: 5, h: 0.35, fontSize: 12, italic: true, color: TAUPE, fontFace: BF, margin: 0 });
s.addShape(pres.shapes.RECTANGLE, { x: MX + 6.35, y: 4.35, w: 5.95, h: 2.15, fill: { color: INK }, shadow: shadow() });
s.addText("REAL AUDIOBOOK", { x: MX + 6.7, y: 4.6, w: 5, h: 0.3, fontSize: 12, bold: true, color: AMBER, fontFace: BF, charSpacing: 2, margin: 0 });
s.addText("2h 23m", { x: MX + 6.7, y: 4.95, w: 5, h: 1.0, fontSize: 56, bold: true, color: CREAM, fontFace: HF, margin: 0 });
s.addText("+161% · 21,514 words ÷ 150 WPM", { x: MX + 6.7, y: 5.95, w: 5.2, h: 0.35, fontSize: 12, italic: true, color: "9C8E78", fontFace: BF, margin: 0 });
footer(s, 6, false);

// ════════ SLIDE 7 — tolerance band (cream, 3 columns) ════════
s = pres.addSlide(); s.background = { color: CREAM };
kicker(s, "Tolerance band — listening gap");
s.addText("Where each format lands", { x: MX, y: 0.85, w: 12, h: 0.8, fontSize: 34, bold: true, color: INK, fontFace: HF, margin: 0 });
const bands = [
  { t: "FINE", rng: "≤ ±15%", col: GREEN, items: [["deep_book_6h", "+2%"], ["deep_book_4h", "−11%"]] },
  { t: "NOTE", rng: "15–25%", col: AMBER, items: [["extended_book_2h", "+24%"]] },
  { t: "ACT", rng: "> 25%", col: RED, items: [["standard_book", "+161%"], ["compact_5ch_15min", "+78%"], ["compact_5ch_20min", "+72%"], ["micro_book_15", "+68%"], ["compact_8ch_30min", "+58%"], ["micro_book_20", "+49%"], ["short_book_30", "+43%"]] },
];
const bw = [3.3, 3.3, 5.35], bx = [MX, MX + 3.7, MX + 7.4];
bands.forEach((b, i) => {
  const x = bx[i], w2 = bw[i];
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: w2, h: 4.7, fill: { color: CARD }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: w2, h: 0.75, fill: { color: b.col } });
  s.addText(b.t, { x: x + 0.3, y: 2.02, w: w2 - 1.4, h: 0.6, fontSize: 22, bold: true, color: "FFFFFF", fontFace: HF, margin: 0, valign: "middle" });
  s.addText(b.rng, { x: x + w2 - 1.6, y: 2.02, w: 1.3, h: 0.6, fontSize: 14, bold: true, color: "FBEFE0", fontFace: BF, margin: 0, valign: "middle", align: "right" });
  let iy = 3.0;
  const rowH = i === 2 ? 0.5 : 0.6;
  b.items.forEach((it) => {
    s.addText(it[0], { x: x + 0.3, y: iy, w: w2 - 1.5, h: rowH, fontSize: i === 2 ? 14 : 15, color: INK, fontFace: BF, margin: 0, valign: "middle" });
    s.addText(it[1], { x: x + w2 - 1.45, y: iy, w: 1.15, h: rowH, fontSize: i === 2 ? 14 : 15, bold: true, color: b.col, fontFace: BF, margin: 0, valign: "middle", align: "right" });
    if (i === 2) s.addShape(pres.shapes.LINE, { x: x + 0.3, y: iy + rowH, w: w2 - 0.6, h: 0, line: { color: "F0E7D8", width: 0.5 } });
    iy += rowH;
  });
});
s.addText("7 act · 1 note · 2 fine", { x: MX, y: 6.8, w: 12, h: 0.35, fontSize: 14, bold: true, color: BODY, fontFace: BF, margin: 0 });
footer(s, 7, false);

// ════════ SLIDE 8 — recommendations (cream) ════════
s = pres.addSlide(); s.background = { color: CREAM };
kicker(s, "Recommendation");
s.addText("Fix the labels, not the books", { x: MX, y: 0.85, w: 12, h: 0.8, fontSize: 34, bold: true, color: INK, fontFace: HF, margin: 0 });
// hero recommendation band
s.addShape(pres.shapes.RECTANGLE, { x: MX, y: 1.9, w: 11.93, h: 1.35, fill: { color: INK }, shadow: shadow() });
s.addText([
  { text: "Re-derive every format's advertised duration from its real word target.   ", options: { bold: true, color: CREAM } },
  { text: "audiobook = words ÷ 150   ·   ebook = words ÷ 230", options: { color: AMBER, bold: true } },
], { x: MX + 0.4, y: 2.18, w: 11.1, h: 0.8, fontSize: 17, fontFace: BF, margin: 0, valign: "middle", lineSpacingMultiple: 1.1 });
// 4 option chips
const opts = [
  ["Fix the wpm math", "8 of 10 formats: replace the hand-set label with the derived pair.", AMBER_DK],
  ["Two cap tweaks", "standard_book 20k→22k; compact formats +5% headroom (Mode 1 tails).", AMBER_DK],
  ["Accept", "deep_book_4h & deep_book_6h — already within tolerance.", GREEN],
  ["Populate stubs", "10 Group-A formats have no duration contract — add word_range + derived minutes before they ship.", RED],
];
opts.forEach((o, i) => {
  const x = MX + i * (2.92 + 0.08), w2 = 2.9;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 3.5, w: w2, h: 2.25, fill: { color: CARD }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y: 3.5, w: 0.1, h: 2.25, fill: { color: o[2] } });
  s.addText(o[0], { x: x + 0.28, y: 3.7, w: w2 - 0.45, h: 0.7, fontSize: 15.5, bold: true, color: INK, fontFace: BF, margin: 0, valign: "top" });
  s.addText(o[1], { x: x + 0.28, y: 4.45, w: w2 - 0.45, h: 1.2, fontSize: 12.5, color: BODY, fontFace: BF, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
});
s.addText([
  { text: "Needs a Pearl_Architect spec:  ", options: { bold: true, color: AMBER_DK } },
  { text: "a duration_derivation rule + a registry schema change (duration_minutes → audiobook_minutes / ebook_minutes), plus a CI guard so word-count and minutes can never drift apart again.", options: { color: BODY } },
], { x: MX, y: 6.0, w: 11.95, h: 0.85, fontSize: 13.5, fontFace: BF, margin: 0, lineSpacingMultiple: 1.05 });
footer(s, 8, false);

// ════════ SLIDE 9 — close / next action (dark) ════════
s = pres.addSlide(); s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: H, fill: { color: AMBER } });
s.addText("NEXT ACTION", { x: MX, y: 1.2, w: 11, h: 0.4, fontSize: 14, bold: true, color: AMBER, fontFace: BF, charSpacing: 4, margin: 0 });
s.addText("You decide per format. Then we ship the fix.", { x: MX, y: 1.75, w: 12, h: 1.0, fontSize: 38, bold: true, color: CREAM, fontFace: HF, margin: 0 });
const steps2 = [
  ["1", "Sign off the new advertised minutes", "per the tolerance table — adjust cap / fix wpm / re-advertise / accept."],
  ["2", "Pearl_Architect specs the derivation rule", "words÷150 listen, words÷230 read + registry schema change."],
  ["3", "Config PR + CI guard", "derived durations for all 10 formats; populate the 10 stubs; lock words↔minutes."],
  ["4", "CJK audit before any CJK duration claim", "character-count math — the English 150 WPM does not apply."],
];
let sy = 3.0;
steps2.forEach((st3) => {
  s.addShape(pres.shapes.OVAL, { x: MX, y: sy, w: 0.55, h: 0.55, fill: { color: AMBER } });
  s.addText(st3[0], { x: MX, y: sy, w: 0.55, h: 0.55, fontSize: 22, bold: true, color: INK, fontFace: HF, align: "center", valign: "middle", margin: 0 });
  s.addText(st3[1], { x: MX + 0.8, y: sy - 0.05, w: 11, h: 0.4, fontSize: 18, bold: true, color: CREAM, fontFace: BF, margin: 0 });
  s.addText(st3[2], { x: MX + 0.8, y: sy + 0.36, w: 11, h: 0.4, fontSize: 13, color: "9C8E78", fontFace: BF, margin: 0 });
  sy += 0.92;
});
footer(s, 9, true);

pres.writeFile({ fileName: "DURATION_AUDIT_DECK.pptx" }).then(f => console.log("WROTE", f));
