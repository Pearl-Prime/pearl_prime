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
  // country / short-code words
  us: "en_us", usa: "en_us", united_states: "en_us",
  japan: "ja_jp", jp: "ja_jp",
  taiwan: "zh_tw", tw: "zh_tw",
  china: "zh_cn", cn: "zh_cn",
  hong_kong: "zh_hk", hk: "zh_hk",
  singapore: "zh_sg", sg: "zh_sg",
  korea: "ko_kr", kr: "ko_kr",
  brazil: "pt_br", br: "pt_br",
  spain: "es_es", es: "es_es",
  mexico: "es_us", us_hispanic: "es_us",
  france: "fr_fr", fr: "fr_fr",
  germany: "de_de", de: "de_de",
  italy: "it_it", it: "it_it",
  hungary: "hu_hu", hu: "hu_hu",
  // explicit lane codes pass through unchanged (entry screen hands in fr_fr etc.)
  en_us: "en_us", ja_jp: "ja_jp", ko_kr: "ko_kr",
  zh_tw: "zh_tw", zh_cn: "zh_cn", zh_hk: "zh_hk", zh_sg: "zh_sg",
  es_us: "es_us", es_es: "es_es", fr_fr: "fr_fr", de_de: "de_de",
  it_it: "it_it", hu_hu: "hu_hu", pt_br: "pt_br",
};

function norm(s) {
  return String(s == null ? "" : s).toLowerCase().replace(/[\s-]+/g, "_");
}

function cleanNamePart(s) {
  return String(s || "")
    .replace(/<[^>]*>/g, "")
    .replace(/[<>"'`]/g, "")
    .trim();
}

function directorNameFromContact(contact) {
  const c = contact || {};
  return [cleanNamePart(c.firstName), cleanNamePart(c.lastName)]
    .filter(Boolean)
    .join(" ")
    .trim();
}

function directorIdFromName(name) {
  return (
    String(name || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 80) || "brand_director"
  );
}

function baseBrandFromId(brandId) {
  return String(brandId || "").replace(/_(en_us|es_us|es_es|fr_fr|de_de|it_it|hu_hu|pt_br|zh_tw|zh_hk|zh_cn|zh_sg|ja_jp|ko_kr)$/, "");
}

function isAssignedBrand(entry) {
  if (!entry || typeof entry !== "object") return false;
  const status = norm(entry.brand_director_status || entry.status || "");
  return (
    status === "assigned" ||
    status === "claimed" ||
    !!String(entry.brand_director_name || "").trim() ||
    !!String(entry.brand_director_id || "").trim()
  );
}

function yamlSafe(s) {
  return String(s == null ? "" : s).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

// ═══════════════════════════════════════════════════════════
// MUSIC-MODE-BRAND-INTEGRATION-V1-01 §2 (Q2 brand_id slug rule: <musician_handle>_music)
//
// Single source of truth for the musician_handle -> brand_id derivation so matchBrand
// (client-side preview, below) and generateYAML (wizard YAML emission, duplicated per
// locale in BrandWizard*.jsx) never disagree about a signup's brand_id.
// ═══════════════════════════════════════════════════════════

export function slugifyMusicianHandle(value) {
  return (
    String(value || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 80) || "musician"
  );
}

// state.musicianSurvey is the flat musician_reflections_survey capture (display_name,
// primary_genre, ...). Falls back to the contact name only if the survey hasn't been
// filled in yet (defensive — the wizard should not reach step 9 without it).
export function musicianHandleFromState(state) {
  state = state || {};
  const survey = state.musicianSurvey || {};
  const fromSurvey = String(survey.display_name || survey.musician_handle || "").trim();
  if (fromSurvey) return slugifyMusicianHandle(fromSurvey);
  return slugifyMusicianHandle(directorNameFromContact(state.contact));
}

export function musicBrandIdFromState(state) {
  return `${musicianHandleFromState(state)}_music`;
}

// Schema mirrors artifacts/musician_survey/SURVEY_TEMPLATE.yaml verbatim (8 top-level
// blocks; Q-MSK-FORK-REUSE-01 — no invented fields). Field values are pulled from the
// flat musician_reflections_survey capture by exact key name; anything the survey didn't
// collect is emitted as null/[] rather than fabricated.
const MUSICIAN_REFLECTIONS_SCHEMA = {
  identity: {
    display_name: "scalar",
    years_active: "scalar",
    primary_genre: "scalar",
    secondary_genres: "list",
    primary_instruments: "list",
    creative_phases: "list",
  },
  themes: {
    primary_themes: "list",
    avoided_themes: "list",
    listener_hope_one: "scalar",
  },
  voice_craft: {
    voice_person: "scalar",
    register: "scalar",
    pacing: "scalar",
    signature_devices: "list",
  },
  material_for_reflection: {
    touchstone_tracks: "list",
    key_collaborators: "scalar",
    citations_links: "list",
  },
  healing_intent: {
    what_helps_heal: "scalar",
    listener_responses_to_amplify: "scalar",
    wellness_framing_rejects: "scalar",
  },
  output_preferences_with_lyrics: {
    lyric_form: "scalar",
    lyric_length_note: "scalar",
    explicit_content_ok: "bool",
    companion_ai_song_consent: "bool",
  },
  output_preferences_no_lyrics: {
    reflection_form: "scalar",
    reflection_perspective: "scalar",
  },
  consent_licensing: {
    ai_reflections_consent: "bool",
    usage_restrictions: "scalar",
    followup_email: "scalar",
    submitted_date: "scalar",
    signature: "scalar",
  },
};

// Emits the `musician_reflections:` YAML block (2-space indent under `brand_admin:`,
// matching generateYAML's existing hand-rolled emitter style). `survey` is the flat
// state.musicianSurvey object; `sanitize` is generateYAML's own `san()` string cleaner
// so music-mode output goes through the same XSS/PII guard as every other field.
export function buildMusicianReflectionsYAML(survey, sanitize) {
  const s = survey || {};
  const clean = typeof sanitize === "function" ? sanitize : (v) => String(v == null ? "" : v);
  const scalar = (v) => {
    if (v === undefined || v === null || v === "") return "null";
    return `"${yamlSafe(clean(String(v)))}"`;
  };
  const bool = (v) => (v === undefined || v === null || v === "" ? "null" : v ? "true" : "false");
  const list = (v) => {
    const arr = Array.isArray(v) ? v : v ? [v] : [];
    return arr.length ? "[" + arr.map((x) => `"${yamlSafe(clean(String(x)))}"`).join(", ") + "]" : "[]";
  };
  let out = "  musician_reflections:\n";
  for (const [block, fields] of Object.entries(MUSICIAN_REFLECTIONS_SCHEMA)) {
    out += `    ${block}:\n`;
    for (const [field, kind] of Object.entries(fields)) {
      const v = s[field];
      const rendered = kind === "list" ? list(v) : kind === "bool" ? bool(v) : scalar(v);
      out += `      ${field}: ${rendered}\n`;
    }
  }
  return out;
}

export function brandAssignmentPayload(match, contact) {
  if (!match || !match.brand_id) return null;
  const name = directorNameFromContact(contact);
  if (!name) return null;
  return {
    brand_id: match.brand_id,
    base_brand: baseBrandFromId(match.brand_id),
    display_brand: match.publication_corp || match.brand_id,
    brand_director_name: name,
    brand_director_id: directorIdFromName(name),
    brand_director_status: "assigned",
  };
}

export function appendBrandAssignmentToYAML(yamlText, match, contact) {
  const a = brandAssignmentPayload(match, contact);
  if (!a) return yamlText;
  return (
    String(yamlText || "").replace(/\s*$/, "\n\n") +
    "matched_brand:\n" +
    `  brand_id: "${yamlSafe(a.brand_id)}"\n` +
    `  base_brand: "${yamlSafe(a.base_brand)}"\n` +
    `  display_brand: "${yamlSafe(a.display_brand)}"\n` +
    `  brand_director_name: "${yamlSafe(a.brand_director_name)}"\n` +
    `  brand_director_id: "${yamlSafe(a.brand_director_id)}"\n` +
    `  brand_director_status: "${yamlSafe(a.brand_director_status)}"\n`
  );
}

export async function loadBrandIndexWithLiveAssignments() {
  const response = await fetch("brand_admin_brands.json", { cache: "no-store" });
  const brands = response.ok ? await response.json() : {};
  // Teacher-originated + hybrid brands (additive registry; never mutates the 40×14 index file).
  try {
    const toResp = await fetch("teacher_originated_brands.json", { cache: "no-store" });
    if (toResp.ok) {
      const extra = await toResp.json();
      if (extra && typeof extra === "object") {
        for (const [bid, row] of Object.entries(extra)) {
          if (row && typeof row === "object" && !brands[bid]) brands[bid] = row;
        }
      }
    }
  } catch (_) {
    /* optional overlay */
  }
  try {
    const liveResponse = await fetch("/api/onboarding/assignments", { cache: "no-store" });
    if (!liveResponse.ok) return brands;
    const live = await liveResponse.json();
    if (!Array.isArray(live.brands)) return brands;
    for (const row of live.brands) {
      if (!row?.brand_id || !brands[row.brand_id] || !String(row.brand_director_name || "").trim()) continue;
      brands[row.brand_id] = {
        ...brands[row.brand_id],
        brand_director_name: row.brand_director_name,
        brand_director_id: row.brand_director_id || "",
        brand_director_status: row.brand_director_status || "assigned",
        assigned_at: row.assigned_at || "",
      };
    }
  } catch (_) {
    // Static index fallback keeps the wizard usable during local dev or API downtime.
  }
  return brands;
}

// state: wizard selections {onboardingMarket, archetype, persona, emotions[], topicTags[], angles[], tradition}
// brands: brand_admin_brands.json (keyed by brand_id)
// teacherMode: {mode:"teacher"|"composite", teacher:string|null}  (from phoenix_book_mode / ?teacher / ?mode)
export function matchBrand(state, brands, teacherMode) {
  state = state || {};
  brands = brands || {};

  // MUSIC-MODE-BRAND-INTEGRATION-V1-01 §2 (Q2 brand_id slug rule): a music-mode signup
  // is NEVER scored against brand_admin_brands.json (the frozen 37/composite imprints)
  // — it mints a brand_id of its own in the 38+ space. Skip ALL teacher/composite
  // scoring below entirely for mode === "music"; non-music behavior below this branch
  // is untouched (byte-identical).
  if (state.mode === "music") {
    const handle = musicianHandleFromState(state);
    const brandId = `${handle}_music`;
    const musicMarket = norm(state.onboardingMarket || "us");
    return {
      brand_id: brandId,
      publication_corp: brandId,
      teacher: "",
      is_teacher: false,
      lane: LANE_FROM_MARKET[musicMarket] || "en_us",
      score: 100,
      basis: `music:new_brand:${handle}`,
      musician_handle: handle,
      mode: "music",
    };
  }

  const market = norm(state.onboardingMarket || "us");
  const laneSuffix = "_" + (LANE_FROM_MARKET[market] || "en_us");

  // Candidates: this market's lane, buildable, and not already assigned. The
  // server still enforces this, but the wizard should not preview an occupied
  // brand as available.
  const inLane = Object.entries(brands).filter(
    ([bid, b]) => bid.endsWith(laneSuffix) && b && b.buildable !== false && !isAssignedBrand(b)
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
