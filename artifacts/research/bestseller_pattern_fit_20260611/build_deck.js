const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.33 x 7.5
pres.author = "Pearl_Research";
pres.title = "Bestseller Consistency — fit our atoms to proven patterns";

// ---- Pearl Prime tokens ----
const INK = "0E0A06";       // near-black ink
const CREAM = "FAF6F0";     // cream bg
const AMBER = "D97706";     // amber accent
const SAND = "EFE3D2";      // warm card fill on cream
const BRICK = "9A3412";     // warm "break" accent (amber-900)
const MUTE = "6B5E4E";      // muted brown body/caption on cream
const W = 13.33, H = 7.5;
const CX = 0.78;            // content left margin (after bar)
const CW = 11.9;            // content width

const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function bar(s, color) { s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: H, fill: { color: color || AMBER } }); }
function eyebrow(s, txt, y, color) {
  s.addText(txt, { x: CX, y: y, w: CW, h: 0.32, fontFace: "Georgia", fontSize: 12.5, bold: true, color: color || AMBER, charSpacing: 3, margin: 0 });
}
function title(s, txt, color) {
  s.addText(txt, { x: CX, y: 0.66, w: CW, h: 0.82, fontFace: "Georgia", fontSize: 29, bold: true, color: color || INK, margin: 0, valign: "top" });
}
function circ(s, n, x, y, d) {
  s.addShape(pres.shapes.OVAL, { x: x, y: y, w: d, h: d, fill: { color: AMBER } });
  s.addText(String(n), { x: x, y: y, w: d, h: d, align: "center", valign: "middle", fontFace: "Georgia", fontSize: d > 0.55 ? 20 : 16, bold: true, color: CREAM, margin: 0 });
}
function caption(s, txt, y) {
  s.addText(txt, { x: CX, y: y, w: CW, h: 0.7, fontFace: "Calibri", fontSize: 12.5, italic: true, color: MUTE, margin: 0, valign: "top" });
}

// ============================ SLIDE 1 — TITLE (dark) ============================
let s = pres.addSlide(); s.background = { color: INK }; bar(s, AMBER);
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 6.55, w: W, h: 0.95, fill: { color: AMBER } });
s.addText("PEARL_RESEARCH  ·  BESTSELLER CONSISTENCY", { x: CX, y: 1.55, w: CW, h: 0.4, fontFace: "Georgia", fontSize: 14, bold: true, color: AMBER, charSpacing: 4, margin: 0 });
s.addText([
  { text: "Making Atom-Assembled Books", options: { breakLine: true } },
  { text: "Consistently Bestseller", options: { color: AMBER } }
], { x: CX, y: 2.1, w: CW, h: 2.0, fontFace: "Georgia", fontSize: 46, bold: true, color: CREAM, margin: 0, lineSpacingMultiple: 1.02 });
s.addText("Proven book patterns  →  fit our atoms  →  reliable cohesion, not luck", { x: CX, y: 4.35, w: CW, h: 0.5, fontFace: "Calibri", fontSize: 21, color: CREAM, margin: 0 });
s.addText("14 patterns cataloged   ·   4 breaks / 10 partial / 0 full-fit   ·   5 deterministic fit-moves", { x: CX, y: 5.25, w: CW, h: 0.4, fontFace: "Calibri", fontSize: 14.5, color: "C9BBA8", margin: 0 });
s.addText("2026-06-11   ·   structure-only analysis (no copyrighted prose reproduced)   ·   41 sources   ·   companion to 3 research artifacts", { x: CX, y: 6.74, w: CW, h: 0.5, fontFace: "Calibri", fontSize: 12.5, color: INK, bold: true, margin: 0 });

// ============================ SLIDE 2 — FRAME + THESIS ============================
s = pres.addSlide(); s.background = { color: CREAM }; bar(s);
eyebrow(s, "THE FRAME", 0.32);
title(s, "The ask — and the one-line answer");
// operator quote card
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 1.7, w: CW, h: 1.85, fill: { color: SAND }, shadow: shadow() });
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 1.7, w: 0.1, h: 1.85, fill: { color: AMBER } });
s.addText("THE OPERATOR'S WORDS", { x: CX + 0.35, y: 1.92, w: CW - 0.7, h: 0.35, fontFace: "Georgia", fontSize: 12.5, bold: true, color: BRICK, charSpacing: 2, margin: 0 });
s.addText("“Find patterns that ALWAYS work — chapters make sense, readers feel they're learning AND earning, by the end they've learned / grown / derived value, and the book is engaging. If we fit our atom-assembly into proven patterns, we get reliable bestseller cohesion.”", { x: CX + 0.35, y: 2.3, w: CW - 0.7, h: 1.15, fontFace: "Calibri", fontSize: 16.5, italic: true, color: INK, margin: 0, valign: "top" });
// thesis card (amber)
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 3.85, w: CW, h: 2.45, fill: { color: INK }, shadow: shadow() });
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 3.85, w: 0.1, h: 2.45, fill: { color: AMBER } });
s.addText("THE THESIS", { x: CX + 0.35, y: 4.08, w: CW - 0.7, h: 0.35, fontFace: "Georgia", fontSize: 12.5, bold: true, color: AMBER, charSpacing: 2, margin: 0 });
s.addText([
  { text: "Bestseller cohesion is a ", options: {} },
  { text: "sequencing problem over atoms we already have", options: { color: AMBER, bold: true } },
  { text: " — not a new-prose problem.", options: {} }
], { x: CX + 0.35, y: 4.45, w: CW - 0.7, h: 0.9, fontFace: "Georgia", fontSize: 24, bold: true, color: CREAM, margin: 0, valign: "top" });
s.addText("Phoenix already encodes every primitive the patterns need — emotional_role_sequence, named-character arc_position ladders, cost_chapter_index, the metaphor registry, the THREAD slot. The patterns don't fire because the primitives are assembled scrambled — not because they're absent.", { x: CX + 0.35, y: 5.45, w: CW - 0.7, h: 0.75, fontFace: "Calibri", fontSize: 14, color: "D8CCBA", margin: 0, valign: "top" });

// ============================ SLIDE 3 — 5 INVARIANTS ============================
s = pres.addSlide(); s.background = { color: CREAM }; bar(s);
eyebrow(s, "WHAT RELIABLY WORKS", 0.32);
title(s, "Five rules behind every pattern that always works");
const inv = [
  ["One spine, many ribs", "One promise, one big idea, one motif, one character-arc — singular through-lines every chapter hangs off.  Cohesion = singularity of through-line."],
  ["Every unit turns", "No scene, chapter, or part is static; each moves a value from one pole to the other.  Engagement = per-unit motion."],
  ["Earn before you tell", "Immersion and identification precede insight, always.  Felt change = experience-before-explanation (the bibliotherapy sequence)."],
  ["Open, then pay", "Curiosity gaps opened rhythmically and always closed.  Momentum = managed tension with a guaranteed payoff."],
  ["Land in the body, changed", "Close on embodied re-entry, not a summary; widen at the very end.  Transformation = a consolidated felt shift."],
];
let y = 1.72; const rh = 1.03;
inv.forEach((r, i) => {
  circ(s, i + 1, CX + 0.05, y + 0.08, 0.62);
  s.addText(r[0], { x: CX + 0.95, y: y, w: CW - 0.95, h: 0.4, fontFace: "Georgia", fontSize: 19, bold: true, color: INK, margin: 0, valign: "top" });
  s.addText(r[1], { x: CX + 0.95, y: y + 0.42, w: CW - 0.95, h: 0.55, fontFace: "Calibri", fontSize: 13.5, color: MUTE, margin: 0, valign: "top" });
  if (i < inv.length - 1) s.addShape(pres.shapes.LINE, { x: CX + 0.95, y: y + rh - 0.06, w: CW - 1.1, h: 0, line: { color: "E3D8C6", width: 1 } });
  y += rh;
});

// ============================ SLIDE 4 — FIT vs BREAK ============================
s = pres.addSlide(); s.background = { color: CREAM }; bar(s);
eyebrow(s, "THE GAP TODAY", 0.32);
title(s, "Where our system fits — and breaks");
const stats = [[ "4", "BREAK", "actively violated", BRICK ], [ "10", "PARTIAL", "primitive present, unenforced", AMBER ], [ "0", "FULL FIT", "(P4 · P13 · P14 closest)", INK ]];
let sx = CX;
const sw = (CW - 0.6) / 3;
stats.forEach((st, i) => {
  s.addShape(pres.shapes.RECTANGLE, { x: sx, y: 1.72, w: sw, h: 1.7, fill: { color: i === 2 ? INK : CREAM }, line: { color: st[3], width: 2 }, shadow: shadow() });
  s.addText(st[0], { x: sx, y: 1.78, w: sw, h: 0.95, align: "center", fontFace: "Georgia", fontSize: 54, bold: true, color: st[3] === INK ? AMBER : st[3], margin: 0 });
  s.addText(st[1], { x: sx, y: 2.72, w: sw, h: 0.35, align: "center", fontFace: "Georgia", fontSize: 17, bold: true, color: i === 2 ? CREAM : INK, charSpacing: 2, margin: 0 });
  s.addText(st[2], { x: sx, y: 3.07, w: sw, h: 0.3, align: "center", fontFace: "Calibri", fontSize: 11.5, italic: true, color: i === 2 ? "C9BBA8" : MUTE, margin: 0 });
  sx += sw + 0.3;
});
s.addText("The four BREAKS — the patterns we actively violate:", { x: CX, y: 3.72, w: CW, h: 0.35, fontFace: "Georgia", fontSize: 15, bold: true, color: INK, margin: 0 });
const breaks = [
  ["P2  Flat spine", "the same 12× chapter grid — no Problem→History→Knowledge→Action→Maintenance macro-arc"],
  ["P5  No value-turn", "the polarity track (emotional_role_sequence) is declared, then ignored at STORY selection"],
  ["P6  Scrambled character arc", "embodiment lands before recognition; no character has a through-line"],
  ["P12  Motif suppressed", "the registry caps recurrence to prevent over-use — the opposite of orchestrating it"],
];
let by = 4.18;
breaks.forEach((b) => {
  s.addShape(pres.shapes.RECTANGLE, { x: CX, y: by, w: 0.09, h: 0.62, fill: { color: BRICK } });
  s.addText([{ text: b[0] + "  —  ", options: { bold: true, color: BRICK } }, { text: b[1], options: { color: INK } }], { x: CX + 0.22, y: by, w: CW - 0.3, h: 0.62, fontFace: "Calibri", fontSize: 13.5, margin: 0, valign: "middle" });
  by += 0.72;
});
caption(s, "10 PARTIALs = the primitive exists but is not enforced or sequenced. Every break + partial cross-references the 8 known craft failures (F1–F8) and the 7-axis audit.", by + 0.02);

// ============================ SLIDE 5 — ROOT CAUSE / EXHIBIT A ============================
s = pres.addSlide(); s.background = { color: CREAM }; bar(s);
eyebrow(s, "ROOT CAUSE", 0.32);
title(s, "The beats exist — they're assembled out of order");
s.addText("EXHIBIT A — gold-ref combo (gen_z×anxiety×overwhelm×F002), STORY arc_position per chapter:", { x: CX, y: 1.62, w: CW, h: 0.35, fontFace: "Calibri", fontSize: 13.5, bold: true, color: MUTE, margin: 0 });
const beats = ["E","R","E","R","E","M","T","T","T","R","T","T"];
const beatColor = { E: BRICK, R: AMBER, T: INK, M: SAND };
const beatTxt = { E: CREAM, R: INK, T: CREAM, M: INK };
const hdr = [{ text: "Ch", options: { fill: { color: "E3D8C6" }, color: INK, bold: true, align: "center", valign: "middle", fontSize: 13 } }];
for (let i = 0; i < 12; i++) hdr.push({ text: String(i), options: { fill: { color: "E3D8C6" }, color: INK, bold: true, align: "center", valign: "middle", fontSize: 13 } });
const valrow = [{ text: "beat", options: { fill: { color: CREAM }, color: MUTE, bold: true, align: "center", valign: "middle", fontSize: 12, italic: true } }];
beats.forEach((b) => valrow.push({ text: b, options: { fill: { color: beatColor[b] }, color: beatTxt[b], bold: true, align: "center", valign: "middle", fontSize: 18 } }));
s.addTable([hdr, valrow], { x: CX, y: 2.05, w: CW, colW: Array(13).fill(CW / 13), rowH: [0.42, 0.66], border: { pt: 2, color: CREAM }, valign: "middle" });
s.addText("R recognition (start-state)      M mechanism_proof      T turning_point      E embodiment (end-state)", { x: CX, y: 3.28, w: CW, h: 0.32, fontFace: "Calibri", fontSize: 12.5, color: MUTE, margin: 0 });
// callout card
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 3.85, w: CW, h: 2.55, fill: { color: INK }, shadow: shadow() });
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 3.85, w: 0.1, h: 2.55, fill: { color: AMBER } });
s.addText([
  { text: "A bestseller arc runs  recognition → mechanism_proof → turning_point → embodiment,  monotonically.", options: { breakLine: true, color: CREAM, bold: true } },
  { text: "Ours is inverted and shuffled", options: { color: AMBER, bold: true } },
  { text: ":  end-states (E) sit at the very start (ch 0/2/4); turning-points (T) clump at the end.", options: { color: CREAM } },
], { x: CX + 0.35, y: 4.1, w: CW - 0.7, h: 1.1, fontFace: "Georgia", fontSize: 17.5, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
s.addText([
  { text: "Why:  ", options: { bold: true, color: AMBER } },
  { text: "the assembler selects atoms by ", options: { color: "D8CCBA" } },
  { text: "slot-fill + dedup", options: { color: CREAM, bold: true } },
  { text: ", never by ", options: { color: "D8CCBA" } },
  { text: "arc-beat continuity", options: { color: CREAM, bold: true } },
  { text: ".  This single fact = 6 of 8 craft failures and 8 of 14 pattern breaks.", options: { color: "D8CCBA" } },
], { x: CX + 0.35, y: 5.35, w: CW - 0.7, h: 0.95, fontFace: "Calibri", fontSize: 14.5, margin: 0, valign: "top" });

// ============================ SLIDE 6 — 5 FIT-MOVES ============================
s = pres.addSlide(); s.background = { color: CREAM }; bar(s);
eyebrow(s, "THE FIX", 0.32);
title(s, "Five deterministic fit-moves — no new engine");
const mh = [
  { text: "#", options: { fill: { color: INK }, color: AMBER, bold: true, align: "center", valign: "middle", fontSize: 14 } },
  { text: "What it does (deterministic, at compile/assembly)", options: { fill: { color: INK }, color: CREAM, bold: true, valign: "middle", fontSize: 14 } },
  { text: "Closes", options: { fill: { color: INK }, color: CREAM, bold: true, align: "center", valign: "middle", fontSize: 14 } },
];
const moves = [
  ["1", "Bind the 12-spine to a 5-phase macro-arc  (add book_phase: Problem→History→Knowledge→Action→Maintenance)", "P2 · F2"],
  ["2", "Spine-character through-line  — one character's 4 arc-positions land at the 4 phase boundaries, monotonically", "P6 · F6"],
  ["3", "Align STORY / REFLECTION to the value-polarity track  + local-embedding conceptual-repetition gate", "P5 · P11 · F1 · F7"],
  ["4", "One orchestrated motif (plant→echo→payoff) + one named book-idea exempt from the repetition cap", "P12 · P9 · F3"],
  ["5", "Voice-zone to slot-type + intra-chapter order integrity + book-scope open-loop ledger", "P8 · P13 · P7 · F5 · F4"],
];
const mrows = [mh];
moves.forEach((m, i) => {
  const fill = i % 2 ? CREAM : SAND;
  mrows.push([
    { text: m[0], options: { fill: { color: AMBER }, color: CREAM, bold: true, align: "center", valign: "middle", fontSize: 19 } },
    { text: m[1], options: { fill: { color: fill }, color: INK, valign: "middle", fontSize: 13 } },
    { text: m[2], options: { fill: { color: fill }, color: BRICK, bold: true, align: "center", valign: "middle", fontSize: 12.5 } },
  ]);
});
s.addTable(mrows, { x: CX, y: 1.72, w: CW, colW: [0.6, 9.0, 2.3], rowH: [0.45, 0.82, 0.82, 0.82, 0.82, 0.82], border: { pt: 1.5, color: CREAM }, valign: "middle" });
caption(s, "Total cost: ~370 LoC + 3 new arc fields + ~25–40 targeted atoms. The 16k+ existing atoms are RE-SEQUENCED, not rewritten. Anti-reinvention honored; every check is structural-deterministic (canonical-spec §9 compatible); no paid LLM API.", 6.55);

// ============================ SLIDE 7 — OPERATOR WORDS MAPPING ============================
s = pres.addSlide(); s.background = { color: CREAM }; bar(s);
eyebrow(s, "DOES IT ANSWER THE ASK?", 0.32);
title(s, "Every word of the ask, mapped to a move");
const wh = [
  { text: "Your words", options: { fill: { color: INK }, color: AMBER, bold: true, valign: "middle", fontSize: 14.5 } },
  { text: "Delivered by", options: { fill: { color: INK }, color: CREAM, bold: true, valign: "middle", fontSize: 14.5 } },
];
const wm = [
  ["“chapters make sense”", "MOVE 1 (phases) + MOVE 4 (one motif / idea) + MOVE 3 (no adjacent repetition)"],
  ["“learning AND earning”", "MOVE 3 (the per-chapter turn = aha cadence) + MOVE 5 (earn-the-insight order kept intact)"],
  ["“by the end they've grown”", "MOVE 2 (spine-character arc = felt growth) + MOVE 1 (Maintenance phase consolidates) + MOVE 4 (idea compounds)"],
  ["“the book is engaging”", "MOVE 5 (open-loop rhythm) + MOVE 3 (every unit turns — no flat middle)"],
];
const wrows = [wh];
wm.forEach((r, i) => {
  const fill = i % 2 ? CREAM : SAND;
  wrows.push([
    { text: r[0], options: { fill: { color: fill }, color: BRICK, bold: true, italic: true, valign: "middle", fontSize: 14.5 } },
    { text: r[1], options: { fill: { color: fill }, color: INK, valign: "middle", fontSize: 13.5 } },
  ]);
});
s.addTable(wrows, { x: CX, y: 1.72, w: CW, colW: [3.7, 8.2], rowH: [0.5, 0.92, 0.92, 0.92, 0.92], border: { pt: 1.5, color: CREAM }, valign: "middle" });
// closing callout
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 5.95, w: CW, h: 1.05, fill: { color: AMBER }, shadow: shadow() });
s.addText([
  { text: "The deterministic guarantee:  ", options: { bold: true, color: INK } },
  { text: "with MOVES 1–5 a book ", options: { color: INK } },
  { text: "cannot", options: { color: INK, bold: true, italic: true } },
  { text: " assemble into the failure shapes — cohesion becomes a property of the assembler, not a lucky draw.", options: { color: INK } },
], { x: CX + 0.35, y: 6.05, w: CW - 0.7, h: 0.85, fontFace: "Georgia", fontSize: 16, margin: 0, valign: "middle" });

// ============================ SLIDE 8 — P0/P1/P2 ============================
s = pres.addSlide(); s.background = { color: CREAM }; bar(s);
eyebrow(s, "PRIORITIZATION", 0.32);
title(s, "Sequenced by leverage — validate before scaling");
const cols = [
  ["P0", "do first — keystone", AMBER, ["MOVE 1  book_phase spine map", "MOVE 2  spine-character through-line", "MOVE 3a  STORY ↔ role alignment", "", "Converts 3 of 4 breaks (P2·P5·P6); root-fixes F1·F2·F6 — mostly sequencing, low / no new atoms."]],
  ["P1", "small gates + tiny config", "B8742C", ["MOVE 4  motif + book-idea orchestration", "MOVE 5a/b  voice-zone + order integrity", "MOVE 3b  repetition gate (local embeddings)", "", "Needs the one C2 ruling (next slide). ~40–60 LoC each; resolves the G1 embedding-model question (local, Tier-2-safe)."]],
  ["P2", "targeted atom authoring", BRICK, ["signal / amplification REFLECTIONs (~10–15)", "Ahjan-specific TEACHER_DOCTRINE atoms", "EXERCISE backfill (~10 combos)", "loop-ledger + THREAD payoff curation", "The genuinely-missing atoms — Pearl_Editor / Pearl_Writer lanes, not mass rewrites."]],
];
let cxp = CX; const cwp = (CW - 0.7) / 3;
cols.forEach((c) => {
  s.addShape(pres.shapes.RECTANGLE, { x: cxp, y: 1.72, w: cwp, h: 4.05, fill: { color: CREAM }, line: { color: c[2], width: 2 }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: cxp, y: 1.72, w: cwp, h: 0.78, fill: { color: c[2] } });
  s.addText(c[0], { x: cxp + 0.18, y: 1.8, w: 1.2, h: 0.62, fontFace: "Georgia", fontSize: 28, bold: true, color: CREAM, margin: 0, valign: "middle" });
  s.addText(c[1], { x: cxp + 1.25, y: 1.8, w: cwp - 1.4, h: 0.62, fontFace: "Calibri", fontSize: 12.5, bold: true, color: CREAM, margin: 0, valign: "middle" });
  let iy = 2.68;
  c[3].forEach((line) => {
    if (line === "") { iy += 0.14; return; }
    const isNote = line.startsWith("Converts") || line.startsWith("Needs") || line.startsWith("The genuinely");
    if (isNote) {
      s.addText(line, { x: cxp + 0.2, y: iy, w: cwp - 0.4, h: 0.9, fontFace: "Calibri", fontSize: 11.5, italic: true, color: MUTE, margin: 0, valign: "top" });
    } else {
      s.addText([{ text: "▸ ", options: { color: c[2], bold: true } }, { text: line, options: { color: INK } }], { x: cxp + 0.2, y: iy, w: cwp - 0.4, h: 0.5, fontFace: "Calibri", fontSize: 12.5, margin: 0, valign: "top" });
      iy += 0.52;
    }
  });
  cxp += cwp + 0.35;
});
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 6.0, w: CW, h: 0.95, fill: { color: INK }, shadow: shadow() });
s.addText([
  { text: "Sequencing:  ", options: { bold: true, color: AMBER } },
  { text: "land gates → verify on the gold-ref combo + one fresh combo → ", options: { color: CREAM } },
  { text: "then", options: { color: AMBER, bold: true, italic: true } },
  { text: " scale.  Gate on the validator's output, not vibes  (feedback_validation_before_scaling).", options: { color: CREAM } },
], { x: CX + 0.35, y: 6.05, w: CW - 0.7, h: 0.85, fontFace: "Calibri", fontSize: 14, margin: 0, valign: "middle" });

// ============================ SLIDE 9 — THE ONE DECISION ============================
s = pres.addSlide(); s.background = { color: SAND }; bar(s);
eyebrow(s, "OPERATOR-TIER DECISION", 0.32, BRICK);
title(s, "One ruling unblocks the most");
s.addShape(pres.shapes.RECTANGLE, { x: CX, y: 1.85, w: CW, h: 2.0, fill: { color: AMBER }, shadow: shadow() });
s.addText("RATIFY", { x: CX + 0.4, y: 2.1, w: CW - 0.8, h: 0.4, fontFace: "Georgia", fontSize: 14, bold: true, color: INK, charSpacing: 3, margin: 0 });
s.addText("C2 voice-braid  Option B (zone)", { x: CX + 0.4, y: 2.45, w: CW - 0.8, h: 0.7, fontFace: "Georgia", fontSize: 33, bold: true, color: INK, margin: 0 });
s.addText("Bind voice / person to slot-type so the three narrative positions stay legible:", { x: CX + 0.4, y: 3.18, w: CW - 0.8, h: 0.35, fontFace: "Calibri", fontSize: 14.5, color: INK, margin: 0 });
s.addText("SCENE = 2nd-person reader-hero    ·    STORY = 3rd-person witness    ·    TEACHER_DOCTRINE = guide    ·    REFLECTION = author-coach    ·    EXERCISE = imperative", { x: CX + 0.4, y: 3.5, w: CW - 0.8, h: 0.3, fontFace: "Calibri", fontSize: 12.5, bold: true, color: "5A3208", margin: 0 });
s.addText([
  { text: "Why this one:  ", options: { bold: true, color: BRICK } },
  { text: "it directly fixes the F5 voice-fragmentation failure (“Am I reading Brené Brown? a Buddhist teacher? a consultant?”) and unblocks MOVE 5.  It was already flagged as a decision item in the craft proposal §9.1.", options: { color: INK } },
], { x: CX, y: 4.15, w: CW, h: 0.9, fontFace: "Calibri", fontSize: 15, margin: 0, valign: "top" });
s.addText([
  { text: "Everything else routes to lanes:  ", options: { bold: true, color: INK } },
  { text: "cap-entries (BOOK-PHASE-SPINE-01, SPINE-CHARACTER-THROUGHLINE-01, STORY-ROLE-ALIGNMENT-01, BOOK-MOTIF-IDEA-01) + Pearl_Dev (~370 LoC) + targeted Pearl_Editor / Pearl_Writer authoring. No other operator-tier call required.", options: { color: MUTE } },
], { x: CX, y: 5.15, w: CW, h: 1.1, fontFace: "Calibri", fontSize: 14, margin: 0, valign: "top" });

// ============================ SLIDE 10 — NEXT ACTION (dark) ============================
s = pres.addSlide(); s.background = { color: INK }; bar(s, AMBER);
eyebrow(s, "NEXT ACTION", 0.32, AMBER);
title(s, "From this deck to consistent bestseller cohesion", CREAM);
const steps = [
  ["Operator", "Review this deck → approve the fit-plan (esp. MOVES 1 + 2 as P0, and the C2 Option B ruling)."],
  ["Pearl_Architect", "Spec the caps: BOOK-PHASE-SPINE-01 · SPINE-CHARACTER-THROUGHLINE-01 · STORY-ROLE-ALIGNMENT-01 · BOOK-MOTIF-IDEA-01  + ratify C2."],
  ["Pearl_Editor / Writer", "Author the P2 atom lanes (~25–40 atoms): signal/amplification REFLECTIONs, Ahjan TEACHER_DOCTRINE, EXERCISE backfill."],
  ["Verify, then scale", "Run the structural checks on the gold-ref combo → gate catalog-scaling on validator uplift, not vibes."],
];
let ny = 1.78;
steps.forEach((st, i) => {
  circ(s, i + 1, CX + 0.05, ny + 0.05, 0.6);
  s.addText(st[0], { x: CX + 0.9, y: ny, w: 3.0, h: 0.55, fontFace: "Georgia", fontSize: 17, bold: true, color: AMBER, margin: 0, valign: "middle" });
  s.addText(st[1], { x: CX + 3.95, y: ny - 0.03, w: CW - 3.95, h: 0.72, fontFace: "Calibri", fontSize: 13.5, color: CREAM, margin: 0, valign: "middle" });
  ny += 0.92;
});
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 6.55, w: W, h: 0.95, fill: { color: AMBER } });
s.addText([
  { text: "Artifacts:  ", options: { bold: true, color: INK } },
  { text: "BESTSELLER_PATTERN_CATALOG.md   ·   OUR_SYSTEM_VS_PATTERNS_GAP.md   ·   FIT_OUR_ATOMS_TO_PATTERNS_PLAN.md   ·   this deck", options: { color: INK } },
], { x: CX, y: 6.74, w: CW, h: 0.5, fontFace: "Calibri", fontSize: 13, margin: 0, valign: "middle" });

pres.writeFile({ fileName: "/tmp/bestseller_salvage_20260611/BESTSELLER_CONSISTENCY_DECK.pptx" }).then(f => console.log("WROTE " + f));
