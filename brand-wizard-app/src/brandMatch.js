// Shared onboarding brand match for the wizards (en/ja/tw/zh).
//
// Maps a signup's selections to ONE buildable brand for its market, honoring the
// teacher-vs-composite contract:
//   • teacher signup   → that teacher's brand (exact teacher_id), if buildable
//   • composite signup → ONLY a non-teacher brand (NEVER forced onto a teacher
//     brand like sai_ma) — scored by topic/emotion overlap
// Runs entirely client-side against the deployed bridge (brand_admin_brands.json),
// which carries per-brand: d (imprint), tid (teacher slug), is_teacher, buildable,
// arch (archetype), tp (primary topics), f (focus), tr (tradition), lane.

export const LANE_FROM_MARKET = {
  us: "en_us", usa: "en_us", united_states: "en_us",
  japan: "ja_jp", jp: "ja_jp",
  taiwan: "zh_tw", tw: "zh_tw",
  china: "zh_cn", cn: "zh_cn",
  hong_kong: "zh_hk", hk: "zh_hk",
  singapore: "zh_sg", sg: "zh_sg",
  korea: "ko_kr", kr: "ko_kr",
  brazil: "pt_br", br: "pt_br",
  spain: "es_es", es: "es_es",
  mexico: "es_us",
};

function norm(s) {
  return String(s == null ? "" : s).toLowerCase().replace(/[\s-]+/g, "_");
}

// state: wizard selections {onboardingMarket, archetype, persona, emotions[], topicTags[], angles[], tradition}
// brands: brand_admin_brands.json (keyed by brand_id)
// teacherMode: {mode:"teacher"|"composite", teacher:string|null}  (from phoenix_book_mode / ?teacher / ?mode)
export function matchBrand(state, brands, teacherMode) {
  state = state || {};
  brands = brands || {};
  const market = norm(state.onboardingMarket || "us");
  const laneSuffix = "_" + (LANE_FROM_MARKET[market] || "en_us");

  // Candidates: this market's lane, and buildable (never strand an admin on a 0-ship brand).
  const inLane = Object.entries(brands).filter(
    ([bid, b]) => bid.endsWith(laneSuffix) && b && b.buildable !== false
  );
  if (!inLane.length) return null;

  const mk = (entry, score, basis) => {
    const [bid, b] = entry;
    return {
      brand_id: bid,
      publication_corp: b.d || bid,
      teacher: b.t || "",
      is_teacher: !!b.is_teacher,
      lane: b.lane || laneSuffix.slice(1),
      score,
      basis,
    };
  };

  // TEACHER signup → that teacher's brand (exact teacher_id), if it's buildable.
  if (teacherMode && teacherMode.teacher) {
    const want = norm(teacherMode.teacher);
    const hit = inLane.find(([, b]) => norm(b.tid) === want);
    if (hit) return mk(hit, 100, "teacher:" + teacherMode.teacher);
    // teacher's brand missing/non-buildable in this lane → fall through to composite
  }

  // COMPOSITE signup → NON-teacher brands ONLY. This is the guardrail: a composite
  // admin is never assigned a hard-coded teacher brand.
  const composite = inLane.filter(([, b]) => !b.is_teacher);
  const pool = composite.length ? composite : inLane;

  const want = new Set(
    [
      ...(state.topicTags || []),
      ...(state.emotions || []),
      ...(state.angles || []),
      state.archetype,
      state.tradition,
      state.persona,
    ]
      .filter(Boolean)
      .map(norm)
  );

  let best = null;
  let bestScore = -1;
  for (const entry of pool) {
    const b = entry[1];
    const have = new Set(
      [...(b.tp || []), b.f, b.tr, b.arch].filter(Boolean).map(norm)
    );
    let score = 0;
    want.forEach((w) =>
      have.forEach((h) => {
        if (h === w || h.includes(w) || w.includes(h)) score += 1;
      })
    );
    if (score > bestScore) {
      bestScore = score;
      best = entry;
    }
  }
  return best
    ? mk(best, bestScore, bestScore > 0 ? "composite:topic-match" : "composite:default")
    : mk(pool[0], 0, "composite:default");
}
