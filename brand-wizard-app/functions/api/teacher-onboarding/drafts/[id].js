// GET/PUT/DELETE /api/teacher-onboarding/drafts/:id
import {
  DRAFT_PREFIX,
  DRAFT_TOKEN_PREFIX,
  deleteKey,
  extractEditToken,
  getJson,
  json,
  publicDraft,
  putJson,
  requireStore,
} from "../../../_lib/teacher_onboarding_store.js";

const MAX_BODY_BYTES = 1024 * 1024;

async function loadAuthorizedDraft(env, draftId, token) {
  if (!draftId || !token) return { error: json({ status: "error", detail: "draft id and edit_token required" }, 400) };
  const draftGet = await getJson(env, `${DRAFT_PREFIX}${draftId}.json`);
  if (!draftGet.ok) return { error: json({ status: "error", detail: "draft not found" }, 404) };
  const record = draftGet.value;
  if (String(record.edit_token || "") !== token) {
    return { error: json({ status: "error", detail: "invalid edit_token" }, 403) };
  }
  return { record };
}

export async function onRequestGet(context) {
  const { request, env, params } = context;
  const blocked = requireStore(env);
  if (blocked) return blocked;
  // Preserve UUID dashes — light sanitize only
  const id = String(params.id || "").trim().slice(0, 80);
  const token = extractEditToken(request);
  const { record, error } = await loadAuthorizedDraft(env, id, token);
  if (error) return error;
  return json({
    ok: true,
    draft_id: record.draft_id,
    edit_token: record.edit_token,
    status: record.status,
    ui_state: record.ui_state || {},
    draft: publicDraft(record),
    server_policy: record.server_policy,
  });
}

export async function onRequestPut(context) {
  const { request, env, params } = context;
  const blocked = requireStore(env);
  if (blocked) return blocked;

  const id = String(params.id || "").trim().slice(0, 80);
  let body;
  try {
    const raw = await request.text();
    if (new TextEncoder().encode(raw).length > MAX_BODY_BYTES) {
      return json({ status: "error", detail: "payload too large" }, 413);
    }
    body = JSON.parse(raw || "{}");
  } catch (_err) {
    return json({ status: "error", detail: "invalid JSON body" }, 400);
  }

  const token = extractEditToken(request, body);
  const { record, error } = await loadAuthorizedDraft(env, id, token);
  if (error) return error;
  if (record.status !== "draft") {
    return json({ status: "error", detail: "only drafts in status=draft may be edited" }, 409);
  }

  const ui_state = body.ui_state && typeof body.ui_state === "object" ? body.ui_state : record.ui_state;
  const teacher_name = String(
    body.teacher_name || ui_state?.identity?.teacherName || record.teacher_name || ""
  ).trim();
  const teacher_id = String(body.teacher_id || ui_state?.identity?.teacherId || record.teacher_id || "").trim();

  const updated = {
    ...record,
    updated_at: new Date().toISOString(),
    teacher_name,
    teacher_id: teacher_id || record.teacher_id,
    ui_state,
    server_policy: {
      production_atoms_created: false,
      operator_review_required: true,
      client_readiness_trusted_for_production: false,
    },
  };

  if (body.status === "submitted") {
    updated.status = "submitted";
    if (body.submission_key) updated.submission_key = String(body.submission_key);
  }

  const put = await putJson(env, `${DRAFT_PREFIX}${id}.json`, updated);
  if (!put.ok) return json({ status: "error", detail: "draft update failed" }, 502);

  return json({
    ok: true,
    draft_id: updated.draft_id,
    edit_token: updated.edit_token,
    status: updated.status,
    draft: publicDraft(updated),
    server_policy: updated.server_policy,
  });
}

export async function onRequestDelete(context) {
  const { request, env, params } = context;
  const blocked = requireStore(env);
  if (blocked) return blocked;

  const id = String(params.id || "").trim().slice(0, 80);
  const token = extractEditToken(request);
  const { record, error } = await loadAuthorizedDraft(env, id, token);
  if (error) return error;
  if (record.status !== "draft") {
    return json({ status: "error", detail: "only drafts may be deleted; submissions are immutable" }, 409);
  }

  await deleteKey(env, `${DRAFT_TOKEN_PREFIX}${record.edit_token}.json`);
  const del = await deleteKey(env, `${DRAFT_PREFIX}${id}.json`);
  if (!del.ok) return json({ status: "error", detail: "draft delete failed" }, 502);
  return json({ ok: true, deleted: id }, 200);
}

export async function onRequest(context) {
  const method = context.request.method;
  if (method === "GET") return onRequestGet(context);
  if (method === "PUT") return onRequestPut(context);
  if (method === "DELETE") return onRequestDelete(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}
