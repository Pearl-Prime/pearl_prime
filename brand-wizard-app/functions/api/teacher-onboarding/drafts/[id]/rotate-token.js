// POST /api/teacher-onboarding/drafts/:id/rotate-token
import {
  DRAFT_PREFIX,
  DRAFT_TOKEN_PREFIX,
  deleteKey,
  extractEditToken,
  getJson,
  json,
  publicDraft,
  putJson,
  randomToken,
  requireStore,
} from "../../../../_lib/teacher_onboarding_store.js";

export async function onRequestPost(context) {
  const { request, env, params } = context;
  const blocked = requireStore(env);
  if (blocked) return blocked;

  const id = String(params.id || "").trim().slice(0, 80);
  let body = {};
  try {
    const raw = await request.text();
    body = raw ? JSON.parse(raw) : {};
  } catch (_err) {
    return json({ status: "error", detail: "invalid JSON body" }, 400);
  }

  const token = extractEditToken(request, body);
  if (!id || !token) return json({ status: "error", detail: "draft id and edit_token required" }, 400);

  const draftGet = await getJson(env, `${DRAFT_PREFIX}${id}.json`);
  if (!draftGet.ok) return json({ status: "error", detail: "draft not found" }, 404);
  const record = draftGet.value;
  if (String(record.edit_token || "") !== token) {
    return json({ status: "error", detail: "invalid edit_token" }, 403);
  }
  if (record.status !== "draft") {
    return json({ status: "error", detail: "only active drafts may rotate tokens" }, 409);
  }

  const oldToken = record.edit_token;
  const newToken = randomToken(24);
  const updated = {
    ...record,
    edit_token: newToken,
    updated_at: new Date().toISOString(),
  };

  const putDraft = await putJson(env, `${DRAFT_PREFIX}${id}.json`, updated);
  if (!putDraft.ok) return json({ status: "error", detail: "draft update failed" }, 502);

  await deleteKey(env, `${DRAFT_TOKEN_PREFIX}${oldToken}.json`);
  const putToken = await putJson(env, `${DRAFT_TOKEN_PREFIX}${newToken}.json`, {
    draft_id: id,
    updated_at: updated.updated_at,
  });
  if (!putToken.ok) return json({ status: "error", detail: "token index update failed" }, 502);

  return json({
    ok: true,
    draft_id: id,
    edit_token: newToken,
    resume_path: `/teacher_onboarding.html?edit_token=${encodeURIComponent(newToken)}`,
    draft: publicDraft(updated),
  });
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ status: "error", detail: "method not allowed" }, 405);
}
