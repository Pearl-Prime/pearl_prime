// Cloudflare Pages Function: public-safe live Brand Director assignment lookup.
//
// POST /api/onboarding/submit writes onboarding/assignments/<brand_id>.json to R2.
// Static ops pages fetch this endpoint to pick up a just-completed Brand Wizard
// assignment before the next repo promotion/deploy. The response deliberately excludes
// email, phone, raw wizard YAML, credentials, and any other contact PII.

import { AwsClient } from "../../_lib/aws4fetch.js";

const DEFAULT_BUCKET = "phoenix-omega-artifacts";
const ASSIGNMENT_PREFIX = "onboarding/assignments/";
const BRAND_RE = /^[a-z0-9][a-z0-9_]{0,127}$/;

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

function publicOnly(record) {
  if (!record || typeof record !== "object") return null;
  const out = {};
  for (const key of [
    "brand_id",
    "base_brand",
    "display_brand",
    "brand_director_name",
    "brand_director_id",
    "brand_director_status",
    "assigned_at",
    "assignment_source",
    "source",
  ]) {
    if (record[key]) out[key] = record[key];
  }
  return out.brand_id && out.brand_director_name ? out : null;
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const brand = String(new URL(request.url).searchParams.get("brand") || "").trim();
  if (!BRAND_RE.test(brand)) {
    return json({ status: "error", detail: "invalid brand" }, 400);
  }

  // The committed brand index is authoritative once a director is assigned.
  // Live R2 assignments only fill brands that have not reached that canonical state.
  try {
    const canonicalUrl = new URL("/brand_admin_brands.json", request.url).toString();
    const canonicalResponse = await fetch(canonicalUrl);
    if (canonicalResponse.ok) {
      const canonicalIndex = await canonicalResponse.json();
      const canonical = canonicalIndex?.[brand];
      if (canonical?.brand_director_name) {
        return json(
          {
            brand_id: brand,
            base_brand: canonical.arch,
            display_brand: canonical.d,
            brand_director_name: canonical.brand_director_name,
            brand_director_id: canonical.brand_director_id,
            brand_director_status: canonical.brand_director_status || "assigned",
            source: "brand_admin_brands",
          },
          200,
        );
      }
    }
  } catch (err) {
    console.error("canonical assignment lookup error:", err);
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
    const record = publicOnly(await got.json());
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
