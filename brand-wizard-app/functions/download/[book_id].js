// Cloudflare Pages Function: on-demand R2 EPUB download proxy (Waystream).
// Feed entries use /download/<book_id>?week=<iso-week> — no presigned URL expiry.

const BRAND = "way_stream_sanctuary";
const BOOK_ID_RE = /^way_stream_sanctuary__[a-z0-9_]+$/i;
const WEEK_RE = /^\d{4}-W\d{2}$/;

export async function onRequest(context) {
  const { book_id: rawId } = context.params;
  const book_id = decodeURIComponent(String(rawId || "")).replace(/\.epub$/i, "");

  if (!BOOK_ID_RE.test(book_id)) {
    return new Response("Invalid book id", { status: 400 });
  }

  const url = new URL(context.request.url);
  const week = url.searchParams.get("week") || "2026-W26";
  if (!WEEK_RE.test(week)) {
    return new Response("Invalid week", { status: 400 });
  }

  const key = `brand/${BRAND}/deliveries/${week}/amazon_kdp/${book_id}.epub`;

  if (!context.env.R2_BUCKET) {
    return new Response("R2 binding not configured", { status: 503 });
  }

  try {
    const object = await context.env.R2_BUCKET.get(key);
    if (!object) {
      return new Response("Book not found", { status: 404 });
    }

    const headers = new Headers();
    object.writeHttpMetadata(headers);
    headers.set("Content-Type", "application/epub+zip");
    headers.set("Content-Disposition", `attachment; filename="${book_id}.epub"`);
    headers.set("Cache-Control", "public, max-age=3600");

    return new Response(object.body, { status: 200, headers });
  } catch (_err) {
    return new Response("Download failed", { status: 500 });
  }
}
