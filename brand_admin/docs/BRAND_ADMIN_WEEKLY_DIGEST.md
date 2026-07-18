# Brand admin weekly digest — manga section

The prose weekly package flow remains the primary source for `GET /api/v1/admin/weekly` (see `server/routes/brand_admin.py`).

The **manga lane** adds Markdown digest fragments under `artifacts/weekly_digests/`:

- `{brand_id}_weekly_digest_{YYYY-MM-DD}.md` — includes a **This week's manga** section with presigned Cloudflare R2 links (PDF, CBZ, EPUB) when uploads succeed.
- Dry runs use placeholder links (`SIGNED_URL_PLACEHOLDER:…`) for operator review without uploading objects.

## Subject line (email integration)

When wired to SendGrid (optional), mirror the prose digest pattern:

`Your weekly books — {YYYY-MM-DD}` with prose links unchanged and a new **Manga** subsection sourced from the same digest Markdown.

## Operator notes

- If no topic meets the image-bank threshold for a brand, the digest records a skip reason; prose-only delivery is unchanged.
- Failures in the manga lane append an **Manga lane failures** section and may trigger `WEEKLY_ROLLOUT_OPERATOR_EMAIL` when configured.
