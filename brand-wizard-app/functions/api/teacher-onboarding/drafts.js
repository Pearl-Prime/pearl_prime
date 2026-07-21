// POST /api/teacher-onboarding/drafts — create draft
// GET  /api/teacher-onboarding/drafts?edit_token= — resume draft
import {
  DRAFT_PREFIX,
  DRAFT_TOKEN_PREFIX,
  extractEditToken,
  getJson,
  json,
  newDraftRecord,
  publicDraft,
  putJson,
  requireStore,
} from "../../_lib/teacher_onboarding_store.js";

const MAX_BODY_BYTES = 1024 * 1024;

export async function onRequestPost(context) {
  const { request, env } = context;
  const blocked = requireStore(env);
  if (blocked) return blocked;

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

  const ui_state = body.ui_state && typeof body.ui_state === "object" ? body.ui_state : body;
  const teacher_name =
    String(body.teacher_name || ui_state?.identity?.teacherName || ui_state?.teacher_name || "").trim();
  const teacher_id = String(body.teacher_id || ui_state?.identity?.teacherId || "").trim();

  const record = newDraftRecord({ teacher_id, teacher_name, ui_state });
  const draftKey = `${DRAFT_PREFIX}${record.draft_id}.json`;
  const tokenKey = `${DRAFT_TOKEN_PREFIX}${record.edit_token}.json`;

  const putDraft = await putJson(env, draftKey, record);
  if (!putDraft.ok) {
    return json({ status: "error", detail: "draft not persisted", code: putDraft.status }, 502);
  }
  const putToken = await putJson(env, tokenKey, { draft_id: record.draft_id, updated_at: record.updated_at });
  if (!putToken.ok) {
    return json({ status: "error", detail: "draft token index not persisted" }, 502);
  }

  return json(
    {
      ok: true,
      draft_id: record.draft_id,
      edit_token: record.edit_token,
      status: record.status,
      resume_path: `/teacher_onboarding.html?edit_token=${encodeURIComponent(record.edit_token)}`,
      draft: publicDraft(record),
      server_policy: record.server_policy,
    },
    201
  );
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const blocked = requireStore(env);
  if (blocked) return blocked;

  const token = extractEditToken(request);
  if (!token) {
    return json({ status: "error", detail: "edit_token is required" }, 400);
  }

  const tokenLookup = await getJson(env, `${DRAFT_TOKEN_PREFIX}${token}.json`);
  if (!tokenLookup.ok) {
    return json({ status: "error", detail: "draft not found for token" }, 404);
  }
  const draftId = String(tokenLookup.value?.draft_id || "").trim();
  if (!draftId) return json({ status: "error", detail: "token index corrupt" }, 502);

  const draftGet = await getJson(env, `${DRAFT_PREFIX}${draftId}.json`);
  if (!draftGet.ok) return json({ status: "error", detail: "draft missing" }, 404);
  const record = draftGet.value;
  if (String(record.edit_token || "") !== token) {
    return json({ status: "error", detail: "token mismatch" }, 403);
  }

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

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  if (context.request.method === "GET") return onRequestGet(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}
