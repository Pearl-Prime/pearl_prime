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
const ASSIGNMENT_PREFIX = "onboarding/assignments/";
const HYBRID_PREFIX = "onboarding/hybrids/";

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
  return String(brandId || "").replace(/_(en_us|es_us|es_es|pt_br|zh_tw|zh_hk|zh_cn|zh_sg|ja_jp|ko_kr)$/, "");
}

function publicAssignment(payload, brandId, index, ts) {
  const contact = payload.contact && typeof payload.contact === "object" ? payload.contact : {};
  const name =
    String(payload.brand_director_name || "").trim() ||
    [contact.first_name, contact.last_name].map((v) => String(v || "").trim()).filter(Boolean).join(" ");
  if (!name) return null;
  const entry = index && typeof index === "object" ? index[brandId] : null;
  const displayBrand =
    String(payload.display_brand || "").trim() ||
    String(payload.publication_corp || "").trim() ||
    (entry && String(entry.d || "").trim()) ||
    brandId;
  return {
    brand_id: brandId,
    base_brand: String(payload.base_brand || "").trim() || baseBrandFromId(brandId),
    display_brand: displayBrand,
    brand_director_name: name,
    brand_director_id: String(payload.brand_director_id || "").trim() || directorIdFromName(name),
    brand_director_status: "assigned",
    assigned_at: ts,
    assignment_source: "brand_onboarding_wizard",
    source: "r2_live_assignment",
  };
}

async function putJson(aws, env, key, value, { conditionalCreate = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  // Conditional create: only write when the object does not already exist (S3/R2 If-None-Match: *).
  // Prevents two concurrent wizard submits from silently overwriting the first claim.
  if (conditionalCreate) headers["If-None-Match"] = "*";
  const putReq = await aws.sign(r2ObjectUrl(env, key), {
    method: "PUT",
    headers,
    body: JSON.stringify(value),
  });
  return fetch(putReq);
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
        // Second claimant gets a generalized-hybrid offer (doctrine without naming).
        let available = [];
        try {
          const origin = new URL(request.url).origin;
          const archResp = await fetch(`${origin}/brand_archetype_ids.json`, { cf: { cacheTtl: 300 } });
          if (archResp.ok) {
            const body = await archResp.json();
            if (Array.isArray(body?.archetypes)) available = body.archetypes.slice();
          }
        } catch (_) {}
        try {
          const ledgerKey = `${HYBRID_PREFIX}${safeKeyPart(lane)}__${safeKeyPart(tid)}.json`;
          const ledger = await fetch(await aws.sign(r2ObjectUrl(env, ledgerKey)));
          if (ledger.ok) {
            const prior = await ledger.json();
            const used = new Set(
              (Array.isArray(prior?.hybrids) ? prior.hybrids : [])
                .map((h) => h?.hybrid_of_archetype)
                .filter(Boolean)
            );
            available = available.filter((a) => !used.has(a));
          }
        } catch (_) {}
        return json(
          {
            error: "teacher_claimed",
            brand_id: existingBrand,
            teacher_id: tid,
            lane,
            offer: {
              teacher_id: tid,
              available_archetypes: available.slice(0, 40),
              attribution_mode: "generalized",
            },
            message:
              "Teacher already claimed in this lane. Accept a generalized hybrid brand (doctrine, no teacher name) via /api/onboarding/accept-hybrid.",
          },
          409
        );
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

  const assignment = publicAssignment(payload, brandId, index, ts);

  // --- Publish the live public-safe assignment overlay FIRST (conditional claim) -----
  // Claim must beat the race before we persist the full submission. If-None-Match: *
  // means a concurrent wizard submit that lost returns 409 with the winner's name.
  // The static ops dashboard reads this by brand_id, so wizard completion becomes live
  // immediately even before an operator promotes the YAML into the repo. No email/phone
  // or raw wizard YAML is written to this public-safe object.
  if (assignment) {
    const assignmentKey = `${ASSIGNMENT_PREFIX}${safeKeyPart(brandId)}.json`;
    try {
      // Optimistic existence check (also matches Pages/test harness GET-before-PUT sequencing).
      const existingAssignment = await fetch(await aws.sign(r2ObjectUrl(env, assignmentKey)));
      if (existingAssignment.status === 200) {
        let assignedTo = "";
        try {
          const prior = await existingAssignment.json();
          assignedTo = String(prior?.brand_director_name || "").trim();
        } catch (_) {}
        return json(
          {
            error: "brand_claimed",
            brand_id: brandId,
            assigned_to: assignedTo || "another brand director",
            message: "This brand was just claimed by another Brand Director. Pick a different brand.",
          },
          409,
        );
      }
      const put = await putJson(aws, env, assignmentKey, assignment, { conditionalCreate: true });
      if (put.status === 412) {
        // Another submit won the race — surface the prior public-safe assignment.
        let assignedTo = "";
        try {
          const got = await fetch(await aws.sign(r2ObjectUrl(env, assignmentKey)));
          if (got.ok) {
            const prior = await got.json();
            assignedTo = String(prior?.brand_director_name || "").trim();
          }
        } catch (err) {
          console.error("assignment race re-fetch error:", err);
        }
        return json(
          {
            error: "brand_claimed",
            brand_id: brandId,
            assigned_to: assignedTo || "another brand director",
            message: "This brand was just claimed by another Brand Director. Pick a different brand.",
          },
          409,
        );
      }
      if (!put.ok) {
        console.error(`assignment PUT failed (${put.status}) for ${assignmentKey}`);
        return json({ status: "error", detail: "assignment not persisted", claim }, 502);
      }
    } catch (err) {
      console.error("assignment PUT error:", err);
      return json({ status: "error", detail: "assignment not persisted", claim }, 502);
    }
  }

  // --- Persist the full submission ------------------------------------------------------
  const emailPart = safeKeyPart(email || "anon");
  const subKey = `${SUBMISSION_PREFIX}${emailPart}__${safeKeyPart(brandId)}__${safeKeyPart(ts)}.json`;
  const subUrl = r2ObjectUrl(env, subKey);
  const record = {
    ...payload,
    brand_id: brandId,
    is_teacher: isTeacher,
    teacher_tid: tid || null,
    brand_assignment: assignment,
    ts,
  };
  try {
    const putReq = await aws.sign(subUrl, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
    const put = await fetch(putReq);
    if (!put.ok) {
      console.error(`submission PUT failed (${put.status}) for ${subKey}`);
      // Submission storage failed, but a recorded teacher/assignment claim still stands.
      // Surface a soft error; the client's catch ignores it and the success screen is unaffected.
      return json({ status: "error", detail: "submission not persisted", claim }, 502);
    }
  } catch (err) {
    console.error("submission PUT error:", err);
    return json({ status: "error", detail: "submission not persisted", claim }, 502);
  }

  return json({ ok: true, key: subKey, claim, assignment }, 200);
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
