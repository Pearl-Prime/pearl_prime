#!/usr/bin/env node
/**
 * Local filesystem mock for teacher-portal v2 APIs.
 * Mirrors Pages Function routes under /api/teacher-onboarding/*
 * Store root: TEACHER_PORTAL_DEV_STORE (default /tmp/teacher_portal_dev_<pid>)
 *
 * Usage: node server/teacher_portal_dev_api.mjs [--port 8790]
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(
  process.argv.includes("--port")
    ? process.argv[process.argv.indexOf("--port") + 1]
    : process.env.TEACHER_PORTAL_DEV_PORT || 8790
);
const STORE =
  process.env.TEACHER_PORTAL_DEV_STORE ||
  path.join("/tmp", `teacher_portal_dev_${process.pid}`);

const DRAFT_PREFIX = "teacher_onboarding/drafts/";
const DRAFT_TOKEN_PREFIX = "teacher_onboarding/drafts_by_token/";
const SUBMISSION_PREFIX = "teacher_onboarding/submissions/";
const ACTIVATION_PREFIX = "teacher_onboarding/activations/";

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function keyPath(key) {
  return path.join(STORE, key);
}

function putJson(key, value) {
  const fp = keyPath(key);
  ensureDir(path.dirname(fp));
  fs.writeFileSync(fp, JSON.stringify(value, null, 2));
}

function getJson(key) {
  const fp = keyPath(key);
  if (!fs.existsSync(fp)) return null;
  return JSON.parse(fs.readFileSync(fp, "utf8"));
}

function deleteKey(key) {
  const fp = keyPath(key);
  if (fs.existsSync(fp)) fs.unlinkSync(fp);
}

function listPrefix(prefix) {
  const root = path.join(STORE, prefix);
  if (!fs.existsSync(root)) return [];
  return fs
    .readdirSync(root)
    .filter((n) => n.endsWith(".json"))
    .map((n) => `${prefix}${n}`);
}

function randomToken(bytes = 24) {
  return crypto.randomBytes(bytes).toString("base64url");
}

function randomId() {
  return crypto.randomUUID();
}

function safeKeyPart(value) {
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

function send(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type, X-Edit-Token",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
  });
  res.end(body);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on("data", (c) => {
      size += c.length;
      if (size > 1024 * 1024) {
        reject(new Error("payload too large"));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function extractToken(req, url, body) {
  const q = url.searchParams.get("edit_token") || url.searchParams.get("token");
  if (q) return q.trim();
  const h = req.headers["x-edit-token"];
  if (h) return String(h).trim();
  if (body && (body.edit_token || body.token)) return String(body.edit_token || body.token).trim();
  return "";
}

function publicDraft(record) {
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

function deriveCounts(payload) {
  const materials = payload.materials || {};
  const teachings = materials.teachings || {};
  const doctrine = String(teachings.doctrine_text || "").trim();
  const stories = Array.isArray(materials.stories) ? materials.stories.length : 0;
  const practices = Array.isArray(materials.practices) ? materials.practices.length : 0;
  const quotes = Array.isArray(materials.quotes) ? materials.quotes.length : 0;
  const files = Array.isArray(materials.files) ? materials.files.length : 0;
  const links = Array.isArray(materials.links) ? materials.links.length : 0;
  return {
    teachings: doctrine ? 1 : 0,
    hooks: 0,
    scenes: 0,
    stories,
    practices,
    reflections: String(materials.reflections_integrations_text || "").trim() ? 1 : 0,
    integrations: String(materials.reflections_integrations_text || "").trim() ? 1 : 0,
    pivots: 0,
    threads: 0,
    permissions: 0,
    takeaways: 0,
    quotes,
    raw_sources: files + links,
  };
}

ensureDir(STORE);
ensureDir(path.join(STORE, DRAFT_PREFIX));
ensureDir(path.join(STORE, DRAFT_TOKEN_PREFIX));
ensureDir(path.join(STORE, SUBMISSION_PREFIX));
ensureDir(path.join(STORE, ACTIVATION_PREFIX));

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://127.0.0.1:${PORT}`);
  if (req.method === "OPTIONS") {
    send(res, 204, {});
    return;
  }

  try {
    // Health
    if (url.pathname === "/health") {
      send(res, 200, { ok: true, store: STORE, mock: true });
      return;
    }

    // POST /api/teacher-onboarding/drafts
    if (req.method === "POST" && url.pathname === "/api/teacher-onboarding/drafts") {
      const body = JSON.parse((await readBody(req)) || "{}");
      const ui_state = body.ui_state && typeof body.ui_state === "object" ? body.ui_state : body;
      const teacher_name = String(
        body.teacher_name || ui_state?.identity?.teacherName || ""
      ).trim();
      const teacher_id = String(body.teacher_id || ui_state?.identity?.teacherId || "").trim();
      const now = new Date().toISOString();
      const draft_id = randomId();
      const edit_token = randomToken(24);
      const record = {
        schema_version: "teacher_onboarding_draft_v1",
        draft_id,
        edit_token,
        status: "draft",
        created_at: now,
        updated_at: now,
        teacher_id: safeKeyPart(teacher_id || teacher_name || "teacher"),
        teacher_name,
        ui_state,
        server_policy: {
          production_atoms_created: false,
          operator_review_required: true,
          client_readiness_trusted_for_production: false,
        },
        submission_key: null,
      };
      putJson(`${DRAFT_PREFIX}${draft_id}.json`, record);
      putJson(`${DRAFT_TOKEN_PREFIX}${edit_token}.json`, { draft_id, updated_at: now });
      send(res, 201, {
        ok: true,
        draft_id,
        edit_token,
        status: "draft",
        resume_path: `/teacher_onboarding.html?edit_token=${encodeURIComponent(edit_token)}`,
        draft: publicDraft(record),
        server_policy: record.server_policy,
        mock: true,
        store: STORE,
      });
      return;
    }

    // GET /api/teacher-onboarding/drafts?edit_token=
    if (req.method === "GET" && url.pathname === "/api/teacher-onboarding/drafts") {
      const token = extractToken(req, url, null);
      if (!token) {
        send(res, 400, { status: "error", detail: "edit_token is required" });
        return;
      }
      const idx = getJson(`${DRAFT_TOKEN_PREFIX}${token}.json`);
      if (!idx) {
        send(res, 404, { status: "error", detail: "draft not found for token" });
        return;
      }
      const record = getJson(`${DRAFT_PREFIX}${idx.draft_id}.json`);
      if (!record || record.edit_token !== token) {
        send(res, 404, { status: "error", detail: "draft missing" });
        return;
      }
      send(res, 200, {
        ok: true,
        draft_id: record.draft_id,
        edit_token: record.edit_token,
        status: record.status,
        ui_state: record.ui_state || {},
        draft: publicDraft(record),
        server_policy: record.server_policy,
        mock: true,
      });
      return;
    }

    // /api/teacher-onboarding/drafts/:id/rotate-token
    const rotateMatch = url.pathname.match(
      /^\/api\/teacher-onboarding\/drafts\/([^/]+)\/rotate-token$/
    );
    if (req.method === "POST" && rotateMatch) {
      const id = decodeURIComponent(rotateMatch[1]);
      const body = JSON.parse((await readBody(req)) || "{}");
      const token = extractToken(req, url, body);
      const record = getJson(`${DRAFT_PREFIX}${id}.json`);
      if (!record || record.edit_token !== token) {
        send(res, 403, { status: "error", detail: "invalid edit_token" });
        return;
      }
      if (record.status !== "draft") {
        send(res, 409, { status: "error", detail: "only active drafts may rotate tokens" });
        return;
      }
      const old = record.edit_token;
      const neu = randomToken(24);
      record.edit_token = neu;
      record.updated_at = new Date().toISOString();
      putJson(`${DRAFT_PREFIX}${id}.json`, record);
      deleteKey(`${DRAFT_TOKEN_PREFIX}${old}.json`);
      putJson(`${DRAFT_TOKEN_PREFIX}${neu}.json`, { draft_id: id, updated_at: record.updated_at });
      send(res, 200, {
        ok: true,
        draft_id: id,
        edit_token: neu,
        resume_path: `/teacher_onboarding.html?edit_token=${encodeURIComponent(neu)}`,
        draft: publicDraft(record),
        mock: true,
      });
      return;
    }

    // /api/teacher-onboarding/drafts/:id
    const draftMatch = url.pathname.match(/^\/api\/teacher-onboarding\/drafts\/([^/]+)$/);
    if (draftMatch) {
      const id = decodeURIComponent(draftMatch[1]);
      if (req.method === "GET") {
        const token = extractToken(req, url, null);
        const record = getJson(`${DRAFT_PREFIX}${id}.json`);
        if (!record || record.edit_token !== token) {
          send(res, 403, { status: "error", detail: "invalid edit_token" });
          return;
        }
        send(res, 200, {
          ok: true,
          draft_id: record.draft_id,
          edit_token: record.edit_token,
          status: record.status,
          ui_state: record.ui_state || {},
          draft: publicDraft(record),
          mock: true,
        });
        return;
      }
      if (req.method === "PUT") {
        const body = JSON.parse((await readBody(req)) || "{}");
        const token = extractToken(req, url, body);
        const record = getJson(`${DRAFT_PREFIX}${id}.json`);
        if (!record || record.edit_token !== token) {
          send(res, 403, { status: "error", detail: "invalid edit_token" });
          return;
        }
        if (record.status !== "draft" && body.status !== "submitted") {
          send(res, 409, { status: "error", detail: "only drafts in status=draft may be edited" });
          return;
        }
        const ui_state = body.ui_state && typeof body.ui_state === "object" ? body.ui_state : record.ui_state;
        record.ui_state = ui_state;
        record.updated_at = new Date().toISOString();
        record.teacher_name = String(
          body.teacher_name || ui_state?.identity?.teacherName || record.teacher_name || ""
        ).trim();
        if (body.status === "submitted") {
          record.status = "submitted";
          if (body.submission_key) record.submission_key = String(body.submission_key);
        }
        putJson(`${DRAFT_PREFIX}${id}.json`, record);
        send(res, 200, {
          ok: true,
          draft_id: record.draft_id,
          edit_token: record.edit_token,
          status: record.status,
          draft: publicDraft(record),
          mock: true,
        });
        return;
      }
      if (req.method === "DELETE") {
        const token = extractToken(req, url, null);
        const record = getJson(`${DRAFT_PREFIX}${id}.json`);
        if (!record || record.edit_token !== token) {
          send(res, 403, { status: "error", detail: "invalid edit_token" });
          return;
        }
        if (record.status !== "draft") {
          send(res, 409, { status: "error", detail: "only drafts may be deleted" });
          return;
        }
        deleteKey(`${DRAFT_TOKEN_PREFIX}${record.edit_token}.json`);
        deleteKey(`${DRAFT_PREFIX}${id}.json`);
        send(res, 200, { ok: true, deleted: id, mock: true });
        return;
      }
    }

    // GET /api/teacher-onboarding/queue
    if (req.method === "GET" && url.pathname === "/api/teacher-onboarding/queue") {
      const drafts = listPrefix(DRAFT_PREFIX)
        .map((key) => {
          const r = getJson(key);
          return r ? { ...publicDraft(r), key } : null;
        })
        .filter(Boolean)
        .sort((a, b) => String(b.updated_at).localeCompare(String(a.updated_at)));
      const submissions = listPrefix(SUBMISSION_PREFIX)
        .map((key) => {
          const r = getJson(key);
          if (!r) return null;
          return {
            key,
            teacher_id: r.teacher_id || "",
            teacher_name: r.teacher_name || "",
            received_at: r.received_at || "",
            status: "submitted",
            readiness_score: r.server_readiness?.server_score ?? null,
            server_policy: {
              production_atoms_created: false,
              operator_review_required: true,
            },
          };
        })
        .filter(Boolean);
      send(res, 200, {
        ok: true,
        generated_at: new Date().toISOString(),
        drafts,
        submissions,
        counts: { drafts: drafts.length, submissions: submissions.length },
        server_policy: {
          production_atoms_created: false,
          operator_review_required: true,
          read_only: true,
        },
        mock: true,
        store: STORE,
      });
      return;
    }

    // POST /api/teacher-onboarding/submit (one-shot + draft-linked)
    if (req.method === "POST" && url.pathname === "/api/teacher-onboarding/submit") {
      const payload = JSON.parse((await readBody(req)) || "{}");
      const teacherName = String(
        payload.teacher_name || payload.identity?.public_teacher_name || ""
      ).trim();
      const email = String(payload.identity?.contact_email || "").trim();
      const rights = payload.rights || {};
      if (!teacherName || !email) {
        send(res, 400, { status: "error", detail: "teacher_name and identity.contact_email required" });
        return;
      }
      if (
        !rights.own_voice_or_original_material &&
        !rights.ownsMaterial &&
        !rights.permission_to_process_into_atoms &&
        !rights.processingConsent
      ) {
        // keep loose for local smoke if rights partially set — still require final consent
      }
      if (!rights.final_consent_to_submit_intake && !rights.consent) {
        send(res, 400, { status: "error", detail: "final consent is required" });
        return;
      }
      const counts = deriveCounts(payload);
      const total = Object.values(counts).reduce((s, n) => s + n, 0);
      if (total <= 0) {
        send(res, 400, { status: "error", detail: "at least one material item is required" });
        return;
      }
      const ts = new Date().toISOString();
      const teacherId = safeKeyPart(payload.teacher_id || teacherName);
      const key = `${SUBMISSION_PREFIX}${teacherId}__${ts.replace(/[:.]/g, "-")}.json`;
      const readiness = {
        server_score: Math.min(100, total * 5),
        server_counts: counts,
        missing_minimums: [],
        recommended_gaps: [],
        activation_ready: true,
      };
      const record = {
        ...payload,
        teacher_id: teacherId,
        teacher_name: teacherName,
        received_at: ts,
        server_readiness: readiness,
        server_policy: {
          client_readiness_trusted_for_production: false,
          production_atoms_created: false,
          operator_review_required: true,
        },
      };
      putJson(key, record);
      const activation = {
        schema_version: "teacher_onboarding_activation_v1",
        teacher_id: teacherId,
        teacher_name: teacherName,
        status: "intake_received_pending_operator_review",
        submitted_at: ts,
        source: "teacher_onboarding_intake",
        activation_ready: true,
        readiness_score: readiness.server_score,
        counts,
        operator_review_required: true,
      };
      putJson(`${ACTIVATION_PREFIX}${teacherId}.json`, activation);

      const draftId = String(payload.draft_id || "").trim();
      const editToken = String(payload.edit_token || "").trim();
      if (draftId && editToken) {
        const draft = getJson(`${DRAFT_PREFIX}${draftId}.json`);
        if (draft && draft.edit_token === editToken) {
          draft.status = "submitted";
          draft.submission_key = key;
          draft.updated_at = ts;
          putJson(`${DRAFT_PREFIX}${draftId}.json`, draft);
        }
      }

      send(res, 200, {
        ok: true,
        key,
        activation,
        production_atoms_created: false,
        mock: true,
        store: STORE,
      });
      return;
    }

    send(res, 404, { status: "error", detail: `no route ${req.method} ${url.pathname}` });
  } catch (err) {
    send(res, 500, { status: "error", detail: String(err.message || err) });
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`teacher_portal_dev_api listening on http://127.0.0.1:${PORT}`);
  console.log(`store=${STORE}`);
  // Write pid for cleanup
  const pidFile = path.join(__dirname, ".teacher_portal_dev_api.pid");
  fs.writeFileSync(pidFile, String(process.pid));
});
