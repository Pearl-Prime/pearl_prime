// GET /api/teacher-onboarding/queue — operator pending queue (public-safe, read-only)
import {
  DRAFT_PREFIX,
  SUBMISSION_PREFIX,
  getJson,
  json,
  listPrefix,
  publicDraft,
  requireStore,
} from "../../_lib/teacher_onboarding_store.js";

function publicSubmission(record, key) {
  if (!record || typeof record !== "object") return null;
  const readiness = record.server_readiness || {};
  return {
    key,
    teacher_id: record.teacher_id || "",
    teacher_name: record.teacher_name || "",
    received_at: record.received_at || record.submitted_at || "",
    status: "submitted",
    readiness_score: readiness.server_score ?? record.readiness?.functional_percent ?? null,
    activation_ready: readiness.activation_ready ?? false,
    server_policy: {
      production_atoms_created: false,
      operator_review_required: true,
      client_readiness_trusted_for_production: false,
      ...(record.server_policy || {}),
      production_atoms_created: false,
    },
  };
}

export async function onRequestGet(context) {
  const { env } = context;
  const blocked = requireStore(env);
  if (blocked) return blocked;

  const draftsListed = await listPrefix(env, DRAFT_PREFIX, 100);
  const subsListed = await listPrefix(env, SUBMISSION_PREFIX, 100);
  if (!draftsListed.ok && !subsListed.ok) {
    return json({ status: "error", detail: "queue list failed" }, 502);
  }

  const drafts = [];
  for (const key of draftsListed.keys || []) {
    if (!key.endsWith(".json")) continue;
    const got = await getJson(env, key);
    if (!got.ok) continue;
    const pub = publicDraft(got.value);
    if (pub) drafts.push({ ...pub, key });
  }

  const submissions = [];
  for (const key of subsListed.keys || []) {
    if (!key.endsWith(".json")) continue;
    const got = await getJson(env, key);
    if (!got.ok) continue;
    const pub = publicSubmission(got.value, key);
    if (pub) submissions.push(pub);
  }

  drafts.sort((a, b) => String(b.updated_at || "").localeCompare(String(a.updated_at || "")));
  submissions.sort((a, b) => String(b.received_at || "").localeCompare(String(a.received_at || "")));

  return json({
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
  });
}

export async function onRequest(context) {
  if (context.request.method === "GET") return onRequestGet(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}
