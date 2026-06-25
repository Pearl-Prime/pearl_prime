// Cloudflare Pages Function: brand-wizard signup persistence proxy.
//
// The static Pages deploy has no FastAPI backend, so the wizard client cannot reach
// POST /api/v1/onboarding/submit directly. This Function receives the signup POST and
// forwards it to the FastAPI submit endpoint (server/routes/brand_onboarding.py), which
// logs the submission + assigns the brand in the gitignored roster overlay.
//
// The backend base URL is a deploy-time Pages env var / binding — NOT hardcoded:
//   ONBOARDING_API_BASE  e.g. "https://api.pearlprime.internal" (no trailing /api/...).
// Mirrors functions/download/[book_id].js (#1886): onRequest + env bindings + graceful
// degradation (clear non-200 instead of a crash) when the backend isn't configured.

const SUBMIT_PATH = "/api/v1/onboarding/submit";
const MAX_BODY_BYTES = 256 * 1024; // wizard_yaml is capped at 200k server-side; allow headroom.

export async function onRequestPost(context) {
  const { request, env } = context;

  // Parse + lightly validate the client payload before we forward anything.
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

  // Backend base must be configured at deploy time. Degrade gracefully (not a crash):
  // return a clear non-200 the client can surface, while still acknowledging the data
  // wasn't silently lost — the client keeps the localStorage record as a fallback.
  const base = String(env.ONBOARDING_API_BASE || "").trim().replace(/\/$/, "");
  if (!base) {
    return json({
      status: "unconfigured",
      detail: "ONBOARDING_API_BASE not set on this Pages deploy; signup retained client-side only",
    }, 503);
  }

  const target = base + SUBMIT_PATH;
  try {
    const upstream = await fetch(target, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(env.ONBOARDING_API_TOKEN ? { Authorization: `Bearer ${String(env.ONBOARDING_API_TOKEN).trim()}` } : {}),
      },
      body: JSON.stringify(payload),
    });

    const text = await upstream.text();
    const contentType = upstream.headers.get("Content-Type") || "application/json";
    // Pass the backend's status + body straight through so the client sees real results
    // (e.g. 422 brand_not_buildable, 200 submitted) rather than a synthesized response.
    return new Response(text, {
      status: upstream.status,
      headers: { "Content-Type": contentType, "Cache-Control": "no-store" },
    });
  } catch (_err) {
    // Backend unreachable — surface a clear 502, signup still retained client-side.
    return json({ status: "error", detail: "onboarding backend unreachable" }, 502);
  }
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
