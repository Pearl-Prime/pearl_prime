// GET /api/download/:sku?email= — entitlement-gated download (§12/§13 delivery).
// Re-checks that the email owns the SKU (account_library, not revoked), then streams
// the paid asset from R2 (env.ASSETS). asset_url is never exposed by the catalog API;
// this route is the only path to the full file.
//
// Hardening follow-up (needs a signing secret): replace the raw ?email= with an
// HMAC-signed, 15-min-TTL token minted by /api/account/library.
import { bad, getDB, sha256Hex } from "../../_lib.js";

const MIME = {
  epub: "application/epub+zip", m4b: "audio/mp4", mp3: "audio/mpeg",
  pdf: "application/pdf", png: "image/png", cbz: "application/vnd.comicbook+zip",
};

export async function onRequestGet({ request, params, env }) {
  try {
    const db = getDB(env);
    const email = (new URL(request.url).searchParams.get("email") || "").trim().toLowerCase();
    const skuId = params.sku;
    if (!email || !skuId) return bad(400, "email and sku required");

    const emailHash = await sha256Hex(email);
    const owns = await db.prepare(
      "SELECT 1 FROM account_library WHERE email_hash = ? AND sku_id = ? AND revoked_at IS NULL LIMIT 1"
    ).bind(emailHash, skuId).first();
    if (!owns) return bad(403, "not entitled to this item");

    const row = await db.prepare("SELECT asset_url, product_type FROM sku WHERE sku_id = ?").bind(skuId).first();
    if (!row || !row.asset_url) return bad(404, "asset not available yet");
    if (!env.ASSETS) return bad(503, "asset storage not provisioned");

    const obj = await env.ASSETS.get(row.asset_url);
    if (!obj) return bad(404, "asset file not uploaded yet");

    const ext = (row.asset_url.split(".").pop() || "bin").toLowerCase();
    const headers = new Headers();
    headers.set("content-type", MIME[ext] || "application/octet-stream");
    headers.set("content-disposition", `attachment; filename="${skuId}.${ext}"`);
    headers.set("cache-control", "private, no-store");
    if (obj.httpEtag) headers.set("etag", obj.httpEtag);
    return new Response(obj.body, { headers });
  } catch (e) { return bad(500, String(e && e.message || e)); }
}
