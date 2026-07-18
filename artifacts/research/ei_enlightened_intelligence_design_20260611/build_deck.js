// EI_TECHNOLOGY_DECK.pptx — Enlightened Intelligence, frontier design (forum-facing)
// Palette: FORUM (deep indigo -> violet -> white, sparing gold "light" accent). FLAGGED in-deck.
// Build: NODE_PATH=$(npm root -g) node build_deck.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const FA = require("react-icons/fa");

// ---------- palette ----------
const C = {
  dark: "17143A", dark2: "221B54", panel: "2C2468", panel2: "352B7A",
  violet: "8158F0", violet2: "9B7BFF", lav: "CBBDF7", ice: "ECE7FF",
  white: "FFFFFF", gold: "F4C56A", ink: "211A49", mute: "766E9E",
  lightbg: "F6F4FF", card: "FFFFFF", border: "E6DFFB", gridline: "EDE8FC",
};
const HF = "Georgia";      // header font (personality)
const BF = "Calibri";      // body font (clean)
const mkShadow = () => ({ type: "outer", color: "1A1340", blur: 9, offset: 3, angle: 135, opacity: 0.16 });
const softShadow = () => ({ type: "outer", color: "1A1340", blur: 6, offset: 2, angle: 135, opacity: 0.10 });

// ---------- icon rasterizer ----------
async function icon(IconComponent, color = "FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color: "#" + color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

(async () => {
  const I = {
    globe: await icon(FA.FaGlobeAmericas), shift: await icon(FA.FaExchangeAlt),
    graph: await icon(FA.FaProjectDiagram), council: await icon(FA.FaUsers),
    breath: await icon(FA.FaWind), garden: await icon(FA.FaSeedling),
    tide: await icon(FA.FaSyncAlt), loop: await icon(FA.FaInfinity),
    rocket: await icon(FA.FaRocket), scale: await icon(FA.FaBalanceScale),
    shield: await icon(FA.FaShieldAlt), server: await icon(FA.FaServer),
    route: await icon(FA.FaRoute), spark: await icon(FA.FaLightbulb),
    brain: await icon(FA.FaBrain), heart: await icon(FA.FaHeartbeat),
    leaf: await icon(FA.FaLeaf), lock: await icon(FA.FaFingerprint),
    check: await icon(FA.FaCheckCircle), seed: await icon(FA.FaDna),
  };
  // violet-on-white variants for light slides
  const Iv = {
    graph: await icon(FA.FaProjectDiagram, C.violet), council: await icon(FA.FaUsers, C.violet),
    breath: await icon(FA.FaWind, C.violet), garden: await icon(FA.FaSeedling, C.violet),
    tide: await icon(FA.FaSyncAlt, C.violet), rocket: await icon(FA.FaRocket, C.violet),
    scale: await icon(FA.FaBalanceScale, C.violet), shield: await icon(FA.FaShieldAlt, C.violet),
    server: await icon(FA.FaServer, C.violet), route: await icon(FA.FaRoute, C.violet),
    globe: await icon(FA.FaGlobeAmericas, C.violet), shift: await icon(FA.FaExchangeAlt, C.violet),
    spark: await icon(FA.FaLightbulb, C.gold),
  };

  const p = new pptxgen();
  p.defineLayout({ name: "W", width: 10, height: 5.625 });
  p.layout = "W"; p.author = "Pearl_Research"; p.company = "Phoenix Omega";
  p.title = "Enlightened Intelligence — Frontier Design";
  const W = 10, H = 5.625;

  // ---------- helpers ----------
  // spine motif: a small vertical constellation of connected dots
  function spine(slide, x, y, color = C.violet2, n = 4, gap = 0.42, r = 0.075) {
    for (let i = 0; i < n; i++) {
      if (i < n - 1) slide.addShape(p.shapes.LINE, { x: x + r, y: y + i * gap + r * 2, w: 0, h: gap - r * 2, line: { color, width: 1, transparency: 35 } });
    }
    for (let i = 0; i < n; i++) slide.addShape(p.shapes.OVAL, { x, y: y + i * gap, w: r * 2, h: r * 2, fill: { color: i === 0 ? C.gold : color } });
  }
  function iconBadge(slide, data, x, y, d = 0.62, circle = C.violet, pad = 0.16) {
    slide.addShape(p.shapes.OVAL, { x, y, w: d, h: d, fill: { color: circle }, shadow: softShadow() });
    slide.addImage({ data, x: x + pad / 2, y: y + pad / 2, w: d - pad, h: d - pad });
  }
  function eyebrow(slide, txt, x, y, color = C.violet, w = 6) {
    slide.addText(txt.toUpperCase(), { x, y, w, h: 0.3, fontFace: BF, fontSize: 11.5, bold: true, color, charSpacing: 2.4, margin: 0 });
  }
  function footer(slide, n, dark = false) {
    slide.addText("Enlightened Intelligence  ·  Frontier Design", { x: 0.5, y: H - 0.36, w: 6, h: 0.28, fontFace: BF, fontSize: 9, color: dark ? C.lav : C.mute, margin: 0 });
    slide.addText(String(n).padStart(2, "0"), { x: W - 0.9, y: H - 0.36, w: 0.4, h: 0.28, fontFace: BF, fontSize: 9, bold: true, color: dark ? C.lav : C.mute, align: "right", margin: 0 });
  }
  // title placed BELOW the icon/eyebrow row (icon bottom = 1.12) to avoid collision
  function title(slide, txt, color = C.ink, y = 1.2, w = 9.2, size = 26) {
    slide.addText(txt, { x: 0.5, y, w, h: 0.62, fontFace: HF, fontSize: size, bold: true, color, margin: 0, lineSpacingMultiple: 0.98 });
  }
  // light content card
  function card(slide, x, y, w, h, fill = C.card) {
    slide.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: C.border, width: 1 }, shadow: softShadow() });
  }

  // ============================================================ 1 · TITLE
  let s = p.addSlide(); s.background = { color: C.dark };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: H, fill: { color: C.dark } });
  // ambient violet glow
  s.addShape(p.shapes.OVAL, { x: 6.6, y: -1.6, w: 5.4, h: 5.4, fill: { color: C.violet, transparency: 78 } });
  s.addShape(p.shapes.OVAL, { x: 7.7, y: 1.6, w: 3.6, h: 3.6, fill: { color: C.gold, transparency: 86 } });
  spine(s, 0.62, 1.05, C.violet2, 6, 0.5);
  eyebrow(s, "Pearl_Research  ·  frontier-design mode  ·  2026-06-11", 1.35, 1.0, C.gold, 8.4);
  s.addText("Enlightened", { x: 1.3, y: 1.45, w: 8.4, h: 1.0, fontFace: HF, fontSize: 58, bold: true, color: C.white, margin: 0 });
  s.addText("Intelligence", { x: 1.3, y: 2.42, w: 8.4, h: 1.0, fontFace: HF, fontSize: 58, bold: true, color: C.violet2, margin: 0 });
  s.addText("Ancient wisdom, met to a young person where they actually are —", { x: 1.35, y: 3.62, w: 8.2, h: 0.4, fontFace: BF, fontSize: 16, italic: true, color: C.ice, margin: 0 });
  s.addText("a living technology that is free, local, and faithful to the teachers.", { x: 1.35, y: 3.98, w: 8.2, h: 0.4, fontFace: BF, fontSize: 16, italic: true, color: C.ice, margin: 0 });
  s.addText([
    { text: "The 5 pillars made real  ·  the living loop  ·  the moonshots  ·  the free / local build", options: {} },
  ], { x: 1.35, y: 4.6, w: 8.2, h: 0.35, fontFace: BF, fontSize: 12.5, bold: true, color: C.lav, margin: 0 });
  s.addText("Forum palette (indigo · violet · white). For the United Spiritual Leaders Forum EI pitch.", { x: 1.35, y: 5.0, w: 8.2, h: 0.3, fontFace: BF, fontSize: 9.5, color: C.mute, margin: 0 });
  s.addNotes("Title. EI = the technology that takes the living teachers' wisdom and applies it to Gen Z / Gen Alpha's real struggles. Free, local, faithful. Forum palette flagged.");

  // ============================================================ 2 · THE MISSION
  s = p.addSlide(); s.background = { color: C.lightbg };
  iconBadge(s, I.globe, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "The mission this technology serves", 1.25, 0.56);
  title(s, "Fifteen living masters. A generation in pain.", C.ink, 1.18, 9.2, 25);
  // three stat callouts
  const stats = [
    ["~60%", "of Gen Z report a diagnosed anxiety condition", C.violet],
    ["73%", "say they feel lonely — the loneliest cohort on record", C.violet],
    ["53%", "doomscroll daily; meaning and stillness are scarce", C.violet],
  ];
  stats.forEach((st, i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 2.5, 2.85, 1.55);
    s.addText(st[0], { x: x + 0.2, y: 2.62, w: 2.45, h: 0.7, fontFace: HF, fontSize: 40, bold: true, color: st[2], margin: 0 });
    s.addText(st[1], { x: x + 0.2, y: 3.34, w: 2.5, h: 0.65, fontFace: BF, fontSize: 11.5, color: C.ink, margin: 0 });
  });
  card(s, 0.5, 4.25, 9.0, 0.92, C.dark2);
  s.addText([
    { text: "The teachers carry what the moment is starving for. ", options: { color: C.white, bold: true } },
    { text: "EI is the bridge — it renders their essence as healing a specific young person can feel, without distorting the wisdom or paying a cloud API.", options: { color: C.ice } },
  ], { x: 0.75, y: 4.4, w: 8.5, h: 0.65, fontFace: BF, fontSize: 13.5, valign: "middle", margin: 0, lineSpacingMultiple: 1.02 });
  footer(s, 2);
  s.addNotes("Gen Z/Alpha figures are indicative (see EI_RESEARCH_SOURCES #32 — secondary aggregator, trace to primary before quoting publicly). The point: the need is acute and the teachers answer it; EI is the bridge.");

  // ============================================================ 3 · THE SHIFT
  s = p.addSlide(); s.background = { color: C.lightbg };
  iconBadge(s, I.shift, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "What changes vs EI v2", 1.25, 0.56);
  title(s, "From a thermometer to an engine", C.ink, 1.18, 9.2, 28);
  // two columns
  card(s, 0.5, 1.95, 4.4, 3.15, C.white);
  s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: 1.95, w: 4.4, h: 0.55, fill: { color: C.mute } });
  s.addText("EI v2  ·  today", { x: 0.7, y: 1.98, w: 4.0, h: 0.5, fontFace: BF, fontSize: 14, bold: true, color: C.white, valign: "middle", margin: 0 });
  [
    "A weighted-sum editorial SCORER that grades a finished book",
    "Flat YAML: 2,418 atoms as {id, band, body, teacher}",
    "Persona = a static 0.3 weight that never reads the prose",
    "Somatic = counting body-words per chapter",
    "“Learning” = an EMA nudging five numbers",
  ].forEach((t, i) => s.addText(t, { x: 0.72, y: 2.66 + i * 0.47, w: 4.0, h: 0.45, fontFace: BF, fontSize: 11.5, color: C.ink, bullet: { code: "2013", indent: 14 }, margin: 0 }));
  card(s, 5.1, 1.95, 4.4, 3.15, C.dark2);
  s.addShape(p.shapes.RECTANGLE, { x: 5.1, y: 1.95, w: 4.4, h: 0.55, fill: { color: C.violet } });
  s.addText("EI  ·  this design", { x: 5.3, y: 1.98, w: 4.0, h: 0.5, fontFace: BF, fontSize: 14, bold: true, color: C.white, valign: "middle", margin: 0 });
  [
    "A generative + evolutionary + learning ENGINE, wired to the planners",
    "A provenance graph: universal spine + 15 authentic voices",
    "Persona = a generative agent that reads + reports felt response",
    "Somatic = a designed nervous-system itinerary",
    "Continual local LoRA — the models themselves improve",
  ].forEach((t, i) => s.addText(t, { x: 5.32, y: 2.66 + i * 0.47, w: 4.0, h: 0.45, fontFace: BF, fontSize: 11.5, color: C.ice, bullet: { code: "2192", indent: 14 }, margin: 0 }));
  footer(s, 3);
  s.addNotes("EI v2 is a thermometer — it grades. We are building the engine. Everything to the right is buildable, free, and local. PR #1516 is the near-term floor we consume, not conflict with.");

  // ============================================================ 4 · THE 5 PILLARS (dark section)
  s = p.addSlide(); s.background = { color: C.dark };
  s.addShape(p.shapes.OVAL, { x: -1.8, y: 2.6, w: 5.2, h: 5.2, fill: { color: C.violet, transparency: 82 } });
  eyebrow(s, "The operator's five pillars — made real", 0.5, 0.55, C.gold);
  s.addText("Five pillars become five subsystems", { x: 0.5, y: 0.85, w: 9, h: 0.75, fontFace: HF, fontSize: 30, bold: true, color: C.white, margin: 0 });
  const pillars = [
    [I.graph, "01", "Knowledge Engineering", "The Living Wisdom Graph", "The Spine"],
    [I.council, "02", "Psychological Modeling", "The Reader Council", "The Mirror"],
    [I.breath, "03", "Somatic Heuristics", "The Felt-Arc State Machine", "The Breath"],
    [I.garden, "04", "Organic Genetic Algorithms", "The Quality-Diversity Garden", "The Garden"],
    [I.tide, "05", "Machine Learning", "The Continual Learning Flywheel", "The Tide"],
  ];
  pillars.forEach((pl, i) => {
    const y = 1.75 + i * 0.72;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 9.0, h: 0.62, rectRadius: 0.06, fill: { color: C.panel }, line: { color: C.panel2, width: 1 } });
    iconBadge(s, pl[0], 0.66, y + 0.06, 0.5, C.violet, 0.14);
    s.addText(pl[1], { x: 1.3, y, w: 0.6, h: 0.62, fontFace: HF, fontSize: 18, bold: true, color: C.gold, valign: "middle", margin: 0 });
    s.addText([
      { text: pl[3] + "   ", options: { bold: true, color: C.white, fontSize: 14 } },
      { text: "“" + pl[4] + "”", options: { italic: true, color: C.violet2, fontSize: 12 } },
    ], { x: 1.95, y, w: 4.7, h: 0.62, fontFace: BF, valign: "middle", margin: 0 });
    s.addText(pl[2], { x: 6.7, y, w: 2.7, h: 0.62, fontFace: BF, fontSize: 11, color: C.lav, valign: "middle", align: "right", margin: 0 });
  });
  footer(s, 4, true);
  s.addNotes("Each operator pillar maps to one buildable subsystem with a poetic name. The next five slides take each one in turn: SOTA, the frontier swing, and what we recommend.");

  // ---------- pillar content slide builder ----------
  function pillarSlide(n, num, iconV, eb, ttl, oldLine, newLine, frontier, fitLine, bigStat) {
    const sl = p.addSlide(); sl.background = { color: C.lightbg };
    iconBadge(sl, iconV, 0.5, 0.5, 0.66, C.violet);
    eyebrow(sl, "Pillar " + num + "  ·  " + eb, 1.3, 0.5);
    sl.addText(ttl, { x: 1.3, y: 0.78, w: 8.1, h: 0.6, fontFace: HF, fontSize: 26, bold: true, color: C.ink, margin: 0 });
    // left: from -> to
    card(sl, 0.5, 1.65, 5.05, 1.5, C.white);
    sl.addText("FROM", { x: 0.72, y: 1.78, w: 1, h: 0.25, fontFace: BF, fontSize: 9.5, bold: true, color: C.mute, charSpacing: 2, margin: 0 });
    sl.addText(oldLine, { x: 0.72, y: 2.02, w: 4.65, h: 0.45, fontFace: BF, fontSize: 11.5, color: C.ink, margin: 0 });
    sl.addText("TO", { x: 0.72, y: 2.5, w: 1, h: 0.25, fontFace: BF, fontSize: 9.5, bold: true, color: C.violet, charSpacing: 2, margin: 0 });
    sl.addText(newLine, { x: 0.72, y: 2.74, w: 4.65, h: 0.45, fontFace: BF, fontSize: 11.5, bold: true, color: C.violet, margin: 0 });
    // big stat panel
    card(sl, 5.75, 1.65, 3.75, 1.5, C.dark2);
    sl.addText(bigStat[0], { x: 5.95, y: 1.74, w: 3.4, h: 0.72, fontFace: HF, fontSize: 33, bold: true, color: C.gold, margin: 0 });
    sl.addText(bigStat[1], { x: 5.95, y: 2.46, w: 3.4, h: 0.6, fontFace: BF, fontSize: 10.5, color: C.ice, margin: 0 });
    // frontier (recommended) panel
    card(sl, 0.5, 3.32, 9.0, 1.32, C.white);
    iconBadge(sl, Iv.spark, 0.68, 3.46, 0.42, C.dark2, 0.12);
    sl.addText("THE FRONTIER MOVE WE RECOMMEND", { x: 1.25, y: 3.46, w: 7.5, h: 0.28, fontFace: BF, fontSize: 10, bold: true, color: C.gold, charSpacing: 1.5, margin: 0 });
    sl.addText(frontier, { x: 1.25, y: 3.74, w: 8.1, h: 0.85, fontFace: BF, fontSize: 12, color: C.ink, margin: 0, lineSpacingMultiple: 1.0 });
    // fit strip
    sl.addText([{ text: "Free / local:  ", options: { bold: true, color: C.violet } }, { text: fitLine, options: { color: C.mute } }], { x: 0.5, y: 4.78, w: 9.0, h: 0.35, fontFace: BF, fontSize: 10.5, margin: 0 });
    footer(sl, n);
    return sl;
  }

  // ============================================================ 5 · PILLAR 01
  let sl = pillarSlide(5, "01", I.graph, "Knowledge Engineering", "The Living Wisdom Graph",
    "Quotes stored in flat YAML, no shared structure",
    "A graph that knows each voice AND the shared root",
    "Discover a universal “Contemplative Spine” by clustering every atom across all 15 traditions (Leiden communities), while each teacher stays a distinct “decoder.” Ask “how do all 15 handle impermanence?” → 15 authentic answers pointing at one root node. Provenance is built-in: every sentence traces to an approved atom.",
    "sentence-transformers + leidenalg + BERTopic + an oxigraph/SHACL provenance store. CPU-minutes; zero GPU pressure.",
    ["15 → 1", "voices, one spine — surfaced, never flattened"]);
  // mini spine-of-voices motif on the big-stat panel
  sl.addNotes("Knowledge: stop storing quotes; build a living graph. The spine is the universal root made queryable; the 15 decoders keep each master's voice. Provenance + doctrine-as-SHACL make fidelity architectural, not aspirational.");

  // ============================================================ 6 · PILLAR 02
  sl = pillarSlide(6, "02", I.council, "Psychological Modeling", "The Reader Council",
    "Persona = a 0.3 weight that never sees the words",
    "Persona = a mind that reads the draft and reacts",
    "Each persona becomes a generative agent (on local Gemma/Qwen) that READS a chapter and returns a beat-by-beat felt response: where resonance drops, what objection rises, where it feels preached-at vs truly seen — grounded in CBT / IFS / Self-Determination. Content can finally be optimized against simulated young readers.",
    "Ollama gemma3:27b/qwen2.5:14b + Outlines structured output. ~10–20s per chapter; 13 personas batch nightly.",
    ["“seen”", "vs “preached-at” — now a measured signal"]);
  sl.addNotes("Psychology: the persona becomes a reactive reader-agent (the EGS pattern, proven to track human raters). Advisory at first; later a fitness driver, continually calibrated against real reviews. Validity guardrails: anonymized ensembles, real data outranks the sim.");

  // ============================================================ 7 · PILLAR 03
  sl = pillarSlide(7, "03", I.breath, "Somatic Heuristics", "The Felt-Arc State Machine",
    "Counting body-words per chapter (a bag of words)",
    "A designed journey through nervous-system states",
    "The book becomes an explicit autonomic itinerary — activation → titrated contact → co-regulation → integration → settled safety — measured by a content→state estimator that adds an AROUSAL axis (not just valence). In audio, the narrator's exhale pacing breathes the listener toward ~6 breaths/min. The vocabulary never appears on the page — wisdom lands as lived experience.",
    "NRC-VAD lexicon + numpy/regex (CPU, milliseconds) + CosyVoice2 prosody. Already pre-figured in the somatic spine YAML.",
    ["activation", "→ co-regulation → ventral safety"]);
  sl.addNotes("Somatic: the felt-arc becomes a designed state machine, optimizable. Honest science: polyvagal is a build-system metaphor; reader-facing claims anchor to breath/interoception evidence (the Stanford cyclic-sighing RCT). Stealth doctrine keeps clinical terms off the page.");

  // ============================================================ 8 · PILLAR 04
  sl = pillarSlide(8, "04", I.garden, "Organic Genetic Algorithms", "The Quality-Diversity Garden",
    "No GA at all — an EMA nudging five weights",
    "Breed the best book for each KIND of reader",
    "Quality-Diversity (MAP-Elites) breeds hundreds of variations and keeps the best one in each niche — the catalog IS a grid of brand × persona × topic. A LOCAL LLM is the smart mutation operator (proposing coherent atom swaps); novelty pressure prevents every book collapsing to one formula. The product's “survival of the fittest,” made real.",
    "pyribs MAP-Elites + a local-LLM mutation operator + a 3-tier fitness (free heuristics → embedding surrogate → budgeted judge).",
    ["best ≠", "most clickable — best PER niche"]);
  sl.addNotes("Evolution: QD gives a garden of diverse, high-fitness books, not one optimum — exactly what a 37-brand catalog needs. The local LLM keeps mutations coherent. It wraps PR #1516's NSGA-II/qNEHVI as the in-niche optimizer.");

  // ============================================================ 9 · PILLAR 05
  sl = pillarSlide(9, "05", I.tide, "Machine Learning", "The Continual Learning Flywheel",
    "An EMA moving average over five numbers",
    "The generators, the judge, and the fitness all learn",
    "Real signal — editor edits, reviews, completion, sales — becomes preference data that fine-tunes the local models (KTO/DPO LoRA on Gemma/Qwen). A frozen “Wisdom-Constitution” judge keeps the target on fidelity, never clickbait. Merging folds in new learning without forgetting. Every cycle, wisdom-delivery measurably improves.",
    "PEFT + TRL + Unsloth + mergekit. 14B QLoRA ≈ 8.5GB — fits Pearl Star with headroom. Idle-window training.",
    ["$0", "runtime LLM cost — all local, all OSS"]);
  sl.addNotes("ML: the EMA becomes a real learning loop. KTO is ideal because Phoenix's signal is sparse binary (sold / returned / finished). Anti-Goodhart: fidelity floor + KL-to-reference + frozen judge + operator merge-gate. The 16GB ceiling is NOT binding — 14B trains in 8.5GB.");

  // ============================================================ 10 · THE LIVING LOOP (dark)
  s = p.addSlide(); s.background = { color: C.dark };
  s.addShape(p.shapes.OVAL, { x: 6.4, y: -1.8, w: 5.4, h: 5.4, fill: { color: C.violet, transparency: 84 } });
  iconBadge(s, I.loop, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "The integrated living system", 1.25, 0.56, C.gold);
  s.addText("One closed loop — the “living” claim, made real", { x: 1.25, y: 0.82, w: 8.4, h: 0.6, fontFace: HF, fontSize: 25, bold: true, color: C.white, margin: 0 });
  // 5 stage cards in a row
  const flow = [
    [I.graph, "01 Spine", "wisdom\nsynthesized"],
    [I.council, "02 + 03", "targeted by\nmind + breath"],
    [I.garden, "04 Garden", "content\nevolved"],
    [I.spark, "Deliver", "book · audio\nmanga"],
    [I.tide, "05 Tide", "real signal\n→ learns"],
  ];
  const fw = 1.6, fgap = 0.18, startx = 0.55;
  flow.forEach((f, i) => {
    const x = startx + i * (fw + fgap);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.95, w: fw, h: 1.5, rectRadius: 0.07, fill: { color: C.panel }, line: { color: C.violet, width: i === 4 ? 1.5 : 1 } });
    iconBadge(s, f[0], x + fw / 2 - 0.26, 2.08, 0.52, i === 4 ? C.gold : C.violet, 0.14);
    s.addText(f[1], { x, y: 2.62, w: fw, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(f[2], { x, y: 2.92, w: fw, h: 0.5, fontFace: BF, fontSize: 9.5, color: C.lav, align: "center", margin: 0, lineSpacingMultiple: 0.95 });
    if (i < 4) s.addText("→", { x: x + fw - 0.02, y: 1.95, w: fgap + 0.04, h: 1.5, fontFace: BF, fontSize: 16, bold: true, color: C.violet2, align: "center", valign: "middle", margin: 0 });
  });
  // feedback arc
  s.addShape(p.shapes.RECTANGLE, { x: 0.9, y: 3.95, w: 8.1, h: 0.02, fill: { color: C.gold } });
  s.addShape(p.shapes.LINE, { x: 0.9, y: 3.45, w: 0, h: 0.5, line: { color: C.gold, width: 1.5 } });
  s.addShape(p.shapes.LINE, { x: 9.0, y: 3.45, w: 0, h: 0.5, line: { color: C.gold, width: 1.5 } });
  s.addText("◄  every cycle, the graph enriches · the personas recalibrate · the fitness sharpens · the models improve", { x: 0.9, y: 4.0, w: 8.1, h: 0.35, fontFace: BF, fontSize: 11, italic: true, bold: true, color: C.gold, align: "center", margin: 0 });
  s.addText("Teachings feed the Spine; the Spine is targeted through the Mirror + the Breath; the Garden evolves the content against a fitness whose floor is spiritual fidelity; delivery yields real-world signal; the Tide learns — and feeds the Spine. Nothing in the loop needs a paid API.", { x: 0.7, y: 4.55, w: 8.9, h: 0.7, fontFace: BF, fontSize: 11.5, color: C.ice, align: "center", margin: 0, lineSpacingMultiple: 1.0 });
  footer(s, 10, true);
  s.addNotes("THE key slide. Read the loop left to right, then the gold feedback arc right to left. Every pillar feeds the next; the last feeds the first. That is what 'living' means — and it all runs on one computer we own.");

  // ============================================================ 11 · MOONSHOTS
  s = p.addSlide(); s.background = { color: C.lightbg };
  iconBadge(s, I.rocket, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "Where the pillars connect in ways no one has shipped", 1.25, 0.56, C.violet, 8.4);
  title(s, "Five moonshots", C.ink, 1.18, 9.2, 28);
  const moon = [
    ["Spine as the Genome", "01 × 04", "Evolve a book as a path through the universal spine; pick which teacher voices each step for this reader."],
    ["Bred Against Simulated Minds", "02 × 04", "Evolve content against the Reader Council; co-evolve the readers to be harder to move (virulence-controlled)."],
    ["Cross-Modal Somatic Conductor", "03 × 04", "Evolve text + manga + voice together so the whole artifact executes one nervous-system arc."],
    ["The Self-Enriching Spine", "05 × 01", "The graph learns which cross-tradition moves heal which struggles — from what actually resonates."],
    ["Predict-Before-You-Render", "02 × 05", "Calibrated simulated readers forecast whether a book will land — before a dollar is spent rendering it."],
  ];
  moon.forEach((m, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 1.95 + row * 0.98;
    const w = (i === 4) ? 9.0 : 4.4;
    card(s, x, y, w, 0.9, C.white);
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.09, h: 0.9, fill: { color: C.violet } });
    s.addText([
      { text: m[0] + "   ", options: { bold: true, color: C.ink, fontSize: 12.5 } },
      { text: m[1], options: { color: C.violet, fontSize: 10, bold: true } },
    ], { x: x + 0.25, y: y + 0.1, w: w - 0.4, h: 0.3, fontFace: BF, margin: 0 });
    s.addText(m[2], { x: x + 0.25, y: y + 0.4, w: w - 0.4, h: 0.45, fontFace: BF, fontSize: 10.5, color: C.mute, margin: 0, lineSpacingMultiple: 0.95 });
  });
  s.addText("Each is real technique on real OSS libs (pyribs · DEAP · CosyVoice2 · networkx · scikit-learn) — research-grade, gated behind a stable floor. No “AI magic.”", { x: 0.5, y: 4.92, w: 9.0, h: 0.32, fontFace: BF, fontSize: 10.5, italic: true, color: C.ink, align: "center", margin: 0 });
  footer(s, 11);
  s.addNotes("Five swings that connect two pillars each. All have buildability notes in the design doc. They are gated behind a working P1 — never the first build.");

  // ============================================================ 12 · FITNESS (dark)
  s = p.addSlide(); s.background = { color: C.dark };
  iconBadge(s, I.scale, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "The crux — everything depends on this", 1.25, 0.56, C.gold);
  s.addText("Therapeutic × Resonant × Faithful", { x: 1.25, y: 0.82, w: 8.4, h: 0.6, fontFace: HF, fontSize: 27, bold: true, color: C.white, margin: 0 });
  // T, E free; F floor
  const TE = [
    ["T", "Therapeutic efficacy", "did it move the nervous system to genuine safety?", C.violet],
    ["E", "Gen-Z / Alpha resonance", "did the readers feel met — not preached at?", C.violet],
  ];
  TE.forEach((t, i) => {
    const x = 0.5 + i * 4.6;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.68, w: 4.4, h: 1.4, rectRadius: 0.07, fill: { color: C.panel }, line: { color: C.violet, width: 1 } });
    s.addText(t[0], { x: x + 0.2, y: 1.74, w: 0.8, h: 1.0, fontFace: HF, fontSize: 44, bold: true, color: C.gold, valign: "middle", margin: 0 });
    s.addText(t[1], { x: x + 1.05, y: 1.8, w: 3.2, h: 0.34, fontFace: BF, fontSize: 13.5, bold: true, color: C.white, margin: 0 });
    s.addText(t[2], { x: x + 1.05, y: 2.16, w: 3.2, h: 0.6, fontFace: BF, fontSize: 10.5, color: C.ice, margin: 0, lineSpacingMultiple: 0.95 });
    s.addText("free objective — Pareto-traded", { x: x + 1.05, y: 2.74, w: 3.2, h: 0.28, fontFace: BF, fontSize: 9, italic: true, color: C.lav, margin: 0 });
  });
  // F = floor bar
  s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: 3.25, w: 9.0, h: 0.9, fill: { color: C.gold } });
  s.addText([
    { text: "F  ", options: { bold: true, color: C.dark, fontSize: 30, fontFace: HF } },
    { text: "Spiritual-root fidelity  =  a HARD FLOOR, never a tradeable knob.  ", options: { bold: true, color: C.dark, fontSize: 14 } },
    { text: "Engagement can never buy it down. Below the floor → the book is non-viable, full stop.", options: { color: C.dark2, fontSize: 12.5 } },
  ], { x: 0.75, y: 3.25, w: 8.5, h: 0.9, fontFace: BF, valign: "middle", margin: 0, lineSpacingMultiple: 1.0 });
  s.addText("Optimized as Quality-Diversity (coverage) × multi-objective Pareto (T↔E) × an ε-feasibility floor (F) + novelty pressure (anti-formula-collapse).  Provenance is checked inside the feasibility test — integrity lives in the optimizer, not in a hope.", { x: 0.5, y: 4.35, w: 9.0, h: 0.75, fontFace: BF, fontSize: 11, color: C.ice, align: "center", margin: 0, lineSpacingMultiple: 1.0 });
  footer(s, 12, true);
  s.addNotes("Do NOT scalarize the three — that IS the EMA failure and is trivially reward-hacked. T and E trade on a Pareto front inside QD niches; F is a feasibility floor engagement cannot cross. That single design choice is the integrity guarantee.");

  // ============================================================ 13 · INTEGRITY
  s = p.addSlide(); s.background = { color: C.lightbg };
  iconBadge(s, I.shield, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "The non-negotiable", 1.25, 0.56);
  title(s, "Spiritual integrity, guaranteed by architecture", C.ink, 1.18, 9.2, 24);
  const guards = [
    [I.check, "Provenance by construction", "every sentence traces to an approved, teacher-vetted atom — ungrounded text cannot ship"],
    [I.check, "No homogenization", "collapsing 15 voices into one generic tone is a measurable failure the system penalizes"],
    [I.check, "Doctrine as executable law", "each teacher's forbidden claims become SHACL gates that hard-block violations"],
    [I.check, "Stealth preserved", "wisdom lands as lived experience — clinical/wellness jargon never reaches the page"],
    [I.check, "A frozen, value-anchored judge", "rewards what is faithful and age-appropriate; penalizes engagement-bait — and cannot drift"],
    [I.check, "A human disposes", "the loop proposes; nothing becomes permanent without an operator + Architect sign-off"],
  ];
  guards.forEach((g, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 1.95 + row * 0.99;
    card(s, x, y, 4.4, 0.9, C.white);
    iconBadge(s, g[0], x + 0.16, y + 0.15, 0.58, C.violet, 0.16);
    s.addText(g[1], { x: x + 0.9, y: y + 0.12, w: 3.4, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: C.ink, margin: 0 });
    s.addText(g[2], { x: x + 0.9, y: y + 0.41, w: 3.42, h: 0.46, fontFace: BF, fontSize: 9.5, color: C.mute, margin: 0, lineSpacingMultiple: 0.92 });
  });
  s.addText("EI never speaks AS a teacher. It recombines approved atoms — and discloses that it does. Full EI disclosure is a feature.", { x: 0.5, y: 4.95, w: 9.0, h: 0.3, fontFace: BF, fontSize: 11, bold: true, italic: true, color: C.violet, align: "center", margin: 0 });
  footer(s, 13);
  s.addNotes("Integrity is enforced by architecture, not goodwill. These map to the design doc's 8 guarantees. The teachers are real, living masters — the tech amplifies their essence, never impersonates or dilutes it.");

  // ============================================================ 14 · FREE & LOCAL
  s = p.addSlide(); s.background = { color: C.lightbg };
  iconBadge(s, I.server, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "The whole thing on one computer we own", 1.25, 0.56);
  title(s, "Free · local · self-hosted — $0 runtime LLM", C.ink, 1.18, 9.2, 24);
  // left: pearl star box
  card(s, 0.5, 1.95, 4.3, 2.86, C.dark2);
  s.addText("PEARL STAR", { x: 0.72, y: 2.08, w: 3.9, h: 0.35, fontFace: HF, fontSize: 18, bold: true, color: C.white, margin: 0 });
  s.addText("one ~16 GB GPU  +  16 CPU threads", { x: 0.72, y: 2.44, w: 3.9, h: 0.3, fontFace: BF, fontSize: 11.5, italic: true, color: C.gold, margin: 0 });
  [
    "gemma3:27b — English wisdom-delivery",
    "qwen2.5:14b — CJK (trains in ~8.5 GB)",
    "ComfyUI / FLUX — manga & covers",
    "CosyVoice2 — audiobook narration",
    "Heavy GPU jobs serialize; CPU work runs alongside",
  ].forEach((t, i) => s.addText(t, { x: 0.74, y: 2.84 + i * 0.375, w: 3.9, h: 0.36, fontFace: BF, fontSize: 10.5, color: C.ice, bullet: { code: "2192", indent: 13 }, margin: 0 }));
  // right: OSS stack grid
  s.addText("The open-source stack — nothing proprietary, nothing paid", { x: 5.0, y: 2.0, w: 4.5, h: 0.3, fontFace: BF, fontSize: 11.5, bold: true, color: C.ink, margin: 0 });
  const oss = [
    ["Knowledge", "sentence-transformers · leidenalg · oxigraph · SHACL"],
    ["Reader Council", "Ollama · Outlines / XGrammar"],
    ["Somatic", "NRC-VAD · numpy · librosa · CosyVoice2"],
    ["Garden (QD/GA)", "pyribs · pymoo · BoTorch · PonyGE2"],
    ["Learning", "PEFT · TRL (KTO/DPO) · Unsloth · mergekit"],
  ];
  oss.forEach((o, i) => {
    const y = 2.42 + i * 0.5;
    card(s, 5.0, y, 4.5, 0.46, C.white);
    s.addText(o[0], { x: 5.15, y, w: 1.45, h: 0.46, fontFace: BF, fontSize: 10.5, bold: true, color: C.violet, valign: "middle", margin: 0 });
    s.addText(o[1], { x: 6.55, y, w: 2.85, h: 0.46, fontFace: BF, fontSize: 9, color: C.ink, valign: "middle", margin: 0 });
  });
  s.addText("Per CLAUDE.md: Tier-2 (Gemma/Qwen) runs every pipeline; Tier-1 (Claude) is design-time only — never in the runtime path.", { x: 0.5, y: 4.92, w: 9.0, h: 0.32, fontFace: BF, fontSize: 10, italic: true, color: C.mute, align: "center", margin: 0 });
  footer(s, 14);
  s.addNotes("This is the constraint that makes EI defensible AND ownable: it runs on hardware we control, with open-source tools, for no per-word cost. The 16GB GPU is enough — 14B fine-tuning fits in 8.5GB.");

  // ============================================================ 15 · ROADMAP
  s = p.addSlide(); s.background = { color: C.lightbg };
  iconBadge(s, I.route, 0.5, 0.5, 0.62, C.violet);
  eyebrow(s, "From EI v2 to the living loop", 1.25, 0.56);
  title(s, "A roadmap that ships value at every step", C.ink, 1.18, 9.2, 24);
  const phases = [
    ["P0", "The substrate + cheap wins", "Discover the Spine · arousal-axis somatic · Reader Council (advisory) · provenance gate · feedback ledger", "weeks · mostly CPU · rides PR #1516", C.violet],
    ["P1", "The engine", "QD Garden · continual-learning Flywheel · provenance graph + heuristics · predict-before-render calibration", "1–2 quarters · the real subsystems", C.violet2],
    ["P2", "The moonshots", "Spine-as-genome · bred-against-minds · cross-modal conductor · self-enriching spine · evolve the grammar", "research-grade · gated behind a stable floor", C.gold],
  ];
  phases.forEach((ph, i) => {
    const y = 1.88 + i * 0.96;
    card(s, 0.5, y, 9.0, 0.86, C.white);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.66, y: y + 0.16, w: 0.95, h: 0.56, rectRadius: 0.06, fill: { color: ph[4] } });
    s.addText(ph[0], { x: 0.66, y: y + 0.16, w: 0.95, h: 0.56, fontFace: HF, fontSize: 22, bold: true, color: i === 2 ? C.dark : C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(ph[1], { x: 1.78, y: y + 0.12, w: 5.0, h: 0.34, fontFace: BF, fontSize: 13.5, bold: true, color: C.ink, margin: 0 });
    s.addText(ph[2], { x: 1.78, y: y + 0.44, w: 7.5, h: 0.42, fontFace: BF, fontSize: 9.8, color: C.mute, margin: 0, lineSpacingMultiple: 0.92 });
    s.addText(ph[3], { x: 6.85, y: y + 0.12, w: 2.5, h: 0.34, fontFace: BF, fontSize: 9, italic: true, color: ph[4] === C.gold ? C.gold : C.violet, align: "right", margin: 0 });
  });
  card(s, 0.5, 4.77, 9.0, 0.45, C.dark2);
  s.addText([
    { text: "Smallest first step:  ", options: { bold: true, color: C.gold } },
    { text: "discover the Spine + run the Reader Council as an advisory gate — pure CPU, zero production risk, two frontier ideas proven.", options: { color: C.ice } },
  ], { x: 0.7, y: 4.77, w: 8.6, h: 0.45, fontFace: BF, fontSize: 10.5, valign: "middle", margin: 0 });
  footer(s, 15);
  s.addNotes("Every phase ships standalone value. P0 are near-term wins riding existing structure + PR #1516. P1 is the engine. P2 are the gated moonshots. The smallest first step proves the two highest-leverage ideas on pure CPU.");

  // ============================================================ 16 · CLOSING (dark)
  s = p.addSlide(); s.background = { color: C.dark };
  s.addShape(p.shapes.OVAL, { x: -2, y: -2, w: 6, h: 6, fill: { color: C.violet, transparency: 80 } });
  s.addShape(p.shapes.OVAL, { x: 7.2, y: 2.6, w: 4.4, h: 4.4, fill: { color: C.gold, transparency: 88 } });
  spine(s, 9.0, 0.7, C.violet2, 5, 0.46);
  eyebrow(s, "The vision, in one breath", 0.6, 0.7, C.gold);
  s.addText("Enlightened Intelligence", { x: 0.6, y: 1.0, w: 8.4, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: C.white, margin: 0 });
  s.addText("It takes the living essence of fifteen masters and renders it as a graph that knows both each voice and the root they share. It targets that wisdom through simulated young readers who say what lands and what feels preached-at, and through a model of the nervous system that designs each book as a journey to genuine settledness. It breeds hundreds of variations and keeps the most faithful one for each kind of reader — never the most clickable, because fidelity is a floor it cannot cross. Everything it ships, it learns from. And it does all of this on one computer we own, with open tools, for no per-word cost — without ever putting words in a teacher's mouth.",
    { x: 0.6, y: 1.75, w: 8.5, h: 2.4, fontFace: BF, fontSize: 14.5, italic: true, color: C.ice, margin: 0, lineSpacingMultiple: 1.12 });
  s.addShape(p.shapes.RECTANGLE, { x: 0.6, y: 4.45, w: 8.5, h: 0.02, fill: { color: C.violet } });
  s.addText([
    { text: "Next:  ", options: { bold: true, color: C.gold } },
    { text: "the operator picks which frontier directions + moonshots to pursue → Pearl_Architect specs the chosen build (gated) → Pearl_Dev / Pearl_Research build it on Pearl Star, local and free.", options: { color: C.lav } },
  ], { x: 0.6, y: 4.6, w: 8.5, h: 0.7, fontFace: BF, fontSize: 11.5, margin: 0, lineSpacingMultiple: 1.0 });
  footer(s, 16, true);
  s.addNotes("Close on the vision. Then the ask: operator chooses directions/moonshots → Architect specs (gated, post-settle) → build on Pearl Star. This deck doubles as the forum's EI pitch.");

  await p.writeFile({ fileName: "EI_TECHNOLOGY_DECK.pptx" });
  console.log("WROTE EI_TECHNOLOGY_DECK.pptx (16 slides)");
})();
