// Cloudflare Pages Function: Teacher Source onboarding intake persistence.
//
// This endpoint records raw intake material for later operator/Pearl_Int review. It
// deliberately does not create production teacher atoms, does not trust the client
// readiness score as truth, and stores only a public-safe activation/status object
// under the activation key.

import { AwsClient } from "../../_lib/aws4fetch.js";
import {
  DRAFT_PREFIX,
  getJson as storeGetJson,
  mockEnabled,
  putJson as storePutJson,
  r2Configured,
} from "../../_lib/teacher_onboarding_store.js";

const MAX_BODY_BYTES = 1024 * 1024;
const DEFAULT_BUCKET = "phoenix-omega-artifacts";
const SUBMISSION_PREFIX = "teacher_onboarding/submissions/";
const ACTIVATION_PREFIX = "teacher_onboarding/activations/";
const EXECUTABLE_FILE_RE =
  /\.(app|bat|bin|cmd|com|cpl|dll|dmg|exe|gadget|hta|html?|jar|js|jse|mjs|msi|php|pl|ps1|py|rb|scr|sh|vb|vbs|war|wasm|wsf)$/i;

const TARGETS = [
  { key: "teachings", label: "Doctrine / teachings", min: 4, preferred: 12 },
  { key: "hooks", label: "Hooks", min: 12, preferred: 12 },
  { key: "scenes", label: "Scenes", min: 12, preferred: 12 },
  { key: "stories", label: "Stories", min: 20, preferred: 20 },
  { key: "practices", label: "Exercises / practices", min: 12, preferred: 40 },
  { key: "reflections", label: "Reflections", min: 12, preferred: 12 },
  { key: "integrations", label: "Integrations", min: 12, preferred: 12 },
  { key: "pivots", label: "Pivots", min: 15, preferred: 15 },
  { key: "threads", label: "Threads", min: 15, preferred: 15 },
  { key: "permissions", label: "Permissions", min: 15, preferred: 15 },
  { key: "takeaways", label: "Takeaways", min: 15, preferred: 15 },
  { key: "quotes", label: "Quotes / source excerpts", min: 0, preferred: 12 },
  { key: "raw_sources", label: "Raw uploads / links", min: 1, preferred: 8 },
];

function r2ObjectUrl(env, key) {
  const bucket = (env.R2_BUCKET || DEFAULT_BUCKET).trim();
  const endpoint =
    (env.R2_ENDPOINT || "").trim() ||
    `https://${String(env.R2_ACCOUNT_ID || "").trim()}.r2.cloudflarestorage.com`;
  return `${endpoint.replace(/\/$/, "")}/${bucket}/${key}`;
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

function timestampKey(ts) {
  return ts.replace(/[:.]/g, "-");
}

function textBlocks(value) {
  const text = String(value || "").trim();
  if (!text) return 0;
  const blocks = text
    .split(/\n{2,}|\n(?=(?:[-*•]|\d+[.)])\s+)/)
    .map((part) => part.replace(/^[-*•\d.)\s]+/, "").trim())
    .filter((part) => part.length > 12);
  return Math.max(1, blocks.length);
}

function countRows(rows, fields) {
  if (!Array.isArray(rows)) return 0;
  return rows.filter((row) => {
    if (!row || typeof row !== "object") return false;
    return fields.some((field) => String(row[field] || "").trim());
  }).length;
}

function countStrings(values) {
  if (!Array.isArray(values)) return 0;
  return values.filter((value) => String(value || "").trim()).length;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function collectFileNames(value, out = []) {
  if (!value || typeof value !== "object") return out;
  if (Array.isArray(value)) {
    value.forEach((item) => collectFileNames(item, out));
    return out;
  }
  if (typeof value.name === "string") out.push(value.name);
  Object.entries(value).forEach(([key, nested]) => {
    if (key !== "name") collectFileNames(nested, out);
  });
  return out;
}

function deriveCounts(payload) {
  const materials = payload.materials && typeof payload.materials === "object" ? payload.materials : {};
  const teachings = materials.teachings && typeof materials.teachings === "object" ? materials.teachings : {};
  const quotes = materials.quotes && typeof materials.quotes === "object" ? materials.quotes : {};
  const uploads = materials.uploads && typeof materials.uploads === "object" ? materials.uploads : {};

  const doctrineText = teachings.doctrine_text || materials.teachings_text || "";
  const reflectionText = materials.reflections_integrations_text || "";
  const teachingUrls = asArray(teachings.urls);
  const links = asArray(materials.links);
  const uploadLinks = asArray(uploads.links);
  const files = asArray(materials.files).length ? asArray(materials.files) : asArray(uploads.files);
  const sourceUrlRows = asArray(materials.urls);

  return {
    teachings: textBlocks(doctrineText) + countStrings(teachingUrls),
    hooks: 0,
    scenes: 0,
    stories: countRows(materials.stories, ["title", "context", "story", "point", "source"]),
    practices: countRows(materials.practices, ["name", "instructions", "guidance", "helps_with", "helpsWith"]),
    reflections: textBlocks(reflectionText),
    integrations: textBlocks(reflectionText),
    pivots: 0,
    threads: 0,
    permissions: 0,
    takeaways: 0,
    quotes:
      countRows(materials.quotes, ["text", "source"]) +
      countStrings(quotes.signature_quotes) +
      countStrings(quotes.repeated_phrases) +
      countStrings(quotes.metaphors),
    raw_sources: files.length + countStrings(links) + countStrings(uploadLinks) + countRows(sourceUrlRows, ["url"]),
  };
}

function deriveReadiness(payload) {
  const counts = deriveCounts(payload);
  const rows = TARGETS.map((target) => {
    const count = counts[target.key] || 0;
    return {
      ...target,
      count,
      ratio: Math.min(1, count / (target.preferred || target.min || 1)),
    };
  });
  const score = Math.round((rows.reduce((sum, row) => sum + row.ratio, 0) / rows.length) * 100);
  const missingMinimums = rows
    .filter((row) => row.min > 0 && row.count < row.min)
    .map((row) => ({
      key: row.key,
      label: row.label,
      current: row.count,
      minimum: row.min,
      missing: row.min - row.count,
    }));
  const recommendedGaps = rows
    .filter((row) => row.count < row.preferred)
    .map((row) => ({
      key: row.key,
      label: row.label,
      current: row.count,
      preferred: row.preferred,
      missing: row.preferred - row.count,
    }));

  return {
    server_score: score,
    server_counts: counts,
    missing_minimums: missingMinimums,
    recommended_gaps: recommendedGaps,
    activation_ready: missingMinimums.length === 0,
  };
}

function validatePayload(payload) {
  if (!payload || typeof payload !== "object") return "JSON object body required";
  const teacherName = String(payload.teacher_name || payload.identity?.public_teacher_name || "").trim();
  const email = String(payload.identity?.contact_email || "").trim();
  const rights = payload.rights && typeof payload.rights === "object" ? payload.rights : {};
  if (!teacherName) return "teacher_name is required";
  if (!email) return "identity.contact_email is required";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "identity.contact_email is invalid";
  if (!rights.own_voice_or_original_material && !rights.ownsMaterial) return "own-voice or source permission attestation is required";
  if (!rights.permission_to_process_into_atoms && !rights.processingConsent) return "permission to process into candidate atoms is required";
  if (!rights.no_unauthorized_copyrighted_material && !rights.noUnauthorizedCopyright) {
    return "no-unauthorized-copyright attestation is required";
  }
  if (!rights.final_consent_to_submit_intake && !rights.consent) return "final consent is required";

  const readiness = deriveReadiness(payload);
  const totalMaterialCount = Object.values(readiness.server_counts).reduce(
    (sum, value) => sum + Number(value || 0),
    0
  );
  if (totalMaterialCount <= 0) {
    return "at least one teaching, source, story, practice, quote, or reflection is required";
  }

  const executable = collectFileNames(payload).find((name) => EXECUTABLE_FILE_RE.test(name));
  if (executable) return `executable file metadata is not accepted: ${executable}`;
  return "";
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
  let raw;
  try {
    raw = await request.text();
    if (new TextEncoder().encode(raw).length > MAX_BODY_BYTES) {
      return json({ status: "error", detail: "payload too large" }, 413);
    }
    payload = JSON.parse(raw || "{}");
  } catch (_err) {
    return json({ status: "error", detail: "invalid JSON body" }, 400);
  }

  const validationError = validatePayload(payload);
  if (validationError) return json({ status: "error", detail: validationError }, 400);

  const useMock = mockEnabled(env);
  if (!useMock && !r2Configured(env)) {
    return json(
      { ok: false, status: "unconfigured", detail: "R2 credentials not configured on this Pages deploy" },
      503
    );
  }

  const ts = new Date().toISOString();
  const teacherId = safeKeyPart(payload.teacher_id || payload.identity?.teacher_id || payload.teacher_name);
  const teacherName = String(payload.teacher_name || payload.identity?.public_teacher_name || "").trim();
  const readiness = deriveReadiness(payload);
  const activation = {
    schema_version: "teacher_onboarding_activation_v1",
    teacher_id: teacherId,
    teacher_name: teacherName,
    status: "intake_received_pending_operator_review",
    submitted_at: ts,
    source: "teacher_onboarding_intake",
    activation_ready: readiness.activation_ready,
    readiness_score: readiness.server_score,
    counts: readiness.server_counts,
    missing_minimums: readiness.missing_minimums,
    recommended_gaps: readiness.recommended_gaps,
    operator_review_required: true,
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

  const key = `${SUBMISSION_PREFIX}${teacherId}__${timestampKey(ts)}.json`;
  const activationKey = `${ACTIVATION_PREFIX}${teacherId}.json`;

  try {
    if (useMock) {
      const submissionPut = await storePutJson(env, key, record);
      if (!submissionPut.ok) {
        return json({ status: "error", detail: "submission not persisted" }, 502);
      }
      const activationPut = await storePutJson(env, activationKey, activation);
      if (!activationPut.ok) {
        return json({ status: "error", detail: "activation not persisted", key }, 502);
      }
    } else {
      const accessKeyId = String(env.R2_ACCESS_KEY_ID || "").trim();
      const secretAccessKey = String(env.R2_SECRET_ACCESS_KEY || "").trim();
      const aws = new AwsClient({ accessKeyId, secretAccessKey, region: "auto", service: "s3" });
      const submissionPut = await putJson(aws, env, key, record);
      if (!submissionPut.ok) {
        console.error(`teacher onboarding submission PUT failed (${submissionPut.status}) for ${key}`);
        return json({ status: "error", detail: "submission not persisted" }, 502);
      }

      const activationPut = await putJson(aws, env, activationKey, activation);
      if (!activationPut.ok) {
        console.error(`teacher onboarding activation PUT failed (${activationPut.status}) for ${activationKey}`);
        return json({ status: "error", detail: "activation not persisted", key }, 502);
      }
    }
  } catch (err) {
    console.error("teacher onboarding R2 write error:", err);
    return json({ status: "error", detail: "R2 write failed" }, 502);
  }

  // Optional: mark linked draft as submitted (portal v2). Failures are non-fatal.
  const draftId = String(payload.draft_id || "").trim();
  const editToken = String(payload.edit_token || "").trim();
  if (draftId && editToken && (useMock || r2Configured(env))) {
    try {
      const draftKey = `${DRAFT_PREFIX}${draftId}.json`;
      const draftGet = await storeGetJson(env, draftKey);
      if (draftGet.ok && String(draftGet.value?.edit_token || "") === editToken) {
        await storePutJson(env, draftKey, {
          ...draftGet.value,
          status: "submitted",
          submission_key: key,
          updated_at: ts,
          server_policy: {
            ...(draftGet.value.server_policy || {}),
            production_atoms_created: false,
            operator_review_required: true,
          },
        });
      }
    } catch (_err) {
      /* non-fatal */
    }
  }

  return json({ ok: true, key, activation, production_atoms_created: false }, 200);
}

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
