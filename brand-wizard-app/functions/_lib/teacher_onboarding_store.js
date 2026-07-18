// Shared R2 / local-mock store helpers for teacher onboarding portal v2.
import { AwsClient } from "./aws4fetch.js";

export const DEFAULT_BUCKET = "phoenix-omega-artifacts";
export const DRAFT_PREFIX = "teacher_onboarding/drafts/";
export const DRAFT_TOKEN_PREFIX = "teacher_onboarding/drafts_by_token/";
export const SUBMISSION_PREFIX = "teacher_onboarding/submissions/";
export const ACTIVATION_PREFIX = "teacher_onboarding/activations/";
export const MAX_BODY_BYTES = 1024 * 1024;

export function r2ObjectUrl(env, keyOrQuery = "") {
  const bucket = (env.R2_BUCKET || DEFAULT_BUCKET).trim();
  const endpoint =
    (env.R2_ENDPOINT || "").trim() ||
    `https://${String(env.R2_ACCOUNT_ID || "").trim()}.r2.cloudflarestorage.com`;
  return `${endpoint.replace(/\/$/, "")}/${bucket}${keyOrQuery.startsWith("?") || keyOrQuery.startsWith("/") ? keyOrQuery : `/${keyOrQuery}`}`;
}

export function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

export function safeKeyPart(value) {
  return (
    String(value || "")
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9._-]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 120) || "teacher"
  );
}

export function r2Configured(env) {
  const accessKeyId = String(env.R2_ACCESS_KEY_ID || "").trim();
  const secretAccessKey = String(env.R2_SECRET_ACCESS_KEY || "").trim();
  const accountId = String(env.R2_ACCOUNT_ID || "").trim();
  const haveEndpoint = !!String(env.R2_ENDPOINT || "").trim();
  return !!(accessKeyId && secretAccessKey && (accountId || haveEndpoint));
}

export function makeAws(env) {
  return new AwsClient({
    accessKeyId: String(env.R2_ACCESS_KEY_ID || "").trim(),
    secretAccessKey: String(env.R2_SECRET_ACCESS_KEY || "").trim(),
    region: "auto",
    service: "s3",
  });
}

export function mockEnabled(env) {
  return String(env.TEACHER_PORTAL_MOCK || "").trim() === "1";
}

// In-memory mock for wrangler/local Function unit tests. The Node mock server
// uses a filesystem store instead; Pages Functions use this Map when MOCK=1.
const MEMORY = globalThis.__TEACHER_PORTAL_MOCK_STORE || new Map();
if (!globalThis.__TEACHER_PORTAL_MOCK_STORE) {
  globalThis.__TEACHER_PORTAL_MOCK_STORE = MEMORY;
}

export async function putJson(env, key, value) {
  if (mockEnabled(env) || !r2Configured(env)) {
    if (!mockEnabled(env) && !r2Configured(env)) {
      return { ok: false, status: 503, unconfigured: true };
    }
    MEMORY.set(key, JSON.stringify(value));
    return { ok: true, status: 200, mock: true };
  }
  const aws = makeAws(env);
  const putReq = await aws.sign(r2ObjectUrl(env, key), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(value),
  });
  const res = await fetch(putReq);
  return { ok: res.ok, status: res.status };
}

export async function getJson(env, key) {
  if (mockEnabled(env) || !r2Configured(env)) {
    if (!mockEnabled(env) && !r2Configured(env)) {
      return { ok: false, status: 503, unconfigured: true };
    }
    if (!MEMORY.has(key)) return { ok: false, status: 404 };
    return { ok: true, status: 200, value: JSON.parse(MEMORY.get(key)), mock: true };
  }
  const aws = makeAws(env);
  const got = await fetch(await aws.sign(r2ObjectUrl(env, key), { method: "GET" }));
  if (!got.ok) return { ok: false, status: got.status };
  try {
    return { ok: true, status: 200, value: await got.json() };
  } catch (_err) {
    return { ok: false, status: 502 };
  }
}

export async function deleteKey(env, key) {
  if (mockEnabled(env) || !r2Configured(env)) {
    if (!mockEnabled(env) && !r2Configured(env)) {
      return { ok: false, status: 503, unconfigured: true };
    }
    MEMORY.delete(key);
    return { ok: true, status: 204, mock: true };
  }
  const aws = makeAws(env);
  const del = await fetch(await aws.sign(r2ObjectUrl(env, key), { method: "DELETE" }));
  return { ok: del.ok || del.status === 404, status: del.status };
}

export async function listPrefix(env, prefix, maxKeys = 100) {
  if (mockEnabled(env) || !r2Configured(env)) {
    if (!mockEnabled(env) && !r2Configured(env)) {
      return { ok: false, status: 503, unconfigured: true, keys: [] };
    }
    const keys = [...MEMORY.keys()].filter((k) => k.startsWith(prefix)).slice(0, maxKeys);
    return { ok: true, status: 200, keys, mock: true };
  }
  const aws = makeAws(env);
  const params = new URLSearchParams({
    "list-type": "2",
    prefix,
    "max-keys": String(maxKeys),
  });
  const listed = await fetch(await aws.sign(r2ObjectUrl(env, `?${params.toString()}`)));
  if (!listed.ok) return { ok: false, status: listed.status, keys: [] };
  const text = await listed.text();
  const keys = [];
  const re = /<Key>([^<]+)<\/Key>/g;
  let match;
  while ((match = re.exec(text))) {
    keys.push(match[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">"));
  }
  return { ok: true, status: 200, keys };
}

export function requireStore(env) {
  if (mockEnabled(env)) return null;
  if (!r2Configured(env)) {
    return json(
      { ok: false, status: "unconfigured", detail: "R2 credentials not configured on this Pages deploy" },
      503
    );
  }
  return null;
}

export function randomToken(bytes = 24) {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  let bin = "";
  arr.forEach((b) => {
    bin += String.fromCharCode(b);
  });
  // URL-safe base64
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

export function randomId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return `draft_${randomToken(16)}`;
}

export function extractEditToken(request, body = null) {
  const url = new URL(request.url);
  const q = url.searchParams.get("edit_token") || url.searchParams.get("token");
  if (q) return String(q).trim();
  const header = request.headers.get("X-Edit-Token");
  if (header) return String(header).trim();
  if (body && typeof body === "object") {
    const t = body.edit_token || body.token;
    if (t) return String(t).trim();
  }
  return "";
}

export function publicDraft(record) {
  if (!record || typeof record !== "object") return null;
  return {
    draft_id: record.draft_id,
    status: record.status,
    created_at: record.created_at,
    updated_at: record.updated_at,
    teacher_id: record.teacher_id || "",
    teacher_name: record.teacher_name || "",
    submission_key: record.submission_key || null,
    server_policy: {
      production_atoms_created: false,
      operator_review_required: true,
      client_readiness_trusted_for_production: false,
    },
  };
}

export function newDraftRecord({ teacher_id = "", teacher_name = "", ui_state = {} } = {}) {
  const now = new Date().toISOString();
  const draft_id = randomId();
  const edit_token = randomToken(24);
  return {
    schema_version: "teacher_onboarding_draft_v1",
    draft_id,
    edit_token,
    status: "draft",
    created_at: now,
    updated_at: now,
    teacher_id: safeKeyPart(teacher_id || teacher_name || "teacher"),
    teacher_name: String(teacher_name || "").trim(),
    ui_state: ui_state && typeof ui_state === "object" ? ui_state : {},
    server_policy: {
      production_atoms_created: false,
      operator_review_required: true,
      client_readiness_trusted_for_production: false,
    },
    submission_key: null,
  };
}
