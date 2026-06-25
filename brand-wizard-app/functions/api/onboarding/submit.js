// Cloudflare Pages Function: brand-wizard signup persistence — R2-native.
//
// The static Pages deploy has no reachable FastAPI backend (server/app.py is not hosted
// anywhere Cloudflare Pages can fetch), so the previous proxy version (#1931) persisted
// nothing in production. This Function instead writes signups DIRECTLY to R2 via the
// S3-compatible API — the same pattern as functions/download/[book_id].js (#1886):
//   AwsClient (SigV4, cross-account creds) + r2ObjectUrl(env, key).
// No ONBOARDING_API_BASE / FastAPI hop.
//
// It also enforces teacher exclusivity in-Function (ports #1933's server-side 409 rule):
// a teacher brand is one real person's voice, so only ONE admin may claim it. Teacher
// identity is DERIVED from the authoritative brand index (brand_admin_brands.json), not
// trusted from the client body — the wizard does not send is_teacher/teacher_tid, and an
// older/forged client must not be able to bypass the 1:1 rule. Claims are keyed by
// "<lane>__<tid>" so the same teacher slug in different lanes stays distinct.
//
// Fail-open discipline (mirrors #1933): R2 read errors other than "no claim" (404/403)
// never block a legitimate sign-up — we log and allow the submission.

import { AwsClient } from "../../_lib/aws4fetch.js";

const MAX_BODY_BYTES = 256 * 1024; // wizard_yaml is capped ~200k upstream; allow headroom.
const DEFAULT_BUCKET = "phoenix-omega-artifacts";
const CLAIM_PREFIX = "onboarding/claimed/";
const SUBMISSION_PREFIX = "onboarding/submissions/";

function r2ObjectUrl(env, key) {
  const bucket = (env.R2_BUCKET || DEFAULT_BUCKET).trim();
  const endpoint =
    (env.R2_ENDPOINT || "").trim() ||
    `https://${String(env.R2_ACCOUNT_ID || "").trim()}.r2.cloudflarestorage.com`;
  return `${endpoint.replace(/\/$/, "")}/${bucket}/${key}`;
}

// Safe component for an R2 object key: keep [a-z0-9._-], collapse the rest to "_".
function safeKeyPart(s) {
  return (
    String(s || "")
      .toLowerCase()
      .replace(/[^a-z0-9._-]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 200) || "x"
  );
}

// Load the authoritative brand index from the co-deployed static asset. Same-origin fetch
// so it works on any *.pages.dev / custom domain without an extra binding.
async function loadBrandIndex(request) {
  try {
    const origin = new URL(request.url).origin;
    const r = await fetch(`${origin}/brand_admin_brands.json`, { cf: { cacheTtl: 60 } });
    if (!r.ok) return {};
    return await r.json();
  } catch (err) {
    console.error("brand index unreadable (fail-open, no teacher gate):", err);
    return {};
  }
}

// Derive teacher identity from the index. Returns { isTeacher, lane, tid } — never trusts
// the client body. Unknown brand or non-teacher -> isTeacher:false (never blocked).
function teacherIdentity(brandId, index) {
  const entry = index && typeof index === "object" ? index[brandId] : null;
  if (!entry || typeof entry !== "object" || !entry.is_teacher) {
    return { isTeacher: false, lane: "", tid: "" };
  }
  const tid = String(entry.tid || "").trim();
  const lane = String(entry.lane || "").trim() || "unknown_lane";
  if (!tid) return { isTeacher: false, lane: "", tid: "" };
  return { isTeacher: true, lane, tid };
}

export async function onRequestPost(context) {
  const { request, env } = context;

  // --- Parse + lightly validate the client payload --------------------------------------
  let payload;
  try {
    const raw = await request.text();
    if (raw.length > MAX_BODY_BYTES) {
      return json({ status: "error", detail: "payload too large" }, 413);
    }
    payload = JSON.parse(raw || "{}");
  } catch (_err) {
    return json({ status: "error", detail: "invalid JSON body" }, 400);
  }
  if (!payload || typeof payload !== "object" || !payload.brand_id || !payload.wizard_yaml) {
    return json({ status: "error", detail: "brand_id and wizard_yaml are required" }, 400);
  }

  const brandId = String(payload.brand_id).trim();
  const email = String(payload.brand_email || "").trim();

  // --- R2 client (cross-account S3 creds, like the download Function) --------------------
  const accessKeyId = String(env.R2_ACCESS_KEY_ID || "").trim();
  const secretAccessKey = String(env.R2_SECRET_ACCESS_KEY || "").trim();
  const accountId = String(env.R2_ACCOUNT_ID || "").trim();
  const haveEndpoint = !!String(env.R2_ENDPOINT || "").trim();
  if (!accessKeyId || !secretAccessKey || (!accountId && !haveEndpoint)) {
    // No persistence configured. Degrade gracefully (not a crash): the client already
    // holds the match in localStorage, and the success screen does not depend on us.
    return json(
      { status: "unconfigured", detail: "R2 credentials not configured on this Pages deploy" },
      503,
    );
  }
  const aws = new AwsClient({ accessKeyId, secretAccessKey, region: "auto", service: "s3" });

  // --- Teacher exclusivity (derive identity from the authoritative index) ---------------
  const index = await loadBrandIndex(request);
  const { isTeacher, lane, tid } = teacherIdentity(brandId, index);
  const ts = new Date().toISOString();
  let claim = null;

  if (isTeacher) {
    const claimKey = `${CLAIM_PREFIX}${safeKeyPart(lane)}__${safeKeyPart(tid)}.json`;
    const claimUrl = r2ObjectUrl(env, claimKey);
    try {
      const existing = await fetch(await aws.sign(claimUrl)); // GET
      if (existing.status === 200) {
        // Already claimed by another admin -> hard 1:1 block.
        let existingBrand = brandId;
        try {
          const prior = await existing.json();
          if (prior && prior.brand_id) existingBrand = prior.brand_id;
        } catch (_) {}
        return json({ error: "teacher_claimed", brand_id: existingBrand }, 409);
      }
      if (existing.status === 404 || existing.status === 403) {
        // Not claimed yet (404 = missing; 403 = some R2 configs return this for absent keys).
        // Record the claim marker, then continue to persist the submission.
        const body = JSON.stringify({ brand_id: brandId, email, ts });
        try {
          const putReq = await aws.sign(claimUrl, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body,
          });
          const put = await fetch(putReq);
          if (put.ok) {
            claim = { key: claimKey, brand_id: brandId };
          } else {
            console.error(`teacher claim PUT failed (${put.status}) for ${claimKey}; allowing submit`);
          }
        } catch (err) {
          console.error("teacher claim PUT error (fail-open, allowing submit):", err);
        }
      } else {
        // Unexpected status (5xx, etc.) — fail open, do NOT block a legit sign-up.
        console.error(`teacher claim GET unexpected status ${existing.status}; failing open`);
      }
    } catch (err) {
      console.error("teacher claim check error (fail-open, allowing submit):", err);
    }
  }

  // --- Persist the full submission ------------------------------------------------------
  const emailPart = safeKeyPart(email || "anon");
  const subKey = `${SUBMISSION_PREFIX}${emailPart}__${safeKeyPart(brandId)}__${safeKeyPart(ts)}.json`;
  const subUrl = r2ObjectUrl(env, subKey);
  const record = { ...payload, brand_id: brandId, is_teacher: isTeacher, teacher_tid: tid || null, ts };
  try {
    const putReq = await aws.sign(subUrl, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
    const put = await fetch(putReq);
    if (!put.ok) {
      console.error(`submission PUT failed (${put.status}) for ${subKey}`);
      // Submission storage failed, but a recorded teacher claim still stands. Surface a
      // soft error; the client's catch ignores it and the success screen is unaffected.
      return json({ status: "error", detail: "submission not persisted", claim }, 502);
    }
  } catch (err) {
    console.error("submission PUT error:", err);
    return json({ status: "error", detail: "submission not persisted", claim }, 502);
  }

  return json({ ok: true, key: subKey, claim }, 200);
}

// Non-POST methods → 405 (clearer than a generic 404 for a misrouted client).
export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}
