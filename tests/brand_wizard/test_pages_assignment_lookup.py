from __future__ import annotations

import subprocess


def test_pages_assignment_lookup_prefers_canonical_brand_index() -> None:
    script = r"""
import { pathToFileURL } from "node:url";

const modUrl = pathToFileURL(`${process.cwd()}/brand-wizard-app/functions/api/onboarding/assignment.js`).href;
const { onRequestGet } = await import(modUrl);

const calls = [];
globalThis.fetch = async (input) => {
  const url = typeof input === "string" ? input : input.url;
  calls.push(url);
  if (url.endsWith("/brand_admin_brands.json")) {
    return new Response(
      JSON.stringify({
        stabilizer_en_us: {
          d: "Harbor Line Books",
          arch: "stabilizer",
          brand_director_name: "Kamiko Parker",
          brand_director_id: "kamiko_parker",
          brand_director_status: "assigned",
        },
        optimizer_en_us: {
          d: "Daybreak Editions",
          arch: "optimizer",
        },
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  if (url.startsWith("https://r2.example/")) {
    return new Response(
      JSON.stringify({
        brand_id: "stabilizer_en_us",
        display_brand: "Harbor Line Books",
        brand_director_name: "aser asdf",
        brand_director_id: "aser_asdf",
        brand_director_status: "assigned",
        source: "r2_live_assignment",
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  throw new Error(`unexpected fetch ${url}`);
};

const env = {
  R2_ACCESS_KEY_ID: "test",
  R2_SECRET_ACCESS_KEY: "test",
  R2_ENDPOINT: "https://r2.example",
};
const request = new Request("https://brand-admin-onboarding-bu2.pages.dev/api/onboarding/assignment?brand=stabilizer_en_us");
const response = await onRequestGet({ request, env });
const body = await response.json();

if (response.status !== 200) throw new Error(`expected 200, got ${response.status}`);
if (body.brand_director_name !== "Kamiko Parker") {
  throw new Error(`canonical assignment did not win: ${JSON.stringify(body)}`);
}
if (body.source !== "brand_admin_brands") {
  throw new Error(`expected canonical source, got ${JSON.stringify(body)}`);
}
if (calls.some((url) => url.startsWith("https://r2.example/"))) {
  throw new Error(`canonical assignment should not fetch R2: ${JSON.stringify(calls)}`);
}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_pages_assignments_roster_merges_public_safe_r2_overlay() -> None:
    script = r"""
import { pathToFileURL } from "node:url";

const modUrl = pathToFileURL(`${process.cwd()}/brand-wizard-app/functions/api/onboarding/assignments.js`).href;
const { onRequestGet } = await import(modUrl);

globalThis.fetch = async (input) => {
  const url = typeof input === "string" ? input : input.url;
  if (url.endsWith("/brand_admin_brands.json")) {
    return new Response(
      JSON.stringify({
        stabilizer_en_us: {
          d: "Harbor Line Books",
          arch: "stabilizer",
          lane: "en_US",
          lifecycle: "active",
          buildable: true,
          brand_director_name: "Kamiko Parker",
          brand_director_id: "kamiko_parker",
          brand_director_status: "assigned",
        },
        optimizer_de_de: {
          d: "Daybreak Editions",
          arch: "optimizer",
          lane: "de_DE",
          lifecycle: "active",
          buildable: true,
        },
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  if (url.startsWith("https://r2.example/phoenix-omega-artifacts?")) {
    return new Response(
      `<?xml version="1.0" encoding="UTF-8"?>
       <ListBucketResult>
         <IsTruncated>false</IsTruncated>
         <Contents><Key>onboarding/assignments/stabilizer_en_us.json</Key></Contents>
         <Contents><Key>onboarding/assignments/optimizer_de_de.json</Key></Contents>
       </ListBucketResult>`,
      { status: 200, headers: { "Content-Type": "application/xml" } },
    );
  }
  if (url.includes("/onboarding/assignments/stabilizer_en_us.json")) {
    return new Response(
      JSON.stringify({
        brand_id: "stabilizer_en_us",
        display_brand: "Harbor Line Books",
        brand_director_name: "Wrong Overlay",
        brand_director_id: "wrong_overlay",
        brand_director_status: "assigned",
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  if (url.includes("/onboarding/assignments/optimizer_de_de.json")) {
    return new Response(
      JSON.stringify({
        brand_id: "optimizer_de_de",
        display_brand: "Daybreak Editions",
        brand_director_name: "Ari Weber",
        brand_director_id: "ari_weber",
        brand_director_status: "assigned",
        assigned_at: "2026-07-17T00:00:00.000Z",
        source: "r2_live_assignment",
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  throw new Error(`unexpected fetch ${url}`);
};

const env = {
  R2_ACCESS_KEY_ID: "test",
  R2_SECRET_ACCESS_KEY: "test",
  R2_ENDPOINT: "https://r2.example",
};
const request = new Request("https://brand-admin-onboarding-bu2.pages.dev/api/onboarding/assignments");
const response = await onRequestGet({ request, env });
const body = await response.json();

if (response.status !== 200) throw new Error(`expected 200, got ${response.status}`);
if (body.summary.total !== 2) throw new Error(`wrong total: ${JSON.stringify(body.summary)}`);
if (body.summary.assigned !== 2) throw new Error(`wrong assigned count: ${JSON.stringify(body.summary)}`);

const rows = Object.fromEntries(body.brands.map((row) => [row.brand_id, row]));
if (rows.stabilizer_en_us.brand_director_name !== "Kamiko Parker") {
  throw new Error(`canonical assignment should win: ${JSON.stringify(rows.stabilizer_en_us)}`);
}
if (rows.optimizer_de_de.base_brand !== "optimizer") {
  throw new Error(`global suffix was not stripped: ${JSON.stringify(rows.optimizer_de_de)}`);
}
if (rows.optimizer_de_de.brand_director_name !== "Ari Weber") {
  throw new Error(`R2 overlay did not fill unassigned brand: ${JSON.stringify(rows.optimizer_de_de)}`);
}
if (rows.optimizer_de_de.ops_url !== "/brand_handoff_dashboard.html?brand=optimizer_de_de") {
  throw new Error(`bad ops url: ${JSON.stringify(rows.optimizer_de_de)}`);
}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_pages_submit_uses_conditional_r2_assignment_claim() -> None:
    script = r"""
import { pathToFileURL } from "node:url";

const modUrl = pathToFileURL(`${process.cwd()}/brand-wizard-app/functions/api/onboarding/submit.js`).href;
const { onRequestPost } = await import(modUrl);

const assignmentPuts = [];
globalThis.fetch = async (input) => {
  const url = typeof input === "string" ? input : input.url;
  const method = typeof input === "string" ? "GET" : input.method || "GET";
  if (url.endsWith("/brand_admin_brands.json")) {
    return new Response(
      JSON.stringify({
        optimizer_en_us: {
          d: "Daybreak Editions",
          arch: "optimizer",
          lane: "en_US",
          lifecycle: "active",
          buildable: true,
        },
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  if (url.includes("/onboarding/assignments/optimizer_en_us.json") && method === "GET") {
    return new Response("missing", { status: 404 });
  }
  if (url.includes("/onboarding/assignments/optimizer_en_us.json") && method === "PUT") {
    assignmentPuts.push(input);
    return new Response("", { status: 200 });
  }
  if (url.includes("/onboarding/assignment_events/") && method === "PUT") {
    return new Response("", { status: 200 });
  }
  if (url.includes("/onboarding/submissions/") && method === "PUT") {
    return new Response("", { status: 200 });
  }
  throw new Error(`unexpected fetch ${method} ${url}`);
};

const env = {
  R2_ACCESS_KEY_ID: "test",
  R2_SECRET_ACCESS_KEY: "test",
  R2_ENDPOINT: "https://r2.example",
};
const request = new Request("https://brand-admin-onboarding-bu2.pages.dev/api/onboarding/submit", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    brand_id: "optimizer_en_us",
    publication_corp: "Daybreak Editions",
    brand_director_name: "Ari Weber",
    brand_director_id: "ari_weber",
    brand_email: "ari@example.com",
    wizard_yaml: "brand_id: optimizer_en_us",
  }),
});
const response = await onRequestPost({ request, env });
const body = await response.json();

if (response.status !== 200) throw new Error(`expected 200, got ${response.status}: ${JSON.stringify(body)}`);
if (assignmentPuts.length !== 1) throw new Error(`expected one assignment PUT, got ${assignmentPuts.length}`);
if (assignmentPuts[0].headers.get("if-none-match") !== "*") {
  throw new Error(`assignment PUT was not conditional: ${assignmentPuts[0].headers.get("if-none-match")}`);
}
if (body.assignment.brand_director_name !== "Ari Weber") {
  throw new Error(`bad assignment response: ${JSON.stringify(body)}`);
}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_pages_submit_returns_409_when_conditional_claim_loses_race() -> None:
    script = r"""
import { pathToFileURL } from "node:url";

const modUrl = pathToFileURL(`${process.cwd()}/brand-wizard-app/functions/api/onboarding/submit.js`).href;
const { onRequestPost } = await import(modUrl);

let assignmentGets = 0;
globalThis.fetch = async (input) => {
  const url = typeof input === "string" ? input : input.url;
  const method = typeof input === "string" ? "GET" : input.method || "GET";
  if (url.endsWith("/brand_admin_brands.json")) {
    return new Response(
      JSON.stringify({
        optimizer_en_us: { d: "Daybreak Editions", arch: "optimizer", lane: "en_US", buildable: true },
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  if (url.includes("/onboarding/assignments/optimizer_en_us.json") && method === "GET") {
    assignmentGets += 1;
    if (assignmentGets === 1) return new Response("missing", { status: 404 });
    return new Response(
      JSON.stringify({
        brand_id: "optimizer_en_us",
        display_brand: "Daybreak Editions",
        brand_director_name: "Prior Director",
        brand_director_id: "prior_director",
        brand_director_status: "assigned",
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  if (url.includes("/onboarding/assignments/optimizer_en_us.json") && method === "PUT") {
    return new Response("precondition failed", { status: 412 });
  }
  throw new Error(`unexpected fetch ${method} ${url}`);
};

const env = {
  R2_ACCESS_KEY_ID: "test",
  R2_SECRET_ACCESS_KEY: "test",
  R2_ENDPOINT: "https://r2.example",
};
const request = new Request("https://brand-admin-onboarding-bu2.pages.dev/api/onboarding/submit", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    brand_id: "optimizer_en_us",
    publication_corp: "Daybreak Editions",
    brand_director_name: "Ari Weber",
    brand_email: "ari@example.com",
    wizard_yaml: "brand_id: optimizer_en_us",
  }),
});
const response = await onRequestPost({ request, env });
const body = await response.json();

if (response.status !== 409) throw new Error(`expected 409, got ${response.status}: ${JSON.stringify(body)}`);
if (body.error !== "brand_claimed") throw new Error(`wrong conflict body: ${JSON.stringify(body)}`);
if (body.assigned_to !== "Prior Director") throw new Error(`missing prior director: ${JSON.stringify(body)}`);
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_pages_assignments_admin_release_requires_token_and_deletes_live_overlay() -> None:
    script = r"""
import { pathToFileURL } from "node:url";

const modUrl = pathToFileURL(`${process.cwd()}/brand-wizard-app/functions/api/onboarding/assignments.js`).href;
const { onRequestPost } = await import(modUrl);

const deleted = [];
globalThis.fetch = async (input) => {
  const url = typeof input === "string" ? input : input.url;
  const method = typeof input === "string" ? "GET" : input.method || "GET";
  if (url.endsWith("/brand_admin_brands.json")) {
    return new Response(
      JSON.stringify({
        optimizer_en_us: {
          d: "Daybreak Editions",
          arch: "optimizer",
          lane: "en_US",
          lifecycle: "active",
          buildable: true,
        },
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  }
  if (url.includes("/onboarding/assignments/optimizer_en_us.json") && method === "DELETE") {
    deleted.push(url);
    return new Response(null, { status: 204 });
  }
  if (url.includes("/onboarding/assignment_events/") && method === "PUT") {
    return new Response("", { status: 200 });
  }
  throw new Error(`unexpected fetch ${method} ${url}`);
};

const env = {
  R2_ACCESS_KEY_ID: "test",
  R2_SECRET_ACCESS_KEY: "test",
  R2_ENDPOINT: "https://r2.example",
  BRAND_DIRECTOR_ADMIN_TOKEN: "secret",
};
const unauthorized = new Request("https://brand-admin-onboarding-bu2.pages.dev/api/onboarding/assignments", {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-Admin-Token": "wrong" },
  body: JSON.stringify({ action: "release", brand_id: "optimizer_en_us" }),
});
const unauthorizedResponse = await onRequestPost({ request: unauthorized, env });
if (unauthorizedResponse.status !== 401) throw new Error(`expected 401, got ${unauthorizedResponse.status}`);

const request = new Request("https://brand-admin-onboarding-bu2.pages.dev/api/onboarding/assignments", {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-Admin-Token": "secret" },
  body: JSON.stringify({ action: "release", brand_id: "optimizer_en_us" }),
});
const response = await onRequestPost({ request, env });
const body = await response.json();
if (response.status !== 200) throw new Error(`expected 200, got ${response.status}: ${JSON.stringify(body)}`);
if (deleted.length !== 1) throw new Error(`expected one deleted assignment, got ${deleted.length}`);
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
