/**
 * Second-claimant hybrid brand offer helpers (Phase C).
 * 409 teacher_claimed stays a 409 — these helpers only parse/surface the offer body.
 * Accept → create generalized hybrid → resubmit onboarding assignment (close the loop).
 */

import { LANE_FROM_MARKET, brandAssignmentPayload } from "./brandMatch.js";

function normMarket(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
}

/** Market token or lane code → registry lane (en_us, ja_jp, …). */
export function resolveLaneFromMarket(market) {
  const m = normMarket(market);
  if (LANE_FROM_MARKET[m]) return LANE_FROM_MARKET[m];
  if (/^[a-z]{2}_[a-z]{2}$/.test(m)) return m;
  return "en_us";
}

export function parseOnboardingErrorPayload(detail) {
  if (!detail || typeof detail !== "object") return {};
  return detail.detail && typeof detail.detail === "object" ? detail.detail : detail;
}

/**
 * @returns {{ kind: 'ok' } | { kind: 'brand_claimed', message: string } | { kind: 'teacher_claimed_offer', message: string, teacherId: string, arches: string[] } | { kind: 'generic', message: string }}
 */
export function classifyOnboardingSubmitFailure(responseStatus, detail, opts = {}) {
  const payload = parseOnboardingErrorPayload(detail);
  const market = opts.onboardingMarket || "en_US";

  if (responseStatus === 409 && payload?.error === "brand_claimed") {
    const assignedTo = payload?.assigned_to;
    return {
      kind: "brand_claimed",
      message: `That brand is already assigned${assignedTo ? ` to ${assignedTo}` : ""}. Do not treat this brand as active; contact ops for a new available brand.`,
    };
  }

  if (responseStatus === 409 && payload?.error === "teacher_claimed") {
    const offer = payload?.offer || {};
    const arches = Array.isArray(offer.available_archetypes) ? offer.available_archetypes : [];
    const teacherId = offer.teacher_id || payload?.teacher_id || "";
    try {
      sessionStorage.setItem(
        "phoenix_hybrid_offer",
        JSON.stringify({
          teacher_id: teacherId,
          lane: payload?.lane || market,
          available_archetypes: arches,
          claimed_brand_id: payload?.brand_id,
        })
      );
    } catch (_) {
      /* ignore */
    }
    if (!arches.length) {
      return {
        kind: "teacher_claimed_offer",
        teacherId,
        arches: [],
        message:
          "This teacher is already claimed in this market, and all 40 hybrid archetype slots are used. Contact ops.",
      };
    }
    return {
      kind: "teacher_claimed_offer",
      teacherId,
      arches,
      message: `TEACHER_CLAIMED_HYBRID_OFFER::${teacherId}::${arches.slice(0, 8).join(",")}`,
    };
  }

  return {
    kind: "generic",
    message:
      "Live assignment did not persist. Keep this screen open and contact ops before treating this brand as active.",
  };
}

export function parseHybridOfferMessage(submissionError) {
  if (!submissionError || !String(submissionError).startsWith("TEACHER_CLAIMED_HYBRID_OFFER::")) {
    return null;
  }
  const parts = String(submissionError).split("::");
  return {
    teacherId: parts[1] || "",
    arches: (parts[2] || "").split(",").filter(Boolean),
  };
}

export async function acceptHybridBrand({ teacherId, archetypeId, lane }) {
  const laneNorm = resolveLaneFromMarket(lane);
  const resp = await fetch("api/onboarding/accept-hybrid", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      teacher_id: teacherId,
      archetype_id: archetypeId,
      lane: laneNorm,
    }),
  });
  const body = await resp.json().catch(() => ({}));
  const payload = parseOnboardingErrorPayload(body);
  if (!resp.ok) {
    const err = new Error(payload?.message || payload?.error || "Hybrid accept failed");
    err.payload = payload;
    err.status = resp.status;
    throw err;
  }
  return {
    brand_id: body.brand_id || payload.brand_id,
    display_name: body.display_name || payload.display_name,
    teacher_id: teacherId,
    lane: laneNorm,
    attribution_mode: body.attribution_mode || "generalized",
    raw: body,
  };
}

/**
 * Create hybrid brand then immediately POST onboarding/submit so the director
 * assignment lands in R2 (closes accept-hybrid's resubmit_onboarding_with_brand_id).
 */
export async function acceptHybridAndAssign({
  teacherId,
  archetypeId,
  lane,
  contact,
  wizardYaml,
}) {
  const accepted = await acceptHybridBrand({ teacherId, archetypeId, lane });
  const match = {
    brand_id: accepted.brand_id,
    publication_corp: accepted.display_name || accepted.brand_id,
    teacher: teacherId,
    is_teacher: false,
    lane: accepted.lane,
    score: 100,
    basis: "hybrid:generalized",
  };
  const assignment = brandAssignmentPayload(match, contact || {});
  if (!assignment) {
    const err = new Error("Add first name and last name before accepting a hybrid brand.");
    err.match = match;
    throw err;
  }
  const c = contact || {};
  const response = await fetch("api/onboarding/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      brand_id: match.brand_id,
      lane: match.lane,
      publication_corp: match.publication_corp,
      ...assignment,
      brand_email: (c.email || "").trim() || null,
      contact: {
        first_name: c.firstName || "",
        last_name: c.lastName || "",
        phone: ((c.phoneCode || "+1") + " " + (c.phone || "")).trim(),
      },
      wizard_yaml: wizardYaml || "",
      match_score: 100,
      match_basis: "hybrid:generalized",
      attribution_mode: "generalized",
    }),
  });
  const detail = await response.json().catch(() => ({}));
  if (!response.ok) {
    const err = new Error(
      detail?.detail || detail?.error || `Hybrid created but assignment failed (${response.status})`
    );
    err.match = match;
    err.status = response.status;
    err.payload = detail;
    throw err;
  }
  try {
    localStorage.setItem("phoenix_pending_brand", JSON.stringify(match));
  } catch (_) {
    /* ignore */
  }
  return { match, submit: detail, accepted };
}
