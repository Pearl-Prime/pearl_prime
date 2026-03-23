const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store"
};

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload, null, 2), {
    status,
    headers: JSON_HEADERS
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === "/" || url.pathname === "/healthz") {
      return jsonResponse({
        service: "pearl-prime",
        status: "ok",
        contract_version: 1,
        source_of_truth: "repo-owned Cloudflare worker contract",
        release_evidence: "artifacts/release/pearl_prime_release_evidence.json"
      });
    }

    return jsonResponse(
      {
        service: "pearl-prime",
        error: "not_found"
      },
      404
    );
  }
};
