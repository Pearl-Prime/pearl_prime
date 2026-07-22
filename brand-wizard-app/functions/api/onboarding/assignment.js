// Cloudflare Pages Function: public-safe live Brand Director assignment lookup.
//
// Canonical brand_admin_brands.json (repo source of truth, deployed as a static
// asset) always wins when it already carries a Brand Director for the brand — see
// assignments.js's rowFromIndex/publicAssignment precedence, which this mirrors.
// POST /api/onboarding/submit writes onboarding/assignments/<brand_id>.json to R2.
// Static ops pages fetch this endpoint to pick up a just-completed Brand Wizard
// assignment before the next repo promotion/deploy. The response deliberately excludes
// email, phone, raw wizard YAML, credentials, and any other contact PII.

import { AwsClient } from "../../_lib/aws4fetch.js";

const DEFAULT_BUCKET = "phoenix-omega-artifacts";
const ASSIGNMENT_PREFIX = "onboarding/assignments/";
const BRAND_RE = /^[a-z0-9][a-z0-9_]{0,127}$/;
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

function baseBrandFromId(brandId) {
  return String(brandId || "").replace(LANE_SUFFIX_RE, "");
}

function isAssignedRecord(record) {
  if (!record || typeof record !== "object") return false;
  const status = String(record.brand_director_status || record.status || "").trim().toLowerCase();
  return (
    status === "assigned" ||
    status === "claimed" ||
    !!String(record.brand_director_name || record.admin_name || "").trim() ||
    !!String(record.brand_director_id || "").trim() ||
    !!String(record.admin_email || "").trim()
  );
}

function publicOnly(record, brandId = "") {
  if (!isAssignedRecord(record)) return null;
  const out = {
    brand_id: String(record.brand_id || brandId || "").trim(),
    base_brand: String(record.base_brand || record.arch || baseBrandFromId(brandId)).trim(),
    display_brand: String(record.display_brand || record.d || brandId).trim(),
    brand_director_name: String(record.brand_director_name || record.admin_name || "").trim(),
    brand_director_id: String(record.brand_director_id || "").trim(),
    brand_director_status: String(record.brand_director_status || record.status || "assigned").trim(),
    assigned_at: String(record.assigned_at || "").trim(),
    assignment_source: String(record.assignment_source || record.source || "brand_admin_brands").trim(),
    source: String(record.source || record.assignment_source || "brand_admin_brands").trim(),
  };
  return out.brand_id && out.brand_director_name ? out : null;
}

async function loadCanonicalAssignment(request, brand) {
  const origin = new URL(request.url).origin;
  const r = await fetch(`${origin}/brand_admin_brands.json`, { cf: { cacheTtl: 60 } });
  if (!r.ok) throw new Error(`brand index fetch failed: ${r.status}`);
  const index = await r.json();
  const record = index && typeof index === "object" ? index[brand] : null;
  return publicOnly(record, brand);
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const brand = String(new URL(request.url).searchParams.get("brand") || "").trim();
  if (!BRAND_RE.test(brand)) {
    return json({ status: "error", detail: "invalid brand" }, 400);
  }

  try {
    const canonical = await loadCanonicalAssignment(request, brand);
    if (canonical) return json(canonical, 200);
  } catch (err) {
    console.error("canonical brand index unreadable for assignment lookup:", err);
  }

  const accessKeyId = String(env.R2_ACCESS_KEY_ID || "").trim();
  const secretAccessKey = String(env.R2_SECRET_ACCESS_KEY || "").trim();
  const accountId = String(env.R2_ACCOUNT_ID || "").trim();
  const haveEndpoint = !!String(env.R2_ENDPOINT || "").trim();
  if (!accessKeyId || !secretAccessKey || (!accountId && !haveEndpoint)) {
    return json({ status: "unconfigured" }, 204);
  }

  const aws = new AwsClient({ accessKeyId, secretAccessKey, region: "auto", service: "s3" });
  const key = `${ASSIGNMENT_PREFIX}${safeKeyPart(brand)}.json`;
  try {
    const got = await fetch(await aws.sign(r2ObjectUrl(env, key)));
    if (got.status === 404 || got.status === 403) return json({ status: "missing" }, 404);
    if (!got.ok) return json({ status: "error", detail: "assignment fetch failed" }, 502);
    const record = publicOnly(await got.json(), brand);
    if (!record) return json({ status: "missing" }, 404);
    return json(record, 200);
  } catch (err) {
    console.error("assignment lookup error:", err);
    return json({ status: "error", detail: "assignment lookup failed" }, 502);
  }
}

export async function onRequest(context) {
  if (context.request.method === "GET") return onRequestGet(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}

function json(obj, status) {
  return new Response(status === 204 ? null : JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}
