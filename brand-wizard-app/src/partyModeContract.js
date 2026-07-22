/**
 * Brand wizard party-mode contract scaffold (gt30d I019).
 * SPECCED in docs/specs/BRAND_WIZARD_PARTY_MODE_V1_SPEC.md.
 * Toggle UI not wired — do not claim EXECUTED-REAL.
 */

export const PARTY_MODE_DEFAULT = false;
export const PARTY_MODE_YAML_KEY = "party_mode";

/** Normalize unknown input to boolean party_mode. */
export function normalizePartyMode(value) {
  if (value === true || value === "true" || value === 1 || value === "1") {
    return true;
  }
  return false;
}

/**
 * Merge party_mode into a brand YAML-shaped object under brand.*.
 * Does not mutate the input.
 */
export function applyPartyModeToBrandYaml(brandObj, partyMode) {
  const base =
    brandObj && typeof brandObj === "object" ? { ...brandObj } : { brand: {} };
  const brand =
    base.brand && typeof base.brand === "object" ? { ...base.brand } : {};
  brand[PARTY_MODE_YAML_KEY] = normalizePartyMode(partyMode);
  return { ...base, brand };
}

export default {
  PARTY_MODE_DEFAULT,
  PARTY_MODE_YAML_KEY,
  normalizePartyMode,
  applyPartyModeToBrandYaml,
};
