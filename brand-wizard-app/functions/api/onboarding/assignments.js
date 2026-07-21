// Cloudflare Pages Function: public-safe Brand Director assignment roster.
//
// GET /api/onboarding/assignments returns all brand-lane rows from the deployed
// static brand index, merged with live R2 assignment overlays written by
// POST /api/onboarding/submit. It exposes only public-safe director fields.

import { AwsClient } from "../../_lib/aws4fetch.js";

const DEFAULT_BUCKET = "phoenix-omega-artifacts";
const ASSIGNMENT_PREFIX = "onboarding/assignments/";
const ASSIGNMENT_EVENTS_PREFIX = "onboarding/assignment_events/";
const CLAIM_PREFIX = "onboarding/claimed/";
const BRAND_RE = /^[a-z0-9][a-z0-9_]{0,127}$/;
const LANE_SUFFIX_RE = /_(en_us|es_us|es_es|fr_fr|de_de|it_it|hu_hu|pt_br|zh_tw|zh_hk|zh_cn|zh_sg|ja_jp|ko_kr)$/;
const XML_ENTITY_RE = /&(amp|lt|gt|quot|apos);/g;

function r2ObjectUrl(env, keyOrQuery = "") {
  const bucket = (env.R2_BUCKET || DEFAULT_BUCKET).trim();
  const endpoint =
    (env.R2_ENDPOINT || "").trim() ||
    `https://${String(env.R2_ACCOUNT_ID || "").trim()}.r2.cloudflarestorage.com`;
  return `${endpoint.replace(/\/$/, "")}/${bucket}${keyOrQuery}`;
}

function baseBrandFromId(brandId) {
  return String(brandId || "").replace(LANE_SUFFIX_RE, "");
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

function laneFromId(brandId) {
  const match = String(brandId || "").match(LANE_SUFFIX_RE);
  return match ? match[1].toUpperCase().replace("_", "_") : "";
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

function publicAssignment(record, brandId = "") {
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
  if (!out.brand_id || !out.brand_director_name) return null;
  return out;
}

function assignmentFromAdminPayload(payload, brandId, index) {
  const name = String(payload.brand_director_name || "").trim();
  if (!name) return null;
  const entry = index && typeof index === "object" ? index[brandId] : null;
  const directorId =
    String(payload.brand_director_id || "").trim() ||
    name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 80) ||
    "brand_director";
  return {
    brand_id: brandId,
    base_brand: String(payload.base_brand || entry?.arch || baseBrandFromId(brandId)).trim(),
    display_brand: String(payload.display_brand || entry?.display_brand || entry?.d || brandId).trim(),
    brand_director_name: name,
    brand_director_id: directorId,
    brand_director_status: "assigned",
    assigned_at: new Date().toISOString(),
    assignment_source: "brand_director_admin",
    source: "r2_live_assignment",
    assignment_version: 2,
  };
}

function rowFromIndex(brandId, record, overlay) {
  const canonical = publicAssignment(record, brandId);
  const assignment = canonical || overlay || null;
  const lifecycle = String(record.lifecycle || "unknown").trim() || "unknown";
  const buildable = record.buildable !== false;
  const active = lifecycle.toLowerCase() === "active";
  const baseBrand = String(record.arch || assignment?.base_brand || baseBrandFromId(brandId)).trim();
  const displayBrand = String(assignment?.display_brand || record.display_brand || record.d || brandId).trim();
  const wizardAccess = buildable ? "available" : "blocked";
  const opsAccess = buildable ? "available" : "blocked";

  return {
    brand_id: brandId,
    base_brand: baseBrand,
    display_brand: displayBrand,
    lane: String(record.lane || laneFromId(brandId)).trim(),
    teacher: String(record.t || "").trim(),
    teacher_id: String(record.tid || "").trim(),
    is_teacher: !!record.is_teacher,
    lifecycle,
    active,
    buildable,
    brand_director_name: assignment?.brand_director_name || "",
    brand_director_id: assignment?.brand_director_id || "",
    brand_director_status: assignment?.brand_director_status || "unassigned",
    assigned_at: assignment?.assigned_at || "",
    assignment_source: assignment?.assignment_source || "none",
    source: assignment?.source || "none",
    wizard_url: `/wizard.html?brand=${encodeURIComponent(brandId)}`,
    // Real-asset-gated Brand Director Operations (never stale brand_admin.html phantom titles).
    ops_url: `/brand_handoff_dashboard.html?brand=${encodeURIComponent(brandId)}`,
    wizard_access: wizardAccess,
    ops_access: opsAccess,
    manga_pct: typeof record.manga_pct === "number" ? record.manga_pct : null,
  };
}

function summaryFor(rows) {
  const assigned = rows.filter((row) => row.brand_director_name).length;
  return {
    total: rows.length,
    assigned,
    unassigned: rows.length - assigned,
    active: rows.filter((row) => row.active).length,
    inactive: rows.filter((row) => !row.active).length,
    wizard_ready: rows.filter((row) => row.wizard_access === "available").length,
    ops_ready: rows.filter((row) => row.ops_access === "available").length,
  };
}

async function loadBrandIndex(request) {
  const origin = new URL(request.url).origin;
  const r = await fetch(`${origin}/brand_admin_brands.json`, { cf: { cacheTtl: 60 } });
  if (!r.ok) throw new Error(`brand index fetch failed: ${r.status}`);
  const index = await r.json();
  return index && typeof index === "object" && !Array.isArray(index) ? index : {};
}

function haveR2(env) {
  const accessKeyId = String(env.R2_ACCESS_KEY_ID || "").trim();
  const secretAccessKey = String(env.R2_SECRET_ACCESS_KEY || "").trim();
  const accountId = String(env.R2_ACCOUNT_ID || "").trim();
  const haveEndpoint = !!String(env.R2_ENDPOINT || "").trim();
  return !!accessKeyId && !!secretAccessKey && (!!accountId || haveEndpoint);
}

function haveAdminToken(env) {
  return !!String(env.BRAND_DIRECTOR_ADMIN_TOKEN || "").trim();
}

function authorized(request, env) {
  const expected = String(env.BRAND_DIRECTOR_ADMIN_TOKEN || "").trim();
  const got = String(request.headers.get("x-admin-token") || "").trim();
  return !!expected && !!got && got === expected;
}

function awsClient(env) {
  return new AwsClient({
    accessKeyId: String(env.R2_ACCESS_KEY_ID || "").trim(),
    secretAccessKey: String(env.R2_SECRET_ACCESS_KEY || "").trim(),
    region: "auto",
    service: "s3",
  });
}

async function putJson(aws, env, key, value, headers = {}) {
  const putReq = await aws.sign(r2ObjectUrl(env, `/${key}`), {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(value),
  });
  return fetch(putReq);
}

async function deleteObject(aws, env, key) {
  const deleteReq = await aws.sign(r2ObjectUrl(env, `/${key}`), { method: "DELETE" });
  return fetch(deleteReq);
}

async function recordAssignmentEvent(aws, env, action, payload = {}) {
  const ts = new Date().toISOString();
  const brandId = safeKeyPart(payload.brand_id || "unknown");
  const key = `${ASSIGNMENT_EVENTS_PREFIX}${safeKeyPart(ts)}__${brandId}__${safeKeyPart(action)}.json`;
  const event = {
    event: action,
    brand_id: payload.brand_id || "",
    brand_director_name: payload.brand_director_name || "",
    brand_director_id: payload.brand_director_id || "",
    source: payload.source || "brand_director_admin",
    ts,
  };
  try {
    await putJson(aws, env, key, event);
  } catch (err) {
    console.error("assignment event write failed:", err);
  }
}

function teacherClaimKey(brandId, index) {
  const entry = index && typeof index === "object" ? index[brandId] : null;
  if (!entry || typeof entry !== "object" || !entry.is_teacher || !entry.tid) return "";
  return `${CLAIM_PREFIX}${safeKeyPart(entry.lane || "unknown_lane")}__${safeKeyPart(entry.tid)}.json`;
}

function xmlDecode(value) {
  return String(value || "").replace(XML_ENTITY_RE, (_m, entity) => {
    if (entity === "amp") return "&";
    if (entity === "lt") return "<";
    if (entity === "gt") return ">";
    if (entity === "quot") return '"';
    if (entity === "apos") return "'";
    return _m;
  });
}

function xmlValues(text, tag) {
  const re = new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`, "g");
  const values = [];
  let match;
  while ((match = re.exec(text))) values.push(xmlDecode(match[1]));
  return values;
}

async function listAssignmentKeys(aws, env) {
  const keys = [];
  let continuation = "";
  for (let page = 0; page < 10; page += 1) {
    const params = new URLSearchParams({
      "list-type": "2",
      prefix: ASSIGNMENT_PREFIX,
      "max-keys": "1000",
    });
    if (continuation) params.set("continuation-token", continuation);
    const listed = await fetch(await aws.sign(r2ObjectUrl(env, `?${params.toString()}`)));
    if (!listed.ok) throw new Error(`assignment list failed: ${listed.status}`);
    const text = await listed.text();
    keys.push(...xmlValues(text, "Key").filter((key) => key.startsWith(ASSIGNMENT_PREFIX) && key.endsWith(".json")));
    const truncated = xmlValues(text, "IsTruncated")[0] === "true";
    continuation = xmlValues(text, "NextContinuationToken")[0] || "";
    if (!truncated || !continuation) break;
  }
  return keys;
}

async function loadR2Assignments(env) {
  if (!haveR2(env)) return { configured: false, overlays: {}, error: "" };
  const aws = awsClient(env);
  const overlays = {};
  try {
    const keys = await listAssignmentKeys(aws, env);
    await Promise.all(
      keys.map(async (key) => {
        const got = await fetch(await aws.sign(r2ObjectUrl(env, `/${key}`)));
        if (!got.ok) return;
        const record = publicAssignment(await got.json());
        if (record?.brand_id) overlays[record.brand_id] = { ...record, source: "r2_live_assignment" };
      }),
    );
    return { configured: true, overlays, error: "" };
  } catch (err) {
    console.error("assignment roster R2 overlay error:", err);
    return { configured: true, overlays, error: "r2_overlay_unavailable" };
  }
}

export async function onRequestGet(context) {
  const { request, env } = context;
  let index;
  try {
    index = await loadBrandIndex(request);
  } catch (err) {
    console.error("brand index unreadable for assignments roster:", err);
    return json({ status: "error", detail: "brand index unavailable" }, 502);
  }

  const r2 = await loadR2Assignments(env);
  const rows = Object.entries(index)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([brandId, record]) => rowFromIndex(brandId, record || {}, r2.overlays[brandId]));

  return json(
    {
      status: "ok",
      generated_at: new Date().toISOString(),
      source: {
        static_brand_count: Object.keys(index).length,
        r2_overlay_count: Object.keys(r2.overlays).length,
        r2_configured: r2.configured,
        r2_status: r2.error || "ok",
        admin_actions_configured: haveAdminToken(env),
      },
      summary: summaryFor(rows),
      brands: rows,
    },
    200,
  );
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!haveR2(env)) return json({ status: "error", detail: "R2 credentials not configured" }, 503);
  if (!haveAdminToken(env)) return json({ status: "error", detail: "admin token not configured" }, 403);
  if (!authorized(request, env)) return json({ status: "error", detail: "unauthorized" }, 401);

  let payload;
  try {
    payload = await request.json();
  } catch (_) {
    return json({ status: "error", detail: "invalid JSON body" }, 400);
  }

  const action = String(payload?.action || "").trim().toLowerCase();
  const brandId = String(payload?.brand_id || "").trim();
  if (!BRAND_RE.test(brandId)) return json({ status: "error", detail: "invalid brand_id" }, 400);

  let index;
  try {
    index = await loadBrandIndex(request);
  } catch (err) {
    console.error("brand index unreadable for assignments admin action:", err);
    return json({ status: "error", detail: "brand index unavailable" }, 502);
  }

  const indexRecord = index[brandId] || {};
  const canonical = publicAssignment(indexRecord, brandId);
  const aws = awsClient(env);
  const assignmentKey = `${ASSIGNMENT_PREFIX}${safeKeyPart(brandId)}.json`;

  if (action === "release") {
    if (canonical) {
      return json(
        {
          status: "blocked",
          detail: "promoted assignment must be changed in the repo source of truth",
          brand_id: brandId,
        },
        409,
      );
    }
    const deleted = await deleteObject(aws, env, assignmentKey);
    if (!deleted.ok && deleted.status !== 404) {
      return json({ status: "error", detail: "release failed", brand_id: brandId }, 502);
    }
    const teacherKey = teacherClaimKey(brandId, index);
    if (teacherKey) await deleteObject(aws, env, teacherKey);
    await recordAssignmentEvent(aws, env, "released", { brand_id: brandId });
    return json({ status: "ok", action, brand_id: brandId }, 200);
  }

  if (action === "assign" || action === "reassign") {
    if (canonical) {
      return json(
        {
          status: "blocked",
          detail: "promoted assignment must be changed in the repo source of truth",
          brand_id: brandId,
        },
        409,
      );
    }
    const assignment = assignmentFromAdminPayload(payload, brandId, index);
    if (!assignment) return json({ status: "error", detail: "brand_director_name is required" }, 422);
    const put = await putJson(aws, env, assignmentKey, assignment);
    if (!put.ok) {
      return json({ status: "error", detail: "assignment write failed", brand_id: brandId }, 502);
    }
    await recordAssignmentEvent(aws, env, action === "assign" ? "admin_assigned" : "admin_reassigned", assignment);
    return json({ status: "ok", action, brand_id: brandId, assignment: publicAssignment(assignment, brandId) }, 200);
  }

  return json({ status: "error", detail: "unsupported action" }, 400);
}

export async function onRequest(context) {
  if (context.request.method === "GET") return onRequestGet(context);
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}
