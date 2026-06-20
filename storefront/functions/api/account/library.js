// GET /api/account/library?email= — entitlements for an email (auto-provisioned
// post-purchase per Q-PRP-AUTH-01). Returns owned SKUs; the signed R2 download URL
// is issued by a follow-up route (R2 binding required — operator-provisioned bucket).
import { json, bad, getDB, sha256Hex, SKU_SELECT } from "../../_lib.js";

export async function onRequestGet({ request, env }) {
  try {
    const db = getDB(env);
    const email = (new URL(request.url).searchParams.get("email") || "").trim().toLowerCase();
    if (!email) return json({ items: [] }); // no identity yet -> empty library
    const emailHash = await sha256Hex(email);
    const rs = await db.prepare(
      `SELECT ${SKU_SELECT}, l.granted_at
       FROM account_library l JOIN sku s ON s.sku_id = l.sku_id
       WHERE l.email_hash = ? AND l.revoked_at IS NULL
       ORDER BY l.granted_at DESC`
    ).bind(emailHash).all();
    const items = (rs.results || []).map((row) => ({
      ...row,
      // Signed R2 URL (60-min TTL) is minted on demand once the ASSETS bucket is bound.
      download_path: `/api/account/library/${encodeURIComponent(row.sku_id)}/url?email=${encodeURIComponent(email)}`,
    }));
    return json({ items });
  } catch (e) { return bad(500, String(e && e.message || e)); }
}
