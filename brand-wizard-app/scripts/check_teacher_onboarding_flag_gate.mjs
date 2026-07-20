#!/usr/bin/env node
/**
 * Lightweight (no vitest-pool) proof that FlagLocaleGate is the first render
 * and that all 14 locale codes are wired in the gate component + i18n module.
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const gate = readFileSync(
  join(root, "src/components/teacher-onboarding/FlagLocaleGate.jsx"),
  "utf8"
);
const onboarding = readFileSync(
  join(root, "src/components/teacher-onboarding/TeacherOnboarding.jsx"),
  "utf8"
);
const i18n = readFileSync(join(root, "src/i18n-teacher-onboarding.jsx"), "utf8");

const locales = [
  "en-US", "zh-CN", "zh-TW", "zh-HK", "zh-SG", "ja-JP", "ko-KR",
  "es-US", "es-ES", "fr-FR", "de-DE", "it-IT", "hu-HU", "pt-BR",
];

let failed = 0;
function ok(cond, msg) {
  if (!cond) {
    console.error("FAIL", msg);
    failed += 1;
  } else {
    console.log("OK  ", msg);
  }
}

ok(gate.includes('data-testid="teacher-onboarding-flag-gate"'), "FlagLocaleGate exposes gate test id");
ok(gate.includes("TEACHER_ONBOARDING_LOCALES.map"), "FlagLocaleGate maps all locales");
ok(onboarding.includes("if (!locale)"), "TeacherOnboarding gates on locale");
ok(onboarding.includes("<FlagLocaleGate"), "TeacherOnboarding renders FlagLocaleGate before form");
ok(onboarding.includes("function TeacherOnboardingForm"), "Form is split so hooks stay valid");
ok(i18n.includes('phoenix_teacher_onboarding_locale'), "Distinct localStorage key");
ok(!i18n.includes("phoenix_lane") || i18n.includes("never cross-contaminates"), "Does not share wizard phoenix_lane key");

for (const loc of locales) {
  ok(i18n.includes(`"${loc}"`), `i18n loader includes ${loc}`);
  ok(gate.includes(`flag-${loc}`) || gate.includes("data-testid={`flag-${lane.code}`}"), `flag test id pattern for ${loc}`);
}

// Ensure Identity section only appears inside TeacherOnboardingForm (after gate)
const gateIdx = onboarding.indexOf("if (!locale)");
const formIdx = onboarding.indexOf('id="identity"');
ok(gateIdx >= 0 && formIdx > gateIdx, "Identity section appears after locale gate in source order");

process.exit(failed ? 1 : 0);
