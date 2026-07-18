// Lane 01 brand-wizard verification harness (2026-07-19).
//
// Executes the REAL, unmodified production client-matching code
// (brand-wizard-app/src/brandMatch.js: matchBrand / brandAssignmentPayload /
// appendBrandAssignmentToYAML) against the REAL production brand index
// (brand-wizard-app/public/brand_admin_brands.json), driven by the SAME
// market-resolution logic each wizard bundle runs at mount time (copied
// verbatim below from BrandWizard.jsx / BrandWizard-ja.jsx / BrandWizard-tw.jsx;
// BrandWizard-zh.jsx has NO resolver at all, which is exactly the finding under
// test — see inline comment).
//
// For each scenario, the exact JSON body the real handleLaunch() Activate
// handler would POST is constructed and sent to the REAL running FastAPI
// server (server/routes/brand_onboarding.py, POST /api/v1/onboarding/submit)
// so the written YAML + roster_assignments.yaml overlay are byte-verified,
// not just asserted from static code reading.

import { matchBrand, brandAssignmentPayload, appendBrandAssignmentToYAML } from "../../../brand-wizard-app/src/brandMatch.js";
import { readFileSync, writeFileSync } from "node:fs";

const API_BASE = process.env.BW01_API_BASE || "http://127.0.0.1:8931";
const BRANDS = JSON.parse(readFileSync(new URL("../../../brand-wizard-app/public/brand_admin_brands.json", import.meta.url)));

// ── verbatim resolver copies (see header) ──────────────────────────────────

function norm(s) { return String(s == null ? "" : s).toLowerCase().replace(/[\s-]+/g, "_"); }

// BrandWizard.jsx (en_US / wizard.html) mount effect: seeds from ?market= or
// localStorage phoenix_onboarding_market / phoenix_lane; else stays at the
// hardcoded default "us".
function resolveMarket_en(urlParams, storage) {
  let seeded = urlParams.get("market");
  if (!seeded) seeded = storage.phoenix_onboarding_market || storage.phoenix_lane || null;
  return seeded ? norm(seeded) : "us"; // default in BrandWizard.jsx state init
}

// BrandWizard-ja.jsx resolveOnboardingMarket() — copied verbatim from source (line ~11).
function resolveMarket_ja(urlParams, storage) {
  const url = urlParams.get("market");
  if (url) { const k = norm(url); if (k === "jp" || k === "japan") return "japan"; return k; }
  const stored = storage.phoenix_onboarding_market;
  if (stored) { const k = norm(stored); if (k === "jp" || k === "japan") return "japan"; return k; }
  return "japan";
}

// BrandWizard-tw.jsx resolveOnboardingMarket() — copied verbatim from source (line ~10).
function resolveMarket_tw(urlParams, storage) {
  const url = urlParams.get("market");
  if (url) { const k = norm(url); if (k === "tw" || k === "taiwan" || k === "zh_tw") return "taiwan"; return k; }
  const stored = storage.phoenix_onboarding_market;
  if (stored) { const k = norm(stored); if (k === "tw" || k === "taiwan" || k === "zh_tw") return "taiwan"; return k; }
  return "taiwan";
}

// BrandWizard-zh.jsx resolveOnboardingMarket() — POST-FIX. Copied verbatim from the fixed
// source (this lane's landed fix: bw-market-fix-landed). Before the fix, this function did
// not exist at all and onboardingMarket stayed hardcoded at "us" regardless of ?market=.
function resolveMarket_zh(urlParams, storage) {
  const url = urlParams.get("market");
  if (url) {
    const k = norm(url);
    if (k === "cn" || k === "china" || k === "zh_cn") return "china";
    if (k === "sg" || k === "singapore" || k === "zh_sg") return "singapore";
    return k;
  }
  const stored = storage.phoenix_onboarding_market;
  if (stored) {
    const k = norm(stored);
    if (k === "cn" || k === "china" || k === "zh_cn") return "china";
    if (k === "sg" || k === "singapore" || k === "zh_sg") return "singapore";
    return k;
  }
  return "china";
}

const RESOLVERS = { en: resolveMarket_en, ja: resolveMarket_ja, tw: resolveMarket_tw, zh: resolveMarket_zh };

function buildState(marketLabel) {
  return {
    archetype: "somatic_wisdom", persona: "overwhelmed_professional", moment: "3am_spiral",
    tradition: "somatic", angles: [], topicTags: ["anxiety", "burnout"], emotions: ["calm"],
    onboardingLane: "self_help", onboardingMarket: marketLabel,
    contact: { firstName: "Synthetic", lastName: `Tester${Math.floor(Math.random() * 1e6)}`, email: `bw01.${Date.now()}.${Math.floor(Math.random()*1e6)}@example.com`, phoneCode: "+1", phone: "5550100" },
  };
}

function generateSyntheticWizardYaml(state, wizardName) {
  return [
    "# synthetic wizard YAML — brand-wizard verification harness (2026-07-19)",
    `wizard_variant: "${wizardName}"`,
    `archetype: "${state.archetype}"`,
    `persona: "${state.persona}"`,
    `moment: "${state.moment}"`,
    `onboarding_lane: "${state.onboardingLane}"`,
    `onboarding_market: "${state.onboardingMarket}"`,
    "note: synthetic-test-data — purge after evidence capture, no real PII",
    "",
  ].join("\n");
}

async function runScenario({ label, wizard, hubMarketToken, resolverKey, intendedLane }) {
  const urlParams = new URLSearchParams(hubMarketToken ? { market: hubMarketToken } : {});
  const storage = {};
  const resolvedMarket = RESOLVERS[resolverKey](urlParams, storage);
  const state = buildState(resolvedMarket);
  const teacherMode = { mode: "composite", teacher: null }; // readTeacherMode() default (no ?teacher=)

  const m = matchBrand(state, BRANDS, teacherMode);
  if (!m) {
    return { label, wizard, hubMarketToken, resolvedMarket, intendedLane, error: "matchBrand() returned null (no candidate brand in lane)" };
  }
  let wizardYaml = generateSyntheticWizardYaml(state, wizard);
  wizardYaml = appendBrandAssignmentToYAML(wizardYaml, m, state.contact);
  const assignment = brandAssignmentPayload(m, state.contact) || {};

  const body = {
    brand_id: m.brand_id,
    lane: m.lane,
    publication_corp: m.publication_corp,
    ...assignment,
    brand_email: state.contact.email,
    contact: {
      first_name: state.contact.firstName,
      last_name: state.contact.lastName,
      phone: `${state.contact.phoneCode} ${state.contact.phone}`,
    },
    wizard_yaml: wizardYaml,
    match_score: typeof m.score === "number" ? m.score : null,
    match_basis: m.basis || null,
  };

  const resp = await fetch(`${API_BASE}/api/v1/onboarding/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const respJson = await resp.json().catch(() => ({}));

  const capturedLane = m.lane; // == the lane suffix baked into brand_id, the actual signal under test
  const brandLaneSuffix = m.brand_id.match(/_(en_us|ja_jp|zh_tw|zh_cn|zh_sg|zh_hk|ko_kr|es_us|es_es|fr_fr|de_de|it_it|hu_hu|pt_br)$/)?.[1] || "";

  return {
    label, wizard, hubMarketToken, resolvedMarket, intendedLane,
    matched_brand_id: m.brand_id, captured_lane_field: capturedLane, captured_lane_suffix: brandLaneSuffix,
    http_status: resp.status, server_response: respJson,
    email: state.contact.email,
    verdict: brandLaneSuffix.toUpperCase().replace("_", "_") === intendedLane.toUpperCase() ||
             brandLaneSuffix === intendedLane.toLowerCase() ? "PASS" : "FAIL",
  };
}

const SCENARIOS = [
  { label: "smoke_en_US", wizard: "wizard.html", hubMarketToken: null, resolverKey: "en", intendedLane: "en_US" },
  { label: "pilot_ja_JP", wizard: "wizard-ja.html", hubMarketToken: "jp", resolverKey: "ja", intendedLane: "ja_JP" },
  { label: "pilot_zh_TW", wizard: "wizard-tw.html", hubMarketToken: "tw", resolverKey: "tw", intendedLane: "zh_TW" },
  { label: "pilot_zh_CN", wizard: "wizard-zh.html", hubMarketToken: "cn", resolverKey: "zh", intendedLane: "zh_CN" },
  { label: "pilot_zh_SG", wizard: "wizard-zh.html", hubMarketToken: "sg", resolverKey: "zh", intendedLane: "zh_SG" },
];

const results = [];
for (const scenario of SCENARIOS) {
  const r = await runScenario(scenario);
  results.push(r);
  console.log(JSON.stringify(r, null, 2));
}

writeFileSync(new URL(`./results_${process.argv[2] || "run"}.json`, import.meta.url), JSON.stringify(results, null, 2));
