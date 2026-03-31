/** Map BrandWizard persona / format selections to example_registry.json fields. */
export const WIZARD_PERSONA_TO_REGISTRY_PERSONA = {
  burned_out_pro: "burned_out_founder",
  gen_z_seeker: "anxious_student",
  gen_alpha: "anxious_student",
  grief_carrier: "overwhelmed_caregiver",
  anxious_achiever: "anxious_student",
  spiritual_returner: "spiritual_seeker",
  new_parent: "overwhelmed_caregiver",
};

/** book → self_help + pearl_news + tools lanes; manga → manga */
export function lanesForFormatFocus(formatFocus) {
  if (formatFocus === "manga") return new Set(["manga"]);
  if (formatFocus === "book") return new Set(["self_help", "pearl_news", "breathwork_tools"]);
  return null;
}

export function registryPersonaForWizard(wizardPersonaId) {
  return WIZARD_PERSONA_TO_REGISTRY_PERSONA[wizardPersonaId] ?? null;
}

export function filterExamples(registryRows, { wizardPersonaId, formatFocus, market = "us" }) {
  const regPersona = registryPersonaForWizard(wizardPersonaId);
  const laneFilter = lanesForFormatFocus(formatFocus);
  return registryRows.filter((row) => {
    if (row.market !== market) return false;
    if (regPersona && row.persona !== regPersona) return false;
    if (laneFilter && !laneFilter.has(row.lane)) return false;
    return true;
  });
}
