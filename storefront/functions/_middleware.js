// Pages Functions middleware: CORS preflight for the /api/* routes.
import { CORS } from "./_lib.js";

export async function onRequest({ request, next }) {
  if (request.method === "OPTIONS") {
    return new Response(null, { headers: { ...CORS, "access-control-max-age": "86400" } });
  }
  return next();
}
