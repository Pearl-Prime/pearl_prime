// POST /api/onboarding/accept-hybrid — lazy hybrid brand accept (second claimant).
// Mirrors FastAPI /api/v1/onboarding/accept-hybrid for Cloudflare Pages (no FastAPI hop).
// Does NOT weaken teacher_claimed 409; only runs after an explicit accept click.
import { AwsClient } from "../../_lib/aws4fetch.js";

const DEFAULT_BUCKET = "phoenix-omega-artifacts";
const HYBRID_PREFIX = "onboarding/hybrids/";
const TO_BRAND_PREFIX = "onboarding/teacher_originated/";
const LANE_SUFFIX_RE = /_(en_us|es_us|es_es|fr_fr|de_de|it_it|hu_hu|pt_br|zh_tw|zh_hk|zh_cn|zh_sg|ja_jp|ko_kr)$/;

function r2ObjectUrl(env, key) {
  const bucket = (env.R2_BUCKET || DEFAULT_BUCKET).trim();
  const endpoint =
    (env.R2_ENDPOINT || "").trim() ||
    `https://${String(env.R2_ACCOUNT_ID || "").trim()}.r2.cloudflarestorage.com`;
  return `${endpoint.replace(/\/$/, "")}/${bucket}/${key}`;
}

function safeKeyPart(s) {
  return (
    String(s || "")
      .toLowerCase()
      .replace(/[^a-z0-9._-]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 200) || "x"
  );
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

function makeAws(env) {
  return new AwsClient({
    accessKeyId: env.R2_ACCESS_KEY_ID,
    secretAccessKey: env.R2_SECRET_ACCESS_KEY,
    service: "s3",
    region: "auto",
  });
}

async function getJson(aws, env, key) {
  const got = await fetch(await aws.sign(r2ObjectUrl(env, key)));
  if (!got.ok) return { status: got.status, body: null };
  try {
    return { status: got.status, body: await got.json() };
  } catch (_) {
    return { status: got.status, body: null };
  }
}

async function putJson(aws, env, key, value) {
  const putReq = await aws.sign(r2ObjectUrl(env, key), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(value),
  });
  return fetch(putReq);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  let payload;
  try {
    payload = await request.json();
  } catch (_) {
    return json({ status: "error", detail: "invalid JSON body" }, 400);
  }
  const teacherId = String(payload.teacher_id || "").trim();
  const archetypeId = String(payload.archetype_id || "").trim();
  let lane = String(payload.lane || "en_us").trim().toLowerCase().replace(/-/g, "_");
  // Accept market tokens (jp, france, …) as well as lane codes (ja_jp, fr_fr).
  const MARKET_TO_LANE = {
    us: "en_us", usa: "en_us", united_states: "en_us",
    jp: "ja_jp", japan: "ja_jp",
    tw: "zh_tw", taiwan: "zh_tw",
    cn: "zh_cn", china: "zh_cn",
    hk: "zh_hk", hong_kong: "zh_hk",
    sg: "zh_sg", singapore: "zh_sg",
    kr: "ko_kr", korea: "ko_kr",
    mexico: "es_us", us_hispanic: "es_us",
    spain: "es_es", es: "es_es",
    france: "fr_fr", fr: "fr_fr",
    germany: "de_de", de: "de_de",
    italy: "it_it", it: "it_it",
    hungary: "hu_hu", hu: "hu_hu",
    brazil: "pt_br", br: "pt_br",
  };
  if (MARKET_TO_LANE[lane]) lane = MARKET_TO_LANE[lane];
  if (!teacherId || !archetypeId) {
    return json({ status: "error", detail: "teacher_id and archetype_id required" }, 422);
  }

  let archetypes = [];
  try {
    const origin = new URL(request.url).origin;
    const resp = await fetch(`${origin}/brand_archetype_ids.json`);
    if (resp.ok) {
      const body = await resp.json();
      if (Array.isArray(body?.archetypes)) archetypes = body.archetypes;
    }
  } catch (_) {}

  const aws = makeAws(env);
  const ledgerKey = `${HYBRID_PREFIX}${safeKeyPart(lane)}__${safeKeyPart(teacherId)}.json`;
  const prior = await getJson(aws, env, ledgerKey);
  const hybrids = Array.isArray(prior.body?.hybrids) ? [...prior.body.hybrids] : [];
  const used = new Set(hybrids.map((h) => h?.hybrid_of_archetype).filter(Boolean));
  if (used.size >= 40 || (archetypes.length && used.size >= archetypes.length)) {
    return json(
      {
        error: "hybrid_cap_reached",
        teacher_id: teacherId,
        lane,
        cap: 40,
        message: "All 40 archetype hybrids already exist for this teacher in this lane.",
      },
      409
    );
  }
  if (used.has(archetypeId)) {
    return json(
      {
        error: "hybrid_already_exists",
        teacher_id: teacherId,
        archetype_id: archetypeId,
        lane,
        available_archetypes: archetypes.filter((a) => !used.has(a)),
      },
      409
    );
  }

  const laneSuffix = lane.toLowerCase();
  const brandId = `hy_${safeKeyPart(teacherId)}_${safeKeyPart(archetypeId)}_${laneSuffix}`.replace(
    /_+/g,
    "_"
  );
  const display = `${archetypeId.replace(/_/g, " ")} × ${teacherId.replace(/_/g, " ")} Path`;
  const brand = {
    brand_id: brandId,
    lane_id: lane,
    display_name: display,
    publication_corp: display,
    source: "teacher_originated",
    origin_teacher_id: teacherId,
    attribution_mode: "generalized",
    hybrid_of_archetype: archetypeId,
    buildable: true,
    teacher_mode: true,
    gtm_identity: {
      emotional_job: `Generalized doctrine angled through ${archetypeId}`,
      functional_job: `Practice without naming ${teacherId}`,
      discovery_hook: `A ${archetypeId.replace(/_/g, " ")} path built on lived teaching`,
    },
    emotional_vocabulary: {
      core: [archetypeId, teacherId],
      doctrine_markers: [teacherId, archetypeId],
    },
    generation: { engine: "cf_pages_accept_hybrid", llm: false, deterministic: true },
  };

  hybrids.push({
    brand_id: brandId,
    hybrid_of_archetype: archetypeId,
    ts: new Date().toISOString(),
  });
  try {
    await putJson(aws, env, ledgerKey, { teacher_id: teacherId, lane, hybrids });
    await putJson(aws, env, `${TO_BRAND_PREFIX}${safeKeyPart(brandId)}.json`, brand);
  } catch (err) {
    console.error("accept-hybrid persist failed", err);
    return json({ status: "error", detail: "hybrid persist failed" }, 503);
  }

  const remaining = archetypes.filter((a) => a !== archetypeId && !used.has(a));
  return json(
    {
      status: "hybrid_created",
      brand_id: brandId,
      display_name: display,
      attribution_mode: "generalized",
      hybrid_of_archetype: archetypeId,
      origin_teacher_id: teacherId,
      remaining_archetypes: remaining,
      next: "resubmit_onboarding_with_brand_id",
    },
    200
  );
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}
