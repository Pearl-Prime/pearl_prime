// Cloudflare Pages Function: on-demand R2 EPUB download proxy (Waystream).
// Uses S3-compatible API credentials (cross-account) — not an R2 binding, because
// phoenix-omega-artifacts lives on the operator R2 account while Pages deploys to
// the b80152c3 GitHub Actions account.

import { AwsClient } from "../_lib/aws4fetch.js";

const BRAND = "way_stream_sanctuary";
const BOOK_ID_RE = /^way_stream_sanctuary__[a-z0-9_]+$/i;
const WEEK_RE = /^\d{4}-W\d{2}$/;
const DEFAULT_BUCKET = "phoenix-omega-artifacts";

function r2ObjectUrl(env, key) {
  const bucket = (env.R2_BUCKET || DEFAULT_BUCKET).trim();
  const endpoint = (env.R2_ENDPOINT || "").trim()
    || `https://${String(env.R2_ACCOUNT_ID || "").trim()}.r2.cloudflarestorage.com`;
  return `${endpoint.replace(/\/$/, "")}/${bucket}/${key}`;
}

export async function onRequest(context) {
  const { env } = context;
  const accessKeyId = String(env.R2_ACCESS_KEY_ID || "").trim();
  const secretAccessKey = String(env.R2_SECRET_ACCESS_KEY || "").trim();
  const accountId = String(env.R2_ACCOUNT_ID || "").trim();

  if (!accessKeyId || !secretAccessKey || !accountId) {
    return new Response("R2 credentials not configured", { status: 503 });
  }

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
  const objectUrl = r2ObjectUrl(env, key);

  try {
    const aws = new AwsClient({
      accessKeyId,
      secretAccessKey,
      region: "auto",
      service: "s3",
    });
    const signed = await aws.sign(objectUrl);
    const object = await fetch(signed);

    if (object.status === 404) {
      return new Response("Book not found", { status: 404 });
    }
    if (!object.ok) {
      return new Response("Download failed", { status: 502 });
    }

    const headers = new Headers();
    headers.set("Content-Type", object.headers.get("Content-Type") || "application/epub+zip");
    headers.set("Content-Disposition", `attachment; filename="${book_id}.epub"`);
    headers.set("Cache-Control", "public, max-age=3600");

    return new Response(object.body, { status: 200, headers });
  } catch (_err) {
    return new Response("Download failed", { status: 500 });
  }
}
