#!/usr/bin/env node
/**
 * Headless locale key parity check for teacher onboarding (all 14 locales).
 * Confirms every locale file has the same key set as en-US (no blank required strings).
 */
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "src", "locales", "teacher_onboarding");
const REQUIRED = [
  "en-US", "zh-CN", "zh-TW", "zh-HK", "zh-SG", "ja-JP", "ko-KR",
  "es-US", "es-ES", "fr-FR", "de-DE", "it-IT", "hu-HU", "pt-BR",
];

function flatten(obj, prefix = "", out = {}) {
  for (const [k, v] of Object.entries(obj || {})) {
    if (k === "_meta") continue;
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) flatten(v, key, out);
    else out[key] = v;
  }
  return out;
}

const en = flatten(JSON.parse(readFileSync(join(root, "en-US.json"), "utf8")));
const enKeys = Object.keys(en).sort();
let failed = 0;

for (const loc of REQUIRED) {
  const path = join(root, `${loc}.json`);
  let data;
  try {
    data = JSON.parse(readFileSync(path, "utf8"));
  } catch (e) {
    console.error(`FAIL ${loc}: missing or unreadable — ${e.message}`);
    failed += 1;
    continue;
  }
  const flat = flatten(data);
  const missing = enKeys.filter((k) => flat[k] == null || flat[k] === "");
  if (missing.length) {
    console.error(`FAIL ${loc}: ${missing.length} blank/missing keys e.g. ${missing.slice(0, 5).join(", ")}`);
    failed += 1;
  } else {
    const todo = data?._meta?.todo ? " (en-US fallback TODO)" : "";
    console.log(`OK   ${loc}: ${enKeys.length} keys${todo}`);
  }
}

const files = readdirSync(root).filter((f) => f.endsWith(".json"));
if (files.length !== 14) {
  console.error(`FAIL expected 14 locale files, found ${files.length}`);
  failed += 1;
}

process.exit(failed ? 1 : 0);
